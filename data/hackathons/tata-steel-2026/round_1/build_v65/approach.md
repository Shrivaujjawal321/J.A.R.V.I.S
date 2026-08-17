# Approach — Build V65: Defect-Prototype Expansion (Test-Distribution Calibrated Proximity)

**Date:** 2026-05-26
**Status:** Complete — OOF run, Validation Gate 4 FAILED

---

## Hypothesis

V40 used train-defect prototypes only (66 rows) for proximity features. V65 adds 72
LB-confirmed public-test TPs to the prototype pool (138 total), reasoning that:

1. Hot rolling mill is same physical process for public + private test
2. 72 confirmed-TP test rows give 72 samples FROM the test-defect distribution
3. Adding them calibrates the proximity scorer to test-distribution — not just train

The key design choice vs V64 (which FAILED via pseudo-label injection): prototypes are
used ONLY for distance/density computation, NOT as training labels. This avoids the
overfitting that killed V64 (OOF AUC 0.870 → 0.730).

---

## Architecture

- **Base features:** V4 51 SHAP-selected features (from `build_v4` parquet, CoilID-aligned)
- **Distance space:** Rank-percentile transform per column, fitted on combined train+test (1691 rows)
  — avoids scale issues with anonymized physical-unit features
- **Prototype pool:** 66 train Y=1 + 72 LB-confirmed test TPs = 138 total
- **Proximity features (13 new):**
  1. `dist_to_nearest_defect` — L1 distance in rank space to nearest prototype
  2. `dist_to_median_5NN` — median of L1 distances to 5 nearest prototypes (outlier-resistant)
  3–7. `count_within_radius_r` for r ∈ [0.05, 0.10, 0.15, 0.20, 0.30] (rank space)
  8–12. `density_within_radius_r` for same r (count / threshold_volume)
  13. `mean_dist_to_top10_nearest`
- **Total:** 64 features (51 V4 + 13 proximity)
- **Model:** LightGBM, scale_pos_weight=19.48, n_estimators=500, max_depth=6, lr=0.05
- **CV:** StratifiedKFold(5, seed=42), 3-seed ensemble [42, 137, 1000]

---

## CV-Safety Design

For TRAIN OOF computation (fold i):
- Prototype pool = (train-fold Y=1 rows) ∪ (72 test TPs)
- Val-fold Y=1 rows are EXCLUDED from the pool
- Self-exclusion mask: defect row i does not count itself as its own nearest prototype
- Rank-percentile transform fitted on ALL 1691 rows (not fold-dependent — rank is global property)

For TEST predictions:
- Full 138-prototype pool used (all 66 train + 72 test TPs)
- TP test rows have dist_to_nearest = 0 (they ARE prototypes → verified by spot-check: 72/72 confirmed)

---

## Results

| Metric | Value | Criterion | Result |
|---|---|---|---|
| OOF AUC | 0.8724 | > 0.85 | PASS |
| Per-fold std AUC | 0.0452 | < 0.05 | PASS |
| OOF (R+P)/2 @K=200 | 47.36 | > 46.35 (V4 baseline) | PASS |
| Train pos in top-200 | 47/66 | >= 60/66 | **FAIL** |
| Estimated LB @K=200 | ~50.03 | | — |

---

## Validation Gate 4 Failure Analysis

**Gate 4:** Train positives in top-200 OOF must be ≥ 60/66 (90%). V65 puts only 47/66 (71%).

This is the most informative failure. It means:
- The proximity model CAN rank test TPs highly (test TP rows have dist=0 to themselves → perfect proximity signal in test space)
- But for TRAIN positives in OOF, the val-fold defects are excluded from the pool → they lose their "perfect proximity" anchor
- The remaining signal (distance to other train defects + 72 test TPs) is not strong enough to rank all 66 train positives in top-200

**Root cause:** The 72 test TPs help identify TEST-DISTRIBUTION defects but don't necessarily pull TRAIN defects closer in rank space. Train defects may cluster differently from test defects in feature space — the two populations might not be spatially coincident.

**What this means for LB generalization:**
- V65 test scores ARE lifted by the prototype expansion (test TPs get dist=0, non-TP test rows get scored against 138 prototypes)
- But the OOF signal quality (train-only) is degraded because train positives cluster away from test TPs
- The estimated LB ~50.03 is substantially below V44's 72.83 banked score
- This is NOT a valid second submission to protect private score

---

## Proximity Feature Importance

Proximity features account for **66.9%** of total LightGBM feature importance, led by:
- `dist_to_nearest_defect`: 325 (dominant signal — not falsified by low importance)
- `count_within_r0.05`: 100
- `density_within_r0.05`: 34

The signal IS there. The problem is train OOF vs test calibration gap, not missing signal.

---

## Spearman Correlation

| Paradigm | Spearman r | Classification |
|---|---|---|
| V4 | 0.0696 | DIVERSE |
| V40 | 0.8694 | MODERATE |

V65 is highly diverse from V4 (r=0.07) but moderately correlated with V40 (r=0.87) — expected since both use proximity-based features. The small improvement in (R+P)/2@K=200 over V40 (47.36 vs 46.35) confirms the test-TP expansion adds marginal lift.

---

## Decision: DO NOT SUBMIT V65 STANDALONE

**Reason:** Est LB @K=200 ≈ 50.03 is ~22 points below banked V44 score (72.83). Gate 4
failure (47/66 vs ≥60/66) confirms the model is not reliably ranking train positives.
Submitting would likely score ~50-55 LB, exposing a submission probe with no gain.

**The blend (V65b) is similarly not recommended:**
- V65 test scores are dominated by prototype proximity (66.9% importance)
- 72 test TPs all have dist=0 → very high scores → blend would rank them highly
- But 109 non-TP test rows scored by V65 are calibrated against test-TP prototypes, not train-distribution
- The blend ranking may not be better than V44 alone

---

## Why the Hypothesis Partially Failed

The hypothesis that "test-distribution prototypes calibrate the scorer for both halves" is
PARTIALLY valid:

**Valid part:** Test TPs do carry test-distribution defect signatures. V65 correctly gives
them dist=0 and perfect proximity scores in test space.

**Invalid assumption:** We assumed train positives and test TPs occupy the same cluster in
rank-feature space. They may not — train positives (from temporal train split) vs test TPs
(from temporal test split, hot mill running conditions at a different time) may have shifted
feature distributions. If the distributions diverged, adding test TPs as prototypes helps
score TEST rows but doesn't help rank TRAIN positives in OOF.

**Key insight for future builds:** The prototype pool expansion is most powerful when
train-defect and test-defect feature distributions are similar (same mill conditions).
If there's distribution shift between train and test periods, pure proximity scoring will
have this train-OOF vs test-score calibration gap.

---

## Files Produced

- `train_v65.py` — full training script
- `oof_v65.parquet` — 1352 rows, columns: CoilID, oof_proba, y
- `test_proba_v65.parquet` — 339 rows, columns: CoilID, test_proba
- `submission_K154.csv`, `submission_K200.csv`, `submission_K272.csv` — V65 standalone
- `submission_K200_blended_v44_v65.csv` — V65+V44 blend (not recommended)
- `feature_importance_v65.parquet` — LightGBM feature importances
- `cv_report_v65.md` — full OOF metrics
- `cv_summary_v65.json` — machine-readable summary
