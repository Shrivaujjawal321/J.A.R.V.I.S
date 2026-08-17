"""
03_threshold_sweep.py — Score-aware threshold sweep for V6 standalone
Sweeps all unique OOF probability thresholds to maximize (R+P)/2 * 100.
Outputs: chosen_threshold_v6.json, expected_submission_v6.csv, threshold_sweep_v6.csv
"""

import json
import numpy as np
import pandas as pd
from pathlib import Path

V6_DIR = Path("data/hackathons/tata-steel-2026/round_1/build_v6")

# Load OOF and test
oof_df   = pd.read_parquet(V6_DIR / "oof_v6.parquet")
test_df  = pd.read_parquet(V6_DIR / "test_meta_v6.parquet")

y_true   = oof_df["Y"].values.astype(int)
oof_prob = oof_df["oof_v6"].values
test_prob= test_df["test_meta_v6"].values

print(f"OOF shape: {oof_df.shape}")
print(f"Test shape: {test_df.shape}")
print(f"OOF prob range: [{oof_prob.min():.4f}, {oof_prob.max():.4f}]")

# ─── Threshold sweep ──────────────────────────────────────────────────────────
thresholds = np.unique(oof_prob)
results = []

for t in thresholds:
    preds = (oof_prob >= t).astype(int)
    tp = int(((preds == 1) & (y_true == 1)).sum())
    fp = int(((preds == 1) & (y_true == 0)).sum())
    fn = int(((preds == 0) & (y_true == 1)).sum())
    recall    = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    score     = (recall + precision) / 2 * 100
    results.append({
        "threshold": float(t), "score": float(score),
        "recall": float(recall), "precision": float(precision),
        "tp": tp, "fp": fp, "fn": fn,
        "n_pos_pred": int(preds.sum()),
    })

sweep_df = pd.DataFrame(results).sort_values("score", ascending=False)
sweep_df.to_csv(V6_DIR / "threshold_sweep_v6.csv", index=False)

best = sweep_df.iloc[0]
T    = float(best["threshold"])
score= float(best["score"])
R    = float(best["recall"])
P    = float(best["precision"])

print(f"\n=== V6 Standalone Threshold ===")
print(f"  Best T     : {T:.6f}")
print(f"  OOF Score  : {score:.4f}  (R={R:.4f}, P={P:.4f})")
print(f"  Positives  : {int(best['n_pos_pred'])} predicted / {int(y_true.sum())} actual")

# Save threshold metadata
chosen = {
    "chosen_threshold_v6": T,
    "oof_score_v6": score,
    "recall_at_T": R,
    "precision_at_T": P,
    "n_pos_oof": int(best["n_pos_pred"]),
    "n_pos_test": int((test_prob >= T).sum()),
    "global_oof_auc": None,  # filled by training script
}
with open(V6_DIR / "chosen_threshold_v6.json", "w") as f:
    json.dump(chosen, f, indent=2)

# Generate test submission
test_preds = (test_prob >= T).astype(int)
sub_df = pd.DataFrame({
    "CoilID": test_df["CoilID"].values,
    "Y":      test_preds,
})
sub_df.to_csv(V6_DIR / "expected_submission_v6.csv", index=False)

print(f"  Test positives: {test_preds.sum()} / {len(test_preds)}")
print(f"  Saved: expected_submission_v6.csv, chosen_threshold_v6.json")
print("03_threshold_sweep.py DONE")
