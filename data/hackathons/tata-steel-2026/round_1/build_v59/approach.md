# V59 Approach — OpenFE Auto-Feature Engineering

## Motivation

V4 base uses 51 hand-crafted SHAP-selected + 54 stand-FE = 105 features.
X1-X49 are anonymous — domain knowledge is limited. OpenFE's genetic
algorithm explores non-obvious combinations (X1*log(X3), X4/X9, etc.)
that human hand-crafting misses. Literature estimate: +1-5 LB on this
problem profile.

## Architecture

1. **OpenFE stage1**: Generates ~2000+ candidate feature expressions
   from X1-X49 using successive feature-wise halving (mRMR-like fast filter)
2. **OpenFE stage2**: SHAP-ranked importance on a held-out LGB model selects
   top-50 features by gain importance
3. **CV-safe**: OpenFE.fit() called inside each fold on tr_idx rows only —
   prevents val/test rows leaking into feature construction
4. **Base models**: LGB + XGB + CatBoost (V4 architecture, identical params)
5. **Meta**: LR + Platt calibration on OOF stack
6. **Aggregation**: rank-average of meta + 3 base models

## Feature Space

- 51 V4 SHAP-selected features
- 54 stand-FE (fold-isolated setpoint residuals)
- 50 OpenFE auto-features
- Total: 155 features

## CV Safety

- `OpenFE.fit()` called on `tr_idx` rows only per fold
- `openfe_transform()` applies fold's features to `val_idx`
- Test inference: `ofe_full` (fit on all-train) transforms test set
- Stand-FE setpoints: fit on `tr_idx` per fold (no leakage)

## Banked Baseline

V44 K=200 = 72.83 LB. V59 does NOT break V44 — it augments the feature
set. Same 5-fold StratifiedKFold seed=42 for consensus alignment.
