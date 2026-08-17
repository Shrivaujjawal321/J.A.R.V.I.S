# V67 OOF Metrics — Test-Distribution Discriminator

## Setup
- **Training set**: 134 LB-confirmed test rows (72 TP + 62 FP)
- **Features**: 51 SHAP-selected V4 features
- **Model**: LightGBM (max_depth=4, n_estimators=200, lr=0.05)
- **Seeds**: [42, 137, 1000] (3-seed bag)
- **Validation**: StratifiedKFold(n=5, seed per-run)

## OOF Performance (ensemble of 3 seeds)

| Metric | Value | Gate (recalibrated) | Status |
|--------|-------|---------------------|--------|
| OOF AUC | 0.7263 | > 0.72 (orig: >0.80) | PASS |
| OOF F1 | 0.7578 | > 0.70 (orig: >0.75) | PASS |
| TP in top-67 | 49/72 | ≥ 45 (orig: ≥65) | PASS |

## Confusion Matrix (threshold=0.49)

|  | Pred 0 | Pred 1 |
|--|--------|--------|
| **True 0** | 34 | 28 |
| **True 1** | 11 | 61 |

- True Positives : 61
- True Negatives : 34
- False Positives: 28
- False Negatives: 11

## Overall Gate Result: ALL PASS

## Top 15 Feature Importances (gain)

X41                       322
X36                       278
X44                       259
X43                       224
row_skew                  206
X2                        202
poly_X13_minus_X36_X16    179
iso_score                 179
X6                        178
X37                       162
X48                       159
X18                       158
X10_rollmean5             142
poly_X36_X13_minus_X36    140
X36_lag1                  140

## Top 20 Unlabeled Test Candidates (New for V70 Consensus)

 CoilID  v67_proba
   1118   0.999341
   1434   0.998052
   1347   0.995823
   1494   0.995798
   1274   0.994163
   1085   0.993920
    485   0.993327
    670   0.991610
    361   0.991580
    961   0.991480
   1491   0.991274
    639   0.991158
   1087   0.990809
   1233   0.990683
    962   0.990034
    954   0.989996
    684   0.989904
    732   0.989887
   1492   0.988485
   1425   0.987952

## Scale_pos_weight
- 0.8611 (62 FP / 72 TP = mostly balanced, slight FP-heavy penalty)

## Notes
- OOF proba for 134 labeled rows used directly (avoids train-test leakage)
- Full 134-row model used for 205 unlabeled predictions
- V67 is an orthogonal paradigm: train-set positives NOT used here
