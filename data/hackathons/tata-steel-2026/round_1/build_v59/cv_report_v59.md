# V59 CV Report — OpenFE Auto-Feature Engineering

**Date:** 2026-05-25
**Banked best:** V44 K=200 = 72.83 LB
**Architecture:** LGB+XGB+CAT → LR meta + Platt | rank-avg ensemble
**Features:** 51 V4 SHAP + 54 stand-FE + 50 OpenFE = 155
**CV:** StratifiedKFold(5, shuffle=True, seed=42)
**OpenFE:** n_estimators=2000, top-50 selected

---

## Gate Results

| Gate | Threshold | Value | Pass? |
|------|-----------|-------|-------|
| OOF F1@K=200 >= 0.391 | 0.391 | 0.353383 (TP=47) | FAIL |
| OpenFE in top-20 SHAP >= 5 | 5 | 8 | PASS |
| Spearman vs V44 >= 0.70 | 0.70 | +0.92766 | PASS |
| **Overall** | — | — | **FAIL (2/3)** |

---

## OOF Metrics

| Metric | Value | V53 reference |
|--------|-------|--------------|
| Meta OOF AUC | **0.87669** | ~0.883 |
| Rank-avg OOF AUC | **0.88296** | — |
| LGB OOF AUC | 0.88317 | — |
| XGB OOF AUC | 0.87417 | — |
| CAT OOF AUC | 0.87516 | — |
| **OOF F1@K=200** | **0.353383 (TP=47)** | **0.391 (TP=52)** |
| OOF F1@K=154 | 0.381818 (TP=42) | 0.400 (TP=44) |
| Best K sweep | K=100 F1=0.397590 TP=33 | K=98 F1=0.415 |

---

## K Sweep

| K | F1@K | TP |
|---|------|-----|
| 50 | 0.362069 | 21 |
| 75 | 0.382979 | 27 |
| 100 | 0.397590 | 33 |
| 130 | 0.387755 | 38 |
| 154 | 0.381818 | 42 |
| 170 | 0.381356 | 45 |
| 200 | 0.353383 | 47 |
| 230 | 0.344595 | 51 |
| 250 | 0.329114 | 52 |

---

## Per-Fold AUCs

| Fold | LGB | XGB | CAT | Time |
|------|-----|-----|-----|------|
| 1 | 0.82767 | 0.85331 | 0.82588 | 643s |
| 2 | 0.87160 | 0.87799 | 0.87993 | 806s |
| 3 | 0.87100 | 0.81562 | 0.84136 | 397s |
| 4 | 0.93325 | 0.92547 | 0.92846 | 563s |
| 5 | 0.92517 | 0.91021 | 0.90841 | 314s |
| **Mean** | **0.88574** | **0.87652** | **0.87681** | — |

---

## Spearman vs Reference OOFs

| Comparison | Spearman ρ |
|------------|------------|
| V59 vs V35 | +0.95119 |
| V59 vs V43 | +0.88916 |
| V59 vs V44 | +0.92766 |

---

## OpenFE Feature Penetration

OpenFE features in SHAP top-20: **8**/20
Gate (>=5): **PASS**

---

## Verdict

**GATES: 2/3 PASS**

OOF F1@K=200 = 0.353383 vs V53 benchmark 0.391: BELOW BENCHMARK

Recommended fire K: 100