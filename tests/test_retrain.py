import json
import sys
from pathlib import Path

import joblib
import pandas as pd
import pytest
from sklearn.model_selection import train_test_split

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
import model_lib, retrain, synth


@pytest.fixture
def env(tmp_path, monkeypatch):
    """Geçici data/ ve models/ ile v1 aktif model; gerçek dosyalara dokunmaz."""
    d, m = tmp_path / "data", tmp_path / "models"
    d.mkdir(); m.mkdir()
    monkeypatch.setattr(retrain, "DATA", d)
    monkeypatch.setattr(retrain, "MODELS", m)
    df = synth.generate(1500, 0)
    tr, te = train_test_split(df, test_size=0.3, stratify=df.urgent_cardiac, random_state=0)
    tr.to_csv(d / "train_pool.csv", index=False)
    te.to_csv(d / "test_frozen.csv", index=False)
    model, thr = model_lib.train(tr)
    joblib.dump({"model": model, "threshold": thr}, m / "symptom_model.joblib")
    reg = [{"version": 1, "created": "x", "train_rows": len(tr), "metrics": {}, "status": "active"}]
    json.dump(reg, open(m / "registry.json", "w"))
    return d, m


def snapshot(d, m):
    return {p.name: p.read_bytes() for p in list(d.iterdir()) + list(m.iterdir())}


def test_invalid_csv_rejected_nothing_changes(env, tmp_path):
    d, m = env
    good = synth.generate(50, 1)
    bad = {"extra": good.assign(foo=1), "age": good.assign(age=17),
           "binary": good.assign(smoker=2), "pain": good.assign(pain_type="x"),
           "dur": good.assign(duration_min=0)}
    before = snapshot(d, m)
    for name, df in bad.items():
        p = tmp_path / f"{name}.csv"; df.to_csv(p, index=False)
        with pytest.raises(SystemExit):
            retrain.main(str(p))
    assert snapshot(d, m) == before


M = lambda missed, sens, spec: {"missed": missed, "sensitivity": sens, "specificity": spec}
OLD = M(5, 0.985, 0.60)


@pytest.mark.parametrize("cand,expected", [
    (M(3, 0.99, 0.55), True),    # daha az kaçırılan
    (M(5, 0.985, 0.65), True),   # eşit kaçırılan, daha iyi özgüllük
    (M(6, 0.99, 0.90), False),   # daha çok kaçırılan
    (M(4, 0.97, 0.90), False),   # duyarlılık < 0.98
    (M(5, 0.985, 0.60), False),  # eşit
])
def test_decide(cand, expected):
    assert retrain.decide(OLD, cand)[0] is expected


def test_end_to_end_registry_entry(env, tmp_path):
    d, m = env
    p = tmp_path / "new.csv"; synth.generate(300, 2).to_csv(p, index=False)
    retrain.main(str(p))
    reg = json.load(open(m / "registry.json"))
    assert len(reg) == 2 and reg[1]["version"] == 2
    assert reg[1]["status"] in ("active", "rejected")
    if reg[1]["status"] == "active":
        assert reg[0]["status"] == "retired" and (m / "symptom_model_v1.joblib").exists()
        assert len(pd.read_csv(d / "train_pool.csv")) == reg[1]["train_rows"]
    else:
        assert reg[0]["status"] == "active" and "reason" in reg[1]
        assert len(pd.read_csv(d / "train_pool.csv")) == reg[0]["train_rows"]
