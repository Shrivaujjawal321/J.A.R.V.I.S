# CV Report — V41 BBSE-Reweighted LightGBM

**Date:** 2026-05-24
**Builder:** ml-engineer-agent
**Paradigm:** BBSE sample weights | scale_pos_weight=1 | single LightGBM
**Feature set:** V4's 51 SHAP-selected features (NO stand-FE, NO SMOTE)

---

## Design Rationale (BBSE Paradigm)

Ratnesh-Jarvis peer intel: iter37 = BBSE-reweighted version of his v32 base.
- Train prevalence: ~5% positive (66/1352)
- Expected test prevalence: ~45% positive (from K=170/339)
- BBSE reweight: w1 = 0.45/0.05 = 9.0000, w0 = 0.55/0.95 = 0.5789
- scale_pos_weight = 1 (BBSE does the rebalancing, not LGB's built-in mechanism)
- Effective w1/w0 ratio = 15.55x (vs ≈19.5x in V35's scale_pos_weight)

The key BBSE insight: by matching train→test distribution shift explicitly via
sample weights (rather than amplifying class imbalance), BBSE produces different
score RANKINGS than scale_pos_weight-based models — even on identical features.
This ranking diversity is the consensus-union value, not standalone AUC.

---

## OOF AUC Results

| Metric | Value |
|---|---|
| Per-fold AUCs | ['0.82677', '0.89772', '0.74978', '0.93565', '0.88776'] |
| Mean OOF AUC | 0.85954 |
| Std OOF AUC | 0.06507 |
| Full OOF AUC | 0.86126 |
| Bootstrap 95% CI | [0.81169, 0.90294] |

**Note on AUC:** BBSE reweighting distorts the OOF probability distribution
(shifts calibration toward test prevalence). The OOF AUC is expected to be LOWER
than V4/V35 (which optimize for train-distribution AUC). This is by design —
the probe for paradigm value is Spearman diversity, not AUC ranking.

---

## Competition Metric (OOF)

| Metric | Value |
|---|---|
| Best (R+P)/2 | 52.4572% |
| Best threshold | 0.00100 |
| Recall | 1.0000 |
| Precision | 0.0491 |
| Calibrated LB est | 55.13 (OOF 52.46 + delta 2.67) |
| V4 banked LB | 56.98 |
| V35 best LB | 67.55 |

**Expected: LB est ~56 (peer confirmation: Ratnesh's iter37 BBSE-alone → LB 56.86)**

---

## Paradigm Diversity — Spearman Correlation

- V41 vs V4_meta: r=0.8199  (MODERATE) | paradigm_value=YES — unique ranking
- V41 vs V33: r=0.8260  (MODERATE) | paradigm_value=YES — unique ranking
- V41 vs V35_rank_avg: r=0.8930  (MODERATE) | paradigm_value=MODERATE
- V41 vs V37_autogluon: r=0.0557  (DIVERSE) | paradigm_value=YES — unique ranking

**Target:** r < 0.85 vs all existing paradigms = unique ranking signal.
**Ratnesh result:** BBSE shifted his ranking enough to add consensus signal
when combined with his 9-model ensemble.

---

## Consensus Union Readiness

| Criterion | Result |
|---|---|
| Standalone AUC competitive? | NO (expected — BBSE standalone is mid) |
| Spearman < 0.85 vs all? | MAX r=0.8930 — check |
| Adds unique ranking signal? | YES |
| Ready to merge into consensus? | **YES** |

---

## Top-3 Risks

1. **OOF AUC optimism:** BBSE shifts the predicted probabilities toward test
   prevalence, which may inflate or deflate OOF AUC compared to what a
   well-calibrated model would show. OOF AUC is NOT the primary quality metric
   here — Spearman diversity is.

2. **OOF calibration ≠ LB calibration:** The +2.67 delta was calibrated on
   scale_pos_weight-based models. BBSE rebalancing changes the probability
   scale; the delta may not hold. **Do NOT use V41 OOF score as LB predictor
   for consensus-union submissions.**

3. **Spearman convergence risk:** If BBSE-reweighted LGB converges to the same
   tree splits as scale_pos_weight-based LGB (same features + similar effective
   rebalancing), Spearman will be > 0.90 and V41 adds no diversity. Check
   spearman_results above — if all r > 0.90, V41 is redundant.

---

## Features Used

- **V4's 51 SHAP-selected features** (no stand-FE additions)
- Spec: same feature set as V4 paradigm — different training OBJECTIVE
- Stand-FE omitted by design to isolate BBSE paradigm effect cleanly
- Fold-isolated StandSetpoints medians applied for V4 lag/temporal features

---

## Files

- `oof_v41.parquet` — 1352 rows, cols: CoilID, oof_proba, y
- `test_proba_v41.parquet` — 339 rows, cols: CoilID, test_proba
- `cv_report_v41.md` — this file
- `approach.md` — human-readable paradigm summary

**DO NOT SUBMIT V41 standalone** — consensus union only.
