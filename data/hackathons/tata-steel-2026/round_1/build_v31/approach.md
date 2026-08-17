# V31 Approach — V4 ⊕ AutoGluon Rank-Blend (K=170)

## Strategy

Pure post-hoc rank-blend of two independent paradigm signals:
1. **V4** — LightGBM + XGBoost + CatBoost stacking with Logistic Regression meta-learner + Platt calibration, trained on 51 features (30 SHAP-selected + 15 polynomial interactions + 6 coil-neighbor temporal features) with SMOTE inside 5-fold StratifiedKFold (seed=42). Banked LB score: 56.98.
2. **AutoGluon best_quality** — 50-minute compute budget, num_bag_folds=5, num_stack_levels=1. OOF AUC ~0.86.

## Blend Method

For each of the 339 test rows:
- Compute V4 rank (descending by test_meta probability)
- Compute AutoGluon rank (descending by predicted probability)
- Equal-weight rank average: blend_rank = (v4_rank + ag_rank) / 2
- Flag top K=170 rows by blended rank as positive

## Diagnostic Numbers

- Spearman correlation V4 vs AG (test): -0.0282 — the two paradigms produce nearly-orthogonal rankings.
- V4-flagged 154 ∩ V31-top170: 108 (70% overlap)
- Vs V4 at K=170: 62 new rows added, 46 V4 rows dropped
- CoilID 654 (AG outlier at 0.687): jumps from V4 rank 221 to V31 blend position 73.

## Why K=170

Borrowed from peer paradigm-pool analysis indicating K within [165,175] is the optimum on related blends. K=180 documented to regress; K=170 sits at the inflection.

## Risk Acknowledgment

Spearman -0.0282 indicates V4 and AG are not in the same paradigm pool. This is a larger distribution perturbation than typical small-perturbation blends. Calibration outcome is uncertain — submission is a deliberate exploration of the orthogonal-signal hypothesis.

## Files

- solution.csv — final 339-row submission with 170 positives flagged
- v31_blend_analysis.csv — full per-row diagnostics
- expected_submission_K170.csv — same as solution.csv
- expected_submission_K185.csv — alternate K=185 variant (not submitted)
