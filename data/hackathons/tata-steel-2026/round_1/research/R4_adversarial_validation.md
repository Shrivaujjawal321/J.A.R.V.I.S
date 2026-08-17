# R4 — Adversarial Validation for Tata Steel Round 1

**Date:** 2026-05-24
**Target:** LB 72.83 → 80+
**Current best:** V10 OOF AUC 0.8936, calibrated LB ~58 (V4 banked 56.98)
**Problem:** Train 5% defect prevalence, test ~45% — severe label + covariate shift. OOF AUC caps at 0.89 partly because train distribution doesn't represent test.

---

## Quick Answer

Adversarial validation trains a binary classifier (train=0, test=1) to identify which features differ most between train and test splits. These divergent features dilute model signal. Two correction strategies exist: (A) drop the top divergent features, (B) weight train samples by density ratio `w = p_test(x) / p_train(x) ≈ p̂/(1-p̂)` from the adversarial classifier. Uber's production deployment of strategy A showed 1.2–5.5% AUC improvement. Strategy B is theoretically sound but empirically fragile on small datasets. **For our 1,400-row train with 70 defects, strategy A (feature dropping) is higher confidence than strategy B (density ratio weighting).**

---

## 1. The Two Shift Problems We Face

This dataset has **two simultaneous shifts**, not one:

### 1a. Label Shift (Prior Shift)
P(Y=1) = 5% in train, ~45% in test. The marginal label distribution changed. This is the dominant problem.

- Under label shift, the Bayes-optimal threshold at prediction time needs adjustment
- BBSE correction: estimate test prevalence from model's soft predictions, rescale posteriors
- Formula: `w_class = P_test(y) / P_train(y)` — for positives this is `0.45/0.05 = 9×` upweight

### 1b. Covariate Shift (Feature Distribution Shift)
P(X) differs between train and test — some process-control features (X39, X42 zone behavior, rolling-schedule patterns) may appear in different distributions across the two splits.

- Corrected by adversarial validation + density-ratio sample weights
- Formula: `w(x) = P_test(x) / P_train(x) ≈ p̂(x)/(1 - p̂(x))` where p̂(x) = adversarial classifier output

**Key distinction:** Label shift and covariate shift require different corrections. Applying covariate-shift weights when the true shift is label shift can make things worse.

---

## 2. Adversarial Validation Pipeline

### Step 1 — Build the adversarial dataset

```python
import pandas as pd
import numpy as np
from lightgbm import LGBMClassifier
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import roc_auc_score

# Load your train and test feature sets (49 raw + 56 engineered = 105 features)
# X_train: (N_train, 105), X_test: (N_test, 105)

adv_X = pd.concat([X_train, X_test], axis=0, ignore_index=True)
adv_y = np.concatenate([np.zeros(len(X_train)), np.ones(len(X_test))])

# Shuffle
idx = np.random.permutation(len(adv_X))
adv_X, adv_y = adv_X.iloc[idx], adv_y[idx]
```

### Step 2 — Train adversarial LightGBM (shallow, fast)

```python
adv_clf = LGBMClassifier(
    n_estimators=300,
    max_depth=4,          # shallow — don't overfit to tiny differences
    learning_rate=0.05,
    num_leaves=15,
    subsample=0.8,
    colsample_bytree=0.8,
    class_weight='balanced',  # equal train/test counts usually, but be safe
    random_state=42,
    verbose=-1
)

# Use 5-fold CV to get OOF probabilities (needed for density ratios)
skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
adv_proba_oof = np.zeros(len(adv_X))

for fold_idx, (tr_idx, val_idx) in enumerate(skf.split(adv_X, adv_y)):
    adv_clf.fit(adv_X.iloc[tr_idx], adv_y[tr_idx])
    adv_proba_oof[val_idx] = adv_clf.predict_proba(adv_X.iloc[val_idx])[:, 1]

adv_auc = roc_auc_score(adv_y, adv_proba_oof)
print(f"Adversarial AUC: {adv_auc:.4f}")
# AUC > 0.70 → significant distribution shift confirmed
# AUC 0.50-0.55 → distributions are similar → adversarial correction won't help
```

### Step 3 — Extract feature importance to identify divergent features

```python
# Retrain on full adversarial dataset for stable importances
adv_clf.fit(adv_X, adv_y)

feat_imp = pd.DataFrame({
    'feature': adv_X.columns,
    'importance': adv_clf.feature_importances_
}).sort_values('importance', ascending=False)

print(feat_imp.head(20))
# Features at top are the ones that most reliably distinguish train from test
# These are your highest-risk features for train→test distribution shift
```

### Step 4 — Get density ratios for train samples

```python
# Re-extract train probabilities (probability of being test)
# Use OOF proba for train rows (index 0:N_train)
train_adv_proba = adv_proba_oof[:len(X_train)]

# Density ratio: p_test(x) / p_train(x) = p̂ / (1 - p̂)
# p̂ here is P(sample is test | features)
density_ratio = train_adv_proba / (1.0 - train_adv_proba + 1e-8)

# CRITICAL: clip extreme weights (a few samples with high p̂ will blow up)
density_ratio_clipped = np.clip(density_ratio, a_min=0.01, a_max=10.0)

# Normalize to mean 1.0 so total effective sample count is preserved
density_ratio_clipped /= density_ratio_clipped.mean()

print(f"Weight stats: min={density_ratio_clipped.min():.3f}, "
      f"max={density_ratio_clipped.max():.3f}, "
      f"mean={density_ratio_clipped.mean():.3f}")
```

---

## 3. Two Correction Strategies

### Strategy A — Feature Dropping (Recommended for our dataset)

Uber's production system: iteratively remove top-importance divergent features until adversarial AUC drops below threshold (θ_auc = 0.55–0.60). Result: 1.2–5.5% AUC improvement across 6 datasets. More robust than reweighting for small samples.

```python
ADVERSARIAL_AUC_THRESHOLD = 0.58  # stop when shift is no longer detectable
features_to_drop = []
current_features = list(adv_X.columns)

while True:
    clf_iter = LGBMClassifier(n_estimators=200, max_depth=4, verbose=-1)
    auc_iter = cross_val_score(clf_iter, adv_X[current_features], adv_y,
                               cv=5, scoring='roc_auc').mean()
    
    if auc_iter < ADVERSARIAL_AUC_THRESHOLD:
        print(f"Shift reduced to AUC {auc_iter:.4f}. Stopping.")
        break
    
    clf_iter.fit(adv_X[current_features], adv_y)
    top_feature = pd.Series(clf_iter.feature_importances_,
                            index=current_features).idxmax()
    features_to_drop.append(top_feature)
    current_features.remove(top_feature)
    print(f"Dropped {top_feature}, adversarial AUC was {auc_iter:.4f}")

print(f"\nTotal features dropped: {len(features_to_drop)}")
print(f"Dropped: {features_to_drop}")
```

### Strategy B — Density Ratio Sample Weighting

Apply computed `density_ratio_clipped` as `sample_weight` in LightGBM. Train samples that look like test data get upweighted; those that look unlike test get downweighted.

```python
# Apply to LightGBM training
import lightgbm as lgb

lgb_train = lgb.Dataset(
    X_train[current_features],
    label=y_train,
    weight=density_ratio_clipped   # <-- here
)

params = {
    'objective': 'binary',
    'metric': 'auc',
    'class_weight': 'balanced',
    'num_leaves': 31,
    'learning_rate': 0.05,
    'n_estimators': 500,
}

# Or via sklearn API:
lgb_model = LGBMClassifier(**params)
lgb_model.fit(
    X_train[current_features], y_train,
    sample_weight=density_ratio_clipped
)
```

**Caution on Strategy B:** Inverse propensity weighting was found to "perform worse than baseline" in Uber's production system (2020 paper, arxiv 2004.03045). For our 1,400 train rows with only 70 defects, clipping at 10× still leaves a handful of samples with 10× influence — very destabilizing for a minority-class problem.

### Strategy C — Importance-Weighted Cross-Validation (IWCV)

Rather than reweighting the model, use the density ratios to weight the OOF validation score. This ensures your CV metric better reflects test distribution performance.

```python
from sklearn.metrics import roc_auc_score

# After OOF predictions, weight the AUC estimate by how "test-like" each
# train row is
def iwcv_auc(y_true, y_pred_proba, importance_weights):
    """
    Importance-weighted AUC approximation.
    Upweights validation rows that look like test data.
    """
    # Sort by predicted probability
    sorted_idx = np.argsort(y_pred_proba)[::-1]
    y_sorted = y_true[sorted_idx]
    w_sorted = importance_weights[sorted_idx]
    
    # Weighted AUROC via trapezoidal rule
    tp_cumsum = np.cumsum(y_sorted * w_sorted)
    fp_cumsum = np.cumsum((1 - y_sorted) * w_sorted)
    
    tp_rate = tp_cumsum / tp_cumsum[-1]
    fp_rate = fp_cumsum / fp_cumsum[-1]
    
    return np.trapz(tp_rate, fp_rate)

# Use this as OOF metric instead of plain roc_auc_score
# Gives a CV estimate closer to what you'll see on test
```

---

## 4. Label Shift Correction (BBSE — directly applicable to our problem)

Our dominant shift is **label shift** (5% → 45%), not primarily covariate shift. BBSE is the correct tool here.

```python
# After training your model on train (5% prevalence),
# it outputs calibrated P(Y=1|X) in [0,1]
# These probabilities are calibrated for train distribution

# Step 1: Get model soft predictions on test set
test_proba = model.predict_proba(X_test)[:, 1]

# Step 2: Estimate test prevalence (Lipton et al. 2018 BBSE-soft)
# Under label shift: E_test[p(x)] ≈ P_test(Y=1) * E_train[p(x)|Y=1]
#                                   + P_test(Y=0) * E_train[p(x)|Y=0]
# Solve for P_test(Y=1):

# Get train-domain expected values conditioned on label
p_pos_train = np.mean(model.predict_proba(X_train[y_train==1])[:, 1])  # E[p̂|Y=1]
p_neg_train = np.mean(model.predict_proba(X_train[y_train==0])[:, 1])  # E[p̂|Y=0]
p_test_mean = np.mean(test_proba)  # E_test[p̂]

# Solve: p_test_mean = q * p_pos_train + (1-q) * p_neg_train
# q = (p_test_mean - p_neg_train) / (p_pos_train - p_neg_train)
q_test = (p_test_mean - p_neg_train) / (p_pos_train - p_neg_train + 1e-10)
q_test = np.clip(q_test, 0.01, 0.99)
print(f"Estimated test prevalence: {q_test:.3f}")  # should be ~0.45 if shift is real

# Step 3: Rescale posterior probabilities for test distribution
# P_test(Y=1|x) ∝ P_train(Y=1|x) × (q_test / q_train)
# where q_train = observed train prevalence
q_train = y_train.mean()  # ~0.05

# Bayes-adjusted posterior:
# p_calibrated = p̂ × (q_test / q_train) /
#                [p̂ × (q_test/q_train) + (1-p̂) × (1-q_test)/(1-q_train)]
ratio = (q_test / q_train) / ((1.0 - q_test) / (1.0 - q_train))
test_proba_adjusted = (test_proba * ratio) / (test_proba * ratio + (1.0 - test_proba))

# Now threshold at 0.5 (or sweep) on test_proba_adjusted
# This is the correct threshold for a 45%-prevalence population
```

**This is directly applicable to our V44 pipeline.** Our model was trained on 5% prevalence; test is 45% prevalence. The OOF AUC is computed on 5%-prevalence holdouts which do NOT represent test. BBSE rescaling adjusts for this.

---

## 5. Predicted Divergent Features in Our Dataset

Based on domain knowledge + adversarial validation theory, these are the features most likely to drive train→test separation:

| Rank | Feature | Why It Likely Diverges |
|------|---------|----------------------|
| 1 | **X39 (rolling mill parameter)** | Hot-zone [158-162] has 11-24% defect rate — test is likely sampled from this operational regime disproportionately. Train contains more "normal run" rows. |
| 2 | **X42 (chemistry gate, >0.025 threshold)** | EDA showed X42 > 0.025 eliminates 41% of test with zero FN — test is disproportionately from X42-high regime. |
| 3 | **Temporal coil-neighbor features** (rolling means of adjacent coils) | These were engineered from temporal ordering. If test coils are from a different production campaign than train, neighbor statistics will diverge systematically. |
| 4 | **X18 (finishing temperature FT)** | FT varies by steel grade and campaign; if test covers grades/campaigns not well-represented in train, X18 distribution will shift. |
| 5 | **Any within-grade z-score features** | Z-scores computed on train grade populations. If test has different grade mix, z-scores computed at train time don't generalize. |

**Run the adversarial classifier to confirm — these are hypotheses, not confirmed divergences.** The classifier will rank them objectively.

---

## 6. Application to V44 Stacking Meta-Learner

If we proceed to V45 with a stacking meta-learner trained on V44 OOF predictions:

### Without adversarial correction (current state)
Meta-learner trained on OOF rows from 5%-prevalence folds. When applied to 45%-prevalence test, it's systematically miscalibrated.

### With BBSE label-shift correction (recommended path)
```python
# V44 OOF predictions are in shape (N_train,)
# y_train labels are known

# Estimate how meta-model's OOF predictions should shift
# to match the test prevalence the meta-model will actually see

# Step 1: Get V44 OOF proba for meta-training
meta_X_train = v44_oof_proba.reshape(-1, 1)  # or multi-col if multiple base models
meta_y_train = y_train

# Step 2: Estimate test prevalence from test predictions
meta_test_proba = base_model.predict_proba(X_test)[:, 1]
q_test_estimated = estimate_prevalence_bbse(meta_test_proba, y_train, base_model, X_train)

# Step 3: Weight OOF rows for meta-training
# Rows where y=1: weight = q_test / q_train (upweight positives 9×)
# Rows where y=0: weight = (1 - q_test) / (1 - q_train) (downweight negatives)
q_train = y_train.mean()  # 0.05
meta_weights = np.where(
    y_train == 1,
    q_test_estimated / q_train,                          # ~9.0 for positives
    (1 - q_test_estimated) / (1 - q_train)               # ~0.58 for negatives
)

# Normalize
meta_weights /= meta_weights.mean()

# Step 4: Train meta-learner with these weights
meta_clf = LogisticRegression(C=0.1)
meta_clf.fit(meta_X_train, meta_y_train, sample_weight=meta_weights)
```

### With adversarial covariate-shift weights (secondary, if adversarial AUC > 0.70)
Use `density_ratio_clipped` from Step 4 of the adversarial pipeline to further weight OOF rows. Combine with BBSE weights multiplicatively (clipped at 20× total).

---

## 7. Expected Lift Estimate

| Method | Basis | Expected LB Delta | Confidence |
|--------|-------|-------------------|------------|
| Feature dropping (adversarial AUC > 0.70) | Uber MaLTA: +3.9% AUC; AutoML3: +1.2-5.5% AUC | +1.5 to +4.0 LB points | Medium |
| BBSE label-shift correction on threshold | Lipton 2018: theoretically correct under pure label shift | +0 to +3.0 LB points (via better threshold) | Medium-High |
| Density ratio sample weighting | Uber production: worse than baseline on large data; unknown for small N | -1.0 to +2.0 LB points | Low |
| IWCV (better CV metric, no model change) | Theoretical: more accurate OOF estimate | Better CV-LB correlation; no direct LB lift | Medium |
| Combined A + BBSE | Complementary if both shifts are real | +2.0 to +5.0 LB points | Medium |

**Honest combined ceiling estimate:** Starting from LB 58, adversarial correction could push to 60–63. To reach 72+ (current target), we still need the AUC gap closed from ~0.89 to ~0.93+. Adversarial correction alone is unlikely to close the full gap.

---

## 8. Risk: Indirect Overfitting to Test Set

This is the primary risk and must be understood clearly.

### What can go wrong

1. **Adversarial AUC is inflated by noise.** On our small dataset (1,400 train + 339 test), a LightGBM with 300 trees can memorize differences that are statistical noise. The divergent "features" may be artifacts, not real domain shifts.

2. **Dropping features = information loss.** If a feature diverges between train and test purely by chance (due to small test N = 339), dropping it removes genuine signal from the model.

3. **Density ratio weights amplify noise.** A train row with `p̂ = 0.9` gets weight ~9× even if that's sampling noise. With only 70 positive train examples, a handful of upweighted rows dominate gradient updates.

4. **BBSE prevalence estimate is wrong.** If test prevalence is NOT 45% (we inferred this from competition context, not confirmed), the BBSE correction inverts the calibration.

### Mitigation protocol

```
BEFORE running adversarial correction:
1. Confirm adversarial AUC on 5-fold CV, not just train AUC
2. If CV adversarial AUC < 0.65 → shift is not reliably detectable → skip
3. Use shallow adversarial model (max_depth=3 or 4) to avoid noise memorization
4. For feature dropping: only drop if feature appears in top importance in ALL 5 CV folds
5. For density ratios: hard clip at 5× (not 10×), total sample weight mass preserved
6. Validate on OOF AUC: if AUC drops after correction → revert
7. Do NOT submit without OOF AUC improvement as gate condition
```

---

## 9. Recommended Execution Plan for V45

```
Phase 1 — Diagnose (30 min, no model change):
  [ ] Run adversarial classifier on our 105 features
  [ ] Report adversarial CV AUC
  [ ] Print top-20 divergent features
  [ ] Check: if AUC < 0.65, skip Phase 2 → go straight to BBSE

Phase 2A — Feature dropping (if adversarial AUC >= 0.65):
  [ ] Iterative drop until AUC < 0.60
  [ ] Retrain V10 stack on reduced feature set
  [ ] Compare OOF AUC: improved or unchanged? Gate: must not drop below 0.8850

Phase 2B — BBSE label-shift correction (always run, independent of Phase 2A):
  [ ] Estimate test prevalence from model soft predictions on test set
  [ ] Apply Bayes posterior rescaling formula
  [ ] Sweep threshold on rescaled posteriors
  [ ] Submit: if calibrated LB estimate > 58 → submit V45

Phase 3 — Density ratio meta-weighting (risky, only if Phase 2 works):
  [ ] Apply density_ratio_clipped to meta-learner training
  [ ] OOF AUC must not drop > 0.002 before submitting
  [ ] Hard pass if OOF drops
```

---

## 10. Key Formulas Reference

```
# Density ratio weight (covariate shift):
w(x) = p̂(x) / (1 - p̂(x))     where p̂(x) = P(sample is test | features x)

# Label shift weight (BBSE):
w_class(y) = P_test(y) / P_train(y)
  → for y=1: 0.45 / 0.05 = 9.0
  → for y=0: 0.55 / 0.95 = 0.58

# Bayes-adjusted posterior for test distribution:
P_test(Y=1|x) = [P_train(Y=1|x) × (q_test/q_train)] /
                [P_train(Y=1|x) × (q_test/q_train) + P_train(Y=0|x) × ((1-q_test)/(1-q_train))]

# BBSE prevalence estimator (soft):
q_test ≈ (E_test[p̂(x)] - E_train[p̂(x)|Y=0]) /
          (E_train[p̂(x)|Y=1] - E_train[p̂(x)|Y=0])
```

---

## 11. Summary of Findings

| Question | Answer |
|----------|--------|
| Should we run adversarial validation? | Yes — mandatory diagnostic step before V45 |
| Main shift type | Label shift (5%→45%) dominates; covariate shift secondary |
| Best correction | BBSE label-shift correction (medium-high confidence); feature dropping (medium confidence) |
| Density ratio weights | High risk on small N; Uber found worse-than-baseline; skip unless adversarial AUC > 0.75 |
| Expected total lift | +2 to +5 LB points if both shifts confirmed and both corrections applied |
| Overfitting risk | Real; mitigate via shallow adversarial model, per-fold importance consensus, OOF AUC gate |
| Honest ceiling | AUC 0.89 → LB ~58. To reach 80+ still needs AUC ~0.95. Adversarial correction alone does not close this gap. |
| Should we try it anyway? | Yes — it's the most principled unexplored axis. Even +3 LB is meaningful. |

---

## Sources

- [Uber Adversarial Validation Approach to Concept Drift (arxiv 2004.03045)](https://ar5iv.labs.arxiv.org/html/2004.03045) — production deployment, +1.2-5.5% AUC, feature dropping outperformed reweighting
- [Managing Dataset Shift by Adversarial Validation for Credit Scoring (arxiv 2112.10078)](https://arxiv.org/abs/2112.10078) — adversarial validation for financial tabular data
- [Detecting and Correcting for Label Shift with Black Box Predictors — Lipton et al. ICML 2018 (arxiv 1802.03916)](https://arxiv.org/abs/1802.03916) — BBSE; the canonical label-shift correction
- [Weighted Adversarial Validation Part 1 — Frederico Nogueira (Medium)](https://medium.com/@frederico.nogueira/weighted-adversarial-validation-part-1-the-theory-af2b9e1f7f23) — density ratio formula, weight = p̂/(1-p̂)
- [Adversarial Learning for Feature Shift Detection and Correction (arxiv 2312.04546)](https://arxiv.org/pdf/2312.04546) — random forest + GBT outperform neural approaches for tabular shift detection
- [Covariate Shift Adaptation by Importance Weighted Cross Validation — Sugiyama et al. JMLR 2007](https://www.jmlr.org/papers/volume8/sugiyama07a/sugiyama07a.pdf) — IWCV theoretical foundation
- [Adversarial Validation — UnfoldAI](https://unfoldai.com/adversarial-validation/) — practical pipeline overview + SHAP importance
- [Adversarial Validation — Analytics Vidhya 2023](https://www.analyticsvidhya.com/blog/2023/02/adversarial-validation-improving-ranking-in-hackathon/) — code template
- [Covariate Shift Demo — Ruoyun Lin's Blog](https://ruoyunlin.github.io/articles/2021-08/covariate_shift) — density ratio sklearn integration

### Confidence: Medium
- Core methodology (adversarial validation, BBSE) is well-established
- Expected lift estimates derived from analogous production systems, not our specific dataset
- Risk of over-applying on small N (1,400 train, 339 test) is real and documented
- Final answer depends on what adversarial AUC we actually observe on our 105 features
