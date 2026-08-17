# V51 Approach — TabICLv2 Standalone Paradigm

## Motivation
After 10+ GBDT variants (V4, V33-V50), all paradigms share the same inductive bias
(gradient-boosted decision trees). Even with diverse hyperparameters, they form a
consensus ceiling around 72-73 LB because they fail in the same ways.

TabICLv2 is a transformer-based in-context learning model: it treats training data as
context and makes predictions via attention over that context. It has a fundamentally
different failure mode from GBDTs — it can capture global dependencies and complex
interactions that decision trees miss, but is weaker on local monotone relationships
that GBDTs excel at.

## Config
- Model: TabICLClassifier (tabicl 2.1.1)
- n_estimators=16: each estimator shuffles column order differently, providing ensemble
  diversity within a single TabICL fit
- Seed ensemble: seed42 + seed123 → rank-average (additional diversity from different
  random column shuffle orderings)
- Features: V4's 51 SHAP-selected features — stable, proven, no physics guesses
- CV: same 5-fold StratifiedKFold seed=42 as all GBDT models (proper consensus alignment)

## V35 vs V51
V35 included TabICLClassifier(n_estimators=5, seed=42) as one of 9 models in a rank-avg.
V51 makes TabICL the primary paradigm with a proper 2-seed ensemble and higher n_estimators.

## Expected Role in Consensus
V51 is designed to be a NEW COLUMN in the consensus matrix (V52 or later).
Ensemble with V4/V40/V43 via rank-average should provide +1.5-3 LB lift if
Spearman vs GBDT stack is < 0.90.

## OOF AUC
0.87780 (rank-avg of 2 seeds)
Gate vs V35 baseline (0.860): PASS
Diversity vs V4 (want < 0.90): ρ=0.81581 → PASS
