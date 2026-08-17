# V4 Approach — Tata Steel Defect Detection

## Problem
Binary classification: predict defect (Y=1) in 339 test coils. 49 anonymized sensor features + CoilID. Train 1352 rows, 66 positives (4.88% defect rate). Test 339 rows.

Scoring (reverse-engineered from V2 LB): `(Recall + Precision) / 2 × 100`.

## Lineage
- V1: Baseline LightGBM. OOF AUC 0.827.
- V2: SMOTE inside folds + IsolationForest meta-feature + fixed-rounds (no early stopping noise). OOF AUC 0.850. **LB = 50.19** (Recall 89%, Precision 11%).
- V3: Stacking (LGB + XGB + CatBoost → LR meta) + SHAP top-30 + polynomial interactions on top-5 + Platt calibration + score-aware threshold sweep. OOF (R+P)/2 = 53.35.
- V4 (this): V3 + **coil-neighbor temporal features** + pseudo-label experiment (failed, dropped).

## V4 — What Was Added

### 1. Coil-Sequence Autocorrelation Discovery
CoilIDs are interleaved across train/test (no gaps). Defect-state propagates between consecutive coils:
- `P(defect | prev=defect) = 0.258` vs baseline `0.049` — **5.28× lift**, χ² p ≈ 0
- Lag-2 lift: 2.79×. 17 consecutive defect pairs in training data.

### 2. Coil-Neighbor Features (priority 1 from V3 retrospective)
- Lag-1, lag-2 of X13, X10, X36, X14 (and X13/X36 ratio)
- First differences (`X13_diff1`, etc.)
- Rolling-window stats (window=5): mean, std, max of X13/X10/X36
- **CV-safe target-encoded `prev_5_defect_rate`** — for each row, defect rate of previous 5 coils, computed only from each fold's training labels

### 3. Re-stacked Ensemble on V4 Feature Set
51 features = 30 SHAP-selected + 15 polynomial + 6 selected neighbor.
- LightGBM OOF AUC: 0.8615
- XGBoost OOF AUC: 0.8668 (+0.008 vs V3)
- CatBoost OOF AUC: 0.8756 (+0.018 vs V3) — neighbor features land hardest here
- **Meta (LR + Platt cal) OOF AUC: 0.8837 (+0.017 vs V3)**

### 4. Pseudo-Labeling — Tried, Failed
Added test rows with proba < 0.05 as pseudo-negatives. Meta AUC dropped to 0.851 → 0.524 OOF score. Lesson: adding redundant negatives makes the precision math harder, not easier. Dropped.

### 5. Score-Aware Threshold
Exact unique-threshold sweep on OOF (~1352 sample points). Best (R+P)/2 at T=0.01428: **OOF 54.31** (R=100%, P=8.62%).

## V4 Results
- Meta OOF AUC: 0.8837 (+0.017 vs V3, +0.034 vs V2)
- OOF (R+P)/2: **54.31**
- Bootstrap 95% CI on score: [53.36, 55.34] — robustly above V2 LB (50.19)
- Stability across 200× 80% subsamples: std 0.049 (very stable)
- Test positive rate at chosen T: 154/339 = 45.4%

## Honest Assessment

V4 lifts predicted LB by ~1 point vs V3 and ~4 points vs V2 baseline. The improvement is real but small.

**The gap to top 10 (cutoff ~74) is now confirmed to be a feature-engineering gap, not a modeling gap.** Tree-based stacking + neighbor features + polynomial interactions cannot crack the "hard tail" — ~7 defects with OOF proba ≤ 0.025 that are genuinely indistinguishable from non-defects in the current feature space.

To reach top 10, V5 needs **physics-informed features** mapping X1–X49 to actual hot-rolling process variables (roll force per unit width, finishing-temperature deviation from Ar3, FT/CT ratio, Ekelund-flow-stress-normalized force).

## Submission Choice
Chosen threshold = 0.01428 (T_max_score from sweep)
- OOF: R=100%, P=8.62%, score=54.31
- Test: 154/339 flagged (45.4%)
- Strategy: maximize-recall posture (every missed defect costs 0.76 recall points; every spurious positive costs ~0.07 precision points — recall-leaning is geometrically correct)

## V5 Plan (in progress)
- Map X1–X49 to process variables via value-range analysis + published HSM literature
- Add Tier-1 physics features (F/w, FT/CT, Ar3 deviation, lambda, Ekelund normalization)
- Refit stacking on enlarged feature set
- Target predicted LB: 60+
