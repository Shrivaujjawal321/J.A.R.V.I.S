# Tata Steel AI Hackathon 2026 - Round 1
# BUILD V2 REPORT: Defect Detection in Hot Rolling

**Date:** 2026-05-22
**Engineer:** ML Engineering Specialist (Jarvis)
**Status:** V2 submitted -- AUC improved, fold stability solved, criteria not yet met

---

## 1. V1 vs V2 Comparison

| Metric | V1 | V2 | Delta |
|--------|----|----|-------|
| OOF AUC | 0.827 | 0.850 | +0.023 |
| Recall @ P>=0.90 | 0.0 | 0.0 | no change |
| Precision @ R=1.0 | 0.059 | 0.054 | -0.005 |
| Test positive rate | 46.3% | 39.5% | -6.8% |
| Min fold iterations | 1 | 250 | +249 |
| Criteria met | NO | NO | -- |

---

## 2. V2 Per-Fold Results

| Fold | AUC | Iterations | SMOTE pos | R@0.5 | P@0.5 |
|------|-----|------------|-----------|-------|-------|
| 1 | 0.804 | 250 (FIXED) | 53->308 | 0.000 | 0.000 |
| 2 | 0.887 | 250 (FIXED) | 52->308 | 0.286 | 1.000 |
| 3 | 0.767 | 250 (FIXED) | 53->308 | 0.000 | 0.000 |
| 4 | 0.914 | 250 (FIXED) | 53->308 | 0.231 | 0.333 |
| 5 | 0.885 | 250 (FIXED) | 53->308 | 0.154 | 0.500 |
| **OOF** | **0.850** | all 250 | -- | -- | -- |

---

## 3. What Each Fix Did

### Fix 1: Fold Stability -- SOLVED
- Root cause diagnosed: val set has only 13 positives per fold
- AUC noise sigma = 0.017 per evaluation step
- Early stopping with patience=100 was killing good folds after 18-30 rounds
  (the fold stopped not because it converged, but because noisy AUC hit a dip)
- Solution: Removed early stopping, fixed 250 rounds for ALL folds
- Result: ALL 5 folds now train fully (v1 min was 1 round)

### Fix 2: SMOTE Inside CV Folds -- APPLIED
- SMOTE(sampling_strategy=0.3, k_neighbors=3) on TRAIN only (val untouched)
- 53 real positives -> 308 synthetic+real per fold training set
- Proba spread improved: defect median=0.065 vs non-defect median=0.0005
  (v1 had proba floor=0.014 with near-identical values for all rows)
- OOF AUC improved 0.827 -> 0.850
- Note: is_unbalance=True was removed (was competing with SMOTE, causing fold collapse)

### Fix 3: IsolationForest Meta-Feature -- ADDED
- Fit on full train set (unsupervised, no leakage)
- Defect coils score: -0.476 vs non-defect: -0.455 (correct direction)
- Feature importance rank: 17th / 96 (just outside top 15)
- Modest contribution -- not a game-changer but adds orthogonal signal

---

## 4. Honest Assessment: Why Criteria Still Not Met

### The math is harsh:
- To achieve Recall=1.0 AND Precision=0.90: need TP=66, FP<=7
- At threshold where all 66 defects are caught: FP = 1,166
- Precision = 66/(66+1166) = 5.4%
- To reach P=0.90 we need to eliminate 1,159 false positives

### The precision-recall frontier of this feature set:
- Maximum achievable precision: ~50% at recall=6% (3-4 defects caught)
- At recall=90%: precision=9% (FP=602)
- At recall=100%: precision=5.4% (FP=1166)
- This is NOT a hyperparameter problem -- it is a feature separability limit

### Why AUC improved but criteria didn't:
- AUC measures ranking quality -- v2 is better at ordering defects above non-defects
- But the ABSOLUTE proba values still don't create a clean enough gap
- The hardest defects (bottom decile of defect probas: 0.0001-0.001) are
  indistinguishable from ~1,000 non-defect coils at those proba levels
- Better AUC = better ranking. Criteria requires near-perfect separation.

---

## 5. Submission Decision

**Threshold: 0.001**
- OOF: Recall=89.4% (59/66), Precision=10.5%
- Test: 134 positive / 339 (39.5%)
- Rationale: Best recall above base-rate precision. Not "flag everything" (46% in v1), not "flag nothing."

---

## 6. Top 3 V3 Ideas (if criteria must be met)

### Idea 1: STACKING ENSEMBLE (Highest impact)
- Level-1 models: LightGBM (v2) + XGBoost (same SMOTE inside folds) + Logistic Regression
- Level-2 meta-learner: Logistic Regression on OOF predictions from all 3 level-1 models
- Why: Ensemble diversity improves precision-recall frontier. Each model makes
  different error patterns; the meta-learner learns which to trust.
- Expected: +5-15% precision at same recall
- Cost: Medium (3x training time)

### Idea 2: SHAP FEATURE SELECTION + POLYNOMIAL INTERACTIONS
- Run SHAP on v2 fold models, keep top 25-30 features, retrain
- Add degree-2 polynomial interactions of top-5 SHAP features:
  X13_over_X36 * X14, X14 * X16, etc.
- Why: 96 features for 1352 samples is high ratio (=14:1).
  Noise features hurt the boundary at extreme thresholds.
  Focused features + cross-terms encode physical process better.
- Expected: Tighter proba separation, fewer FP at high recall
- Cost: Low

### Idea 3: PROBABILITY CALIBRATION (Platt Scaling)
- Post-hoc calibrate OOF probas: CalibratedClassifierCV with sigmoid method
- Apply calibration on held-out OOF fold
- Why: Calibrated probas are better-spread across [0,1]; threshold selection
  becomes more predictable and stable at extreme operating points.
- Apply isotonic regression (more flexible) as variant if Platt underfits
- Expected: Better threshold stability, ~2-5% precision improvement
- Cost: Very low (no retraining)

### Why these three and in what order:
1. Stacking first -- most likely to change the precision ceiling, not just tune it
2. Feature selection + polynomials -- removes noise that blurs the boundary
3. Calibration -- quick win, run it alongside v3 regardless

---

## 7. Files Generated

```
build_v2/
+-- 01_load_features.py      # IsolationForest meta-feature
+-- 02_train_v2.py           # Fixed 250-round LightGBM + SMOTE in fold
+-- 03_threshold_tune.py     # OOF precision-recall sweep
+-- 04_predict_submit.py     # Test prediction + CoilID-aware submission
+-- 05_compare_v1.py         # Comparison script (syntax fix pending)
+-- approach.md              # 1-page approach summary
+-- solution.ipynb           # Notebook version
+-- expected_submission.csv  # 339 rows, CoilID + Y
+-- train_v2.parquet         # v1 features + iso_score (1352 x 98)
+-- test_v2.parquet          # v1 features + iso_score (339 x 97)
+-- oof_v2.parquet           # OOF predictions (CoilID, Y, oof_proba)
+-- test_probas_v2.parquet   # Test ensemble probas
+-- cv_summary_v2.json       # Per-fold metrics
+-- chosen_threshold_v2.json # Threshold decision + rationale
+-- feature_list_v2.json     # Feature list (96 features)
+-- figures/
|   +-- recall_precision_v2.png
+-- models/
    +-- fold_0.lgb through fold_4.lgb
```
