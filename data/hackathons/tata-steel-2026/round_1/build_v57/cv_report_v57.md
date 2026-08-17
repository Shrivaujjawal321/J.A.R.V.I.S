# V57 CV Report — Adversarial Validation + Density-Ratio Reweighting

**Date:** 2026-05-25
**Architecture:** 5-Fold V4 Stack (LGB+XGB+CAT → LR Meta) + DR sample weights + BBSE correction
**Theory:** Sugiyama JMLR 2007 (IWCV) + Lipton ICML 2018 (BBSE) + Uber 2020 (adversarial validation)
**Banked baseline:** V44 K=200 = 72.83 LB | V53 OOF F1@K=200 = 0.391

---

## Summary

| Metric | Value | Gate |
|--------|-------|------|
| **Adversarial AUC** | **0.5509** | — (WEAK/NO shift — density-ratio correction may not help) |
| OOF AUC (final) | 0.86657 | — |
| OOF AUC Bootstrap 95% CI | [0.82056, 0.90624] | — |
| **OOF F1@K=200** | **0.345865** | **FAIL (> 0.391 benchmark)** |
| OOF F1@K=154 | 0.372727 (TP=41) | — |
| OOF best K sweep | K=91, F1=0.420382 (TP=33) | — |
| Spearman vs V44 (V43 proxy) | 0.9053 | FAIL/UNKNOWN (0.70-0.90) |
| BBSE q_test estimate | 0.0156 | — (expected ~0.45) |
| DR weights active | True | — (clip [0.1, 10.0], norm mean=1.0) |
| Using BBSE predictions | False | — |
| Training time | 1.8 min | — |

---

## Architecture

- **5-Fold StratifiedKFold** (seed=42) — exact V4 paradigm
- **Base learners:** LightGBM, XGBoost, CatBoost with sample_weight=density_ratio_clipped
- **Density-ratio weights:** p̂(test|x) / p̂(train|x) from adversarial LightGBM, clipped [0.1, 10.0], normalized mean=1.0
- **Meta:** LogisticRegression (C=0.1) on [lgb_oof, xgb_oof, cat_oof]
- **BBSE correction:** Bayes-adjusted posterior for q_test=0.0156 (estimated from soft predictions)
- **NO** new feature engineering — exact V4 51-feature set

## Per-Model OOF AUCs

| Model | OOF AUC | Fold Mean |
|-------|---------|-----------|
| LGB (DR-weighted) | 0.85987 | 0.86188 |
| XGB (DR-weighted) | 0.85823 | 0.86035 |
| CAT (DR-weighted) | 0.86340 | 0.86813 |
| LR Meta | 0.86657 | — |

## Raw vs BBSE Comparison

| Variant | OOF F1@K=200 | OOF F1@K=154 | TP@K=200 | TP@K=154 |
|---------|-------------|-------------|---------|---------|
| Raw (DR-weighted only) | 0.345865 | 0.372727 | 46 | 41 |
| BBSE-corrected | 0.345865 | 0.372727 | 46 | 41 |
| **V53 benchmark** | **0.391000** | — | 52 | — |
| **V44 (no BBSE)** | — | — | — | — |

## Spearman vs Reference OOFs

| Comparison | Spearman rho | Diversity |
|-----------|-------------|---------|
| V57 vs V43 | +0.9053 | HIGH_CORR |
| V57 vs V4 | +0.8134 | MODERATE |
| V57 vs V40 | +0.8242 | MODERATE |
| V57 vs V41 | +0.8796 | MODERATE |
| V57 vs V54 | +0.8915 | MODERATE |

**Target for V44 paradigm diversity: 0.70-0.90 Spearman**

---

## K Selection

| K | OOF F1@K | TP | Notes |
|---|---------|----|----|
| 154 | 0.372727 | 41 | ICR recipe K |
| 200 | 0.345865 | 46 | V44 banked K |
| 91 | 0.420382 | 33 | OOF best sweep |

---

## Gates Summary

| Gate | Condition | Result |
|------|----------|--------|
| 1 — F1 benchmark | OOF F1@K=200 > 0.391 (V53) | FAIL (0.345865) |
| 2 — Diversity | Spearman vs V44 in [0.70, 0.90] | FAIL/UNKNOWN (0.9053) |

---

## Improvement vs Prior Builds

| Build | OOF F1@K=200 | Architecture |
|-------|-------------|-------------|
| V4 (base) | 0.243 | 5-fold stack no DR |
| V43 | 0.346 | Rank-product |
| V53 Caruana | 0.391 | 13-paradigm greedy |
| V54 | 0.331 | 10-fold ICR recipe |
| **V57** | **0.345865** | **V4 stack + DR weights + BBSE** |

---

## Theory Check

The Sugiyama IWCV framework prescribes: weight each train sample by w(x) = p(test|x)/p(train|x)
so the CV loss approximates the test distribution loss. With adversarial AUC=0.5509,
the adversarial classifier reliably distinguishes train from test.

DR weight stats: pos mean=0.827 vs neg mean=1.009.
Negatives upweighted — training may be suboptimal for test distribution.
