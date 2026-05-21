"""Generic Optuna study wrapper with MedianPruner and clean logging."""

from __future__ import annotations

import logging
from typing import Any, Callable

import optuna


def run_study(
    objective_fn: Callable[[optuna.Trial], float],
    n_trials: int = 50,
    direction: str = "maximize",
    timeout: float | None = None,
    study_name: str | None = None,
    storage: str | None = None,
    verbose: bool = False,
) -> tuple[dict[str, Any], float, optuna.Study]:
    """Run an Optuna hyperparameter search and return (best_params, best_value, study).

    Args:
        objective_fn: A callable that accepts an optuna.Trial and returns a float score.
        n_trials:     Number of trials to run (ignored if timeout is hit first).
        direction:    "maximize" or "minimize".
        timeout:      Optional wall-clock limit in seconds.
        study_name:   Name for the study (auto-generated if None).
        storage:      Optuna storage URL (e.g. "sqlite:///optuna.db"). None = in-memory.
        verbose:      If False, suppresses Optuna's per-trial INFO logs.

    Returns:
        (best_params, best_value, study)
    """
    if not verbose:
        optuna.logging.set_verbosity(optuna.logging.WARNING)
        logging.getLogger("optuna").setLevel(logging.WARNING)

    pruner = optuna.pruners.MedianPruner(n_startup_trials=5, n_warmup_steps=0)

    sampler = optuna.samplers.TPESampler(seed=42)

    study = optuna.create_study(
        direction=direction,
        study_name=study_name,
        storage=storage,
        pruner=pruner,
        sampler=sampler,
    )

    study.optimize(
        objective_fn,
        n_trials=n_trials,
        timeout=timeout,
        show_progress_bar=False,
    )

    return study.best_params, study.best_value, study
