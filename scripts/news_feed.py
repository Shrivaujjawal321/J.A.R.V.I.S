"""
AI/ML News Digest — Pipeline 2 for Jarvis.

Pulls from RSS feeds and produces a daily markdown digest.

Feeds (verified live 2026-05-11 — see data/notes/feed-sources-2026-05-11.md):
  - https://huggingface.co/blog/feed.xml
  - https://deepmind.google/blog/feed/basic/
  - https://openai.com/news/rss.xml
  - https://thegradientpub.substack.com/feed
  - https://raw.githubusercontent.com/taobojlen/anthropic-rss-feed/main/anthropic_news_rss.xml

Output:
  - data/briefings/news-YYYY-MM-DD.md

Failures:
  - Logged to data/logs/news_feed.log
  - Never crash the whole job on a single feed failure

Usage:
  .venv/bin/python scripts/news_feed.py
"""

import html
import logging
import re
import sys
from datetime import date, datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Any

import feedparser
import requests

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[1]
BRIEFINGS_DIR = ROOT / "data" / "briefings"
LOGS_DIR = ROOT / "data" / "logs"
TODAY = date.today().isoformat()  # YYYY-MM-DD

DIGEST_MD = BRIEFINGS_DIR / f"news-{TODAY}.md"
LOG_FILE = LOGS_DIR / "news_feed.log"

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
BRIEFINGS_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Feed registry
# ---------------------------------------------------------------------------
FEEDS = [
    {
        "name": "Hugging Face Blog",
        "url": "https://huggingface.co/blog/feed.xml",
        "skip_if_404": False,
    },
    {
        "name": "Google DeepMind",
        "url": "https://deepmind.google/blog/feed/basic/",
        "skip_if_404": False,
    },
    {
        "name": "OpenAI News",
        "url": "https://openai.com/news/rss.xml",
        "skip_if_404": False,
    },
    {
        "name": "The Gradient",
        "url": "https://thegradientpub.substack.com/feed",
        "skip_if_404": False,
    },
    {
        "name": "Anthropic News (community RSS)",
        "url": "https://raw.githubusercontent.com/taobojlen/anthropic-rss-feed/main/anthropic_news_rss.xml",
        "skip_if_404": True,
    },
    # Added 2026-05-21 for daily-tech-news LinkedIn post mode.
    # The original 5 feeds avg < 1 entry/day — too thin for a daily post.
    {
        "name": "TechCrunch AI",
        "url": "https://techcrunch.com/category/artificial-intelligence/feed/",
        "skip_if_404": True,
    },
    {
        "name": "VentureBeat AI",
        "url": "https://venturebeat.com/category/ai/feed/",
        "skip_if_404": True,
    },
    {
        "name": "Hacker News — AI/ML (>100 points)",
        "url": "https://hnrss.org/newest?q=AI+OR+LLM+OR+ML+OR+%22machine+learning%22&points=100",
        "skip_if_404": True,
    },
    {
        "name": "arXiv cs.LG (Machine Learning)",
        "url": "http://export.arxiv.org/rss/cs.LG",
        "skip_if_404": True,
    },
    {
        "name": "MIT Technology Review",
        "url": "https://www.technologyreview.com/feed/",
        "skip_if_404": True,
    },
]

REQUEST_TIMEOUT = 20
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64; Jarvis-Bot/1.0) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
}

# Only entries published in the last 24 hours
LOOKBACK_HOURS = 24


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _strip_html(raw: str) -> str:
    """Remove HTML tags and decode entities."""
    text = re.sub(r"<[^>]+>", " ", raw or "")
    text = html.unescape(text)
    return " ".join(text.split())


def _one_liner(summary: str, max_chars: int = 200) -> str:
    """Collapse a multi-line summary to a single clean line."""
    clean = _strip_html(summary)
    if len(clean) > max_chars:
        clean = clean[:max_chars].rsplit(" ", 1)[0] + "..."
    return clean


def _parse_date(entry: Any) -> datetime | None:
    """Extract a timezone-aware datetime from a feedparser entry."""
    # Try published_parsed (struct_time) — feedparser's normalised field
    if hasattr(entry, "published_parsed") and entry.published_parsed:
        try:
            import calendar
            ts = calendar.timegm(entry.published_parsed)
            return datetime.fromtimestamp(ts, tz=timezone.utc)
        except Exception:
            pass
    # Try updated_parsed
    if hasattr(entry, "updated_parsed") and entry.updated_parsed:
        try:
            import calendar
            ts = calendar.timegm(entry.updated_parsed)
            return datetime.fromtimestamp(ts, tz=timezone.utc)
        except Exception:
            pass
    # Try raw published string via email.utils
    for attr in ("published", "updated"):
        raw = getattr(entry, attr, None)
        if raw:
            try:
                return parsedate_to_datetime(raw)
            except Exception:
                pass
    return None


def _is_recent(entry: Any, cutoff: datetime) -> bool:
    dt = _parse_date(entry)
    if dt is None:
        # If we can't determine date, include it (conservative)
        return True
    return dt >= cutoff


# ---------------------------------------------------------------------------
# Feed fetcher
# ---------------------------------------------------------------------------

def fetch_feed(name: str, url: str, skip_if_404: bool, cutoff: datetime) -> list[dict[str, str]]:
    """
    Fetch a single RSS feed and return recent entries as dicts:
      {title, link, summary}
    Returns empty list on failure (logs the error).
    """
    try:
        # Fetch raw bytes with requests so we control User-Agent and timeout
        resp = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)

        if resp.status_code == 404 and skip_if_404:
            log.info("%s: 404 — skipping silently (skip_if_404=True)", name)
            return []

        if resp.status_code != 200:
            log.warning("%s: HTTP %d — skipping", name, resp.status_code)
            return []

        feed = feedparser.parse(resp.content)

        if feed.bozo and not feed.entries:
            log.warning("%s: feedparser bozo error: %s", name, feed.bozo_exception)
            return []

        entries = []
        for entry in feed.entries:
            if not _is_recent(entry, cutoff):
                continue
            title = _strip_html(getattr(entry, "title", "Untitled"))
            link = getattr(entry, "link", url)
            raw_summary = getattr(entry, "summary", "") or getattr(entry, "description", "")
            summary = _one_liner(raw_summary)
            entries.append({"title": title, "link": link, "summary": summary})

        log.info("%s: %d entries in last %dh", name, len(entries), LOOKBACK_HOURS)
        return entries

    except requests.exceptions.RequestException as exc:
        log.error("%s: network error — %s", name, exc)
        return []
    except Exception as exc:
        log.error("%s: unexpected error — %s", name, exc)
        return []


# ---------------------------------------------------------------------------
# Digest builder
# ---------------------------------------------------------------------------

def build_digest(sections: list[dict[str, Any]]) -> str:
    """Build the full markdown digest string."""
    lines = [f"# AI/ML News — {TODAY}", ""]
    total = 0
    for section in sections:
        name = section["name"]
        entries = section["entries"]
        if not entries:
            lines.append(f"## {name}")
            lines.append("_No new entries in the last 24 hours._")
            lines.append("")
            continue
        lines.append(f"## {name}")
        for e in entries:
            title = e["title"]
            link = e["link"]
            summary = e["summary"]
            if summary:
                lines.append(f"- **[{title}]({link})** — {summary}")
            else:
                lines.append(f"- **[{title}]({link})**")
            total += 1
        lines.append("")
    lines.append(f"---")
    lines.append(f"_Generated by Jarvis news_feed.py on {TODAY}. Total entries: {total}._")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    log.info("=== News Feed starting: %s ===", TODAY)

    cutoff = datetime.now(timezone.utc) - timedelta(hours=LOOKBACK_HOURS)
    log.info("Cutoff: entries published after %s", cutoff.isoformat())

    sections = []
    total_entries = 0

    for feed_cfg in FEEDS:
        name = feed_cfg["name"]
        url = feed_cfg["url"]
        skip_if_404 = feed_cfg["skip_if_404"]

        entries = fetch_feed(name, url, skip_if_404, cutoff)
        sections.append({"name": name, "entries": entries})
        total_entries += len(entries)

    log.info("Total entries aggregated: %d", total_entries)

    digest = build_digest(sections)
    DIGEST_MD.write_text(digest, encoding="utf-8")
    log.info("Digest saved to %s", DIGEST_MD)
    log.info("=== News Feed done ===")


if __name__ == "__main__":
    main()
