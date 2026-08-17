"""
train_v48.py — V35 Architecture + Pseudo-Label Augmentation (CAST 2024 / DARP Recipe)

Key innovation over V35:
- Extract 132 vote=6/6 confident test predictions from V44 consensus
- Add as pseudo-Y=1 labels with sample_weight=0.6 into training set
- Augments positive prevalence: 5% -> ~13% (closer to test's ~45%)
- Fold integrity: pseudo rows always in TRAIN split, val = real-train rows ONLY
- OOF AUC computed exclusively on real-train labels (no contamination)

Architecture: V35's 9-model rank-average (LGB×2, XGB×2, CatBoost, RF, ET, HGB, TabICL/LGB3)
Gates:
  OOF AUC (real-train only) >= 0.87
  Spearman vs V35 OOF < 0.95  (diversity check)
  Pseudo-positive count == 132 (exact)
"""

from __future__ import annotations

import json
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import rankdata, spearmanr
from sklearn.ensemble import (
    RandomForestClassifier,
    ExtraTreesClassifier,
    HistGradientBoostingClassifier,
)
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import roc_auc_score

import lightgbm as lgb
import xgboost as xgb
import catboost as cb

warnings.filterwarnings("ignore")

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE    = Path("/home/ujjwal/Documents/J.A.R.V.I.S.")
RAW_DIR = BASE / "data set of tata steel/dataset"
V4_DIR  = BASE / "data/hackathons/tata-steel-2026/round_1/build_v4"
V35_DIR = BASE / "data/hackathons/tata-steel-2026/round_1/build_v35"
V48_DIR = BASE / "data/hackathons/tata-steel-2026/round_1/build_v48"
ROUND_ROOT = BASE / "data/hackathons/tata-steel-2026/round_1"
V48_DIR.mkdir(parents=True, exist_ok=True)

# ── Constants ──────────────────────────────────────────────────────────────────
SEED             = 42
N_FOLDS          = 5
PSEUDO_WEIGHT    = 0.6
SPW              = 1286 / 66     # neg/pos for real train = 19.48
TEMP_COLS        = ["X4","X5","X6","X7","X8","X9"]
FORCE_COLS       = ["X29","X30","X31","X32","X33"]
TARGET           = "Y"
ID_COL           = "CoilID"

print("=" * 70)
print("V48 — V35 Architecture + Pseudo-Label Augmentation (R2 CAST/DARP)")
print(f"Pseudo-weight={PSEUDO_WEIGHT} | {N_FOLDS}-fold StratifiedKFold | seed={SEED}")
print("=" * 70)


# ═══════════════════════════════════════════════════════════════════════════════
# STEP 0: Generate Pseudo-Labels from V44 Consensus (vote=6/6)
# ═══════════════════════════════════════════════════════════════════════════════

print("\n[0/7] Generating pseudo-labels from V44 consensus (vote=6 CoilIDs)...")

test_v4 = pd.read_parquet(V4_DIR / "test_v4.parquet")
coil_order = test_v4[ID_COL].tolist()
N_TEST = len(coil_order)

df_test_scores = pd.DataFrame({ID_COL: coil_order})
df_test_scores = df_test_scores.merge(
    pd.read_parquet(V35_DIR / "test_proba_v35.parquet")[
        [ID_COL, "rank_avg_proba"]
    ].rename(columns={"rank_avg_proba": "v35"}),
    on=ID_COL,
)
df_test_scores = df_test_scores.merge(
    pd.read_parquet(ROUND_ROOT / "build_v39/test_proba_v39.parquet")[
        [ID_COL, "test_proba"]
    ].rename(columns={"test_proba": "v39"}),
    on=ID_COL,
)
df_test_scores = df_test_scores.merge(
    pd.read_parquet(ROUND_ROOT / "build_v40/test_proba_v40.parquet")[
        [ID_COL, "test_proba"]
    ].rename(columns={"test_proba": "v40"}),
    on=ID_COL,
)
df_test_scores = df_test_scores.merge(
    pd.read_parquet(ROUND_ROOT / "build_v41/test_proba_v41.parquet")[
        [ID_COL, "test_proba"]
    ].rename(columns={"test_proba": "v41"}),
    on=ID_COL,
)

v43_df = pd.read_parquet(ROUND_ROOT / "build_v43/test_proba_v43.parquet")
v43_col = None
for c in ["test_proba", "rank_product", "oof_proba", "proba"]:
    if c in v43_df.columns:
        v43_col = c; break
if v43_col is None:
    v43_col = [c for c in v43_df.columns if c != ID_COL][0]
df_test_scores = df_test_scores.merge(
    v43_df[[ID_COL, v43_col]].rename(columns={v43_col: "v43"}),
    on=ID_COL,
)

paradigms     = ["v35", "v39", "v40", "v41", "v43"]
K_ANCHOR      = 181
paradigm_topK = {
    p: set(df_test_scores.sort_values(p, ascending=False)[ID_COL].tolist()[:K_ANCHOR])
    for p in paradigms
}
v4_sub       = pd.read_csv(ROUND_ROOT / "build_v4/expected_submission.csv")
v4_154_coils = set(v4_sub[v4_sub["Y"] == 1][ID_COL].tolist())

vote = pd.Series(0, index=df_test_scores[ID_COL])
for p in paradigms:
    vote.loc[list(paradigm_topK[p])] += 1
vote.loc[list(v4_154_coils & set(coil_order))] += 1

rank_pct = pd.DataFrame(index=df_test_scores[ID_COL])
for p in paradigms:
    rank_pct[p] = df_test_scores.set_index(ID_COL)[p].rank(pct=True)
rank_pct_mean = rank_pct.mean(axis=1)

consensus = pd.DataFrame({
    ID_COL: vote.index,
    "vote": vote.values,
    "rank_pct_mean": rank_pct_mean.loc[vote.index].values,
}).sort_values(["vote", "rank_pct_mean"], ascending=[False, False]).reset_index(drop=True)

vote6_coils = consensus[consensus["vote"] == 6][ID_COL].tolist()
assert len(vote6_coils) == 132, f"Expected 132 vote=6 CoilIDs, got {len(vote6_coils)}"
print(f"  Vote=6 CoilIDs: {len(vote6_coils)} — GATE PASS")

# Save pseudo_labels.json
pseudo_label_data = {
    "pseudo_positive_count": len(vote6_coils),
    "pseudo_weight": PSEUDO_WEIGHT,
    "source": "V44 consensus vote=6 (all 5 paradigms + V4_154 anchor agreed)",
    "coil_ids": vote6_coils,
}
with open(V48_DIR / "pseudo_labels.json", "w") as f:
    json.dump(pseudo_label_data, f, indent=2)
print(f"  Saved pseudo_labels.json ({len(vote6_coils)} CoilIDs)")


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 1: Stand-FE (identical to V35 — fold-isolated)
# ═══════════════════════════════════════════════════════════════════════════════

class StandSetpoints:
    """Fold-isolated setpoint statistics — NEVER fitted on val/test rows."""

    def __init__(self):
        self.temp_medians    = None
        self.force_medians   = None
        self.temp_stds       = None
        self.force_stds      = None
        self.x35_high_median = None
        self.x35_high_std    = None
        self.is_fitted       = False

    def fit(self, df_fold: pd.DataFrame) -> "StandSetpoints":
        self.temp_medians  = df_fold[TEMP_COLS].median()
        self.force_medians = df_fold[FORCE_COLS].median()
        self.temp_stds     = df_fold[TEMP_COLS].std().replace(0, 1e-9)
        self.force_stds    = df_fold[FORCE_COLS].std().replace(0, 1e-9)
        if "X35" in df_fold.columns:
            high_mask = df_fold["X35"] > 1e6
            if high_mask.sum() > 5:
                self.x35_high_median = float(df_fold.loc[high_mask, "X35"].median())
                self.x35_high_std    = float(df_fold.loc[high_mask, "X35"].std()) or 1e-9
            else:
                self.x35_high_median = float(df_fold["X35"].median())
                self.x35_high_std    = float(df_fold["X35"].std()) or 1e-9
        self.is_fitted = True
        return self

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        assert self.is_fitted
        df = df.copy()
        for i, col in enumerate(TEMP_COLS):
            med = self.temp_medians[col]
            df[f"res_temp_{i+1}"]     = df[col] - med
            df[f"abs_res_temp_{i+1}"] = (df[col] - med).abs()
        for i, col in enumerate(FORCE_COLS):
            med = self.force_medians[col]
            df[f"res_force_{i+1}"]     = df[col] - med
            df[f"abs_res_force_{i+1}"] = (df[col] - med).abs()
        temp_z  = (df[TEMP_COLS]  - self.temp_medians)  / self.temp_stds
        force_z = (df[FORCE_COLS] - self.force_medians) / self.force_stds
        all_z   = pd.concat([temp_z, force_z], axis=1)
        df["cum_process_dev"] = all_z.abs().sum(axis=1)
        df["max_abs_z_dev"]   = all_z.abs().max(axis=1)
        df["cum_force_dev_raw"]  = (df[FORCE_COLS] - self.force_medians).sum(axis=1)
        df["max_abs_force_dev"]  = (df[FORCE_COLS] - self.force_medians).abs().max(axis=1)
        df["max_abs_temp_dev"]   = (df[TEMP_COLS]  - self.temp_medians).abs().max(axis=1)
        temp_res_cols  = [f"res_temp_{s}"  for s in range(1, 7)]
        force_res_cols = [f"res_force_{s}" for s in range(1, 6)]
        df["worst_temp_stand"]  = df[temp_res_cols].abs().values.argmax(axis=1).astype(float)
        df["worst_temp_mag"]    = df[temp_res_cols].abs().max(axis=1)
        df["worst_force_stand"] = df[force_res_cols].abs().values.argmax(axis=1).astype(float)
        df["worst_force_mag"]   = df[force_res_cols].abs().max(axis=1)
        for i in range(len(TEMP_COLS) - 1):
            df[f"temp_drop_{i+1}_{i+2}"] = df[TEMP_COLS[i]] - df[TEMP_COLS[i + 1]]
        if "X35" in df.columns:
            df["X35_is_high"]          = (df["X35"] > 1e6).astype(float)
            df["X35_log1p"]            = np.log1p(df["X35"])
            df["X35_high_mode_zscore"] = np.where(
                df["X35"] > 1e6,
                (df["X35"] - self.x35_high_median) / self.x35_high_std,
                0.0,
            )
            df["X35_flag_x_cum_force"] = df["X35_is_high"] * df["cum_force_dev_raw"]
        for k in range(5):
            t_col = TEMP_COLS[k]; f_col = FORCE_COLS[k]
            df[f"res_cross_{k+1}"] = (
                (df[t_col] - self.temp_medians[t_col]) *
                (df[f_col] - self.force_medians[f_col])
            )
        df["temp_span"]  = df[TEMP_COLS[0]] - df[TEMP_COLS[-1]]
        df["temp_entry"] = df[TEMP_COLS[0]]
        df["temp_exit"]  = df[TEMP_COLS[-1]]
        df["force_escalation_ratio"] = df[FORCE_COLS[-1]] / (df[FORCE_COLS[0]] + 1e-6)
        for col in FORCE_COLS:
            df[f"log_{col}"] = np.log1p(df[col].clip(lower=0))
        return df


STAND_FE_COLS = (
    [f"res_temp_{i+1}"     for i in range(6)] +
    [f"abs_res_temp_{i+1}" for i in range(6)] +
    [f"res_force_{i+1}"    for i in range(5)] +
    [f"abs_res_force_{i+1}" for i in range(5)] +
    ["cum_process_dev","max_abs_z_dev","cum_force_dev_raw",
     "max_abs_force_dev","max_abs_temp_dev"] +
    ["worst_temp_stand","worst_temp_mag","worst_force_stand","worst_force_mag"] +
    [f"temp_drop_{i+1}_{i+2}" for i in range(5)] +
    ["X35_is_high","X35_log1p","X35_high_mode_zscore","X35_flag_x_cum_force"] +
    [f"res_cross_{k+1}" for k in range(5)] +
    ["temp_span","temp_entry","temp_exit","force_escalation_ratio"] +
    [f"log_{col}" for col in FORCE_COLS]
)
print(f"\nStand-FE columns: {len(STAND_FE_COLS)}")


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 2: Model Definitions (identical to V35)
# ═══════════════════════════════════════════════════════════════════════════════

def make_lgb1():
    return lgb.LGBMClassifier(
        is_unbalance=True, learning_rate=0.02, num_leaves=15,
        min_child_samples=5, subsample=0.7, colsample_bytree=0.7,
        n_estimators=300, random_state=42, verbose=-1, n_jobs=-1,
    )

def make_lgb2():
    return lgb.LGBMClassifier(
        is_unbalance=True, learning_rate=0.025, num_leaves=20, max_depth=5,
        min_child_samples=4, subsample=0.8, colsample_bytree=0.8,
        n_estimators=300, random_state=137, verbose=-1, n_jobs=-1,
    )

def make_lgb3():
    return lgb.LGBMClassifier(
        is_unbalance=True, learning_rate=0.015, num_leaves=31, max_depth=6,
        min_child_samples=3, subsample=0.75, colsample_bytree=0.75,
        n_estimators=400, random_state=2024, verbose=-1, n_jobs=-1,
    )

def make_xgb1():
    return xgb.XGBClassifier(
        scale_pos_weight=SPW, learning_rate=0.03, max_depth=4,
        n_estimators=300, subsample=0.7, colsample_bytree=0.7,
        random_state=42, eval_metric="auc", verbosity=0, n_jobs=-1,
    )

def make_xgb2():
    return xgb.XGBClassifier(
        scale_pos_weight=SPW, learning_rate=0.025, max_depth=5,
        n_estimators=350, subsample=0.8, colsample_bytree=0.75, min_child_weight=2,
        random_state=137, eval_metric="auc", verbosity=0, n_jobs=-1,
    )

def make_catboost():
    return cb.CatBoostClassifier(
        auto_class_weights="Balanced", learning_rate=0.03,
        depth=4, iterations=300, random_seed=42, verbose=0,
    )

def make_rf():
    return RandomForestClassifier(
        n_estimators=500, class_weight="balanced",
        random_state=42, n_jobs=-1,
    )

def make_et():
    return ExtraTreesClassifier(
        n_estimators=500, class_weight="balanced",
        random_state=42, n_jobs=-1,
    )

def make_hgb():
    return HistGradientBoostingClassifier(
        max_iter=300, learning_rate=0.03, max_leaf_nodes=15,
        min_samples_leaf=5, class_weight="balanced", random_state=42,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 3: Load Data
# ═══════════════════════════════════════════════════════════════════════════════

print("\n[1/7] Loading data...")

train_raw = pd.read_csv(RAW_DIR / "train.csv")
test_raw  = pd.read_csv(RAW_DIR / "test.csv")

v4_train = pd.read_parquet(V4_DIR / "train_v4.parquet")
v4_test  = pd.read_parquet(V4_DIR / "test_v4.parquet")

with open(V4_DIR / "v4_final_features.json") as f:
    V4_FEATURES = json.load(f)["features"]

print(f"  Real train: {v4_train.shape} | positives: {int(v4_train[TARGET].sum())}/{len(v4_train)}")
print(f"  Test:  {v4_test.shape}")
print(f"  V4 features: {len(V4_FEATURES)} | Stand-FE: {len(STAND_FE_COLS)} | Total: {len(V4_FEATURES)+len(STAND_FE_COLS)}")

# Validate stand ordering
temp_means  = train_raw[TEMP_COLS].mean().values
force_means = train_raw[FORCE_COLS].mean().values
assert all(temp_means[i] >= temp_means[i+1] for i in range(len(temp_means)-1))
assert all(force_means[i] <= force_means[i+1] for i in range(len(force_means)-1))
print("  Stand ordering validation: PASS")

# Real train labels + indices
y_real = v4_train[TARGET].values
n_real = len(v4_train)  # 1352


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 4: Build Augmented Training Set
# ═══════════════════════════════════════════════════════════════════════════════

print("\n[2/7] Building augmented training set...")

# Pull pseudo-labeled rows from test parquet (using V4 test parquet features)
pseudo_coil_set = set(vote6_coils)
pseudo_test_rows = v4_test[v4_test[ID_COL].isin(pseudo_coil_set)].copy()
assert len(pseudo_test_rows) == 132, f"Expected 132 pseudo rows, got {len(pseudo_test_rows)}"

# Assign pseudo-label Y=1
pseudo_test_rows[TARGET] = 1
# Mark as pseudo (for fold assignment logic)
pseudo_test_rows["_is_pseudo"] = True
v4_train_marked = v4_train.copy()
v4_train_marked["_is_pseudo"] = False

# Concatenate: real train first, then pseudo
aug_train = pd.concat([v4_train_marked, pseudo_test_rows], ignore_index=True)

# Compute augmented stats
n_aug      = len(aug_train)
n_pseudo   = int(pseudo_test_rows[TARGET].sum())
pos_real   = int(v4_train[TARGET].sum())
pos_total  = int(aug_train[TARGET].sum())
prev_real  = pos_real / n_real * 100
prev_aug   = pos_total / n_aug * 100

print(f"  Real train rows:   {n_real:4d} | positives: {pos_real:3d} ({prev_real:.1f}%)")
print(f"  Pseudo rows added: {n_pseudo:4d} | all positive, weight={PSEUDO_WEIGHT}")
print(f"  Augmented total:   {n_aug:4d} | positives: {pos_total:3d} ({prev_aug:.1f}%)")
print(f"  Prevalence shift:  {prev_real:.1f}% -> {prev_aug:.1f}% (test est ~45%)")

# Build sample weights
sample_weights_aug = np.where(aug_train["_is_pseudo"].values, PSEUDO_WEIGHT, 1.0)

# is_pseudo boolean array
is_pseudo_mask = aug_train["_is_pseudo"].values.astype(bool)
real_indices_in_aug = np.where(~is_pseudo_mask)[0]  # indices of real rows in aug
assert len(real_indices_in_aug) == n_real

y_aug = aug_train[TARGET].values


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 5: Model Roster
# ═══════════════════════════════════════════════════════════════════════════════

print("\n[3/7] Building model roster...")

tabicl_model = None
try:
    from tabicl import TabICLClassifier
    tabicl_model = TabICLClassifier(n_estimators=5, random_state=42, verbose=0)
    print("  TabICL available — using as M9")
    MODEL_NAMES = ["LGB1","LGB2","XGB1","XGB2","CatBoost","RF","ET","HGB","TabICL"]
    MODEL_FACTORIES = {
        "LGB1":     make_lgb1,
        "LGB2":     make_lgb2,
        "XGB1":     make_xgb1,
        "XGB2":     make_xgb2,
        "CatBoost": make_catboost,
        "RF":       make_rf,
        "ET":       make_et,
        "HGB":      make_hgb,
        "TabICL":   lambda: TabICLClassifier(n_estimators=5, random_state=42, verbose=False),
    }
    TABICL_NAMES = {"TabICL"}
except Exception as e:
    print(f"  TabICL unavailable ({e}) — using LGB3 as M9")
    MODEL_NAMES = ["LGB1","LGB2","XGB1","XGB2","CatBoost","RF","ET","HGB","LGB3"]
    MODEL_FACTORIES = {
        "LGB1":     make_lgb1,
        "LGB2":     make_lgb2,
        "XGB1":     make_xgb1,
        "XGB2":     make_xgb2,
        "CatBoost": make_catboost,
        "RF":       make_rf,
        "ET":       make_et,
        "HGB":      make_hgb,
        "LGB3":     make_lgb3,
    }
    TABICL_NAMES = set()

n_models = len(MODEL_NAMES)
print(f"  Models ({n_models}): {MODEL_NAMES}")

# OOF / test storage — indexed on REAL train only
oof_probas  = {m: np.zeros(n_real)  for m in MODEL_NAMES}
test_probas = {m: np.zeros(N_TEST) for m in MODEL_NAMES}
fold_aucs   = {m: []               for m in MODEL_NAMES}


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 6: 5-Fold CV — Pseudo rows ALWAYS in train, val = real rows ONLY
# ═══════════════════════════════════════════════════════════════════════════════

print(f"\n[4/7] Training {n_models}-model ensemble ({N_FOLDS}-fold StratifiedKFold)...")
print("  CRITICAL: StratifiedKFold on real-train rows only; pseudo always in train split")

# StratifiedKFold on REAL train rows only (indices 0..n_real-1 in aug_train)
skf = StratifiedKFold(n_splits=N_FOLDS, shuffle=True, random_state=SEED)
pseudo_aug_indices = np.where(is_pseudo_mask)[0]   # indices of pseudo rows in aug_train

for fold_idx, (real_tr_idx, real_val_idx) in enumerate(skf.split(np.zeros(n_real), y_real)):
    # real_tr_idx / real_val_idx are positions within REAL-train array (0..n_real-1)
    # Map to aug_train indices
    aug_tr_real  = real_indices_in_aug[real_tr_idx]   # real train rows for this fold
    aug_val_real = real_indices_in_aug[real_val_idx]  # real val rows

    # Train split = real train fold rows + ALL pseudo rows
    aug_tr_all = np.concatenate([aug_tr_real, pseudo_aug_indices])

    print(f"\n  --- Fold {fold_idx+1}/{N_FOLDS} | "
          f"real_tr={len(aug_tr_real)}, pseudo_tr={len(pseudo_aug_indices)}, "
          f"total_tr={len(aug_tr_all)}, val={len(aug_val_real)} "
          f"(val pos={int(y_real[real_val_idx].sum())}) ---")

    # Fit StandSetpoints on REAL TRAIN FOLD rows only (no pseudo contamination of setpoints)
    setpoints = StandSetpoints()
    setpoints.fit(aug_train.iloc[aug_tr_real])

    # For test: fit setpoints on full real train (no labels, no leakage)
    test_setpoints = StandSetpoints()
    test_setpoints.fit(v4_train)
    test_fe = test_setpoints.transform(v4_test.copy())

    # Apply stand-FE
    tr_fe  = setpoints.transform(aug_train.iloc[aug_tr_all].copy())
    val_fe = setpoints.transform(aug_train.iloc[aug_val_real].copy())

    # Feature matrices
    X_tr  = pd.concat([
        tr_fe[V4_FEATURES].reset_index(drop=True),
        tr_fe[STAND_FE_COLS].reset_index(drop=True),
    ], axis=1).values

    X_val = pd.concat([
        val_fe[V4_FEATURES].reset_index(drop=True),
        val_fe[STAND_FE_COLS].reset_index(drop=True),
    ], axis=1).values

    X_test = pd.concat([
        test_fe[V4_FEATURES].reset_index(drop=True),
        test_fe[STAND_FE_COLS].reset_index(drop=True),
    ], axis=1).values

    y_tr_all = y_aug[aug_tr_all]
    y_val    = y_real[real_val_idx]
    sw_tr    = sample_weights_aug[aug_tr_all]

    if fold_idx == 0:
        n_pseudo_in_fold = len(pseudo_aug_indices)
        n_pos_tr = int(y_tr_all.sum())
        n_real_pos_tr = int(y_real[real_tr_idx].sum())
        print(f"    X_tr shape: {X_tr.shape} | positives in tr: {n_pos_tr} "
              f"(real={n_real_pos_tr} + pseudo={n_pseudo_in_fold})")

    # Train each model with sample_weight
    for model_name in MODEL_NAMES:
        try:
            model = MODEL_FACTORIES[model_name]()
            is_tabicl = model_name in TABICL_NAMES

            if model_name == "CatBoost":
                model.fit(X_tr, y_tr_all, sample_weight=sw_tr, verbose=0)
            elif model_name in {"HGB"}:
                # HistGradientBoosting: sample_weight goes in fit
                model.fit(X_tr, y_tr_all, sample_weight=sw_tr)
            elif model_name in {"RF", "ET"}:
                model.fit(X_tr, y_tr_all, sample_weight=sw_tr)
            elif is_tabicl:
                # TabICL may not support sample_weight — fall through without
                try:
                    model.fit(X_tr, y_tr_all, sample_weight=sw_tr)
                except TypeError:
                    model.fit(X_tr, y_tr_all)
            else:
                # LGB, XGB
                model.fit(X_tr, y_tr_all, sample_weight=sw_tr)

            val_proba  = model.predict_proba(X_val)[:, 1]
            test_proba = model.predict_proba(X_test)[:, 1]

            # OOF: store at REAL-train indices only
            oof_probas[model_name][real_val_idx] += val_proba
            test_probas[model_name]              += test_proba / N_FOLDS

            fold_auc = roc_auc_score(y_val, val_proba)
            fold_aucs[model_name].append(fold_auc)
            print(f"    [{model_name:12s}] fold AUC: {fold_auc:.4f}")

        except Exception as e:
            print(f"    [ERROR] {model_name} failed on fold {fold_idx+1}: {e}")
            print(f"    Falling back to LGB3...")
            fallback = make_lgb3()
            fallback.fit(X_tr, y_tr_all, sample_weight=sw_tr)
            val_proba  = fallback.predict_proba(X_val)[:, 1]
            test_proba = fallback.predict_proba(X_test)[:, 1]
            oof_probas[model_name][real_val_idx] += val_proba
            test_probas[model_name]              += test_proba / N_FOLDS
            fold_auc = roc_auc_score(y_val, val_proba)
            fold_aucs[model_name].append(fold_auc)
            print(f"    [LGB3-fallback {model_name:6s}] fold AUC: {fold_auc:.4f}")


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 7: Rank-Average Aggregation
# ═══════════════════════════════════════════════════════════════════════════════

print("\n[5/7] Rank-average aggregation...")
oof_rank_avg  = np.zeros(n_real)
test_rank_avg = np.zeros(N_TEST)

for model_name in MODEL_NAMES:
    oof_rank_avg  += rankdata(oof_probas[model_name])
    test_rank_avg += rankdata(test_probas[model_name])

oof_rank_avg  /= n_models
test_rank_avg /= n_models

# OOF AUC on REAL train labels only
oof_auc = roc_auc_score(y_real, oof_rank_avg)
print(f"  V48 OOF AUC (real-train only): {oof_auc:.4f}")

# Per-model stats
per_model_aucs = {}
print("\n  Per-model OOF AUCs:")
for model_name in MODEL_NAMES:
    auc_val  = roc_auc_score(y_real, oof_probas[model_name])
    fold_std = float(np.std(fold_aucs[model_name]))
    per_model_aucs[model_name] = {
        "mean_oof_auc": round(auc_val, 4),
        "fold_std": round(fold_std, 4),
        "fold_aucs": [round(a, 4) for a in fold_aucs[model_name]],
    }
    print(f"    {model_name:12s}: {auc_val:.4f} ± {fold_std:.4f}")

# Bootstrap 95% CI
rng = np.random.default_rng(SEED)
boot_aucs = []
for _ in range(1000):
    idx  = rng.integers(0, n_real, n_real)
    y_b  = y_real[idx]; p_b = oof_rank_avg[idx]
    if 0 < y_b.sum() < len(y_b):
        boot_aucs.append(roc_auc_score(y_b, p_b))
ci_lower = float(np.percentile(boot_aucs, 2.5))
ci_upper = float(np.percentile(boot_aucs, 97.5))
print(f"\n  Bootstrap 95% CI: [{ci_lower:.4f}, {ci_upper:.4f}]")

avg_fold_std = float(np.mean([np.std(fold_aucs[m]) for m in MODEL_NAMES]))
print(f"  Mean fold std: {avg_fold_std:.4f}")


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 8: Spearman Diversity vs V35
# ═══════════════════════════════════════════════════════════════════════════════

print("\n[6/7] Spearman diversity check vs V35...")
v35_oof = pd.read_parquet(V35_DIR / "oof_v35.parquet")
# Align on CoilID
v4_coil_order = v4_train[ID_COL].values
v35_oof_aligned = v35_oof.set_index(ID_COL).loc[v4_coil_order]["rank_avg_proba"].values

spearman_v35, _ = spearmanr(oof_rank_avg, v35_oof_aligned)
print(f"  Spearman (V48 OOF vs V35 OOF): ρ={spearman_v35:.4f}")

# Also check vs other paradigms (test-level)
v35_test = pd.read_parquet(V35_DIR / "test_proba_v35.parquet").set_index(ID_COL).loc[coil_order]["rank_avg_proba"].values
v39_test = pd.read_parquet(ROUND_ROOT/"build_v39/test_proba_v39.parquet").set_index(ID_COL).loc[coil_order]["test_proba"].values
v40_test = pd.read_parquet(ROUND_ROOT/"build_v40/test_proba_v40.parquet").set_index(ID_COL).loc[coil_order]["test_proba"].values
v41_test = pd.read_parquet(ROUND_ROOT/"build_v41/test_proba_v41.parquet").set_index(ID_COL).loc[coil_order]["test_proba"].values

test_spearman = {}
for name, arr in [("v35",v35_test),("v39",v39_test),("v40",v40_test),("v41",v41_test)]:
    s, _ = spearmanr(test_rank_avg, arr)
    test_spearman[name] = round(float(s), 4)
    print(f"  Spearman test V48 vs {name}: ρ={s:.4f}")


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 9: Score + SHAP
# ═══════════════════════════════════════════════════════════════════════════════

def score_fn(y_true, y_pred):
    tp = int(((y_true==1)&(y_pred==1)).sum())
    fp = int(((y_true==0)&(y_pred==1)).sum())
    fn = int(((y_true==1)&(y_pred==0)).sum())
    recall    = tp / (tp + fn + 1e-9)
    precision = tp / (tp + fp + 1e-9)
    return (recall + precision) / 2 * 100

print(f"\n[7/7] Score computation and artifact save...")
oof_sorted = np.argsort(oof_rank_avg)[::-1]
test_sorted = np.argsort(test_rank_avg)[::-1]

K_THRESHOLD = 200  # V44 banked best is K=200
oof_pred_k = np.zeros(n_real, dtype=int)
oof_pred_k[oof_sorted[:K_THRESHOLD]] = 1
oof_score_k = score_fn(y_real, oof_pred_k)
print(f"  OOF (R+P)/2 at K={K_THRESHOLD}: {oof_score_k:.2f}")

# Sweep K
best_oof_score = 0.0; best_k = K_THRESHOLD
for k in range(50, 300):
    pred_k = np.zeros(n_real, dtype=int)
    pred_k[oof_sorted[:k]] = 1
    s = score_fn(y_real, pred_k)
    if s > best_oof_score:
        best_oof_score = s; best_k = k
print(f"  Best OOF K-sweep: K={best_k}, score={best_oof_score:.2f}")

# Test prediction at K=200
submission_y = np.zeros(N_TEST, dtype=int)
submission_y[test_sorted[:K_THRESHOLD]] = 1
assert submission_y.sum() == K_THRESHOLD
print(f"  K={K_THRESHOLD} sanity: {submission_y.sum()} positives — PASS")

# SHAP top-5 (using LGB1 as representative)
print("\n  Computing SHAP on LGB1 (representative model)...")
try:
    import shap
    # Refit LGB1 on full real train + pseudo for SHAP
    shap_setpoints = StandSetpoints().fit(v4_train)
    v4_train_fe_shap = shap_setpoints.transform(v4_train.copy())
    pseudo_fe_shap   = shap_setpoints.transform(pseudo_test_rows.copy())
    aug_shap = pd.concat([v4_train_fe_shap, pseudo_fe_shap], ignore_index=True)
    X_shap = pd.concat([aug_shap[V4_FEATURES].reset_index(drop=True),
                        aug_shap[STAND_FE_COLS].reset_index(drop=True)], axis=1).values
    y_shap = aug_shap[TARGET].values
    sw_shap = np.where(aug_shap[ID_COL].isin(pseudo_coil_set) if ID_COL in aug_shap.columns
                       else np.array([False]*len(aug_shap)), PSEUDO_WEIGHT, 1.0)

    lgb1_shap = make_lgb1()
    lgb1_shap.fit(X_shap, y_shap, sample_weight=sw_shap)

    feature_names = V4_FEATURES + STAND_FE_COLS
    explainer = shap.TreeExplainer(lgb1_shap)
    shap_vals = explainer.shap_values(X_shap[:200])
    if isinstance(shap_vals, list):
        shap_vals = shap_vals[1]
    mean_abs_shap = np.abs(shap_vals).mean(axis=0)
    top5_idx = mean_abs_shap.argsort()[::-1][:5]
    top5_features = [(feature_names[i], round(float(mean_abs_shap[i]), 4)) for i in top5_idx]
    print(f"  SHAP top-5: {top5_features}")
except Exception as e:
    print(f"  SHAP failed ({e}) — skipping (not critical)")
    top5_features = [("SHAP_unavailable", 0.0)]


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 10: Save Artifacts
# ═══════════════════════════════════════════════════════════════════════════════

# OOF parquet (real-train only)
oof_df = v4_train[[ID_COL, TARGET]].copy()
oof_df["rank_avg_proba"] = oof_rank_avg
for m in MODEL_NAMES:
    oof_df[f"proba_{m}"] = oof_probas[m]
oof_df.to_parquet(V48_DIR / "oof_v48.parquet", index=False)
print(f"\n  oof_v48.parquet: {oof_df.shape}")

# Test proba parquet
test_df_out = v4_test[[ID_COL]].copy().reset_index(drop=True)
test_df_out["test_proba"] = test_rank_avg
test_df_out[f"pred_k{K_THRESHOLD}"] = submission_y
for m in MODEL_NAMES:
    test_df_out[f"proba_{m}"] = test_probas[m]
test_df_out.to_parquet(V48_DIR / "test_proba_v48.parquet", index=False)
print(f"  test_proba_v48.parquet: {test_df_out.shape}")

# Expected submission
sub = pd.DataFrame({ID_COL: v4_test[ID_COL].values, TARGET: submission_y})
sub.to_csv(V48_DIR / "expected_submission.csv", index=False)
print(f"  expected_submission.csv: positives={sub[TARGET].sum()}")


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 11: Gate Evaluation
# ═══════════════════════════════════════════════════════════════════════════════

V35_OOF_AUC = 0.87   # gate floor (context says V35 ~0.91, floor is 0.87)
SPEARMAN_CEILING = 0.95

gates = [
    ("OOF AUC >= 0.87 (real-train only)", bool(oof_auc >= V35_OOF_AUC), f"{oof_auc:.4f}"),
    ("Spearman vs V35 OOF < 0.95",        bool(spearman_v35 < SPEARMAN_CEILING), f"{spearman_v35:.4f}"),
    ("Pseudo-positive count == 132",       bool(n_pseudo == 132), f"{n_pseudo}"),
]

print("\n" + "=" * 70)
print("GATE EVALUATION")
print("=" * 70)
gates_passed = 0
for name, passed, val in gates:
    status = "PASS" if passed else "FAIL"
    print(f"  [{status}] {name} | {val}")
    if passed: gates_passed += 1
print(f"\n  {gates_passed}/{len(gates)} gates passed")


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 12: Summary Report
# ═══════════════════════════════════════════════════════════════════════════════

print("\n" + "=" * 70)
print("V48 SUMMARY FOR ORCHESTRATOR")
print("=" * 70)
print(f"  Approach    : Pseudo-label augmentation (132 vote=6 CoilIDs, weight=0.6)")
print(f"  Prevalence  : {prev_real:.1f}% real -> {prev_aug:.1f}% augmented (test ~45%)")
print(f"  OOF AUC     : {oof_auc:.4f} (real-train only) | CI [{ci_lower:.4f},{ci_upper:.4f}]")
print(f"  Spearman vs V35 OOF: ρ={spearman_v35:.4f}")
print(f"  Gates       : {gates_passed}/{len(gates)}")
print(f"  SHAP top-5  : {top5_features}")
print(f"\n  PER-MODEL AUCs:")
for m, d in per_model_aucs.items():
    print(f"    {m:12s}: {d['mean_oof_auc']:.4f} ± {d['fold_std']:.4f}")
print("=" * 70)
print("\nArtifacts saved to build_v48/. NO AUTO-SUBMIT — await V49 consensus merge.")


# Save full gate result JSON
gate_result = {
    "oof_auc": round(oof_auc, 4),
    "ci_lower": round(ci_lower, 4),
    "ci_upper": round(ci_upper, 4),
    "spearman_vs_v35_oof": round(float(spearman_v35), 4),
    "test_spearman": test_spearman,
    "pseudo_count": n_pseudo,
    "pseudo_weight": PSEUDO_WEIGHT,
    "prevalence_real_pct": round(prev_real, 2),
    "prevalence_aug_pct": round(prev_aug, 2),
    "oof_score_k200": round(oof_score_k, 2),
    "best_oof_k": best_k,
    "best_oof_score": round(best_oof_score, 2),
    "shap_top5": top5_features,
    "gates_passed": gates_passed,
    "total_gates": len(gates),
    "gates_detail": [{"name": g[0], "pass": bool(g[1]), "value": g[2]} for g in gates],
    "per_model_aucs": per_model_aucs,
    "avg_fold_std": round(avg_fold_std, 4),
}
with open(V48_DIR / "_gate_results.json", "w") as f:
    json.dump(gate_result, f, indent=2)
print("  _gate_results.json: saved")
