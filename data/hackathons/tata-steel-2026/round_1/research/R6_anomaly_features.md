# R6: Anomaly Detection Scores as Ensemble Features
**Tata Steel Defect Detection — Research Brief**
**Date:** 2026-05-24
**LB baseline:** 72.83 (V39/V40 range implied). Target: 80+.
**Research scope:** Using unsupervised anomaly detectors (PyOD suite) as feature generators inside a supervised LightGBM/XGBoost pipeline on 49-D tabular data with severe class imbalance.

---

## 1. Quick Verdict

Adding 3-5 anomaly detector scores as supervised features is **well-supported by both theory and competition practice**. The right detectors for our problem (49 features, small-N tabular, imbalanced) are:

**Ranked recommendation (best first):**

| Rank | Detector | Rationale | CV-safe? |
|------|----------|-----------|----------|
| 1 | **ECOD** | Non-parametric, zero hyperparams, top ADBench perf on tail anomalies, extremely fast, interpretable | Yes |
| 2 | **IsolationForest** | Proven baseline, scikit-learn native, handles high-D well, already in V2 — extend properly | Yes |
| 3 | **LOF** | Statistically best shallow method for LOCAL anomalies per ADBench; density-based, captures cluster-boundary defects | Yes |
| 4 | **COPOD** | Copula-based, handles correlated features explicitly (which our 49 rolling-process features are), deterministic, zero hyperparams | Yes |
| 5 | **Autoencoder recon error** | Train on Y=0 only; captures nonlinear manifold deviations; best complement to the 4 above (different signal) | Yes (with care) |

**Skip for now:**
- **ABOD**: O(N^3) — prohibitively slow; PyOD has approximations but still noisy on small N
- **DeepSVDD**: ADBench showed "surprisingly worse than shallow methods" due to hypersphere collapse, hyperparameter sensitivity, and mode collapse without label guidance. Not worth the training cost here.

---

## 2. Algorithm Details

### 2.1 ECOD — Empirical CDF-based Outlier Detection

**Paper:** Zhang et al., TKDE 2022 (originally arXiv 2201.00382)
**Core idea:** For each feature dimension d, estimate the left-tail CDF F_L(x_d) and right-tail CDF F_R(x_d) empirically. Outlier score = -log(min(F_L, F_R)) aggregated across all d. No distributional assumption.

**Why it fits our problem:**
- Defects in rolling steel = out-of-spec process readings = tail events in individual sensor dimensions
- Zero hyperparameters — no contamination rate to guess, no kernel bandwidth to tune
- O(N log N) per feature — fastest possible for N rows, 49 features
- ADBench NeurIPS 2022: top performer on "tail anomaly" datasets (which is exactly what manufacturing defects are — rare process exceedances)
- Limitation: if defects are NOT in tails (i.e., defects appear mid-distribution on all features), ECOD degrades. Mitigated because steel rolling defects are by definition process exceedances.

**PyOD API:**
```python
from pyod.models.ecod import ECOD
clf = ECOD()
clf.fit(X_train)
scores = clf.decision_function(X_test)  # higher = more anomalous
```

### 2.2 COPOD — Copula-Based Outlier Detection

**Paper:** Li et al., ICDM 2020
**Core idea:** Models joint distribution via empirical copula (captures correlations between features), then estimates tail probability in the copula space. The copula transform maps marginals to Uniform[0,1] via empirical CDF first, then examines joint tail probability.

**Why it fits our problem:**
- Our 49 features are rolling-process parameters: speed, temperature, thickness, force, tension — ALL correlated by physics. ECOD ignores feature correlations; COPOD captures them.
- Best ADBench ROC-AUC across 30 benchmark datasets (one study's ranking)
- Deterministic (no randomness), fast, interpretable
- Limitation: assumes linear copula structure; if nonlinear coupling is dominant, COPOD may miss it. Still fine as a supplementary score.

**PyOD API:**
```python
from pyod.models.copod import COPOD
clf = COPOD()
clf.fit(X_train)
scores = clf.decision_function(X_test)
```

### 2.3 IsolationForest

**Core idea:** Random recursive partitioning. Anomalies are isolated in fewer splits → short path length → high anomaly score.

**Already in V2** (used as a meta-feature naively). Proper usage:
- `decision_function()` gives signed scores (negative = more anomalous in sklearn convention; flip sign for "anomaly score" direction)
- Fit on X_train only, score X_val and X_test
- Key hyperparams: `n_estimators=200`, `max_samples='auto'`, `contamination='auto'`

**Why keep it:** Complementary signal to ECOD/COPOD (tree-based path-length vs. distribution-tail). Well-understood, robust.

```python
from sklearn.ensemble import IsolationForest
clf = IsolationForest(n_estimators=200, random_state=42)
clf.fit(X_train)
scores = -clf.decision_function(X_test)  # negate: high = more anomalous
```

### 2.4 LOF — Local Outlier Factor

**Core idea:** Compares local density of a point to k nearest neighbors. Points in sparse regions relative to neighbors get high LOF score.

**ADBench finding:** LOF statistically outperforms other unsupervised methods for **local anomalies** — samples that are anomalous relative to their local neighbourhood but not globally outlying. In steel rolling, a defect may be an outlier within a specific operating regime (coil grade, speed range) even if it's not globally extreme.

**Key setting:** `n_neighbors` — use 5, 10, 20 (or ensemble all three). For small-N datasets, `n_neighbors=5` or `10` is typical.
- `novelty=True` mode allows `predict()` on new data (required for OOF pattern)

```python
from sklearn.neighbors import LocalOutlierFactor
clf = LocalOutlierFactor(n_neighbors=10, novelty=True)
clf.fit(X_train)
scores = -clf.decision_function(X_test)  # negate: high = more anomalous
```

### 2.5 Autoencoder Reconstruction Error

**Core idea:** Train a shallow MLP autoencoder on Y=0 (normal) samples only. At inference, compute MSE between input x and reconstruction x_hat. Large MSE = the sample is far from the normal manifold = potential defect.

**Why different:** Captures nonlinear manifold deviations that ECOD/COPOD/LOF miss. The other detectors are linear or kernel-based; AE learns a nonlinear compression of normal behaviour.

**Critical implementation detail:** Train ONLY on `X_train[y_train == 0]`. If you train on mixed data, the autoencoder learns to reconstruct defects too and loses sensitivity.

**Architecture for 49 features:**
```
Input(49) → Dense(32, relu) → Dense(16, relu) → Dense(32, relu) → Dense(49, linear)
Loss: MSE
Epochs: 50, batch: 32, early_stop patience=5 on val_loss
```

**Score = per-sample MSE** on reconstruction. Normalize to [0,1] via RobustScaler for consistent feature magnitude.

**Risk:** Autoencoders can sometimes reconstruct anomalies well (the "generalization paradox"). Research (arXiv 2501.13864) confirms this is a real failure mode. Mitigation: combine with the 4 shallow detectors — don't rely on AE alone.

---

## 3. CV-Safe Implementation Pattern (NO LEAKAGE)

This is the most critical engineering requirement. Anomaly detectors trained on the full dataset and used as features = severe data leakage. Must use OOF (out-of-fold) pattern.

### Pattern: Anomaly Score OOF Stacking

```python
import numpy as np
from sklearn.model_selection import StratifiedKFold
from pyod.models.ecod import ECOD
from pyod.models.copod import COPOD
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor
from sklearn.preprocessing import RobustScaler

def build_anomaly_features_oof(X_train, y_train, X_test, n_splits=5, random_state=42):
    """
    Returns:
        train_anomaly_feats: shape (N_train, n_detectors)
        test_anomaly_feats:  shape (N_test, n_detectors)
    
    CV-safe: each detector is fit on (n_splits-1) folds, scores the held-out fold.
    Test scores are averaged across all n_splits detector fits.
    """
    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=random_state)
    
    n_detectors = 5  # ECOD, COPOD, IForest, LOF, AE-placeholder
    train_feats = np.zeros((len(X_train), n_detectors))
    test_feats_accum = np.zeros((len(X_test), n_detectors))
    
    for fold, (tr_idx, val_idx) in enumerate(skf.split(X_train, y_train)):
        X_tr, X_val = X_train[tr_idx], X_train[val_idx]
        
        # Scale (inside fold — no leakage)
        scaler = RobustScaler()
        X_tr_sc = scaler.fit_transform(X_tr)
        X_val_sc = scaler.transform(X_val)
        X_test_sc = scaler.transform(X_test)
        
        detectors = [
            ECOD(),
            COPOD(),
            IsolationForest(n_estimators=200, random_state=random_state),
            LocalOutlierFactor(n_neighbors=10, novelty=True),
        ]
        
        for d_idx, det in enumerate(detectors):
            if isinstance(det, IsolationForest):
                det.fit(X_tr_sc)
                train_feats[val_idx, d_idx] = -det.decision_function(X_val_sc)
                test_feats_accum[:, d_idx] += -det.decision_function(X_test_sc)
            elif isinstance(det, LocalOutlierFactor):
                det.fit(X_tr_sc)
                train_feats[val_idx, d_idx] = -det.decision_function(X_val_sc)
                test_feats_accum[:, d_idx] += -det.decision_function(X_test_sc)
            else:
                # PyOD detectors
                det.fit(X_tr_sc)
                train_feats[val_idx, d_idx] = det.decision_function(X_val_sc)
                test_feats_accum[:, d_idx] += det.decision_function(X_test_sc)
        
        # AE reconstruction error (d_idx=4) — placeholder, implement with keras/torch
        # ae = build_ae(X_tr_sc[y_train[tr_idx] == 0])  # train on normal only
        # train_feats[val_idx, 4] = ae.reconstruction_error(X_val_sc)
        # test_feats_accum[:, 4] += ae.reconstruction_error(X_test_sc)
    
    test_feats = test_feats_accum / n_splits  # average across folds
    
    # Final scale each anomaly score column to [0, 1]
    for col in range(n_detectors):
        col_min = train_feats[:, col].min()
        col_max = train_feats[:, col].max()
        if col_max > col_min:
            train_feats[:, col] = (train_feats[:, col] - col_min) / (col_max - col_min)
            test_feats[:, col] = np.clip(
                (test_feats[:, col] - col_min) / (col_max - col_min), 0, 1
            )
    
    return train_feats, test_feats


# Usage in V35/V39/V40 retrain:
# train_anom, test_anom = build_anomaly_features_oof(X_train_np, y_train_np, X_test_np)
# X_train_aug = np.hstack([X_train_np, train_anom])
# X_test_aug  = np.hstack([X_test_np,  test_anom])
# ... then train LGB/XGB/Cat on X_train_aug, predict on X_test_aug
```

**Key leakage checks:**
1. Scaler is fit inside each fold — no global scaler
2. Detectors are fit on `X_tr` only (never on `X_val` or `X_test`)
3. Test scores averaged across `n_splits` fits (not fit once on full train) — this is the standard stacking test inference trick
4. Autoencoder trains on `X_tr[y_tr == 0]` — normal-only, inside-fold

---

## 4. Integration into V35/V39/V40/V41 Retrain

### Step 1: Feature generation (one-time, ~5 min)
```python
# After loading your train/test DataFrames as usual:
X_train_np = X_train.values.astype(np.float32)
y_train_np = y_train.values
X_test_np  = X_test.values.astype(np.float32)

train_anom, test_anom = build_anomaly_features_oof(
    X_train_np, y_train_np, X_test_np, n_splits=5
)
anom_cols = ['score_ecod', 'score_copod', 'score_iforest', 'score_lof', 'score_ae']
train_anom_df = pd.DataFrame(train_anom, columns=anom_cols, index=X_train.index)
test_anom_df  = pd.DataFrame(test_anom,  columns=anom_cols, index=X_test.index)

X_train_v2 = pd.concat([X_train, train_anom_df], axis=1)
X_test_v2  = pd.concat([X_test,  test_anom_df],  axis=1)
```

### Step 2: Model retrain
Replace `X_train` with `X_train_v2` and `X_test` with `X_test_v2` in your existing V35/V39 pipeline. No other changes needed. LightGBM / XGBoost will discover the relevant anomaly scores via feature importance and incorporate them automatically.

### Step 3: Verify signal (before submitting)
```python
# Check feature importance to confirm anomaly scores are being used
import shap
explainer = shap.TreeExplainer(lgb_model)
shap_vals  = explainer.shap_values(X_val_v2)
# Plot top-20 features — if score_ecod / score_lof appear in top-10, signal is real
```

If anomaly scores rank near-zero importance → they add noise → drop before submission.

---

## 5. Expected Lift Estimate

### Theoretical basis:
- In ADBench (57 datasets, NeurIPS 2022): combining unsupervised anomaly scores with supervised models in a stacking setup shows consistent improvements on imbalanced datasets where the minority class IS the anomaly class (our exact setting).
- The "meta-feature from anomaly detector" technique is a well-established Kaggle trick for fraud detection, manufacturing QC, and medical anomaly tasks.

### Competition evidence:
- Kaggle LEAD (Large-scale Energy Anomaly Detection) winner used equal-weight ensemble of LGB+XGB+Cat+HistGB — anomaly-aware feature engineering contributed to top-tier performance
- Industrial IoT anomaly detection: XGBoost with anomaly features reduced false alarms from 4.81% baseline to 1.83%

### Our expected impact:
- **Optimistic scenario:** +2 to +5 LB points if ECOD/LOF scores correlate with defect cluster structure in test set. This would push 72.83 → 75-78.
- **Conservative scenario:** +0.5 to +1.5 LB points — anomaly scores are a weak signal but not harmful
- **Neutral scenario:** 0 lift, anomaly scores show low SHAP importance → drop them, no regression

**Note:** Getting from 72.83 → 80+ likely requires more than anomaly features alone. Anomaly features are one piece; threshold calibration, coil-neighbour features, and stacking architecture are the others.

---

## 6. Risks and Mitigations

| Risk | Severity | Mitigation |
|------|----------|------------|
| **Anomaly ≠ Defect always** — Some defects are in-distribution; some anomalies are benign (measurement noise, new coil grade). Scores add noise for these. | Medium | Monitor SHAP importance. If scores rank low → drop. |
| **Leakage if implemented incorrectly** — Fitting detector on full train before OOF split inflates OOF AUC (and misleads you about real LB impact). | High | Use the OOF pattern above exactly. Never fit on full train before OOF. |
| **AE reconstruction paradox** — Autoencoders sometimes reconstruct anomalies well (generalisation to novel samples). Paper arXiv 2501.13864 documents this failure mode. | Medium | Use AE as 1 of 5 scores, not sole signal. If AE score SHAP importance near zero → skip. |
| **DeepSVDD mode collapse** — Hypersphere collapse makes all scores identical. ADBench confirmed this empirically. | High | Do not use DeepSVDD. |
| **ABOD O(N^3) slowness** — Angle-Based Outlier Detection is cubic in samples; will time out. | High | Skip ABOD. |
| **Score scale mismatch** — ECOD outputs log-probability scores; IForest outputs path-length scores; AE outputs MSE. Mixed scales confuse the GBDT if not normalized. | Medium | Always normalize to [0,1] per column using train-fold min/max (done in code above). |
| **OOF vs LB calibration gap (V27 lesson)** — Our OOF score improvements can diverge from LB. Validate with actual submit. | High | Submit as V_anom_test, compare delta to V4/V40 baseline. Don't trust OOF alone. |

---

## 7. Which Existing Versions to Retrain

Recommended integration order:

1. **V40 (best current architecture)** — Add 4 anomaly features (ECOD, COPOD, IForest, LOF). Skip AE first run (simpler, fewer failure modes). This is V41.
2. **If V41 OOF ≥ V40 OOF by >0.5 points** → submit
3. **V41 + AE** as V42 — add the 5th feature. Submit if V42 OOF > V41 OOF.
4. **Feature importance check** — if any anomaly score has SHAP mean < 0.001 → drop before final submit to avoid noise.

---

## 8. Sources and Confidence

**Confidence: Medium-High**

The core pattern (unsupervised anomaly score as supervised feature) is well-validated across industry. The specific detector rankings from ADBench are from NeurIPS 2022 — large comprehensive benchmark (57 datasets, 30 algorithms). The CV-safe implementation pattern is standard stacking practice.

**Uncertainty:** Expected lift (2-5 points) is an estimate based on analogous competition solutions. Actual lift depends on whether defects in THIS dataset are tail-anomalies in the feature space (likely yes for manufacturing) or mid-distribution (would reduce ECOD/LOF sensitivity).

---

### Sources:
- [ADBench: Anomaly Detection Benchmark (NeurIPS 2022)](https://ar5iv.labs.arxiv.org/html/2206.09426)
- [ECOD Paper: Unsupervised Outlier Detection Using Empirical CDF](https://arxiv.org/pdf/2201.00382)
- [COPOD Paper: Copula-Based Outlier Detection](https://www.researchgate.net/publication/344306968_COPOD_Copula-Based_Outlier_Detection)
- [PyOD Library Benchmarks](https://pyod.readthedocs.io/en/latest/benchmark.html)
- [PyOD GitHub — 60+ detectors, ADBench-backed](https://github.com/yzhao062/pyod)
- [Autoencoders for Anomaly Detection are Unreliable (arXiv 2501.13864)](https://arxiv.org/html/2501.13864v1)
- [Avoiding Data Leakage in Cross-Validation](https://medium.com/@silva.f.francis/avoiding-data-leakage-in-cross-validation-ba344d4d55c0)
- [Building Leak-Free ML Pipelines with sklearn](https://markaicode.com/sklearn-pipeline-no-leakage/)
- [Anomaly Detection in Industrial IoT with XGBoost+LSTM (Nature Scientific Reports 2024)](https://www.nature.com/articles/s41598-024-74822-6)
- [Feature Encoding with AutoEncoders for Weakly-supervised Anomaly Detection](https://arxiv.org/pdf/2105.10500)
