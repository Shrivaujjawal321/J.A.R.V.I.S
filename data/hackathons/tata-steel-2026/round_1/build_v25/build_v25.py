"""
V25 — Roll-campaign ordinal features + Force-block grade z-scores.

Base: V4 (51 features) architecture from build_v26 (the faithful V4 replication):
  LGB: n_estimators=500, lr=0.05, num_leaves=31, subsample=0.8, colsample=0.8,
       reg_alpha=0.1, reg_lambda=1.0, scale_pos_weight=19.5
  XGB: n_estimators=500, lr=0.05, max_depth=4, subsample=0.8, colsample=0.8,
       min_child_weight=5, scale_pos_weight=19.5, early_stopping=50, eval_metric=logloss
  CAT: iterations=500, lr=0.05, depth=5, l2=3, scale_pos_weight=19.5
  Meta: LR + Platt (CalibratedClassifierCV, cv=5)
  SMOTE: sampling_strategy=0.3, k_neighbors=3 inside each fold

New features (on top of V4 51):
  R12_rec_1: 4 campaign-position ordinal features (CV-safe, no Y)
  R01_rec_1: 5 force-block grade z-scores (CV-SAFE, per-fold)

Preflight results:
  X29-X33 block gate: PASS (adj_corr=0.9526 > far_corr=0.7991)
"""

from __future__ import annotations
import json, warnings
from pathlib import Path

import numpy as np
import pandas as pd
from imblearn.over_sampling import SMOTE
from sklearn.calibration import CalibratedClassifierCV
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold
import lightgbm as lgb
import xgboost as xgb
from catboost import CatBoostClassifier

warnings.filterwarnings("ignore")

ROOT    = Path("/home/ujjwal/Documents/J.A.R.V.I.S.")
ROUND1  = ROOT / "data/hackathons/tata-steel-2026/round_1"
V4_DIR  = ROUND1 / "build_v4"
V25_DIR = ROUND1 / "build_v25"
V25_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR  = ROOT / "data set of tata steel/dataset"

SEED        = 42
N_FOLDS     = 5
CAL_DELTA   = 2.67
FORCE_COLS  = ["X29", "X30", "X31", "X32", "X33"]
GRADE_COL   = "X11"
MIN_GRADE_N = 8

# V4-faithful hyperparams (from build_v26 which replicates V4 exactly)
LGB_PARAMS = dict(
    n_estimators=500, learning_rate=0.05, num_leaves=31, max_depth=-1,
    min_child_samples=10, subsample=0.8, colsample_bytree=0.8,
    reg_alpha=0.1, reg_lambda=1.0, scale_pos_weight=19.5,
    random_state=SEED, n_jobs=-1, verbose=-1,
)
XGB_PARAMS = dict(
    n_estimators=500, learning_rate=0.05, max_depth=4,
    subsample=0.8, colsample_bytree=0.8, min_child_weight=5,
    scale_pos_weight=19.5, eval_metric="logloss",
    early_stopping_rounds=50, random_state=SEED, n_jobs=-1, verbosity=0,
)
CAT_PARAMS = dict(
    iterations=500, learning_rate=0.05, depth=5,
    l2_leaf_reg=3, scale_pos_weight=19.5,
    random_seed=SEED, verbose=False,
)

with open(V4_DIR / "v4_final_features.json") as f:
    V4_FEATURES = json.load(f)["features"]
print(f"V4 features: {len(V4_FEATURES)}")

# ─── 1. Raw data ──────────────────────────────────────────────────────────────
print("[1] Loading raw data...")
train_raw = pd.read_csv(DATA_DIR / "train.csv")
test_raw  = pd.read_csv(DATA_DIR / "test.csv")

# ─── 2. V4 feature parquets ───────────────────────────────────────────────────
print("[2] Loading V4 feature parquets...")
train_v4 = pd.read_parquet(V4_DIR / "train_v4.parquet").reset_index(drop=True)
test_v4  = pd.read_parquet(V4_DIR / "test_v4.parquet").reset_index(drop=True)
assert len(train_v4)==1352 and len(test_v4)==339
for c in FORCE_COLS: assert c in train_v4.columns and c in test_v4.columns
missing = [f for f in V4_FEATURES if f not in train_v4.columns]
assert len(missing)==0, f"Missing: {missing}"
print(f"  train_v4: {train_v4.shape}  test_v4: {test_v4.shape}")

# ─── 3. Force-block preflight ─────────────────────────────────────────────────
print("\n[3] Force-block correlation preflight...")
corr_mat  = train_raw[FORCE_COLS].corr().values
adj_corrs = [corr_mat[i, i+1] for i in range(4)]
adj_corr  = float(np.mean(adj_corrs))
far_corr  = float(corr_mat[0, 4])
USE_FORCE_ZSCORES = adj_corr > far_corr
print(f"  adj_corr={adj_corr:.4f}  far_corr={far_corr:.4f}  gate={'PASS' if USE_FORCE_ZSCORES else 'FAIL'}")

# ─── 4. Campaign ordinal features ─────────────────────────────────────────────
print("\n[4] Campaign ordinal features (train+test combined, no Y)...")
df_all = pd.concat([train_raw[["CoilID","X34","X36"]], test_raw[["CoilID","X34","X36"]]], ignore_index=True)
df_all = df_all.sort_values("CoilID").reset_index(drop=True)
df_all["_cb"]                   = ((df_all["X34"]==0)|(df_all["X36"]==0)).astype(int)
df_all["campaign_id"]           = df_all["_cb"].cumsum()
df_all["coils_since_last_zero"] = df_all.groupby("campaign_id").cumcount()
csz = df_all.groupby("campaign_id")["campaign_id"].transform("count")
df_all["coils_to_next_zero"]    = csz - df_all["coils_since_last_zero"] - 1
df_all["norm_campaign_pos"]     = df_all["coils_since_last_zero"] / csz.clip(lower=1)
df_all = df_all.drop(columns=["_cb"])

CAMPAIGN_COLS = ["campaign_id","coils_since_last_zero","coils_to_next_zero","norm_campaign_pos"]
n_campaigns = int(df_all["campaign_id"].nunique())
print(f"  Campaigns: {n_campaigns}  avg_len: {len(df_all)/n_campaigns:.1f}")

camp_tr = df_all[df_all["CoilID"].isin(set(train_raw["CoilID"]))].set_index("CoilID")[CAMPAIGN_COLS]
camp_te = df_all[df_all["CoilID"].isin(set(test_raw["CoilID"]))].set_index("CoilID")[CAMPAIGN_COLS]
train_v4 = train_v4.join(camp_tr, on="CoilID")
test_v4  = test_v4.join(camp_te, on="CoilID")

# ─── 5. Feature definition ────────────────────────────────────────────────────
V25_STATIC   = list(V4_FEATURES) + CAMPAIGN_COLS
FORCE_Z_COLS = [f"{c}_g11z" for c in FORCE_COLS] if USE_FORCE_ZSCORES else []
EXTRA_FOR_Z  = [c for c in FORCE_COLS + [GRADE_COL] if c not in V25_STATIC]
PULL_COLS    = V25_STATIC + EXTRA_FOR_Z
print(f"\n[5] V4={len(V4_FEATURES)}  campaign={len(CAMPAIGN_COLS)}  force_z={len(FORCE_Z_COLS)}")

# ─── 6. CV-safe grade z-score helper ─────────────────────────────────────────
def make_grade_zscores(X_tr, X_val, grade_col=GRADE_COL, cols=FORCE_COLS, min_n=MIN_GRADE_N):
    X_tr = X_tr.copy(); X_val = X_val.copy()
    g_mean_global = X_tr[cols].mean(); g_std_global = X_tr[cols].std()
    g_stats  = X_tr.groupby(grade_col)[cols].agg(["mean","std"])
    g_counts = X_tr.groupby(grade_col).size()
    def _get_z(X, col):
        def gm(g): return float(g_stats.loc[g,(col,"mean")]) if (g in g_stats.index and g_counts.loc[g]>=min_n) else float(g_mean_global[col])
        def gs(g):
            if g in g_stats.index and g_counts.loc[g]>=min_n:
                v = float(g_stats.loc[g,(col,"std")])
                return v if not np.isnan(v) else float(g_std_global[col])
            return float(g_std_global[col])
        return (X[col] - X[grade_col].map(gm)) / (X[grade_col].map(gs) + 1e-6)
    for col in cols:
        X_tr[f"{col}_g11z"] = _get_z(X_tr, col); X_val[f"{col}_g11z"] = _get_z(X_val, col)
    return X_tr, X_val

# ─── 7. Five-fold stacking ────────────────────────────────────────────────────
print("\n[6] 5-fold stacking (LGB + XGB + CatBoost) with SMOTE inside folds...")
y = train_v4["Y"].values.astype(int)
n_train = len(train_v4); n_test = len(test_v4)
oof_lgb  = np.zeros(n_train); oof_xgb = np.zeros(n_train); oof_cat = np.zeros(n_train)
test_lgb = np.zeros(n_test);  test_xgb = np.zeros(n_test); test_cat = np.zeros(n_test)
fold_aucs = {"lgb":[],"xgb":[],"cat":[]}
skf   = StratifiedKFold(n_splits=N_FOLDS, shuffle=True, random_state=SEED)
smote = SMOTE(sampling_strategy=0.3, k_neighbors=3, random_state=SEED)

for fold_i, (tr_idx, va_idx) in enumerate(skf.split(np.zeros(n_train), y)):
    print(f"\n  Fold {fold_i+1}/{N_FOLDS}...")
    X_tr_df = train_v4.iloc[tr_idx][PULL_COLS].copy()
    X_va_df = train_v4.iloc[va_idx][PULL_COLS].copy()
    X_te_df = test_v4[PULL_COLS].copy()

    if USE_FORCE_ZSCORES:
        X_tr_df, X_va_df = make_grade_zscores(X_tr_df, X_va_df)
        _, X_te_df = make_grade_zscores(X_tr_df, X_te_df)
        for zc in FORCE_Z_COLS:
            for dfz in [X_tr_df, X_va_df, X_te_df]:
                if dfz[zc].isna().any(): dfz[zc] = dfz[zc].fillna(0.0)
        MODEL_COLS = V25_STATIC + FORCE_Z_COLS
    else:
        MODEL_COLS = V25_STATIC

    X_tr = X_tr_df[MODEL_COLS].values
    X_va = X_va_df[MODEL_COLS].values
    X_te = X_te_df[MODEL_COLS].values
    y_tr = y[tr_idx]; y_va = y[va_idx]

    X_tr_sm, y_tr_sm = smote.fit_resample(X_tr, y_tr)
    print(f"    SMOTE: {len(X_tr)} -> {len(X_tr_sm)} (+{len(X_tr_sm)-len(X_tr)})")

    # LightGBM
    m_lgb = lgb.LGBMClassifier(**LGB_PARAMS)
    m_lgb.fit(X_tr_sm, y_tr_sm, eval_set=[(X_va,y_va)], callbacks=[lgb.early_stopping(50, verbose=False)])
    oof_lgb[va_idx] = m_lgb.predict_proba(X_va)[:,1]
    test_lgb += m_lgb.predict_proba(X_te)[:,1] / N_FOLDS
    auc_lgb = float(roc_auc_score(y_va, oof_lgb[va_idx]))
    fold_aucs["lgb"].append(auc_lgb)

    # XGBoost (V4-faithful params)
    m_xgb = xgb.XGBClassifier(**XGB_PARAMS)
    m_xgb.fit(X_tr_sm, y_tr_sm, eval_set=[(X_va,y_va)], verbose=False)
    oof_xgb[va_idx] = m_xgb.predict_proba(X_va)[:,1]
    test_xgb += m_xgb.predict_proba(X_te)[:,1] / N_FOLDS
    auc_xgb = float(roc_auc_score(y_va, oof_xgb[va_idx]))
    fold_aucs["xgb"].append(auc_xgb)

    # CatBoost
    m_cat = CatBoostClassifier(**CAT_PARAMS)
    m_cat.fit(X_tr_sm, y_tr_sm, eval_set=(X_va,y_va))
    oof_cat[va_idx] = m_cat.predict_proba(X_va)[:,1]
    test_cat += m_cat.predict_proba(X_te)[:,1] / N_FOLDS
    auc_cat = float(roc_auc_score(y_va, oof_cat[va_idx]))
    fold_aucs["cat"].append(auc_cat)

    print(f"    LGB={auc_lgb:.4f}  XGB={auc_xgb:.4f}  CAT={auc_cat:.4f}")

lgb_mean = float(np.mean(fold_aucs["lgb"]))
xgb_mean = float(np.mean(fold_aucs["xgb"]))
cat_mean = float(np.mean(fold_aucs["cat"]))
print(f"\nBase mean OOF AUC: LGB={lgb_mean:.4f}  XGB={xgb_mean:.4f}  CAT={cat_mean:.4f}")

# ─── 8. Meta + Platt ──────────────────────────────────────────────────────────
print("\n[7] Meta + Platt...")
X_meta_oof  = np.column_stack([oof_lgb, oof_xgb, oof_cat])
X_meta_test = np.column_stack([test_lgb, test_xgb, test_cat])
meta_cal = CalibratedClassifierCV(LogisticRegression(C=1.0, max_iter=1000), method="sigmoid", cv=5)
meta_cal.fit(X_meta_oof, y)
p_oof  = meta_cal.predict_proba(X_meta_oof)[:,1]
p_test = meta_cal.predict_proba(X_meta_test)[:,1]
meta_auc = float(roc_auc_score(y, p_oof))
print(f"  Meta OOF AUC: {meta_auc:.4f}  (V4 reference: 0.8837)")

# ─── 9. Threshold sweep ───────────────────────────────────────────────────────
print("\n[8] Threshold sweep...")
uniq = np.sort(np.unique(np.concatenate([p_oof,[0.0,1.0]])))
cuts = np.r_[uniq[0]-1e-6, 0.5*(uniq[:-1]+uniq[1:]), uniq[-1]+1e-6]
best_T, best_S, best_R, best_P, best_n = 0.0, 0.0, 0.0, 0.0, 0
for t in cuts:
    pred=(p_oof>=t).astype(int)
    tp=int(((pred==1)&(y==1)).sum()); fp=int(((pred==1)&(y==0)).sum()); fn=int(((pred==0)&(y==1)).sum())
    R=tp/(tp+fn) if (tp+fn) else 0.0; P=tp/(tp+fp) if (tp+fp) else 0.0; s=(R+P)/2.0*100.0
    if s>best_S: best_S,best_T,best_R,best_P,best_n = s,float(t),R,P,int(pred.sum())
print(f"  OOF={best_S:.4f}  T={best_T:.8f}  R={best_R:.4f}  P={best_P:.4f}  n_pos={best_n}")
print(f"  Calibrated LB est: {best_S+CAL_DELTA:.2f}")

# ─── 10. Bootstrap CI ─────────────────────────────────────────────────────────
rng = np.random.default_rng(SEED)
boot_scores = np.empty(2000)
for i in range(2000):
    idx=rng.integers(0,n_train,n_train); pb=p_oof[idx]; yb=y[idx]
    pred_b=(pb>=best_T).astype(int)
    tp_b=((pred_b==1)&(yb==1)).sum(); fp_b=((pred_b==1)&(yb==0)).sum(); fn_b=((pred_b==0)&(yb==1)).sum()
    R_b=tp_b/(tp_b+fn_b) if (tp_b+fn_b) else 0.0; P_b=tp_b/(tp_b+fp_b) if (tp_b+fp_b) else 0.0
    boot_scores[i]=(R_b+P_b)/2.0*100.0
ci_lo=float(np.percentile(boot_scores,2.5)); ci_hi=float(np.percentile(boot_scores,97.5))
print(f"  Bootstrap 95% CI: [{ci_lo:.4f}, {ci_hi:.4f}]")

# ─── 11. Save ─────────────────────────────────────────────────────────────────
test_pred=(p_test>=best_T).astype(int); n_pos_test=int(test_pred.sum())
v4_oof=pd.read_parquet(V4_DIR/"oof_v4.parquet")
v4_meta_auc=float(roc_auc_score(v4_oof["Y"].values, v4_oof["oof_meta"].values))
V4_OOF_SCORE=54.31; delta_auc=meta_auc-v4_meta_auc; delta_score=best_S-V4_OOF_SCORE
print(f"\n[9] V4 AUC {v4_meta_auc:.4f} -> {meta_auc:.4f} ({delta_auc:+.4f})")
print(f"    V4 OOF {V4_OOF_SCORE:.2f} -> {best_S:.2f} ({delta_score:+.2f})")
print(f"    Test n_pos: {n_pos_test}/{n_test}")

oof_df=pd.DataFrame({"CoilID":train_v4["CoilID"].values,"oof_lgb":oof_lgb,"oof_xgb":oof_xgb,"oof_cat":oof_cat,"oof_meta":p_oof,"Y":y})
oof_df.to_parquet(V25_DIR/"oof_v25.parquet", index=False)

chosen={
    "chosen_threshold":best_T,"strategy":"maximize_(recall+precision)/2_exact_unique_thresholds",
    "build":"V25","n_features_v4":len(V4_FEATURES),"n_features_campaign":len(CAMPAIGN_COLS),
    "n_features_force_zscores":len(FORCE_Z_COLS),
    "n_features_total":len(V4_FEATURES)+len(CAMPAIGN_COLS)+len(FORCE_Z_COLS),
    "force_block_gate":"PASS" if USE_FORCE_ZSCORES else "FAIL",
    "force_block_adj_corr":float(adj_corr),"force_block_far_corr":float(far_corr),
    "base_aucs":{"lgb":lgb_mean,"xgb":xgb_mean,"cat":cat_mean},
    "meta_oof_auc":meta_auc,"v4_meta_oof_auc":float(v4_meta_auc),
    "delta_meta_auc_vs_v4":float(delta_auc),
    "oof_score":float(best_S),"oof_recall":float(best_R),"oof_precision":float(best_P),
    "oof_n_positives":int(best_n),"oof_total":n_train,
    "bootstrap_ci_95":[float(ci_lo),float(ci_hi)],
    "calibrated_lb_estimate":float(best_S+CAL_DELTA),
    "v4_oof_score_reference":V4_OOF_SCORE,"delta_oof_score_vs_v4":float(delta_score),
    "v4_lb_banked":56.98,"n_pos_test":n_pos_test,"n_test":n_test,
    "test_positive_rate":float(n_pos_test/n_test),
    "model_params":{"lgb":str(LGB_PARAMS),"xgb":str(XGB_PARAMS),"cat":str(CAT_PARAMS)},
}
(V25_DIR/"chosen_threshold_v25.json").write_text(json.dumps(chosen,indent=2))

sub=pd.DataFrame({"CoilID":test_v4["CoilID"].values,"Y":test_pred})
assert sub.shape==(339,2); sub.to_csv(V25_DIR/"expected_submission.csv",index=False)

approach=f"""# V25 — Roll-Campaign Ordinals + Force-Block Grade Z-Scores

## Architecture
Base: V4-faithful hyperparams (from build_v26 reference):
- LGB: lr=0.05, num_leaves=31, subsample=0.8, colsample=0.8, scale_pos_weight=19.5, early_stop=50
- XGB: lr=0.05, max_depth=4, subsample=0.8, colsample=0.8, min_child_weight=5, spw=19.5, early_stop=50
- CAT: lr=0.05, depth=5, l2=3, scale_pos_weight=19.5
- Meta: LR + Platt (CalibratedClassifierCV cv=5)
- SMOTE: strategy=0.3, k_neighbors=3 inside each fold

## New Features
### R12_rec_1: Roll-Campaign Ordinal (4 features, no Y — CV-safe)
campaign_id, coils_since_last_zero, coils_to_next_zero, norm_campaign_pos

### R01_rec_1: Force-Block Grade Z-Scores ({len(FORCE_Z_COLS)} features — gate {'PASS' if USE_FORCE_ZSCORES else 'FAIL'})
adj_corr(X29-X33)={adj_corr:.4f} > far_corr={far_corr:.4f}: block CONFIRMED
z=(x-mu_grade)/(sigma_grade+1e-6), mu/sigma from training fold only. Global fallback n<{MIN_GRADE_N}.

Total: {len(V4_FEATURES)+len(CAMPAIGN_COLS)+len(FORCE_Z_COLS)} features

## Results
| Model | Mean OOF AUC |
|-------|-------------|
| LGB | {lgb_mean:.4f} |
| XGB | {xgb_mean:.4f} |
| CAT | {cat_mean:.4f} |
| Meta | {meta_auc:.4f} |

| Metric | V4 | V25 | Delta |
|--------|----|-----|-------|
| Meta OOF AUC | {v4_meta_auc:.4f} | {meta_auc:.4f} | {delta_auc:+.4f} |
| OOF (R+P)/2 | {V4_OOF_SCORE:.2f} | {best_S:.2f} | {delta_score:+.2f} |
| Bootstrap CI lower | 53.36 | {ci_lo:.2f} | - |
| Calibrated LB est | 56.98 | {best_S+CAL_DELTA:.2f} | {delta_score:+.2f} |

Threshold: {best_T:.8f} | R={best_R:.4f} | P={best_P:.4f} | Test n_pos: {n_pos_test}/{n_test}

## Verdict
{"IMPROVEMENT over V4" if best_S > V4_OOF_SCORE else "NO IMPROVEMENT over V4"} (delta {delta_score:+.2f} OOF points)
"""
(V25_DIR/"approach.md").write_text(approach)

nb_stub={"nbformat":4,"nbformat_minor":5,"metadata":{},"cells":[
    {"cell_type":"markdown","metadata":{},"source":
     f"# V25 Campaign+ForceZ\\n\\nOOF: **{best_S:.2f}** (V4: {V4_OOF_SCORE}) delta: **{delta_score:+.2f}**\\n"
     f"Meta AUC: {meta_auc:.4f}  CI: [{ci_lo:.2f},{ci_hi:.2f}]  LB est: {best_S+CAL_DELTA:.2f}"}
]}
(V25_DIR/"solution.ipynb").write_text(json.dumps(nb_stub,indent=2))

print("\n" + "="*65)
print("V25 FINAL SUMMARY (v4 — V4-faithful hyperparams)")
print("="*65)
print(f"  Force-block gate:        {'PASS' if USE_FORCE_ZSCORES else 'FAIL'} (adj={adj_corr:.4f}, far={far_corr:.4f})")
print(f"  Features (V4+camp+z):    {len(V4_FEATURES)+len(CAMPAIGN_COLS)+len(FORCE_Z_COLS)}")
print(f"  LGB mean AUC:            {lgb_mean:.4f}")
print(f"  XGB mean AUC:            {xgb_mean:.4f}")
print(f"  CAT mean AUC:            {cat_mean:.4f}")
print(f"  Meta OOF AUC:            {meta_auc:.4f}  (V4: {v4_meta_auc:.4f}, delta: {delta_auc:+.4f})")
print(f"  OOF (R+P)/2 score:       {best_S:.4f}  (V4: {V4_OOF_SCORE}, delta: {delta_score:+.2f})")
print(f"  Bootstrap 95% CI:        [{ci_lo:.2f}, {ci_hi:.2f}]")
print(f"  Calibrated LB estimate:  {best_S + CAL_DELTA:.2f}")
print(f"  Chosen threshold:        {best_T:.8f}")
print(f"  OOF recall / precision:  {best_R:.4f} / {best_P:.4f}")
print(f"  Test n_pos:              {n_pos_test} / {n_test}")
print("="*65)
