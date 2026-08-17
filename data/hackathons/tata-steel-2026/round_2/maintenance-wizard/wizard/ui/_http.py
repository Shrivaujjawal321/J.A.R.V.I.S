"""
wizard.ui._http
===============
Sync httpx.Client singleton — one per Streamlit session.

CRITICAL: Streamlit runs its own event loop (Starlette/Uvicorn in 1.58).
Using httpx.AsyncClient or asyncio.run() inside any Streamlit callback will
raise RuntimeError("This event loop is already running").

RULE: httpx.Client (sync) ONLY throughout wizard.ui.*. Never AsyncClient.

Usage::

    from wizard.ui._http import get_client

    def my_page():
        client = get_client()   # returns per-session singleton
        try:
            resp = client.get("/health", timeout=5)
            data = resp.json()
        except Exception as exc:
            st.warning(f"Backend unreachable: {exc}")
"""

from __future__ import annotations

import os

import httpx
import streamlit as st

# Read backend port from environment (BACKEND_PORT) or settings — fallback to 8000.
# This lets `BACKEND_PORT=8013 streamlit run wizard/ui/app.py` work for demos.
def _backend_base() -> str:
    port = os.environ.get("BACKEND_PORT", "")
    if not port:
        try:
            from wizard.core.config import settings
            port = str(settings.backend_port)
        except Exception:
            port = "8000"
    return f"http://localhost:{port}"

_BACKEND_BASE = _backend_base()
_DEFAULT_TIMEOUT = httpx.Timeout(connect=3.0, read=15.0, write=10.0, pool=5.0)


def get_client() -> httpx.Client:
    """
    Return a per-session httpx.Client singleton stored in st.session_state.

    - Keyed as 'wizard_http_client'
    - Created fresh if missing (first call per session)
    - base_url includes /v1 prefix matching FastAPI router mount
    - Sync ONLY — see module docstring for the asyncio constraint
    """
    if "wizard_http_client" not in st.session_state:
        st.session_state["wizard_http_client"] = httpx.Client(
            base_url=_BACKEND_BASE,
            timeout=_DEFAULT_TIMEOUT,
            headers={"Accept": "application/json", "Content-Type": "application/json"},
        )
    return st.session_state["wizard_http_client"]  # type: ignore[return-value]


def safe_get(path: str, params: dict | None = None) -> dict | list | None:
    """
    GET with error swallowing — returns None on any failure.
    Caller should display st.warning when None is returned.
    """
    client = get_client()
    try:
        resp = client.get(path, params=params)
        resp.raise_for_status()
        return resp.json()
    except Exception:
        return None


def safe_post(path: str, json_body: dict | None = None) -> dict | None:
    """
    POST with error swallowing — returns None on any failure.
    """
    client = get_client()
    try:
        resp = client.post(path, json=json_body or {})
        resp.raise_for_status()
        return resp.json()
    except Exception:
        return None


def safe_put(path: str, json_body: dict | None = None) -> dict | None:
    """
    PUT with error swallowing — returns None on any failure.
    """
    client = get_client()
    try:
        resp = client.put(path, json=json_body or {})
        resp.raise_for_status()
        return resp.json()
    except Exception:
        return None
