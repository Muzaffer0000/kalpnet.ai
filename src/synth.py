"""Sentetik göğüs ağrısı vakaları: kardiyak / panik / reflü / kas-iskelet.

UYARI: Olasılıklar literatürden ve klinik genel bilgiden esinlenen VARSAYIMLARDIR, ölçülmüş değerler
değildir. Bu veriyle eğitilen model gerçek dünyada doğru çalıştığını kanıtlamaz; sadece boru hattını
geliştirmek ve sınıfları dengelemek içindir. Gerçek veriyle (MIMIC vb.) doğrulanmalıdır.
"""
import numpy as np
import pandas as pd

N, SEED, NOISE = 5000, 0, 0.05
CLASSES = ["cardiac", "panic", "reflux", "msk"]
PRIORS = [0.15, 0.35, 0.25, 0.25]

AGE = {"cardiac": (62, 12), "panic": (34, 10), "reflux": (45, 13), "msk": (42, 14)}
MALE = {"cardiac": .60, "panic": .35, "reflux": .50, "msk": .50}
# süreler bilerek çakışır: kalp krizi dakikalardan saatlere uzanır, uzun ağrı onu dışlamaz
DUR_MEDIAN_SD = {"cardiac": (45, 1.0), "panic": (15, .8), "reflux": (60, 1.0), "msk": (90, 1.2)}
PAIN = {  # pressure, sharp, burning, ache, other
    "cardiac": [.60, .10, .10, .15, .05], "panic": [.20, .40, .05, .10, .25],
    "reflux": [.10, .10, .65, .10, .05], "msk": [.05, .45, .02, .40, .08]}
PAIN_TYPES = ["pressure", "sharp", "burning", "ache", "other"]

# sütun: (kardiyak, panik, reflü, kas-iskelet) olasılıkları
BIN = {
    "radiates_arm_jaw": (.55, .08, .05, .10),
    "exertional_onset": (.55, .05, .10, .20),
    "onset_during_stress": (.15, .60, .10, .05),
    "sweating_cold": (.55, .30, .05, .03),
    "nausea": (.40, .25, .30, .03),
    "short_breath": (.55, .65, .10, .10),
    "tingling_hands_lips": (.03, .45, .01, .02),
    "fear_of_dying": (.20, .60, .02, .02),
    "palpitations": (.30, .60, .05, .05),
    "worse_breath_or_movement": (.10, .15, .08, .65),
    "tender_on_pressing": (.03, .05, .05, .60),
    "worse_after_meal_or_lying": (.05, .05, .65, .03),
    "relieved_by_antacid": (.05, .02, .55, .02),
    "relieved_by_rest": (.50, .20, .10, .10),
    "prior_panic_history": (.03, .45, .02, .02),
    "smoker": (.40, .25, .20, .20),
    "hypertension": (.55, .15, .25, .20),
    "diabetes": (.30, .05, .10, .08),
    "family_heart_history": (.45, .20, .20, .20),
    "high_cholesterol": (.50, .15, .25, .20),
}
CLASSIC = ["radiates_arm_jaw", "exertional_onset"]  # atipik kardiyakte zayıf görünür


def generate(n=N, seed=SEED):
    rng = np.random.default_rng(seed)
    label = rng.choice(CLASSES, n, p=PRIORS)
    rows = pd.DataFrame({"condition": label})
    k = lambda c: CLASSES.index(c)
    rows["age"] = [int(np.clip(rng.normal(*AGE[c]), 18, 90)) for c in label]
    rows["male"] = [int(rng.random() < MALE[c]) for c in label]
    # atipik kardiyak sunum: kadın ve diyabetlide daha sık (bilinen klinik gerçek)
    for col in ("diabetes",):
        rows[col] = [int(rng.random() < BIN[col][k(c)]) for c in label]
    p_atyp = np.clip(.15 + .20 * (1 - rows.male) + .20 * rows.diabetes, 0, 1)
    atyp = (rows.condition == "cardiac") & (rng.random(n) < p_atyp)
    for col, p in BIN.items():
        if col == "diabetes":
            continue
        pr = np.array([p[k(c)] for c in label], float)
        if col in CLASSIC:
            pr = np.where(atyp, pr * .4, pr)
        rows[col] = (rng.random(n) < pr).astype(int)
    rows["pain_type"] = [
        rng.choice(PAIN_TYPES, p=PAIN["panic" if a else c]) for c, a in zip(label, atyp)]
    rows["duration_min"] = [
        max(1, int(rng.lognormal(np.log(DUR_MEDIAN_SD[c][0]), DUR_MEDIAN_SD[c][1]))) for c in label]
    flip = rng.random((n, len(BIN))) < NOISE  # etiket-dışı gürültü: özellikleri bozar
    cols = list(BIN)
    rows[cols] = (rows[cols].values ^ flip).astype(int)
    rows["urgent_cardiac"] = (rows.condition == "cardiac").astype(int)
    rows["atypical"] = atyp.astype(int)
    return rows


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=N)
    ap.add_argument("--seed", type=int, default=SEED)
    ap.add_argument("--out", default="data/synthetic_chestpain.csv")
    a = ap.parse_args()
    df = generate(a.n, a.seed)
    assert len(df) == a.n and not df.isna().any().any()
    share = df.condition.value_counts(normalize=True)
    assert abs(share["cardiac"] - PRIORS[0]) < .03
    df.to_csv(a.out, index=False)
    print(df.condition.value_counts().to_string())
    print(f"atipik kardiyak: {int(df.atypical.sum())} / {int(df.urgent_cardiac.sum())}")
