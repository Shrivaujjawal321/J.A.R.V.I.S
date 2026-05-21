"""Ensemble combiners for OOF predictions: simple average, weighted average, rank average."""

from __future__ import annotations

import numpy as np
from scipy.stats import rankdata


def simple_average(predictions: list[np.ndarray]) -> np.ndarray:
    """Average a list of prediction arrays element-wise.

    Accepts 1-D (regression scores) or 2-D (class probabilities, shape [n, n_classes]).
    All arrays must share the same shape.
    """
    if not predictions:
        raise ValueError("predictions list is empty")
    stacked = np.stack([np.asarray(p, dtype=float) for p in predictions], axis=0)
    return stacked.mean(axis=0)


def weighted_average(
    predictions: list[np.ndarray],
    weights: list[float],
) -> np.ndarray:
    """Weighted average of prediction arrays; weights are auto-normalised to sum=1.

    Accepts 1-D or 2-D arrays — same shape requirement as simple_average.
    """
    if not predictions:
        raise ValueError("predictions list is empty")
    if len(predictions) != len(weights):
        raise ValueError(
            f"Length mismatch: {len(predictions)} predictions vs {len(weights)} weights"
        )
    w = np.asarray(weights, dtype=float)
    if w.sum() == 0:
        raise ValueError("weights must not all be zero")
    w = w / w.sum()

    arrs = [np.asarray(p, dtype=float) for p in predictions]
    # broadcast weights over the array dimensions
    if arrs[0].ndim == 1:
        return sum(wi * arr for wi, arr in zip(w, arrs))  # type: ignore[return-value]
    # 2-D: weight per model, keep class axis
    return sum(wi * arr for wi, arr in zip(w, arrs))  # type: ignore[return-value]


def rank_average(predictions: list[np.ndarray]) -> np.ndarray:
    """Rank-transform each prediction array then average the ranks.

    For 1-D arrays: rank each model's predictions, then average.
    For 2-D arrays (class probs): rank within each column independently, then average.
    Robust to scale differences between models (e.g. tree scores vs NN logits).
    """
    if not predictions:
        raise ValueError("predictions list is empty")

    arrs = [np.asarray(p, dtype=float) for p in predictions]
    ndim = arrs[0].ndim

    if ndim == 1:
        ranked = [rankdata(a) for a in arrs]
        return np.stack(ranked, axis=0).mean(axis=0)

    # 2-D: rank each column (class) across samples for every model
    ranked_list = []
    for a in arrs:
        ranked_cols = np.column_stack([rankdata(a[:, c]) for c in range(a.shape[1])])
        ranked_list.append(ranked_cols)
    return np.stack(ranked_list, axis=0).mean(axis=0)
