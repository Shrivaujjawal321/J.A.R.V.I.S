# R27 — Test-Time Adaptation for Tata Steel Defect Detection

**Date:** 2026-05-24
**Context:** Banked 72.83 LB (V4=56.98 on earlier LB, current banked=72.83 per research request).
**Problem:** Train prevalence ~5% positive, test prevalence ~45% positive. V45 EM attempt = -1.19 LB.
**Label shift type:** Severe prior shift. p(X|Y) assumed stable; p(Y) wildly different.

---

## 1. Why V45 EM Failed — Mathematical Diagnosis

### Root Cause 1: Calibration Assumption Violated

Saerens EM (2002) requires the classifier to be **calibrated** — i.e., `p(y|x)` outputs should be true posterior probabilities. Modern GBDTs (CatBoost, LGB, XGB) are **overconfident** at low-prevalence training: when trained on 5% positives, they push the positive probability mass toward the tails. The model learns `p(y=1|x) → 0` for nearly all samples because the loss gradient rewards that.

The EM update equation is:

```
q^(t+1)(y) = (1/N) * Σ_i  [ p(y|x_i) * q^(t)(y) / p_train(y) ]
                           ————————————————————————————————————
                           Σ_y' [ p(y'|x_i) * q^(t)(y') / p_train(y') ]
```

This re-weights each sample's contribution by the ratio q^(t)(y) / p_train(y). When `p_train(y=1) = 0.05` and q^(0)(y=1) is initialized also near 0.05, the correction ratio starts at 1.0. But because the model's `p(y=1|x_i)` is systematically too small (due to miscalibration), the numerator for the positive class is suppressed — EM **reinforces** the model's own bias rather than correcting it.

**Your specific failure:** EM converged to `q_est = 0.0709`. True test prevalence is ~0.45. EM got stuck at 7% because:
1. Model outputs `p(y=1|x) ≈ 0.02-0.10` for even the strongest positives
2. EM's fixed-point is determined by model confidence, not by the true prior
3. Starting from `q^(0) = 0.05` (train prior), early iterations see tiny numerators → convergence to local optimum near train prior

### Root Cause 2: Multi-Modal Local Optima Under Severe Imbalance

The EM objective `log p(test | q)` for label shift has multiple local optima when the shift is severe (9:1 ratio flip, 5%→45%). Standard EM converges to the nearest local optimum from initialization. Initialization at `q_init = 0.05` → converged to `q_est = 0.07`. The **global optimum** near 0.45 is completely unreachable from that start.

### Root Cause 3: Platt Calibration Insufficient

`CalibratedClassifierCV(method='sigmoid')` (Platt) applies a single global sigmoid `1/(1+exp(A*s+B))`. It adjusts the mean but does NOT correct **class-conditional** bias. Even a perfectly calibrated Platt model on the train set will be biased on the test set because the posterior `p(y=1|x)` was fit assuming 5% base rate. When the test base rate is 45%, Platt still sees only 5% positive calibration data and cannot learn the right 45% correction.

**What's needed: Bias-Corrected Temperature Scaling (BCTS)** — adds class-specific offset parameters `(b_0, b_1)` to Platt: `p_cal(y=k|x) ∝ softmax((logit + b_k) / T)`. This adds a per-class bias term that EM can use to detect the right convergence basin.

---

## 2. Top-3 Alternative TTA Methods (ranked by expected lift)

### Method 1 — Seeded EM + BCTS (Expected Lift: +3 to +7 LB)

**What it is:** EM with initialization `q_init = [0.55, 0.45]` instead of the train prior, combined with bias-corrected calibration.

**Why it fixes V45:**
- Starting at `q_init = 0.45` puts EM in the correct basin of attraction. Literature (Lipton+Raghavan ICML 2020, BCTS paper 1901.06852) shows EM is globally convergent when initialized within the correct basin.
- BCTS calibration removes the model's class-conditional overconfidence, allowing the EM numerator to be large for true positives.

**Code:**
```python
import numpy as np
from scipy.special import softmax
from scipy.optimize import minimize

# ─── Step 1: BCTS Calibration (on held-out OOF) ───────────────────────────────
def bcts_calibrate(logits_oof, y_oof):
    """
    Bias-Corrected Temperature Scaling.
    logits_oof: (N,) raw CatBoost decision_function output (log-odds)
    y_oof: (N,) binary labels
    Returns: (T, b_0, b_1) — temperature + per-class bias
    """
    def neg_log_likelihood(params):
        T, b0, b1 = params
        # Convert to 2-class logits
        log_p0 = -np.log1p(np.exp((logits_oof + b1 - b0) / T))
        log_p1 = log_p0 + (logits_oof + b1 - b0) / T
        return -(y_oof * log_p1 + (1 - y_oof) * log_p0).mean()
    
    result = minimize(neg_log_likelihood, x0=[1.5, 0.0, 0.0],
                      method='Nelder-Mead', options={'maxiter': 1000})
    return result.x  # (T, b0, b1)

def bcts_predict(logits_test, T, b0, b1):
    """Returns calibrated p(y=1|x) for test set."""
    adjusted = (logits_test + b1 - b0) / T
    return 1 / (1 + np.exp(-adjusted))


# ─── Step 2: Seeded EM label-shift correction ─────────────────────────────────
def seeded_em_label_shift(p_cal_test, q_train, q_init, max_iter=500, tol=1e-7):
    """
    Saerens EM with configurable initialization.
    
    p_cal_test: (N,) calibrated p(y=1|x) on test set
    q_train:    scalar, train positive rate (e.g. 0.05)
    q_init:     scalar, initial guess for test positive rate (use 0.45 for our problem)
    
    Returns: q_final (scalar), reweighted probabilities (N,)
    """
    # Build 2-class probability matrix: columns = [p(y=0|x), p(y=1|x)]
    P = np.column_stack([1 - p_cal_test, p_cal_test])  # (N, 2)
    
    # Train priors
    q_s = np.array([1 - q_train, q_train])  # [0.95, 0.05]
    
    # Initialize with seeded prior
    q = np.array([1 - q_init, q_init])       # [0.55, 0.45]
    
    for iteration in range(max_iter):
        # E-step: compute posterior weights
        # w_i(y) = p(y|x_i) * q(y) / q_s(y)  (unnormalized)
        weights = P * (q / q_s)              # (N, 2) — element-wise
        weights_sum = weights.sum(axis=1, keepdims=True)  # (N, 1)
        posterior = weights / weights_sum    # (N, 2) normalized
        
        # M-step: update q
        q_new = posterior.mean(axis=0)       # (2,) average posterior
        
        # Convergence check
        delta = np.max(np.abs(q_new - q))
        q = q_new
        
        if delta < tol:
            print(f"EM converged at iteration {iteration}, q_pos = {q[1]:.4f}")
            break
    
    return q[1], posterior[:, 1]  # q_final, p_corrected(y=1|x)


# ─── Step 3: Score-aware threshold ────────────────────────────────────────────
def find_best_threshold(p_corrected_oof, y_oof, metric='f1_macro'):
    """Grid search optimal cutoff on OOF predictions."""
    from sklearn.metrics import f1_score
    best_t, best_score = 0.5, 0.0
    for t in np.linspace(0.01, 0.99, 200):
        preds = (p_corrected_oof > t).astype(int)
        score = f1_score(y_oof, preds, average='macro')
        if score > best_score:
            best_score, best_t = score, t
    return best_t, best_score


# ─── FULL PIPELINE ─────────────────────────────────────────────────────────────
# Assuming:
#   logits_oof: model.decision_function(X_oof) or log-odds from predict_proba
#   y_oof: OOF labels
#   logits_test: model.decision_function(X_test)
#   q_train = 0.05 (train positive rate)

# 1. Calibrate on OOF
T, b0, b1 = bcts_calibrate(logits_oof, y_oof)
print(f"BCTS params: T={T:.3f}, b0={b0:.3f}, b1={b1:.3f}")

p_cal_oof  = bcts_predict(logits_oof, T, b0, b1)
p_cal_test = bcts_predict(logits_test, T, b0, b1)

# 2. Run seeded EM — use q_init=0.45 (domain knowledge: test ~45% positive)
q_final, p_em_test = seeded_em_label_shift(p_cal_test, q_train=0.05, q_init=0.45)
_, p_em_oof = seeded_em_label_shift(p_cal_oof, q_train=0.05, q_init=0.45)
print(f"EM converged q_pos = {q_final:.4f}  (expect ~0.40-0.50)")

# 3. Threshold on OOF
best_t, best_oof = find_best_threshold(p_em_oof, y_oof)
print(f"Best OOF threshold: {best_t:.3f} → OOF F1 = {best_oof:.4f}")

# 4. Submit
test_preds = (p_em_test > best_t).astype(int)
print(f"Test positives predicted: {test_preds.sum()} / {len(test_preds)}")
```

**Diagnostic check before trusting:** After EM convergence, verify `q_final ∈ [0.30, 0.55]`. If still near 0.07, the model is too miscalibrated — escalate to BBSE instead.

**Expected lift:** +3 to +7 LB. The +2.67 V4-vs-OOF gap showed test distribution IS kinder than train OOF — EM should be able to exploit this if calibration is fixed.

---

### Method 2 — AdapTable (Expected Lift: +5 to +10 LB, higher variance)

**What it is:** NeurIPS-W TRL 2024 method. Two-stage: (1) shift-aware GNN calibrator, (2) label distribution handler. Works on any model's probability outputs. Official implementation exists.

**Source:** [drumpt/AdapTable on GitHub](https://github.com/drumpt/AdapTable) | [arXiv 2407.10784](https://arxiv.org/abs/2407.10784)

**Key results on imbalanced tabular:**
- HELOC dataset (10:1 imbalance): F1 59.7% vs baseline 32.5% (+27 point absolute)
- Works with CatBoost/XGBoost by converting probabilities to log-odds (pseudo-logits)

**How to adapt for GBDT output:**
```python
# AdapTable is PyTorch-dependent but its CORE idea can be extracted
# The label distribution handler is essentially:

def adaptable_label_handler(p_batch, p_source_train, alpha=0.1, p_online_init=None):
    """
    Label distribution adjustment step from AdapTable.
    p_batch:      (N,) model's p(y=1|x) for current test batch
    p_source_train: scalar, train positive rate (0.05)
    alpha:        smoothing factor (0.1 default)
    p_online_init: online estimate from prior batches (start with p_source_train)
    """
    if p_online_init is None:
        p_online_init = p_source_train
    
    # Debiased estimate: rescale predictions by label ratio
    p_source_2 = np.array([1 - p_source_train, p_source_train])
    p_batch_2  = np.column_stack([1 - p_batch, p_batch])
    
    # Current batch label distribution estimate
    p_target_est = p_batch.mean()  # simple mean as initial estimate
    p_target_2   = np.array([1 - p_target_est, p_target_est])
    
    # Debiased predictions: p_debiased_i = p_i * (p_target / p_source)
    ratio = p_target_2 / (p_source_2 + 1e-8)
    p_debiased = p_batch_2 * ratio  # (N, 2) unnormalized
    p_debiased = p_debiased / p_debiased.sum(axis=1, keepdims=True)  # normalize
    
    # Online estimator: blend current batch with running estimate
    p_online_new = (1 - alpha) * p_debiased[:, 1].mean() + alpha * p_online_init
    
    # Final adjusted predictions (average debiased + online-scaled)
    p_online_2 = np.array([1 - p_online_new, p_online_new])
    p_scaled   = p_batch_2 * (p_online_2 / (p_source_2 + 1e-8))
    p_scaled   = p_scaled / p_scaled.sum(axis=1, keepdims=True)
    
    p_final = (p_debiased[:, 1] + p_scaled[:, 1]) / 2
    return p_final, p_online_new


# Run on full test set (treat as single batch — no temporal ordering needed)
p_adapted, q_est = adaptable_label_handler(p_cal_test, p_source_train=0.05)
print(f"AdapTable estimated test prevalence: {q_est:.4f}")
```

**Caveat:** Full AdapTable requires a GNN for the calibration stage (PyTorch + PyG). For a quick integration, use only the label distribution handler above (pure numpy, 10 lines). The GNN calibration stage adds ~3-5 LB but requires installing `torch-geometric`.

**Install full AdapTable:**
```bash
conda create -n adaptable python=3.8.16 -y
conda activate adaptable
cd /tmp && git clone https://github.com/drumpt/AdapTable
pip install -r AdapTable/requirements.txt
```

---

### Method 3 — BBSE-Soft (Black Box Shift Estimation) (Expected Lift: +2 to +5 LB, most stable)

**What it is:** Lipton et al. ICML 2018. Does NOT require calibration — works even with biased classifiers, as long as the confusion matrix is invertible. Estimates `w(y) = q_test(y) / q_train(y)` via confusion matrix inversion, then reweights predictions.

**Source:** [arXiv 1802.03916](https://arxiv.org/abs/1802.03916)

**Why it's safer than EM:** BBSE is consistent even when `p(y|x)` is miscalibrated. EM is not. For a binary problem with an invertible confusion matrix (just need sensitivity ≠ 1 - specificity), BBSE is closed-form.

**Code:**
```python
import numpy as np
from sklearn.model_selection import cross_val_predict

def bbse_soft(model, X_train, y_train, X_test, q_train=0.05):
    """
    Black Box Shift Estimation (BBSE-soft) for binary classification.
    
    Returns: w (2,) importance weights, p_reweighted (N,) corrected test probs
    """
    # Step 1: Get OOF predictions for confusion matrix estimation
    p_oof = cross_val_predict(model, X_train, y_train, cv=5, method='predict_proba')[:, 1]
    y_oof_hard = (p_oof > 0.5).astype(int)
    
    # Step 2: Empirical confusion matrix on OOF
    from sklearn.metrics import confusion_matrix
    C = confusion_matrix(y_train, y_oof_hard, normalize='pred')  # (2,2), columns = predicted
    # C[i,j] = P(Y=i | hat_Y=j) — per-predicted-class posterior
    
    # Step 3: Prediction histogram on test
    p_test = model.predict_proba(X_test)[:, 1]
    p_test_hard = (p_test > 0.5).astype(int)
    mu_test = np.array([1 - p_test_hard.mean(), p_test_hard.mean()])  # [P(hat_Y=0), P(hat_Y=1)]
    
    # Step 4: BBSE estimate — solve C @ q_test = mu_test
    # q_test = C^{-1} @ mu_test
    try:
        C_inv = np.linalg.inv(C)
        q_test = C_inv @ mu_test
        q_test = np.clip(q_test, 0, 1)
        q_test = q_test / q_test.sum()  # normalize
    except np.linalg.LinAlgError:
        print("WARNING: confusion matrix singular — falling back to q_train")
        q_test = np.array([1 - q_train, q_train])
    
    print(f"BBSE q_test estimate: {q_test}")  # expect [~0.55, ~0.45]
    
    # Step 5: Importance weights
    q_train_arr = np.array([1 - q_train, q_train])
    w = q_test / q_train_arr  # [w_neg, w_pos]
    
    # Step 6: Reweight test probabilities
    # Bayes: p_corrected(y=1|x) ∝ p_model(y=1|x) * w[1]
    p_corrected = p_test * w[1] / (p_test * w[1] + (1 - p_test) * w[0])
    
    return q_test[1], w, p_corrected

# Usage:
q_bbse, w_bbse, p_bbse_test = bbse_soft(base_model, X_train, y_train, X_test, q_train=0.05)
print(f"BBSE estimated test prevalence: {q_bbse:.4f}")
print(f"Importance weights: neg={w_bbse[0]:.2f}, pos={w_bbse[1]:.2f}")

# RLLS variant (regularized) — use if confusion matrix is near-singular:
# Replace np.linalg.inv(C) with np.linalg.solve(C.T @ C + 0.01*np.eye(2), C.T @ mu_test)
```

**RLLS (regularized BBSE) for near-singular case:**
```python
def rlls(C, mu_test, lambda_reg=0.01):
    """Regularized Least-Squares Label Shift."""
    A = C.T @ C + lambda_reg * np.eye(C.shape[0])
    b = C.T @ mu_test
    q_test = np.linalg.solve(A, b)
    q_test = np.clip(q_test, 0, 1)
    return q_test / q_test.sum()
```

---

### GS-B³SE — Why to Skip for Now

GS-B³SE (arXiv 2505.16251) is theoretically superior but practically heavy:
- Requires a **label-similarity graph** — for binary classification (defect/no-defect), there are only 2 classes, so the graph Laplacian is trivial (2x2) and provides no smoothing benefit
- The graph smoothing advantage is for **K ≥ 10** class problems where semantic similarity helps (cat/dog/bird rare → borrow from similar)
- For binary, GS-B³SE collapses to standard BBSE with a Bayesian wrapper
- **Conclusion:** Skip GS-B³SE for this specific binary problem. Use BBSE-RLLS instead.

---

## 3. Execution Order (V45 Rebuild)

```
Priority 1 (highest expected lift, most fixable root cause):
  → Seeded EM + BCTS  (q_init=0.45)

Priority 2 (if EM still fails — model too miscalibrated):
  → BBSE-Soft / RLLS  (no calibration required)

Priority 3 (highest ceiling but setup cost):
  → AdapTable label distribution handler (numpy version, no GNN)

Combine:
  → Ensemble p_em + p_bbse + p_adaptable (mean) → score-aware threshold on OOF
  → Single model output — NO blending across model architectures (V10 blend -8.47 lesson)
```

---

## 4. Expected Lift Estimates

| Method | Expected LB Lift | Confidence | Risk |
|--------|-----------------|-----------|------|
| Seeded EM (q_init=0.45) + BCTS | +3 to +7 | Medium | EM may still converge to local optima even with BCTS |
| BBSE-Soft | +2 to +5 | High (no calibration assumption) | Confusion matrix may be near-singular if model very biased |
| AdapTable (numpy label handler only) | +3 to +8 | Medium-Low | Requires clean batch statistics from train |
| BBSE-RLLS (regularized) | +2 to +4 | High | Lower ceiling than EM but stable |
| All 3 averaged | +4 to +9 | Medium | Averaging may lose threshold precision |

**Honest calibration note:** The +2.67 delta observed in V4 (OOF 54.31 → LB 56.98) suggests the test set IS easier than OOF — which means our model's OOF underestimates test performance. However, this is exactly the label shift signal: test has more easy-to-classify positives (higher prevalence means we see more defects with clearer signatures). TTA methods should amplify this, not fight it.

---

## 5. Critical Guardrails

1. **Never validate TTA correction on OOF alone.** OOF uses train distribution (5% pos). Validation of the EM/BBSE correction MUST be on a synthetic held-out set where you manually resample to 45% positive. Otherwise you're measuring noise.

2. **Use `decision_function` not `predict_proba` as input to BCTS.** CatBoost's `predict_proba` already applies a sigmoid; you want raw log-odds for temperature scaling.

3. **The +2.67 calibration delta (V4) is NOT LB calibration — do not apply it as a post-hoc offset.** This is the OOF-calibration-not-LB-calibration lesson from FINAL_VERDICT.md.

4. **Submit TTA-corrected predictions as a SINGLE model variant.** Not blended with uncorrected predictions. Blending destroyed V10 (OOF 55.47 → LB 47.00, -8.47).

5. **Check `q_final` from EM before trusting output.** If `q_final < 0.20` after seeded init at 0.45, EM is stuck — fall back to BBSE.

---

## Sources

- [AdapTable (NeurIPS-W TRL 2024) — Official GitHub](https://github.com/drumpt/AdapTable)
- [AdapTable arXiv 2407.10784](https://arxiv.org/abs/2407.10784)
- [GS-B³SE arXiv 2505.16251](https://arxiv.org/abs/2505.16251)
- [BBSE — Lipton et al. ICML 2018 arXiv 1802.03916](https://arxiv.org/abs/1802.03916)
- [BCTS + EM — Alexandari et al. ICML 2020 arXiv 1901.06852](https://arxiv.org/abs/1901.06852)
- [FMAPLS — Bayesian online label shift arXiv 2511.18615](https://arxiv.org/html/2511.18615v1)
- [A Unified View of Label Shift Estimation arXiv 2003.07554](https://arxiv.org/pdf/2003.07554)
