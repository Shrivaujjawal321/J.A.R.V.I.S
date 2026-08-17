# V57 Adversarial Classifier Report

**Date:** 2026-05-25
**Purpose:** Diagnose train→test distribution shift before applying density-ratio weights.
**Reference:** Lipton/Sugiyama ICML 2018, Uber arxiv:2004.03045

---

## Adversarial AUC

| Metric | Value |
|--------|-------|
| **Overall OOF AUC** | **0.5509** |
| Fold 1 AUC | 0.5571 |
| Fold 2 AUC | 0.5644 |
| Fold 3 AUC | 0.6248 |
| Fold 4 AUC | 0.4791 |
| Fold 5 AUC | 0.5405 |
| Fold std | 0.0467 |

**Interpretation:** WEAK/NO shift — density-ratio correction may not help

- AUC = 0.50 → distributions identical, no shift
- AUC = 0.60 → detectable shift, mild correction motivated
- AUC = 0.70 → significant shift, density-ratio correction justified (Uber threshold)
- AUC > 0.80 → extreme shift, feature dropping also recommended

---

## Density-Ratio Weight Statistics

| Statistic | Value |
|-----------|-------|
| DR min (before clip) | 0.0154 |
| DR max (before clip) | 5.5606 |
| DR mean (before clip) | 0.5870 |
| Clip range | [0.1, 10.0] |
| Rows clipped low | 122 |
| Rows clipped high | 0 |
| DR mean (after clip+norm) | 1.0000 |
| DR mean for positives (y=1) | 0.8274 |
| DR mean for negatives (y=0) | 1.0089 |

Interpretation: If pos_DR_mean > neg_DR_mean, positive (defect) train rows look more like
test data → the model sees more "test-like" defects, which is the correct signal for a
test set with ~45% prevalence.

---

## Top-20 Shifted Features

These features most reliably distinguish train samples from test samples.
High importance = feature distribution differs most between train and test.

| Rank | Feature | Adversarial Importance |
|------|---------|----------------------|
| 1 | X36_roll5 | 206.0 |
| 2 | iso_score | 130.0 |
| 3 | X36_lag1 | 95.0 |
| 4 | X23 | 91.0 |
| 5 | X13_rollmean5 | 91.0 |
| 6 | X9 | 90.0 |
| 7 | X27 | 85.0 |
| 8 | X7 | 82.0 |
| 9 | X48 | 80.0 |
| 10 | X41 | 80.0 |
| 11 | X49 | 79.0 |
| 12 | X43 | 79.0 |
| 13 | X2 | 77.0 |
| 14 | X10_rollmean5 | 76.0 |
| 15 | X44 | 71.0 |
| 16 | X6 | 61.0 |
| 17 | row_skew | 60.0 |
| 18 | poly_X13_minus_X36_X16 | 59.0 |
| 19 | X13_lag1 | 58.0 |
| 20 | X14 | 56.0 |

---

## BBSE Label-Shift Estimate

| Parameter | Value |
|-----------|-------|
| Train prevalence q_train | 0.0488 |
| BBSE estimated test prevalence q_test | 0.0156 |
| q_test / q_train ratio | 0.32x |
| E[p̂|Y=1] train | 0.1132 |
| E[p̂|Y=0] train | 0.0456 |
| E[p̂] test | 0.0466 |

Expected test prevalence under label shift hypothesis: ~0.45
BBSE estimate of 0.0156 SUGGESTS LOWER-THAN-EXPECTED label shift.

---

## Conclusion

Adversarial AUC of 0.5509 suggests moderate covariate shift.
Density-ratio reweighting applied to V57 base models.
BBSE label-shift correction computed but not used (raw wins at K=200).
