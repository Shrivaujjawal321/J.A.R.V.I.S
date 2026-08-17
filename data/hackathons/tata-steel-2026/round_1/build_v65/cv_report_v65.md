# CV Report — Build V65
**Date:** 2026-05-26
**Architecture:** LightGBM 3-seed ensemble + V4 51-feature base + 13 rank-proximity features = 64 total
**Key Innovation:** 72 LB-confirmed test TPs added to defect prototype pool (138 total)

## Summary

| Metric | Value |
|---|---|
| Architecture | LightGBM 3-seed ensemble (seeds: [42, 137, 1000]) |
| Feature set | V4 51 + 13 rank-proximity = 64 features |
| Proximity space | L1 in rank-percentile [0,1] per column |
| Prototype pool | 66 train Y=1 + 72 test TPs = 138 total |
| Proximity radii | [0.05, 0.1, 0.15, 0.2, 0.3] |
| CV | StratifiedKFold(5, seed=42) |
| OOF AUC | 0.8724 |
| Per-fold mean AUC | 0.8703 ± 0.0452 |
| Bootstrap 95% CI | [0.8540, 0.8948] |
| OOF (R+P)/2 @K=200 | 47.3561 |
| V4 baseline @K=200 | 46.3500 |
| Delta vs V4 | +1.0061 |
| Best K (sweep) | 162 |
| Best OOF (R+P)/2 | 49.0460 |
| Est LB @K=200 | 50.03 |
| Banked LB (V44 K200) | 72.83 |
| Proximity importance | 66.9% of total |
| Train pos in top-200 | 47/66 |

## Validation Gates

| Gate | Criterion | Value | Result |
|---|---|---|---|
| G1 | OOF (R+P)/2@K=200 > 46.35 | 47.3561 | PASS |
| G2 | OOF AUC > 0.85 | 0.8724 | PASS |
| G3 | Per-fold std AUC < 0.05 | 0.0452 | PASS |
| G4 | Train pos in top-200 >= 60 | 47/66 | FAIL |
| **ALL** | All 4 pass | — | **FAIL** |

## Per-Fold CV Results (mean across seeds)

| Fold | Mean AUC |
|---|---|
| 1 | 0.9484 |
| 2 | 0.8745 |
| 3 | 0.8136 |
| 4 | 0.8744 |
| 5 | 0.8406 |
**Mean: 0.8703 | Std: 0.0452**

## Per-Seed Per-Fold AUC Detail

| Seed | Fold | AUC |
|---|---|---|
| 42 | 1 | 0.9475 |
| 42 | 2 | 0.8702 |
| 42 | 3 | 0.8054 |
| 42 | 4 | 0.8878 |
| 42 | 5 | 0.8557 |
| 137 | 1 | 0.9484 |
| 137 | 2 | 0.8749 |
| 137 | 3 | 0.8069 |
| 137 | 4 | 0.8659 |
| 137 | 5 | 0.8354 |
| 1000 | 1 | 0.9493 |
| 1000 | 2 | 0.8783 |
| 1000 | 3 | 0.8285 |
| 1000 | 4 | 0.8695 |
| 1000 | 5 | 0.8306 |


## Spearman vs Other Paradigms

| Paradigm | Spearman r | Diversity |
|---|---|---|
| V4 | 0.0696 | DIVERSE |
| V40 | 0.8694 | MODERATE |

## Proximity Features — Importance

Proximity features account for **66.9%** of total LightGBM feature importance.
Threshold for "signal present": > 2% (per V65 falsification criterion).

## Estimated LB

| K | OOF (R+P)/2 | Calibrated LB est |
|---|---|---|
| 154 | (see output above) | OOF@154 + 2.67 |
| 200 | 47.3561 | 50.03 |
| best | 49.0460 @K=162 | 51.72 |

**Note:** 2.67 calibration delta was established on V4 stacked ensemble OOF→LB.
Single-paradigm OOF may have different delta. Use as rough estimate.

## New Test CoilIDs (not in V44 K=200)

Top-10 V65 candidates not already banked by V44: `[np.int64(2), np.int64(515), np.int64(474), np.int64(934), np.int64(1676), np.int64(229), np.int64(1477), np.int64(539), np.int64(1210), np.int64(692)]`

These are prime LB-probe targets if V65 is submitted.
