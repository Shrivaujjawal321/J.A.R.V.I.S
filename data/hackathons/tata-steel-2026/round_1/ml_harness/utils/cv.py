"""Cross-validation split factories for classification, time-series, and grouped data."""

from __future__ import annotations

from typing import Generator

import numpy as np
from sklearn.model_selection import GroupKFold, StratifiedKFold, TimeSeriesSplit


def stratified_kfold(
    y: np.ndarray,
    n_splits: int = 5,
    seed: int = 42,
) -> Generator[tuple[np.ndarray, np.ndarray], None, None]:
    """Yield (train_idx, val_idx) using stratified splits — use for classification / image defect tracks."""
    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=seed)
    yield from skf.split(np.zeros(len(y)), y)


def timeseries_split(
    X: np.ndarray,
    n_splits: int = 5,
) -> Generator[tuple[np.ndarray, np.ndarray], None, None]:
    """Yield (train_idx, val_idx) using expanding-window splits — NO shuffle to prevent temporal leakage."""
    tss = TimeSeriesSplit(n_splits=n_splits)
    yield from tss.split(X)


def group_kfold(
    groups: np.ndarray,
    n_splits: int = 5,
) -> Generator[tuple[np.ndarray, np.ndarray], None, None]:
    """Yield (train_idx, val_idx) ensuring no group appears in both train and val — use when rows share a patient/unit ID."""
    gkf = GroupKFold(n_splits=n_splits)
    # GroupKFold.split needs an X placeholder and y; groups drives the split
    n = len(groups)
    yield from gkf.split(np.zeros(n), np.zeros(n), groups=groups)
