# Component 10: Failure Prediction / Early-Warning Classification
**Tata Steel AI Hackathon 2026 — Round 2 Research Brief**
*Researched: 2026-06-06 | Deadline: 2026-06-15*

---

## 1. Recommended Approach — ONE Clear Winner

**Calibrated LightGBM 4.6 with Horizon-Aware Multi-Label Classification + Rolling Statistical Features**

Concretely: `lightgbm 4.6` trained as a **4-class ordinal classifier** (NORMAL / WARN_72H / WARN_24H / IMMINENT) with `scale_pos_weight` for imbalance, Isotonic Regression calibration via `sklearn.calibration.CalibratedClassifierCV`, and a `tsfresh`-extracted rolling-window feature matrix (window = 30 cycles). Optuna tunes 7 hyperparameters in 50 trials via `optuna-integration[lightgbm]`. SHAP TreeExplainer provides per-alert explanations in <5ms.

### Why multi-class ordinal (not binary or pure regression)

The problem says "early warning of catastrophic failures" and "urgency assessment" — those are two distinct deliverables.

A binary fail/no-fail classifier loses urgency resolution. A pure RUL regressor (covered in Component 08) tells you *when*, but not the discrete alert level that the engineer needs to act on. Ordinal 4-class (NORMAL, WARN_72H, WARN_24H, IMMINENT) maps directly to action protocols: schedule next PM cycle / order spares now / mobilize shift crew / stop machine immediately. Each class corresponds to a time-to-failure window derived from the sensor trajectory, and the calibrated probability output (`P(IMMINENT)`, `P(WARN_24H)`) feeds the alerting + prioritization engine with uncertainty-quantified numbers, not opaque flags.

### What the 4 classes mean in construction

Training labels are assigned using a **look-ahead window** over the historical log:

```
Label = IMMINENT    if failure occurs within next 1 cycle  (failure_flag=1)
Label = WARN_24H    if failure occurs within next T_24 cycles
Label = WARN_72H    if failure occurs within next T_72 cycles
Label = NORMAL      otherwise
```

T_24 and T_72 are dataset-specific: for AI4I 2020 (discrete machine events), set T_24 = 3 records, T_72 = 9 records, based on a 15-min sample cadence. For NASA C-MAPSS, set T_24 = 10 cycles, T_72 = 30 cycles (engine-cycle cadence).

---

## 2. WHY — Evidence-Based Reasoning

### 2a. LightGBM dominates structured tabular sensor data

A 2026 arXiv paper (arXiv:2603.13343) benchmarked LightGBM on AI4I 2020 under 5-fold stratified cross-validation with SMOTE confined to training folds — achieving **AUC-ROC 0.973**. The same framework scored macro F1 of 0.855 with contextual features vs. 0.807 without, showing feature engineering is the primary lever, not model architecture.

The Scania truck failure IDA Challenge study (CMC v86n3) showed a two-stage LightGBM framework outperforming XGBoost and Bi-LSTM by **3.8–13.5%** on total misclassification cost, achieving validation cost of 36,113. Their key insight — a "last_k_summary" rolling statistical descriptor — is exactly the tsfresh rolling approach.

A 2025 IoT manufacturing study (ResearchGate: LightGBM Predictive Maintenance IoT) reported AUC of 0.89 for aviation engine failure prediction using LightGBM, with lower RMSE than XGBoost and Random Forest across multiple datasets.

LightGBM 4.6.0 (February 2025) delivers: histogram-based learning (memory-efficient on a judge's CPU), native missing value handling (critical for sparse sensor logs), `scale_pos_weight` for imbalanced classes, configurable `min_delta` early stopping, and full scikit-learn API compatibility for pipeline integration.

### 2b. Calibration is non-negotiable for alert systems

An uncalibrated gradient boosting classifier (LightGBM, XGBoost) overestimates extreme probabilities — this is well-documented (Niculescu-Mizil & Caruana, ICML 2005; confirmed by recent 2025 arXiv:2601.19944 at scale). For a Maintenance Wizard, a mis-calibrated 0.9 probability that actually corresponds to 0.6 true frequency will trigger false IMMINENT alerts and erode engineer trust within days of deployment.

Isotonic Regression calibration (`CalibratedClassifierCV(method='isotonic', cv=5)`) beats Platt scaling when the calibration set has ≥1000 points — which AI4I 2020 (10,000 samples) comfortably satisfies. The 2025 vehicle maintenance study (arXiv:2603.13343) showed Platt scaling reduced Brier score from 0.082 to 0.080 on LightGBM — isotonic would improve further on larger calibration sets.

### 2c. SMOTE-in-fold + scale_pos_weight: complementary, not competing

The AI4I 2020 dataset has ~3.4% positive failure rate (339/10,000). A 2025 Springer study ("Enhancing predictive maintenance in automotive industry") demonstrated that hybrid SMOTE + model-level class weighting outperforms either alone on F1 for the minority class. The 2025 MDPI paper (Machines 13/8/663) corroborated this: combining SMOTE, class weighting, and focal-loss emphasis achieved F1=0.7199 and recall=0.9545 on the minority class for neural networks; XGBoost with weighted objectives hit PR-AUC 0.7126 — competitive for a simple ensemble.

In practice: apply SMOTE only inside each CV fold's training split (never on validation), then set `scale_pos_weight = n_negatives / n_positives` (~29 for AI4I). Use `metric='average_precision'` (PR-AUC) as the early stopping metric, not accuracy or AUC-ROC, because PR-AUC is directly sensitive to minority-class precision/recall trade-off.

### 2d. tsfresh rolling features are the real moat

Raw sensor readings are weak predictors; the signal lives in the derivative behavior (trend, variance growth, spectral shift). tsfresh 0.21.0 extracts 794 features per window by default via 63 characterization methods. For production use, `EfficientFCParameters()` reduces this to ~780 features with 40% lower compute. From those, `select_features()` (FRESH algorithm) retains only statistically significant ones — typically 40–120 features survive for a given failure type.

Rolling window size = 30 cycles balances: enough history to detect trend (>10), not so long it smears onset signal (>50 starts including pre-degradation normal baseline). This matches the Scania study's "last_k_summary" approach and the C-MAPSS literature's standard 30-cycle window.

---

## 3. Exact Stack

| Library | Version | Role |
|---|---|---|
| `lightgbm` | 4.6.0 | Primary classifier: 4-class ordinal, histogram trees, native imbalance handling |
| `scikit-learn` | 1.6.x | `CalibratedClassifierCV` (isotonic), `StratifiedKFold`, `Pipeline`, metrics |
| `imbalanced-learn` | 0.14.x | `SMOTE` confined to training folds inside CV; `SMOTETomek` optional |
| `tsfresh` | 0.21.0 | Rolling window feature extraction (794 → ~80 after FRESH selection) |
| `optuna` | 4.x | Bayesian hyperparameter optimization (50 trials, Haiku pruner) |
| `optuna-integration[lightgbm]` | 4.x | LightGBM callback for optuna; auto early-stopping |
| `shap` | 0.46.x | TreeExplainer for per-prediction feature attribution (<5ms) |
| `numpy` | 1.26.x | Array ops, rolling computation |
| `pandas` | 2.2.x | Data wrangling, look-ahead label construction |
| `scipy` | 1.13.x | Brier score, calibration curve validation |
| `joblib` | 1.4.x | Model serialization (`.pkl` artefact stored in `models/`) |

All CPU-only. No GPU required. `pip install lightgbm==4.6.0 scikit-learn imbalanced-learn tsfresh optuna optuna-integration[lightgbm] shap` — single pip command, no docker, no CUDA.

---

## 4. Alternatives Considered

### Alt A: XGBoost 2.1 with DMatrix
**Why it loses:** XGBoost 2.1 has strong calibration out-of-box and excellent SHAP integration, but LightGBM 4.6 is 2–4x faster on training with the histogram algorithm (critical when tsfresh produces 100+ features and Optuna runs 50 trials). The Scania study showed LightGBM beat XGBoost by 3.8% on misclassification cost. For a 9-day solo build where iteration speed matters, LightGBM wins. **Tradeoff:** XGBoost has slightly better documentation; use it as a swap-in if LightGBM shows instability on judge's machine.

### Alt B: CNN-BiLSTM end-to-end on raw sensor sequences
**Why it loses:** CNN-LSTM hybrids achieve ~96% accuracy on manufacturing datasets (per the 2025 early-warning review). But they require GPU or at least a warm CPU for inference latency — risk on a judge's machine. Training takes 30+ minutes. Explainability requires SHAP DeepExplainer which is 10–100x slower than TreeExplainer. The Tata judging rubric scores "easy-to-use, doesn't break, smooth" — a DL model with CUDA dependencies is a liability. **Tradeoff:** Better temporal representation; acceptable only if there's a clear validation advantage >5% F1.

### Alt C: Conformal Prediction wrapper over any base model
**Why it loses:** The 2025 MDPI/Futures paper on conformal prediction for IoT maintenance is compelling — distribution-free coverage guarantees, model-agnostic. The Transformer + MC Dropout + CP framework is theoretically superior for uncertainty quantification. But it adds ~200 lines of non-trivial calibration code, a separate nonconformity score computation, and conformal sets are harder to explain to a steel-plant engineer than "85% chance of failure in 24h." Isotonic calibration achieves 90% of the practical benefit. **Tradeoff:** Reserve conformal prediction as a future improvement narrative in the design document — it signals research depth without adding demo-crash risk.

### Alt D: Isolation Forest / One-Class SVM anomaly detection
**Why it loses:** Anomaly detection finds deviations from normal — it is NOT failure prediction. An anomaly may not lead to failure; a failure may not look anomalous until the moment it happens. Relying on anomaly detection for the "will fail in N" output is a fundamental category error. Seen in many 2022-tier hackathon submissions. The Component 09 (anomaly detection) handles this separately; Component 10 must use supervised failure-labeled training data. **Tradeoff:** Isolation Forest is fine as an *upstream* pre-filter to flag unusual readings before the failure classifier runs, but not as a replacement.

---

## 5. Anti-Patterns (what screams "amateur / 2022-tier")

1. **Binary fail/no-fail with accuracy as the metric.** If 96.6% of samples are NORMAL, a constant-predict-NORMAL classifier gets 96.6% accuracy and zero utility. Any submission reporting >95% accuracy without PR-AUC or F1-minority is red-flagged immediately.

2. **SMOTE on the entire dataset before train/test split.** This leaks validation examples into synthetic training samples, inflating all metrics. The correct pattern: `imblearn.Pipeline` with SMOTE inside `cross_val_score` folds only.

3. **Raw sensor values fed directly without rolling features.** Single-timestep sensor readings have low predictive power for failure *horizon*. Failure prediction requires the trajectory — variance trends, rate-of-change, spectral shift. Not extracting rolling features is leaving >50% of signal on the floor.

4. **Using anomaly score as a failure probability.** Isolation Forest output is not a calibrated probability. Passing it directly to the alert engine gives nonsense thresholds.

5. **No calibration on gradient boosted trees.** GBMs are notoriously miscalibrated. Shipping uncalibrated probabilities to an alert system that thresholds on 0.7 or 0.8 will produce either too many false positives or dangerous missed detections.

6. **Threshold = 0.5 hardcoded.** The optimal threshold for an imbalanced failure-detection problem is rarely 0.5. It must be set by maximizing F1-minority on a validation fold (typically 0.2–0.4 for 3% prevalence).

7. **One model for all failure types.** AI4I 2020 has 5 distinct failure modes (HDF, PWF, OSF, RNF, TWF). A single monolithic model trained on `machine failure` (binary) loses the mode-specific signal. Train separate failure-mode columns or use multi-label. This is the difference between "AI predicted failure" and "AI predicted overstrain failure — check tool wear indicator."

---

## 6. Integration Notes

### Inputs this component consumes

- **From Component 09 (Anomaly Detection):** `anomaly_score: float`, `anomaly_flag: bool` per sensor tick. These become features in the failure classifier input.
- **From Component 08 (RUL):** `rul_days_p50: float`, `rul_days_p10: float`. These are high-signal features — a unit with RUL P50 < 5 days is far more likely to enter WARN_24H class.
- **Raw sensor tick stream:** temperature, rotational speed, torque, tool wear, process parameters. Each tick triggers a rolling window recompute.
- **Equipment metadata:** equipment type, age, last maintenance date. Static features appended to each tsfresh feature row.

### Outputs this component produces

```json
{
  "equipment_id": "ROLL_MILL_07",
  "timestamp": "2026-06-06T14:23:00Z",
  "alert_class": "WARN_24H",
  "probabilities": {
    "NORMAL": 0.08,
    "WARN_72H": 0.21,
    "WARN_24H": 0.54,
    "IMMINENT": 0.17
  },
  "calibrated": true,
  "threshold_used": 0.35,
  "top_shap_features": [
    {"feature": "tool_wear__mean_30", "value": 0.82, "direction": "up"},
    {"feature": "torque__variance_30", "value": 0.67, "direction": "up"},
    {"feature": "rul_days_p50", "value": -0.41, "direction": "down"}
  ],
  "failure_modes": {
    "TWF": 0.42,
    "HDF": 0.31,
    "OSF": 0.19,
    "PWF": 0.05,
    "RNF": 0.03
  }
}
```

### Components this talks to

- **Component 11 (Risk Classification / Prioritization Engine):** Consumes `alert_class` + `probabilities` to compute plant-level urgency ranking. `P(IMMINENT)` × `process_criticality_weight` = urgency score for the leaderboard.
- **Component 07 (Alerting / Notification):** Triggers real-time Telegram/dashboard notification when `alert_class` transitions from NORMAL to any WARN level, or when `P(IMMINENT) > 0.6`.
- **Component 06 (Explainability):** Receives `top_shap_features` and formats them into engineer-readable narrative ("Torque variance spiked 2.3σ above baseline over last 30 cycles — primary driver of WARN_24H classification").
- **Component 04 (RAG — Knowledge Integration):** When alert fires, RAG layer is triggered to retrieve relevant SOP sections and historical incident reports for that failure mode.
- **Feedback Loop (Component FR):** Engineer confirms or dismisses the alert via UI. Outcome stored in `feedback_log.jsonl`. Weekly retraining run uses these labels to update the classifier's training set — closing the feedback-driven improvement loop (Functional Requirement 6).

### Inference latency budget

- tsfresh rolling recompute on 30-cycle window: ~80ms (EfficientFCParameters, single equipment unit)
- LightGBM inference (100 trees, 120 features): <2ms
- SHAP TreeExplainer top-3 features: <5ms
- **Total per tick: ~90ms** — well within real-time alert requirements

---

## 7. Open Risks / Unknowns

1. **tsfresh compute time on large fleets** [verified concern]: For 100 equipment units with 30-cycle windows computed every minute, tsfresh will add ~8 seconds/batch. Mitigation: cache feature matrix per unit, only recompute on new tick. Use `EfficientFCParameters` not `ComprehensiveFCParameters`.

2. **Label quality on synthetic steel-plant data** [key risk]: The synthetic maintenance logs we generate must have realistic failure-to-window ratios. If the generator creates too many IMMINENT labels, the classifier will overfit to synthetic patterns. Mitigation: match AI4I 2020's 3.4% failure rate as the prior; generate failures from Weibull degradation trajectories (consistent with Component 08's RUL model).

3. **Threshold selection on demo data** [unverified]: The optimal threshold (maximizing F-beta on validation) will shift between the public benchmark and the synthetic data. Must run threshold sweep during demo preparation — don't hardcode 0.5.

4. **Calibration adequacy on small datasets** [verified risk]: Isotonic regression needs ~1000 calibration samples. If the demo synthetic dataset has fewer, use Platt scaling (`method='sigmoid'`) instead. The difference is rarely visible in a demo but calibration curve shape matters for the judge's technical review.

5. **SHAP version compatibility with LightGBM 4.6** [unverified]: SHAP 0.46.x added `TreeExplainer` updates for LightGBM 4.x API. Confirm `shap.TreeExplainer(model)` doesn't raise `LightGBMError` on `booster_.dump_model()`. Known to work on LightGBM ≥ 4.0; spot-test on 4.6 during setup.

6. **Multi-label vs. ordinal class design** [design choice not yet locked]: The 4-class ordinal formulation above is cleaner for explainability. An alternative is 5 separate binary classifiers (one per AI4I failure mode) with independent SMOTE + calibration. The multi-label approach gives richer `failure_modes` breakdown but complicates the alert aggregation. Recommendation: implement ordinal first (2 days), add per-mode binary classifiers as enhancement if time allows.

---

*Sources consulted: arXiv:2603.13343 (AI4I 2020 LightGBM AUC 0.973) · CMC v86n3/65500 (Two-stage LightGBM, Scania trucks) · MDPI Machines 13/8/663 (SMOTE+focal loss, 2025) · Springer "Enhancing predictive maintenance" (SMOTE+weighting, 2025) · LightGBM 4.6.0 release notes (lightgbm.readthedocs.io) · imbalanced-learn 0.14 changelog (imbalanced-learn.org) · tsfresh 0.21 docs (tsfresh.readthedocs.io) · Optuna LightGBM integration (optuna.org) · arXiv:2601.19944 (calibration at scale) · MDPI Future Internet 17/6/244 (conformal prediction for PdM, 2025)*
