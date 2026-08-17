# wizard.ml — Machine Learning Layer

Production ML inference layer for the Maintenance Wizard.
All four inference functions are CPU-only, artifact-loaded, and return typed schema models.

## Module map

| File | Responsibility |
|---|---|
| `__init__.py` | Public re-exports: `predict_rul`, `get_anomaly_score`, `predict_failure`, `rca_analyze` |
| `registry.py` | Thread-safe lazy joblib artifact loader (singleton per key) |
| `feature_utils.py` | Sliding-window feature extraction, degradation index, sensor vector builder |
| `rul_estimator.py` | WeibullAFT + degradation index + Bayesian engineer correction → `RULResult` |
| `anomaly_detector.py` | IsolationForest + LSTM-AE + River HST + adaptive threshold + SHAP → anomaly dict |
| `failure_predictor.py` | LightGBM 4-class ordinal + isotonic calibration + SHAP → failure dict |
| `rca_engine.py` | 3-layer RCA (NetworkX FMEA + DoWhy GCM + LLM 5-whys with CauseChainValidator) → `RCAResult` |
| `smoke_ml.py` | Self-contained smoke test (no network, mock artifacts, < 30s) |

## Inference API

```python
from wizard.ml import predict_rul, get_anomaly_score, predict_failure, rca_analyze

# RUL prediction
from wizard.core.schemas import RULResult
result: RULResult = predict_rul(
    asset_id="EAF-04",
    sensor_readings={"temperature_c": 420.0, "vibration_mm_s": 3.5, ...},
    sensor_summary_id="SS-12345",
    equipment_class="bearing",
)
# result.rul_days_p10 / .p50 / .p90, .degradation_index, .risk_class (field on RULResult)

# Anomaly score
score_dict = get_anomaly_score(
    asset_id="EAF-04",
    sensor_readings={...},
    readings_history=[{...}, ...],  # ordered oldest→newest
    equipment_class="bearing",
)
# score_dict["score"], ["severity"], ["shap_values"], ["triggered_sensors"]

# Failure prediction
fail_dict = predict_failure(
    asset_id="EAF-04",
    sensor_readings={...},
    readings_history=[...],
    equipment_class="bearing",
    rul_days_p50=8.0,    # from predict_rul
    anomaly_score=0.72,  # from get_anomaly_score
)
# fail_dict["alert_class"]  -> NORMAL|WARN_72H|WARN_24H|IMMINENT
# fail_dict["probabilities"], ["top_shap_features"], ["failure_modes"]

# RCA
from wizard.core.schemas import RCAResult
rca: RCAResult = rca_analyze(
    asset_id="EAF-04",
    fault_log_id="FL-001",
    fault_code="WRD",
    fault_description="Work roll degradation",
    sensor_df=sensor_dataframe,      # pd.DataFrame, 24h window
    context_chunks=["SOP §3.4 ..."], # from RAG layer
    anomaly_scores={"vibration_mm_s": 0.82},
)
# rca.cause_chain (List[CauseChainStep]), .root_cause_summary, .five_whys, .gcm_attributions
```

## Engineer feedback / Bayesian RUL correction

```python
from wizard.ml import apply_rul_correction

apply_rul_correction(asset_id="EAF-04", engineer_rul_days=5.0)
# Persisted to data/feedback/rul_corrections.jsonl
# Replayed on server restart
# Effect: next predict_rul → 0.7 * model_rul + 0.3 * 5.0
```

## Offline training

Train all models in one command (safe offline with --synthetic-only):

```bash
# Offline (synthetic data, no network):
python scripts/train_ml_models.py --synthetic-only

# With real datasets (requires internet + ~200MB download):
python scripts/train_ml_models.py --use-cmapss --use-ai4i --epochs 20

# Single equipment class:
python scripts/train_ml_models.py --subset bearing --synthetic-only
```

Artifacts are written to `data/models/`. The server loads them lazily on first call.

## Smoke test

```bash
python wizard/ml/smoke_ml.py
# Expected: "All smoke tests PASSED." + exit 0
```

## Graceful degradation

All four inference functions degrade gracefully when artifacts are missing:

| Condition | Behavior |
|---|---|
| No WeibullAFT artifact | Falls back to population WeibullFitter; if also missing → stub RULResult |
| No IsolationForest | Head A disabled; fused score = LSTM-AE score only |
| No LSTM-AE | Head B disabled; fused score = IF score only |
| No LightGBM | Returns NORMAL class stub with calibrated=False |
| No DoWhy | RCA Layer 2 uses anomaly_scores mapping as fallback attribution |
| LLM offline | RCA Layer 3 returns empty five_whys; Layer 1+2 chain still returned |

This means the server NEVER crashes on missing artifacts — safe for demo day.

## Heavy dependencies (not pre-installed)

See `MASTER_BRIEF §2` for pinned versions. This module requires:

```
lifelines==0.30.*
scikit-learn==1.5.*
lightgbm==4.6.0
torch==2.3.* (CPU wheel)
shap==0.45.*
river==0.21.*
dowhy==0.12
networkx==3.3
tsfresh==0.21.0
imbalanced-learn==0.14.*
joblib==1.4.*
pandas==2.2.*
numpy==1.26.*
litellm==1.45.*
```

Install: `pip install -r requirements.txt` (all pinned in repo root `requirements.txt`).
