"""
Step 5 — Final predictions on test set.
- Average 5 fold models
- Apply chosen threshold
- Generate submission CSV (339 rows × 2 cols)
- Save raw probabilities for v2 iteration
"""

import sys
sys.path.insert(0, "/home/ujjwal/Documents/J.A.R.V.I.S./data/hackathons/tata-steel-2026/round_1/ml_harness")

import json
import warnings
import numpy as np
import pandas as pd
import lightgbm as lgb
from pathlib import Path

from utils.submission import write_submission

warnings.filterwarnings("ignore")

# ── Paths ─────────────────────────────────────────────────────────────────────
DATA_DIR  = Path("/home/ujjwal/Documents/J.A.R.V.I.S./data set of tata steel/dataset")
OUT_DIR   = Path("/home/ujjwal/Documents/J.A.R.V.I.S./data/hackathons/tata-steel-2026/round_1/build_v1")
MODEL_DIR = OUT_DIR / "models"

# ── Load ──────────────────────────────────────────────────────────────────────
test_eng  = pd.read_parquet(OUT_DIR / "test_engineered.parquet")
feat_info = json.loads((OUT_DIR / "feature_list.json").read_text())
thr_doc   = json.loads((OUT_DIR / "chosen_threshold.json").read_text())
sample    = pd.read_csv(DATA_DIR / "sample_submission.csv")
test_orig = pd.read_csv(DATA_DIR / "test.csv")

feature_cols = feat_info["feature_cols"]
threshold    = thr_doc["chosen_threshold"]

X_test = test_eng[feature_cols].values
coil_ids_test = test_eng["CoilID"].values

print(f"Test rows   : {len(X_test)}")
print(f"Features    : {len(feature_cols)}")
print(f"Threshold   : {threshold:.4f}")
print(f"Criteria met: {thr_doc['criteria_met']}")
print()

# ── Load 5 fold models and predict ────────────────────────────────────────────
fold_probas = []
for i in range(5):
    model_path = MODEL_DIR / f"fold_{i}.lgb"
    model = lgb.Booster(model_file=str(model_path))
    proba = model.predict(X_test)
    fold_probas.append(proba)
    print(f"  Fold {i+1} — predicted {(proba >= threshold).sum()} positives (mean proba={proba.mean():.4f})")

# Average ensemble
test_proba_mean = np.mean(fold_probas, axis=0)
test_proba_std  = np.std(fold_probas, axis=0)

print(f"\nEnsemble mean proba — min={test_proba_mean.min():.4f}, max={test_proba_mean.max():.4f}, mean={test_proba_mean.mean():.4f}")
print(f"Ensemble std         — mean={test_proba_std.mean():.4f} (model agreement)")

# ── Apply threshold ────────────────────────────────────────────────────────────
test_pred = (test_proba_mean >= threshold).astype(int)

n_pred_pos = test_pred.sum()
n_pred_neg = (test_pred == 0).sum()
pred_rate  = n_pred_pos / len(test_pred)

print(f"\nPredictions:")
print(f"  Y=0: {n_pred_neg}")
print(f"  Y=1: {n_pred_pos}")
print(f"  Predicted positive rate: {pred_rate:.2%}")
print(f"  (Train positive rate was: 4.88%)")

# ── Validate CoilID alignment ──────────────────────────────────────────────────
# test_eng was sorted by CoilID in Step 2 — confirm match with test.csv sorted
test_orig_sorted = test_orig.sort_values("CoilID")
assert list(test_eng["CoilID"].values) == list(test_orig_sorted["CoilID"].values), \
    "CoilID mismatch between engineered test and original test!"
print("\nCoilID alignment: PASSED")

# ── Build submission dataframe ────────────────────────────────────────────────
# Must match sample_submission.csv format: CoilID, Y
# But we need the original CoilID order from test.csv (not sorted)
# Actually — let's align to the ORIGINAL test.csv order
test_orig_coil_order = pd.read_csv(DATA_DIR / "test.csv")["CoilID"].values

# Build coilid → pred map
coilid_to_pred  = dict(zip(coil_ids_test, test_pred))
coilid_to_proba = dict(zip(coil_ids_test, test_proba_mean))

# Apply in original test.csv order
y_submission = [coilid_to_pred[c] for c in test_orig_coil_order]
p_submission = [coilid_to_proba[c] for c in test_orig_coil_order]

submission_df = pd.DataFrame({
    "CoilID": test_orig_coil_order,
    "Y": y_submission,
})

print(f"\nSubmission shape: {submission_df.shape}")
print(f"Y=1 count: {submission_df['Y'].sum()}")
print(f"Y=0 count: {(submission_df['Y'] == 0).sum()}")
print(f"Nulls: {submission_df.isnull().sum().sum()}")

# ── Validate row count (can't use write_submission validator since sample has only 10 rows) ──
assert len(submission_df) == len(test_orig_coil_order), f"Row count mismatch: {len(submission_df)} vs {len(test_orig_coil_order)}"
assert list(submission_df.columns) == ["CoilID", "Y"], f"Column mismatch: {list(submission_df.columns)}"
assert submission_df["Y"].isnull().sum() == 0, "Nulls in Y column!"

# Check CoilIDs match
expected_coils = set(test_orig_coil_order)
actual_coils   = set(submission_df["CoilID"])
assert expected_coils == actual_coils, f"CoilID set mismatch!"
print("Validation: PASSED (339 rows, 2 cols, no nulls, all CoilIDs present)")

# ── Save ──────────────────────────────────────────────────────────────────────
submission_path = OUT_DIR / "expected_submission.csv"
submission_df.to_csv(submission_path, index=False)
print(f"\nSubmission saved: {submission_path}")

# Raw probabilities for v2
proba_df = pd.DataFrame({
    "CoilID": test_orig_coil_order,
    "proba": p_submission,
    "Y_pred": y_submission,
})
proba_df.to_parquet(OUT_DIR / "test_probas.parquet", index=False)
print(f"Raw probas saved: {OUT_DIR / 'test_probas.parquet'}")

# Quick preview
print("\n--- Submission preview (first 10 rows) ---")
print(submission_df.head(10).to_string(index=False))
print(f"\n--- Rows predicted as DEFECT (Y=1): {submission_df[submission_df['Y']==1]['CoilID'].tolist()[:20]} ---")
print()
print("Step 5 complete.")
