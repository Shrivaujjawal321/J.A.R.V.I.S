# V41 Approach — BBSE-Reweighted LightGBM

## TL;DR
BBSE (Black-Box Shift Estimation) sample-weight paradigm on V4's 51 features.
iter37-equivalent per Ratnesh-Jarvis peer intel.
Standalone LB ≈ 56. Value = ranking diversity in consensus union.

## Problem Setup
- Binary classification: defect (Y=1) in hot-rolling coils
- Train: 1352 rows, 66 positives (4.88%)
- Test: 339 rows, expected ~45% positive (→ w1=9.0, w0=0.579)
- Score: (Recall + Precision) / 2 × 100

## BBSE Paradigm
Dataset shift: train prevalence ≠ test prevalence. BBSE corrects by
reweighting each training sample to match the test distribution:
  w(x) = p_test(y) / p_train(y)
  w1 = 0.45 / 0.05 = 9.00  (Y=1 samples get 9x weight)
  w0 = 0.55 / 0.95 = 0.5789  (Y=0 samples get 0.58x weight)

This is different from scale_pos_weight which only corrects class imbalance
without modeling the test prevalence explicitly.

## Key Differences vs V4 (same features, different paradigm)
| Dimension        | V4 (meta-stack)          | V41 (BBSE)                  |
|-----------------|--------------------------|------------------------------|
| Model           | LGB + XGB + CatBoost + LR meta | Single LightGBM         |
| Rebalancing     | SMOTE inside folds       | BBSE sample_weight           |
| scale_pos_weight| ≈ 19.5 (class ratio)     | 1.0 (neutral)                |
| Calibration     | Platt scaling            | None (raw BBSE proba)        |
| Feature set     | 51 SHAP-selected         | Same 51 SHAP-selected        |

## Results
- OOF AUC: 0.86126
- Bootstrap 95% CI: [0.81169, 0.90294]
- Best OOF (R+P)/2: 52.46%
- Calibrated LB est: 55.13
- Spearman vs V4: 0.8199
- Spearman vs V35: 0.8930

## Lineage
V1 → V2 (SMOTE) → V3 (stacking) → V4 (neighbor FE + meta, OOF AUC 0.8837)
V33 (stand-FE) → V35 (9-model rank-avg) → V37 (AutoGluon) → V41 (BBSE paradigm)

## Consensus Union Role
V41's value is NOT its standalone score. It is the Spearman < 0.85 diversity
it brings to the consensus union. Ratnesh used BBSE+9-model consensus to
reach LB 72 — the diversity of BBSE rankings was part of that signal.

## Next Step
Feed oof_v41.parquet + test_proba_v41.parquet into consensus union alongside
V35/V33/V37. The consensus orchestrator picks K=170 positives from the
blended rank-average.
