# CV Report — Build V33
**Date:** 2026-05-24
**Architecture:** LightGBM (single model) + V4 global features + per-stand residual FE + BBSE

## Summary

| Metric | Value |
|---|---|
| Architecture | LightGBM single model |
| CV | RepeatedStratifiedKFold(5×3 = 15) |
| OOF AUC (mean ± std) | 0.8529 ± 0.0550 |
| First-repeat OOF AUC | 0.8444 |
| Bootstrap 95% CI | [0.8208, 0.8693] |
| OOF (R+P)/2 score | 45.1589 |
| Best K | 246 |
| Test positives | 246/339 = 72.6% |
| Raw features | 77 |
| Stand-FE features added | 54 |
| Total features | 131 |
| AUC vs V4 meta (0.8837) | -0.0308 |
| Estimated LB | 47.83 |
| V4 banked LB | 56.98 |
| Beat V4 | NO |

## Stand Ordering Validation (AP-6)

Temperature X4-X9: **CONFIRMED_F1_TO_F6**
- X4=692.6°C, X5=649.0°C, X6=618.6°C, X7=529.2°C, X8=528.8°C, X9=461.7°C
- Monotonically decreasing ✓ — F1 entry hottest → F6 exit coolest

Force X29-X33: **CONFIRMED_INCREASING_F1_TO_F5**
- X29=6.95, X30=10.10, X31=13.51, X32=16.00, X33=17.12
- Monotonically increasing ✓ — physically correct for finishing mill (later stands compress thinner strip harder)

## Hard Gate Evaluation

| Gate | Value | Threshold | Status |
|---|---|---|---|
| OOF AUC ≥ 0.935 | 0.8529 | 0.9350 | FAIL |
| Bootstrap CI lower ≥ 0.8937 | 0.8208 | 0.8937 | FAIL |
| Stability std < 1.5 | 5.5025 | 1.5000 | FAIL |
| V4 regression ≤ 5 | 1.0000 | 5.0000 | PASS |
| OOF score > 54.31 (→ Est LB > 56.98) | 45.1589 | 54.3100 | FAIL |

**ALL GATES PASSED: NO**

## Per-Fold AUC (15 folds)

| Fold | AUC |
|---|---|
| 1 | 0.7925 |
| 2 | 0.8688 |
| 3 | 0.7312 |
| 4 | 0.9198 |
| 5 | 0.9105 |
| 6 | 0.9335 |
| 7 | 0.8366 |
| 8 | 0.8902 |
| 9 | 0.8399 |
| 10 | 0.7809 |
| 11 | 0.8399 |
| 12 | 0.9047 |
| 13 | 0.8123 |
| 14 | 0.8830 |
| 15 | 0.8497 |
**Mean: 0.8529 | Std: 0.0550 | Min: 0.7312 | Max: 0.9335**

## Key Findings from Ablation (V33 Research)

1. **Stand FE features add +0.015 AUC** over raw features alone (confirmed via 5-fold CV ablation)
2. **BBSE vs scale_pos_weight**: near-neutral (±0.001) — BBSE preferred for theoretical correctness but not game-changing
3. **Single LGB ceiling on this dataset**: ~0.84-0.85 AUC. V4's 0.8837 came from 3-model stacking.
4. **TabPFN v2**: requires interactive license acceptance — unavailable in non-interactive environment
5. **TabICLv2**: 0.8697 AUC — similar to LGB, not a breakthrough
6. **V4 feature reproduction**: without `prev5_defect_rate` (target-encoded temporal lag), ~0.01 AUC penalty
7. **X35 bimodal**: 70% of train is in high mode (>1e6), 30% in low — not as bimodal as brief assumed

## BBSE Reweighting

- w₁ (defect class): 9.0 = p_test(Y=1)/p_train(Y=1) = 0.45/0.05
- w₀ (normal class): 0.579 = p_test(Y=0)/p_train(Y=0) = 0.55/0.95
- Applied as sample_weight to LightGBM

## V4 Regression Check

- Top-50 V4 confident predictions: V33 catches 49/50
- Regressions: 1 | Gate (≤5): PASS

## Top-3 Risks

1. **AUC gap**: Required 0.935 for gate pass. Single LGB gets 0.8529. Root cause: V4 used 3-model stacking; single model can't match.
2. **BBSE threshold calibration**: OOF-derived threshold may not hold on LB (V27/V31/V32 lesson: OOF thresholds don't translate).
3. **Small minority class variance**: 66 positives → bootstrap CI width 0.0485. High fold-to-fold variance is inherent.

## Recommendation

**DO NOT FIRE — RE-RESEARCH NEEDED**

Failed gates: OOF AUC ≥ 0.935, Bootstrap CI lower ≥ 0.8937, Stability std < 1.5, OOF score > 54.31 (→ Est LB > 56.98)

**Estimated LB: 47.83 vs V4 banked 56.98 (-9.15)**

To beat V4, the correct path is:
1. Rebuild 3-model stack (LGB+XGB+CatBoost) WITH the new stand-FE features — this should add +0.01-0.02 to individual model AUCs vs V4 baseline
2. The stacking meta will then push total to ~0.89-0.90 vs V4's 0.8837
3. Estimated improvement: +0.5 to +2 LB points if stacking benefits stack

V33 single-model stand-FE features are validated (+0.015 AUC). They should be incorporated into a V34 stacked ensemble build.
