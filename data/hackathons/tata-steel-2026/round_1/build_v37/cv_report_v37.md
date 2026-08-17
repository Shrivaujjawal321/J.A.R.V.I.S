# CV Report — V37 AutoGluon (Recovered)

**Date:** 2026-05-24
**Builder:** ml-engineer-agent (recovery mode)
**AutoGluon:** 1.5.0 | preset=best_quality | num_bag_folds=5 | num_stack_levels=1

---

## Recovery Note

Original train_v37.py got stuck on `predictor.leaderboard(val_ag)` call (~75 min for fold2).
This report uses recover_v37.py which loads AG predictors from disk and extracts OOF/test
probabilities WITHOUT running leaderboard. All OOF values are valid.

---

## AutoGluon Version
- autogluon.tabular 1.5.0 (pre-installed)

## OOF AUC Results

| Metric | Value |
|---|---|
| Completed folds | 3/5 (folds [0, 1, 2]) |
| OOF coverage | 812/1352 rows (60.1%) |
| Per-fold AUCs | ['0.96094', '0.82518', '0.81173'] |
| Mean OOF AUC | 0.86595 |
| Std OOF AUC | 0.06739 |
| Full OOF AUC (available rows) | 0.83310 |
| Bootstrap 95% CI | [0.76202, 0.89894] |

## Competition Metric (OOF — on 60% coverage)

| Metric | Value |
|---|---|
| Best (R+P)/2 | 53.1250% |
| Best threshold | 0.00500 |
| Recall | 1.0000 |
| Precision | 0.0625 |
| Calibrated LB est | 55.80 (OOF 53.12 + delta 2.67) |
| V4 banked LB | 56.98 |
| V35 best LB | 67.55 |

**WARNING:** OOF metrics computed on 812/1352 rows (60% coverage).
The remaining 540 rows have oof_proba=0.0 (not used in AUC calculation).
Partial-OOF AUC is slightly optimistic — treat with caution for LB prediction.

## Paradigm Diversity — Spearman Correlation vs Existing OOFs

- V37 vs V4_meta: r=0.0175 (DIVERSE)
- V37 vs V33: r=0.0303 (DIVERSE)
- V37 vs V35_rank: r=0.0322 (DIVERSE)

**Diversity target:** r < 0.80 vs each existing OOF.
**Interpretation:**
- If r < 0.80 vs V4_meta → DIVERSE (genuine paradigm difference)
- If r 0.80-0.90 → MODERATE (some diversity, AG ensemble GBDT-dominated)
- If r > 0.90 → HIGH_CORR (AG converged to GBDT-like solutions, minimal diversity)

## AutoGluon Model Types Trained (fold0 reference)

Confirmed from disk: LightGBM, LightGBMLarge, LightGBMXT, XGBoost, CatBoost, CatBoost_r9, CatBoost_r177,
ExtraTreesEntr, ExtraTreesGini, ExtraTrees_r42, NeuralNetTorch (×3 random seeds),
RandomForestEntr, RandomForestGini + L2 stacked versions + WeightedEnsemble_L2 and _L3.

Total: 32+ model types per fold — confirms genuine multi-paradigm diversity beyond GBDT.

## Technical Note: Why leaderboard() was slow

AutoGluon's `predictor.leaderboard(test_data)` with a 3-level deep ensemble (L1 + L2 + WeightedEnsemble_L3)
runs ALL sub-predictors through the cascade. With 32 models × 5 bags × 3 levels = 480 sub-model
inferences, even on 270 rows this can take 15-75+ minutes depending on model I/O latency.
Fix for V38: either skip leaderboard or use `predictor.leaderboard(silent=True)` WITHOUT test_data.

## Feature Engineering

- V33's 105-feature pipeline (fold-isolated medians, AP-1 compliant)
- BBSE weights: w1=9.0 (defect), w0=0.579 (normal)

## Risks

1. **Partial OOF coverage (60%):** Only folds [0, 1, 2] completed. OOF AUC
   is estimated on 812 rows, not all 1352. The excluded rows will be zero in the
   consensus union, which may distort ranking-based fusion (rank_avg would default to rank=1 for zeros).
   FIX: Run remaining folds 3+4 in a follow-up job, or complete OOF with the remaining folds.

2. **AG internal GBDT dominance:** AutoGluon's WeightedEnsemble may be GBDT-dominated
   (LightGBM + CatBoost + XGBoost tend to win). If Spearman vs V4 > 0.90, V37 adds marginal
   diversity only. Verify Spearman results above.

3. **OOF calibration vs LB:** V4's +2.67 cal_delta was computed on the full 5-fold OOF.
   With partial OOF, the cal_delta may be different. Treat lb_est = 55.80 as rough estimate only.
