"""VULCAN ML — fault classifier + anomaly detector + RUL estimator (CPU, keyless).

Trained on the steel-native dense per-equipment sensor tables + RUL trajectories.
Artifacts persist in vulcan/data/models/ via ModelRegistry; inference is fail-soft.
"""

from .registry import ModelRegistry, models_dir
from .models import (
    train_all, train_rul, train_equipment_class,
    predict_fault, anomaly_score, estimate_rul,
    FAULT_CLASSES,
)

__all__ = [
    "ModelRegistry", "models_dir",
    "train_all", "train_rul", "train_equipment_class",
    "predict_fault", "anomaly_score", "estimate_rul",
    "FAULT_CLASSES",
]
