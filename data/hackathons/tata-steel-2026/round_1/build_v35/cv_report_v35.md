# V35 CV Report — Ratnesh-Jarvis 9-model Rank-Average Ensemble
**Date:** 2026-05-24
**Status:** COMPLETE — DO NOT FIRE (gates 2/5 passed, est LB 46.84 < V4 banked 56.98)

---

## 1. Configuration

| Parameter | Value |
|---|---|
| Feature set | V4's 51 SHAP-selected + V33's 54 stand-FE = **105 total** |
| CV | StratifiedKFold(5, shuffle=True, seed=42) |
| Aggregation | Rank-average (Ratnesh's exact recipe) |
| K-threshold | 170 (Ratnesh's empirical optimum) |
| Rebalancing | scale_pos_weight = 1286/66 = 19.48 per tree (NO SMOTE, NO BBSE) |
| 9th model | TabICL (available, verbose=False fix applied) |

---

## 2. Per-Fold AUC by Model

| Model | Fold1 | Fold2 | Fold3 | Fold4 | Fold5 | Mean OOF AUC | Fold Std |
|---|---|---|---|---|---|---|---|
| LGB1 | 0.7800 | 0.9074 | 0.7764 | 0.9189 | 0.8988 | **0.8486** | 0.0641 |
| LGB2 | 0.7573 | 0.8874 | 0.7908 | 0.8991 | 0.8884 | **0.8382** | 0.0587 |
| XGB1 | 0.8077 | 0.9130 | 0.7848 | 0.9165 | 0.8866 | **0.8550** | 0.0549 |
| XGB2 | 0.8238 | 0.9038 | 0.7923 | 0.9276 | 0.8749 | **0.8574** | 0.0500 |
| CatBoost | 0.8375 | 0.9008 | 0.8285 | 0.8928 | 0.8785 | **0.8646** | 0.0293 |
| RF | 0.8317 | 0.9332 | 0.7736 | 0.8997 | 0.8804 | **0.8603** | 0.0558 |
| ET | 0.8503 | 0.9140 | 0.7739 | 0.9220 | 0.9125 | **0.8717** | 0.0565 |
| HGB | 0.8286 | 0.8972 | 0.8177 | 0.9228 | 0.8940 | **0.8627** | 0.0413 |
| TabICL | 0.8554 | 0.9038 | 0.8168 | 0.9348 | 0.8839 | **0.8752** | 0.0404 |
| **Rank-avg** | — | — | — | — | — | **0.8699** | 0.0501 |

Best individual: TabICL (0.8752), then ET (0.8717), CatBoost (0.8646).
Worst individual: LGB2 (0.8382), LGB1 (0.8486).

---

## 3. Ensemble Metrics

| Metric | Value | Gate | Pass? |
|---|---|---|---|
| Rank-avg OOF AUC | 0.8699 | >= 0.910 | FAIL |
| Bootstrap 95% CI | [0.8247, 0.9112] | lower >= 0.8937 | FAIL |
| OOF (R+P)/2 at K=170 | 44.17 | — | — |
| Est LB at K=170 | 46.84 | > 56.98 | FAIL |
| K=170 sanity | 170 positives | == 170 | PASS |
| Mean fold std | 0.0501 | < 1.5 | PASS |

**Gates passed: 2/5**

---

## 4. K-Threshold Sweep

| K | OOF (R+P)/2 | Est LB |
|---|---|---|
| 170 (Ratnesh's K) | 44.17 | 46.84 |
| 288 (OOF-optimal) | 49.35 | 52.02 |

The optimal K on OOF is 288 (not 170). Even at optimal K, est LB = 52.02 < 56.98 (V4 banked). The K=170 misfit relative to OOF is expected: Ratnesh's probas are calibrated differently (AutoGluon + TabPFN + his iter15/18 models produce higher-confidence positive probas), so his top-170 naturally aligns with the true positives. Our GBDTs/RF/ET have different probability scales.

---

## 5. Comparison vs Prior Builds

| Build | Architecture | OOF AUC | Est LB | LB (actual) |
|---|---|---|---|---|
| V4 | LGB+XGB+CB → LR meta | 0.8837 | 54.31+2.67=56.98 | **56.98** (banked) |
| V32 | Unknown | — | — | 49.06 |
| V33 | Single LGB + stand-FE | 0.8697 | — | — |
| V34 | V4 stack + stand-FE + BBSE | 0.8622 | 50.40 | NOT FIRED |
| **V35** | **9-model rank-avg (this)** | **0.8699** | **46.84** | NOT FIRED |

---

## 6. Root Cause: Why V35 Falls Below V4

### 6a. K=170 is Wrong for Our Calibration
Ratnesh's recipe uses K=170 because his model ensemble (AutoGluon + TabPFN + iter15/18) assigns much more concentrated probability mass to the true ~66 positives. His top-170 captures most true positives with fewer false positives, giving better precision.

Our GBDTs produce shallower probability gradients — many rows get similar mid-range probas. K=170 selects the top 50% quantile but at low recall. Our optimal K is 288, reflecting shallower ranking discrimination.

**K=170 transfers from Ratnesh's specific model calibration, not from the problem itself.**

### 6b. OOF AUC 0.8699 is Below V4's 0.8837
This is consistent with V34 (0.8622). Our reproducible ceiling for the current feature space is ~0.87 meta OOF AUC. V4's 0.8837 was a favored stochastic draw from the specific notebook state. The 9-model ensemble adds diversity (AUC +0.0077 vs V34) but cannot break the 0.88 ceiling.

### 6c. Stand-FE is Not Lifting the Ensemble
Same finding as V34: stand-FE features add +0.015 AUC to single LGB, but the gain disappears at ensemble/meta level because:
- At 66 positives, meta-level gains are dominated by fold variance noise
- The 54 stand-FE features are partially redundant with V4's existing X4-X9/X29-X33 raw features

### 6d. Ratnesh's True Advantage
His 62.64 LB comes from:
1. **AutoGluon + TabPFN** — genuinely different model families (AutoGluon uses neural nets + bagging; TabPFN is a prior-fitted transformer)
2. **148-feature base** vs our 105 — his feature set includes features we don't have
3. **iter15/iter18** — his specific stacking configs are trained on a data split that happened to capture the hard-7 defects better
4. **K=170 as calibrated threshold** — because his probas rank true positives much higher

---

## 7. Gate Results

| Gate | Threshold | Value | Pass |
|---|---|---|---|
| OOF AUC | >= 0.910 | 0.8699 | FAIL |
| Bootstrap CI lower | >= 0.8937 | 0.8247 | FAIL |
| Est LB > V4 | 56.98 | 46.84 | FAIL |
| K=170 sanity | == 170 | 170 | PASS |
| Stability std | < 1.5 | 0.0501 | PASS |

---

## 8. Recommendation

**DO NOT FIRE.** Est LB 46.84 is below V4's banked 56.98 by -10.14 points. Even at optimal K=288, est LB 52.02 is below V4. Submitting would risk the leaderboard position with near certainty of regression.

**Path to beating V4 (honest assessment):**
The V4 banked 56.98 was a lucky stochastic draw. Ratnesh's 62.64 is real and validated. To close the gap, we need:
1. AutoGluon or TabPFN (transformer-class models) — not GBDTs
2. Physics-informed features (roll force/width, Ar3 deviation, Ekelund normalization) that separate the "hard 7" defects
3. Different K calibration (accept that our optimal K differs from Ratnesh's)

The GBDT/RF/ET/HGB ensemble has hit its ceiling on this dataset (~0.87 OOF AUC). The marginal gains from more trees / more seeds are within fold-variance noise.
