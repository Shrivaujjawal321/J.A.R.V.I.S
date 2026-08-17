"""
Step 1 — Load & Verify
- Shape / class balance / missing counts
- CoilID sequentiality test (lag feature engineering validity)
- Saves notes_step1.md
"""

import sys
import os
sys.path.insert(0, "/home/ujjwal/Documents/J.A.R.V.I.S./data/hackathons/tata-steel-2026/round_1/ml_harness")

import pandas as pd
import numpy as np
from scipy import stats
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path

from utils.seed import set_seed

set_seed(42)

# ── Paths ─────────────────────────────────────────────────────────────────────
DATA_DIR = Path("/home/ujjwal/Documents/J.A.R.V.I.S./data set of tata steel/dataset")
OUT_DIR  = Path("/home/ujjwal/Documents/J.A.R.V.I.S./data/hackathons/tata-steel-2026/round_1/build_v1")
FIG_DIR  = OUT_DIR / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)

# ── Load ──────────────────────────────────────────────────────────────────────
train  = pd.read_csv(DATA_DIR / "train.csv")
test   = pd.read_csv(DATA_DIR / "test.csv")
sample = pd.read_csv(DATA_DIR / "sample_submission.csv")

print("=" * 60)
print("SHAPES")
print(f"  train  : {train.shape}")
print(f"  test   : {test.shape}")
print(f"  sample : {sample.shape}")
print()

# ── Class balance ─────────────────────────────────────────────────────────────
y = train["Y"]
vc = y.value_counts()
print("CLASS BALANCE (train Y)")
print(f"  Y=0: {vc[0]}  ({vc[0]/len(y)*100:.2f}%)")
print(f"  Y=1: {vc[1]}  ({vc[1]/len(y)*100:.2f}%)")
print(f"  Imbalance ratio: {vc[0]/vc[1]:.1f}:1")
print()

# ── Missing counts ─────────────────────────────────────────────────────────────
missing_train = train.isnull().sum()
missing_test  = test.isnull().sum()
missing_train = missing_train[missing_train > 0]
missing_test  = missing_test[missing_test > 0]

print("MISSING VALUES — TRAIN")
for col, cnt in missing_train.items():
    print(f"  {col}: {cnt} ({cnt/len(train)*100:.2f}%)")
print()

print("MISSING VALUES — TEST")
for col, cnt in missing_test.items():
    print(f"  {col}: {cnt} ({cnt/len(test)*100:.2f}%)")
print()

# ── Sample submission format ──────────────────────────────────────────────────
print("SAMPLE SUBMISSION")
print(f"  columns  : {list(sample.columns)}")
print(f"  rows     : {len(sample)}")
print(f"  test rows: {len(test)}")
print(f"  submission must be: {len(test)} rows × {len(sample.columns)} cols")
print()

# ── CoilID sequentiality test ─────────────────────────────────────────────────
print("=" * 60)
print("COILID SEQUENTIALITY ANALYSIS")
print()

# Sort train by CoilID and examine X13 (top feature)
train_sorted = train.sort_values("CoilID").reset_index(drop=True)

coil_ids = train_sorted["CoilID"].values
x13      = train_sorted["X13"].values

# 1. Check if CoilIDs are monotonically increasing integers or have gaps
coil_diffs = np.diff(coil_ids)
print(f"  CoilID range       : {coil_ids.min()} → {coil_ids.max()}")
print(f"  CoilID diffs — min : {coil_diffs.min():.0f}")
print(f"  CoilID diffs — max : {coil_diffs.max():.0f}")
print(f"  CoilID diffs — mean: {coil_diffs.mean():.2f}")
print(f"  Unique diff values : {len(np.unique(coil_diffs))}")
print()

# 2. Lag-1 autocorrelation of X13
x13_valid = x13[~np.isnan(x13)]
if len(x13_valid) > 2:
    lag1_corr = np.corrcoef(x13_valid[:-1], x13_valid[1:])[0, 1]
    lag2_corr = np.corrcoef(x13_valid[:-2], x13_valid[2:])[0, 1]
    print(f"  X13 lag-1 autocorrelation: {lag1_corr:.4f}")
    print(f"  X13 lag-2 autocorrelation: {lag2_corr:.4f}")

# 3. Spearman of CoilID (sorted) vs X13 — do they covary?
spear_r, spear_p = stats.spearmanr(coil_ids, x13)
print(f"  Spearman(CoilID, X13): r={spear_r:.4f}, p={spear_p:.4f}")

# 4. Check if defect coils cluster by CoilID (are consecutive defects common?)
defect_coil_ids = sorted(train_sorted[train_sorted["Y"] == 1]["CoilID"].values)
if len(defect_coil_ids) > 1:
    defect_gaps = np.diff(defect_coil_ids)
    small_gap = (defect_gaps <= 10).sum()
    print(f"\n  Defect coil IDs — {len(defect_coil_ids)} defects")
    print(f"  Gaps between consecutive defect CoilIDs — min: {defect_gaps.min():.0f}, max: {defect_gaps.max():.0f}, mean: {defect_gaps.mean():.1f}")
    print(f"  Defect pairs with gap ≤ 10 CoilIDs: {small_gap} (out of {len(defect_gaps)})")

# 5. Plot X13 vs CoilID position, coloring defects
fig, axes = plt.subplots(2, 1, figsize=(14, 8))

axes[0].scatter(
    range(len(train_sorted)),
    train_sorted["X13"],
    c=train_sorted["Y"].map({0: "steelblue", 1: "red"}),
    s=10, alpha=0.6
)
axes[0].set_xlabel("Row index (sorted by CoilID)")
axes[0].set_ylabel("X13 value")
axes[0].set_title("X13 vs CoilID position — Blue=normal, Red=defect")

# Zoom to defect neighborhoods
defect_idx = train_sorted[train_sorted["Y"] == 1].index.tolist()
x10 = train_sorted["X10"].values
axes[1].scatter(
    range(len(train_sorted)),
    train_sorted["X36"],
    c=train_sorted["Y"].map({0: "steelblue", 1: "red"}),
    s=10, alpha=0.6
)
axes[1].set_xlabel("Row index (sorted by CoilID)")
axes[1].set_ylabel("X36 value")
axes[1].set_title("X36 (cooling/tension — drops on defect) vs CoilID position")

plt.tight_layout()
plt.savefig(FIG_DIR / "coilid_sequentiality.png", dpi=120, bbox_inches="tight")
plt.close()
print(f"\n  Figure saved: {FIG_DIR / 'coilid_sequentiality.png'}")

# ── Decision: lag features valid? ─────────────────────────────────────────────
print()
print("=" * 60)
print("VERDICT: IS LAG FEATURE ENGINEERING VALID?")
print()

lag_valid = False

# Criteria: strong lag-1 autocorr OR defect clustering OR Spearman significant
if abs(lag1_corr) > 0.3:
    print(f"  VALID — X13 lag-1 autocorr = {lag1_corr:.4f} > 0.3 threshold")
    lag_valid = True
elif small_gap >= 5:
    print(f"  VALID — {small_gap} defect pairs within 10 CoilIDs = temporal clustering")
    lag_valid = True
elif abs(spear_r) > 0.1 and spear_p < 0.05:
    print(f"  VALID — Spearman(CoilID, X13) = {spear_r:.4f}, p={spear_p:.4f}")
    lag_valid = True
else:
    print(f"  SKIP — No strong evidence of temporal ordering")
    print(f"         lag1_corr={lag1_corr:.4f}, small_gap={small_gap}, Spearman r={spear_r:.4f} p={spear_p:.4f}")

print()

# ── Save notes ────────────────────────────────────────────────────────────────
notes = f"""# Step 1 Notes — Load & Verify

## Data shapes
- train : {train.shape}
- test  : {test.shape}
- sample: {sample.shape}
- Submission must be: {len(test)} rows × {len(sample.columns)} cols

## Class balance
- Y=0: {vc[0]} ({vc[0]/len(y)*100:.2f}%)
- Y=1: {vc[1]} ({vc[1]/len(y)*100:.2f}%)
- Imbalance: {vc[0]/vc[1]:.1f}:1

## Missing values (train)
{chr(10).join(f"- {col}: {cnt} ({cnt/len(train)*100:.2f}%)" for col, cnt in missing_train.items()) if len(missing_train) else "- None"}

## Missing values (test)
{chr(10).join(f"- {col}: {cnt} ({cnt/len(test)*100:.2f}%)" for col, cnt in missing_test.items()) if len(missing_test) else "- None"}

## CoilID sequentiality
- Range: {coil_ids.min()} → {coil_ids.max()}
- Diffs mean: {coil_diffs.mean():.2f}
- X13 lag-1 autocorrelation: {lag1_corr:.4f}
- X13 lag-2 autocorrelation: {lag2_corr:.4f}
- Spearman(CoilID, X13): r={spear_r:.4f}, p={spear_p:.4f}
- Defect clustering (gaps ≤ 10): {small_gap} pairs

## Verdict: Lag features valid?
{'YES — build lag features in Step 2' if lag_valid else 'NO — skip lag features in Step 2 (no reliable sequential ordering)'}

## Key observations
- Top features confirmed: X13, X10, X36, X34 (AUC 0.77–0.83)
- X15 has {missing_train.get("X15", 0)} missing train values ({missing_train.get("X15", 0)/len(train)*100:.2f}%) — use KNN imputation
- Class imbalance is severe — scale_pos_weight = {vc[0]/vc[1]:.1f}
"""

notes_path = OUT_DIR / "notes_step1.md"
notes_path.write_text(notes)
print(f"Notes saved: {notes_path}")

# Save lag verdict for use in step 2
import json
verdict = {"lag_features_valid": lag_valid, "lag1_autocorr": float(lag1_corr), "spearman_r": float(spear_r), "spearman_p": float(spear_p)}
(OUT_DIR / "lag_verdict.json").write_text(json.dumps(verdict, indent=2))
print(f"Lag verdict saved: {OUT_DIR / 'lag_verdict.json'}")
print()
print("Step 1 complete.")
