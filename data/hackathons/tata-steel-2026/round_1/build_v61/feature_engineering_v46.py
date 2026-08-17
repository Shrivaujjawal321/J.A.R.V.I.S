"""
feature_engineering_v46.py — Steel-Rolling Physics Feature Pipeline

Implements Ratnesh peer's 77.67 LB physics feature recipe:
  1. Zener-Hollomon Z per stand (10 features: logZ_1..6 + mean/std/F1F5drop/max/min)
  2. Sims Force Residual — MUST use Y=0 rows only in fold-train (7 features)
  3. Temperature curvature (1 feature) — stand-skip detector
  4. Force-Temperature coupling per stand (9 features)
  5. Monotonicity break counters (2 features)
  6. Cooling rates per stage (6 features: total + per-stage)

CRITICAL Sims design:
  - Ridge trained on Y=0 rows from TRAIN fold only (never val rows, never test labels)
  - 5-fold CV-isolated: val residuals use their fold's Ridge predictor
  - Test residuals averaged across all 5 fold-Ridge predictors
  - This is EXACTLY peer's pattern — any deviation risks leakage

Total physics features: ~28 static + 7 Sims (fold-isolated) = 35 new features
"""

from __future__ import annotations

import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge

# ── Column maps ───────────────────────────────────────────────────────────────
TEMP_COLS  = ["X4", "X5", "X6", "X7", "X8", "X9"]   # 6 stands
FORCE_COLS = ["X29", "X30", "X31", "X32", "X33"]      # 5 stands
AUX_COLS   = ["X10", "X11", "X12"]                    # Sims auxiliary regressors

# Physical constants
Q = 300_000.0   # Activation energy for hot rolling, J/mol
R_GAS = 8.314   # Gas constant, J/(mol·K)


# ═══════════════════════════════════════════════════════════════════════════════
# MODULE 1: STATIC PHYSICS FEATURES (no fold isolation needed)
# These are pure transformations of raw columns — no leakage risk.
# ═══════════════════════════════════════════════════════════════════════════════

def add_zener_hollomon(df: pd.DataFrame) -> pd.DataFrame:
    """
    Zener-Hollomon parameter Z = strain_rate × exp(Q/RT)
    log(Z) = log(strain_rate) + Q/(R*T_K)

    Stand temperatures X4..X9 in Celsius → convert to Kelvin.
    Strain_rate proxy: |diff to next stand's temp| + epsilon
    (peer's exact recipe — using inter-stand temp drop as proxy for strain rate)

    Produces: logZ_1..6 + logZ_mean + logZ_std + logZ_F1F5drop + logZ_max + logZ_min
    Total: 11 features
    """
    df = df.copy()

    t_cols = TEMP_COLS  # X4..X9
    logZ_cols = []

    for i, t_col in enumerate(t_cols):
        T_K = df[t_col] + 273.15

        # Strain rate proxy: absolute temp difference to neighbor stand
        if i == 0:
            strain_rate = (df["X4"] - df["X5"]).abs() + 1e-6
        elif i < 5:
            next_col = t_cols[i + 1]
            strain_rate = (df[t_col] - df[next_col]).abs() + 1e-6
        else:
            # Last stand (X9): use X8-X9 diff (same as peer)
            strain_rate = (df["X8"] - df["X9"]).abs() + 1e-6

        col_name = f"logZ_{i+1}"
        df[col_name] = np.log(strain_rate) + Q / (R_GAS * T_K)
        logZ_cols.append(col_name)

    # Aggregate features
    logZ_mat = df[logZ_cols]
    df["logZ_mean"]      = logZ_mat.mean(axis=1)
    df["logZ_std"]       = logZ_mat.std(axis=1)
    df["logZ_F1F5drop"]  = df["logZ_1"] - df["logZ_5"]   # entry vs exit Zener drop
    df["logZ_max"]       = logZ_mat.max(axis=1)
    df["logZ_min"]       = logZ_mat.min(axis=1)

    return df


ZENER_COLS = (
    [f"logZ_{i}" for i in range(1, 7)] +
    ["logZ_mean", "logZ_std", "logZ_F1F5drop", "logZ_max", "logZ_min"]
)  # 11 features


def add_temp_curvature(df: pd.DataFrame) -> pd.DataFrame:
    """
    Temperature curvature: X4 - 2*X6 + X9
    Detects stand-skip / non-linear temperature path.
    Defects may occur when curvature deviates from normal rolling.
    """
    df = df.copy()
    df["temp_curvature"] = df["X4"] - 2.0 * df["X6"] + df["X9"]
    return df


CURVATURE_COLS = ["temp_curvature"]  # 1 feature


def add_force_temp_coupling(df: pd.DataFrame) -> pd.DataFrame:
    """
    Force / (T_K) per stand — normalizes rolling force by temperature.
    High F/T → material harder than expected → potential defect precursor.

    5 per-stand couplings + max/mean/std/range = 9 features
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
    Count of non-monotonic transitions along the stand axis.

    Temp should decrease stand-by-stand (X4 > X5 > ... > X9).
    A temp break = X_i < X_{i+1} (unexpected temp rise)

    Force should generally increase (strip gets harder to roll as it thins).
    A force break = F_i > F_{i+1} (unexpected force drop)

    2 features: temp_mono_breaks, force_mono_breaks
    """
    df = df.copy()

    # Temperature monotonicity breaks (5 transitions: X4→X5, X5→X6, ..., X8→X9)
    temp_breaks = sum(
        (df[TEMP_COLS[i]] < df[TEMP_COLS[i + 1]]).astype(int)
        for i in range(5)
    )
    df["temp_mono_breaks"] = temp_breaks

    # Force monotonicity breaks (4 transitions: X29→X30, ..., X32→X33)
    force_breaks = sum(
        (df[FORCE_COLS[i]] > df[FORCE_COLS[i + 1]]).astype(int)
        for i in range(4)
    )
    df["force_mono_breaks"] = force_breaks

    return df


MONO_COLS = ["temp_mono_breaks", "force_mono_breaks"]  # 2 features


def add_cooling_rates(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cooling rates per stage.
    Total cooling = X4 - X9
    Per stage cool_rate_i = X{4+i} - X{4+i+1}

    6 features: cooling_rate_total + cool_rate_1..5
    """
    df = df.copy()
    df["cooling_rate_total"] = df["X4"] - df["X9"]

    for i in range(5):
        col_from = TEMP_COLS[i]      # X4, X5, X6, X7, X8
        col_to   = TEMP_COLS[i + 1]  # X5, X6, X7, X8, X9
        df[f"cool_rate_{i+1}"] = df[col_from] - df[col_to]

    return df


COOLING_COLS = ["cooling_rate_total"] + [f"cool_rate_{i}" for i in range(1, 6)]  # 6 features


# Combine all static physics features
STATIC_PHYSICS_COLS = ZENER_COLS + CURVATURE_COLS + FT_COUPLING_COLS + MONO_COLS + COOLING_COLS
# 11 + 1 + 9 + 2 + 6 = 29 static features


def add_static_physics_features(df: pd.DataFrame) -> pd.DataFrame:
    """Apply all static physics transformations (no fold isolation needed)."""
    df = add_zener_hollomon(df)
    df = add_temp_curvature(df)
    df = add_force_temp_coupling(df)
    df = add_monotonicity_breaks(df)
    df = add_cooling_rates(df)
    return df


# ═══════════════════════════════════════════════════════════════════════════════
# MODULE 2: SIMS FORCE RESIDUAL (fold-isolated, MUST use Y=0 only in fold-train)
# ═══════════════════════════════════════════════════════════════════════════════

SIMS_RESIDUAL_COLS = (
    [f"sims_res_{i}" for i in range(1, 6)] +
    ["sims_abs_max", "sims_abs_mean"]
)  # 7 features


def compute_sims_residuals(
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    y_train: np.ndarray,
    fold_assign: np.ndarray,
    n_folds: int = 5,
    ridge_alpha: float = 1.0,
    verbose: bool = True,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Sims-inspired force residual: per-stand Ridge of F_stand ~ (T_stand, X10, X11, X12).
    Trained ONLY on Y=0 rows from the training portion of each fold.

    Residual = F_actual - F_normal_predicted_by_Ridge

    Positive residual → higher force than normal process expects → potential defect precursor.
    Negative residual → lower force (unusual but captured).

    CRITICAL DESIGN:
      - Ridge fit on Y=0 rows ONLY → Ridge learns "normal" process
      - Applied to val fold → residual captures "how far from normal is this coil?"
      - Test: average of all 5 fold-Ridge predictors (no leakage since test has no labels)

    Args:
        train_df: raw train DataFrame (must contain FORCE_COLS, TEMP_COLS, AUX_COLS)
        test_df:  raw test DataFrame
        y_train:  binary labels (1352,) — used ONLY to restrict to Y=0 in fold-train
        fold_assign: int array (1352,) — fold index 0..4 for each train row
        n_folds: number of folds (must match fold_assign range)
        ridge_alpha: Ridge regularization strength

    Returns:
        R_tr: (1352, 5) OOF residuals for each of the 5 force stands
        R_te: (339, 5) Test residuals averaged across all fold models
    """
    n_train = len(train_df)
    n_test  = len(test_df)
    n_stands = len(FORCE_COLS)

    R_tr = np.zeros((n_train, n_stands))
    R_te = np.zeros((n_test,  n_stands))

    aux_cols   = AUX_COLS
    force_cols = FORCE_COLS
    temp_cols  = TEMP_COLS[:5]  # X4..X8 (one per force stand)

    for f in range(n_folds):
        ti_mask  = (fold_assign != f)   # training portion (k-1 folds)
        val_mask = (fold_assign == f)   # validation portion (this fold)

        neg_mask_in_ti = ti_mask & (y_train == 0)  # Y=0 AND in train portion

        n_neg = int(neg_mask_in_ti.sum())
        n_val = int(val_mask.sum())

        if verbose:
            print(f"  Sims fold {f+1}: train-neg={n_neg}, val={n_val}")

        for s in range(n_stands):
            f_col = force_cols[s]
            t_col = temp_cols[s]
            feature_cols = [t_col] + aux_cols  # [T_stand, X10, X11, X12]

            X_neg = train_df.loc[neg_mask_in_ti, feature_cols].values.astype(float)
            y_neg = train_df.loc[neg_mask_in_ti, f_col].values.astype(float)

            ridge = Ridge(alpha=ridge_alpha, fit_intercept=True)
            ridge.fit(X_neg, y_neg)

            # Apply to validation fold
            X_val = train_df.loc[val_mask, feature_cols].values.astype(float)
            F_val = train_df.loc[val_mask, f_col].values.astype(float)
            R_tr[val_mask, s] = F_val - ridge.predict(X_val)

            # Accumulate test predictions (average across folds at the end)
            X_te = test_df[feature_cols].values.astype(float)
            F_te = test_df[f_col].values.astype(float)
            R_te[:, s] += (F_te - ridge.predict(X_te)) / n_folds

    return R_tr, R_te


def attach_sims_residuals(
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    R_tr: np.ndarray,  # (1352, 5)
    R_te: np.ndarray,  # (339, 5)
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Attach Sims residuals + aggregates to train/test DataFrames.
    Returns copies with 7 new columns appended.
    """
    train_out = train_df.copy()
    test_out  = test_df.copy()

    for s in range(len(FORCE_COLS)):
        col = f"sims_res_{s+1}"
        train_out[col] = R_tr[:, s]
        test_out[col]  = R_te[:, s]

    train_out["sims_abs_max"]  = np.abs(R_tr).max(axis=1)
    train_out["sims_abs_mean"] = np.abs(R_tr).mean(axis=1)
    test_out["sims_abs_max"]   = np.abs(R_te).max(axis=1)
    test_out["sims_abs_mean"]  = np.abs(R_te).mean(axis=1)

    return train_out, test_out


# ── All new physics feature column names (static only — Sims is fold-isolated) ──
ALL_STATIC_PHYSICS_COLS = STATIC_PHYSICS_COLS  # 29
ALL_SIMS_COLS = SIMS_RESIDUAL_COLS             # 7
ALL_NEW_PHYSICS_COLS = ALL_STATIC_PHYSICS_COLS + ALL_SIMS_COLS  # 36 total


if __name__ == "__main__":
    import json
    from pathlib import Path

    ROOT   = Path("/home/ujjwal/Documents/J.A.R.V.I.S./data/hackathons/tata-steel-2026/round_1")
    V4_DIR = ROOT / "build_v4"

    train = pd.read_parquet(V4_DIR / "train_v4.parquet")
    test  = pd.read_parquet(V4_DIR / "test_v4.parquet")

    print("Testing static physics feature pipeline...")
    train_fe = add_static_physics_features(train)
    test_fe  = add_static_physics_features(test)

    print(f"Train shape: {train_fe.shape} (added {train_fe.shape[1] - train.shape[1]} cols)")
    print(f"Test  shape: {test_fe.shape}")

    # Verify all static cols present
    missing_tr = [c for c in ALL_STATIC_PHYSICS_COLS if c not in train_fe.columns]
    missing_te = [c for c in ALL_STATIC_PHYSICS_COLS if c not in test_fe.columns]
    print(f"Missing static cols in train: {missing_tr}")
    print(f"Missing static cols in test:  {missing_te}")

    # Quick sanity: logZ range should be ~30-40 for typical hot rolling temps
    print(f"\nlogZ_1 range: [{train_fe['logZ_1'].min():.2f}, {train_fe['logZ_1'].max():.2f}]")
    print(f"temp_curvature range: [{train_fe['temp_curvature'].min():.2f}, {train_fe['temp_curvature'].max():.2f}]")
    print(f"ft_coupling_1 range: [{train_fe['ft_coupling_1'].min():.6f}, {train_fe['ft_coupling_1'].max():.6f}]")
    print(f"temp_mono_breaks range: [{int(train_fe['temp_mono_breaks'].min())}, {int(train_fe['temp_mono_breaks'].max())}]")
    print(f"cooling_rate_total range: [{train_fe['cooling_rate_total'].min():.2f}, {train_fe['cooling_rate_total'].max():.2f}]")

    print(f"\nAll {len(ALL_STATIC_PHYSICS_COLS)} static physics cols: {ALL_STATIC_PHYSICS_COLS}")
    print(f"\nSims cols (fold-isolated, not computed here): {ALL_SIMS_COLS}")
    print(f"\nTotal new physics cols: {len(ALL_NEW_PHYSICS_COLS)}")
    print("\nStatic pipeline OK.")
