# V61 CV Report — Physics Features (Collinearity Fixed)

**Date:** 2026-05-25
**Fix vs V46/V60:** Dropped collinear raw cols (X6,X7,X9,X30,X30_over_X35) before adding physics
**Architecture:** 5-Fold × 3-Learner × 5-Seed rank-avg | NO SMOTE | scale_pos_weight=19.48
**Features:** 46 V4-clean + 29 static physics + 7 Sims = 82 total
**Banked baseline:** V44 K=200 = 72.83 LB

---

## Summary

| Metric | Value | Gate |
|---|---|---|
| OOF AUC | 0.85716 | MISS (0.85716 < 0.93) |
| OOF AUC Bootstrap 95% CI | [0.81143, 0.89776] | — |
| **OOF F1@K=200** | **0.330827 (TP=44)** | **FAIL (0.330827)** |
| OOF F1@K=154 | 0.381818 (TP=42) | — |
| OOF best K | K=100, F1=0.421687 (TP=35) | — |
| Spearman vs V46 | 0.849 | PASS (0.849) |
| Training time | 6.3 min | — |

---

## V61 Feature Set

| Group | Count | Collinear drop |
|---|---|---|
| V4 SHAP-selected (clean) | 46 | Dropped X6,X7,X9,X30,X30_over_X35 |
| Static physics (Zener+curvature+FT+mono+cooling) | 29 | None |
| Sims force-residual (fold-isolated) | 7 | None |
| **TOTAL** | **82** | |

---

## Per-Fold CV Results

| Fold | LGB_mean | XGB_mean | CAT_mean | Time |
|---|---|---|---|---|
| 1 | 0.8132 | 0.8145 | 0.8618 | 74s |
| 2 | 0.8508 | 0.8575 | 0.8752 | 85s |
| 3 | 0.8418 | 0.8400 | 0.8447 | 69s |
| 4 | 0.8761 | 0.8957 | 0.8685 | 71s |
| 5 | 0.8359 | 0.8313 | 0.8552 | 75s |

---

## Per-Model OOF AUCs (top sorted)

| Model | OOF AUC |
|---|---|
| cat_s2024 | 0.86390 |
| cat_s7 | 0.86289 |
| cat_s1000 | 0.85987 |
| cat_s137 | 0.85461 |
| cat_s42 | 0.85365 |
| xgb_s7 | 0.85313 |
| xgb_s42 | 0.85158 |
| xgb_s137 | 0.85041 |
| lgb_s137 | 0.84747 |
| lgb_s1000 | 0.84382 |
| lgb_s7 | 0.84275 |
| lgb_s42 | 0.84249 |
| xgb_s2024 | 0.84217 |
| xgb_s1000 | 0.83955 |
| lgb_s2024 | 0.83737 |

---

## K Sweep

| K | OOF F1@K | TP |
|---|---|---|
| 50 | 0.379310 | 22 |
| 75 | 0.411348 | 29 |
| 100 | 0.421687 | 35 |
| 130 | 0.397959 | 39 |
| 154 | 0.381818 | 42 |
| 170 | 0.364407 | 43 |
| 186 | 0.341270 | 43 |
| 197 | 0.334601 | 44 |
| 200 | 0.330827 | 44 |
| 210 | 0.318841 | 44 |
| 220 | 0.307692 | 44 |
| 229 | 0.305085 | 45 |
| 250 | 0.284810 | 45 |

---

## Spearman vs Reference OOFs

| Reference | Spearman ρ |
|---|---|
| V46 | 0.849 |
| V43 | 0.8239 |
| V54b | 0.7828 |

---

## Gates

| Gate | Condition | Result |
|---|---|---|
| 1 — F1 benchmark | OOF F1@K=200 > 0.391 | FAIL (0.330827) |
| 2 — AUC target | OOF AUC > 0.93 (Ratnesh iter51=0.9534) | MISS (0.85716 < 0.93) |
| 3 — Diversity | Spearman vs V46 in [0.70, 0.90] | PASS (0.849) |

---

## Improvement vs Prior Builds

| Build | OOF AUC | OOF F1@K=200 | Key diff |
|---|---|---|---|
| V4 base | 0.884 | — | 51 V4 features |
| V46 physics | 0.863 | — | V4 + physics (collinear) |
| V53 Caruana | 0.883 | 0.391 | 13-paradigm greedy |
| V60 stand-decomp | 0.858 | 0.338 | Wrong base decomp |
| **V61** | **0.85716** | **0.330827** | **V4-clean + physics (collinearity fixed)** |
