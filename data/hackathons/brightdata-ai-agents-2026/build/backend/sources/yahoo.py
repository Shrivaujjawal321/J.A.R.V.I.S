"""
backend/sources/yahoo.py
========================
Yahoo Finance source via yfinance (primary) with Tiingo REST fallback.

Returns a SourceResult with data containing:
    price           float
    change_pct_1d   float
    market_cap      float | None
    pe_ratio        float | None
    52w_high        float | None
    52w_low         float | None
    short_interest  float | None   (short interest as % of float)
    inst_ownership  float | None   (institutional ownership %)
    analyst_consensus str | None  (Strong Buy / Buy / Hold / Sell / Strong Sell)
    analyst_target  float | None
    volume_ratio    float | None   (today volume / avg 90d volume)
    company_name    str
    sector          str | None
    industry        str | None

Fallback: if yfinance returns stale/empty data or raises, we attempt Tiingo
via TIINGO_API_KEY env var. If that also fails, returns SourceStatus.ERROR
with a descriptive error_msg.

Both yfinance and Tiingo are synchronous HTTP clients; we run them in a
ThreadPoolExecutor to keep the asyncio event loop free.
"""
from __future__ import annotations

import asyncio
import logging
import os
import time
from concurrent.futures import ThreadPoolExecutor

from ..schemas import SourceResult, SourceStatus
from ..cache import ttl_cache
from ..observability import instrument

logger = logging.getLogger(__name__)

_EXECUTOR = ThreadPoolExecutor(max_workers=4, thread_name_prefix="yahoo_worker")
_TIINGO_KEY: str = os.getenv("TIINGO_API_KEY", "")


# ---------------------------------------------------------------------------
# Synchronous fetch helpers (run in executor)
# ---------------------------------------------------------------------------

def _fetch_yfinance(ticker: str) -> dict:
    """Synchronous yfinance fetch. Returns raw data dict."""
    import yfinance as yf  # type: ignore

    tkr = yf.Ticker(ticker)
    info = tkr.info or {}

    # Validate — yfinance sometimes returns an empty dict for bad tickers
    if not info.get("regularMarketPrice") and not info.get("currentPrice"):
        raise ValueError(f"yfinance returned no price data for {ticker}")

    price = info.get("currentPrice") or info.get("regularMarketPrice") or 0.0
    prev_close = info.get("previousClose") or info.get("regularMarketPreviousClose") or price
    change_pct = ((price - prev_close) / prev_close * 100) if prev_close else 0.0

    # Short interest as % float
    short_pct: float | None = None
    shares_short = info.get("sharesShort")
    float_shares = info.get("floatShares")
    if shares_short and float_shares and float_shares > 0:
        short_pct = round((shares_short / float_shares) * 100, 2)

    # Volume ratio today vs 90-day avg
    vol_ratio: float | None = None
    vol_today = info.get("regularMarketVolume")
    vol_avg = info.get("averageVolume") or info.get("averageVolume10days")
    if vol_today and vol_avg and vol_avg > 0:
        vol_ratio = round(vol_today / vol_avg, 2)

    return {
        "price": round(float(price), 2),
        "change_pct_1d": round(change_pct, 2),
        "market_cap": info.get("marketCap"),
        "pe_ratio": info.get("trailingPE") or info.get("forwardPE"),
        "52w_high": info.get("fiftyTwoWeekHigh"),
        "52w_low": info.get("fiftyTwoWeekLow"),
        "short_interest": short_pct,
        "inst_ownership": info.get("heldPercentInstitutions"),
        "analyst_consensus": info.get("recommendationKey", "").replace("_", " ").title() or None,
        "analyst_target": info.get("targetMeanPrice"),
        "volume_ratio": vol_ratio,
        "company_name": info.get("longName") or info.get("shortName") or ticker,
        "sector": info.get("sector"),
        "industry": info.get("industry"),
    }


def _fetch_tiingo(ticker: str) -> dict:
    """
    Synchronous Tiingo REST fetch as fallback.
    Requires TIINGO_API_KEY env var.
    """
    if not _TIINGO_KEY:
        raise ValueError("TIINGO_API_KEY not set — Tiingo fallback unavailable")

    import httpx  # already a dep from sec.py

    headers = {"Authorization": f"Token {_TIINGO_KEY}", "Content-Type": "application/json"}
    base = "https://api.tiingo.com"

    # Meta endpoint for company info
    meta_r = httpx.get(f"{base}/tiingo/daily/{ticker}", headers=headers, timeout=10.0)
    meta_r.raise_for_status()
    meta = meta_r.json()

    # Latest price
    price_r = httpx.get(
        f"{base}/tiingo/daily/{ticker}/prices",
        headers=headers,
        params={"startDate": "2020-01-01"},
        timeout=10.0,
    )
    price_r.raise_for_status()
    prices = price_r.json()
    if not prices:
        raise ValueError("Tiingo returned empty price list")

    latest = prices[-1]
    prev = prices[-2] if len(prices) >= 2 else latest

    price = latest.get("adjClose") or latest.get("close") or 0.0
    prev_price = prev.get("adjClose") or prev.get("close") or price
    change_pct = ((price - prev_price) / prev_price * 100) if prev_price else 0.0

    return {
        "price": round(float(price), 2),
        "change_pct_1d": round(change_pct, 2),
        "market_cap": None,
        "pe_ratio": None,
        "52w_high": None,
        "52w_low": None,
        "short_interest": None,
        "inst_ownership": None,
        "analyst_consensus": None,
        "analyst_target": None,
        "volume_ratio": None,
        "company_name": meta.get("name") or ticker,
        "sector": None,
        "industry": None,
    }


# ---------------------------------------------------------------------------
# Public async entry point
# ---------------------------------------------------------------------------

@instrument("yahoo")
@ttl_cache(ttl_seconds=3600)
async def fetch(ticker: str) -> SourceResult:
    """
    Async entry: fetches Yahoo Finance data, falls back to Tiingo.
    Cached 1h via ttl_cache decorator.
    """
    t0 = time.monotonic()
    ticker = ticker.upper().strip()
    loop = asyncio.get_event_loop()

    # Primary: yfinance
    data: dict | None = None
    error_msg: str | None = None

    try:
        data = await asyncio.wait_for(
            loop.run_in_executor(_EXECUTOR, _fetch_yfinance, ticker),
            timeout=12.0,
        )
    except asyncio.TimeoutError:
        error_msg = "yfinance timed out after 12s"
        logger.warning("yfinance timeout for %s", ticker)
    except Exception as exc:
        error_msg = f"yfinance error: {type(exc).__name__}: {exc}"
        logger.warning("yfinance failed for %s: %s", ticker, exc)

    # Fallback: Tiingo
    if data is None and _TIINGO_KEY:
        try:
            data = await asyncio.wait_for(
                loop.run_in_executor(_EXECUTOR, _fetch_tiingo, ticker),
                timeout=12.0,
            )
            logger.info("tiingo_fallback_used", extra={"ticker": ticker})
        except asyncio.TimeoutError:
            error_msg = (error_msg or "") + " | Tiingo timed out"
        except Exception as exc:
            error_msg = (error_msg or "") + f" | Tiingo error: {exc}"

    latency_ms = int((time.monotonic() - t0) * 1000)

    if data is None:
        return SourceResult(
            source="yahoo",
            status=SourceStatus.ERROR,
            error_msg=error_msg or "All Yahoo/Tiingo fetches failed",
            latency_ms=latency_ms,
        )

    return SourceResult(
        source="yahoo",
        status=SourceStatus.OK,
        data=data,
        latency_ms=latency_ms,
    )
