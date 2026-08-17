"""
wizard.ml
=========
Machine-learning layer for the Maintenance Wizard.

Public inference API (imported by wizard.agents and wizard.backend):

    from wizard.ml import predict_rul, get_anomaly_score, predict_failure, rca_analyze

Each function is thin — loads a joblib artifact once at first call (singleton),
runs fast CPU inference, returns a typed schema model from wizard.core.schemas.

Sub-modules
-----------
  rul_estimator.py     -- WeibullAFT + degradation index + Bayesian correction -> RULResult
  anomaly_detector.py  -- IsolationForest + LSTM-AE + adaptive threshold -> AnomalyScore
  failure_predictor.py -- LightGBM 4-class ordinal + isotonic calibration -> FailurePrediction
  rca_engine.py        -- 3-layer RCA (NetworkX + DoWhy GCM + LLM 5-whys) -> RCAResult
  feature_utils.py     -- Shared sliding-window feature extraction utilities
  registry.py          -- Lazy model artifact loader (singleton per model key)

Training scripts (offline, not imported by server):
  scripts/train_rul.py
  scripts/train_anomaly.py
  scripts/train_failure.py
  scripts/train_rca_gcm.py
"""

from __future__ import annotations

from wizard.ml.rul_estimator import predict_rul, apply_engineer_correction as apply_rul_correction
from wizard.ml.anomaly_detector import get_anomaly_score
from wizard.ml.failure_predictor import predict_failure
from wizard.ml.rca_engine import rca_analyze

__all__ = [
    "predict_rul",
    "apply_rul_correction",
    "get_anomaly_score",
    "predict_failure",
    "rca_analyze",
]
