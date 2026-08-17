# R9 — Probability Calibration for V44 Consensus Output

**Date:** 2026-05-24
**Context:** V44 consensus produces vote-scores + rank-pct tiebreaker. Current LB = 72.83. Target = 80+.
**Scoring:** HE uses (R+P)/2 at fixed K. This research answers: does calibrating V44's raw scores improve threshold/K selection?

---

## Quick Answer

For our specific case — (R+P)/2 at fixed K, where K is NOT the decision threshold but the top-K cutoff — calibration's primary value is **enabling principled K selection**, not raw scoring. If V44's rank ordering is already good (high AUC), calibration won't reorder predictions. But it will replace arbitrary rank-pct scores with interpretable probabilities, enabling theoretically optimal K choice. Expected LB lift: **0.5–1.5 points IF K is currently suboptimal.** Risk: calibrator overfit on small val set.

---

## 1. Method Comparison for Our Case

### Platt Scaling (sigmoid)

**What it does:** Fits a logistic regression `p = 1 / (1 + exp(A*s + B))` on (score, label) pairs. Maps raw scores to [0,1].

**Best for:**
- Small calibration sets (<1000 samples)
- When miscalibration is sigmoid-shaped (systematic over/under-confidence)
- SVMs, Naive Bayes outputs

**Pros for V44:**
- Only 2 parameters (A, B) — low overfit risk even on small val fold
- Preserves rank ordering STRICTLY (monotone sigmoid)
- AUC unchanged post-calibration

**Cons:**
- Assumes miscalibration is logistic in shape — may not hold for consensus rank-pct scores
- Cannot handle non-monotone distortions

**Implementation on raw scores:**
```python
from sklearn.linear_model import LogisticRegression
import numpy as np

# oof_scores: V44 consensus scores on OOF fold
# oof_labels: true 0/1 labels on OOF fold
lr = LogisticRegression(C=1.0)
lr.fit(oof_scores.reshape(-1, 1), oof_labels)

# Apply to test
test_proba = lr.predict_proba(test_scores.reshape(-1, 1))[:, 1]
```

---

### Isotonic Regression

**What it does:** Non-parametric, piecewise constant monotone mapping. Fits the minimum-MSE monotone function from scores to labels. No shape assumption.

**Best for:**
- Datasets with >~1000 calibration samples
- When distortion shape is unknown/complex

**Pros:**
- Most flexible — corrects ANY monotone distortion
- Can handle non-sigmoid miscalibration

**Cons for V44 — CRITICAL:**
- Heavily prone to overfit on small val sets (our val fold may be 300–500 samples)
- May introduce **probability ties** (multiple samples assigned the same calibrated p) — directly hurts K selection because ties break the ordering needed to pick top-K
- sklearn docs warn: "more prone to overfitting, performs worse than Platt when data is scarce"

**Implementation on raw scores:**
```python
from sklearn.isotonic import IsotonicRegression

ir = IsotonicRegression(out_of_bounds='clip')
ir.fit(oof_scores, oof_labels)

test_proba = ir.transform(test_scores)
```

---

### Beta Calibration

**What it does:** Uses a beta-distribution family: `log(p/(1-p)) = a*log(s) + b*log(1-s) + c`. Three parameters. Generalizes both Platt (a=b, c=0) and log-odds (a=1, b=0).

**Best for:**
- Skewed score distributions (e.g., most scores near 0 with few near 1 — typical for rare-defect detection like ours)
- Classifiers with overconfident or boundary-hugging distributions

**Pros for V44:**
- Rank-pct scores from consensus voting ARE likely skewed toward 0 (only ~10% defect rate in training)
- Handles asymmetric distortions Platt cannot
- Only 3 parameters — still low overfit risk
- Paper shows superior to logistic (Platt) for Naive Bayes and Adaboost — both ensemble-like methods

**Cons:**
- Not natively in sklearn; requires `betacal` package (`pip install betacal`)
- Slightly more complex than Platt

**Implementation:**
```python
from betacal import BetaCalibration

bc = BetaCalibration(parameters="abm")  # full 3-param version
bc.fit(oof_scores.reshape(-1, 1), oof_labels)

test_proba = bc.predict(test_scores.reshape(-1, 1))
```

**Verdict for V44:** Beta calibration is the BEST fit given the skewed score distribution from a 10%-positive-rate consensus ensemble.

---

### Temperature Scaling

Designed for neural network logits (softmax outputs). V44 is not a neural net. **Skip.**

### Histogram Binning

Coarse, needs many samples per bin. With ~300–500 val samples, bins become unreliable. **Skip.**

---

## 2. Ranked Recommendation for V44

| Rank | Method | Why |
|------|--------|-----|
| 1 | **Beta calibration** | Best for skewed distributions (rare defect); 3 params; generalizes Platt |
| 2 | **Platt scaling** | Safe, simple, 2 params, zero overfit risk, preserves ranking strictly |
| 3 | Isotonic regression | Most powerful BUT highest overfit risk on small val; introduces ties |
| 4 | Temperature scaling | Wrong tool (for NNs) |
| 5 | Histogram binning | Too coarse for our N |

---

## 3. CV-Safe Calibration Protocol

**The golden rule:** The calibrator must see labels the base model never trained on. If V44 uses 5-fold CV:

```
Fold 1: model trained on folds 2-5 → predicts fold 1 → (score_1, label_1)
Fold 2: model trained on folds 1,3-5 → predicts fold 2 → (score_2, label_2)
...
Concatenate all OOF → (oof_scores, oof_labels)   [N rows, full dataset]
↓
Fit calibrator on (oof_scores, oof_labels)
↓
Apply calibrator to test_scores → test_proba
```

**No leakage.** The calibrator sees the true labels only via OOF predictions that were never used in model training.

**Implementation with sklearn FrozenEstimator (post-hoc):**
```python
# If V44 is already a fitted ensemble:
from sklearn.calibration import CalibratedClassifierCV
from sklearn.frozen import FrozenEstimator

# Use pre-computed OOF scores directly (cleaner for our case)
# Don't wrap in CalibratedClassifierCV — just use IsotonicRegression or LogisticRegression directly
# on (oof_scores, oof_labels) and apply to test_scores

# WRONG: fitting calibrator on same data model trained on
# RIGHT: use OOF scores only
```

**Recommended simple recipe:**
```python
from sklearn.linear_model import LogisticRegression  # Platt
import numpy as np

# Step 1: Collect OOF scores (already computed during V44 cross-val)
# oof_scores shape: (N_train,) — V44 consensus score on held-out fold
# oof_labels shape: (N_train,) — true labels

# Step 2: Fit calibrator
platt = LogisticRegression(C=1.0, solver='lbfgs')
platt.fit(oof_scores.reshape(-1, 1), oof_labels)

# Step 3: Apply to test
test_proba = platt.predict_proba(test_scores.reshape(-1, 1))[:, 1]

# Step 4: Select K using calibrated probas
# For (R+P)/2 = HE score, optimal threshold ≈ 0.5 * optimal_F1_value
# But we don't know true test prevalence.
# Instead: use OOF calibrated probas to sweep K:
oof_proba = platt.predict_proba(oof_scores.reshape(-1, 1))[:, 1]
from sklearn.metrics import precision_recall_fscore_support
results = []
for k in range(10, 200, 5):
    thresh = np.sort(oof_proba)[::-1][k]  # score at rank K
    preds = (oof_proba >= thresh).astype(int)
    p, r, _, _ = precision_recall_fscore_support(oof_labels, preds, average='binary', zero_division=0)
    results.append({'K': k, 'score': (p+r)/2, 'P': p, 'R': r})

best = max(results, key=lambda x: x['score'])
print(f"Optimal OOF K={best['K']}, (P+R)/2={best['score']:.4f}")

# Apply same K to test
test_preds = np.zeros(len(test_proba))
test_preds[np.argsort(test_proba)[::-1][:best['K']]] = 1
```

---

## 4. BBSE + Calibration (Prevalence Shift Correction)

**What BBSE does:** Corrects for the shift in class prevalence between train and test by re-weighting the confusion matrix. Equation: `w = C^{-1} * mu_test` where C = calibrated confusion matrix, mu_test = mean predicted probability vector on test.

**Is it relevant?**
- BBSE requires calibrated p(y|x) as input — so calibration is a prerequisite
- Our train set: ~10% defect rate. Test set: unknown but possibly different
- If test defect rate differs significantly from train rate, our threshold K choice is miscalibrated
- BBSE could estimate the true test prevalence `p_test(y=1)` from test predictions alone

**Practical recipe:**
```python
# After calibrating with Platt/beta:
# Step 1: Estimate confusion matrix on OOF with calibrated probas (at threshold 0.5)
from sklearn.metrics import confusion_matrix
preds_oof_binary = (oof_proba >= 0.5).astype(int)
C = confusion_matrix(oof_labels, preds_oof_binary, normalize='true')
# C shape: (2,2), rows=true, cols=pred

# Step 2: Estimate test mean prediction vector
mu_test = np.array([1 - test_proba.mean(), test_proba.mean()])

# Step 3: Solve C.T @ w = mu_test for w (= shifted prevalence)
from numpy.linalg import solve
try:
    w = solve(C.T, mu_test)
    w = np.clip(w, 0, 1)
    w /= w.sum()
    estimated_test_prevalence = w[1]
    print(f"BBSE estimated test prevalence: {estimated_test_prevalence:.4f}")
except np.linalg.LinAlgError:
    print("Singular matrix — BBSE not applicable")

# Step 4: Adjust K based on estimated prevalence
# If test_prevalence << train_prevalence, shrink K
# K_adjusted = int(len(test_scores) * estimated_test_prevalence * recall_factor)
```

**Expected impact:** If train prevalence is 10% but test is 5%, submitting top-154 (= 10% of 1540 test rows) when true positives are ~77 will hurt precision catastrophically. BBSE-adjusted K could correct this.

**Risk:** BBSE is only reliable when the calibrated confusion matrix C is well-conditioned AND the calibration quality is high. On small OOF sets, C estimate is noisy.

---

## 5. Reliability Diagrams + Calibration Metrics

```python
from sklearn.calibration import calibration_curve
import matplotlib.pyplot as plt
import numpy as np

# Plot before/after calibration
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

for ax, (name, proba) in zip(axes, [
    ("Raw V44 score", oof_scores / oof_scores.max()),  # normalize to [0,1]
    ("Platt calibrated", oof_proba)
]):
    prob_true, prob_pred = calibration_curve(oof_labels, proba, n_bins=10)
    ax.plot(prob_pred, prob_true, 'o-', label=name)
    ax.plot([0,1],[0,1], 'k--', label='Perfect')
    ax.set_xlabel('Mean predicted probability')
    ax.set_ylabel('Fraction of positives')
    ax.set_title(name)
    ax.legend()

plt.tight_layout()
plt.savefig('reliability_diagram.png')

# ECE
def ece(y_true, y_pred, n_bins=10):
    bins = np.linspace(0, 1, n_bins + 1)
    ece_val = 0
    for i in range(n_bins):
        mask = (y_pred >= bins[i]) & (y_pred < bins[i+1])
        if mask.sum() > 0:
            bin_acc = y_true[mask].mean()
            bin_conf = y_pred[mask].mean()
            ece_val += mask.mean() * abs(bin_acc - bin_conf)
    return ece_val

from sklearn.metrics import brier_score_loss

brier_raw = brier_score_loss(oof_labels, oof_scores / oof_scores.max())
brier_cal = brier_score_loss(oof_labels, oof_proba)
ece_raw = ece(oof_labels, oof_scores / oof_scores.max())
ece_cal = ece(oof_labels, oof_proba)

print(f"Brier raw: {brier_raw:.4f} → calibrated: {brier_cal:.4f}")
print(f"ECE   raw: {ece_raw:.4f} → calibrated: {ece_cal:.4f}")
```

**Interpretation:**
- Brier score lower → better
- ECE lower → better (0 = perfect calibration)
- If reliability diagram shows raw scores are systematically under-confident (curve ABOVE diagonal), Platt/beta will bring it toward diagonal
- If raw V44 scores are ALREADY well-ranked but poorly scaled, calibration helps K selection but won't change which samples are ranked high

---

## 6. Expected Lift Analysis

**How calibration helps LB score specifically:**

The HE score = (R+P)/2 at fixed predicted K (you submit exactly K=1 predictions as positive).

With uncalibrated scores:
- K is chosen heuristically (e.g., K = expected_positives_from_prior = 0.10 * 1540 = 154)
- If the actual number of positives in test is 110 (lower prevalence), K=154 gives precision = 22/154 = 0.143, R = 1.0 → score = 57.1

With calibrated scores + BBSE:
- BBSE estimates test prevalence = 7% → K_adjusted = 110
- Precision = 22/110 = 0.20, R = 1.0 → score = 60.0 (+3 LB points)

**This is a significant gain IF the prevalence shift is real.**

For K that's already well-tuned (e.g., via OOF sweep), calibration's marginal value is lower.

**Summary of expected lift:**
| Scenario | Expected LB Change |
|----------|-------------------|
| K currently suboptimal due to prevalence shift + BBSE corrects it | +1 to +4 LB |
| K already optimal from OOF sweep, calibration only changes probabilities not rank | +0 to +0.5 |
| Isotonic calibration introduces ties → breaks ranking | -0.5 to -2 |
| Beta calibration + well-estimated K | +0.5 to +2 |

---

## 7. Overfitting Risk Assessment

| Method | Parameters | Risk on N=300 val |
|--------|-----------|-------------------|
| Platt (logistic) | 2 | **Low** — nearly impossible to overfit with 2 params |
| Beta calibration | 3 | **Low** — still very few params |
| Isotonic regression | up to N | **HIGH** — can fit every point exactly |
| Histogram binning | n_bins | **Medium** — depends on bin count |

**Mitigation for isotonic on small N:**
- Use `sklearn.isotonic.IsotonicRegression` with `out_of_bounds='clip'`
- Apply L2 regularization manually (not native to sklearn IR)
- OR use ROC-regularized isotonic (arXiv:2311.12436) which preserves AUC while calibrating — but adds complexity

**Strong recommendation:** For our dataset size (train ~1540, OOF fold ~300), **stick with Platt or beta calibration**. Isotonic is the wrong choice here despite being "more powerful" in theory.

---

## 8. Full Recommended Recipe for V44

```python
# ================================================
# V44 Calibration Recipe — Tata Steel Round 1
# ================================================
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import precision_recall_fscore_support, brier_score_loss
from sklearn.calibration import calibration_curve

# INPUTS (must have from V44 build):
# oof_scores: np.array shape (N_train,) — V44 consensus scores on OOF
# oof_labels: np.array shape (N_train,) — true 0/1 labels
# test_scores: np.array shape (N_test,) — V44 consensus scores on test

# -----------------------------------------------
# STEP 1: Fit Platt calibrator on OOF scores
# -----------------------------------------------
platt = LogisticRegression(C=1.0, solver='lbfgs')
platt.fit(oof_scores.reshape(-1, 1), oof_labels)

oof_proba = platt.predict_proba(oof_scores.reshape(-1, 1))[:, 1]
test_proba = platt.predict_proba(test_scores.reshape(-1, 1))[:, 1]

# -----------------------------------------------
# STEP 2: (Optional) Try beta calibration, compare
# -----------------------------------------------
try:
    from betacal import BetaCalibration
    bc = BetaCalibration(parameters="abm")
    bc.fit(oof_scores.reshape(-1, 1), oof_labels)
    oof_proba_beta = bc.predict(oof_scores.reshape(-1, 1))
    test_proba_beta = bc.predict(test_scores.reshape(-1, 1))
    
    # Compare Brier scores — pick whichever is lower
    b_platt = brier_score_loss(oof_labels, oof_proba)
    b_beta = brier_score_loss(oof_labels, oof_proba_beta)
    print(f"Platt Brier: {b_platt:.4f}, Beta Brier: {b_beta:.4f}")
    if b_beta < b_platt:
        oof_proba = oof_proba_beta
        test_proba = test_proba_beta
        print("Using beta calibration")
    else:
        print("Using Platt calibration")
except ImportError:
    print("betacal not installed — using Platt only")

# -----------------------------------------------
# STEP 3: K sweep on OOF calibrated probas
# -----------------------------------------------
results = []
n_test = len(test_proba)
for k in range(5, 250, 5):
    if k >= len(oof_proba):
        break
    thresh = np.sort(oof_proba)[::-1][k - 1]
    preds = (oof_proba >= thresh).astype(int)
    p, r, _, _ = precision_recall_fscore_support(
        oof_labels, preds, average='binary', zero_division=0
    )
    score = (p + r) / 2
    results.append({'K': k, 'score': score, 'P': p, 'R': r, 'thresh': thresh})

best = max(results, key=lambda x: x['score'])
print(f"Optimal OOF K={best['K']}, (P+R)/2={best['score']:.4f}, P={best['P']:.3f}, R={best['R']:.3f}")

# -----------------------------------------------
# STEP 4: Apply optimal K to test
# -----------------------------------------------
K_final = best['K']
ranked_idx = np.argsort(test_proba)[::-1]
test_preds = np.zeros(n_test, dtype=int)
test_preds[ranked_idx[:K_final]] = 1

print(f"Submitting K={K_final} positives (test prevalence est = {K_final/n_test:.3f})")

# -----------------------------------------------
# STEP 5: (Optional) BBSE prevalence check
# -----------------------------------------------
from sklearn.metrics import confusion_matrix
from numpy.linalg import solve

preds_oof_binary = (oof_proba >= 0.5).astype(int)
C = confusion_matrix(oof_labels, preds_oof_binary, normalize='true')
mu_test = np.array([1 - test_proba.mean(), test_proba.mean()])
try:
    w = solve(C.T, mu_test)
    w = np.clip(w, 0, 1)
    w /= w.sum()
    est_prev = w[1]
    K_bbse = int(round(n_test * est_prev))
    print(f"BBSE estimated test prevalence: {est_prev:.4f} → K_BBSE = {K_bbse}")
    print(f"Compare: K_oof_sweep={K_final}, K_bbse={K_bbse}")
    # Use K_bbse only if it's close to K_final (within 30%) — otherwise BBSE is unreliable
    if abs(K_bbse - K_final) / K_final < 0.30:
        # Blend: average the two K estimates
        K_blend = int(round((K_final + K_bbse) / 2))
        print(f"Blended K = {K_blend}")
except Exception as e:
    print(f"BBSE failed: {e}")
```

---

## 9. Key Insight for V44 Specifically

V44's consensus score is already a **rank-based composite** (vote fraction + rank-pct tiebreaker). This means:

1. The AUC/ranking is already as good as the ensemble can make it. Calibration will NOT improve which samples are ranked high.
2. Calibration only converts the scale to [0,1] probabilities — useful for K threshold selection.
3. Since V44 was presumably tuned with some K, the main question is: **is the current K optimal given the test prevalence?**
4. **If V44 submitted K=154 and the actual test positives are ~100–110, you're over-predicting and hurting precision.** Calibration + BBSE or OOF sweep can catch this.
5. The (R+P)/2 scoring means: if you submit K=22 (ultra-conservative, only the very top), you get R~1, P~1 → score=100 IF your top-22 are all correct. With AUC=0.89, top-22 catches ~60% of TPs → R=0.6, P=1.0 → score=80. **This K=22 might be worth trying even without calibration.**

---

## 10. Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| Isotonic overfit on val fold | High | -0.5 to -2 LB | Use Platt/beta instead |
| Calibrator trained on same data as model | Medium | Score inflates OOF, degrades LB | Always use OOF-only |
| BBSE singular matrix | Medium | Can't estimate prevalence | Fall back to OOF K sweep |
| Beta calibration not installed | Low | Use Platt instead | `pip install betacal` |
| K-sweep overfits to OOF fold | Low | OOF optimal K ≠ LB optimal K | Smooth K sweep, pick stable plateau |

---

## Sources

- [sklearn Calibration Docs](https://scikit-learn.org/stable/modules/calibration.html) — authoritative, covers all methods
- [CalibratedClassifierCV API](https://scikit-learn.org/stable/modules/generated/sklearn.calibration.CalibratedClassifierCV.html)
- [Beta Calibration Paper (PMLR 2017)](https://proceedings.mlr.press/v54/kull17a/kull17a.pdf)
- [Classifier Calibration Survey (Springer ML 2023)](https://link.springer.com/article/10.1007/s10994-023-06336-7)
- [BBSE Paper — Label Shift Detection](https://arxiv.org/abs/1802.03916)
- [Optimal Thresholding for F1 (PMC)](https://pmc.ncbi.nlm.nih.gov/articles/PMC4442797/)
- [Platt vs Isotonic FastML guide](https://fastml.com/classifier-calibration-with-platts-scaling-and-isotonic-regression/)
- [ROC-Regularized Isotonic Regression (arXiv 2023)](https://arxiv.org/abs/2311.12436)

---

**Confidence: High**
Calibration theory is well-settled. The specific recommendations for Platt > isotonic on small N, beta for skewed distributions, and BBSE for prevalence shift are supported by multiple authoritative sources. Uncertainty is only in the actual LB lift, which depends on whether V44's K is currently suboptimal.
