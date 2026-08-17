#!/usr/bin/env python3
"""
train_v46.py — V4 Base + Steel-Rolling Physics Features (Peer's 77.67 LB Recipe)
Tata Steel Hot Rolling Defect Detection

Architecture:
  BASE: V4 LGB+XGB+CatBoost stack → LR meta + Platt calibration
        scale_pos_weight=18.9, NO SMOTE (removed after V46 initial run showed
        SMOTE hurts in 87-dim space: kNN synthesis dominated by Zener magnitudes),
        5-fold StratifiedKFold seed=42

  V46b fix: drop SMOTE, rely on scale_pos_weight=18.9 for class imbalance
  This matches V40 (which achieved 0.87 OOF AUC without SMOTE on 62-dim).

  NEW:  ~36 steel-rolling physics features added to base 51 features
        = 87 total input features to LGB/XGB/CatBoost base learners

Physics feature groups:
  1. Zener-Hollomon Z per stand (11): logZ_1..6 + mean/std/F1F5drop/max/min
  2. Sims Force Residual (7): sims_res_1..5 + sims_abs_max + sims_abs_mean
     CRITICAL: Ridge trained on Y=0 rows from TRAIN fold ONLY (peer's exact pattern)
  3. Temp curvature (1): X4 - 2*X6 + X9
  4. Force-Temp coupling (9): ft_coupling_1..5 + max/mean/std/range
  5. Monotonicity breaks (2): temp_mono_breaks + force_mono_breaks
  6. Cooling rates (6): cooling_rate_total + cool_rate_1..5

Design principles (peer's 77.67 recipe):
  - Sims residual tells the model "this coil's force is abnormal for its temperature"
  - Zener-Hollomon captures metallurgical state — defects correlate with extreme Z values
  - fold_assign derived from SAME StratifiedKFold(5, seed=42) so Sims aligns with CV

Gates:
  - OOF AUC >= 0.93 (peer iter52 = 0.9534)
  - Spearman vs V4 OOF < 0.95 (meaningful diversity)
  - Estimated LB at K=200 >= 75

HARD RULES (do NOT modify):
  - NO submission generation
  - NO leakage: Sims Ridge uses Y=0 AND ti_mask rows only
  - NO fold_assign misalignment between Sims and CV loop
  - All stats (StandSetpoints medians) fit on TRAIN FOLD only
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
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import StandardScaler

warnings.filterwarnings("ignore")

# ── Add this build dir to path so we can import feature_engineering_v46 ───────
BUILD_DIR = Path(__file__).parent
sys.path.insert(0, str(BUILD_DIR))

from feature_engineering_v46 import (
    add_static_physics_features,
    compute_sims_residuals,
    attach_sims_residuals,
    ALL_STATIC_PHYSICS_COLS,
    SIMS_RESIDUAL_COLS,
)

# ── Paths ──────────────────────────────────────────────────────────────────────
ROOT   = Path("/home/ujjwal/Documents/J.A.R.V.I.S./data/hackathons/tata-steel-2026/round_1")
V4_DIR = ROOT / "build_v4"
OUT    = ROOT / "build_v46"
OUT.mkdir(parents=True, exist_ok=True)

# ── Constants ──────────────────────────────────────────────────────────────────
SEED    = 42
N_FOLDS = 5
TARGET  = "Y"
ID_COL  = "CoilID"
N_POS   = 154  # Fixed test positives for HE F1 formula: F1 = 200*TP / (K + N_POS)

# scale_pos_weight = neg / pos = 1286 / 66 ≈ 19.48 ≈ 18.9 (peer-confirmed)
SPW = 1286 / 66

print("=" * 70)
print("V46 — V4 Base + Steel-Rolling Physics Features (Peer 77.67 LB Recipe)")
print(f"scale_pos_weight={SPW:.2f} | {N_FOLDS}-fold StratifiedKFold seed={SEED} | SMOTE inside folds")
print("=" * 70)


# ═══════════════════════════════════════════════════════════════════════════════
# STEP 1: Load V4 data (51 SHAP-selected features + raw cols for physics)
# ═══════════════════════════════════════════════════════════════════════════════

print("\n[1/8] Loading data...")

train_v4 = pd.read_parquet(V4_DIR / "train_v4.parquet")
test_v4  = pd.read_parquet(V4_DIR / "test_v4.parquet")

with open(V4_DIR / "v4_final_features.json") as f:
    V4_FEATURES = json.load(f)["features"]  # 51 SHAP-selected

y      = train_v4[TARGET].values.astype(float)
n_train = len(train_v4)
n_test  = len(test_v4)
coil_train = train_v4[ID_COL].values
coil_test  = test_v4[ID_COL].values

print(f"  Train: {train_v4.shape} | Test: {test_v4.shape}")
print(f"  V4 features: {len(V4_FEATURES)}")
print(f"  Positives: {int(y.sum())} / {n_train} ({y.mean()*100:.2f}%)")

# Validate V4 features all present
missing_v4 = [f for f in V4_FEATURES if f not in train_v4.columns]
assert not missing_v4, f"Missing V4 features: {missing_v4}"
print(f"  V4 feature validation: ALL {len(V4_FEATURES)} present [OK]")


# ═══════════════════════════════════════════════════════════════════════════════
# STEP 2: Add static physics features (no fold isolation needed)
# ═══════════════════════════════════════════════════════════════════════════════

print("\n[2/8] Adding static physics features (Zener-Hollomon, FT-coupling, etc.)...")

train_fe = add_static_physics_features(train_v4)
test_fe  = add_static_physics_features(test_v4)

# Validate all static physics cols
missing_phys = [c for c in ALL_STATIC_PHYSICS_COLS if c not in train_fe.columns]
assert not missing_phys, f"Missing static physics cols: {missing_phys}"

print(f"  Static physics features added: {len(ALL_STATIC_PHYSICS_COLS)}")
print(f"  logZ_mean: train min={train_fe['logZ_mean'].min():.2f} max={train_fe['logZ_mean'].max():.2f}")
print(f"  temp_curvature: train min={train_fe['temp_curvature'].min():.2f} max={train_fe['temp_curvature'].max():.2f}")
print(f"  ft_coupling_mean: train min={train_fe['ft_coupling_mean'].min():.5f} max={train_fe['ft_coupling_mean'].max():.5f}")

# Defect vs non-defect distributions (sanity)
for col in ["logZ_mean", "temp_curvature", "ft_coupling_mean", "sims_abs_max" if "sims_abs_max" in train_fe.columns else "cooling_rate_total"]:
    if col not in train_fe.columns:
        continue
    pos_mean = train_fe.loc[y == 1, col].mean()
    neg_mean = train_fe.loc[y == 0, col].mean()
    print(f"  {col}: defect_mean={pos_mean:.4f}, normal_mean={neg_mean:.4f}, delta={pos_mean-neg_mean:+.4f}")


# ═══════════════════════════════════════════════════════════════════════════════
# STEP 3: Pre-compute fold assignments for Sims residuals
# CRITICAL: fold_assign MUST match the CV loop below (same SKF instance)
# ═══════════════════════════════════════════════════════════════════════════════

print("\n[3/8] Pre-computing fold assignments (must match CV loop)...")

SKF_SIMS = StratifiedKFold(n_splits=N_FOLDS, shuffle=True, random_state=SEED)
fold_assign = np.zeros(n_train, dtype=int)
for fold_idx, (_, val_idx) in enumerate(SKF_SIMS.split(np.zeros(n_train), y)):
    fold_assign[val_idx] = fold_idx

fold_counts = {f: int((fold_assign == f).sum()) for f in range(N_FOLDS)}
print(f"  Fold assignment: {fold_counts}")
print(f"  Total: {sum(fold_counts.values())} (expected {n_train})")
assert sum(fold_counts.values()) == n_train


# ═══════════════════════════════════════════════════════════════════════════════
# STEP 4: Compute Sims Force Residuals (FOLD-ISOLATED, Y=0 rows only in fold-train)
# ═══════════════════════════════════════════════════════════════════════════════

print("\n[4/8] Computing Sims Force Residuals (fold-isolated, Y=0 rows only)...")
print("  CRITICAL: Ridge trained on Y=0 AND in-train-fold rows ONLY. No leakage.")

R_tr, R_te = compute_sims_residuals(
    train_df=train_fe,
    test_df=test_fe,
    y_train=y,
    fold_assign=fold_assign,
    n_folds=N_FOLDS,
    ridge_alpha=1.0,
    verbose=True,
)

train_fe, test_fe = attach_sims_residuals(train_fe, test_fe, R_tr, R_te)

print(f"  Sims residuals attached: {len(SIMS_RESIDUAL_COLS)} features")
print(f"  sims_res_1 range: [{R_tr[:,0].min():.4f}, {R_tr[:,0].max():.4f}]")
print(f"  sims_abs_max: defect mean={train_fe.loc[y==1,'sims_abs_max'].mean():.4f}, "
      f"normal mean={train_fe.loc[y==0,'sims_abs_max'].mean():.4f}")


# ═══════════════════════════════════════════════════════════════════════════════
# STEP 5: Build feature set
# V4 51 features + 29 static physics + 7 Sims = 87 total
# ═══════════════════════════════════════════════════════════════════════════════

print("\n[5/8] Building feature matrix...")

# New physics cols (static + Sims)
NEW_PHYSICS_COLS = ALL_STATIC_PHYSICS_COLS + SIMS_RESIDUAL_COLS

# Full feature list: V4 base + physics
V46_FEATURES = V4_FEATURES + NEW_PHYSICS_COLS

# Check for duplicates
assert len(V46_FEATURES) == len(set(V46_FEATURES)), "Duplicate feature names!"

# Validate all present
missing_all = [f for f in V46_FEATURES if f not in train_fe.columns]
if missing_all:
    raise ValueError(f"Missing V46 features in train: {missing_all}")
missing_te = [f for f in V46_FEATURES if f not in test_fe.columns]
if missing_te:
    raise ValueError(f"Missing V46 features in test: {missing_te}")

X_train_raw = train_fe[V46_FEATURES].fillna(0).values.astype(np.float64)
X_test_raw  = test_fe[V46_FEATURES].fillna(0).values.astype(np.float64)

print(f"  V4 base features:       {len(V4_FEATURES)}")
print(f"  Static physics new:     {len(ALL_STATIC_PHYSICS_COLS)}")
print(f"  Sims residuals new:     {len(SIMS_RESIDUAL_COLS)}")
print(f"  TOTAL V46 features:     {len(V46_FEATURES)}")
print(f"  X_train: {X_train_raw.shape} | X_test: {X_test_raw.shape}")
print(f"  NaN check train: {np.isnan(X_train_raw).sum()} | test: {np.isnan(X_test_raw).sum()}")


# ═══════════════════════════════════════════════════════════════════════════════
# STEP 6: 5-Fold Stacking Loop
# LGB + XGB + CatBoost base learners → LR meta + Platt calibration
# SMOTE inside folds (fold-isolated, only on TRAIN fold)
# Sims residuals are already fold-correct (fold_assign aligned with SKF)
# ═══════════════════════════════════════════════════════════════════════════════

print("\n[6/8] Training 5-fold stacking (LGB + XGB + CatBoost → LR meta)...")

try:
    import lightgbm as lgb
    import xgboost as xgb
    from catboost import CatBoostClassifier
    print("  Libraries OK: lightgbm, xgboost, catboost")
except ImportError as e:
    raise ImportError(f"Missing library: {e}. Install: pip install lightgbm xgboost catboost")

# LightGBM config
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

# XGBoost config
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

# CatBoost config
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
# CRITICAL: This SKF must produce SAME fold splits as SKF_SIMS above
# Verified: same StratifiedKFold(5, shuffle=True, random_state=42) instance

oof_lgb = np.zeros(n_train)
oof_xgb = np.zeros(n_train)
oof_cat = np.zeros(n_train)

test_lgb_folds = np.zeros((n_test, N_FOLDS))
test_xgb_folds = np.zeros((n_test, N_FOLDS))
test_cat_folds = np.zeros((n_test, N_FOLDS))

fold_aucs_lgb = []
fold_aucs_xgb = []
fold_aucs_cat = []

# Verify fold alignment with Sims
print("  Verifying fold alignment (Sims fold_assign matches CV splits)...")
for fold_idx, (tr_idx, val_idx) in enumerate(SKF.split(np.zeros(n_train), y)):
    fa_val = fold_assign[val_idx]
    assert np.all(fa_val == fold_idx), f"Fold {fold_idx} alignment mismatch! Sims residuals corrupted."
print("  Fold alignment: ALL FOLDS OK [verified]")

print(f"\n  Starting CV loop (N_FOLDS={N_FOLDS})...")

for fold_idx, (tr_idx, val_idx) in enumerate(SKF.split(np.zeros(n_train), y)):
    y_tr  = y[tr_idx]
    y_val = y[val_idx]

    X_tr  = X_train_raw[tr_idx]
    X_val = X_train_raw[val_idx]

    print(f"\n  --- Fold {fold_idx+1}/{N_FOLDS} | train={len(tr_idx)}, val={len(val_idx)}, "
          f"pos_train={int(y_tr.sum())}, pos_val={int(y_val.sum())} ---")

    # NO SMOTE — scale_pos_weight handles imbalance
    # SMOTE was dropped after initial V46 run: in 87-dim space, kNN synthesis
    # is dominated by Zener-Hollomon values (range 43-51), generating noisy
    # synthetic positives that hurt all three base learners.
    X_tr_sm, y_tr_sm = X_tr, y_tr
    print(f"    No SMOTE: using {len(y_tr)} samples (pos={int(y_tr.sum())}), scale_pos_weight={SPW:.1f}")

    # ── LightGBM ─────────────────────────────────────────────────────────────
    model_lgb = lgb.LGBMClassifier(**LGB_PARAMS)
    model_lgb.fit(X_tr_sm, y_tr_sm)
    oof_lgb[val_idx] = model_lgb.predict_proba(X_val)[:, 1]
    test_lgb_folds[:, fold_idx] = model_lgb.predict_proba(X_test_raw)[:, 1]
    fold_aucs_lgb.append(roc_auc_score(y_val, oof_lgb[val_idx]))

    # ── XGBoost ──────────────────────────────────────────────────────────────
    model_xgb = xgb.XGBClassifier(**XGB_PARAMS)
    model_xgb.fit(X_tr_sm, y_tr_sm, verbose=False)
    oof_xgb[val_idx] = model_xgb.predict_proba(X_val)[:, 1]
    test_xgb_folds[:, fold_idx] = model_xgb.predict_proba(X_test_raw)[:, 1]
    fold_aucs_xgb.append(roc_auc_score(y_val, oof_xgb[val_idx]))

    # ── CatBoost ─────────────────────────────────────────────────────────────
    model_cat = CatBoostClassifier(**CAT_PARAMS)
    model_cat.fit(X_tr_sm, y_tr_sm)
    oof_cat[val_idx] = model_cat.predict_proba(X_val)[:, 1]
    test_cat_folds[:, fold_idx] = model_cat.predict_proba(X_test_raw)[:, 1]
    fold_aucs_cat.append(roc_auc_score(y_val, oof_cat[val_idx]))

    print(f"    LGB AUC={fold_aucs_lgb[-1]:.5f} | XGB AUC={fold_aucs_xgb[-1]:.5f} | CAT AUC={fold_aucs_cat[-1]:.5f}")

# Average test predictions across folds
test_lgb_avg = test_lgb_folds.mean(axis=1)
test_xgb_avg = test_xgb_folds.mean(axis=1)
test_cat_avg = test_cat_folds.mean(axis=1)

# Per-model OOF AUCs
auc_lgb = roc_auc_score(y, oof_lgb)
auc_xgb = roc_auc_score(y, oof_xgb)
auc_cat = roc_auc_score(y, oof_cat)
print(f"\n  Per-model OOF AUC: LGB={auc_lgb:.5f} | XGB={auc_xgb:.5f} | CAT={auc_cat:.5f}")
print(f"  V4 reference:      LGB=0.86150 | XGB=0.86680 | CAT=0.87560")
print(f"  Deltas:            LGB={auc_lgb-0.86150:+.5f} | XGB={auc_xgb-0.86680:+.5f} | CAT={auc_cat-0.87560:+.5f}")


# ═══════════════════════════════════════════════════════════════════════════════
# STEP 7: Meta-learner (LR + Platt calibration) + SHAP importance
# ═══════════════════════════════════════════════════════════════════════════════

print("\n[7/8] Training meta-learner (LR + Platt calibration)...")

X_meta_train = np.column_stack([oof_lgb, oof_xgb, oof_cat])
X_meta_test  = np.column_stack([test_lgb_avg, test_xgb_avg, test_cat_avg])

lr = LogisticRegression(C=1.0, max_iter=1000, random_state=SEED)
meta_cal = CalibratedClassifierCV(lr, method="sigmoid", cv=5)
meta_cal.fit(X_meta_train, y)

oof_meta  = meta_cal.predict_proba(X_meta_train)[:, 1]
test_meta = meta_cal.predict_proba(X_meta_test)[:, 1]

meta_auc = roc_auc_score(y, oof_meta)
print(f"  Meta OOF AUC: {meta_auc:.5f}")
print(f"  V4 reference: 0.88370 | Peer iter52: 0.95340")
print(f"  Delta vs V4:  {meta_auc - 0.88370:+.5f}")

# Bootstrap 95% CI
rng = np.random.default_rng(SEED)
boot_aucs = []
for _ in range(2000):
    idx = rng.choice(n_train, size=n_train, replace=True)
    if y[idx].sum() < 2:
        continue
    boot_aucs.append(roc_auc_score(y[idx], oof_meta[idx]))
ci_lo = float(np.percentile(boot_aucs, 2.5))
ci_hi = float(np.percentile(boot_aucs, 97.5))
print(f"  Bootstrap 95% CI: [{ci_lo:.5f}, {ci_hi:.5f}]")

# Per-fold averages
mean_fold_lgb = float(np.mean(fold_aucs_lgb))
mean_fold_xgb = float(np.mean(fold_aucs_xgb))
mean_fold_cat = float(np.mean(fold_aucs_cat))
std_fold_lgb  = float(np.std(fold_aucs_lgb))
std_fold_xgb  = float(np.std(fold_aucs_xgb))
std_fold_cat  = float(np.std(fold_aucs_cat))


# ═══════════════════════════════════════════════════════════════════════════════
# SHAP Feature Importance (on LGB — fastest)
# ═══════════════════════════════════════════════════════════════════════════════

print("\n  Computing SHAP feature importances (LGB last fold, train set)...")
try:
    import shap

    # Refit LGB on full train for SHAP (using last fold's SMOTE data as proxy)
    lgb_full = lgb.LGBMClassifier(**LGB_PARAMS)
    # No SMOTE — consistent with training loop
    lgb_full.fit(X_train_raw, y)
    explainer = shap.TreeExplainer(lgb_full)
    shap_vals = explainer.shap_values(X_train_raw)
    if isinstance(shap_vals, list):
        shap_vals = shap_vals[1]  # class 1

    mean_abs_shap = np.abs(shap_vals).mean(axis=0)
    top_idx = np.argsort(mean_abs_shap)[::-1][:20]

    shap_results = []
    print(f"  Top-20 SHAP features (LGB, mean |SHAP|):")
    for rank, idx in enumerate(top_idx, 1):
        print(f"    {rank:2d}. {V46_FEATURES[idx]:35s}  |SHAP|={mean_abs_shap[idx]:.6f}")
        shap_results.append({"rank": rank, "feature": V46_FEATURES[idx], "mean_abs_shap": float(mean_abs_shap[idx])})

    # Check if physics features are in top 10 (gate validation)
    top10_feats = set(V46_FEATURES[i] for i in top_idx[:10])
    sims_in_top10 = any("sims" in f for f in top10_feats)
    zener_in_top10 = any("logZ" in f for f in top10_feats)
    print(f"\n  Physics in top-10: Sims={sims_in_top10}, Zener={zener_in_top10}")
    shap_available = True

except ImportError:
    print("  SHAP not available — skipping (install: pip install shap)")
    shap_results = [{"rank": i+1, "feature": V46_FEATURES[i], "mean_abs_shap": None}
                    for i in range(min(20, len(V46_FEATURES)))]
    sims_in_top10 = None
    zener_in_top10 = None
    shap_available = False


# ═══════════════════════════════════════════════════════════════════════════════
# Estimated LB calculation using HE F1 formula
# F1 = 200 * TP / (K + N_POS), N_POS=154 (fixed test positives)
# ═══════════════════════════════════════════════════════════════════════════════

print("\n  Estimated LB via HE F1 formula: F1 = 200*TP/(K+N_POS), N_POS=154")

def he_f1(tp: int, k: int, n_pos: int = N_POS) -> float:
    return 200 * tp / (k + n_pos)

# Estimate TPs from OOF: at each K, the fraction of positives we'd catch
sorted_meta = np.argsort(oof_meta)[::-1]

# Best OOF-based LB estimate over range of K
best_oof_score = 0.0
best_oof_k = 200
for k_cand in range(100, 280):
    top_k_idx = sorted_meta[:k_cand]
    tp_oof = int(y[top_k_idx].sum())
    f1_cand = he_f1(tp_oof, k_cand)
    if f1_cand > best_oof_score:
        best_oof_score = f1_cand
        best_oof_k = k_cand

# Fixed K=200 and K=216 (peer's K)
top200_idx = sorted_meta[:200]
tp200 = int(y[top200_idx].sum())
f1_200 = he_f1(tp200, 200)

top216_idx = sorted_meta[:216]
tp216 = int(y[top216_idx].sum())
f1_216 = he_f1(tp216, 216)

# Legacy delta-based estimate (for comparison)
lb_delta_est = meta_auc * 100 + 2.67

print(f"  OOF TP@K=200: {tp200}/66 | F1@K=200: {f1_200:.2f}")
print(f"  OOF TP@K=216: {tp216}/66 | F1@K=216: {f1_216:.2f}")
print(f"  OOF best F1 @ K={best_oof_k}: {best_oof_score:.2f} (TP={int(y[sorted_meta[:best_oof_k]].sum())})")
print(f"  Delta-based est: {lb_delta_est:.2f} (AUC*100+2.67, legacy method)")
print(f"\n  Peer banked: 77.67 LB @ K=216 (iter52 with same physics features)")
print(f"  V4 banked:   72.83 LB @ K=200 (V44 consensus)")
print(f"  V46 est:     {f1_200:.2f} @K=200 | {f1_216:.2f} @K=216")


# ═══════════════════════════════════════════════════════════════════════════════
# Spearman vs V4 OOF (diversity check)
# ═══════════════════════════════════════════════════════════════════════════════

print("\n  Computing Spearman vs existing paradigms...")

spearman_results = {}
ref_paradigms = {
    "v4_meta":       (ROOT / "build_v4"  / "oof_v4.parquet",  "oof_meta"),
    "v40_proba":     (ROOT / "build_v40" / "oof_v40.parquet", "oof_proba"),
    "v41_proba":     (ROOT / "build_v41" / "oof_v41.parquet", "oof_proba"),
    "v43_rp":        (ROOT / "build_v43" / "oof_v43.parquet", "oof_proba"),
}

for name, (path, col) in ref_paradigms.items():
    try:
        ref_df = pd.read_parquet(path)
        if col in ref_df.columns:
            ref_arr = ref_df[col].values
        else:
            num_cols = [c for c in ref_df.columns if c not in (ID_COL, "Y", "y")]
            ref_arr = ref_df[num_cols[0]].values

        if len(ref_arr) == n_train:
            r, _ = spearmanr(oof_meta, ref_arr)
            spearman_results[name] = float(r)
            tag = "DIVERSE" if abs(r) < 0.80 else ("MODERATE" if abs(r) < 0.92 else "HIGH_CORR")
            print(f"  V46 vs {name}: ρ={r:+.4f} [{tag}]")
        else:
            print(f"  {name}: length mismatch")
    except Exception as e:
        print(f"  {name}: FAILED — {e}")

spearman_vs_v4 = spearman_results.get("v4_meta", None)


# ═══════════════════════════════════════════════════════════════════════════════
# STEP 8: Save artifacts
# ═══════════════════════════════════════════════════════════════════════════════

print(f"\n[8/8] Saving artifacts to {OUT}...")

# OOF parquet: CoilID, oof_proba (meta), y
oof_df = pd.DataFrame({
    "CoilID":    coil_train,
    "oof_proba": oof_meta,
    "y":         y.astype(int),
})
oof_df.to_parquet(OUT / "oof_v46.parquet", index=False)
print(f"  oof_v46.parquet: {oof_df.shape}")

# Test proba parquet: CoilID, test_proba
test_df_out = pd.DataFrame({
    "CoilID":     coil_test,
    "test_proba": test_meta,
})
test_df_out.to_parquet(OUT / "test_proba_v46.parquet", index=False)
print(f"  test_proba_v46.parquet: {test_df_out.shape}")

# SHAP importance JSON
shap_json = {
    "top_20_features": shap_results,
    "sims_in_top10": sims_in_top10,
    "zener_in_top10": zener_in_top10,
    "available": shap_available,
}
with open(OUT / "shap_importance_v46.json", "w") as f:
    json.dump(shap_json, f, indent=2)
print(f"  shap_importance_v46.json: saved")

# Summary JSON for orchestrator
summary = {
    "oof_auc":              round(meta_auc, 5),
    "oof_auc_ci_lo":        round(ci_lo, 5),
    "oof_auc_ci_hi":        round(ci_hi, 5),
    "per_model_oof_auc": {
        "lgb": round(auc_lgb, 5),
        "xgb": round(auc_xgb, 5),
        "cat": round(auc_cat, 5),
    },
    "fold_aucs": {
        "lgb": [round(a, 5) for a in fold_aucs_lgb],
        "xgb": [round(a, 5) for a in fold_aucs_xgb],
        "cat": [round(a, 5) for a in fold_aucs_cat],
    },
    "mean_fold_auc": {
        "lgb": round(mean_fold_lgb, 5),
        "xgb": round(mean_fold_xgb, 5),
        "cat": round(mean_fold_cat, 5),
    },
    "est_lb": {
        "K200": round(f1_200, 2),
        "K216": round(f1_216, 2),
        "best": round(best_oof_score, 2),
        "best_k": int(best_oof_k),
        "legacy_delta": round(lb_delta_est, 2),
    },
    "oof_tp": {
        "K200": int(tp200),
        "K216": int(tp216),
        "total_pos": int(y.sum()),
    },
    "spearman_vs_existing": spearman_results,
    "n_features": {
        "v4_base": len(V4_FEATURES),
        "static_physics": len(ALL_STATIC_PHYSICS_COLS),
        "sims_residuals": len(SIMS_RESIDUAL_COLS),
        "total": len(V46_FEATURES),
    },
    "gates": {
        "oof_auc_gte_093": bool(meta_auc >= 0.93),
        "spearman_v4_lt_095": bool(abs(spearman_vs_v4) < 0.95) if spearman_vs_v4 is not None else None,
        "est_lb_k200_gte_75": bool(f1_200 >= 75.0),
    },
    "v4_reference": {"oof_auc": 0.88370, "lb": 56.98},
    "peer_reference": {"oof_auc": 0.95340, "lb": 77.67, "k": 216},
    "v44_banked": {"lb": 72.83, "k": 200},
}

with open(OUT / "cv_summary_v46.json", "w") as f:
    json.dump(summary, f, indent=2)
print(f"  cv_summary_v46.json: saved")


# ═══════════════════════════════════════════════════════════════════════════════
# CV Report
# ═══════════════════════════════════════════════════════════════════════════════

gates_ok = all(v for v in summary["gates"].values() if v is not None)
gates_summary = "\n".join(
    f"  - {'PASS' if v else 'FAIL'}: {k} = {v}"
    for k, v in summary["gates"].items()
)

spearman_lines = "\n".join(
    f"- V46 vs {name}: ρ={r:+.4f}  {'[DIVERSE <0.80]' if abs(r)<0.80 else '[MODERATE <0.92]' if abs(r)<0.92 else '[HIGH CORR]'}"
    for name, r in spearman_results.items()
)

fold_table_lgb = "\n".join(f"| {i+1} | {a:.5f} |" for i, a in enumerate(fold_aucs_lgb))
fold_table_xgb = "\n".join(f"| {i+1} | {a:.5f} |" for i, a in enumerate(fold_aucs_xgb))
fold_table_cat = "\n".join(f"| {i+1} | {a:.5f} |" for i, a in enumerate(fold_aucs_cat))

top5_shap = "\n".join(
    f"- {r['rank']}. {r['feature']}: {r['mean_abs_shap']:.6f}" if r["mean_abs_shap"] is not None
    else f"- {r['rank']}. {r['feature']}: (SHAP not computed)"
    for r in shap_results[:5]
) if shap_results else "- SHAP not available"

report = f"""# V46 CV Report — V4 Base + Steel-Rolling Physics Features

**Date:** 2026-05-24
**Builder:** ml-engineer-agent (Jarvis)
**Architecture:** LGB+XGB+CatBoost → LR meta + Platt | NO SMOTE (dropped: hurt in 87-dim) | scale_pos_weight={SPW:.2f}
**Physics recipe:** Peer Ratnesh's 77.67 LB feature set (Zener-Hollomon + Sims + FT coupling + curvature + mono breaks + cooling)

---

## Gate Results

{gates_summary}

Gate: OOF AUC >= 0.93 | Spearman vs V4 < 0.95 | Est LB @K=200 >= 75

**Overall gate: {'PASS — ready to merge into V47 consensus' if gates_ok else 'FAIL — do NOT merge until gates clear'}**

---

## OOF AUC Summary

| Metric | Value | Reference |
|---|---|---|
| Meta OOF AUC | **{meta_auc:.5f}** | V4=0.88370, Peer=0.95340 |
| Bootstrap 95% CI | [{ci_lo:.5f}, {ci_hi:.5f}] | |
| Delta vs V4 | {meta_auc - 0.88370:+.5f} | |
| Delta vs Peer | {meta_auc - 0.95340:+.5f} | |
| LGB OOF AUC | {auc_lgb:.5f} | V4 LGB=0.86150 |
| XGB OOF AUC | {auc_xgb:.5f} | V4 XGB=0.86680 |
| CAT OOF AUC | {auc_cat:.5f} | V4 CAT=0.87560 |

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

## Estimated LB (HE F1 Formula: F1 = 200*TP/(K+N_POS), N_POS=154)

| K | OOF TP | Est LB |
|---|---|---|
| 200 | {tp200}/66 | **{f1_200:.2f}** |
| 216 (peer K) | {tp216}/66 | **{f1_216:.2f}** |
| Best (K={best_oof_k}) | {int(y[sorted_meta[:best_oof_k]].sum())}/66 | **{best_oof_score:.2f}** |

Legacy delta-based estimate (AUC*100+2.67): {lb_delta_est:.2f}

**Gap to peer's 77.67:** {f1_216 - 77.67:+.2f} @K=216
**Gap to V44 banked 72.83:** {f1_200 - 72.83:+.2f} @K=200

---

## Top-5 SHAP Features (LGB, mean |SHAP|)

{top5_shap}

Physics in top-10: Sims={sims_in_top10}, Zener={zener_in_top10}

---

## Spearman vs Existing Paradigms

{spearman_lines if spearman_lines else "- No reference OOFs found"}

Target: ρ < 0.95 vs V4 meta = meaningful diversity for consensus

---

## Feature Set

| Group | Count | Columns |
|---|---|---|
| V4 base (SHAP-selected) | {len(V4_FEATURES)} | X-features + poly + neighbor + iso_score |
| Zener-Hollomon | 11 | logZ_1..6 + mean/std/F1F5drop/max/min |
| Sims residuals (fold-isolated) | 7 | sims_res_1..5 + sims_abs_max/mean |
| Temp curvature | 1 | temp_curvature = X4 - 2*X6 + X9 |
| F/T coupling | 9 | ft_coupling_1..5 + max/mean/std/range |
| Mono breaks | 2 | temp_mono_breaks + force_mono_breaks |
| Cooling rates | 6 | cooling_rate_total + cool_rate_1..5 |
| **TOTAL V46** | **{len(V46_FEATURES)}** | |

---

## Design Notes

**Sims Residual Leak Safety:**
- Ridge fit on Y=0 AND ti_mask rows (training fold) only — never sees val labels
- fold_assign verified aligned with CV loop (same SKF(5, seed=42) instance)
- Test residuals = average of 5 fold-Ridge predictors

**Why physics features jump LB from ~73 to ~77 (peer's result):**
- Zener-Hollomon captures metallurgical recrystallization state — extreme Z = rapid
  strain rate at a given temp → increased dislocation density → surface defect risk
- Sims residual is the strongest signal: a coil whose rolling force is anomalous
  for its temperature is experiencing abnormal plastic flow → defect precursor
- FT coupling normalizes force by temperature → removes co-linearity artifact
- Mono breaks detect process upsets (re-heating between stands) → rare, diagnostic

---

## Top-3 Risks

1. **OOF AUC vs LB gap:** Sims residuals are fold-proper but their signal strength
   in OOF may not fully transfer to test (different process conditions per batch).
   The 0.95 CI lower bound is the true safety net.

2. **Physics feature scaling:** Zener-Hollomon log values are in range 30-40 (large).
   LGB handles this natively. XGB/CatBoost may benefit from StandardScaler on physics
   cols — not done here to preserve V4 exact parity. Monitor per-model delta.

3. **OOF ≠ LB calibration for physics:** The +2.67 calibration delta was fitted on
   V4-tier models (no physics). With physics features, OOF AUC→LB relationship may
   shift. The HE F1 formula estimate (based on OOF TPs) is more reliable than the
   delta method for V46+.

---

## Merge into V47 Consensus?

**{'YES — all gates pass' if gates_ok else 'CONDITIONAL — check failed gates above'}**

If gates pass: feed oof_v46.parquet + test_proba_v46.parquet into V47 consensus
union alongside V4/V40/V41/V43. Recommend rank-average or rank-product with V43
(which is already the V44 banked submission's basis).

---

## Files

- `oof_v46.parquet` — 1352 rows: CoilID, oof_proba, y
- `test_proba_v46.parquet` — 339 rows: CoilID, test_proba
- `cv_summary_v46.json` — machine-readable summary for orchestrator
- `shap_importance_v46.json` — top-20 features + physics validation
- `feature_engineering_v46.py` — physics feature pipeline (importable)
- `train_v46.py` — this training script
- `approach.md` — human-readable design notes
- `cv_report_v46.md` — this file
"""

with open(OUT / "cv_report_v46.md", "w") as f:
    f.write(report)
print(f"  cv_report_v46.md: saved")


# Approach.md
approach_content = f"""# V46 Approach — V4 Base + Steel-Rolling Physics Features

## TL;DR
Peer Ratnesh's physics features (Zener-Hollomon + Sims + FT coupling + curvature + mono breaks + cooling)
layered on top of V4's 51 SHAP-selected features. Peer jumped from 62 → 77.67 LB with the same architecture.

## Problem Setup
- Binary classification: defect (Y=1) in hot-rolling coils
- Train: 1352 rows, 66 positives (4.88%)
- Test: 339 rows, N_POS=154 (confirmed test positives)
- Score: HE F1 = 200*TP/(K+154)

## Architecture
- Base: LGB + XGB + CatBoost (5-fold StratKFold seed=42, NO SMOTE, scale_pos_weight={SPW:.2f})
- Meta: LR + Platt calibration on [oof_lgb, oof_xgb, oof_cat]
- New: {len(NEW_PHYSICS_COLS)} physics features appended to base 51 = {len(V46_FEATURES)} total

## Physics Features Added ({len(NEW_PHYSICS_COLS)} total)
1. Zener-Hollomon (11): logZ per stand + aggregates — metallurgical state
2. Sims residuals (7, fold-isolated Y=0-only): how far force deviates from normal process
3. Temp curvature (1): stand-skip / non-linear path detector
4. F/T coupling (9): force normalized by temp per stand
5. Mono breaks (2): count of non-monotonic stand transitions
6. Cooling rates (6): total + per-stage temp drop

## Sims Leak Safety (CRITICAL)
Ridge trained on Y=0 AND fold-train rows ONLY. fold_assign verified aligned with CV loop.

## Results
- Meta OOF AUC: {meta_auc:.5f} (V4=0.88370, Peer=0.95340)
- Est LB @K=200: {f1_200:.2f}
- Est LB @K=216: {f1_216:.2f}
- V44 banked: 72.83 @K=200
- Peer banked: 77.67 @K=216

## Lineage
V1 → V2 (SMOTE) → V3 (stacking) → V4 (neighbor FE + meta, 0.8837 AUC)
→ V46 (physics features on V4 base, peer's 77.67 recipe)
"""

with open(OUT / "approach.md", "w") as f:
    f.write(approach_content)
print(f"  approach.md: saved")


# ═══════════════════════════════════════════════════════════════════════════════
# FINAL SUMMARY FOR ORCHESTRATOR
# ═══════════════════════════════════════════════════════════════════════════════

print("\n" + "=" * 70)
print("V46 COMPLETE — ORCHESTRATOR REPORT")
print("=" * 70)
print(f"1. OOF AUC:      {meta_auc:.5f}  (V4={0.88370:.5f}, peer={0.95340:.5f})")
print(f"   Bootstrap CI: [{ci_lo:.5f}, {ci_hi:.5f}]")
print(f"   Gate >= 0.93: {'PASS' if meta_auc >= 0.93 else 'FAIL'}")
print(f"\n2. Top-5 SHAP features (see shap_importance_v46.json for full list)")
for r in shap_results[:5]:
    v = f"{r['mean_abs_shap']:.6f}" if r['mean_abs_shap'] is not None else "N/A"
    print(f"   {r['rank']}. {r['feature']}: {v}")
print(f"   Sims in top-10: {sims_in_top10} | Zener in top-10: {zener_in_top10}")
print(f"\n3. Spearman vs V4 meta: {spearman_vs_v4}")
if spearman_vs_v4 is not None:
    print(f"   Gate < 0.95: {'PASS' if abs(spearman_vs_v4) < 0.95 else 'FAIL'}")
print(f"\n4. Estimated LB:")
print(f"   @K=200: {f1_200:.2f}  (TP={tp200}/66)")
print(f"   @K=216: {f1_216:.2f}  (TP={tp216}/66)")
print(f"   Gate >= 75 @K=200: {'PASS' if f1_200 >= 75.0 else 'FAIL'}")
print(f"\n5. Top-3 risks:")
print(f"   R1: OOF AUC may not transfer — Sims signal depends on test process conditions")
print(f"   R2: Physics features not scaled — large Zener values (30-40) could affect XGB")
print(f"   R3: +2.67 delta calibration from V4 may not hold for physics-augmented models")
print(f"\n6. Ready to merge into V47 consensus? {'YES' if gates_ok else 'NO — check gates'}")
print(f"\n   Files: {OUT}")
print("=" * 70)
