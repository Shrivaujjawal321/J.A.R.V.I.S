"""
Step 4: Generate test predictions + submission CSV.
Key fix: test_engineered parquet is sorted by CoilID (for lag features),
but test.csv has original unordered CoilIDs. We merge on CoilID to
produce submission in the original test.csv order.
Threshold selected from OOF analysis (best recall@P>=0.90, or best precision@R>=1.0).
Run: .venv/bin/python data/hackathons/tata-steel-2026/round_1/build_v2/04_predict_submit.py
"""
import json
import numpy as np
import pandas as pd
import lightgbm as lgb
from sklearn.metrics import roc_auc_score

V2_DIR  = "data/hackathons/tata-steel-2026/round_1/build_v2"
RAW_DIR = "data set of tata steel/dataset"

print("=" * 60)
print("STEP 4: Test predictions + submission (CoilID-aware)")
print("=" * 60)

test_eng  = pd.read_parquet(f"{V2_DIR}/test_v2.parquet")
test_raw  = pd.read_csv(f"{RAW_DIR}/test.csv")
feat_meta = json.load(open(f"{V2_DIR}/feature_list_v2.json"))
thr_meta  = json.load(open(f"{V2_DIR}/chosen_threshold_v2.json"))

feat_cols = [c for c in feat_meta["features"] if c in test_eng.columns]

print(f"test_eng shape: {test_eng.shape}  (sorted by CoilID)")
print(f"test_raw shape: {test_raw.shape}   (original order)")
print(f"Features: {len(feat_cols)}")

# ─── Predict with all 5 folds ─────────────────────────────────────────────────
X_test = test_eng[feat_cols].values.astype(np.float64)
test_probas = []
print("\nLoading fold models...")
for fold_idx in range(5):
    model = lgb.Booster(model_file=f"{V2_DIR}/models/fold_{fold_idx}.lgb")
    prob = model.predict(X_test)
    test_probas.append(prob)
    print(f"  Fold {fold_idx+1}: median={np.median(prob):.4f}  max={prob.max():.4f}")

ensemble_proba = np.mean(test_probas, axis=0)

# ─── Map to original test.csv CoilID order ────────────────────────────────────
# test_eng is sorted by CoilID; merge on CoilID to get original test.csv order
proba_df = pd.DataFrame({"CoilID": test_eng["CoilID"].values, "proba": ensemble_proba})
merged   = test_raw[["CoilID"]].merge(proba_df, on="CoilID", how="left")

if merged["proba"].isnull().any():
    print(f"[ERROR] {merged['proba'].isnull().sum()} test rows couldn't be matched!")
    raise ValueError("CoilID merge failed")

ordered_proba = merged["proba"].values
print(f"\nEnsemble proba (in test.csv order):")
print(f"  min={ordered_proba.min():.6f}  p25={np.percentile(ordered_proba,25):.6f}  "
      f"median={np.median(ordered_proba):.4f}  max={ordered_proba.max():.4f}")

# ─── Select submission threshold ─────────────────────────────────────────────
# OOF says: criteria NOT met at any threshold
# Best strategy for submission: use threshold that targets ~5% positive rate
# (matching expected test defect rate), which balances recall vs precision
# 
# OOF proba at 0.200 gives P=40%, R=35% — too conservative
# We use threshold=0.10 for submission (OOF: 26/339=7.7%) for honest estimate
# Override available via thr_meta if criteria were met
if thr_meta.get("criteria_met"):
    CHOSEN_THR = thr_meta["chosen_threshold"]
    print(f"\nUsing OOF-optimized threshold (criteria MET): {CHOSEN_THR:.4f}")
else:
    # Use best recall-at-P>=0.10 (honest submission, not all-positive garbage)
    # OOF: at thr=0.001 -> Recall=0.894, Prec=0.105
    # That's our best honest OOF recall point
    CHOSEN_THR = 0.001
    print(f"\nCriteria NOT met on OOF. Using thr={CHOSEN_THR} for submission:")
    print(f"  OOF: Recall=0.894 (59/66), Precision=0.105")
    print(f"  Rationale: Best recall with precision > 10% (better than all-positive garbage)")

test_preds = (ordered_proba >= CHOSEN_THR).astype(int)
pos_count  = int(test_preds.sum())
pos_rate   = 100 * pos_count / len(test_preds)

print(f"\nTest predictions @ threshold={CHOSEN_THR}:")
print(f"  Positive: {pos_count} / {len(test_preds)} ({pos_rate:.1f}%)")
print(f"  V1: 157/339 (46.3%)  -> V2: {pos_count}/339 ({pos_rate:.1f}%)")

if pos_rate > 30:
    print(f"[WARN] Still over-flagging ({pos_rate:.1f}%)")
elif pos_rate > 15:
    print(f"[NOTE] Elevated positive rate ({pos_rate:.1f}%) vs expected ~5%")
else:
    print(f"[OK]  Reasonable positive rate ({pos_rate:.1f}%)")

# ─── Build and validate submission ────────────────────────────────────────────
submission = pd.DataFrame({
    "CoilID": test_raw["CoilID"].values,
    "Y":      test_preds,
})
assert len(submission) == 339, f"Expected 339 rows, got {len(submission)}"
assert submission.isnull().sum().sum() == 0, "Nulls in submission!"
assert set(submission["Y"].unique()).issubset({0,1}), "Y values not 0/1!"
print(f"\nSubmission validated: shape={submission.shape}  Y dist={submission['Y'].value_counts().to_dict()}")

# ─── Save ─────────────────────────────────────────────────────────────────────
submission.to_csv(f"{V2_DIR}/expected_submission.csv", index=False)

prob_export = pd.DataFrame({
    "CoilID": test_raw["CoilID"].values,
    "proba":  ordered_proba,
    "Y_pred": test_preds,
})
prob_export.to_parquet(f"{V2_DIR}/test_probas_v2.parquet", index=False)

# Save updated threshold info
thr_meta["submission_threshold"] = float(CHOSEN_THR)
thr_meta["submission_pos_count"] = int(pos_count)
thr_meta["submission_pos_rate_pct"] = float(pos_rate)
json.dump(thr_meta, open(f"{V2_DIR}/chosen_threshold_v2.json","w"), indent=2)

print(f"Saved expected_submission.csv + test_probas_v2.parquet")
print("Step 4 DONE.")
