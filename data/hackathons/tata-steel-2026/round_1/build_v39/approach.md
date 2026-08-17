# V39 Approach — iter35-equivalent (CoilID + 6 derivatives)

## Lineage

V39 replicates Ratnesh-Jarvis's iter35 paradigm (one of 4 in his 72.71 LB consensus union).

## What iter35 Does

Adds 7 CoilID-derived features to the V4 51-feature base and trains a single LightGBM with
scale_pos_weight=18.9 (no SMOTE, no BBSE):

| Feature | Rationale |
|---------|-----------|
| `CoilID` (raw) | Linear coil-sequence trend |
| `CoilID_sq` | Quadratic — captures non-linear aging/wear |
| `CoilID_log` | Compresses high-ID range, emphasizes early coils |
| `CoilID_gt_med` | Regime split: before/after median (fold-isolated) |
| `CoilID_gt_p75` | Regime split: top-quartile coil-age flag (fold-isolated) |
| `CoilID_sin(2π/1700)` | Cyclic production run pattern |
| `CoilID_cos(2π/1700)` | Cyclic production run pattern (quadrature) |

Threshold flags (gt_med, gt_p75) computed from fold-train CoilID stats only — same
leakage-safe pattern as V33's fold-isolated stand setpoints.

## Why CoilID Might Help

Per V4 discovery: `P(defect | prev=defect) = 0.258` (5.28× lift). CoilID encodes
temporal position in the production sequence — roll wear, thermal drift, and periodic
maintenance cycles all correlate with CoilID. The cyclic sin/cos pair captures any
periodic maintenance schedule with period ≈ 1700 coils.

Ratnesh's iter35 OOF AUC = 0.9412 vs V4's 0.8837. The gap is large — suggests
CoilID features are capturing strong temporal structure.

## Configuration

- scale_pos_weight = 19.48 (1286/66, pure class-weight balancing)
- 5-fold StratifiedKFold, seed=42 (aligns with V4/V33/V34/V35 for consensus)
- LGB: lr=0.03, leaves=63, depth=6, n_est=700, subsample=0.8, colsample=0.7
- Total features: 58 (51 V4 + 7 CoilID)

## Role in Consensus Pipeline

V39 = Paradigm 4 candidate for Ratnesh-style 4-paradigm consensus union.
Other paradigms: V4 (meta-stacking), V35 (9-model rank-avg), V37 (AutoGluon).
Diversity target: Spearman(V39, V4_meta) < 0.85.

## Results

- OOF AUC: 0.8634
- Bootstrap 95% CI: [0.8118, 0.9118]
- Spearman vs V4_meta: 0.7549
- OOF (R+P)/2: 50.0713 (K=223)
- Est LB: 52.74
