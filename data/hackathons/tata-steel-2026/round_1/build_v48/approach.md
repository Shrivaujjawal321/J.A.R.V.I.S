# V48 Approach — Pseudo-Label Augmentation

## Problem Statement

V44 consensus (K=200, LB 72.83) uses 5 paradigms + V4_154 anchor. Test prevalence is ~45% but real train is only 4.9% positive. Every model trained on real-train systematically under-predicts because it's calibrated to a 5% prior. The R2 research recipe (CAST 2024 + DARP) addresses this via confident pseudo-labeling.

## Core Idea

The 132 vote=6/6 CoilIDs in V44 consensus are the ones where all 5 paradigms AND the V4_154 anchor ALL agreed they are defective. This is the highest possible confidence signal from a 6-way committee. Use them as pseudo-Y=1 training examples to:

1. Shift augmented prevalence from 4.9% to 13.3% (closer to test's ~45%)
2. Give models more positive examples to learn from without real label acquisition
3. Produce a 6th paradigm with a genuinely different learning signal for V49 consensus

## Method

### Pseudo-Label Generation
- Source: V44 consensus vote computation (v35 + v39 + v40 + v41 + v43 + V4_154 anchor)
- Threshold: vote == 6 (unanimous agreement across all 6 sources)
- Count: exactly 132 CoilIDs (verified at runtime)
- Pseudo-Y = 1, sample_weight = 0.6

### Augmented Training Set
- Real train: 1352 rows (66 positive, 1286 negative), weight=1.0
- Pseudo: 132 rows (132 positive), weight=0.6
- Total: 1484 rows, 198 positives (13.3% prevalence)

### Fold Integrity (CRITICAL)
- StratifiedKFold is computed on REAL train rows only (1352 rows, stratified on real Y)
- Each fold: train = real train fold rows + ALL 132 pseudo rows
- Val = REAL train rows only (real labels, no pseudo contamination)
- OOF AUC computed ONLY on real-train labels
- StandSetpoints fit on REAL train fold rows (pseudo excluded from setpoint computation)
- Test setpoints fit on full real train (not augmented)

This ensures:
- OOF AUC is a valid measure of generalization on real data
- No validation contamination from pseudo rows
- Pseudo rows are exclusively a training signal

### Architecture
Identical to V35: 9-model rank-average ensemble
- LGB1: is_unbalance, lr=0.02, leaves=15
- LGB2: is_unbalance, lr=0.025, leaves=20, depth=5
- XGB1: scale_pos_weight=19.48, lr=0.03, depth=4
- XGB2: scale_pos_weight=19.48, lr=0.025, depth=5
- CatBoost: auto_class_weights=Balanced, lr=0.03, depth=4
- RF: n_est=500, class_weight=balanced
- ET: n_est=500, class_weight=balanced
- HGB: max_iter=300, lr=0.03, class_weight=balanced
- TabICL: n_estimators=5 (or LGB3 fallback)

Features: V4 51 SHAP-selected + 54 stand-FE = 105 total (identical to V35)

### sample_weight application
All models receive `sample_weight` in `.fit()`. HGB, RF, ET natively support it. TabICL: try with weight, fall back without if TypeError. LGB and XGB: standard `sample_weight` parameter.

## What V48 is NOT
- V48 is NOT a standalone submission candidate — its OOF K-score is lower because there are only 66 real positives but we're thresholding at K=200.
- V48 IS a new paradigm for V49 consensus. Its test_proba_v48 ranks test coils with a different calibration signal (prevalence-corrected).
- V48's value is: does it agree or disagree with V44's vote=6 cluster on the BORDERLINE coils (vote=3/4/5)?

## Expected V49 Impact
- V48 adds a 7th paradigm (pseudo-label-aware)
- Coils where V48 strongly predicts positive but V44 vote was 3-4 = NEW positive signal
- Coils where V48 strongly predicts negative but V44 vote was 5-6 = confidence-correcting signal
- V49 should use V48 as an additional vote source with K_ANCHOR tuned to ~170-181

## Risks
See cv_report_v48.md section "Top-3 risks" for detailed analysis.

## Files
- `train_v48.py` — this pipeline
- `pseudo_labels.json` — 132 vote=6 CoilIDs
- `oof_v48.parquet` — OOF probas on real-train (1352 rows)
- `test_proba_v48.parquet` — test probas (339 rows)
- `cv_report_v48.md` — full CV metrics
- `_gate_results.json` — machine-readable gate outcomes
