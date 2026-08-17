# V34 Approach — Tata Steel Hot Rolling Defect Detection

**Date:** 2026-05-24
**Status:** COMPLETE — DO NOT FIRE (gates failed, est LB 50.40 < V4 banked 56.98)

---

## 1. Architecture

V34 is V4's 3-model stacking ensemble (LGB + XGB + CatBoost → LR meta + Platt calibration)
augmented with V33's 54 per-stand residual features.

**Base models (V3/V4 canonical hyperparameters):**
- LightGBM: `is_unbalance=True`, `learning_rate=0.02`, `num_leaves=15`, `min_child_samples=5`,
  `subsample=0.7`, `colsample_bytree=0.7`, `n_estimators=300`
- XGBoost: `scale_pos_weight=19.5`, `learning_rate=0.03`, `max_depth=4`,
  `n_estimators=300`, `subsample=0.7`, `colsample_bytree=0.7`
- CatBoost: `auto_class_weights=Balanced`, `learning_rate=0.03`, `depth=4`, `iterations=300`

**Meta layer:** LogisticRegression(C=1.0) + Platt sigmoid calibration (cv=5)

**CV:** StratifiedKFold(5, shuffle=True, seed=42), SMOTE(sampling_strategy=0.3) inside each fold

---

## 2. Feature Set (105 features = 51 V4 backbone + 54 stand-FE)

**V4 backbone (51 SHAP-selected features):**
Loaded from `build_v4/train_v4.parquet`. Includes:
- 30 SHAP-selected raw X features (X13, X36, X14, X16, etc.)
- 15 polynomial interactions on top-5 features
- IsolationForest anomaly score
- Row statistics (skew, range, etc.)
- Cluster-ratio features (c3_over_c2_mean, etc.)
- 6 coil-neighbor features (lag-1/2, rollmean5, prev5_defect_rate)

**V33 stand-FE (54 new features, fold-isolated medians):**
- 6 signed temperature residuals (X4-X9 minus train-fold median)
- 6 absolute temperature residuals
- 5 signed force residuals (X29-X33 minus train-fold median)
- 5 absolute force residuals
- Cumulative process deviation (z-weighted sum)
- Max abs z-deviation across stands
- Cumulative force deviation (raw)
- Max force/temp deviations
- Worst-deviant stand index + magnitude (temp/force)
- 5 inter-stand temperature gradients
- X35 bimodal decomposition (3 features: is_high flag, log1p, z-score)
- X35 flag × cumulative force interaction
- 5 temperature × force residual cross-products
- Temperature span (X4-X9), entry temp, exit temp
- Force escalation ratio (F5/F1)
- 5 log-force columns

**CRITICAL AP-1 compliance:** All stand setpoint medians/stds computed on TRAIN FOLD ONLY inside
the CV loop. Test transformation uses all-train setpoints. NO `pd.concat([train, test])` anywhere.

---

## 3. Rebalancing Decision

Both SMOTE and BBSE variants were run and compared empirically.

| Variant | Meta OOF AUC |
|---|---|
| A: SMOTE sampling_strategy=0.3 | 0.8595 |
| B: BBSE w1=9, w0=0.579 (no SMOTE) | 0.8622 |
| Winner | **B (BBSE)** by +0.0027 |

**BBSE empirical finding:** BBSE wins by a narrow margin (+0.0027 meta AUC). This answers the
Ratnesh-Jarvis question: "does BBSE w1=9 on top of SMOTE compound and over-correct?" — yes, combining
them hurts. Clean BBSE (no SMOTE) is marginally better. However the delta is within noise range at
66 positives, so this is not a decisive result.

---

## 4. Critical Finding: Stand-FE Features Not Lifting V4 Stack as Expected

**V33 ablation result (reproduced):** Stand-FE features add +0.015 AUC to single LGB.
**V34 result:** Stand-FE features do NOT translate to a meta-level lift on the 3-model stack.

Root cause analysis:
1. **V4's original 0.8837 is not reproducible.** Reproducing V4 exactly (same features, same params,
   same seed) gives meta OOF AUC 0.8676, not 0.8837. The original V4 solution.ipynb had internal
   stochastic state differences. The 0.8837 was real (saved in oof_v4.parquet) but cannot be matched
   from scratch.
2. **V34 (0.8622) vs reproduced V4 without stand-FE (0.8676):** Stand-FE actually HURTS by -0.005.
   This contradicts the +0.015 V33 single-LGB ablation, because:
   - At 66 positives, meta-level gains are dominated by fold variance, not feature quality.
   - SMOTE generates 308 positives from 53 real ones — the stand-FE residuals based on fold medians
     have different distributions for SMOTE-synthetic vs real samples (median computed on real data,
     applied to synthetic samples → distribution mismatch).
   - XGB and CAT (which had the largest stand-FE gains in theory) actually dropped vs the reproduced
     V4 baseline.

**Conclusion:** V33's stand-FE features are validated on single-LGB with BBSE (no SMOTE). They are
*not* validated in the SMOTE+stacking context at this dataset size. The V4 stacking ceiling (~0.87-0.88
meta AUC in reproduction) is a function of the 66-positive hard tail, not of the feature space.

---

## 5. Results

| Metric | V34 (Var B winner) | V4 (banked) |
|---|---|---|
| LGB OOF AUC | 0.8526 | 0.8615 |
| XGB OOF AUC | 0.8586 | 0.8668 |
| CAT OOF AUC | 0.8586 | 0.8756 |
| Meta OOF AUC | 0.8622 | 0.8837 |
| Bootstrap 95% CI | [0.8418, 0.8838] | — |
| OOF (R+P)/2 | 47.7273 | 54.31 |
| Estimated LB | 50.40 | 56.98 |
| Delta vs V4 LB | -6.58 | — |

**Gates: 4/5 FAIL. DO NOT FIRE.**

---

## 6. Path Forward (V35)

V34 confirms that the stacking architecture has hit its ceiling (~0.87-0.88 reproducible meta AUC).
The original V4's 0.8837 was a lucky draw from the stochastic distribution.

To actually beat V4's LB of 56.98, V35 needs:

1. **Physics-informed features** (original V4 roadmap): Map X1-X49 to actual hot-rolling process
   variables. Published HSM literature suggests X4-X9 = stand temperatures, X29-X33 = stand forces.
   Physics-grounded ratios (force/width, FT deviation from Ar3, draft schedule) can separate the
   "hard 7" defects that trees can't catch.

2. **Larger ensemble**: Add more diverse base models (ExtraTrees, Ridge regression on stand-FE,
   linear SVM) to the stack for meta diversity rather than 3 correlated GBDT models.

3. **Fix the stand-FE + SMOTE mismatch**: Apply stand-FE AFTER SMOTE (so synthetic samples get
   correct residuals), or use BBSE without SMOTE consistently.

The V4 banked LB (56.98) remains the ceiling for the current architecture. Submit V4 for now;
do not submit V34 (est LB 50.40 < 56.98).
