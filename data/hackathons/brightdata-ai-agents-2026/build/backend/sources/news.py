"""
backend/sources/news.py
========================
News sentiment source via BrightData SERP + Reuters structured data.

Two-phase:
    Phase 1: BrightData web_data_reuter_news for structured Reuters articles
    Phase 2: BrightData search_engine SERP for broader news coverage
             (Financial Times, WSJ, Bloomberg, CNBC, etc.)

Sentiment is derived via keyword heuristics (fast, no extra LLM call).

Returns SourceResult.data = {
    "article_count":        int
    "reuters_count":        int
    "sentiment_score":      float   (-1.0 to +1.0)
    "direction":            str     ("bullish" | "bearish" | "neutral")
    "top_headlines":        list[str]  (up to 5)
    "top_urls":             list[str]  (up to 5)
    "date_range":           str     (e.g. "last 30 days")
    "key_events":           list[str]  (earnings, M&A, regulatory, etc.)
    "sentiment_narrative":  str
}

Degraded mode: returns SourceStatus.BLOCKED if no API key.
"""
from __future__ import annotations

import asyncio
import json
import logging
import re
import time
from datetime import date, timedelta

from ..schemas import SourceResult, SourceStatus
from ..cache import ttl_cache
from ..observability import instrument
from .brightdata import web_data_reuter_news, search_engine, BrightDataError

logger = logging.getLogger(__name__)

# Keyword lists for heuristic sentiment
_POS_KEYWORDS = frozenset([
    "beat", "beats", "exceeds", "raised guidance", "record revenue", "profit surge",
    "upgrade", "buy rating", "outperform", "strong demand", "partnership", "acquisition target",
    "dividend increase", "share buyback", "analyst upgrade", "market share gain", "breakthrough",
    "new contract", "regulatory approval", "growth", "expansion",
])
_NEG_KEYWORDS = frozenset([
    "miss", "misses", "below expectations", "lowered guidance", "profit warning",
    "downgrade", "sell rating", "underperform", "layoffs", "job cuts", "investigation",
    "lawsuit", "regulatory fine", "recall", "downside", "competition pressure",
    "margin compression", "debt load", "short seller", "fraud",
])
_EVENT_PATTERNS = [
    (re.compile(r'\b(?:earnings?|quarterly results?|EPS)\b', re.I), "earnings"),
    (re.compile(r'\b(?:acquisition|merger|M&A|buyout|deal)\b', re.I), "m&a"),
    (re.compile(r'\b(?:FDA|regulatory|SEC|antitrust|investigation)\b', re.I), "regulatory"),
    (re.compile(r'\b(?:layoffs?|job cuts?|restructur)\b', re.I), "layoffs"),
    (re.compile(r'\b(?:dividend|buyback|share repurchase)\b', re.I), "capital_return"),
    (re.compile(r'\b(?:product launch|new product|partnership)\b', re.I), "product"),
]


def _score_text(text: str) -> float:
    """Return sentiment score in [-1, 1] based on keyword density."""
    words = set(re.findall(r'\b\w[\w\-]*\w\b', text.lower()))
    bigrams = set()
    word_list = re.findall(r'\b\w[\w\-]*\w\b', text.lower())
    for i in range(len(word_list) - 1):
        bigrams.add(f"{word_list[i]} {word_list[i+1]}")

    combined = words | bigrams
    pos = len(combined & _POS_KEYWORDS)
    neg = len(combined & _NEG_KEYWORDS)
    total = pos + neg
    if total == 0:
        return 0.0
    return (pos - neg) / total


def _extract_events(text: str) -> list[str]:
    """Detect key event types in news text."""
    found = []
    for pattern, label in _EVENT_PATTERNS:
        if pattern.search(text) and label not in found:
            found.append(label)
    return found


def _parse_news_results(reuters_raw: str, serp_raw: str, ticker: str) -> dict:
    """Merge and analyze Reuters + SERP news data."""
    headlines: list[str] = []
    urls: list[str] = []
    texts: list[str] = []
    reuters_count = 0

    # Parse Reuters structured data
    if reuters_raw:
        try:
            reuters_data = json.loads(reuters_raw)
            if isinstance(reuters_data, list):
                articles = reuters_data
            elif isinstance(reuters_data, dict):
                articles = reuters_data.get("articles", [reuters_data])
            else:
                articles = []

            for art in articles:
                title = str(art.get("title", art.get("headline", "")))
                url = str(art.get("url", art.get("link", "")))
                body = str(art.get("body", art.get("text", art.get("summary", ""))))
                if title:
                    headlines.append(title)
                    texts.append(f"{title} {body[:300]}")
                    reuters_count += 1
                if url:
                    urls.append(url)
        except (json.JSONDecodeError, TypeError):
            # Markdown fallback
            for line in reuters_raw.split("\n"):
                line = line.strip()
                if len(line) > 20 and not line.startswith("#") and not line.startswith("|"):
                    headlines.append(line[:150])
                    texts.append(line)
                    reuters_count += 1
                    if reuters_count >= 10:
                        break

    # Parse SERP results
    if serp_raw:
        # SERP returns markdown with titles and URLs
        title_re = re.compile(r'\[([^\]]+)\]\(([^\)]+)\)', re.M)
        for m in title_re.finditer(serp_raw):
            title, url = m.group(1), m.group(2)
            if len(title) > 15:
                headlines.append(title)
                urls.append(url)
                texts.append(title)

        # Also extract plain text headlines
        for line in serp_raw.split("\n"):
            line = line.strip()
            if 30 < len(line) < 200 and not line.startswith("http"):
                texts.append(line)

    # Score combined
    combined_text = " ".join(texts)
    score = _score_text(combined_text)

    direction: str
    if score > 0.1:
        direction = "bullish"
    elif score < -0.1:
        direction = "bearish"
    else:
        direction = "neutral"

    events = _extract_events(combined_text)
    article_count = len(headlines)

    narrative = (
        f"News coverage: {article_count} articles ({reuters_count} Reuters). "
        f"Sentiment score: {score:.2f} → {direction}. "
        f"Key events detected: {', '.join(events) if events else 'none'}."
    )

    return {
        "article_count": article_count,
        "reuters_count": reuters_count,
        "sentiment_score": round(score, 3),
        "direction": direction,
        "top_headlines": headlines[:5],
        "top_urls": urls[:5],
        "date_range": "last 30 days",
        "key_events": events,
        "sentiment_narrative": narrative,
    }


@instrument("news")
@ttl_cache(ttl_seconds=3600)
async def fetch(ticker: str) -> SourceResult:
    """
    Async entry: fetch news via BrightData Reuters + SERP.
    """
    t0 = time.monotonic()
    ticker = ticker.upper().strip()

    try:
        # Run Reuters and SERP in parallel
        reuters_query = f"{ticker} stock news"
        serp_query = f'"{ticker}" stock news site:reuters.com OR site:bloomberg.com OR site:ft.com last 30 days'

        reuters_raw, serp_raw = await asyncio.gather(
            asyncio.wait_for(web_data_reuter_news(reuters_query, limit=10), timeout=10.0),
            asyncio.wait_for(search_engine(serp_query), timeout=10.0),
            return_exceptions=True,
        )

        # Handle partial failures gracefully
        if isinstance(reuters_raw, Exception):
            logger.warning("Reuters fetch failed: %s", reuters_raw)
            reuters_raw = ""
        if isinstance(serp_raw, Exception):
            logger.warning("SERP fetch failed: %s", serp_raw)
            serp_raw = ""

        if not reuters_raw and not serp_raw:
            return SourceResult(
                source="news",
                status=SourceStatus.ERROR,
                error_msg="Both Reuters and SERP news fetches failed",
                latency_ms=int((time.monotonic() - t0) * 1000),
            )

        data = _parse_news_results(str(reuters_raw), str(serp_raw), ticker)

        return SourceResult(
            source="news",
            status=SourceStatus.OK,
            data=data,
            latency_ms=int((time.monotonic() - t0) * 1000),
        )

    except BrightDataError as exc:
        status = SourceStatus.BLOCKED if exc.code == 0 else SourceStatus.ERROR
        return SourceResult(
            source="news",
            status=status,
            error_msg=str(exc),
            latency_ms=int((time.monotonic() - t0) * 1000),
        )
    except asyncio.TimeoutError:
        return SourceResult(
            source="news",
            status=SourceStatus.TIMEOUT,
            error_msg="News BrightData calls timed out",
            latency_ms=int((time.monotonic() - t0) * 1000),
        )
    except Exception as exc:
        return SourceResult(
            source="news",
            status=SourceStatus.ERROR,
            error_msg=f"{type(exc).__name__}: {exc}",
            latency_ms=int((time.monotonic() - t0) * 1000),
        )
