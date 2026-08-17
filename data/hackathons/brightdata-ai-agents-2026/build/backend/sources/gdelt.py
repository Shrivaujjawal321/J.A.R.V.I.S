"""
backend/sources/gdelt.py
========================
GDELT Project news tone source.

GDELT tracks news articles worldwide with sentiment scores. We use:
    1. gdeltdoc Python library (free, no API key) — article search + tone scores
    2. Fallback: direct GDELT 2.0 GKG API query via httpx if gdeltdoc fails

Returns SourceResult.data = {
    "avg_tone":         float   (-10 to +10, negative=negative tone)
    "article_count":    int
    "tone_label":       str     ("very_positive" | "positive" | "neutral" | "negative" | "very_negative")
    "top_themes":       list[str]   (up to 5 GDELT event themes)
    "volume_trend":     str     ("increasing" | "stable" | "decreasing")
    "sentiment_label":  str     (human-friendly one-liner)
    "top_urls":         list[str]   (up to 3 article URLs)
}
"""
from __future__ import annotations

import asyncio
import logging
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, date

from ..schemas import SourceResult, SourceStatus
from ..cache import ttl_cache
from ..observability import instrument

logger = logging.getLogger(__name__)

_EXECUTOR = ThreadPoolExecutor(max_workers=2, thread_name_prefix="gdelt_worker")

_GDELT_DOC_API = "https://api.gdeltproject.org/api/v2/doc/doc"


def _tone_label(avg_tone: float) -> str:
    if avg_tone >= 3.0:
        return "very_positive"
    if avg_tone >= 0.5:
        return "positive"
    if avg_tone >= -0.5:
        return "neutral"
    if avg_tone >= -3.0:
        return "negative"
    return "very_negative"


def _fetch_gdeltdoc(ticker: str) -> dict:
    """Try gdeltdoc library first."""
    from gdeltdoc import GdeltDoc, Filters  # type: ignore

    f = Filters(
        keyword=ticker,
        start_date=(date.today() - timedelta(days=30)).strftime("%Y-%m-%d"),
        end_date=date.today().strftime("%Y-%m-%d"),
    )
    gd = GdeltDoc()
    articles = gd.article_search(f)

    if articles is None or articles.empty:
        raise ValueError("gdeltdoc returned empty result")

    # gdeltdoc returns a DataFrame with columns: url, title, seendate, socialimage, domain, language, sourcecountry
    # Tone is NOT directly in the doc API — use timeline_tone for aggregate tone
    timeline = gd.timeline_search("timelinetone", f)

    avg_tone = 0.0
    volume_trend = "stable"
    if timeline is not None and not timeline.empty and "Average Tone" in timeline.columns:
        tones = timeline["Average Tone"].dropna().tolist()
        avg_tone = sum(tones) / len(tones) if tones else 0.0
        if len(tones) >= 2:
            first_half = sum(tones[: len(tones) // 2]) / (len(tones) // 2)
            second_half = sum(tones[len(tones) // 2 :]) / (len(tones) - len(tones) // 2)
            if second_half > first_half + 0.5:
                volume_trend = "increasing"
            elif second_half < first_half - 0.5:
                volume_trend = "decreasing"

    top_urls = articles["url"].head(3).tolist() if "url" in articles.columns else []
    article_count = len(articles)

    label = _tone_label(avg_tone)
    sentiment_label = (
        f"GDELT analyzed {article_count} news articles about {ticker} over 30 days. "
        f"Average tone: {avg_tone:.2f} ({label.replace('_', ' ')}). "
        f"Coverage volume is {volume_trend}."
    )

    return {
        "avg_tone": round(avg_tone, 3),
        "article_count": article_count,
        "tone_label": label,
        "top_themes": [],  # gdeltdoc doc API doesn't expose themes directly
        "volume_trend": volume_trend,
        "sentiment_label": sentiment_label,
        "top_urls": top_urls,
    }


def _fetch_gdelt_api(ticker: str) -> dict:
    """
    Fallback: GDELT Doc 2.0 API ArtList query.
    Returns tone via article list metadata.
    """
    import httpx

    # GDELT doc query
    end_dt = datetime.utcnow()
    start_dt = end_dt - timedelta(days=30)

    params = {
        "query": f"{ticker} company stock",
        "mode": "ArtList",
        "maxrecords": "50",
        "format": "json",
        "STARTDATETIME": start_dt.strftime("%Y%m%d%H%M%S"),
        "ENDDATETIME": end_dt.strftime("%Y%m%d%H%M%S"),
        "SORTBY": "DateDesc",
    }

    resp = httpx.get(_GDELT_DOC_API, params=params, timeout=15.0)
    resp.raise_for_status()
    body = resp.json()

    articles = body.get("articles", [])
    if not articles:
        return {
            "avg_tone": 0.0,
            "article_count": 0,
            "tone_label": "neutral",
            "top_themes": [],
            "volume_trend": "stable",
            "sentiment_label": f"No GDELT coverage found for {ticker} in the last 30 days.",
            "top_urls": [],
        }

    # Extract tone from article metadata (tone field in GDELT ArtList)
    tones = []
    top_urls = []
    themes_flat: list[str] = []

    for art in articles[:50]:
        tone = art.get("tone", {})
        if isinstance(tone, dict):
            val = tone.get("tone")
            if val is not None:
                try:
                    tones.append(float(val))
                except (ValueError, TypeError):
                    pass
        elif isinstance(tone, (int, float)):
            tones.append(float(tone))

        url = art.get("url", "")
        if url and len(top_urls) < 3:
            top_urls.append(url)

        for th in art.get("themes", []):
            if th and th not in themes_flat:
                themes_flat.append(th)

    avg_tone = sum(tones) / len(tones) if tones else 0.0
    label = _tone_label(avg_tone)

    sentiment_label = (
        f"GDELT analyzed {len(articles)} news articles about {ticker} over 30 days. "
        f"Average tone: {avg_tone:.2f} ({label.replace('_', ' ')})."
    )

    return {
        "avg_tone": round(avg_tone, 3),
        "article_count": len(articles),
        "tone_label": label,
        "top_themes": themes_flat[:5],
        "volume_trend": "stable",  # GDELT ArtList doesn't expose volume trend directly
        "sentiment_label": sentiment_label,
        "top_urls": top_urls,
    }


def _sync_fetch(ticker: str) -> dict:
    """Try gdeltdoc first, fall back to GDELT API."""
    try:
        return _fetch_gdeltdoc(ticker)
    except ImportError:
        logger.info("gdeltdoc not installed, using GDELT API fallback")
    except Exception as exc:
        logger.warning("gdeltdoc failed for %s: %s — trying GDELT API", ticker, exc)

    return _fetch_gdelt_api(ticker)


@instrument("gdelt")
@ttl_cache(ttl_seconds=3600)
async def fetch(ticker: str) -> SourceResult:
    """Async entry point for GDELT news tone source."""
    t0 = time.monotonic()
    loop = asyncio.get_event_loop()

    try:
        data = await asyncio.wait_for(
            loop.run_in_executor(_EXECUTOR, _sync_fetch, ticker),
            timeout=25.0,
        )
        return SourceResult(
            source="gdelt",
            status=SourceStatus.OK,
            data=data,
            latency_ms=int((time.monotonic() - t0) * 1000),
        )
    except asyncio.TimeoutError:
        return SourceResult(
            source="gdelt",
            status=SourceStatus.TIMEOUT,
            error_msg="GDELT fetch timed out after 25s",
            latency_ms=int((time.monotonic() - t0) * 1000),
        )
    except Exception as exc:
        return SourceResult(
            source="gdelt",
            status=SourceStatus.ERROR,
            error_msg=f"{type(exc).__name__}: {exc}",
            latency_ms=int((time.monotonic() - t0) * 1000),
        )
