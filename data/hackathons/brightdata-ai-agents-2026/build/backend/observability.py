"""
backend/observability.py
========================
Structured logging (structlog) + optional Langfuse OTel hook.

Usage
-----
    from backend.observability import get_logger, configure_logging

    configure_logging()                 # call once at startup
    log = get_logger("sources.yahoo")
    log.info("fetch_complete", ticker="NVDA", latency_ms=143)

Environment variables
---------------------
    LOG_LEVEL          DEBUG | INFO | WARNING | ERROR  (default: INFO)
    LOG_JSON           1 = JSON output (prod), 0 = pretty console (dev)
    LANGFUSE_PUBLIC_KEY / LANGFUSE_SECRET_KEY  -- optional OTel hook
    LANGFUSE_HOST      default https://cloud.langfuse.com
"""
from __future__ import annotations

import logging
import os
import sys
import time
from functools import wraps
from typing import Any, Callable, TypeVar

import structlog

# ---------------------------------------------------------------------------
# Type alias
# ---------------------------------------------------------------------------
F = TypeVar("F", bound=Callable[..., Any])

# ---------------------------------------------------------------------------
# Module-level flag so configure_logging() is idempotent
# ---------------------------------------------------------------------------
_configured = False


def configure_logging() -> None:
    """
    Configure structlog once. Call from FastAPI lifespan / startup event.
    Safe to call multiple times — subsequent calls are no-ops.
    """
    global _configured
    if _configured:
        return

    log_level_str = os.getenv("LOG_LEVEL", "INFO").upper()
    log_level = getattr(logging, log_level_str, logging.INFO)

    json_mode = os.getenv("LOG_JSON", "0") == "1"

    # Standard library root logger
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=log_level,
    )

    # Silence noisy libraries in prod
    for noisy in ("httpx", "httpcore", "asyncio", "urllib3"):
        logging.getLogger(noisy).setLevel(logging.WARNING)

    shared_processors: list[Any] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.StackInfoRenderer(),
    ]

    if json_mode:
        shared_processors.append(structlog.processors.format_exc_info)
        renderer: Any = structlog.processors.JSONRenderer()
    else:
        renderer = structlog.dev.ConsoleRenderer(colors=True)

    structlog.configure(
        processors=[
            *shared_processors,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    formatter = structlog.stdlib.ProcessorFormatter(
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            renderer,
        ],
        foreign_pre_chain=shared_processors,
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(log_level)

    _configured = True

    # Optional Langfuse OTel setup
    _maybe_configure_langfuse()


def _maybe_configure_langfuse() -> None:
    """
    If LANGFUSE_PUBLIC_KEY is set, configure Langfuse as an OTel exporter.
    Silently skips if langfuse SDK is not installed.
    """
    pub_key = os.getenv("LANGFUSE_PUBLIC_KEY", "")
    sec_key = os.getenv("LANGFUSE_SECRET_KEY", "")
    if not pub_key or not sec_key:
        return

    try:
        from langfuse import Langfuse  # type: ignore
        host = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
        _lf = Langfuse(public_key=pub_key, secret_key=sec_key, host=host)
        log = get_logger("observability")
        log.info("langfuse_connected", host=host)
    except ImportError:
        pass  # langfuse not installed — silent
    except Exception as exc:
        get_logger("observability").warning("langfuse_init_failed", error=str(exc))


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """
    Return a structlog BoundLogger bound to `name`.

    Example::

        log = get_logger("sources.yahoo")
        log = log.bind(ticker="NVDA", request_id="abc123")
        log.info("fetch_started")
    """
    return structlog.get_logger(name)


# ---------------------------------------------------------------------------
# Decorator: log + time any async function automatically
# ---------------------------------------------------------------------------

def instrument(source_name: str) -> Callable[[F], F]:
    """
    Decorator for source fetch functions.
    Logs start/complete/error with latency_ms automatically.

    Usage::

        @instrument("yahoo")
        async def fetch(ticker: str) -> SourceResult:
            ...
    """
    def decorator(fn: F) -> F:
        log = get_logger(f"sources.{source_name}")

        @wraps(fn)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            ticker = args[0] if args else kwargs.get("ticker", "?")
            bound = log.bind(source=source_name, ticker=ticker)
            t0 = time.monotonic()
            bound.debug("fetch_started")
            try:
                result = await fn(*args, **kwargs)
                latency_ms = int((time.monotonic() - t0) * 1000)
                status = getattr(result, "status", "unknown")
                bound.info(
                    "fetch_complete",
                    latency_ms=latency_ms,
                    status=str(status),
                )
                return result
            except Exception as exc:
                latency_ms = int((time.monotonic() - t0) * 1000)
                bound.error(
                    "fetch_error",
                    latency_ms=latency_ms,
                    error=str(exc),
                    exc_info=True,
                )
                raise

        return wrapper  # type: ignore[return-value]

    return decorator
