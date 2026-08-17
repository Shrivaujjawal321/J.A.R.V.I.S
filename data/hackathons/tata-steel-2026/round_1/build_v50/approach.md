# V50 Approach — Pure-Physics Base (no raw temp/force in model)

## TL;DR
V46 failed (AUC regressed 0.8837 → 0.8627) because raw temp/force cols were still in the V4 base,
making physics features collinear. V50 drops the raw cols first, then adds physics.
This mirrors peer's iter52 design (0.9534 OOF, 77.67 LB).

## The Collinearity Problem
V4 features include: X6, X7, X9 (raw temps), X30 (raw force), X30_over_X35 (force ratio).
V46 added: logZ_i = f(X4..X9), ft_coupling_i = X29_i/T_K_i.
→ logZ highly correlated with X6/X7/X9 already in base → redundant dimension → trees wasted splits.

## V50 Fix
Drop from final model input: X4,X5,X6,X7,X8,X9,X29,X30,X31,X32,X33,X30_over_X35
Keep for physics FE only (compute from, but exclude from model).
Result: V4 clean base = 46 features + 36 physics = 82 total features.

## Feature Engineering Pipeline
1. Load V4 parquet (has all raw cols available for FE)
2. Compute static physics: Zener-Hollomon(11) + temp_curvature(1) + FT_coupling(9) + mono_breaks(2) + cooling_rates(6) = 29
3. Compute fold-isolated Sims residuals: Ridge(Y=0 train-fold rows) per stand = 7
4. DROP raw cols from final feature matrix → 82 features enter the model

## Architecture
LGB+XGB+CatBoost (5-fold StratKFold seed=42, NO SMOTE, scale_pos_weight=19.48) → LR meta + Platt cal

## Results
- Meta OOF AUC: 0.86848
- V4 reference: 0.88370 | Delta: -0.01522
- V46 regressed: 0.86268 | Delta vs V46: +0.00580
- Peer iter52: 0.95340
- Est LB @K=200: 24.86
- Est LB @K=216: 24.86
- V44 banked: 72.83 | Peer banked: 77.67
