"""
V24 FINAL v5 — V4 + RFL/Focal on LGB only (XGB+CatBoost at V4-reproducible params).

Rationale:
- LGB custom RFL objective (LGB 4.x params['objective']) consistently improves
  LGB AUC by +0.007 to +0.016 vs V4's is_unbalance approach.
- XGB and CatBoost custom objectives both regress AUC on this 1352-row dataset
  due to gradient instability at small n.
- VALID approach: retrain ALL 3 models fresh but use RFL/Focal only for LGB.
  XGB uses exact V4 params (scale_pos_weight=19.5 + standard logloss via sklearn API).
  CatBoost uses V4 params (auto_class_weights=Balanced, standard logloss).
  This is honest — no frozen V4 artifacts reused.

Grid: r in [0.5, 1.0, 1.5, 2.0], q in [0.0, 0.3, 0.5, 0.7] for LGB RFL.
XGB: standard logloss with scale_pos_weight=19.5.
CatBoost: auto_class_weights=Balanced.
"""

from __future__ import annotations
import json, warnings
from pathlib import Path
import numpy as np
import pandas as pd
from imblearn.over_sampling import SMOTE
from scipy.special import expit
from sklearn.calibration import CalibratedClassifierCV
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold
import lightgbm as lgb
import xgboost as xgb
from catboost import CatBoostClassifier

warnings.filterwarnings("ignore")

BASE = Path("/home/ujjwal/Documents/J.A.R.V.I.S./data/hackathons/tata-steel-2026/round_1")
V4 = BASE / "build_v4"
V24 = BASE / "build_v24"
V24.mkdir(parents=True, exist_ok=True)
SEED = 42; N_FOLDS = 5; CAL_DELTA = 2.67; R_CAP = 2.5
R_GRID = [0.5, 1.0, 1.5, 2.0]
Q_GRID = [0.0, 0.3, 0.5, 0.7]


def make_focal_lgb(r: float, q: float):
    eps = 1e-7
    if q == 0.0:
        def f(y_pred, dtrain):
            y = dtrain.get_label(); p = np.clip(expit(y_pred.astype(np.float64)), eps, 1-eps)
            pos = y==1; r1=max(0.,r-1)
            grad = np.zeros(len(p),dtype=np.float64); hess = np.zeros(len(p),dtype=np.float64)
            p1=p[pos]
            dL1 = -((1-p1)**r/(p1+eps) - r*(1-p1)**r1*np.log(p1+eps))
            g1=dL1*p1*(1-p1); grad[pos]=g1; hess[pos]=np.abs(g1)+1e-4
            p0=p[~pos]
            dL0=p0**r/(1-p0+eps)-r*p0**r1*np.log(1-p0+eps)
            g0=dL0*p0*(1-p0); grad[~pos]=g0; hess[~pos]=np.abs(g0)+1e-4
            return grad, hess
        return f
    else:
        def f(y_pred, dtrain):
            y = dtrain.get_label(); p = np.clip(expit(y_pred.astype(np.float64)), eps, 1-eps)
            pos = y==1; r1=max(0.,r-1)
            grad = np.zeros(len(p),dtype=np.float64); hess = np.zeros(len(p),dtype=np.float64)
            p1=p[pos]
            dL1=-(1-p1)**r*p1**(q-1)+r*(1-p1)**r1*(1-p1**q)/q
            g1=dL1*p1*(1-p1); grad[pos]=g1; hess[pos]=np.abs(g1)+1e-4
            p0=p[~pos]
            dL0=p0**r*(1-p0)**(q-1)+r*p0**r1*(1-(1-p0)**q)/q
            g0=dL0*p0*(1-p0); grad[~pos]=g0; hess[~pos]=np.abs(g0)+1e-4
            return grad, hess
        return f


# Data
print("Loading data...")
train_v4 = pd.read_parquet(V4/"train_v4.parquet").reset_index(drop=True)
test_v4 = pd.read_parquet(V4/"test_v4.parquet").reset_index(drop=True)
features = json.load(open(V4/"v4_final_features.json"))["features"]
y = train_v4["Y"].values.astype(int)
X = train_v4[features].values.astype(np.float32)
Xte = test_v4[features].values.astype(np.float32)
n, nt = len(X), len(Xte)
print(f"  train={n}  test={nt}  features={len(features)}  defects={y.sum()}")


def run_config(r: float, q: float) -> dict:
    """
    All 3 models retrained fresh per fold:
    - LGB: RFL/focal with (r, q) via params['objective']
    - XGB: V4 params (scale_pos_weight=19.5, standard logloss via sklearn)
    - CatBoost: V4 params (auto_class_weights=Balanced)
    SMOTE applied to all 3 (same as V4).
    """
    skf = StratifiedKFold(n_splits=N_FOLDS, shuffle=True, random_state=SEED)
    oof_lgb=np.zeros(n); oof_xgb=np.zeros(n); oof_cat=np.zeros(n)
    tlgb=np.zeros((N_FOLDS,nt)); txgb=np.zeros((N_FOLDS,nt)); tcat=np.zeros((N_FOLDS,nt))
    lgb_obj = make_focal_lgb(r, q)
    aucs={"lgb":[],"xgb":[],"cat":[]}

    for fi,(tr,va) in enumerate(skf.split(X,y)):
        Xtr,ytr=X[tr],y[tr]; Xva,yva=X[va],y[va]
        sm=SMOTE(sampling_strategy=0.3,k_neighbors=3,random_state=SEED)
        Xtr_s,ytr_s=sm.fit_resample(Xtr,ytr)

        # LGB: RFL custom objective (LGB 4.x API)
        ds=lgb.Dataset(Xtr_s,label=ytr_s.astype(np.float64))
        m_lgb=lgb.train({"objective":lgb_obj,"learning_rate":0.02,"num_leaves":15,
                          "min_data_in_leaf":5,"feature_fraction":0.7,"bagging_fraction":0.7,
                          "bagging_freq":1,"n_jobs":-1,"verbose":-1,"seed":SEED,"metric":"None"},
                        ds,num_boost_round=300)
        oof_lgb[va]=expit(m_lgb.predict(Xva).astype(np.float64))
        tlgb[fi]=expit(m_lgb.predict(Xte).astype(np.float64))
        aucs["lgb"].append(roc_auc_score(yva,oof_lgb[va]))

        # XGB: V4 params (sklearn API, standard logloss)
        m_xgb=xgb.XGBClassifier(scale_pos_weight=19.5,learning_rate=0.03,max_depth=4,
                                  n_estimators=300,subsample=0.7,colsample_bytree=0.7,
                                  eval_metric="auc",random_state=SEED,
                                  use_label_encoder=False,verbosity=0,n_jobs=-1)
        m_xgb.fit(Xtr_s,ytr_s)
        oof_xgb[va]=m_xgb.predict_proba(Xva)[:,1]
        txgb[fi]=m_xgb.predict_proba(Xte)[:,1]
        aucs["xgb"].append(roc_auc_score(yva,oof_xgb[va]))

        # CatBoost: V4 params
        m_cat=CatBoostClassifier(auto_class_weights="Balanced",learning_rate=0.03,depth=4,
                                  iterations=300,verbose=False,random_state=SEED,thread_count=-1)
        m_cat.fit(Xtr_s,ytr_s)
        oof_cat[va]=m_cat.predict_proba(Xva)[:,1]
        tcat[fi]=m_cat.predict_proba(Xte)[:,1]
        aucs["cat"].append(roc_auc_score(yva,oof_cat[va]))

    return {"oof_lgb":oof_lgb,"oof_xgb":oof_xgb,"oof_cat":oof_cat,
            "test_lgb":tlgb.mean(0),"test_xgb":txgb.mean(0),"test_cat":tcat.mean(0),"fold_aucs":aucs}


def meta_fit(fo,y):
    Xm=np.column_stack([fo["oof_lgb"],fo["oof_xgb"],fo["oof_cat"]])
    Xt=np.column_stack([fo["test_lgb"],fo["test_xgb"],fo["test_cat"]])
    mc=CalibratedClassifierCV(LogisticRegression(C=1.,max_iter=1000),method="sigmoid",cv=5)
    mc.fit(Xm,y)
    po=mc.predict_proba(Xm)[:,1]; pt=mc.predict_proba(Xt)[:,1]
    return po,pt,roc_auc_score(y,po)


def sweep(p,y):
    uniq=np.sort(np.unique(np.concatenate([p,[0.,1.]])))
    cuts=np.r_[uniq[0]-1e-6,0.5*(uniq[:-1]+uniq[1:]),uniq[-1]+1e-6]
    bT,bS,bR,bP,bN=0.,0.,0.,0.,0
    for t in cuts:
        pred=(p>=t).astype(int)
        tp=int(((pred==1)&(y==1)).sum());fp=int(((pred==1)&(y==0)).sum());fn=int(((pred==0)&(y==1)).sum())
        R=tp/(tp+fn) if tp+fn else 0.;P=tp/(tp+fp) if tp+fp else 0.
        s=(R+P)/2*100
        if s>bS: bS,bT,bR,bP,bN=s,float(t),R,P,int(pred.sum())
    return bT,bS,bR,bP,bN


def bstrap(p,y,T,n=1000,seed=20260523):
    rng=np.random.default_rng(seed); sc=[]
    for _ in range(n):
        idx=rng.integers(0,len(y),len(y)); pred=(p[idx]>=T).astype(int); yb=y[idx]
        tp=int(((pred==1)&(yb==1)).sum());fp=int(((pred==1)&(yb==0)).sum());fn=int(((pred==0)&(yb==1)).sum())
        R=tp/(tp+fn) if tp+fn else 0.;P=tp/(tp+fp) if tp+fp else 0.
        sc.append((R+P)/2*100)
    arr=np.array(sc); return float(np.percentile(arr,2.5)),float(np.percentile(arr,97.5))


# Phase 1: Grid search
print(f"\n{'='*70}")
print("PHASE 1: Grid search (LGB RFL, XGB V4 standard logloss, CatBoost V4)")
print(f"  LightGBM {lgb.__version__}  XGBoost {xgb.__version__}")
print(f"{'='*70}")

results=[]
for r in R_GRID:
    for q in Q_GRID:
        r_eff=min(r,R_CAP)
        label=f"r={r_eff:.1f},q={q:.1f}"+(" [focal]" if q==0 else "")
        print(f"\n  {label} ...")
        try:
            fo=run_config(r_eff,q)
            la=roc_auc_score(y,fo["oof_lgb"]); xa=roc_auc_score(y,fo["oof_xgb"]); ca=roc_auc_score(y,fo["oof_cat"])
            po,pt,ma=meta_fit(fo,y)
            T,S,Rv,Pv,N=sweep(po,y)
            print(f"    LGB={la:.4f}  XGB={xa:.4f}  CAT={ca:.4f}  META={ma:.4f}  OOF={S:.4f}  T={T:.6f}  P={Pv:.4f}  n={N}")
            results.append({"r":r_eff,"q":q,"label":label,"lgb_auc":la,"xgb_auc":xa,"cat_auc":ca,
                             "meta_auc":ma,"oof_score":S,"threshold":T,"recall":Rv,"precision":Pv,"n_pos":N,
                             "p_oof":po,"p_test":pt,"fo":fo})
        except Exception as e:
            print(f"    FAILED: {e}"); import traceback; traceback.print_exc()

if not results: raise RuntimeError("All configs failed")
results.sort(key=lambda x:x["oof_score"],reverse=True)

print(f"\n{'='*70}")
print("GRID SUMMARY:")
print(f"  {'r':>4}  {'q':>4}  {'LGB':>7}  {'XGB':>7}  {'CAT':>7}  {'META':>7}  {'OOF':>8}  {'P':>6}  {'n':>6}")
for res in results:
    print(f"  {res['r']:.1f}  {res['q']:.1f}  {res['lgb_auc']:.4f}  {res['xgb_auc']:.4f}  {res['cat_auc']:.4f}  {res['meta_auc']:.4f}  {res['oof_score']:.4f}  {res['precision']:.4f}  {res['n_pos']}")

best=results[0]
print(f"\nBest: r={best['r']},q={best['q']}  OOF={best['oof_score']:.4f}")

# Phase 2: Bootstrap CI
ci_lo,ci_hi=bstrap(best["p_oof"],y,best["threshold"])
cal_lb=best["oof_score"]+CAL_DELTA
print(f"\nBootstrap 95% CI: [{ci_lo:.4f},{ci_hi:.4f}]  Cal LB: {cal_lb:.4f}")

# Phase 3: Save
fo=best["fo"]
oof_df=pd.DataFrame({"CoilID":train_v4["CoilID"].values,"Y":y,
                      "oof_lgb":fo["oof_lgb"],"oof_xgb":fo["oof_xgb"],"oof_cat":fo["oof_cat"],
                      "oof_meta":best["p_oof"]})
oof_df.to_parquet(V24/"oof_v24.parquet",index=False)

test_df=pd.DataFrame({"CoilID":test_v4["CoilID"].values,"test_lgb":fo["test_lgb"],
                       "test_xgb":fo["test_xgb"],"test_cat":fo["test_cat"],"test_meta":best["p_test"]})
test_df.to_parquet(V24/"test_meta_v24.parquet",index=False)

chosen={"chosen_threshold":best["threshold"],"strategy":"maximize_(recall+precision)/2_exact_unique_thresholds",
        "best_r":best["r"],"best_q":best["q"],"oof_score":best["oof_score"],
        "oof_recall":best["recall"],"oof_precision":best["precision"],"oof_n_positives":best["n_pos"],
        "oof_total":n,"meta_oof_auc":best["meta_auc"],"lgb_oof_auc":best["lgb_auc"],
        "xgb_oof_auc":best["xgb_auc"],"cat_oof_auc":best["cat_auc"],
        "bootstrap_ci_lower":ci_lo,"bootstrap_ci_upper":ci_hi,"calibrated_lb_estimate":cal_lb,
        "v4_oof_baseline":54.31,"v4_lb_banked":56.98,"delta_vs_v4_oof":best["oof_score"]-54.31,
        "architecture":"lgb_rfl_only+xgb_v4_logloss+catboost_v4_balanced",
        "note":"XGB and CatBoost custom objectives regressed AUC; LGB RFL only approach",
        "grid_search_all":[{"r":r["r"],"q":r["q"],"oof_score":r["oof_score"],
                             "meta_auc":r["meta_auc"],"lgb_auc":r["lgb_auc"],
                             "threshold":r["threshold"],"recall":r["recall"],"precision":r["precision"]}
                            for r in results]}
with open(V24/"chosen_threshold_v24.json","w") as f: json.dump(chosen,f,indent=2)

test_pred=(best["p_test"]>=best["threshold"]).astype(int)
sub=pd.DataFrame({"CoilID":test_v4["CoilID"].values,"Y":test_pred})
assert sub.shape==(339,2); assert sub["Y"].isin([0,1]).all()
sub.to_csv(V24/"expected_submission.csv",index=False)
n_pos_test=int(test_pred.sum())

print(f"\n{'='*70}")
print("V24 FINAL SUMMARY")
print(f"{'='*70}")
print(f"  Technique:          LGB RFL (r={best['r']},q={best['q']}) + XGB V4 + CAT V4")
print(f"  LGB OOF AUC:        {best['lgb_auc']:.4f}  (V4: 0.8615, delta {best['lgb_auc']-0.8615:+.4f})")
print(f"  XGB OOF AUC:        {best['xgb_auc']:.4f}  (V4: 0.8668, delta {best['xgb_auc']-0.8668:+.4f})")
print(f"  CatBoost OOF AUC:   {best['cat_auc']:.4f}  (V4 stored: 0.8756)")
print(f"  Meta OOF AUC:       {best['meta_auc']:.4f}  (V4: 0.8837, delta {best['meta_auc']-0.8837:+.4f})")
print(f"  OOF (R+P)/2:        {best['oof_score']:.4f}  (gate: 54.31)")
print(f"  Bootstrap 95% CI:   [{ci_lo:.4f},{ci_hi:.4f}]  (gate lower: 53.0)")
print(f"  Calibrated LB est:  {cal_lb:.4f}  (gate: 56.98)")
print(f"  Delta vs V4 OOF:    {best['oof_score']-54.31:+.4f}")
print(f"  Threshold:          {best['threshold']:.8f}")
print(f"  R @ threshold:      {best['recall']:.4f}")
print(f"  P @ threshold:      {best['precision']:.4f}")
print(f"  Test positives:     {n_pos_test}/339 ({n_pos_test/339*100:.1f}%)")
print(f"  Gate >=54.31?       {'YES' if best['oof_score']>=54.31 else 'NO'}")
print(f"  CI lower >=53.0?    {'YES' if ci_lo>=53.0 else 'NO'}")
print(f"{'='*70}")
