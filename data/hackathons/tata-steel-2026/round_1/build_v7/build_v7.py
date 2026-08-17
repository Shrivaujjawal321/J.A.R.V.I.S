"""
Tata Steel AI Hackathon 2026 - Round 1
BUILD V7: Chemistry Breakthrough + Temporal Features

Key additions over V5:
- X42 (%P) and X46 (%S) -- the two MISSING strongest predictors
- Log transforms for skewed chemistry distributions
- Chemistry ratios: Si/Mn, Mn/P, Si/P, CarbonEq proxy
- Temporal rolling defect rates (Y_roll10, Y_roll20, Y_roll50) -- CV-safe
- Cross-feature interactions: coiling temp x Mn, coiling temp x X49, S x X49
- Optional two-stage architecture if meta AUC >= 0.888
- V7 + V5 blends at multiple weights

Usage:
    /home/ujjwal/Documents/J.A.R.V.I.S./.venv/bin/python build_v7/build_v7.py
"""

import json
import warnings
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

warnings.filterwarnings("ignore")

ROUND1 = Path("/home/ujjwal/Documents/J.A.R.V.I.S./data/hackathons/tata-steel-2026/round_1")
V5_DIR = ROUND1 / "build_v5"
V7_DIR = ROUND1 / "build_v7"
V7_DIR.mkdir(exist_ok=True)

V5_META_AUC = 0.8886139780385504
V5_OOF_SCORE = 53.70058610799352
V4_ACTUAL_LB = 56.98
CALIB_CORRECTION = V4_ACTUAL_LB - 54.31  # +2.67

from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import roc_auc_score
import lightgbm as lgb
import xgboost as xgb
import catboost as cb
import shap

print("=" * 70)
print("BUILD V7 -- Chemistry Breakthrough + Temporal Features")
print("=" * 70)

# ============================================================
# Phase A: Load V5 data
# ============================================================
print("\n[Phase A] Loading V5 data...")

train_v5 = pd.read_parquet(V5_DIR / "train_v5.parquet")
test_v5  = pd.read_parquet(V5_DIR / "test_v5.parquet")

with open(V5_DIR / "feature_list_v5.json") as f:
    feat_cfg = json.load(f)
v5_features = feat_cfg["features"]

print(f"  Train: {train_v5.shape}  |  Test: {test_v5.shape}")
print(f"  V5 features: {len(v5_features)}")
print(f"  Defect rate: {train_v5['Y'].mean():.4f} ({int(train_v5['Y'].sum())}/{len(train_v5)})")

for col in ["X42", "X46"]:
    if col in train_v5.columns:
        print(f"  {col} confirmed in V5 parquet (mean={train_v5[col].mean():.5f})")
    else:
        print(f"  WARNING: {col} not in V5 parquet columns!")

print("\n  [Chemistry correlation check against Y]")
for col in ["X41","X42","X43","X44","X46","X49"]:
    if col in train_v5.columns:
        r, p_val = stats.pointbiserialr(train_v5[col], train_v5["Y"])
        m0 = train_v5.loc[train_v5["Y"]==0, col].mean()
        m1 = train_v5.loc[train_v5["Y"]==1, col].mean()
        t_stat, _ = stats.ttest_ind(
            train_v5.loc[train_v5["Y"]==1, col],
            train_v5.loc[train_v5["Y"]==0, col]
        )
        print(f"    {col}: r={r:+.4f}  t={t_stat:+.2f}  neg_mean={m0:.5f}  pos_mean={m1:.5f}")

# ============================================================
# Phase A: Feature engineering
# ============================================================
print("\n[Phase A] Engineering V7 chemistry + interaction features...")

def add_chemistry_features(df):
    df = df.copy()
    for col in ["X42", "X46"]:
        if col not in df.columns:
            df[col] = 0.0
    # Log transforms
    df["v7_log_X42"] = np.log(df["X42"] + 1e-6)
    df["v7_log_X46"] = np.log(df["X46"] + 1e-6)
    # Ratios
    df["v7_X43_over_X41"] = df["X43"] / (df["X41"] + 1e-6)   # Si/Mn
    df["v7_X41_over_X42"] = df["X41"] / (df["X42"] + 1e-6)   # Mn/P
    df["v7_X43_over_X42"] = df["X43"] / (df["X42"] + 1e-6)   # Si/P
    df["v7_CarbonEq_proxy"] = df["X41"] / 6.0 + df["X44"] / 5.0
    # Interactions
    df["v7_X14_x_X41"] = df["X14"] * df["X41"]
    df["v7_X14_x_X49"] = df["X14"] * df["X49"]
    df["v7_X46_x_X49"] = df["X46"] * df["X49"]
    return df

train_v7 = add_chemistry_features(train_v5)
test_v7  = add_chemistry_features(test_v5)

# Rolling feature placeholders (filled per-fold for train; from all-train for test)
ROLL_WINDOWS = (10, 20, 50)
for w in ROLL_WINDOWS:
    train_v7[f"v7_Y_roll{w}"] = np.nan
    # Test: use all-train Y rolling end value
    roll_all = pd.Series(train_v5["Y"].values).rolling(window=w, min_periods=1).mean()
    test_v7[f"v7_Y_roll{w}"] = float(roll_all.iloc[-1])

V7_NEW_DET = [
    "X42", "X46",
    "v7_log_X42", "v7_log_X46",
    "v7_X43_over_X41",
    "v7_X41_over_X42",
    "v7_X43_over_X42",
    "v7_CarbonEq_proxy",
    "v7_X14_x_X41",
    "v7_X14_x_X49",
    "v7_X46_x_X49",
]
V7_ROLL = [f"v7_Y_roll{w}" for w in ROLL_WINDOWS]
V7_ALL_NEW = V7_NEW_DET + V7_ROLL
v7_features = v5_features + V7_ALL_NEW

print(f"  V5: {len(v5_features)} + V7 new det: {len(V7_NEW_DET)} + roll: {len(V7_ROLL)} = {len(v7_features)} total")

# Correlation check on new features
print("\n  [V7 new feature correlations]")
for col in V7_NEW_DET:
    vals = train_v7[col].fillna(train_v7[col].median())
    r, p_val = stats.pointbiserialr(vals, train_v7["Y"])
    print(f"    {col}: r={r:+.4f}  p={p_val:.2e}")

with open(V7_DIR / "feature_list_v7.json", "w") as f:
    json.dump({
        "features": v7_features,
        "v5_features": v5_features,
        "v7_new_deterministic": V7_NEW_DET,
        "v7_rolling_features": V7_ROLL,
        "n_features": len(v7_features),
        "n_v5": len(v5_features),
        "n_v7_new": len(V7_ALL_NEW),
    }, f, indent=2)
print(f"\n  feature_list_v7.json saved")

# ============================================================
# Phase B: 5-fold stacking
# ============================================================
print("\n" + "=" * 70)
print("[Phase B] 5-fold StratifiedKFold stacking (seed=42)")
print("=" * 70)

LGB_PARAMS = dict(
    objective="binary", metric="auc", learning_rate=0.03,
    num_leaves=31, min_child_samples=20,
    subsample=0.8, colsample_bytree=0.8,
    reg_alpha=0.1, reg_lambda=1.0,
    n_estimators=1000, random_state=42, verbose=-1, n_jobs=-1,
)
XGB_PARAMS = dict(
    early_stopping_rounds=50,
    objective="binary:logistic", eval_metric="auc", learning_rate=0.03,
    max_depth=4, subsample=0.8, colsample_bytree=0.8,
    reg_alpha=0.1, reg_lambda=1.0,
    n_estimators=1000, random_state=42, verbosity=0, n_jobs=-1,
)
CAT_PARAMS = dict(
    iterations=1000, learning_rate=0.03, depth=6, l2_leaf_reg=3,
    eval_metric="AUC", random_seed=42, verbose=False, thread_count=-1,
)

SKF = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
y_train = train_v7["Y"].values
n_train, n_test = len(train_v7), len(test_v7)

oof_lgb = np.zeros(n_train)
oof_xgb = np.zeros(n_train)
oof_cat = np.zeros(n_train)
test_lgb = np.zeros(n_test)
test_xgb = np.zeros(n_test)
test_cat = np.zeros(n_test)
fold_aucs = {"lgb": [], "xgb": [], "cat": []}

# Feature columns split: deterministic vs rolling
DET_COLS = [f for f in v7_features if "Y_roll" not in f]
ROLL_COLS = V7_ROLL

# Test feature matrix (rolling already filled from all-train)
test_X = test_v7[DET_COLS + ROLL_COLS].values.astype(np.float64)

print(f"\n  {len(DET_COLS)} det + {len(ROLL_COLS)} roll = {len(v7_features)} features")
print(f"  Positives: {int(y_train.sum())} / {n_train}")

for fold_i, (tr_idx, val_idx) in enumerate(SKF.split(np.zeros(n_train), y_train)):
    print(f"\n  --- Fold {fold_i+1}/5 ({y_train[tr_idx].sum():.0f} pos train | {y_train[val_idx].sum():.0f} pos val) ---")

    # CV-safe rolling: compute from fold-train Y only
    fold_train_y = pd.Series(y_train[tr_idx])
    fold_roll_end = {}
    fold_train_roll = {}
    for w in ROLL_WINDOWS:
        rs = fold_train_y.rolling(window=w, min_periods=1).mean()
        fold_train_roll[f"v7_Y_roll{w}"] = rs.values
        fold_roll_end[f"v7_Y_roll{w}"] = float(rs.iloc[-1])

    # Build train/val matrices
    tr_df  = train_v7.iloc[tr_idx].copy()
    val_df = train_v7.iloc[val_idx].copy()

    for col, arr in fold_train_roll.items():
        tr_df[col] = arr
    for col, val_scalar in fold_roll_end.items():
        val_df[col] = val_scalar

    X_tr  = tr_df[DET_COLS + ROLL_COLS].values.astype(np.float64)
    X_val = val_df[DET_COLS + ROLL_COLS].values.astype(np.float64)
    y_tr  = y_train[tr_idx]
    y_val = y_train[val_idx]
    spc   = float((y_tr==0).sum()) / max(float((y_tr==1).sum()), 1)

    # LGB
    m_lgb = lgb.LGBMClassifier(**{**LGB_PARAMS, "scale_pos_weight": spc})
    m_lgb.fit(X_tr, y_tr, eval_set=[(X_val, y_val)],
              callbacks=[lgb.early_stopping(50, verbose=False), lgb.log_evaluation(-1)])
    oof_lgb[val_idx] = m_lgb.predict_proba(X_val)[:,1]
    test_lgb += m_lgb.predict_proba(test_X)[:,1] / 5
    a = roc_auc_score(y_val, oof_lgb[val_idx]); fold_aucs["lgb"].append(a)
    print(f"    LGB AUC={a:.4f}")

    # XGB
    m_xgb = xgb.XGBClassifier(**{**XGB_PARAMS, "scale_pos_weight": spc})
    m_xgb.fit(X_tr, y_tr, eval_set=[(X_val, y_val)], verbose=False)
    oof_xgb[val_idx] = m_xgb.predict_proba(X_val)[:,1]
    test_xgb += m_xgb.predict_proba(test_X)[:,1] / 5
    a = roc_auc_score(y_val, oof_xgb[val_idx]); fold_aucs["xgb"].append(a)
    print(f"    XGB AUC={a:.4f}")

    # CatBoost
    m_cat = cb.CatBoostClassifier(**{**CAT_PARAMS, "class_weights": [1, spc]})
    m_cat.fit(X_tr, y_tr, eval_set=[(X_val, y_val)],
              use_best_model=True, early_stopping_rounds=50, verbose=False)
    oof_cat[val_idx] = m_cat.predict_proba(X_val)[:,1]
    test_cat += m_cat.predict_proba(test_X)[:,1] / 5
    a = roc_auc_score(y_val, oof_cat[val_idx]); fold_aucs["cat"].append(a)
    print(f"    CAT AUC={a:.4f}")

lgb_mean = np.mean(fold_aucs["lgb"])
xgb_mean = np.mean(fold_aucs["xgb"])
cat_mean  = np.mean(fold_aucs["cat"])
print(f"\n  LGB mean AUC: {lgb_mean:.4f}  (V5: 0.8853)")
print(f"  XGB mean AUC: {xgb_mean:.4f}  (V5: 0.8386)")
print(f"  CAT mean AUC: {cat_mean:.4f}  (V5: 0.8890)")

# Meta: LR + Platt calibration
print("\n[Phase B] Meta learner (LR + Platt calibration)...")
X_meta_oof  = np.column_stack([oof_lgb, oof_xgb, oof_cat])
X_meta_test = np.column_stack([test_lgb, test_xgb, test_cat])

meta_model = CalibratedClassifierCV(
    LogisticRegression(C=1.0, max_iter=1000, random_state=42),
    method="sigmoid", cv=5
)
meta_model.fit(X_meta_oof, y_train)
oof_meta  = meta_model.predict_proba(X_meta_oof)[:,1]
test_meta = meta_model.predict_proba(X_meta_test)[:,1]

meta_oof_auc = roc_auc_score(y_train, oof_meta)
print(f"\n  Meta OOF AUC: {meta_oof_auc:.6f}  (V5: {V5_META_AUC:.6f})")
print(f"  Delta vs V5:  {meta_oof_auc - V5_META_AUC:+.6f}")

# ============================================================
# Phase C: Two-stage (if meta AUC >= 0.888)
# ============================================================
two_stage_done = False
oof_stage2 = np.zeros(n_train)
test_stage2_full = np.zeros(n_test)

print("\n[Phase C] Two-stage check...")
if meta_oof_auc >= 0.888:
    print(f"  Meta AUC {meta_oof_auc:.4f} >= 0.888 -- attempting two-stage")
    S1_T = 0.01
    s_mask_tr = oof_meta >= S1_T
    s_mask_te = test_meta >= S1_T
    n_susp_tr = s_mask_tr.sum()
    n_pos_susp = int(y_train[s_mask_tr].sum())
    print(f"  Stage-1 suspects (train): {n_susp_tr}  ({n_pos_susp} pos, recall={n_pos_susp/y_train.sum():.3f})")
    print(f"  Stage-1 suspects (test):  {s_mask_te.sum()}")

    S2_FEATS = [f for f in ["X14","X41","X42","X46","X49","v7_X43_over_X41",
                             "v7_X14_x_X41","v7_log_X42","v7_log_X46","v7_CarbonEq_proxy"]
                if f in train_v7.columns]

    if n_susp_tr >= 50 and n_pos_susp >= 10 and len(S2_FEATS) >= 3:
        # Build stage-2 data (use all-train rolling for Y_roll features)
        susp_tr_df = train_v7[s_mask_tr].copy()
        susp_te_df = test_v7[s_mask_te].copy()
        for w in (20, 50):
            col = f"v7_Y_roll{w}"
            roll_all = pd.Series(y_train).rolling(window=w, min_periods=1).mean()
            # assign by position
            susp_tr_df[col] = roll_all.iloc[np.where(s_mask_tr)[0]].values
            susp_te_df[col] = float(roll_all.iloc[-1])
        s2_all_feats = S2_FEATS + ["v7_Y_roll20","v7_Y_roll50"]
        s2_all_feats = [f for f in s2_all_feats if f in susp_tr_df.columns]

        X_s2   = susp_tr_df[s2_all_feats].fillna(0).values
        y_s2   = y_train[s_mask_tr]
        X_s2te = susp_te_df[s2_all_feats].fillna(0).values if s_mask_te.sum() > 0 else np.zeros((0, len(s2_all_feats)))

        if len(np.unique(y_s2)) > 1:
            oof_s2_arr = np.zeros(n_susp_tr)
            skf2 = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
            for _, (tr2, va2) in enumerate(skf2.split(X_s2, y_s2)):
                spc2 = float((y_s2[tr2]==0).sum()) / max(float((y_s2[tr2]==1).sum()), 1)
                m2 = cb.CatBoostClassifier(iterations=500, learning_rate=0.05, depth=4,
                                           class_weights=[1, spc2], random_seed=42, verbose=False)
                m2.fit(X_s2[tr2], y_s2[tr2],
                       eval_set=[(X_s2[va2], y_s2[va2])],
                       use_best_model=True, early_stopping_rounds=30, verbose=False)
                oof_s2_arr[va2] = m2.predict_proba(X_s2[va2])[:,1]

            s2_auc = roc_auc_score(y_s2, oof_s2_arr)
            print(f"  Stage-2 OOF AUC (on suspects): {s2_auc:.4f}")

            # Full-train Stage-2
            spc_all = float((y_s2==0).sum()) / max(float((y_s2==1).sum()), 1)
            m2_final = cb.CatBoostClassifier(iterations=500, learning_rate=0.05, depth=4,
                                              class_weights=[1, spc_all], random_seed=42, verbose=False)
            m2_final.fit(X_s2, y_s2, verbose=False)

            oof_stage2[s_mask_tr] = oof_meta[s_mask_tr] * oof_s2_arr
            if X_s2te.shape[0] > 0:
                test_stage2_full[s_mask_te] = test_meta[s_mask_te] * m2_final.predict_proba(X_s2te)[:,1]
            two_stage_done = True
            print(f"  Two-stage complete.")
        else:
            print("  Stage-2 skipped: no label diversity in suspects")
    else:
        print(f"  Stage-2 skipped: suspects={n_susp_tr}, pos={n_pos_susp}, feats={len(S2_FEATS)}")
else:
    print(f"  Meta AUC {meta_oof_auc:.4f} < 0.888 -- skipping two-stage")

# ============================================================
# Phase D: Threshold sweep
# ============================================================
print("\n" + "=" * 70)
print("[Phase D] Threshold sweep -- maximize (R+P)/2")
print("=" * 70)

def sweep_threshold(oof_p, y_true, label=""):
    rows = []
    for t in np.unique(oof_p):
        pred = (oof_p >= t).astype(int)
        tp = int(((pred==1)&(y_true==1)).sum())
        fp = int(((pred==1)&(y_true==0)).sum())
        fn = int(((pred==0)&(y_true==1)).sum())
        rec  = tp / max(tp+fn, 1)
        prec = tp / max(tp+fp, 1)
        rows.append({"threshold": float(t), "recall": rec, "precision": prec,
                     "score": (rec+prec)/2, "n_pos": int(pred.sum())})
    df = pd.DataFrame(rows)
    best = df.loc[df["score"].idxmax()]
    if label:
        print(f"  [{label}]  score={best['score']:.4f}  R={best['recall']:.3f}  "
              f"P={best['precision']:.3f}  T={best['threshold']:.6f}  n_pos={best['n_pos']}")
    return float(best["score"]), float(best["threshold"]), df

score_v7, T_v7, sweep_df_v7 = sweep_threshold(oof_meta, y_train, "V7 standalone")
sweep_df_v7.to_csv(V7_DIR / "threshold_sweep_v7.csv", index=False)

# V5 blend
oof_v5_df    = pd.read_parquet(V5_DIR / "oof_v5.parquet")
test_v5_df   = pd.read_parquet(V5_DIR / "test_meta_v5.parquet")
v5_oof_col   = [c for c in oof_v5_df.columns if "meta" in c.lower()] or [oof_v5_df.columns[-1]]
v5_test_col  = [c for c in test_v5_df.columns if "meta" in c.lower()] or [test_v5_df.columns[-1]]
oof_v5_meta  = oof_v5_df[v5_oof_col[0]].values
test_v5_meta_arr = test_v5_df[v5_test_col[0]].values

print("\n  [V7+V5 blends]")
best_blend_score = score_v7
best_blend_w     = 1.0
best_blend_oof   = oof_meta.copy()
best_blend_test  = test_meta.copy()
blend_results    = {}
for w in [0.5, 0.6, 0.7, 0.8, 0.9]:
    ob = w*oof_meta + (1-w)*oof_v5_meta
    tb = w*test_meta + (1-w)*test_v5_meta_arr
    s, t, _ = sweep_threshold(ob, y_train, f"V7x{w:.1f}+V5x{1-w:.1f}")
    blend_results[str(w)] = {"score": s, "threshold": t}
    if s > best_blend_score:
        best_blend_score = s; best_blend_w = w
        best_blend_oof = ob; best_blend_test = tb

if two_stage_done:
    score_s2, T_s2, sweep_s2 = sweep_threshold(oof_stage2, y_train, "V7 two-stage")
    sweep_s2.to_csv(V7_DIR / "threshold_sweep_v7_stage2.csv", index=False)
else:
    score_s2, T_s2 = 0.0, 0.0

# Pick winner
print("\n  [Variant comparison]")
print(f"  V5 standalone:    {V5_OOF_SCORE:.4f}")
print(f"  V7 standalone:    {score_v7:.4f}")
if two_stage_done:
    print(f"  V7 two-stage:     {score_s2:.4f}")
print(f"  V7+V5 best blend: {best_blend_score:.4f}  (w={best_blend_w})")

candidates = {"v7_standalone": score_v7, "v7_blend": best_blend_score}
if two_stage_done: candidates["v7_stage2"] = score_s2
best_variant = max(candidates, key=candidates.get)
best_score   = candidates[best_variant]
print(f"\n  WINNER: {best_variant}  (score={best_score:.4f})")

if best_variant == "v7_standalone":
    final_oof, final_test, final_T = oof_meta, test_meta, T_v7
elif best_variant == "v7_blend":
    final_oof, final_test = best_blend_oof, best_blend_test
    _, final_T, _ = sweep_threshold(final_oof, y_train)
else:
    final_oof, final_test, final_T = oof_stage2, test_stage2_full, T_s2

preds_final = (final_test >= final_T).astype(int)

# Save OOF and test meta parquets
oof_out = pd.DataFrame({
    "CoilID": train_v7["CoilID"].values,
    "Y": y_train,
    "oof_lgb": oof_lgb,
    "oof_xgb": oof_xgb,
    "oof_cat": oof_cat,
    "oof_meta_v7": oof_meta,
})
if two_stage_done:
    oof_out["oof_stage2"] = oof_stage2
oof_out.to_parquet(V7_DIR / "oof_v7.parquet", index=False)

test_out = pd.DataFrame({"CoilID": test_v7["CoilID"].values, "test_meta_v7": test_meta})
test_out.to_parquet(V7_DIR / "test_meta_v7.parquet", index=False)

if two_stage_done:
    pd.DataFrame({"CoilID": test_v7["CoilID"].values, "test_meta_v7_stage2": test_stage2_full}).to_parquet(
        V7_DIR / "test_meta_v7_stage2.parquet", index=False)

# ============================================================
# Phase E: SHAP
# ============================================================
print("\n[Phase E] SHAP top-20 (LGB retrained on all train)...")

# Build full-train feature matrix with all-train rolling values
train_shap = train_v7.copy()
for w in ROLL_WINDOWS:
    col = f"v7_Y_roll{w}"
    roll_all = pd.Series(y_train).rolling(window=w, min_periods=1).mean()
    train_shap[col] = roll_all.values

ALL_FEAT_COLS = DET_COLS + ROLL_COLS
X_shap = train_shap[ALL_FEAT_COLS].values.astype(np.float64)

spc_all = float((y_train==0).sum()) / max(float((y_train==1).sum()), 1)
lgb_shap = lgb.LGBMClassifier(**{**LGB_PARAMS, "scale_pos_weight": spc_all})
lgb_shap.fit(X_shap, y_train)

explainer = shap.TreeExplainer(lgb_shap)
sv = explainer.shap_values(X_shap)
if isinstance(sv, list): sv = sv[1]

mean_abs = np.abs(sv).mean(axis=0)
shap_rank = sorted(zip(ALL_FEAT_COLS, mean_abs.tolist()), key=lambda x: x[1], reverse=True)
shap_top20 = shap_rank[:20]

print("\n  Top 20 SHAP features:")
for rank, (feat, val) in enumerate(shap_top20, 1):
    src = "V7-NEW" if feat in V7_ALL_NEW else "V5"
    print(f"    {rank:2d}. {feat:<42s} {val:.4f}  [{src}]")

chem_top10 = [f for f,_ in shap_top20[:10] if f in ["X42","X46","v7_X43_over_X41","v7_log_X42","v7_log_X46","v7_CarbonEq_proxy"]]
print(f"\n  Chemistry features in top 10: {chem_top10}")

with open(V7_DIR / "shap_top20_v7.json", "w") as f:
    json.dump([{"rank": i+1, "feature": fn, "shap": sv_} for i,(fn,sv_) in enumerate(shap_top20)], f, indent=2)

# ============================================================
# Bootstrap CI
# ============================================================
print("\n[Phase E] Bootstrap 95% CI (N=1000)...")
N_BOOT = 1000
rng = np.random.default_rng(42)
boot_scores = []
for _ in range(N_BOOT):
    idx = rng.choice(n_train, size=n_train, replace=True)
    yb = y_train[idx]; pb = final_oof[idx]
    if yb.sum() < 2: continue
    best_s = 0.0
    for t in np.unique(pb):
        pred = (pb >= t).astype(int)
        tp = int(((pred==1)&(yb==1)).sum()); fp = int(((pred==1)&(yb==0)).sum()); fn = int(((pred==0)&(yb==1)).sum())
        s = ((tp/max(tp+fn,1)) + (tp/max(tp+fp,1))) / 2
        if s > best_s: best_s = s
    boot_scores.append(best_s)

ci_lo  = float(np.percentile(boot_scores, 2.5))
ci_hi  = float(np.percentile(boot_scores, 97.5))
b_mean = float(np.mean(boot_scores))
print(f"  Bootstrap: mean={b_mean:.4f}  95% CI=[{ci_lo:.4f}, {ci_hi:.4f}]")

lb_est    = best_score + CALIB_CORRECTION
lb_est_lo = ci_lo + CALIB_CORRECTION
lb_est_hi = ci_hi + CALIB_CORRECTION
print(f"\n  Calib correction: +{CALIB_CORRECTION:.2f}  (V4 OOF 54.31 -> actual {V4_ACTUAL_LB})")
print(f"  Predicted LB: {lb_est:.2f}  [CI: {lb_est_lo:.2f}-{lb_est_hi:.2f}]")

# Stacking summary
summary = {
    "lgb_mean_auc": float(lgb_mean), "xgb_mean_auc": float(xgb_mean), "cat_mean_auc": float(cat_mean),
    "meta_oof_auc": float(meta_oof_auc), "meta_oof_auc_v5": V5_META_AUC,
    "delta_meta_auc": float(meta_oof_auc - V5_META_AUC),
    "best_oof_score_v7": float(score_v7), "best_oof_score_v5": V5_OOF_SCORE,
    "delta_oof_score": float(score_v7 - V5_OOF_SCORE),
    "blend_results": blend_results,
    "best_blend_weight": float(best_blend_w), "best_blend_score": float(best_blend_score),
    "two_stage_done": two_stage_done,
    "stage2_score": float(score_s2) if two_stage_done else None,
    "chosen_variant": best_variant, "chosen_score": float(best_score),
    "bootstrap_mean": float(b_mean), "ci_lo": float(ci_lo), "ci_hi": float(ci_hi),
    "lb_estimate": float(lb_est), "lb_ci_lo": float(lb_est_lo), "lb_ci_hi": float(lb_est_hi),
    "n_features": len(v7_features), "n_v7_new": len(V7_ALL_NEW),
    "fold_aucs": {k: [float(x) for x in v] for k,v in fold_aucs.items()},
    "chem_features_top10_shap": chem_top10,
}
with open(V7_DIR / "v7_stacking_summary.json", "w") as f:
    json.dump(summary, f, indent=2)

# ============================================================
# Phase F: Submission files
# ============================================================
print("\n[Phase F] Writing submission files...")

sub_main  = pd.DataFrame({"CoilID": test_v7["CoilID"].values, "Y": preds_final})
sub_main.to_csv(V7_DIR / "expected_submission.csv", index=False)
print(f"  expected_submission.csv: {len(sub_main)} rows, {int(preds_final.sum())} positives")

sub_sa = pd.DataFrame({"CoilID": test_v7["CoilID"].values, "Y": (test_meta >= T_v7).astype(int)})
sub_sa.to_csv(V7_DIR / "expected_submission_v7_standalone.csv", index=False)

_, T_blend, _ = sweep_threshold(best_blend_oof, y_train)
sub_bl = pd.DataFrame({"CoilID": test_v7["CoilID"].values, "Y": (best_blend_test >= T_blend).astype(int)})
sub_bl.to_csv(V7_DIR / "expected_submission_v7_blend.csv", index=False)

# Sweep row for threshold metadata
row_v7 = sweep_df_v7[np.isclose(sweep_df_v7["threshold"], T_v7, atol=1e-10)]
rec_at_T  = float(row_v7["recall"].iloc[0])  if len(row_v7) > 0 else 0.0
prec_at_T = float(row_v7["precision"].iloc[0]) if len(row_v7) > 0 else 0.0

with open(V7_DIR / "chosen_threshold_v7.json", "w") as f:
    json.dump({
        "chosen_variant": best_variant, "chosen_score": float(best_score),
        "chosen_threshold": float(final_T),
        "meta_oof_auc_v7": float(meta_oof_auc),
        "recall_at_T": rec_at_T, "precision_at_T": prec_at_T,
        "n_pos_test": int(preds_final.sum()),
        "lb_estimate": float(lb_est), "lb_ci_lo": float(lb_est_lo), "lb_ci_hi": float(lb_est_hi),
        "bootstrap_mean": float(b_mean), "calibration_correction": float(CALIB_CORRECTION),
    }, f, indent=2)

# ============================================================
# Summary printout
# ============================================================
print("\n" + "=" * 70)
print("BUILD V7 COMPLETE")
print("=" * 70)
print(f"\n  V4 actual LB:         {V4_ACTUAL_LB}")
print(f"  V5 OOF score:         {V5_OOF_SCORE:.4f}")
print(f"  V5 meta AUC:          {V5_META_AUC:.6f}")
print(f"  V7 meta OOF AUC:      {meta_oof_auc:.6f}  (delta={meta_oof_auc-V5_META_AUC:+.6f})")
print(f"  V7 standalone score:  {score_v7:.4f}  (delta vs V5={score_v7-V5_OOF_SCORE:+.4f})")
if two_stage_done:
    print(f"  V7 two-stage score:   {score_s2:.4f}")
print(f"  V7+V5 blend score:    {best_blend_score:.4f}  (w={best_blend_w})")
print(f"  CHOSEN VARIANT:       {best_variant}  (score={best_score:.4f})")
print(f"  Bootstrap 95% CI:     [{ci_lo:.4f}, {ci_hi:.4f}]")
print(f"  Predicted LB:         {lb_est:.2f}  [CI: {lb_est_lo:.2f}-{lb_est_hi:.2f}]")
print(f"  Chemistry in SHAP top-10: {chem_top10}")
print(f"\n  Files in: {V7_DIR}")

print("\n[VERDICT]")
if lb_est >= 70:
    print(f"  SUBMIT V7 -- Predicted LB={lb_est:.2f}. Chemistry cracked 70!")
elif lb_est >= 65:
    print(f"  SUBMIT V7 -- Predicted LB={lb_est:.2f}. Major gain. Chemistry confirmed working.")
elif lb_est >= 60:
    print(f"  SUBMIT V7 -- Predicted LB={lb_est:.2f}. Crossed 60. Clear improvement over V4.")
elif lb_est >= 58:
    print(f"  SUBMIT V7 (cautious) -- Predicted LB={lb_est:.2f}. Better than V4 {V4_ACTUAL_LB}. Submit.")
else:
    print(f"  HOLD -- Predicted LB={lb_est:.2f} below V4 actual {V4_ACTUAL_LB}. Keep V4 banked.")
    print(f"  Note: chemistry delta={best_score-V5_OOF_SCORE:+.4f} on OOF -- not enough signal.")

print("\nDone.")
