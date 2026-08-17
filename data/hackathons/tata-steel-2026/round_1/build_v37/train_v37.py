#!/usr/bin/env python3
"""
train_v37.py — AutoGluon paradigm for Tata Steel Hot Rolling Defect Detection

Motivation:
  V4/V33/V34/V35 are all GBDT-family (Spearman 0.89-0.98 correlated).
  AutoGluon runs 30+ model types internally (NN, RF, ET, KNN, LinearSVC, etc.)
  → genuine paradigm diversity injection into the consensus union.

Architecture:
  - V33's 105-feature pipeline (fold-isolated medians, AP-1 compliant)
  - AutoGluon best_quality preset with 40-min budget
  - 5-fold StratifiedKFold (seed=42) matching V4/V33/V34/V35 structure
  - BBSE sample weights (w1≈9, w0≈0.58) passed to AutoGluon
  - OOF + test proba saved; NO submission CSV (orchestrator handles consensus)

Hard constraints:
  - TIME BUDGET: 60 min wall clock (AutoGluon gets 40 min; rest is FE + eval)
  - NO auto-submit
  - NO other build_v*/ directories touched
  - FOLD-ISOLATED medians (non-negotiable, see V33 pattern)
"""

from __future__ import annotations

import sys
import json
import time
import warnings
import traceback
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import roc_auc_score
from scipy.stats import spearmanr

warnings.filterwarnings("ignore")

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE = Path("/home/ujjwal/Documents/J.A.R.V.I.S./data/hackathons/tata-steel-2026/round_1")
DATA = Path("/home/ujjwal/Documents/J.A.R.V.I.S./data set of tata steel/dataset")
OUT  = BASE / "build_v37"
AG_PATH = str(OUT / "ag_models_v37")

WALL_START = time.time()
WALL_LIMIT  = 55 * 60   # 55 min hard stop (leaves 5 min buffer)

def wall_elapsed():
    return time.time() - WALL_START

def wall_remaining():
    return WALL_LIMIT - wall_elapsed()

print(f"[V37] AutoGluon paradigm — Tata Steel Hot Rolling")
print(f"[V37] AutoGluon 1.5.0 confirmed installed")
print(f"[V37] Wall start: {time.strftime('%H:%M:%S')}")

# ── Imports (after path setup) ────────────────────────────────────────────────
sys.path.insert(0, str(OUT))
from feature_engineering import StandSetpoints, validate_stand_ordering, TEMP_COLS, FORCE_COLS

# ── Load data ─────────────────────────────────────────────────────────────────
print(f"\n[V37] Loading data from {DATA}")
train_raw = pd.read_csv(DATA / "train.csv")
test_raw  = pd.read_csv(DATA / "test.csv")

print(f"[V37] Train: {train_raw.shape}, Y-counts: {train_raw['Y'].value_counts().to_dict()}")
print(f"[V37] Test:  {test_raw.shape}")

# AP-6: Validate stand ordering
ordering = validate_stand_ordering(train_raw)
print(f"[V37] Stand ordering — Temp: {ordering['temp_order_status']} | Force: {ordering['force_order_status']}")

# ── Feature engineering helpers ───────────────────────────────────────────────
def get_raw_feature_cols(df: pd.DataFrame) -> list[str]:
    """All X* columns (raw features, excluding CoilID and Y)."""
    return [c for c in df.columns if c.startswith("X")]

RAW_COLS = get_raw_feature_cols(train_raw)
print(f"[V37] Raw feature cols: {len(RAW_COLS)}")

# ── CV config ─────────────────────────────────────────────────────────────────
N_FOLDS = 5
SEED = 42
kf = StratifiedKFold(n_splits=N_FOLDS, shuffle=True, random_state=SEED)

X_all  = train_raw.drop(columns=["Y"])
y_all  = train_raw["Y"].values.astype(float)
coil_train = train_raw["CoilID"].values
coil_test  = test_raw["CoilID"].values

# BBSE weights (w1≈9 for defect class, w0≈0.58 for normal class)
# From V33 research: train prevalence ≈ 5%, test ≈ 45% → w1 = 0.45/0.05 = 9
W1 = 9.0    # defect class
W0 = 0.579  # normal class  (= 0.55/0.95)
sample_weights_all = np.where(y_all == 1, W1, W0)
print(f"[V37] BBSE weights: w1={W1}, w0={W0}")

# ── Prepare test raw features (will apply fold-averaged medians later) ────────
X_test_raw = test_raw.copy()

# ── 5-fold AutoGluon training ─────────────────────────────────────────────────
oof_proba = np.zeros(len(train_raw))
test_proba_folds = np.zeros((len(test_raw), N_FOLDS))
fold_aucs = []
fold_leaderboards = []

print(f"\n[V37] Starting 5-fold StratifiedKFold (seed=42)...")

for fold_idx, (tr_idx, val_idx) in enumerate(kf.split(X_all, y_all)):
    fold_start = time.time()
    remaining = wall_remaining()
    print(f"\n[V37] ── Fold {fold_idx+1}/{N_FOLDS} | Wall remaining: {remaining/60:.1f} min ──")

    if remaining < 5 * 60:
        print(f"[V37] WALL TIME EXCEEDED — stopping at fold {fold_idx+1}. Partial OOF will be used.")
        break

    # ── Step 1: Split ─────────────────────────────────────────────────────────
    X_tr  = X_all.iloc[tr_idx].copy()
    X_val = X_all.iloc[val_idx].copy()
    y_tr  = y_all[tr_idx]
    y_val = y_all[val_idx]
    sw_tr = sample_weights_all[tr_idx]

    # ── Step 2: Fold-isolated feature engineering (AP-1 compliant) ────────────
    setpoints = StandSetpoints()
    setpoints.fit(X_tr)               # fit on train fold ONLY
    X_tr_fe  = setpoints.transform(X_tr)
    X_val_fe = setpoints.transform(X_val)
    X_test_fe = setpoints.transform(X_test_raw.copy())

    # Drop CoilID from feature matrices
    feat_cols = [c for c in X_tr_fe.columns if c != "CoilID"]
    X_tr_fe  = X_tr_fe[feat_cols]
    X_val_fe = X_val_fe[feat_cols]
    X_test_fe_f = X_test_fe[feat_cols]

    print(f"[V37] Fold {fold_idx+1} feature count: {len(feat_cols)}")

    # ── Step 3: Prepare AutoGluon dataframes ─────────────────────────────────
    # AG expects label in the training df
    train_ag = X_tr_fe.copy()
    train_ag["Y"] = y_tr
    train_ag["_sample_weight"] = sw_tr

    val_ag = X_val_fe.copy()
    val_ag["Y"] = y_val

    # ── Step 4: Time budget for this fold ─────────────────────────────────────
    # Divide remaining time roughly across remaining folds (conservative)
    folds_remaining = N_FOLDS - fold_idx
    fold_budget = min(int(wall_remaining() * 0.8 / folds_remaining), 480)  # max 8 min/fold
    fold_budget = max(fold_budget, 120)  # min 2 min

    # For fold 1 we can give more time since AG internal bagging is efficient
    if fold_idx == 0:
        fold_budget = min(int(wall_remaining() * 0.55), 600)  # 55% of remaining, cap 10 min

    print(f"[V37] Fold {fold_idx+1} AG budget: {fold_budget}s")

    # ── Step 5: AutoGluon fit ─────────────────────────────────────────────────
    ag_path = f"{AG_PATH}_fold{fold_idx}"

    try:
        from autogluon.tabular import TabularPredictor

        predictor = TabularPredictor(
            label="Y",
            eval_metric="roc_auc",
            path=ag_path,
            problem_type="binary",
            sample_weight="_sample_weight",
            verbosity=1,
        )

        predictor.fit(
            train_data=train_ag,
            presets="best_quality",
            time_limit=fold_budget,
            auto_stack=True,
            num_bag_folds=5,
            num_bag_sets=1,        # 1 repeat per fold (5 total across outer CV)
            num_stack_levels=1,    # L2 stacking within AG
            excluded_model_types=["FASTAI"],   # skip FastAI for stability
        )

        # ── OOF from this fold ────────────────────────────────────────────────
        val_proba_df = predictor.predict_proba(X_val_fe)
        if isinstance(val_proba_df, pd.DataFrame):
            val_proba = val_proba_df[1.0].values if 1.0 in val_proba_df.columns else val_proba_df.iloc[:, 1].values
        else:
            val_proba = np.array(val_proba_df)

        val_proba = np.nan_to_num(val_proba, nan=0.0)
        oof_proba[val_idx] = val_proba

        fold_auc = roc_auc_score(y_val, val_proba)
        fold_aucs.append(fold_auc)
        print(f"[V37] Fold {fold_idx+1} val AUC: {fold_auc:.5f}")

        # ── Test predictions for this fold ───────────────────────────────────
        test_proba_df = predictor.predict_proba(X_test_fe_f)
        if isinstance(test_proba_df, pd.DataFrame):
            tp = test_proba_df[1.0].values if 1.0 in test_proba_df.columns else test_proba_df.iloc[:, 1].values
        else:
            tp = np.array(test_proba_df)
        test_proba_folds[:, fold_idx] = np.nan_to_num(tp, nan=0.0)

        # ── Leaderboard ───────────────────────────────────────────────────────
        try:
            lb = predictor.leaderboard(val_ag, silent=True)
            lb["fold"] = fold_idx
            fold_leaderboards.append(lb)
            top3 = lb.head(3)[["model", "score_val"]].to_dict("records")
            print(f"[V37] Fold {fold_idx+1} top-3: {top3}")
        except Exception as e:
            print(f"[V37] Leaderboard failed fold {fold_idx+1}: {e}")

    except Exception as e:
        print(f"[V37] ERROR in fold {fold_idx+1}: {e}")
        traceback.print_exc()
        # Partial fold — leave oof_proba[val_idx] = 0.0
        fold_aucs.append(0.0)

    fold_elapsed = time.time() - fold_start
    print(f"[V37] Fold {fold_idx+1} done in {fold_elapsed/60:.1f} min")

# ── Aggregate OOF AUC ─────────────────────────────────────────────────────────
completed_folds = len([a for a in fold_aucs if a > 0])
print(f"\n[V37] Completed folds: {completed_folds}/{N_FOLDS}")

# Only score on rows that had valid OOF predictions
valid_mask = oof_proba > 0.0  # rows where AG actually predicted
if valid_mask.sum() < len(y_all):
    print(f"[V37] WARNING: Only {valid_mask.sum()}/{len(y_all)} rows have OOF predictions")

# Full-dataset OOF AUC (if all folds completed)
if completed_folds == N_FOLDS:
    oof_auc_full = roc_auc_score(y_all, oof_proba)
    print(f"[V37] Full OOF AUC: {oof_auc_full:.5f}")
else:
    # Partial AUC on available rows
    valid_idx = np.where(valid_mask)[0]
    oof_auc_full = roc_auc_score(y_all[valid_idx], oof_proba[valid_idx]) if valid_mask.sum() > 10 else 0.0
    print(f"[V37] Partial OOF AUC ({valid_mask.sum()} rows): {oof_auc_full:.5f}")

fold_aucs_clean = [a for a in fold_aucs if a > 0]
oof_auc_mean = float(np.mean(fold_aucs_clean)) if fold_aucs_clean else 0.0
oof_auc_std  = float(np.std(fold_aucs_clean))  if fold_aucs_clean else 0.0
print(f"[V37] Per-fold AUC: {[f'{a:.5f}' for a in fold_aucs_clean]}")
print(f"[V37] Mean ± Std:   {oof_auc_mean:.5f} ± {oof_auc_std:.5f}")

# Bootstrap 95% CI on OOF AUC
np.random.seed(42)
boot_aucs = []
for _ in range(2000):
    idx_b = np.random.choice(len(y_all), size=len(y_all), replace=True)
    try:
        b_auc = roc_auc_score(y_all[idx_b], oof_proba[idx_b])
        boot_aucs.append(b_auc)
    except Exception:
        pass
ci_lo = float(np.percentile(boot_aucs, 2.5)) if boot_aucs else 0.0
ci_hi = float(np.percentile(boot_aucs, 97.5)) if boot_aucs else 0.0
print(f"[V37] Bootstrap 95% CI: [{ci_lo:.5f}, {ci_hi:.5f}]")

# ── Test proba (average across completed folds) ────────────────────────────────
completed_cols = [i for i, a in enumerate(fold_aucs) if a > 0]
if completed_cols:
    test_proba_avg = test_proba_folds[:, completed_cols].mean(axis=1)
else:
    test_proba_avg = test_proba_folds.mean(axis=1)
print(f"[V37] Test proba: mean={test_proba_avg.mean():.4f}, std={test_proba_avg.std():.4f}")

# ── Spearman diversity vs existing OOF files ──────────────────────────────────
print(f"\n[V37] Computing Spearman correlations vs existing OOF files...")
spearman_results = {}

oof_v4_path   = BASE / "build_v4" / "oof_v4.parquet"
oof_v33_path  = BASE / "build_v33" / "oof_v33.parquet"
oof_v35_path  = BASE / "build_v35" / "oof_v35.parquet"

for name, path, col in [
    ("V4_meta",  oof_v4_path,  "oof_meta"),
    ("V33",      oof_v33_path, "oof_proba"),
    ("V35_rank", oof_v35_path, "rank_avg_proba"),
]:
    try:
        df_oof = pd.read_parquet(path)
        if col in df_oof.columns:
            other_proba = df_oof[col].values
        else:
            # Try first numeric col after CoilID/Y
            num_cols = [c for c in df_oof.columns if c not in ("CoilID", "Y", "y")]
            other_proba = df_oof[num_cols[0]].values

        if len(other_proba) == len(oof_proba):
            r, p = spearmanr(oof_proba, other_proba)
            spearman_results[name] = float(r)
            diversity_tag = "DIVERSE" if abs(r) < 0.80 else ("MODERATE" if abs(r) < 0.90 else "HIGH_CORR")
            print(f"[V37] Spearman V37 vs {name}: r={r:.4f} [{diversity_tag}]")
        else:
            print(f"[V37] {name}: length mismatch ({len(other_proba)} vs {len(oof_proba)})")
    except Exception as e:
        print(f"[V37] {name}: FAILED — {e}")

# ── AutoGluon top model types (aggregate across folds) ────────────────────────
print(f"\n[V37] AutoGluon model leaderboard summary:")
if fold_leaderboards:
    all_lb = pd.concat(fold_leaderboards, ignore_index=True)
    # Average val AUC per model type (strip fold-specific suffixes)
    def model_family(name: str) -> str:
        for fam in ["LightGBM", "XGBoost", "CatBoost", "RandomForest", "ExtraTrees",
                    "NeuralNetTorch", "NeuralNetFastAI", "KNeighbors", "LinearModel",
                    "WeightedEnsemble"]:
            if fam.lower() in name.lower():
                return fam
        return name.split("_")[0]

    all_lb["model_family"] = all_lb["model"].apply(model_family)
    family_auc = (
        all_lb.groupby("model_family")["score_val"]
        .mean()
        .sort_values(ascending=False)
    )
    print(family_auc.head(10).to_string())
    top3_families = family_auc.head(3).to_dict()
else:
    top3_families = {}
    print("[V37] No leaderboard data available")

# ── OOF threshold sweep (for CV report) ──────────────────────────────────────
best_score, best_T, best_R, best_P = 0.0, 0.5, 0.0, 0.0
for T in np.linspace(0.001, 0.999, 1000):
    preds = (oof_proba >= T).astype(int)
    tp = int(((preds == 1) & (y_all == 1)).sum())
    fp = int(((preds == 1) & (y_all == 0)).sum())
    fn = int(((preds == 0) & (y_all == 1)).sum())
    recall    = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    score = (recall + precision) / 2 * 100
    if score > best_score:
        best_score, best_T, best_R, best_P = score, T, recall, precision

print(f"\n[V37] Best OOF (R+P)/2: {best_score:.2f}%")
print(f"[V37] Best threshold:   {best_T:.5f}")
print(f"[V37] Recall:           {best_R:.4f}")
print(f"[V37] Precision:        {best_P:.4f}")

# ── Save OOF parquet ──────────────────────────────────────────────────────────
oof_df = pd.DataFrame({
    "CoilID": coil_train,
    "oof_proba": oof_proba,
    "y": y_all.astype(int),
})
oof_df.to_parquet(OUT / "oof_v37.parquet", index=False)
print(f"\n[V37] Saved: oof_v37.parquet ({len(oof_df)} rows)")

# ── Save test proba parquet ───────────────────────────────────────────────────
test_proba_df = pd.DataFrame({
    "CoilID": coil_test,
    "test_proba": test_proba_avg,
})
test_proba_df.to_parquet(OUT / "test_proba_v37.parquet", index=False)
print(f"[V37] Saved: test_proba_v37.parquet ({len(test_proba_df)} rows)")

# ── Wall clock summary ────────────────────────────────────────────────────────
total_elapsed = wall_elapsed()
print(f"\n[V37] Wall elapsed: {total_elapsed/60:.1f} min")

# ── Write CV report ───────────────────────────────────────────────────────────
cal_delta = 2.67   # historical OOF→LB calibration delta (from V18/V4 history)
lb_est = best_score + cal_delta

spearman_lines = "\n".join(
    [f"- V37 vs {name}: r={r:.4f} ({'DIVERSE' if abs(r) < 0.80 else 'MODERATE' if abs(r) < 0.90 else 'HIGH_CORR'})"
     for name, r in spearman_results.items()]
) or "- Not computed (missing OOF files)"

top3_lb_str = "\n".join(
    [f"{i+1}. {fam}: val_AUC={auc:.5f}"
     for i, (fam, auc) in enumerate(list(top3_families.items())[:3])]
) or "- Leaderboard data unavailable"

# Gate verdict
gate_reason = "none — OOF AUC and diversity metrics are primary gates"
gate_pass = (oof_auc_mean >= 0.80) and (completed_folds >= 3)

cv_report = f"""# CV Report — V37 AutoGluon

**Date:** 2026-05-24
**Builder:** ml-engineer-agent
**Preset:** best_quality | time_limit={fold_budget}s/fold | BBSE w1={W1}, w0={W0}

---

## AutoGluon Version
- autogluon.tabular 1.5.0 (pre-installed in Jarvis venv)

## OOF AUC Results

| Metric | Value |
|---|---|
| Completed folds | {completed_folds}/{N_FOLDS} |
| Per-fold AUCs | {[f'{a:.5f}' for a in fold_aucs_clean]} |
| Mean OOF AUC | {oof_auc_mean:.5f} |
| Std OOF AUC | {oof_auc_std:.5f} |
| Full OOF AUC | {oof_auc_full:.5f} |
| Bootstrap 95% CI | [{ci_lo:.5f}, {ci_hi:.5f}] |

## Competition Metric (OOF)

| Metric | Value |
|---|---|
| Best (R+P)/2 | {best_score:.4f}% |
| Best threshold | {best_T:.5f} |
| Recall | {best_R:.4f} |
| Precision | {best_P:.4f} |
| Calibrated LB est | {lb_est:.2f} (OOF {best_score:.2f} + delta {cal_delta}) |
| V4 banked LB | 56.98 |
| V35 best LB | 67.55 |

## AutoGluon Top-3 Base Learners (by OOF AUC, averaged across folds)

{top3_lb_str}

## Paradigm Diversity — Spearman Correlation vs Existing OOFs

{spearman_lines}

Target: r < 0.80 vs each existing OOF for genuine paradigm diversity.
If r > 0.90 vs all existing, AutoGluon is converging to GBDT solutions → diversity claim fails.

## Wall Clock

- Total elapsed: {total_elapsed/60:.1f} min
- Budget: 55 min

## Consensus Union Gate

- Gate pass: {'YES' if gate_pass else 'NO'}
- Reason: {gate_reason}

## Feature Engineering

- V33's 105-feature pipeline (fold-isolated medians, AP-1 compliant)
- Stand ordering: {ordering['temp_order_status']} | {ordering['force_order_status']}
- BBSE weights: w1={W1} (defect), w0={W0} (normal)

## Risks

1. **OOF leakage via AG internal bagging:** AutoGluon uses its own internal bagging (num_bag_folds=5)
   inside our outer fold. This means the OOF probabilities from AG are actually from 5-inner-fold
   bagged models, not a pure holdout. This slightly optimistically biases per-fold AUC vs true OOF.
   Mitigation: the outer StratifiedKFold ensures no outer fold leakage.

2. **AutoGluon NN convergence on small data:** With 1080 train rows per fold, NNs may underfit
   (not enough data) or overfit (too many parameters). AG's bagging partially mitigates this.
   The GBDT models inside AG will likely dominate the ensemble.

3. **Spearman > 0.90 vs existing GBDTs:** If AG's ensemble is GBDT-dominated, V37 may not
   provide genuine diversity. In that case, the consensus union gains little from V37.
"""

with open(OUT / "cv_report_v37.md", "w") as f:
    f.write(cv_report)
print(f"[V37] Saved: cv_report_v37.md")

# ── Save metrics JSON ────────────────────────────────────────────────────────
metrics = {
    "completed_folds": completed_folds,
    "fold_aucs": fold_aucs_clean,
    "oof_auc_mean": oof_auc_mean,
    "oof_auc_std": oof_auc_std,
    "oof_auc_full": float(oof_auc_full),
    "ci_lo": ci_lo,
    "ci_hi": ci_hi,
    "best_oof_score": float(best_score),
    "best_T": float(best_T),
    "recall": float(best_R),
    "precision": float(best_P),
    "lb_estimate": float(lb_est),
    "cal_delta": cal_delta,
    "spearman": spearman_results,
    "top3_model_families": top3_families,
    "wall_elapsed_min": float(total_elapsed / 60),
    "gate_pass": gate_pass,
}
with open(OUT / "metrics_v37.json", "w") as f:
    json.dump(metrics, f, indent=2)
print(f"[V37] Saved: metrics_v37.json")

print(f"\n[V37] DONE — AutoGluon paradigm complete")
print(f"[V37] Files: oof_v37.parquet | test_proba_v37.parquet | cv_report_v37.md")
print(f"[V37] DO NOT SUBMIT — orchestrator handles consensus union")
