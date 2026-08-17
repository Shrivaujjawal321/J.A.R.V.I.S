# Approach — Build V40: Defect-Proximity Features (Ratnesh iter36 recipe)

**Date:** 2026-05-24
**Status:** Complete — OOF run, NO LB submission

---

## Motivation

Ratnesh-Jarvis peer-disclosed iter36 at OOF AUC 0.9465 using "CV-safe defect-proximity"
(dist_to_nearest + 5 radius counts + 5 densities = 11 features). This build replicates
that recipe on our V4 51-feature base to (a) validate the idea and (b) generate a
maximally-diverse paradigm for the consensus union.

---

## Architecture

- **Base features:** V4 51 SHAP-selected features (ratios, poly interactions, IsoForest score,
  lag/rolling, prev5_defect_rate, c3_over_c2_mean)
- **Proximity features (11 new):**
  1. `dist_to_nearest_defect` — Euclidean distance in standardized 51-dim space to nearest Y=1 training row
  2–6. `count_within_radius_r` for r ∈ [0.5, 1.0, 1.5, 2.0, 3.0]
  7–11. `density_within_radius_r` for same r (count_Y1_within_r / count_all_train_within_r)
- **Total:** 62 features
- **Model:** LightGBM, scale_pos_weight=19.48, NO SMOTE, NO BBSE
- **CV:** StratifiedKFold(5, seed=42)

---

## CV-Safety Design (critical)

The proximity recipe has a subtle leakage trap: if a Y=1 train row computes its own
nearest-defect distance, it gets dist=0 (it's its own neighbour). LGB learns "dist=0 → class=1"
but val rows NEVER have dist=0 → model collapses to AUC=0.5.

**Fix applied (self-exclusion masks):**
- For each fold's train rows: build a boolean mask `(N_tr, N_defects)` where `mask[i,j]=True`
  iff row i and defect j are the same global row. The distance matrix entry is set to `inf`
  so it doesn't affect min/count.
- Similarly for the density denominator: `(N_tr, N_tr)` diagonal mask (self excluded from
  all-train count).
- Val rows: never in fold_defects → no self-exclusion needed.
- Test rows: use ALL-TRAIN defects (legitimate, no label leakage since test has no labels).
- Scaler fitted on TRAIN FOLD only (not val, not test).

This matches Ratnesh's "CV-safe" claim exactly.

---

## Results

| Metric | Value |
|---|---|
| OOF AUC | 0.8732 |
| Mean fold AUC | 0.8728 ± 0.0336 |
| Bootstrap 95% CI | [0.8539, 0.8966] |
| Delta vs V4 OOF AUC (0.8837) | -0.0105 |
| Delta vs Ratnesh iter36 (0.9465) | -0.0733 |
| OOF (R+P)/2 score | 48.68 |
| Best K | 254 |
| Estimated LB | 51.35 |
| V4 banked LB | 56.98 |
| Delta vs V4 banked LB | -5.63 |

---

## Paradigm Diversity

| Paradigm | Spearman r | Status |
|---|---|---|
| V4 (stacked 3-model) | 0.0343 | DIVERSE |
| V33 (single LGB + stand FE) | 0.0175 | DIVERSE |
| V34 (stacked + stand FE) | 0.0355 | DIVERSE |
| V35 (9-model rank-avg) | 0.0375 | DIVERSE |

All correlations well below 0.85. V40 is **maximally diverse** from all existing paradigms.
This is the primary value — not standalone AUC (which is below V4), but as a unique signal
for consensus ensemble / rank-fusion.

---

## Why V40 AUC < Ratnesh iter36 (0.9465)

Ratnesh's iter36 achieves 0.9465 vs our 0.8732 despite the same proximity recipe. Likely causes:

1. **Different base feature space:** Ratnesh's base features may be lower-dimensional or better
   structured for Euclidean distance. 51-dim distance in V4's engineered feature space (ratios,
   polynomial terms) is not the same as raw X feature space or a PCA-reduced space.
2. **PCA pre-reduction:** Ratnesh likely reduces to top-k principal components before computing
   proximity — distances in a 10-20 dim space are cleaner than 51-dim.
3. **Different standardization:** Ratnesh may standardize per-feature with robust scaler vs
   standard scaler, reducing outlier influence on distance.
4. **Training data composition:** Unknown if Ratnesh uses all 49 raw X features vs 51 engineered.

**Follow-up to test:** Compute proximity in PCA(10) space of raw X1-X49 features instead of
51-dim V4 space. Expected to tighten distance distribution and improve AUC.

---

## Top-3 Risks

1. **Curse of dimensionality:** 51-dim Euclidean distance with 66 positives in 1352 rows is
   inherently noisy. Nearest-defect distances are large (mean ~6 std units) and may not be
   meaningful separators.

2. **OOF→LB calibration:** The V4 +2.67 delta was calibrated for V4's stacked ensemble. Single
   LGB OOF→LB delta may differ. Treat Est LB 51.35 as rough estimate.

3. **K=254 threshold instability:** Best K=254 is substantially higher than V4's K=154 and
   V35's K=170. This reflects a different score distribution; the threshold may not hold on LB.

---

## Consensus Union Recommendation

**YES** — include V40 as a diversity component in the consensus union.

V40 adds a fundamentally different signal (defect-proximity in feature space) that is nearly
orthogonal to all other paradigms (Spearman r < 0.04 vs all). Even though standalone AUC
(0.8732) is below V4 (0.8837), the ultra-low correlation means rank-fusion with V40 can
uncover defects that GBDT-based models miss entirely.

Suggested fusion weight: 0.5x relative to V35/V34 (downweighted due to lower standalone AUC
and higher K instability).

---

## Files Produced

- `train_v40.py` — full training script
- `oof_v40.parquet` — 1352 rows, columns: CoilID, oof_proba, y
- `test_proba_v40.parquet` — 339 rows, columns: CoilID, test_proba
- `cv_report_v40.md` — full CV metrics
- `cv_summary_v40.json` — machine-readable summary
- `expected_submission.csv` — K=254 threshold, 254 positives (DO NOT SUBMIT STANDALONE)
