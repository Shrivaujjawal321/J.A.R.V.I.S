"""
Step 2 — Feature Engineering
Priority order: ratio features → KNN imputation → stage aggregations → row stats → lag features
Saves: train_engineered.parquet, test_engineered.parquet
"""

import sys
sys.path.insert(0, "/home/ujjwal/Documents/J.A.R.V.I.S./data/hackathons/tata-steel-2026/round_1/ml_harness")

import json
import warnings
import pandas as pd
import numpy as np
from scipy.stats import skew
from sklearn.impute import KNNImputer
from pathlib import Path

from utils.seed import set_seed

warnings.filterwarnings("ignore")
set_seed(42)

# ── Paths ─────────────────────────────────────────────────────────────────────
DATA_DIR = Path("/home/ujjwal/Documents/J.A.R.V.I.S./data set of tata steel/dataset")
OUT_DIR  = Path("/home/ujjwal/Documents/J.A.R.V.I.S./data/hackathons/tata-steel-2026/round_1/build_v1")

train  = pd.read_csv(DATA_DIR / "train.csv")
test   = pd.read_csv(DATA_DIR / "test.csv")

lag_verdict = json.loads((OUT_DIR / "lag_verdict.json").read_text())
LAG_VALID   = lag_verdict["lag_features_valid"]

print(f"Train: {train.shape}, Test: {test.shape}")
print(f"Lag features valid: {LAG_VALID}")
print()

# Cluster definitions from EDA
CLUSTER3 = ["X4", "X5", "X6", "X7", "X8", "X9", "X10", "X13", "X15", "X29", "X30", "X31", "X32", "X33"]
CLUSTER2 = ["X14", "X19", "X24", "X34", "X35", "X36", "X37", "X38", "X39", "X40", "X41", "X42"]
CLUSTER1 = ["X1", "X2", "X3", "X11", "X12", "X16", "X17", "X18", "X20", "X21", "X22", "X23",
            "X25", "X26", "X27", "X28", "X43", "X44", "X45", "X46", "X47", "X48", "X49"]
ALL_X    = [f"X{i}" for i in range(1, 50)]

# Preserve labels before engineering
y_train = train["Y"].copy()

# Sort both by CoilID (sequential ordering confirmed)
train = train.sort_values("CoilID").reset_index(drop=True)
test  = test.sort_values("CoilID").reset_index(drop=True)
y_train = y_train[train.index].reset_index(drop=True)  # reindex with sorted train
# Actually re-read Y from sorted train
y_train = train["Y"].copy()

def add_engineered_features(df_train, df_test):
    """All engineering done on train-fit parameters, applied to test without leakage."""

    # ── A. KNN IMPUTATION (fit on train, transform both) ─────────────────────
    print("A. KNN imputation for X15 + other missing cols...")
    # Include the KNN neighbors from EDA: X10, X13, X29, X30 + X15 itself
    # Also impute ALL missing cols jointly for consistency
    feat_cols = ALL_X.copy()

    imputer = KNNImputer(n_neighbors=5)
    train_x = df_train[feat_cols].values.copy()
    test_x  = df_test[feat_cols].values.copy()

    train_imputed = imputer.fit_transform(train_x)
    test_imputed  = imputer.transform(test_x)

    df_train = df_train.copy()
    df_test  = df_test.copy()
    df_train[feat_cols] = train_imputed
    df_test[feat_cols]  = test_imputed

    missing_after_train = df_train[feat_cols].isnull().sum().sum()
    missing_after_test  = df_test[feat_cols].isnull().sum().sum()
    print(f"   Missing after imputation — train: {missing_after_train}, test: {missing_after_test}")

    # ── B. RATIO FEATURES (cross-cluster: rolling ÷ cooling) ─────────────────
    print("B. Ratio features (rolling force / cooling divergence)...")
    for df in [df_train, df_test]:
        df["X13_over_X36"]   = df["X13"] / (df["X36"].abs() + 1e-6)
        df["X10_over_X34"]   = df["X10"] / (df["X34"].abs() + 1e-6)
        df["X13_over_X34"]   = df["X13"] / (df["X34"].abs() + 1e-6)   # rising/falling
        df["X30_over_X35"]   = df["X30"] / (df["X35"].abs() + 1e-6)   # force/coiler
        df["X13_minus_X36"]  = df["X13"] - df["X36"]
        df["X10_minus_X34"]  = df["X10"] - df["X34"]
        # Multiplicative interactions (both-rising and both-falling amplify signal)
        df["X13_x_X10"]      = df["X13"] * df["X10"]
        df["X36_x_X34"]      = df["X36"] * df["X34"]
        df["X13_div_X34"]    = df["X13"] / (df["X34"].abs() + 1e-6)
    print(f"   Ratio features added: 9")

    # ── C. STAGE-WISE AGGREGATIONS ────────────────────────────────────────────
    print("C. Stage-wise aggregations (mean, std, min, max per cluster)...")
    for df in [df_train, df_test]:
        for name, cols in [("c3", CLUSTER3), ("c2", CLUSTER2), ("c1", CLUSTER1)]:
            valid_cols = [c for c in cols if c in df.columns]
            sub = df[valid_cols]
            df[f"{name}_mean"] = sub.mean(axis=1)
            df[f"{name}_std"]  = sub.std(axis=1)
            df[f"{name}_min"]  = sub.min(axis=1)
            df[f"{name}_max"]  = sub.max(axis=1)
        # Cross-cluster ratio: rolling cluster mean / cooling cluster mean
        df["c3_over_c2_mean"] = df["c3_mean"] / (df["c2_mean"].abs() + 1e-6)
        df["c3_std_ratio"]    = df["c3_std"] / (df["c3_mean"].abs() + 1e-6)  # coefficient of variation
    print(f"   Cluster aggregation features added: 14")

    # ── D. PER-ROW STATISTICS ─────────────────────────────────────────────────
    print("D. Per-row statistics (mean, std, skew across all X1-X49)...")
    for df in [df_train, df_test]:
        x_vals = df[ALL_X]
        df["row_mean"] = x_vals.mean(axis=1)
        df["row_std"]  = x_vals.std(axis=1)
        df["row_skew"] = x_vals.apply(lambda r: skew(r.dropna()), axis=1)
        df["row_max"]  = x_vals.max(axis=1)
        df["row_min"]  = x_vals.min(axis=1)
        df["row_range"] = df["row_max"] - df["row_min"]
    print(f"   Row stat features added: 6")

    # ── E. WITHIN-CLUSTER Z-SCORES (deviation from cluster mean) ─────────────
    print("E. Within-cluster deviation features for top features...")
    for df in [df_train, df_test]:
        # X13 deviation within Cluster 3
        c3_valid = [c for c in CLUSTER3 if c in df.columns]
        df["X13_c3_zscore"] = (df["X13"] - df["c3_mean"]) / (df["c3_std"] + 1e-6)
        df["X10_c3_zscore"] = (df["X10"] - df["c3_mean"]) / (df["c3_std"] + 1e-6)
        # X36 deviation within Cluster 2
        df["X36_c2_zscore"] = (df["X36"] - df["c2_mean"]) / (df["c2_std"] + 1e-6)
        df["X34_c2_zscore"] = (df["X34"] - df["c2_mean"]) / (df["c2_std"] + 1e-6)
    print(f"   Z-score features added: 4")

    # ── F. LOG TRANSFORM of heavy right-skewed features ───────────────────────
    print("F. Log transforms for heavily skewed features...")
    log_cols = ["X35"]  # EDA: X35 mean~10M for Y=0 vs ~2M for Y=1
    for df in [df_train, df_test]:
        for col in log_cols:
            if col in df.columns:
                df[f"{col}_log"] = np.log1p(df[col].abs())
    print(f"   Log features added: {len(log_cols)}")

    # ── G. LAG FEATURES (conditional on sequentiality verdict) ───────────────
    if LAG_VALID:
        print("G. Lag features (CoilID is sequential — lag-1, lag-2, rolling-5 mean)...")
        lag_features = ["X13", "X10", "X36"]
        for df in [df_train, df_test]:
            for feat in lag_features:
                df[f"{feat}_lag1"]    = df[feat].shift(1).fillna(df[feat].median())
                df[f"{feat}_lag2"]    = df[feat].shift(2).fillna(df[feat].median())
                df[f"{feat}_roll5"]   = df[feat].rolling(5, min_periods=1).mean()
                # Delta: current vs lag-1 (process drift)
                df[f"{feat}_delta1"]  = df[feat] - df[f"{feat}_lag1"]
        print(f"   Lag/rolling features added: {len(lag_features) * 4}")
    else:
        print("G. Lag features SKIPPED (no sequential ordering confirmed)")

    return df_train, df_test


# ── Run engineering ───────────────────────────────────────────────────────────
train_eng, test_eng = add_engineered_features(train, test)

# ── Feature count report ──────────────────────────────────────────────────────
# Drop CoilID and Y from feature list
feature_cols = [c for c in train_eng.columns if c not in ["CoilID", "Y"]]
print()
print(f"Total features after engineering: {len(feature_cols)}")
print(f"  Original: 49")
print(f"  Added   : {len(feature_cols) - 49}")

# ── Sanity check: no NaNs remaining ──────────────────────────────────────────
nan_train = train_eng[feature_cols].isnull().sum().sum()
nan_test  = test_eng[feature_cols].isnull().sum().sum()
print(f"\nNaN check — train: {nan_train}, test: {nan_test}")
if nan_train > 0 or nan_test > 0:
    remaining = train_eng[feature_cols].isnull().sum()
    print("  Remaining NaN cols:", remaining[remaining > 0].to_dict())
    remaining_test = test_eng[feature_cols].isnull().sum()
    print("  Remaining NaN cols (test):", remaining_test[remaining_test > 0].to_dict())

# ── Save ──────────────────────────────────────────────────────────────────────
print()
train_eng.to_parquet(OUT_DIR / "train_engineered.parquet", index=False)
test_eng.to_parquet(OUT_DIR / "test_engineered.parquet", index=False)

print(f"Saved: {OUT_DIR / 'train_engineered.parquet'}  — {train_eng.shape}")
print(f"Saved: {OUT_DIR / 'test_engineered.parquet'}   — {test_eng.shape}")

# Save feature list for downstream scripts
feat_info = {
    "feature_cols": feature_cols,
    "n_features": len(feature_cols),
    "original_x_cols": ALL_X,
}
(OUT_DIR / "feature_list.json").write_text(json.dumps(feat_info, indent=2))
print(f"Saved feature list: {OUT_DIR / 'feature_list.json'}")
print()
print("Step 2 complete.")
