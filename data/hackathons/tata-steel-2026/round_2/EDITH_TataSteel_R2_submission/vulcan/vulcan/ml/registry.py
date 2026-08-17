"""VULCAN model registry — lazy, thread-safe joblib artifact loader.

Artifacts live in `vulcan/data/models/`. Missing artifact -> graceful `fallback`
(never crashes inference). Ported from the proven wizard registry, repointed at
the VULCAN package data dir.
"""

from __future__ import annotations

import logging
import threading
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)

_LOCK = threading.Lock()
_CACHE: dict[str, Any] = {}


def models_dir() -> Path:
    """`<project>/data/models/` — aligned with config.package_root so RAG, ML and
    the demo cache all share ONE canonical data dir (the outer `vulcan/data/`)."""
    from ..config import get_settings
    d = get_settings().package_root / "data" / "models"
    d.mkdir(parents=True, exist_ok=True)
    return d


class ModelRegistry:
    @staticmethod
    def load(key: str, fallback: Any = None) -> Any:
        with _LOCK:
            if key in _CACHE:
                return _CACHE[key]
            path = models_dir() / f"{key}.pkl"
            if not path.exists():
                logger.debug("ModelRegistry: %s not found (fallback).", path)
                return fallback
            try:
                import joblib  # type: ignore[import]
                obj = joblib.load(path)
                _CACHE[key] = obj
                return obj
            except Exception as exc:  # noqa: BLE001
                logger.error("ModelRegistry: failed to load %s — %s", key, exc)
                return fallback

    @staticmethod
    def save(key: str, obj: Any) -> Path:
        import joblib  # type: ignore[import]
        path = models_dir() / f"{key}.pkl"
        joblib.dump(obj, path)
        with _LOCK:
            _CACHE[key] = obj
        return path

    @staticmethod
    def register(key: str, obj: Any) -> None:
        with _LOCK:
            _CACHE[key] = obj

    @staticmethod
    def clear(key: Optional[str] = None) -> None:
        with _LOCK:
            if key is None:
                _CACHE.clear()
            else:
                _CACHE.pop(key, None)
