#!/usr/bin/env python3
"""
train_v50.py — Pure-Physics Base (no raw X4-X9 / X29-X33 in model input)
Tata Steel Hot Rolling Defect Detection

## The V46 Problem (why this exists)
V46 OOF AUC = 0.8627 (LOWER than V4's 0.8837).
Root cause: collinearity.
  - V4 features INCLUDE X6, X7, X9, X30, X30_over_X35 as model inputs
  - V46 added Zener (logZ_i ~ fn(X4..X9)) + FT coupling ~ fn(X29..X33) + cooling rates
  - Physics features are near-linear transforms of the same raw cols → redundant dimensions
  - LGB/XGB/CatBoost split budget wasted on collinear features → AUC regressed

## V50 Fix (peer's iter52 insight)
Peer's base did NOT include raw temps/forces → physics transforms filled GENUINE new dimensions.
V50 replicates this:
  - DROP from final model input: X4,X5,X6,X7,X8,X9,X29,X30,X31,X32,X33,X30_over_X35
  - KEEP: all other 46 V4 features (X-range sensors, ratios, polys, lags, rollstats)
  - ADD: 36 physics features computed FROM raw (but raw excluded from model input)
  - Final feature matrix: 46 + 36 = 82 features (vs V4=51, V46=87)

## Architecture
  BASE: LGB+XGB+CatBoost stack → LR meta + Platt calibration
  FOLDS: 5-fold StratifiedKFold seed=42, scale_pos_weight=18.9, NO SMOTE
  SIMS: Fold-isolated Ridge on Y=0-only rows (same leak-safe design as V46)

## Gates
  - OOF AUC >= 0.91 (V4=0.8837, meaningfully higher = physics-pure-base works)
  - SHAP top-5 must include Sims/Zener/ft_coupling features
  - Spearman vs V4 OOF < 0.85 (genuine diversity from different feature space)

HARD RULES:
  - NO submission generation
  - NO leakage: Sims Ridge uses Y=0 AND ti_mask rows only
  - Raw temp/force cols (X4-X9, X29-X33) used ONLY for physics FE, NOT in model input
  - fold_assign for Sims MUST match CV loop (same SKF instance)
"""

from __future__ import annotations

import json
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.calibration import CalibratedClassifierCV
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold

warnings.filterwarnings("ignore")

# ── Paths ──────────────────────────────────────────────────────────────────────
ROOT   = Path("/home/ujjwal/Documents/J.A.R.V.I.S./data/hackathons/tata-steel-2026/round_1")
V4_DIR = ROOT / "build_v4"
OUT    = ROOT / "build_v50"
OUT.mkdir(parents=True, exist_ok=True)

# ── Constants ──────────────────────────────────────────────────────────────────
SEED    = 42
N_FOLDS = 5
TARGET  = "Y"
ID_COL  = "CoilID"
N_POS   = 154      # Fixed test positives for HE F1 formula

SPW = 1286 / 66    # scale_pos_weight = neg/pos ≈ 19.48

print("=" * 70)
print("V50 — Pure-Physics Base (raw X4-X9/X29-X33 EXCLUDED from model input)")
print(f"scale_pos_weight={SPW:.2f} | {N_FOLDS}-fold StratifiedKFold seed={SEED} | NO SMOTE")
print("Design: physics transforms fill NEW dimensions, not collinear with raw")
print("=" * 70)


# ── Column maps (physics FE uses raw cols, but they DON'T enter model) ─────────
TEMP_COLS  = ["X4", "X5", "X6", "X7", "X8", "X9"]   # 6 stands — FE only
FORCE_COLS = ["X29", "X30", "X31", "X32", "X33"]     # 5 stands — FE only
AUX_COLS   = ["X10", "X11", "X12"]                   # Sims auxiliary regressors (kept in model)

# Physical constants for Zener-Hollomon
Q     = 300_000.0   # Activation energy for hot rolling, J/mol
R_GAS = 8.314       # Gas constant, J/(mol·K)

# Cols to drop from final model input matrix (raw temps + forces + ratio derived from X30)
DROP_FROM_MODEL = {
    "X4", "X5", "X6", "X7", "X8", "X9",
    "X29", "X30", "X31", "X32", "X33",
    "X30_over_X35",   # ratio derived from X30 (force col)
}


# ═══════════════════════════════════════════════════════════════════════════════
# PHYSICS FEATURE PIPELINE (identical to V46 — no changes)
# Computes FROM raw cols. Raw cols excluded from model AFTER FE.
# ═══════════════════════════════════════════════════════════════════════════════

def add_zener_hollomon(df: pd.DataFrame) -> pd.DataFrame:
    """
    logZ_i = log(strain_rate_proxy) + Q / (R * T_K_i)
    Strain rate proxy: inter-stand temperature drop (peer's exact recipe)
    Produces: logZ_1..6 + logZ_mean/std/F1F5drop/max/min = 11 features
    """
    df = df.copy()
    t_cols = TEMP_COLS
    logZ_cols = []

    for i, t_col in enumerate(t_cols):
        T_K = df[t_col] + 273.15
        if i == 0:
            strain_rate = (df["X4"] - df["X5"]).abs() + 1e-6
        elif i < 5:
            strain_rate = (df[t_col] - df[t_cols[i + 1]]).abs() + 1e-6
        else:
            strain_rate = (df["X8"] - df["X9"]).abs() + 1e-6

        col_name = f"logZ_{i+1}"
        df[col_name] = np.log(strain_rate) + Q / (R_GAS * T_K)
        logZ_cols.append(col_name)

    logZ_mat = df[logZ_cols]
    df["logZ_mean"]     = logZ_mat.mean(axis=1)
    df["logZ_std"]      = logZ_mat.std(axis=1)
    df["logZ_F1F5drop"] = df["logZ_1"] - df["logZ_5"]
    df["logZ_max"]      = logZ_mat.max(axis=1)
    df["logZ_min"]      = logZ_mat.min(axis=1)

    return df


ZENER_COLS = (
    [f"logZ_{i}" for i in range(1, 7)] +
    ["logZ_mean", "logZ_std", "logZ_F1F5drop", "logZ_max", "logZ_min"]
)  # 11 features


def add_temp_curvature(df: pd.DataFrame) -> pd.DataFrame:
    """X4 - 2*X6 + X9 — stand-skip / non-linear path detector"""
    df = df.copy()
    df["temp_curvature"] = df["X4"] - 2.0 * df["X6"] + df["X9"]
    return df


CURVATURE_COLS = ["temp_curvature"]  # 1 feature


def add_force_temp_coupling(df: pd.DataFrame) -> pd.DataFrame:
    """
    F_stand / T_K_stand per stand.
    High F/T → material harder than expected → defect precursor.
    5 per-stand + max/mean/std/range = 9 features
    """
    df = df.copy()
    ft_cols = []
    for i, (t_col, f_col) in enumerate(zip(TEMP_COLS[:5], FORCE_COLS)):
        T_K = df[t_col] + 273.15
        col_name = f"ft_coupling_{i+1}"
        df[col_name] = df[f_col] / T_K
        ft_cols.append(col_name)

    ft_mat = df[ft_cols]
    df["ft_coupling_max"]   = ft_mat.max(axis=1)
    df["ft_coupling_mean"]  = ft_mat.mean(axis=1)
    df["ft_coupling_std"]   = ft_mat.std(axis=1)
    df["ft_coupling_range"] = ft_mat.max(axis=1) - ft_mat.min(axis=1)

    return df


FT_COUPLING_COLS = (
    [f"ft_coupling_{i}" for i in range(1, 6)] +
    ["ft_coupling_max", "ft_coupling_mean", "ft_coupling_std", "ft_coupling_range"]
)  # 9 features


def add_monotonicity_breaks(df: pd.DataFrame) -> pd.DataFrame:
    """
    temp_mono_breaks: count of X_i < X_{i+1} transitions (temp should decrease)
    force_mono_breaks: count of F_i > F_{i+1} transitions (force should increase)
    2 features
    """
    df = df.copy()
    df["temp_mono_breaks"] = sum(
        (df[TEMP_COLS[i]] < df[TEMP_COLS[i + 1]]).astype(int)
        for i in range(5)
    )
    df["force_mono_breaks"] = sum(
        (df[FORCE_COLS[i]] > df[FORCE_COLS[i + 1]]).astype(int)
        for i in range(4)
    )
    return df


MONO_COLS = ["temp_mono_breaks", "force_mono_breaks"]  # 2 features


def add_cooling_rates(df: pd.DataFrame) -> pd.DataFrame:
    """
    cooling_rate_total = X4 - X9
    cool_rate_i = X{4+i} - X{4+i+1}
    6 features
    """
    df = df.copy()
    df["cooling_rate_total"] = df["X4"] - df["X9"]
    for i in range(5):
        df[f"cool_rate_{i+1}"] = df[TEMP_COLS[i]] - df[TEMP_COLS[i + 1]]
    return df


COOLING_COLS = ["cooling_rate_total"] + [f"cool_rate_{i}" for i in range(1, 6)]  # 6 features

STATIC_PHYSICS_COLS = ZENER_COLS + CURVATURE_COLS + FT_COUPLING_COLS + MONO_COLS + COOLING_COLS
# 11 + 1 + 9 + 2 + 6 = 29 static physics features

SIMS_RESIDUAL_COLS = [f"sims_res_{i}" for i in range(1, 6)] + ["sims_abs_max", "sims_abs_mean"]
# 7 fold-isolated Sims features

ALL_PHYSICS_COLS = STATIC_PHYSICS_COLS + SIMS_RESIDUAL_COLS  # 36 total


def add_static_physics_features(df: pd.DataFrame) -> pd.DataFrame:
    """Apply all static physics transforms (no fold isolation needed)."""
    df = add_zener_hollomon(df)
    df = add_temp_curvature(df)
    df = add_force_temp_coupling(df)
    df = add_monotonicity_breaks(df)
    df = add_cooling_rates(df)
    return df


# ═══════════════════════════════════════════════════════════════════════════════
# STEP 1: Load V4 data
# ═══════════════════════════════════════════════════════════════════════════════

print("\n[1/8] Loading data...")

train_v4 = pd.read_parquet(V4_DIR / "train_v4.parquet")
test_v4  = pd.read_parquet(V4_DIR / "test_v4.parquet")

with open(V4_DIR / "v4_final_features.json") as f:
    V4_FEATURES = json.load(f)["features"]   # 51 SHAP-selected

y          = train_v4[TARGET].values.astype(float)
n_train    = len(train_v4)
n_test     = len(test_v4)
coil_train = train_v4[ID_COL].values
coil_test  = test_v4[ID_COL].values

print(f"  Train: {train_v4.shape} | Test: {test_v4.shape}")
print(f"  Positives: {int(y.sum())} / {n_train} ({y.mean()*100:.2f}%)")
print(f"  Raw cols available for physics FE: {[c for c in DROP_FROM_MODEL if c in train_v4.columns]}")

# Validate V4 features all present in parquet (they must be — same parquet as V46)
missing_v4 = [f for f in V4_FEATURES if f not in train_v4.columns]
assert not missing_v4, f"Missing V4 features in parquet: {missing_v4}"
print(f"  V4 feature validation: ALL {len(V4_FEATURES)} present in parquet [OK]")


# ═══════════════════════════════════════════════════════════════════════════════
# STEP 2: Build V50 clean base feature list (V4 minus raw/derived-raw)
# ═══════════════════════════════════════════════════════════════════════════════

print("\n[2/8] Building V50 clean base feature list (V4 − raw temps/forces)...")

V50_V4_BASE = [f for f in V4_FEATURES if f not in DROP_FROM_MODEL]
dropped_from_v4 = [f for f in V4_FEATURES if f in DROP_FROM_MODEL]

print(f"  V4 original features: {len(V4_FEATURES)}")
print(f"  Dropped (raw/raw-derived): {dropped_from_v4}")
print(f"  V50 clean base: {len(V50_V4_BASE)} features")

assert len(V50_V4_BASE) + len(dropped_from_v4) == len(V4_FEATURES)
# Sanity: none of the raw temp/force cols should be in V50 base
for col in DROP_FROM_MODEL:
    assert col not in V50_V4_BASE, f"DROP col still in base: {col}"
print(f"  No-leakage check: PASS (none of {len(DROP_FROM_MODEL)} raw cols in base)")


# ═══════════════════════════════════════════════════════════════════════════════
# STEP 3: Add static physics features (Zener, FT coupling, curvature, mono, cooling)
# ═══════════════════════════════════════════════════════════════════════════════

print("\n[3/8] Computing static physics features (from raw cols, not in model input)...")

train_fe = add_static_physics_features(train_v4)
test_fe  = add_static_physics_features(test_v4)

missing_static = [c for c in STATIC_PHYSICS_COLS if c not in train_fe.columns]
assert not missing_static, f"Missing static physics cols: {missing_static}"

print(f"  Static physics features computed: {len(STATIC_PHYSICS_COLS)}")
print(f"  logZ_mean: [{train_fe['logZ_mean'].min():.2f}, {train_fe['logZ_mean'].max():.2f}]")
print(f"  temp_curvature: [{train_fe['temp_curvature'].min():.2f}, {train_fe['temp_curvature'].max():.2f}]")
print(f"  ft_coupling_mean: [{train_fe['ft_coupling_mean'].min():.5f}, {train_fe['ft_coupling_mean'].max():.5f}]")
print(f"  cooling_rate_total: [{train_fe['cooling_rate_total'].min():.2f}, {train_fe['cooling_rate_total'].max():.2f}]")

# Physics feature discriminability sanity
for col in ["logZ_mean", "ft_coupling_mean", "temp_curvature", "cooling_rate_total", "temp_mono_breaks"]:
    pos_mean = train_fe.loc[y == 1, col].mean()
    neg_mean = train_fe.loc[y == 0, col].mean()
    print(f"  {col:30s}: defect={pos_mean:.4f}, normal={neg_mean:.4f}, delta={pos_mean-neg_mean:+.4f}")


# ═══════════════════════════════════════════════════════════════════════════════
# STEP 4: Pre-compute fold assignments for Sims residuals
# CRITICAL: fold_assign MUST match the CV loop (same SKF instance)
# ═══════════════════════════════════════════════════════════════════════════════

print("\n[4/8] Pre-computing fold assignments for Sims (must match CV loop)...")

SKF_SIMS = StratifiedKFold(n_splits=N_FOLDS, shuffle=True, random_state=SEED)
fold_assign = np.zeros(n_train, dtype=int)
for fold_idx, (_, val_idx) in enumerate(SKF_SIMS.split(np.zeros(n_train), y)):
    fold_assign[val_idx] = fold_idx

fold_counts = {f: int((fold_assign == f).sum()) for f in range(N_FOLDS)}
print(f"  Fold counts: {fold_counts} (total={sum(fold_counts.values())})")
assert sum(fold_counts.values()) == n_train


# ═══════════════════════════════════════════════════════════════════════════════
# STEP 5: Compute Sims Force Residuals (fold-isolated, Y=0 only in fold-train)
# ═══════════════════════════════════════════════════════════════════════════════

print("\n[5/8] Computing Sims Force Residuals (fold-isolated, Y=0 rows only)...")
print("  Ridge: F_stand ~ (T_stand, X10, X11, X12) trained on Y=0 AND fold-train rows")

n_stands = len(FORCE_COLS)
R_tr = np.zeros((n_train, n_stands))
R_te = np.zeros((n_test,  n_stands))

for f in range(N_FOLDS):
    ti_mask          = (fold_assign != f)
    val_mask         = (fold_assign == f)
    neg_mask_in_ti   = ti_mask & (y == 0)

    n_neg = int(neg_mask_in_ti.sum())
    n_val = int(val_mask.sum())
    print(f"  Fold {f+1}: train-neg={n_neg}, val={n_val}")

    for s in range(n_stands):
        f_col         = FORCE_COLS[s]
        t_col         = TEMP_COLS[s]          # X4..X8 (one per force stand)
        feature_cols  = [t_col] + AUX_COLS    # [T_stand, X10, X11, X12]

        X_neg = train_fe.loc[neg_mask_in_ti, feature_cols].values.astype(float)
        y_neg = train_fe.loc[neg_mask_in_ti, f_col].values.astype(float)

        ridge = Ridge(alpha=1.0, fit_intercept=True)
        ridge.fit(X_neg, y_neg)

        # Validation fold residuals
        X_val = train_fe.loc[val_mask, feature_cols].values.astype(float)
        F_val = train_fe.loc[val_mask, f_col].values.astype(float)
        R_tr[val_mask, s] = F_val - ridge.predict(X_val)

        # Test residuals — average across all 5 fold models
        X_te = test_fe[feature_cols].values.astype(float)
        F_te = test_fe[f_col].values.astype(float)
        R_te[:, s] += (F_te - ridge.predict(X_te)) / N_FOLDS

# Attach Sims residuals
for s in range(n_stands):
    col = f"sims_res_{s+1}"
    train_fe[col] = R_tr[:, s]
    test_fe[col]  = R_te[:, s]

train_fe["sims_abs_max"]  = np.abs(R_tr).max(axis=1)
train_fe["sims_abs_mean"] = np.abs(R_tr).mean(axis=1)
test_fe["sims_abs_max"]   = np.abs(R_te).max(axis=1)
test_fe["sims_abs_mean"]  = np.abs(R_te).mean(axis=1)

print(f"  Sims residuals attached: {len(SIMS_RESIDUAL_COLS)} features")
print(f"  sims_abs_max: defect_mean={train_fe.loc[y==1,'sims_abs_max'].mean():.4f}, "
      f"normal_mean={train_fe.loc[y==0,'sims_abs_max'].mean():.4f}")


# ═══════════════════════════════════════════════════════════════════════════════
# STEP 6: Build FINAL feature matrix
# V50 = V4_clean_base (46) + static_physics (29) + Sims (7) = 82 features
# Raw X4-X9/X29-X33 ARE EXCLUDED from this matrix
# ═══════════════════════════════════════════════════════════════════════════════

print("\n[6/8] Building final V50 feature matrix (raw cols excluded)...")

V50_FEATURES = V50_V4_BASE + ALL_PHYSICS_COLS
assert len(V50_FEATURES) == len(set(V50_FEATURES)), "Duplicate feature names in V50!"

# Final safety check: no raw temp/force in model input
for col in DROP_FROM_MODEL:
    assert col not in V50_FEATURES, f"LEAK: {col} still in V50 feature list!"

# Validate all present in engineered DFs
missing_tr = [f for f in V50_FEATURES if f not in train_fe.columns]
missing_te = [f for f in V50_FEATURES if f not in test_fe.columns]
if missing_tr:
    raise ValueError(f"Missing features in train: {missing_tr}")
if missing_te:
    raise ValueError(f"Missing features in test: {missing_te}")

X_train_raw = train_fe[V50_FEATURES].fillna(0).values.astype(np.float64)
X_test_raw  = test_fe[V50_FEATURES].fillna(0).values.astype(np.float64)

print(f"  V4 clean base:          {len(V50_V4_BASE)} features")
print(f"  Static physics:         {len(STATIC_PHYSICS_COLS)} features")
print(f"  Sims residuals:         {len(SIMS_RESIDUAL_COLS)} features")
print(f"  TOTAL V50 features:     {len(V50_FEATURES)}")
print(f"  X_train: {X_train_raw.shape} | X_test: {X_test_raw.shape}")
print(f"  NaN check train: {np.isnan(X_train_raw).sum()} | test: {np.isnan(X_test_raw).sum()}")
print(f"  Raw col leak check: PASS (none of DROP_FROM_MODEL in feature set)")


# ═══════════════════════════════════════════════════════════════════════════════
# STEP 7: 5-Fold Stacking Loop (LGB + XGB + CatBoost → LR meta + Platt)
# ═══════════════════════════════════════════════════════════════════════════════

print("\n[7/8] Training 5-fold stacking (LGB + XGB + CatBoost → LR meta)...")

try:
    import lightgbm as lgb
    import xgboost as xgb
    from catboost import CatBoostClassifier
    print("  Libraries: lightgbm, xgboost, catboost — OK")
except ImportError as e:
    raise ImportError(f"Missing library: {e}")

# Model configs (identical to V46 for fair comparison)
LGB_PARAMS = dict(
    objective="binary",
    metric="auc",
    learning_rate=0.03,
    num_leaves=63,
    max_depth=6,
    min_child_samples=10,
    subsample=0.8,
    subsample_freq=1,
    colsample_bytree=0.7,
    reg_alpha=0.05,
    reg_lambda=0.5,
    n_estimators=700,
    random_state=SEED,
    verbosity=-1,
    n_jobs=-1,
    scale_pos_weight=SPW,
)

XGB_PARAMS = dict(
    objective="binary:logistic",
    eval_metric="auc",
    learning_rate=0.03,
    max_depth=6,
    min_child_weight=5,
    subsample=0.8,
    colsample_bytree=0.7,
    reg_alpha=0.05,
    reg_lambda=0.5,
    n_estimators=700,
    random_state=SEED,
    verbosity=0,
    n_jobs=-1,
    scale_pos_weight=SPW,
    use_label_encoder=False,
    tree_method="hist",
)

CAT_PARAMS = dict(
    iterations=700,
    learning_rate=0.03,
    depth=6,
    l2_leaf_reg=5,
    random_seed=SEED,
    eval_metric="AUC",
    scale_pos_weight=SPW,
    verbose=0,
)

SKF = StratifiedKFold(n_splits=N_FOLDS, shuffle=True, random_state=SEED)

oof_lgb = np.zeros(n_train)
oof_xgb = np.zeros(n_train)
oof_cat = np.zeros(n_train)

test_lgb_folds = np.zeros((n_test, N_FOLDS))
test_xgb_folds = np.zeros((n_test, N_FOLDS))
test_cat_folds = np.zeros((n_test, N_FOLDS))

fold_aucs_lgb = []
fold_aucs_xgb = []
fold_aucs_cat = []

# Verify fold alignment with Sims pre-computation
print("  Verifying fold alignment (Sims fold_assign matches CV splits)...")
for fold_idx, (tr_idx, val_idx) in enumerate(SKF.split(np.zeros(n_train), y)):
    fa_val = fold_assign[val_idx]
    assert np.all(fa_val == fold_idx), f"Fold {fold_idx} misaligned — Sims residuals corrupted!"
print("  Fold alignment: ALL FOLDS OK [verified]")

print(f"\n  Starting CV loop (N_FOLDS={N_FOLDS}, scale_pos_weight={SPW:.2f})...")

for fold_idx, (tr_idx, val_idx) in enumerate(SKF.split(np.zeros(n_train), y)):
    y_tr  = y[tr_idx]
    y_val = y[val_idx]
    X_tr  = X_train_raw[tr_idx]
    X_val = X_train_raw[val_idx]

    print(f"\n  --- Fold {fold_idx+1}/{N_FOLDS} | train={len(tr_idx)}, val={len(val_idx)}, "
          f"pos_train={int(y_tr.sum())}, pos_val={int(y_val.sum())} ---")

    # No SMOTE — scale_pos_weight handles imbalance (same as V46b decision)
    model_lgb = lgb.LGBMClassifier(**LGB_PARAMS)
    model_lgb.fit(X_tr, y_tr)
    oof_lgb[val_idx] = model_lgb.predict_proba(X_val)[:, 1]
    test_lgb_folds[:, fold_idx] = model_lgb.predict_proba(X_test_raw)[:, 1]
    fold_aucs_lgb.append(roc_auc_score(y_val, oof_lgb[val_idx]))

    model_xgb = xgb.XGBClassifier(**XGB_PARAMS)
    model_xgb.fit(X_tr, y_tr, verbose=False)
    oof_xgb[val_idx] = model_xgb.predict_proba(X_val)[:, 1]
    test_xgb_folds[:, fold_idx] = model_xgb.predict_proba(X_test_raw)[:, 1]
    fold_aucs_xgb.append(roc_auc_score(y_val, oof_xgb[val_idx]))

    model_cat = CatBoostClassifier(**CAT_PARAMS)
    model_cat.fit(X_tr, y_tr)
    oof_cat[val_idx] = model_cat.predict_proba(X_val)[:, 1]
    test_cat_folds[:, fold_idx] = model_cat.predict_proba(X_test_raw)[:, 1]
    fold_aucs_cat.append(roc_auc_score(y_val, oof_cat[val_idx]))

    print(f"    LGB AUC={fold_aucs_lgb[-1]:.5f} | XGB AUC={fold_aucs_xgb[-1]:.5f} | "
          f"CAT AUC={fold_aucs_cat[-1]:.5f}")

test_lgb_avg = test_lgb_folds.mean(axis=1)
test_xgb_avg = test_xgb_folds.mean(axis=1)
test_cat_avg = test_cat_folds.mean(axis=1)

auc_lgb = roc_auc_score(y, oof_lgb)
auc_xgb = roc_auc_score(y, oof_xgb)
auc_cat = roc_auc_score(y, oof_cat)

mean_fold_lgb = float(np.mean(fold_aucs_lgb))
mean_fold_xgb = float(np.mean(fold_aucs_xgb))
mean_fold_cat = float(np.mean(fold_aucs_cat))
std_fold_lgb  = float(np.std(fold_aucs_lgb))
std_fold_xgb  = float(np.std(fold_aucs_xgb))
std_fold_cat  = float(np.std(fold_aucs_cat))

print(f"\n  Per-model OOF AUC: LGB={auc_lgb:.5f} | XGB={auc_xgb:.5f} | CAT={auc_cat:.5f}")
print(f"  V4 reference:      LGB=0.86150 | XGB=0.86680 | CAT=0.87560")
print(f"  V46 reference:     LGB=0.86683 | XGB=0.86274 | CAT=0.85317 (collinear, regressed)")
print(f"  Deltas vs V4:      LGB={auc_lgb-0.86150:+.5f} | XGB={auc_xgb-0.86680:+.5f} | "
      f"CAT={auc_cat-0.87560:+.5f}")


# ── Meta-learner (LR + Platt calibration) ─────────────────────────────────────

print("\n  Training meta-learner (LR + Platt calibration on [oof_lgb, oof_xgb, oof_cat])...")

X_meta_train = np.column_stack([oof_lgb, oof_xgb, oof_cat])
X_meta_test  = np.column_stack([test_lgb_avg, test_xgb_avg, test_cat_avg])

lr = LogisticRegression(C=1.0, max_iter=1000, random_state=SEED)
meta_cal = CalibratedClassifierCV(lr, method="sigmoid", cv=5)
meta_cal.fit(X_meta_train, y)

oof_meta  = meta_cal.predict_proba(X_meta_train)[:, 1]
test_meta = meta_cal.predict_proba(X_meta_test)[:, 1]

meta_auc = roc_auc_score(y, oof_meta)
print(f"  Meta OOF AUC: {meta_auc:.5f}")
print(f"  V4 reference: 0.88370 | V46 regressed: 0.86268 | Peer iter52: 0.95340")
print(f"  Delta vs V4:  {meta_auc - 0.88370:+.5f}")
print(f"  Delta vs V46: {meta_auc - 0.86268:+.5f}")
print(f"  V50 hypothesis: meta AUC should be ABOVE V4 (0.8837) — physics now in clean dims")

# Bootstrap 95% CI
rng = np.random.default_rng(SEED)
boot_aucs = [
    roc_auc_score(y[idx := rng.choice(n_train, size=n_train, replace=True)], oof_meta[idx])
    for _ in range(2000)
    if y[idx := rng.choice(n_train, size=n_train, replace=True)].sum() >= 2
]
# Redo cleanly
rng = np.random.default_rng(SEED)
boot_aucs = []
for _ in range(2000):
    idx = rng.choice(n_train, size=n_train, replace=True)
    if y[idx].sum() >= 2:
        boot_aucs.append(roc_auc_score(y[idx], oof_meta[idx]))
ci_lo = float(np.percentile(boot_aucs, 2.5))
ci_hi = float(np.percentile(boot_aucs, 97.5))
print(f"  Bootstrap 95% CI: [{ci_lo:.5f}, {ci_hi:.5f}]")


# ── SHAP Feature Importance ────────────────────────────────────────────────────

print("\n  Computing SHAP feature importances (LGB, full-train refit)...")
try:
    import shap

    lgb_full = lgb.LGBMClassifier(**LGB_PARAMS)
    lgb_full.fit(X_train_raw, y)
    explainer = shap.TreeExplainer(lgb_full)
    shap_vals = explainer.shap_values(X_train_raw)
    if isinstance(shap_vals, list):
        shap_vals = shap_vals[1]

    mean_abs_shap = np.abs(shap_vals).mean(axis=0)
    top_idx = np.argsort(mean_abs_shap)[::-1][:20]

    shap_results = []
    print(f"  Top-20 SHAP features (LGB, mean |SHAP|):")
    for rank, idx in enumerate(top_idx, 1):
        print(f"    {rank:2d}. {V50_FEATURES[idx]:40s}  {mean_abs_shap[idx]:.6f}")
        shap_results.append({
            "rank": rank,
            "feature": V50_FEATURES[idx],
            "mean_abs_shap": float(mean_abs_shap[idx])
        })

    top10_feats = {V50_FEATURES[i] for i in top_idx[:10]}
    sims_in_top10  = any("sims" in f for f in top10_feats)
    zener_in_top10 = any("logZ" in f for f in top10_feats)
    ft_in_top10    = any("ft_coupling" in f for f in top10_feats)
    physics_in_top5 = sum(
        1 for f in {V50_FEATURES[i] for i in top_idx[:5]}
        if any(p in f for p in ["sims", "logZ", "ft_coupling", "cool_rate", "temp_curv", "mono"])
    )
    print(f"\n  Physics in top-10: Sims={sims_in_top10}, Zener={zener_in_top10}, FT={ft_in_top10}")
    print(f"  Physics features in top-5: {physics_in_top5}/5")
    shap_available = True

except ImportError:
    print("  SHAP not available — skipping")
    shap_results = [{"rank": i+1, "feature": V50_FEATURES[i], "mean_abs_shap": None}
                    for i in range(min(20, len(V50_FEATURES)))]
    sims_in_top10 = zener_in_top10 = ft_in_top10 = None
    physics_in_top5 = None
    shap_available = False


# ── Estimated LB (HE F1 formula) ──────────────────────────────────────────────

print("\n  Estimated LB via HE F1: F1 = 200*TP/(K+N_POS), N_POS=154")

def he_f1(tp: int, k: int, n_pos: int = N_POS) -> float:
    return 200 * tp / (k + n_pos)

sorted_meta = np.argsort(oof_meta)[::-1]

best_oof_score = 0.0
best_oof_k = 200
for k_cand in range(100, 280):
    top_k_idx = sorted_meta[:k_cand]
    tp_oof = int(y[top_k_idx].sum())
    f1_cand = he_f1(tp_oof, k_cand)
    if f1_cand > best_oof_score:
        best_oof_score = f1_cand
        best_oof_k = k_cand

tp200 = int(y[sorted_meta[:200]].sum())
tp216 = int(y[sorted_meta[:216]].sum())
f1_200 = he_f1(tp200, 200)
f1_216 = he_f1(tp216, 216)
lb_delta_est = meta_auc * 100 + 2.67

print(f"  OOF TP@K=200: {tp200}/66 | F1@K=200: {f1_200:.2f}")
print(f"  OOF TP@K=216: {tp216}/66 | F1@K=216: {f1_216:.2f}")
print(f"  OOF best F1 @ K={best_oof_k}: {best_oof_score:.2f} (TP={int(y[sorted_meta[:best_oof_k]].sum())})")
print(f"  Delta-based est: {lb_delta_est:.2f} (AUC*100+2.67, legacy method)")


# ── Spearman vs existing paradigms ────────────────────────────────────────────

print("\n  Spearman diversity vs existing OOFs...")

spearman_results = {}
ref_paradigms = {
    "v4_meta":   (ROOT / "build_v4"  / "oof_v4.parquet",  "oof_meta"),
    "v46_proba": (ROOT / "build_v46" / "oof_v46.parquet", "oof_proba"),
    "v40_proba": (ROOT / "build_v40" / "oof_v40.parquet", "oof_proba"),
    "v41_proba": (ROOT / "build_v41" / "oof_v41.parquet", "oof_proba"),
}

for name, (path, col) in ref_paradigms.items():
    try:
        ref_df = pd.read_parquet(path)
        col_use = col if col in ref_df.columns else [c for c in ref_df.columns if c not in (ID_COL, "Y", "y")][0]
        ref_arr = ref_df[col_use].values
        if len(ref_arr) == n_train:
            r, _ = spearmanr(oof_meta, ref_arr)
            spearman_results[name] = float(r)
            tag = "DIVERSE" if abs(r) < 0.80 else ("MODERATE" if abs(r) < 0.85 else ("HIGH" if abs(r) < 0.95 else "VERY HIGH"))
            print(f"  V50 vs {name}: ρ={r:+.4f} [{tag}]")
        else:
            print(f"  {name}: length mismatch ({len(ref_arr)} vs {n_train})")
    except Exception as e:
        print(f"  {name}: FAILED — {e}")

spearman_vs_v4  = spearman_results.get("v4_meta", None)
spearman_vs_v46 = spearman_results.get("v46_proba", None)


# ═══════════════════════════════════════════════════════════════════════════════
# STEP 8: Save Artifacts
# ═══════════════════════════════════════════════════════════════════════════════

print(f"\n[8/8] Saving artifacts to {OUT}...")

# OOF parquet
oof_df = pd.DataFrame({
    "CoilID":    coil_train,
    "oof_proba": oof_meta,
    "y":         y.astype(int),
})
oof_df.to_parquet(OUT / "oof_v50.parquet", index=False)
print(f"  oof_v50.parquet: {oof_df.shape}")

# Test proba parquet
test_df_out = pd.DataFrame({
    "CoilID":     coil_test,
    "test_proba": test_meta,
})
test_df_out.to_parquet(OUT / "test_proba_v50.parquet", index=False)
print(f"  test_proba_v50.parquet: {test_df_out.shape}")

# Gates
gates = {
    "oof_auc_gte_091":      bool(meta_auc >= 0.91),
    "oof_auc_gt_v4_0_8837": bool(meta_auc > 0.8837),
    "oof_auc_gt_v46_0_8627":bool(meta_auc > 0.8627),
    "shap_sims_in_top10":   bool(sims_in_top10) if sims_in_top10 is not None else None,
    "shap_zener_in_top10":  bool(zener_in_top10) if zener_in_top10 is not None else None,
    "spearman_v4_lt_085":   bool(abs(spearman_vs_v4) < 0.85) if spearman_vs_v4 is not None else None,
    "est_lb_k200_gte_75":   bool(f1_200 >= 75.0),
}

summary = {
    "oof_auc":            round(meta_auc, 5),
    "oof_auc_ci":         [round(ci_lo, 5), round(ci_hi, 5)],
    "per_model_oof_auc":  {"lgb": round(auc_lgb, 5), "xgb": round(auc_xgb, 5), "cat": round(auc_cat, 5)},
    "fold_aucs":          {
        "lgb": [round(a, 5) for a in fold_aucs_lgb],
        "xgb": [round(a, 5) for a in fold_aucs_xgb],
        "cat": [round(a, 5) for a in fold_aucs_cat],
    },
    "mean_fold_auc":      {"lgb": round(mean_fold_lgb, 5), "xgb": round(mean_fold_xgb, 5), "cat": round(mean_fold_cat, 5)},
    "est_lb":             {"K200": round(f1_200, 2), "K216": round(f1_216, 2),
                           "best": round(best_oof_score, 2), "best_k": int(best_oof_k),
                           "legacy_delta": round(lb_delta_est, 2)},
    "oof_tp":             {"K200": int(tp200), "K216": int(tp216), "total_pos": int(y.sum())},
    "spearman":           spearman_results,
    "n_features":         {
        "v4_clean_base":   len(V50_V4_BASE),
        "dropped_from_v4": len(dropped_from_v4),
        "static_physics":  len(STATIC_PHYSICS_COLS),
        "sims_residuals":  len(SIMS_RESIDUAL_COLS),
        "total":           len(V50_FEATURES),
    },
    "dropped_raw_cols":   sorted(DROP_FROM_MODEL),
    "gates":              gates,
    "references":         {
        "v4_oof_auc":  0.88370, "v4_lb": 56.98,
        "v46_oof_auc": 0.86268, "v46_lb": "N/A (gates failed)",
        "peer_oof_auc": 0.95340, "peer_lb": 77.67,
        "v44_banked_lb": 72.83,
    },
}

with open(OUT / "cv_summary_v50.json", "w") as f:
    json.dump(summary, f, indent=2)
print(f"  cv_summary_v50.json: saved")

# SHAP JSON
with open(OUT / "shap_importance_v50.json", "w") as f:
    json.dump({
        "top_20": shap_results,
        "sims_in_top10": sims_in_top10,
        "zener_in_top10": zener_in_top10,
        "ft_in_top10": ft_in_top10,
        "physics_in_top5": physics_in_top5,
        "available": shap_available,
    }, f, indent=2)
print(f"  shap_importance_v50.json: saved")


# ── CV Report ──────────────────────────────────────────────────────────────────

fold_table_lgb = "\n".join(f"| {i+1} | {a:.5f} |" for i, a in enumerate(fold_aucs_lgb))
fold_table_xgb = "\n".join(f"| {i+1} | {a:.5f} |" for i, a in enumerate(fold_aucs_xgb))
fold_table_cat = "\n".join(f"| {i+1} | {a:.5f} |" for i, a in enumerate(fold_aucs_cat))

top5_shap_lines = "\n".join(
    f"- {r['rank']}. {r['feature']}: {r['mean_abs_shap']:.6f}" if r["mean_abs_shap"] is not None
    else f"- {r['rank']}. {r['feature']}: N/A"
    for r in shap_results[:5]
) if shap_results else "- SHAP unavailable"

spearman_lines = "\n".join(
    f"- V50 vs {n}: ρ={r:+.4f}  {'[DIVERSE <0.80]' if abs(r)<0.80 else '[MODERATE <0.85]' if abs(r)<0.85 else '[HIGH <0.95]' if abs(r)<0.95 else '[VERY HIGH]'}"
    for n, r in spearman_results.items()
) if spearman_results else "- No reference OOFs found"

gates_summary_lines = "\n".join(
    f"- {'PASS' if v else ('FAIL' if v is False else 'N/A')}: {k} = {v}"
    for k, v in gates.items()
)
gates_ok = all(v for v in gates.values() if v is not None)

report = f"""# V50 CV Report — Pure-Physics Base (raw X4-X9/X29-X33 excluded)

**Date:** 2026-05-24
**Architecture:** LGB+XGB+CatBoost → LR meta + Platt | NO SMOTE | scale_pos_weight={SPW:.2f}
**Key fix vs V46:** Dropped raw temp/force cols from model input → physics fills new dimensions, not collinear ones

---

## Gate Results

{gates_summary_lines}

**Win condition (critical):** OOF AUC > V4 (0.8837). If V50 AUC <= 0.86, physics-on-pure-base is also dead.

**Overall: {'PASS — physics-pure-base works!' if gates_ok else 'PARTIAL/FAIL — check gates above'}**

---

## OOF AUC Summary

| Metric | Value | Reference |
|---|---|---|
| Meta OOF AUC | **{meta_auc:.5f}** | V4=0.8837, V46=0.8627 (regressed), Peer=0.9534 |
| Bootstrap 95% CI | [{ci_lo:.5f}, {ci_hi:.5f}] | |
| Delta vs V4 | {meta_auc - 0.88370:+.5f} | |
| Delta vs V46 (collinear fail) | {meta_auc - 0.86268:+.5f} | |
| Delta vs Peer | {meta_auc - 0.95340:+.5f} | |
| LGB OOF AUC | {auc_lgb:.5f} | V4 LGB=0.86150 |
| XGB OOF AUC | {auc_xgb:.5f} | V4 XGB=0.86680 |
| CatBoost OOF AUC | {auc_cat:.5f} | V4 CAT=0.87560 |

---

## Per-Fold AUCs (LGB)

| Fold | AUC |
|---|---|
{fold_table_lgb}
**Mean: {mean_fold_lgb:.5f} ± {std_fold_lgb:.5f}**

## Per-Fold AUCs (XGB)

| Fold | AUC |
|---|---|
{fold_table_xgb}
**Mean: {mean_fold_xgb:.5f} ± {std_fold_xgb:.5f}**

## Per-Fold AUCs (CatBoost)

| Fold | AUC |
|---|---|
{fold_table_cat}
**Mean: {mean_fold_cat:.5f} ± {std_fold_cat:.5f}**

---

## Estimated LB (HE F1: 200*TP/(K+154))

| K | OOF TP | Est LB |
|---|---|---|
| 200 | {tp200}/66 | **{f1_200:.2f}** |
| 216 (peer K) | {tp216}/66 | **{f1_216:.2f}** |
| Best (K={best_oof_k}) | {int(y[sorted_meta[:best_oof_k]].sum())}/66 | **{best_oof_score:.2f}** |

Legacy delta-based (AUC*100+2.67): {lb_delta_est:.2f}
Gap to peer 77.67 @K=216: {f1_216 - 77.67:+.2f}
Gap to V44 banked 72.83 @K=200: {f1_200 - 72.83:+.2f}

---

## Top-5 SHAP Features (LGB, mean |SHAP|)

{top5_shap_lines}

Physics in top-10: Sims={sims_in_top10}, Zener={zener_in_top10}, FT={ft_in_top10}
Gate: Sims+Zener should appear → {'PASS' if (sims_in_top10 and zener_in_top10) else 'FAIL/NA'}

---

## Spearman vs Existing Paradigms

{spearman_lines}

Gate: Spearman vs V4 < 0.85 (genuine diversity)
Result: {f'{spearman_vs_v4:.4f}' if spearman_vs_v4 is not None else 'N/A'} → {'PASS' if spearman_vs_v4 is not None and abs(spearman_vs_v4) < 0.85 else 'FAIL/NA'}

---

## Feature Set

| Group | Count |
|---|---|
| V4 clean base (raw/derived-raw dropped) | {len(V50_V4_BASE)} |
| Dropped from V4 (raw/derived) | {len(dropped_from_v4)}: {dropped_from_v4} |
| Zener-Hollomon (11) | logZ_1..6 + mean/std/F1F5drop/max/min |
| Sims residuals (7, fold-isolated) | sims_res_1..5 + sims_abs_max/mean |
| Temp curvature (1) | X4 - 2*X6 + X9 |
| F/T coupling (9) | ft_coupling_1..5 + max/mean/std/range |
| Mono breaks (2) | temp_mono_breaks + force_mono_breaks |
| Cooling rates (6) | cooling_rate_total + cool_rate_1..5 |
| **TOTAL V50** | **{len(V50_FEATURES)}** |

---

## Why V50 Should Beat V46

V46 added physics features ON TOP of a V4 base that still had raw X6, X7, X9, X30 in it.
- logZ_i = f(X4..X9) → near-collinear with X6, X7, X9 already in V4
- ft_coupling_i = X29_i / T_K_i → near-collinear with X30 already in V4
- Result: trees wasted splits on redundant dimensions → AUC regressed (0.8837 → 0.8627)

V50 drops the raw cols first:
- Physics features now occupy genuinely NEW dimensions in feature space
- Trees can discover the physics signal without competing with its raw sources
- Peer's iter52 (0.9534 OOF) did exactly this — pure-physics base

---

## Top-3 Risks

1. **Signal magnitude:** With 5 raw cols removed from V4, the base loses some discriminative
   power. The physics features need to MORE than compensate. If V50 AUC < 0.8837, the
   remaining V4 features (X13/X36 ratio domain) aren't sufficient to carry the load even
   with physics augmentation. → Pivot to TabPFN / OpenFE.

2. **OOF vs LB gap:** The +2.67 calibration was fitted on V4-tier models. Physics-augmented
   OOF→LB relationship is unknown. Use HE F1 formula (TP-based) as primary LB estimator,
   not the legacy delta method.

3. **Fold-3 variance:** Historical hard fold (13 val positives). Physics features with high
   within-stand variance may amplify fold-3 noise. Monitor per-fold std.

---

## Ready for V51 Consensus?

{'YES — OOF AUC > V4 + physics in SHAP top-10 + diversity confirmed' if gates_ok else 'CONDITIONAL — check failed gates. If AUC <= 0.86, physics-pure-base dead → pivot.'}

Files:
- `oof_v50.parquet` — 1352 rows: CoilID, oof_proba, y
- `test_proba_v50.parquet` — 339 rows: CoilID, test_proba
- `cv_summary_v50.json` — machine-readable summary
- `shap_importance_v50.json` — SHAP rankings + physics validation
- `train_v50.py` — this script
- `approach.md` — design notes
- `cv_report_v50.md` — this file
"""

with open(OUT / "cv_report_v50.md", "w") as f:
    f.write(report)
print(f"  cv_report_v50.md: saved")

# Approach.md
approach = f"""# V50 Approach — Pure-Physics Base (no raw temp/force in model)

## TL;DR
V46 failed (AUC regressed 0.8837 → 0.8627) because raw temp/force cols were still in the V4 base,
making physics features collinear. V50 drops the raw cols first, then adds physics.
This mirrors peer's iter52 design (0.9534 OOF, 77.67 LB).

## The Collinearity Problem
V4 features include: X6, X7, X9 (raw temps), X30 (raw force), X30_over_X35 (force ratio).
V46 added: logZ_i = f(X4..X9), ft_coupling_i = X29_i/T_K_i.
→ logZ highly correlated with X6/X7/X9 already in base → redundant dimension → trees wasted splits.

## V50 Fix
Drop from final model input: X4,X5,X6,X7,X8,X9,X29,X30,X31,X32,X33,X30_over_X35
Keep for physics FE only (compute from, but exclude from model).
Result: V4 clean base = 46 features + 36 physics = 82 total features.

## Feature Engineering Pipeline
1. Load V4 parquet (has all raw cols available for FE)
2. Compute static physics: Zener-Hollomon(11) + temp_curvature(1) + FT_coupling(9) + mono_breaks(2) + cooling_rates(6) = 29
3. Compute fold-isolated Sims residuals: Ridge(Y=0 train-fold rows) per stand = 7
4. DROP raw cols from final feature matrix → 82 features enter the model

## Architecture
LGB+XGB+CatBoost (5-fold StratKFold seed=42, NO SMOTE, scale_pos_weight={SPW:.2f}) → LR meta + Platt cal

## Results
- Meta OOF AUC: {meta_auc:.5f}
- V4 reference: 0.88370 | Delta: {meta_auc-0.88370:+.5f}
- V46 regressed: 0.86268 | Delta vs V46: {meta_auc-0.86268:+.5f}
- Peer iter52: 0.95340
- Est LB @K=200: {f1_200:.2f}
- Est LB @K=216: {f1_216:.2f}
- V44 banked: 72.83 | Peer banked: 77.67
"""

with open(OUT / "approach.md", "w") as f:
    f.write(approach)
print(f"  approach.md: saved")


# ═══════════════════════════════════════════════════════════════════════════════
# FINAL ORCHESTRATOR SUMMARY
# ═══════════════════════════════════════════════════════════════════════════════

print("\n" + "=" * 70)
print("V50 COMPLETE — ORCHESTRATOR REPORT")
print("=" * 70)
print(f"1. OOF AUC:      {meta_auc:.5f}")
print(f"   V4 reference: 0.88370 | Delta: {meta_auc-0.88370:+.5f}")
print(f"   V46 regressed: 0.86268 | Delta: {meta_auc-0.86268:+.5f}")
print(f"   Gate >= 0.91:  {'PASS' if meta_auc >= 0.91 else 'FAIL'}")
print(f"   Gate > V4:     {'PASS' if meta_auc > 0.8837 else 'FAIL'}")
print(f"   Bootstrap CI:  [{ci_lo:.5f}, {ci_hi:.5f}]")
print(f"\n2. SHAP top-5:")
for r in shap_results[:5]:
    v = f"{r['mean_abs_shap']:.6f}" if r["mean_abs_shap"] is not None else "N/A"
    print(f"   {r['rank']}. {r['feature']}: {v}")
print(f"   Sims in top-10: {sims_in_top10} | Zener in top-10: {zener_in_top10} | FT in top-10: {ft_in_top10}")
print(f"\n3. Spearman vs V4: {spearman_vs_v4}")
if spearman_vs_v4 is not None:
    print(f"   Gate < 0.85: {'PASS' if abs(spearman_vs_v4) < 0.85 else 'FAIL'}")
print(f"\n4. Estimated LB:")
print(f"   @K=200: {f1_200:.2f}  (TP={tp200}/66)")
print(f"   @K=216: {f1_216:.2f}  (TP={tp216}/66)")
print(f"   Best @K={best_oof_k}: {best_oof_score:.2f}")
print(f"   Gate >= 75 @K=200: {'PASS' if f1_200 >= 75.0 else 'FAIL'}")
print(f"\n5. Top-3 risks:")
print(f"   R1: V4 base lost 5 features — net signal may drop if physics doesn't compensate")
print(f"   R2: OOF→LB calibration unknown for physics-pure models (use HE formula, not delta)")
print(f"   R3: Fold-3 hard fold (13 val positives) — physics feature variance may amplify noise")
print(f"\n6. Ready for V51 consensus? {'YES' if gates_ok else 'CONDITIONAL — see gates'}")
print(f"\n   Files: {OUT}")
print("=" * 70)
