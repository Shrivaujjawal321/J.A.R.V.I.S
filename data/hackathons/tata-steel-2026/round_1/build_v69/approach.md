# V69 — Tabular Foundation Model Stack

## Motivation

V44 is a 5-paradigm GBDT-heavy ensemble (LightGBM + XGBoost + CatBoost + neural nets). All these models share the same inductive bias: gradient boosted trees are decision-boundary machines that partition feature space via axis-aligned splits, biased toward high-frequency patterns.

V69 introduces a completely orthogonal inductive bias: **pre-trained tabular transformers** that have seen millions of diverse tabular tasks and learned meta-priors about tabular data distributions. This is analogous to how BERT embeddings benefit NLP pipelines that already have TF-IDF — different representational space, different error modes, complementary when combined.

## Models

### TabICL (In-Context Learning for Tabular Data)
- **Architecture:** Transformer trained in-context style — treats training data as a "prompt" and test rows as queries. No gradient update at fit time.
- **Inductive bias:** Learns from examples in context, like few-shot learning. Particularly good at capturing inter-sample relationships.
- **Source:** Open-source, HuggingFace-released. `pip install tabicl`.
- **Config:** n_estimators=8, 3 seeds [42, 137, 1000], StratifiedKFold(5).

### TabDPT (Deep Prediction Transformer)
- **Architecture:** Pretrained deep transformer with retrieval-augmented inference. At inference it retrieves similar training examples to condition predictions.
- **Inductive bias:** Explicitly models similarity structure in feature space — complementary to TabICL's global in-context approach.
- **Source:** HuggingFace weights download at first run. `pip install tabdpt`.
- **Config:** Default params (CPU-safe inf_batch_size), 3 seeds, StratifiedKFold(5).

### TabPFN v2 (Prior-data Fitted Network)
- **Status:** Token required (TABPFN_TOKEN env var). Skipped if not set.
- **Architecture:** Meta-learned prior over Bayesian Neural Networks, trained to approximate Bayesian inference on tabular data.
- **Why skipped:** Requires account at priorlabs.ai and one-time model weight download.

## Feature Engineering

Using V4's 51 SHAP-selected features directly. No additional engineering — these foundation models benefit from clean, informative features without needing GBM-style interaction engineering. They learn their own interactions.

## Training Protocol

- **CV:** StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
- **Imbalance handling:** TabICL handles internally (class shuffle augmentation). TabDPT handles via retrieval weighting.
- **Seeds:** 3 seeds (42, 137, 1000) per model, averaged to reduce variance.
- **Aggregation:** Rank-normalize each model's OOF + test probabilities, then average. Rank-normalization prevents any single model from dominating due to miscalibration.

## Validation Gates

| Gate | Criterion | Rationale |
|------|-----------|-----------|
| G1 | OOF AUC > 0.85 | Must match V35 baseline quality to be useful |
| G2 | Fold std AUC < 0.05 | Stability required for reliable LB estimate |
| G3 | Spearman vs V44: 0.50–0.80 | Diverse enough to add value, coherent enough to not be noise |

## Role in V70

V69 is NOT a standalone submission. It is a **voter** in V70's consensus ensemble. Its value is its orthogonal error profile vs V44's GBDT stack — disagreements between V69 and V44 signal genuine uncertainty, where one or the other may have found the true signal.

Expected V70 strategy: rank-average or logistic meta-learner on [V44_oof, V69_oof] → optimize threshold on HE scoring formula Score = 50·TP·(K+154)/(K·154).
