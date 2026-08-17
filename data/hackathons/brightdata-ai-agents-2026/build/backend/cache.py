"""File-based TTL cache. Survives process restarts. Zero infra."""
from __future__ import annotations

import json
import time
from functools import wraps
from pathlib import Path
from typing import Awaitable, Callable, Any

CACHE_DIR = Path(__file__).parent.parent / ".cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

DEFAULT_TTL = 3600  # 1 hour


def ttl_cache(ttl_seconds: int = DEFAULT_TTL):
    """Decorator: cache async function results to JSON file with TTL."""

    def decorator(fn: Callable[..., Awaitable[Any]]):
        @wraps(fn)
        async def wrapper(ticker: str, *args, **kwargs):
            key = f"{fn.__module__}.{fn.__name__}__{ticker}.json"
            path = CACHE_DIR / key
            if path.exists():
                try:
                    payload = json.loads(path.read_text())
                    if time.time() - payload["ts"] < ttl_seconds:
                        return payload["result"]
                except Exception:
                    pass  # corrupt cache → recompute
            result = await fn(ticker, *args, **kwargs)
            try:
                path.write_text(json.dumps({"ts": time.time(), "result": result}, default=str))
            except Exception:
                pass  # non-serialisable result → skip cache, don't fail
            return result

        return wrapper

    return decorator


def cache_exists(ticker: str, source_name: str, ttl_seconds: int = DEFAULT_TTL) -> bool:
    """Quick check used by orchestrator to mark `cached=True` in SourceResult."""
    for p in CACHE_DIR.glob(f"*{source_name}*__{ticker}.json"):
        try:
            payload = json.loads(p.read_text())
            if time.time() - payload["ts"] < ttl_seconds:
                return True
        except Exception:
            continue
    return False
