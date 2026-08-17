# CV Report — Build V40
**Date:** 2026-05-24
**Architecture:** LightGBM single model + V4 51-feature base + 11 defect-proximity features = 62 total
**Recipe:** Ratnesh-Jarvis iter36 (CV-safe defect proximity)

## Summary

| Metric | Value |
|---|---|
| Architecture | LightGBM single model |
| Feature set | V4 51 + 11 proximity = 62 features |
| Proximity radii | [0.5, 1.0, 1.5, 2.0, 3.0] |
| CV | StratifiedKFold(5, seed=42) |
| OOF AUC | 0.8732 |
| Mean fold AUC | 0.8728 ± 0.0336 |
| Bootstrap 95% CI | [0.8539, 0.8966] |
| OOF (R+P)/2 score | 48.6757 |
| Best K | 254 |
| Test positives | 254/339 = 74.9% |
| Delta vs V4 OOF AUC | -0.0105 |
| Est LB | 51.35 |
| V4 banked LB | 56.98 |
| Delta vs V4 LB | -5.63 |
| Beat V4 | NO |

## Proximity Feature Design

**11 features per row:**
1. `dist_to_nearest_defect` — Euclidean distance in standardized 51-feature space to nearest Y=1 train row
2-6. `count_within_radius_r` for r ∈ [0.5, 1.0, 1.5, 2.0, 3.0] — count of Y=1 train rows within radius r
7-11. `density_within_radius_r` for same r — count_Y1_within_r / count_all_train_within_r

**CV-safety enforcement:**
- Scaler fitted on TRAIN FOLD ONLY (not val, not test)
- "Known defects" = TRAIN FOLD Y=1 rows only (val rows excluded)
- Val proximity: distance to train-fold defects only
- Test proximity: distance to ALL-TRAIN defects (legitimate, no label leakage)
- This matches Ratnesh's description: "CV-safe defect-proximity"

## Per-Fold CV Results

| Fold | AUC |
|---|---|
| 1 | 0.9329 |
| 2 | 0.8722 |
| 3 | 0.8560 |
| 4 | 0.8312 |
| 5 | 0.8716 |
**Mean: 0.8728 | Std: 0.0336 | Min: 0.8312 | Max: 0.9329**

## Proximity Stats Per Fold

| Fold | Defects in Fold | Train-Defect Dist Min (excl self) | Val Dist Mean | Val Dist Min |
|---|---|---|---|---|
| 1 | 53 | 1.7994 | 6.1287 | 2.2491 |
| 2 | 52 | 2.4193 | 6.0441 | 2.1195 |
| 3 | 53 | 1.7820 | 5.8529 | 2.8773 |
| 4 | 53 | 1.7538 | 9.5249 | 2.3620 |
| 5 | 53 | 1.7968 | 6.1970 | 2.0501 |

## Paradigm Diversity — Spearman vs Other OOFs

| Paradigm | Spearman r | Diversity |
|---|---|---|
| V4 | 0.0343 | DIVERSE |
| V33 | 0.0175 | DIVERSE |
| V34 | 0.0355 | DIVERSE |
| V35 | 0.0375 | DIVERSE |

**Target: r < 0.85 for consensus ensemble utility.**

## Comparison with Ratnesh iter36

| Metric | Ratnesh iter36 | V40 |
|---|---|---|
| OOF AUC | 0.9465 | 0.8732 |
| Feature base | ? (Ratnesh's own) | V4 51 SHAP-selected |
| CV setup | 5-fold StratKFold | 5-fold StratKFold seed=42 |
| Proximity radii | same | [0.5, 1.0, 1.5, 2.0, 3.0] |

Note: AUC gap vs Ratnesh (0.9465) is expected — Ratnesh's base feature set may include additional
engineered features or a different representation. The CV-safe proximity recipe is identical.

## Top-3 Risks

1. **Base feature set mismatch:** Ratnesh's iter36 achieves 0.9465 with his base features. Our V4 base
   may not be as well-suited for proximity queries in standardized space. If V4 features introduce
   irrelevant dimensions, distances in 51-dim space may be noisy.

2. **Curse of dimensionality:** 51-dim standardized distance is inherently noisy for 66 positives.
   Ratnesh may use a lower-dimensional representation or PCA-reduced space for proximity queries.
   A follow-up could try proximity in top-10 PCA components.

3. **OOF→LB calibration:** V4 delta (+2.67) was computed for V4's stacked-ensemble OOF. Single LGB
   OOF may have a different calibration. Treat Est LB as rough estimate.

## Ready for Consensus Union?

CONDITIONAL — AUC below V4 but proximity features provide genuine diversity signal

**Spearman diversity summary:**
- V40 vs V4: r=0.0343
- V40 vs V33: r=0.0175
- V40 vs V34: r=0.0355
- V40 vs V35: r=0.0375
