"""
backend/sources/linkedin.py
============================
LinkedIn hiring trends source via BrightData MCP.

Fetches:
    1. Company profile (headcount, description, follower count)
    2. Active job listings (count + role-mix breakdown)

Derives:
    - posting_growth_direction: "expanding" | "contracting" | "stable"
    - role_mix: engineering% vs sales% vs ops% (growth signal proxy)
    - hiring_signal: bullish/bearish/neutral based on posting activity

Signal weight: 0.60 (medium — lagging ~90 days; Green et al use Glassdoor not LinkedIn,
but hiring direction is a solid leading indicator of capex direction)

Degraded mode: returns SourceStatus.BLOCKED if no API key.
"""
from __future__ import annotations

import asyncio
import json
import logging
import re
import time

from ..schemas import SourceResult, SourceStatus
from ..cache import ttl_cache
from ..observability import instrument
from .brightdata import (
    web_data_linkedin_company_profile,
    web_data_linkedin_job_listings,
    search_engine,
    BrightDataError,
)

logger = logging.getLogger(__name__)

# Role classification keywords
_ENGINEERING_KEYWORDS = frozenset([
    "engineer", "developer", "swe", "software", "data scientist", "ml", "ai",
    "devops", "platform", "infrastructure", "architect", "research scientist",
])
_SALES_KEYWORDS = frozenset([
    "sales", "account executive", "ae", "sdr", "bdr", "account manager",
    "business development", "revenue", "gtm", "growth",
])
_OPS_KEYWORDS = frozenset([
    "operations", "ops", "program manager", "product manager", "pm",
    "supply chain", "logistics", "finance", "hr", "legal", "compliance",
])


def _classify_role(title: str) -> str:
    t = title.lower()
    if any(k in t for k in _ENGINEERING_KEYWORDS):
        return "engineering"
    if any(k in t for k in _SALES_KEYWORDS):
        return "sales"
    if any(k in t for k in _OPS_KEYWORDS):
        return "ops"
    return "other"


def _find_linkedin_url(search_text: str, company_name: str) -> str | None:
    """Extract LinkedIn company URL from search result text."""
    # Match linkedin.com/company/... pattern
    m = re.search(
        r'https?://(?:www\.)?linkedin\.com/company/[a-zA-Z0-9\-_]+',
        search_text,
    )
    if m:
        return m.group(0).rstrip("/")
    return None


def _parse_job_listings(raw_text: str) -> dict:
    """Parse job listings text (JSON or markdown) into structured data."""
    jobs: list[dict] = []

    try:
        parsed = json.loads(raw_text)
        if isinstance(parsed, list):
            jobs = parsed
        elif isinstance(parsed, dict):
            jobs = parsed.get("jobs", parsed.get("listings", []))
    except (json.JSONDecodeError, ValueError):
        # Parse from markdown — each job is typically a line with title
        lines = [l.strip() for l in raw_text.split("\n") if l.strip()]
        for line in lines:
            if re.search(r'\b(engineer|manager|analyst|scientist|developer|director)\b', line, re.I):
                jobs.append({"title": line[:100]})

    role_counts = {"engineering": 0, "sales": 0, "ops": 0, "other": 0}
    titles = []
    for job in jobs:
        title = str(job.get("title", job.get("position", "")))
        if title:
            titles.append(title)
            role = _classify_role(title)
            role_counts[role] += 1

    total = max(sum(role_counts.values()), 1)
    role_mix = {k: round(v / total * 100, 1) for k, v in role_counts.items()}
    return {
        "total_postings": len(jobs),
        "role_mix": role_mix,
        "sample_titles": titles[:5],
    }


def _parse_company_profile(raw_text: str) -> dict:
    """Parse company profile text into structured data."""
    try:
        data = json.loads(raw_text)
        if isinstance(data, dict):
            return {
                "headcount": data.get("employeeCount") or data.get("staffCount"),
                "followers": data.get("followersCount") or data.get("followers"),
                "description": str(data.get("description", ""))[:500],
                "industry": data.get("industries", [None])[0] if isinstance(data.get("industries"), list) else data.get("industry"),
            }
    except (json.JSONDecodeError, ValueError):
        pass

    # Regex fallback on markdown
    headcount: int | None = None
    m = re.search(r'(\d[\d,]+)\s+(?:employees?|staff)', raw_text, re.I)
    if m:
        try:
            headcount = int(m.group(1).replace(",", ""))
        except ValueError:
            pass

    return {
        "headcount": headcount,
        "followers": None,
        "description": raw_text[:500],
        "industry": None,
    }


@instrument("linkedin")
@ttl_cache(ttl_seconds=3600)
async def fetch(ticker: str) -> SourceResult:
    """
    Async entry: fetch LinkedIn hiring data via BrightData MCP.
    """
    t0 = time.monotonic()
    ticker = ticker.upper().strip()

    try:
        # Step 1: Find company LinkedIn URL via SERP
        search_query = f"{ticker} site:linkedin.com/company"
        search_raw = await asyncio.wait_for(
            search_engine(search_query),
            timeout=8.0,
        )
        linkedin_url = _find_linkedin_url(search_raw, ticker)

        company_data: dict = {}
        if linkedin_url:
            # Step 2: Company profile
            try:
                profile_raw = await asyncio.wait_for(
                    web_data_linkedin_company_profile(linkedin_url),
                    timeout=10.0,
                )
                company_data = _parse_company_profile(profile_raw)
            except Exception as exc:
                logger.warning("LinkedIn profile fetch failed: %s", exc)
                company_data = {}

        # Step 3: Job listings — use ticker as company keyword
        listings_raw = await asyncio.wait_for(
            web_data_linkedin_job_listings(ticker, limit=30),
            timeout=10.0,
        )
        listing_data = _parse_job_listings(listings_raw)

        total_postings = listing_data["total_postings"]
        role_mix = listing_data["role_mix"]

        # Determine hiring signal
        if total_postings >= 20:
            hiring_direction = "expanding"
            signal = "bullish"
        elif total_postings >= 5:
            hiring_direction = "stable"
            signal = "neutral"
        else:
            hiring_direction = "contracting"
            signal = "bearish"

        # R&D investment signal: high engineering % = innovation investment
        eng_pct = role_mix.get("engineering", 0)
        sales_pct = role_mix.get("sales", 0)
        growth_focus = "r&d_heavy" if eng_pct > 50 else ("gtm_heavy" if sales_pct > 40 else "balanced")

        data = {
            "total_postings": total_postings,
            "hiring_direction": hiring_direction,
            "signal": signal,
            "role_mix": role_mix,
            "growth_focus": growth_focus,
            "headcount": company_data.get("headcount"),
            "linkedin_url": linkedin_url,
            "sample_job_titles": listing_data["sample_titles"],
            "hiring_narrative": (
                f"{ticker} has {total_postings} active LinkedIn postings. "
                f"Role mix: {eng_pct:.0f}% engineering, {sales_pct:.0f}% sales. "
                f"Hiring direction: {hiring_direction} ({growth_focus})."
            ),
        }

        return SourceResult(
            source="linkedin",
            status=SourceStatus.OK,
            data=data,
            latency_ms=int((time.monotonic() - t0) * 1000),
        )

    except BrightDataError as exc:
        status = SourceStatus.BLOCKED if exc.code == 0 else SourceStatus.ERROR
        return SourceResult(
            source="linkedin",
            status=status,
            error_msg=str(exc),
            latency_ms=int((time.monotonic() - t0) * 1000),
        )
    except asyncio.TimeoutError:
        return SourceResult(
            source="linkedin",
            status=SourceStatus.TIMEOUT,
            error_msg="LinkedIn BrightData call timed out",
            latency_ms=int((time.monotonic() - t0) * 1000),
        )
    except Exception as exc:
        return SourceResult(
            source="linkedin",
            status=SourceStatus.ERROR,
            error_msg=f"{type(exc).__name__}: {exc}",
            latency_ms=int((time.monotonic() - t0) * 1000),
        )
