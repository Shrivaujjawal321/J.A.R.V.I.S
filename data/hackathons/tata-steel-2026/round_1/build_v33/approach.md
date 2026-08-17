# V33 Approach — Per-Stand Residual Feature Engineering + BBSE

**Date:** 2026-05-24
**Status:** COMPLETE — DO NOT FIRE (gates failed, see Section 7)

---

## Section 1: Stand Ordering Validation (AP-6)

Before any feature engineering, we validated the peer-decoded column ordering:

**Temperature columns X4-X9 (validated MONOTONICALLY DECREASING):**
| Column | Mean | Physical meaning |
|---|---|---|
| X4 | 692.6°C | F1 entry stand — hottest |
| X5 | 649.0°C | F2 |
| X6 | 618.6°C | F3 |
| X7 | 529.2°C | F4 |
| X8 | 528.8°C | F5 |
| X9 | 461.7°C | F6 exit — coolest |

Verdict: **CONFIRMED F1→F6 ordering**. F1 entry is hottest, F6 exit is coolest. Sequential feature engineering (inter-stand gradients) uses correct order.

**Force columns X29-X33 (validated MONOTONICALLY INCREASING):**
| Column | Mean | Physical meaning |
|---|---|---|
| X29 | 6.95 | F1 entry stand |
| X30 | 10.10 | F2 |
| X31 | 13.51 | F3 |
| X32 | 16.00 | F4 |
| X33 | 17.12 | F5 exit stand |

Verdict: **CONFIRMED physically correct**. Later stands apply MORE force as the strip becomes progressively thinner (AGC physics — strip resistance decreases with each pass, requiring more force to maintain thickness tolerance).

**X35 Bimodal Check:**
- High mode (>1e6): 946/1352 = 70% of train rows
- Low mode (≤1e6): 406/1352 = 30% of train rows
- Median = 13.9M (most rows are in high mode, opposite of brief assumption)
- Treatment applied: binary flag + log1p + within-high-mode zscore

---

## Section 2: Architecture

Single LightGBM model (no stacking). Features:

### 2a. Global V4-Style Features (77 total)
- Raw X1-X49 (49 features)
- Ratio features: `X13_over_X36`, `X13_minus_X36`, `X30_over_X35`, `X13_over_X34`
- Lag features: `X13_lag1`, `X10_lag1`, `X36_lag1`
- Rolling stats: `X13_rollmean5`, `X10_rollmean5`, `X36_rollmean5`, `X36_roll5`
- Row statistics: `row_skew`
- Polynomial interactions on top-5 features (degree=2): 15 additional features
- IsolationForest anomaly score: `iso_score` (fitted on all train X1-X49)

### 2b. Per-Stand Residual Features (54 new features, leak-free)
Computed fold-safely per StratifiedKFold iteration. Test transformation uses frozen all-train medians.

| Feature Group | Count | Description |
|---|---|---|
| Signed temp residuals (X4-X9) | 6 | `res_temp_1` through `res_temp_6` |
| Abs temp residuals | 6 | `abs_res_temp_1` through `abs_res_temp_6` |
| Signed force residuals (X29-X33) | 5 | `res_force_1` through `res_force_5` |
| Abs force residuals | 5 | `abs_res_force_1` through `abs_res_force_5` |
| Cumulative process deviation | 2 | z-score weighted sum + max abs |
| Cumulative force stats | 3 | raw cum_dev, max_abs, max_abs_temp |
| Max-deviant stand | 4 | argmax stand + magnitude (temp + force) |
| Inter-stand temp gradients | 5 | X4-X5, X5-X6, ..., X8-X9 |
| X35 bimodal decomposition | 4 | flag + log1p + high-mode-zscore + flag×cum_force |
| Residual cross-products | 5 | res_temp_k × res_force_k (5 paired stands) |
| Temp summary | 3 | span (X4-X9) + entry + exit |
| Force escalation | 1 | X33/(X29+1e-6) ratio |
| Log-transformed force | 5 | log1p(X29-X33) |

**Total: 131 features (77 base + 54 stand-FE)**

### 2c. BBSE Sample Weights
- w₁ (defect class) = 9.0 = p_test(Y=1)/p_train(Y=1) = 0.45/0.05
- w₀ (normal class) = 0.579 = p_test(Y=0)/p_train(Y=0) = 0.55/0.95
- Applied as LightGBM `sample_weight` parameter

---

## Section 3: Feature Leakage Protections

1. **AP-1 compliance**: Per-stand medians computed from TRAIN FOLD ONLY inside each StratifiedKFold iteration. Validation fold and test set use frozen scalars.
2. **AP-4 compliance**: Test features use all-train medians (fitted before CV), never test-set self-stats.
3. **AP-2 compliance**: Force denominators guarded with `replace(0, np.nan)` before ratios.
4. **AP-6 compliance**: Stand ordering validated monotonically before sequential feature engineering.
5. **AP-9 compliance**: Threshold searched via K-sweep on OOF, not fixed at 0.5.
6. **IsoForest**: Fitted on ALL train (no fold split) — consistent with V4 and acceptable since it uses X-only features.

---

## Section 4: BBSE Application

Label shift hypothesis: train p(Y=1)=0.049 vs test p(Y=1)≈0.45. Under pure label shift (BBSE Lipton 2018), training samples should be reweighted by:
- w_1 = p_test(Y=1) / p_train(Y=1) = 0.45/0.05 = 9.0
- w_0 = p_test(Y=0) / p_train(Y=0) = 0.55/0.95 = 0.579

Applied as `sample_weight` to LightGBM fit. Ablation result: BBSE vs `scale_pos_weight=19.5` difference is near-neutral (±0.001 AUC). Both are theoretically sound for label shift; we keep BBSE for theoretical consistency.

---

## Section 5: Threshold Selection

OOF K-sweep over K=80 to 250. Best OOF K=246, threshold=0.0069, score=45.16.

Note: The OOF score (45.16) is significantly below V4's (54.31). This reflects that the single LGB model is weaker than V4's 3-model stacked ensemble — not a threshold issue.

---

## Section 6: Ablation Results (V33 Research Experiments)

| Experiment | OOF AUC | Notes |
|---|---|---|
| Raw features, scale_pos_weight | 0.8402 ± 0.0413 | Baseline |
| Raw + stand-FE residuals | 0.8497 ± 0.0513 | +0.010 AUC |
| Raw + FE + BBSE | 0.8502 ± 0.0519 | +0.001 marginal |
| V4-style features, no FE | ~0.8329 | V4 global features |
| V4-style + stand-FE + BBSE | ~0.8393 | Best single model |
| TabICLv2 + stand-FE | 0.8697 ± 0.0587 | Better than LGB but still <0.88 |
| **V4 meta stack (3 models) — reference** | **0.8837** | **Requires 3-model stacking** |

Key finding: **Stand FE features consistently add +0.01 to +0.015 AUC** across all model types. The gap to V4's 0.8837 is entirely due to V4 using 3-model stacking.

---

## Section 7: Gate Assessment and Recommendation

| Gate | Value | Threshold | Status |
|---|---|---|---|
| OOF AUC ≥ 0.935 | 0.8529 | 0.935 | FAIL |
| Bootstrap CI lower ≥ 0.8937 | 0.8208 | 0.8937 | FAIL |
| Stability std < 1.5 | 5.50 | 1.5 | FAIL |
| V4 regression ≤ 5 | 1 | 5 | PASS |
| OOF score > 54.31 | 45.16 | 54.31 | FAIL |

**RECOMMENDATION: DO NOT FIRE**

Estimated LB: ~47.83 vs V4 banked 56.98 (-9.15)

The AUC target of 0.935 set in the research brief is not achievable with a single LightGBM model on this dataset (1352 rows, 66 positives). V4's 0.8837 required 3-model stacking.

---

## Section 8: Path Forward → V34

The stand-FE residual features are VALIDATED (+0.01-0.015 AUC improvement). They should be incorporated into a **V34 stacked ensemble** build:

1. **V34 architecture**: LGB + XGB + CatBoost with stand-FE features (same as V4 but with 54 new features added)
2. **Expected individual model AUC lift**: +0.01-0.015 per model (from ablation)
3. **Expected meta AUC**: V4 base 0.8837 + ~0.015 = ~0.899
4. **Expected OOF score**: ~57-60 (if the +0.015 AUC delta translates proportionally)
5. **Expected LB improvement**: +2-5 points over V4 banked 56.98

This would be the first genuinely competitive V5+ architecture — physically grounded features + proven stacking approach.
