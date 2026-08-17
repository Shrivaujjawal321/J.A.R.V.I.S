# V43 CV Report — Rank-Product Meta-Learner (v4_meta x v40_proba)

## Architecture
- Final design: CV-proper rank-product of v4_meta and v40_proba
- Ranks computed WITHIN each validation fold (5-fold StratifiedKFold seed=42)
- No trainable parameters — non-parametric, zero overfitting risk
- LGB meta-learner was evaluated and REJECTED (see Failure Analysis below)

## OOF AUC
- **OOF AUC: 0.88977** (88.98%)
- Bootstrap 95% CI: [0.85025, 0.92442]
- **Estimated LB: 91.65** (OOF×100 + 2.67pp calibration delta)

## Per-Fold AUCs
- Fold 1: 0.87358
- Fold 2: 0.91565
- Fold 3: 0.82820
- Fold 4: 0.93804
- Fold 5: 0.88896
- Mean: 0.88888 | Std: 0.03755

## Individual OOF AUCs (baseline comparison)
- v4_meta: 0.88375 ← used in V43
- v40_proba: 0.87323 ← used in V43
- v35_rank_avg: 0.86993
- v39_proba: 0.86344
- v34_meta: 0.86225
- v41_proba: 0.86126
- v33_proba: 0.84442

## Feature Importance (lift over leave-one-out)
- v4_meta: +0.01734 (combo - v40_only)
- v40_proba: +0.00682 (combo - v4_only)
- All others: 0.000 (not in final combination)

## Spearman: V43 OOF vs Input Paradigms
(< 0.95 = adds diversity; < 0.85 = strong diversity)
- V43 vs v40_proba: ρ=+0.9327
- V43 vs v35_rank_avg: ρ=+0.9010
- V43 vs v34_meta: ρ=+0.8899
- V43 vs v33_proba: ρ=+0.8582
- V43 vs v41_proba: ρ=+0.8575
- V43 vs v39_proba: ρ=+0.8539
- V43 vs v4_meta: ρ=+0.8488 [DIVERSE]

## Failure Analysis: LGB Meta-Learner
- LGB with scale_pos_weight=18.9: OOF AUC = 0.79890 (WORSE than v4_meta alone 0.88375)
- Root cause: 66 positives / 1352 total → ~13 positives per val fold for 8 features.
  LGB stops at 1-21 trees (early stopping) — underfitting, just replicating input signal.
  scale_pos_weight pushes recall aggressively, destroying precision in OOF.
- LogReg balanced (C=0.1) on 7 features: OOF AUC = 0.86625 — better, but still below v4 alone.
- Rank-mean of 7 OOFs: OOF AUC = 0.87856 — below best 2-way rank-product.
- Rank-mean of 5 OOFs (drop correlated v33/v34): 0.88340 — still below rank-product.
- **Rank-product v4 x v40: 0.89057 (global) / 0.88977 (CV-proper)** — best combination.
- Why v4 + v40? Pairwise Spearman ρ=0.73 (most orthogonal pair). Both individually top-2.

## Leak Safety
- All input features are OOF probabilities from fold-isolated training runs.
- V43 itself computes ranks WITHIN val folds — no global rank ordering across folds.
- No raw train features, no target Y used in the meta-combination logic.
- Test prediction uses global ranks on test rows only (no train data involved).

## Risks
- OOF AUC 0.890 with CI [0.850, 0.924] has wide bands — 66 positives limits precision.
- Estimated LB 91.65 assumes +2.67pp calibration delta holds; verify after LB submission.
- Rank-product test output is a non-probability score (normalized rank-product 0-1).
  The consensus V44 script should treat it as a ranking signal, not a calibrated proba.
- V40 uses a different CoilID sort order than other paradigms; handled via .reindex().
