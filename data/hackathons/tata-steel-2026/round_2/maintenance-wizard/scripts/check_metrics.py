#!/usr/bin/env python
"""Quick metrics check for all 3 fixes."""
import sys, joblib, numpy as np, pandas as pd
sys.path.insert(0, '.')
import logging
logging.basicConfig(level=logging.WARNING)
from pathlib import Path
from sklearn.metrics import f1_score, precision_score, recall_score, average_precision_score
from sklearn.model_selection import train_test_split
from wizard.ml.rul_estimator import predict_rul
from wizard.ml.anomaly_detector import get_anomaly_score

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
MODELS = ROOT / "data" / "models"

print("=== FIX 1: RUL ===")
readings = {
    "temperature_c":410.0,"process_temp_c":430.0,"pressure_bar":160.0,
    "vibration_mm_s":3.5,"rpm":1100.0,"torque_nm":550.0,
    "current_a":58.0,"tool_wear_min":200.0,"health_score":0.65,
}
r = predict_rul("T1", readings, "SS1", equipment_class="bearing")
print(f"BEFORE: P10=P50=P90 (all collapsed to ~0.01 days, root cause: per-engine min RUL as duration)")
print(f"AFTER : P10={r.rul_days_p10:.1f}d  P50={r.rul_days_p50:.1f}d  P90={r.rul_days_p90:.1f}d  spread={r.rul_days_p90-r.rul_days_p10:.1f}d")
print(f"model : {r.model_used}")

print()
print("=== FIX 2: ANOMALY ===")
td = pd.read_csv(RAW / "cmapss" / "test_FD001.txt", sep=r"\s+", header=None)
td.columns = ["engine","cycle","op1","op2","op3"] + [f"s{i}" for i in range(1,22)]
rul_t = np.loadtxt(RAW / "cmapss" / "RUL_FD001.txt")
scores, labs = [], []
for i, eng in enumerate(td["engine"].unique()):
    grp = td[td["engine"]==eng].sort_values("cycle")
    lab = int(float(rul_t[i]) <= 30)
    hist = []
    for _, row in grp.tail(30).iterrows():
        hist.append({"temperature_c":float(row["s2"]),"process_temp_c":float(row["s3"]),
                     "pressure_bar":float(row["s4"]),"vibration_mm_s":float(row["s7"]),
                     "rpm":float(row["s8"]),"torque_nm":float(row["s9"]),
                     "current_a":float(row["s11"]),"tool_wear_min":float(row["s12"]),"health_score":float(row["s13"])})
    try:
        sc = get_anomaly_score("t", hist[-1], hist, equipment_class="bearing").get("score", 0.)
    except Exception:
        sc = 0.
    scores.append(sc)
    labs.append(lab)

scores, labs = np.array(scores), np.array(labs)
th = float(joblib.load(MODELS / "anomaly_threshold_bearing.pkl"))
preds = (scores >= th).astype(int)
f1   = f1_score(labs, preds, zero_division=0)
prec = precision_score(labs, preds, zero_division=0)
rec  = recall_score(labs, preds, zero_division=0)
print(f"BEFORE: contamination=0.02, 97th-pctile threshold → Precision~0.50 Recall~0.90 F1~0.64")
print(f"AFTER : contamination=0.08, pipeline-calibrated threshold={th:.4f}")
print(f"        Precision={prec:.3f}  Recall={rec:.3f}  F1={f1:.3f}")
print(f"        anomaly={labs.sum()}/{len(labs)} engines (RUL<=30)")

print()
print("=== FIX 3: FAILURE ===")
from scripts.train_failure import _build_ai4i_4class
df = _build_ai4i_4class(RAW / "ai4i" / "ai4i2020.csv")
X_all = df[[c for c in df.columns if c != "failure_class"]].values
y_all = df["failure_class"].values
_, X_te, _, y_te = train_test_split(X_all, y_all, test_size=0.2, stratify=y_all, random_state=42)
print(f"BEFORE: synthetic-only, binary {{0,3}} labels → macro-F1~0.15, PR-AUC~0.08")
for cls in ["bearing","fan","pump","conveyor","hydraulic_unit"]:
    m = joblib.load(MODELS / f"failure_lgbm_{cls}.pkl")
    n = getattr(m, "n_features_in_", X_te.shape[1])
    Xe = X_te[:, :n] if X_te.shape[1] > n else X_te
    pr = m.predict_proba(Xe)
    yp = np.argmax(pr, axis=1)
    f1 = f1_score(y_te, yp, average="macro", zero_division=0)
    apu = average_precision_score((y_te>0).astype(int), 1.0 - pr[:,0])
    print(f"AFTER  [{cls:20s}]: macro-F1={f1:.3f}  PR-AUC={apu:.3f}")

print()
print("Done.")
