"""İlk model: Cleveland verisinde kalp hastalığı var/yok tahmini (5-katlı çapraz doğrulama)."""
import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix, roc_auc_score
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier

COLS = ["age", "sex", "cp", "trestbps", "chol", "fbs", "restecg", "thalach",
        "exang", "oldpeak", "slope", "ca", "thal", "num"]

df = pd.read_csv("data/uci_heart/processed.cleveland.data", names=COLS, na_values="?")
assert len(df) == 303
y = (df.pop("num") > 0).astype(int)  # 0 = sağlıklı, 1-4 = hastalık var
print(f"hasta: {len(df)}, hastalık oranı: {y.mean():.2f}, eksik değer: {int(df.isna().sum().sum())}")

models = {
    "lojistik regresyon": make_pipeline(SimpleImputer(strategy="median"), StandardScaler(),
                                        LogisticRegression(max_iter=1000)),
    "xgboost": XGBClassifier(n_estimators=100, max_depth=3, learning_rate=0.1, eval_metric="logloss"),
}
cv = StratifiedKFold(5, shuffle=True, random_state=0)

def report(name, p, thr):
    tn, fp, fn, tp = confusion_matrix(y, p >= thr).ravel()
    print(f"  eşik {thr:.2f}: duyarlılık {tp/(tp+fn):.2f}  özgüllük {tn/(tn+fp):.2f}  kaçırılan hasta {fn}")

for name, m in models.items():
    p = cross_val_predict(m, df, y, cv=cv, method="predict_proba")[:, 1]
    print(f"{name}: AUC {roc_auc_score(y, p):.3f}")
    report(name, p, 0.5)
    # güvenlik odaklı: hastaların %95'ini yakalayan en yüksek eşik
    report(name, p, np.quantile(p[y == 1], 0.05))
