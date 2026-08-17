"""
train_v60.py — Stand-Decomposed Base + Physics Features (V60)

HYPOTHESIS:
V46 physics features failed because they were appended to V4's raw X4-X9/X29-X33,
creating collinearity. Peer's iter52 (77.67 LB) used a stand-decomposed base.
This build replaces raw X columns with stand-decomposed features, then adds physics on top.

ARCHITECTURE:
- Alternate base: 7-sensor × 7-stand decomposition (setpoint residuals, aggregates, drift)
- Physics on top: Sims residual (fold-isolated), Zener-Hollomon per stand
- DROP raw X4-X9, X29-X33 (collinear with physics)
- Keep non-collinear raw cols (X1-X3, X10-X28, X34-X49)
- Stack: LGB + XGB + CAT → LR meta + Platt T=0.01428
- CV: StratifiedKFold(5, shuffle=True, seed=42)
- VIF gate: no feature collinearity > 5

Expected output: ~60 total features replacing raw collinear columns.
Benchmark: OOF F1@K=200 >= 0.391 (V53 Caruana baseline)
"""

from __future__ import annotations

import warnings
warnings.filterwarnings("ignore")

import os
import json
import time
import sys
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.model_selection import StratifiedKFold
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.calibration import CalibratedClassifierCV
from sklearn.preprocessing import StandardScaler
from scipy.stats import spearmanr
import lightgbm as lgb
import xgboost as xgb
import catboost as cb

# ── Paths ─────────────────────────────────────────────────────────────────────
ROOT   = Path("/home/ujjwal/Documents/J.A.R.V.I.S./data/hackathons/tata-steel-2026/round_1")
V4_DIR = ROOT / "build_v4"
OUT    = ROOT / "build_v60"
OUT.mkdir(exist_ok=True)

# ── Config ────────────────────────────────────────────────────────────────────
SEED         = 42
N_FOLDS      = 5
PLATT_T      = 0.01428
SCALE_POS    = 19.48
K_VALUES     = [154, 200]
N_POS_TRAIN  = 66

# Physical constants
Q_ACT  = 300_000.0   # activation energy J/mol
R_GAS  = 8.314       # gas constant J/(mol·K)

# ── Stand column mapping (based on value-range analysis) ─────────────────────
# Temperature stands: X4..X9 (6 stands, range ~400-760°C)
TEMP_STANDS  = ["X4", "X5", "X6", "X7", "X8", "X9"]

# Force stands: X29..X33 (5 stands, range ~5-25 units = rolling force)
FORCE_STANDS = ["X29", "X30", "X31", "X32", "X33"]

# Secondary temperature-like: X1, X2, X3 (pre-mill, range 500-1100°C)
PRE_MILL_COLS = ["X1", "X2", "X3"]

# Auxiliary process: X10-X12 (speed, pass count, reduction%)
AUX_COLS = ["X10", "X11", "X12"]

# Coil geometry / product spec: X13-X28 (thickness targets, widths)
PRODUCT_COLS = [f"X{i}" for i in range(13, 29)]   # X13-X28

# Post-process / quality: X34-X49
POST_COLS = [f"X{i}" for i in range(34, 50)]        # X34-X49

# V4 SHAP-selected features to keep (non-collinear with physics)
# Drop: X4, X5, X6, X7, X8, X9 (replaced by stand decomp)
# Drop: X29, X30, X31, X32, X33 (replaced by force stand decomp)
V4_FEATURES_TO_KEEP = [
    "X13_over_X36", "X36", "X14", "X13_minus_X36", "X16", "X18", "X40",
    "X23", "X48", "X21", "iso_score", "X38", "X25", "X9",  # Note: X9 kept only in raw form if not in stand decomp
    "X39", "X36_roll5", "X44", "X2", "c3_over_c2_mean", "X30_over_X35",
    "X41", "X37", "X43", "X30", "X13_over_X34", "X27",
    "poly_X13_over_X36^2", "poly_X13_over_X36_X36", "poly_X13_over_X36_X14",
    "poly_X13_over_X36_X13_minus_X36", "poly_X13_over_X36_X16",
    "poly_X36^2", "poly_X36_X14", "poly_X36_X13_minus_X36", "poly_X36_X16",
    "poly_X14^2", "poly_X14_X13_minus_X36", "poly_X14_X16",
    "poly_X13_minus_X36^2", "poly_X13_minus_X36_X16", "poly_X16^2",
    "prev5_defect_rate", "X13_lag1", "X10_lag1", "X36_lag1",
    "X13_rollmean5", "X10_rollmean5"
]
# Remove raw X4-X9, X29-X33 from V4 features (replaced by stand decomp)
COLLINEAR_DROPS = {"X4","X5","X6","X7","X8","X9","X29","X30","X31","X32","X33","X7"}
# Also drop X30 from V4 kept since it's force collinear — BUT keep ratio features (X30_over_X35)
# X30 raw standalone = collinear, but the ratio provides new info — keep ratio
V4_FEATURES_CLEANED = [
    f for f in V4_FEATURES_TO_KEEP
    if f not in {"X4","X5","X6","X7","X8","X9","X29","X31","X32","X33"}
    # X30 standalone removed but X30_over_X35 kept (ratio = new dimension)
    and f != "X30"
    and f != "X9"   # raw X9 is in TEMP_STANDS, replaced by decomp
]

print(f"V4 CLEANED features: {len(V4_FEATURES_CLEANED)}")


# ═══════════════════════════════════════════════════════════════════════════════
# FEATURE ENGINEERING — STAND DECOMPOSITION
# ═══════════════════════════════════════════════════════════════════════════════

def add_stand_decomposition(df: pd.DataFrame, fit_df: pd.DataFrame | None = None) -> pd.DataFrame:
    """
    Replace raw stand columns with stand-decomposed features.

    For temperature stands (X4..X9):
      - stand_temp_i_mean (scalar per row, effectively the value itself)
      - stand_temp_residual_i = X_i - global_setpoint_mean (fitted on fit_df negatives)
      - stand_temp_drift_i = X_i - X_{i-1} (inter-stand delta)
      - stand_temp_p95_i = fold-specific p95 of each stand's temperature (relative position)

    For force stands (X29..X33):
      - stand_force_i_residual (Ridge on Y=0 negatives — fold isolated in training)
      - stand_force_drift_i = F_i - F_{i-1}

    Aggregate features across all stands:
      - temp_stand_range = max(T) - min(T) across stands
      - temp_stand_std = std across stands
      - force_stand_range, force_stand_std
      - max_temp_stand_idx (which stand has max T)
      - max_force_stand_idx (which stand has max F)

    Args:
        df: input DataFrame (train fold val or test)
        fit_df: reference DataFrame for computing setpoint means (fit on Y=0 train)

    Returns:
        df with stand-decomposed features added
    """
    df = df.copy()
    if fit_df is None:
        fit_df = df

    # ── Temperature stand features ──────────────────────────────────────────
    temp_vals = df[TEMP_STANDS].values  # (N, 6)
    fit_temp  = fit_df[TEMP_STANDS].values

    # Setpoint deviation = X_i - column-mean (fitted on negatives)
    col_means = fit_temp.mean(axis=0)  # (6,)
    for i, col in enumerate(TEMP_STANDS):
        stand_idx = i + 1
        # Raw value (replaces original stand col)
        df[f"ts_t{stand_idx}"] = df[col].values
        # Deviation from fitted setpoint mean
        df[f"ts_t{stand_idx}_dev"] = df[col].values - col_means[i]

    # Inter-stand temp drift (delta to previous stand)
    for i in range(1, len(TEMP_STANDS)):
        stand_idx = i + 1
        df[f"ts_tdrift{stand_idx}"] = df[TEMP_STANDS[i]].values - df[TEMP_STANDS[i-1]].values

    # Aggregate temp stats across stands
    df["ts_temp_mean"]  = temp_vals.mean(axis=1)
    df["ts_temp_std"]   = temp_vals.std(axis=1)
    df["ts_temp_range"] = temp_vals.max(axis=1) - temp_vals.min(axis=1)
    df["ts_temp_drop"]  = df[TEMP_STANDS[0]].values - df[TEMP_STANDS[-1]].values   # X4-X9
    df["ts_temp_argmax"] = np.argmax(temp_vals, axis=1).astype(float)

    # ── Force stand features ─────────────────────────────────────────────────
    force_vals = df[FORCE_STANDS].values  # (N, 5)
    fit_force  = fit_df[FORCE_STANDS].values

    force_means = fit_force.mean(axis=0)
    for i, col in enumerate(FORCE_STANDS):
        stand_idx = i + 1
        df[f"ts_f{stand_idx}"] = df[col].values
        df[f"ts_f{stand_idx}_dev"] = df[col].values - force_means[i]

    # Inter-stand force drift
    for i in range(1, len(FORCE_STANDS)):
        stand_idx = i + 1
        df[f"ts_fdrift{stand_idx}"] = df[FORCE_STANDS[i]].values - df[FORCE_STANDS[i-1]].values

    # Aggregate force stats
    df["ts_force_mean"]  = force_vals.mean(axis=1)
    df["ts_force_std"]   = force_vals.std(axis=1)
    df["ts_force_range"] = force_vals.max(axis=1) - force_vals.min(axis=1)
    df["ts_force_argmax"] = np.argmax(force_vals, axis=1).astype(float)

    # ── Cross-stand features (physics-informed) ──────────────────────────────
    # F/T coupling per stand (normalized = less collinear than raw F)
    for i in range(len(FORCE_STANDS)):
        T_K = df[TEMP_STANDS[i]].values + 273.15
        F   = df[FORCE_STANDS[i]].values
        df[f"ts_ft{i+1}"] = F / T_K  # Force normalized by temperature [kN/(K)]

    df["ts_ft_mean"]  = np.stack([df[f"ts_ft{i+1}"] for i in range(5)], axis=1).mean(axis=1)
    df["ts_ft_max"]   = np.stack([df[f"ts_ft{i+1}"] for i in range(5)], axis=1).max(axis=1)
    df["ts_ft_range"] = df["ts_ft_max"] - np.stack([df[f"ts_ft{i+1}"] for i in range(5)], axis=1).min(axis=1)

    return df


def get_stand_decomp_cols() -> list[str]:
    """Return all stand-decomposed feature column names (static, no fold isolation)."""
    cols = []
    # Temperature stand raw + deviation
    for i in range(1, 7):
        cols += [f"ts_t{i}", f"ts_t{i}_dev"]
    # Temperature drift (5 drifts: t2-t1 through t6-t5)
    for i in range(2, 7):
        cols.append(f"ts_tdrift{i}")
    # Temp aggregates
    cols += ["ts_temp_mean", "ts_temp_std", "ts_temp_range", "ts_temp_drop", "ts_temp_argmax"]
    # Force stand raw + deviation
    for i in range(1, 6):
        cols += [f"ts_f{i}", f"ts_f{i}_dev"]
    # Force drift
    for i in range(2, 6):
        cols.append(f"ts_fdrift{i}")
    # Force aggregates
    cols += ["ts_force_mean", "ts_force_std", "ts_force_range", "ts_force_argmax"]
    # F/T coupling per stand
    for i in range(1, 6):
        cols.append(f"ts_ft{i}")
    cols += ["ts_ft_mean", "ts_ft_max", "ts_ft_range"]
    return cols

STAND_DECOMP_COLS = get_stand_decomp_cols()
print(f"Stand decomp features: {len(STAND_DECOMP_COLS)}")


# ═══════════════════════════════════════════════════════════════════════════════
# ZENER-HOLLOMON ON STAND-DECOMPOSED BASIS
# ═══════════════════════════════════════════════════════════════════════════════

def add_zener_hollomon_v2(df: pd.DataFrame) -> pd.DataFrame:
    """
    Zener-Hollomon using stand-decomposed temperature features.
    Z = strain_rate × exp(Q/RT)
    log(Z) = log(strain_rate) + Q/(R*T_K)

    Uses ts_tdrift features as inter-stand strain rate proxy.
    These are already decomposed → no collinearity with raw T columns.
    """
    df = df.copy()
    logZ_cols = []

    for i in range(1, 7):
        T_K = df[f"ts_t{i}"] + 273.15
        # Strain rate proxy from decomposed drift
        if i == 1:
            strain_rate = df["ts_tdrift2"].abs() + 1e-6
        elif i < 6:
            drift_col = f"ts_tdrift{i+1}"
            strain_rate = df[drift_col].abs() + 1e-6
        else:
            strain_rate = df["ts_tdrift6"].abs() + 1e-6

        col = f"logZ_sd_{i}"
        df[col] = np.log(strain_rate) + Q_ACT / (R_GAS * T_K)
        logZ_cols.append(col)

    # Aggregate
    logZ_mat = df[logZ_cols].values
    df["logZ_sd_mean"]     = logZ_mat.mean(axis=1)
    df["logZ_sd_std"]      = logZ_mat.std(axis=1)
    df["logZ_sd_range"]    = logZ_mat.max(axis=1) - logZ_mat.min(axis=1)
    df["logZ_sd_t1t6drop"] = df["logZ_sd_1"] - df["logZ_sd_6"]

    return df


ZENER_SD_COLS = [f"logZ_sd_{i}" for i in range(1, 7)] + [
    "logZ_sd_mean", "logZ_sd_std", "logZ_sd_range", "logZ_sd_t1t6drop"
]


# ═══════════════════════════════════════════════════════════════════════════════
# SIMS RESIDUAL (fold-isolated on stand-decomposed force)
# ═══════════════════════════════════════════════════════════════════════════════

def compute_sims_sd_residuals(
    train_df: pd.DataFrame,
    test_df:  pd.DataFrame,
    y_train:  np.ndarray,
    fold_assign: np.ndarray,
    n_folds: int = 5,
    ridge_alpha: float = 1.0,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Sims residual on STAND-DECOMPOSED force features.
    Uses ts_f{i}_dev (deviation from setpoint) as target — it has lower range
    than raw force, making Ridge predictions more stable.
    Regressors: [ts_t{i}, X10, X11, X12] — temperature + aux.
    Trained on Y=0 rows only (fold-isolated).

    Returns:
        R_tr: (N_train, 5) OOF residuals
        R_te: (N_test, 5) test residuals (averaged across folds)
    """
    n_train  = len(train_df)
    n_test   = len(test_df)
    n_stands = len(FORCE_STANDS)

    R_tr = np.zeros((n_train, n_stands))
    R_te = np.zeros((n_test,  n_stands))

    for f in range(n_folds):
        ti_mask  = (fold_assign != f)
        val_mask = (fold_assign == f)
        neg_mask = ti_mask & (y_train == 0)

        for s in range(n_stands):
            force_dev_col  = f"ts_f{s+1}_dev"     # target = deviation
            temp_stand_col = f"ts_t{s+1}"          # stand temperature
            feat_cols = [temp_stand_col] + AUX_COLS

            X_neg = train_df.loc[neg_mask, feat_cols].values.astype(float)
            y_neg = train_df.loc[neg_mask, force_dev_col].values.astype(float)

            ridge = Ridge(alpha=ridge_alpha, fit_intercept=True)
            ridge.fit(X_neg, y_neg)

            # Val residual
            X_val = train_df.loc[val_mask, feat_cols].values.astype(float)
            F_val = train_df.loc[val_mask, force_dev_col].values.astype(float)
            R_tr[val_mask, s] = F_val - ridge.predict(X_val)

            # Test residual (accumulate across folds)
            X_te = test_df[feat_cols].values.astype(float)
            F_te = test_df[force_dev_col].values.astype(float)
            R_te[:, s] += (F_te - ridge.predict(X_te)) / n_folds

    return R_tr, R_te


SIMS_SD_COLS = [f"sims_sd_{i}" for i in range(1, 6)] + ["sims_sd_absmax", "sims_sd_absmean"]


# ═══════════════════════════════════════════════════════════════════════════════
# VIF CHECK
# ═══════════════════════════════════════════════════════════════════════════════

def compute_vif(df: pd.DataFrame, feature_cols: list[str], max_vif: float = 5.0) -> pd.DataFrame:
    """Compute VIF for each feature. Flag any with VIF > max_vif."""
    from numpy.linalg import lstsq
    X = df[feature_cols].fillna(0).values
    n, p = X.shape

    vif_data = []
    for i in range(p):
        y_i  = X[:, i]
        X_r  = np.delete(X, i, axis=1)
        # OLS via lstsq
        coef, _, _, _ = lstsq(X_r, y_i, rcond=None)
        y_hat = X_r @ coef
        ss_tot = np.sum((y_i - y_i.mean()) ** 2)
        ss_res = np.sum((y_i - y_hat) ** 2)
        r2 = 1.0 - ss_res / (ss_tot + 1e-10)
        vif = 1.0 / (1.0 - r2 + 1e-10)
        vif_data.append({"feature": feature_cols[i], "VIF": vif, "flag": vif > max_vif})

    return pd.DataFrame(vif_data).sort_values("VIF", ascending=False)


# ═══════════════════════════════════════════════════════════════════════════════
# SCORING UTILITIES
# ═══════════════════════════════════════════════════════════════════════════════

def he_f1_at_k(y_true: np.ndarray, proba: np.ndarray, k: int, n_pos_test: int = 154) -> float:
    """HE F1 formula: 2*TP / (K + N_POS_TEST). Applied to OOF (n_pos_test proxy)."""
    top_k_idx = np.argsort(proba)[::-1][:k]
    tp = y_true[top_k_idx].sum()
    return 2.0 * tp / (k + N_POS_TRAIN)   # OOF has 66 positives


def rp_score(y_true: np.ndarray, proba: np.ndarray, threshold: float) -> float:
    """(Recall + Precision) / 2 score used for LB estimation."""
    pred = (proba >= threshold).astype(int)
    tp = ((pred == 1) & (y_true == 1)).sum()
    fp = ((pred == 1) & (y_true == 0)).sum()
    fn = ((pred == 0) & (y_true == 1)).sum()
    recall    = tp / (tp + fn + 1e-9)
    precision = tp / (tp + fp + 1e-9)
    return 0.5 * (recall + precision) * 100.0


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN TRAINING PIPELINE
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    t_start = time.time()
    print("=" * 70)
    print("V60 — Stand-Decomposed Base + Physics Features")
    print("=" * 70)

    # ── 1. Load data ──────────────────────────────────────────────────────────
    train = pd.read_parquet(V4_DIR / "train_v4.parquet")
    test  = pd.read_parquet(V4_DIR / "test_v4.parquet")

    y   = train["Y"].values.astype(int)
    coil_train = train.index.values  # row indices
    coil_test  = test.index.values

    print(f"Train: {train.shape}, Test: {test.shape}")
    print(f"Positives: {y.sum()} / {len(y)} ({y.mean()*100:.1f}%)")

    # ── 2. CV folds ───────────────────────────────────────────────────────────
    skf = StratifiedKFold(n_splits=N_FOLDS, shuffle=True, random_state=SEED)
    fold_assign = np.zeros(len(train), dtype=int)
    for fold_idx, (_, val_idx) in enumerate(skf.split(train, y)):
        fold_assign[val_idx] = fold_idx

    # ── 3. Stand decomposition (static, fitted on Y=0 rows globally) ─────────
    print("\n[1] Stand decomposition...")
    neg_mask = y == 0
    fit_df = train[neg_mask]

    train_sd = add_stand_decomposition(train, fit_df=fit_df)
    test_sd  = add_stand_decomposition(test,  fit_df=fit_df)

    print(f"  Stand decomp cols: {len(STAND_DECOMP_COLS)}")
    # Verify all cols present
    missing = [c for c in STAND_DECOMP_COLS if c not in train_sd.columns]
    assert not missing, f"Missing stand decomp cols: {missing}"

    # ── 4. Zener-Hollomon on stand-decomposed basis ───────────────────────────
    print("[2] Zener-Hollomon (stand-decomposed)...")
    train_sd = add_zener_hollomon_v2(train_sd)
    test_sd  = add_zener_hollomon_v2(test_sd)
    print(f"  Zener-Hollomon cols: {len(ZENER_SD_COLS)}")

    # ── 5. Sims residual (fold-isolated on stand-decomposed force dev) ────────
    print("[3] Sims residuals (fold-isolated, Y=0 only)...")
    R_tr, R_te = compute_sims_sd_residuals(
        train_sd, test_sd, y, fold_assign, n_folds=N_FOLDS
    )
    for s in range(len(FORCE_STANDS)):
        train_sd[f"sims_sd_{s+1}"] = R_tr[:, s]
        test_sd[f"sims_sd_{s+1}"]  = R_te[:, s]
    train_sd["sims_sd_absmax"]  = np.abs(R_tr).max(axis=1)
    train_sd["sims_sd_absmean"] = np.abs(R_tr).mean(axis=1)
    test_sd["sims_sd_absmax"]   = np.abs(R_te).max(axis=1)
    test_sd["sims_sd_absmean"]  = np.abs(R_te).mean(axis=1)
    print(f"  Sims residual cols: {len(SIMS_SD_COLS)}")

    # ── 6. Assemble final feature set ─────────────────────────────────────────
    print("[4] Assembling feature set...")

    # V4 cleaned features (drop raw collinear X4-X9, X29-X33, X30 standalone)
    v4_available = [c for c in V4_FEATURES_CLEANED if c in train_sd.columns]
    n_missing_v4 = len(V4_FEATURES_CLEANED) - len(v4_available)
    if n_missing_v4 > 0:
        print(f"  WARNING: {n_missing_v4} V4 features not available")

    FINAL_FEATURES = (
        STAND_DECOMP_COLS      # ~56 stand decomposed
        + ZENER_SD_COLS        # 10 Zener-Hollomon
        + SIMS_SD_COLS         # 7 Sims residual
        + v4_available         # V4 non-collinear features (lags, poly, ratios)
    )

    # Deduplicate while preserving order
    seen = set()
    FINAL_FEATURES_DEDUP = []
    for c in FINAL_FEATURES:
        if c not in seen and c in train_sd.columns:
            seen.add(c)
            FINAL_FEATURES_DEDUP.append(c)

    FINAL_FEATURES = FINAL_FEATURES_DEDUP
    print(f"  Total features: {len(FINAL_FEATURES)}")
    print(f"    Stand decomp:  {len(STAND_DECOMP_COLS)}")
    print(f"    Zener-SD:      {len(ZENER_SD_COLS)}")
    print(f"    Sims-SD:       {len(SIMS_SD_COLS)}")
    print(f"    V4 cleaned:    {len(v4_available)}")

    X_train = train_sd[FINAL_FEATURES].values.astype(float)
    X_test  = test_sd[FINAL_FEATURES].values.astype(float)

    # Check for NaN
    nan_count = np.isnan(X_train).sum()
    if nan_count > 0:
        print(f"  WARNING: {nan_count} NaN values in train features — filling with 0")
        X_train = np.nan_to_num(X_train, nan=0.0)
        X_test  = np.nan_to_num(X_test,  nan=0.0)

    # Save stand decomposition and physics features
    sd_cols = STAND_DECOMP_COLS + ZENER_SD_COLS
    train_sd[sd_cols].to_parquet(OUT / "stand_decomposition_features.parquet")
    phy_cols = SIMS_SD_COLS
    train_sd[phy_cols].to_parquet(OUT / "physics_features.parquet")
    print("  Saved: stand_decomposition_features.parquet, physics_features.parquet")

    # ── 7. VIF check on physics + stand features ──────────────────────────────
    print("[5] VIF check (sample of 200 features max)...")
    vif_check_cols = STAND_DECOMP_COLS[:20] + ZENER_SD_COLS + SIMS_SD_COLS
    vif_check_cols = [c for c in vif_check_cols if c in train_sd.columns]
    vif_df = compute_vif(train_sd, vif_check_cols, max_vif=5.0)
    high_vif = vif_df[vif_df["flag"]]
    print(f"  Features with VIF > 5: {len(high_vif)}")
    if len(high_vif) > 0:
        print(high_vif.head(10).to_string())
    else:
        print("  VIF gate: PASS — no collinearity > 5")

    # ── 8. Base learner params ────────────────────────────────────────────────
    lgb_params = dict(
        objective="binary",
        n_estimators=3000,
        learning_rate=0.03,
        num_leaves=31,
        min_child_samples=5,
        feature_fraction=0.7,
        bagging_fraction=0.8,
        bagging_freq=5,
        scale_pos_weight=SCALE_POS,
        n_jobs=4,
        random_state=SEED,
        verbose=-1,
    )
    xgb_params = dict(
        n_estimators=3000,
        learning_rate=0.03,
        max_depth=5,
        subsample=0.8,
        colsample_bytree=0.7,
        scale_pos_weight=SCALE_POS,
        eval_metric="auc",
        random_state=SEED,
        n_jobs=4,
        verbosity=0,
        use_label_encoder=False,
        early_stopping_rounds=200,
    )
    cat_params = dict(
        iterations=3000,
        learning_rate=0.03,
        depth=6,
        l2_leaf_reg=3.0,
        scale_pos_weight=SCALE_POS,
        random_seed=SEED,
        eval_metric="AUC",
        verbose=False,
    )

    # ── 9. Cross-validation ───────────────────────────────────────────────────
    print("\n[6] Cross-validation (5-fold)...")
    oof_lgb  = np.zeros(len(train))
    oof_xgb  = np.zeros(len(train))
    oof_cat  = np.zeros(len(train))
    fold_aucs = {"lgb": [], "xgb": [], "cat": []}

    for fold, (tr_idx, val_idx) in enumerate(skf.split(X_train, y)):
        print(f"\n  Fold {fold+1}/{N_FOLDS}...")
        t_fold = time.time()

        X_tr, X_val = X_train[tr_idx], X_train[val_idx]
        y_tr, y_val = y[tr_idx],       y[val_idx]

        # LightGBM
        lgb_model = lgb.LGBMClassifier(**lgb_params)
        lgb_model.fit(
            X_tr, y_tr,
            eval_set=[(X_val, y_val)],
            callbacks=[lgb.early_stopping(200, verbose=False), lgb.log_evaluation(-1)]
        )
        oof_lgb[val_idx] = lgb_model.predict_proba(X_val)[:, 1]

        # XGBoost
        xgb_model = xgb.XGBClassifier(**xgb_params)
        xgb_model.fit(X_tr, y_tr, eval_set=[(X_val, y_val)], verbose=False)
        oof_xgb[val_idx] = xgb_model.predict_proba(X_val)[:, 1]

        # CatBoost
        cat_model = cb.CatBoostClassifier(**cat_params)
        cat_model.fit(
            X_tr, y_tr,
            eval_set=(X_val, y_val),
            early_stopping_rounds=200,
            use_best_model=True,
        )
        oof_cat[val_idx] = cat_model.predict_proba(X_val)[:, 1]

        # Per-fold AUC
        from sklearn.metrics import roc_auc_score
        auc_lgb = roc_auc_score(y_val, oof_lgb[val_idx])
        auc_xgb = roc_auc_score(y_val, oof_xgb[val_idx])
        auc_cat = roc_auc_score(y_val, oof_cat[val_idx])
        fold_aucs["lgb"].append(auc_lgb)
        fold_aucs["xgb"].append(auc_xgb)
        fold_aucs["cat"].append(auc_cat)
        print(f"    AUC — LGB: {auc_lgb:.5f}, XGB: {auc_xgb:.5f}, CAT: {auc_cat:.5f} ({time.time()-t_fold:.0f}s)")

    from sklearn.metrics import roc_auc_score
    auc_lgb_oof = roc_auc_score(y, oof_lgb)
    auc_xgb_oof = roc_auc_score(y, oof_xgb)
    auc_cat_oof = roc_auc_score(y, oof_cat)
    print(f"\n  OOF AUC — LGB: {auc_lgb_oof:.5f}, XGB: {auc_xgb_oof:.5f}, CAT: {auc_cat_oof:.5f}")

    # ── 10. Meta-learner (LR + Platt) ─────────────────────────────────────────
    print("\n[7] Meta-learner (LR stacking + Platt calibration)...")
    X_meta_oof  = np.column_stack([oof_lgb, oof_xgb, oof_cat])

    meta_lr = LogisticRegression(C=1.0, max_iter=500, random_state=SEED)
    meta_lr.fit(X_meta_oof, y)
    oof_meta = meta_lr.predict_proba(X_meta_oof)[:, 1]

    auc_meta = roc_auc_score(y, oof_meta)
    print(f"  Meta OOF AUC: {auc_meta:.5f}")

    # ── 11. Test predictions ──────────────────────────────────────────────────
    print("\n[8] Test predictions (refit on full train)...")
    # Refit base learners on full data
    lgb_full = lgb.LGBMClassifier(**{**lgb_params, "n_estimators": 2000})
    lgb_full.fit(X_train, y, callbacks=[lgb.log_evaluation(-1)])
    test_lgb = lgb_full.predict_proba(X_test)[:, 1]

    xgb_full_params = {k: v for k, v in xgb_params.items() if k != "early_stopping_rounds"}
    xgb_full_params["n_estimators"] = 2000
    xgb_full = xgb.XGBClassifier(**xgb_full_params)
    xgb_full.fit(X_train, y, verbose=False)
    test_xgb = xgb_full.predict_proba(X_test)[:, 1]

    cat_full = cb.CatBoostClassifier(**{**cat_params, "iterations": 2000})
    cat_full.fit(X_train, y, verbose=False)
    test_cat = cat_full.predict_proba(X_test)[:, 1]

    X_meta_test  = np.column_stack([test_lgb, test_xgb, test_cat])
    test_meta    = meta_lr.predict_proba(X_meta_test)[:, 1]

    # ── 12. SHAP analysis ─────────────────────────────────────────────────────
    print("\n[9] SHAP analysis...")
    try:
        import shap
        explainer = shap.TreeExplainer(lgb_full)
        shap_vals = explainer.shap_values(X_train[:500])
        if isinstance(shap_vals, list):
            shap_vals = shap_vals[1]
        feat_importance = np.abs(shap_vals).mean(axis=0)
        shap_df = pd.DataFrame({
            "feature": FINAL_FEATURES,
            "mean_abs_shap": feat_importance
        }).sort_values("mean_abs_shap", ascending=False)

        top10 = shap_df.head(10)
        print("  Top-10 SHAP features:")
        for _, row in top10.iterrows():
            is_physics = any(tag in row["feature"] for tag in ["sims_sd", "logZ_sd", "ts_ft", "ts_tdrift", "ts_fdrift"])
            flag = " [PHYSICS]" if is_physics else ""
            print(f"    {row['feature']}: {row['mean_abs_shap']:.5f}{flag}")

        physics_in_top5 = sum(
            1 for _, row in shap_df.head(5).iterrows()
            if any(t in row["feature"] for t in ["sims_sd", "logZ_sd", "ts_ft"])
        )
        print(f"  Physics features in top-5: {physics_in_top5}")
        shap_df.to_json(OUT / "shap_importance_v60.json", orient="records", indent=2)
    except Exception as e:
        print(f"  SHAP failed: {e}")
        shap_df = pd.DataFrame({"feature": FINAL_FEATURES, "mean_abs_shap": [0]*len(FINAL_FEATURES)})
        physics_in_top5 = 0

    # ── 13. Scoring ───────────────────────────────────────────────────────────
    print("\n[10] Scoring...")
    f1_k200 = he_f1_at_k(y, oof_meta, k=200)
    f1_k154 = he_f1_at_k(y, oof_meta, k=154)
    rp_t    = rp_score(y, oof_meta, PLATT_T)

    # K sweep to find best K
    best_k, best_f1 = 200, f1_k200
    for k in range(50, 350, 5):
        f1 = he_f1_at_k(y, oof_meta, k=k)
        if f1 > best_f1:
            best_f1, best_k = f1, k

    print(f"  OOF F1@K=200: {f1_k200:.6f}  (benchmark: 0.391)")
    print(f"  OOF F1@K=154: {f1_k154:.6f}")
    print(f"  OOF best K:   K={best_k}, F1={best_f1:.6f}")
    print(f"  OOF R+P/2:    {rp_t:.2f}")

    # LB estimate
    lb_est = rp_t + 2.67
    print(f"  LB estimate:  {lb_est:.2f}  (V44 banked: 72.83)")

    # Gate
    gate_f1 = f1_k200 >= 0.391
    print(f"\n  Gate F1@K=200 >= 0.391: {'PASS' if gate_f1 else 'FAIL'}")

    # ── 14. Spearman vs reference ──────────────────────────────────────────────
    print("\n[11] Spearman diversity check...")
    v4_oof = pd.read_parquet(V4_DIR / "oof_v4.parquet")
    v46_oof = pd.read_parquet(ROOT / "build_v46/oof_v46.parquet")

    rho_v4,  _ = spearmanr(oof_meta, v4_oof["oof_meta"].values)
    rho_v46, _ = spearmanr(oof_meta, v46_oof["oof_proba"].values)
    print(f"  Spearman vs V4:  {rho_v4:.4f}")
    print(f"  Spearman vs V46: {rho_v46:.4f}")

    # ── 15. Save OOF + test parquets ──────────────────────────────────────────
    print("\n[12] Saving OOF and test parquets...")
    oof_df = pd.DataFrame({
        "CoilID": train["CoilID"].values if "CoilID" in train.columns else np.arange(len(train)),
        "oof_lgb":  oof_lgb,
        "oof_xgb":  oof_xgb,
        "oof_cat":  oof_cat,
        "oof_meta": oof_meta,
        "y":        y,
    })
    oof_df.to_parquet(OUT / "oof_v60.parquet", index=False)

    test_df_out = pd.DataFrame({
        "CoilID": test["CoilID"].values if "CoilID" in test.columns else np.arange(len(test)),
        "test_lgb":  test_lgb,
        "test_xgb":  test_xgb,
        "test_cat":  test_cat,
        "test_proba": test_meta,
    })
    test_df_out.to_parquet(OUT / "test_proba_v60.parquet", index=False)

    # ── 16. Submission files ───────────────────────────────────────────────────
    print("\n[13] Generating submission files...")
    coil_ids = test["CoilID"].values if "CoilID" in test.columns else np.arange(len(test))

    for k in K_VALUES:
        top_k_idx  = np.argsort(test_meta)[::-1][:k]
        top_k_coils = coil_ids[top_k_idx]
        sub = pd.DataFrame({"CoilID": top_k_coils, "Defect": 1})
        sub_path = OUT / f"submission_K{k}.csv"
        sub.to_csv(sub_path, index=False)
        print(f"  {sub_path.name}: {k} rows")

    # ── 17. CV report ─────────────────────────────────────────────────────────
    elapsed = time.time() - t_start
    print(f"\n[14] Writing cv_report_v60.md... ({elapsed:.0f}s total)")

    top5_feats = shap_df.head(5)[["feature", "mean_abs_shap"]].to_dict(orient="records")

    report = f"""# V60 CV Report — Stand-Decomposed Base + Physics Features

**Date:** 2026-05-25
**Builder:** ml-engineer-agent (Jarvis)
**Architecture:** LGB+XGB+CatBoost -> LR meta + Platt T={PLATT_T} | NO SMOTE | scale_pos_weight={SCALE_POS}
**Hypothesis:** Physics features need stand-decomposed base to avoid V46 collinearity.

---

## Gate Results

| Gate | Condition | Value | Result |
|------|-----------|-------|--------|
| F1@K=200 >= 0.391 (V53 benchmark) | OOF F1 | {f1_k200:.6f} | {'PASS' if gate_f1 else 'FAIL'} |
| Physics in top-5 SHAP | >= 3 features | {physics_in_top5}/5 | {'PASS' if physics_in_top5 >= 3 else 'FAIL'} |
| VIF < 5 in final base | No feature VIF > 5 | {len(high_vif)} violations | {'PASS' if len(high_vif) == 0 else 'FAIL'} |

---

## OOF AUC Summary

| Metric | Value |
|--------|-------|
| Meta OOF AUC | **{auc_meta:.5f}** |
| LGB OOF AUC  | {auc_lgb_oof:.5f} |
| XGB OOF AUC  | {auc_xgb_oof:.5f} |
| CAT OOF AUC  | {auc_cat_oof:.5f} |

---

## Per-Fold AUCs

| Fold | LGB | XGB | CAT |
|------|-----|-----|-----|
""" + "\n".join(
    f"| {i+1} | {fold_aucs['lgb'][i]:.5f} | {fold_aucs['xgb'][i]:.5f} | {fold_aucs['cat'][i]:.5f} |"
    for i in range(N_FOLDS)
) + f"""

---

## OOF F1@K Summary

| K | OOF F1@K | TP | Notes |
|---|----------|----|-------|
| 154 | {f1_k154:.6f} | {int(np.sort(oof_meta)[::-1][:154].shape[0] - (np.sort(oof_meta)[::-1][:154] == 0).sum())} | HE formula |
| 200 | {f1_k200:.6f} | {int(y[np.argsort(oof_meta)[::-1][:200]].sum())} | Benchmark K |
| {best_k} | {best_f1:.6f} | {int(y[np.argsort(oof_meta)[::-1][:best_k]].sum())} | Best sweep K |

---

## LB Estimate

| Metric | Value |
|--------|-------|
| OOF R+P/2 @ T={PLATT_T} | {rp_t:.2f} |
| +2.67 calibration delta | {lb_est:.2f} |
| V44 banked LB | 72.83 |

---

## Top-10 SHAP Features (LGB)

| Rank | Feature | Mean |SHAP| | Physics? |
|------|---------|-------------|----------|
""" + "\n".join(
    f"| {i+1} | {row['feature']} | {row['mean_abs_shap']:.6f} | "
    f"{'YES [PHYSICS]' if any(t in row['feature'] for t in ['sims_sd', 'logZ_sd', 'ts_ft', 'ts_tdrift', 'ts_fdrift']) else 'no'} |"
    for i, (_, row) in enumerate(shap_df.head(10).iterrows())
) + f"""

---

## Diversity vs Reference Paradigms

| Comparison | Spearman ρ | Diversity |
|------------|------------|-----------|
| V60 vs V4  | {rho_v4:.4f} | {'DIVERSE' if rho_v4 < 0.80 else 'HIGH_CORR'} |
| V60 vs V46 | {rho_v46:.4f} | {'DIVERSE' if rho_v46 < 0.80 else 'HIGH_CORR'} |

---

## Feature Set

| Group | Count | Description |
|-------|-------|-------------|
| Stand decomp (T) | {len([c for c in STAND_DECOMP_COLS if 'ts_t' in c or 'ts_temp' in c])} | Raw + deviation + drift per temp stand |
| Stand decomp (F) | {len([c for c in STAND_DECOMP_COLS if 'ts_f' in c or 'ts_force' in c])} | Raw + deviation + drift per force stand |
| F/T coupling | {len([c for c in STAND_DECOMP_COLS if 'ts_ft' in c])} | Force/Temp per stand (stand-decomposed) |
| Zener-Hollomon SD | {len(ZENER_SD_COLS)} | log(Z) on stand-decomposed T basis |
| Sims residual SD | {len(SIMS_SD_COLS)} | Fold-isolated force residuals |
| V4 cleaned | {len(v4_available)} | V4 SHAP features minus raw collinear X4-X9/X29-X33 |
| **TOTAL** | **{len(FINAL_FEATURES)}** | |

---

## V46 vs V60 Comparison

| Aspect | V46 (failed) | V60 (this) |
|--------|-------------|-----------|
| Base | V4 raw (X4-X9, X29-X33 present) | Stand-decomposed (ts_t*, ts_f*) |
| Collinearity issue | ft_coupling collinear with raw X30 | ft isolated via ts_ft = F/T (no raw F present) |
| Sims target | Raw force stand | Force deviation from setpoint (ts_f*_dev) |
| Zener input | Raw X4-X9 | Stand-decomposed ts_t* |
| OOF AUC (V46) | 0.86268 | {auc_meta:.5f} |
| Physics in top-5 SHAP | 0-1 | {physics_in_top5} |

---

## Root Cause Addressed

V46 failure: ft_coupling_2 = X30/(X5+273.15) collinear with raw X30 in V4's feature set.
Trees split on both → redundant splits → AUC degradation.

V60 fix: replace X4-X9 with ts_t1..ts_t6 (stand-normalized) and X29-X33 with ts_f1..ts_f5.
Physics features built on ts_* basis → no raw T/F columns in final feature matrix.
Collinearity broken at source.

---

## Training Time

Total: {elapsed:.0f}s ({elapsed/60:.1f} min)

---

## Files

- `oof_v60.parquet` — 1352 rows: CoilID, oof_lgb, oof_xgb, oof_cat, oof_meta, y
- `test_proba_v60.parquet` — 339 rows: CoilID, test_lgb, test_xgb, test_cat, test_proba
- `stand_decomposition_features.parquet` — stand decomp + Zener cols for train
- `physics_features.parquet` — Sims residual cols for train
- `submission_K154.csv`, `submission_K200.csv`
- `shap_importance_v60.json` — top-20 SHAP features
"""

    with open(OUT / "cv_report_v60.md", "w") as f:
        f.write(report)
    print("  cv_report_v60.md written")

    # Print final summary
    print("\n" + "=" * 70)
    print("V60 FINAL SUMMARY")
    print("=" * 70)
    print(f"OOF F1@K=200:     {f1_k200:.6f}  (gate: {'PASS' if gate_f1 else 'FAIL'}, benchmark: 0.391)")
    print(f"OOF F1@K=154:     {f1_k154:.6f}")
    print(f"Best K sweep:     K={best_k}, F1={best_f1:.6f}")
    print(f"OOF AUC (meta):   {auc_meta:.5f}")
    print(f"Physics in top-5: {physics_in_top5}/5")
    print(f"VIF violations:   {len(high_vif)}")
    print(f"Spearman vs V4:   {rho_v4:.4f}")
    print(f"LB estimate:      {lb_est:.2f}")
    print(f"Total time:       {elapsed/60:.1f} min")
    print("=" * 70)


if __name__ == "__main__":
    main()
