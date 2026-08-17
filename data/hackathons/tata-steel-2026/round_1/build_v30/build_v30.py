#!/usr/bin/env python3
"""
build_v30.py -- Compound Feature Engineering: V23 base + 3 new feature groups

Architecture (Cycle 2, data-engineer-agent):
  V23 two-stage cascade base (CatBoost Stage-2 on 836-row suspect pool)
  + Group 1: Per-grade 5-NN anomaly distance on {X14,X18,X22,X23,X41,X8} (C2_N06_rec_2)
  + Group 2: DiCE-proxy X14-grade residual features {X14_grade_dev, X14_grade_p75_excess,
              X14_iso_resid, X14_X18_consistency} (C2_N02_rec_1, pre-engineered)
  + Group 3: Symbolic regression top expressions {X48_div_X49, X13_div_thermal,
              abs_X18_minus_880, v_ct_spread_x_X49} (C2_R13b)

Feature budget: V23 base (15 cols) + 1 NN anomaly + 4 DiCE residual + 4 symbolic = 24 Stage-2 features
CV: 5-fold StratifiedKFold(seed=42) matching V23 exactly.
Stage-1: V4 OOF probas @ T_s1=0.013 (100% recall guarantee from V23).
Stage-2: CatBoost (same hyperparams as V23) on new enriched feature matrix.

Acceptance gates:
  oof_score >= 54.41
  bootstrap_lower_ci >= 53.0
  hard7_recall_at_threshold >= 6
  easy59_caught >= 58
"""

from __future__ import annotations

import json
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from catboost import CatBoostClassifier
from sklearn.ensemble import IsolationForest
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler

warnings.filterwarnings("ignore")

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

BASE = Path(__file__).resolve().parents[1]
DATA_DIR = BASE.parents[3] / "data set of tata steel" / "dataset"
BUILD_V4 = BASE / "build_v4"
BUILD_OUT = BASE / "build_v30"

TRAIN_CSV = DATA_DIR / "train.csv"
TEST_CSV = DATA_DIR / "test.csv"
OOF_V4 = BUILD_V4 / "oof_v4.parquet"
TRAIN_V4_PARQUET = BUILD_V4 / "train_v4.parquet"

print("=" * 70)
print("V30 -- Compound FE: 5-NN Anomaly + X14-Grade Residual + Symbolic")
print("=" * 70)

# ---------------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------------

train_raw = pd.read_csv(TRAIN_CSV)
test_df = pd.read_csv(TEST_CSV).copy()

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
# PHASE 1: CT-Spread Features (same as V23, unconditional)
# ---------------------------------------------------------------------------

print("\n--- Phase 1: CT-Spread Features ---")

ct_cols = ["X4", "X5", "X6", "X14"]
for df in [ref_df, test_df]:
    df["v_ct_spread"]   = df[ct_cols].max(axis=1) - df[ct_cols].min(axis=1)
    df["v_ct_mean"]     = df[ct_cols].mean(axis=1)
    df["v_ct_std"]      = df[ct_cols].std(axis=1)
    df["v_ct_range_sq"] = df["v_ct_spread"] ** 2

print(f"  v_ct_spread: mean={ref_df['v_ct_spread'].mean():.2f}  std={ref_df['v_ct_spread'].std():.2f}")

# ---------------------------------------------------------------------------
# PHASE 2: Group 3 -- Symbolic Regression Features (C2_R13b)
# Arithmetic on raw columns -- zero leakage risk
# ---------------------------------------------------------------------------

print("\n--- Phase 2: Group 3 Symbolic Regression Features (C2_R13b) ---")

eps = 1e-6
for df in [ref_df, test_df]:
    df["X48_div_X49"]        = df["X48"] / (df["X49"] + eps)
    df["X13_div_thermal"]    = df["X13"] / (df["X18"] - df["X14"] + eps)
    df["abs_X18_minus_880"]  = (df["X18"] - 880).abs()
    df["v_ct_spread_x_X49"]  = df["v_ct_spread"] * df["X49"]

print(f"  X48_div_X49:        mean={ref_df['X48_div_X49'].mean():.4f}")
print(f"  X13_div_thermal:    mean={ref_df['X13_div_thermal'].mean():.4f}")
print(f"  abs_X18_minus_880:  mean={ref_df['abs_X18_minus_880'].mean():.2f}")
print(f"  v_ct_spread_x_X49:  mean={ref_df['v_ct_spread_x_X49'].mean():.4f}")

# Diagnostic: Hard-7 + FP-10 signatures
h7_ids   = [1495, 913, 1499, 473, 624, 1436, 72]
fp10_ids = [689, 642, 247, 189, 279, 757, 188, 651, 467, 690]
h7_mask   = ref_df["CoilID"].isin(h7_ids)
fp10_mask = ref_df["CoilID"].isin(fp10_ids)

print(f"  X48_div_X49 (H7):   {ref_df.loc[h7_mask,   'X48_div_X49'].values.round(4)}")
print(f"  X48_div_X49 (FP10): {ref_df.loc[fp10_mask, 'X48_div_X49'].values.round(4)}")
print(f"  CoilID 473 X48_div_X49: {ref_df.loc[ref_df['CoilID']==473, 'X48_div_X49'].values[0]:.4f}")

# ---------------------------------------------------------------------------
# PHASE 3: Helper functions
# ---------------------------------------------------------------------------

NN_FEATURES   = ["X14", "X18", "X22", "X23", "X41", "X8"]
NN_K          = 5
NN_GRADE_COL  = "X11"
NN_MIN_SIZE   = NN_K + 2

SYMBOLIC_COLS  = ["X48_div_X49", "X13_div_thermal", "abs_X18_minus_880", "v_ct_spread_x_X49"]
CT_COLS        = ["v_ct_spread", "v_ct_mean", "v_ct_std", "v_ct_range_sq"]
X14_RESID_COLS = ["X14_grade_dev", "X14_grade_p75_excess", "X14_iso_resid", "X14_X18_consistency"]
NN_DIST_COL    = "nn_anomaly_dist"
S2_BASE        = ["X14", "X49", "X41", "X46", "X48", "X42", "X18", "X11"]


def per_grade_5nn_dist_cv(
    X_tr: pd.DataFrame,
    X_va: pd.DataFrame,
    X_te: pd.DataFrame,
    grade_col: str = NN_GRADE_COL,
    k: int = NN_K,
    feat_cols: list = NN_FEATURES,
) -> tuple:
    """CV-safe per-grade 5-NN distance. StandardScaler fitted on X_tr only."""
    sc = StandardScaler()
    sc.fit(X_tr[feat_cols].fillna(X_tr[feat_cols].median()))
    tr_med = X_tr[feat_cols].median()

    X_tr_s = pd.DataFrame(sc.transform(X_tr[feat_cols].fillna(tr_med)), index=X_tr.index)
    X_va_s = pd.DataFrame(sc.transform(X_va[feat_cols].fillna(tr_med)), index=X_va.index)
    X_te_s = pd.DataFrame(sc.transform(X_te[feat_cols].fillna(tr_med)), index=X_te.index)

    out_tr = np.zeros(len(X_tr))
    out_va = np.zeros(len(X_va))
    out_te = np.zeros(len(X_te))

    for g in X_tr[grade_col].unique():
        tm = (X_tr[grade_col] == g).values
        vm = (X_va[grade_col] == g).values
        em = (X_te[grade_col] == g).values
        n  = int(tm.sum())
        if n < NN_MIN_SIZE:
            continue
        nn = NearestNeighbors(n_neighbors=min(k + 1, n), metric="euclidean")
        nn.fit(X_tr_s.values[tm])
        d, _ = nn.kneighbors(X_tr_s.values[tm])
        out_tr[tm] = d[:, 1:].mean(axis=1)
        if vm.sum() > 0:
            dv, _ = nn.kneighbors(X_va_s.values[vm], n_neighbors=min(k, n))
            out_va[vm] = dv.mean(axis=1)
        if em.sum() > 0:
            de, _ = nn.kneighbors(X_te_s.values[em], n_neighbors=min(k, n))
            out_te[em] = de.mean(axis=1)

    return out_tr, out_va, out_te


def build_x14_grade_feats(
    X_ref: pd.DataFrame,
    X_tgt: pd.DataFrame,
) -> pd.DataFrame:
    """X14-grade residual features. X_ref = training fold for CV-safe statistics."""
    out = pd.DataFrame(index=X_tgt.index)
    g_med = X_ref.groupby("X11")["X14"].median()
    g_p75 = X_ref.groupby("X11")["X14"].quantile(0.75)
    gmed_global = X_ref["X14"].median()
    gp75_global = X_ref["X14"].quantile(0.75)

    out["X14_grade_dev"]        = X_tgt["X14"] - X_tgt["X11"].map(g_med).fillna(gmed_global)
    out["X14_grade_p75_excess"] = (X_tgt["X14"] - X_tgt["X11"].map(g_p75).fillna(gp75_global)).clip(lower=0)

    iso = IsolationForest(contamination=0.05, random_state=42, n_estimators=100)
    iso.fit(X_ref[["X14"]])
    out["X14_iso_resid"] = -iso.score_samples(X_tgt[["X14"]])

    out["X14_X18_consistency"] = (
        (X_tgt["X14"] > 580) & (X_tgt["X14"] < 660)
        & (X_tgt["X18"] > 880) & (X_tgt["X18"] < 920)
    ).astype(int)
    return out


def build_s2_matrix(df: pd.DataFrame, extra_cols: list) -> pd.DataFrame:
    """Assemble Stage-2 feature matrix from a DataFrame that already has all cols computed."""
    out = df[S2_BASE].copy()
    out["X11_X14"]       = df["X11"] * df["X14"]
    out["X49_X46_ratio"] = df["X49"] / (df["X46"] + 1e-9)
    out["X41_X49_diff"]  = df["X41"] - df["X49"]
    for c in CT_COLS + SYMBOLIC_COLS + extra_cols:
        out[c] = df[c].values
    return out


# ---------------------------------------------------------------------------
# PHASE 4: Stage-1 Suspect Pool
# ---------------------------------------------------------------------------

print("\n--- Phase 3: Stage-1 Suspect Pool ---")

T_S1 = 0.013
suspect_mask = ref_df["oof_meta"].values > T_S1
n_suspect = int(suspect_mask.sum())
n_pos_sus = int(y_train[suspect_mask].sum())
suspect_indices = np.where(suspect_mask)[0]
y_s2 = y_train[suspect_mask]

print(f"  T_s1={T_S1}  |  Suspect pool: {n_suspect} rows  ({n_pos_sus} pos)")
print(f"  All 66 positives in pool: {n_pos_sus == 66}")
h7_in_pool = sum(cid in set(ref_df.loc[suspect_mask, 'CoilID'].astype(int)) for cid in h7_ids)
print(f"  Hard-7 in pool: {h7_in_pool}/7")

# ---------------------------------------------------------------------------
# PHASE 5: 5-fold CV on suspect pool
# ---------------------------------------------------------------------------

print("\n--- Phase 4: 5-fold Stage-2 CV ---")

skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
s2_oof      = np.zeros(n_suspect)
fold_id_arr = np.zeros(n_suspect, dtype=int)
auc_per_fold = []
fold_importances = {}
test_df_ri = test_df.reset_index(drop=True)

for fold_i, (tr_local, va_local) in enumerate(
    skf.split(np.zeros(n_suspect), y_s2), start=1
):
    gi_tr = suspect_indices[tr_local]
    gi_va = suspect_indices[va_local]

    X_tr_full = ref_df.iloc[gi_tr].copy().reset_index(drop=True)
    X_va_full = ref_df.iloc[gi_va].copy().reset_index(drop=True)

    # Group 1: 5-NN anomaly distance (CV-safe)
    nn_tr, nn_va, _ = per_grade_5nn_dist_cv(
        X_tr_full, X_va_full, test_df_ri
    )
    X_tr_full[NN_DIST_COL] = nn_tr
    X_va_full[NN_DIST_COL] = nn_va

    # Group 2: X14 grade residual (CV-safe)
    x14_tr = build_x14_grade_feats(X_tr_full, X_tr_full)
    x14_va = build_x14_grade_feats(X_tr_full, X_va_full)
    for c in X14_RESID_COLS:
        X_tr_full[c] = x14_tr[c].values
        X_va_full[c] = x14_va[c].values

    extra = [NN_DIST_COL] + X14_RESID_COLS
    X_tr_mat = build_s2_matrix(X_tr_full, extra)
    X_va_mat = build_s2_matrix(X_va_full, extra)
    y_tr = y_train[gi_tr]
    y_va = y_train[gi_va]

    model = CatBoostClassifier(
        depth=3, l2_leaf_reg=10, iterations=500, learning_rate=0.02,
        auto_class_weights="Balanced", random_state=42, verbose=0,
    )
    model.fit(X_tr_mat, y_tr)
    val_pred = model.predict_proba(X_va_mat)[:, 1]
    s2_oof[va_local] = val_pred
    fold_id_arr[va_local] = fold_i

    if y_va.sum() > 0:
        auc = roc_auc_score(y_va, val_pred)
        auc_per_fold.append(auc)
        fold_importances[fold_i] = dict(zip(X_tr_mat.columns, model.get_feature_importance()))
        print(f"    Fold {fold_i}: size={len(va_local):4d}  pos={int(y_va.sum()):2d}  AUC={auc:.4f}  n_feats={X_tr_mat.shape[1]}")
    else:
        print(f"    Fold {fold_i}: size={len(va_local):4d}  pos=0  (no AUC)")

s2_oof_auc = float(np.mean(auc_per_fold)) if auc_per_fold else float("nan")
print(f"\n  Stage-2 mean OOF AUC: {s2_oof_auc:.4f}  (V23 baseline: 0.7204)")

# ---------------------------------------------------------------------------
# PHASE 6: Threshold Sweep
# ---------------------------------------------------------------------------

print("\n--- Phase 5: Threshold Sweep ---")

final_oof = np.zeros(1352)
final_oof[suspect_mask] = s2_oof

pos_missed = int(((final_oof == 0) & (y_train == 1)).sum())
print(f"  Positives with zero OOF proba (should be 0): {pos_missed}")

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

v23_oof = 54.41
delta_v23 = best_score - v23_oof
v4_oof = 54.31
delta_v4 = best_score - v4_oof

print(f"  OOF (R+P)/2:    {best_score:.4f}")
print(f"  Chosen T:       {best_T:.8f}")
print(f"  Recall:         {best_recall:.4f}  ({int(round(best_recall*66))}/66)")
print(f"  Precision:      {best_precision:.4f}")
print(f"  n_pos (train):  {best_n_pos}")
print(f"  Delta vs V23:   {delta_v23:+.4f}")
print(f"  Delta vs V4:    {delta_v4:+.4f}")

# ---------------------------------------------------------------------------
# PHASE 7: Acceptance Gates + Bootstrap CI
# ---------------------------------------------------------------------------

print("\n--- Phase 6: Acceptance Gates ---")

# Bootstrap CI
rng = np.random.RandomState(42)
boot_scores = []
for _ in range(1000):
    idx = rng.choice(1352, size=1352, replace=True)
    y_b = y_train[idx]
    p_b = final_oof[idx]
    if y_b.sum() == 0:
        continue
    best_b = 0.0
    for T in np.sort(np.unique(p_b[p_b > 0])):
        preds_b = (p_b >= T).astype(int)
        tp_b = int(((preds_b == 1) & (y_b == 1)).sum())
        fp_b = int(((preds_b == 1) & (y_b == 0)).sum())
        fn_b = int(((preds_b == 0) & (y_b == 1)).sum())
        R_b  = tp_b / (tp_b + fn_b) if (tp_b + fn_b) > 0 else 0.0
        P_b  = tp_b / (tp_b + fp_b) if (tp_b + fp_b) > 0 else 0.0
        best_b = max(best_b, (R_b + P_b) / 2.0 * 100.0)
    boot_scores.append(best_b)

boot_lower = float(np.percentile(boot_scores, 2.5))
boot_upper = float(np.percentile(boot_scores, 97.5))
print(f"  Bootstrap 95% CI: [{boot_lower:.2f}, {boot_upper:.2f}]")

# Test-case gate values
preds_at_T = np.zeros(1352, dtype=int)
preds_at_T[suspect_mask] = (s2_oof >= best_T).astype(int)

h7_csv  = pd.read_csv(BASE / "cycles_v2" / "_fixtures" / "hard7.csv")
h7_all  = h7_csv["CoilID"].astype(int).values
h7_idx  = ref_df[ref_df["CoilID"].isin(h7_all)].index
hard7_caught = int(preds_at_T[h7_idx].sum())

c473_mask    = (ref_df["CoilID"] == 473).values
c473_proba   = float(final_oof[c473_mask][0])
c473_flagged = int(preds_at_T[c473_mask][0])

e59_csv  = pd.read_csv(BASE / "cycles_v2" / "_fixtures" / "easy59.csv")
e59_ids  = e59_csv["CoilID"].astype(int).values
e59_idx  = ref_df[ref_df["CoilID"].isin(e59_ids)].index
easy59_caught = int(preds_at_T[e59_idx].sum())

fp10_csv = pd.read_csv(BASE / "cycles_v2" / "_fixtures" / "hard_fp10.csv")
fp10_all = fp10_csv["CoilID"].astype(int).values
fp10_idx = ref_df[ref_df["CoilID"].isin(fp10_all)].index
fp10_flagged = int(preds_at_T[fp10_idx].sum())

print(f"  Hard-7 caught @ T:  {hard7_caught}/7  (target >= 6)")
print(f"  CoilID 473 proba:   {c473_proba:.6f}  T={best_T:.6f}  flagged={'YES' if c473_flagged else 'NO'}")
print(f"  Easy-59 caught @ T: {easy59_caught}/59  (target >= 58)")
print(f"  FP-10 flagged @ T:  {fp10_flagged}/10  (lower = better)")

# Proba of each Hard-7
print("  Per-CoilID Hard-7 probas:")
for cid in h7_all:
    idx_c = ref_df[ref_df["CoilID"] == cid].index
    p = float(final_oof[idx_c.values][0]) if len(idx_c) > 0 else -1.0
    flag = "FLAGGED" if p >= best_T else "MISSED"
    print(f"    CoilID {cid:5d}: proba={p:.6f}  [{flag}]")

g1 = best_score >= 54.41
g2 = boot_lower >= 53.0
g3 = hard7_caught >= 6
g4 = easy59_caught >= 58
all_pass = all([g1, g2, g3, g4])

print(f"\n  GATE 1 oof >= 54.41:      {'PASS' if g1 else 'FAIL'}  ({best_score:.4f})")
print(f"  GATE 2 ci_lower >= 53.0:  {'PASS' if g2 else 'FAIL'}  ({boot_lower:.2f})")
print(f"  GATE 3 hard7 >= 6:        {'PASS' if g3 else 'FAIL'}  ({hard7_caught}/7)")
print(f"  GATE 4 easy59 >= 58:      {'PASS' if g4 else 'FAIL'}  ({easy59_caught}/59)")
print(f"  ALL GATES: {'PASS' if all_pass else 'FAIL'}")

# ---------------------------------------------------------------------------
# PHASE 8: Feature importance summary
# ---------------------------------------------------------------------------

print("\n--- Phase 7: Feature Importance Summary (avg across folds) ---")

if fold_importances:
    all_feats = list(next(iter(fold_importances.values())).keys())
    avg_imp = {f: np.mean([fold_importances[fi].get(f, 0.0) for fi in fold_importances]) for f in all_feats}
    sorted_imp = sorted(avg_imp.items(), key=lambda x: -x[1])
    print("  Top-20 features:")
    for rank, (feat, imp) in enumerate(sorted_imp[:20], 1):
        tag = ""
        if feat == NN_DIST_COL:
            tag = " [NEW-NN]"
        elif feat in X14_RESID_COLS:
            tag = " [NEW-X14-RESID]"
        elif feat in SYMBOLIC_COLS:
            tag = " [NEW-SYMBOLIC]"
        print(f"    {rank:2d}. {feat:<38s}  {imp:7.2f}{tag}")

# ---------------------------------------------------------------------------
# PHASE 9: Save OOF parquet
# ---------------------------------------------------------------------------

fold_assignments = np.full(1352, -1, dtype=int)
fold_assignments[suspect_mask] = fold_id_arr

oof_out = pd.DataFrame({
    "CoilID":    ref_df["CoilID"].values,
    "fold":      fold_assignments,
    "oof_proba": final_oof,
})
oof_out.to_parquet(BUILD_OUT / "oof_v30.parquet", index=False)
print(f"\n  Saved: oof_v30.parquet")

# ---------------------------------------------------------------------------
# PHASE 10: Save threshold JSON
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
    "v23_oof_baseline":          v23_oof,
    "v4_oof_baseline":           v4_oof,
    "delta_vs_v23":              delta_v23,
    "delta_vs_v4":               delta_v4,
    "stage2_oof_auc":            s2_oof_auc,
    "stage2_suspect_pool_size":  n_suspect,
    "stage2_suspect_positives":  n_pos_sus,
    "T_s1":                      T_S1,
    "bootstrap_lower_ci":        boot_lower,
    "bootstrap_upper_ci":        boot_upper,
    "hard7_caught_at_T":         hard7_caught,
    "easy59_caught_at_T":        easy59_caught,
    "fp10_flagged_at_T":         fp10_flagged,
    "coilid_473_proba":          c473_proba,
    "coilid_473_flagged":        bool(c473_flagged),
    "all_gates_pass":            bool(all_pass),
    "feature_groups": {
        "v23_base_s2":    S2_BASE + ["X11_X14", "X49_X46_ratio", "X41_X49_diff"] + CT_COLS,
        "group1_nn":      [NN_DIST_COL],
        "group2_x14":     X14_RESID_COLS,
        "group3_symbolic": SYMBOLIC_COLS,
    },
}
with open(BUILD_OUT / "chosen_threshold_v30.json", "w") as f:
    json.dump(threshold_data, f, indent=2)
print(f"  Saved: chosen_threshold_v30.json")

# ---------------------------------------------------------------------------
# PHASE 11: Full-train fit + test inference
# ---------------------------------------------------------------------------

print("\n--- Phase 8: Full-train fit + Test Inference ---")

X_sus_full = ref_df.loc[suspect_mask].copy().reset_index(drop=True)

# NN dist: full-train reference
sc_ft = StandardScaler()
sc_ft.fit(ref_df[NN_FEATURES].fillna(ref_df[NN_FEATURES].median()))
ft_med = ref_df[NN_FEATURES].median()
X_ref_s = pd.DataFrame(sc_ft.transform(ref_df[NN_FEATURES].fillna(ft_med)), index=ref_df.index)
X_te_s  = pd.DataFrame(sc_ft.transform(test_df_ri[NN_FEATURES].fillna(ft_med)), index=test_df_ri.index)
X_sus_s = pd.DataFrame(sc_ft.transform(X_sus_full[NN_FEATURES].fillna(ft_med)), index=X_sus_full.index)

nn_sus_ft  = np.zeros(len(X_sus_full))
nn_test_ft = np.zeros(len(test_df_ri))

for g in ref_df[NN_GRADE_COL].unique():
    gm_ref = (ref_df[NN_GRADE_COL] == g).values
    gm_sus = (X_sus_full[NN_GRADE_COL] == g).values
    gm_te  = (test_df_ri[NN_GRADE_COL] == g).values
    n      = int(gm_ref.sum())
    if n < NN_MIN_SIZE:
        continue
    nn_ft = NearestNeighbors(n_neighbors=min(NN_K, n), metric="euclidean")
    nn_ft.fit(X_ref_s.values[gm_ref])
    # self-included for suspect rows (small grade overlap is acceptable for full-train)
    if gm_sus.sum() > 0:
        d_sus, _ = nn_ft.kneighbors(X_sus_s.values[gm_sus], n_neighbors=min(NN_K, n))
        nn_sus_ft[gm_sus] = d_sus.mean(axis=1)
    if gm_te.sum() > 0:
        d_te, _ = nn_ft.kneighbors(X_te_s.values[gm_te], n_neighbors=min(NN_K, n))
        nn_test_ft[gm_te] = d_te.mean(axis=1)

X_sus_full[NN_DIST_COL] = nn_sus_ft
test_df_ri[NN_DIST_COL] = nn_test_ft

# X14 resid: full-train reference
x14_sus_ft = build_x14_grade_feats(ref_df, X_sus_full)
x14_te_ft  = build_x14_grade_feats(ref_df, test_df_ri)
for c in X14_RESID_COLS:
    X_sus_full[c]  = x14_sus_ft[c].values
    test_df_ri[c]  = x14_te_ft[c].values

extra = [NN_DIST_COL] + X14_RESID_COLS
X_s2_ft = build_s2_matrix(X_sus_full, extra)
y_s2_ft = y_train[suspect_mask]

stage2_final = CatBoostClassifier(
    depth=3, l2_leaf_reg=10, iterations=500, learning_rate=0.02,
    auto_class_weights="Balanced", random_state=42, verbose=0,
)
stage2_final.fit(X_s2_ft, y_s2_ft)
print(f"  Full fit: {len(y_s2_ft)} rows  |  {int(y_s2_ft.sum())} pos  |  {X_s2_ft.shape[1]} features")

# Test inference
test_meta_v4  = pd.read_parquet(BUILD_V4 / "test_meta_v4.parquet")
v4_test_proba = test_meta_v4["test_meta"].values
test_sus_mask = v4_test_proba > T_S1
n_test_sus    = int(test_sus_mask.sum())
print(f"  Test suspect pool: {n_test_sus} / {len(test_df)}")

test_preds = np.zeros(len(test_df), dtype=int)
if n_test_sus > 0:
    X_te_sus = test_df_ri[test_sus_mask].copy().reset_index(drop=True)
    X_te_mat = build_s2_matrix(X_te_sus, extra)
    test_s2_proba = stage2_final.predict_proba(X_te_mat)[:, 1]
    test_preds[test_sus_mask] = (test_s2_proba >= best_T).astype(int)

n_pos_test = int(test_preds.sum())
print(f"  Test positives: {n_pos_test} / {len(test_df)}")

sub_df = pd.DataFrame({"CoilID": test_df["CoilID"].values, "Y": test_preds})
assert len(sub_df) == len(test_df)
assert sub_df["Y"].isin([0, 1]).all()
sub_df.to_csv(BUILD_OUT / "expected_submission.csv", index=False)
print(f"  Saved: expected_submission.csv  ({n_pos_test} positives)")

# ---------------------------------------------------------------------------
# Final Summary
# ---------------------------------------------------------------------------

print("\n" + "=" * 70)
print("V30 BUILD COMPLETE")
print("=" * 70)
print(f"Feature count (Stage-2): {X_s2_ft.shape[1]}")
print(f"  V23 base:              {len(S2_BASE) + 3 + len(CT_COLS)}")
print(f"  Group 1 (NN anomaly):  1")
print(f"  Group 2 (X14 resid):   {len(X14_RESID_COLS)}")
print(f"  Group 3 (symbolic):    {len(SYMBOLIC_COLS)}")
print(f"Suspect pool:            {n_suspect} rows / {n_pos_sus} pos")
print(f"Stage-2 OOF AUC:         {s2_oof_auc:.4f}  (V23: 0.7204)")
print(f"OOF (R+P)/2:             {best_score:.4f}  (V23: 54.41, V4: 54.31)")
print(f"Delta vs V23:            {delta_v23:+.4f}  {'IMPROVED' if delta_v23 > 0 else 'REGRESSED'}")
print(f"Delta vs V4:             {delta_v4:+.4f}")
print(f"Chosen T:                {best_T:.8f}")
print(f"Bootstrap 95% CI:        [{boot_lower:.2f}, {boot_upper:.2f}]")
print(f"Hard-7 @ T:              {hard7_caught}/7")
print(f"Easy-59 @ T:             {easy59_caught}/59")
print(f"FP-10 flagged @ T:       {fp10_flagged}/10")
print(f"CoilID 473 proba:        {c473_proba:.6f}  flagged={'YES' if c473_flagged else 'NO'}")
print(f"Calibrated LB est:       {best_score + 2.67:.4f}")
print(f"Test positives:          {n_pos_test}")
print(f"ALL GATES PASS:          {'YES' if all_pass else 'NO'}")
print("=" * 70)
