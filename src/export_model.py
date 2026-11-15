"""models/symptom_model.joblib -> app/model.json (JSON; skor app'te düz JS ile hesaplanır)."""
import json
from datetime import datetime, timezone

import joblib

d = joblib.load("models/symptom_model.joblib")
pipe, thr = d["model"], float(d["threshold"])
ct, lr = pipe[0], pipe[-1]
ohe = ct.named_transformers_["onehotencoder"]
sc = ct.named_transformers_["standardscaler"]
cat_col = ct.transformers_[0][2][0]
num_cols = list(ct.transformers_[1][2])
bin_cols = list(ct.transformers_[2][2])
names = list(ct.get_feature_names_out())
coef = lr.coef_[0]
assert len(names) == len(coef)
w = dict(zip(names, (float(c) for c in coef)))
strip = lambda n: n.split("__", 1)[1]
cw = {strip(n): v for n, v in w.items()}  # sütun adý -> aðýrlýk
out = {
    "generated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    "feature_order": names,
    "categorical": {"column": cat_col, "categories": [str(c) for c in ohe.categories_[0]],
                    "coef": {str(c): cw[f"{cat_col}_{c}"] for c in ohe.categories_[0]}},
    "numeric": {c: {"mean": float(m), "scale": float(s), "coef": cw[c]} for c, m, s in zip(num_cols, sc.mean_, sc.scale_)},
    "binary": {c: cw[c] for c in bin_cols},
    "coefficients": w,
    "intercept": float(lr.intercept_[0]),
    "threshold": thr,
}
json.dump(out, open("app/model.json", "w"), indent=1)
print(f"app/model.json yazıldı: {len(names)} özellik, eşik {thr:.4f}, intercept {out['intercept']:.4f}")
print("kategoriler:", out["categorical"]["categories"]); print("ikili:", bin_cols)
