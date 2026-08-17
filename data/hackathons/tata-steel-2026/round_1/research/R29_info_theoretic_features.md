# R29 — Information-Theoretic Feature Selection for Tata Steel Round 1

**Date:** 2026-05-24
**Context:** Banked V4 = 56.98 LB. Current best feature space ~105 (V4 51 + V35 54 new). Paradigms correlated 0.77–0.99. Question: is extra feature mass adding information or just correlated noise that hurts generalization on small private test split?
**N:** ~340 train, ~339 test (50/50 public/private). Tiny N = noise features hurt badly.

---

## Quick Answer

On N~340 with 105 features, information-redundant features are **actively harmful** — they add estimation variance to LightGBM's split-finding without adding signal. The expected reduction is 105 → 40–55 features that carry genuinely independent mutual information with Y. AUC impact: typically **+0.005 to +0.015 OOF**, more importantly **+0.02–0.04 generalization gap narrowing** on held-out private split.

Three methods are recommended in ranked order for our specific problem shape.

---

## Method 1 (RECOMMENDED PRIMARY): mRMR — Maximum Relevance, Minimum Redundancy

### What it does

Iteratively selects features using conditional mutual information: at each step picks the feature maximising `I(X_j ; Y) - (1/|S|) * sum_{X_i in S} I(X_j ; X_i)`. This directly targets the paradigm-correlation problem: two features correlated at 0.95 carry essentially the same `I(X; Y)`, so the second one is penalised by the redundancy term and dropped.

### Why it fits our problem

- Small N, high inter-feature correlation (0.77–0.99) = textbook mRMR use case
- Filter method = no retraining required = fast on 105 features × 340 samples
- Result is a ranked list; we can sweep K (30, 40, 50, 60) with a single 5-fold CV run
- Directly tests the hypothesis: "do paradigms 2–5 add information beyond paradigm 1?"

### Python implementation

```bash
pip install mrmr-selection
```

```python
import pandas as pd
from mrmr import mrmr_classif

# X: pd.DataFrame, shape (340, 105). y: pd.Series, binary defect label
ranked_features = mrmr_classif(X=X_train, y=y_train, K=60)
# ranked_features is a list of column names, most informative first

# Sweep K to find AUC plateau
import lightgbm as lgb
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import roc_auc_score

results = {}
for k in [20, 30, 40, 50, 60, 75, 105]:
    cols = ranked_features[:k] if k <= len(ranked_features) else ranked_features
    oof_scores = []
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    for tr, va in skf.split(X_train, y_train):
        m = lgb.LGBMClassifier(n_estimators=500, learning_rate=0.02,
                                num_leaves=15, min_child_samples=10,
                                class_weight='balanced', random_state=42)
        m.fit(X_train.iloc[tr][cols], y_train.iloc[tr])
        oof_scores.append(roc_auc_score(y_train.iloc[va], m.predict_proba(X_train.iloc[va][cols])[:,1]))
    results[k] = sum(oof_scores) / len(oof_scores)

# Expect plateau around K=40-55; beyond that AUC flattens or degrades
print(results)
```

### Expected outcome

- K=105 (all): OOF AUC ~0.89 (baseline, V10 territory)
- K=40–55 (mRMR subset): OOF AUC ~0.895–0.905 (+0.005–0.015)
- Generalization to private split: likely narrows overfit gap by 2–4 LB points

### Key paper

Ding, C., Peng, H. (2005) — "Minimum Redundancy Feature Selection From Microarray Gene Expression Data." Classic but still state-of-art for filter-based IT selection. Modern Python implementation: [smazzanti/mrmr](https://github.com/smazzanti/mrmr) — last updated 2024.

2024 hybrid study: BoMGene (Boruta + mRMR combined) on gene expression showed feature reduction from ~200 → 40 while **improving** AUC vs either method alone. [arXiv:2510.00907](https://arxiv.org/pdf/2510.00907)

---

## Method 2 (RECOMMENDED SECONDARY): shap-select — SHAP-Value Linear Regression Filter

### What it does

Train LightGBM once on all 105 features. Compute TreeSHAP values (exact, fast). Run logistic regression of Y on SHAP values. Use L1 + recursive elimination to drop features whose SHAP coefficient is statistically non-significant (p > 0.05). Handles collinearity explicitly via L1 regularization (λ=1e-6) + recursive re-evaluation.

### Why it fits

- Model-aware: uses the actual LightGBM's learned relationships, not just marginal MI estimates
- Handles the "correlated paradigms" problem: if two paradigm aggregates have same SHAP pattern, the regression drops the redundant one
- **2024 paper (Wise Plc / TransferWise):** on 30-feature fraud dataset, reduced to 6 features while retaining 98.7% of F1. 4.5x faster than Boruta. [arXiv:2410.06815](https://arxiv.org/abs/2410.06815)
- One-shot cost: train model once, run regression — no resampling needed

### Python implementation

```bash
pip install shap-select shap
```

```python
import lightgbm as lgb
import shap
from shap_select import shap_select

# Train base model on full 105-feature space
base_model = lgb.LGBMClassifier(n_estimators=300, learning_rate=0.02,
                                  num_leaves=15, class_weight='balanced',
                                  random_state=42)
base_model.fit(X_train, y_train)

# Run shap-select with a validation split
X_tr, X_val, y_tr, y_val = train_test_split(X_train, y_train, test_size=0.2,
                                              stratify=y_train, random_state=42)
base_model.fit(X_tr, y_tr)

selected = shap_select(base_model, X_val, y_val, task='classification', threshold=0.05)
print(f"Selected {len(selected)} features: {selected}")

# Retrain on selected features with full train
final_model = lgb.LGBMClassifier(n_estimators=500, learning_rate=0.02,
                                   num_leaves=15, class_weight='balanced',
                                   random_state=42)
final_model.fit(X_train[selected], y_train)
```

### Expected outcome

- Typically retains 35–50 features from 105 on correlated tabular data
- F1/AUC comparison vs Boruta and RFE: competitive with Boruta, 4x faster
- Best used as cross-validation against mRMR: if both methods agree on a feature subset, that set is highly stable

### Key paper

Kraev et al. (2024, Wise Plc). "Shap-Select: Lightweight Feature Selection Using SHAP Values and Regression." [arXiv:2410.06815](https://arxiv.org/abs/2410.06815). GitHub: [transferwise/shap-select](https://github.com/transferwise/shap-select).

---

## Method 3 (DIAGNOSTIC / OPTIONAL): HSIC Lasso — Non-linear Independence Criterion

### What it does

Measures Hilbert-Schmidt Independence Criterion between each feature kernel matrix `K(X_j)` and the target kernel `L(Y)`. Solves a convex Lasso-penalized problem to find a minimal set of features with maximum non-linear statistical independence from Y, while penalising redundancy between selected features. It is strictly more powerful than mRMR for non-linear relationships.

### Why it fits (but use carefully)

- Can catch non-linear feature–target relationships that mRMR's MI estimate misses (MI assumes discretised bins; HSIC is exact in kernel RKHS)
- Downside on N~340: block HSIC Lasso memory is O(d·N·B·M). With N=340, B=50, M=3 → manageable
- Slower than mRMR; best used as a verification run rather than primary

### Python implementation

```bash
pip install pyHSICLasso
```

```python
from pyHSICLasso import HSICLasso

hsic = HSICLasso()
# For classification: use 'classification' mode
hsic.input(X_train.values, y_train.values)
hsic.classification(num_feat=50, B=50, M=3)

selected_idx = hsic.get_index()
selected_names = [X_train.columns[i] for i in selected_idx]
print(f"HSIC Lasso selected {len(selected_names)} features: {selected_names}")
```

Note: HSIC Lasso paper (Yamada et al., 2014, NeurIPS) shows on biomedical data (N~500, D~5000) it reduces features 10–50x while preserving or improving AUC. For N=340 expect 30–45 features selected from 105.

### Key paper

Yamada, M., et al. (2014). "High-Dimensional Feature Selection by Feature-Wise Kernelized Lasso." Neural Computation. Implemented in: [riken-aip/pyHSICLasso](https://github.com/riken-aip/pyHSICLasso).

---

## Method 4 (CAUSAL / RESEARCH-GRADE): PC Algorithm — Causal Parent Discovery

### Why lower priority for our use case

The PC algorithm (Peter-Clark) uses conditional independence tests to recover the Markov blanket of Y — i.e., the features that are *direct causal parents* of Y, not just correlated with it. On our hot-rolling dataset this is theoretically compelling (X18=finishing temperature genuinely *causes* defects; its correlated proxies like X17, X19 are not causes).

However: PC algorithm requires N >> p for reliable CI testing. At N=340, p=105, we are in the regime where PC is unreliable — false edge exclusions are common, and the output varies with CI test threshold. **Do not use as primary selector on this dataset.**

Use PC only for causal *interpretation* of what mRMR selected: if mRMR picks X18 but not X17, that's consistent with X18 being a causal parent. Python: `causal-learn` (CMU), Salesforce `causalai`.

---

## Recommended Execution Plan (Parallel, 30 min total)

```
Agent A: Run mRMR sweep K=[20,30,40,50,60,75,105] → plot AUC curve
Agent B: Run shap-select with threshold=[0.01, 0.05, 0.10] → count selected features per threshold
Agent C: (optional) Run HSIC Lasso K=40 → compare overlap with mRMR-50 set
```

### Decision rule after sweep

| Scenario | Action |
|---|---|
| mRMR-K AUC plateau at K=40–50 | Use mRMR-K as V45 feature space. Submit. |
| mRMR-K AUC peak then degrades above K=50 | Strong evidence noise features are hurting. Use K at peak. |
| mRMR-K AUC monotone increasing to K=105 | Features are not redundant; skip IT filter, move to other strategies |
| mRMR and shap-select agree on ~40-feature overlap | HIGH CONFIDENCE subset. This is our gold feature set. |

---

## Expected Feature Count Reduction and AUC Impact

| Method | Expected Output Features (from 105) | Expected OOF AUC Delta | Generalization Gain (Private Split) |
|---|---|---|---|
| mRMR K-sweep | 40–55 | +0.005 to +0.015 | +1 to +3 LB points |
| shap-select (p<0.05) | 35–50 | +0.003 to +0.012 | +1 to +3 LB points |
| HSIC Lasso (K=40) | 30–45 | +0.005 to +0.020 | +1 to +4 LB points |
| Intersection (mRMR ∩ shap-select) | 30–40 | potentially +0.015–0.025 | +2 to +5 LB points |

**Key context:** Our ceiling is ~58 LB (V10 meta-estimate). These methods are not miracle workers — but they directly address the 0.77–0.99 paradigm correlation problem. A 3-point LB gain on the private split (where it counts for ranking) is plausible given the overfit risk of 105 correlated features on N=340.

---

## 2024–2025 Papers (Cited Above)

1. **BoMGene (2025)** — Boruta + mRMR hybrid. Feature reduction ~200 → 40, AUC maintained or improved. [arXiv:2510.00907](https://arxiv.org/pdf/2510.00907)
2. **shap-select (2024, Wise Plc)** — SHAP-value logistic regression for feature selection. 6 from 30, 98.7% F1 retention. [arXiv:2410.06815](https://arxiv.org/abs/2410.06815)
3. **Stability of IT feature selection (2024)** — Shows that small-N instability in feature rankings is a real concern; recommends ensemble-of-selectors approach. [arXiv:2402.05295](https://arxiv.org/pdf/2402.05295)
4. **Survey: Causality, ML, and Feature Selection (2025, PMC)** — Comprehensive review including causal vs correlational methods. [PMC12030831](https://pmc.ncbi.nlm.nih.gov/articles/PMC12030831/)
5. **Optimal Data Reduction under IT Criteria (2025)** — Formal theory of minimum-information-loss feature reduction. [arXiv:2508.16123](https://arxiv.org/pdf/2508.16123)

---

## Anti-Patterns to Avoid

- **Do NOT run RFECV** on N=340 with 105 features — retrains model for every feature subset, very slow, high variance
- **Do NOT trust a single run of mRMR** with K fixed — sweep K and look at the AUC curve shape
- **Do NOT apply feature selection inside the CV loop without tracking leak** — run mRMR outside CV (filter method) to avoid contamination
- **Do NOT discard features with low individual MI** if they are part of an interaction — HSIC Lasso handles this; mRMR partially does via redundancy term

---

## Confidence: Medium-High

mRMR and shap-select are mature, well-validated methods. The specific AUC gains are estimates — actual impact depends on how much genuine new information our 54 V35 features add vs. how correlated they are with V4's 51. Given paradigm correlations of 0.77–0.99, mRMR is very likely to drop 30–50 features without AUC loss. Generalization improvement on the private split (small N) is the primary expected win.
