"""
train_v39.py — V39 iter35-equivalent: V4 base + 7 CoilID-derived features
Tata Steel Hot Rolling Defect Detection

Architecture:
  - V4's 51-feature base (SHAP-selected + neighbor + poly + iso_score)
  - PLUS 7 CoilID-derived features (Ratnesh iter35 recipe):
      1. CoilID (raw)
      2. CoilID_sq  = CoilID ** 2
      3. CoilID_log = log(CoilID + 1)
      4. CoilID_gt_median  = (CoilID > fold_median).astype(float)
      5. CoilID_gt_p75     = (CoilID > fold_p75).astype(float)
      6. CoilID_sin        = sin(2π × CoilID / 1700)
      7. CoilID_cos        = cos(2π × CoilID / 1700)
  = 58 total features

  - Single LightGBM, scale_pos_weight=18.9 (≈1286/66, NO SMOTE, NO BBSE)
  - StratifiedKFold(5, shuffle=True, random_state=42)
  - Fold-isolated CoilID medians/percentiles (V33 leakage-safe pattern)
  - NO stand-FE, NO BBSE, NO repeated CV — pure iter35 equiv

Reference:
  Ratnesh iter35 OOF AUC = 0.9412 (peer-chat disclosure)
  His 4-paradigm consensus union → LB 72.71

V4 calibration anchor:
  V4 OOF score 54.31 → LB 56.98 (delta +2.67)
  V4 OOF AUC  0.8837

Outputs:
  oof_v39.parquet     — CoilID, oof_proba, y (for consensus merge + Spearman)
  test_proba_v39.parquet — CoilID, test_proba
  cv_report_v39.md
  approach.md
"""

from __future__ import annotations

import json
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import rankdata, spearmanr
from sklearn.metrics import roc_auc_score, precision_score, recall_score
from sklearn.model_selection import StratifiedKFold
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import PolynomialFeatures
import lightgbm as lgb
import re

warnings.filterwarnings("ignore")

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE     = Path("/home/ujjwal/Documents/J.A.R.V.I.S.")
RAW_DIR  = BASE / "data set of tata steel/dataset"
V4_DIR   = BASE / "data/hackathons/tata-steel-2026/round_1/build_v4"
V39_DIR  = BASE / "data/hackathons/tata-steel-2026/round_1/build_v39"
V39_DIR.mkdir(parents=True, exist_ok=True)

# ── Constants ─────────────────────────────────────────────────────────────────
SEED       = 42
N_FOLDS    = 5
SPW        = 1286 / 66   # scale_pos_weight = neg/pos ≈ 19.48 ≈ 18.9
TARGET     = "Y"
ID_COL     = "CoilID"
CYCLIC_N   = 1700        # Ratnesh's cyclic period

print("=" * 70)
print("V39 — iter35-equivalent: V4 base + 7 CoilID-derived features")
print(f"scale_pos_weight={SPW:.2f} | {N_FOLDS}-fold StratifiedKFold seed={SEED}")
print(f"Cyclic period = {CYCLIC_N} | NO SMOTE | NO BBSE | NO stand-FE")
print("=" * 70)

# ── LGB params (conservative, single model) ───────────────────────────────────
LGB_PARAMS = {
    "objective":          "binary",
    "metric":             "auc",
    "learning_rate":      0.03,
    "num_leaves":         63,
    "max_depth":          6,
    "min_child_samples":  10,
    "subsample":          0.8,
    "subsample_freq":     1,
    "colsample_bytree":   0.7,
    "reg_alpha":          0.05,
    "reg_lambda":         0.5,
    "n_estimators":       700,
    "scale_pos_weight":   SPW,
    "random_state":       SEED,
    "verbosity":          -1,
    "n_jobs":             -1,
}

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 1: Load data
# ═══════════════════════════════════════════════════════════════════════════════
print("\n[1/5] Loading data...")

train_raw = pd.read_csv(RAW_DIR / "train.csv").sort_values(ID_COL).reset_index(drop=True)
test_raw  = pd.read_csv(RAW_DIR / "test.csv").sort_values(ID_COL).reset_index(drop=True)
v4_train  = pd.read_parquet(V4_DIR / "train_v4.parquet")
v4_test   = pd.read_parquet(V4_DIR / "test_v4.parquet")

# Sort v4 parquets to match raw order (CoilID-sorted)
v4_train = v4_train.sort_values(ID_COL).reset_index(drop=True)
v4_test  = v4_test.sort_values(ID_COL).reset_index(drop=True)

# Verify alignment
assert (train_raw[ID_COL].values == v4_train[ID_COL].values).all(), "Train CoilID mismatch"
assert (test_raw[ID_COL].values  == v4_test[ID_COL].values).all(),  "Test CoilID mismatch"

with open(V4_DIR / "v4_final_features.json") as f:
    V4_FEATURES = json.load(f)["features"]   # 51 features

y              = v4_train[TARGET].values.astype(int)
coil_ids_train = v4_train[ID_COL].values
coil_ids_test  = v4_test[ID_COL].values
n_train        = len(v4_train)
n_test         = len(v4_test)

# Validate V4 features present
missing = [f for f in V4_FEATURES if f not in v4_train.columns]
assert not missing, f"Missing V4 features: {missing}"

print(f"  Train: {n_train} | Test: {n_test} | Positives: {y.sum()} ({y.mean():.4f})")
print(f"  V4 features: {len(V4_FEATURES)}")
print(f"  CoilID (train): min={coil_ids_train.min()} max={coil_ids_train.max()}")

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 2: CoilID feature builder (fold-isolated for threshold flags)
# ═══════════════════════════════════════════════════════════════════════════════

def build_coilid_features(
    coil_ids: np.ndarray,
    fold_median: float,
    fold_p75: float,
    cyclic_n: int = CYCLIC_N,
) -> pd.DataFrame:
    """
    Build 7 CoilID-derived features per Ratnesh iter35:
      1. CoilID        — raw
      2. CoilID_sq     — squared
      3. CoilID_log    — log(CoilID + 1)
      4. CoilID_gt_med — threshold flag: CoilID > fold_median
      5. CoilID_gt_p75 — threshold flag: CoilID > fold_p75
      6. CoilID_sin    — sin(2π × CoilID / cyclic_n)
      7. CoilID_cos    — cos(2π × CoilID / cyclic_n)

    fold_median and fold_p75 MUST be computed from train-fold rows only
    (to preserve leakage-safe fold isolation per V33 pattern).
    For test set, pass global train median/p75.
    """
    ids = coil_ids.astype(float)
    df = pd.DataFrame({
        "CoilID":        ids,
        "CoilID_sq":     ids ** 2,
        "CoilID_log":    np.log1p(ids),
        "CoilID_gt_med": (ids > fold_median).astype(float),
        "CoilID_gt_p75": (ids > fold_p75).astype(float),
        "CoilID_sin":    np.sin(2 * np.pi * ids / cyclic_n),
        "CoilID_cos":    np.cos(2 * np.pi * ids / cyclic_n),
    })
    return df

COILID_FEATURE_NAMES = [
    "CoilID", "CoilID_sq", "CoilID_log",
    "CoilID_gt_med", "CoilID_gt_p75",
    "CoilID_sin", "CoilID_cos",
]
TOTAL_FEATURES = len(V4_FEATURES) + len(COILID_FEATURE_NAMES)
print(f"  CoilID features: {len(COILID_FEATURE_NAMES)} — {COILID_FEATURE_NAMES}")
print(f"  Total features:  {TOTAL_FEATURES}  (51 V4 + 7 CoilID)")

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 3: 5-Fold StratifiedKFold CV (fold-isolated CoilID stats)
# ═══════════════════════════════════════════════════════════════════════════════
print(f"\n[2/5] Training single LGB — {N_FOLDS}-fold StratifiedKFold (seed={SEED})...")

skf = StratifiedKFold(n_splits=N_FOLDS, shuffle=True, random_state=SEED)

oof_proba  = np.zeros(n_train)
test_proba = np.zeros(n_test)
fold_aucs  = []

# Precompute global train stats for test-set CoilID flags (no test labels)
global_median = float(np.median(coil_ids_train))
global_p75    = float(np.percentile(coil_ids_train, 75))
print(f"  Global CoilID median (train): {global_median:.2f}")
print(f"  Global CoilID p75   (train): {global_p75:.2f}")

# Build test CoilID features once (global stats, no leakage)
test_coilid_feats = build_coilid_features(coil_ids_test, global_median, global_p75)
X_test_v4         = v4_test[V4_FEATURES].fillna(0).values
X_test_full       = np.hstack([X_test_v4, test_coilid_feats.values])

for fold_idx, (tr_idx, val_idx) in enumerate(skf.split(np.zeros(n_train), y)):
    # ── Fold-isolated CoilID stats (V33 leakage-safe pattern) ─────────────────
    fold_coil_ids   = coil_ids_train[tr_idx]
    fold_med        = float(np.median(fold_coil_ids))
    fold_p75_val    = float(np.percentile(fold_coil_ids, 75))

    # ── Build feature matrices ─────────────────────────────────────────────────
    # Train fold
    tr_coilid = build_coilid_features(coil_ids_train[tr_idx], fold_med, fold_p75_val)
    X_tr = np.hstack([
        v4_train.iloc[tr_idx][V4_FEATURES].fillna(0).values,
        tr_coilid.values,
    ])

    # Val fold — use fold_med/fold_p75 from TRAIN fold (not val fold)
    val_coilid = build_coilid_features(coil_ids_train[val_idx], fold_med, fold_p75_val)
    X_val = np.hstack([
        v4_train.iloc[val_idx][V4_FEATURES].fillna(0).values,
        val_coilid.values,
    ])

    y_tr  = y[tr_idx]
    y_val = y[val_idx]

    if fold_idx == 0:
        print(f"  Fold 0 | X_tr shape: {X_tr.shape} | pos_tr={y_tr.sum()} | pos_val={y_val.sum()}")
        print(f"    fold_med={fold_med:.2f} | fold_p75={fold_p75_val:.2f}")

    # ── Train ──────────────────────────────────────────────────────────────────
    model = lgb.LGBMClassifier(**LGB_PARAMS)
    model.fit(X_tr, y_tr)

    val_preds  = model.predict_proba(X_val)[:, 1]
    test_preds = model.predict_proba(X_test_full)[:, 1]

    oof_proba[val_idx]  = val_preds
    test_proba         += test_preds / N_FOLDS

    fold_auc = roc_auc_score(y_val, val_preds)
    fold_aucs.append(fold_auc)
    print(f"  Fold {fold_idx+1}/{N_FOLDS} | AUC: {fold_auc:.4f} | pos={y_val.sum()} neg={int((y_val==0).sum())}")

mean_fold_auc = float(np.mean(fold_aucs))
std_fold_auc  = float(np.std(fold_aucs))
oof_auc       = float(roc_auc_score(y, oof_proba))

print(f"\n  Mean fold AUC: {mean_fold_auc:.4f} ± {std_fold_auc:.4f}")
print(f"  OOF AUC:       {oof_auc:.4f}")
print(f"  Ratnesh iter35 OOF AUC (peer disclosure): 0.9412")
print(f"  V4 meta OOF AUC (reference):              0.8837")

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 4: Bootstrap CI + OOF score + Spearman vs V4
# ═══════════════════════════════════════════════════════════════════════════════
print("\n[3/5] Computing bootstrap CI + Spearman correlation vs V4 meta...")

# Bootstrap 95% CI
rng = np.random.default_rng(SEED)
boot_aucs = []
for _ in range(1000):
    idx = rng.integers(0, n_train, n_train)
    y_b = y[idx]; p_b = oof_proba[idx]
    if 0 < y_b.sum() < len(y_b):
        boot_aucs.append(roc_auc_score(y_b, p_b))

ci_lower = float(np.percentile(boot_aucs, 2.5))
ci_upper = float(np.percentile(boot_aucs, 97.5))
boot_mean = float(np.mean(boot_aucs))
print(f"  Bootstrap AUC: {boot_mean:.4f} | 95% CI: [{ci_lower:.4f}, {ci_upper:.4f}]")

# Spearman correlation vs V4 meta OOF
oof_v4 = pd.read_parquet(V4_DIR / "oof_v4.parquet")
v4_meta = oof_v4["oof_meta"].values
spearman_corr, spearman_p = spearmanr(oof_proba, v4_meta)
print(f"  Spearman(V39, V4_meta): rho={spearman_corr:.4f} | p={spearman_p:.4e}")
diversity_signal = "DIVERSE (rho < 0.85 — good for consensus)" if spearman_corr < 0.85 else "CORRELATED (rho >= 0.85 — limited consensus value)"
print(f"  Diversity signal: {diversity_signal}")

# OOF score sweep (R+P)/2
def score_fn(y_true, y_pred_binary):
    tp = int(((y_true == 1) & (y_pred_binary == 1)).sum())
    fp = int(((y_true == 0) & (y_pred_binary == 1)).sum())
    fn = int(((y_true == 1) & (y_pred_binary == 0)).sum())
    recall    = tp / (tp + fn + 1e-9)
    precision = tp / (tp + fp + 1e-9)
    return (recall + precision) / 2 * 100, recall, precision

sorted_proba = np.sort(oof_proba)[::-1]
best_score = -1.0; best_k = -1; best_t = -1.0; best_r = 0.0; best_p = 0.0

for k in range(50, 300):
    if k > len(sorted_proba):
        break
    t   = float(sorted_proba[k - 1])
    pred = (oof_proba >= t).astype(int)
    s, r, p = score_fn(y, pred)
    if s > best_score:
        best_score = s; best_k = k; best_t = t; best_r = r; best_p = p

print(f"\n  Best OOF K-sweep: K={best_k}, threshold={best_t:.6f}")
print(f"  OOF (R+P)/2: {best_score:.4f} (R={best_r:.4f}, P={best_p:.4f})")
print(f"  Est LB (OOF + 2.67): {best_score + 2.67:.2f}")
print(f"  V4 OOF score: 54.31 | V4 LB: 56.98")

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 5: Save artifacts
# ═══════════════════════════════════════════════════════════════════════════════
print("\n[4/5] Saving artifacts to build_v39/...")

# oof_v39.parquet — schema: CoilID, oof_proba, y
oof_df = pd.DataFrame({
    "CoilID":    coil_ids_train,
    "oof_proba": oof_proba,
    "y":         y,
})
oof_df.to_parquet(V39_DIR / "oof_v39.parquet", index=False)
print(f"  oof_v39.parquet:      {oof_df.shape} | AUC={oof_auc:.4f}")

# test_proba_v39.parquet — schema: CoilID, test_proba
test_df = pd.DataFrame({
    "CoilID":     coil_ids_test,
    "test_proba": test_proba,
})
test_df.to_parquet(V39_DIR / "test_proba_v39.parquet", index=False)
print(f"  test_proba_v39.parquet: {test_df.shape}")

# ── cv_report_v39.md ──────────────────────────────────────────────────────────
cv_report = f"""# V39 CV Report — iter35-equivalent (CoilID + 6 derivatives)

## Summary

| Metric | Value |
|--------|-------|
| OOF AUC | **{oof_auc:.4f}** |
| Mean fold AUC | {mean_fold_auc:.4f} ± {std_fold_auc:.4f} |
| Bootstrap mean AUC | {boot_mean:.4f} |
| Bootstrap 95% CI | [{ci_lower:.4f}, {ci_upper:.4f}] |
| OOF (R+P)/2 best | {best_score:.4f} (K={best_k}) |
| Est LB (OOF+2.67) | {best_score + 2.67:.2f} |
| Ratnesh iter35 OOF AUC (peer) | 0.9412 |
| V4 meta OOF AUC (baseline) | 0.8837 |
| V4 LB (banked) | 56.98 |

## Fold-level AUCs

| Fold | AUC |
|------|-----|
{chr(10).join(f"| {i+1} | {a:.4f} |" for i, a in enumerate(fold_aucs))}
| **Mean** | **{mean_fold_auc:.4f}** |
| **Std** | **{std_fold_auc:.4f}** |

## Diversity vs V4 (consensus merge signal)

| Metric | Value | Signal |
|--------|-------|--------|
| Spearman(V39, V4_meta) | **{spearman_corr:.4f}** (p={spearman_p:.2e}) | {diversity_signal} |

> Target: rho < 0.85 for genuine OOF diversity (independent error signal for consensus union)

## Feature Engineering

- **Total features**: {TOTAL_FEATURES} (51 V4 base + 7 CoilID-derived)
- **V4 base (51)**: SHAP-selected ratios, poly interactions, IsoForest score, neighbor features, prev5_defect_rate
- **CoilID-derived (7)**:
  1. `CoilID` — raw
  2. `CoilID_sq` — squared (quadratic trend)
  3. `CoilID_log` — log(CoilID + 1) (compresses high-ID range)
  4. `CoilID_gt_med` — flag: CoilID > fold-median ({global_median:.1f})
  5. `CoilID_gt_p75` — flag: CoilID > fold-75th-pct ({global_p75:.1f})
  6. `CoilID_sin` — sin(2π × CoilID / {CYCLIC_N}) (cyclic signal)
  7. `CoilID_cos` — cos(2π × CoilID / {CYCLIC_N}) (cyclic signal)
- Threshold flags computed fold-isolated (fold-train CoilID stats only — no leakage)

## Configuration

- scale_pos_weight = {SPW:.2f}
- NO SMOTE, NO BBSE, NO stand-FE
- StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
- LGB: lr=0.03, num_leaves=63, max_depth=6, n_estimators=700

## Top-3 Risks

1. **OOF overfit on cyclic signal**: CoilID cyclic features (sin/cos) are continuous and interpolate perfectly — risk that they capture a chance correlation in 1352 rows (only 66 positives). AUC bump may not generalize to LB.
2. **Temporal leakage via CoilID raw/sq/log**: If LB test coils are from a very different range, CoilID-trend features may degrade. Cyclic features (sin/cos) are safer.
3. **High Spearman with V4 base**: Both paradigms use the same V4 51-feature base; CoilID adds 7 new signals but correlation with V4 meta may still be high, limiting consensus union benefit.

## Consensus-Ready Verdict

| Check | Result |
|-------|--------|
| OOF AUC computed | YES ({oof_auc:.4f}) |
| test_proba saved | YES |
| Spearman vs V4 computed | YES ({spearman_corr:.4f}) |
| rho < 0.85 (diversity) | {'YES' if spearman_corr < 0.85 else 'NO'} |
| est LB > V4 banked (56.98) | {'YES' if best_score + 2.67 > 56.98 else 'NO'} ({best_score + 2.67:.2f}) |

**Ready for consensus union: {'YES' if spearman_corr < 0.85 else 'CONDITIONAL (check rho)'}**
"""

with open(V39_DIR / "cv_report_v39.md", "w") as f:
    f.write(cv_report)
print("  cv_report_v39.md: saved")

# ── approach.md ───────────────────────────────────────────────────────────────
approach_md = f"""# V39 Approach — iter35-equivalent (CoilID + 6 derivatives)

## Lineage

V39 replicates Ratnesh-Jarvis's iter35 paradigm (one of 4 in his 72.71 LB consensus union).

## What iter35 Does

Adds 7 CoilID-derived features to the V4 51-feature base and trains a single LightGBM with
scale_pos_weight=18.9 (no SMOTE, no BBSE):

| Feature | Rationale |
|---------|-----------|
| `CoilID` (raw) | Linear coil-sequence trend |
| `CoilID_sq` | Quadratic — captures non-linear aging/wear |
| `CoilID_log` | Compresses high-ID range, emphasizes early coils |
| `CoilID_gt_med` | Regime split: before/after median (fold-isolated) |
| `CoilID_gt_p75` | Regime split: top-quartile coil-age flag (fold-isolated) |
| `CoilID_sin(2π/1700)` | Cyclic production run pattern |
| `CoilID_cos(2π/1700)` | Cyclic production run pattern (quadrature) |

Threshold flags (gt_med, gt_p75) computed from fold-train CoilID stats only — same
leakage-safe pattern as V33's fold-isolated stand setpoints.

## Why CoilID Might Help

Per V4 discovery: `P(defect | prev=defect) = 0.258` (5.28× lift). CoilID encodes
temporal position in the production sequence — roll wear, thermal drift, and periodic
maintenance cycles all correlate with CoilID. The cyclic sin/cos pair captures any
periodic maintenance schedule with period ≈ 1700 coils.

Ratnesh's iter35 OOF AUC = 0.9412 vs V4's 0.8837. The gap is large — suggests
CoilID features are capturing strong temporal structure.

## Configuration

- scale_pos_weight = {SPW:.2f} (1286/66, pure class-weight balancing)
- 5-fold StratifiedKFold, seed=42 (aligns with V4/V33/V34/V35 for consensus)
- LGB: lr=0.03, leaves=63, depth=6, n_est=700, subsample=0.8, colsample=0.7
- Total features: {TOTAL_FEATURES} (51 V4 + 7 CoilID)

## Role in Consensus Pipeline

V39 = Paradigm 4 candidate for Ratnesh-style 4-paradigm consensus union.
Other paradigms: V4 (meta-stacking), V35 (9-model rank-avg), V37 (AutoGluon).
Diversity target: Spearman(V39, V4_meta) < 0.85.

## Results

- OOF AUC: {oof_auc:.4f}
- Bootstrap 95% CI: [{ci_lower:.4f}, {ci_upper:.4f}]
- Spearman vs V4_meta: {spearman_corr:.4f}
- OOF (R+P)/2: {best_score:.4f} (K={best_k})
- Est LB: {best_score + 2.67:.2f}
"""

with open(V39_DIR / "approach.md", "w") as f:
    f.write(approach_md)
print("  approach.md: saved")

# ── Final summary ─────────────────────────────────────────────────────────────
print("\n" + "=" * 70)
print("V39 COMPLETE — SUMMARY FOR ORCHESTRATOR")
print("=" * 70)
print(f"  OOF AUC              : {oof_auc:.4f}")
print(f"  Bootstrap 95% CI     : [{ci_lower:.4f}, {ci_upper:.4f}]")
print(f"  OOF (R+P)/2          : {best_score:.4f} at K={best_k}")
print(f"  Est LB (OOF+2.67)    : {best_score + 2.67:.2f} vs V4 banked 56.98")
print(f"  Spearman vs V4_meta  : {spearman_corr:.4f} — {diversity_signal}")
print(f"  Ratnesh iter35 (peer): 0.9412 OOF AUC")
print(f"  AUC gap to Ratnesh   : {0.9412 - oof_auc:+.4f}")
print(f"  Fold AUCs            : {[round(a,4) for a in fold_aucs]}")
print("=" * 70)
print(f"\nArtifacts in: {V39_DIR}")
print("  oof_v39.parquet       — CoilID, oof_proba, y")
print("  test_proba_v39.parquet — CoilID, test_proba")
print("  cv_report_v39.md")
print("  approach.md")
print("\nNO LB SUBMISSION. Orchestrator handles consensus merge.")
print("=" * 70)
