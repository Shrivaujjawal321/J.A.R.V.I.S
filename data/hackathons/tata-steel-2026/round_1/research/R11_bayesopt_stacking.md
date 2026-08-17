# R11 — Bayesian-Optimized Stacking Weights vs Equal-Vote Consensus
**Context:** V44 = equal-vote consensus of 5 paradigms + V4_154 anchor + rank-pct-mean tiebreak. LB 72.83.
**Target:** Learn paradigm weights w_1..w_6 to beat equal-vote. Goal: 80+.
**Date:** 2026-05-24

---

## 1. Executive Summary

Equal-vote consensus is a strong, safe baseline but provably suboptimal when paradigms have different
discrimination power for your specific task (steel-coil defect detection at K=200). Learned weights
can add **0.5–2.5 LB points** in practice. The key risk is overfitting a small OOF pool —
controlled by nested CV and L1 regularization. **Recommended approach: Optuna with Dirichlet
simplex sampling, 300 trials, objective = OOF (R+P)/2 at K=200, validated on a held-out fold.**

---

## 2. Method Comparison Matrix

| Method | Search Space | Gradient-free? | Overfits small N? | Implementation effort | Expected lift |
|---|---|---|---|---|---|
| Optuna (Dirichlet, TPE) | w_1..w_6 simplex | Yes | Low–Med | Low | 0.5–2 pts |
| scipy SLSQP | w_1..w_6 simplex | No (needs grad) | Low | Very Low | 0.3–1 pt |
| CMA-ES | w_1..w_6 continuous | Yes | Med (need normalization) | Low | 0.5–2 pts |
| Stacked LR (meta-learner) | Coefficient vector | No | Low (L2 reg) | Low | 0.5–1.5 pts |
| Linear Programming (LP/ILP) | Weights + threshold | Solver-based | Low | Medium | 0.5–1 pt |
| Bayesian Model Averaging | Marginal likelihood | N/A | Low | High | 0.3–0.8 pt |
| Per-cluster weighting | Separate w per cluster | Varies | High | High | 1–3 pts (risky) |
| Mixture-of-Experts gating | Gating network | No (NN) | High | High | 1–3 pts (risky) |

---

## 3. Detailed Method Analysis

### 3.1 Optuna — Dirichlet TPE (RECOMMENDED FIRST ATTEMPT)

**Why it fits your problem:**
- 6 paradigm weights on simplex → black-box, non-differentiable objective ((R+P)/2 at K=200)
- TPE (Tree-structured Parzen Estimator) is efficient for 6-dim continuous space
- Dirichlet sampling natively handles the sum-to-1 constraint without rejection loops
- No gradients needed — your metric is a rank-based step function

**How Optuna's Dirichlet trick works:**

```python
import optuna
import numpy as np

# oof_scores: shape (n_rows, 6) — one column per paradigm's OOF probability/score
# oof_labels: shape (n_rows,)  — binary defect ground truth

def objective(trial):
    # Sample 6 raw values from Uniform[0,1], transform to Dirichlet
    x = [-np.log(trial.suggest_float(f"x_{i}", 1e-9, 1.0)) for i in range(6)]
    w = np.array(x) / sum(x)  # Dirichlet: sums to 1, all > 0

    # Store actual weights as user attrs for inspection
    for i, wi in enumerate(w):
        trial.set_user_attr(f"w_{i}", wi)

    # Weighted ensemble score
    combined = oof_scores @ w  # (n_rows,)

    # Evaluate at K=200
    top_k_idx = np.argsort(combined)[-200:]
    pred_labels = np.zeros(len(combined), dtype=int)
    pred_labels[top_k_idx] = 1

    precision = (pred_labels & oof_labels).sum() / pred_labels.sum()
    recall    = (pred_labels & oof_labels).sum() / oof_labels.sum()
    score = (recall + precision) / 2

    return -score  # minimize negative = maximize

study = optuna.create_study(
    direction="minimize",
    sampler=optuna.samplers.TPESampler(seed=42)
)
study.optimize(objective, n_trials=300, show_progress_bar=True)

best_w = np.array([study.best_trial.user_attrs[f"w_{i}"] for i in range(6)])
print("Optimal weights:", best_w)
print("Best OOF score:", -study.best_value)
```

**Practical notes:**
- 300 trials for 6 dims is sufficient. 500 if you have time.
- Use `suggest_float(f"x_{i}", 1e-9, 1.0)` not `0` to avoid log(0)
- Optuna 4.7+ (Jan 2026) is stable; uses TPE by default which is more efficient than random
- If any paradigm consistently gets w < 0.02, consider dropping it from the ensemble

---

### 3.2 scipy SLSQP — Fast Gradient-Based with Simplex Constraint

Fastest to implement (2 minutes). Works because scipy will numerically approximate gradients.

```python
from scipy.optimize import minimize
import numpy as np

def neg_f1_at_k(weights, oof_scores, oof_labels, k=200):
    weights = np.array(weights)
    weights = np.maximum(weights, 0)
    weights /= weights.sum()

    combined = oof_scores @ weights
    top_k_idx = np.argsort(combined)[-k:]
    pred = np.zeros(len(combined), dtype=int)
    pred[top_k_idx] = 1

    tp = (pred & oof_labels).sum()
    precision = tp / pred.sum() if pred.sum() else 0
    recall    = tp / oof_labels.sum() if oof_labels.sum() else 0
    return -((recall + precision) / 2)

n_paradigms = 6
result = minimize(
    neg_f1_at_k,
    x0=np.ones(n_paradigms) / n_paradigms,  # warm-start from equal weights
    args=(oof_scores, oof_labels, 200),
    method='SLSQP',
    bounds=[(0, 1)] * n_paradigms,
    constraints={'type': 'eq', 'fun': lambda w: w.sum() - 1},
    options={'maxiter': 200, 'ftol': 1e-9}
)
print("Weights:", result.x / result.x.sum())  # re-normalize for safety
```

**Key limitation:** SLSQP uses numerical gradients on a step-function objective (discrete rank cut at K=200).
The gradient is 0 almost everywhere — convergence is unreliable. **Use Optuna or CMA-ES instead for rank-based metrics.**

**When SLSQP works well:** If you replace the metric with a smooth proxy (e.g., sum of paradigm scores for
top-200 positives, or log-loss), SLSQP converges cleanly.

---

### 3.3 CMA-ES — Best for Non-Differentiable Objectives

CMA-ES (Covariance Matrix Adaptation Evolution Strategy) is the canonical choice for black-box
optimization of non-differentiable losses. The AutoML literature (arxiv:2307.00286) shows it
**statistically outperforms Greedy Ensemble Selection (GES)** on balanced-accuracy metrics.

**Critical finding from AutoML paper (2307.00286):**
- Unconstrained CMA-ES OVERFITS severely on ROC AUC: val rank 1.02 → test rank 1.83 (big degradation)
- Fix: **apply softmax normalization BEFORE aggregation** + pseudo-discrete sparsity constraint
- With normalization: CMA-ES matches or beats GES with no overfitting
- Keeping ensemble sparse (~6 non-zero weights vs ~13) improves generalization
- Monitor val-to-test rank drift: > 0.5–1.0 rank positions = dangerous overfit

```python
import cma
import numpy as np

def neg_score(weights_raw):
    # softmax normalization prevents unconstrained drift
    w = np.exp(weights_raw) / np.exp(weights_raw).sum()

    combined = oof_scores @ w
    top_k_idx = np.argsort(combined)[-200:]
    pred = np.zeros(len(combined), dtype=int)
    pred[top_k_idx] = 1
    tp = (pred & oof_labels).sum()
    p = tp / pred.sum() if pred.sum() else 0
    r = tp / oof_labels.sum() if oof_labels.sum() else 0
    return -((r + p) / 2)

x0 = np.zeros(6)          # log-space starting point = uniform weights after softmax
sigma0 = 0.5               # initial step size

es = cma.CMAEvolutionStrategy(x0, sigma0, {
    'maxiter': 200,
    'tolx': 1e-7,
    'seed': 42,
    'verbose': 1
})
es.optimize(neg_score)

raw_best = es.result.xbest
best_w = np.exp(raw_best) / np.exp(raw_best).sum()
print("CMA-ES optimal weights:", best_w)
```

Install: `pip install cma` (~100KB, no heavy deps)

---

### 3.4 Stacked Logistic Regression (Meta-Learner)

You noted LGB stacking failed. LR stacking is a different beast — it's essentially learning a
soft linear combination of paradigm OOF scores with L2 regularization preventing overfitting.

**Why LGB stacking failed but LR may work:**
- LGB can memorize OOF patterns → overfit small meta-train set
- LR with L2 (C=1.0) is equivalent to ridge regression on paradigm outputs
- Coefficients are interpretable as weights
- sklearn's LogisticRegression with `C` tuned on validation = safe and fast

```python
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
import numpy as np

# meta_X: (n_rows, 6) = OOF paradigm scores
# meta_y: (n_rows,)   = binary defect labels

# Scale features (important for LR coefficient interpretation)
scaler = StandardScaler()
meta_X_scaled = scaler.fit_transform(meta_X)

# Use low C (strong regularization) to avoid overfitting
# C=0.01 → strong L2; C=1.0 → moderate L2
for C in [0.001, 0.01, 0.1, 1.0]:
    lr = LogisticRegression(C=C, max_iter=1000, random_state=42)
    lr.fit(meta_X_scaled, meta_y)
    proba = lr.predict_proba(meta_X_scaled)[:, 1]

    top_k = np.argsort(proba)[-200:]
    pred = np.zeros(len(proba), dtype=int)
    pred[top_k] = 1
    tp = (pred & meta_y).sum()
    precision = tp / pred.sum()
    recall = tp / meta_y.sum()
    print(f"C={C}: (R+P)/2 = {(recall+precision)/2:.4f}, coefs = {lr.coef_[0]}")
```

**The coef_ values after fitting ARE the learned weights** (in scaled space).
To get interpretable weights back: un-scale via `coef / scaler.scale_`.

**Advantage over Optuna:** Closed-form solution, no search needed, very fast.
**Risk:** LR optimizes log-loss, not your actual (R+P)/2@K=200 metric — slight mismatch.

---

### 3.5 Linear Programming for Optimal K-Selection

LP formulation: instead of optimizing weights on continuous scores, directly solve for a binary
selection vector x ∈ {0,1}^N subject to sum(x) = K=200, maximizing TP.

**Simplified LP relaxation:**

```python
from scipy.optimize import linprog
import numpy as np

# For fixed weights w, combined score = oof_scores @ w
# The K-cut threshold is a function of w
# LP won't directly solve rank-based metrics well — use as post-hoc threshold optimizer

# Alternative: LP to find optimal weight combination
# Maximize: Σ_i combined_i * y_i  (reward score mass on true positives)
# Subject to: Σ_j w_j = 1, w_j >= 0

# combined_i = Σ_j oof_scores[i,j] * w_j = oof_scores[i,:] @ w

# Objective: maximize Σ_i y_i * (oof_scores[i,:] @ w)
#          = maximize w^T (oof_scores^T @ y)

# This is trivial LP: put all weight on paradigm with highest oof_scores^T @ y
c = -(oof_scores.T @ oof_labels)  # negative for minimization
A_eq = np.ones((1, 6))
b_eq = [1.0]
bounds = [(0, 1)] * 6
result = linprog(c, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')
print("LP weights:", result.x)
```

**Limitation:** This LP objective (maximize TP mass) doesn't respect the top-K constraint.
It degenerates to a one-hot solution (all weight on best single paradigm).
**LP is better suited for threshold optimization than weight search.** Not recommended as primary approach.

---

### 3.6 Per-Coil-Cluster Weighting

The idea: coils may cluster into sub-populations (e.g., by grade, thickness, width, speed).
For cluster A, paradigm 3 (temporal) might dominate; for cluster B, paradigm 1 (isolation forest) wins.

**Algorithm:**
1. Cluster coils in feature space: `KMeans(n_clusters=4)` on coil-level features
2. For each cluster, run Optuna weight search on that cluster's OOF rows only
3. At inference: assign each test coil to nearest cluster → use that cluster's weights

**Risk assessment:**
- With 6 paradigms and 4 clusters = 24 free parameters → severe overfit on small N
- Only viable if each cluster has > 500 OOF rows
- Partial fix: use cluster as a feature in LR meta-learner (interaction term) instead of full separate models

**Practical compromise:**

```python
from sklearn.cluster import KMeans
import numpy as np

# Step 1: Cluster test coils by coil-level features (not row-level)
coil_features = ...  # e.g., grade, thickness, speed per coil
km = KMeans(n_clusters=3, random_state=42).fit(coil_features)
cluster_ids = km.predict(coil_features)

# Step 2: Train separate LR per cluster (with high regularization)
from sklearn.linear_model import LogisticRegression
cluster_models = {}
for c in range(3):
    mask = cluster_ids == c
    if mask.sum() < 200:
        cluster_models[c] = None  # fallback to global model
        continue
    lr = LogisticRegression(C=0.01, max_iter=1000)
    lr.fit(meta_X[mask], meta_y[mask])
    cluster_models[c] = lr
```

**Verdict:** High-risk, medium-reward. Try only after global weight optimization plateau.

---

### 3.7 Mixture-of-Experts (MoE) Gating Network

MoE assigns each input row to its "expert" (paradigm) based on input features. The gating network
outputs soft weights per row, not global weights.

**Architecture for tabular steel data:**
- Gating: small neural net or LR on row features → softmax → per-row weight vector w(x)
- Expert outputs: paradigm OOF scores
- Final: sum_j w_j(x) * paradigm_j(x)

**Why it might work:** Different defect types may have different signal sources. Cracks may be
better detected by temporal paradigms; pits by spatial isolation forest.

**Why it might fail:**
- Training a gating network requires the combined OOF scores AND matching features
- If row features are correlated with paradigm quality, MoE wins
- If not, gating is noise and it overfits
- Needs substantial data to train a credible gating network (>2000 OOF rows)

**Simplified 2-layer gating in sklearn:**

```python
from sklearn.linear_model import LogisticRegression
import numpy as np

# Gate: for each row, which paradigm should we trust most?
# Proxy: use per-paradigm "correctness" as soft label
# correctness[i,j] = 1 if paradigm j would rank row i in top-200 AND row i is truly defective

for j in range(6):
    p_scores = oof_scores[:, j]
    top_k = np.argsort(p_scores)[-200:]
    correctness[:, j] = 0
    correctness[top_k[oof_labels[top_k] == 1], j] = 1

# Train gating per paradigm (one-vs-rest)
gates = []
for j in range(6):
    g = LogisticRegression(C=0.1).fit(row_features, correctness[:, j])
    gates.append(g)

# Inference: per-row weights
gate_w = np.column_stack([g.predict_proba(row_features)[:, 1] for g in gates])
gate_w /= gate_w.sum(axis=1, keepdims=True)  # row-normalize
final_score = (oof_scores * gate_w).sum(axis=1)
```

**Verdict:** Theoretically compelling, but highest engineering cost. Try post-global-weight-opt.

---

### 3.8 Bayesian Model Averaging (BMA)

BMA assigns weights proportional to the marginal likelihood (how well each paradigm explains
the observed defect labels, integrating over parameters).

**BIC approximation (fastest):**

```python
import numpy as np
from sklearn.metrics import log_loss

def bma_weights_bic(oof_scores, oof_labels, n_params_per_model=1):
    """Approximate BMA weights via BIC: weight_j ∝ exp(-BIC_j / 2)"""
    n = len(oof_labels)
    bic_scores = []
    for j in range(oof_scores.shape[1]):
        scores = np.clip(oof_scores[:, j], 1e-9, 1 - 1e-9)
        ll = -log_loss(oof_labels, scores, normalize=False)  # sum log-likelihood
        bic = -2 * ll + n_params_per_model * np.log(n)
        bic_scores.append(bic)
    bic_scores = np.array(bic_scores)
    log_weights = -0.5 * (bic_scores - bic_scores.min())  # relative to best
    weights = np.exp(log_weights)
    return weights / weights.sum()

w_bma = bma_weights_bic(oof_scores, oof_labels)
print("BMA weights:", w_bma)
```

**Characteristics:**
- No optimization loop — closed-form from OOF log-likelihoods
- BIC penalizes model complexity (n_params); here all paradigms have similar complexity so penalty is equal
- Effectively: weight ∝ exp(-log_loss) = exp(log_likelihood)
- This IS a valid weight assignment but metric mismatch: BIC uses log-loss, not (R+P)/2@K=200
- Fast to compute, zero tuning, good as a baseline comparison against Optuna result

---

## 4. Cross-Validation Safety Protocol (CRITICAL)

**The core risk:** If you run weight search on the same OOF folds that generated the paradigm scores,
you have no out-of-sample estimate of the weights' validity.

### Protocol A — Nested K-Fold (Cleanest, Recommended)

```
Outer: 5-fold CV
  For each outer fold (test fold):
    Inner: weight search on the other 4 folds' OOF scores
    Validate weights on outer (test) fold
Report: mean (R+P)/2 across 5 outer folds
```

If inner-fold score ≈ outer-fold score: weights generalize.
If inner >> outer: overfit detected. Increase regularization or reduce n_trials.

### Protocol B — Temporal Holdout (For Tata Steel Specifically)

Since steel coil data is likely temporal (production order matters):
```
Early coils (80%): weight search OOF pool
Late coils (20%): weight validation holdout
```
This respects temporal ordering and prevents future leakage.

### Protocol C — K-Fold Average Weights (Quick and Dirty)

```python
fold_weights = []
for fold_i in range(5):
    val_mask = oof_folds == fold_i
    train_mask = ~val_mask

    # Run Optuna on train portion of OOF
    w_fold = run_optuna_weight_search(
        oof_scores[train_mask], oof_labels[train_mask], n_trials=100
    )
    fold_weights.append(w_fold)

# Average weights across folds = more stable than single-split
final_w = np.mean(fold_weights, axis=0)
final_w /= final_w.sum()
```

### Red Flags for Overfitting

1. Optimal weight puts > 0.8 on a single paradigm → almost certainly overfit
2. OOF score with learned weights > OOF score with equal weights by > 3 pts → suspect
3. n_trials >> 50 × n_paradigms without nested CV → search has seen too many val evaluations
4. Any paradigm getting w < 0.01 when equal-weight gives it ~0.17 → likely overfitting to noise

---

## 5. Expected Lift Estimates

Based on ensemble literature (AutoML 2307.00286, COWE paper, Kaggle meta-wisdom):

| Scenario | Expected OOF lift | Expected LB lift |
|---|---|---|
| 5 highly similar paradigms | +0.3–0.7 pts | +0.2–0.5 pts |
| 5 paradigms with 1 clearly dominant | +1.0–2.5 pts | +0.7–2.0 pts |
| 5 paradigms with orthogonal errors | +0.5–1.5 pts | +0.4–1.2 pts |
| With per-cluster weighting (if clusters valid) | +1.5–3.5 pts | +1.0–2.5 pts |

**For V44 (72.83 LB):** If your paradigms are reasonably diverse, targeting **73.5–74.5 via
global weight optimization is realistic.** Per-cluster could push to 75+, but with overfit risk.

**Key insight from AutoML literature:** The lift is NOT primarily from weights — it's from
**paradigm diversity**. If paradigms share similar error patterns, no weighting scheme helps much.
The first diagnostic should be: correlation of paradigm OOF error vectors.

```python
# Check paradigm diversity before weight search
oof_binary_errors = (oof_pred_topk != oof_labels).astype(int)  # per-paradigm errors
corr_matrix = np.corrcoef(oof_binary_errors.T)
print("Paradigm error correlation:\n", corr_matrix)
# If all off-diagonal > 0.8: paradigms agree → weighting gives < 0.5 pt lift
# If some off-diagonal < 0.5: paradigms disagree on different samples → weighting helps more
```

---

## 6. Recommended Execution Order

### Step 1: Diversity Check (5 min)
Compute paradigm error correlation on OOF. If max off-diagonal correlation > 0.85 across
all pairs, weighting is unlikely to help much (< 0.5 pt). Proceed but calibrate expectations.

### Step 2: BMA Quick Baseline (2 min)
Compute BMA weights from OOF log-loss. Check if any paradigm is clearly dominant (w > 0.4).
This is your zero-cost weight estimate and a sanity check for the optimization results.

### Step 3: Optuna Dirichlet Search (10–15 min)
- 300 trials, TPE sampler
- Objective: OOF (R+P)/2 at K=200 on 80% of OOF pool (Protocol B temporal split)
- Validate on remaining 20%
- If val score within 0.5 of train score: weights are good → use on test
- If val score drops > 1 pt from train: reduce n_trials to 100 and re-run

### Step 4: CMA-ES Cross-Check (5 min)
Run CMA-ES with softmax normalization on same 80% train pool.
If CMA-ES weights ≈ Optuna weights → high confidence in the solution.
If they diverge: the landscape is flat/noisy → don't trust either; fall back to equal vote.

### Step 5: LR Meta-Learner Comparison (3 min)
Fit sklearn LR with C=0.01 on same train pool. Compare predicted weights to Optuna.
If all three methods (Optuna, CMA-ES, LR) agree on which paradigm is top-weighted:
that paradigm is genuinely better — strong signal.

### Step 6: Cluster Weighting (optional, if Steps 1–5 plateau)
Only if OOF diversity analysis shows sub-population structure and you have > 300 rows per cluster.

---

## 7. Anti-Patterns (Do NOT Do)

1. **Optimize weights on the entire OOF pool, then report OOF score as validation.** That's test-on-train.
2. **Use Optuna with n_trials=1000 on < 5000 OOF rows without nested CV.** Weight search DF = n_trials * n_paradigms ≈ 6000 effective params compared to 5000 samples = guaranteed overfit.
3. **Trust any single-method result without cross-checking.** Always compare 2+ methods.
4. **Abandon equal-vote if learned-weight OOF gain is < 0.3 pts.** Below 0.3 pts OOF improvement, LB noise will swamp the signal.
5. **Run CMA-ES without softmax normalization on ROC-AUC-like metrics.** Shown to overfit drastically (val rank 1.02 → test rank 1.83 in AutoML paper).
6. **Use LP formulation for weight search.** LP degenerates to one-hot (puts all weight on best paradigm). Only useful for threshold optimization.

---

## 8. Final Recommendation for V45

**First ship: V45 = Optuna Dirichlet weights (Protocol B temporal holdout)**

```python
# Pseudocode for V45
weights_v45 = optuna_dirichlet_search(
    oof_scores=oof_scores_6paradigms,  # (N, 6)
    oof_labels=oof_labels,
    k_top=200,
    n_trials=300,
    train_fraction=0.8,  # Protocol B: temporal split
    seed=42
)

# Cross-check
weights_cmaes = cmaes_search(oof_scores_6paradigms, oof_labels, k=200)
print("Optuna:", weights_v45)
print("CMA-ES:", weights_cmaes)
print("Agreement:", np.allclose(weights_v45, weights_cmaes, atol=0.05))

# If agreement: use average as final weights for robustness
final_w = (weights_v45 + weights_cmaes) / 2
final_w /= final_w.sum()
```

**Expected result:** If paradigms are moderately diverse (error correlation < 0.75), V45 should
gain 0.8–1.5 pts OOF, translating to ~0.6–1.2 pts LB. Target: 73.5–74.0 LB from 72.83.

To hit 80+, weight optimization alone is insufficient. Combine with:
- Better paradigm scores (feature engineering, architecture improvements)
- Per-cluster weighting on validated sub-populations
- Threshold/K optimization (is K=200 actually optimal for your test set?)

---

## Sources

- [CMA-ES for Post Hoc Ensembling in AutoML: A Great Success and Salvageable Failure](https://arxiv.org/html/2307.00286) — Core paper on CMA-ES overfit behavior + normalization fix
- [Optuna FAQ — Dirichlet Simplex Sampling](https://optuna.readthedocs.io/en/stable/faq.html) — Official Optuna code for sum-to-1 weights
- [Optuna GitHub](https://github.com/optuna/optuna) — v4.7.0 (Jan 2026), actively maintained
- [Finding Optimal Weights using Optuna](https://medium.com/@khawajaabaid/finding-optimal-weights-for-taking-weighted-average-to-ensemble-models-using-optuna-36569c46292b) — Practical implementation guide
- [Optimizing Ensemble Weights for Regression (COWE paper)](https://arxiv.org/pdf/1908.05287) — Cross-validated Optimal Weighted Ensemble methodology
- [Bayesian Stacking via Proper Scoring Rule](https://arxiv.org/pdf/2509.04203) — Recent BMA/stacking theory
- [Kaggle Grandmasters Playbook — NVIDIA](https://developer.nvidia.com/blog/the-kaggle-grandmasters-playbook-7-battle-tested-modeling-techniques-for-tabular-data/) — 2025 stacking patterns in tabular competitions
- [Mixture of Experts Introduction](https://machinelearningmastery.com/mixture-of-experts/) — MoE gating mechanism overview
- [PhishNet — Optuna Stacking (2026)](https://www.nature.com/articles/s41598-025-31447-7) — Recent applied Optuna stacking
- [Hybrid Stacking with Optuna for Rock Mechanics (2025)](https://link.springer.com/article/10.1007/s00603-025-05043-0) — Domain-specific Optuna stacking lift evidence
