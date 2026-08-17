# Approach — Defect Detection in Hot Rolling
## Tata Steel AI Hackathon 2026, Round 1

**Team / Author:** Ujjawal Shrivastav
**Date:** 2026-05-22

---

## Problem

Predict which coils of hot-rolled steel will develop defects (Y=1) based on 49 anonymized process parameters. The evaluation criteria is extremely strict: Recall=100% (catch every defect) AND Precision>90% (less than 10% false alarms).

---

## Why This Is Hard

The dataset has only 66 defective coils out of 1352 (4.88%). At this imbalance ratio, there is a mathematical ceiling on simultaneous high precision and high recall. To catch every defect (Recall=100%), the model must set a very low confidence threshold — which flags many non-defects too, collapsing precision to near the base rate (~5%). Our engineering goal was to sharpen the decision boundary so the model can distinguish defects with higher confidence.

---

## Data Understanding

Through exploratory data analysis, we identified:
1. **Top 10 features by discriminative power:** X13, X10, X32, X30, X36, X31, X15, X34, X35, X39. Top 4 have Cohen's d > 1.0 (strong effect sizes).
2. **3 physical stages:** Features cluster into rolling stand parameters (Cluster 3), cooling/finishing parameters (Cluster 2), and furnace/background parameters (Cluster 1). Defects arise when rolling force (C3) rises while cooling (C2) drops.
3. **Sequential production order:** CoilID is a production sequence number. X13 shows lag-1 autocorrelation of 0.69 — consecutive coils share process state. 55% of defect coils have a neighboring defect within 10 coils.
4. **X15 missingness:** 160/1352 rows missing — not a defect signal (chi-square p=0.51). Imputed using KNN.

---

## Approach

### Feature Engineering (49 → 95 features)
- **KNN Imputation:** Fit on training set, applied to test. No data leakage.
- **Ratio features:** X13/X36 (rolling force / cooling flow) encodes the physical defect mechanism in one number.
- **Stage aggregations:** Mean, std, min, max per cluster captures process-level state.
- **Lag features:** Lag-1, lag-2, rolling-5-mean for top features (valid because CoilID is sequential).
- **Within-cluster z-scores:** Amplifies individual feature anomaly relative to cluster behavior.

### Model
- LightGBM with scale_pos_weight=19.5 (inverse class ratio)
- 5-fold Stratified Cross-Validation
- Early stopping on AUC (up to 1000 rounds)

### Threshold Selection
- Swept all possible thresholds on out-of-fold predictions
- Selected threshold=0.02 which achieves OOF recall=0.924 (catches 61/66 defects)
- No threshold achieves the target (Recall=1.0 AND Precision>90%) with the current model
- Final submission uses threshold=0.02 (prioritizing recall as the primary constraint)

---

## Results

| Metric | Value | Notes |
|--------|-------|-------|
| OOF AUC | 0.827 | Strong ranking signal |
| OOF Recall @ thr=0.02 | 0.924 | Catches 61/66 defects |
| OOF Precision @ thr=0.02 | 0.078 | 724 false positives |
| Full criteria met? | No | Precision too low |

---

## Limitations & Next Steps

The fundamental gap is **precision**. With 66 positive examples, the model cannot learn a boundary precise enough to achieve 90%+ precision while catching all defects. The next version will address this with:
1. **SMOTE oversampling** to give the model 5-10x more synthetic defect examples
2. **Anomaly detection ensemble** (Isolation Forest) to use unsupervised signal
3. **Model stability fixes** (some folds trained trivial models — parameter tuning needed)
