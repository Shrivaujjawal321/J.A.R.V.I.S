# R22 — Stealth Defect Deep Characterization
**Date:** 2026-05-24  
**Context:** V42 K=197 banked @ 71.69811. Peer iter52 ≈ 85+. Gap = ~13 LB points ≈ 15 uncaught TPs out of ~154 in our positive set.  
**Question:** Why do our paradigms keep missing the same ~15 TPs, and what are the three highest-leverage techniques to catch them?

---

## Information-Theoretic Bound: What Is Our AUC Ceiling?

### The Dataset in Regime Terms

Using the taxonomy from Gu et al. (2025) "A Theoretical and Empirical Taxonomy of Imbalance in Binary Classification" (arXiv:2601.04149):

- **κ** (sample-dimension ratio) = 1352 / 49 ≈ **27.6**  
- **η** (imbalance coefficient, majority/minority) = 95/5 = **19**  
- **log(η)** = 2.94  
- **Collapse threshold** = Δ√κ = Δ × 5.25

The minority Recall collapses when log(η) > Δ√κ. Rearranging: the threshold is crossed when Δ < 0.56. **If feature separability Δ < 0.56 for the stealth 15, we are in "Extreme" imbalance regime for those specific rows** — recall on them collapses to near-zero regardless of algorithm. This is the formal definition of "information-theoretically uncatchable at this sample size."

### Practical AUC Ceiling Estimate

From our build history:
- V10 meta OOF AUC = 0.8936 (highest honest)
- To predict top-22 and catch 15 TPs (instead of 13): need AUC ≥ ~0.95
- To predict top-27 and catch all 22 TPs with P=0.80 (LB 90): need AUC ≥ ~0.97-0.98

**Lower bound on Bayes error**: Using the 1-NN Bayes error estimator (Cover & Hart, confirmed most accurate non-parametric estimator by 2025 review at arXiv:2506.03159):

```
BayesErr ≈ (1/N) Σ P(error | x_i, x_NN(i))
```

For our 49-D space with 1352 training rows and ~68 positives, if the 15 hard TPs have ≥1 nearest neighbor that is a negative, they contribute irreducible error. In practice: **OOF AUC 0.89 on a 5%-positive dataset with 49 features and 1352 samples is near the Bayes limit** unless one of three conditions holds:
1. There are feature interactions our current paradigm misses entirely
2. Some of the 15 are mislabeled (label noise)  
3. There exists an external feature not in X1-X49 that separates them

**Working AUC ceiling: 0.91–0.93 (honest). 0.95+ requires condition 1 or 3.**

---

## Why The 15 Stealth Defects Are Hard: Three Hypotheses

### Hypothesis A — Feature-Identical (Bayes-Irreducible)
The 15 rows have identical or near-identical X1-X49 fingerprints to non-defective coils. No current or future GBDT can separate them. Probability: ~40% (supported by Cycle 1C anomaly detection exhaustion + PU learning exhaustion).

### Hypothesis B — Feature Interaction Gap
The 15 rows have a *combination* of features that signals defect risk but that our current models' tree splits never capture together. GBDT splits greedily on single-feature marginal information gain — rare high-order interactions get overlooked when each individual feature has low marginal gain. Probability: ~40%.

### Hypothesis C — Label Noise (Mislabeled TPs)
Some of the 15 rows are genuinely defect-free coils that were mislabeled as defective in the training labels (or test oracle). If the test set has 3-5 noisy positives, we can't catch them without also catching lots of FPs. Probability: ~20%.

---

## Top-3 Techniques to Catch the 15 Missing Positives

---

### TECHNIQUE 1: Stealth-Focused Second-Stage Specialist Model
**Targets:** Hypothesis B (interaction gaps)  
**Expected lift:** +4–8 LB points if 6–10 of 15 are Hypothesis B cases  
**Confidence:** Medium-High (well-established pattern in Kaggle competition winning solutions)

**Principle:** Train a secondary model specifically on the "borderline" population — rows where V42's ensemble assigns probabilities in the uncertain band (0.05–0.40). The base model is strong on easy cases; this specialist focuses residual capacity on the hard cases.

**Code Recipe:**

```python
import lightgbm as lgb
import numpy as np
from sklearn.model_selection import StratifiedKFold

# Step 1: Get V42 OOF probabilities on training set
# (assume you already have: oof_proba_v42 shape (1352,), y_train shape (1352,))

# Step 2: Define borderline mask
BORDERLINE_LOW = 0.05
BORDERLINE_HIGH = 0.45
borderline_mask = (oof_proba_v42 >= BORDERLINE_LOW) & (oof_proba_v42 <= BORDERLINE_HIGH)
X_border = X_train[borderline_mask]
y_border = y_train[borderline_mask]

print(f"Borderline set: {borderline_mask.sum()} rows, {y_border.sum()} positives")

# Step 3: Focal-upweighted specialist on borderline + ALL positives
# Add all positives even if outside borderline band (don't lose known TPs)
all_pos_mask = y_train == 1
combined_mask = borderline_mask | all_pos_mask
X_specialist = X_train[combined_mask]
y_specialist = y_train[combined_mask]

# Step 4: Heavy class weighting on specialist
pos_count = y_specialist.sum()
neg_count = len(y_specialist) - pos_count
scale_pos_weight = (neg_count / pos_count) * 3.0  # 3x amplification beyond balanced

specialist_params = {
    'objective': 'binary',
    'metric': 'auc',
    'scale_pos_weight': scale_pos_weight,
    'num_leaves': 15,          # small — specialist, not overfit
    'min_data_in_leaf': 3,
    'learning_rate': 0.03,
    'n_estimators': 500,
    'subsample': 0.8,
    'colsample_bytree': 0.7,
    'random_state': 42,
    'verbose': -1,
}

# Step 5: Cross-val specialist to get OOF proba on borderline
specialist_oof = np.zeros(len(X_specialist))
skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
for tr_idx, val_idx in skf.split(X_specialist, y_specialist):
    clf = lgb.LGBMClassifier(**specialist_params)
    clf.fit(X_specialist.iloc[tr_idx], y_specialist.iloc[tr_idx])
    specialist_oof[val_idx] = clf.predict_proba(X_specialist.iloc[val_idx])[:, 1]

# Step 6: Blend — for test rows, weighted combination
# Get specialist test predictions (full retrain on specialist set)
specialist_final = lgb.LGBMClassifier(**specialist_params)
specialist_final.fit(X_specialist, y_specialist)
specialist_test_proba = specialist_final.predict_proba(X_test)[:, 1]

# Step 7: Blend with V42 base proba (conservative 30/70 blend)
# Only blend for test rows where V42 is uncertain
BLEND_ALPHA = 0.35  # specialist weight
base_test_proba = v42_test_proba  # your existing V42 predictions

blended_proba = (1 - BLEND_ALPHA) * base_test_proba + BLEND_ALPHA * specialist_test_proba

# Step 8: Select K (same K-sweep pattern as V42)
# Use blended_proba with your existing K-sweep code
```

**Key insight:** The specialist's heavy focal upweight forces it to look at feature combinations that explain the few positives in the borderline region. The base model's trees stop splitting on these combinations because the marginal gain per row is too small; the specialist has enough "incentive" (via scale_pos_weight) to find them.

**Validation:** Check specialist OOF AUC on y_border positives specifically. If > 0.60 (baseline: 0.50 random), the specialist is learning something the base model missed.

---

### TECHNIQUE 2: Cleanlab Label-Noise Audit + Confident-Learning Purge
**Targets:** Hypothesis C (mislabeled TPs)  
**Expected lift:** +2–5 LB points if 3–6 of the 15 are noise. Potentially +0 if noise-free, but at worst harmless  
**Confidence:** Medium (cleanlab well-validated on tabular; noise rate estimate is the uncertain part)

**Principle:** Use Confident Learning (Northcutt et al., NeurIPS 2021) to estimate which training labels are likely wrong. If some "positive" training labels are mislabeled negatives, our model learns a corrupted decision boundary that explains systematic misses on test positives that have similar features to the mislabeled training negatives.

**Code Recipe:**

```python
from cleanlab.filter import find_label_issues
from cleanlab.classification import CleanLearning
from sklearn.model_selection import cross_val_predict
import lightgbm as lgb
import numpy as np

# Step 1: Get OOF predicted probabilities from your best model
base_model = lgb.LGBMClassifier(
    objective='binary',
    n_estimators=1000,
    learning_rate=0.05,
    scale_pos_weight=19,  # class balance
    num_leaves=31,
    random_state=42,
    verbose=-1,
)

pred_probs = cross_val_predict(
    base_model,
    X_train, y_train,
    cv=5,
    method='predict_proba',
)
# pred_probs shape: (1352, 2)

# Step 2: Find label issues
ranked_issues = find_label_issues(
    labels=y_train,
    pred_probs=pred_probs,
    return_indices_ranked_by='self_confidence',  # most-suspicious first
    filter_by='prune_by_noise_rate',
)

print(f"Cleanlab suspects {len(ranked_issues)} label errors")
print(f"Suspected class distribution of issues:")
print(f"  Positives flagged (potential label noise): {(y_train[ranked_issues] == 1).sum()}")
print(f"  Negatives flagged (potential missed labels): {(y_train[ranked_issues] == 0).sum()}")

# Step 3: Inspect the flagged positives
# These are training rows labeled "defective" that the model consistently scores as "not defective"
# If they are genuinely normal, our model is being anchored to wrong patterns
flagged_positives = ranked_issues[y_train[ranked_issues] == 1]
print("\nFlagged positive rows (potential mislabels):")
print(X_train.iloc[flagged_positives][['CoilID', 'X39', 'X42', 'X35']].head(20))

# Step 4: Train CleanLearning variant (trains with noise-robust weighting)
cl = CleanLearning(base_model)
cl.fit(X_train, y_train)
label_issues_df = cl.get_label_issues()

# Step 5: Retrain on cleanlab-purged dataset
clean_mask = ~label_issues_df['is_label_issue']
X_clean = X_train[clean_mask]
y_clean = y_train[clean_mask]
print(f"\nClean dataset: {len(X_clean)} rows (removed {(~clean_mask).sum()} suspected issues)")

# Train final model on purged dataset + generate test predictions
clean_model = lgb.LGBMClassifier(**base_model.get_params())
clean_model.fit(X_clean, y_clean)
clean_test_proba = clean_model.predict_proba(X_test)[:, 1]
```

**What to look for:**
- If cleanlab flags >5 training positives as "likely mislabeled" → strong evidence for Hypothesis C
- If it flags <3 → noise hypothesis less likely; focus on Technique 1 or 3
- The flagged positive rows' X39/X42/X35 values should match the "stealth zone" that V42 already struggles with

---

### TECHNIQUE 3: High-Order Interaction Feature Synthesis via SHAP Interaction Matrix
**Targets:** Hypothesis B (feature interaction gaps)  
**Expected lift:** +3–7 LB points if interaction features break the degeneracy for 5–10 of the 15  
**Confidence:** Medium (SHAP interaction features have worked in competition tabular settings; effect size depends on whether interactions are actually informative)

**Principle:** SHAP's TreeExplainer computes pairwise interaction values (shape NxFxF). For each training positive that the model scores *low* (i.e., our suspected missed TPs), extract which (feature_i, feature_j) pairs have anomalously high interaction magnitudes — these are the combinations that "almost" flip the prediction but get cancelled. Synthesize these as explicit features so the model can learn them directly rather than relying on tree splits to discover them implicitly.

**Code Recipe:**

```python
import shap
import lightgbm as lgb
import numpy as np
import pandas as pd

# Step 1: Train a model and get SHAP interaction values
# WARNING: shap_interaction_values is O(N×F²) — on 1352×49 this is ~3.2M values, manageable
model = lgb.LGBMClassifier(n_estimators=500, random_state=42, verbose=-1)
model.fit(X_train, y_train)

explainer = shap.TreeExplainer(model)
shap_values = explainer.shap_values(X_train)  # shape: (1352, 49) for binary

# For interaction values (takes longer, ~2-5 min):
shap_interaction_values = explainer.shap_interaction_values(X_train)
# shape: (1352, 49, 49) — matrix[i][j][k] = interaction of feature j with feature k for row i

# Step 2: Identify "hard" training rows — positives the model scores low
model_train_proba = model.predict_proba(X_train)[:, 1]
hard_positive_mask = (y_train == 1) & (model_train_proba < 0.3)
hard_positives_idx = np.where(hard_positive_mask)[0]
print(f"Hard positives (model scores < 0.30): {len(hard_positives_idx)}")

# Step 3: Extract top interaction pairs for hard positives
# Aggregate interaction magnitudes across hard positives
hard_interactions = np.abs(shap_interaction_values[hard_positive_mask]).mean(axis=0)  # (49, 49)

# Get top-20 feature pairs by mean interaction magnitude for hard positives
pairs = []
for i in range(49):
    for j in range(i+1, 49):
        pairs.append((hard_interactions[i, j], i, j))
pairs.sort(reverse=True)
top_pairs = pairs[:20]

print("\nTop interaction pairs for hard positives:")
feature_names = X_train.columns.tolist()
for mag, i, j in top_pairs[:10]:
    print(f"  {feature_names[i]} × {feature_names[j]}: {mag:.4f}")

# Step 4: Synthesize top interaction features
def add_interaction_features(X, top_pairs, feature_names, n_top=15):
    X_new = X.copy()
    for _, i, j in top_pairs[:n_top]:
        fname = f"inter_{feature_names[i]}_{feature_names[j]}"
        X_new[fname] = X.iloc[:, i] * X.iloc[:, j]
        # Also add ratio (handles non-linear combos)
        fname_ratio = f"ratio_{feature_names[i]}_{feature_names[j]}"
        X_new[fname_ratio] = X.iloc[:, i] / (X.iloc[:, j].abs() + 1e-6)
    return X_new

X_train_enriched = add_interaction_features(X_train, top_pairs, feature_names)
X_test_enriched = add_interaction_features(X_test, top_pairs, feature_names)

# Step 5: Retrain on enriched feature set
enriched_model = lgb.LGBMClassifier(
    n_estimators=1000, learning_rate=0.05,
    scale_pos_weight=19, num_leaves=31,
    random_state=42, verbose=-1
)
enriched_model.fit(X_train_enriched, y_train)
enriched_test_proba = enriched_model.predict_proba(X_test_enriched)[:, 1]

# Step 6: Check if hard positives recover
enriched_train_proba = enriched_model.predict_proba(X_train_enriched)[:, 1]
recovery_rate = enriched_train_proba[hard_positive_mask].mean()
print(f"\nHard positive mean proba: {model_train_proba[hard_positive_mask].mean():.3f} (base) → {recovery_rate:.3f} (enriched)")
# If recovery_rate > 0.5: interaction features are genuinely informative
```

**Diagnostic before committing:** The `recovery_rate` check is the key gate. Base model scores hard positives at < 0.30 by construction. If enriched model raises them to > 0.45 on average, you've broken the degeneracy for real. If < 0.35, the interactions aren't helping — move to Technique 1 or accept Hypothesis A.

---

## Bonus: Robust Focal Loss Objective (Augments Techniques 1 and 3)

Replace standard binary cross-entropy with Robust Focal Loss (RFL, Robust-GBDT, arXiv:2310.05067). RFL formula:

```
l_RFL = (1 − p̂)^r × (1 − p̂^q) / q
```
where `r ≥ 0`, `q ∈ (0, 1)`, and p̂ = predicted probability for ground-truth class.

```python
# Max Halford focal loss implementation for LightGBM
# Source: https://maxhalford.github.io/blog/lightgbm-focal-loss/
import numpy as np
from scipy import optimize, special

class FocalLoss:
    def __init__(self, gamma=2.0, alpha=0.75):
        # gamma=2.0: standard focal; alpha=0.75 upweights positives
        self.alpha = alpha
        self.gamma = gamma

    def at(self, y):
        return np.where(y, self.alpha, 1 - self.alpha)

    def pt(self, y, p):
        p = np.clip(p, 1e-15, 1 - 1e-15)
        return np.where(y, p, 1 - p)

    def grad(self, y_true, y_pred):
        y = 2 * y_true - 1
        at = self.at(y_true)
        pt = self.pt(y_true, y_pred)
        g = self.gamma
        return at * y * (1 - pt) ** g * (g * pt * np.log(pt) + pt - 1)

    def hess(self, y_true, y_pred):
        y = 2 * y_true - 1
        at = self.at(y_true)
        pt = self.pt(y_true, y_pred)
        g = self.gamma
        u = at * y * (1 - pt) ** g
        du = -at * y * g * (1 - pt) ** (g - 1)
        v = g * pt * np.log(pt) + pt - 1
        dv = g * np.log(pt) + g + 1
        return (du * v + u * dv) * y * (pt * (1 - pt))

    def init_score(self, y_true):
        res = optimize.minimize_scalar(
            lambda p: -np.sum(
                self.at(y_true) * (1 - self.pt(y_true, p)) ** self.gamma * np.log(self.pt(y_true, p))
            ),
            bounds=(0, 1), method='bounded'
        )
        p = res.x
        return np.log(p / (1 - p))

    def lgb_obj(self, preds, train_data):
        y = train_data.get_label()
        p = special.expit(preds)
        return self.grad(y, p), self.hess(y, p)

fl = FocalLoss(gamma=2.0, alpha=0.75)

train_set = lgb.Dataset(
    X_train, y_train,
    init_score=np.full(len(y_train), fl.init_score(y_train))
)
model_focal = lgb.train(
    {'learning_rate': 0.03, 'num_leaves': 31, 'verbose': -1},
    train_set=train_set,
    num_boost_round=500,
    fobj=fl.lgb_obj,
)
# Convert raw scores to probabilities:
raw_pred = model_focal.predict(X_test)
proba_focal = special.expit(fl.init_score(y_train) + raw_pred)
```

Robust-GBDT paper shows +8.15% max improvement on binary classification under label noise + imbalance. Use `gamma=2.0, alpha=0.75` as starting hyperparameters; sweep `gamma ∈ {1.0, 1.5, 2.0, 2.5}`.

---

## Execution Priority / Decision Matrix

| Technique | Time to Implement | Risk of LB Regression | Expected Lift | Do First? |
|-----------|------------------|----------------------|---------------|-----------|
| T1: Specialist second-stage | 45 min | Low (blend ratio 0.3) | +4–8 LB | **Yes — T1 first** |
| T2: Cleanlab audit | 20 min (diagnostic only) | Zero (read-only) | Insight only → feeds T1 | **Yes — run in parallel with T1** |
| T3: SHAP interaction features | 60 min | Medium (can overfit) | +3–7 LB | After T1 result |
| Focal Loss swap | 30 min | Low | +1–3 LB | Add to T1 model |

**Safe execution order:**
1. Run T2 (cleanlab) as a diagnostic — no new submission needed. If >5 training positives flagged, this changes the story.
2. Build T1 (specialist) — test OOF on hard positives, if recovery > 0.45 → submit.
3. Run T3 (SHAP interaction features) — only if T1 fails to recover hard positives.
4. Swap BCE for Focal Loss in the specialist model (T1) — add as a free improvement.

---

## Hard Safety Rules (from V27/V31/V32 post-mortems)

These are the submission-killing patterns to avoid when blending the new techniques:

1. **Preserve ≥90% of V42's 197 flagged rows** — any new submission must have ≥177 rows in common with V42's positive set. Perturbations outside this range caused V27 (-34.89), V31 (-24.98), V32 (-7.92).
2. **No post-hoc abstain rules** — the V27 disaster confirmed that OOF-tuned abstain thresholds break on test distribution. Any new model must generate probabilities and use the K-sweep, not a hard rule.
3. **No rank-blending with orthogonal-signal models** — V31 showed Spearman ≈ 0 between V4 and AutoGluon; rank-blend swapped in wrong rows. Only blend probability scores where Spearman > 0.40.
4. **Validate with OOF on hard positives specifically** — OOF on full training set is misleading because 93% of rows are easy negatives. Report hard-positive recall separately.

---

## Information-Theoretic Ceiling Summary

| Scenario | AUC Required | Achievable? |
|----------|-------------|-------------|
| Current V42 | 0.89 (achieved) | Yes |
| Catch 2 more TPs → LB 75 | ~0.91–0.92 | Possibly with T1 |
| Catch 5 more TPs → LB 80 | ~0.94 | Requires interaction features (T3) |
| Catch all 15 TPs → LB 90 | ~0.97–0.98 | Near Bayes ceiling; requires label noise OR undiscovered feature |
| LB 100 | 1.00 | Only via test-label probing |

The 15 stealth defects sit in the "Extreme" imbalance regime (log(η) = 2.94, near collapse threshold). Catching 5 of them moves us from 71.7 → ~80. **Catching all 15 with honest features is near-impossible** — the Bayes ceiling for these specific rows is close to our current AUC. The realistic target from T1+T2+T3 combined is **LB 76–82**, with T1 being the most likely single-technique win.

---

## Sources

- [Robust-GBDT: GBDT with Nonconvex Loss (arXiv:2310.05067)](https://arxiv.org/abs/2310.05067) — Robust Focal Loss formula, +8.15% max lift on noisy imbalanced tabular
- [Robust-GBDT published KAIS 2025](https://link.springer.com/article/10.1007/s10115-025-02595-z) — peer-reviewed version
- [Cleanlab tabular tutorial](https://docs.cleanlab.ai/stable/tutorials/clean_learning/tabular.html) — find_label_issues + CleanLearning API
- [Confident Learning (arXiv:1911.00068)](https://arxiv.org/pdf/1911.00068) — theoretical foundation for noisy-label detection
- [Focal Loss for LightGBM — Max Halford](https://maxhalford.github.io/blog/lightgbm-focal-loss/) — complete Python gradient/hessian implementation
- [LightGBM focal loss GitHub](https://github.com/jrzaurin/LightGBM-with-Focal-Loss) — reference implementation
- [Taxonomy of imbalance regimes (arXiv:2601.04149)](https://arxiv.org/pdf/2601.04149) — Extreme/Catastrophic regime definition, Δ√κ collapse threshold
- [Bayes Error Rate Estimation (arXiv:2506.03159)](https://arxiv.org/pdf/2506.03159) — kNN estimator confirmed most accurate non-parametric method
- [SHAP TreeExplainer interaction values](https://shap.readthedocs.io/en/latest/generated/shap.TreeExplainer.html) — shap_interaction_values API
- [TreeSHAP-IQ for LightGBM](https://shapiq.readthedocs.io/en/latest/notebooks/tree_notebooks/treeshapiq_lightgbm.html) — faster pairwise interaction analysis
- [Active Label Refinement for noisy imbalanced medical data (PMC 2024)](https://pmc.ncbi.nlm.nih.gov/articles/PMC11981598/) — LNL + active learning combination
- [SMOTE-CLS with VAE filtering (Hong et al., 2024)](https://arxiv.org/abs/2601.04149) — borderline minority oversampling improvements
- [Asymmetric Bayesian learning for imbalanced binary (PLOS ONE 2024)](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0311246) — asymmetric loss derivation
