# V60 Approach — Stand-Decomposed Base + Physics Features

## Hypothesis

V46 physics features (Sims residual + Zener-Hollomon + F/T coupling) failed to improve over V4 (OOF AUC dropped 0.02) because of feature collinearity:

- V4's 51 features already include raw X4-X9 (temperatures) and X29-X33 (forces)
- Physics transforms like `ft_coupling_2 = X30 / (X5+273.15)` are algebraically collinear with X30 and X5
- Trees split redundantly on both raw and transformed versions → wasted split budget → overfit on 66 positives

Peer's iter52 (77.67 LB) used a stand-decomposed feature base (iter36: 148 features). Their physics features filled genuinely new information dimensions because their raw stand columns were NOT in their base feature set.

**V60 Hypothesis:** Replace raw X4-X9 and X29-X33 with stand-decomposed features first, then build physics on top. This breaks the collinearity at the source.

## Stand Decomposition Strategy

Based on value-range analysis of X1-X49:
- X4-X9: temperature stands (range 400-760°C, highly correlated r>0.69)
- X29-X33: rolling force stands (range 5-25 units)

Per-stand decomposed features:
- `ts_t{i}` = raw stand temperature (replaces X4-X9 directly)
- `ts_t{i}_dev` = deviation from Y=0 mean setpoint (fitted on negatives)
- `ts_tdrift{i}` = inter-stand delta X_i - X_{i-1} (process drift signal)
- `ts_f{i}` = raw stand force (replaces X29-X33)
- `ts_f{i}_dev` = deviation from Y=0 mean force setpoint
- `ts_fdrift{i}` = inter-stand force drift
- `ts_ft{i}` = F_i / T_i_K = force normalized by temperature (stand-decomposed coupling)
- Aggregates: mean, std, range, argmax across all stands

## Physics Features (on Stand-Decomposed Basis)

### Zener-Hollomon (stand-decomposed)
- Uses `ts_tdrift{i}` as strain-rate proxy (inter-stand temp delta)
- Uses `ts_t{i}` as stand temperature input
- No raw X4-X9 in the formula → collinearity broken
- logZ_sd_1..6 + aggregates (10 features)

### Sims Force Residual (fold-isolated)
- Target: `ts_f{i}_dev` (force deviation from setpoint) — more stable than raw force
- Regressors: [ts_t{i}, X10, X11, X12] — stand temperature + auxiliary
- Trained ONLY on Y=0 rows from fold-train (peer's exact protocol)
- sims_sd_1..5 + absmax + absmean (7 features)

### F/T Coupling (stand-decomposed)
- Already in stand decomp as `ts_ft{i}` — included above, not double-counted

## Why V46 Failed, Why V60 Should Work

| Root Cause | V46 | V60 |
|------------|-----|-----|
| ft_coupling = F/T | Built on raw X30/X5 → collinear with X30 in V4 | Built as ts_ft = F/T where F=ts_f, T=ts_t → no raw F/T in feature matrix |
| Zener-Hollomon | Built on raw X4-X9 → collinear | Built on ts_t{i} (stand-normalized deviations) |
| Sims target | Raw force → correlated with force in feature set | Force deviation ts_f{i}_dev → captures only anomaly signal |
| Feature base | V4 raw (includes X4-X9 and X29-X33) | Stand-decomposed (raw X4-X9/X29-X33 dropped) |

## Final Feature Matrix (~73 features)

- 56 stand decomp (T: 6×2 + 5drift + 5agg + F: 5×2 + 4drift + 4agg + 5 F/T + 3 agg)
- 10 Zener-Hollomon (stand-decomposed)
- 7 Sims residuals (fold-isolated, stand-decomposed)
- ~44 V4 cleaned features (minus raw X4-X9, X29-X33, X30 standalone)
  - Includes: X13_over_X36, poly interactions, lag features, prev5_defect_rate
  - Ratio features (X30_over_X35) kept — ratio = new dimension, not collinear

## Architecture

- LGB + XGB + CatBoost → LR meta → Platt calibration at T=0.01428
- StratifiedKFold(5, shuffle=True, seed=42)
- scale_pos_weight=19.48 (class imbalance)
- NO SMOTE (V4 lesson)
- Early stopping patience=200

## Success Criteria

- OOF F1@K=200 >= 0.391 (V53 Caruana benchmark)
- Physics features in top-5 SHAP (>=3 of: sims_sd, logZ_sd, ts_ft)
- VIF < 5 for all final features
- Spearman vs V4 < 0.95 (diverse signal)
