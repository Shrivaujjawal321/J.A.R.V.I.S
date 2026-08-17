"""
backend/sources/fred.py
========================
FRED macro context source.

Fetches three macro indicators that contextualise the investment brief:
    1. 10-Year Treasury yield (DGS10) — risk-free rate proxy
    2. VIX (VIXCLS) — market fear gauge
    3. Sector ETF 90-day performance — sector-relative context

FRED API is free, no key required for public series.
Sector ETF data from yfinance (free).

Returns SourceResult.data = {
    "treasury_10y":     float   (latest value, %)
    "vix":              float   (latest value)
    "treasury_trend":   str     ("rising" | "falling" | "stable")
    "vix_regime":       str     ("low" | "moderate" | "high" | "extreme")
    "sector_etf":       str     (ETF ticker, e.g. "XLK")
    "sector_perf_90d":  float   (% return last 90d)
    "macro_summary":    str     (one-sentence context for synthesizer)
}
"""
from __future__ import annotations

import asyncio
import logging
import time
from concurrent.futures import ThreadPoolExecutor

from ..schemas import SourceResult, SourceStatus
from ..cache import ttl_cache
from ..observability import instrument

logger = logging.getLogger(__name__)

_EXECUTOR = ThreadPoolExecutor(max_workers=2, thread_name_prefix="fred_worker")

# FRED series endpoints (no key needed for public series)
_FRED_BASE = "https://fred.stlouisfed.org/graph/fredgraph.csv?id="
_FRED_JSON = "https://api.stlouisfed.org/fred/series/observations"

# Map sector name to ETF ticker
_SECTOR_ETF_MAP: dict[str, str] = {
    "Technology": "XLK",
    "Information Technology": "XLK",
    "Healthcare": "XLV",
    "Health Care": "XLV",
    "Financials": "XLF",
    "Energy": "XLE",
    "Consumer Discretionary": "XLY",
    "Consumer Staples": "XLP",
    "Industrials": "XLI",
    "Materials": "XLB",
    "Real Estate": "XLRE",
    "Communication Services": "XLC",
    "Utilities": "XLU",
}
_DEFAULT_ETF = "SPY"  # fallback if sector unknown


def _fetch_fred_series(series_id: str) -> list[tuple[str, float]]:
    """
    Fetch a FRED series as (date, value) pairs via the public CSV endpoint.
    Returns the last 90 observations.
    """
    import httpx

    # FRED public API — no key for this CSV endpoint
    url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}"
    resp = httpx.get(url, timeout=15.0, headers={"User-Agent": "AltBrief/1.0"})
    resp.raise_for_status()

    rows: list[tuple[str, float]] = []
    for line in resp.text.strip().splitlines()[1:]:  # skip header
        parts = line.split(",")
        if len(parts) != 2:
            continue
        date_str, val_str = parts
        try:
            val = float(val_str)
            if val > 0:  # FRED uses negative values for missing data
                rows.append((date_str.strip(), val))
        except ValueError:
            continue

    return rows[-90:] if rows else []


def _fetch_sector_perf(etf: str) -> float:
    """
    Fetch 90-day return for a sector ETF using yfinance.
    Returns percentage change (e.g., 5.23 for +5.23%).
    """
    import yfinance as yf  # type: ignore
    from datetime import date, timedelta

    end = date.today()
    start = end - timedelta(days=120)  # extra buffer for trading days

    hist = yf.download(etf, start=str(start), end=str(end), progress=False)
    if hist.empty or len(hist) < 2:
        return 0.0

    # Use adjusted close
    adj_close = hist.get("Adj Close", hist.get("Close"))
    if adj_close is None or adj_close.empty:
        return 0.0

    # Get roughly 90 trading days ago (63 trading days ≈ 90 calendar days)
    n = min(63, len(adj_close) - 1)
    price_now = float(adj_close.iloc[-1])
    price_then = float(adj_close.iloc[-n])

    if price_then == 0:
        return 0.0

    return round((price_now - price_then) / price_then * 100, 2)


def _sync_fetch(ticker: str, sector: str | None = None) -> dict:
    """
    Synchronous combined fetch. Runs in executor.
    ticker is passed for context only (to look up sector ETF).
    """
    # 1. Treasury 10Y
    treasury_data = _fetch_fred_series("DGS10")
    treasury_val = treasury_data[-1][1] if treasury_data else 4.5
    treasury_trend = "stable"
    if len(treasury_data) >= 5:
        delta = treasury_data[-1][1] - treasury_data[-5][1]
        treasury_trend = "rising" if delta > 0.05 else ("falling" if delta < -0.05 else "stable")

    # 2. VIX
    vix_data = _fetch_fred_series("VIXCLS")
    vix_val = vix_data[-1][1] if vix_data else 20.0
    if vix_val < 15:
        vix_regime = "low"
    elif vix_val < 25:
        vix_regime = "moderate"
    elif vix_val < 35:
        vix_regime = "high"
    else:
        vix_regime = "extreme"

    # 3. Sector ETF
    etf = _SECTOR_ETF_MAP.get(sector or "", _DEFAULT_ETF)
    sector_perf = 0.0
    try:
        sector_perf = _fetch_sector_perf(etf)
    except Exception as exc:
        logger.warning("Sector ETF fetch failed for %s: %s", etf, exc)

    # Macro summary sentence
    sentiment_dir = "risk-off" if vix_val > 25 else "risk-on"
    rate_note = f"10Y Treasury at {treasury_val:.2f}% and {treasury_trend}"
    macro_summary = (
        f"Macro environment: {sentiment_dir} (VIX={vix_val:.1f}, {vix_regime}). "
        f"{rate_note}. Sector ETF {etf} +{sector_perf:.1f}% over 90 days."
    )

    return {
        "treasury_10y": round(treasury_val, 3),
        "vix": round(vix_val, 2),
        "treasury_trend": treasury_trend,
        "vix_regime": vix_regime,
        "sector_etf": etf,
        "sector_perf_90d": sector_perf,
        "macro_summary": macro_summary,
    }


@instrument("fred")
@ttl_cache(ttl_seconds=3600)
async def fetch(ticker: str, sector: str | None = None) -> SourceResult:
    """
    Async entry point. `sector` is optional — when provided, looks up the
    relevant sector ETF for performance context.
    """
    t0 = time.monotonic()
    loop = asyncio.get_event_loop()

    try:
        data = await asyncio.wait_for(
            loop.run_in_executor(_EXECUTOR, _sync_fetch, ticker, sector),
            timeout=20.0,
        )
        return SourceResult(
            source="fred",
            status=SourceStatus.OK,
            data=data,
            latency_ms=int((time.monotonic() - t0) * 1000),
        )
    except asyncio.TimeoutError:
        return SourceResult(
            source="fred",
            status=SourceStatus.TIMEOUT,
            error_msg="FRED fetch timed out after 20s",
            latency_ms=int((time.monotonic() - t0) * 1000),
        )
    except Exception as exc:
        return SourceResult(
            source="fred",
            status=SourceStatus.ERROR,
            error_msg=f"{type(exc).__name__}: {exc}",
            latency_ms=int((time.monotonic() - t0) * 1000),
        )
