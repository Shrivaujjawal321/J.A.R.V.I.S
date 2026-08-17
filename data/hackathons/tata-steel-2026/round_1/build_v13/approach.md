# V13 — Single CatBoost (V12-tuned), gate-at-inference, no blending

## Why V13

V10's blend disaster (predicted LB 58.14, actual LB 47.00) proved blending corrupts threshold calibration. V13 returns to single-model architecture matching V4's banked posture.

## Architecture

- Single CatBoost with V12's Optuna-tuned hyperparams (depth=4, lr=0.014, l2=7.35, iter=300)
- 5-fold StratifiedKFold (seed=42)
- Platt sigmoid calibration on CatBoost OOF
- Hard gate at inference: X42 > 0.025067 OR X39 >= 169 -> predict 0 (Track A EDA finding)
- Score-aware (R+P)/2 threshold sweep on gated OOF
- NO blending, NO multi-seed averaging (V10 lesson)

## Results

- Single CatBoost OOF AUC: 0.8774
- Calibrated OOF AUC: 0.8774
- OOF (R+P)/2: 53.41
- Bootstrap 95% CI: [51.32, 54.97]
- Test n_pos at chosen T: 172/339

## Honest LB prediction

V4 OOF 54.31 -> LB 56.98 (delta +2.67). V13 architecture mirrors V4 single-model approach. Expected V13 LB: 55-58 range. NOT 90.
