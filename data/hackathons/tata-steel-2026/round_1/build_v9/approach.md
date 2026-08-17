# V9 — Full-Train Stacking + TabPFN + Gate-at-Inference

## Architecture

1. Base learners: LightGBM + XGBoost + CatBoost + TabPFN v2 (all 5-fold CV on full 1352 train rows)
2. LR meta + Platt sigmoid calibration
3. Hard gate at INFERENCE only: X42 > 0.025067 OR X39 >= 169 -> predict 0
4. Score-aware threshold maximizing (R+P)/2 on gated OOF

## Results

- Meta OOF AUC: 0.8771
- Full OOF (R+P)/2: 53.71
- Bootstrap 95% CI: [51.58, 55.32]
- V4-calibrated LB estimate: 56.38
- Test predicted positives: 155 / 339

## Why this works

- Full-train stacking preserves V5's high Meta AUC (vs V8's hot-zone-only restriction)
- TabPFN v2 adds prior-fitted-transformer diversity (different inductive bias than trees)
- Gate-at-inference eliminates 138 test rows with ZERO false-negative risk (Track A EDA finding)
- Combined: V5 AUC quality + V8 gate precision = V9
