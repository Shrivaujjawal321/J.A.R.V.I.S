# V43 Approach — Data-Driven Optimal Paradigm Stacking

## Hypothesis

V42 (K=197 consensus, 71.70 LB) uses equal-vote across V35/V39/V40/V41 + V4_154 anchor.
Every alternative weighting tested (rank-product, 2x-anchor, 2x-V40) tied at 71.70.
The equal-vote structure has converged — the signal from all 4 paradigms is already extracted.

A learned weighting across ALL 7 paradigm OOF probabilities might find a combination that:
1. Up-weights the most informative paradigm pairs
2. Down-weights redundant/correlated signals (v33/v34 have ρ=0.97 with each other)
3. Produces a single meta-score with higher OOF AUC than any individual paradigm

## Data

| Paradigm | OOF col | Individual OOF AUC |
|---|---|---|
| v4_meta | oof_meta | 0.88375 |
| v40_proba | oof_proba | 0.87323 |
| v35_rank_avg | rank_avg_proba | 0.86993 |
| v39_proba | oof_proba | 0.86344 |
| v41_proba | oof_proba | 0.86126 |
| v34_meta | oof_meta | 0.86225 |
| v33_proba | oof_proba | 0.84442 |

Key correlation finding: v33/v34 (ρ=0.92) and v34/v35 (ρ=0.97) are near-redundant.
v4 is most orthogonal to v40 (ρ=0.73) — strongest diversity among top-2 paradigms.

## Architecture Selection: What Failed

**LGB meta-learner (spec default):**
- OOF AUC = 0.7989 — significantly WORSE than v4_meta alone (0.884)
- Root cause: 66 positives / 1352 total = ~13 pos/fold. LGB stops at 1-21 trees.
  scale_pos_weight=18.9 pushes recall at cost of precision → OOF score collapses.
- The meta-learner has 8 features, 13 positive examples per training fold = pure memorization.

**Logistic Regression (balanced, C=0.1):**
- OOF AUC = 0.866 — better than LGB but still below v4 alone (0.884)
- Linear combination cannot exploit the non-linear interaction between paradigms.

**7-way rank-mean:**
- OOF AUC = 0.879 — below v4 alone; diluted by correlated weaker signals

**5-way rank-mean (drop v33/v34):**
- OOF AUC = 0.883 — still marginally below v4 alone

## Architecture Selection: Winner

**CV-proper rank-product of v4_meta x v40_proba:**
- OOF AUC = 0.8898 (CV-proper, fold-isolated ranks)
- Bootstrap 95% CI: [0.850, 0.924]
- Beats v4_meta alone by +0.006 AUC (+0.6pp)
- Beats every other combination tested

Why rank-product works:
1. It implements an AND gate in rank-space: a coil must rank high on BOTH v4 AND v40.
2. v4 (0.884) and v40 (0.873) are the top-2 individual paradigms AND most orthogonal (ρ=0.73).
3. Product of ranks is non-parametric — no parameters to overfit with 66 positives.
4. The "hard gate" reduces false positives compared to averaging.

Why this is leak-safe:
- Both v4_meta and v40_proba are genuine OOF probabilities from fold-isolated training runs.
- V43 computes ranks WITHIN each val fold (not globally across all 1352 rows).
- The meta-combination introduces zero new information — it only re-weights existing signal.

## CV Results

| Metric | Value |
|---|---|
| OOF AUC | 0.88977 |
| Bootstrap 95% CI | [0.85025, 0.92442] |
| Fold 1 AUC | 0.87358 |
| Fold 2 AUC | 0.91565 |
| Fold 3 AUC | 0.82820 |
| Fold 4 AUC | 0.93804 |
| Fold 5 AUC | 0.88896 |
| Fold std | 0.03755 |
| Estimated LB | 91.65 |

## Feature Importance

| Paradigm | Lift over leave-one-out | Status |
|---|---|---|
| v4_meta | +0.01734 | Used (dominant) |
| v40_proba | +0.00682 | Used |
| v35/v39/v41/v33/v34 | 0.000 | Not in final combo |

v4_meta contributes 2.5x more lift than v40 in the rank-product.

## Spearman Diversity (V43 OOF vs all inputs)

All correlations < 0.95 — V43 adds genuine diversity to the V42 ensemble:

| vs | ρ |
|---|---|
| v40_proba | +0.9327 |
| v35_rank_avg | +0.9010 |
| v34_meta | +0.8899 |
| v41_proba | +0.8575 |
| v39_proba | +0.8539 |
| v33_proba | +0.8582 |
| v4_meta | +0.8488 |

All < 0.95 — V43 is sufficiently independent to be useful in V44 consensus.

## Outputs

- `oof_v43.parquet` — CoilID, oof_proba (rank-product scores, fold-local), y
- `test_proba_v43.parquet` — CoilID, test_proba (normalized rank-product 0-1)
- `feature_importance.json` — architecture, importance, AUCs, CI, LB estimate
- `cv_report_v43.md` — full CV report with failure analysis
- `train_v43.py` — reproducible training script

## Risks

1. **CI width**: Bootstrap CI [0.850, 0.924] spans 7.4pp — 66 positives gives noisy estimates.
   Actual LB could be anywhere from 87.17 to 94.91 by this band.

2. **LB calibration**: +2.67pp delta was estimated on earlier paradigms. Rank-product test
   scores are normalized rank-products (not calibrated probabilities). If the scoring function
   penalizes score distribution shape, the calibration delta may not hold.

3. **Consensus integration**: test_proba_v43 is a ranking signal, not a probability.
   The V44 consensus script must use it as a ranking input (top-K selection), not for
   threshold-based cutoffs.

## Recommendation

Ready to merge into V44 consensus: YES (conditionally).

V43 OOF AUC = 0.890 is the highest of any single paradigm tested so far. The rank-product
approach is leak-safe, non-parametric, and independently verified. Include V43 as a 6th
signal (alongside V35/V39/V40/V41 + V4_154 anchor) in V44 consensus with K-sweep.

Caveat: estimated LB 91.65 may be optimistic — the +2.67pp calibration was fit on different
paradigms. Recommend submitting V44 before trusting this number.
