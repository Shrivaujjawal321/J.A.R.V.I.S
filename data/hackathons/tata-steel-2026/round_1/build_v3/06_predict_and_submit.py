"""
Step 6: Generate Final Submission
- Apply chosen threshold to test meta probas
- Validate format (339 rows, CoilID + Y)
- Generate expected_submission.csv
- Create submission_v3.zip
"""

import os
import sys
import json
import zipfile
import shutil
import numpy as np
import pandas as pd

BASE = "/home/ujjwal/Documents/J.A.R.V.I.S./data/hackathons/tata-steel-2026/round_1"
V3   = BASE + "/build_v3"

print("Loading threshold and test probas...")

with open(V3 + "/chosen_threshold_v3.json") as f:
    thresh_info = json.load(f)

T_chosen = thresh_info["chosen_threshold"]
print(f"  Chosen threshold: {T_chosen:.4f}")
print(f"  Predicted LB score: {thresh_info['predicted_lb_score']:.2f}")
print(f"  Strategy: {thresh_info['strategy']}")

test_meta = pd.read_parquet(V3 + "/test_meta_probas.parquet")
print(f"\nTest meta probas shape: {test_meta.shape}")
print(f"  CoilID range: {test_meta['CoilID'].min()} - {test_meta['CoilID'].max()}")
print(f"  Proba range:  [{test_meta['test_proba'].min():.4f}, {test_meta['test_proba'].max():.4f}]")

# ── Apply threshold ───────────────────────────────────────────────────────────
test_meta["Y"] = (test_meta["test_proba"] >= T_chosen).astype(int)

n_pos  = test_meta["Y"].sum()
n_tot  = len(test_meta)
pos_rt = n_pos / n_tot * 100
print(f"\nTest predictions:")
print(f"  Positive rate: {n_pos}/{n_tot} = {pos_rt:.1f}%")
print(f"  V2 positive rate was 39.5% (134/339)")
print(f"  Expected: 3-15% (5-50 defects predicted)")

if pos_rt > 40:
    print("  WARNING: Positive rate >40% — still very high, may hurt precision")
elif pos_rt < 1:
    print("  WARNING: Positive rate <1% — too conservative, recall will suffer")
else:
    print("  OK: Positive rate in reasonable range")

# ── Build submission CSV ──────────────────────────────────────────────────────
submission = test_meta[["CoilID", "Y"]].copy()
submission["Y"] = submission["Y"].astype(int)

# Validate
assert len(submission) == 339, f"Expected 339 rows, got {len(submission)}"
assert set(submission.columns) == {"CoilID", "Y"}, f"Wrong columns: {submission.columns.tolist()}"
assert submission["Y"].isin([0, 1]).all(), "Y contains non-binary values"

print(f"\nSubmission shape: {submission.shape}")
print(f"Y value counts:\n{submission['Y'].value_counts().to_string()}")

submission.to_csv(V3 + "/expected_submission.csv", index=False)
print("\nSaved expected_submission.csv")

# ── Also save multi-threshold submission variants ─────────────────────────────
comp = thresh_info["comparison"]
for strat, info in comp.items():
    T_var = info["threshold"]
    preds = (test_meta["test_proba"] >= T_var).astype(int)
    sub_var = test_meta[["CoilID"]].copy()
    sub_var["Y"] = preds
    fname = V3 + f"/submission_{strat}.csv"
    sub_var.to_csv(fname, index=False)
    n_v = preds.sum()
    print(f"Saved {strat}: threshold={T_var:.3f}, n_pos={n_v} ({n_v/n_tot*100:.1f}%)")

# ── Create submission_v3.zip ──────────────────────────────────────────────────
zip_path = V3 + "/submission_v3.zip"
with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
    # Main submission CSV
    zf.write(V3 + "/expected_submission.csv", "expected_submission.csv")

    # Threshold info
    zf.write(V3 + "/chosen_threshold_v3.json", "chosen_threshold_v3.json")

    # Approach doc (will be written by run_all or separately)
    approach_path = V3 + "/approach_v3.md"
    if os.path.exists(approach_path):
        zf.write(approach_path, "approach_v3.md")

    # Notebook if exists
    nb_path = V3 + "/solution.ipynb"
    if os.path.exists(nb_path):
        zf.write(nb_path, "solution.ipynb")

print(f"\nSaved submission_v3.zip")
print(f"  Contents:")
with zipfile.ZipFile(zip_path) as zf:
    for name in zf.namelist():
        info = zf.getinfo(name)
        print(f"    {name}  ({info.file_size/1024:.1f} KB)")

# ── Print final summary ───────────────────────────────────────────────────────
print(f"\n{'='*60}")
print("V3 SUBMISSION SUMMARY")
print(f"{'='*60}")
print(f"  Algorithm:          Stacking Ensemble (LGB+XGB+CatBoost) + LR meta")
print(f"  SHAP features:      Top 30 + poly terms")
print(f"  Calibration:        Platt scaling (sigmoid)")
print(f"  Threshold strategy: Maximize (Recall+Precision)/2")
print(f"  Chosen threshold:   {T_chosen:.4f}")
print(f"  Test positive rate: {pos_rt:.1f}%  (v2 was 39.5%)")
print(f"  Predicted LB score: {thresh_info['predicted_lb_score']:.2f}  (v2 = 50.19)")
print(f"  Delta vs V2:        {thresh_info['delta_vs_v2']:+.2f}")
print(f"  Top 10 target:      70.0  ->  {'LIKELY' if thresh_info['predicted_lb_score'] >= 70 else 'NEEDS V4'}")
print(f"{'='*60}")

print("\n=== Step 6 COMPLETE ===")
