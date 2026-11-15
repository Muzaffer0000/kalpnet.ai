"""Kendini geliştirme döngüsü: yeni vakalarla aday model eğit, donmuş test setinde eskisiyle kıyasla,
kurala uyarsa terfi ettir. Kullanım: python src/retrain.py <yeni_vakalar.csv>"""
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path

import joblib
import pandas as pd

import model_lib
import synth

DATA, MODELS = Path("data"), Path("models")
BINARY = list(synth.BIN) + ["male", "atypical", "urgent_cardiac"]
REQUIRED = ["condition", "age", "pain_type", "duration_min"] + BINARY


def validate(df):
    """Güven sınırı: geçersizse ValueError, tüm dosya reddedilir."""
    if set(df.columns) != set(REQUIRED) or len(df.columns) != len(REQUIRED):
        raise ValueError(f"sütunlar tam olarak şunlar olmalı: {sorted(REQUIRED)}")
    if df.empty:
        raise ValueError("dosya boş")
    num = df.drop(columns=["condition", "pain_type"]).apply(pd.to_numeric, errors="coerce")
    if num.isna().any().any():
        raise ValueError("sayısal sütunlarda eksik/sayısal olmayan değer var")
    if not num[BINARY].isin([0, 1]).all().all():
        raise ValueError("ikili sütunlar sadece 0/1 olabilir")
    if not df.pain_type.isin(synth.PAIN_TYPES).all():
        raise ValueError(f"pain_type şunlardan biri olmalı: {synth.PAIN_TYPES}")
    if not df.condition.isin(synth.CLASSES).all():
        raise ValueError(f"condition şunlardan biri olmalı: {synth.CLASSES}")
    if not num.age.between(18, 90).all():
        raise ValueError("age 18-90 aralığında olmalı")
    if not (num.duration_min >= 1).all():
        raise ValueError("duration_min >= 1 olmalı")
    return df.astype({c: int for c in num.columns})


def decide(active, cand):
    """(terfi mi, neden). active/cand: evaluate() sözlükleri."""
    if cand["missed"] > active["missed"]:
        return False, f"daha çok kaçırılan vaka ({cand['missed']} > {active['missed']})"
    if cand["sensitivity"] < model_lib.TARGET_SENS:
        return False, f"duyarlılık {cand['sensitivity']:.3f} < {model_lib.TARGET_SENS}"
    if cand["missed"] < active["missed"] or cand["specificity"] > active["specificity"]:
        return True, "daha iyi"
    return False, "iyileşme yok"


def main(path):
    try:
        new = validate(pd.read_csv(path))
    except (ValueError, pd.errors.ParserError) as e:
        sys.exit(f"REDDEDİLDİ: {e}")

    pool = pd.read_csv(DATA / "train_pool.csv")
    test = pd.read_csv(DATA / "test_frozen.csv")  # asla eğitimde kullanılmaz
    merged = pd.concat([pool, new], ignore_index=True)
    reg_path = MODELS / "registry.json"
    reg = json.load(open(reg_path))
    active_e = next(e for e in reg if e["status"] == "active")
    old = joblib.load(MODELS / "symptom_model.joblib")

    cand, thr = model_lib.train(merged)
    m_old = model_lib.evaluate(old["model"], old["threshold"], test)
    m_new = model_lib.evaluate(cand, thr, test)
    ok, reason = decide(m_old, m_new)

    entry = {"version": max(e["version"] for e in reg) + 1,
             "created": datetime.now().isoformat(timespec="seconds"),
             "train_rows": len(merged), "metrics": m_new}
    if ok:
        shutil.copy(MODELS / "symptom_model.joblib", MODELS / f"symptom_model_v{active_e['version']}.joblib")
        joblib.dump({"model": cand, "threshold": thr}, MODELS / "symptom_model.joblib")
        merged.to_csv(DATA / "train_pool.csv", index=False)
        active_e["status"] = "retired"
        entry["status"] = "active"
    else:
        entry.update(status="rejected", reason=reason)
    json.dump(reg + [entry], open(reg_path, "w"), indent=2)

    for name, m in (("eski", m_old), ("yeni", m_new)):
        print(f"{name}: AUC {m['auc']:.3f}  duyarlılık {m['sensitivity']:.3f}  "
              f"özgüllük {m['specificity']:.3f}  kaçırılan {m['missed']}/{m['n']}")
    print(f"+{len(new)} vaka, havuz {len(pool)} -> {len(merged)}")
    print(f"SONUÇ: v{entry['version']} " + ("TERFİ ETTİ (eski model v%d olarak saklandı)" % active_e["version"]
          if ok else f"REDDEDİLDİ: {reason}"))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("kullanım: python src/retrain.py <yeni_vakalar.csv>")
    main(sys.argv[1])
