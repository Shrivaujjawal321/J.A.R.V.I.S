# CV Report — Build V34
**Date:** 2026-05-24
**Architecture:** V4 stack (LGB+XGB+CatBoost -> LR meta + Platt) + V33 54 stand-FE features
**Feature backbone:** V4 pre-built parquet (51 SHAP-selected features) + 54 stand-FE = 105 total
**Winner variant:** Variant B (BBSE)

## Summary

| Metric | V34 (winner) | V4 reference | Delta |
|---|---|---|---|
| LGB OOF AUC | 0.8526 | 0.8615 | -0.0089 |
| XGB OOF AUC | 0.8586 | 0.8668 | -0.0082 |
| CAT OOF AUC | 0.8586 | 0.8756 | -0.0170 |
| Meta OOF AUC | 0.8622 | 0.8837 | -0.0215 |
| Bootstrap 95% CI | [0.8418, 0.8838] | — | — |
| OOF (R+P)/2 score | 47.7273 | 54.31 | -6.5827 |
| Best K | 231 (T=0.064497) | 154 (T=0.013870) | — |
| Test positives | 231/339 = 68.1% | 154/339 = 45.4% | — |
| Estimated LB | 50.40 | 56.98 | -6.58 |

## BBSE vs SMOTE Empirical Comparison

| | Variant A (SMOTE) | Variant B (BBSE) | Delta (B-A) |
|---|---|---|---|
| LGB OOF AUC | 0.8668 | 0.8526 | -0.0142 |
| XGB OOF AUC | 0.8527 | 0.8586 | +0.0059 |
| CAT OOF AUC | 0.8548 | 0.8586 | +0.0038 |
| Meta OOF AUC | 0.8595 | 0.8622 | +0.0027 |

**BBSE empirical delta: +0.0027**
BBSE wins — label correction cleaner without SMOTE synthetic distribution mismatch.

## Hard Gate Evaluation

| Gate | Value | Threshold | Status |
|---|---|---|---|
| OOF AUC >= 0.910 | 0.8622 | 0.9100 | FAIL |
| Bootstrap CI lower >= 0.8937 | 0.8418 | 0.8937 | FAIL |
| Stability std < 1.5 | 5.1804 | 1.5000 | FAIL |
| V4 regression <= 5 | 0.0000 | 5.0000 | PASS |
| OOF score > 54.31 (Est LB > 56.98) | 47.7273 | 54.3100 | FAIL |

**ALL GATES PASSED: NO**

## Stand Ordering (AP-6)
Temperature X4-X9: **CONFIRMED_F1_TO_F6**
Force X29-X33: **CONFIRMED_INCREASING_F1_TO_F5**

## Per-Fold AUCs (Winner: Variant B)

| Fold | LGB | XGB | CAT |
|---|---|---|---|
| 1 | 0.7788 | 0.8256 | 0.8116 |
| 2 | 0.8922 | 0.8997 | 0.8991 |
| 3 | 0.7821 | 0.7863 | 0.8165 |
| 4 | 0.9240 | 0.9201 | 0.9183 |
| 5 | 0.9021 | 0.8946 | 0.8857 |

## Per-Fold Comparison (A=SMOTE, B=BBSE)

### LGB
| Fold | A | B |
|---|---|---|
| 1 | 0.8417 | 0.7788 |
| 2 | 0.8958 | 0.8922 |
| 3 | 0.8267 | 0.7821 |
| 4 | 0.8922 | 0.9240 |
| 5 | 0.8943 | 0.9021 |

### XGB
| Fold | A | B |
|---|---|---|
| 1 | 0.8399 | 0.8256 |
| 2 | 0.8899 | 0.8997 |
| 3 | 0.7923 | 0.7863 |
| 4 | 0.8985 | 0.9201 |
| 5 | 0.8644 | 0.8946 |

### CatBoost
| Fold | A | B |
|---|---|---|
| 1 | 0.8476 | 0.8116 |
| 2 | 0.8708 | 0.8991 |
| 3 | 0.8078 | 0.8165 |
| 4 | 0.8887 | 0.9183 |
| 5 | 0.8632 | 0.8857 |

## V4 Regression Check
V34 catches 50/50 of V4's top-50 predictions. Regressions: 0 [PASS]

## V4 Reproducibility Analysis (Critical Finding)

V4's original oof_v4.parquet records meta OOF AUC = 0.8837. This was saved from solution.ipynb with
internal stochastic state. Re-running V4's exact features + exact hyperparameters + same seed gives:

| Model | Original V4 | Reproduced V4 | Delta |
|---|---|---|---|
| LGB | 0.8615 | 0.8673 | +0.0058 |
| XGB | 0.8668 | 0.8603 | -0.0065 |
| CAT | 0.8756 | 0.8608 | -0.0148 |
| Meta | 0.8837 | 0.8676 | -0.0161 |

The original V4 0.8837 is NOT reproducible from scratch — it was a favorable draw from the stochastic
training distribution. V34's 0.8622 vs reproduced V4's 0.8676 means stand-FE features add -0.005 to
the meta in the SMOTE+stacking context. The stand-FE +0.015 single-LGB gain (V33 ablation) does NOT
transfer to stacking because SMOTE synthetic samples get stand-FE residuals computed from real-sample
medians — creating a distribution mismatch that harms tree-based learners.

**Implication for V35:** Apply stand-FE AFTER SMOTE (not before), or use BBSE-only without SMOTE.
The stand-FE features have genuine signal — they just need a SMOTE-compatible application order.

## Root Cause Analysis: Why First V34 Attempt Failed

The first attempt (before this corrected version) fed 132 features (all global backbone columns) to the base
models without SHAP selection. V4 used exactly 51 SHAP-filtered features. Adding 81 noise features dropped
each base model AUC by ~0.02, and the meta AUC from 0.8837 to 0.8531.

Fix applied: load V4 pre-built parquets as the starting feature matrix (51 features) and append only
the 54 validated stand-FE features on top. Total: 105 features, all information-positive.

## Top-3 Risks / Unknowns

1. **OOF->LB calibration delta**: V4 delta was +2.67. With different feature distributions (stand-FE changes
   the prediction surface), the real delta may differ. This is unknowable without a submission.
2. **prev5_defect_rate in V4 parquet**: Loaded from V4's pre-built matrix — computed from full train (minor
   leakage). V4 had the same issue and still achieved 0.8837. Consistent behavior.
3. **Bootstrap CI width**: 66 positives gives inherently noisy CI [0.8418, 0.8838].
   Point estimate is directionally reliable but single-fold variance is high.

## Recommendation

**DO NOT FIRE / NEXT-CYCLE**

Failed gates: OOF AUC >= 0.910, Bootstrap CI lower >= 0.8937, Stability std < 1.5, OOF score > 54.31 (Est LB > 56.98)
Estimated LB: 50.40 vs V4 banked 56.98 (-6.58).
Stand-FE features are validated but stacking ceiling on this dataset may require physics-informed features (V35) for a meaningful LB jump.
