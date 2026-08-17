# V51 CV Report — TabICLv2 Standalone Paradigm (2-seed ensemble)

## Architecture
- Model: TabICLClassifier (tabicl 2.1.1) — transformer-based in-context learning
- Seed 42: n_estimators=16, random_state=42
- Seed 123: n_estimators=16, random_state=123
- V51 = rank-average of seed42 + seed123 OOF probabilities
- Features: V4's 51 SHAP-selected features (no engineered physics)
- CV: 5-fold StratifiedKFold seed=42 (identical to GBDT stack for consensus alignment)
- No SMOTE, no BBSE — TabICLv2 handles imbalance via internal column shuffles

## OOF AUC Results
| Model | OOF AUC |
|-------|---------|
| V51 rank-avg (seed42+123) | **0.87780** |
| V51 seed42 | 0.87773 |
| V51 seed123 | 0.87754 |
| V35-TabICL (n_est=5, baseline) | 0.87519 |
| V4 meta (GBDT best) | 0.88375 |

Bootstrap 95% CI: [0.83297, 0.91485]
Gate threshold (V35 AUC): 0.86993
Gate 1 (AUC >= 0.860): **PASS**

## Per-Fold AUCs
| Fold | seed42 | seed123 |
|------|--------|---------|
| 1 | 0.86762 | 0.86583 |
| 2 | 0.90272 | 0.90245 |
| 3 | 0.83957 | 0.83957 |
| 4 | 0.92906 | 0.93325 |
| 5 | 0.86082 | 0.85992 |
| Mean | 0.87996 | 0.88020 |
| Std  | 0.03187 | 0.03340 |

## Diversity vs GBDT Stack
| Paradigm | Spearman vs V51 | Verdict |
|----------|----------------|---------|
| v4_meta | ρ=+0.81581 | STRONG DIVERSITY |
| v35_rank_avg | ρ=+0.90575 | MODERATE |
| v40_proba | ρ=+0.78101 | STRONG DIVERSITY |
| v41_proba | ρ=+0.85031 | GOOD DIVERSITY |
| v43_proba | ρ=+0.88327 | GOOD DIVERSITY |
| v50_proba | ρ=+0.86397 | GOOD DIVERSITY |
| V35-TabICL (n_est=5) | ρ=+0.95729 | Expected high (same model family) |

**Gate 2 (Spearman vs V4 < 0.90): PASS** (ρ=0.81581)

Internal seed diversity (seed42 vs seed123): ρ=+0.99805

## V51 vs V35-TabICL Comparison
- V35 used: n_estimators=5, single seed (42), part of 9-model rank-avg ensemble
- V51 uses: n_estimators=16 (3.2x more), 2-seed ensemble, standalone paradigm
- V51 AUC lift: +0.261pp over V35-TabICL alone

## Compute
- Total wall time: 2808s (~46.8 min)
- Per-fold mean: 233s
- Hardware: CPU only (TabICLv2 CPU mode, 1352 train rows × 51 features)

## Gates Summary
- Gate 1 (OOF AUC >= 0.860): **PASS** — 0.87780
- Gate 2 (Spearman vs V4 < 0.90): **PASS** — ρ=0.81581
- **Ready for V52 consensus: YES**

## Risks
1. TabICLv2 probabilities are not calibrated — treat as ranking signal in consensus, not raw probability
2. OOF AUC CI [0.83297, 0.91485] wide due to only 66 positives in 1352 rows
3. TabICLv2 is a CPU-only model here; ensemble with GBDT stack is the intended use (not solo submission)
4. V51 vs V35-TabICL Spearman 0.957 — as expected, high within-family correlation; diversity gain comes from vs GBDT members
