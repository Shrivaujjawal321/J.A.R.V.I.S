# V64a CV Report — V35 recipe (9-model) on ENRICHED train

## Fold Strategy
- 5-fold StratifiedKFold on ORIGINAL 1352 train rows only
- Injected rows (134) always in TRAIN fold, never in val
- OOF metric: original 1352 rows only (clean, no injection contamination)
- StandSetpoints.fit: orig train fold rows only

## Results

| Metric | Value |
|--------|-------|
| OOF AUC | **0.7298** |
| OOF F1@K=200 | **0.2105** (gate >0.391) |
| OOF (R+P)/2 best | **33.59** at K=285 |
| Avg fold std | 0.0675 |
| Spearman vs V44 | 0.1806 |
| TPs in top-200 | 72/72 = 100.0% |
| Est LB conservative | **35.09** |
| Gates passed | 1/5 |

## Per-model OOF AUCs
| Model | OOF AUC | Fold Std |
|-------|---------|---------|
| LGB1 | 0.7055 | 0.0685 |
| LGB2 | 0.6900 | 0.0718 |
| XGB1 | 0.7240 | 0.0671 |
| XGB2 | 0.7428 | 0.0706 |
| CatBoost | 0.7264 | 0.0487 |
| RF | 0.7487 | 0.0684 |
| ET | 0.7368 | 0.0757 |
| HGB | 0.7029 | 0.0714 |
| LGB3 | 0.7004 | 0.0650 |

## Gates
- [FAIL] Gate 1: OOF F1@K=200 > 0.391: 0.2105
- [PASS] Gate 2: TP coverage ≥ 97%: 72/72 = 100.0%
- [FAIL] Gate 3: Fold std < 0.05: 0.0675
- [FAIL] Gate 4: Spearman in [0.70,0.90]: ρ=0.1806
- [FAIL] Gate 5: Calibrated LB > 76: 35.09

## Unlabeled top-200 (candidate TPs)
14, 15, 35, 54, 96, 112, 121, 153, 156, 160, 161, 162, 171, 176, 197, 215, 217, 239, 240, 246, 257, 264, 274, 275, 282, 297, 302, 361, 376, 404, 411, 457, 459, 462, 477, 485, 500, 511, 528, 532, 622, 631, 639, 654, 670, 682, 683, 691, 693, 694, 730, 732, 747, 759, 770, 776, 802, 803, 804, 806, 822, 826, 829, 835, 853, 857, 883, 902, 919, 933, 940, 958, 972, 994, 1022, 1023, 1025, 1063, 1073, 1088, 1090, 1091, 1097, 1100, 1111, 1117, 1118, 1137, 1138, 1183, 1184, 1187, 1189, 1209, 1233, 1266, 1304, 1346, 1347, 1392, 1412, 1425, 1434, 1453, 1492, 1494, 1498, 1540, 1589
