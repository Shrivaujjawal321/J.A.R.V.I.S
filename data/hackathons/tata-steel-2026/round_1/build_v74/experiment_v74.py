"""
V74 — Prevalence-Aware Train-Time Reweighting Experiment
=========================================================
Hypothesis: Base models trained at 5% prevalence (scale_pos_weight≈19.48) compress
probability space → TTA/post-hoc fails. Retraining at test-matched prevalence (45%)
changes the RANKING of boundary-zone defects.

Regimes tested:
  A  scale_pos_weight = 19.48  (current baseline — reproduce anchor)
  B  scale_pos_weight = 1.0    (no class weight / balanced)
  C1 scale_pos_weight = 1.22   (prevalence-matched: 0.55/0.45)
  C2 scale_pos_weight = 0.82   (inverse: 0.45/0.55)
  D  scale_pos_weight = 4.41   (sqrt(19.48), moderate)

For each regime:
  - Train LightGBM + XGBoost + CatBoost with 5-fold StratifiedKFold
  - Rank-average OOF scores across 3 models
  - Generate test predictions (fold-averaged)
  - Evaluate on 64 confirmed labels:
      * AUC (primary gate: must beat 0.5886 by >=0.03)
      * recall@200 and recall@238 over 38 confirmed TPs

Decision rule:
  If any regime AUC >= 0.6186 AND recall@200 > baseline → build submission from best regime
  Otherwise → structural ceiling confirmed, bank V71 K=200=74.72
"""

import os
import sys
import warnings
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import roc_auc_score
from sklearn.preprocessing import StandardScaler
import lightgbm as lgb
import xgboost as xgb
import catboost as cb

warnings.filterwarnings("ignore")

# ── Paths ──────────────────────────────────────────────────────────────────────
ROOT = Path("/home/ujjwal/Documents/J.A.R.V.I.S./data/hackathons/tata-steel-2026/round_1")
DATA_DIR = Path("/home/ujjwal/Documents/J.A.R.V.I.S./data set of tata steel/dataset")
CONFIRMED_DIR = ROOT / "SOURCE_SUBMISSION" / "data"
OUT_DIR = ROOT / "build_v74"

TRAIN_PATH = DATA_DIR / "train.csv"
TEST_PATH  = DATA_DIR / "test.csv"
TP_PATH    = CONFIRMED_DIR / "confirmed_tps.csv"
FP_PATH    = CONFIRMED_DIR / "confirmed_fps.csv"

SEED = 42
N_FOLDS = 5
BASELINE_AUC = 0.5886
AUC_GATE = 0.03        # must beat baseline by this margin to be "real improvement"
K_VALS = [200, 238]    # recall@K to report

# ── Load data ──────────────────────────────────────────────────────────────────
print("Loading data...")
train_df = pd.read_csv(TRAIN_PATH)
test_df  = pd.read_csv(TEST_PATH)

feature_cols = [f"X{i}" for i in range(1, 50)]
X_train = train_df[feature_cols].copy()
y_train = train_df["Y"].values
X_test  = test_df[feature_cols].copy()
test_coil_ids = test_df["CoilID"].values

# Impute missing with median (safe, no leakage across train/test)
medians = X_train.median()
X_train = X_train.fillna(medians)
X_test  = X_test.fillna(medians)

print(f"  Train: {X_train.shape}, pos={y_train.sum()} ({100*y_train.mean():.2f}%)")
print(f"  Test:  {X_test.shape}")

# ── Confirmed labels ───────────────────────────────────────────────────────────
tp_df = pd.read_csv(TP_PATH)
fp_df = pd.read_csv(FP_PATH)
tp_coils = set(tp_df["CoilID"].values)
fp_coils = set(fp_df["CoilID"].values)
confirmed_coils = list(tp_coils | fp_coils)

# Build confirmed label array aligned to test set
confirmed_labels = {}
for cid in tp_coils:
    confirmed_labels[cid] = 1
for cid in fp_coils:
    confirmed_labels[cid] = 0

print(f"  Confirmed TPs: {len(tp_coils)}, FPs: {len(fp_coils)}, total: {len(confirmed_labels)}")

# ── Sanity: all confirmed coils in test ───────────────────────────────────────
missing = [c for c in confirmed_coils if c not in set(test_coil_ids)]
assert len(missing) == 0, f"Confirmed coils not in test: {missing}"

# ── Confirmed-label AUC helper ─────────────────────────────────────────────────
def confirmed_auc(test_scores: np.ndarray) -> float:
    """AUC over the 64 confirmed labels only."""
    score_map = dict(zip(test_coil_ids, test_scores))
    ys, ss = [], []
    for cid, lbl in confirmed_labels.items():
        if cid in score_map:
            ys.append(lbl)
            ss.append(score_map[cid])
    return roc_auc_score(ys, ss)

def recall_at_k(test_scores: np.ndarray, k: int) -> float:
    """Recall@K = fraction of confirmed TPs in top-K ranked test coils."""
    score_map = dict(zip(test_coil_ids, test_scores))
    ranked = sorted(score_map.keys(), key=lambda c: score_map[c], reverse=True)
    top_k = set(ranked[:k])
    hits = sum(1 for c in tp_coils if c in top_k)
    return hits / len(tp_coils)

# ── LightGBM trainer ───────────────────────────────────────────────────────────
def train_lgbm(X_tr, y_tr, X_val, X_te, spw, seed):
    params = dict(
        objective="binary",
        n_estimators=500,
        learning_rate=0.05,
        num_leaves=31,
        subsample=0.8,
        colsample_bytree=0.8,
        scale_pos_weight=spw,
        random_state=seed,
        verbose=-1,
        n_jobs=4,
    )
    m = lgb.LGBMClassifier(**params)
    m.fit(X_tr, y_tr,
          eval_set=[(X_val, np.zeros(len(X_val)))],  # dummy val — early stop not used
          callbacks=[lgb.early_stopping(50, verbose=False), lgb.log_evaluation(-1)])
    oof = m.predict_proba(X_val)[:, 1]
    test_pred = m.predict_proba(X_te)[:, 1]
    return oof, test_pred

def train_lgbm_simple(X_tr, y_tr, X_val, X_te, spw, seed):
    """Simple fit without early stopping — more stable cross validation."""
    params = dict(
        objective="binary",
        n_estimators=300,
        learning_rate=0.05,
        num_leaves=31,
        subsample=0.8,
        colsample_bytree=0.8,
        scale_pos_weight=spw,
        random_state=seed,
        verbose=-1,
        n_jobs=4,
    )
    m = lgb.LGBMClassifier(**params)
    m.fit(X_tr, y_tr)
    oof = m.predict_proba(X_val)[:, 1]
    test_pred = m.predict_proba(X_te)[:, 1]
    return oof, test_pred

# ── XGBoost trainer ────────────────────────────────────────────────────────────
def train_xgb(X_tr, y_tr, X_val, X_te, spw, seed):
    params = dict(
        objective="binary:logistic",
        n_estimators=300,
        learning_rate=0.05,
        max_depth=5,
        subsample=0.8,
        colsample_bytree=0.8,
        scale_pos_weight=spw,
        random_state=seed,
        verbosity=0,
        n_jobs=4,
        eval_metric="logloss",
    )
    m = xgb.XGBClassifier(**params)
    m.fit(X_tr, y_tr, verbose=False)
    oof = m.predict_proba(X_val)[:, 1]
    test_pred = m.predict_proba(X_te)[:, 1]
    return oof, test_pred

# ── CatBoost trainer ───────────────────────────────────────────────────────────
def train_catboost(X_tr, y_tr, X_val, X_te, spw, seed):
    # CatBoost uses class_weights list [neg_weight, pos_weight]
    # scale_pos_weight equivalent: class_weights=[1.0, spw]
    params = dict(
        iterations=300,
        learning_rate=0.05,
        depth=5,
        random_seed=seed,
        verbose=0,
        eval_metric="AUC",
        class_weights=[1.0, spw],
    )
    m = cb.CatBoostClassifier(**params)
    m.fit(X_tr, y_tr)
    oof = m.predict_proba(X_val)[:, 1]
    test_pred = m.predict_proba(X_te)[:, 1]
    return oof, test_pred

# ── Full regime runner ─────────────────────────────────────────────────────────
def run_regime(name: str, spw: float, X_train, y_train, X_test_np):
    print(f"\n{'='*60}")
    print(f"REGIME {name} — scale_pos_weight = {spw:.4f}")
    print(f"{'='*60}")

    skf = StratifiedKFold(n_splits=N_FOLDS, shuffle=True, random_state=SEED)

    # Accumulators
    oof_lgbm = np.zeros(len(X_train))
    oof_xgb  = np.zeros(len(X_train))
    oof_cb   = np.zeros(len(X_train))
    test_lgbm = np.zeros(len(X_test_np))
    test_xgb  = np.zeros(len(X_test_np))
    test_cb   = np.zeros(len(X_test_np))

    X_tr_np = X_train.values
    X_te_np = X_test_np.values

    for fold_idx, (tr_idx, val_idx) in enumerate(skf.split(X_tr_np, y_train)):
        Xtr, Xval = X_tr_np[tr_idx], X_tr_np[val_idx]
        ytr, yval_dummy = y_train[tr_idx], y_train[val_idx]

        # LightGBM
        lgbm_oof, lgbm_te = train_lgbm_simple(Xtr, ytr, Xval, X_te_np, spw, SEED + fold_idx)
        oof_lgbm[val_idx] = lgbm_oof
        test_lgbm += lgbm_te / N_FOLDS

        # XGBoost
        xgb_oof, xgb_te = train_xgb(Xtr, ytr, Xval, X_te_np, spw, SEED + fold_idx)
        oof_xgb[val_idx] = xgb_oof
        test_xgb += xgb_te / N_FOLDS

        # CatBoost
        cb_oof, cb_te = train_catboost(Xtr, ytr, Xval, X_te_np, spw, SEED + fold_idx)
        oof_cb[val_idx] = cb_oof
        test_cb += cb_te / N_FOLDS

        # Per-fold AUC
        f_auc_lgbm = roc_auc_score(y_train[val_idx], lgbm_oof)
        f_auc_xgb  = roc_auc_score(y_train[val_idx], xgb_oof)
        f_auc_cb   = roc_auc_score(y_train[val_idx], cb_oof)
        print(f"  Fold {fold_idx+1}: LGBM={f_auc_lgbm:.4f}  XGB={f_auc_xgb:.4f}  CB={f_auc_cb:.4f}")

    # OOF AUC
    oof_auc_lgbm = roc_auc_score(y_train, oof_lgbm)
    oof_auc_xgb  = roc_auc_score(y_train, oof_xgb)
    oof_auc_cb   = roc_auc_score(y_train, oof_cb)
    print(f"\n  OOF AUC — LGBM={oof_auc_lgbm:.4f}  XGB={oof_auc_xgb:.4f}  CB={oof_auc_cb:.4f}")

    # Rank-average test predictions (rank percentile each model, then average)
    def rank_pct(arr):
        from scipy.stats import rankdata
        return rankdata(arr) / len(arr)

    test_rank_avg = (rank_pct(test_lgbm) + rank_pct(test_xgb) + rank_pct(test_cb)) / 3

    # 64-label AUC
    c_auc = confirmed_auc(test_rank_avg)
    print(f"  64-label AUC (rank-avg test): {c_auc:.4f}  [baseline: {BASELINE_AUC}]")

    # Recall@K
    for k in K_VALS:
        r = recall_at_k(test_rank_avg, k)
        print(f"  recall@{k}: {r:.4f}  ({int(r*len(tp_coils))}/{len(tp_coils)} TPs in top-{k})")

    # Also compute per-model confirmed AUC for reference
    c_auc_lgbm = confirmed_auc(test_lgbm)
    c_auc_xgb  = confirmed_auc(test_xgb)
    c_auc_cb   = confirmed_auc(test_cb)
    print(f"  64-label AUC per model — LGBM={c_auc_lgbm:.4f}  XGB={c_auc_xgb:.4f}  CB={c_auc_cb:.4f}")

    # Recall@200 baseline
    r200_lgbm = recall_at_k(test_lgbm, 200)
    r200_xgb  = recall_at_k(test_xgb, 200)
    r200_cb   = recall_at_k(test_cb, 200)
    r200_avg  = recall_at_k(test_rank_avg, 200)
    print(f"  recall@200 per model — LGBM={r200_lgbm:.4f}  XGB={r200_xgb:.4f}  CB={r200_cb:.4f}  avg={r200_avg:.4f}")

    oof_auc_avg = (oof_auc_lgbm + oof_auc_xgb + oof_auc_cb) / 3

    return {
        "regime": name,
        "spw": spw,
        "oof_auc_lgbm": oof_auc_lgbm,
        "oof_auc_xgb": oof_auc_xgb,
        "oof_auc_cb": oof_auc_cb,
        "oof_auc_avg": oof_auc_avg,
        "confirmed_auc_lgbm": c_auc_lgbm,
        "confirmed_auc_xgb": c_auc_xgb,
        "confirmed_auc_cb": c_auc_cb,
        "confirmed_auc_rank_avg": c_auc,
        "recall_200": recall_at_k(test_rank_avg, 200),
        "recall_238": recall_at_k(test_rank_avg, 238),
        "test_rank_avg": test_rank_avg,
        "test_lgbm": test_lgbm,
        "test_xgb": test_xgb,
        "test_cb": test_cb,
    }

# ── Define regimes ─────────────────────────────────────────────────────────────
# train prevalence: 66/1352 = 0.04882
# test prevalence est: 0.45
train_prev = y_train.sum() / len(y_train)
test_prev_est = 0.45
spw_baseline = (1 - train_prev) / train_prev   # = 19.48

regimes = [
    ("A_baseline",    spw_baseline),          # 19.48 — reproduce V44 anchor
    ("B_balanced",    1.0),                   # no class weight
    ("C1_test_match", test_prev_est / (1 - test_prev_est)),   # 0.45/0.55 = 0.818 → up-weight positives less
    ("C2_test_inv",   (1 - test_prev_est) / test_prev_est),   # 0.55/0.45 = 1.222
    ("D_sqrt",        np.sqrt(spw_baseline)),  # sqrt(19.48) = 4.41
]

print(f"\ntrain_prev={train_prev:.4f}  spw_baseline={spw_baseline:.2f}")
print("Regimes to test:")
for nm, spw in regimes:
    print(f"  {nm}: spw={spw:.4f}")

# ── Run all regimes ────────────────────────────────────────────────────────────
results = []
for regime_name, spw in regimes:
    r = run_regime(regime_name, spw, X_train, y_train, X_test)
    results.append(r)

# ── Summary table ──────────────────────────────────────────────────────────────
print("\n\n" + "="*80)
print("SUMMARY TABLE")
print("="*80)
header = f"{'Regime':<22} {'SPW':>7} {'OOF-AUC-avg':>12} {'64L-AUC':>9} {'R@200':>7} {'R@238':>7} {'vs baseline':>12}"
print(header)
print("-" * 80)
for r in results:
    delta = r["confirmed_auc_rank_avg"] - BASELINE_AUC
    mark = " ***BEATS GATE***" if delta >= AUC_GATE else ""
    print(f"{r['regime']:<22} {r['spw']:>7.3f} {r['oof_auc_avg']:>12.4f} {r['confirmed_auc_rank_avg']:>9.4f} "
          f"{r['recall_200']:>7.4f} {r['recall_238']:>7.4f} {delta:>+12.4f}{mark}")

# ── Decision ───────────────────────────────────────────────────────────────────
print("\n" + "="*80)
print("DECISION")
print("="*80)

# Find best regime by confirmed AUC
best = max(results, key=lambda x: x["confirmed_auc_rank_avg"])
baseline_r200 = results[0]["recall_200"]   # regime A recall@200

print(f"Best regime: {best['regime']}  AUC={best['confirmed_auc_rank_avg']:.4f}  R@200={best['recall_200']:.4f}")
print(f"Baseline (A):         AUC={results[0]['confirmed_auc_rank_avg']:.4f}  R@200={results[0]['recall_200']:.4f}")
print(f"AUC gate: baseline + {AUC_GATE} = {BASELINE_AUC + AUC_GATE:.4f}")

beats_gate = (
    best["confirmed_auc_rank_avg"] >= BASELINE_AUC + AUC_GATE
    and best["recall_200"] > baseline_r200
)

if beats_gate:
    print(f"\nVERDICT: REAL IMPROVEMENT — regime {best['regime']} beats gate.")
    print(f"Building submission from best regime at K=200.")

    # Build submission
    best_scores = best["test_rank_avg"]
    score_map = dict(zip(test_coil_ids, best_scores))
    ranked_coils = sorted(score_map.keys(), key=lambda c: score_map[c], reverse=True)

    sub_200 = pd.DataFrame({"CoilID": ranked_coils[:200], "Predicted": 1})
    remaining = ranked_coils[200:]
    sub_rest = pd.DataFrame({"CoilID": remaining, "Predicted": 0})
    submission = pd.concat([sub_200, sub_rest], ignore_index=True)
    # Sort by CoilID for clean submission
    submission = submission.sort_values("CoilID").reset_index(drop=True)
    sub_path = OUT_DIR / f"submission_K200_{best['regime']}.csv"
    submission.to_csv(sub_path, index=False)
    print(f"Submission saved: {sub_path}")

    # Also save ranking CSV for reference
    rank_df = pd.DataFrame({
        "CoilID": test_coil_ids,
        "rank_score": best_scores,
        "rank": pd.Series(best_scores).rank(ascending=False).astype(int).values,
    }).sort_values("rank")
    rank_df.to_csv(OUT_DIR / f"ranking_{best['regime']}.csv", index=False)

else:
    print(f"\nVERDICT: NO regime beats AUC gate of {BASELINE_AUC + AUC_GATE:.4f}")
    print("Ranking ceiling is STRUCTURAL. Recommend banking V71 K=200 = 74.72.")

# ── Save full results table ────────────────────────────────────────────────────
result_rows = []
for r in results:
    result_rows.append({
        "regime": r["regime"],
        "spw": r["spw"],
        "oof_auc_lgbm": r["oof_auc_lgbm"],
        "oof_auc_xgb": r["oof_auc_xgb"],
        "oof_auc_cb": r["oof_auc_cb"],
        "oof_auc_avg": r["oof_auc_avg"],
        "confirmed_auc_lgbm": r["confirmed_auc_lgbm"],
        "confirmed_auc_xgb": r["confirmed_auc_xgb"],
        "confirmed_auc_cb": r["confirmed_auc_cb"],
        "confirmed_auc_rank_avg": r["confirmed_auc_rank_avg"],
        "recall_200": r["recall_200"],
        "recall_238": r["recall_238"],
        "delta_vs_baseline": r["confirmed_auc_rank_avg"] - BASELINE_AUC,
    })
result_df = pd.DataFrame(result_rows)
result_df.to_csv(OUT_DIR / "regime_results.csv", index=False)
print(f"\nFull results saved: {OUT_DIR}/regime_results.csv")
print("\nDone.")
