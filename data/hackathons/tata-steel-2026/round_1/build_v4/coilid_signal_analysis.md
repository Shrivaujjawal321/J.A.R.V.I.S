# CoilID Sequential Signal Analysis

**Date:** 2026-05-22

## Summary

- CoilID range: 1-1691, NO GAPS. Train/test perfectly interleaved (zero overlap).
- Lift = **5.28x** (chi2 p=0.000000, highly significant)
- P(defect | prev=defect) = 0.2576 vs baseline 0.0488
- Lag-2 lift: 2.79x
- Consecutive defect pairs: 17

## Verdict

**STRONG — coil-neighbor features are PRIORITY 1**

Build lag-1, lag-2, rolling-defect-rate features. CV-safe target encoding.

## Why This Matters

Train and test CoilIDs are perfectly interleaved — every test coil has train coils as
immediate neighbors in production order. The coil state (temperature, chemistry, roll wear)
persists between consecutive coils, creating a strong autocorrelation signal that generic
cross-sectional features completely miss.

## CV Safety Note

`prev_defect_rate` MUST be computed inside each CV fold using only that fold's training labels.
For test predictions: use the full training set Y to compute neighbor features.
