# V48 CV Report — Pseudo-Label Augmentation (R2 CAST/DARP)

## Run Summary

| Field | Value |
|-------|-------|
| Date | 2026-05-24 |
| Architecture | V35 9-model rank-avg (LGB×2, XGB×2, CatBoost, RF, ET, HGB, TabICL) |
| Augmentation | 132 pseudo-positive rows (vote=6/6 from V44 consensus), weight=0.6 |
| Folds | 5-fold StratifiedKFold, seed=42, val=real-train-only |
| OOF AUC (real-train only) | **0.8742** |
| V35 OOF AUC (reference) | 0.91 (approx, from gate) |
| Bootstrap 95% CI | [0.8360, 0.9069] |
| Mean fold std | 0.0247 |

## Gate Results (3/3 PASS)

| Gate | Threshold | Actual | Status |
|------|-----------|--------|--------|
| OOF AUC (real-train only) | >= 0.87 | 0.8742 | PASS |
| Spearman vs V35 OOF | < 0.95 | 0.8989 | PASS |
| Pseudo-positive count | == 132 | 132 | PASS |

## Augmentation Effect

| Dataset | Rows | Positives | Prevalence |
|---------|------|-----------|------------|
| Real train | 1352 | 66 | 4.9% |
| Pseudo rows | 132 | 132 | 100% (all pseudo-Y=1) |
| Augmented total | 1484 | 198 | 13.3% |
| Test (estimated) | 339 | ~150 | ~45% |

Prevalence gap: 4.9% (real train) → 13.3% (augmented) — still below test ~45%, but substantial improvement.

## Per-Fold AUC (real-val only)

| Fold | LGB1 | LGB2 | XGB1 | XGB2 | CatBoost | RF | ET | HGB | TabICL |
|------|------|------|------|------|----------|----|----|-----|--------|
| 1 | 0.8602 | 0.8470 | 0.8497 | 0.8629 | 0.8620 | 0.8479 | 0.8511 | 0.8605 | 0.8590 |
| 2 | 0.8902 | 0.8872 | 0.8758 | 0.8835 | 0.8880 | 0.8894 | 0.8583 | 0.8677 | 0.8797 |
| 3 | 0.8150 | 0.8381 | 0.8459 | 0.8345 | 0.8405 | 0.8219 | 0.7869 | 0.8126 | 0.8447 |
| 4 | 0.8797 | 0.9015 | 0.8833 | 0.8913 | 0.8809 | 0.8768 | 0.8824 | 0.8878 | 0.9048 |
| 5 | 0.8677 | 0.8650 | 0.8943 | 0.8979 | 0.8973 | 0.8747 | 0.9021 | 0.8599 | 0.8961 |

Note: Fold 3 is the hard fold (only 13 positives in val, fold std high) — same pattern seen in V35.

## Per-Model OOF AUCs

| Model | OOF AUC | Fold Std |
|-------|---------|----------|
| LGB1 | 0.8626 | 0.0259 |
| LGB2 | 0.8683 | 0.0238 |
| XGB1 | 0.8692 | 0.0189 |
| XGB2 | 0.8729 | 0.0230 |
| CatBoost | 0.8735 | 0.0203 |
| RF | 0.8586 | 0.0242 |
| ET | 0.8566 | 0.0391 |
| HGB | 0.8574 | 0.0247 |
| TabICL | 0.8738 | 0.0224 |
| **Rank-avg ensemble** | **0.8742** | 0.0247 |

## Spearman Diversity vs Paradigms (test-level)

| Paradigm | Spearman ρ |
|----------|------------|
| V35 (OOF-level) | 0.8989 |
| V35 (test-level) | 0.9226 |
| V39 (test-level) | 0.7964 |
| V40 (test-level) | 0.7898 |
| V41 (test-level) | 0.9125 |

V48 is meaningfully different from V39/V40 (ρ~0.79) and has reasonable diversity from V35 (ρ=0.90 OOF). The pseudo-labeling has successfully shifted the prediction surface — confirmed by sub-0.95 Spearman gate.

## SHAP Top-5 Features (LGB1 representative)

| Rank | Feature | Mean |SHAP| |
|------|---------|------|
| 1 | poly_X13_over_X36_X16 | 0.5871 |
| 2 | X13_over_X36 | 0.5232 |
| 3 | poly_X13_minus_X36^2 | 0.2374 |
| 4 | X36 | 0.2071 |
| 5 | iso_score | 0.1772 |

SHAP assessment: X13/X36 ratio features dominate — same as V35 baseline. Pseudo-label augmentation did NOT distort feature importance ranking. The model learned from the augmented positives without changing which features drive the predictions. iso_score entering top-5 is new (was lower in V35) — consistent with pseudo rows potentially having a signal pattern the real positives don't fully capture.

## OOF Score at K

| K | OOF (R+P)/2 |
|---|-------------|
| 200 | 43.33 |
| Best (K=299) | 46.24 |

Note: OOF K-score is expected to be lower than V35's because the OOF calibration here is evaluated against real-train labels only (66 positives vs 200 threshold = mismatch). The actual value of V48 is its contribution to V49 consensus, not standalone K-threshold. OOF calibration vs LB delta analysis deferred to V49 pipeline.
