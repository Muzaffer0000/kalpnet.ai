"""200 satır örnekle + Python predict_proba -> tests/parity_cases.json (JS eşitlik testi için)."""
import json

import joblib
import pandas as pd

d = joblib.load("models/symptom_model.joblib")
df = pd.read_csv("data/synthetic_chestpain.csv").sample(200, random_state=1)
X = df.drop(columns=["condition", "urgent_cardiac", "atypical"])
p = d["model"].predict_proba(X)[:, 1]
cases = [{"input": r, "p": float(pi)} for r, pi in zip(X.to_dict("records"), p)]
json.dump({"threshold": float(d["threshold"]), "cases": cases}, open("tests/parity_cases.json", "w"))
print(len(cases), "vaka yazıldı;", int((p >= d["threshold"]).sum()), "tanesi eşiğin üstünde")
