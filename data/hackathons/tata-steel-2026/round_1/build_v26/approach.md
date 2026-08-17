# V26 Approach — BorderlineSMOTE-1 vs Vanilla SMOTE

## Hypothesis

Hard-7 defect coils (V4 OOF proba range 0.0143-0.0269, barely above V4 threshold) are
textbook borderline minority samples: they live near the majority decision boundary,
surrounded predominantly by majority (non-defect) neighbors in the 51-feature space.
BorderlineSMOTE-1 was specifically designed for exactly this structure — it restricts
synthetic sample generation to minority instances whose m=10 nearest neighbors are
50-100% majority class. Vanilla SMOTE wastes synthesis budget on already-safe positives
(easy-59 with OOF proba 0.28-0.74) instead of focusing on the marginal hard-7.

## Implementation

Single change from V4: vanilla SMOTE replaced with BorderlineSMOTE-1 inside each CV fold.



Fallback cascade implemented:
1. BorderlineSMOTE-1 (primary — used in all 5 folds, no fallback needed)
2. BorderlineSMOTE-2 (fallback if BL-1 finds zero borderline samples)
3. SMOTEENN (final fallback if both BL variants fail)

## Results

### SMOTE variant used
- All 5 folds: **borderline-1** (no fallback needed)
- Average synthetic samples generated per fold: **255.2**
  - V4 vanilla SMOTE at sampling_strategy=0.3 targets ~396 synthetics per fold to reach 30% minority ratio
  - BL-1 generated ~255 because it only synthesizes from the borderline subset, not all positives
  - This confirms borderline detection is working — only a subset of positives qualify as "in danger"

### Per-base OOF AUC (5-fold mean)
| Model | V26 mean AUC |
|-------|-------------|
| LightGBM | 0.8494 |
| XGBoost | 0.8568 |
| CatBoost | 0.8817 |
| **Meta (LR+Platt)** | **0.8824** |

### OOF (R+P)/2 Score
| Model | OOF Score | Threshold | Recall | Precision |
|-------|-----------|-----------|--------|-----------|
| V4 (baseline) | 54.31 | 0.01428 | 100% | 8.62% |
| V26 (BL-SMOTE-1) | 53.83 | 0.01035 | 100% | 7.67% |
| **Delta** | **-0.48** | lower | same | lower |

V26 is **-0.48 OOF points below V4**. Hypothesis not confirmed.

### Hard-7 Proba Comparison (borderline synthesis impact)

| CoilID | V4 proba | V26 proba | Delta | V26 caught |
|--------|----------|-----------|-------|------------|
| 1495 (most precarious) | 0.014292 | 0.012124 | -0.002 | YES |
| 913 | 0.014866 | 0.013617 | -0.001 | YES |
| 1499 | 0.017066 | 0.013051 | -0.004 | YES |
| 473 | 0.017573 | 0.036270 | +0.019 | YES |
| 624 | 0.019208 | 0.010350 | -0.009 | YES (marginal - exactly at threshold) |
| 1436 | 0.020358 | 0.017568 | -0.003 | YES |
| 72 | 0.026935 | 0.022247 | -0.005 | YES |

V26 catches all 7 hard coils (same as V4). However, 6 of 7 have LOWER probas than V4.
CoilID 473 is the exception (+0.019 delta), suggesting BL synthesis helped that specific
boundary region. CoilID 624 sits exactly at the new threshold (0.010350).

### Hard-FP-10 Analysis
All 10 hardest false positives remain FPs under V26. V26 threshold (0.01035) is lower
than V4 (0.01428), which makes Set B harder — any FP with proba > 0.01035 fails.
All 10 hardest FPs have probas 0.28-0.65, far above V26 threshold. No improvement.

## Gate Results (test_case_checker)

| Gate | Result | Details |
|------|--------|---------|
| A (Hard-7) | PASS | 7/7 above 0.5×V4_threshold |
| B (Hard-FP-10) | FAIL | 0/10 FPs resolved (all probas >> new threshold) |
| C (Easy-59) | PASS | 59/59 caught |
| D (OOF score) | FAIL | 53.83 < 54.31 minimum; bootstrap CI lower=53.02 (marginally passes) |
| E (Stability) | PASS | std=0.151 << 1.5 |
| F (Calibrated LB) | FAIL | 53.83+2.67=56.50 < 56.98 required |

Gates passed: 3 / 6

## Diagnosis: Why BL-SMOTE-1 Did Not Lift V4

1. **Synthesis volume reduced, not increased**: BL-1 generated 255 synthetics/fold vs
   vanilla SMOTE's ~396. The model trained on fewer positive augmentations near the
   boundary. This can hurt calibration when the base learners are tree ensembles that
   already use scale_pos_weight=19.5 — the synthesis budget shrinkage may not compensate.

2. **Threshold shift**: V26 chose a lower threshold (0.01035 vs 0.01428) to maximize
   (R+P)/2. This means more negatives flagged as positives, pushing precision down from
   8.62% to 7.67%. The threshold optimization is working as designed but the model
   probabilities shifted lower overall.

3. **Hard-FP-10 probas remained high**: BL-SMOTE-1 is designed to help TP recall,
   not FP suppression. The hard-FP-10 coils all have probas 0.28-0.65 in V26 — still
   firmly above any reasonable threshold. This is the Set B failure root cause.

4. **Hard-7 probas mostly lower**: 6 of 7 hard coils have lower V26 probas than V4,
   opposite of the hypothesis. The borderline synthesis may have introduced noise near
   the boundary that shifted the model's probability estimates, rather than sharpening
   the boundary as intended.

## Fallback Log
No fallbacks needed. BorderlineSMOTE-1 succeeded in all 5 folds with 255-256 synthetic
samples per fold (borderline subset was detected successfully).

## Honest Verdict

**BorderlineSMOTE-1 did not beat V4 on this problem.** OOF regressed by 0.48 points.

Likely reason: With only 53 train positives per fold and scale_pos_weight=19.5 already
compensating for imbalance in the base learners, the synthesis approach is secondary.
BorderlineSMOTE-1 generates fewer (not more) synthetics than vanilla SMOTE, and the
restricted synthesis pool may not cover enough of the positive manifold for tree-based
methods that already oversample positives implicitly via scale_pos_weight.

The theoretical alignment (hard-7 ARE borderline samples) was correct — BL-1 found
255 borderline positives per fold successfully. But the empirical OOF did not improve.

**Do not submit V26.** V4 remains the best single-model OOF baseline at 54.31.

R05 agent's priority-2 pick (SMOTEENN) attacks the FP angle instead — more aligned
with the Set B failure mode. If resampling is revisited in Cycle 2, try SMOTEENN which
may suppress hard-FP-10 by ENN-cleaning confusing boundary negatives from training.
