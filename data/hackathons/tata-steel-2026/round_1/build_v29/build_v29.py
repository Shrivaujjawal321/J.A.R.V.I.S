"""
V29 — NS1: New Stage-1 Architecture from Scratch
=================================================
4-component ensemble -> LR + isotonic calibration meta

Components:
  A: LGB with Robust Focal Loss (r=0.5, q=0.3)  — confirmed +0.0108 AUC vs V4-LGB
  B: TabICLv2 (n_estimators=4, CPU)              — fallback if fold-1 AUC < 0.75
  C: CatBoost + Optuna (30 trials, AUC objective)
  D: FT-Transformer 5-seed deep ensemble + EMA (decay=0.999, fixed 200 epochs)

Features: V4 51-feature set + 8 CT features = 59 features total
  (TabICL component B uses raw X1-X49 — its own internal processing)

Meta: CalibratedClassifierCV(LogisticRegression(C=1.0), method='isotonic', cv=5)

CV: StratifiedKFold(n_splits=5, shuffle=True, random_state=42) — same as V4 for alignment

References:
  - build_v24/build_v24.py  (LGB-RFL implementation)
  - build_v6/02_train_ft_xfm.py (FTTransformer architecture)
  - C2_N01_report.yaml, C2_N05_report.yaml, C2_R02_report.yaml, C2_R04_report.yaml
"""

from __future__ import annotations

import json
import time
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from imblearn.over_sampling import SMOTE
from scipy.special import expit
from sklearn.calibration import CalibratedClassifierCV
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import StandardScaler
from torch.utils.data import DataLoader, TensorDataset

warnings.filterwarnings("ignore")

# ─── Paths ─────────────────────────────────────────────────────────────────────
BASE = Path("/home/ujjwal/Documents/J.A.R.V.I.S./data/hackathons/tata-steel-2026/round_1")
V4   = BASE / "build_v4"
OUT  = BASE / "build_v29"
DATA = Path("/home/ujjwal/Documents/J.A.R.V.I.S./data set of tata steel/dataset")

OUT.mkdir(parents=True, exist_ok=True)

SEED      = 42
N_FOLDS   = 5
CAL_DELTA = 2.67

# ─── Data Loading ──────────────────────────────────────────────────────────────
print("=" * 70)
print("V29 — NS1 Architecture (LGB-RFL + TabICLv2 + CatBoost-Optuna + FT-EMA)")
print("=" * 70)

print("\n[DATA] Loading V4 parquet artifacts + raw CSV for CT features...")
train_v4 = pd.read_parquet(V4 / "train_v4.parquet").reset_index(drop=True)
test_v4  = pd.read_parquet(V4 / "test_v4.parquet").reset_index(drop=True)
features_v4 = json.load(open(V4 / "v4_final_features.json"))["features"]
neighbor_features = json.load(open(V4 / "v4_final_features.json"))["neighbor_subset"]

y  = train_v4["Y"].values.astype(int)
n  = len(y)
nt = len(test_v4)

print(f"  Train: {n} rows  Test: {nt} rows  Features V4: {len(features_v4)}  Defects: {y.sum()}")

# ─── CT Features (C2_R02_rec_1) ────────────────────────────────────────────────
print("\n[FEATURES] Building 8 CT features from raw X4, X5, X6, X14, X15, X18...")

train_raw = pd.read_csv(DATA / "train.csv")
test_raw  = pd.read_csv(DATA / "test.csv")

# Align raw to V4 order
train_raw = train_raw.set_index("CoilID").reindex(train_v4["CoilID"].values).reset_index()
test_raw  = test_raw.set_index("CoilID").reindex(test_v4["CoilID"].values).reset_index()


def build_ct_features(df):
    df = df.copy()
    # Impute X15 NaN (160 missing) with median before computing CT features
    if df["X15"].isna().any():
        df["X15"] = df["X15"].fillna(df["X15"].median())
    ct_cols = ["X4", "X5", "X6", "X14"]
    out = pd.DataFrame(index=df.index)
    ct = df[ct_cols]
    out["v_ct_spread"]       = ct.max(axis=1) - ct.min(axis=1)
    out["v_ct_mean"]         = ct.mean(axis=1)
    out["v_ct_std"]          = ct.std(axis=1, ddof=0)
    out["v_ct_range_sq"]     = (ct.max(axis=1) - ct.min(axis=1)) ** 2
    out["v_min_ct"]          = ct.min(axis=1)
    out["v_cool_drop"]       = df["X18"] - out["v_min_ct"]
    out["v_cool_rate_proxy"] = out["v_cool_drop"] / (df["X15"] + 1e-3)
    out["v_flag_bainite_ct"] = (out["v_min_ct"] < 600).astype(int)
    return out


ct_train = build_ct_features(train_raw)
ct_test  = build_ct_features(test_raw)
ct_cols  = list(ct_train.columns)
print(f"  CT features built: {ct_cols}")

# ─── Feature Matrix (59 features) ──────────────────────────────────────────────
STATIC_FEATURES = [f for f in features_v4 if f not in neighbor_features]

X_static_train = pd.concat([
    train_v4[STATIC_FEATURES].reset_index(drop=True),
    ct_train.reset_index(drop=True)
], axis=1).values.astype(np.float32)

X_static_test = pd.concat([
    test_v4[STATIC_FEATURES].reset_index(drop=True),
    ct_test.reset_index(drop=True)
], axis=1).values.astype(np.float32)

X_neighbor_train = train_v4[neighbor_features].values.astype(np.float32)
X_neighbor_test  = test_v4[neighbor_features].values.astype(np.float32)

X_full_train = np.concatenate([X_static_train, X_neighbor_train], axis=1)
X_full_test  = np.concatenate([X_static_test, X_neighbor_test], axis=1)
# Impute any remaining NaN with column median (safety net)
for j in range(X_full_train.shape[1]):
    col_nan = np.isnan(X_full_train[:, j])
    if col_nan.any():
        med = float(np.nanmedian(X_full_train[:, j]))
        X_full_train[col_nan, j] = med
        X_full_test[np.isnan(X_full_test[:, j]), j] = med
nan_train = np.isnan(X_full_train).sum(); nan_test = np.isnan(X_full_test).sum()
print(f"  Full feature matrix: train={X_full_train.shape}  test={X_full_test.shape}  NaN train={nan_train}  NaN test={nan_test}")

# Raw X1-X49 for TabICLv2
RAW_COLS = [f"X{i}" for i in range(1, 50)]
X_raw_train = train_raw[RAW_COLS].values.astype(np.float32)
X_raw_test  = test_raw[RAW_COLS].values.astype(np.float32)


# ─── Utility Functions ─────────────────────────────────────────────────────────

def make_focal_lgb(r, q):
    eps = 1e-7
    if q == 0.0:
        def f(y_pred, dtrain):
            y = dtrain.get_label(); p = np.clip(expit(y_pred.astype(np.float64)), eps, 1-eps)
            pos = y == 1; r1 = max(0., r - 1)
            grad = np.zeros(len(p), dtype=np.float64); hess = np.zeros(len(p), dtype=np.float64)
            p1 = p[pos]
            dL1 = -((1-p1)**r/(p1+eps) - r*(1-p1)**r1*np.log(p1+eps))
            g1 = dL1*p1*(1-p1); grad[pos] = g1; hess[pos] = np.abs(g1)+1e-4
            p0 = p[~pos]
            dL0 = p0**r/(1-p0+eps)-r*p0**r1*np.log(1-p0+eps)
            g0 = dL0*p0*(1-p0); grad[~pos] = g0; hess[~pos] = np.abs(g0)+1e-4
            return grad, hess
        return f
    else:
        def f(y_pred, dtrain):
            y = dtrain.get_label(); p = np.clip(expit(y_pred.astype(np.float64)), eps, 1-eps)
            pos = y == 1; r1 = max(0., r - 1)
            grad = np.zeros(len(p), dtype=np.float64); hess = np.zeros(len(p), dtype=np.float64)
            p1 = p[pos]
            dL1 = -(1-p1)**r*p1**(q-1)+r*(1-p1)**r1*(1-p1**q)/q
            g1 = dL1*p1*(1-p1); grad[pos] = g1; hess[pos] = np.abs(g1)+1e-4
            p0 = p[~pos]
            dL0 = p0**r*(1-p0)**(q-1)+r*p0**r1*(1-(1-p0)**q)/q
            g0 = dL0*p0*(1-p0); grad[~pos] = g0; hess[~pos] = np.abs(g0)+1e-4
            return grad, hess
        return f


def sweep(p, y):
    uniq = np.sort(np.unique(np.concatenate([p, [0., 1.]])))
    cuts = np.r_[uniq[0]-1e-6, 0.5*(uniq[:-1]+uniq[1:]), uniq[-1]+1e-6]
    bT, bS, bR, bP, bN = 0., 0., 0., 0., 0
    for t in cuts:
        pred = (p >= t).astype(int)
        tp = int(((pred==1)&(y==1)).sum()); fp = int(((pred==1)&(y==0)).sum())
        fn = int(((pred==0)&(y==1)).sum())
        R = tp/(tp+fn) if (tp+fn) else 0.; P = tp/(tp+fp) if (tp+fp) else 0.
        s = (R+P)/2*100
        if s > bS: bS,bT,bR,bP,bN = s,float(t),R,P,int(pred.sum())
    return bT, bS, bR, bP, bN


def bstrap(p, y, T, n=1000, seed=20260523):
    rng = np.random.default_rng(seed); sc = []
    for _ in range(n):
        idx = rng.integers(0, len(y), len(y)); pred = (p[idx]>=T).astype(int); yb = y[idx]
        tp = int(((pred==1)&(yb==1)).sum()); fp = int(((pred==1)&(yb==0)).sum())
        fn = int(((pred==0)&(yb==1)).sum())
        R = tp/(tp+fn) if (tp+fn) else 0.; P = tp/(tp+fp) if (tp+fp) else 0.
        sc.append((R+P)/2*100)
    arr = np.array(sc)
    return float(np.percentile(arr, 2.5)), float(np.percentile(arr, 97.5))


# ─── FT-Transformer ───────────────────────────────────────────────────────────

class FeatureTokenizer(nn.Module):
    def __init__(self, n_features, d_token):
        super().__init__()
        self.weight = nn.Parameter(torch.empty(n_features, d_token))
        self.bias   = nn.Parameter(torch.zeros(n_features, d_token))
        nn.init.kaiming_uniform_(self.weight, nonlinearity="linear")
    def forward(self, x):
        return x.unsqueeze(-1)*self.weight.unsqueeze(0)+self.bias.unsqueeze(0)


class TransformerBlock(nn.Module):
    def __init__(self, d_token, n_heads, d_ffn, attn_drop, ffn_drop):
        super().__init__()
        self.norm1 = nn.LayerNorm(d_token)
        self.attn  = nn.MultiheadAttention(d_token, n_heads, dropout=attn_drop, batch_first=True)
        self.norm2 = nn.LayerNorm(d_token)
        self.ffn   = nn.Sequential(nn.Linear(d_token,d_ffn),nn.GELU(),nn.Dropout(ffn_drop),
                                    nn.Linear(d_ffn,d_token),nn.Dropout(ffn_drop))
    def forward(self, x):
        x2=self.norm1(x); a,_=self.attn(x2,x2,x2); x=x+a; x=x+self.ffn(self.norm2(x)); return x


class FTTransformer(nn.Module):
    def __init__(self, n_features, d_token=96, n_blocks=3, n_heads=4,
                 d_ffn=192, attn_drop=0.2, ffn_drop=0.2):
        super().__init__()
        self.tokenizer = FeatureTokenizer(n_features, d_token)
        self.bn_input  = nn.BatchNorm1d(n_features)
        self.cls_token = nn.Parameter(torch.zeros(1,1,d_token))
        nn.init.trunc_normal_(self.cls_token, std=0.02)
        self.blocks    = nn.ModuleList([TransformerBlock(d_token,n_heads,d_ffn,attn_drop,ffn_drop)
                                        for _ in range(n_blocks)])
        self.norm_out  = nn.LayerNorm(d_token)
        self.head      = nn.Linear(d_token, 1)
    def forward(self, x):
        x=self.bn_input(x); tokens=self.tokenizer(x)
        cls=self.cls_token.expand(x.size(0),-1,-1); tokens=torch.cat([cls,tokens],dim=1)
        for block in self.blocks: tokens=block(tokens)
        return self.head(self.norm_out(tokens[:,0,:])).squeeze(-1)


def train_one_epoch(model, loader, optimizer, loss_fn, device):
    model.train(); total=0.
    for Xb,yb in loader:
        Xb,yb=Xb.to(device),yb.to(device); optimizer.zero_grad()
        loss=loss_fn(model(Xb),yb); loss.backward()
        nn.utils.clip_grad_norm_(model.parameters(),1.0); optimizer.step()
        total+=loss.item()*len(Xb)
    return total/len(loader.dataset)


@torch.no_grad()
def predict_proba_ft(model, X_np, device, batch_size=256):
    model.eval()
    dl=DataLoader(TensorDataset(torch.tensor(X_np,dtype=torch.float32)),
                  batch_size=batch_size,shuffle=False)
    return np.concatenate([torch.sigmoid(model(Xb.to(device))).cpu().numpy() for (Xb,) in dl])


# ─── Fold setup ───────────────────────────────────────────────────────────────
skf = StratifiedKFold(n_splits=N_FOLDS, shuffle=True, random_state=SEED)
folds = list(skf.split(X_full_train, y))
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"\n[DEVICE] {device}")

oof_a = np.zeros(n, dtype=np.float64)
oof_b = np.zeros(n, dtype=np.float64)
oof_c = np.zeros(n, dtype=np.float64)
oof_d = np.zeros(n, dtype=np.float64)
oof_d_var = np.zeros(n, dtype=np.float64)
test_a = np.zeros(nt, dtype=np.float64)
test_b = np.zeros(nt, dtype=np.float64)
test_c = np.zeros(nt, dtype=np.float64)
test_d = np.zeros(nt, dtype=np.float64)
tabicl_ok = False
t_total = time.time()

# ==============================================================================
# COMPONENT A — LGB-RFL
# ==============================================================================
print(f"\n{'='*70}")
print("COMPONENT A — LGB Robust Focal Loss (r=0.5, q=0.3)")
print(f"{'='*70}")

import lightgbm as lgb

lgb_obj = make_focal_lgb(r=0.5, q=0.3)
smote_a = SMOTE(sampling_strategy=0.3, k_neighbors=3, random_state=SEED)
aucs_a = []; test_a_folds = np.zeros((N_FOLDS, nt)); t_a = time.time()

for fi, (tr, va) in enumerate(folds):
    Xtr,ytr = X_full_train[tr],y[tr]; Xva,yva = X_full_train[va],y[va]
    Xtr_s,ytr_s = smote_a.fit_resample(Xtr, ytr.astype(np.float64))
    ds = lgb.Dataset(Xtr_s, label=ytr_s)
    m_lgb = lgb.train(
        {"objective":lgb_obj,"learning_rate":0.02,"num_leaves":15,
         "min_data_in_leaf":5,"feature_fraction":0.7,"bagging_fraction":0.7,
         "bagging_freq":1,"n_jobs":-1,"verbose":-1,"seed":SEED,"metric":"None"},
        ds, num_boost_round=300)
    oof_a[va] = expit(m_lgb.predict(Xva).astype(np.float64))
    test_a_folds[fi] = expit(m_lgb.predict(X_full_test).astype(np.float64))
    auc = roc_auc_score(yva, oof_a[va]); aucs_a.append(auc)
    print(f"  Fold {fi+1}: AUC={auc:.4f}")

test_a = test_a_folds.mean(0)
auc_a_global = roc_auc_score(y, oof_a)
print(f"\n  Component A OOF AUC: {auc_a_global:.4f}  time={( time.time()-t_a)/60:.1f}min")

# ==============================================================================
# COMPONENT B — TabICLv2
# ==============================================================================
print(f"\n{'='*70}")
print("COMPONENT B — TabICLv2 (n_estimators=4, CPU)")
print(f"{'='*70}")

t_b = time.time()
try:
    from tabicl import TabICLClassifier
    print("  TabICLv2 import OK")

    # Pre-download checkpoint
    try:
        _clf_dummy = TabICLClassifier(n_estimators=1, random_state=42)
        _X_dummy = X_raw_train[:20]; _y_dummy = np.zeros(20); _y_dummy[0] = 1
        _clf_dummy.fit(_X_dummy, _y_dummy)
        print("  Checkpoint ready")
    except Exception as e_pre:
        print(f"  Pre-flight warn: {e_pre}")

    test_b_folds = np.zeros((N_FOLDS, nt)); aucs_b = []

    for fi, (tr, va) in enumerate(folds):
        Xtr_b,Xva_b = X_raw_train[tr],X_raw_train[va]
        ytr_b,yva_b = y[tr],y[va]
        # NO SMOTE for TabICLv2
        clf_b = TabICLClassifier(n_estimators=4, random_state=SEED)
        clf_b.fit(Xtr_b, ytr_b)
        oof_b[va] = clf_b.predict_proba(Xva_b)[:, 1]
        test_b_folds[fi] = clf_b.predict_proba(X_raw_test)[:, 1]
        auc = roc_auc_score(yva_b, oof_b[va]); aucs_b.append(auc)
        print(f"  Fold {fi+1}: AUC={auc:.4f}  time={time.time()-t_b:.0f}s")

        if fi == 0:
            if auc < 0.75:
                print(f"  DIAGNOSTIC FAIL: fold-1 AUC={auc:.4f} < 0.75 — aborting TabICLv2")
                oof_b[:] = 0.0; tabicl_ok = False; break
            else:
                print(f"  Fold-1 PASS: AUC={auc:.4f} >= 0.75"); tabicl_ok = True

    if tabicl_ok and len(aucs_b) == N_FOLDS:
        test_b = test_b_folds.mean(0)
        auc_b_global = roc_auc_score(y, oof_b)
        print(f"\n  Component B OOF AUC: {auc_b_global:.4f}")
    elif tabicl_ok and len(aucs_b) < N_FOLDS:
        print(f"  Component B incomplete ({len(aucs_b)} folds) — dropping")
        tabicl_ok = False; oof_b[:] = 0.0

except Exception as e_b:
    print(f"  Component B FAILED: {e_b}"); tabicl_ok = False; oof_b[:] = 0.0

print(f"  TabICLv2 status: {'OK' if tabicl_ok else 'ABORTED'}  time={(time.time()-t_b)/60:.1f}min")

# ==============================================================================
# COMPONENT C — CatBoost + Optuna
# ==============================================================================
print(f"\n{'='*70}")
print("COMPONENT C — CatBoost + Optuna (30 trials, AUC objective)")
print(f"{'='*70}")

import optuna
from catboost import CatBoostClassifier

optuna.logging.set_verbosity(optuna.logging.WARNING)
t_c = time.time()
smote_c = SMOTE(sampling_strategy=0.3, k_neighbors=3, random_state=SEED)

def catboost_objective(trial):
    depth = trial.suggest_categorical("depth", [6, 7, 8])
    lr    = trial.suggest_categorical("learning_rate", [0.03, 0.05])
    l2    = trial.suggest_categorical("l2_leaf_reg", [3, 5, 7])
    fold_aucs_c = []
    for fi, (tr, va) in enumerate(folds):
        Xtr,ytr = X_full_train[tr],y[tr]; Xva,yva = X_full_train[va],y[va]
        Xtr_s,ytr_s = smote_c.fit_resample(Xtr, ytr)
        m = CatBoostClassifier(depth=depth, learning_rate=lr, l2_leaf_reg=l2,
                               iterations=1000, auto_class_weights="Balanced",
                               loss_function="Logloss", eval_metric="AUC",
                               od_type="Iter", od_wait=50,
                               random_seed=SEED, thread_count=-1, verbose=False)
        m.fit(Xtr_s, ytr_s, eval_set=(Xva, yva))
        fold_auc = roc_auc_score(yva, m.predict_proba(Xva)[:, 1])
        fold_aucs_c.append(fold_auc)
        if fi == 0 and fold_auc < 0.84:
            raise optuna.TrialPruned()
    return float(np.mean(fold_aucs_c))

print("  Running 30 Optuna trials...")
study = optuna.create_study(direction="maximize", pruner=optuna.pruners.MedianPruner(n_warmup_steps=3))
study.optimize(catboost_objective, n_trials=30, timeout=2400)
best_cat_params = study.best_params; best_cat_cv_auc = study.best_value
print(f"  Best params: {best_cat_params}  CV AUC: {best_cat_cv_auc:.4f}")

print("  Retraining final CatBoost (5-fold OOF)...")
aucs_c = []; test_c_folds = np.zeros((N_FOLDS, nt))
for fi, (tr, va) in enumerate(folds):
    Xtr,ytr = X_full_train[tr],y[tr]; Xva,yva = X_full_train[va],y[va]
    Xtr_s,ytr_s = smote_c.fit_resample(Xtr, ytr)
    m_cat = CatBoostClassifier(
        depth=best_cat_params["depth"], learning_rate=best_cat_params["learning_rate"],
        l2_leaf_reg=best_cat_params["l2_leaf_reg"],
        iterations=1000, auto_class_weights="Balanced",
        loss_function="Logloss", eval_metric="AUC",
        od_type="Iter", od_wait=50,
        random_seed=SEED, thread_count=-1, verbose=False)
    m_cat.fit(Xtr_s, ytr_s, eval_set=(Xva, yva))
    oof_c[va] = m_cat.predict_proba(Xva)[:, 1]
    test_c_folds[fi] = m_cat.predict_proba(X_full_test)[:, 1]
    auc = roc_auc_score(yva, oof_c[va]); aucs_c.append(auc)
    print(f"  Fold {fi+1}: AUC={auc:.4f}")

test_c = test_c_folds.mean(0)
auc_c_global = roc_auc_score(y, oof_c)
print(f"\n  Component C OOF AUC: {auc_c_global:.4f}  time={(time.time()-t_c)/60:.1f}min")

# ==============================================================================
# COMPONENT D — FT-Transformer 5-seed + EMA
# ==============================================================================
print(f"\n{'='*70}")
print("COMPONENT D — FT-Transformer 5-seed + EMA (decay=0.999, 200 epochs fixed)")
print(f"{'='*70}")

FT_SEEDS = [42, 43, 44, 45, 46]
D_TOKEN = 96; N_BLOCKS = 3; N_HEADS = 4; D_FFN = 192
ATTN_DROP = 0.2; FFN_DROP = 0.2; FT_LR = 1e-4; FT_WD = 1e-4
FT_EPOCHS = 200; BATCH_SIZE = 64; EMA_DECAY = 0.999
POS_WEIGHT = float((y==0).sum()/(y==1).sum())
print(f"  pos_weight={POS_WEIGHT:.2f}  device={device}  seeds={FT_SEEDS}")

scaler_ft = StandardScaler()
X_ft_train = scaler_ft.fit_transform(X_full_train).astype(np.float32)
X_ft_test  = scaler_ft.transform(X_full_test).astype(np.float32)
N_FT_FEATURES = X_ft_train.shape[1]

all_seed_oofs = []; all_seed_tests = []; t_d = time.time()

for seed_i, ft_seed in enumerate(FT_SEEDS):
    torch.manual_seed(ft_seed); np.random.seed(ft_seed)
    print(f"\n  --- FT Seed {ft_seed} ({seed_i+1}/{len(FT_SEEDS)}) ---")
    seed_oof = np.zeros(n, dtype=np.float32)
    seed_test_folds = np.zeros((N_FOLDS, nt), dtype=np.float32)

    for fi, (tr, va) in enumerate(folds):
        Xtr_ft,ytr_ft = X_ft_train[tr],y[tr]
        Xva_ft,yva_ft = X_ft_train[va],y[va]
        tr_ds = TensorDataset(torch.tensor(Xtr_ft,dtype=torch.float32),
                              torch.tensor(ytr_ft,dtype=torch.float32))
        tr_dl = DataLoader(tr_ds, batch_size=BATCH_SIZE, shuffle=True, drop_last=False)

        model = FTTransformer(n_features=N_FT_FEATURES, d_token=D_TOKEN, n_blocks=N_BLOCKS,
                              n_heads=N_HEADS, d_ffn=D_FFN, attn_drop=ATTN_DROP, ffn_drop=FFN_DROP).to(device)
        pw = torch.tensor([POS_WEIGHT], dtype=torch.float32).to(device)
        loss_fn = nn.BCEWithLogitsLoss(pos_weight=pw)
        optimizer = optim.AdamW(model.parameters(), lr=FT_LR, weight_decay=FT_WD)
        scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=FT_EPOCHS, eta_min=1e-6)

        # EMA shadow weights (C2_N05_rec_2)
        ema_weights = {k: v.cpu().float().clone() for k, v in model.state_dict().items()}

        for epoch in range(1, FT_EPOCHS + 1):
            train_one_epoch(model, tr_dl, optimizer, loss_fn, device)
            scheduler.step()
            with torch.no_grad():
                for k, v in model.state_dict().items():
                    ema_weights[k] = EMA_DECAY*ema_weights[k] + (1-EMA_DECAY)*v.cpu().float()
            if epoch % 50 == 0:
                val_p = predict_proba_ft(model, Xva_ft, device)
                print(f"    Seed {ft_seed} F{fi+1} Ep{epoch}: base_AUC={roc_auc_score(yva_ft,val_p):.4f}")

        model.load_state_dict({k: v.to(device) for k, v in ema_weights.items()})
        seed_oof[va] = predict_proba_ft(model, Xva_ft, device)
        seed_test_folds[fi] = predict_proba_ft(model, X_ft_test, device)
        fold_auc = roc_auc_score(yva_ft, seed_oof[va])
        print(f"    Seed {ft_seed} F{fi+1} EMA OOF AUC: {fold_auc:.4f}")

    seed_test = seed_test_folds.mean(0)
    seed_auc  = roc_auc_score(y, seed_oof)
    print(f"  Seed {ft_seed} global OOF AUC: {seed_auc:.4f}")
    all_seed_oofs.append(seed_oof.copy()); all_seed_tests.append(seed_test.copy())

oof_d_stack = np.stack(all_seed_oofs, axis=0)
oof_d     = oof_d_stack.mean(axis=0); oof_d_var = oof_d_stack.var(axis=0)
test_d_stack = np.stack(all_seed_tests, axis=0); test_d = test_d_stack.mean(axis=0)
auc_d_global = roc_auc_score(y, oof_d)
auc_d_seeds  = [roc_auc_score(y, s) for s in all_seed_oofs]
var_mean = float(oof_d_var.mean())
use_ft_var = var_mean >= 1e-5
print(f"\n  Component D OOF AUC (mean): {auc_d_global:.4f}  per-seed: {[f'{a:.4f}' for a in auc_d_seeds]}")
print(f"  FT var mean: {var_mean:.2e}  -> {'INCLUDE ft_var' if use_ft_var else 'DROP ft_var'}")
print(f"  Time: {(time.time()-t_d)/60:.1f}min")

# ==============================================================================
# META-LEARNER — LR + isotonic calibration
# ==============================================================================
print(f"\n{'='*70}")
print("META — LR + isotonic calibration (NOT Platt/sigmoid)")
print(f"{'='*70}")

meta_cols  = [oof_a, oof_c, oof_d]
meta_names = ["lgb_rfl", "catboost", "ft_mean"]
test_cols  = [test_a, test_c, test_d]

if tabicl_ok:
    meta_cols.insert(1, oof_b); meta_names.insert(1, "tabicl"); test_cols.insert(1, test_b)

if use_ft_var:
    meta_cols.append(oof_d_var); meta_names.append("ft_var")
    test_d_var = test_d_stack.var(axis=0); test_cols.append(test_d_var)

X_meta_train = np.column_stack(meta_cols)
X_meta_test  = np.column_stack(test_cols)
print(f"  Meta features: {meta_names}  shape={X_meta_train.shape}")

for name, oof_col in zip(meta_names, meta_cols):
    if name == "ft_var": continue
    auc = roc_auc_score(y, oof_col)
    print(f"  {name}: OOF AUC={auc:.4f}")

meta_lr = CalibratedClassifierCV(
    LogisticRegression(C=1.0, max_iter=1000, random_state=SEED),
    method="isotonic", cv=5)
meta_lr.fit(X_meta_train, y)

oof_meta  = meta_lr.predict_proba(X_meta_train)[:, 1]
test_meta = meta_lr.predict_proba(X_meta_test)[:, 1]
auc_meta  = roc_auc_score(y, oof_meta)
print(f"\n  Meta OOF AUC: {auc_meta:.4f}  (target >= 0.884)")

T_best,S_best,R_best,P_best,N_best = sweep(oof_meta, y)
ci_lo,ci_hi = bstrap(oof_meta, y, T_best)
cal_lb = S_best + CAL_DELTA

print(f"  OOF Score (R+P)/2: {S_best:.4f}")
print(f"  Threshold: {T_best:.8f}  R={R_best:.4f}  P={P_best:.4f}  N={N_best}")
print(f"  Bootstrap 95% CI:  [{ci_lo:.4f}, {ci_hi:.4f}]")
print(f"  Calibrated LB est: {cal_lb:.4f}")

# ==============================================================================
# SAVE OUTPUTS
# ==============================================================================
print(f"\n{'='*70}")
print("SAVING OUTPUTS")
print(f"{'='*70}")

oof_dict = {
    "CoilID":           train_v4["CoilID"].values,
    "fold":             -1,
    "oof_proba_meta":   oof_meta,
    "a_oof":            oof_a,
    "c_oof":            oof_c,
    "d_oof":            oof_d,
    "d_var":            oof_d_var,
    "Y":                y,
}
if tabicl_ok: oof_dict["b_oof"] = oof_b
oof_df = pd.DataFrame(oof_dict)
oof_df.to_parquet(OUT/"oof_v29.parquet", index=False)
oof_df.to_parquet(OUT/"meta_components_v29.parquet", index=False)
print(f"  Saved: oof_v29.parquet + meta_components_v29.parquet")

test_dict = {"CoilID":test_v4["CoilID"].values, "test_meta":test_meta,
             "test_a":test_a, "test_c":test_c, "test_d":test_d}
if tabicl_ok: test_dict["test_b"] = test_b
pd.DataFrame(test_dict).to_parquet(OUT/"test_pred_v29.parquet", index=False)
print(f"  Saved: test_pred_v29.parquet")

threshold_out = {
    "chosen_threshold":       T_best,
    "strategy":               "exact_unique_threshold_sweep_maximize_(R+P)/2",
    "oof_score":              S_best,
    "oof_recall":             R_best,
    "oof_precision":          P_best,
    "oof_n_positives":        N_best,
    "oof_total":              n,
    "meta_oof_auc":           auc_meta,
    "a_lgb_rfl_oof_auc":     float(roc_auc_score(y, oof_a)),
    "b_tabicl_oof_auc":      float(roc_auc_score(y, oof_b)) if tabicl_ok else None,
    "c_catboost_oof_auc":    float(roc_auc_score(y, oof_c)),
    "d_ft_mean_oof_auc":     float(roc_auc_score(y, oof_d)),
    "d_ft_seeds_auc":        auc_d_seeds,
    "d_ft_var_mean":         var_mean,
    "tabicl_ok":             tabicl_ok,
    "use_ft_var":            use_ft_var,
    "meta_features":         meta_names,
    "meta_method":           "isotonic_calibration",
    "catboost_best_params":  best_cat_params,
    "catboost_cv_auc":       best_cat_cv_auc,
    "bootstrap_ci_lower":    ci_lo,
    "bootstrap_ci_upper":    ci_hi,
    "calibrated_lb_estimate":cal_lb,
    "v4_oof_baseline":       54.31,
    "v23_oof_baseline":      54.41,
    "v26_oof_baseline":      53.83,
    "delta_vs_v4_oof":       S_best - 54.31,
    "delta_vs_v23_oof":      S_best - 54.41,
    "gate_meta_auc":         auc_meta >= 0.884,
    "gate_oof_score":        S_best >= 54.41,
    "gate_ci_lower":         ci_lo >= 53.0,
    "total_runtime_min":     round((time.time()-t_total)/60, 2),
    "architecture":          "NS1 (LGB-RFL + TabICLv2 + CatBoost-Optuna + FT-EMA-5seed)"
}
with open(OUT/"chosen_threshold_v29.json","w") as f: json.dump(threshold_out, f, indent=2)
print(f"  Saved: chosen_threshold_v29.json")

test_preds = (test_meta >= T_best).astype(int)
sub = pd.DataFrame({"CoilID":test_v4["CoilID"].values, "Y":test_preds})
assert sub.shape == (339,2); assert sub["Y"].isin([0,1]).all()
sub.to_csv(OUT/"expected_submission.csv", index=False)
n_pos_test = int(test_preds.sum())
print(f"  Saved: expected_submission.csv  ({n_pos_test}/339 = {n_pos_test/339*100:.1f}% positives)")

# ==============================================================================
# FINAL SUMMARY
# ==============================================================================
print(f"\n{'='*70}")
print("V29 FINAL SUMMARY")
print(f"{'='*70}")
print(f"  Architecture:       NS1 (4-component LR+isotonic meta)")
print(f"  Features:           {len(features_v4)} V4 + {len(ct_cols)} CT = {len(features_v4)+len(ct_cols)} total")
print(f"  Meta features:      {meta_names}")
print(f"")
print(f"  A (LGB-RFL r=0.5,q=0.3):  AUC={roc_auc_score(y,oof_a):.4f}  (V4-LGB: 0.8615)")
if tabicl_ok:
    print(f"  B (TabICLv2):             AUC={roc_auc_score(y,oof_b):.4f}")
else:
    print(f"  B (TabICLv2):             ABORTED — fold-1 gate or install fail")
print(f"  C (CatBoost-Optuna):       AUC={roc_auc_score(y,oof_c):.4f}  (V4-Cat: 0.8756 frozen)")
print(f"  D (FT-EMA 5seed mean):     AUC={roc_auc_score(y,oof_d):.4f}  (V6: 0.8425)")
print(f"  D variance used:            {'YES' if use_ft_var else 'NO'}  (mean={var_mean:.2e})")
print(f"")
print(f"  Meta OOF AUC:      {auc_meta:.4f}  gate>=0.884 -> {'PASS' if auc_meta>=0.884 else 'FAIL'}")
print(f"  OOF (R+P)/2:       {S_best:.4f}  gate>=54.41 -> {'PASS' if S_best>=54.41 else 'FAIL'}")
print(f"  Bootstrap CI:      [{ci_lo:.4f},{ci_hi:.4f}]  lower>=53.0 -> {'PASS' if ci_lo>=53.0 else 'FAIL'}")
print(f"  Calibrated LB est: {cal_lb:.4f}  (V23 est: 57.08)")
print(f"  Threshold:         {T_best:.8f}")
print(f"  Recall:            {R_best:.4f}  Precision: {P_best:.4f}")
print(f"  Test positives:    {n_pos_test}/339 ({n_pos_test/339*100:.1f}%)")
print(f"  Total runtime:     {(time.time()-t_total)/60:.1f} min")
print(f"")
print(f"  vs V4  OOF 54.31:  {S_best-54.31:+.4f}")
print(f"  vs V23 OOF 54.41:  {S_best-54.41:+.4f}")
print(f"  vs V26 OOF 53.83:  {S_best-53.83:+.4f}")
print(f"{'='*70}")
print("build_v29.py DONE")
