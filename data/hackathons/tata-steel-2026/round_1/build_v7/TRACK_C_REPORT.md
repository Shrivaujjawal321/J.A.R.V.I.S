# Track C — Anomaly Detection Report

## 1. Headline
**Exhausted — supervised framing was correct (ensemble 52.8 approx V5 53.7)**

## 2. Per-Method Results

| Method | AUC | OOF (R+P)/2 | Top Features |
|--------|-----|-------------|--------------|
| M1_IF | 0.7899 | 53.09 | X39, poly_X13_over_X36_X14, v5_ratio_X16_div_X14 |
| M2_OCSVM | 0.6039 | 52.44 | — |
| M3_LOF | 0.5679 | 52.63 | — |
| M4_Mah | 0.7636 | 52.84 | — |
| M5_AE | 0.7284 | 52.95 | — |
| M6_PCA | 0.6952 | 53.04 | X13_rollmean5, X13_over_X36, poly_X13_over_X36_X16 |
| 7-way LR Ensemble | 0.8674 | 52.82 | — |
| V5 Supervised | 0.8886 | 53.68 | — |

## 3. Ensemble + Predicted LB

- V5 standalone OOF: **53.68**
- Best single AD: **53.09** (M1_IF)
- 7-way LR ensemble OOF: **52.82**
- V4 calibration delta: +2.67
- **Predicted LB: 55.49**

## 4. Hard-Defect Recovery

Hard defects = 15 Y=1 rows with lowest V5 meta proba.
**Verdict: PARTIAL_LIFT**  —  2/15 hard defects caught (>=1 AD in top 5%)

| CoilID | V5 Proba | IF% | OCSVM% | LOF% | Mah% | AE% | PCA% | Caught? |
|--------|----------|-----|--------|------|------|-----|------|---------|
| 72 | 0.02217 | 39 | 11 | 63 | 50 | 44 | 37 | no |
| 473 | 0.02694 | 51 | 27 | 30 | 68 | 80 | 56 | no |
| 1499 | 0.02829 | 21 | 23 | 71 | 76 | 61 | 55 | no |
| 1436 | 0.03068 | 34 | 6 | 49 | 48 | 54 | 32 | no |
| 913 | 0.03336 | 38 | 70 | 78 | 82 | 95 | 94 | no |
| 708 | 0.03990 | 44 | 0 | 33 | 22 | 58 | 45 | no |
| 709 | 0.04319 | 54 | 1 | 22 | 14 | 54 | 50 | no |
| 1495 | 0.04382 | 40 | 7 | 64 | 43 | 29 | 20 | no |
| 624 | 0.04465 | 61 | 58 | 98 | 84 | 80 | 82 | YES(LOF) |
| 1153 | 0.04982 | 91 | 99 | 90 | 97 | 99 | 97 | YES(OCSVM,Mah,AE,PCA) |
| 778 | 0.05111 | 47 | 9 | 50 | 49 | 73 | 66 | no |
| 814 | 0.06922 | 93 | 78 | 38 | 58 | 40 | 53 | no |
| 722 | 0.07870 | 85 | 88 | 67 | 92 | 94 | 91 | no |
| 86 | 0.08032 | 52 | 35 | 40 | 72 | 50 | 27 | no |
| 258 | 0.08233 | 76 | 42 | 11 | 31 | 18 | 26 | no |

## 5. Recommendation

Add best AD scores as V8 features for +0.5-1pp lift.

---
_2026-05-23_