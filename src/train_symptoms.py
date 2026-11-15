"""Semptom modeli: kardiyak (acil) mı değil mi. Eşik, test setine bakmadan %98 duyarlılığa göre seçilir.
Ayrıca DONMUŞ test setini (data/test_frozen.csv) ve eğitim havuzunu (data/train_pool.csv) üretir."""
import json
import sys
from datetime import datetime
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

import model_lib

# kayıt defteri, havuz ve donmuş test sıfırlanır: retrain geçmişi silinmesin diye açık onay iste
if Path("models/registry.json").exists() and "--reset" not in sys.argv:
    sys.exit("models/registry.json zaten var. Her şeyi sıfırlamak için: python src/train_symptoms.py --reset")

df = pd.read_csv("data/synthetic_chestpain.csv")
dtr, dte = train_test_split(df, test_size=0.3, stratify=df.urgent_cardiac, random_state=0)
dtr.to_csv("data/train_pool.csv", index=False)
dte.to_csv("data/test_frozen.csv", index=False)

model, thr = model_lib.train(dtr)
yte = dte.urgent_cardiac
p = model.predict_proba(model_lib.features(dte))[:, 1]

def line(name, mask):
    t = yte[mask]; pred = p[mask] >= thr
    tp = int((pred & (t == 1)).sum()); fn = int((~pred & (t == 1)).sum())
    tn = int((~pred & (t == 0)).sum()); fp = int((pred & (t == 0)).sum())
    print(f"{name:<22} n={len(t):<5} duyarlılık {tp/max(tp+fn,1):.3f}  özgüllük {tn/max(tn+fp,1):.3f}  kaçırılan {fn}")

m = model_lib.evaluate(model, thr, dte)
print(f"test AUC {m['auc']:.3f}, eşik {thr:.3f}")
line("tüm test", np.ones(len(yte), bool))
line("atipik kalp krizi", (dte.atypical == 1).values)  # hepsi kardiyak: özgüllük anlamsız
line("kadın", (dte.male == 0).values)
line("diyabetli", (dte.diabetes == 1).values)
line("65 yaş üstü", (dte.age > 65).values)
print("en etkili belirtiler (kalp krizi lehine +, aleyhine -):")
names = model[0].get_feature_names_out(); coef = model[-1].coef_[0]
for i in np.argsort(-np.abs(coef))[:8]:
    print(f"  {names[i].split('__')[-1]:<28} {coef[i]:+.2f}")

joblib.dump({"model": model, "threshold": thr}, "models/symptom_model.joblib")
entry = {"version": 1, "created": datetime.now().isoformat(timespec="seconds"),
         "train_rows": len(dtr), "metrics": m, "status": "active"}
json.dump([entry], open("models/registry.json", "w"), indent=2)
print("kayıt: models/registry.json (v1 aktif)")
