# R3: TTA and Seed Ensembling for Tabular ML
**Research Date:** 2026-05-24
**Context:** Tata Steel defect detection — 339 test rows, 49 features, imbalanced multiclass. Current LB 72.83. Target 80+.
**Active builds:** V35, V39, V40, V41, V43

---

## Quick Verdict

Seed ensembling gives **real, consistent, low-risk lift** on tabular GBM competitions. TTA (feature perturbation) gives **marginal lift** for GBMs specifically — not the same story as CNNs. CatBoost virtual ensembles are an efficient TTA-adjacent trick but are primarily an uncertainty tool, not an accuracy booster. Combined, these techniques are likely worth +0.5–1.5 LB points on a small, noisy dataset like ours.

---

## 1. TTA for Tabular: Ranked Techniques

### 1A. Seed Ensembling (BEST for GBMs)
**Expected lift:** +0.3 to +1.5 LB points  
**Mechanism:** Same architecture, different `random_state`/`seed` values. Each seed takes a different bagging path, builds slightly different trees, makes different errors. Average of probabilities cancels variance.  
**Evidence:** NVIDIA Kaggle Grandmasters Playbook (2024) explicitly names this as a standard final-model technique. Empirically: 100-seed XGBoost ensemble in the Predicting Optimal Fertilizers Kaggle challenge achieved ~MAP@3 0.379 vs single-seed 0.376 — approximately +0.8% improvement. Separate CatBoost 10-model ensemble on network intrusion classification: error rate 4.0% (single) → 3.6% (ensemble), ROC-AUC 92.8 → 94.2.
**Risk:** None. Pure variance reduction. Bias is unchanged — if your model is systematically wrong, seeds won't fix it.

### 1B. CV Fold × Seed Grid (BEST total coverage)
**Expected lift:** +0.5–2.0 LB points (combined with above)  
**Mechanism:** Train with K folds × S seeds = K×S models. Average all test probas. Each fold sees different train/val split; each seed sees different subsampling path.  
**Recipe:** 5 folds × 4 seeds = 20 models per paradigm. Average their `predict_proba` outputs on the 339 test rows.  
**Compute cost:** Linear with K×S. With LGB/XGB/CatBoost on 49 features, 20 models each takes ~minutes.

### 1C. Bootstrap Resample Ensembling (GOOD for imbalanced)
**Expected lift:** +0.3–0.8 LB  
**Mechanism:** Draw N bootstrap samples from training data (with replacement). Train one model per bootstrap. Average test predictions.  
**Why useful for imbalanced:** Each bootstrap sample has a different class balance realization — the ensemble implicitly sees multiple imbalance regimes and averages them out.  
**Key finding:** Oversampling/undersampling within bootstrap loops can improve boosting performance specifically (literature confirms this for imbalanced cases).

### 1D. Feature Perturbation / Noise Injection TTA (WEAK for GBMs)
**Expected lift:** +0.0–0.3 LB for tree models (marginal)  
**Mechanism:** At inference, add Gaussian/Laplace noise to numeric features, flip categorical features with small probability. Run 10–50 perturbed copies, average probabilities.  
**Critical finding from Teague (2022) paper:** Gradient boosting is robust to mild inference noise (trees split on thresholds, not smooth gradients), but **training noise injections degraded GBM performance** — opposite of NNs. The paper found "strongest performance came from injections only to the test features for inference" and noted "gradient boosting appears robust to a mild noise profile in inference."  
**Bottom line:** Not worth the complexity for GBMs unless your features have known noise distributions you're deliberately modeling. Skip for our pipeline.

### 1E. Dropout-at-Inference (NOT applicable to GBMs)
MC Dropout is a neural-network technique. LGB/XGB/CatBoost don't have inference dropout. DART mode in LGB drops trees during **training** (not inference). Not applicable here.

### 1F. CatBoost Virtual Ensembles (SITUATIONAL)
**Expected lift:** Uncertainty estimation > accuracy improvement  
**API:** `model.virtual_ensembles_predict(X_test, prediction_type='VirtEnsembles', virtual_ensembles_count=10)`  
**Requirement:** Model must be trained with `PosteriorSampling=True` parameter.  
**What it does:** Splits a single trained model into N "truncated" sub-models (each uses a prefix of the full tree sequence). Returns N probability vectors per row. Average them for a smoothed probability.  
**Accuracy evidence:** 10-model virtual ensemble: error 4.0% → 3.6%, ROC-AUC 92.8 → 94.2 on network intrusion. That's ~+1.4 pp ROC-AUC.  
**Caveat:** This requires retraining the CatBoost model from scratch with `PosteriorSampling=True`. It's a training-time parameter change, not pure inference-only. If our CatBoost builds (V40/V41/V43) are already trained, we need a retrain.  
**Verdict:** Worth doing for CatBoost-specific models, but low priority vs. seed ensembling.

---

## 2. Implementation: How to Add to V35/V39/V40/V41/V43

### Pattern A: Seed Ensemble Layer (applies to all 5 paradigms)

```python
import numpy as np

SEEDS = [42, 137, 2024, 1000, 7]  # 5 seeds minimum; 10 if compute allows

def seed_ensemble_predict(ModelClass, base_params, X_train, y_train, X_test, seeds=SEEDS):
    """
    Train same model architecture with different seeds,
    return averaged test probabilities.
    """
    all_test_probas = []
    for seed in seeds:
        params = {**base_params, 'random_state': seed}  # LGB/XGB/sklearn style
        # For CatBoost: use 'random_seed' key
        model = ModelClass(**params)
        model.fit(X_train, y_train)
        proba = model.predict_proba(X_test)  # shape (339, n_classes)
        all_test_probas.append(proba)
    
    avg_proba = np.mean(all_test_probas, axis=0)  # (339, n_classes)
    return avg_proba
```

### Pattern B: CV Fold × Seed Grid (recommended approach)

```python
from sklearn.model_selection import StratifiedKFold
import numpy as np

def cv_seed_ensemble(model_factory, X, y, X_test, n_folds=5, seeds=[42, 137, 1000, 7]):
    """
    Full CV × seed grid. Returns:
    - oof_probas: out-of-fold predictions on X (for blending)
    - test_probas: averaged test predictions
    """
    n_classes = len(np.unique(y))
    oof_probas = np.zeros((len(X), n_classes))
    all_test_probas = []

    for seed in seeds:
        skf = StratifiedKFold(n_splits=n_folds, shuffle=True, random_state=seed)
        seed_test_probas = []
        
        for fold, (tr_idx, val_idx) in enumerate(skf.split(X, y)):
            X_tr, X_val = X[tr_idx], X[val_idx]
            y_tr, y_val = y[tr_idx], y[val_idx]
            
            model = model_factory(seed=seed)
            model.fit(X_tr, y_tr)
            
            # OOF (only fill from first seed to avoid OOF leakage confusion)
            if seed == seeds[0]:
                oof_probas[val_idx] = model.predict_proba(X_val)
            
            seed_test_probas.append(model.predict_proba(X_test))
        
        all_test_probas.append(np.mean(seed_test_probas, axis=0))

    final_test_probas = np.mean(all_test_probas, axis=0)
    return oof_probas, final_test_probas
```

### Pattern C: LGB-specific seed params

```python
# LightGBM
lgb_params = {
    'objective': 'multiclass',
    'num_class': N_CLASSES,
    'seed': 42,          # data + feature sampling seed
    'bagging_seed': 42,  # explicit bagging seed (some versions)
    'feature_fraction_seed': 42,
    # ... rest of your tuned params from V35/V39
}
```

### Pattern D: XGBoost seed

```python
# XGBoost
xgb_params = {
    'seed': 42,          # or 'random_state' in sklearn API
    # ... rest of params from V40
}
```

### Pattern E: CatBoost seed + optional virtual ensembles

```python
# CatBoost — seed
cb_params = {
    'random_seed': 42,
    # PosteriorSampling for virtual ensembles (requires retrain):
    # 'posterior_sampling': True,  # enable only if doing virtual_ensembles
    # ... rest from V41/V43
}

# If you retrain with PosteriorSampling=True:
# avg_proba = np.mean(
#     model.virtual_ensembles_predict(X_test, virtual_ensembles_count=10),
#     axis=0
# )
```

---

## 3. Compute Cost vs. Benefit Table

| Technique | Models Trained | Relative Compute | Expected LB Lift | Risk |
|-----------|---------------|-----------------|-----------------|------|
| 5-seed ensemble (per paradigm) | 5× | 5× | +0.3–0.8 | Near zero |
| 10-seed ensemble (per paradigm) | 10× | 10× | +0.5–1.2 | Near zero |
| 5 folds × 5 seeds = 25 | 25× | 25× | +0.8–2.0 | Low (watch OOF leakage) |
| 5 seeds × 5 paradigms | 25 total | Moderate | +0.5–1.5 | Low |
| Bootstrap TTA (20 resamples) | 20× | 20× | +0.2–0.6 | Low-medium (tiny dataset risk) |
| CatBoost virtual ensembles | 1 model, N inferences | ~1× inference | +0.1–0.5 | Requires retrain |
| Feature noise TTA (GBM) | Same model, 20× inference | ~0.5× | +0.0–0.2 | Not worth it |

**For 339 training rows + 49 features on GBMs: a 5-seed × 5-fold grid per paradigm runs in minutes per paradigm on CPU.**

---

## 4. Recommended Implementation Order for This Competition

### Priority 1 (do now, high ROI):
**Seed ensemble across all 5 paradigms**
- V35 (LGB): retrain with seeds [42, 137, 1000, 7, 2024] — average 5 test probas
- V39 (LGB variant): same
- V40 (XGB): same with `seed` param
- V41 (CatBoost): same with `random_seed` param
- V43 (CatBoost variant): same
- Then re-blend the 5-paradigm meta-ensemble on the seed-averaged probas

### Priority 2 (do next, if Priority 1 shows gains):
**CV Fold × Seed for best 2 paradigms**
- Pick the 2 strongest individual paradigms by OOF score
- Run 5 folds × 5 seeds = 25 models each
- This directly replaces single-fold test predictions with much more stable estimates

### Priority 3 (bonus if time permits):
**CatBoost virtual ensembles**
- Retrain V41 or V43 with `posterior_sampling=True`
- Call `virtual_ensembles_predict(..., virtual_ensembles_count=10)`
- Average the 10 virtual predictions
- Replace the CatBoost proba in the blend

### Skip:
- Feature noise TTA (GBM-specific: weak effect)
- MC Dropout (no trees have inference dropout)

---

## 5. Risk Analysis

### What seed ensembling DOES fix:
- High variance from stochastic subsampling (bagging fraction, feature fraction)
- Lucky/unlucky initialization artifacts
- Fold-specific overfitting when using single CV split

### What seed ensembling does NOT fix:
- **Bias.** If your feature engineering is systematically wrong, seeds just average the same error more confidently. A 5-seed ensemble of a model with bad features scores the same as 1 model — more stably wrong.
- **Distribution shift.** If test distribution differs from train, seeds amplify calibration consistency but not generalization.
- **Class imbalance.** Seeds don't change what the model learned about minority classes. Use class weights + SMOTE + stratified sampling inside each fold for that.
- **OOF calibration drift.** Our V27 lesson: post-hoc rules validated on OOF can appear to gain +1.04 CV but collapse -34.89 LB. Seed ensembling reduces variance of the base predictions but does NOT validate threshold decisions — those still need LB sanity checks.

### Expected ceiling for our dataset:
- 339 rows is very small. Seeds make a meaningful difference here (more so than on 100k+ row datasets where variance self-averages).
- Realistic from pure seed ensembling: **+0.5–1.5 LB points**
- Realistic from CV × seed grid on best paradigm: **+1.0–2.0 LB points**
- Combined with our current 72.83: potential to reach **73.3–75.0** from this alone
- To reach 80+, ensembling must combine with better feature engineering, calibrated blending weights, or a stronger paradigm. Seed ensembling is a multiplier, not a savior.

---

## 6. Quick Checklist Before Running

- [ ] All paradigm models use `predict_proba()` not `predict()` — we need soft probabilities for averaging
- [ ] Seeds list is fixed and documented per build so results are reproducible
- [ ] Stratified splits (not random) so each fold has representative class distribution
- [ ] After seed averaging per paradigm, re-optimize blending weights on OOF (the OOF probas also become the seed-averaged OOF)
- [ ] Do NOT re-run post-hoc threshold rules on OOF after seed-averaging without LB validation (V27 lesson)

---

## Sources

- [Test-Time Augmentation for Tabular Data — kozodoi.me](https://www.kozodoi.me/blog/20210908/tta-tabular)
- [Stochastic Perturbations of Tabular Features — Teague (2022) arXiv:2202.09248](https://arxiv.org/pdf/2202.09248)
- [CatBoost virtual_ensembles_predict API](https://catboost.ai/docs/en/concepts/python-reference_virtual_ensembles_predict)
- [CatBoost Uncertainty Reference](https://catboost.ai/docs/en/references/uncertainty)
- [Estimating Uncertainty with CatBoost Classifiers — TDS](https://towardsdatascience.com/estimating-uncertainty-with-catboost-classifiers-2d0b2229ad6/)
- [Kaggle Grandmasters Playbook — NVIDIA Technical Blog](https://developer.nvidia.com/blog/the-kaggle-grandmasters-playbook-7-battle-tested-modeling-techniques-for-tabular-data/)
- [How Ensemble Learning Balances Accuracy and Overfitting — arXiv:2512.05469](https://arxiv.org/pdf/2512.05469)
- [Revisiting Gradient Boosting for Imbalanced Data — MDPI](https://www.mdpi.com/2504-2289/6/2/41)
- [Feature Augmentation based Test-Time Adaptation — WACV 2025](https://openaccess.thecvf.com/content/WACV2025/papers/Cho_Feature_Augmentation_Based_Test-Time_Adaptation_WACV_2025_paper.pdf)
- [D.A.R.T — Dropout in Boosting Models — Medium](https://medium.com/@meir412_37692/d-a-r-t-your-new-weapon-against-overfitting-in-boosting-models-9ea4e6aa435b)
