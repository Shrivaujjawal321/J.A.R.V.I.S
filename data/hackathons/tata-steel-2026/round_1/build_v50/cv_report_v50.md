# V50 CV Report — Pure-Physics Base (raw X4-X9/X29-X33 excluded)

**Date:** 2026-05-24
**Architecture:** LGB+XGB+CatBoost → LR meta + Platt | NO SMOTE | scale_pos_weight=19.48
**Key fix vs V46:** Dropped raw temp/force cols from model input → physics fills new dimensions, not collinear ones

---

## Gate Results

- FAIL: oof_auc_gte_091 = False
- FAIL: oof_auc_gt_v4_0_8837 = False
- PASS: oof_auc_gt_v46_0_8627 = True
- PASS: shap_sims_in_top10 = True
- FAIL: shap_zener_in_top10 = False
- PASS: spearman_v4_lt_085 = True
- FAIL: est_lb_k200_gte_75 = False

**Win condition (critical):** OOF AUC > V4 (0.8837). If V50 AUC <= 0.86, physics-on-pure-base is also dead.

**Overall: PARTIAL/FAIL — check gates above**

---

## OOF AUC Summary

| Metric | Value | Reference |
|---|---|---|
| Meta OOF AUC | **0.86848** | V4=0.8837, V46=0.8627 (regressed), Peer=0.9534 |
| Bootstrap 95% CI | [0.82399, 0.90941] | |
| Delta vs V4 | -0.01522 | |
| Delta vs V46 (collinear fail) | +0.00580 | |
| Delta vs Peer | -0.08492 | |
| LGB OOF AUC | 0.87171 | V4 LGB=0.86150 |
| XGB OOF AUC | 0.86717 | V4 XGB=0.86680 |
| CatBoost OOF AUC | 0.85686 | V4 CAT=0.87560 |

---

## Per-Fold AUCs (LGB)

| Fold | AUC |
|---|---|
| 1 | 0.84735 |
| 2 | 0.88772 |
| 3 | 0.80844 |
| 4 | 0.91679 |
| 5 | 0.90422 |
**Mean: 0.87290 ± 0.03984**

## Per-Fold AUCs (XGB)

| Fold | AUC |
|---|---|
| 1 | 0.84884 |
| 2 | 0.91801 |
| 3 | 0.76743 |
| 4 | 0.90183 |
| 5 | 0.90901 |
**Mean: 0.86902 ± 0.05622**

## Per-Fold AUCs (CatBoost)

| Fold | AUC |
|---|---|
| 1 | 0.84526 |
| 2 | 0.87882 |
| 3 | 0.80994 |
| 4 | 0.89644 |
| 5 | 0.86082 |
**Mean: 0.85826 ± 0.02963**

---

## Estimated LB (HE F1: 200*TP/(K+154))

| K | OOF TP | Est LB |
|---|---|---|
| 200 | 44/66 | **24.86** |
| 216 (peer K) | 46/66 | **24.86** |
| Best (K=145) | 39/66 | **26.09** |

Legacy delta-based (AUC*100+2.67): 89.52
Gap to peer 77.67 @K=216: -52.81
Gap to V44 banked 72.83 @K=200: -47.97

---

## Top-5 SHAP Features (LGB, mean |SHAP|)

- 1. X14: 0.472865
- 2. poly_X13_over_X36_X16: 0.371770
- 3. X23: 0.336098
- 4. sims_abs_mean: 0.328243
- 5. X18: 0.312429

Physics in top-10: Sims=True, Zener=False, FT=False
Gate: Sims+Zener should appear → FAIL/NA

---

## Spearman vs Existing Paradigms

- V50 vs v4_meta: ρ=+0.7698  [DIVERSE <0.80]
- V50 vs v46_proba: ρ=+0.9845  [VERY HIGH]
- V50 vs v40_proba: ρ=+0.0236  [DIVERSE <0.80]
- V50 vs v41_proba: ρ=+0.8121  [MODERATE <0.85]

Gate: Spearman vs V4 < 0.85 (genuine diversity)
Result: 0.7698 → PASS

---

## Feature Set

| Group | Count |
|---|---|
| V4 clean base (raw/derived-raw dropped) | 46 |
| Dropped from V4 (raw/derived) | 5: ['X6', 'X7', 'X9', 'X30_over_X35', 'X30'] |
| Zener-Hollomon (11) | logZ_1..6 + mean/std/F1F5drop/max/min |
| Sims residuals (7, fold-isolated) | sims_res_1..5 + sims_abs_max/mean |
| Temp curvature (1) | X4 - 2*X6 + X9 |
| F/T coupling (9) | ft_coupling_1..5 + max/mean/std/range |
| Mono breaks (2) | temp_mono_breaks + force_mono_breaks |
| Cooling rates (6) | cooling_rate_total + cool_rate_1..5 |
| **TOTAL V50** | **82** |

---

## Why V50 Should Beat V46

V46 added physics features ON TOP of a V4 base that still had raw X6, X7, X9, X30 in it.
- logZ_i = f(X4..X9) → near-collinear with X6, X7, X9 already in V4
- ft_coupling_i = X29_i / T_K_i → near-collinear with X30 already in V4
- Result: trees wasted splits on redundant dimensions → AUC regressed (0.8837 → 0.8627)

V50 drops the raw cols first:
- Physics features now occupy genuinely NEW dimensions in feature space
- Trees can discover the physics signal without competing with its raw sources
- Peer's iter52 (0.9534 OOF) did exactly this — pure-physics base

---

## Top-3 Risks

1. **Signal magnitude:** With 5 raw cols removed from V4, the base loses some discriminative
   power. The physics features need to MORE than compensate. If V50 AUC < 0.8837, the
   remaining V4 features (X13/X36 ratio domain) aren't sufficient to carry the load even
   with physics augmentation. → Pivot to TabPFN / OpenFE.

2. **OOF vs LB gap:** The +2.67 calibration was fitted on V4-tier models. Physics-augmented
   OOF→LB relationship is unknown. Use HE F1 formula (TP-based) as primary LB estimator,
   not the legacy delta method.

3. **Fold-3 variance:** Historical hard fold (13 val positives). Physics features with high
   within-stand variance may amplify fold-3 noise. Monitor per-fold std.

---

## Ready for V51 Consensus?

CONDITIONAL — check failed gates. If AUC <= 0.86, physics-pure-base dead → pivot.

Files:
- `oof_v50.parquet` — 1352 rows: CoilID, oof_proba, y
- `test_proba_v50.parquet` — 339 rows: CoilID, test_proba
- `cv_summary_v50.json` — machine-readable summary
- `shap_importance_v50.json` — SHAP rankings + physics validation
- `train_v50.py` — this script
- `approach.md` — design notes
- `cv_report_v50.md` — this file
