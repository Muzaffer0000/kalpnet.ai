"""Semptom modeli: kardiyak (acil) mı değil mi. Eşik, test setine bakmadan %98 duyarlılığa göre seçilir."""
import joblib
import numpy as np
import pandas as pd
from sklearn.compose import make_column_transformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix, roc_auc_score
from sklearn.model_selection import StratifiedKFold, cross_val_predict, train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

TARGET_SENS = 0.98
df = pd.read_csv("data/synthetic_chestpain.csv")
y = df.urgent_cardiac
X = df.drop(columns=["condition", "urgent_cardiac", "atypical"])
Xtr, Xte, ytr, yte, dtr, dte = train_test_split(X, y, df, test_size=0.3, stratify=y, random_state=0)

model = make_pipeline(
    make_column_transformer((OneHotEncoder(), ["pain_type"]),
                            (StandardScaler(), ["age", "duration_min"]),
                            remainder="passthrough"),
    LogisticRegression(max_iter=2000, class_weight="balanced"))

# eşik: sadece eğitim verisinin çapraz doğrulama tahminlerinden
p_cv = cross_val_predict(model, Xtr, ytr, cv=StratifiedKFold(5, shuffle=True, random_state=0),
                         method="predict_proba")[:, 1]
thr = np.quantile(p_cv[ytr == 1], 1 - TARGET_SENS)
model.fit(Xtr, ytr)
p = model.predict_proba(Xte)[:, 1]
assert 0 < thr < 1

def line(name, mask):
    t = yte[mask]; pred = p[mask] >= thr
    tp = int((pred & (t == 1)).sum()); fn = int((~pred & (t == 1)).sum())
    tn = int((~pred & (t == 0)).sum()); fp = int((pred & (t == 0)).sum())
    print(f"{name:<22} n={len(t):<5} duyarlılık {tp/max(tp+fn,1):.3f}  özgüllük {tn/max(tn+fp,1):.3f}  kaçırılan {fn}")

print(f"test AUC {roc_auc_score(yte, p):.3f}, eşik {thr:.3f}")
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
