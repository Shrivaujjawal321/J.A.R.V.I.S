# V68 — Approach Document

## Core Hypothesis

Defective steel coils are **anomalies in the feature distribution** — they deviate from normal operating conditions regardless of the label. Unsupervised anomaly detection, fit on train+test combined, should surface these without depending on any label-based training signal.

This matters because: V64/V65 failed due to train-test distribution gap. V68 has no such vulnerability — it scores every row relative to the combined distribution it's actually part of.

## Method

### Detectors Fit

All detectors are trained on the **combined 1691-row matrix** (train + test), StandardScaler-normalized. This is intentional: the test rows participate in defining "normal" alongside train rows.

**IsolationForest (3-seed bag)**
- n_estimators=200, contamination='auto', seeds [42, 137, 1000]
- Anomaly score = mean of `-score_samples()` across 3 seeds
- Isolates anomalies by randomly partitioning feature space; shorter average path = more anomalous
- Best single-detector: AUC 0.7474

**COPOD (Copula-Based Outlier Detection)**
- Parameter-free empirical copula fitting
- Models each feature's marginal CDF, then combines via tail probabilities
- AUC 0.6887, adds complementary signal to IF

**ECOD (fit, excluded from ensemble)**
- Empirical CDF, similar to COPOD but strictly marginal (no copula cross-terms)
- AUC 0.5989 — weaker, adds noise to ensemble

**LOF (fit, excluded from ensemble)**
- Local density ratio vs neighbors, n_neighbors=20
- AUC 0.5294 with **negative** Spearman vs V44 — harmful to ensemble

### Score Aggregation

For each detector → rank-normalize scores to [0,1] (1=most anomalous). Average ranks across ensemble detectors (IF + COPOD). Result: V68 score per row, where 1.0 = both detectors agree this row is maximally anomalous.

### Why rank-averaging not raw score averaging

Raw scores are on incompatible scales (IF: ~0.4-0.6; COPOD: 42-126). Rank normalization makes them comparable without assumptions about their distributions.

## Diagnostic Findings

Initial run with all 5 detectors (IF + ECOD + COPOD + LOF + DeepSVDD) equal-weighted:
- Ensemble AUC: 0.6687 (worse than IF alone at 0.7474)
- G2 recall@10%: 18.2% — FAIL
- Spearman vs V44: 0.18 — FAIL (too uncorrelated = noise, not signal)

Root cause: LOF negative contribution pulls consensus toward random. ECOD redundant with COPOD, dilutes. DeepSVDD loss plateau (stuck at ~54.75 across all 50 epochs) — not converging on this 1691×51 tabular dataset. All three excluded.

Final IF+COPOD ensemble: AUC 0.7312, G2=22.7%, rho=0.446 — ALL GATES PASS.

## Limitations

1. **No refit on test subset.** LOF doesn't support `novelty=True` when trained on combined data — scores are for training instances only. COPOD/IF do provide proper combined scores.
2. **Spearman 0.446 means correlation with V44.** This is expected — IF detects the same process anomalies that V44's supervised models learned. The 0.446 is the goldilocks zone: correlated enough to be useful signal, different enough to be genuinely additive.
3. **No temporal features.** V68 operates on the 51 static+engineered V4 features. Temporal patterns (lag features) are in the feature set but LOF was excluded — the ensemble may miss coils that are only anomalous in temporal sequence.

## Files

| File | Description |
|---|---|
| `train_v68.py` | Full build script (reproducible) |
| `test_proba_v68.parquet` | 339 test rows with v68 anomaly score [0,1] |
| `oof_v68.parquet` | 1352 train rows with v68 score + per-detector scores |
| `v68_metrics.json` | Gate results + per-detector AUCs |
| `top30_test_v68.csv` | Top 30 test CoilIDs by V68 anomaly score |
| `oof_v68_metrics.md` | Human-readable metrics + V70 recommendation |
| `approach.md` | This document |
