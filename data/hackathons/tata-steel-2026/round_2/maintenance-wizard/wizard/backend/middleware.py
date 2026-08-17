"""
wizard.backend.middleware
=========================
Cross-cutting concerns for the FastAPI backend:

1. Correlation ID middleware — per-request UUID bound to structlog context.
   Replaces asgi-correlation-id (not in requirements.txt) with a zero-dep
   implementation using contextvars + Starlette BaseHTTPMiddleware.

2. Structlog configuration — JSON-structured logs with correlation_id,
   agent_step, equipment_id, latency_ms fields for demo traceability.

3. AsyncCircuitBreaker — minimal async-native circuit breaker protecting
   LLM calls. Uses pybreaker's state constants for display but manages
   state in-process (avoids pybreaker's sync-lock conflicts with asyncio).

Usage in app.py::

    from wizard.backend.middleware import (
        configure_structlog,
        CorrelationIdMiddleware,
        llm_circuit_breaker,
        get_request_id,
    )
"""
from __future__ import annotations

import asyncio
import contextvars
import time
import uuid
from typing import Any, Callable, Optional

import structlog
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp

# ---------------------------------------------------------------------------
# 1. Correlation ID context var
# ---------------------------------------------------------------------------

_request_id_var: contextvars.ContextVar[str] = contextvars.ContextVar(
    "request_id", default="no-request"
)


def get_request_id() -> str:
    """Return the current request's correlation ID (or 'no-request' if outside a request)."""
    return _request_id_var.get()


def set_request_id(request_id: str) -> None:
    """Bind a correlation ID to the current async context."""
    _request_id_var.set(request_id)


# ---------------------------------------------------------------------------
# 2. Middleware
# ---------------------------------------------------------------------------

class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """
    Per-request correlation ID middleware.

    - Reads 'X-Request-ID' header if present; generates UUID4 otherwise.
    - Sets 'X-Request-ID' response header.
    - Binds the ID to the structlog context for the lifetime of the request.
    """

    HEADER_NAME = "X-Request-ID"

    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        request_id = request.headers.get(self.HEADER_NAME) or str(uuid.uuid4())
        set_request_id(request_id)

        # Bind to structlog contextvars so all log calls in this request carry it
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(
            request_id=request_id,
            method=request.method,
            path=request.url.path,
        )

        start = time.monotonic()
        response = await call_next(request)
        latency_ms = round((time.monotonic() - start) * 1000, 2)

        structlog.contextvars.bind_contextvars(
            status_code=response.status_code,
            latency_ms=latency_ms,
        )
        _log = structlog.get_logger(__name__)
        _log.info("http_request_complete")

        response.headers[self.HEADER_NAME] = request_id
        return response


# ---------------------------------------------------------------------------
# 3. Structlog configuration
# ---------------------------------------------------------------------------

def configure_structlog() -> None:
    """
    Configure structlog for JSON-structured logging.
    Call once at app startup (idempotent — safe to call multiple times).

    Log fields per request:
      request_id, method, path, status_code, latency_ms,
      agent_step, tool_called, equipment_id, llm_provider, retry_count

    NOTE: structlog.stdlib.add_logger_name is intentionally omitted because it
    calls ``logger.name`` on the underlying logger object. PrintLoggerFactory
    returns PrintLogger which has no ``.name`` attribute — adding that processor
    raises AttributeError on every log call, which crashes the lifespan before
    the application can serve any requests.  The logger identity is already
    carried via the structlog.get_logger(__name__) binding.
    """
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


# ---------------------------------------------------------------------------
# 4. Async Circuit Breaker
# ---------------------------------------------------------------------------

class CircuitOpenError(Exception):
    """Raised when the circuit breaker is in OPEN state."""

    def __init__(self, resets_in_seconds: float) -> None:
        self.resets_in_seconds = resets_in_seconds
        super().__init__(
            f"LLM circuit breaker OPEN — resets in {resets_in_seconds:.0f}s"
        )


class AsyncCircuitBreaker:
    """
    Minimal async-native circuit breaker.

    States:
      CLOSED   — normal operation, failures counted
      OPEN     — all calls rejected immediately, no LLM traffic
      HALF_OPEN — one probe allowed; if it succeeds → CLOSED, else → OPEN

    Protects LLM calls from cascading failures.
    On OPEN: raises CircuitOpenError → caller returns 503 with ErrorEnvelope.
    """

    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

    def __init__(self, fail_max: int = 5, reset_timeout: float = 60.0) -> None:
        self._fail_max = fail_max
        self._reset_timeout = reset_timeout
        self._fail_count: int = 0
        self._opened_at: Optional[float] = None
        self._state: str = self.CLOSED
        self._lock = asyncio.Lock()
        self._half_open_probe_in_flight: bool = False

    @property
    def state(self) -> str:
        """Compute effective state (respects HALF_OPEN transition from elapsed time)."""
        if self._state == self.OPEN:
            if self._opened_at is not None:
                elapsed = time.monotonic() - self._opened_at
                if elapsed >= self._reset_timeout:
                    return self.HALF_OPEN
        return self._state

    def seconds_until_reset(self) -> float:
        """Seconds until OPEN → HALF_OPEN transition; 0 if already CLOSED/HALF_OPEN."""
        if self._state == self.OPEN and self._opened_at is not None:
            remaining = self._reset_timeout - (time.monotonic() - self._opened_at)
            return max(0.0, remaining)
        return 0.0

    async def call(
        self,
        coro_factory: Callable[[], Any],
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """
        Execute ``coro_factory()`` (which must return an awaitable) with
        circuit breaker protection.

        Usage::

            result = await llm_circuit_breaker.call(
                lambda: litellm.acompletion(model=..., messages=...)
            )
        """
        current_state = self.state

        if current_state == self.OPEN:
            raise CircuitOpenError(self.seconds_until_reset())

        if current_state == self.HALF_OPEN:
            # Only allow one probe at a time
            async with self._lock:
                if self._half_open_probe_in_flight:
                    raise CircuitOpenError(0.0)
                self._half_open_probe_in_flight = True

        try:
            result = await coro_factory(*args, **kwargs)
            # Success — reset
            async with self._lock:
                self._fail_count = 0
                self._state = self.CLOSED
                self._half_open_probe_in_flight = False
            return result
        except Exception:
            async with self._lock:
                self._fail_count += 1
                self._half_open_probe_in_flight = False
                if self._fail_count >= self._fail_max:
                    self._state = self.OPEN
                    self._opened_at = time.monotonic()
            raise


# ---------------------------------------------------------------------------
# 5. Module-level singletons — imported by app.py and wrps.py
# ---------------------------------------------------------------------------

# Configure structlog immediately on import so sub-module loggers pick it up
configure_structlog()

# LLM circuit breaker singleton — shared across all LLM call sites
# Fail-max / reset-timeout overridden at lifespan startup from settings
llm_circuit_breaker = AsyncCircuitBreaker(fail_max=5, reset_timeout=60.0)

log = structlog.get_logger(__name__)
