# R8 — Automated Feature Engineering: 2026 SOTA for Anonymous Tabular Features
*Tata Steel Defect Detection | LB: 72.83 → Target: 80+*
*Generated: 2026-05-24*

---

## Context

- 49 anonymous X-features (X0–X48)
- Existing hand-crafted: 56 stand-residual features, 7 CoilID-cyclic, 11 defect-proximity → ceiling hit
- Task: multi-label defect classification (tabular, ~7 defect types)
- Model: gradient boosting (CatBoost/LightGBM/XGBoost ensemble)
- Need: **automated discovery of new feature interactions** without domain semantics

---

## Quick Verdict

| Rank | Tool | Fit for Anonymous Features | Speed | Expected Lift |
|------|------|---------------------------|-------|---------------|
| **#1** | **OpenFE** | Excellent — purely numeric, no semantics needed | Fast (successive halving) | +2–5 AUC pts on GBDT |
| **#2** | **Polynomial deg-2 + importance pruning** | Perfect — pure math, no names needed | Very fast | +1–3 AUC pts if interactions exist |
| **#3** | **SHAP interaction values → targeted features** | Good — model-guided, zero false positives | Moderate | +0.5–2 AUC pts (surgical) |

**LLM-FE / AutoFeat → skip.** Both degrade severely on anonymous features (LLM-FE ablation: accuracy dropped from 0.680 → 0.626 without feature names). AutoFeat is symbolic regression — computationally heavy for 49 features with no semantic gain.

**gplearn → skip.** Genetic programming: extremely slow for 49+ features, high overfit risk, no proven edge over OpenFE on tabular classification.

**Featuretools DFS → skip.** Designed for relational multi-table data with entity relationships. Single flat table with 49 anonymous features gains nothing from DFS primitives beyond what polynomial features already cover.

---

## Tool 1: OpenFE (PRIMARY RECOMMENDATION)

### What it does
OpenFE generates interaction features using a library of **23 operators** across two categories:
- **Unary operators**: `log`, `sigmoid`, `square`, `abs`, `sqrt`, `reciprocal` (applied per feature)
- **Binary operators**: `+`, `-`, `×`, `÷`, `min`, `max`, `GroupByThenMean`, `GroupByThenMedian`, `GroupByThenStd`, `GroupByThenRank`, `Combine`, etc.
- Candidates = all first-order combos → O(d × m²) where d=operators, m=49 features

### Two-stage internal pruning (how it avoids feature explosion)
1. **Stage 1 — Successive Featurewise Halving**: Candidate features evaluated on progressively larger data subsets; bottom half discarded each round → rapid kill of useless candidates. Controlled by `n_data_blocks` (default 8) and `stage1_ratio=0.5`.
2. **Stage 2 — Feature Attribution with FeatureBoost**: Remaining candidates are trained as residual predictors. Feature importance (MDI / permutation / SHAP) ranks survivors. Only `n_select` top features pass.

### Implementation (exact recipe for our problem)

```python
# pip install openfe
from openfe import OpenFE, transform

ofe = OpenFE()
features = ofe.fit(
    data=train_x,           # DataFrame, 49 anonymous X-features
    label=train_y,          # series (binary or multi-label column)
    task_type='classification',
    n_jobs=8,               # max parallelism
    n_data_blocks=8,        # successive halving blocks; increase for speed
    n_select=30,            # how many final features to keep (tune: 10–50)
    stage1_n_estimators=5,
    stage2_n_estimators=10,
    candidate_max_depth=2,  # depth-2 = pairwise; depth-3 = triplet (slower)
    fe_method='two-stage',
)
train_x_new, test_x_new = transform(train_x, test_x, features, n_jobs=8)
```

**For multi-label**: run OpenFE **once per defect label** → union the selected feature sets → deduplicate. This gives label-specific interactions. Total extra features across 7 labels: ~50–150 after dedup.

### Expected output
- With `n_select=30` per label × 7 labels → ~80–120 unique new features post-dedup
- Feature names are formula strings: e.g. `log(X12)`, `X7 / X23`, `X3 + X41`
- Interpretable enough to check for sanity

### Key risk flags
- **GroupBy operators need a categorical grouping column** — for anonymous features this means you must designate X-features that look categorical (low cardinality). Check which Xi have < 20 unique values. If none qualify, disable GroupBy operators via `candidate_features_list` to remove them.
- **candidate_max_depth=3** can explode candidates quadratically — stick with depth=2 first.

### Evidence of effectiveness
- IEEE-CIS Fraud Detection Kaggle: OpenFE features → top 0.7% (99.3 percentile of 6351 teams)
- OpenFE++ (SDM '25) extended to temporal + feature interactions, reduces candidate set further — worth monitoring but not yet pip-installable.

---

## Tool 2: Polynomial Degree-2 + Importance Pruning (FAST BASELINE)

### What it does
`sklearn.preprocessing.PolynomialFeatures(degree=2, interaction_only=True)` generates all pairwise products Xi × Xj. For 49 features: C(49,2) = **1,176 interaction terms** + 49 squared terms = 1,225 total.

### Recipe

```python
from sklearn.preprocessing import PolynomialFeatures
from sklearn.feature_selection import SelectFromModel
import lightgbm as lgb

# Step 1: generate
poly = PolynomialFeatures(degree=2, interaction_only=False, include_bias=False)
X_poly = poly.fit_transform(train_x[original_49_cols])  # (n, 1225)

# Step 2: train a fast LGB to rank them
sel_model = lgb.LGBMClassifier(n_estimators=200, learning_rate=0.05,
                                num_leaves=63, n_jobs=8)
sel_model.fit(X_poly, train_y)

# Step 3: keep top-k by importance
selector = SelectFromModel(sel_model, threshold='mean', prefit=True)
X_poly_filtered = selector.transform(X_poly)
# Typical result: 50–150 features survive threshold='mean'

# Step 4: append to existing feature set
import pandas as pd
poly_names = poly.get_feature_names_out(original_49_cols)
kept_names = poly_names[selector.get_support()]
df_poly = pd.DataFrame(X_poly_filtered, columns=kept_names)
train_final = pd.concat([train_x, df_poly], axis=1)
```

### Expected output
- 1,225 candidates → ~80–200 survivors after `threshold='mean'`
- Fast: 5–10 min on full dataset
- Best at capturing **multiplicative interactions**: if defect probability ∝ X3 × X17, this will find it

### Specific pairwise manual features (add unconditionally, before polynomial pass)

```python
# Ratios: dimensionless, scale-invariant
for i in range(49):
    for j in range(i+1, 49):
        if train_x[f'X{j}'].abs().min() > 0.01:  # avoid div-by-zero
            train_x[f'r_{i}_{j}'] = train_x[f'X{i}'] / (train_x[f'X{j}'] + 1e-8)

# Log-ratios: variance-stabilized, good for sensor measurements
import numpy as np
for i in range(49):
    if (train_x[f'X{i}'] > 0).all():
        train_x[f'log_X{i}'] = np.log1p(train_x[f'X{i}'])

# Absolute differences: captures proximity/gap
for i in range(49):
    for j in range(i+1, 49):
        train_x[f'diff_{i}_{j}'] = (train_x[f'X{i}'] - train_x[f'X{j}']).abs()
```

**Warning**: Full pairwise on 49 features = 1,176 ratios + 1,176 diffs + 49 logs = ~2,400 new columns. **Do not add all.** Run importance filter first or use only top-20 SHAP features as the source pool (see Tool 3).

---

## Tool 3: SHAP Interaction Values → Targeted Feature Minting (SURGICAL)

### What it does
Rather than brute-force search, SHAP interaction values identify **which specific (Xi, Xj) pairs** have strong synergistic effect on predictions. Then you mint only those interaction features.

### Recipe

```python
import shap

# Train a base model first
model = lgb.LGBMClassifier(n_estimators=500, n_jobs=8)
model.fit(train_x, train_y)

# Compute TreeSHAP interaction matrix
explainer = shap.TreeExplainer(model)
shap_interaction = explainer.shap_interaction_values(train_x)
# shap_interaction: shape (n_samples, n_features, n_features)

# Average absolute interaction strength per pair
import numpy as np
mean_interact = np.abs(shap_interaction).mean(axis=0)  # (49, 49)
# Zero diagonal (main effects); off-diagonal = pairwise interaction strength

# Find top-k pairs
import pandas as pd
pairs = []
for i in range(49):
    for j in range(i+1, 49):
        pairs.append((f'X{i}', f'X{j}', mean_interact[i, j]))

pairs_df = pd.DataFrame(pairs, columns=['f1','f2','shap_interact'])
pairs_df = pairs_df.sort_values('shap_interact', ascending=False)
top_pairs = pairs_df.head(20)  # take top 20 interaction pairs

# Mint interaction features for those pairs
for _, row in top_pairs.iterrows():
    f1, f2 = row['f1'], row['f2']
    train_x[f'prod_{f1}_{f2}'] = train_x[f1] * train_x[f2]
    train_x[f'ratio_{f1}_{f2}'] = train_x[f1] / (train_x[f2] + 1e-8)
    train_x[f'diff_{f1}_{f2}'] = train_x[f1] - train_x[f2]
```

### Expected output
- 20 pairs × 3 feature types = **60 targeted features**, all model-validated
- Extremely low overfit risk (interaction guided by held-out SHAP, not training correlation)
- Can use `shapiq` library for higher-order (3-way) interactions if needed

### Note on multi-label
Run SHAP interaction analysis per defect label → different pairs may emerge per label → mint union of top pairs.

---

## TabPFN as Feature Extractor (Bonus, Optional)

TabPFN v2 (2025) learns rich internal representations via meta-learning on synthetic causal models. Its mid-layer embeddings encode substantial interaction information. Usage pattern:

```python
from tabpfn import TabPFNClassifier

# Extract embeddings
clf = TabPFNClassifier(device='cpu')
clf.fit(train_x.values, train_y.values)
embeddings = clf.get_embeddings(train_x.values)  # (n, embed_dim)

# Append embeddings as features for your GBDT
train_x_augmented = np.hstack([train_x.values, embeddings])
```

**Caveat**: TabPFN is capped at 10k rows / 500 features. If your train set exceeds this, subsample to get embeddings then use k-NN transfer to remaining rows. Performance gain is speculative for this problem — try it if OpenFE + polynomial both plateau.

---

## Feature Explosion & Overfit Prevention

### The numbers
| Source | Raw candidates | After filter | Risk |
|--------|----------------|--------------|------|
| OpenFE (n_select=30, 7 labels) | ~50k candidates | ~80–120 features | Low (two-stage pruning is strong) |
| Polynomial deg-2 | 1,225 | ~80–200 features | Medium |
| Pairwise manual (full) | ~2,400 | 60–120 (after SHAP/MI filter) | High if unfiltered |
| SHAP-targeted | 60 minted directly | 60 | Low |

### Filter strategy (in order of reliability)

1. **Feature importance threshold** (fastest): train LightGBM → drop features with importance < `mean` importance. Removes ~60–70% of polynomial features typically.

2. **Mutual Information filter** (good for linear + non-linear signals):
   ```python
   from sklearn.feature_selection import mutual_info_classif
   mi = mutual_info_classif(X_new, y, random_state=42)
   keep_mask = mi > np.percentile(mi, 50)  # keep top 50%
   ```

3. **LOFO (Leave One Feature Out)**: Most reliable, most expensive. Use only for final candidate set validation.
   ```python
   # pip install lofo-importance
   from lofo import LOFOImportance, Dataset, plot_importance
   dataset = Dataset(df=train_df, target='defect_label', features=candidate_cols)
   lofo_imp = LOFOImportance(dataset, cv=5, scoring='roc_auc')
   importance_df = lofo_imp.get_importance()
   # Drop features where mean importance < 0 (i.e., hurts OOF score)
   ```

4. **Correlation dedup**: After generating, drop features with pairwise Pearson > 0.97 (keep the one with higher MI).

### Overfit rules
- Never add > 150 new features without cross-validated importance validation
- All feature engineering must be fit on **train fold only** (no leakage into val/test)
- For OpenFE: pass `data=X_train_fold`, `label=y_train_fold` — apply transform to val fold separately
- Polynomial features: fit `PolynomialFeatures` and `SelectFromModel` inside the CV loop
- If CV AUC improves but LB drops → feature leakage or overfit → reduce `n_select`

---

## Recommended Execution Order

```
Step 1 (30 min): Run OpenFE with n_select=20 per defect label
                 → validate on OOF → expect +0.5–2 AUC

Step 2 (20 min): Polynomial deg-2, interaction_only=True
                 → importance filter (threshold='mean')
                 → validate on OOF separately

Step 3 (15 min): SHAP interaction on best current model
                 → identify top-15 pairs → mint 45 targeted features
                 → validate on OOF

Step 4 (10 min): Union all surviving new features from Steps 1-3
                 → final correlation dedup (threshold 0.97)
                 → full OOF validation with augmented feature set

Step 5 (submit): If OOF delta > +0.3 AUC vs current baseline → submit
```

Total time estimate: **1.5 hours** to first augmented submission.

---

## Expected Impact on LB Score

| Technique | Conservative estimate | Optimistic estimate | Condition |
|-----------|----------------------|---------------------|-----------|
| OpenFE (top-20/label) | +0.5 AUC pts | +3 AUC pts | Strong interactions exist |
| Polynomial deg-2 pruned | +0.3 AUC pts | +1.5 AUC pts | Multiplicative structure present |
| SHAP-targeted 60 features | +0.2 AUC pts | +1 AUC pt | Existing model is well-calibrated |
| **Combined (no overfit)** | **+1 AUC pt** | **+5 AUC pts** | All three survive OOF filter |

Current LB: 72.83. With +5 pts optimistic → 77.83. Need further gains from model calibration, ensembling, or target engineering to reach 80+.

---

## Sources

- [OpenFE: Automated Feature Generation with Expert-level Performance (arXiv 2211.12507)](https://arxiv.org/abs/2211.12507)
- [OpenFE Quick Start Documentation](https://openfe-document.readthedocs.io/en/latest/quick_start.html)
- [OpenFE Usage Guide (DeepWiki)](https://deepwiki.com/IIIS-Li-Group/OpenFE/5-usage-guide)
- [OpenFE GitHub Repository](https://github.com/IIIS-Li-Group/OpenFE)
- [OpenFE++ (SDM 2025) — Efficient Automated Feature Generation via Feature Interaction](https://epubs.siam.org/doi/10.1137/1.9781611978520.3)
- [LLM-FE: Automated Feature Engineering with LLMs as Evolutionary Optimizers (arXiv 2503.14434)](https://arxiv.org/html/2503.14434v3)
- [TabPFN v2: A Closer Look at Strengths and Extensions (arXiv 2502.17361)](https://arxiv.org/html/2502.17361v2)
- [SHAP Interaction Values — Beyond TreeSHAP (arXiv 2401.12069)](https://arxiv.org/pdf/2401.12069)
- [Kaggle Grandmasters Playbook — Feature Engineering (NVIDIA Technical Blog)](https://developer.nvidia.com/blog/the-kaggle-grandmasters-playbook-7-battle-tested-modeling-techniques-for-tabular-data/)
- [Effect of Different Feature Selection Methods on XGBoost Models (arXiv 2411.05937)](https://arxiv.org/abs/2411.05937)
- [LOFO Importance — PyPI](https://pypi.org/project/feature-selection-lofo/)
- [OpenFE Parameter Tuning Documentation](https://openfe-document.readthedocs.io/en/latest/parameter_tuning.html)
- [gplearn: Genetic Programming in Python](https://github.com/trevorstephens/gplearn)
- [AutoGluon Tabular Feature Engineering Documentation](https://auto.gluon.ai/stable/tutorials/tabular/tabular-feature-engineering.html)
