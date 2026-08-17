"""
train_v55.py — Stealth-Defect Specialist (R22 recommendation)

Architecture: Second-stage LightGBM with Focal Loss, trained on the BORDERLINE CLUSTER
that V44 finds hardest — specifically targeting the ~18 training positives (OOF)
that V44's K=200 consensus misses.

Key design decisions:
- Borderline cluster = rows where V44_rank ∈ [100, 400] (OOF). All training Y=1 included.
- Focal loss (γ=2.0, α=0.85) — down-weights easy negatives in the cluster
- init_score = log(pos_prior / (1 - pos_prior)) — CRITICAL for focal to work
- scale_pos_weight calibrated to CLUSTER imbalance (not full dataset 19x)
- 5-fold StratifiedKFold seed=42 (matches V44 folds for consensus alignment)
- Features: same 105-feature set as V35 (51 V4 SHAP + 54 stand-FE)

Validation gate (per R22 spec):
  Gate 1: OOF AUC >= 0.80 (specialist on hard cluster — ceiling lower than V44)
  Gate 2: Hard-positive mean OOF proba >= 0.45 (genuine new signal lift)
  Gate 3: Spearman vs V44 in [0.40, 0.70] (genuinely different, not echoing)

Outputs:
  oof_v55.parquet     — 1352 rows: CoilID, Y, oof_proba
  test_proba_v55.parquet — 339 rows: CoilID, test_proba
  cv_report_v55.md    — gates + metrics
  approach.md         — design notes

Reference: Max Halford focal loss recipe
  https://maxhalford.github.io/blog/lightgbm-focal-loss/
"""

from __future__ import annotations

import json
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold

import lightgbm as lgb

warnings.filterwarnings("ignore")

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE    = Path("/home/ujjwal/Documents/J.A.R.V.I.S.")
RAW_DIR = BASE / "data set of tata steel/dataset"
V4_DIR  = BASE / "data/hackathons/tata-steel-2026/round_1/build_v4"
V35_DIR = BASE / "data/hackathons/tata-steel-2026/round_1/build_v35"
V55_DIR = BASE / "data/hackathons/tata-steel-2026/round_1/build_v55"
V55_DIR.mkdir(parents=True, exist_ok=True)

ROUND_DIR = BASE / "data/hackathons/tata-steel-2026/round_1"

# ── Constants ──────────────────────────────────────────────────────────────────
SEED        = 42
N_FOLDS     = 5
TARGET      = "Y"
ID_COL      = "CoilID"
TEMP_COLS   = ["X4","X5","X6","X7","X8","X9"]
FORCE_COLS  = ["X29","X30","X31","X32","X33"]

# V44 borderline cluster: ranks 100-400 (OOF) + all Y=1
# Derived from V44_score = mean rank_pct across v35/v39/v40/v41/v43
V44_BORDERLINE_RANK_LOW  = 100
V44_BORDERLINE_RANK_HIGH = 400

# Validation gate thresholds (per R22 spec)
GATE_OOF_AUC       = 0.80
GATE_HARD_POS_PROBA = 0.45    # V55 must lift hard-positive mean proba above this
GATE_SPEARMAN_LOW  = 0.40
GATE_SPEARMAN_HIGH = 0.70

# Hard-positive definition: V44 OOF rank > K=200 AND Y=1
V44_K = 200

print("=" * 70)
print("V55 — Stealth-Defect Focal-Loss Specialist")
print(f"Borderline cluster: V44 rank [{V44_BORDERLINE_RANK_LOW}, {V44_BORDERLINE_RANK_HIGH}] + all Y=1")
print(f"Focal loss: γ=2.0, α=0.85 | {N_FOLDS}-fold StratifiedKFold seed={SEED}")
print("=" * 70)


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 1: Stand-FE (V33 recipe) — fold-isolated setpoints
# ═══════════════════════════════════════════════════════════════════════════════

class StandSetpoints:
    """Fold-isolated setpoint statistics. Identical to V35 — no leakage."""

    def __init__(self):
        self.temp_medians = None; self.force_medians = None
        self.temp_stds = None;    self.force_stds = None
        self.x35_high_median = None; self.x35_high_std = None
        self.is_fitted = False

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
                (df["X35"] - self.x35_high_median) / self.x35_high_std, 0.0)
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
    [f"res_force_{i+1}"     for i in range(5)] +
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
assert len(STAND_FE_COLS) == 54, f"Expected 54 stand-FE cols, got {len(STAND_FE_COLS)}"
print(f"Stand-FE columns: {len(STAND_FE_COLS)}")


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 2: Focal Loss for LightGBM
# Reference: https://maxhalford.github.io/blog/lightgbm-focal-loss/
# ═══════════════════════════════════════════════════════════════════════════════

class FocalLossLGBM:
    """
    Focal loss for LightGBM custom objective.
    γ (gamma) > 0 down-weights easy examples (well-classified negatives).
    α (alpha) up-weights the positive class gradient.

    CRITICAL: init_score must be set to log-odds of class prior in the TRAINING
    CLUSTER, not the full dataset. Otherwise the initial loss landscape is wrong.
    """
    def __init__(self, gamma: float = 2.0, alpha: float = 0.85):
        self.gamma = gamma
        self.alpha = alpha

    def init_score(self, y_train: np.ndarray) -> float:
        """Log-odds of class prior in training cluster."""
        p = np.clip(np.mean(y_train), 1e-7, 1 - 1e-7)
        return float(np.log(p / (1.0 - p)))

    def fobj(self, y_pred: np.ndarray, dataset: lgb.Dataset):
        """Custom gradient + hessian for focal loss."""
        y_true = dataset.get_label()
        # Convert log-odds to probability
        p = 1.0 / (1.0 + np.exp(-y_pred))
        p = np.clip(p, 1e-7, 1.0 - 1e-7)

        # Focal weights
        # For positives (y=1): weight = α * (1-p)^γ
        # For negatives (y=0): weight = (1-α) * p^γ
        focal_weight = np.where(
            y_true == 1,
            self.alpha * np.power(1.0 - p, self.gamma),
            (1.0 - self.alpha) * np.power(p, self.gamma),
        )

        # Cross-entropy gradient
        # dL/dy_pred = p - y_true (for standard cross-entropy)
        # With focal weighting:
        grad = focal_weight * (p - y_true)

        # For hessian we use the "working hessian" trick:
        # h = focal_weight * p * (1 - p)
        # This is an approximation that ignores second-order focal terms
        # but is stable and standard for LightGBM custom obj
        hess = focal_weight * p * (1.0 - p) + 1e-9

        return grad, hess

    def feval(self, y_pred: np.ndarray, dataset: lgb.Dataset):
        """Track standard AUC (not focal loss) for monitoring."""
        y_true = dataset.get_label()
        p = 1.0 / (1.0 + np.exp(-y_pred))
        if y_true.sum() < 1 or y_true.sum() == len(y_true):
            return "auc", 0.5, True
        return "auc", float(roc_auc_score(y_true, p)), True


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 3: Load Data
# ═══════════════════════════════════════════════════════════════════════════════

print("\n[1/7] Loading V4 parquets and building V44 OOF consensus...")

v4_train = pd.read_parquet(V4_DIR / "train_v4.parquet")
v4_test  = pd.read_parquet(V4_DIR / "test_v4.parquet")

with open(V4_DIR / "v4_final_features.json") as f:
    V4_FEATURES = json.load(f)["features"]   # 51 SHAP-selected

y_full = v4_train[TARGET].values
n_train = len(v4_train)
n_test  = len(v4_test)
coil_ids_train = v4_train[ID_COL].values
coil_ids_test  = v4_test[ID_COL].values

print(f"  Train: {n_train} rows, {int(y_full.sum())} positives")
print(f"  Test:  {n_test} rows")
print(f"  V4 features: {len(V4_FEATURES)}")
print(f"  Total features (V4+stand-FE): {len(V4_FEATURES)+len(STAND_FE_COLS)}")


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 4: Build V44 OOF Consensus Score (to identify borderline cluster)
# ═══════════════════════════════════════════════════════════════════════════════

print("\n[2/7] Building V44 OOF consensus score...")

oof35 = pd.read_parquet(ROUND_DIR / "build_v35/oof_v35.parquet")
oof39 = pd.read_parquet(ROUND_DIR / "build_v39/oof_v39.parquet")
oof40 = pd.read_parquet(ROUND_DIR / "build_v40/oof_v40.parquet")
oof41 = pd.read_parquet(ROUND_DIR / "build_v41/oof_v41.parquet")
oof43 = pd.read_parquet(ROUND_DIR / "build_v43/oof_v43.parquet")

v44_base = oof35[["CoilID", "Y"]].copy()
v44_base = v44_base.merge(oof39[["CoilID","oof_proba"]].rename(columns={"oof_proba":"v39r"}), on="CoilID")
v44_base = v44_base.merge(oof40[["CoilID","oof_proba"]].rename(columns={"oof_proba":"v40r"}), on="CoilID")
v44_base = v44_base.merge(oof41[["CoilID","oof_proba"]].rename(columns={"oof_proba":"v41r"}), on="CoilID")
v44_base = v44_base.merge(oof43[["CoilID","oof_proba"]].rename(columns={"oof_proba":"v43r"}), on="CoilID")

# Rank-pct each paradigm (same as V44 consensus logic)
v44_base["v35_pct"] = oof35["rank_avg_proba"].rank(pct=True)
v44_base["v39_pct"] = v44_base["v39r"].rank(pct=True)
v44_base["v40_pct"] = v44_base["v40r"].rank(pct=True)
v44_base["v41_pct"] = v44_base["v41r"].rank(pct=True)
v44_base["v43_pct"] = v44_base["v43r"].rank(pct=True)
v44_base["V44_score"] = v44_base[["v35_pct","v39_pct","v40_pct","v41_pct","v43_pct"]].mean(axis=1)
v44_base["V44_rank"]  = v44_base["V44_score"].rank(ascending=False, method="first")

# Hard positives: Y=1 rows NOT in V44 top-K=200
hard_pos_coils = set(
    v44_base.loc[(v44_base.Y == 1) & (v44_base.V44_rank > V44_K), "CoilID"].tolist()
)
all_pos_coils  = set(v44_base.loc[v44_base.Y == 1, "CoilID"].tolist())
borderline_coils = set(
    v44_base.loc[
        (v44_base.V44_rank >= V44_BORDERLINE_RANK_LOW) &
        (v44_base.V44_rank <= V44_BORDERLINE_RANK_HIGH),
        "CoilID"
    ].tolist()
)

# Cluster = borderline rows + ALL positives
cluster_coils = borderline_coils | all_pos_coils
n_cluster = len(cluster_coils)
n_cluster_pos = len(cluster_coils & all_pos_coils)
n_cluster_neg = n_cluster - n_cluster_pos

print(f"  V44 K=200 TPs (OOF): {len(all_pos_coils) - len(hard_pos_coils)}/{len(all_pos_coils)}")
print(f"  Hard positives (V44 rank > {V44_K}): {len(hard_pos_coils)}")
print(f"  Borderline cluster (rank {V44_BORDERLINE_RANK_LOW}-{V44_BORDERLINE_RANK_HIGH}): {len(borderline_coils)} rows")
print(f"  V55 training cluster: {n_cluster} rows | pos={n_cluster_pos}, neg={n_cluster_neg}")
print(f"  Cluster imbalance: {n_cluster_neg/n_cluster_pos:.2f}:1")

# Compute V44 mean proba for hard positives (for gate validation)
model_cols_35 = [c for c in oof35.columns if c.startswith("proba_")]
oof35["v35_mean_raw"] = oof35[model_cols_35].mean(axis=1)
hard_pos_v44_mean_proba = float(
    oof35.loc[oof35.CoilID.isin(hard_pos_coils), "v35_mean_raw"].mean()
)
print(f"  V44 hard-positive mean raw proba (V35): {hard_pos_v44_mean_proba:.4f}")


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 5: 5-Fold Training on Borderline Cluster
# ═══════════════════════════════════════════════════════════════════════════════

print(f"\n[3/7] Training V55 focal-loss LGB on {n_cluster}-row cluster ({N_FOLDS}-fold)...")

focal_loss = FocalLossLGBM(gamma=2.0, alpha=0.85)

# OOF and test accumulators (full 1352-row space)
oof_proba_full  = np.zeros(n_train, dtype=float)
oof_covered     = np.zeros(n_train, dtype=bool)   # which rows were val-set in their fold
test_proba_sum  = np.zeros(n_test,  dtype=float)

# Build a mapping: CoilID → row index in v4_train
coil_to_idx = {cid: i for i, cid in enumerate(coil_ids_train)}
cluster_mask = np.array([coil_ids_train[i] in cluster_coils for i in range(n_train)])

skf = StratifiedKFold(n_splits=N_FOLDS, shuffle=True, random_state=SEED)
fold_aucs_cluster = []    # AUC on val fold (cluster rows only)
fold_aucs_full    = []    # AUC on full val fold
fold_hard_probas  = []    # Mean proba of hard positives in val fold

# Fit StandSetpoints once on full train (for test inference)
sp_full = StandSetpoints()
sp_full.fit(v4_train)
test_fe_full = sp_full.transform(v4_test.copy())
X_test_arr = pd.concat([
    test_fe_full[V4_FEATURES].reset_index(drop=True),
    test_fe_full[STAND_FE_COLS].reset_index(drop=True),
], axis=1).values.astype(np.float32)

for fold_idx, (tr_idx, val_idx) in enumerate(skf.split(np.zeros(n_train), y_full)):
    # Only use cluster rows for TRAINING in this fold
    tr_cluster_mask = cluster_mask[tr_idx]
    tr_cluster_idx  = tr_idx[tr_cluster_mask]

    y_tr  = y_full[tr_cluster_idx]
    y_val = y_full[val_idx]

    if y_tr.sum() == 0:
        print(f"  Fold {fold_idx+1}: NO positives in cluster train — skipping")
        continue

    # Fit StandSetpoints on full train fold (not just cluster) for consistency
    sp = StandSetpoints()
    sp.fit(v4_train.iloc[tr_idx])

    # Apply stand-FE
    tr_fe  = sp.transform(v4_train.iloc[tr_cluster_idx].copy())
    val_fe = sp.transform(v4_train.iloc[val_idx].copy())

    X_tr  = pd.concat([
        tr_fe[V4_FEATURES].reset_index(drop=True),
        tr_fe[STAND_FE_COLS].reset_index(drop=True),
    ], axis=1).values.astype(np.float32)

    X_val = pd.concat([
        val_fe[V4_FEATURES].reset_index(drop=True),
        val_fe[STAND_FE_COLS].reset_index(drop=True),
    ], axis=1).values.astype(np.float32)

    # Compute init_score for this cluster fold
    init_score_val = focal_loss.init_score(y_tr)

    # scale_pos_weight for the CLUSTER (not full dataset 19x)
    n_pos_tr = int(y_tr.sum())
    n_neg_tr = int((y_tr == 0).sum())
    cluster_spw = (n_neg_tr / max(n_pos_tr, 1)) * 3   # triple weight per R22 spec

    # LightGBM 4.x: custom objective goes in params dict as a callable
    lgb_params = {
        "objective":         focal_loss.fobj,   # callable — LGB4 style
        "boosting_type":     "gbdt",
        "num_leaves":        15,
        "min_child_samples": 3,
        "subsample":         0.7,
        "colsample_bytree":  0.7,
        "scale_pos_weight":  cluster_spw,
        "seed":              SEED + fold_idx,
        "verbose":           -1,
        "n_jobs":            -1,
    }

    # init_score must be an array of the same length as y_train
    init_score_arr_tr  = np.full(len(y_tr), init_score_val, dtype=float)
    init_score_arr_val = np.full(len(y_val), init_score_val, dtype=float)

    # Build LightGBM datasets with custom init_score
    lgb_train_ds = lgb.Dataset(
        X_tr, label=y_tr,
        init_score=init_score_arr_tr,
        free_raw_data=False,
    )
    lgb_val_ds = lgb.Dataset(
        X_val, label=y_val,
        init_score=init_score_arr_val,
        reference=lgb_train_ds,
        free_raw_data=False,
    )

    # Train with custom objective (LGB4: objective in params, feval separate)
    booster = lgb.train(
        lgb_params,
        lgb_train_ds,
        num_boost_round=600,
        valid_sets=[lgb_val_ds],
        feval=focal_loss.feval,
        callbacks=[lgb.early_stopping(50, verbose=False), lgb.log_evaluation(period=-1)],
    )

    # Predict: custom obj returns raw margin (log-odds relative to init_score).
    # Full log-odds = init_score + booster.predict(X)
    # Probability = sigmoid(init_score + raw_prediction)
    val_raw  = booster.predict(X_val)
    val_prob = 1.0 / (1.0 + np.exp(-(init_score_val + val_raw)))
    val_prob = np.clip(val_prob, 1e-7, 1.0 - 1e-7)

    test_raw  = booster.predict(X_test_arr)
    test_prob = 1.0 / (1.0 + np.exp(-(init_score_val + test_raw)))
    test_prob = np.clip(test_prob, 1e-7, 1.0 - 1e-7)

    # Store OOF
    oof_proba_full[val_idx] = val_prob
    oof_covered[val_idx]    = True
    test_proba_sum += test_prob

    # AUC on val fold
    if y_val.sum() > 0:
        auc_val_full = roc_auc_score(y_val, val_prob)
    else:
        auc_val_full = 0.5
    fold_aucs_full.append(auc_val_full)

    # AUC restricted to cluster rows in val
    val_cluster_mask = np.array([coil_ids_train[i] in cluster_coils for i in val_idx])
    if val_cluster_mask.sum() > 0 and y_val[val_cluster_mask].sum() > 0:
        auc_cluster = roc_auc_score(y_val[val_cluster_mask], val_prob[val_cluster_mask])
    else:
        auc_cluster = 0.5
    fold_aucs_cluster.append(auc_cluster)

    # Hard-positive mean proba in val fold
    val_hard_mask = np.array([coil_ids_train[i] in hard_pos_coils for i in val_idx])
    if val_hard_mask.sum() > 0:
        mean_hard = float(val_prob[val_hard_mask].mean())
        fold_hard_probas.append(mean_hard)
    else:
        mean_hard = float("nan")

    n_pos_val = int(y_val.sum())
    n_hard_val = int(val_hard_mask.sum())
    print(f"  Fold {fold_idx+1}: AUC_full={auc_val_full:.4f} | AUC_cluster={auc_cluster:.4f} | "
          f"hard_pos_in_val={n_hard_val} | hard_mean_proba={mean_hard:.4f} | "
          f"best_iter={booster.best_iteration} | cluster_spw={cluster_spw:.1f}")

# Average test predictions
test_proba_final = test_proba_sum / N_FOLDS

# ── Final OOF metrics ──────────────────────────────────────────────────────────
print("\n[4/7] Computing final OOF metrics...")

oof_auc_full = roc_auc_score(y_full, oof_proba_full)
hard_pos_idx = np.array([coil_to_idx[c] for c in hard_pos_coils if c in coil_to_idx])
v55_hard_pos_mean = float(oof_proba_full[hard_pos_idx].mean()) if len(hard_pos_idx) > 0 else 0.0

print(f"  OOF AUC (full 1352 rows):    {oof_auc_full:.5f}")
print(f"  V44 hard-positive mean proba: {hard_pos_v44_mean_proba:.4f}")
print(f"  V55 hard-positive mean proba: {v55_hard_pos_mean:.4f}")
print(f"  Delta (V55-V44):              {v55_hard_pos_mean - hard_pos_v44_mean_proba:+.4f}")
print(f"  Per-fold AUC mean (full): {np.mean(fold_aucs_full):.5f} ± {np.std(fold_aucs_full):.5f}")

# Spearman vs V44
v44_oof_scores = v44_base.set_index("CoilID")["V44_score"].loc[coil_ids_train].values
spearman_vs_v44, _ = spearmanr(oof_proba_full, v44_oof_scores)
print(f"  Spearman vs V44: {spearman_vs_v44:+.5f}")


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 6: Gate Validation
# ═══════════════════════════════════════════════════════════════════════════════

print("\n[5/7] Gate validation...")

gate1_pass = oof_auc_full >= GATE_OOF_AUC
gate2_pass = v55_hard_pos_mean >= GATE_HARD_POS_PROBA
gate3_pass = GATE_SPEARMAN_LOW <= spearman_vs_v44 <= GATE_SPEARMAN_HIGH

print(f"  Gate 1 (OOF AUC >= {GATE_OOF_AUC}): {'PASS' if gate1_pass else 'FAIL'} — {oof_auc_full:.5f}")
print(f"  Gate 2 (hard-pos mean >= {GATE_HARD_POS_PROBA}): {'PASS' if gate2_pass else 'FAIL'} — {v55_hard_pos_mean:.4f}")
print(f"  Gate 3 (Spearman in [{GATE_SPEARMAN_LOW}, {GATE_SPEARMAN_HIGH}]): {'PASS' if gate3_pass else 'FAIL'} — {spearman_vs_v44:+.4f}")
all_gates_pass = gate1_pass and gate2_pass and gate3_pass
print(f"\n  VERDICT: {'ALL GATES PASS — blend with V44' if all_gates_pass else 'GATES FAILED — investigate before blend'}")


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 7: Save Outputs
# ═══════════════════════════════════════════════════════════════════════════════

print("\n[6/7] Saving outputs...")

oof_df = pd.DataFrame({
    "CoilID": coil_ids_train,
    "Y":      y_full,
    "oof_proba": oof_proba_full,
})
oof_df.to_parquet(V55_DIR / "oof_v55.parquet", index=False)
print(f"  Saved oof_v55.parquet ({len(oof_df)} rows)")

test_df = pd.DataFrame({
    "CoilID":    coil_ids_test,
    "test_proba": test_proba_final,
})
test_df.to_parquet(V55_DIR / "test_proba_v55.parquet", index=False)
print(f"  Saved test_proba_v55.parquet ({len(test_df)} rows)")


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 8: CV Report
# ═══════════════════════════════════════════════════════════════════════════════

print("\n[7/7] Writing cv_report_v55.md...")

report_lines = [
    "# V55 CV Report — Stealth-Defect Focal-Loss Specialist",
    "",
    f"**Date:** 2026-05-24",
    f"**Banked best:** V44 K=200 = 72.83 LB",
    f"**Architecture:** LightGBM + Focal Loss (γ=2.0, α=0.85) on borderline cluster",
    f"**Training cluster:** V44 OOF rank [{V44_BORDERLINE_RANK_LOW}-{V44_BORDERLINE_RANK_HIGH}] + all Y=1 = {n_cluster} rows",
    f"**Features:** 105 (51 V4 SHAP + 54 stand-FE) — identical to V35",
    f"**CV:** StratifiedKFold({N_FOLDS}, shuffle=True, seed={SEED})",
    "",
    "---",
    "",
    "## Gate Results",
    "",
    f"| Gate | Threshold | Value | Pass? |",
    f"|------|-----------|-------|-------|",
    f"| OOF AUC >= {GATE_OOF_AUC} | {GATE_OOF_AUC} | {oof_auc_full:.5f} | {'PASS' if gate1_pass else 'FAIL'} |",
    f"| Hard-positive mean proba >= {GATE_HARD_POS_PROBA} | {GATE_HARD_POS_PROBA} | {v55_hard_pos_mean:.4f} | {'PASS' if gate2_pass else 'FAIL'} |",
    f"| Spearman in [{GATE_SPEARMAN_LOW}, {GATE_SPEARMAN_HIGH}] | [{GATE_SPEARMAN_LOW}, {GATE_SPEARMAN_HIGH}] | {spearman_vs_v44:+.4f} | {'PASS' if gate3_pass else 'FAIL'} |",
    f"| **Overall** | — | — | **{'PASS' if all_gates_pass else 'FAIL'}** |",
    "",
    "---",
    "",
    "## OOF AUC Summary",
    "",
    f"| Metric | Value |",
    f"|--------|-------|",
    f"| OOF AUC (full 1352 rows) | **{oof_auc_full:.5f}** |",
    f"| Per-fold AUC mean (full) | {np.mean(fold_aucs_full):.5f} ± {np.std(fold_aucs_full):.5f} |",
    f"| Per-fold AUC mean (cluster) | {np.mean(fold_aucs_cluster):.5f} ± {np.std(fold_aucs_cluster):.5f} |",
    "",
    "---",
    "",
    "## Hard-Positive Analysis",
    "",
    f"Hard positives = Y=1 rows where V44 OOF rank > {V44_K} (not in V44 top-{V44_K})",
    f"Count: **{len(hard_pos_coils)}** of 66 training positives",
    "",
    f"| Model | Hard-Positive Mean Proba |",
    f"|-------|--------------------------|",
    f"| V44 (V35 mean raw proba) | {hard_pos_v44_mean_proba:.4f} |",
    f"| V55 (this model) | **{v55_hard_pos_mean:.4f}** |",
    f"| Delta | **{v55_hard_pos_mean - hard_pos_v44_mean_proba:+.4f}** |",
    "",
    "**Interpretation:**",
    f"{'V55 LIFTS hard positives above 0.45 threshold — genuine new signal found.' if gate2_pass else 'V55 does NOT lift hard positives above 0.45 — limited new signal. Blend cautiously.'}",
    "",
    "---",
    "",
    "## Spearman vs V44",
    "",
    f"| Comparison | Spearman ρ | Interpretation |",
    f"|------------|------------|----------------|",
    f"| V55 vs V44 | {spearman_vs_v44:+.5f} | {'GOOD DIVERSITY (0.40-0.70 target)' if gate3_pass else ('TOO CORRELATED — V55 echoing V44' if spearman_vs_v44 > GATE_SPEARMAN_HIGH else 'TOO DIVERSE / ANTI-CORRELATED — check stability')} |",
    "",
    "---",
    "",
    "## Per-Fold Results",
    "",
    f"| Fold | AUC (full) | AUC (cluster) |",
    f"|------|------------|---------------|",
]
for i, (af, ac) in enumerate(zip(fold_aucs_full, fold_aucs_cluster)):
    report_lines.append(f"| {i+1} | {af:.5f} | {ac:.5f} |")
report_lines += [
    f"| **Mean** | **{np.mean(fold_aucs_full):.5f}** | **{np.mean(fold_aucs_cluster):.5f}** |",
    f"| **Std** | {np.std(fold_aucs_full):.5f} | {np.std(fold_aucs_cluster):.5f} |",
    "",
    "---",
    "",
    "## Recommended Blend",
    "",
    "```",
    "blend_score = 0.70 * V44_score_pct + 0.30 * V55_oof_proba_pct",
    "```",
    "",
    "Rationale: V44 banked 72.83 — it carries strong ranking signal for the 80%+ of",
    "positives it already finds. V55 contributes specialist signal for the missed 18.",
    "70/30 split preserves V44's core ranking while injecting V55's hard-positive lift.",
    "",
    "**Before blending:** Run consensus_v55.py to verify submission overlap with V44 K=200",
    f"meets >= 90% threshold (>= 180 of 200 rows must overlap).",
    "",
    "---",
    "",
    "## Top-3 Risks",
    "",
    "1. **OOF vs LB calibration gap (V27 lesson):** Focal-loss probabilities are not",
    "   calibrated. They must be used as RANKING signal only (rank_pct before blending).",
    "   Never use raw focal probability as a threshold-based classifier for this metric.",
    "",
    "2. **Cluster overfitting:** V55 is trained on only 340 rows (25% of data).",
    "   The hard positives ({len(hard_pos_coils)} rows) may have idiosyncratic OOF behavior.",
    "   Gate 2 (hard-pos mean >= 0.45) guards against this — if failed, cluster is too noisy.",
    "",
    "3. **Spearman outside target range:** If Spearman > 0.70, V55 is echoing V44 and the",
    "   blend adds no new information. If < 0.40, V55 may be predicting something orthogonal",
    "   to the true positives (overfitting to cluster noise). Both cases reduce blend value.",
    "",
    "---",
    "",
    "## Verdict",
    "",
    f"**{'BLEND RECOMMENDED' if all_gates_pass else 'DO NOT BLEND — gates failed'}**",
    "",
    f"All gates: {'PASS (3/3)' if all_gates_pass else f'FAIL ({sum([gate1_pass, gate2_pass, gate3_pass])}/3)'}",
    "",
    "Files:",
    f"- `oof_v55.parquet` — 1352 rows: CoilID, Y, oof_proba",
    f"- `test_proba_v55.parquet` — 339 rows: CoilID, test_proba",
    f"- `cv_report_v55.md` — this file",
    f"- `approach.md` — design notes",
]

report_text = "\n".join(report_lines)
(V55_DIR / "cv_report_v55.md").write_text(report_text)
print(f"  Saved cv_report_v55.md")

print("\n" + "=" * 70)
print("V55 COMPLETE")
print(f"  OOF AUC:              {oof_auc_full:.5f}  (gate >= {GATE_OOF_AUC}: {'PASS' if gate1_pass else 'FAIL'})")
print(f"  Hard-pos mean proba:  {v55_hard_pos_mean:.4f}   (V44={hard_pos_v44_mean_proba:.4f}, delta={v55_hard_pos_mean - hard_pos_v44_mean_proba:+.4f})")
print(f"  Spearman vs V44:      {spearman_vs_v44:+.5f}")
print(f"  Gates:                {'ALL PASS' if all_gates_pass else f'FAIL ({sum([gate1_pass, gate2_pass, gate3_pass])}/3)'}")
print("=" * 70)
