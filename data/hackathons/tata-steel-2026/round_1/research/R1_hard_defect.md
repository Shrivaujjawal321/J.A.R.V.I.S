# Hard-Defect Characterization — Research Brief
**Topic:** What's special about test rows we're missing? How to catch hard-positive defects.  
**Context:** 1352 train + 339 test rows. 49 anonymous X-features. ~5% train defect / ~45% test defect (severe prevalence inversion). V44 consensus LB 72.83. Target 80+.  
**Date:** 2026-05-24  

---

## The Core Diagnosis (Before Techniques)

Our problem has TWO distinct failure modes that look identical in OOF metrics but require different fixes:

1. **Model failure**: The model genuinely can't separate defective vs non-defective in feature space → hard positives that look like negatives by feature profile.
2. **Calibration failure**: The model CAN separate them, but its output probabilities are calibrated to 5% prevalence, so at 45% test prevalence it scores real defects too low → they fall below the decision threshold.

The prevalence inversion (5% → 45%) is a **9x shift**. This alone, without any model improvement, will cause a well-trained classifier to miss roughly half the positives at threshold 0.5. This is the single highest-expected-lift issue to fix and it's essentially free.

---

## Top 5 Techniques Ranked by Expected Lift

### Rank 1 — Posterior Recalibration for Label/Prevalence Shift (Expected lift: +5 to +12 LB points)

**What it is:** Post-hoc Bayesian correction of output probabilities to account for the 9x shift in class prevalence between train (5%) and test (45%).

**Why it's #1:**
- It addresses the root cause mathematically: if p(y=1|train)=0.05 but p(y=1|test)=0.45, every output probability from a model trained on the imbalanced set is systematically too low by a computable factor. The correction requires zero retraining.
- Confirmed by Saerens et al. EM algorithm (widely cited) and Tasche (2025) recalibration framework.
- AdapTable (NeurIPSW 2024) showed up to 16% improvement on HELOC with label distribution shift correction — and our shift is more extreme.

**The formula (from Tasche 2025 [arxiv 2505.19068]):**
```
p_corrected(x) = (q/p) * p_model(x) / [(q/p) * p_model(x) + ((1-q)/(1-p)) * (1 - p_model(x))]
```
Where:
- `p_model(x)` = raw model probability (calibrated to train set)
- `p` = 0.05 (train prevalence — fraction of defects in train)
- `q` = 0.45 (estimated test prevalence)

**Important caveat:** The simple label-shift formula can be unreliable if the model is poorly calibrated (Tasche 2025). The robust path is: (1) calibrate the model with Platt scaling or isotonic regression on OOF predictions first, THEN (2) apply the prevalence correction.

**EM variant (Saerens algorithm) — no need to know q in advance:**
```python
from abstention.calibration import TempScaling
from abstention.label_shift import EMImbalanceAdapter

bcts_calibrator = TempScaling(verbose=False, bias_positions='all')
adapter = EMImbalanceAdapter(calibrator_factory=bcts_calibrator)
adapter_func = adapter(
    valid_labels=val_labels,
    tofit_initial_posterior_probs=test_preds,   # unlabeled test preds
    valid_posterior_probs=val_preds
)
adjusted_test_preds = adapter_func(test_preds)
```
The EM algorithm iteratively estimates q from the test data itself — no oracle needed.

**Risk:** Low. Purely post-hoc. The base model is unchanged. If q estimate is off (e.g., test is 40% not 45%), error is small. No overfit risk.

---

### Rank 2 — Asymmetric Loss / Weighted Cross-Entropy in GBDT (Expected lift: +3 to +8 LB points)

**What it is:** Replace vanilla log-loss with a loss that penalizes False Negatives (missed defects) more heavily than False Positives.

**Why it's #2:**
- Luo et al. (arXiv 2407.14381, 2024) — first comprehensive study of class-balanced losses on GBDT across 15 datasets. Weighted Cross-Entropy (WCE) gave the highest consistent gains in binary classification: +0.38% to +28.91% F1 across 13/15 datasets. Improvements were largest on severely imbalanced sets.
- Asymmetric Loss (ASL) (separate γ⁺ for positives, γ⁻ for negatives) also performed well — useful when you want to focus on hard positive recall without wrecking precision.
- Imbalance-XGBoost (Wang et al., Pattern Recognition Letters 2020 / benchmark still used 2024) demonstrated consistent AUC and F1 gains at gamma=2, especially with imbalance ratios ≥9:1.

**Implementation (XGBoost custom objective — Weighted Cross-Entropy):**
```python
import numpy as np

def weighted_log_loss(y_pred, dtrain):
    y_true = dtrain.get_label()
    # w_pos = ratio of negatives to positives (19:1 for 5% prevalence)
    w_pos = 19.0
    p = 1.0 / (1.0 + np.exp(-y_pred))
    # gradient and hessian
    grad = p - y_true
    grad[y_true == 1] *= w_pos
    hess = p * (1 - p)
    hess[y_true == 1] *= w_pos
    return grad, hess

# In XGBoost:
xgb_model = xgb.train(
    params={"tree_method": "hist", "eval_metric": "auc"},
    dtrain=dtrain,
    obj=weighted_log_loss,
    ...
)
```

**LightGBM equivalent:**
```python
# LightGBM — simpler, built-in:
lgb_params = {
    "is_unbalance": False,       # don't use this — it uses 1:1 weight
    "scale_pos_weight": 19,      # negatives / positives
    "objective": "binary",
    "metric": "auc",
}
# OR use class_weight in sklearn API:
lgb_model = LGBMClassifier(scale_pos_weight=19, ...)
```

**Focal Loss (harder to implement in GBDT, smaller marginal gain over WCE):**
- γ=1 to γ=2 recommended for tabular with ~5% positive rate (Luo 2024)
- Use `imbalance_xgboost` package: `pip install imbalance-xgboost`
```python
from imbalance_xgboost import imbalance_xgboost as imb_xgb
bst = imb_xgb(special_objective='focal', focal_gamma=2.0)
```

**Risk:** Medium on small data. Aggressive class weighting (scale_pos_weight=19) can cause variance spikes in small folds. Tune carefully: try 5, 10, 15, 19 — pick via OOF AUC, not F1.

---

### Rank 3 — Error Analysis + Hard-Example Isolation via SHAP (Expected lift: indirect, +2 to +5 via downstream feature engineering)

**What it is:** Systematically identify which rows your current model gets wrong (OOF False Negatives and borderline cases), then analyze what features make them hard.

**Why it's #3:**
- Not a model change — this is diagnostic. But diagnostics drive targeted feature engineering that unlocks step-function improvements.
- SHAP analysis on misclassified examples reveals whether hard positives are hard because: (a) they genuinely look like negatives in the feature space, (b) they lie on the decision boundary due to feature noise, or (c) they form a separate cluster that the model has not learned.

**Implementation:**
```python
import shap
import numpy as np
import pandas as pd

# Step 1: Get OOF predictions and identify hard cases
oof_preds = cross_val_predict(model, X_train, y_train, cv=5, method='predict_proba')[:,1]

# False Negatives (missed defects): y=1 but model predicts low probability
fn_mask = (y_train == 1) & (oof_preds < 0.4)
hard_positives = X_train[fn_mask]

# Borderline positives (model is uncertain)
uncertain_mask = (y_train == 1) & (oof_preds < 0.6) & (oof_preds >= 0.3)

# Step 2: SHAP analysis on hard cases vs easy cases
explainer = shap.TreeExplainer(model)
shap_vals_hard = explainer.shap_values(hard_positives)
shap_vals_easy = explainer.shap_values(X_train[(y_train == 1) & (oof_preds > 0.7)])

# Step 3: Compare feature distributions
# Which features push hard positives toward class 0?
mean_shap_hard = np.mean(np.abs(shap_vals_hard), axis=0)
mean_shap_easy = np.mean(np.abs(shap_vals_easy), axis=0)
contrast_df = pd.DataFrame({
    'feature': X_train.columns,
    'shap_hard': mean_shap_hard,
    'shap_easy': mean_shap_easy,
    'ratio': mean_shap_hard / (mean_shap_easy + 1e-9)
}).sort_values('ratio', ascending=False)

# High ratio = feature behaves DIFFERENTLY for hard vs easy positives
# These are the features to engineer
```

**Key pattern to look for:** Hard positives that cluster separately in 2D UMAP/t-SNE → suggests a subpopulation of defect that the model hasn't learned. Fix: add cluster membership as a feature, or train a separate specialist for that cluster.

**Risk:** Low — diagnostic only. Time cost: ~30 min analysis.

---

### Rank 4 — Two-Stage Cascade Classifier (Expected lift: +3 to +6 LB points on recall)

**What it is:** Stage 1 = high-recall detector (maximize sensitivity, flag everything likely defective). Stage 2 = precision filter (of the flagged cases, which are truly defective). Ensemble outputs by multiplication or meta-learning.

**Why it's #4:**
- Classical technique validated in object detection (Viola-Jones, FPN cascades) adapted to tabular: stage 1 uses aggressive class weighting (scale_pos_weight=50+) to catch everything, stage 2 is calibrated on the positive class only.
- Particularly effective when hard positives are a heterogeneous group — the cascade partitions the problem.
- ScienceDirect overview confirms this is a standard approach for severe class imbalance.

**Implementation:**
```python
# Stage 1: High-recall first-pass (trained on full imbalanced data, heavy weighting)
stage1 = LGBMClassifier(scale_pos_weight=50, n_estimators=500, ...)
stage1.fit(X_train, y_train)
stage1_preds = stage1.predict_proba(X_train)[:,1]

# Threshold 1: low (e.g. 0.1) — catches almost all positives + some negatives
flagged_mask = stage1_preds > 0.10
X_flagged = X_train[flagged_mask]
y_flagged = y_train[flagged_mask]

# Stage 2: Precision filter (trained on flagged subset — roughly balanced now)
stage2 = LGBMClassifier(n_estimators=300, ...)
stage2.fit(X_flagged, y_flagged)

# At test time:
stage1_test = stage1.predict_proba(X_test)[:,1]
stage2_test = stage2.predict_proba(X_test)[:,1]

# Combine: use geometric mean or learned blend
final_preds = np.sqrt(stage1_test * stage2_test)  # geometric mean
```

**Risk:** Medium-high on our 1352 sample dataset. Splitting the training data for stage 2 creates very small subsets. Use 5-fold OOF to train stage 2 to avoid leakage. Also: the blend strategy needs tuning.

---

### Rank 5 — Tabular Mixup / Synthetic Minority Augmentation (Expected lift: +1 to +4 LB points)

**What it is:** Generate synthetic minority class samples by interpolating between real positive examples in feature space. This is SMOTE's cleaner cousin — linear interpolation at the feature level.

**Why it's #5:**
- 2025 study on small tabular health data showed 4-31% ROC-AUC improvement from augmentation, average 15% relative gain (pmc.ncbi.nlm.nih.gov/PMC12661835).
- Most valuable when minority class is genuinely underrepresented (n_positives ~68 in our case with 5% of 1352).
- MixBoost (2020) and class-distance Mixup (2022) specifically target imbalanced scenarios.

**Simple Tabular Mixup for minority class:**
```python
import numpy as np

def minority_mixup(X_pos, n_synthetic=200, alpha=0.4):
    """Generate synthetic positives by interpolating between real ones."""
    n = len(X_pos)
    synthetic = []
    for _ in range(n_synthetic):
        i, j = np.random.choice(n, 2, replace=False)
        lam = np.random.beta(alpha, alpha)
        synthetic.append(lam * X_pos[i] + (1 - lam) * X_pos[j])
    return np.array(synthetic)

pos_mask = (y_train == 1)
X_synthetic = minority_mixup(X_train[pos_mask].values, n_synthetic=300)
y_synthetic = np.ones(len(X_synthetic))

X_augmented = np.vstack([X_train.values, X_synthetic])
y_augmented = np.concatenate([y_train.values, y_synthetic])
```

**Risk:** High on small data. Interpolation in anonymous feature space may violate manifold structure — we don't know if features are continuous/discrete/ordinal. Test with OOF AUC carefully. If OOF degrades, abandon immediately.

---

## Implementation Priority — What to Build First

```
Priority 1 (do NOW, 30 min, zero overfit risk):
  → Posterior recalibration — test the Saerens EM correction on our current V44 ensemble.
     p=0.05, q=0.45 (or let EM estimate it from test distribution).
     This should give immediate LB lift if our model is well-calibrated on the training set.

Priority 2 (next build, 2-4h):
  → Retrain ensemble with WCE (scale_pos_weight=10 to 19) + Platt-scale calibration.
     Then apply prevalence correction on top.

Priority 3 (parallel with P2):
  → SHAP error analysis on current OOF misclassifications.
     Find which features drive hard positive failures.
     Use those features to engineer new interaction terms for next build.

Priority 4 (if P1+P2 don't reach 80):
  → Two-stage cascade on the re-trained ensemble.

Priority 5 (last resort, high risk):
  → Mixup augmentation — only if we have OOF evidence of underfitting on minority class.
```

---

## Full Implementation: Priority 1 — Posterior Recalibration

```python
"""
posterior_recalibration.py
Post-hoc prevalence correction for label-shifted test set.
V44 model → adjusted predictions for submission.
"""
import numpy as np
from sklearn.calibration import CalibratedClassifierCV
from sklearn.isotonic import IsotonicRegression

def recalibrate_with_isotonic(oof_preds, oof_labels, test_preds):
    """
    Step 1: Calibrate model probabilities using OOF predictions.
    Isotonic regression is more flexible than Platt scaling for small datasets.
    """
    iso = IsotonicRegression(out_of_bounds='clip')
    iso.fit(oof_preds, oof_labels)
    calibrated_oof = iso.predict(oof_preds)
    calibrated_test = iso.predict(test_preds)
    return calibrated_test, calibrated_oof

def label_shift_correction(p_model, p_train=0.05, p_test=0.45):
    """
    Saerens/Tasche posterior recalibration formula.
    Corrects for prevalence shift: 5% train → 45% test.
    
    Args:
        p_model: calibrated model probabilities (array)
        p_train: training set positive rate
        p_test: test set positive rate (estimated)
    Returns:
        corrected probabilities
    """
    ratio = (p_test / p_train) / ((1 - p_test) / (1 - p_train))
    corrected = ratio * p_model / (ratio * p_model + (1 - p_model))
    return np.clip(corrected, 1e-7, 1 - 1e-7)

def em_label_shift_correction(test_preds, val_preds, val_labels, 
                               max_iter=1000, tol=1e-6):
    """
    EM variant — estimates test prevalence from data, no oracle needed.
    Converges in ~50 iterations typically.
    
    Args:
        test_preds: calibrated model probabilities on test set
        val_preds: calibrated model probabilities on validation set  
        val_labels: true labels on validation set
        max_iter: max EM iterations
        tol: convergence tolerance
    Returns:
        (corrected_test_preds, estimated_test_prevalence)
    """
    p_train = np.mean(val_labels)   # empirical train prevalence
    # Initialize q with mean of test predictions
    q_est = np.mean(test_preds)
    
    for iteration in range(max_iter):
        q_old = q_est
        # E-step: correct test predictions with current q estimate
        corrected = label_shift_correction(test_preds, p_train, q_est)
        # M-step: re-estimate q
        q_est = np.mean(corrected)
        
        if abs(q_est - q_old) < tol:
            print(f"EM converged at iteration {iteration+1}, q_est={q_est:.4f}")
            break
    
    return corrected, q_est


# ---- Usage with V44 ensemble ----
# Assuming you have:
#   oof_preds_v44 : shape (1352,) — OOF predictions from V44 ensemble
#   oof_labels    : shape (1352,) — y_train
#   test_preds_v44: shape (339,)  — V44 test predictions

# Step 1: Calibrate on OOF
calibrated_test, calibrated_oof = recalibrate_with_isotonic(
    oof_preds_v44, oof_labels, test_preds_v44
)

# Step 2: Apply EM label shift correction
corrected_test, q_estimated = em_label_shift_correction(
    calibrated_test, calibrated_oof, oof_labels
)

print(f"Estimated test prevalence: {q_estimated:.3f}")  # expect ~0.40-0.50
print(f"Mean raw test pred: {np.mean(test_preds_v44):.4f}")
print(f"Mean corrected test pred: {np.mean(corrected_test):.4f}")

# Step 3: Build submission
# For binary classification, threshold corrected_test at 0.5
# (or optimize threshold on OOF after calibration)
predictions = (corrected_test > 0.5).astype(int)

# Diagnostic: OOF calibration check
print(f"OOF positive rate after calibration: {np.mean(calibrated_oof[oof_labels==1]):.4f}")
print(f"OOF negative rate after calibration: {np.mean(calibrated_oof[oof_labels==0]):.4f}")
```

---

## Expected OOF AUC Improvement Range

| Technique | Expected LB Lift | Confidence | Notes |
|-----------|-----------------|------------|-------|
| Posterior recalibration (EM) | +4 to +10 | HIGH | Our shift is severe (9x). Direct mathematical correction. |
| WCE (scale_pos_weight=10-19) + recalib | +3 to +8 | MEDIUM-HIGH | Luo 2024 showed +0.38-28.91% F1; AUC improvement typically 60-70% of F1 gain |
| SHAP error analysis → feature engineering | +2 to +5 | MEDIUM | Indirect — depends on what patterns we find |
| Two-stage cascade | +2 to +5 | MEDIUM | Effective but complex; overfit risk on 1352 samples |
| Tabular Mixup | +0 to +4 | LOW-MEDIUM | High variance; may hurt if feature space isn't continuous |

**Caveat (critical):** OOF calibration is NOT LB calibration (Tata V27 disaster: CV-est +1.04 → actual -34.89 LB). The prevalence correction especially must be tested on LB, not just trusted from OOF. The EM algorithm will happily converge to a q_est that overfits the test set structure. Build one corrected submission early to validate direction before going deep.

---

## Risk Assessment Summary

| Technique | Overfit Risk | Implementation Complexity | LB Test Needed Before Committing? |
|-----------|-------------|--------------------------|----------------------------------|
| Posterior recalibration (simple formula) | LOW | LOW (20 lines) | Yes — 1 submission to validate |
| Posterior recalibration (EM) | LOW-MEDIUM | LOW (50 lines) | Yes — 1 submission |
| WCE with scale_pos_weight | MEDIUM | LOW | Yes — validate vs V44 baseline |
| SHAP error analysis | NONE (diagnostic) | MEDIUM | N/A — purely analytical |
| Two-stage cascade | HIGH | MEDIUM-HIGH | Yes — compare OOF carefully first |
| Tabular Mixup | HIGH | MEDIUM | Yes — validate OOF first, only submit if OOF gains ≥ 0.01 AUC |

---

## What The Research Consensus Says About Our Specific Problem Profile

Profile match: small data (1352 train) + severe imbalance (5%) + severe prevalence shift (→45%) + anonymous features + competitive LB.

1. **Prevalence shift is the elephant in the room** — virtually every paper on label shift (Saerens, Alexandari 2020 ICML, AdapTable NeurIPS 2024, Tasche 2025) confirms that naive classifiers trained on 5% positive rate will systematically underestimate positives at 45% prevalence. The EM correction is the canonical fix.

2. **For small tabular data with GBDT, WCE beats Focal Loss** — Luo et al. 2024 empirical study (15 datasets, 3 GBDT algorithms). Focal loss adds complexity without consistent gain over well-tuned WCE on tabular. Use scale_pos_weight or sample_weight, not focal loss.

3. **SHAP on misclassified examples is the diagnostic standard** — Multiple 2024 papers (SHAP-EE-LightGBM, SHAP appendix cancer prediction) confirm: analyzing SHAP distribution on FN class separately from TP class routinely reveals 1-3 features where the two groups diverge. That divergence = feature engineering target.

4. **Augmentation risk is real on small data** — 2025 small-data health study shows augmentation helps more when dataset is smaller, but the variance is huge. Our 68 positive samples (5% of 1352) is exactly the regime where it can help or badly overfit. Use only after OOF validation.

5. **Two-stage cascade is validated but data-hungry** — Best used when the second stage can train on ≥200 samples. At 68 positives, stage 2 would have ~34 positives in a 50-50 flagged set. Marginal viability.

---

## Sources

- [Improving GBDT Performance on Imbalanced Datasets (Luo et al., 2024)](https://arxiv.org/abs/2407.14381) — Neurocomputing 2025; first comprehensive WCE/Focal/ASL study on GBDT; binary WCE is the recommended baseline
- [AdapTable: Test-Time Adaptation for Tabular Data (Kim et al., NeurIPSW-TRL 2024)](https://arxiv.org/abs/2407.10784) — Label distribution handler; up to 16% improvement with prevalence shift
- [Recalibrating Binary Probabilistic Classifiers (Tasche, 2025)](https://arxiv.org/abs/2505.19068) — Full QMM framework; posterior correction formula; risk of naive label-shift formula
- [Label Shift Estimation for Class-Imbalance (Ye et al., WACV 2024)](https://openaccess.thecvf.com/content/WACV2024/papers/Ye_Label_Shift_Estimation_for_Class-Imbalance_Problem_A_Bayesian_WACV_2024_paper.pdf) — Bayesian MAP approach; outperforms EM on severely imbalanced long-tailed problems
- [Maximum Likelihood with Bias-Corrected Calibration for Label Shift (Alexandari et al., ICML 2020)](https://proceedings.mlr.press/v119/alexandari20a.html) — Canonical EM label shift algorithm; BBSC calibration prerequisite
- [Imbalance-XGBoost: Focal + Weighted Loss (Wang et al., 2020, benchmark 2024)](https://arxiv.org/pdf/1908.01672) — First XGBoost focal loss implementation; γ=2 benchmarks; pip installable
- [Battling Label Distribution Shift in a Dynamic World (Towards Data Science)](https://towardsdatascience.com/battling-label-distribution-shift-in-a-dynamic-world-bc1f4c4d2f92/) — Practical EM implementation with `abstention` package
- [AdapTable GitHub Implementation](https://github.com/drumpt/AdapTable) — NeurIPSW 2024 official code
- [Why ROC-AUC Is Misleading for Highly Imbalanced Data (MDPI 2026)](https://www.mdpi.com/2227-7080/14/1/54) — MCC preferred over ROC-AUC for severe imbalance
- [Cost-Sensitive YOLOv5 for Industrial Defect Detection (PMC)](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10007231/) — Steel domain validation of asymmetric FN cost in manufacturing
- [Augmenting Small Tabular Health Data (PMC 2025)](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12661835/) — 4-43% ROC-AUC gains from augmentation; risk on small data

---

**Confidence: HIGH** on diagnosis (prevalence shift) and Priority 1 implementation. MEDIUM on expected lift magnitudes — they are calibrated from published benchmarks but our anonymous feature space may have domain-specific properties that change the picture. The OOF → LB reliability issue (V27 disaster) means every technique must be LB-validated before going deep.
