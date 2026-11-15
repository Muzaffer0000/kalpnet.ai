"""Ortak model kodu: eğitim (eşik dahil) ve değerlendirme. train_symptoms.py ve retrain.py kullanır."""
import numpy as np
from sklearn.compose import make_column_transformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

TARGET_SENS = 0.98
DROP = ["condition", "urgent_cardiac", "atypical"]  # etiket ve etiket sızdıran sütunlar


def features(df):
    return df.drop(columns=DROP)


def train(df):
    """df'den (pipeline, eşik) üretir. Eşik sadece df'nin çapraz doğrulama tahminlerinden seçilir."""
    X, y = features(df), df.urgent_cardiac
    model = make_pipeline(
        make_column_transformer((OneHotEncoder(), ["pain_type"]),
                                (StandardScaler(), ["age", "duration_min"]),
                                remainder="passthrough"),
        LogisticRegression(max_iter=2000, class_weight="balanced"))
    p_cv = cross_val_predict(model, X, y, cv=StratifiedKFold(5, shuffle=True, random_state=0),
                             method="predict_proba")[:, 1]
    thr = np.quantile(p_cv[y == 1], 1 - TARGET_SENS)
    model.fit(X, y)
    assert 0 < thr < 1
    return model, thr


def evaluate(model, thr, df):
    y = df.urgent_cardiac.values
    p = model.predict_proba(features(df))[:, 1]
    pred = p >= thr
    tp = int((pred & (y == 1)).sum()); fn = int((~pred & (y == 1)).sum())
    tn = int((~pred & (y == 0)).sum()); fp = int((pred & (y == 0)).sum())
    return {"auc": float(roc_auc_score(y, p)), "sensitivity": tp / max(tp + fn, 1),
            "specificity": tn / max(tn + fp, 1), "missed": fn, "n": len(y)}
