#!/usr/bin/env python3
"""
V61 — Physics Features (Collinearity Fixed)

ROOT CAUSE FIX vs V46/V60:
  V46 appended 29 physics features to V4's 51 features.
  BUT V4 already contains X6, X7, X9 (raw temps) and X30, X30_over_X35 (raw force).
  Physics features like ft_coupling_i = X30/(X5+273) are collinear with raw X30 in V4.
  => Trees wasted splits on both => AUC dropped by 0.02 vs V4 standalone.

V61 FIX:
  1. Start with V4's 51 SHAP-selected features
  2. DROP the 5 collinear raw cols: X6, X7, X9, X30, X30_over_X35
  3. ADD 29 static physics + 7 Sims fold-isolated = 36 new features
  4. Net: 46 clean V4 + 36 physics = 82 features, zero raw-physics collinearity
  5. 5-seed bag per model type (LGB, XGB, CAT) — same as Ratnesh iter52

Ratnesh's architecture:
  - Same LGB+XGB+CAT rank-avg (NOT meta stacking)
  - 5 seeds per model [42, 137, 1000, 7, 2024]
  - 5-fold StratifiedKFold seed=42
  - scale_pos_weight=19.48
  - NO SMOTE

Target:
  OOF AUC > 0.93 (Ratnesh iter51 = 0.9534)
  OOF F1@K=200 > 0.391

BANKED: V44 K=200 = 72.83 LB. DO NOT BREAK.
"""

from __future__ import annotations

import json
import sys
import time
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import rankdata, spearmanr
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold

import lightgbm as lgb
import xgboost as xgb
import catboost as cb

warnings.filterwarnings("ignore")

BUILD_DIR = Path(__file__).parent
sys.path.insert(0, str(BUILD_DIR))

from feature_engineering_v46 import (
    add_static_physics_features,
    compute_sims_residuals,
    attach_sims_residuals,
    ALL_STATIC_PHYSICS_COLS,
    SIMS_RESIDUAL_COLS,
)

# ─── Paths ────────────────────────────────────────────────────────────────────
ROOT   = Path("/home/ujjwal/Documents/J.A.R.V.I.S./data/hackathons/tata-steel-2026/round_1")
V4_DIR = ROOT / "build_v4"
RAW_DIR = Path("/home/ujjwal/Documents/J.A.R.V.I.S./data set of tata steel/dataset")
OUT    = ROOT / "build_v61"
OUT.mkdir(parents=True, exist_ok=True)

# ─── Config ───────────────────────────────────────────────────────────────────
SEED       = 42
N_FOLDS    = 5
SPW        = 1286 / 66   # 19.48
K_DEFAULT  = 200
K_ICR      = 154
GBDT_SEEDS = [42, 137, 1000, 7, 2024]

# Collinear raw cols to DROP from V4 (overlap with physics features)
COLLINEAR_DROP = ["X6", "X7", "X9", "X30", "X30_over_X35"]

print("=" * 75)
print("V61 — Physics Features (Collinearity Fixed: drop X6,X7,X9,X30,X30_over_X35)")
print(f"N_FOLDS={N_FOLDS} | SPW={SPW:.2f} | seeds={GBDT_SEEDS}")
print("=" * 75)

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 1: Load Data
# ═══════════════════════════════════════════════════════════════════════════════

print("\n[1/7] Loading data...")

train_v4 = pd.read_parquet(V4_DIR / "train_v4.parquet")
test_v4  = pd.read_parquet(V4_DIR / "test_v4.parquet")

with open(V4_DIR / "v4_final_features.json") as f:
    V4_FEATURES = json.load(f)["features"]  # 51 SHAP-selected

# Also load raw data for physics computation
raw_train = pd.read_csv(RAW_DIR / "train.csv")
raw_test  = pd.read_csv(RAW_DIR / "test.csv")

y      = train_v4["Y"].values.astype(float)
n_train = len(train_v4)
n_test  = len(test_v4)
coil_train = train_v4["CoilID"].values
coil_test  = test_v4["CoilID"].values

print(f"  Train: {train_v4.shape} | Test: {test_v4.shape}")
print(f"  V4 features: {len(V4_FEATURES)}")
print(f"  Positives: {int(y.sum())} / {n_train} ({y.mean()*100:.2f}%)")

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 2: V4 Base Features (drop collinear cols)
# ═══════════════════════════════════════════════════════════════════════════════

print("\n[2/7] Preparing V4 base features (collinear drop)...")

# V4 features after dropping collinear raw cols
V4_CLEAN = [f for f in V4_FEATURES if f not in COLLINEAR_DROP]
print(f"  V4 features: {len(V4_FEATURES)} original → {len(V4_CLEAN)} after dropping {COLLINEAR_DROP}")

X_train_v4 = train_v4[V4_CLEAN].fillna(0).values.astype(np.float64)
X_test_v4  = test_v4[V4_CLEAN].fillna(0).values.astype(np.float64)

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 3: Static Physics Features
# ═══════════════════════════════════════════════════════════════════════════════

print("\n[3/7] Computing static physics features...")

train_phys = add_static_physics_features(raw_train.copy())
test_phys  = add_static_physics_features(raw_test.copy())

phys_cols = [c for c in ALL_STATIC_PHYSICS_COLS if c in train_phys.columns and c in test_phys.columns]
print(f"  Static physics features: {len(phys_cols)}")
print(f"  Physics cols: {phys_cols}")

X_train_phys_static = train_phys[phys_cols].fillna(0).values.astype(np.float64)
X_test_phys_static  = test_phys[phys_cols].fillna(0).values.astype(np.float64)

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 4: Sims Force Residual (fold-isolated)
# ═══════════════════════════════════════════════════════════════════════════════

print("\n[4/7] Computing Sims force residuals (fold-isolated, Y=0 only)...")

skf = StratifiedKFold(n_splits=N_FOLDS, shuffle=True, random_state=SEED)
fold_assign = np.zeros(n_train, dtype=int)
for fold_idx, (_, val_idx) in enumerate(skf.split(np.zeros(n_train), y)):
    fold_assign[val_idx] = fold_idx

R_tr, R_te = compute_sims_residuals(
    train_df=raw_train.fillna(raw_train.median(numeric_only=True)),
    test_df=raw_test.fillna(raw_train.median(numeric_only=True)),
    y_train=y.astype(int),
    fold_assign=fold_assign,
    n_folds=N_FOLDS,
    ridge_alpha=1.0,
    verbose=True,
)

# Attach sims residual cols
train_sims, test_sims = attach_sims_residuals(raw_train.copy(), raw_test.copy(), R_tr, R_te)

sims_cols = [c for c in SIMS_RESIDUAL_COLS if c in train_sims.columns and c in test_sims.columns]
print(f"  Sims residual features: {len(sims_cols)}")

X_train_sims = train_sims[sims_cols].fillna(0).values.astype(np.float64)
X_test_sims  = test_sims[sims_cols].fillna(0).values.astype(np.float64)

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 5: Assemble Final Feature Matrix
# ═══════════════════════════════════════════════════════════════════════════════

X_train = np.hstack([X_train_v4, X_train_phys_static, X_train_sims])
X_test  = np.hstack([X_test_v4,  X_test_phys_static,  X_test_sims])

n_features = X_train.shape[1]
print(f"\n  Final feature matrix: {X_train.shape}")
print(f"  = {len(V4_CLEAN)} V4-clean + {len(phys_cols)} static physics + {len(sims_cols)} Sims = {n_features}")

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 6: Model Factories
# ═══════════════════════════════════════════════════════════════════════════════

def make_lgb(seed: int) -> lgb.LGBMClassifier:
    return lgb.LGBMClassifier(
        n_estimators=800, learning_rate=0.05, num_leaves=31,
        max_depth=6, min_child_samples=20, subsample=0.8,
        colsample_bytree=0.8, reg_alpha=0.1, reg_lambda=1.0,
        scale_pos_weight=SPW, random_state=seed, n_jobs=-1, verbose=-1,
    )

def make_xgb(seed: int) -> xgb.XGBClassifier:
    return xgb.XGBClassifier(
        n_estimators=800, learning_rate=0.05, max_depth=5,
        subsample=0.8, colsample_bytree=0.8, reg_alpha=0.1, reg_lambda=1.0,
        scale_pos_weight=SPW, random_state=seed,
        eval_metric="logloss", tree_method="hist", n_jobs=-1, verbosity=0,
    )

def make_cat(seed: int) -> cb.CatBoostClassifier:
    return cb.CatBoostClassifier(
        iterations=800, learning_rate=0.05, depth=6,
        l2_leaf_reg=3, subsample=0.8, colsample_bylevel=0.8,
        scale_pos_weight=SPW, random_seed=seed, verbose=0,
    )

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 7: 5-Fold CV with 5-Seed Bag
# ═══════════════════════════════════════════════════════════════════════════════

print("\n[5/7] Running 5-fold CV with 5-seed bag...")

model_names = []
for seed in GBDT_SEEDS:
    model_names += [f"lgb_s{seed}", f"xgb_s{seed}", f"cat_s{seed}"]

oof_store  = {mn: np.zeros(n_train) for mn in model_names}
test_store = {mn: np.zeros(n_test)  for mn in model_names}
fold_aucs  = {mn: [] for mn in model_names}
fold_summary = []
t_start = time.time()

# Regenerate folds (same as fold_assign above)
for fold_idx, (tr_idx, val_idx) in enumerate(skf.split(np.zeros(n_train), y)):
    t_fold = time.time()
    n_pos_val = int(y[val_idx].sum())
    print(f"\n  ── Fold {fold_idx+1}/{N_FOLDS} | train={len(tr_idx)}, val={len(val_idx)}, pos_val={n_pos_val} ──")

    X_tr  = X_train[tr_idx]
    X_val = X_train[val_idx]
    y_tr  = y[tr_idx]
    y_val = y[val_idx]

    fold_model_aucs = {}
    for seed in GBDT_SEEDS:
        # LightGBM
        mn = f"lgb_s{seed}"
        try:
            m = make_lgb(seed)
            m.fit(X_tr, y_tr)
            vp = m.predict_proba(X_val)[:, 1]
            tp = m.predict_proba(X_test)[:, 1]
            oof_store[mn][val_idx] = vp
            test_store[mn]        += tp / N_FOLDS
            fa = roc_auc_score(y_val, vp) if y_val.sum() > 0 else 0.5
            fold_aucs[mn].append(fa)
            fold_model_aucs[mn] = fa
        except Exception as e:
            print(f"    LGB s{seed} FAILED: {e}")
            fold_aucs[mn].append(0.5)

        # XGBoost
        mn = f"xgb_s{seed}"
        try:
            m = make_xgb(seed)
            m.fit(X_tr, y_tr)
            vp = m.predict_proba(X_val)[:, 1]
            tp = m.predict_proba(X_test)[:, 1]
            oof_store[mn][val_idx] = vp
            test_store[mn]        += tp / N_FOLDS
            fa = roc_auc_score(y_val, vp) if y_val.sum() > 0 else 0.5
            fold_aucs[mn].append(fa)
            fold_model_aucs[mn] = fa
        except Exception as e:
            print(f"    XGB s{seed} FAILED: {e}")
            fold_aucs[mn].append(0.5)

        # CatBoost
        mn = f"cat_s{seed}"
        try:
            m = make_cat(seed)
            m.fit(X_tr, y_tr)
            vp = m.predict_proba(X_val)[:, 1]
            tp = m.predict_proba(X_test)[:, 1]
            oof_store[mn][val_idx] = vp
            test_store[mn]        += tp / N_FOLDS
            fa = roc_auc_score(y_val, vp) if y_val.sum() > 0 else 0.5
            fold_aucs[mn].append(fa)
            fold_model_aucs[mn] = fa
        except Exception as e:
            print(f"    CAT s{seed} FAILED: {e}")
            fold_aucs[mn].append(0.5)

    elapsed = time.time() - t_fold
    lgb_aucs = [fold_model_aucs.get(f"lgb_s{s}", 0.5) for s in GBDT_SEEDS]
    xgb_aucs = [fold_model_aucs.get(f"xgb_s{s}", 0.5) for s in GBDT_SEEDS]
    cat_aucs = [fold_model_aucs.get(f"cat_s{s}", 0.5) for s in GBDT_SEEDS]
    print(f"    LGB: {np.mean(lgb_aucs):.4f} | XGB: {np.mean(xgb_aucs):.4f} | CAT: {np.mean(cat_aucs):.4f} | {elapsed:.0f}s")
    fold_summary.append({
        "fold": fold_idx + 1,
        "n_pos_val": n_pos_val,
        "lgb_mean": float(np.mean(lgb_aucs)),
        "xgb_mean": float(np.mean(xgb_aucs)),
        "cat_mean": float(np.mean(cat_aucs)),
        "elapsed_s": round(elapsed, 1),
    })

total_time = time.time() - t_start
print(f"\nTotal training time: {total_time/60:.1f} min")

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 8: Rank-Average Aggregation
# ═══════════════════════════════════════════════════════════════════════════════

print("\n[6/7] Rank-average aggregation...")

oof_rank_sum  = np.zeros(n_train)
test_rank_sum = np.zeros(n_test)

for mn in model_names:
    oof_rank_sum  += rankdata(oof_store[mn])
    test_rank_sum += rankdata(test_store[mn])

oof_rank_avg  = oof_rank_sum  / len(model_names)
test_rank_avg = test_rank_sum / len(model_names)
oof_norm  = oof_rank_avg  / oof_rank_avg.max()
test_norm = test_rank_avg / test_rank_avg.max()

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 9: Evaluation + Save
# ═══════════════════════════════════════════════════════════════════════════════

print("\n[7/7] Evaluating and saving...")

def f1_at_k(y_true, scores, k):
    top_k = np.argsort(scores)[::-1][:k]
    pred  = np.zeros(len(y_true), dtype=int)
    pred[top_k] = 1
    tp = int((pred * y_true).sum())
    fp = int((pred * (1 - y_true)).sum())
    fn = int(((1 - pred) * y_true).sum())
    prec = tp / (tp + fp) if (tp + fp) > 0 else 0
    rec  = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1   = 2 * prec * rec / (prec + rec) if (prec + rec) > 0 else 0
    return f1, tp, fp, fn

oof_auc = roc_auc_score(y, oof_norm)
f1_200, tp_200, _, _ = f1_at_k(y, oof_norm, K_DEFAULT)
f1_154, tp_154, _, _ = f1_at_k(y, oof_norm, K_ICR)

# K sweep
k_sweep = []
for k in [50, 75, 100, 130, 154, 170, 186, 197, 200, 210, 220, 229, 250]:
    f1_k, tp_k, _, _ = f1_at_k(y, oof_norm, k)
    k_sweep.append({"K": k, "F1@K": round(f1_k, 6), "TP": tp_k})
best_k = max(k_sweep, key=lambda x: x["F1@K"])

# Bootstrap AUC CI
np.random.seed(SEED)
boot_aucs = [
    roc_auc_score(y[idx := np.random.choice(n_train, n_train, replace=True)], oof_norm[idx])
    for _ in range(500) if y[np.random.choice(n_train, n_train, replace=True)].sum() > 0
]
auc_lo, auc_hi = np.percentile(boot_aucs, [2.5, 97.5])

# Per-model AUCs
model_aucs = {mn: roc_auc_score(y, oof_store[mn]) for mn in model_names}

# Spearman vs references
spearman_refs = {}
for ref_name, rel_path, col in [
    ("V46", "build_v46/oof_v46.parquet", "oof_proba"),
    ("V43", "build_v43/oof_v43.parquet", None),
    ("V54b", "build_v54b/oof_v54b.parquet", "oof_rank_avg"),
]:
    ref_path = ROOT / rel_path
    if ref_path.exists():
        try:
            rdf = pd.read_parquet(ref_path)
            if col is None:
                col = [c for c in rdf.columns if "oof" in c.lower() and "proba" in c.lower()]
                col = col[0] if col else rdf.columns[1]
            rho, _ = spearmanr(oof_norm, rdf[col].values[:n_train])
            spearman_refs[ref_name] = round(float(rho), 4)
        except Exception as e:
            spearman_refs[ref_name] = f"ERR:{e}"

print(f"\n  OOF AUC:       {oof_auc:.5f}  [{auc_lo:.5f}, {auc_hi:.5f}]")
print(f"  OOF F1@K=200:  {f1_200:.6f}  (TP={tp_200})")
print(f"  OOF F1@K=154:  {f1_154:.6f}  (TP={tp_154})")
print(f"  Best K:        K={best_k['K']} F1={best_k['F1@K']:.6f}")
print(f"  Spearman:      {spearman_refs}")

# ── Save OOF parquet ──────────────────────────────────────────────────────────
oof_df = pd.DataFrame({"CoilID": coil_train, "oof_rank_avg": oof_norm, "y": y})
for mn in model_names:
    oof_df[f"oof_{mn}"] = oof_store[mn]
oof_df.to_parquet(OUT / "oof_v61.parquet", index=False)

# ── Save test proba parquet ───────────────────────────────────────────────────
test_df = pd.DataFrame({"CoilID": coil_test, "rank_avg_proba": test_norm})
for mn in model_names:
    test_df[f"test_{mn}"] = test_store[mn]
test_df.to_parquet(OUT / "test_proba_v61.parquet", index=False)

# ── Submission CSVs ───────────────────────────────────────────────────────────
k_list = list({K_ICR, K_DEFAULT, 186, 197, 210, 220, best_k["K"]})
for K_sub in sorted(k_list):
    top_k_idx = np.argsort(test_norm)[::-1][:K_sub]
    pred      = np.zeros(n_test, dtype=int)
    pred[top_k_idx] = 1
    sub = pd.DataFrame({"CoilID": coil_test, "Y": pred})
    sub.to_csv(OUT / f"submission_K{K_sub}.csv", index=False)
    assert len(sub) == n_test
    assert sub["Y"].sum() == K_sub

print(f"  Saved submission CSVs: K={sorted(k_list)}")

# Integrity check
for K_sub in [K_ICR, K_DEFAULT]:
    chk = pd.read_csv(OUT / f"submission_K{K_sub}.csv")
    assert len(chk) == n_test and chk["Y"].sum() == K_sub
print(f"  Integrity checks PASSED (K154={n_test} rows, K200={n_test} rows)")

# ── CV Report ─────────────────────────────────────────────────────────────────
gate1 = "PASS" if f1_200 > 0.391 else f"FAIL ({f1_200:.6f})"
gate2 = "PASS" if oof_auc > 0.93  else f"MISS ({oof_auc:.5f} < 0.93)"
spv46 = spearman_refs.get("V46", "N/A")
gate3_ok = isinstance(spv46, float) and 0.70 <= spv46 <= 0.90
gate3 = f"PASS ({spv46})" if gate3_ok else f"{'HIGH_CORR' if isinstance(spv46,float) and spv46>0.90 else 'N/A'} ({spv46})"

fold_rows = "\n".join(
    f"| {r['fold']} | {r['lgb_mean']:.4f} | {r['xgb_mean']:.4f} | {r['cat_mean']:.4f} | {r['elapsed_s']:.0f}s |"
    for r in fold_summary
)
model_rows = "\n".join(
    f"| {mn} | {auc:.5f} |"
    for mn, auc in sorted(model_aucs.items(), key=lambda x: -x[1])
)
k_rows = "\n".join(f"| {r['K']} | {r['F1@K']:.6f} | {r['TP']} |" for r in k_sweep)
spearman_rows = "\n".join(f"| {k} | {v} |" for k, v in spearman_refs.items())

report = f"""# V61 CV Report — Physics Features (Collinearity Fixed)

**Date:** 2026-05-25
**Fix vs V46/V60:** Dropped collinear raw cols (X6,X7,X9,X30,X30_over_X35) before adding physics
**Architecture:** 5-Fold × 3-Learner × 5-Seed rank-avg | NO SMOTE | scale_pos_weight={SPW:.2f}
**Features:** {len(V4_CLEAN)} V4-clean + {len(phys_cols)} static physics + {len(sims_cols)} Sims = {n_features} total
**Banked baseline:** V44 K=200 = 72.83 LB

---

## Summary

| Metric | Value | Gate |
|---|---|---|
| OOF AUC | {oof_auc:.5f} | {gate2} |
| OOF AUC Bootstrap 95% CI | [{auc_lo:.5f}, {auc_hi:.5f}] | — |
| **OOF F1@K=200** | **{f1_200:.6f} (TP={tp_200})** | **{gate1}** |
| OOF F1@K=154 | {f1_154:.6f} (TP={tp_154}) | — |
| OOF best K | K={best_k['K']}, F1={best_k['F1@K']:.6f} (TP={best_k['TP']}) | — |
| Spearman vs V46 | {spv46} | {gate3} |
| Training time | {total_time/60:.1f} min | — |

---

## V61 Feature Set

| Group | Count | Collinear drop |
|---|---|---|
| V4 SHAP-selected (clean) | {len(V4_CLEAN)} | Dropped X6,X7,X9,X30,X30_over_X35 |
| Static physics (Zener+curvature+FT+mono+cooling) | {len(phys_cols)} | None |
| Sims force-residual (fold-isolated) | {len(sims_cols)} | None |
| **TOTAL** | **{n_features}** | |

---

## Per-Fold CV Results

| Fold | LGB_mean | XGB_mean | CAT_mean | Time |
|---|---|---|---|---|
{fold_rows}

---

## Per-Model OOF AUCs (top sorted)

| Model | OOF AUC |
|---|---|
{model_rows}

---

## K Sweep

| K | OOF F1@K | TP |
|---|---|---|
{k_rows}

---

## Spearman vs Reference OOFs

| Reference | Spearman ρ |
|---|---|
{spearman_rows}

---

## Gates

| Gate | Condition | Result |
|---|---|---|
| 1 — F1 benchmark | OOF F1@K=200 > 0.391 | {gate1} |
| 2 — AUC target | OOF AUC > 0.93 (Ratnesh iter51=0.9534) | {gate2} |
| 3 — Diversity | Spearman vs V46 in [0.70, 0.90] | {gate3} |

---

## Improvement vs Prior Builds

| Build | OOF AUC | OOF F1@K=200 | Key diff |
|---|---|---|---|
| V4 base | 0.884 | — | 51 V4 features |
| V46 physics | 0.863 | — | V4 + physics (collinear) |
| V53 Caruana | 0.883 | 0.391 | 13-paradigm greedy |
| V60 stand-decomp | 0.858 | 0.338 | Wrong base decomp |
| **V61** | **{oof_auc:.5f}** | **{f1_200:.6f}** | **V4-clean + physics (collinearity fixed)** |
"""

with open(OUT / "cv_report_v61.md", "w") as f:
    f.write(report)

print(f"\n  Saved cv_report_v61.md, oof_v61.parquet, test_proba_v61.parquet")

print("\n" + "=" * 75)
print("V61 FINAL RESULTS")
print("=" * 75)
print(f"  OOF AUC:       {oof_auc:.5f}  [{auc_lo:.5f}, {auc_hi:.5f}]")
print(f"  OOF F1@K=200:  {f1_200:.6f}  (TP={tp_200})  gate={gate1}")
print(f"  OOF F1@K=154:  {f1_154:.6f}  (TP={tp_154})")
print(f"  Best K:        K={best_k['K']} F1={best_k['F1@K']:.6f} (TP={best_k['TP']})")
print(f"  Spearman V46:  {spv46}")
print(f"  Features:      {n_features} ({len(V4_CLEAN)} V4 + {len(phys_cols)} phys + {len(sims_cols)} sims)")
print(f"  Training time: {total_time/60:.1f} min")
print("=" * 75)
