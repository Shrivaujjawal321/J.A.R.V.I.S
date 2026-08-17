# V2 Approach - Tata Steel Defect Detection

## Problem
Binary classification: predict defect (Y=1) in 339 test coils.
Criteria: Recall=100% AND Precision>90% simultaneously.

## Dataset
- Train: 1352 rows, 66 positives (4.88% defect rate)
- Test: 339 rows
- 49 sensor features + CoilID

## What V1 Taught Us
- OOF AUC = 0.827 (real signal exists)
- 3 of 5 folds stopped at round 1-17 (fold instability)
- Test positive rate = 46% (model over-flagging)
- Precision @ R=1.0 = 5.9% vs target 90%
- Gap: need FP <= 7 at full recall, had FP=1166

## V2 Fixes Applied

### Fix 1: Fold Stability
- Removed is_unbalance=True (was competing with SMOTE)
- Switched to fixed 250 rounds (no early stopping)
- Root cause: 13 val positives gives AUC noise sigma=0.017 per step - killed early stopping
- Result: ALL 5 folds now run 250 rounds (vs min=1 in v1)

### Fix 2: SMOTE Inside CV Folds
- Applied SMOTE(sampling_strategy=0.3, k_neighbors=3) ONLY on training split
- Validation untouched (zero leakage)
- Each fold: 53 real positives -> 308 synthetic+real positives
- Result: Better probability spread on OOF (defect median 0.065 vs non-defect 0.0005)

### Fix 3: IsolationForest Meta-Feature
- Fit on full train (unsupervised - no leakage risk)
- iso_score = anomaly score (more negative = more anomalous)
- Defect coils score -0.476 vs non-defect -0.455 (delta = -0.02, correct direction)
- iso_score ranks 17th in feature importance (just outside top 15)

## V2 Results
- OOF AUC: 0.850 (v1: 0.827, +0.023 improvement)
- Precision @ R=1.0: 0.054 (v1: 0.059, slight regression at extreme threshold)
- Recall @ P>=0.90: 0.0 (unchanged - not achievable with current approach)
- Test positive rate @ thr=0.001: 39.5% (v1: 46.3%, improved)
- Fold stability: ALL 5 folds ran 250 rounds (v1 min = 1 round)

## Honest Assessment
V2 improves AUC (+2.3%), fold stability (solved), and proba spread.
But the fundamental gap remains: we need FP<=7 at R=1.0, and the model cannot
learn a decision boundary achieving this with 66 positive examples.

The precision-recall curve tops at ~50% precision at recall=6% -- this is a
fundamental feature separability limit, not a hyperparameter issue.

## Submission Choice
Threshold = 0.001 (OOF: Recall=89.4%, Precision=10.5%)
- Better than all-positive (Prec=5%)
- Maximizes recall while keeping precision above base rate
- 134/339 test rows flagged (39.5%)

## V3 Plan
1. Stacking ensemble (LightGBM + XGBoost + LogReg meta-learner)
2. SHAP feature selection (top 30) + polynomial interactions of top-5
3. Probability calibration (Platt scaling)
