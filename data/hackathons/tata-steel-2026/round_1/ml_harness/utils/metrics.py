"""Pluggable metric matcher — maps (task_type, metric_name) to a callable (y_true, y_pred) -> float."""

from __future__ import annotations

from typing import Callable, Literal

import numpy as np
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    roc_auc_score,
)

TaskType = Literal["classification", "regression", "segmentation"]

# ── per-task defaults ──────────────────────────────────────────────────────────
_DEFAULTS: dict[TaskType, str] = {
    "classification": "f1_macro",
    "regression": "rmse",
    "segmentation": "dice",
}


# ── metric implementations ─────────────────────────────────────────────────────

def _rmse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return float(np.sqrt(mean_squared_error(y_true, y_pred)))


def _mae(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return float(mean_absolute_error(y_true, y_pred))


def _mape(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    mask = y_true != 0
    return float(np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100)


def _dice(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Dice coefficient for binary masks — both arrays expected as float in [0, 1] or int {0, 1}."""
    y_true = np.asarray(y_true, dtype=float).ravel()
    y_pred = np.asarray(y_pred, dtype=float).ravel()
    intersection = (y_true * y_pred).sum()
    denom = y_true.sum() + y_pred.sum()
    return float(2.0 * intersection / denom) if denom > 0 else 1.0


def _map_at_k(k: int = 5) -> Callable[[np.ndarray, np.ndarray], float]:
    """Returns a MAP@K callable. y_pred should be (n_samples, n_classes) probability matrix."""

    def _fn(y_true: np.ndarray, y_pred: np.ndarray) -> float:
        y_true = np.asarray(y_true)
        y_pred = np.asarray(y_pred)
        n = len(y_true)
        ap_sum = 0.0
        for i in range(n):
            top_k = np.argsort(y_pred[i])[::-1][:k]
            hits = [1 if top_k[j] == y_true[i] else 0 for j in range(len(top_k))]
            precisions = [
                sum(hits[: r + 1]) / (r + 1) for r in range(len(hits)) if hits[r]
            ]
            ap_sum += (sum(precisions) / 1.0) if precisions else 0.0
        return ap_sum / n

    return _fn


def _f1_macro(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return float(f1_score(y_true, y_pred, average="macro", zero_division=0))


def _f1_weighted(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return float(f1_score(y_true, y_pred, average="weighted", zero_division=0))


def _roc_auc(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Works for binary (1-D scores) and multiclass (2-D probs, OvR)."""
    y_pred = np.asarray(y_pred)
    if y_pred.ndim == 2:
        return float(roc_auc_score(y_true, y_pred, multi_class="ovr"))
    return float(roc_auc_score(y_true, y_pred))


_REGISTRY: dict[str, Callable] = {
    "accuracy": accuracy_score,
    "f1_macro": _f1_macro,
    "f1_weighted": _f1_weighted,
    "roc_auc": _roc_auc,
    "rmse": _rmse,
    "mae": _mae,
    "mape": _mape,
    "dice": _dice,
    "map_at_5": _map_at_k(5),
    "map_at_k": _map_at_k(5),  # default k=5; call _map_at_k(k) directly if needed
}


def get_metric(
    task_type: TaskType,
    metric_name: str | None = None,
) -> Callable[[np.ndarray, np.ndarray], float]:
    """Return a (y_true, y_pred) -> float callable for the given task and metric name.

    If metric_name is None, returns the default metric for task_type.
    Raises ValueError for unknown names.
    """
    name = metric_name or _DEFAULTS[task_type]
    if name not in _REGISTRY:
        raise ValueError(
            f"Unknown metric '{name}'. Available: {sorted(_REGISTRY.keys())}"
        )
    return _REGISTRY[name]
