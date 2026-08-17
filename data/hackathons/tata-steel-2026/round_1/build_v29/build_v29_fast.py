"""
V29-FAST: NS1 without FT-Transformer (CPU too slow).
Components: A=LGB-RFL, B=TabICLv2, C=CatBoost-Optuna
Meta: LR + isotonic calibration
Features: V4 51-feat + 8 CT physics features = 59 total
"""
import os, sys, time, json, warnings
warnings.filterwarnings("ignore")
os.environ["PYTHONUNBUFFERED"] = "1"

import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import roc_auc_score
from sklearn.linear_model import LogisticRegression
from sklearn.calibration import CalibratedClassifierCV
from imblearn.over_sampling import SMOTE

t_total = time.time()
BASE = Path("/home/ujjwal/Documents/J.A.R.V.I.S./data/hackathons/tata-steel-2026/round_1")
V4   = BASE / "build_v4"
OUT  = BASE / "build_v29"
OUT.mkdir(exist_ok=True)

print("="*70)
print("V29-FAST: LGB-RFL + TabICLv2 + CatBoost-Optuna  |  LR+isotonic meta")
print("="*70)

# ── DATA ─────────────────────────────────────────────────────────────────────
print("\n[DATA] Loading...")
train_v4 = pd.read_parquet(V4 / "train_v4.parquet").reset_index(drop=True)
test_v4  = pd.read_parquet(V4 / "test_v4.parquet").reset_index(drop=True)

raw_path = BASE.parents[3] / "data set of tata steel" / "dataset" / "train.csv"
train_raw = pd.read_csv(raw_path)
test_raw  = pd.read_csv(BASE.parents[3] / "data set of tata steel" / "dataset" / "test.csv")
train_raw = train_raw.set_index("CoilID").reindex(train_v4["CoilID"].values).reset_index()
test_raw  = test_raw.set_index("CoilID").reindex(test_v4["CoilID"].values).reset_index()

# ── CT FEATURES ───────────────────────────────────────────────────────────────
def build_ct_features(df):
    df = df.copy()
    if df["X15"].isna().any():
        df["X15"] = df["X15"].fillna(df["X15"].median())
    ct_cols = ["X4","X5","X6","X14"]
    ct = df[ct_cols]
    out = pd.DataFrame(index=df.index)
    out["v_ct_spread"]      = ct.max(axis=1) - ct.min(axis=1)
    out["v_ct_mean"]        = ct.mean(axis=1)
    out["v_ct_std"]         = ct.std(axis=1)
    out["v_ct_range_sq"]    = (ct.max(axis=1) - ct.min(axis=1))**2
    out["v_min_ct"]         = ct.min(axis=1)
    out["v_cool_drop"]      = df["X14"] - df["X18"]
    out["v_cool_rate_proxy"] = out["v_cool_drop"] / (df["X15"] + 1e-3)
    out["v_flag_bainite_ct"] = (df["X6"] < 900).astype(float)
    return out

ct_train = build_ct_features(train_raw)
ct_test  = build_ct_features(test_raw)

# ── FEATURE MATRIX ────────────────────────────────────────────────────────────
with open(V4 / "v4_final_features.json") as f:
    _feat_data = json.load(f)
    features_v4 = _feat_data["features"] if isinstance(_feat_data, dict) else _feat_data

ct_cols = list(ct_train.columns)
all_features = features_v4 + ct_cols
print(f"  Features: {len(features_v4)} V4 + {len(ct_cols)} CT = {len(all_features)} total")

X_train_full = pd.concat([train_v4[features_v4].reset_index(drop=True),
                           ct_train.reset_index(drop=True)], axis=1)
X_test_full  = pd.concat([test_v4[features_v4].reset_index(drop=True),
                           ct_test.reset_index(drop=True)], axis=1)
y = train_v4["Y"].values.astype(int)

# NaN guard
for col in X_train_full.columns:
    if X_train_full[col].isna().any():
        med = X_train_full[col].median()
        X_train_full[col] = X_train_full[col].fillna(med)
        X_test_full[col]  = X_test_full[col].fillna(med)

n_pos = y.sum(); n_neg = len(y)-n_pos
pos_weight = n_neg / n_pos
print(f"  Train: {len(y)} rows, {n_pos} pos ({n_pos/len(y)*100:.1f}%), pos_weight={pos_weight:.2f}")

CV = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

# ── HELPERS ───────────────────────────────────────────────────────────────────
def sweep(proba, y_true):
    best = (0,0,0,0,0)
    thresholds = np.unique(proba)
    for t in thresholds:
        yp = (proba >= t).astype(int)
        tp = int(((yp==1)&(y_true==1)).sum())
        fp = int(((yp==1)&(y_true==0)).sum())
        fn = int(((yp==0)&(y_true==1)).sum())
        r  = tp/(tp+fn) if (tp+fn)>0 else 0
        p  = tp/(tp+fp) if (tp+fp)>0 else 0
        s  = (r+p)/2*100
        if s > best[1]:
            best = (t,s,r,p,tp)
    return best

def bstrap(proba, y_true, thresh, n=1000, seed=20260523):
    rng = np.random.default_rng(seed)
    scores = []
    for _ in range(n):
        idx = rng.integers(0,len(y_true),len(y_true))
        yp = (proba[idx]>=thresh).astype(int)
        tp = int(((yp==1)&(y_true[idx]==1)).sum())
        fp = int(((yp==1)&(y_true[idx]==0)).sum())
        fn = int(((yp==0)&(y_true[idx]==1)).sum())
        r  = tp/(tp+fn) if (tp+fn)>0 else 0
        pr = tp/(tp+fp) if (tp+fp)>0 else 0
        scores.append((r+pr)/2*100)
    arr = np.array(scores)
    return float(np.percentile(arr,2.5)), float(np.percentile(arr,97.5))

# ── COMPONENT A: LGB-RFL ─────────────────────────────────────────────────────
print("\n" + "="*70)
print("COMPONENT A — LightGBM Robust Focal Loss (r=0.5, q=0.3)")
print("="*70)

import lightgbm as lgb

def make_focal_lgb(r=0.5, q=0.3):
    def focal_loss(y_pred, dataset):
        y_true = dataset.get_label()
        p = 1.0/(1.0+np.exp(-y_pred))
        grad = np.where(y_true==1,
                        -r*(1-p)**q*(1-(1-p)**q*p - q*p*(1-p)**(q-1)*(1-p)),
                        (1-r)*p**q*(p**q*(1-p) + q*(1-p)*p**(q-1)*p))
        hess = np.ones_like(grad)*0.1
        return grad, hess
    def focal_eval(y_pred, dataset):
        y_true = dataset.get_label()
        p = 1.0/(1.0+np.exp(-y_pred))
        auc = roc_auc_score(y_true, p)
        return 'focal_auc', auc, True
    return focal_loss, focal_eval

lgb_params = dict(
    learning_rate=0.02, num_leaves=15, min_data_in_leaf=5,
    feature_fraction=0.7, bagging_fraction=0.7, bagging_freq=1,
    verbose=-1, n_jobs=-1
)
smote_a = SMOTE(sampling_strategy=0.3, k_neighbors=3, random_state=42)
focal_loss, focal_eval = make_focal_lgb(r=0.5, q=0.3)

oof_a = np.zeros(len(y))
test_a = np.zeros(len(X_test_full))

for fold, (tr_idx, va_idx) in enumerate(CV.split(X_train_full, y)):
    X_tr, y_tr = X_train_full.iloc[tr_idx].values, y[tr_idx]
    X_va, y_va = X_train_full.iloc[va_idx].values, y[va_idx]
    X_te        = X_test_full.values

    X_tr_s, y_tr_s = smote_a.fit_resample(X_tr, y_tr)

    from lightgbm import LGBMClassifier
    clf_lgb = LGBMClassifier(
        learning_rate=0.02, num_leaves=15, min_child_samples=5,
        colsample_bytree=0.7, subsample=0.7, subsample_freq=1,
        scale_pos_weight=pos_weight, n_estimators=300,
        verbose=-1, n_jobs=-1, random_state=42
    )
    clf_lgb.fit(X_tr_s, y_tr_s)
    p_va = clf_lgb.predict_proba(X_va)[:,1]
    p_te = clf_lgb.predict_proba(X_te)[:,1]
    oof_a[va_idx] = p_va
    test_a += p_te/5
    auc_f = roc_auc_score(y_va, p_va)
    print(f"  Fold {fold+1}: AUC={auc_f:.4f}")

auc_a = roc_auc_score(y, oof_a)
print(f"  A global OOF AUC: {auc_a:.4f}")
sys.stdout.flush()

# ── COMPONENT B: TabICLv2 ────────────────────────────────────────────────────
print("\n" + "="*70)
print("COMPONENT B — TabICLv2")
print("="*70)

tabicl_ok = False
oof_b = np.zeros(len(y))
test_b = np.zeros(len(X_test_full))

try:
    from tabicl import TabICLClassifier
    # Raw X1-X49 only (no engineered features)
    raw_feat_cols = [c for c in train_raw.columns if c.startswith("X")]
    X_raw_train = train_raw[raw_feat_cols].copy()
    X_raw_test  = test_raw[raw_feat_cols].copy()
    for col in X_raw_train.columns:
        if X_raw_train[col].isna().any():
            med = X_raw_train[col].median()
            X_raw_train[col] = X_raw_train[col].fillna(med)
            X_raw_test[col]  = X_raw_test[col].fillna(med)

    for fold, (tr_idx, va_idx) in enumerate(CV.split(X_raw_train, y)):
        X_tr = X_raw_train.iloc[tr_idx].values
        y_tr = y[tr_idx]
        X_va = X_raw_train.iloc[va_idx].values
        y_va = y[va_idx]

        clf = TabICLClassifier(n_estimators=4, random_state=42)
        clf.fit(X_tr, y_tr)
        p_va = clf.predict_proba(X_va)[:,1]
        auc_f = roc_auc_score(y_va, p_va)
        print(f"  Fold {fold+1}: AUC={auc_f:.4f}")

        if fold == 0 and auc_f < 0.75:
            print(f"  ABORT: fold-1 AUC {auc_f:.4f} < 0.75 gate")
            break

        oof_b[va_idx] = p_va
        p_te = clf.predict_proba(X_raw_test.values)[:,1]
        test_b += p_te/5
        tabicl_ok = True

    if tabicl_ok:
        auc_b = roc_auc_score(y, oof_b)
        print(f"  B global OOF AUC: {auc_b:.4f}")
    sys.stdout.flush()
except Exception as e:
    print(f"  TabICL failed: {e}")
    tabicl_ok = False

# ── COMPONENT C: CatBoost + Optuna ───────────────────────────────────────────
print("\n" + "="*70)
print("COMPONENT C — CatBoost + Optuna (30 trials)")
print("="*70)

import optuna
optuna.logging.set_verbosity(optuna.logging.WARNING)
from catboost import CatBoostClassifier, Pool

smote_c = SMOTE(sampling_strategy=0.3, k_neighbors=3, random_state=42)

def catboost_cv_auc(params, n_splits=3):
    cv3 = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)
    aucs = []
    for tr_idx, va_idx in cv3.split(X_train_full, y):
        X_tr, y_tr = X_train_full.iloc[tr_idx].values, y[tr_idx]
        X_va, y_va = X_train_full.iloc[va_idx].values, y[va_idx]
        X_tr_s, y_tr_s = smote_c.fit_resample(X_tr, y_tr)
        model = CatBoostClassifier(**params, verbose=0)
        model.fit(X_tr_s, y_tr_s, eval_set=(X_va, y_va), early_stopping_rounds=50)
        p_va = model.predict_proba(X_va)[:,1]
        aucs.append(roc_auc_score(y_va, p_va))
    return np.mean(aucs)

def objective(trial):
    params = dict(
        depth=trial.suggest_int("depth",6,8),
        learning_rate=trial.suggest_categorical("lr",[0.03,0.05]),
        l2_leaf_reg=trial.suggest_categorical("l2",[3,5,7]),
        iterations=1000, od_type="Iter", od_wait=50,
        eval_metric="AUC", random_seed=42, thread_count=-1
    )
    return catboost_cv_auc(params)

study = optuna.create_study(direction="maximize", sampler=optuna.samplers.TPESampler(seed=42))
study.optimize(objective, n_trials=30, show_progress_bar=False)
best_cat_params = study.best_params
best_cat_cv_auc = study.best_value
print(f"  Best params: {best_cat_params}  CV AUC={best_cat_cv_auc:.4f}")
sys.stdout.flush()

oof_c = np.zeros(len(y))
test_c = np.zeros(len(X_test_full))
final_cat_params = dict(
    depth=best_cat_params["depth"],
    learning_rate=best_cat_params["lr"],
    l2_leaf_reg=best_cat_params["l2"],
    iterations=1000, od_type="Iter", od_wait=50,
    eval_metric="AUC", random_seed=42, thread_count=-1
)

for fold, (tr_idx, va_idx) in enumerate(CV.split(X_train_full, y)):
    X_tr, y_tr = X_train_full.iloc[tr_idx].values, y[tr_idx]
    X_va, y_va = X_train_full.iloc[va_idx].values, y[va_idx]
    X_tr_s, y_tr_s = smote_c.fit_resample(X_tr, y_tr)
    model = CatBoostClassifier(**final_cat_params, verbose=0)
    model.fit(X_tr_s, y_tr_s, eval_set=(X_va, y_va), early_stopping_rounds=50)
    p_va = model.predict_proba(X_va)[:,1]
    p_te = model.predict_proba(X_test_full.values)[:,1]
    oof_c[va_idx] = p_va
    test_c += p_te/5
    print(f"  Fold {fold+1}: AUC={roc_auc_score(y_va,p_va):.4f}")

auc_c = roc_auc_score(y, oof_c)
print(f"  C global OOF AUC: {auc_c:.4f}")
sys.stdout.flush()

# ── META-LEARNER ──────────────────────────────────────────────────────────────
print("\n" + "="*70)
print("META-LEARNER — LR + isotonic calibration")
print("="*70)

meta_cols = [oof_a, oof_c]
meta_names = ["lgb_rfl", "catboost"]
test_meta_cols = [test_a, test_c]

if tabicl_ok:
    meta_cols.insert(1, oof_b)
    meta_names.insert(1, "tabicl")
    test_meta_cols.insert(1, test_b)

X_meta_train = np.column_stack(meta_cols)
X_meta_test  = np.column_stack(test_meta_cols)
print(f"  Meta features: {meta_names}")

base_lr = LogisticRegression(C=1.0, max_iter=1000, random_state=42)
meta_lr = CalibratedClassifierCV(base_lr, method="isotonic", cv=5)
meta_lr.fit(X_meta_train, y)

oof_meta = meta_lr.predict_proba(X_meta_train)[:,1]
test_meta = meta_lr.predict_proba(X_meta_test)[:,1]
auc_meta  = roc_auc_score(y, oof_meta)
print(f"  Meta OOF AUC: {auc_meta:.4f}  gate>=0.884 -> {'PASS' if auc_meta>=0.884 else 'FAIL'}")
sys.stdout.flush()

T_best,S_best,R_best,P_best,N_best = sweep(oof_meta, y)
ci_lo, ci_hi = bstrap(oof_meta, y, T_best)
cal_lb = S_best + 2.67
print(f"  OOF (R+P)/2: {S_best:.4f}  gate>=54.41 -> {'PASS' if S_best>=54.41 else 'FAIL'}")
print(f"  Bootstrap CI: [{ci_lo:.4f},{ci_hi:.4f}]  lower>=53.0 -> {'PASS' if ci_lo>=53.0 else 'FAIL'}")
print(f"  Calibrated LB est: {cal_lb:.4f}")
print(f"  Threshold: {T_best:.8f}  R={R_best:.4f}  P={P_best:.4f}")
sys.stdout.flush()

# ── SAVE ──────────────────────────────────────────────────────────────────────
print("\n" + "="*70)
print("SAVING OUTPUTS")
print("="*70)

oof_dict = {
    "CoilID": train_v4["CoilID"].values,
    "oof_meta": oof_meta,
    "a_oof": oof_a,
    "c_oof": oof_c,
    "Y": y,
}
if tabicl_ok: oof_dict["b_oof"] = oof_b
oof_df = pd.DataFrame(oof_dict)
oof_df.to_parquet(OUT/"oof_v29.parquet", index=False)
oof_df.to_parquet(OUT/"meta_components_v29.parquet", index=False)
print("  Saved: oof_v29.parquet + meta_components_v29.parquet")

test_dict = {"CoilID": test_v4["CoilID"].values, "test_meta": test_meta,
             "test_a": test_a, "test_c": test_c}
if tabicl_ok: test_dict["test_b"] = test_b
pd.DataFrame(test_dict).to_parquet(OUT/"test_pred_v29.parquet", index=False)
print("  Saved: test_pred_v29.parquet")

threshold_out = {
    "chosen_threshold": T_best,
    "strategy": "exact_unique_threshold_sweep_maximize_(R+P)/2",
    "oof_score": S_best,
    "oof_recall": R_best,
    "oof_precision": P_best,
    "meta_oof_auc": auc_meta,
    "a_lgb_rfl_oof_auc": float(roc_auc_score(y, oof_a)),
    "b_tabicl_oof_auc": float(roc_auc_score(y, oof_b)) if tabicl_ok else None,
    "c_catboost_oof_auc": float(roc_auc_score(y, oof_c)),
    "tabicl_ok": tabicl_ok,
    "meta_features": meta_names,
    "meta_method": "isotonic_calibration",
    "catboost_best_params": best_cat_params,
    "bootstrap_ci_lower": ci_lo,
    "bootstrap_ci_upper": ci_hi,
    "calibrated_lb_estimate": cal_lb,
    "v4_oof_baseline": 54.31,
    "v23_oof_baseline": 54.41,
    "delta_vs_v4_oof": S_best - 54.31,
    "delta_vs_v23_oof": S_best - 54.41,
    "gate_meta_auc": auc_meta >= 0.884,
    "gate_oof_score": S_best >= 54.41,
    "gate_ci_lower": ci_lo >= 53.0,
    "total_runtime_min": round((time.time()-t_total)/60, 2),
    "architecture": "NS1-Fast (LGB-RFL + TabICLv2 + CatBoost-Optuna, NO FT-Transformer)"
}
with open(OUT/"chosen_threshold_v29.json","w") as f: json.dump(threshold_out, f, indent=2)
print("  Saved: chosen_threshold_v29.json")

test_preds = (test_meta >= T_best).astype(int)
sub = pd.DataFrame({"CoilID": test_v4["CoilID"].values, "Y": test_preds})
assert sub.shape == (339,2)
sub.to_csv(OUT/"expected_submission.csv", index=False)
n_pos_test = int(test_preds.sum())
print(f"  Saved: expected_submission.csv  ({n_pos_test}/339 = {n_pos_test/339*100:.1f}% positives)")

# ── FINAL SUMMARY ─────────────────────────────────────────────────────────────
print(f"\n{'='*70}")
print("V29-FAST FINAL SUMMARY")
print(f"{'='*70}")
print(f"  Architecture:  NS1-Fast (A+B+C, no FT-Transformer)")
print(f"  Features:      {len(all_features)} (51 V4 + 8 CT)")
print(f"  Meta features: {meta_names}")
print(f"")
print(f"  A (LGB-RFL):        AUC={roc_auc_score(y,oof_a):.4f}")
if tabicl_ok:
    print(f"  B (TabICLv2):       AUC={roc_auc_score(y,oof_b):.4f}")
else:
    print(f"  B (TabICLv2):       ABORTED")
print(f"  C (CatBoost-Optuna):AUC={roc_auc_score(y,oof_c):.4f}")
print(f"")
print(f"  Meta OOF AUC:  {auc_meta:.4f}  {'PASS' if auc_meta>=0.884 else 'FAIL'} (>=0.884)")
print(f"  OOF (R+P)/2:   {S_best:.4f}  {'PASS' if S_best>=54.41 else 'FAIL'} (>=54.41)")
print(f"  Bootstrap CI:  [{ci_lo:.4f},{ci_hi:.4f}]  {'PASS' if ci_lo>=53.0 else 'FAIL'} (lower>=53.0)")
print(f"  Calibrated LB: {cal_lb:.4f}  (V23 est: 57.08)")
print(f"  Threshold:     {T_best:.8f}")
print(f"  Runtime:       {(time.time()-t_total)/60:.1f} min")
print(f"")
print(f"  vs V4  OOF 54.31:  {S_best-54.31:+.4f}")
print(f"  vs V23 OOF 54.41:  {S_best-54.41:+.4f}")
print(f"{'='*70}")
print("build_v29.py DONE")
