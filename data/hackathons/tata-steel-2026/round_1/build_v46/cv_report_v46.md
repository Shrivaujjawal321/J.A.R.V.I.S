# V46 CV Report — V4 Base + Steel-Rolling Physics Features

**Date:** 2026-05-24
**Builder:** ml-engineer-agent (Jarvis)
**Architecture:** LGB+XGB+CatBoost -> LR meta + Platt | NO SMOTE | scale_pos_weight=19.48
**Physics recipe:** Peer Ratnesh's 77.67 LB feature set (Zener-Hollomon + Sims + FT coupling + curvature + mono breaks + cooling)

---

## Gate Results

- FAIL: oof_auc_gte_093 = False (actual: 0.86268)
- PASS: spearman_v4_lt_095 = True (actual: 0.7719 — highly diverse)
- FAIL: est_lb_k200_gte_75 = False (correct LB est: ~51)

**Overall gate: FAIL — do NOT use as standalone. Use as DIVERSE CONSENSUS PARADIGM.**

---

## OOF AUC Summary

| Metric | Value | Reference |
|---|---|---|
| Meta OOF AUC | **0.86268** | V4=0.88370, Peer=0.95340 |
| Bootstrap 95% CI | [0.81436, 0.90714] | |
| Delta vs V4 | -0.02102 | |
| LGB OOF AUC | 0.86683 | V4 LGB=0.86150 (+0.005) |
| XGB OOF AUC | 0.86274 | V4 XGB=0.86680 (-0.004) |
| CAT OOF AUC | 0.85317 | V4 CAT=0.87560 (-0.022) |

---

## Per-Fold AUCs

| Fold | LGB | XGB | CAT |
|---|---|---|---|
| 1 | 0.84287 | 0.85450 | 0.84705 |
| 2 | 0.88911 | 0.90411 | 0.88549 |
| 3 | 0.78509 | 0.75516 | 0.78659 |
| 4 | 0.91170 | 0.89734 | 0.90961 |
| 5 | 0.90901 | 0.90422 | 0.85872 |

---

## Correct LB Estimate

**Method: OOF best (R+P)/2 score + 2.67 calibration delta (same as V4 standalone)**

| Metric | Value |
|---|---|
| OOF (R+P)/2 | 48.23 @ K=328 |
| **Estimated LB** | **~50.90** (via OOF score + delta method) |
| V4 standalone LB | 56.98 |
| V44 consensus banked | 72.83 @ K=200 |

NOTE on HE F1 formula (200*TP/(K+154)): Applied to OOF data, max possible F1 = 37.3 since OOF only has 66 positives. These values do NOT predict test LB. The correct LB proxy is (R+P)/2 + delta.

V46 standalone would be WORSE than V4 banked 56.98.

---

## Top-5 SHAP Features (LGB, mean |SHAP|)

1. X14: 0.480297 (V4 feature)
2. X13_over_X36: 0.344718 (V4 feature)
3. X16: 0.320838 (V4 feature)
4. sims_abs_mean: 0.318988 (new physics — ranked #4)
5. X23: 0.317078 (V4 feature)

Physics in top-10: Sims=True, Zener=False (logZ_min at rank #16)

---

## Spearman vs Existing Paradigms

- V46 vs v4_meta: rho=+0.7719 [DIVERSE < 0.80]
- V46 vs v40_proba: rho=+0.0234 [DIVERSE < 0.80] -- near orthogonal to V40!
- V46 vs v41_proba: rho=+0.8167 [MODERATE]
- V46 vs v43_rp: rho=+0.8626 [MODERATE]

V46 is maximally diverse vs V40 (rho=0.023). This makes it valuable for consensus union despite lower standalone AUC.

---

## Root Cause Analysis: Why Physics Features Hurt Standalone AUC

**Finding:** Physics features appended to V4 consistently reduce meta AUC by ~0.02.

**Root cause:**
1. V4's 51 features already include X6, X7, X9 (temps) and X30 (force) from raw columns
2. Physics transforms like ft_coupling_2 = X30/(X5+273.15) are collinear with X30 and X5
3. Trees spend split budget on both raw and transformed versions -> redundant splits
4. With only 66 positives, extra collinear features increase overfitting risk

**Individual physics feature AUCs (standalone, all useful):**
- ft_coupling_2: 0.8016 (highest)
- logZ_4: 0.7110
- temp_mono_breaks: 0.6405
- sims_res_5: 0.6274 (best Sims stand)
- cooling_rate_total: 0.6349

Physics features ARE discriminative. The problem is collinearity with V4 in the tree ensemble.

**Why peer's physics features worked better:**
Peer's base feature set was different -- their raw X columns weren't already in their 51 features.
Their ft_coupling filled genuinely new information dimensions.
Our V4 already captured temperature-force structure via polynomial interactions and raw col selection.

---

## Consensus Union Value

| Criterion | Result |
|---|---|
| Standalone AUC competitive? | NO (0.863 < V4's 0.884) |
| Spearman < 0.80 vs V4? | YES (rho=0.77) -- DIVERSE |
| Spearman < 0.80 vs V40? | YES (rho=0.023) -- NEAR ORTHOGONAL |
| Adds unique ranking signal? | YES |
| Ready for consensus union? | YES -- as diversity paradigm ONLY |

---

## Feature Set

| Group | Count |
|---|---|
| V4 base (SHAP-selected) | 51 |
| Zener-Hollomon (logZ_1..6 + aggregates) | 11 |
| Sims residuals (fold-isolated, Y=0 only) | 7 |
| Temp curvature | 1 |
| F/T coupling per stand | 9 |
| Mono breaks | 2 |
| Cooling rates | 6 |
| TOTAL V46 | 87 |

---

## Top-3 Risks

1. Physics feature collinearity with V4: ft_coupling and logZ use X4-X9 and X29-X33 which overlap with V4's raw columns. This is the primary AUC regression cause.

2. Sims residual signal is weak (AUC 0.52-0.63): Possible cause: auxiliary regressors X10/X11/X12 may not be the right Sims covariates in this anonymized dataset.

3. OOF->LB calibration: The +2.67 delta was fitted on V4-tier models. V46's LB estimate of ~51 should be treated as +-5 points uncertain.

---

## Files

- `oof_v46.parquet` -- 1352 rows: CoilID, oof_proba, y
- `test_proba_v46.parquet` -- 339 rows: CoilID, test_proba
- `cv_summary_v46.json` -- machine-readable summary
- `shap_importance_v46.json` -- top-20 SHAP features
- `feature_engineering_v46.py` -- physics feature pipeline (importable)
- `train_v46.py` -- training script
- `approach.md` -- design notes
