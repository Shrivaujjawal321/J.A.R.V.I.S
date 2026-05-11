"""
Hackathon Radar — Pipeline 1 for Jarvis.

Pulls AI/ML hackathons from:
  - Unstop public API  (https://unstop.com)
  - Devpost public API (https://devpost.com)

HackerEarth was checked and found to be a Next.js SPA with no accessible
public JSON API — all /api/* endpoints return Webflow HTML. Skipped;
failure is logged.

For each hackathon found:
  - Extracts name, organizer, deadline, prize, eligibility, focus, URL
  - Filters: registration open + AI/ML relevant (by skills or themes)
  - Persists full JSON to data/hackathons/radar-YYYY-MM-DD.json
  - Maintains data/hackathons/seen.json (already-alerted IDs)
  - Sends ONE consolidated Telegram message for new hackathons
  - Appends IDs to seen.json after alerting

Usage:
  .venv/bin/python scripts/hackathon_radar.py
"""

import json
import logging
import os
import re
import sys
import textwrap
import urllib.parse
import urllib.request
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

import requests

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[1]
HACKATHONS_DIR = ROOT / "data" / "hackathons"
LOGS_DIR = ROOT / "data" / "logs"
TODAY = date.today().isoformat()  # YYYY-MM-DD

RADAR_JSON = HACKATHONS_DIR / f"radar-{TODAY}.json"
SEEN_JSON = HACKATHONS_DIR / "seen.json"
LOG_FILE = LOGS_DIR / "hackathon_radar.log"

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
HACKATHONS_DIR.mkdir(parents=True, exist_ok=True)
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
# Config
# ---------------------------------------------------------------------------
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64; Jarvis-Bot/1.0) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
}
REQUEST_TIMEOUT = 20  # seconds

# AI/ML relevance keywords — checked against title + skills + themes + description
AI_ML_KEYWORDS = {
    "artificial intelligence", "machine learning", "deep learning",
    "nlp", "natural language processing", "computer vision", "generative ai",
    "llm", "large language model", "data science", "neural network",
    "reinforcement learning", "ai/ml", "ai & ml", "ml ops", "mlops",
    "transformer", "diffusion", "stable diffusion", "chatgpt", "gpt",
    "claude", "gemini", "pytorch", "tensorflow", "hugging face", "huggingface",
    "data analytics", "predictive modeling", "ai hackathon",
}

# Minimum keyword hits to include a hackathon
RELEVANCE_THRESHOLD = 1


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_env() -> dict[str, str]:
    env_path = ROOT / "bridge" / ".env"
    env: dict[str, str] = {}
    if not env_path.exists():
        return env
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        env[k.strip()] = v.strip()
    return env


def _tg_send(token: str, chat_id: str, text: str) -> None:
    """Send a Telegram message, splitting at 3900 chars if needed."""
    chunks = textwrap.wrap(text, 3900, replace_whitespace=False, drop_whitespace=False) or [text]
    for chunk in chunks:
        data = urllib.parse.urlencode({
            "chat_id": chat_id,
            "text": chunk,
            "disable_web_page_preview": "true",
        }).encode()
        req = urllib.request.Request(
            f"https://api.telegram.org/bot{token}/sendMessage",
            data=data,
            method="POST",
        )
        try:
            urllib.request.urlopen(req, timeout=20).read()
        except Exception as exc:
            log.error("Telegram send failed: %s", exc)


def _relevance_score(text_blob: str) -> int:
    """Count how many AI/ML keywords appear in text (case-insensitive)."""
    blob = text_blob.lower()
    return sum(1 for kw in AI_ML_KEYWORDS if kw in blob)


def _strip_html(html: str) -> str:
    return re.sub(r"<[^>]+>", " ", html or "").strip()


def _load_seen() -> set[str]:
    if SEEN_JSON.exists():
        try:
            return set(json.loads(SEEN_JSON.read_text()))
        except Exception:
            return set()
    return set()


def _save_seen(seen: set[str]) -> None:
    SEEN_JSON.write_text(json.dumps(sorted(seen), indent=2))


# ---------------------------------------------------------------------------
# Source 1: Unstop
# ---------------------------------------------------------------------------

def _fetch_unstop_page(page: int) -> tuple[list[dict[str, Any]], int]:
    url = (
        "https://unstop.com/api/public/opportunity/search-result"
        f"?opportunity=hackathons&page={page}&per_page=20"
    )
    r = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
    r.raise_for_status()
    data = r.json()
    return data["data"]["data"], data["data"].get("last_page", 1)


def _parse_unstop_item(item: dict[str, Any]) -> dict[str, Any]:
    """Normalise an Unstop API item into our common schema."""
    regn = item.get("regnRequirements") or {}
    org = item.get("organisation") or {}

    # Deadline: prefer registration end, fall back to event end
    deadline_raw = regn.get("end_regn_dt") or item.get("end_date") or ""
    deadline = deadline_raw[:10] if deadline_raw else "unknown"

    # Build prize string
    prizes = item.get("prizes") or []
    prize_parts: list[str] = []
    for p in prizes:
        cash = p.get("cash")
        others = p.get("others") or ""
        if cash:
            code = p.get("currencyCode") or "INR"
            prize_parts.append(f"{code} {cash}")
        elif others:
            prize_parts.append(others[:80])
    prize = "; ".join(prize_parts) if prize_parts else "not specified"

    # Skills for relevance scoring
    skills = [s.get("skill_name", "") for s in (item.get("required_skills") or [])]
    skills_blob = " ".join(skills)

    # Eligibility tags
    filters = item.get("filters") or []
    eligibility_tags = [f["name"] for f in filters if f.get("type") == "eligible"]

    fresh_grad_terms = {"undergraduate", "engineering students", "students", "postgraduate", "graduate"}
    is_fresh_grad = any(tag.lower() in fresh_grad_terms for tag in eligibility_tags)

    url = f"https://unstop.com/{item['public_url']}"
    title = item.get("title", "")
    details_text = _strip_html(item.get("details") or "")[:500]
    score = _relevance_score(f"{title} {skills_blob} {details_text}")

    return {
        "id": f"unstop-{item['id']}",
        "source": "unstop",
        "name": title,
        "organizer": org.get("name", "unknown"),
        "deadline": deadline,
        "prize": prize,
        "eligibility": eligibility_tags or ["open"],
        "focus_area": skills[:5],
        "url": url,
        "regn_open": item.get("regn_open", 0) == 1,
        "is_fresh_grad_eligible": is_fresh_grad,
        "relevance_score": score,
    }


def fetch_unstop(max_pages: int = 5) -> list[dict[str, Any]]:
    """Pull up to max_pages of Unstop hackathons, return open AI/ML ones."""
    results: list[dict[str, Any]] = []
    try:
        for page in range(1, max_pages + 1):
            items, last_page = _fetch_unstop_page(page)
            log.info("Unstop page %d/%d: %d items", page, last_page, len(items))
            for item in items:
                parsed = _parse_unstop_item(item)
                if parsed["regn_open"] and parsed["relevance_score"] >= RELEVANCE_THRESHOLD:
                    results.append(parsed)
            if page >= last_page:
                break
    except Exception as exc:
        log.error("Unstop fetch failed: %s", exc)
    log.info("Unstop: %d AI/ML open hackathons found", len(results))
    return results


# ---------------------------------------------------------------------------
# Source 2: Devpost
# ---------------------------------------------------------------------------

def _parse_devpost_item(item: dict[str, Any]) -> dict[str, Any]:
    """Normalise a Devpost API item into our common schema."""
    themes = [t["name"] for t in (item.get("themes") or [])]
    prize_raw = item.get("prize_amount") or ""
    prize = _strip_html(prize_raw) or "not specified"

    dates_str = item.get("submission_period_dates", "")
    deadline = "unknown"
    end_match = re.search(r"[-\u2013]\s*([A-Za-z]+ \d+,\s*\d{4})", dates_str)
    if end_match:
        try:
            deadline = datetime.strptime(end_match.group(1).strip(), "%b %d, %Y").strftime("%Y-%m-%d")
        except ValueError:
            pass

    url = item.get("url") or ""
    title = item.get("title", "").strip()
    score = _relevance_score(f"{title} {' '.join(themes)}")

    return {
        "id": f"devpost-{item['id']}",
        "source": "devpost",
        "name": title,
        "organizer": item.get("organization_name") or "unknown",
        "deadline": deadline,
        "prize": prize,
        "eligibility": ["open"] if not item.get("invite_only") else ["invite-only"],
        "focus_area": themes,
        "url": url,
        "regn_open": item.get("open_state") == "open",
        "is_fresh_grad_eligible": True,
        "relevance_score": score,
    }


def fetch_devpost(max_pages: int = 3) -> list[dict[str, Any]]:
    """Pull open hackathons from Devpost, return AI/ML ones."""
    results: list[dict[str, Any]] = []
    try:
        seen_ids: set[int] = set()
        for page in range(1, max_pages + 1):
            url = (
                "https://devpost.com/api/hackathons"
                f"?status[]=open&challenge_type[]=hackathon&page={page}"
            )
            r = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
            r.raise_for_status()
            data = r.json()
            items = data.get("hackathons") or []
            log.info("Devpost page %d: %d items", page, len(items))
            if not items:
                break
            for item in items:
                if item["id"] in seen_ids:
                    continue
                seen_ids.add(item["id"])
                parsed = _parse_devpost_item(item)
                if parsed["regn_open"] and parsed["relevance_score"] >= RELEVANCE_THRESHOLD:
                    results.append(parsed)
    except Exception as exc:
        log.error("Devpost fetch failed: %s", exc)
    log.info("Devpost: %d AI/ML open hackathons found", len(results))
    return results


# ---------------------------------------------------------------------------
# Source 3: HackerEarth (checked — not accessible without browser)
# ---------------------------------------------------------------------------

def fetch_hackerearth() -> list[dict[str, Any]]:
    """
    HackerEarth: their challenges page is a Next.js SPA with no embedded
    __NEXT_DATA__. All /api/* paths return a Webflow HTML landing page
    (200 OK, wrong content-type). Skipping — would need Selenium/Playwright.
    """
    log.warning(
        "HackerEarth: no public JSON API reachable — SPA returns HTML for "
        "all /api/* endpoints. Skipping to avoid brittle HTML scraping."
    )
    return []


# ---------------------------------------------------------------------------
# Telegram alert builder
# ---------------------------------------------------------------------------

def _build_telegram_message(new_hackathons: list[dict[str, Any]]) -> str:
    n = len(new_hackathons)
    lines = [f"New AI/ML Hackathons on Radar ({n})\n"]
    for h in new_hackathons:
        name = h["name"]
        deadline = h["deadline"]
        url = h["url"]
        organizer = h["organizer"]
        prize = h["prize"] if h["prize"] != "not specified" else ""
        prize_str = f" | Prize: {prize[:60]}" if prize else ""
        lines.append(
            f"{name}\n"
            f"  Organizer: {organizer}\n"
            f"  Deadline: {deadline}{prize_str}\n"
            f"  {url}\n"
        )
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    log.info("=== Hackathon Radar starting: %s ===", TODAY)

    env = _load_env()
    token = env.get("TELEGRAM_BOT_TOKEN") or os.getenv("TELEGRAM_BOT_TOKEN")
    allowed = (env.get("ALLOWED_USER_IDS") or os.getenv("ALLOWED_USER_IDS") or "").split(",")
    chat_id = next((x.strip() for x in allowed if x.strip()), None)

    if not token or not chat_id:
        log.error("TELEGRAM_BOT_TOKEN / ALLOWED_USER_IDS not configured — will not send alerts")

    all_hackathons: list[dict[str, Any]] = []
    all_hackathons.extend(fetch_unstop(max_pages=5))
    all_hackathons.extend(fetch_devpost(max_pages=3))
    fetch_hackerearth()

    # Deduplicate by URL
    seen_urls: set[str] = set()
    unique: list[dict[str, Any]] = []
    for h in all_hackathons:
        if h["url"] not in seen_urls:
            seen_urls.add(h["url"])
            unique.append(h)

    log.info("Total unique AI/ML open hackathons: %d", len(unique))

    # Persist radar file
    radar_payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "date": TODAY,
        "total": len(unique),
        "hackathons": unique,
    }
    RADAR_JSON.write_text(json.dumps(radar_payload, indent=2, ensure_ascii=False))
    log.info("Radar saved to %s", RADAR_JSON)

    # Diff against seen.json
    seen = _load_seen()
    new_ones = [h for h in unique if h["id"] not in seen]
    log.info("New hackathons (not in seen.json): %d", len(new_ones))

    if new_ones and token and chat_id:
        msg = _build_telegram_message(new_ones)
        log.info("Sending Telegram alert for %d new hackathons", len(new_ones))
        _tg_send(token, chat_id, msg)
    elif new_ones:
        log.warning("New hackathons found but Telegram not configured — skipping alert")
    else:
        log.info("No new hackathons — no Telegram alert needed")

    # Update seen.json
    for h in new_ones:
        seen.add(h["id"])
    _save_seen(seen)
    log.info("seen.json updated with %d total entries", len(seen))
    log.info("=== Hackathon Radar done ===")


if __name__ == "__main__":
    main()
