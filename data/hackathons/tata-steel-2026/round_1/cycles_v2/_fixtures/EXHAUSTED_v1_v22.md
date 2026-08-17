# EXHAUSTED V1-V22 — Techniques Already Tried (Auto-Reject Contract)

Every research agent in cycles_v2/ receives this as a dedup contract. Any recommendation matching ANY line here is auto-rejected at synthesis time.

**Source:** Compiled from BUILD_V*_REPORT.md, approach.md files, CYCLE_LOG.md, FINAL_VERDICT.md, STRUCTURAL_FINDINGS.md, SUBMISSION_LOG.md, cycle1/track_a_eda_findings.md, cycle1/track_b_findings.md, build_v7/REPORT_PU.md, build_v7/TRACK_C_REPORT.md. All V1-V22 covered.

---

## Models tried

- LightGBM with scale_pos_weight=19.48 (V1) — OOF AUC 0.827
- LightGBM with fixed 250 rounds (no early stopping), is_unbalance removed (V2) — OOF AUC 0.850
- LightGBM with scale_pos_weight (V3, V4, V5) — incremental improvements only
- XGBoost (V3, V4, V5) — OOF AUC up to 0.8668 but no standalone breakthrough
- CatBoost with auto_class_weights=Balanced (V3, V4, V5) — OOF AUC up to 0.8890
- CatBoost single model with Optuna-tuned hyperparams depth=4, lr=0.014, l2=7.35, iter=300 (V13) — OOF 53.41
- CatBoost with AutoGluon-discovered config depth=6, lr=0.069, l2=2.15, max_ctr_complexity=4 (V22) — OOF 53.55, worse than V5
- LightGBM + XGBoost + CatBoost 3-model stacking with LR meta-learner (V3, V4, V5, V6 base for all subsequent builds)
- FT-Transformer (V6): d_token=96, 3 Pre-LN blocks, 4 attention heads, d_ffn=192, BCEWithLogitsLoss pos_weight=19.48, AdamW lr=1e-4, CosineAnnealingLR, early stopping patience=15. OOF AUC 0.8425 standalone — WEAKER than trees on 1352 rows
- FT-Transformer 90/10 blend with V5 tree stack (V6) — OOF 54.11, best of V6 variants but only +0.41 over V5
- TabPFN v2 (V9, V21) — BLOCKED by interactive auth requirement (tabpfn-client requires manual browser login). NOT a modeling exhaustion — auth-blocked, alternatives exist
- TabNet (V19): n_d=16, n_a=16, n_steps=3, gamma=1.5, mask_type=entmax, 5-fold, sample weights 19.5x. OOF AUC 0.8562 — -0.033 vs V5 baseline. ELIMINATED.
- NCA (Neighbourhood Components Analysis) + distance-weighted KNN (V20) — OOF AUC 0.7849, score 42.64. Dramatically worse. ELIMINATED.
- AutoGluon best_quality deep search with gate (V18) — highest val AUC CatBoost_r128 = 0.9008 (val AUC inflated by bag), OOF (R+P)/2 not better than V5
- Adversarial Validation (AV) reweighting via CatBoost (V16) — AV AUC 0.5354, OOF AUC 0.8719, delta -0.017 vs V5
- Per-grade specialist models (V15) — specialist grades [158, 159, 160, 161, 162]. OOF AUC 0.7978, score 52.85. WORSE.
- Hierarchical gated architecture: Stage-1 hard gate (X42 > 0.025067 OR X39 >= 169 → predict 0, eliminates 41% test rows), Stage-2 hot-zone-only stacking on 918 ungated rows (V8) — hot-zone training hurt AUC (0.8363), score 53.78
- Full-train stacking + gate-at-inference (V9): gate applied ONLY at prediction time, full 1352-row training preserved — OOF AUC 0.8771, score 53.71. Marginally better than V8 but doesn't beat V5

---

## Features engineered

### V1 baseline features (49 → 95)
- 9 ratio features: X13/X36, X10/X34, X13/X34, X30/X35, X13−X36, X10−X34, X13×X10, X36×X34, X13/X34
- 14 stage-wise cluster aggregations: mean/std/min/max for Cluster 1 (furnace), Cluster 2 (cooling/finishing), Cluster 3 (rolling core); cross-cluster ratio c3_mean/c2_mean; CV c3_std/c3_mean
- 6 per-row statistics: row_mean, row_std, row_skew, row_max, row_min, row_range across all 49 features
- 4 within-cluster z-scores: X13_c3_zscore, X10_c3_zscore, X36_c2_zscore, X34_c2_zscore
- 1 log transform: X35_log (heavy skew feature)
- 12 lag features: lag-1, lag-2, rolling-5-mean, delta-1 for X13, X10, X36
- KNN imputation (n_neighbors=5) fit on train only for X15 (160 missing) + X42 (31 missing) + X48 (13 missing)

### V2-V3 additional features
- IsolationForest meta-feature iso_score (unsupervised, fit on full train) — ranks 17th SHAP, included V2-V5
- SHAP top-30 feature selection from 96 engineered features (V3)
- 15 polynomial interaction features: degree-2 on top-5 SHAP features (X13_over_X36, X36, X14, X13_minus_X36, X16) — all cross/squared terms (V3+)

### V4 coil-neighbor temporal features (6 selected after SHAP)
- prev_5_defect_rate: CV-safe target-encoded defect rate of previous 5 coils (computed from fold training labels only, zero leakage)
- X13_lag1, X10_lag1, X36_lag1, X14_lag1 (extended from V1 lags)
- Rolling-window stats (window=5): mean, std, max of X13, X10, X36
- First differences: X13_diff1, X10_diff1, X36_diff1

### V5 physics features (8 new, all built)
- v5_ratio_X13_div_X14 — SHAP rank #1 (0.386), X13/coiling-temp normalization
- v5_ratio_X16_div_X14 — SHAP rank #2 (0.377), X16/coiling-temp normalization
- v5_FT_CT_ratio_X18_X14 — SHAP rank #11 (0.226), FT/CT ratio (X18=finishing temp confirmed at ~890°C=Ar3, X14=coiling temp confirmed)
- v5_T_finish_dev_Ar3_sq — quadratic Ar3 deviation using X18
- v5_grade_x_temp_dev — X11 (grade code) × Ar3 deviation
- v5_any_campaign_zero — binary: X34=0 OR X36=0 (campaign start signal, sep=2.0+)
- v5_log_X34, v5_log_X36 — log-scale campaign position counters
- SKIPPED (could not confidently ID columns): specific rolling force F/w, Ekelund lambda = sqrt(R×draft)/h_mean, 3-way Ekelund F/(T×w), coil_sequence_mod_100

### V5 column identification findings (physics knowledge, NOT features)
- X18 confirmed: finishing temperature ~890°C = Ar3 transformation temperature
- X17 confirmed: entry-to-finishing temperature ~1158°C
- X4, X5, X6, X14 confirmed: coiling temperatures (X6 shows +41.1°C defect separation)
- X11 confirmed: steel grade code (integer 24-40, 17 unique values, strong defect separation)
- X39 confirmed: grade code / roll schedule (integer 98-173, 49 unique values)
- X40 confirmed: small categorical 56-72, 13 unique values
- X34, X36 confirmed: roll campaign position counters (large integer 0-4380, 15.8% zeros = campaign start = defects)
- X35 confirmed: cumulative production counter (~10M range)
- X34/X36 zero signal: is_start_of_campaign (zeros = campaign-start defect signal sep=2.0+)

### V7 chemistry features (X42/X46 as composition proxies)
- X42_is_zero, X42_in_danger_band (V7 + V8)
- X42 > 0.025067 hard gate (exploits: max X42 among all 66 train defects = 0.025067, never exceeded)
- X39 >= 169 hard gate (exploits: grade >= 169 = zero defects in entire training set)
- These two gates eliminate 41% of test rows (138/339) with zero false-negative risk (V8, V9, V13)
- Within-X39-grade z-scores — CV-safe per fold (V11, V8)
- within-grade z-scores general for chemistry features (V11)

### V14 defect-taxonomy features (15 new, specifics not logged)
- Meta OOF AUC: 0.8751 (delta -0.0135 vs V5) — REGRESSED. Not listed in detail because they hurt.

### V16 features
- CatBoost native categorical handling for X11, X39, X40
- AV (adversarial validation) sample reweighting — AV AUC 0.5354 (train/test near-identical = good), OOF AUC -0.017 vs V5

### Anomaly detection meta-features (Cycle 1C — all exhausted)
- IsolationForest (M1_IF) score as meta-feature — OOF 53.09 standalone
- OneClassSVM (M2_OCSVM) score as meta-feature — OOF 52.44
- LOF (M3_LOF) score as meta-feature — OOF 52.63
- Mahalanobis distance (M4_Mah) score as meta-feature — OOF 52.84
- AutoEncoder reconstruction error (M5_AE) score as meta-feature — OOF 52.95
- PCA reconstruction error (M6_PCA) score as meta-feature — OOF 53.04
- 7-way LR ensemble of all above — OOF 52.82
- All AD methods exhausted: 2/15 hard defects caught at top-5% threshold (barely above random). Hard defects are genuinely "stealth" in X1-X49 space.

---

## Imbalance handling tried

- SMOTE(sampling_strategy=0.3, k_neighbors=3) applied only on training split inside CV folds (V2+) — validated zero leakage
- scale_pos_weight = 19.48 (LightGBM, V1, V2)
- is_unbalance = True (LightGBM V1 — REMOVED in V2 because it competed with SMOTE causing fold instability)
- class_weight=balanced (V3+)
- auto_class_weights=Balanced (CatBoost V3+)
- BCEWithLogitsLoss pos_weight=19.48 (FT-Transformer V6)
- Asymmetric loss via scale_pos_weight=100 (PU M3) — HURT: OOF dropped to 48.25 (extreme pos_weight crushes precision which is half the score)
- Sample weights ~19.5x in TabNet (V19)
- ADASYN — researched (Track B recommendation) but NOT implemented. NOT exhausted.
- Focal loss for LGB/XGB — researched but NOT implemented. NOT exhausted.

---

## Ensemble / stacking tried

- LR meta-learner on [LGB_oof, XGB_oof, CatBoost_oof] (V3+)
- Platt scaling via CalibratedClassifierCV(method='sigmoid', cv=5) on meta-learner output (V3+)
- Isotonic calibration — tested, Platt chosen (similar AUC on small n)
- 50/50 blend V6+V5 — OOF 52.91 (worse than both standalone)
- 90/10 blend V6 FT-Transformer + V5 tree stack — OOF 54.11 (best V6 variant, +0.41 over V5)
- V10 mean-blend of V5+V8+V9 — OOF 55.47, calibrated LB estimate 58.14 — **ACTUAL LB 47.00 (DISASTER, delta -8.47)**. Blending probabilities kills threshold calibration for the (R+P)/2 metric. DO NOT BLEND for this scoring metric.
- V13 single CatBoost (no blending) — OOF 53.41, back to V4-class performance
- V11 mean-blend of V11+V5+V9 — OOF 54.97, calibrated LB est 57.64 — NOT submitted (blend disaster rule)
- V12 multi-seed bagging + Optuna + blend V12+V5+V9 — OOF 55.02, calibrated 57.69 — NOT submitted
- AutoGluon ensemble (V18): best_quality, 40-min time limit, 50+ models tried via AG
- 80/20 V5+TabNet blend (V19) — OOF AUC 0.8870 vs V5 0.8886 (-0.0016); below safety threshold
- V5-only reference reuse (V19, V21) — confirmed V5 standalone is ceiling for tree+physics approach

---

## Threshold strategies tried

- Manual threshold selection at T=0.02 (V1, V2)
- Full OOF precision-recall sweep all unique thresholds (V2+)
- Score-aware exact-unique-threshold sweep: maximize (Recall+Precision)/2 directly on OOF (V3+)
- T_balanced: balanced precision/recall operating point (V4, archived)
- T_v2_style: threshold=0.001, high-recall posture (V4, archived)
- Bootstrap 95% CI computation on OOF score (V4+ standard), seed=42, n=200/1000 subsamples
- V4 actual vs OOF calibration delta: +2.67 applied to all LB estimates V4 onward

---

## CV strategies tried

- 5-fold StratifiedKFold (seed=42) — used throughout V1-V22, no variation attempted

---

## Pseudo-label / semi-supervised tried

- V4: pseudo-negatives from test rows where proba < 0.05 added as synthetic Y=0 train rows — Meta AUC dropped 0.884 → 0.851, score OOF 54.31 → 52.4. REGRESSED, dropped immediately.
- PU learning (Cycle 1D) — all 5 methods below V5 baseline:
  - M1 Elkan-Noto reweighting (c=0.154, rescale P(s|x)/c → P(y|x)) — OOF 53.12 (best PU method, -0.29 vs V5)
  - M2 Spy technique (10% spy rate, 15th percentile threshold) — OOF 51.15
  - M3 Asymmetric loss scale_pos_weight=100 — OOF 48.25 (extreme weight crushed precision)
  - M4 Self-training CV-safe — OOF 47.98 (V4 OOF probas on Y=0 never exceed 0.95, zero rows relabeled across all folds)
  - M5 Co-training 2 views (chemistry + temperature) — OOF 49.47 (views too correlated, independence assumption fails)
  - 6-way PU meta blend — OOF 52.54 (pulls V5 DOWN to 52.54)
- Label propensity c ≈ 0.154 estimated (Elkan-Noto 2008) — HIGH label noise confirmed (~361 hidden positives), but knowing this doesn't help identify WHICH Y=0 rows are hidden defects

---

## Anomaly detection tried (all exhausted — Cycle 1C)

- IsolationForest as standalone classifier (M1_IF): OOF AUC 0.7899, score 53.09
- OneClassSVM (M2_OCSVM): OOF AUC 0.6039, score 52.44
- LOF Local Outlier Factor (M3_LOF): OOF AUC 0.5679, score 52.63
- Mahalanobis distance (M4_Mah): OOF AUC 0.7636, score 52.84
- AutoEncoder reconstruction error (M5_AE): OOF AUC 0.7284, score 52.95
- PCA reconstruction error (M6_PCA): OOF AUC 0.6952, score 53.04
- All 6 AD meta-scores as features in 7-way LR ensemble: OOF AUC 0.8674, score 52.82
- Verdict: Hard defects are "stealth" — invisible in X1-X49 feature space. AD methods cannot rescue them. **EXHAUSTED.**

---

## Architectures tried (summary)

- LightGBM (gradient boosted trees) — ceiling ~0.885 AUC with current features
- XGBoost (gradient boosted trees) — ceiling ~0.867 AUC with current features
- CatBoost (gradient boosted trees) — ceiling ~0.889 AUC with current features
- LGB+XGB+CatBoost stack with LR meta + Platt calibration — meta ceiling ~0.889 AUC, score ceiling ~54.3 OOF
- FT-Transformer 3-block d_token=96 (V6) — too few rows (1352), early stops epoch 17-42, global OOF AUC 0.8425
- TabNet (V19) — n_d=16, n_a=16, n_steps=3 — OOF AUC 0.8562, -0.032 vs V5
- TabPFN v2 (V9, V21) — auth-blocked (interactive login required, license)
- AutoGluon best_quality (V18) — discovers CatBoost variants, best val AUC 0.9008 on bag (inflated), no OOF improvement
- Hierarchical gating: hard rules (X42 + X39) as preprocessing stage (V8, V9, V13) — gate works, improves precision but hot-zone-only training hurts AUC
- NCA + KNN (V20) — AUC 0.7849, score 42.64. Eliminated.
- Per-grade specialist ensemble (V15) — AUC 0.7978, score 52.85. Eliminated.

---

## Tactics tried

- Score-aware threshold optimization (all V3+)
- Bootstrap CI on OOF (n=200 to 1000, seed=42)
- Per-feature SHAP top-30 selection (V3+)
- Optuna hyperparameter search on LGB (V3: 20 trials, score ceiling 53.18 confirmed)
- Multi-seed bagging + full Optuna search (V12)
- AutoGluon hyperparameter discovery (V18)
- KNN imputation (fit-on-train, apply to test)
- Physics column identification via value-range analysis + published Tata Steel / ISIJ International HSM literature
- Swansea EngD thesis (Latham 2025) column cross-reference — X13=RM_model_error, X41=FM_model_error hypothesis (HIGH confidence), but anonymized unit thresholds don't directly translate
- 6 published papers on HSM defect ML reviewed (KPLS paper PMC10346850, CTGAN+CatBoost HSLA crack paper PMC12348153, plus 4 others)
- Test-Time Augmentation (TTA) with N(0, 0.01) noise (V19) — delta ~0.0006, negligible. Eliminated.
- AV (adversarial validation) reweighting (V16) — AV AUC 0.535 means train/test near-identical, reweighting had no effect

---

## Anti-patterns confirmed (DO NOT REPEAT)

- **Mean-blend across builds (V10: ACTUAL LB 47.00 vs OOF calibrated estimate 58.14 = -8.47 LB)**. Blending probabilities from independently-calibrated models destroys threshold calibration for the (R+P)/2 score. Never blend for this metric.
- **Pseudo-label test negatives (V4)**: adding test rows with proba < 0.05 as pseudo Y=0 regressed OOF from 54.31 → 52.4. Adding redundant negatives makes precision math harder.
- **K-means cluster aggregations on raw sensors**: anti-pattern documented in V5 research. Statistical cluster features (mean/std/min/max per cluster) add noise without domain signal. V5 showed these plateau quickly.
- **Naive PCA dimensionality reduction**: anti-pattern. PCA reconstruction error tried in AD (M6_PCA), underperforms supervised models. Naive PCA as input compression never tested but expected to hurt.
- **Early stopping on noisy AUC at small n (V1)**: With 13 val positives per fold, AUC variance per step = 0.017 — early stopping fired at round 1 in some folds (model barely trained). Fixed in V2 with fixed 250 rounds. Do not re-introduce early stopping unless fold n_positive > 30.
- **Asymmetric loss pos_weight=100 (V7 M3 PU)**: extreme positive weight crushes precision. Since score = (R+P)/2, destroying precision hurts as much as missing recall. For this metric, optimal pos_weight range is 15-25.
- **Blending FT-Transformer with 50/50 weight**: 50/50 V6+V5 blend OOF 52.91, worse than V5 alone (53.70). Only the 90/10 blend (heavily tree-dominant) marginally helps.
- **Per-grade specialist training (V15)**: specialists overfit on tiny grade subsets (some grades have <5 defects), global OOF collapses to 0.798 AUC.
- **Defect-taxonomy-driven features (V14)**: 15 new features with specific physics taxonomy, meta AUC -0.014 vs V5. Domain-typed features not automatically better.
- **Co-training with correlated views (V7 M5 PU)**: steel physics couples temperature to chemistry — view independence assumption fails, relabeling noise propagates to training set.
- **Self-training when seed model insufficient (V7 M4 PU)**: if base model probas on Y=0 rows never exceed 0.95, zero rows are relabeled and the method reduces to plain supervised. Not a bug — the model's calibrated uncertainty is genuinely high.

---

## Known hard defect profile

7 most-precarious positive cases (V4 OOF proba, sorted ASC):
- CoilID 1495 — v4_oof_proba 0.01429 (barely above V4 threshold 0.01428)
- CoilID 913 — v4_oof_proba 0.01487
- CoilID 1499 — v4_oof_proba 0.01707
- CoilID 473 — v4_oof_proba 0.01757
- CoilID 624 — v4_oof_proba 0.01921
- CoilID 1436 — v4_oof_proba 0.02036
- CoilID 72 — v4_oof_proba 0.02694

These 7 coils have near-identical sensor profiles to non-defect coils in the current feature space (V5 AUC 0.8886, AD methods show 2/15 partially anomalous at top-5% threshold). Any new feature suggestion MUST specifically argue why it would separate THESE coils.

10 hardest false positives (Y=0 with highest V4 OOF proba):
- CoilID 689 — v4_oof_proba 0.778
- CoilID 642 — v4_oof_proba 0.698
- CoilID 247 — v4_oof_proba 0.627
- CoilID 189 — v4_oof_proba 0.624
- CoilID 279 — v4_oof_proba 0.616

These 10 non-defect coils look extremely defect-like in the current feature space. Any new approach claiming to reduce FPs must show why these specific CoilIDs would be correctly predicted negative.

---

## Mathematical ceiling (verified)

- V4 actual LB = 56.98 ⇒ test set has ~22 true defects (back-solved)
- To reach LB 80: AUC ~0.94+ required
- To reach LB 90: AUC ~0.97+ required
- Best OOF AUC achieved (V5 meta): 0.8886
- Gap to honest LB 80: AUC +0.055 minimum — requires new feature signal, not modeling tricks
- Public/private 50/50 split confirmed (HackerEarth T&C) — top-100 scorers may be overfit to public split only; offline evaluation reveals final rank

---

*Compiled: 2026-05-23. V1-V22 builds + 4 cycle tracks exhaustively sourced.*
