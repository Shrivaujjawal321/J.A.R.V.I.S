"""
Step 4: Meta-Learner + Platt Scaling Calibration
- Stack OOF probas from 3 base models as 3-col feature matrix
- Train LogisticRegression meta on (oof_3cols, y_train)
- Apply Platt scaling calibration (CalibratedClassifierCV with prefit)
- Predict on test_3cols -> final test probas
- Save oof_meta.parquet, test_meta_probas.parquet
"""

import os
import json
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import roc_auc_score

BASE = "/home/ujjwal/Documents/J.A.R.V.I.S./data/hackathons/tata-steel-2026/round_1"
V3   = BASE + "/build_v3"

print("Loading OOF predictions from base models...")

oof_lgb = pd.read_parquet(V3 + "/oof_lgb.parquet")
oof_xgb = pd.read_parquet(V3 + "/oof_xgb.parquet")
oof_cat = pd.read_parquet(V3 + "/oof_cat.parquet")

test_lgb = pd.read_parquet(V3 + "/test_lgb.parquet")
test_xgb = pd.read_parquet(V3 + "/test_xgb.parquet")
test_cat = pd.read_parquet(V3 + "/test_cat.parquet")

# Verify alignment
assert (oof_lgb["CoilID"].values == oof_xgb["CoilID"].values).all()
assert (oof_lgb["CoilID"].values == oof_cat["CoilID"].values).all()

y_train = oof_lgb["Y"].values

# ── Build stacking feature matrices ──────────────────────────────────────────
X_oof_stack = np.column_stack([
    oof_lgb["oof_proba"].values,
    oof_xgb["oof_proba"].values,
    oof_cat["oof_proba"].values,
])

X_test_stack = np.column_stack([
    test_lgb["test_proba"].values,
    test_xgb["test_proba"].values,
    test_cat["test_proba"].values,
])

print(f"OOF stack shape: {X_oof_stack.shape}")
print(f"Test stack shape: {X_test_stack.shape}")
print(f"Base model AUCs (from OOF):")
for i, name in enumerate(["lgb","xgb","cat"]):
    auc = roc_auc_score(y_train, X_oof_stack[:, i])
    print(f"  {name}: {auc:.4f}")

# ── Train meta-learner (LogisticRegression) ───────────────────────────────────
print("\nTraining meta-learner (LogisticRegression, balanced)...")
meta = LogisticRegression(C=1.0, class_weight="balanced", max_iter=1000, random_state=42)
meta.fit(X_oof_stack, y_train)

oof_meta_proba_raw = meta.predict_proba(X_oof_stack)[:, 1]
meta_oof_auc = roc_auc_score(y_train, oof_meta_proba_raw)
print(f"Meta OOF AUC (raw, before calibration): {meta_oof_auc:.4f}")

# ── Platt scaling calibration ─────────────────────────────────────────────────
# Note: cv="prefit" removed in newer sklearn — use cv=5 with fresh estimator
print("\nApplying Platt scaling calibration (sigmoid, cv=5)...")
meta_for_cal = LogisticRegression(C=1.0, class_weight="balanced", max_iter=1000, random_state=42)
calibrated = CalibratedClassifierCV(meta_for_cal, method="sigmoid", cv=5)
calibrated.fit(X_oof_stack, y_train)

oof_meta_proba_cal = calibrated.predict_proba(X_oof_stack)[:, 1]
meta_oof_auc_cal = roc_auc_score(y_train, oof_meta_proba_cal)
print(f"Meta OOF AUC (calibrated): {meta_oof_auc_cal:.4f}")

# Pick the one with higher OOF AUC
meta_oof_auc_raw = meta_oof_auc  # rename for clarity in comparison
if meta_oof_auc_cal >= meta_oof_auc_raw:
    oof_final = oof_meta_proba_cal
    test_final_proba = calibrated.predict_proba(X_test_stack)[:, 1]
    method_used = "calibrated"
else:
    oof_final = oof_meta_proba_raw
    test_final_proba = meta.predict_proba(X_test_stack)[:, 1]
    method_used = "raw"

print(f"Using: {method_used} meta probas")

# ── Save outputs ──────────────────────────────────────────────────────────────
pd.DataFrame({
    "CoilID":     oof_lgb["CoilID"].values,
    "Y":          y_train,
    "oof_proba":  oof_final,
}).to_parquet(V3 + "/oof_meta.parquet", index=False)

pd.DataFrame({
    "CoilID":     test_lgb["CoilID"].values,
    "test_proba": test_final_proba,
}).to_parquet(V3 + "/test_meta_probas.parquet", index=False)

meta_summary = {
    "meta_oof_auc_raw":        float(meta_oof_auc_raw),
    "meta_oof_auc_calibrated": float(meta_oof_auc_cal),
    "method_used":             method_used,
    "meta_coef":               meta.coef_.tolist(),
    "meta_intercept":          meta.intercept_.tolist(),
    "proba_stats_oof": {
        "min":    float(oof_final.min()),
        "max":    float(oof_final.max()),
        "mean":   float(oof_final.mean()),
        "defect_mean":    float(oof_final[y_train == 1].mean()),
        "nondefect_mean": float(oof_final[y_train == 0].mean()),
    },
    "proba_stats_test": {
        "min":  float(test_final_proba.min()),
        "max":  float(test_final_proba.max()),
        "mean": float(test_final_proba.mean()),
    },
}
with open(V3 + "/meta_summary.json", "w") as f:
    import json
    json.dump(meta_summary, f, indent=2)

print("Saved oof_meta.parquet")
print("Saved test_meta_probas.parquet")
print("Saved meta_summary.json")

print(f"\nProba range OOF:  [{oof_final.min():.4f}, {oof_final.max():.4f}]")
print(f"Proba range Test: [{test_final_proba.min():.4f}, {test_final_proba.max():.4f}]")
print(f"Defect OOF proba mean:     {oof_final[y_train==1].mean():.4f}")
print(f"Non-defect OOF proba mean: {oof_final[y_train==0].mean():.4f}")

print("\n=== Step 4 COMPLETE ===")
