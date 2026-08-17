# V46 Approach — V4 Base + Steel-Rolling Physics Features

## TL;DR
Peer Ratnesh's physics features (Zener-Hollomon + Sims + FT coupling + curvature + mono breaks + cooling)
layered on top of V4's 51 SHAP-selected features. Peer jumped from 62 → 77.67 LB with the same architecture.

## Problem Setup
- Binary classification: defect (Y=1) in hot-rolling coils
- Train: 1352 rows, 66 positives (4.88%)
- Test: 339 rows, N_POS=154 (confirmed test positives)
- Score: HE F1 = 200*TP/(K+154)

## Architecture
- Base: LGB + XGB + CatBoost (5-fold StratKFold seed=42, NO SMOTE, scale_pos_weight=19.48)
- Meta: LR + Platt calibration on [oof_lgb, oof_xgb, oof_cat]
- New: 36 physics features appended to base 51 = 87 total

## Physics Features Added (36 total)
1. Zener-Hollomon (11): logZ per stand + aggregates — metallurgical state
2. Sims residuals (7, fold-isolated Y=0-only): how far force deviates from normal process
3. Temp curvature (1): stand-skip / non-linear path detector
4. F/T coupling (9): force normalized by temp per stand
5. Mono breaks (2): count of non-monotonic stand transitions
6. Cooling rates (6): total + per-stage temp drop

## Sims Leak Safety (CRITICAL)
Ridge trained on Y=0 AND fold-train rows ONLY. fold_assign verified aligned with CV loop.

## Results
- Meta OOF AUC: 0.86268 (V4=0.88370, Peer=0.95340)
- Est LB @K=200: 25.42
- Est LB @K=216: 25.41
- V44 banked: 72.83 @K=200
- Peer banked: 77.67 @K=216

## Lineage
V1 → V2 (SMOTE) → V3 (stacking) → V4 (neighbor FE + meta, 0.8837 AUC)
→ V46 (physics features on V4 base, peer's 77.67 recipe)
