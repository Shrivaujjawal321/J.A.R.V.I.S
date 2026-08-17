# V37 Approach — AutoGluon Paradigm Injection

**Date:** 2026-05-24
**Status:** BUILT — pending execution + OOF evaluation

---

## 1. Motivation

V4/V33/V34/V35 are all GBDT-family (Spearman 0.89-0.98 correlated). The consensus union
at K=186 achieved LB 67.55 but is fundamentally a GBDT echo chamber.

Peer Ratnesh-Jarvis hit LB 72.71 with multi-paradigm consensus including AutoGluon + TabPFN,
confirming that genuine model-family diversity is the lever we need.

AutoGluon's `best_quality` preset runs 30+ internal model types:
- Neural nets (NeuralNetTorch)
- Random Forest, Extra Trees
- KNN, LinearModel
- Multiple GBDT configs (LightGBM, XGBoost, CatBoost — different from our tuned versions)
- Weighted stacking ensemble across all of these

This gives us instant paradigm diversity without engineering individual model types.

---

## 2. Architecture

**Feature set:** V33's 105-feature pipeline
- 49 raw X features
- 54 per-stand residual features (fold-isolated medians, AP-1 compliant)
- Total: 103 features after CoilID drop

**CV:** StratifiedKFold(5, shuffle=True, seed=42) — matches V4/V33/V34/V35

**Inner AutoGluon config per fold:**
- `presets="best_quality"`
- `time_limit` = dynamic per fold (wall-aware)
- `num_bag_folds=5, num_bag_sets=1` — AG's own internal bagging
- `num_stack_levels=1` — L2 AG stacking within each outer fold
- `excluded_model_types=["FASTAI"]` — stability (FastAI install issues in some envs)

**Imbalance:** BBSE sample weights (w1=9.0, w0=0.579) passed via `sample_weight` column

**Wall budget:** 55 min hard stop (5 min buffer below 60 min spec)

---

## 3. Key Differences from V18 (previous AG attempt)

| Aspect | V18 | V37 |
|---|---|---|
| Feature set | V5 features (no stand-FE) | V33's 105-feature set (stand-FE) |
| CV structure | Single AG fit on all train | 5-fold outer CV matching other models |
| BBSE weights | Not used | w1=9, w0=0.579 via sample_weight col |
| OOF structure | predict_oof() from AG | True outer-fold OOF for Spearman comparison |
| Goal | Standalone submission | Consensus union diversity injection |

---

## 4. Diversity Hypothesis

**Claim:** AutoGluon's NNs + RF + ET + KNN will produce OOF probabilities with Spearman r < 0.80
vs V4's GBDT meta OOF.

**Why this matters:** The consensus union ranks predictions. If V37 adds diverse ordering of
borderline coils (those near the defect threshold), the union K-vote can make better decisions
than any individual GBDT.

**Verification threshold:** Spearman r vs V4_meta < 0.80 → confirm diversity. If r > 0.90 →
AutoGluon converged to GBDT-dominated ensemble → marginal diversity benefit only.

---

## 5. CRITICAL Implementation Notes

- **Fold-isolated medians:** StandSetpoints.fit() called on tr_idx rows only. transform() applied
  to val and test using frozen scalars. AP-1 compliance enforced.
- **Test proba:** Average of per-fold test predictions (5 folds × 339 test rows matrix).
- **NO submission CSV generated.** Orchestrator handles consensus union + LB fire.
- **BBSE weights:** Passed as `_sample_weight` column to AutoGluon (AG supports sample_weight
  via column-name mechanism as of v1.0+).

---

## 6. Expected Outputs

1. `train_v37.py` — training script
2. `feature_engineering.py` — copy from V33
3. `oof_v37.parquet` — (CoilID, oof_proba, y) × 1352 rows
4. `test_proba_v37.parquet` — (CoilID, test_proba) × 339 rows
5. `cv_report_v37.md` — OOF AUC, CI, model leaderboard, Spearman correlations
6. `metrics_v37.json` — machine-readable version of cv_report
7. `ag_models_v37_fold*/` — AG model artifacts (can be deleted after OOF saved)

---

## 7. Gate for Consensus Union

- OOF AUC >= 0.78 (baseline bar — below this AG is not useful)
- Spearman r vs V4_meta < 0.90 (if > 0.90 across all, diversity claim is weak)
- At least 3/5 folds completed (wall-time aware exit)
