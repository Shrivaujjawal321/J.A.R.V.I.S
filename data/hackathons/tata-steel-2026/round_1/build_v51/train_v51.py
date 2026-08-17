#!/usr/bin/env python3
"""
V51 — TabICLv2 Standalone Paradigm (2-seed ensemble)
=====================================================

Goal: Introduce a FUNDAMENTALLY DIFFERENT model family vs the GBDT consensus stack.
      All V4/V33/V34/V35/V39/V40/V41/V43/V46/V48/V50 are GBDT or GBDT-derived combos.
      TabICLv2 is a transformer-based in-context learning model — different inductive bias.

Architecture:
  - TabICLClassifier(n_estimators=16, random_state=42)   → seed42 OOF probas
  - TabICLClassifier(n_estimators=16, random_state=123)  → seed123 OOF probas
  - V51 OOF = rank-average of two seeds (per R10 recipe)
  - No SMOTE, no BBSE — TabICLv2 handles imbalance internally

Features:
  - V4's 51 SHAP-selected features (the proven feature set, no engineered physics)
  - Loaded from build_v4/train_v4.parquet (already pre-processed)

CV:
  - 5-fold StratifiedKFold seed=42 (matches all other paradigms for consensus alignment)

TabICL version: 2.1.1 (installed)
  Previous V35 usage: n_estimators=5, random_state=42 — single seed, fewer estimators
  V51 improvement: n_estimators=16 (3.2x more column shuffles), 2-seed diversity ensemble

Gates:
  - OOF AUC >= 0.86 (V35 baseline)
  - Spearman vs V4 OOF < 0.90 (genuine diversity)
"""

import json
import time
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import rankdata, spearmanr
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold

from tabicl import TabICLClassifier

warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────────────────────────────────────
# Paths
# ─────────────────────────────────────────────────────────────────────────────
ROOT = Path("/home/ujjwal/Documents/J.A.R.V.I.S./data/hackathons/tata-steel-2026/round_1")
OUT  = ROOT / "build_v51"
OUT.mkdir(exist_ok=True)

print("=" * 70)
print("V51 — TabICLv2 Standalone Paradigm (seed42 + seed123 rank-avg)")
print("tabicl version: 2.1.1 | n_estimators=16 | 5-fold StratifiedKFold seed=42")
print("=" * 70)

# ─────────────────────────────────────────────────────────────────────────────
# 1. Load data — V4's 51 features
# ─────────────────────────────────────────────────────────────────────────────
print("\n[1] Loading data from V4 feature set...")
t0 = time.time()

train_df = pd.read_parquet(ROOT / "build_v4/train_v4.parquet")
test_df  = pd.read_parquet(ROOT / "build_v4/test_v4.parquet")

# Load 51-feature list from V4's final feature JSON
with open(ROOT / "build_v4/v4_final_features.json") as f:
    feat_meta = json.load(f)
FEATURES = feat_meta["features"]  # exactly 51 features

coil_ids_train = train_df["CoilID"].tolist()
coil_ids_test  = test_df["CoilID"].tolist()
Y = train_df["Y"].astype(int).values

X_train = train_df[FEATURES].values.astype(np.float32)
X_test  = test_df[FEATURES].values.astype(np.float32)

n_pos = Y.sum()
n_neg = (Y == 0).sum()
print(f"  Train: {len(Y)} rows | Y=1: {n_pos} | Y=0: {n_neg} | ratio: {n_neg/n_pos:.2f}")
print(f"  Test:  {len(coil_ids_test)} rows")
print(f"  Features: {len(FEATURES)} (V4 51-feature base)")
print(f"  Data load time: {time.time()-t0:.1f}s")

# ─────────────────────────────────────────────────────────────────────────────
# 2. 5-fold StratifiedKFold — run BOTH seeds in each fold
# ─────────────────────────────────────────────────────────────────────────────
print("\n[2] Running 5-fold CV (seed42 + seed123 per fold)...")

SKF = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

oof_seed42  = np.zeros(len(Y), dtype=np.float64)
oof_seed123 = np.zeros(len(Y), dtype=np.float64)

fold_aucs_42  = []
fold_aucs_123 = []
fold_times    = []

for fold, (trn_idx, val_idx) in enumerate(SKF.split(X_train, Y)):
    t_fold = time.time()
    X_trn, X_val = X_train[trn_idx], X_train[val_idx]
    y_trn, y_val = Y[trn_idx], Y[val_idx]

    n_pos_trn = y_trn.sum()
    n_pos_val = y_val.sum()

    print(f"\n  Fold {fold+1}/5 | train_pos={n_pos_trn} | val_pos={n_pos_val}")

    # Seed 42
    t1 = time.time()
    clf42 = TabICLClassifier(n_estimators=16, random_state=42)
    clf42.fit(X_trn, y_trn)
    proba42 = clf42.predict_proba(X_val)[:, 1]
    oof_seed42[val_idx] = proba42
    auc42 = roc_auc_score(y_val, proba42)
    fold_aucs_42.append(auc42)
    print(f"    seed42:  AUC={auc42:.5f} | fit+pred: {time.time()-t1:.1f}s")

    # Seed 123
    t2 = time.time()
    clf123 = TabICLClassifier(n_estimators=16, random_state=123)
    clf123.fit(X_trn, y_trn)
    proba123 = clf123.predict_proba(X_val)[:, 1]
    oof_seed123[val_idx] = proba123
    auc123 = roc_auc_score(y_val, proba123)
    fold_aucs_123.append(auc123)
    print(f"    seed123: AUC={auc123:.5f} | fit+pred: {time.time()-t2:.1f}s")

    fold_t = time.time() - t_fold
    fold_times.append(fold_t)
    print(f"    Fold total: {fold_t:.1f}s")

# ─────────────────────────────────────────────────────────────────────────────
# 3. V51 OOF = rank-average of two seeds
# ─────────────────────────────────────────────────────────────────────────────
print("\n[3] Computing V51 OOF = rank-average(seed42, seed123)...")

# Rank-average: rank within each seed, average the ranks, re-rank, normalize
rank42  = rankdata(oof_seed42)   / len(Y)
rank123 = rankdata(oof_seed123)  / len(Y)
oof_v51 = (rank42 + rank123) / 2.0

auc_seed42_global  = roc_auc_score(Y, oof_seed42)
auc_seed123_global = roc_auc_score(Y, oof_seed123)
auc_v51            = roc_auc_score(Y, oof_v51)

print(f"  seed42  OOF AUC: {auc_seed42_global:.5f}")
print(f"  seed123 OOF AUC: {auc_seed123_global:.5f}")
print(f"  V51 rank-avg AUC: {auc_v51:.5f}")
print(f"  Per-fold AUC (seed42):  {[f'{a:.5f}' for a in fold_aucs_42]}")
print(f"  Per-fold AUC (seed123): {[f'{a:.5f}' for a in fold_aucs_123]}")

# Bootstrap CI
rng = np.random.default_rng(42)
boot_aucs = []
for _ in range(1000):
    idx = rng.choice(len(Y), size=len(Y), replace=True)
    if Y[idx].sum() < 2:
        continue
    boot_aucs.append(roc_auc_score(Y[idx], oof_v51[idx]))
ci_lo, ci_hi = np.percentile(boot_aucs, [2.5, 97.5])
print(f"  Bootstrap 95% CI: [{ci_lo:.5f}, {ci_hi:.5f}]")

# ─────────────────────────────────────────────────────────────────────────────
# 4. Diversity check — Spearman vs other paradigms
# ─────────────────────────────────────────────────────────────────────────────
print("\n[4] Diversity check — Spearman vs other paradigms...")

def load_oof_col(path, col):
    df = pd.read_parquet(path)
    return df.set_index("CoilID")[col].reindex(coil_ids_train).values

# V4 OOF (positionally aligned, no CoilID)
oof_v4 = pd.read_parquet(ROOT / "build_v4/oof_v4.parquet")
v4_meta = oof_v4["oof_meta"].values

# Other paradigms
paradigms = {
    "v4_meta":       v4_meta,
    "v35_rank_avg":  load_oof_col(ROOT / "build_v35/oof_v35.parquet",  "rank_avg_proba"),
    "v40_proba":     load_oof_col(ROOT / "build_v40/oof_v40.parquet",  "oof_proba"),
    "v41_proba":     load_oof_col(ROOT / "build_v41/oof_v41.parquet",  "oof_proba"),
    "v43_proba":     load_oof_col(ROOT / "build_v43/oof_v43.parquet",  "oof_proba"),
}

# Add V48 and V50 if present
for vname, fname, col in [
    ("v48_proba", "build_v48/oof_v48.parquet", "oof_proba"),
    ("v50_proba", "build_v50/oof_v50.parquet", "oof_proba"),
]:
    p = ROOT / fname
    if p.exists():
        try:
            paradigms[vname] = load_oof_col(p, col)
        except Exception as e:
            print(f"  Warning: could not load {vname}: {e}")

spearman_results = {}
print(f"  {'Paradigm':<20} {'Spearman vs V51':<20} {'Verdict'}")
print(f"  {'-'*55}")
for name, col in paradigms.items():
    s, pval = spearmanr(oof_v51, col)
    spearman_results[name] = float(s)
    if abs(s) < 0.85:
        verdict = "STRONG DIVERSITY"
    elif abs(s) < 0.90:
        verdict = "GOOD DIVERSITY"
    elif abs(s) < 0.95:
        verdict = "MODERATE"
    else:
        verdict = "HIGH CORR - WARNING"
    print(f"  {name:<20} ρ={s:+.5f}            {verdict}")

# Seed-to-seed diversity
s_seeds, _ = spearmanr(oof_seed42, oof_seed123)
print(f"\n  seed42 vs seed123: ρ={s_seeds:+.5f} (internal diversity)")

# V35 TabICL for direct comparison (same model, weaker config)
oof_v35 = pd.read_parquet(ROOT / "build_v35/oof_v35.parquet")
v35_tabicl = oof_v35.set_index("CoilID")["proba_TabICL"].reindex(coil_ids_train).values
s_v35tabicl, _ = spearmanr(oof_v51, v35_tabicl)
auc_v35tabicl  = roc_auc_score(Y, v35_tabicl)
print(f"\n  V35-TabICL (n_est=5, seed42) AUC: {auc_v35tabicl:.5f}")
print(f"  V51 vs V35-TabICL: ρ={s_v35tabicl:+.5f} (expected high — same model family)")
print(f"  V51 AUC lift over V35-TabICL: +{(auc_v51 - auc_v35tabicl)*100:.3f}pp")

# ─────────────────────────────────────────────────────────────────────────────
# 5. Test predictions — full retrain on all train data, both seeds
# ─────────────────────────────────────────────────────────────────────────────
print("\n[5] Building test predictions (full retrain on all train rows)...")

t_test = time.time()

clf42_full = TabICLClassifier(n_estimators=16, random_state=42)
clf42_full.fit(X_train, Y)
test_proba42 = clf42_full.predict_proba(X_test)[:, 1]
print(f"  seed42 full retrain: {time.time()-t_test:.1f}s")

t_test2 = time.time()
clf123_full = TabICLClassifier(n_estimators=16, random_state=123)
clf123_full.fit(X_train, Y)
test_proba123 = clf123_full.predict_proba(X_test)[:, 1]
print(f"  seed123 full retrain: {time.time()-t_test2:.1f}s")

# Rank-average test probabilities
test_rank42  = rankdata(test_proba42)  / len(test_proba42)
test_rank123 = rankdata(test_proba123) / len(test_proba123)
test_proba_v51 = (test_rank42 + test_rank123) / 2.0

print(f"  Test proba range: [{test_proba_v51.min():.6f}, {test_proba_v51.max():.6f}]")
print(f"  Test proba top 10: {sorted(test_proba_v51, reverse=True)[:10]}")

# ─────────────────────────────────────────────────────────────────────────────
# 6. Gate checks
# ─────────────────────────────────────────────────────────────────────────────
print("\n[6] Gate checks...")

v35_auc = float(roc_auc_score(Y, paradigms["v35_rank_avg"]))
gate_auc = auc_v51 >= 0.860
gate_diversity = abs(spearman_results.get("v4_meta", 1.0)) < 0.90

print(f"  Gate 1 — OOF AUC >= 0.860:  {'PASS' if gate_auc else 'FAIL'} ({auc_v51:.5f})")
print(f"  Gate 2 — Spearman vs V4 < 0.90: {'PASS' if gate_diversity else 'FAIL'} (ρ={spearman_results.get('v4_meta', 99):.5f})")

all_gates = gate_auc and gate_diversity
print(f"\n  Overall: {'ALL GATES PASS — ready for V52 consensus' if all_gates else 'GATE FAILURES — review before consensus'}")

# ─────────────────────────────────────────────────────────────────────────────
# 7. Save outputs
# ─────────────────────────────────────────────────────────────────────────────
print("\n[7] Saving outputs...")

# OOF
oof_df = pd.DataFrame({
    "CoilID":    coil_ids_train,
    "oof_proba": oof_v51,          # rank-avg of seed42 + seed123
    "oof_seed42":  oof_seed42,
    "oof_seed123": oof_seed123,
    "y":         Y,
})
oof_df.to_parquet(OUT / "oof_v51.parquet", index=False)
print(f"  Saved oof_v51.parquet (shape={oof_df.shape})")

# Test
test_df_out = pd.DataFrame({
    "CoilID":    coil_ids_test,
    "test_proba": test_proba_v51,
    "test_proba_seed42":  test_proba42,
    "test_proba_seed123": test_proba123,
})
test_df_out.to_parquet(OUT / "test_proba_v51.parquet", index=False)
print(f"  Saved test_proba_v51.parquet (shape={test_df_out.shape})")

# ─────────────────────────────────────────────────────────────────────────────
# 8. CV Report
# ─────────────────────────────────────────────────────────────────────────────
total_time = sum(fold_times) + (time.time() - t0)

fold_avg_42  = float(np.mean(fold_aucs_42))
fold_std_42  = float(np.std(fold_aucs_42))
fold_avg_123 = float(np.mean(fold_aucs_123))
fold_std_123 = float(np.std(fold_aucs_123))

report = f"""# V51 CV Report — TabICLv2 Standalone Paradigm (2-seed ensemble)

## Architecture
- Model: TabICLClassifier (tabicl 2.1.1) — transformer-based in-context learning
- Seed 42: n_estimators=16, random_state=42
- Seed 123: n_estimators=16, random_state=123
- V51 = rank-average of seed42 + seed123 OOF probabilities
- Features: V4's 51 SHAP-selected features (no engineered physics)
- CV: 5-fold StratifiedKFold seed=42 (identical to GBDT stack for consensus alignment)
- No SMOTE, no BBSE — TabICLv2 handles imbalance via internal column shuffles

## OOF AUC Results
| Model | OOF AUC |
|-------|---------|
| V51 rank-avg (seed42+123) | **{auc_v51:.5f}** |
| V51 seed42 | {auc_seed42_global:.5f} |
| V51 seed123 | {auc_seed123_global:.5f} |
| V35-TabICL (n_est=5, baseline) | {auc_v35tabicl:.5f} |
| V4 meta (GBDT best) | {roc_auc_score(Y, v4_meta):.5f} |

Bootstrap 95% CI: [{ci_lo:.5f}, {ci_hi:.5f}]
Gate threshold (V35 AUC): {v35_auc:.5f}
Gate 1 (AUC >= 0.860): **{'PASS' if gate_auc else 'FAIL'}**

## Per-Fold AUCs
| Fold | seed42 | seed123 |
|------|--------|---------|
{chr(10).join(f'| {i+1} | {a42:.5f} | {a123:.5f} |' for i, (a42, a123) in enumerate(zip(fold_aucs_42, fold_aucs_123)))}
| Mean | {fold_avg_42:.5f} | {fold_avg_123:.5f} |
| Std  | {fold_std_42:.5f} | {fold_std_123:.5f} |

## Diversity vs GBDT Stack
| Paradigm | Spearman vs V51 | Verdict |
|----------|----------------|---------|
{chr(10).join(f'| {name} | ρ={s:+.5f} | {"STRONG DIVERSITY" if abs(s) < 0.85 else ("GOOD DIVERSITY" if abs(s) < 0.90 else ("MODERATE" if abs(s) < 0.95 else "HIGH CORR"))} |' for name, s in spearman_results.items())}
| V35-TabICL (n_est=5) | ρ={s_v35tabicl:+.5f} | Expected high (same model family) |

**Gate 2 (Spearman vs V4 < 0.90): {'PASS' if gate_diversity else 'FAIL'}** (ρ={spearman_results.get('v4_meta', 99):.5f})

Internal seed diversity (seed42 vs seed123): ρ={s_seeds:+.5f}

## V51 vs V35-TabICL Comparison
- V35 used: n_estimators=5, single seed (42), part of 9-model rank-avg ensemble
- V51 uses: n_estimators=16 (3.2x more), 2-seed ensemble, standalone paradigm
- V51 AUC lift: +{(auc_v51 - auc_v35tabicl)*100:.3f}pp over V35-TabICL alone

## Compute
- Total wall time: {total_time:.0f}s (~{total_time/60:.1f} min)
- Per-fold mean: {np.mean(fold_times):.0f}s
- Hardware: CPU only (TabICLv2 CPU mode, 1352 train rows × 51 features)

## Gates Summary
- Gate 1 (OOF AUC >= 0.860): **{'PASS' if gate_auc else 'FAIL'}** — {auc_v51:.5f}
- Gate 2 (Spearman vs V4 < 0.90): **{'PASS' if gate_diversity else 'FAIL'}** — ρ={spearman_results.get('v4_meta', 99):.5f}
- **Ready for V52 consensus: {'YES' if all_gates else 'NO — review gates above'}**

## Risks
1. TabICLv2 probabilities are not calibrated — treat as ranking signal in consensus, not raw probability
2. OOF AUC CI [{ci_lo:.5f}, {ci_hi:.5f}] wide due to only 66 positives in 1352 rows
3. TabICLv2 is a CPU-only model here; ensemble with GBDT stack is the intended use (not solo submission)
4. V51 vs V35-TabICL Spearman {s_v35tabicl:.3f} — as expected, high within-family correlation; diversity gain comes from vs GBDT members
"""

with open(OUT / "cv_report_v51.md", "w") as f:
    f.write(report)
print("  Saved cv_report_v51.md")

# ─────────────────────────────────────────────────────────────────────────────
# 9. Approach doc (brief)
# ─────────────────────────────────────────────────────────────────────────────
approach = f"""# V51 Approach — TabICLv2 Standalone Paradigm

## Motivation
After 10+ GBDT variants (V4, V33-V50), all paradigms share the same inductive bias
(gradient-boosted decision trees). Even with diverse hyperparameters, they form a
consensus ceiling around 72-73 LB because they fail in the same ways.

TabICLv2 is a transformer-based in-context learning model: it treats training data as
context and makes predictions via attention over that context. It has a fundamentally
different failure mode from GBDTs — it can capture global dependencies and complex
interactions that decision trees miss, but is weaker on local monotone relationships
that GBDTs excel at.

## Config
- Model: TabICLClassifier (tabicl 2.1.1)
- n_estimators=16: each estimator shuffles column order differently, providing ensemble
  diversity within a single TabICL fit
- Seed ensemble: seed42 + seed123 → rank-average (additional diversity from different
  random column shuffle orderings)
- Features: V4's 51 SHAP-selected features — stable, proven, no physics guesses
- CV: same 5-fold StratifiedKFold seed=42 as all GBDT models (proper consensus alignment)

## V35 vs V51
V35 included TabICLClassifier(n_estimators=5, seed=42) as one of 9 models in a rank-avg.
V51 makes TabICL the primary paradigm with a proper 2-seed ensemble and higher n_estimators.

## Expected Role in Consensus
V51 is designed to be a NEW COLUMN in the consensus matrix (V52 or later).
Ensemble with V4/V40/V43 via rank-average should provide +1.5-3 LB lift if
Spearman vs GBDT stack is < 0.90.

## OOF AUC
{auc_v51:.5f} (rank-avg of 2 seeds)
Gate vs V35 baseline (0.860): {'PASS' if gate_auc else 'FAIL'}
Diversity vs V4 (want < 0.90): ρ={spearman_results.get('v4_meta', 99):.5f} → {'PASS' if gate_diversity else 'FAIL'}
"""

with open(OUT / "approach.md", "w") as f:
    f.write(approach)
print("  Saved approach.md")

# ─────────────────────────────────────────────────────────────────────────────
# Final summary
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "=" * 70)
print("V51 COMPLETE")
print("=" * 70)
print(f"Architecture:    TabICLv2 rank-avg (seed42 + seed123, n_est=16)")
print(f"OOF AUC:         {auc_v51:.5f}")
print(f"Bootstrap CI:    [{ci_lo:.5f}, {ci_hi:.5f}]")
print(f"Spearman vs V4:  ρ={spearman_results.get('v4_meta', 99):.5f}")
print(f"Gate 1 (AUC):    {'PASS' if gate_auc else 'FAIL'}")
print(f"Gate 2 (Diversity): {'PASS' if gate_diversity else 'FAIL'}")
print(f"Total compute:   {total_time:.0f}s")
print(f"Outputs: {OUT}")
print(f"  oof_v51.parquet")
print(f"  test_proba_v51.parquet")
print(f"  cv_report_v51.md")
print(f"  approach.md")
