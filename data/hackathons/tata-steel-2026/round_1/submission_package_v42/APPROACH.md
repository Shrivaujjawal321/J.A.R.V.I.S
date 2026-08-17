# Tata Steel AI Hackathon 2026 — Round 1: Hot Rolling Defect Detection
## Approach Summary — V42 Consensus Union

**Participant:** Ujjawal Shrivastav (shriva.ujjawal@gmail.com)
**Submission:** V42 K=197 — 4-paradigm consensus union + V4 anchor
**Public LB Score:** 71.69811

---

## 1. Problem Framing

Binary classification on 1352 train + 339 test rows with 49 anonymous X-features.
- Train defect prevalence: 5.0% (66 positives / 1352)
- Inferred test defect prevalence: ~45% (severe label-shift)
- Evaluation: (Recall + Precision) / 2 on top-K predicted positives

The dataset is small, severely imbalanced, and exhibits **prevalence inversion** between train (5%) and test (~45%). Single-model approaches cap at ~OOF AUC 0.87 due to the limited positive class signal.

## 2. Strategy: Multi-Paradigm Consensus Union

Instead of optimizing a single model, we build **4 diverse paradigms** and aggregate their rankings via consensus voting + a leaderboard-validated anchor set.

### Paradigm 1 — V35 (9-model rank-average base)
- 9 base learners: LGB×2 (seeds 42/137), XGB×2 (seeds 42/137), CatBoost, RandomForest, ExtraTrees, HistGradientBoosting, TabICLv2
- 105-feature base (V4 51 features + 54 stand-residual features)
- Rank-average aggregation across models
- `scale_pos_weight = 18.9`, no SMOTE, 5-fold StratifiedKFold seed=42

### Paradigm 2 — V39 (CoilID cyclic + derivative features)
- V4 51-feature base + 7 CoilID-derived features:
  - CoilID raw
  - CoilID² (squared)
  - log(CoilID + 1)
  - Two threshold flags (CoilID > median, > 75th percentile)
  - sin(2π × CoilID / 1700) — cyclic
  - cos(2π × CoilID / 1700) — cyclic
- Single LightGBM, scale_pos_weight=18.9, 5-fold StratifiedKFold seed=42
- OOF AUC: 0.86, Spearman vs V4 = 0.75 (diverse)

### Paradigm 3 — V40 (defect-proximity, CV-safe)
- V4 51-feature base + 11 defect-proximity features:
  - dist_to_nearest_defect (standardized Euclidean in 49-D)
  - count_within_radius for r ∈ {0.5, 1.0, 1.5, 2.0, 3.0}
  - density_within_radius for same radii
- **Critical CV safety:** "known defects" set computed from train-fold only, never validation rows
- For test: uses all train defects
- OOF AUC: 0.87, Spearman vs other paradigms = 0.02-0.04 (maximally orthogonal)

### Paradigm 4 — V41 (BBSE-reweighted)
- V4 51-feature base, no SMOTE, scale_pos_weight=1 (neutral)
- BBSE sample-weight reweighting per Lipton et al. ICML 2018:
  - w₁ = p_test/p_train ≈ 9.0 for Y=1
  - w₀ = (1-p_test)/(1-p_train) ≈ 0.58 for Y=0
- Single LightGBM, 5-fold StratifiedKFold seed=42
- OOF AUC: 0.86, Spearman vs V37 = 0.06 (very diverse)

### Anchor: V4_154
- Banked LB-validated baseline (V4 = LightGBM + XGBoost + CatBoost stack + LR meta + Platt calibration, T=0.01428)
- Selected positives from V4's expected_submission.csv (154 CoilIDs)
- Provides empirical LB-grounding to the consensus

## 3. Consensus Aggregation

1. For each paradigm, take the **top-181 predicted positives** (matches literature recipe)
2. Add the **V4_154 anchor set**
3. For each CoilID, count "votes" = number of paradigms (out of 4) + 1 if in V4_154 anchor that selected it (max vote = 5)
4. Tiebreak by mean rank-percentile across the 4 paradigms
5. Sort by (vote DESC, rank-percentile-mean DESC)
6. Select **top-K = 197** as final positives

## 4. Vote Distribution

| Votes | # Coils | Cumulative K |
|---|---|---|
| 5 (all sources agree) | 132 | 132 |
| 4 | 23 | 155 |
| 3 | 18 | 173 |
| 2 | 20 | 193 |
| 1 | 32 | 225 |
| 0 | 114 | — |

K=197 includes 132 full-consensus + 23 four-vote + 18 three-vote + 20 two-vote + 4 one-vote = 197.

## 5. Leakage Protection (Critical)

- **Fold-isolated medians/statistics** — Per Lipton et al. label-shift bias analysis, train+test combined statistics leak Y-signal via the 5%→45% prevalence inversion. All paradigm features use train-fold-only statistics.
- **CV-safe defect proximity** — V40's known-defects set computed from train-fold only.
- **No SMOTE** in V39/V40/V41 — SMOTE-augmented samples create distribution mismatch with real-sample feature engineering (validated empirically in V34).

## 6. Anti-Patterns Avoided

- AP-1: `pd.concat([train,test]).median()` for setpoint inference → leakage via prevalence shift. Train-fold-only used.
- AP-2: SMOTE before outer CV split → synthetic leakage across folds. SMOTE inside fold via `imblearn.pipeline.Pipeline` (when used).
- AP-3: BBSE-on-top-of-scale_pos_weight compound effect → ~177x effective positive weight, model collapses. Used neutral weights when applying BBSE.
- AP-4: External datasets → DISQUALIFIED per rules. Only Tata Steel-provided data used.

## 7. Results Summary

| Build | Public LB Score | Method |
|---|---|---|
| V4 (baseline) | 56.98 | LGB+XGB+CB stack + Platt |
| V36 (4-GBDT consensus) | 67.55 | 4 GBDT variants (Spearman 0.89-0.98) |
| V38 (5-paradigm + AutoGluon) | 66.36 | Added AutoGluon (test Spearman 0.92 collapsed) |
| **V42 K=197** | **71.69811** | **Multi-paradigm + anchor + K-sweep** |

Lift over V4 baseline: **+14.72 LB points**.

## 8. References

- Lipton, Wang, Smola (ICML 2018) — "Detecting and Correcting for Label Shift with Black Box Predictors"
- Zhu et al. (Sensors 2023, PMC10346850) — KPLS-based steel strip quality monitoring (per-stand residual physics)
- Hollmann et al. (arXiv:2502.17361) — TabPFN v2
- Sugiyama et al. (JMLR 2007) — Importance-Weighted Cross Validation

## 9. File Manifest

- `APPROACH.md` — This document
- `main.ipynb` — End-to-end notebook reproducing the V42 K=197 submission
- `feature_engineering.py` — Stand-residual + auxiliary feature pipeline (fold-isolated)
- `train_v35.py` — 9-model rank-average paradigm
- `train_v39.py` — CoilID cyclic-features paradigm
- `train_v40.py` — Defect-proximity (CV-safe) paradigm
- `train_v41.py` — BBSE-reweighted paradigm
- `consensus_union_v42.py` — Consensus voting + K-sweep
- `submission_final.csv` — Final predictions (339 rows, K=197 positives)
- `V4_baseline_approach.md` — V4 reference architecture documentation
- `requirements.txt` — Python dependencies
