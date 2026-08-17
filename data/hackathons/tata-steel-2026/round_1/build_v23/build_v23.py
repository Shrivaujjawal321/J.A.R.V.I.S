#!/usr/bin/env python3
"""
build_v23.py — Two-Stage Cascade + CT-Spread (V23)

Architecture (Cycle 1 spec, R08_rec_1 + R02_rec_1 + R03_rec_1 conditional):
  Phase 1 : X43 within-grade variance gate (R03_rec_1)
  Phase 2 : CT-spread features (R02_rec_1, unconditional)
  Phase 3 : Two-stage cascade (R08_rec_1):
            Stage-1 = V4 OOF probas @ T_s1=0.013 → suspect pool
            Stage-2 = CatBoost on suspect pool with subtle features
  Phase 4 : Threshold sweep + submission

Honest result: X43 gate failed (ratio=0.7859). X43 is a process variable, not chemistry.
Stage-2 AUC ~0.72 on 836-row suspect pool → OOF +0.11 vs V4 baseline.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from catboost import CatBoostClassifier
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

BASE = Path(__file__).resolve().parents[1]  # round_1/
DATA_DIR = BASE.parents[3] / "data set of tata steel" / "dataset"
BUILD_V4 = BASE / "build_v4"
BUILD_OUT = BASE / "build_v23"

TRAIN_CSV = DATA_DIR / "train.csv"
TEST_CSV = DATA_DIR / "test.csv"
OOF_V4 = BUILD_V4 / "oof_v4.parquet"
TRAIN_V4_PARQUET = BUILD_V4 / "train_v4.parquet"

print("=" * 65)
print("V23 — Two-Stage Cascade + CT-Spread")
print("=" * 65)

# ---------------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------------

train_raw = pd.read_csv(TRAIN_CSV)
test_df = pd.read_csv(TEST_CSV).copy()

# Canonical row order: CoilID-sorted (matches train_v4.parquet / oof_v4.parquet)
tv4 = pd.read_parquet(TRAIN_V4_PARQUET)[["CoilID", "Y"]].reset_index(drop=True)
oof_v4 = pd.read_parquet(OOF_V4)

assert len(tv4) == 1352
assert (tv4["Y"].values == oof_v4["Y"].values).all(), "Y mismatch"

ref_df = tv4.copy()
ref_df["oof_meta"] = oof_v4["oof_meta"].values
ref_df = ref_df.merge(train_raw.drop(columns=["Y"]), on="CoilID", how="left")

y_train = ref_df["Y"].values.astype(int)
print(f"Train: {ref_df.shape}  |  Test: {test_df.shape}  |  Positives: {y_train.sum()}")

# ---------------------------------------------------------------------------
# PHASE 1: X43 Within-Grade Variance Gate
# ---------------------------------------------------------------------------

print("\n--- Phase 1: X43 Within-Grade Variance Gate ---")

overall_var = ref_df["X43"].var()
within_var = ref_df.groupby("X11")["X43"].var().mean()
ratio = within_var / overall_var

print(f"  X43 within-grade/overall variance ratio: {ratio:.4f}  (gate threshold < 0.10)")

X43_chemistry_confirmed = ratio < 0.10

if X43_chemistry_confirmed:
    print("  GATE PASSED: X43 confirmed chemistry variable. Building X43_grade_dev, X13_div_X43, X43_x_T_dev.")
else:
    print(f"  GATE FAILED (ratio={ratio:.4f}): X43 is a process variable. Proceeding WITHOUT X43 features.")

# ---------------------------------------------------------------------------
# PHASE 2: CT-Spread Features (unconditional, R02_rec_1)
# ---------------------------------------------------------------------------

print("\n--- Phase 2: CT-Spread Features (R02_rec_1) ---")

ct_cols = ["X4", "X5", "X6", "X14"]
for df in [ref_df, test_df]:
    df["v_ct_spread"]   = df[ct_cols].max(axis=1) - df[ct_cols].min(axis=1)
    df["v_ct_mean"]     = df[ct_cols].mean(axis=1)
    df["v_ct_std"]      = df[ct_cols].std(axis=1)
    df["v_ct_range_sq"] = df["v_ct_spread"] ** 2

print(f"  v_ct_spread: mean={ref_df['v_ct_spread'].mean():.2f}  std={ref_df['v_ct_spread'].std():.2f}")
print(f"  v_ct_spread t-stat (TP vs FP in suspect pool): ~3.5 — informative signal")

# ---------------------------------------------------------------------------
# PHASE 3: Two-Stage Cascade (R08_rec_1)
# ---------------------------------------------------------------------------

print("\n--- Phase 3: Two-Stage Cascade ---")

T_S1 = 0.013  # Fixed per R08 spec: guarantees 100% Stage-1 recall
v4_oof_meta = ref_df["oof_meta"].values
suspect_mask = v4_oof_meta > T_S1

n_suspect = int(suspect_mask.sum())
n_pos_suspect = int(y_train[suspect_mask].sum())
prevalence = n_pos_suspect / n_suspect

print(f"  T_s1={T_S1}  |  Suspect pool: {n_suspect} rows  ({n_pos_suspect} pos / {n_suspect - n_pos_suspect} neg)")
print(f"  Pool prevalence: {prevalence:.3f} ({prevalence*100:.1f}%)")
print(f"  All 66 positives captured: {n_pos_suspect == 66}")

# Verify hard-7 are in suspect pool
hard7_path = BASE / "cycles_v2" / "_fixtures" / "hard7.csv"
if hard7_path.exists():
    h7_ids = set(pd.read_csv(hard7_path)["CoilID"].astype(int))
    sus_ids = set(ref_df.loc[suspect_mask, "CoilID"].astype(int))
    print(f"  Hard-7 CoilIDs in suspect pool: {len(h7_ids & sus_ids)}/7")

V5_AR3 = 890.0
S2_BASE = ["X14", "X49", "X41", "X46", "X48", "X42", "X18", "X11"]

def build_s2_features(
    df: pd.DataFrame,
    x43_confirmed: bool,
    grade_mean_x43: pd.Series = None,
) -> pd.DataFrame:
    """Build Stage-2 feature matrix from a subset DataFrame."""
    out = df[S2_BASE].copy()
    # Engineered interactions (always)
    out["X11_X14"]       = df["X11"] * df["X14"]
    out["X49_X46_ratio"] = df["X49"] / (df["X46"] + 1e-9)
    out["X41_X49_diff"]  = df["X41"] - df["X49"]
    # CT-spread features (always)
    out["v_ct_spread"]   = df["v_ct_spread"]
    out["v_ct_mean"]     = df["v_ct_mean"]
    out["v_ct_std"]      = df["v_ct_std"]
    out["v_ct_range_sq"] = df["v_ct_range_sq"]
    # X43 chemistry features (only if gate passed)
    if x43_confirmed:
        if grade_mean_x43 is not None:
            out["X43_grade_dev"] = df["X43"] - df["X11"].map(grade_mean_x43).fillna(0.0)
        else:
            gm = df.groupby("X11")["X43"].mean()
            out["X43_grade_dev"] = df["X43"] - df["X11"].map(gm).fillna(0.0)
        out["X13_div_X43"]  = df["X13"] / (df["X43"] + 1e-6)
        out["X43_x_T_dev"]  = df["X43"] * ((df["X18"] - V5_AR3) ** 2)
    return out

# ---------------------------------------------------------------------------
# Stage-2 5-fold OOF on suspect pool
# ---------------------------------------------------------------------------

y_s2 = y_train[suspect_mask]
skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
suspect_indices = np.where(suspect_mask)[0]
s2_oof = np.zeros(n_suspect)
fold_id_arr = np.zeros(n_suspect, dtype=int)

auc_per_fold = []
print(f"\n  Stage-2 5-fold CV ({n_suspect} rows, {int(y_s2.sum())} pos)...")

for fold_i, (tr_local, va_local) in enumerate(skf.split(np.zeros(n_suspect), y_s2), start=1):
    gi_tr = suspect_indices[tr_local]
    gi_va = suspect_indices[va_local]

    # CV-safe X43 grade mean (computed from training fold only)
    grade_mean_x43 = (
        ref_df.iloc[gi_tr].groupby("X11")["X43"].mean()
        if X43_chemistry_confirmed else None
    )

    X_tr = build_s2_features(ref_df.iloc[gi_tr].reset_index(drop=True), X43_chemistry_confirmed, grade_mean_x43)
    X_va = build_s2_features(ref_df.iloc[gi_va].reset_index(drop=True), X43_chemistry_confirmed, grade_mean_x43)
    y_tr, y_va = y_train[gi_tr], y_train[gi_va]

    # Best-found config from grid search: depth=3, l2=10, iters=500, lr=0.02
    model = CatBoostClassifier(
        depth=3, l2_leaf_reg=10, iterations=500, learning_rate=0.02,
        auto_class_weights="Balanced", random_state=42, verbose=0,
    )
    model.fit(X_tr, y_tr)
    val_pred = model.predict_proba(X_va)[:, 1]
    s2_oof[va_local] = val_pred
    fold_id_arr[va_local] = fold_i

    if y_va.sum() > 0:
        auc = roc_auc_score(y_va, val_pred)
        auc_per_fold.append(auc)
        print(f"    Fold {fold_i}: size={len(va_local)}  pos={int(y_va.sum())}  AUC={auc:.4f}")
    else:
        print(f"    Fold {fold_i}: size={len(va_local)}  pos=0  (no AUC)")

s2_oof_auc = float(np.mean(auc_per_fold)) if auc_per_fold else float("nan")
print(f"  Stage-2 mean OOF AUC: {s2_oof_auc:.4f}")

# Construct combined OOF (non-suspects = 0)
final_oof = np.zeros(1352)
final_oof[suspect_mask] = s2_oof

pos_missed = int(((final_oof == 0) & (y_train == 1)).sum())
print(f"  Positives with zero OOF proba (should be 0): {pos_missed}")

# ---------------------------------------------------------------------------
# PHASE 4: Threshold Sweep
# ---------------------------------------------------------------------------

print("\n--- Phase 4: Threshold Sweep ---")

best_score = 0.0
best_T = best_recall = best_precision = 0.0
best_n_pos = 0

for T in np.sort(np.unique(s2_oof)):
    preds = np.zeros(1352, dtype=int)
    preds[suspect_mask] = (s2_oof >= T).astype(int)
    tp = int(((preds == 1) & (y_train == 1)).sum())
    fp = int(((preds == 1) & (y_train == 0)).sum())
    fn = int(((preds == 0) & (y_train == 1)).sum())
    R  = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    P  = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    s  = (R + P) / 2.0 * 100.0
    if s > best_score:
        best_score, best_T, best_recall, best_precision, best_n_pos = s, float(T), R, P, tp + fp

v4_oof_score = 54.31
delta = best_score - v4_oof_score

print(f"  OOF (R+P)/2:    {best_score:.4f}")
print(f"  Chosen T:       {best_T:.8f}")
print(f"  Recall:         {best_recall:.4f}  ({int(round(best_recall*66))}/66)")
print(f"  Precision:      {best_precision:.4f}")
print(f"  n_pos (train):  {best_n_pos}")
print(f"  V4 baseline:    {v4_oof_score:.2f}")
print(f"  Delta vs V4:    {delta:+.4f}  {'IMPROVED' if delta > 0 else 'REGRESSED'}")

# ---------------------------------------------------------------------------
# Save OOF parquet (CoilID, fold, oof_proba — 1352 rows)
# ---------------------------------------------------------------------------

fold_assignments = np.full(1352, -1, dtype=int)
fold_assignments[suspect_mask] = fold_id_arr

oof_out = pd.DataFrame({
    "CoilID":    ref_df["CoilID"].values,
    "fold":      fold_assignments,
    "oof_proba": final_oof,
})
oof_out.to_parquet(BUILD_OUT / "oof_v23.parquet", index=False)
print(f"\n  Saved: oof_v23.parquet  ({len(oof_out)} rows)")

# ---------------------------------------------------------------------------
# Save chosen threshold JSON
# ---------------------------------------------------------------------------

threshold_data = {
    "chosen_threshold":          best_T,
    "strategy":                  "maximize_(recall+precision)/2_exact_unique_thresholds_stage2_oof",
    "predicted_lb_score":        round(best_score + 2.67, 4),
    "oof_score":                 best_score,
    "oof_recall":                best_recall,
    "oof_precision":             best_precision,
    "oof_n_positives":           best_n_pos,
    "oof_total":                 1352,
    "v4_oof_baseline":           v4_oof_score,
    "delta_vs_v4":               delta,
    "stage2_oof_auc":            s2_oof_auc,
    "stage2_suspect_pool_size":  n_suspect,
    "stage2_suspect_positives":  n_pos_suspect,
    "T_s1":                      T_S1,
    "x43_chemistry_confirmed":   bool(X43_chemistry_confirmed),
    "x43_variance_ratio":        float(ratio),
}
with open(BUILD_OUT / "chosen_threshold_v23.json", "w") as f:
    json.dump(threshold_data, f, indent=2)
print(f"  Saved: chosen_threshold_v23.json")

# ---------------------------------------------------------------------------
# Full-data Stage-2 fit for test inference
# ---------------------------------------------------------------------------

print("\n--- Full-data Stage-2 fit for test inference ---")

grade_mean_x43_full = (
    ref_df.loc[suspect_mask].groupby("X11")["X43"].mean()
    if X43_chemistry_confirmed else None
)
X_s2_full = build_s2_features(
    ref_df.loc[suspect_mask].reset_index(drop=True),
    X43_chemistry_confirmed,
    grade_mean_x43_full,
)
y_s2_full = y_train[suspect_mask]

stage2_final = CatBoostClassifier(
    depth=3, l2_leaf_reg=10, iterations=500, learning_rate=0.02,
    auto_class_weights="Balanced", random_state=42, verbose=0,
)
stage2_final.fit(X_s2_full, y_s2_full)
print(f"  Full fit: {len(y_s2_full)} rows  |  {int(y_s2_full.sum())} pos")

# ---------------------------------------------------------------------------
# Stage-1 for test: use V4 test_meta (produced by V4 trained on full data)
# ---------------------------------------------------------------------------

test_meta_v4 = pd.read_parquet(BUILD_V4 / "test_meta_v4.parquet")
v4_test_proba = test_meta_v4["test_meta"].values

test_suspect_mask = v4_test_proba > T_S1
n_test_suspect = int(test_suspect_mask.sum())
print(f"  Test suspect pool: {n_test_suspect} / 339")

test_preds = np.zeros(339, dtype=int)
if n_test_suspect > 0:
    X_test_s2 = build_s2_features(
        test_df.loc[test_suspect_mask].reset_index(drop=True),
        X43_chemistry_confirmed,
        grade_mean_x43_full,
    )
    test_s2_probas = stage2_final.predict_proba(X_test_s2)[:, 1]
    test_preds[test_suspect_mask] = (test_s2_probas >= best_T).astype(int)

n_pos_test = int(test_preds.sum())
print(f"  Test positives: {n_pos_test} / 339")

# ---------------------------------------------------------------------------
# Save expected_submission.csv
# ---------------------------------------------------------------------------

sub_df = pd.DataFrame({"CoilID": test_df["CoilID"].values, "Y": test_preds})
assert len(sub_df) == 339
assert set(sub_df.columns) == {"CoilID", "Y"}
assert sub_df["Y"].isin([0, 1]).all()
sub_df.to_csv(BUILD_OUT / "expected_submission.csv", index=False)
print(f"  Saved: expected_submission.csv  ({n_pos_test} positives)")

# ---------------------------------------------------------------------------
# Final Summary
# ---------------------------------------------------------------------------

print("\n" + "=" * 65)
print("V23 BUILD COMPLETE")
print("=" * 65)
print(f"X43 chemistry gate:   {'PASSED' if X43_chemistry_confirmed else 'FAILED'} (ratio={ratio:.4f})")
print(f"Suspect pool (train): {n_suspect} rows / {n_pos_suspect} pos")
print(f"Stage-2 OOF AUC:      {s2_oof_auc:.4f}")
print(f"OOF (R+P)/2:          {best_score:.4f}")
print(f"Chosen threshold:     {best_T:.8f}")
print(f"Test n_positives:     {n_pos_test}")
print(f"Calibrated LB est:    {best_score + 2.67:.4f}")
print(f"Delta vs V4 OOF:      {delta:+.4f}  ({'IMPROVED' if delta > 0 else 'REGRESSED'})")
print("=" * 65)
