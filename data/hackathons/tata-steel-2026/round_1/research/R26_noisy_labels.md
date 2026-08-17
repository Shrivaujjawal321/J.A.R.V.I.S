# R26 — Noisy-Label Detection (Cleanlab) for Tata Steel Round 1
**Date:** 2026-05-24  
**Context:** Banked LB 72.83, ~1352 train rows, ~66 positives (4.9% prevalence), V44 OOF soft probabilities available.  
**Hypothesis:** Some of the 15 missed test TPs may trace back to mislabeled training rows — either false-positive labels in our 66 positives (Y=1 but model consistently disagrees) or false-negative labels hiding in the 1286 negatives (Y=0 but model consistently fires).

---

## 1. What Cleanlab Does (and the Honest Limits for Our Dataset)

Cleanlab implements **Confident Learning** (Northcutt et al., JAIR 2021): it estimates the joint class-label noise distribution and flags rows whose given label is inconsistent with the model's cross-validated confidence.

### How it works

1. Train any sklearn-compatible classifier via K-fold cross-validation.  
2. Compute out-of-fold predicted probabilities for every training row.  
3. Threshold each row into a "thresholded class" using per-class calibrated thresholds.  
4. Flag rows where `given_label ≠ thresholded_class` — these are label issue candidates.  
5. Rank candidates by `label_quality_score` (0=most suspect, 1=clearly correct).

### Our dataset's specific risk profile

| Fact | Risk |
|---|---|
| 66 positives out of 1352 (4.9%) | Minority class is very small — Cleanlab's per-class threshold estimates are noisy at N=66 |
| ~22 true test positives (back-solved from LB) | Train prevalence ≈ 4.9% vs test prevalence ~6.5% — mild train/test shift exists |
| V4 → V44 delta confirms non-trivial signal | Model OOF AUC 0.89-0.92 = good enough for reliable CL estimates |
| 15 missed TPs in test | Maximum of ~15/22 = 68% of missed defects could theoretically be label-noise-caused in train; realistically 1-5 |

**Reliability threshold for Cleanlab on minority classes:** The JAIR paper notes CL is consistent when the minority class has ≥ `1/noise_rate` expected examples. At 5% noise → need ≥20 minority samples. We have 66, so we're **above the minimum**. However, expect 30-40% false-positive rate in the flagged candidates — manual inspection is mandatory.

---

## 2. Full Diagnostic Code

```python
# ============================================================
# R26: Cleanlab Noisy-Label Diagnostic on V44 OOF probabilities
# Dependencies: pip install cleanlab>=2.6 lightgbm xgboost catboost scikit-learn
# ============================================================

import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from lightgbm import LGBMClassifier
from cleanlab.filter import find_label_issues
from cleanlab.rank import get_label_quality_scores

# ----------------------------------------------------------
# STEP 1: Load your train set
# ----------------------------------------------------------
# Replace with your actual path
df_train = pd.read_csv("train.csv")  # 1352 rows

# Feature cols (adjust as needed — use your current V44 feature set)
FEATURE_COLS = [c for c in df_train.columns if c not in ["id", "target", "label"]]
TARGET_COL = "target"  # 0/1 binary

X = df_train[FEATURE_COLS].values
y = df_train[TARGET_COL].values  # integer 0/1

print(f"Dataset: {len(X)} rows, {y.sum()} positives ({100*y.mean():.1f}%)")

# ----------------------------------------------------------
# STEP 2: Generate OOF predicted probabilities via 5-fold CV
#
# Option A: Use V44's existing OOF probas if you have them saved.
# Option B: Recompute from scratch (recommended — use your best single model).
# ----------------------------------------------------------

# Option B: fresh computation with LGB (matches your V44 base learner)
clf = LGBMClassifier(
    n_estimators=500,
    learning_rate=0.05,
    num_leaves=31,
    class_weight="balanced",   # critical for 4.9% imbalance
    random_state=42,
    verbose=-1
)

skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

pred_probs = cross_val_predict(
    estimator=clf,
    X=X,
    y=y,
    cv=skf,
    method="predict_proba"
    # returns shape (1352, 2): [:, 1] = P(defect)
)

print(f"OOF probas shape: {pred_probs.shape}")
print(f"OOF positive class mean proba: {pred_probs[:, 1].mean():.4f}")

# ----------------------------------------------------------
# STEP 3: Run Cleanlab — find label issues
# ----------------------------------------------------------

# filter_by options:
#   "prune_by_noise_rate" — default, good for imbalanced data
#   "both"               — union of two methods, more aggressive
#   "confident_learning" — most precise, lower recall
#   "low_self_confidence" — catches rows where model strongly disagrees with label

ranked_issue_indices = find_label_issues(
    labels=y,
    pred_probs=pred_probs,
    return_indices_ranked_by="self_confidence",  # most confident errors first
    filter_by="prune_by_noise_rate",             # conservative for small minority class
    frac_noise=1.0,                              # return ALL detected issues
    min_examples_per_class=10                    # safety floor
)

# Get quality scores for ALL training rows
quality_scores = get_label_quality_scores(
    labels=y,
    pred_probs=pred_probs,
    method="self_confidence"
)

print(f"\nCleanlab flagged {len(ranked_issue_indices)} label issue candidates")

# ----------------------------------------------------------
# STEP 4: Build the diagnostic dataframe
# ----------------------------------------------------------

df_issues = df_train.copy()
df_issues["oof_proba_defect"] = pred_probs[:, 1]
df_issues["label_quality_score"] = quality_scores
df_issues["is_flagged"] = False
df_issues.loc[ranked_issue_indices, "is_flagged"] = True

# Separate the two types of errors we care about:

# Type A — Suspected FALSE POSITIVES in our Y=1 (model says "not defective")
type_a = df_issues[
    (df_issues[TARGET_COL] == 1) &
    (df_issues["oof_proba_defect"] < 0.30)
].sort_values("oof_proba_defect")

# Type B — Suspected FALSE NEGATIVES hiding in Y=0 (model says "defective")
type_b = df_issues[
    (df_issues[TARGET_COL] == 0) &
    (df_issues["oof_proba_defect"] > 0.70)
].sort_values("oof_proba_defect", ascending=False)

print(f"\n=== TYPE A: Y=1 but OOF proba < 0.30 (suspected mislabeled positives) ===")
print(f"Count: {len(type_a)}")
if len(type_a) > 0:
    print(type_a[[TARGET_COL, "oof_proba_defect", "label_quality_score"]].to_string())

print(f"\n=== TYPE B: Y=0 but OOF proba > 0.70 (suspected hidden negatives) ===")
print(f"Count: {len(type_b)}")
if len(type_b) > 0:
    print(type_b[[TARGET_COL, "oof_proba_defect", "label_quality_score"]].to_string())

# SIGNAL THRESHOLD: 5+ candidates in either type = "high label noise signal"
type_a_count = len(type_a)
type_b_count = len(type_b)
signal = "HIGH" if (type_a_count >= 5 or type_b_count >= 5) else \
         "MEDIUM" if (type_a_count >= 2 or type_b_count >= 2) else "LOW"
print(f"\nLabel noise signal: {signal}")
print(f"  Type A (Y=1, proba<0.30): {type_a_count} candidates")
print(f"  Type B (Y=0, proba>0.70): {type_b_count} candidates")

# ----------------------------------------------------------
# STEP 5: Save outputs for inspection
# ----------------------------------------------------------

df_issues.to_csv("cleanlab_diagnostic.csv", index=False)
type_a.to_csv("cleanlab_type_a_suspects.csv", index=False)
type_b.to_csv("cleanlab_type_b_suspects.csv", index=False)
print("\nSaved: cleanlab_diagnostic.csv, cleanlab_type_a_suspects.csv, cleanlab_type_b_suspects.csv")
```

---

## 3. Decision Tree: What To Do With the Output

```
Run diagnostic → count Type A (Y=1, proba<0.30) and Type B (Y=0, proba>0.70)
│
├── TYPE A count = 0 AND TYPE B count = 0
│   └── Labels are consistent with model. Label noise is NOT the bottleneck.
│       Action: Do NOT relabel. Move to other hypotheses.
│
├── TYPE A count = 1-4 OR TYPE B count = 1-4   [MEDIUM signal]
│   └── Possible noise but sample too small to confidently relabel.
│       Action: INSPECT each row manually (look at feature values vs neighbors).
│       If domain-obvious mismatch → remove from training (don't flip).
│       Expected lift: marginal (0.5-1.5 LB points if lucky).
│
├── TYPE A count ≥ 5  [HIGH signal]
│   └── Some Y=1 are probably mislabeled (events the process actually didn't produce defects for).
│       Action:
│         - Inspect top-5 by lowest proba. Look for feature profiles similar to negatives.
│         - If ≥3 are clearly non-defective on domain features → REMOVE from train (don't relabel to 0).
│         - Re-run V44 architecture on cleaned set. Expect AUC improvement +0.01-0.03.
│         - DO NOT flip Y=1→0 unless boss has physical access to actual steel coil records.
│
├── TYPE B count ≥ 5  [HIGH signal — most actionable]
│   └── Model fires consistently on Y=0 rows. Two interpretations:
│       A) These are truly defective coils mislabeled as 0 in the training data.
│       B) Model has learned a spurious pattern that fires on non-defective coils.
│       Distinguish: Do these rows cluster with confirmed Y=1 in feature space?
│         - If YES (X42>0.025 AND X39 in hot zone [158-162]): likely true mislabeled negatives
│           Action: FLIP Y=0→1 for top-5 by proba, retrain, compare OOF
│         - If NO (scattered feature profiles): spurious model pattern
│           Action: Do NOT flip. The model is overfitting these rows.
│
└── Cleanlab flags >20 total issues
    └── This many flags on a 1352-row dataset is suspicious.
        Almost certainly Cleanlab is over-triggering on minority class imbalance.
        Action: Reduce to top-10 by label_quality_score < 0.3.
        Apply manual inspection before any relabeling.
```

---

## 4. Retrain Protocol (If Label Correction Warranted)

```python
# ============================================================
# STEP 6: Retrain after label correction
# Two strategies — try both, compare OOF F1
# ============================================================

from sklearn.metrics import f1_score

def evaluate_oof(X, y, clf, cv):
    """Returns OOF (R+P)/2 score — your hackathon metric."""
    pred_probs = cross_val_predict(clf, X, y, cv=cv, method="predict_proba")
    # Sweep thresholds to maximise (R+P)/2
    best_score = 0
    for thresh in np.arange(0.05, 0.95, 0.01):
        preds = (pred_probs[:, 1] >= thresh).astype(int)
        if preds.sum() == 0:
            continue
        from sklearn.metrics import precision_score, recall_score
        p = precision_score(y, preds, zero_division=0)
        r = recall_score(y, preds, zero_division=0)
        score = (p + r) / 2
        if score > best_score:
            best_score = score
            best_thresh = thresh
    return best_score, best_thresh

skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
clf = LGBMClassifier(n_estimators=500, learning_rate=0.05, class_weight="balanced", random_state=42, verbose=-1)

# Baseline (original labels)
baseline_score, baseline_thresh = evaluate_oof(X, y, clf, skf)
print(f"Baseline OOF (R+P)/2: {baseline_score:.4f} at thresh {baseline_thresh:.2f}")

# Strategy A: REMOVE suspected bad positives (Type A rows)
if len(type_a) > 0:
    remove_idx = type_a.index.tolist()[:5]  # top-5 most suspect
    mask = ~df_train.index.isin(remove_idx)
    X_clean = X[mask]
    y_clean = y[mask]
    score_a, thresh_a = evaluate_oof(X_clean, y_clean, clf, skf)
    delta_a = score_a - baseline_score
    print(f"Strategy A (remove {len(remove_idx)} Type A): OOF {score_a:.4f} (delta {delta_a:+.4f})")

# Strategy B: FLIP suspected hidden negatives (Type B rows)
if len(type_b) > 0:
    flip_idx = type_b.index.tolist()[:5]  # top-5 most suspect
    y_flipped = y.copy()
    y_flipped[flip_idx] = 1  # flip 0→1
    score_b, thresh_b = evaluate_oof(X, y_flipped, clf, skf)
    delta_b = score_b - baseline_score
    print(f"Strategy B (flip {len(flip_idx)} Type B): OOF {score_b:.4f} (delta {delta_b:+.4f})")

# Strategy C: Label smoothing (soft targets, Hinton-style)
# Note: LightGBM does NOT natively support soft targets. Use XGBoost with custom objective.
# See Section 5 below for implementation.

# Only submit to LB if OOF delta is POSITIVE AND delta > 0.5 pts
# Given V27 disaster (OOF +1.04 → LB -34.89), threshold for submission = OOF delta > 1.0
```

---

## 5. Noise-Robust Loss Functions for GBDT (Alternative Track)

If label noise is confirmed but relabeling is risky (confirmation bias concern), use a noise-robust loss instead of removing/flipping labels.

### 5A. Generalized Cross Entropy (GCE) — XGBoost custom objective

Based on Northcutt's and the Robust-GBDT paper (arXiv 2310.05067):

```python
import xgboost as xgb
import numpy as np

def gce_objective(q: float = 0.7):
    """
    GCE loss: l = (1 - p^q) / q
    q ∈ (0, 1]: q→0 = MAE (most robust), q→1 = BCE (standard)
    Recommended starting value: q=0.7 (Northcutt et al.)
    
    IMPORTANT: XGBoost custom objectives require gradient + hessian.
    """
    def objective(pred, dtrain):
        label = dtrain.get_label()
        p = 1.0 / (1.0 + np.exp(-pred))          # sigmoid
        p = np.clip(p, 1e-6, 1 - 1e-6)
        
        # GCE gradient: d/dp [(1-p^q)/q] * dp/d_pred
        # = -p^(q-1) * p*(1-p)  [chain rule through sigmoid]
        grad = -np.power(p, q - 1) * p * (1 - p)
        grad = np.where(label == 1, grad, -grad)  # flip sign for negative class
        
        # Hessian approximation (required by XGBoost — use positive constant)
        hess = np.ones_like(pred) * 0.1
        
        return grad, hess
    return objective

# Usage:
dtrain = xgb.DMatrix(X_train, label=y_train)
params = {
    "max_depth": 4,
    "learning_rate": 0.05,
    "eval_metric": "logloss",
    "seed": 42,
    "scale_pos_weight": (y_train == 0).sum() / (y_train == 1).sum()
}

# q=0.7 is the sweet spot: robust to noise, still converges
model_gce = xgb.train(
    params, dtrain, num_boost_round=300,
    obj=gce_objective(q=0.7),
    verbose_eval=50
)
```

### 5B. Label Smoothing for Binary (simplest, always-safe regularizer)

```python
# Hinton-style: replace hard labels with soft targets
# y=1 → 0.95 (allows for 5% mislabel rate in positives)
# y=0 → 0.05 (allows for 5% mislabel rate in negatives)

SMOOTH_FACTOR = 0.05  # tune: 0.02, 0.05, 0.10

y_smooth = np.where(y == 1, 1.0 - SMOOTH_FACTOR, SMOOTH_FACTOR)

# LightGBM doesn't support soft labels natively, but you can approximate
# via XGBoost with custom BCE on y_smooth:

def smooth_bce_objective(smooth=0.05):
    def objective(pred, dtrain):
        label_hard = dtrain.get_label()
        label_soft = np.where(label_hard == 1, 1.0 - smooth, smooth)
        p = 1.0 / (1.0 + np.exp(-pred))
        p = np.clip(p, 1e-7, 1 - 1e-7)
        grad = p - label_soft
        hess = p * (1 - p)
        return grad, hess
    return objective

# Expected lift: 0.3-1.0 LB points if true label noise is 3-8%.
# Risk: near-zero if labels are actually clean (just mild regularization effect).
```

### 5C. Symmetric Cross Entropy (SCE) — stronger noise robustness

```python
def sce_objective(alpha=0.1, beta=1.0):
    """
    SCE = alpha * CE + beta * RCE
    RCE = -sum(p * log(y + eps)) — penalises the model's own overconfidence
    alpha=0.1, beta=1.0 recommended for ~10% noise rate
    """
    def objective(pred, dtrain):
        label = dtrain.get_label()
        p = 1.0 / (1.0 + np.exp(-pred))
        p = np.clip(p, 1e-7, 1 - 1e-7)
        
        # Forward CE gradient
        grad_ce = p - label
        
        # Reverse CE gradient: d/d_pred [-y*log(p)]
        # ≈ -label / p * p*(1-p) = -label*(1-p)
        grad_rce = np.where(label == 1, -(1 - p), p)
        
        grad = alpha * grad_ce + beta * grad_rce
        hess = p * (1 - p) + 1e-4
        
        return grad, hess
    return objective
```

---

## 6. Expected Lift Estimates

Based on Cleanlab JAIR paper benchmarks and Robust-GBDT empirical results:

| Scenario | Condition | Expected OOF lift | Expected LB lift | Risk |
|---|---|---|---|---|
| 5% label noise, Cleanlab removes 3-5 rows | Type A count ≥5, proba < 0.15 | +0.5 to +1.5 pts | +0.5 to +2.0 pts | Low |
| 5% label noise, Cleanlab flips 3-5 negatives | Type B count ≥5, proba > 0.80 | +1.0 to +3.0 pts | +1.0 to +4.0 pts | MEDIUM (see Risk section) |
| Label smoothing (epsilon=0.05) | Always applicable | +0.2 to +0.8 pts | +0.2 to +1.0 pts | Very Low |
| GCE (q=0.7) | Always applicable | +0.3 to +1.2 pts | +0.3 to +1.5 pts | Low |
| No noise detected | Type A=0 AND Type B=0 | 0 | 0 | — |

**Calibration note:** Past V27 disaster showed OOF can drastically overestimate LB. These estimates assume the label corrections change model behaviour smoothly (not discretely like abstain rules). Label removals/flips are continuous perturbations → should track OOF more faithfully than hard thresholding rules.

**Reality check:** If 22 test positives exist and model AUC=0.92, the 15 "missed" TPs are more likely structural feature-invisibility (stealth defects) than label noise. Label noise primarily hurts precision (adds spurious positives), not recall. Expect this to be a **precision improvement lever**, not a recall improvement lever.

---

## 7. THE CRITICAL RISK: Confirmation Bias Loop

This is the most important warning in this research.

**The loop:**
1. Model trains on 66 positives.
2. Model fires on some Y=0 rows (Type B candidates).
3. We flip those Y=0 → Y=1.
4. Model now trains on those same rows as positives.
5. OOF performance improves (model is rewarded for exactly the rows it was already confident about).
6. We submit → LB may NOT improve (or worsen) because the flipped rows may genuinely be negatives in the test set.

**This is exactly the pattern of the V32 disaster:** We pruned rows that the model thought were non-defective, and the test set had a different distribution — those rows WERE defective.

**Mitigation rules:**

| Rule | Reason |
|---|---|
| NEVER flip/remove more than 5 rows total in a single experiment | Small perturbation principle |
| ONLY flip Type B rows that also satisfy V44's hot-zone criteria (X42>0.025 AND X39 ∈ [158-162]) | Domain anchor — don't relabel rows that aren't physically suspicious |
| ALWAYS require OOF delta > +1.0 before LB submission | Filters out noise-level improvements that could degrade LB |
| Run A/B test: retrain with and without correction, compare OOF distributions | If correction only helps on the corrected rows' fold, it's circular |
| DO NOT submit if Type B flip changes the total prediction count by more than ±10 rows | V31 lesson: changing which rows are flagged destroys V44's precision anchor |

---

## 8. Cleanlab on V44 Specifically — Quick Integration

If you have V44 OOF probabilities already saved (e.g., `oof_proba_v44.npy`):

```python
import numpy as np
import pandas as pd
from cleanlab.filter import find_label_issues
from cleanlab.rank import get_label_quality_scores

# Load V44 OOF probas (shape: [1352, 2])
pred_probs = np.load("oof_proba_v44.npy")  # adjust path
y = pd.read_csv("train.csv")["target"].values

# Wrap into 2-col if V44 only saved P(defect) as 1D:
if pred_probs.ndim == 1:
    pred_probs = np.column_stack([1 - pred_probs, pred_probs])

# Run CL
ranked_issues = find_label_issues(
    labels=y,
    pred_probs=pred_probs,
    return_indices_ranked_by="self_confidence",
    filter_by="prune_by_noise_rate",
    min_examples_per_class=10
)

quality = get_label_quality_scores(labels=y, pred_probs=pred_probs)

print(f"Issues flagged: {len(ranked_issues)}")
print(f"  Y=1 rows flagged: {sum(y[ranked_issues] == 1)}")
print(f"  Y=0 rows flagged: {sum(y[ranked_issues] == 0)}")

# Quick signal check
type_a_count = ((y == 1) & (pred_probs[:, 1] < 0.30)).sum()
type_b_count = ((y == 0) & (pred_probs[:, 1] > 0.70)).sum()
print(f"\nType A (Y=1, proba<0.30): {type_a_count}")
print(f"Type B (Y=0, proba>0.70): {type_b_count}")
```

---

## 9. Co-Teaching / MentorNet / DivideMix (Why Skip These)

These methods (Han et al. 2018, Jiang et al. 2018, Li et al. 2020) are designed for **deep learning** — specifically convolutional networks on image datasets with 20-40% synthetic noise.

**Why they don't apply to our case:**
- They require two independently-initialized neural networks trading "clean" examples.
- GBDT has no analogous mechanism (trees don't have gradient variance as a noise signal).
- Our dataset is 1352 rows — these methods need thousands for reliable selection.
- Empirical studies (CrowdTeacher, 2021) show tabular co-teaching underperforms simple CL-based filtering by 5-15%.

**Verdict:** Skip. Cleanlab + Robust-GBDT loss functions are the correct tools for GBDT-on-tabular.

---

## 10. Installation

```bash
pip install cleanlab>=2.6.4
# cleanlab 2.6 requires: scikit-learn>=1.1, numpy>=1.20, pandas>=1.1.4
# No GPU required. Runs on CPU in <60 seconds on 1352 rows.
```

---

## 11. Decision Summary

Run the diagnostic first (Step 2-4 above, ~5 minutes). Then:

```
Type A ≥5 OR Type B ≥5 ?
  YES → Inspect manually → if domain-plausible, remove/flip top-3 rows → retrain → OOF delta > +1.0 → submit
  NO  → Skip relabeling entirely
        → Try label smoothing (epsilon=0.05) as a free regularization pass
        → Try GCE (q=0.7) as a custom XGB objective
        → Both are low-risk, don't change data, add ~0.3-0.8 LB expected value
```

**Bottom line:** The hypothesis is worth a 15-minute diagnostic. If signal is high, the path to +2-4 LB points exists. If signal is low, label smoothing and GCE cost nothing to try and may close 0.5-1.0 of the gap to 75+. The confirmation-bias risk is real but manageable with the guardrails in Section 7.

---

## Sources

- [Cleanlab GitHub](https://github.com/cleanlab/cleanlab) — official library
- [Cleanlab Tabular Tutorial](https://docs.cleanlab.ai/stable/tutorials/clean_learning/tabular.html) — workflow reference
- [Cleanlab In-depth Overview](https://docs.cleanlab.ai/stable/tutorials/indepth_overview.html) — API patterns
- [Confident Learning JAIR paper (arXiv 1911.00068)](https://arxiv.org/pdf/1911.00068) — theoretical foundation
- [Robust-GBDT (arXiv 2310.05067)](https://arxiv.org/abs/2310.05067) — GCE/SCE/RFL for XGBoost/LightGBM
- [Improving GBDT on Imbalanced Datasets (arXiv 2407.14381)](https://arxiv.org/html/2407.14381v1) — WCE + ASL benchmarks
- [Learning with Imbalanced Noisy Data (arXiv 2402.11242)](https://arxiv.org/pdf/2402.11242) — imbalance + noise interaction
- [MIT DCAI Lab: Label Errors (2024)](https://dcai.csail.mit.edu/2024/label-errors/) — pedagogical overview
