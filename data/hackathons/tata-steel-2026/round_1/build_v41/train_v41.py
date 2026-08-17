#!/usr/bin/env python3
"""
train_v41.py — BBSE-Reweighted Single LightGBM (iter37-equivalent paradigm)
Tata Steel Hot Rolling Defect Detection

Motivation (Ratnesh-Jarvis peer intel):
  iter37 = BBSE-reweighted version of v32 9-model base.
  From peer-chat: "iter37 BBSE-alone K=170 → LB 56.86.
  My LGB used default scale_pos_weight=cw=neg/pos≈19.5 — adding BBSE
  w₁=9.3 gave ~177x effective positive weight."

  BBSE STANDALONE is mid (~LB 56). BUT as a CONSENSUS PARADIGM it is
  valuable because it produces different score-RANKINGS than
  scale_pos_weight-based models. That Spearman diversity is the goal.

Architecture:
  - V4's 51 SHAP-selected features (same features, different objective)
  - Single LightGBM (no ensemble, no stacking)
  - NO SMOTE
  - scale_pos_weight = 1  (neutral — BBSE handles rebalancing via weights)
  - BBSE sample_weight: w1 = 0.45/0.05 = 9.0 (Y=1), w0 = 0.55/0.95 ≈ 0.579 (Y=0)
    Derivation: train prevalence ≈ 5%, expected test prevalence ≈ 45%
  - 5-fold StratifiedKFold seed=42 (matches V4/V33/V35 structure)
  - Fold-isolated StandSetpoints medians (AP-1 compliant, inherited from V35 pattern)

Hard constraints:
  - NO auto-submission
  - NO pd.concat([train, test]) feature fit
  - NO other build_v*/ directories touched
  - scale_pos_weight = 1 (non-negotiable for BBSE paradigm purity)

Output:
  - oof_v41.parquet   — 1352 rows: CoilID, oof_proba, y
  - test_proba_v41.parquet — 339 rows: CoilID, test_proba
  - cv_report_v41.md
  - approach.md (written by train script at end)
"""

from __future__ import annotations

import json
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import roc_auc_score
import lightgbm as lgb

warnings.filterwarnings("ignore")

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE    = Path("/home/ujjwal/Documents/J.A.R.V.I.S./data/hackathons/tata-steel-2026/round_1")
RAW_DIR = Path("/home/ujjwal/Documents/J.A.R.V.I.S./data set of tata steel/dataset")
V4_DIR  = BASE / "build_v4"
OUT     = BASE / "build_v41"
OUT.mkdir(parents=True, exist_ok=True)

# ── Constants ──────────────────────────────────────────────────────────────────
SEED        = 42
N_FOLDS     = 5
TARGET      = "Y"
ID_COL      = "CoilID"

# BBSE weights
# Train prevalence: 66/1352 ≈ 0.0488 ≈ 5%
# Expected test prevalence: ~45% (Ratnesh peer intel + prior LB calibration)
# w1 = p_test_pos / p_train_pos = 0.45 / 0.05 = 9.0
# w0 = p_test_neg / p_train_neg = 0.55 / 0.95 ≈ 0.5789
W1 = 0.45 / 0.05          # = 9.0
W0 = 0.55 / 0.95           # ≈ 0.5789

# Stand-FE source columns (needed for StandSetpoints)
TEMP_COLS  = ["X4", "X5", "X6", "X7", "X8", "X9"]
FORCE_COLS = ["X29", "X30", "X31", "X32", "X33"]

print("=" * 70)
print("V41 — BBSE-Reweighted Single LightGBM (iter37-equivalent)")
print(f"BBSE: w1={W1:.4f} (Y=1), w0={W0:.4f} (Y=0) | scale_pos_weight=1 (neutral)")
print(f"{N_FOLDS}-fold StratifiedKFold seed={SEED}")
print("=" * 70)


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 1: StandSetpoints (fold-isolated medians — V35 pattern, AP-1 compliant)
# ═══════════════════════════════════════════════════════════════════════════════

class StandSetpoints:
    """Fold-isolated setpoint statistics.
    Fit ONLY on the training fold; never on val or test rows."""

    def __init__(self):
        self.temp_medians      = None
        self.force_medians     = None
        self.temp_stds         = None
        self.force_stds        = None
        self.x35_high_median   = None
        self.x35_high_std      = None
        self.is_fitted         = False

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
        assert self.is_fitted, "Must call .fit() before .transform()"
        df = df.copy()
        # Signed + absolute temperature residuals (12 features)
        for i, col in enumerate(TEMP_COLS):
            med = self.temp_medians[col]
            df[f"res_temp_{i+1}"]     = df[col] - med
            df[f"abs_res_temp_{i+1}"] = (df[col] - med).abs()
        # Signed + absolute force residuals (10 features)
        for i, col in enumerate(FORCE_COLS):
            med = self.force_medians[col]
            df[f"res_force_{i+1}"]     = df[col] - med
            df[f"abs_res_force_{i+1}"] = (df[col] - med).abs()
        # Cumulative z-deviation (2 features)
        temp_z  = (df[TEMP_COLS]  - self.temp_medians)  / self.temp_stds
        force_z = (df[FORCE_COLS] - self.force_medians) / self.force_stds
        all_z   = pd.concat([temp_z, force_z], axis=1)
        df["cum_process_dev"] = all_z.abs().sum(axis=1)
        df["max_abs_z_dev"]   = all_z.abs().max(axis=1)
        # Raw deviations (3 features)
        df["cum_force_dev_raw"]  = (df[FORCE_COLS] - self.force_medians).sum(axis=1)
        df["max_abs_force_dev"]  = (df[FORCE_COLS] - self.force_medians).abs().max(axis=1)
        df["max_abs_temp_dev"]   = (df[TEMP_COLS]  - self.temp_medians).abs().max(axis=1)
        # Worst-deviant stand (4 features)
        temp_res_cols  = [f"res_temp_{s}"  for s in range(1, 7)]
        force_res_cols = [f"res_force_{s}" for s in range(1, 6)]
        df["worst_temp_stand"]  = df[temp_res_cols].abs().values.argmax(axis=1).astype(float)
        df["worst_temp_mag"]    = df[temp_res_cols].abs().max(axis=1)
        df["worst_force_stand"] = df[force_res_cols].abs().values.argmax(axis=1).astype(float)
        df["worst_force_mag"]   = df[force_res_cols].abs().max(axis=1)
        # Inter-stand temperature gradients (5 features)
        for i in range(len(TEMP_COLS) - 1):
            df[f"temp_drop_{i+1}_{i+2}"] = df[TEMP_COLS[i]] - df[TEMP_COLS[i + 1]]
        # X35 bimodal decomposition (4 features)
        if "X35" in df.columns:
            df["X35_is_high"]          = (df["X35"] > 1e6).astype(float)
            df["X35_log1p"]            = np.log1p(df["X35"])
            df["X35_high_mode_zscore"] = np.where(
                df["X35"] > 1e6,
                (df["X35"] - self.x35_high_median) / self.x35_high_std,
                0.0,
            )
            df["X35_flag_x_cum_force"] = df["X35_is_high"] * df["cum_force_dev_raw"]
        # Temperature × Force residual cross-products (5 features)
        for k in range(5):
            t_col = TEMP_COLS[k]; f_col = FORCE_COLS[k]
            df[f"res_cross_{k+1}"] = (
                (df[t_col] - self.temp_medians[t_col]) *
                (df[f_col] - self.force_medians[f_col])
            )
        # Temperature span (3 features)
        df["temp_span"]  = df[TEMP_COLS[0]] - df[TEMP_COLS[-1]]
        df["temp_entry"] = df[TEMP_COLS[0]]
        df["temp_exit"]  = df[TEMP_COLS[-1]]
        # Force escalation ratio (1 feature)
        df["force_escalation_ratio"] = df[FORCE_COLS[-1]] / (df[FORCE_COLS[0]] + 1e-6)
        # Log force columns (5 features)
        for col in FORCE_COLS:
            df[f"log_{col}"] = np.log1p(df[col].clip(lower=0))
        return df


STAND_FE_COLS = (
    [f"res_temp_{i+1}"     for i in range(6)] +
    [f"abs_res_temp_{i+1}" for i in range(6)] +
    [f"res_force_{i+1}"     for i in range(5)] +
    [f"abs_res_force_{i+1}" for i in range(5)] +
    ["cum_process_dev", "max_abs_z_dev", "cum_force_dev_raw",
     "max_abs_force_dev", "max_abs_temp_dev"] +
    ["worst_temp_stand", "worst_temp_mag", "worst_force_stand", "worst_force_mag"] +
    [f"temp_drop_{i+1}_{i+2}" for i in range(5)] +
    ["X35_is_high", "X35_log1p", "X35_high_mode_zscore", "X35_flag_x_cum_force"] +
    [f"res_cross_{k+1}" for k in range(5)] +
    ["temp_span", "temp_entry", "temp_exit", "force_escalation_ratio"] +
    [f"log_{col}" for col in FORCE_COLS]
)
print(f"Stand-FE columns: {len(STAND_FE_COLS)}")  # should be 54


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 2: Load Data
# ═══════════════════════════════════════════════════════════════════════════════

print("\n[1/6] Loading data...")

v4_train = pd.read_parquet(V4_DIR / "train_v4.parquet")
v4_test  = pd.read_parquet(V4_DIR / "test_v4.parquet")

with open(V4_DIR / "v4_final_features.json") as f:
    V4_FEATURES = json.load(f)["features"]  # 51 SHAP-selected

print(f"  V4 train: {v4_train.shape} | V4 test: {v4_test.shape}")
print(f"  V4 features: {len(V4_FEATURES)} SHAP-selected")
print(f"  Positives: {int(v4_train[TARGET].sum())} / {len(v4_train)} ({v4_train[TARGET].mean()*100:.2f}%)")

# Validate all 51 V4 features exist
missing = [f for f in V4_FEATURES if f not in v4_train.columns]
assert not missing, f"Missing V4 features: {missing}"
print(f"  V4 feature validation: ALL {len(V4_FEATURES)} present")

y = v4_train[TARGET].values.astype(float)
coil_train = v4_train[ID_COL].values
coil_test  = v4_test[ID_COL].values
n_train    = len(v4_train)
n_test     = len(v4_test)

# Build BBSE sample weights for all training rows
sample_weights_all = np.where(y == 1, W1, W0)
print(f"\n  BBSE weights: w1={W1:.4f} (Y=1, n={int(y.sum())}), w0={W0:.4f} (Y=0, n={int((1-y).sum())})")
print(f"  Effective pos/neg ratio: {W1/W0:.2f}x  (vs scale_pos_weight≈19.5 in V35)")


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 3: LightGBM model factory
# ═══════════════════════════════════════════════════════════════════════════════

def make_lgb_bbse() -> lgb.LGBMClassifier:
    """Single LightGBM with scale_pos_weight=1.
    BBSE rebalancing is carried by sample_weight — NOT by scale_pos_weight.
    Hyperparams kept close to V4's base LGB to isolate the BBSE paradigm effect."""
    return lgb.LGBMClassifier(
        # scale_pos_weight = 1 (BBSE paradigm: weights do the rebalancing)
        scale_pos_weight=1,
        learning_rate=0.02,
        num_leaves=15,
        min_child_samples=5,
        subsample=0.7,
        colsample_bytree=0.7,
        n_estimators=300,
        random_state=SEED,
        verbose=-1,
        n_jobs=-1,
    )

print(f"\n[2/6] Model: Single LightGBM (scale_pos_weight=1, BBSE sample_weight)")


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 4: 5-Fold CV Training Loop
# ═══════════════════════════════════════════════════════════════════════════════

print(f"\n[3/6] Training {N_FOLDS}-fold StratifiedKFold (seed={SEED})...")

skf = StratifiedKFold(n_splits=N_FOLDS, shuffle=True, random_state=SEED)

oof_proba     = np.zeros(n_train)
test_proba_folds = np.zeros((n_test, N_FOLDS))
fold_aucs     = []

for fold_idx, (tr_idx, val_idx) in enumerate(skf.split(np.zeros(n_train), y)):
    y_tr  = y[tr_idx]
    y_val = y[val_idx]
    sw_tr = sample_weights_all[tr_idx]

    print(f"\n  --- Fold {fold_idx+1}/{N_FOLDS} | train={len(tr_idx)}, val={len(val_idx)}, "
          f"pos_train={int(y_tr.sum())}, pos_val={int(y_val.sum())} ---")

    # ── Fold-isolated StandSetpoints (fit on train fold ONLY) ─────────────────
    setpoints = StandSetpoints()
    setpoints.fit(v4_train.iloc[tr_idx])   # AP-1: only train-fold rows

    tr_fe   = setpoints.transform(v4_train.iloc[tr_idx].copy())
    val_fe  = setpoints.transform(v4_train.iloc[val_idx].copy())

    # Test: fit setpoints on FULL train (no label leakage for test)
    test_setpoints = StandSetpoints()
    test_setpoints.fit(v4_train)
    test_fe = test_setpoints.transform(v4_test.copy())

    # ── Feature matrix: V4 51 features ONLY (no stand-FE for V41)  ───────────
    # Key spec: "same features as V4" = 51 SHAP-selected features
    # Stand-FE was V33/V35's contribution — V41 uses only V4's 51 to isolate
    # the BBSE paradigm effect cleanly
    X_tr   = tr_fe[V4_FEATURES].values
    X_val  = val_fe[V4_FEATURES].values
    X_test = test_fe[V4_FEATURES].values

    if fold_idx == 0:
        print(f"    Feature matrix shape: {X_tr.shape} (V4 51 features, BBSE paradigm)")
        print(f"    sample_weight sum: pos={sw_tr[y_tr==1].sum():.2f}, neg={sw_tr[y_tr==0].sum():.2f}")

    # ── Train ─────────────────────────────────────────────────────────────────
    model = make_lgb_bbse()
    model.fit(
        X_tr, y_tr,
        sample_weight=sw_tr,
    )

    val_proba_fold  = model.predict_proba(X_val)[:, 1]
    test_proba_fold = model.predict_proba(X_test)[:, 1]

    oof_proba[val_idx]          = val_proba_fold
    test_proba_folds[:, fold_idx] = test_proba_fold

    fold_auc = roc_auc_score(y_val, val_proba_fold)
    fold_aucs.append(fold_auc)
    print(f"    Fold {fold_idx+1} AUC: {fold_auc:.5f}")


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 5: Aggregate + Metrics
# ═══════════════════════════════════════════════════════════════════════════════

print(f"\n[4/6] Computing metrics...")

test_proba_avg = test_proba_folds.mean(axis=1)

# Full OOF AUC
oof_auc = roc_auc_score(y, oof_proba)
print(f"  Full OOF AUC: {oof_auc:.5f}")
print(f"  Per-fold AUC: {[f'{a:.5f}' for a in fold_aucs]}")
print(f"  Mean ± Std:   {np.mean(fold_aucs):.5f} ± {np.std(fold_aucs):.5f}")

# Bootstrap 95% CI
np.random.seed(SEED)
boot_aucs = []
for _ in range(2000):
    idx_b = np.random.choice(n_train, size=n_train, replace=True)
    try:
        b_auc = roc_auc_score(y[idx_b], oof_proba[idx_b])
        boot_aucs.append(b_auc)
    except Exception:
        pass
ci_lo = float(np.percentile(boot_aucs, 2.5))
ci_hi = float(np.percentile(boot_aucs, 97.5))
print(f"  Bootstrap 95% CI: [{ci_lo:.5f}, {ci_hi:.5f}]")

# OOF threshold sweep for (R+P)/2
best_score, best_T, best_R, best_P = 0.0, 0.5, 0.0, 0.0
for T in np.linspace(0.001, 0.999, 2000):
    preds = (oof_proba >= T).astype(int)
    tp = int(((preds == 1) & (y == 1)).sum())
    fp = int(((preds == 1) & (y == 0)).sum())
    fn = int(((preds == 0) & (y == 1)).sum())
    recall    = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    score     = (recall + precision) / 2 * 100
    if score > best_score:
        best_score, best_T, best_R, best_P = score, T, recall, precision

print(f"\n  Best OOF (R+P)/2: {best_score:.2f}%  at T={best_T:.5f}")
print(f"  Recall={best_R:.4f}, Precision={best_P:.4f}")

cal_delta = 2.67
lb_est = best_score + cal_delta
print(f"  Calibrated LB est: {lb_est:.2f} (OOF {best_score:.2f} + delta {cal_delta})")


# ── Spearman diversity ────────────────────────────────────────────────────────

print(f"\n[5/6] Computing Spearman correlations vs existing paradigms...")

spearman_results = {}
oof_refs = [
    ("V4_meta",      BASE / "build_v4"  / "oof_v4.parquet",  "oof_meta"),
    ("V33",          BASE / "build_v33" / "oof_v33.parquet", "oof_proba"),
    ("V35_rank_avg", BASE / "build_v35" / "oof_v35.parquet", "rank_avg_proba"),
    ("V37_autogluon",BASE / "build_v37" / "oof_v37.parquet", "oof_proba"),
]

for name, path, col in oof_refs:
    try:
        df_ref = pd.read_parquet(path)
        if col in df_ref.columns:
            other = df_ref[col].values
        else:
            num_cols = [c for c in df_ref.columns if c not in (ID_COL, "Y", "y")]
            other = df_ref[num_cols[0]].values
        if len(other) == n_train:
            r, p = spearmanr(oof_proba, other)
            spearman_results[name] = float(r)
            tag = "DIVERSE" if abs(r) < 0.80 else ("MODERATE" if abs(r) < 0.90 else "HIGH_CORR")
            print(f"  V41 vs {name}: r={r:.4f} [{tag}]  (target: < 0.85 for paradigm value)")
        else:
            print(f"  {name}: length mismatch ({len(other)} vs {n_train})")
    except Exception as e:
        print(f"  {name}: FAILED — {e}")


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 6: Save Artifacts
# ═══════════════════════════════════════════════════════════════════════════════

print(f"\n[6/6] Saving artifacts...")

# OOF parquet
oof_df = pd.DataFrame({
    "CoilID": coil_train,
    "oof_proba": oof_proba,
    "y": y.astype(int),
})
oof_df.to_parquet(OUT / "oof_v41.parquet", index=False)
print(f"  oof_v41.parquet: {oof_df.shape}")

# Test proba parquet
test_proba_df = pd.DataFrame({
    "CoilID": coil_test,
    "test_proba": test_proba_avg,
})
test_proba_df.to_parquet(OUT / "test_proba_v41.parquet", index=False)
print(f"  test_proba_v41.parquet: {test_proba_df.shape}")

print(f"\n[V41] OOF proba stats: mean={oof_proba.mean():.4f}, std={oof_proba.std():.4f}, "
      f"max={oof_proba.max():.4f}, min={oof_proba.min():.4f}")
print(f"[V41] Test proba stats: mean={test_proba_avg.mean():.4f}, std={test_proba_avg.std():.4f}")


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 7: CV Report
# ═══════════════════════════════════════════════════════════════════════════════

spearman_lines = "\n".join(
    [f"- V41 vs {name}: r={r:.4f}  "
     f"({'DIVERSE' if abs(r) < 0.80 else 'MODERATE' if abs(r) < 0.90 else 'HIGH_CORR'}) "
     f"| paradigm_value={'YES — unique ranking' if abs(r) < 0.85 else 'MODERATE' if abs(r) < 0.92 else 'LOW — high overlap'}"
     for name, r in spearman_results.items()]
) or "- Spearman not computed (missing OOF files)"

# Ready-to-merge verdict
max_spearman = max(abs(r) for r in spearman_results.values()) if spearman_results else 1.0
merge_verdict = "YES" if max_spearman < 0.92 else "MARGINAL (high Spearman — check consensus gain)"

cv_report = f"""# CV Report — V41 BBSE-Reweighted LightGBM

**Date:** 2026-05-24
**Builder:** ml-engineer-agent
**Paradigm:** BBSE sample weights | scale_pos_weight=1 | single LightGBM
**Feature set:** V4's 51 SHAP-selected features (NO stand-FE, NO SMOTE)

---

## Design Rationale (BBSE Paradigm)

Ratnesh-Jarvis peer intel: iter37 = BBSE-reweighted version of his v32 base.
- Train prevalence: ~5% positive (66/1352)
- Expected test prevalence: ~45% positive (from K=170/339)
- BBSE reweight: w1 = 0.45/0.05 = {W1:.4f}, w0 = 0.55/0.95 = {W0:.4f}
- scale_pos_weight = 1 (BBSE does the rebalancing, not LGB's built-in mechanism)
- Effective w1/w0 ratio = {W1/W0:.2f}x (vs ≈19.5x in V35's scale_pos_weight)

The key BBSE insight: by matching train→test distribution shift explicitly via
sample weights (rather than amplifying class imbalance), BBSE produces different
score RANKINGS than scale_pos_weight-based models — even on identical features.
This ranking diversity is the consensus-union value, not standalone AUC.

---

## OOF AUC Results

| Metric | Value |
|---|---|
| Per-fold AUCs | {[f'{a:.5f}' for a in fold_aucs]} |
| Mean OOF AUC | {np.mean(fold_aucs):.5f} |
| Std OOF AUC | {np.std(fold_aucs):.5f} |
| Full OOF AUC | {oof_auc:.5f} |
| Bootstrap 95% CI | [{ci_lo:.5f}, {ci_hi:.5f}] |

**Note on AUC:** BBSE reweighting distorts the OOF probability distribution
(shifts calibration toward test prevalence). The OOF AUC is expected to be LOWER
than V4/V35 (which optimize for train-distribution AUC). This is by design —
the probe for paradigm value is Spearman diversity, not AUC ranking.

---

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

**Expected: LB est ~56 (peer confirmation: Ratnesh's iter37 BBSE-alone → LB 56.86)**

---

## Paradigm Diversity — Spearman Correlation

{spearman_lines}

**Target:** r < 0.85 vs all existing paradigms = unique ranking signal.
**Ratnesh result:** BBSE shifted his ranking enough to add consensus signal
when combined with his 9-model ensemble.

---

## Consensus Union Readiness

| Criterion | Result |
|---|---|
| Standalone AUC competitive? | NO (expected — BBSE standalone is mid) |
| Spearman < 0.85 vs all? | {'YES' if max_spearman < 0.85 else f'MAX r={max_spearman:.4f} — check'} |
| Adds unique ranking signal? | {merge_verdict} |
| Ready to merge into consensus? | **{merge_verdict}** |

---

## Top-3 Risks

1. **OOF AUC optimism:** BBSE shifts the predicted probabilities toward test
   prevalence, which may inflate or deflate OOF AUC compared to what a
   well-calibrated model would show. OOF AUC is NOT the primary quality metric
   here — Spearman diversity is.

2. **OOF calibration ≠ LB calibration:** The +2.67 delta was calibrated on
   scale_pos_weight-based models. BBSE rebalancing changes the probability
   scale; the delta may not hold. **Do NOT use V41 OOF score as LB predictor
   for consensus-union submissions.**

3. **Spearman convergence risk:** If BBSE-reweighted LGB converges to the same
   tree splits as scale_pos_weight-based LGB (same features + similar effective
   rebalancing), Spearman will be > 0.90 and V41 adds no diversity. Check
   spearman_results above — if all r > 0.90, V41 is redundant.

---

## Features Used

- **V4's 51 SHAP-selected features** (no stand-FE additions)
- Spec: same feature set as V4 paradigm — different training OBJECTIVE
- Stand-FE omitted by design to isolate BBSE paradigm effect cleanly
- Fold-isolated StandSetpoints medians applied for V4 lag/temporal features

---

## Files

- `oof_v41.parquet` — 1352 rows, cols: CoilID, oof_proba, y
- `test_proba_v41.parquet` — 339 rows, cols: CoilID, test_proba
- `cv_report_v41.md` — this file
- `approach.md` — human-readable paradigm summary

**DO NOT SUBMIT V41 standalone** — consensus union only.
"""

with open(OUT / "cv_report_v41.md", "w") as f:
    f.write(cv_report)
print(f"  cv_report_v41.md: saved")


# ── approach.md ───────────────────────────────────────────────────────────────

approach_md = f"""# V41 Approach — BBSE-Reweighted LightGBM

## TL;DR
BBSE (Black-Box Shift Estimation) sample-weight paradigm on V4's 51 features.
iter37-equivalent per Ratnesh-Jarvis peer intel.
Standalone LB ≈ 56. Value = ranking diversity in consensus union.

## Problem Setup
- Binary classification: defect (Y=1) in hot-rolling coils
- Train: 1352 rows, 66 positives (4.88%)
- Test: 339 rows, expected ~45% positive (→ w1=9.0, w0=0.579)
- Score: (Recall + Precision) / 2 × 100

## BBSE Paradigm
Dataset shift: train prevalence ≠ test prevalence. BBSE corrects by
reweighting each training sample to match the test distribution:
  w(x) = p_test(y) / p_train(y)
  w1 = 0.45 / 0.05 = {W1:.2f}  (Y=1 samples get 9x weight)
  w0 = 0.55 / 0.95 = {W0:.4f}  (Y=0 samples get 0.58x weight)

This is different from scale_pos_weight which only corrects class imbalance
without modeling the test prevalence explicitly.

## Key Differences vs V4 (same features, different paradigm)
| Dimension        | V4 (meta-stack)          | V41 (BBSE)                  |
|-----------------|--------------------------|------------------------------|
| Model           | LGB + XGB + CatBoost + LR meta | Single LightGBM         |
| Rebalancing     | SMOTE inside folds       | BBSE sample_weight           |
| scale_pos_weight| ≈ 19.5 (class ratio)     | 1.0 (neutral)                |
| Calibration     | Platt scaling            | None (raw BBSE proba)        |
| Feature set     | 51 SHAP-selected         | Same 51 SHAP-selected        |

## Results
- OOF AUC: {oof_auc:.5f}
- Bootstrap 95% CI: [{ci_lo:.5f}, {ci_hi:.5f}]
- Best OOF (R+P)/2: {best_score:.2f}%
- Calibrated LB est: {lb_est:.2f}
- Spearman vs V4: {spearman_results.get('V4_meta', float('nan')):.4f}
- Spearman vs V35: {spearman_results.get('V35_rank_avg', float('nan')):.4f}

## Lineage
V1 → V2 (SMOTE) → V3 (stacking) → V4 (neighbor FE + meta, OOF AUC 0.8837)
V33 (stand-FE) → V35 (9-model rank-avg) → V37 (AutoGluon) → V41 (BBSE paradigm)

## Consensus Union Role
V41's value is NOT its standalone score. It is the Spearman < 0.85 diversity
it brings to the consensus union. Ratnesh used BBSE+9-model consensus to
reach LB 72 — the diversity of BBSE rankings was part of that signal.

## Next Step
Feed oof_v41.parquet + test_proba_v41.parquet into consensus union alongside
V35/V33/V37. The consensus orchestrator picks K=170 positives from the
blended rank-average.
"""

with open(OUT / "approach.md", "w") as f:
    f.write(approach_md)
print(f"  approach.md: saved")

print("\n" + "=" * 70)
print("V41 SUMMARY")
print("=" * 70)
print(f"  OOF AUC         : {oof_auc:.5f}")
print(f"  Bootstrap CI    : [{ci_lo:.5f}, {ci_hi:.5f}]")
print(f"  Best OOF score  : {best_score:.2f}% (R+P)/2")
print(f"  LB estimate     : {lb_est:.2f}")
print(f"  Spearman vs V4  : {spearman_results.get('V4_meta', float('nan')):.4f}")
print(f"  Spearman vs V35 : {spearman_results.get('V35_rank_avg', float('nan')):.4f}")
print(f"  Merge ready     : {merge_verdict}")
print("=" * 70)
print("\n[V41] Files: oof_v41.parquet | test_proba_v41.parquet | cv_report_v41.md | approach.md")
print("[V41] DO NOT SUBMIT STANDALONE — consensus union only")
