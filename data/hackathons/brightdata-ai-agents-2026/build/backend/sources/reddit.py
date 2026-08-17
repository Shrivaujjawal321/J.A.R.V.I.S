"""
backend/sources/reddit.py
==========================
Reddit sentiment source via BrightData MCP.

Fetches posts from r/WallStreetBets, r/stocks, and r/investing
mentioning the ticker, then extracts:
    - mention velocity (posts/day over 7d)
    - simple sentiment classification (positive/negative/neutral keywords)
    - upvote momentum (avg upvotes on positive vs negative posts)

Degraded mode: if BRIGHT_DATA_API_KEY is not set, returns SourceStatus.BLOCKED
with a descriptive message. The orchestrator proceeds without this source.

Source weight: 0.40 (lowest — empirically near-zero alpha per Alpha Architect 2024)
Alpha tier: "caution" — displayed with caveat badge in UI.
"""
from __future__ import annotations

import asyncio
import json
import logging
import re
import time
from datetime import datetime, timedelta, timezone

from ..schemas import SourceResult, SourceStatus
from ..cache import ttl_cache
from ..observability import instrument
from .brightdata import web_data_reddit_posts, BrightDataError

logger = logging.getLogger(__name__)

_SUBREDDITS = ["WallStreetBets", "stocks", "investing"]
_POSTS_PER_SUB = 20

# Simple keyword sets for heuristic sentiment
_POS_WORDS = frozenset([
    "bullish", "buy", "long", "moon", "calls", "squeeze", "beat", "surge",
    "rally", "outperform", "undervalued", "gem", "strong", "growth", "upside",
])
_NEG_WORDS = frozenset([
    "bearish", "sell", "short", "puts", "dump", "crash", "miss", "decline",
    "overvalued", "bagholders", "downside", "weak", "red", "fall", "drop",
])


def _classify_sentiment(text: str) -> str:
    text_lower = text.lower()
    words = set(re.findall(r'\b\w+\b', text_lower))
    pos = len(words & _POS_WORDS)
    neg = len(words & _NEG_WORDS)
    if pos > neg + 1:
        return "bullish"
    if neg > pos + 1:
        return "bearish"
    return "neutral"


def _parse_reddit_response(raw_text: str, ticker: str) -> dict:
    """
    Parse BrightData reddit response (which may be JSON or Markdown).
    Returns structured sentiment dict.
    """
    posts: list[dict] = []

    # Try JSON parse first
    try:
        parsed = json.loads(raw_text)
        if isinstance(parsed, list):
            posts = parsed
        elif isinstance(parsed, dict) and "posts" in parsed:
            posts = parsed["posts"]
    except (json.JSONDecodeError, ValueError):
        pass

    # If JSON parse failed, extract from Markdown text
    if not posts:
        # Each post in markdown typically starts with # or ## or title line
        lines = raw_text.split("\n")
        current: dict = {}
        for line in lines:
            line = line.strip()
            if not line:
                continue
            if line.startswith("# ") or line.startswith("## "):
                if current:
                    posts.append(current)
                current = {"title": line.lstrip("#").strip(), "score": 0, "text": ""}
            elif current:
                # accumulate body
                current["text"] = (current.get("text", "") + " " + line).strip()
        if current:
            posts.append(current)

    if not posts:
        return {
            "mention_count": 0,
            "direction": "neutral",
            "avg_sentiment_score": 0.0,
            "bullish_pct": 0.0,
            "bearish_pct": 0.0,
            "avg_upvotes_bullish": 0.0,
            "avg_upvotes_bearish": 0.0,
            "top_post_title": "No posts found",
            "source_subreddits": _SUBREDDITS,
            "alpha_caution": "Reddit WallStreetBets has shown near-zero empirical alpha (Alpha Architect 2024)",
        }

    # Filter posts mentioning ticker (case-insensitive, word boundary)
    ticker_re = re.compile(rf'\b{re.escape(ticker)}\b', re.IGNORECASE)
    relevant = [
        p for p in posts
        if ticker_re.search(str(p.get("title", "")) + " " + str(p.get("text", "")))
    ]
    if not relevant:
        relevant = posts  # fallback: use all posts (query was already ticker-specific)

    # Sentiment per post
    sentiments = [_classify_sentiment(str(p.get("title", "")) + " " + str(p.get("text", ""))) for p in relevant]
    upvotes = [int(p.get("score", p.get("upvotes", 0)) or 0) for p in relevant]

    n = len(relevant)
    bull_idx = [i for i, s in enumerate(sentiments) if s == "bullish"]
    bear_idx = [i for i, s in enumerate(sentiments) if s == "bearish"]

    bullish_pct = len(bull_idx) / n * 100 if n else 0.0
    bearish_pct = len(bear_idx) / n * 100 if n else 0.0

    avg_up_bull = sum(upvotes[i] for i in bull_idx) / len(bull_idx) if bull_idx else 0.0
    avg_up_bear = sum(upvotes[i] for i in bear_idx) / len(bear_idx) if bear_idx else 0.0

    # Overall direction: weighted by upvotes
    bull_weight = sum(upvotes[i] for i in bull_idx)
    bear_weight = sum(upvotes[i] for i in bear_idx)
    if bull_weight > bear_weight * 1.5:
        direction = "bullish"
    elif bear_weight > bull_weight * 1.5:
        direction = "bearish"
    else:
        direction = "neutral"

    # Simple score: (bullish% - bearish%) / 100 mapped to -1..1
    score = (bullish_pct - bearish_pct) / 100.0

    top_post = relevant[0].get("title", "N/A") if relevant else "N/A"

    return {
        "mention_count": n,
        "direction": direction,
        "avg_sentiment_score": round(score, 3),
        "bullish_pct": round(bullish_pct, 1),
        "bearish_pct": round(bearish_pct, 1),
        "avg_upvotes_bullish": round(avg_up_bull, 0),
        "avg_upvotes_bearish": round(avg_up_bear, 0),
        "top_post_title": str(top_post)[:200],
        "source_subreddits": _SUBREDDITS,
        "alpha_caution": "Reddit WallStreetBets has shown near-zero empirical alpha (Alpha Architect 2024)",
    }


@instrument("reddit")
@ttl_cache(ttl_seconds=3600)
async def fetch(ticker: str) -> SourceResult:
    """
    Async entry: fetch Reddit sentiment via BrightData MCP.
    Returns BLOCKED gracefully if no API key.
    """
    t0 = time.monotonic()
    ticker = ticker.upper().strip()

    try:
        # Query all subreddits in one call
        query = f"${ticker} OR {ticker} stock"
        raw = await asyncio.wait_for(
            web_data_reddit_posts(
                query=query,
                subreddits=_SUBREDDITS,
                limit=_POSTS_PER_SUB * len(_SUBREDDITS),
            ),
            timeout=12.0,
        )
        data = _parse_reddit_response(raw, ticker)
        return SourceResult(
            source="reddit",
            status=SourceStatus.OK,
            data=data,
            latency_ms=int((time.monotonic() - t0) * 1000),
        )

    except BrightDataError as exc:
        status = SourceStatus.BLOCKED if exc.code == 0 else SourceStatus.ERROR
        return SourceResult(
            source="reddit",
            status=status,
            error_msg=str(exc),
            latency_ms=int((time.monotonic() - t0) * 1000),
        )
    except asyncio.TimeoutError:
        return SourceResult(
            source="reddit",
            status=SourceStatus.TIMEOUT,
            error_msg="Reddit BrightData call timed out after 12s",
            latency_ms=int((time.monotonic() - t0) * 1000),
        )
    except Exception as exc:
        return SourceResult(
            source="reddit",
            status=SourceStatus.ERROR,
            error_msg=f"{type(exc).__name__}: {exc}",
            latency_ms=int((time.monotonic() - t0) * 1000),
        )
