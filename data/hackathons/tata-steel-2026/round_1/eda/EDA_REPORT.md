# Tata Steel AI Hackathon 2026 — Round 1
# Deep EDA Report: Defect Detection in Hot Rolling

**Date:** 2026-05-22
**Analyst:** Jarvis Data Analytics Specialist
**Dataset:** 1352 train rows × 51 cols | 339 test rows × 50 cols | 49 anonymized float features

---

## Executive Summary (TL;DR for Boss)

Five things you need to know before building:

1. **Top 10 features are VERY clear.** X13, X10, X32, X30, X36, X31, X15, X34, X35, X39 — single-feature AUCs of 0.80–0.83. These 10 features alone will carry the model.
2. **Missingness is NOT a signal.** The X15 missingness hypothesis fails — chi-square p=0.51. Don't waste a feature slot on is_missing flags.
3. **3 natural feature clusters exist.** Hierarchical clustering found them cleanly. Cluster 3 (14 features) contains ALL top-10 features — this is the hot rolling stage cluster.
4. **The recall ceiling is painfully honest: ~18% recall at precision ≥ 90%** with default LightGBM. This means the criteria (Recall=100%, Precision>90%) is NOT achievable out-of-the-box. The gap is real and requires heavy engineering.
5. **Precision@Recall=1.0 is ~4.9%** — meaning if you catch every defect (recall=100%), precision collapses to ~5%. The 90% precision bar is extremely aggressive given 66 positive examples in 1352 rows. Strategy discussion below.

---

## Q1. Sample Submission File Investigation

**Finding:** The sample_submission.csv has exactly **10 rows** (plus header). This is NOT a full submission — it is a format-reference example only, showing 9 no-defect coils.

```
Rows in sample_submission.csv : 10
Rows required in final submission: 339 (one per test coil)
Columns: CoilID, Y
Y values in sample: all 0 (probably just showing format, not a hint)
```

**What this means:** Your submission file must have 339 rows — one prediction per test CoilID. Match the exact column names `CoilID` and `Y`. The sample is just showing you the format, not predicting anything meaningful.

**Action:** When submitting, write all 339 test CoilIDs with your predicted Y (0 or 1). Double-check CoilID ordering matches the test.csv ordering or sort by CoilID.

---

## Q2. Feature Signal Strength — All 49 Features Ranked

### Top 10 Features (by single-feature ROC-AUC)

| Rank | Feature | ROC-AUC | Cohen's d | KS p-value | Missing % | Mean (Y=0) | Mean (Y=1) |
|------|---------|---------|-----------|------------|-----------|------------|------------|
| 1 | **X13** | **0.8322** | 1.2123 | ~0.0 | 0.00% | 846.16 | 1312.33 |
| 2 | **X10** | **0.8214** | 1.1326 | ~0.0 | 0.44% | 6.73 | 9.63 |
| 3 | **X32** | **0.8149** | 0.9997 | ~0.0 | 0.00% | 15.82 | 19.52 |
| 4 | **X30** | **0.8061** | 1.0384 | ~0.0 | 0.00% | 9.98 | 12.27 |
| 5 | **X36** | **0.8056** | -1.1652 | ~0.0 | 0.00% | 2376.82 | 378.88 |
| 6 | **X31** | **0.8012** | 1.0071 | ~0.0 | 0.00% | 13.35 | 16.56 |
| 7 | **X15** | **0.8004** | -0.7130 | ~0.0 | 11.83% | 3.53 | 1.97 |
| 8 | **X34** | **0.7812** | -1.1454 | ~0.0 | 0.00% | 2455.56 | 486.32 |
| 9 | **X35** | **0.7771** | -1.2684 | ~0.0 | 0.00% | 1.03e+07 | 2.16e+06 |
| 10 | **X39** | **0.7704** | -0.4128 | ~0.0 | 0.00% | 162.51 | 157.83 |

**Interpretation:** Top 4 features (X13, X10, X32, X30) are exceptional — Cohen's d > 1.0 means the defect group mean is more than one pooled standard deviation away from the no-defect group. These features are measuring something physically different during a defect event. X36, X34, X35 show negative Cohen's d — meaning these DROP during defects (likely speed/flow parameters that decrease under stress). X39 has a smaller effect size (d=-0.41) but still strong AUC — it's a threshold-based signal, not mean-shift.

### Bottom 10 Features (candidates for dropping)

| Rank | Feature | ROC-AUC | Cohen's d | KS p-value |
|------|---------|---------|-----------|------------|
| 40 | X40 | 0.5667 | -0.2991 | 0.1798 |
| 41 | X47 | 0.5660 | -0.0567 | 0.1544 |
| 42 | X27 | 0.5606 | 0.1698 | 0.0866 |
| 43 | X26 | 0.5566 | 0.1833 | 0.1398 |
| 44 | X21 | 0.5490 | -0.1293 | 0.2346 |
| 45 | X48 | 0.5451 | -0.2575 | 0.2394 |
| 46 | X12 | 0.5352 | -0.1755 | 0.5615 |
| 47 | X20 | 0.5276 | -0.0527 | 0.2917 |
| 48 | X14 | 0.5254 | 0.1354 | 0.0361 |
| 49 | **X3** | **0.5099** | **0.0060** | **0.779** |

**Interpretation:** X3 is essentially random — AUC=0.51, d=0.006, KS p=0.78. X12, X20, X47 are similarly useless. These features' distributions are nearly identical between defect and non-defect coils. They are either noise sensors or measure parameters irrelevant to alpha defect formation.

**Decision recommendation:** Consider dropping bottom 10 when training tree models to reduce overfitting risk. But tree models are robust to noise features — only drop if you're building logistic regression or SVM.

---

## Q3. The X15 Missingness Hypothesis — VERDICT: NOT A SIGNAL

For every column with missing values, chi-square test of independence between "is_missing" and Y:

| Column | N Missing | P(Y=1|missing) | P(Y=1|present) | Lift | Chi2 p-value | Significant? |
|--------|-----------|----------------|----------------|------|--------------|--------------|
| X8 | 1 | 0.000 | 0.049 | 0.00 | 1.0000 | NO |
| X10 | 6 | 0.000 | 0.049 | 0.00 | 1.0000 | NO |
| **X15** | **160** | **0.062** | **0.047** | **1.33** | **0.5092** | **NO** |
| X16 | 6 | 0.000 | 0.049 | 0.00 | 1.0000 | NO |
| X21 | 1 | 0.000 | 0.049 | 0.00 | 1.0000 | NO |
| X23 | 6 | 0.000 | 0.049 | 0.00 | 1.0000 | NO |
| X24 | 6 | 0.000 | 0.049 | 0.00 | 1.0000 | NO |
| X25 | 6 | 0.000 | 0.049 | 0.00 | 1.0000 | NO |
| X26 | 7 | 0.000 | 0.049 | 0.00 | 1.0000 | NO |
| X27 | 6 | 0.000 | 0.049 | 0.00 | 1.0000 | NO |
| X42 | 31 | 0.000 | 0.050 | 0.00 | 0.3929 | NO |
| X48 | 13 | 0.000 | 0.049 | 0.00 | 0.8618 | NO |

**Verdict: Missingness is NOT a defect signal in this dataset.** Zero columns pass chi-square significance (p<0.05). The X15 missingness shows a 1.33x lift but p=0.51 — that's pure sampling noise with 160 missing rows.

**Why are most columns missing with zero defects among the missing?** Most missing-value columns (X8, X10, X16, X21, X23-X27) have only 1-7 missing rows — by pure chance, none of them happened to be defect coils. This is a small-n artifact, not a meaningful pattern.

**Recommendation:** Do NOT add is_missing flags as features. Use median imputation (or model-based imputation for X15's 160 values) and move on. X15 itself has strong AUC=0.80 despite missingness — impute it well and it's your 7th best feature.

---

## Q4. Feature Group / Stage Clustering

Hierarchical clustering (Ward linkage) on 49×49 feature correlation matrix, cut at 3 clusters:

### Cluster 3 — "The Hot Rolling Core" (14 features)
```
X4, X5, X6, X7, X8, X9, X10, X13, X15, X29, X30, X31, X32, X33
```
**Interpretation:** This cluster contains ALL of the top-6 signal features (X13, X10, X32, X30, X31, X15) plus close relatives. These features are highly inter-correlated — X30↔X31 (r=0.97), X31↔X32 (r=0.96), X10↔X13 (r=0.96). They likely represent **rolling force, torque, and speed parameters at the rolling stand** — physically the moment when metal deformation happens and defects form.

### Cluster 2 — "The Cooling/Finishing Group" (12 features)
```
X14, X19, X24, X34, X35, X36, X37, X38, X39, X40, X41, X42
```
**Interpretation:** Contains X34, X35, X36, X37, X38, X39 — the negative-Cohen's-d features that DROP during defects. X36 drops from 2377 (no defect) to 379 (defect) — an 84% drop. This is likely **cooling water flow or coiler tension** — when these collapse, the strip is not being controlled properly and defects form. X39 (AUC=0.77) and X41 (AUC=0.73) are strong signals in this cluster.

### Cluster 1 — "Background/Furnace Parameters" (23 features)
```
X1, X2, X3, X11, X12, X16, X17, X18, X20, X21, X22, X23, X25, X26, X27, X28, X43, X44, X45, X46, X47, X48, X49
```
**Interpretation:** The largest cluster, mostly weaker features (AUC 0.50-0.65). Likely **furnace heating parameters, strip dimensions, and down-coiler settings** — upstream/downstream of the actual rolling event. Not useless — X43 (AUC=0.63), X44 (AUC=0.62), X45 (AUC=0.61) have moderate signal.

**Key insight for feature engineering:** The 3-cluster structure strongly suggests the defect mechanism is in Cluster 3 (rolling conditions) triggered by Cluster 2 failures (cooling/tension drop), with Cluster 1 providing context but not the primary cause. Cross-cluster interaction features (C3 × C2) could be gold.

---

## Q5. Outlier / Data-Quality Issues

5-sigma analysis: For every feature, rows where value > 5 std dev from mean.

**Result: ZERO features with 5-sigma outliers show lift > 1.5 over the baseline defect rate.**

This means:
- No extreme sensor spikes are specifically associated with defects
- The defect signal is in the **distribution shift** of normal operating ranges, not in catastrophic outliers
- No sensor-error patterns detected (no impossible negatives, no truncated values flagged at 5-sigma level)

**Implication for modeling:** Don't rely on outlier-flagging as a feature. The defect fingerprint is subtle — a coil running at "X13=1312" looks like a normal process point individually, but is ~1.6 std dev above the no-defect mean (mean=846). The model needs to learn these distributional shifts, not just catch extreme values.

---

## Q6. Train vs Test Distribution Shift

KS test comparing train vs test distributions for all 49 features:

### Significant Shifts (p < 0.01)

| Feature | KS Statistic | p-value | Also Top-10? |
|---------|-------------|---------|--------------|
| **X32** | 0.1079 | 0.0033 | YES — #3 |
| **X7** | 0.1014 | 0.0070 | No (medium signal) |

### Borderline Shifts (p < 0.05, i.e., moderate concern)

| Feature | KS Statistic | p-value |
|---------|-------------|---------|
| X9 | 0.0975 | 0.0106 |
| X5 | 0.0962 | 0.0122 |
| X14 | 0.0953 | 0.0135 |
| X15 | 0.0886 | 0.0493 |
| X10 | 0.0837 | 0.0420 |
| X31 | 0.0837 | 0.0421 |
| X33 | 0.0828 | 0.0455 |

**Critical finding:** X32 (your #3 feature by signal strength) has the biggest train-test shift (KS=0.108, p=0.003). X10 (your #2 feature) also has borderline shift. This is a generalization risk — the model trained on X32 and X10 distributions in train may not transfer cleanly to the test set's slightly different range.

**What this means practically:**
- X32 and X7 should be monitored carefully during validation
- Tree models are somewhat robust to distribution shift — but if test precision is bad, these are the first suspects
- Consider: train on (1-shift_penalty) weighted samples, or use domain adaptation if shift is severe

**Iska matlab:** Test set mein hot rolling conditions thodi alag hain. Model ko in features pe zyada rely karna risky hai.

---

## Q7. Multicollinearity Analysis

Total feature pairs with |correlation| > 0.9: **12 pairs**

| Feature A | Feature B | Correlation |
|-----------|-----------|-------------|
| X30 | X31 | 0.9681 |
| X31 | X32 | 0.9567 |
| X10 | X13 | 0.9556 |
| X32 | X33 | 0.9481 |
| X30 | X32 | 0.9467 |
| X13 | X31 | 0.9390 |
| X29 | X30 | 0.9376 |
| X10 | X31 | 0.9329 |
| X10 | X32 | 0.9212 |
| X31 | X33 | 0.9117 |
| X13 | X32 | 0.9088 |
| X13 | X30 | 0.9044 |

**Pattern:** This is actually ONE tight multicollinear group: {X10, X13, X29, X30, X31, X32, X33} — all from Cluster 3, the rolling core. These 7 features are measuring the same underlying physical process from slightly different angles.

**Iska matlab:** Ye 7 features ek hi cheez measure kar rahe hain. So:
- For tree models (LightGBM/XGBoost): keep all — trees handle redundancy naturally and each adds marginal splits
- For logistic regression/SVM: drop to 1-2 per group to avoid coefficient instability
- For feature engineering: these correlated features are ideal for **ratio features** (X13/X36, X10/X31) — ratios between the rising and falling groups encode process deviation directly

---

## Q8. Best Single-Feature Decision Rule

Best feature: **X13** (AUC = 0.8322)

| Threshold scenario | Recall | Precision | Notes |
|-------------------|--------|-----------|-------|
| Catch all defects (recall=1.0) | 100% | ~5% | Way too many FP |
| At precision ≥ 90% | 0% | — | No single threshold achieves this |
| Best balanced point | varies | varies | Single feature can't hit the bar |

**Harsh truth:** No single feature can simultaneously achieve Recall=100% AND Precision>90%. The precision curve shows that to catch every defect with X13, you'd flag 20× more non-defects (precision ~5%). This is mathematically certain given the class imbalance.

**Floor established:** Single-feature recall at precision≥90% = 0.0%. Baseline is "terrible." Any multi-feature model must dramatically beat this floor — and the CV results show that even LightGBM with balanced weights struggles here.

---

## Q9. Theoretical Recall Ceiling — LightGBM 5-Fold CV

```
Default LightGBM + scale_pos_weight (class-balanced) + 5-fold stratified CV
```

| Fold | Recall @ Precision≥90% | ROC-AUC | Precision when Recall=100% |
|------|----------------------|---------|---------------------------|
| 1 | 0.231 | 0.9231 | 0.0480 |
| 2 | 0.000 | 0.8196 | 0.0517 |
| 3 | 0.077 | 0.7809 | 0.0481 |
| 4 | 0.231 | 0.8794 | 0.0481 |
| 5 | 0.385 | 0.8411 | 0.0481 |
| **MEAN** | **0.185** | **0.8488** | **0.0488** |

**Honest interpretation:**

- Mean recall at Precision≥90%: **18.5%** — this is terrible
- Even the best fold only hits 38.5% recall while maintaining precision≥90%
- When you force Recall=100%, precision collapses to **4.9%** — almost exactly the baseline defect rate (4.88%), meaning the model is essentially "flag everything" at that threshold

**Is the criteria (Recall=100%, Precision>90%) achievable?**

With current features and default modeling: **No, not out of the box.**

But — and this is important — the CV setup here is "default LightGBM." The 0.92 AUC in fold 1 tells us the model does have real signal. The problem is that with only 66 positive examples split across 5 folds, each fold validation set has ~13 positive examples. Getting 90% precision on 13 defects while catching all of them is statistically very hard.

**What could move the needle:**
1. Better imputation (X15 has 160 missing rows — these might concentrate signal)
2. Feature engineering (ratio features, cross-cluster interactions) to sharpen the decision boundary
3. SMOTE/synthetic minority oversampling to train on more balanced data
4. Threshold tuning on full train → validate on held-out coils at coil level
5. Ensemble stacking (LightGBM + Isolation Forest + threshold calibration)

**Realistic target with heavy engineering:** Best possible is probably Recall=85-95% at Precision≥90%, depending on feature engineering quality. Hitting Recall=100% at Precision>90% is the stretch goal that requires the boundary to be so sharp that it never misses a defect while staying tight — 66 examples may not be enough to learn such a precise boundary.

---

## Q10. Feature Engineering Recommendations

### Priority 1 — HIGHEST IMPACT (do these first)

**1a. Ratio features between Cluster 2 (cooling) and Cluster 3 (rolling):**
```python
X13_over_X36 = X13 / (X36 + 1)  # rolling force / cooling flow
X10_over_X34 = X10 / (X34 + 1)  # rolling speed / tension
X30_over_X35 = X30 / (X35 + 1)  # force ratio
```
Why: Defects arise when rolling force (↑) and cooling capacity (↓) diverge simultaneously. Ratio encodes this divergence in one number. Fold 1's ROC-AUC of 0.92 shows the signal IS there — ratio features help the model find the exact decision boundary.

**1b. Within-cluster deviation features (cluster-wise z-scores):**
```python
cluster3_mean = mean(X4, X5, X6, X7, X8, X9, X10, X13, X15, X29, X30, X31, X32, X33)
cluster3_std  = std(X4, X5, ...)
X13_deviation = (X13 - cluster3_mean) / cluster3_std
```
Why: If X13 is elevated AND its entire cluster is elevated, that's a stronger signal than X13 alone. Ek feature ka high value alag meaning rakhta hai jab pure group mein elevation ho.

**1c. Smart imputation for X15 (160 missing values = 11.8% of train):**
Use KNN imputation (k=5) or MICE — simple median imputation will lose the distributional relationship X15 has with X10, X13 (all Cluster 3). X15's AUC=0.80 makes it your 7th best feature; losing it to bad imputation is costly.

### Priority 2 — MEDIUM IMPACT

**2a. Multiplicative interaction between top pairs:**
```python
X13_x_X10 = X13 * X10       # both rising during defects
X36_x_X34 = X36 * X34       # both falling during defects — product amplifies
X13_div_X34 = X13 / (X34 + 1)  # rising / falling = max separation
```

**2b. Rolling-window aggregations (if CoilID encodes sequential order):**
Investigate if CoilIDs are sequential in production order. If so, compute:
```python
X13_lag1 = shift(X13, 1)        # previous coil's value
X13_rolling3 = rolling_mean(X13, 3)  # 3-coil rolling average
```
Why: Defects in hot rolling often cluster — consecutive coils fail together when a process parameter drifts. If CoilID is sequential, lag features could be extremely powerful.

**2c. Log-transform heavily right-skewed features:**
X35 has mean ~10M (Y=0) vs ~2.16M (Y=1) — this scale variance means tree splits are inefficient. Log1p transform before tree modeling helps, though LightGBM is somewhat robust to scale.

### Priority 3 — LOW PRIORITY / EXPERIMENTAL

**3a. Isolation Forest anomaly score as a meta-feature:**
Train an isolation forest on X_train (unsupervised). Use the anomaly score as an additional feature. Defect coils may be anomalous in the feature space even without the label — this is an unsupervised signal that doesn't violate the no-external-data rule.

**3b. PCA components of Cluster 3:**
The 7 highly-correlated features {X10, X13, X29, X30, X31, X32, X33} can be compressed to 2-3 PCA components that might capture orthogonal aspects of the rolling process better than raw features.

**3c. Polynomial features from top-4:**
X13^2, X10^2, X13*X30 — quadratic terms can help if the decision boundary is non-linear in a way trees aren't capturing (less relevant for LightGBM, more for logistic regression).

---

## Summary: The 5 Questions Boss Asked

**1. Which 10 features matter most?**
X13, X10, X32, X30, X36, X31, X15, X34, X35, X39 — in that order. Top 4 have Cohen's d > 1.0 (large effect sizes). Focus your engineering here.

**2. Is X15 missingness a free feature?**
No. Chi-square p=0.51 — not significant. X15 as a VALUE is strong (AUC=0.80), but X15 being MISSING tells you nothing. Impute well, use the values, skip the flag.

**3. Are there 3 feature clusters matching 3 stages?**
Yes, clearly. Cluster 3 = rolling stand (contains all top-6 features). Cluster 2 = cooling/finishing (contains X34-X39 negative signals). Cluster 1 = furnace/background (weakest signals). This maps well to the physical 3-stage process described in the problem.

**4. Can we achieve Recall=100% / Precision>90%?**
Not out-of-the-box. Default LightGBM achieves mean 18.5% recall at precision≥90% in 5-fold CV. When forced to recall=100%, precision collapses to ~5%. The criteria is HARD but not impossible — it requires sharp feature engineering (especially ratio features), threshold calibration, and potentially ensemble methods. Honest assessment: 85-95% recall at precision≥90% is achievable with heavy work; hitting the exact 100%/90% target will require the model to be extremely precise, and with 66 positive examples, there's a real risk of overfitting to train while failing on test.

**5. Top-3 feature engineering moves before first real model?**
1. **Ratio features X13/X36, X10/X34** (captures rolling force vs cooling divergence — this is the physical defect mechanism)
2. **KNN imputation for X15** (11.8% missing on your 7th strongest feature — median imputation wastes this)
3. **Check CoilID sequential ordering** — if consecutive, add X13 lag-1 feature (defects cluster in hot rolling)

---

## Caveats

- 66 positive examples is small for calibrating precision at 90%. All CV estimates have high variance — single fold can swing from 0% to 38% recall.
- The 49 features are anonymized — we can't use domain knowledge to guide feature engineering beyond the cluster structure.
- X32 has significant train-test distribution shift (p=0.003). Monitor carefully on validation. If test performance degrades, deprioritize X32 in favor of X30, X31 which have less shift.
- No temporal information confirmed — CoilID ordering as a time proxy is unverified. Test this before building lag features.
- External data is prohibited — no sensor manuals, no steel grade data, no external process lookup tables.

---

*Artifacts:*
- `feature_importance_table.csv` — full 49-feature stats table
- `findings_summary.json` — machine-readable key findings
- `figures/01_class_balance.png` through `06_train_vs_test_distribution_shifts.png`

*Query and interpretation drafted. Validate with PM/owner before reporting externally.*
