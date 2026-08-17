"""
backend/sources/__init__.py
===========================
Registry of all 8 data source fetch functions.

Each fetch function has signature:
    async def fetch(ticker: str) -> SourceResult

The orchestrator imports these via the SOURCES constant.
"""
from __future__ import annotations

from .sec import fetch as fetch_sec
from .yahoo import fetch as fetch_yahoo
from .news import fetch as fetch_news
from .reddit import fetch as fetch_reddit
from .linkedin import fetch as fetch_linkedin
from .glassdoor import fetch as fetch_glassdoor
from .gdelt import fetch as fetch_gdelt
from .satellite import fetch as fetch_satellite

__all__ = [
    "fetch_sec",
    "fetch_yahoo",
    "fetch_news",
    "fetch_reddit",
    "fetch_linkedin",
    "fetch_glassdoor",
    "fetch_gdelt",
    "fetch_satellite",
]
