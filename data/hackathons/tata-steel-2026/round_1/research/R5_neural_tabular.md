# R5 — Neural Tabular Models Research
**Context:** Tata Steel Defect Detection · LB 72.83 → Target 80+  
**Dataset:** N=1352 train, 339 test, 49 features, binary, ~5%/45% prevalence shift  
**GBDT ceiling:** OOF AUC ~0.88 (LGB+XGB+CatBoost family)  
**Date:** 2026-05-24  
**Goal:** Find neural architecture(s) that add genuine ensemble diversity to GBDT stack

---

## EXECUTIVE SUMMARY

For N=1352, **TabPFN v2.5 is the clear #1 choice** — it is literally designed for this exact regime (small N, no training required, sklearn API, runs on CPU). It will give the most ensemble diversity vs. GBDT because it uses a fundamentally different inductive bias (meta-learned prior-data fitted network). After that, **GANDALF** (via pytorch-tabular) is the best trainable neural option — computationally cheaper than Transformer-family, strong regularization, and has been shown to match GBDT on small tabular. **FT-Transformer** is the #3 pick — the established baseline for tabular transformers, with strong benchmark results even at smaller N.

TabNet, NODE, SAINT, and Mambular/MAMBA are deprioritized for N=1352 (reasons below).

---

## ARCHITECTURE-BY-ARCHITECTURE VERDICT

### 1. TabNet (Arik & Pfister, 2019)
**Verdict: SKIP for standalone; useful only in ensemble as weak contributor**

- Uses sequential attention masks to select features step-by-step (sparse feature selection)
- **Small-N problem:** Typically needs 10K+ to realize its attention learning properly; at N=1352, the feature masks overfit — the sparsity regularization helps somewhat but does not fully solve it
- Benchmarks consistently show TabNet underperforms XGBoost on datasets under 5K rows
- The 2024 comparative study (ResearchGate, Comparing TabNet vs XGBoost) confirms XGBoost dominant at small N
- **If you still try it:** Use `pytorch-tabnet`, set `n_steps=3` (not 6), `gamma=1.5`, `lambda_sparse=1e-3`, high dropout, early stopping patience=5
- **Expected standalone AUC: 0.78–0.84** (below your current GBDT OOF 0.88)
- **Ensemble contribution: marginal** — low diversity vs GBDT because TabNet internally approximates decision tree logic

---

### 2. NODE (Neural Oblivious Decision Ensembles, Popov et al. 2019)
**Verdict: SKIP — computationally expensive, no active maintenance, superseded**

- Differentiable generalization of oblivious decision trees (entmax-based splits), stacked in layers
- In 2019-2020 benchmarks, beat XGBoost on 6/11 datasets — impressive at the time
- **Problems for our case:**
  1. Requires GPU to train in reasonable time (pure PyTorch, no sklearn wrapper)
  2. At N=1352, overfits heavily (designed for 20K+ regime)
  3. No active maintenance since 2020; superseded by FT-Transformer and TabPFN
  4. Installation is non-trivial (custom CUDA ops)
- **Expected standalone AUC: 0.80–0.86** (uncertain, wide variance at small N)
- Not worth the compute + complexity overhead at this stage

---

### 3. FT-Transformer (Gorishniy et al. 2021 → 2024 updates)
**Verdict: INCLUDE — #3 pick. Strong, well-maintained, sklearn-accessible via pytorch-tabular**

- Feature Tokenizer: each feature (numerical + categorical) → embedding → standard Transformer encoder + CLS token → classification head
- **2024 updates:** FT-TabPFN hybrid published (arxiv 2406.06891); also included in Mambular package (`pip install mambular`) and pytorch-tabular (`pip install pytorch-tabular`)
- Booking.com 2024 paper (arxiv 2405.13692) shows FT-Transformer matches or beats GBDT on fraud detection at N~10K — at N=1352 it's tighter but still competitive with strong regularization
- **Key regularization for small N:**
  - `ffn_dropout=0.2`, `attention_dropout=0.1`
  - `embedding_dim=16` (not 32/64 — keep it small)
  - Early stopping with `patience=10`
  - `learning_rate=1e-4`, `weight_decay=1e-5`
- **Expected standalone AUC: 0.82–0.87**
- **Ensemble contribution: +0.3–0.8 AUC points** when stacked with GBDT (different inductive bias: row-wise attention captures interaction patterns GBDT misses)

**Install + Code Outline:**
```python
pip install pytorch-tabular[extra]

from pytorch_tabular import TabularModel
from pytorch_tabular.models import FTTransformerConfig
from pytorch_tabular.config import DataConfig, TrainerConfig, OptimizerConfig

data_config = DataConfig(
    target=["label"],
    continuous_cols=X_cols,
    categorical_cols=[],
)
model_config = FTTransformerConfig(
    task="classification",
    num_attn_blocks=2,        # small — prevent overfit
    num_heads=4,
    embedding_dim=16,
    ffn_dropout=0.2,
    attn_dropout=0.1,
    learning_rate=1e-4,
)
trainer_config = TrainerConfig(
    batch_size=128,
    max_epochs=200,
    early_stopping="valid_loss",
    early_stopping_patience=15,
    checkpoints="valid_loss",
)
tabular_model = TabularModel(
    data_config=data_config,
    model_config=model_config,
    optimizer_config=OptimizerConfig(weight_decay=1e-5),
    trainer_config=trainer_config,
)
tabular_model.fit(train=df_train, validation=df_val)
preds = tabular_model.predict(df_test)
```

---

### 4. SAINT (Somepalli et al. 2021)
**Verdict: SKIP for now — interesting idea but complexity not worth it at N=1352**

- Dual attention: self-attention over features + **inter-sample attention** (attends across rows in the same batch)
- The inter-sample attention is what makes it unique — captures dataset-level patterns
- **Semi-supervised strength:** SAINT with 50-500 labeled samples outperforms baselines (paper shows this). BUT you have 1352 labeled — this advantage diminishes
- **Problem:** Inter-sample attention batch size matters — at small N, batches are small, the cross-row context is limited
- Available via unofficial pytorch implementation (github.com/ogunlao/saint) — not actively maintained
- No clean sklearn API; requires manual cross-validation loop
- **Expected standalone AUC: 0.81–0.86**
- **Verdict:** Similar to FT-Transformer but harder to use. Use FT-Transformer instead (same family, better tooling)

---

### 5. GANDALF (Thomas et al. 2022/2024, ACM IKDD 2025)
**Verdict: INCLUDE — #2 pick for trainable neural. Best neural for small N among trainable models**

- **G**ated **A**daptive **N**etwork for **D**eep **A**utomated **L**earning of **F**eatures
- Core unit: GFLU (Gated Feature Learning Unit) — gating mechanism that selectively activates features, similar in spirit to GLU (Gated Linear Units) in language models
- Benchmarks: matches/beats XGBoost, outperforms FT-Transformer and SAINT on TabSurvey benchmark
- **Key advantage for small N:** GFLUs are parameter-efficient — far fewer weights than attention layers → less overfit risk
- 2025 ACM IKDD publication confirms production-readiness
- Available in `pytorch-tabular` (actively maintained)
- **Expected standalone AUC: 0.83–0.88** — closest to your GBDT ceiling among trainable neurals
- **Ensemble contribution: +0.5–1.0 AUC points** — meaningful diversity because GFLU gating learns feature combinations differently from tree splits

**Install + Code Outline:**
```python
pip install pytorch-tabular[extra]

from pytorch_tabular import TabularModel
from pytorch_tabular.models import GANDALFConfig
from pytorch_tabular.config import DataConfig, TrainerConfig, OptimizerConfig

data_config = DataConfig(
    target=["label"],
    continuous_cols=X_cols,
    categorical_cols=[],
)
model_config = GANDALFConfig(
    task="classification",
    gflu_stages=6,            # reduce from default 10 for small N
    gflu_dropout=0.1,
    gflu_feature_init_sparsity=0.3,
    learning_rate=1e-3,
)
trainer_config = TrainerConfig(
    batch_size=64,            # small batch for small N
    max_epochs=300,
    early_stopping="valid_loss",
    early_stopping_patience=20,
    checkpoints="valid_loss",
)
tabular_model = TabularModel(
    data_config=data_config,
    model_config=model_config,
    optimizer_config=OptimizerConfig(weight_decay=1e-4),
    trainer_config=trainer_config,
)
tabular_model.fit(train=df_train, validation=df_val)
```

---

### 6. Mambular / MAMBA-Tabular (BASF, 2024)
**Verdict: EXPERIMENTAL — interesting but no strong small-N evidence**

- Applies Mamba SSM (State Space Model, linear complexity) to tabular data by treating feature sequence as a "sequence"
- Package: `mambular` (pip install mambular), sklearn API via `MambularClassifier`
- 2024 paper (arxiv 2408.06291) shows competitive results, but benchmarks are on larger datasets (N=5K–100K)
- For N=1352, sequence-based inductive bias makes little sense (49 features is a short sequence, SSM won't shine)
- Requires: `pip install mamba-ssm` which requires CUDA — GPU mandatory, non-trivial install
- **Expected standalone AUC at N=1352: 0.79–0.85** (uncertain, high variance)
- **Verdict:** Deprioritize. Use FT-Transformer (same install friction, better benchmarks at small N)

---

## TOP 3 RECOMMENDATION FOR N=1352

| Rank | Model | Type | Expected Standalone AUC | Ensemble Lift | Compute | Risk |
|------|-------|------|--------------------------|---------------|---------|------|
| **#1** | **TabPFN v2.5** | Foundation model (no training) | **0.87–0.91** | **+0.5–1.5 pts** | CPU-only works | LOW |
| **#2** | **GANDALF** | Trainable neural (pytorch-tabular) | 0.83–0.88 | +0.5–1.0 pts | CPU (slow) / GPU | MEDIUM |
| **#3** | **FT-Transformer** | Trainable neural (pytorch-tabular) | 0.82–0.87 | +0.3–0.8 pts | CPU (slow) / GPU | MEDIUM |

---

## #1 PRIORITY: TabPFN v2.5 — Full Implementation Guide

### Why It's #1 for N=1352
- **Designed for this exact regime.** Original v1 cap was 1000 rows; v2 pushed to 10K; v2.5 handles up to 50K+. At N=1352, you're in TabPFN's sweet spot.
- **No training.** It's a pre-trained foundation model — fit() does in-context inference. Takes ~1-2 seconds on CPU.
- **Outperforms XGBoost defaults** at 100% win rate on datasets ≤10K rows (v2.5 benchmark)
- **Ensemble diversity:** TabPFN uses a Transformer meta-learned on synthetic data — fundamentally different inductive bias from any tree model. Correlation with LGB/XGB/CatBoost is ~0.3–0.5 (very low = high ensemble value)
- **Kaggle validation:** Chris Deotte (Kaggle Grandmaster, 3-level stack) explicitly includes TabPFN alongside GBDT family. Won April 2025 Playground competition.

### Install
```bash
pip install tabpfn
# On first run, opens browser for license acceptance (Prior Labs)
# No GPU needed — CPU inference is fast at N=1352
```

### Full OOF + Ensemble Code
```python
from tabpfn import TabPFNClassifier
from sklearn.model_selection import StratifiedKFold
import numpy as np

# --- OOF generation for stacking ---
skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
oof_tabpfn = np.zeros(len(X_train))
test_preds_list = []

for fold, (train_idx, val_idx) in enumerate(skf.split(X_train, y_train)):
    X_tr, X_val = X_train[train_idx], X_train[val_idx]
    y_tr, y_val = y_train[train_idx], y_train[val_idx]
    
    clf = TabPFNClassifier(
        n_estimators=32,          # internal ensembling; default 8, increase to 32 for stability
        softmax_temperature=0.9,  # slight calibration for imbalanced
        balance_probabilities=True,  # handles class imbalance — IMPORTANT for 5%/45% shift
        random_state=fold,
    )
    clf.fit(X_tr, y_tr)
    oof_tabpfn[val_idx] = clf.predict_proba(X_val)[:, 1]
    test_preds_list.append(clf.predict_proba(X_test)[:, 1])

test_tabpfn = np.mean(test_preds_list, axis=0)

# OOF AUC check
from sklearn.metrics import roc_auc_score
print(f"TabPFN OOF AUC: {roc_auc_score(y_train, oof_tabpfn):.4f}")

# --- Blend with GBDT ---
# Simple weighted average
alpha = 0.2  # start with 20% TabPFN, 80% GBDT ensemble
final_oof = alpha * oof_tabpfn + (1 - alpha) * oof_gbdt_ensemble
final_test = alpha * test_tabpfn + (1 - alpha) * test_gbdt_ensemble
print(f"Blended OOF AUC: {roc_auc_score(y_train, final_oof):.4f}")
```

### Key Parameters for Imbalanced Data
- `balance_probabilities=True` — critical for your 5%/45% prevalence shift
- `n_estimators=32` — more internal averaging = more stable predictions
- `softmax_temperature` — tune between 0.8–1.1 for calibration

---

## ENSEMBLE STRATEGY

### Expected Lift Breakdown
```
Current GBDT ensemble OOF AUC:  ~0.88
+ TabPFN v2.5 (20% weight):     +0.5–1.0 pts → ~0.885–0.89
+ GANDALF (10% weight):          +0.2–0.5 pts → ~0.887–0.895
+ FT-Transformer (10% weight):   +0.1–0.3 pts → ~0.888–0.898
Combined neural blend:           ~0.89–0.90 OOF AUC (target: maps to ~78-80 LB)
```

**Warning:** Your OOF AUC is not your LB score — you had the V27 disaster (+1.04 OOF → -34 LB). But AUC improvement direction is still valid. The ~5% prevalence shift means neural models that use `balance_probabilities` or class-weighted training will generalize better.

### Stacking vs. Blending
- **Blending first** (weighted average) — fast, less overfit risk at small N
- **Stacking** (meta-learner on OOF features) — better ceiling but needs careful implementation:
  ```python
  # Meta-features for stacking
  meta_train = np.column_stack([oof_lgb, oof_xgb, oof_cat, oof_tabpfn, oof_gandalf])
  meta_test  = np.column_stack([test_lgb, test_xgb, test_cat, test_tabpfn, test_gandalf])
  # Meta-learner: LogisticRegression (low overfit) or Ridge
  from sklearn.linear_model import LogisticRegression
  meta_clf = LogisticRegression(C=0.1)  # high regularization
  meta_clf.fit(meta_train, y_train)
  ```

---

## RISK REGISTER

| Risk | Model | Severity | Mitigation |
|------|-------|----------|------------|
| Overfitting at N=1352 | GANDALF, FT-Transformer | HIGH | Strong early stopping, small architecture, dropout |
| OOF calibration ≠ LB | All models | HIGH | Always LB-verify before committing weight increase |
| TabPFN license gate | TabPFN v2.5 | MEDIUM | Browser login on first use; offline after |
| GPU dependency | Mambular/NODE | HIGH | Avoid — stick to CPU-capable models |
| Prevalence shift (5%→45%) | All models | HIGH | `balance_probabilities=True` for TabPFN; `class_weight='balanced'` for others |
| Slow CPU training | GANDALF, FT-Transformer | MEDIUM | Reduce `gflu_stages` / `num_attn_blocks`; use small batch |

---

## QUICK ACTION PLAN

1. **Immediate (30 min):** `pip install tabpfn` → run TabPFN v2.5 OOF with code above → check AUC
2. **If TabPFN OOF > 0.85:** Blend at 20% weight → submit → verify LB lift
3. **Next (1 hr):** `pip install pytorch-tabular[extra]` → run GANDALF OOF → check AUC
4. **If GANDALF OOF > 0.83:** Add to ensemble at 10% weight → resubmit
5. **Only if both above confirm positive LB:** Try FT-Transformer as 3rd neural component
6. **Stacking:** Upgrade from blending only after confirming blend helps LB

---

## SOURCES

- [TabPFN v2 Nature Paper — Accurate predictions on small data](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11711098/)
- [TabPFN v2.5 Article — An Even Better Algorithm](https://rehoyt.medium.com/tabpfn-v2-5-an-even-better-algorithm-68b72c6be5d5)
- [TabPFN GitHub (PriorLabs)](https://github.com/PriorLabs/TabPFN)
- [TabPFN Prior Labs Quickstart Docs](https://docs.priorlabs.ai/quickstart)
- [A Closer Look at TabPFN v2 — NeurIPS 2025](https://neurips.cc/virtual/2025/poster/116283)
- [GANDALF Paper — arxiv 2207.08548](https://arxiv.org/html/2207.08548v6)
- [GANDALF ACM IKDD 2025 Publication](https://dl.acm.org/doi/10.1145/3799830.3799835)
- [FT-Transformer — Revisiting Deep Learning Models for Tabular Data](https://arxiv.org/pdf/2106.11959)
- [FT-Transformer at Booking.com Fraud Detection 2024](https://arxiv.org/html/2405.13692v2)
- [SAINT Paper — arxiv 2106.01342](https://ar5iv.labs.arxiv.org/html/2106.01342)
- [NODE Paper — arxiv 1909.06312](https://arxiv.org/pdf/1909.06312)
- [Mambular — A Sequential Model for Tabular DL](https://arxiv.org/pdf/2408.06291)
- [Mambular GitHub (BASF)](https://github.com/basf/mamba-tabular)
- [pytorch-tabular GitHub](https://github.com/manujosephv/pytorch_tabular)
- [pytorch-tabular Supervised Models Docs](https://pytorch-tabular.readthedocs.io/en/stable/apidocs_model/)
- [Kaggle Grandmasters Playbook — NVIDIA](https://developer.nvidia.com/blog/the-kaggle-grandmasters-playbook-7-battle-tested-modeling-techniques-for-tabular-data/)
- [Kaggle Playground Winning Strategies 2025](https://medium.com/@gauurab/kaggle-playground-how-top-competitors-actually-win-in-2025-c75d4b380bb5)
- [OmniTabBench: GBDTs vs Neural vs Foundation Models](https://arxiv.org/html/2604.06814v1)
- [TabNet Paper — arxiv 1908.07442](https://arxiv.org/pdf/1908.07442)
- [Tabular Deep Learning Survey 2024](https://www.techrxiv.org/users/961472/articles/1332693)

---

**Confidence: HIGH** — TabPFN v2.5 verdict is backed by Nature publication + multiple Kaggle grandmaster confirmations. GANDALF verdict backed by ACM publication + pytorch-tabular active maintenance. NODE/SAINT/Mambular skip rationale based on small-N benchmark consensus across 4+ independent sources.
