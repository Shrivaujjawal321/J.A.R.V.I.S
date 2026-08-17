"""
wizard.ml.registry
==================
Lazy singleton model artifact loader.

All ML inference wrappers call ``ModelRegistry.load(key)`` rather than
opening joblib files themselves.  This ensures:

  - Artifacts are loaded once (cold-start safe).
  - Missing artifact → graceful fallback (no server crash).
  - Any module can replace an artifact by calling ``registry.register(key, obj)``.

Usage::

    from wizard.ml.registry import ModelRegistry

    model = ModelRegistry.load("rul_bearing")           # -> WeibullAFTFitter | None
    ModelRegistry.register("rul_bearing", fitted_model) # testing / hot-swap
"""

from __future__ import annotations

import logging
import threading
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

_LOCK = threading.Lock()
_CACHE: Dict[str, Any] = {}


def _models_dir() -> Path:
    """Resolve data/models/ relative to repo root."""
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "pyproject.toml").exists():
            return parent / "data" / "models"
    return Path.cwd() / "data" / "models"


class ModelRegistry:
    """Thread-safe lazy loader for joblib / torch checkpoint artifacts."""

    @staticmethod
    def load(key: str, fallback: Any = None) -> Any:
        """
        Load artifact from data/models/<key>.pkl if not already cached.

        Parameters
        ----------
        key : str
            Artifact name without extension (e.g. 'rul_bearing').
        fallback : Any
            Return value if file does not exist (instead of crashing).

        Returns
        -------
        Loaded object or ``fallback``.
        """
        with _LOCK:
            if key in _CACHE:
                return _CACHE[key]

            path = _models_dir() / f"{key}.pkl"
            if not path.exists():
                logger.warning(
                    "ModelRegistry: artifact not found — %s  (fallback mode)", path
                )
                return fallback

            try:
                import joblib  # type: ignore[import]
                obj = joblib.load(path)
                _CACHE[key] = obj
                logger.info("ModelRegistry: loaded %s from %s", key, path)
                return obj
            except Exception as exc:  # pragma: no cover
                logger.error("ModelRegistry: failed to load %s — %s", key, exc)
                return fallback

    @staticmethod
    def register(key: str, obj: Any) -> None:
        """
        Manually register an artifact (used in tests / hot-swap).
        Overwrites any cached value for ``key``.
        """
        with _LOCK:
            _CACHE[key] = obj
            logger.debug("ModelRegistry: registered %s in-memory", key)

    @staticmethod
    def clear(key: Optional[str] = None) -> None:
        """Clear one or all cached artifacts (useful in tests)."""
        with _LOCK:
            if key is None:
                _CACHE.clear()
            else:
                _CACHE.pop(key, None)

    @staticmethod
    def is_loaded(key: str) -> bool:
        with _LOCK:
            return key in _CACHE
