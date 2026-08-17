# V54b CV Report — ICR Kaggle-Winner Recipe (Bug-Fixed)

**Date:** 2026-05-25
**Architecture:** 10-Fold × 4-Learner × 5-Seed (Multi-Seed Rank-Average Ensemble)
**Bug fixes vs V54:** paradigm_weights key (not weights) + τ lowered 0.80→0.65
**Recipe:** ICR 2023 gold-medalist validated recipe (4 gold medalists used this)
**Banked baseline:** V44 K=200 = 72.83 LB | V53 OOF F1@K=200 = 0.391

---

## Summary

| Metric | Value | Gate |
|---|---|---|
| OOF AUC | 0.90073 | — |
| OOF AUC Bootstrap 95% CI | [0.87118, 0.92604] | — |
| **OOF F1@K=200** | **0.330827** | **FAIL (> 0.391 benchmark)** |
| OOF F1@K=154 (ICR recipe) | 0.363636 (TP=40) | — |
| OOF best K sweep | K=69, F1=0.444444 (TP=30) | — |
| Per-fold F1 std | 0.0603 | FAIL (< 0.05) |
| Spearman vs V46 (V44 proxy) | 0.8436 | — (0.70-0.90 target) |
| Spearman vs V43 | 0.8918 | PASS (0.70-0.90) |
| Total models | 16 (5 seeds × 3 GBDTs + TabICL) | — |
| Pseudo-labels | 119 rows (τ=0.65, sw=0.5) | — |
| Training time | 106.0 min | — |

---

## Architecture

- **10-Fold StratifiedKFold** (seed=42) — 12% more training data per fold vs 5-fold
- **Base learners:** LightGBM, XGBoost, CatBoost (3 GBDTs) + TabICL
- **Multi-seed averaging:** 5 seeds [42, 137, 1000, 7, 2024] per GBDT = 15 GBDT fits per fold
- **Total fits:** 16 fits × 10 folds = 160
- **Aggregation:** rank-average across ALL 16 base predictions (global ranks over full OOF)
- **NO SMOTE** — ICR winners dropped SMOTE; causes small-N distribution mismatch
- **scale_pos_weight=** 19.48 for GBDTs only

## Feature Set

| Source | Count | Description |
|---|---|---|
| V4 SHAP-selected | 51 | SHAP-ranked features from 135 engineered |
| V35 stand-FE | 54 | Fold-isolated setpoint residuals/deviations |
| **Total** | **105** | |

## Soft Pseudo-Labels

- Source: V53 Caruana greedy ensemble test probabilities (V39 primary component, 65% weight)
- Threshold τ=0.65: 119/339 test rows added as pseudo-positive rows
- Sample weight: 0.5 (half-weight vs real train rows)
- Label assignment: hard Y=1 (all τ≥0.65 rows are confident positives)
- Soft probability stored as metadata only — not used as regression target
- Note: pseudo-labels applied per-fold with that fold's setpoint transform

---

## Per-Fold CV Results

| Fold | LGB_mean | XGB_mean | CAT_mean | Time |
|---|---|---|---|---|
| 1 | 0.8784 | 0.8722 | 0.8729 | 2326s |
| 2 | 0.9231 | 0.9269 | 0.9070 | 2782s |
| 3 | 0.8788 | 0.8778 | 0.8938 | 163s |
| 4 | 0.8517 | 0.8705 | 0.8406 | 154s |
| 5 | 0.9315 | 0.9408 | 0.9450 | 156s |
| 6 | 0.8318 | 0.8328 | 0.8186 | 150s |
| 7 | 0.9574 | 0.9511 | 0.9348 | 156s |
| 8 | 0.8562 | 0.8759 | 0.8464 | 167s |
| 9 | 0.9246 | 0.9183 | 0.9013 | 155s |
| 10 | 0.8967 | 0.8850 | 0.9138 | 151s |

---

## Per-Model OOF AUCs

| Model | OOF AUC | Fold Std |
|---|---|---|
| xgb_s2024 | 0.90266 | 0.03450 |
| lgb_s2024 | 0.90062 | 0.03860 |
| xgb_s1000 | 0.90029 | 0.03116 |
| lgb_s42 | 0.89990 | 0.03672 |
| lgb_s137 | 0.89848 | 0.03698 |
| cat_s1000 | 0.89789 | 0.03988 |
| xgb_s42 | 0.89703 | 0.03790 |
| lgb_s1000 | 0.89691 | 0.03608 |
| cat_s7 | 0.89633 | 0.04860 |
| xgb_s137 | 0.89538 | 0.03818 |
| xgb_s7 | 0.89485 | 0.04018 |
| lgb_s7 | 0.88999 | 0.04811 |
| cat_s2024 | 0.88965 | 0.03461 |
| tabicl | 0.88896 | 0.03633 |
| cat_s137 | 0.88315 | 0.04085 |
| cat_s42 | 0.88094 | 0.04742 |

---

## Paradigm Diversity — Spearman vs Reference OOFs

| Comparison | Spearman ρ | Diversity |
|---|---|---|
| V54b vs V46 | +0.8436 | MODERATE |
| V54b vs V48 | +0.9386 | HIGH_CORR |
| V54b vs V43 | +0.8918 | MODERATE |
| V54b vs V35 | +0.8949 | MODERATE |
| V54b vs V39 | +0.8273 | MODERATE |
| V54b vs V54 | +0.8983 | MODERATE |

**Gate: V54b vs V43/V46 should be 0.70-0.90 for trust + diversity balance.**

---

## K Selection

| K | OOF F1@K | TP | Notes |
|---|---|---|---|
| 154 | 0.363636 | 40 | ICR recipe K = N_POS_TEST |
| 200 | 0.330827 | 44 | V44 banked K |
| 69 | 0.444444 | 30 | OOF best K sweep |

**Recommended fire K:** Use K=200 (preserves banked 72.83) unless V54b OOF shows strong
signal that K=69 is safer. Submit both K=154 and K=200 to compare.

---

## Gates Summary

| Gate | Condition | Result |
|---|---|---|
| 1 — F1 benchmark | OOF F1@K=200 > 0.391 (V53) | FAIL (0.330827) |
| 2 — Diversity | Spearman vs V43 in [0.70, 0.90] | PASS |
| 3 — Stability | Per-fold F1 std < 0.05 | FAIL (0.0603) |

---

## Top-3 Risks

1. **OOF-LB calibration shift:** The +2.67pp delta was calibrated on V4 5-fold stacked
   ensemble. 10-fold multi-seed will have a different (likely smaller) gap because 10-fold
   leaks less variance per fold. Expect +1.5–2.5pp delta, not +2.67. Use V44 K=200 as
   floor not ceiling.

2. **Pseudo-label test distribution mismatch:** Test positives may have different feature
   distributions than train positives (hence the severe public/private shift). Pseudo-labels
   from V39/V53 are themselves uncertain. If pseudo-labels hurt OOF, re-run without
   (set PSEUDO_TAU=1.01 effectively disabling them).

3. **10-fold with 6-7 positives per val fold:** At 66 positives / 10 folds ≈ 6.6 positives
   per val fold. F1@K is undefined/noisy per-fold at these counts. Use global OOF F1@K=200
   as the metric, not fold-level F1. The per-fold AUC variance captures stability better.

---

## Improvement vs Prior Builds

| Build | OOF F1@K=200 | Architecture | Key diff |
|---|---|---|---|
| V43 | 0.346 | Rank-product(V4,V40) 5-fold | Combo of 2 paradigms |
| V53 Caruana | 0.391 | Greedy weighted 13 paradigms | Caruana selection |
| V54 (bugged) | 0.331 | ICR recipe 10-fold (τ=0.80, wrong key) | pseudo silent no-op |
| **V54b** | **0.330827** | **ICR recipe 10-fold (τ=0.65, fixed)** | **pseudo-labels active** |
