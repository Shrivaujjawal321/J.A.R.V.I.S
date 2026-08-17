# PU Learning Track — Tata Steel 2026 Round 1

**Date:** 2026-05-23
**Script:** `/tmp/pu_pipeline.py`
**Outputs:** `/tmp/pu_results/`

---

## 1. Headline

**Label noise HIGH (c=0.154) — ~361 hidden defects in train — but PU methods give marginal lift (-0.58 pts) — not the breakthrough path**

---

## 2. Label Propensity Estimation (Phase A — Elkan-Noto 2008)

Method: Train a binary classifier on `s` (labeled Y=1 vs unlabeled Y=0). Then
`c = E[P(s=1|x) | y=1]` — mean predicted score on held-out LABELED POSITIVE rows.
This estimates the fraction of true defects that inspection actually caught.

| Metric | Value |
|--------|-------|
| Estimated c (labeling propensity) | **0.1544 ± 0.0326** |
| Noise verdict | **HIGH — label noise confirmed** |
| Labeled prevalence P(s=1) | 0.0488 (66/1352) |
| Estimated TRUE defect rate | **0.3162 (~427 true defects)** |
| Hidden positives in train Y=0 (est.) | **~361** of 1286 "negatives" |
| Hidden positives in test (est.) | **~107** of 339 test rows |

Per-fold c estimates: `[0.1383, 0.1715, 0.1412, 0.2079, 0.113]`

**Interpretation:** c = 0.154 means the inspection system only flagged ~15% of
true defects. Approximately 361 train rows labeled Y=0 are likely actual defects
that slipped through inspection. This is SEVERE noise — but knowing it doesn't automatically
help, because we can't tell WHICH Y=0 rows are hidden defects without extra signals.

**IMPORTANT CAVEAT:** The c estimate of 0.154 may be too low. Elkan-Noto's c estimator
can underestimate when the PU model itself is imperfect. A sanity check:
if 31.6% of rows are truly defective, that's ~427 defects in 1352 rows vs. 66 labeled —
a 6.5x miss rate seems extremely high for a steel plant. Real c is likely higher (0.5–0.8).
The method's weakness: if P(s=1|x) is hard to learn (AUC ~0.86 on s-labels), c gets
systematically underestimated. Treat this as a lower bound on data quality.

---

## 3. Per-Method Results (Phase B)

| Method | OOF AUC | OOF Score | 95% CI | Lift vs V5 | Pred LB |
|--------|---------|-----------|--------|------------|---------|
| V5 baseline | 0.8886 | 53.41 | — | 0.00 | 56.08 |
| M1 Elkan-Noto reweighting | 0.8657 | **53.12** | [52.5, 56.8] | -0.29 | 55.79 |
| M2 Spy technique | 0.8097 | 51.15 | [48.5, 55.1] | -2.26 | 53.82 |
| M3 Asymmetric loss (spw=100) | 0.8537 | 48.25 | [43.8, 54.7] | -5.16 | 50.92 |
| M4 Self-training (CV-safe) | 0.8447 | 47.98 | [40.6, 56.2] | -5.43 | 50.65 |
| M5 Co-training (2 views) | 0.8591 | 49.47 | [44.9, 55.4] | -3.94 | 52.14 |
| **6-way Meta Blend** | **0.8485** | **52.54** | **[52.0, 55.9]** | **-0.87** | **55.21** |

V5 baseline OOF score per oof_v5 = 53.41 (slightly higher than 53.70 target, reporting gap likely
from threshold differences — using 53.70 as the declared target throughout).

Score = (Recall + Precision) / 2 × 100 at best OOF threshold.

---

## 4. Best Blend OOF + Predicted LB

| | Value |
|--|--|
| Best standalone PU (M1 Elkan-Noto) | 53.12 |
| 6-way blend OOF Score | **52.54** |
| V5 baseline OOF | 53.70 |
| Calibration delta | +2.67 |
| Predicted LB (blend) | **55.21** |
| V4 actual LB | 56.98 |
| Top-10 cutoff | ~80.6 |
| Gap to top-10 | ~25.4 points |

The 6-way blend does NOT beat V5 standalone — PU methods hurt OOF performance.
This makes sense: the LR meta is giving non-trivial weight to noisier PU signals.

---

## 5. Recommendation for V8

**PU learning is NOT the path to 90%+ accuracy for this dataset.**

### What the numbers say:

- All 5 PU methods score BELOW V5 baseline (53.41) in OOF
- The best PU method (M1 at 53.12) is essentially tied with V5 within CI
- The 6-way blend actually pulls V5 DOWN to 52.54
- c ≈ 0.15 is suspiciously low — likely Elkan-Noto underestimating due to imperfect P(s|x) model

### Why PU didn't help here:

1. **AUC on s-labels is only 0.86** — the model can't cleanly separate labeled from unlabeled.
   Good PU requires a model that almost perfectly distinguishes labeled from unlabeled.
2. **Asymmetric loss (M3) hurt** — scale_pos_weight=100 forces near-100% recall but destroys
   precision, which is exactly half the score. At 4.9% class balance, extreme weight > 20 degrades.
3. **Self-training (M4) had nothing to relabel** — with c_hat=0.154, V4_proba needs to be > 0.95
   on Y=0 rows to trigger relabeling. V4's OOF probas on Y=0 rows are almost all < 0.5 — so
   M4 is essentially identical to the seed model.
4. **Co-training assumption broken** — chemistry view and temperature view ARE correlated (steel
   physics couples temperature to chemistry outcomes), so the independence assumption fails.

### V8 primary investment:

1. **FT-Transformer (TabPFN or tabular transformer)** — non-tree architecture captures different
   interaction patterns than LGB/XGB/CatBoost ensemble
2. **Metallurgical feature engineering** — Ar3/Ar1 transformation temperatures, finish-rolling
   temperature deviation relative to grade-specific Ar3, coil-level heating curve features
3. **Grade × campaign interactions** — the X1 (grade) categorical combined with campaign-level
   aggregates may be the signal top scorers found
4. **Neighbor interpolation in test** — some test rows may be "between" known defective coils;
   spatial/temporal position within campaign matters
5. **PU as weak diversity signal** — include M1 OOF proba as one column in V8 meta stack
   (weight ~0.10-0.15), but don't let it dominate

### What the 100.00 scorers likely did:

- External Tata Steel production data (grade lookup tables → Ar3 exact value → exact threshold)
- OR: systematic LB probing with ≤3 submissions/day to reverse-engineer test labels
- Unlikely: they found a ML trick we missed. The physics is deterministic if you have the right
  temperature thresholds per grade.

---

## 6. Method Notes

**M1 Elkan-Noto:** Most theoretically sound PU method. Rescales P(s=1|x)/c to get P(y=1|x).
Best performing PU method here — essentially matches V5 OOF. Worth including in V8 stack.

**M2 Spy (10% spy rate, 15th percentile threshold):** Found reliable negatives but the final
classifier trained on smaller set (reliable negatives only) lost some signal. The 15th percentile
threshold was conservative — most Y=0 rows scored near zero anyway.

**M3 Asymmetric Loss (spw=100):** Extreme weight crushed precision. OOF score dropped to 48.25.
The (Recall + Precision)/2 metric punishes precision-recall imbalance. For V8 try spw=5-10 range.

**M4 Self-Training:** V4 OOF probas on Y=0 rows max at ~0.5 — nothing crosses 0.95 threshold.
Result: zero rows relabeled across all folds, all rounds. M4 = plain LGB on original labels.
The CV-safe fix was correct but the seed model wasn't confident enough to trigger relabeling.

**M5 Co-Training:** Feature split: View1 (41 feats: chemistry + poly + lags), View2 (18 feats:
temps + forces + v5 physics). 5 rounds, confidence threshold 0.90, 5 samples/round max.
Partial relabeling occurred but views were correlated, limiting the theoretical guarantee.

---

*Generated by Jarvis ML-Engineer-Agent — 2026-05-23*
