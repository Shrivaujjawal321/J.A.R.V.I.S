# V35 Approach — Ratnesh-Jarvis Recipe Replication
**Date:** 2026-05-24
**Status:** COMPLETE — DO NOT FIRE (gates 2/5, est LB 46.84 < V4 banked 56.98)

---

## 1. What We Built

V35 is a faithful replication of Ratnesh-Jarvis's disclosed 62.64 LB recipe:
- 9-model ensemble with pure rank-average aggregation
- K=170 threshold (Ratnesh's empirically determined optimum)
- scale_pos_weight=18.9, no SMOTE, no BBSE
- 5-fold StratifiedKFold, seed=42

Our 9 base learners (substituting for Ratnesh's AutoGluon/TabPFN/iter15/iter18 with equivalent model classes):

| # | Model | Config | Our Substitute For |
|---|---|---|---|
| 1 | LGB1 | seed=42, V4 params | Ratnesh's ts1 |
| 2 | LGB2 | seed=137, diverse params | Ratnesh's ts3 |
| 3 | XGB1 | seed=42, V4 params | Ratnesh's ts4 |
| 4 | XGB2 | seed=137, diverse params | Ratnesh's ts5 |
| 5 | CatBoost | seed=42, V4 params | Ratnesh's gaurita (RF component) |
| 6 | RF | 500 trees, balanced | Ratnesh's gaurita (ET component) |
| 7 | ET | 500 trees, balanced | Ratnesh's iter15 (ET component) |
| 8 | HGB | balanced, 300 iter | Ratnesh's iter15 (HGB component) |
| 9 | TabICL | n_estimators=5, seed=42 | Ratnesh's TabPFN cloud |

---

## 2. Feature Set

**105 features = 51 (V4 SHAP-selected) + 54 (V33 stand-FE)**

V4 features loaded directly from `build_v4/train_v4.parquet` and `build_v4/test_v4.parquet` — avoids reimplementing KMeans cluster features, polynomial features, and coil-neighbor features (which were already validated in V4).

V33 stand-FE applied with fold-isolated setpoints (no leakage):
- Signed + absolute temperature residuals (X4-X9): 12 features
- Signed + absolute force residuals (X29-X33): 10 features
- Cumulative z-deviation, max z-deviation: 2 features
- Raw force/temp deviations: 3 features
- Worst-deviant stand (index + magnitude, temp + force): 4 features
- Inter-stand temperature gradients (F1-F2, F2-F3, ... F5-F6): 5 features
- X35 bimodal decomposition (is_high, log1p, z-score, flag × force): 4 features
- Temperature × Force residual cross-products (5 paired stands): 5 features
- Temperature span (X4-X9), entry temp, exit temp: 3 features
- Force escalation ratio (F5/F1): 1 feature
- Log force columns (X29-X33): 5 features

---

## 3. Rank-Average Aggregation (Ratnesh's Exact Recipe)

```python
from scipy.stats import rankdata
oof_rank_avg  = np.zeros(n_train)
test_rank_avg = np.zeros(n_test)
for m in MODEL_NAMES:
    oof_rank_avg  += rankdata(oof_probas[m])
    test_rank_avg += rankdata(test_probas[m])
oof_rank_avg  /= n_models
test_rank_avg /= n_models
```

NOT meta-stacking with LR (V4's approach). Pure rank-average so no meta-learner overfitting.

---

## 4. Results

| Metric | V35 | V4 (banked) |
|---|---|---|
| Rank-avg OOF AUC | 0.8699 | 0.8837 |
| Bootstrap 95% CI | [0.8247, 0.9112] | — |
| OOF (R+P)/2 at K=170 | 44.17 | 54.31 |
| OOF (R+P)/2 at K=288 (OOF-optimal) | 49.35 | — |
| Est LB at K=170 | 46.84 | — |
| Est LB at K=288 | 52.02 | — |
| V4 actual LB | — | 56.98 |

**Best individual models:** TabICL (0.8752 OOF AUC), ET (0.8717), CatBoost (0.8646)

---

## 5. Key Finding: K=170 Does Not Transfer

Ratnesh's K=170 is calibrated to his specific ensemble's probability outputs. His models (AutoGluon + TabPFN + iter15/18 stacking meta) assign much more concentrated probability mass to true positives — his top 170 rows naturally align with the bulk of the 66 positives.

Our GBDT/RF/ET/HGB ensemble produces shallower probability gradients. OOF-optimal K=288 (not 170). Even at K=288, est LB=52.02 < 56.98.

**Lesson: K-threshold is model-family dependent, not dataset-dependent.**

---

## 6. Why This Recipe Doesn't Close the Gap to Ratnesh's 62.64

Three structural reasons:

1. **Model family gap.** Ratnesh uses AutoGluon (neural nets + bagging ensembles internally) + TabPFN (prior-fitted transformer). These are qualitatively different from GBDT/RF/ET and learn different decision surfaces. We substituted with GBDT-family + TabICL, which is closer to TabPFN but still different.

2. **Feature set gap.** Ratnesh's 148-feature base vs our 105. The additional 43 features likely include physics-derived features or AutoGluon-generated features that capture the "hard 7" defects.

3. **Calibration mismatch.** K=170 is empirically determined for HIS model calibrations, not ours. This alone explains the OOF score difference (44.17 at K=170 vs 49.35 at our K=288).

---

## 7. Anti-Pattern Compliance

| Anti-pattern | Status |
|---|---|
| pd.concat([train, test]) | NOT used anywhere |
| SMOTE | NOT used (no distribution mismatch) |
| BBSE on top of scale_pos_weight | NOT used (no compound over-correction) |
| Fold setpoints on val/test | All StandSetpoints.fit() on train_fold ONLY |
| Auto-submit | NOT triggered — awaiting Boss approval |

---

## 8. Path Forward (V36 Candidate Ideas)

Since V35 confirms the GBDT ceiling is ~0.87 OOF AUC, the next logical move is one of:

**Option A: Proper AutoGluon** — run AutoGluon on our 105-feature set with `presets="best_quality"`. AutoGluon internally uses LGB+XGB+CB+NN+Tabular transformers. Likely to match or exceed Ratnesh's model quality since he uses AutoGluon too. Cost: high compute (~30-60 min).

**Option B: Physics features V2** — original V4 roadmap. Map X1-X49 to actual hot-rolling process variables (roll force per unit width, finishing-temperature deviation from Ar3, draft schedule, Ekelund flow-stress normalization). These features target the "hard 7" defects that all tree models fail on.

**Option C: TabPFN cloud** — Ratnesh confirmed this as one of his components. V33 confirmed license blocker for TabPFN cloud v2. TabICL (local) is already included in V35 as M9 (0.8752 OOF AUC — best single model).

**Option D: Different K calibration with current stack** — Fire V35 at K=288 (OOF-optimal). Est LB 52.02 > V32 49.06 but < V4 56.98. Risk: losing banked V4 position. Only worth it if we genuinely believe OOF-estimated 52.02 will land above 56.98 LB (unlikely, +4pt LB gap too large to attribute to OOF→LB calibration error).

**Recommendation: Option A (AutoGluon) or Option B (physics features)**. Both attack the root cause — model family gap and feature space gap respectively.
