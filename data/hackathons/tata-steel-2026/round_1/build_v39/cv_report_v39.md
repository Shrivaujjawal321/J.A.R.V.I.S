# V39 CV Report — iter35-equivalent (CoilID + 6 derivatives)

## Summary

| Metric | Value |
|--------|-------|
| OOF AUC | **0.8634** |
| Mean fold AUC | 0.8640 ± 0.0470 |
| Bootstrap mean AUC | 0.8641 |
| Bootstrap 95% CI | [0.8118, 0.9118] |
| OOF (R+P)/2 best | 50.0713 (K=223) |
| Est LB (OOF+2.67) | 52.74 |
| Ratnesh iter35 OOF AUC (peer) | 0.9412 |
| V4 meta OOF AUC (baseline) | 0.8837 |
| V4 LB (banked) | 56.98 |

## Fold-level AUCs

| Fold | AUC |
|------|-----|
| 1 | 0.8214 |
| 2 | 0.8747 |
| 3 | 0.8081 |
| 4 | 0.9404 |
| 5 | 0.8755 |
| **Mean** | **0.8640** |
| **Std** | **0.0470** |

## Diversity vs V4 (consensus merge signal)

| Metric | Value | Signal |
|--------|-------|--------|
| Spearman(V39, V4_meta) | **0.7549** (p=1.53e-249) | DIVERSE (rho < 0.85 — good for consensus) |

> Target: rho < 0.85 for genuine OOF diversity (independent error signal for consensus union)

## Feature Engineering

- **Total features**: 58 (51 V4 base + 7 CoilID-derived)
- **V4 base (51)**: SHAP-selected ratios, poly interactions, IsoForest score, neighbor features, prev5_defect_rate
- **CoilID-derived (7)**:
  1. `CoilID` — raw
  2. `CoilID_sq` — squared (quadratic trend)
  3. `CoilID_log` — log(CoilID + 1) (compresses high-ID range)
  4. `CoilID_gt_med` — flag: CoilID > fold-median (824.5)
  5. `CoilID_gt_p75` — flag: CoilID > fold-75th-pct (1254.2)
  6. `CoilID_sin` — sin(2π × CoilID / 1700) (cyclic signal)
  7. `CoilID_cos` — cos(2π × CoilID / 1700) (cyclic signal)
- Threshold flags computed fold-isolated (fold-train CoilID stats only — no leakage)

## Configuration

- scale_pos_weight = 19.48
- NO SMOTE, NO BBSE, NO stand-FE
- StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
- LGB: lr=0.03, num_leaves=63, max_depth=6, n_estimators=700

## Top-3 Risks

1. **OOF overfit on cyclic signal**: CoilID cyclic features (sin/cos) are continuous and interpolate perfectly — risk that they capture a chance correlation in 1352 rows (only 66 positives). AUC bump may not generalize to LB.
2. **Temporal leakage via CoilID raw/sq/log**: If LB test coils are from a very different range, CoilID-trend features may degrade. Cyclic features (sin/cos) are safer.
3. **High Spearman with V4 base**: Both paradigms use the same V4 51-feature base; CoilID adds 7 new signals but correlation with V4 meta may still be high, limiting consensus union benefit.

## Consensus-Ready Verdict

| Check | Result |
|-------|--------|
| OOF AUC computed | YES (0.8634) |
| test_proba saved | YES |
| Spearman vs V4 computed | YES (0.7549) |
| rho < 0.85 (diversity) | YES |
| est LB > V4 banked (56.98) | NO (52.74) |

**Ready for consensus union: YES**
