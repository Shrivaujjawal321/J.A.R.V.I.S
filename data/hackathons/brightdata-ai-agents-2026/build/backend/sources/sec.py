"""
backend/sources/sec.py
======================
SEC EDGAR source for AltBrief.

Returns for a given ticker:
  - InsiderTxn list: Form 4 transactions in the last 90 days with net sentiment
  - RiskFactor list: top 5 from the latest 10-K Item 1A
  - EarningsGuidance: extracted from latest 10-Q MD&A + 8-K (Item 2.02 / press release)

Architecture
------------
edgartools (v5.31.5+) is the primary parsing layer — it gives us structured Python
objects instead of raw XML/HTML gymnastics.  It is synchronous, so all calls are
wrapped in asyncio.run_in_executor(thread_pool) to keep the FastAPI event loop free.

Rate limiting is handled by edgartools' internal pyrate-limiter (default 9 req/s).
We additionally set EDGAR_ACCESS_MODE=CAUTION (5 connections, 20s timeout) to be
well-behaved. A module-level ThreadPoolExecutor(max_workers=4) avoids spawning
new threads per request.

CIK lookup: cached locally in {CACHE_DIR}/company_tickers.json, refreshed weekly.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import re
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import httpx
from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Local schema import — adjust relative path to match your project layout
# ---------------------------------------------------------------------------
try:
    from backend.schemas import SourceResult, SourceStatus
except ImportError:
    # Fallback for running this file standalone / in tests
    from schemas import SourceResult, SourceStatus  # type: ignore

# ---------------------------------------------------------------------------
# edgartools — hard dependency
# ---------------------------------------------------------------------------
try:
    import edgar as et
    from edgar import Company as EdgarCompany
    from edgar import set_identity
    _HAS_EDGARTOOLS = True
except ImportError as _e:
    _HAS_EDGARTOOLS = False
    _EDGARTOOLS_ERR = str(_e)

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
EDGAR_IDENTITY: str = os.getenv(
    "EDGAR_IDENTITY",
    "AltBrief research@altbrief.com",
)
CACHE_DIR: Path = Path(os.getenv("ALTBRIEF_CACHE_DIR", "/tmp/altbrief_cache"))
TICKER_CACHE_FILE: Path = CACHE_DIR / "company_tickers.json"
TICKER_CACHE_TTL_DAYS: int = 7

# SEC public endpoint for ticker → CIK mapping
TICKERS_URL = "https://www.sec.gov/files/company_tickers.json"

# User-Agent header for raw httpx calls (SEC requires this; 403 without it)
SEC_HEADERS: dict[str, str] = {
    "User-Agent": EDGAR_IDENTITY,
    "Accept-Encoding": "gzip, deflate",
}

# Thread pool for wrapping synchronous edgartools calls
_EXECUTOR = ThreadPoolExecutor(max_workers=4, thread_name_prefix="edgar_worker")

# Window for insider transaction lookups
INSIDER_LOOKBACK_DAYS = 90

# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------


class InsiderTxn(BaseModel):
    """A single Form 4 non-derivative transaction (open-market buy or sell only)."""
    insider_name: str
    role: str = Field(description="Officer title, Director, or 10% Owner")
    transaction_date: date
    transaction_code: str = Field(description="P=purchase S=sale A=grant M=exercise")
    shares: float
    price_per_share: float | None = None
    total_value: float | None = None
    acquired_disposed: str = Field(description="A=acquired D=disposed")
    security_title: str = "Common Stock"
    filing_url: str | None = None


class InsiderSummary(BaseModel):
    ticker: str
    lookback_days: int = INSIDER_LOOKBACK_DAYS
    transactions: list[InsiderTxn] = Field(default_factory=list)
    net_buy_volume_usd: float = 0.0
    net_sell_volume_usd: float = 0.0
    sentiment: str = Field(
        description="net_buy | net_sell | neutral | insufficient_data"
    )
    unique_insiders: int = 0


class RiskFactor(BaseModel):
    rank: int
    text: str = Field(description="Full paragraph text of the risk factor")
    char_count: int = 0


class EarningsGuidance(BaseModel):
    source_form: str = Field(description="10-Q | 8-K | none")
    filing_date: date | None = None
    guidance_snippets: list[str] = Field(
        default_factory=list,
        description="Verbatim sentences containing forward guidance language",
    )
    raw_truncated: str = Field(
        default="",
        description="First 1000 chars of MD&A / Item 2.02 text for LLM synthesis",
    )


class SECData(BaseModel):
    ticker: str
    company_name: str = ""
    cik: str = ""
    insider_summary: InsiderSummary | None = None
    risk_factors: list[RiskFactor] = Field(default_factory=list)
    earnings_guidance: EarningsGuidance | None = None
    data_quality: str = Field(
        default="full", description="full | partial | minimal"
    )


# ---------------------------------------------------------------------------
# CIK lookup cache
# ---------------------------------------------------------------------------


def _load_ticker_cache() -> dict[str, int]:
    """Return ticker -> CIK int mapping. Refresh if stale or missing."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    now = time.time()

    if TICKER_CACHE_FILE.exists():
        age_days = (now - TICKER_CACHE_FILE.stat().st_mtime) / 86400
        if age_days < TICKER_CACHE_TTL_DAYS:
            try:
                raw = json.loads(TICKER_CACHE_FILE.read_text())
                # raw is ordinal-keyed dict from SEC; convert to ticker->cik
                return {v["ticker"].upper(): v["cik_str"] for v in raw.values()}
            except (json.JSONDecodeError, KeyError):
                logger.warning("Ticker cache corrupted — will re-fetch")

    # Fetch fresh
    logger.info("Fetching company_tickers.json from SEC")
    try:
        resp = httpx.get(TICKERS_URL, headers=SEC_HEADERS, timeout=20.0, follow_redirects=True)
        resp.raise_for_status()
        raw = resp.json()
        TICKER_CACHE_FILE.write_text(json.dumps(raw))
        return {v["ticker"].upper(): v["cik_str"] for v in raw.values()}
    except Exception as exc:
        logger.error("Failed to fetch company_tickers.json: %s", exc)
        return {}


_TICKER_CACHE: dict[str, int] = {}
_TICKER_CACHE_LOADED_AT: float = 0.0


def _get_cik(ticker: str) -> int | None:
    """Return integer CIK for ticker, or None if not found in EDGAR."""
    global _TICKER_CACHE, _TICKER_CACHE_LOADED_AT
    now = time.time()
    if not _TICKER_CACHE or (now - _TICKER_CACHE_LOADED_AT) > TICKER_CACHE_TTL_DAYS * 86400:
        _TICKER_CACHE = _load_ticker_cache()
        _TICKER_CACHE_LOADED_AT = now
    return _TICKER_CACHE.get(ticker.upper())


def _cik_padded(cik_int: int) -> str:
    """Return zero-padded 10-digit CIK string."""
    return str(cik_int).zfill(10)


# ---------------------------------------------------------------------------
# edgartools identity bootstrap
# ---------------------------------------------------------------------------


def _bootstrap_edgartools() -> None:
    """Configure edgartools once. Called lazily before first use."""
    if not _HAS_EDGARTOOLS:
        raise ImportError(
            f"edgartools is required: pip install 'edgartools>=5.31,<6'. "
            f"Original error: {_EDGARTOOLS_ERR}"
        )
    set_identity(EDGAR_IDENTITY)
    # Use CAUTION mode: 5 connections, 20s timeout, conservative on rate
    os.environ.setdefault("EDGAR_ACCESS_MODE", "CAUTION")
    # Enable local file caching to avoid re-downloading filings
    edgar_cache = str(CACHE_DIR / "edgar_files")
    os.environ.setdefault("EDGAR_LOCAL_DATA_DIR", edgar_cache)


# ---------------------------------------------------------------------------
# Insider transaction parsing helpers
# ---------------------------------------------------------------------------

# Transaction codes that carry directional signal
_BULLISH_CODES = {"P"}   # Open-market purchase
_BEARISH_CODES = {"S"}   # Open-market sale
_NEUTRAL_CODES = {"A", "M", "G", "F", "J", "C", "X", "W", "Z"}


def _safe_float(val: Any) -> float | None:
    if val is None:
        return None
    try:
        return float(str(val).replace(",", "").strip())
    except (ValueError, TypeError):
        return None


def _parse_edgartools_form4(filing, cik_int: int) -> list[InsiderTxn]:
    """Parse one Form 4 filing via edgartools; return list of InsiderTxn."""
    try:
        ownership = filing.obj()
    except Exception as exc:
        logger.debug("edgartools could not parse Form 4 filing: %s", exc)
        return []

    txns: list[InsiderTxn] = []

    # Resolve role label
    try:
        is_officer = getattr(ownership, "is_officer", False) or False
        officer_title = getattr(ownership, "officer_title", "") or ""
        is_director = getattr(ownership, "is_director", False) or False
        is_10pct = getattr(ownership, "is_ten_percent_owner", False) or False
        owner_name = getattr(ownership, "reporting_owner_name", None) or \
                     getattr(ownership, "owner_name", "Unknown")

        if is_officer and officer_title:
            role = officer_title
        elif is_director:
            role = "Director"
        elif is_10pct:
            role = "10% Owner"
        else:
            role = "Insider"
    except Exception:
        owner_name, role = "Unknown", "Insider"

    # Build accession URL for attribution
    try:
        acc = filing.accession_number.replace("-", "")
        filing_url = (
            f"https://www.sec.gov/Archives/edgar/data/{cik_int}/{acc}/"
            f"{filing.accession_number}-index.htm"
        )
    except Exception:
        filing_url = None

    # Extract transactions DataFrame and iterate rows
    try:
        df = ownership.to_dataframe()
        if df is None or df.empty:
            return []

        for _, row in df.iterrows():
            code = str(row.get("transaction_code", "")).strip().upper()
            if code not in (_BULLISH_CODES | _BEARISH_CODES):
                continue  # Skip non-market transactions (grants, exercises, etc.)

            shares = _safe_float(row.get("shares", row.get("transaction_shares")))
            price = _safe_float(row.get("price", row.get("price_per_share")))
            total = (shares * price) if (shares and price) else None

            # Date
            raw_date = row.get("transaction_date", row.get("date"))
            if raw_date is None:
                continue
            if isinstance(raw_date, (datetime, date)):
                txn_date = raw_date.date() if isinstance(raw_date, datetime) else raw_date
            else:
                try:
                    txn_date = date.fromisoformat(str(raw_date)[:10])
                except ValueError:
                    continue

            acq_disp = str(row.get("acquired_disposed_code", "D")).strip().upper()
            security = str(row.get("security_title", "Common Stock")) or "Common Stock"

            txns.append(InsiderTxn(
                insider_name=str(owner_name),
                role=str(role),
                transaction_date=txn_date,
                transaction_code=code,
                shares=shares or 0.0,
                price_per_share=price,
                total_value=total,
                acquired_disposed=acq_disp,
                security_title=security,
                filing_url=filing_url,
            ))
    except Exception as exc:
        logger.warning("Error iterating Form 4 DataFrame: %s", exc)

    return txns


def _compute_insider_summary(ticker: str, cik_int: int) -> InsiderSummary:
    """Fetch Form 4 filings for last 90 days and compute sentiment."""
    _bootstrap_edgartools()
    cutoff = date.today() - timedelta(days=INSIDER_LOOKBACK_DAYS)

    try:
        company = EdgarCompany(ticker.upper())
        all_filings = company.get_filings(form="4")
    except Exception as exc:
        logger.error("edgartools get_filings(4) failed for %s: %s", ticker, exc)
        return InsiderSummary(
            ticker=ticker, sentiment="insufficient_data", transactions=[]
        )

    transactions: list[InsiderTxn] = []

    try:
        # edgartools Filings object supports iteration; filter by date
        for filing in all_filings:
            try:
                filing_date_str = filing.filing_date
                if isinstance(filing_date_str, str):
                    fd = date.fromisoformat(filing_date_str[:10])
                elif isinstance(filing_date_str, (date, datetime)):
                    fd = filing_date_str.date() if isinstance(filing_date_str, datetime) else filing_date_str
                else:
                    continue
            except (ValueError, AttributeError):
                continue

            if fd < cutoff:
                break  # Filings are returned newest-first; stop early

            parsed = _parse_edgartools_form4(filing, cik_int)
            transactions.extend(parsed)
    except Exception as exc:
        logger.warning("Error iterating Form 4 filings for %s: %s", ticker, exc)

    # Compute sentiment
    buy_vol = sum(t.total_value or 0 for t in transactions if t.transaction_code == "P")
    sell_vol = sum(t.total_value or 0 for t in transactions if t.transaction_code == "S")
    net = buy_vol - sell_vol

    if not transactions:
        sentiment = "insufficient_data"
    elif abs(net) < 50_000:  # Less than $50k net — call it neutral
        sentiment = "neutral"
    elif net > 0:
        sentiment = "net_buy"
    else:
        sentiment = "net_sell"

    unique_insiders = len({t.insider_name for t in transactions})

    return InsiderSummary(
        ticker=ticker,
        lookback_days=INSIDER_LOOKBACK_DAYS,
        transactions=transactions,
        net_buy_volume_usd=buy_vol,
        net_sell_volume_usd=sell_vol,
        sentiment=sentiment,
        unique_insiders=unique_insiders,
    )


# ---------------------------------------------------------------------------
# Risk factor extraction
# ---------------------------------------------------------------------------

# Regex for Item 1A / Item 1B boundary detection (fallback path)
_ITEM_1A_RE = re.compile(
    r'(?:item\s*1a\.?\s*[-—]?\s*risk\s*factors|risk\s*factors\s*item\s*1a)',
    re.IGNORECASE,
)
_ITEM_1B_RE = re.compile(
    r'item\s*1b\.?\s',
    re.IGNORECASE,
)
_ITEM_2_RE = re.compile(
    r'item\s*2\.?\s',
    re.IGNORECASE,
)


def _extract_risk_factors_fallback(html_or_text: str) -> str:
    """Regex + BS4 fallback when edgartools risk_factors returns None."""
    try:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html_or_text, "lxml")
        text = soup.get_text(separator="\n")
    except ImportError:
        text = html_or_text

    lines = text.split("\n")
    capturing = False
    buffer: list[str] = []
    found_once = False

    for line in lines:
        stripped = line.strip()
        if not stripped:
            if capturing:
                buffer.append("")
            continue

        if _ITEM_1A_RE.search(stripped):
            if not found_once:
                found_once = True
                # Skip TOC entries (very short matches without body text)
                if len(stripped) < 80:
                    continue
            capturing = True
            continue

        if capturing:
            if _ITEM_1B_RE.search(stripped) or _ITEM_2_RE.search(stripped):
                break
            buffer.append(stripped)

    result = "\n".join(buffer).strip()

    # If we got less than 200 chars, probably hit a TOC — return empty to signal failure
    if len(result) < 200:
        return ""
    return result


def _split_risk_factors(full_text: str) -> list[str]:
    """
    Split the Item 1A block into individual risk factors.
    Risk factors are typically separated by bolded headings or blank lines
    followed by a capital-letter sentence. We use length as a quality proxy.
    """
    # Try splitting on double-newline + uppercase start (common pattern)
    chunks = re.split(r'\n{2,}', full_text)
    # Filter out very short chunks (headers, page numbers, boilerplate)
    paragraphs = [c.strip() for c in chunks if len(c.strip()) > 150]
    # Sort by length descending — longer = more specific
    paragraphs.sort(key=len, reverse=True)
    return paragraphs


def _fetch_risk_factors(ticker: str) -> list[RiskFactor]:
    """Fetch and return top-5 risk factors from the latest 10-K."""
    _bootstrap_edgartools()

    try:
        company = EdgarCompany(ticker.upper())
        tenk_filings = company.get_filings(form="10-K")
    except Exception as exc:
        logger.error("get_filings(10-K) failed for %s: %s", ticker, exc)
        return []

    # Try up to 2 most recent 10-K filings (in case the latest is still processing)
    for idx in range(min(2, len(tenk_filings) if hasattr(tenk_filings, '__len__') else 2)):
        try:
            filing = tenk_filings[idx]
            tenk = filing.obj()
        except (IndexError, Exception) as exc:
            logger.debug("Could not parse 10-K[%d] for %s: %s", idx, ticker, exc)
            continue

        # Primary path: edgartools built-in property
        risk_text: str | None = None
        try:
            rf = getattr(tenk, "risk_factors", None)
            if rf and isinstance(rf, str) and len(rf) > 200:
                risk_text = rf
        except Exception:
            pass

        # Fallback: fetch raw filing HTML and regex-parse
        if not risk_text:
            try:
                raw_html = filing.text()
                risk_text = _extract_risk_factors_fallback(raw_html)
            except Exception as exc2:
                logger.warning("Fallback risk factor extraction failed for %s: %s", ticker, exc2)

        if not risk_text:
            continue

        paragraphs = _split_risk_factors(risk_text)
        top5 = paragraphs[:5]

        return [
            RiskFactor(
                rank=i + 1,
                text=p,
                char_count=len(p),
            )
            for i, p in enumerate(top5)
        ]

    logger.warning("No risk factors extracted for %s", ticker)
    return []


# ---------------------------------------------------------------------------
# Earnings guidance extraction
# ---------------------------------------------------------------------------

_GUIDANCE_PATTERNS: list[re.Pattern] = [
    re.compile(
        r'(?:we\s+expect|we\s+anticipate|we\s+project|we\s+guide|guidance|outlook|forecast)'
        r'[^\n]{0,350}',
        re.IGNORECASE,
    ),
    re.compile(
        r'(?:revenue|net revenue|total revenue|earnings per share|eps|operating income)'
        r'[^\n]*(?:guidance|expects?|anticipates?|projects?|will\s+be|to\s+be\s+approximately)'
        r'[^\n]{0,200}',
        re.IGNORECASE,
    ),
]


def _extract_guidance_snippets(text: str) -> list[str]:
    """Return up to 5 forward-guidance sentences from a text block."""
    snippets: list[str] = []
    for pat in _GUIDANCE_PATTERNS:
        for m in pat.finditer(text):
            snippet = m.group(0).strip()
            if len(snippet) > 40 and snippet not in snippets:
                snippets.append(snippet)
            if len(snippets) >= 5:
                break
        if len(snippets) >= 5:
            break
    return snippets[:5]


def _fetch_earnings_guidance(ticker: str) -> EarningsGuidance:
    """Fetch earnings guidance from latest 10-Q (MD&A) and 8-K (Item 2.02)."""
    _bootstrap_edgartools()

    # --- Try 10-Q MD&A first ---
    try:
        company = EdgarCompany(ticker.upper())
        tenq_filings = company.get_filings(form="10-Q")

        if tenq_filings:
            tenq_filing = tenq_filings[0]
            tenq = tenq_filing.obj()

            mda_text: str | None = None
            for attr in ("management_discussion", "mda", "management_discussion_and_analysis"):
                mda_text = getattr(tenq, attr, None)
                if mda_text and isinstance(mda_text, str) and len(mda_text) > 100:
                    break

            if not mda_text:
                # Fallback: full text search
                try:
                    mda_text = tenq_filing.text()[:8000]
                except Exception:
                    mda_text = ""

            if mda_text:
                snippets = _extract_guidance_snippets(mda_text)
                filing_date_raw = getattr(tenq_filing, "filing_date", None)
                try:
                    fd = (
                        date.fromisoformat(str(filing_date_raw)[:10])
                        if filing_date_raw else None
                    )
                except ValueError:
                    fd = None

                return EarningsGuidance(
                    source_form="10-Q",
                    filing_date=fd,
                    guidance_snippets=snippets,
                    raw_truncated=mda_text[:1000],
                )
    except Exception as exc:
        logger.warning("10-Q guidance extraction failed for %s: %s", ticker, exc)

    # --- Fallback: 8-K Item 2.02 ---
    try:
        company = EdgarCompany(ticker.upper())
        eightk_filings = company.get_filings(form="8-K")

        for filing in eightk_filings.head(5):
            try:
                eightk = filing.obj()

                # Try structured item access
                item_text: str | None = None
                for item_key in ("Item 2.02", "item 2.02", "Item 7", "item 7"):
                    try:
                        val = eightk.get(item_key) if hasattr(eightk, "get") else None
                        if val and isinstance(val, str) and len(val) > 50:
                            item_text = val
                            break
                    except Exception:
                        pass

                # Fallback: full filing text
                if not item_text:
                    item_text = filing.text()[:6000]

                if not item_text:
                    continue

                snippets = _extract_guidance_snippets(item_text)
                if not snippets:
                    continue  # This 8-K has no guidance language — try next

                filing_date_raw = getattr(filing, "filing_date", None)
                try:
                    fd = date.fromisoformat(str(filing_date_raw)[:10]) if filing_date_raw else None
                except ValueError:
                    fd = None

                return EarningsGuidance(
                    source_form="8-K",
                    filing_date=fd,
                    guidance_snippets=snippets,
                    raw_truncated=item_text[:1000],
                )
            except Exception as exc:
                logger.debug("8-K parse attempt failed: %s", exc)
                continue

    except Exception as exc:
        logger.warning("8-K guidance extraction failed for %s: %s", ticker, exc)

    return EarningsGuidance(source_form="none", guidance_snippets=[])


# ---------------------------------------------------------------------------
# Synchronous core (called from executor)
# ---------------------------------------------------------------------------


def _fetch_all_sync(ticker: str) -> SECData:
    """
    Synchronous fetch of all three data types.
    Runs in a thread pool — do NOT call directly from async code.
    """
    ticker_upper = ticker.upper()
    cik_int = _get_cik(ticker_upper)

    if cik_int is None:
        # Return minimal object — caller will surface as error
        return SECData(
            ticker=ticker_upper,
            company_name="NOT_IN_EDGAR",
            cik="",
            data_quality="minimal",
        )

    cik_str = _cik_padded(cik_int)

    # Resolve company name from submissions API (lightweight)
    company_name = ticker_upper
    try:
        resp = httpx.get(
            f"https://data.sec.gov/submissions/CIK{cik_str}.json",
            headers=SEC_HEADERS,
            timeout=15.0,
            follow_redirects=True,
        )
        resp.raise_for_status()
        company_name = resp.json().get("name", ticker_upper)
    except Exception:
        pass  # Company name is cosmetic — don't fail on it

    # Insider transactions
    insider_summary: InsiderSummary | None = None
    quality_flags: list[str] = []
    try:
        insider_summary = _compute_insider_summary(ticker_upper, cik_int)
    except Exception as exc:
        logger.error("Insider summary failed for %s: %s", ticker_upper, exc)
        quality_flags.append("insider_failed")

    # Risk factors
    risk_factors: list[RiskFactor] = []
    try:
        risk_factors = _fetch_risk_factors(ticker_upper)
    except Exception as exc:
        logger.error("Risk factors failed for %s: %s", ticker_upper, exc)
        quality_flags.append("risk_factors_failed")

    # Earnings guidance
    earnings_guidance: EarningsGuidance | None = None
    try:
        earnings_guidance = _fetch_earnings_guidance(ticker_upper)
    except Exception as exc:
        logger.error("Earnings guidance failed for %s: %s", ticker_upper, exc)
        quality_flags.append("guidance_failed")

    # Determine data quality
    n_failed = len(quality_flags)
    if n_failed == 0:
        quality = "full"
    elif n_failed == 1:
        quality = "partial"
    else:
        quality = "minimal"

    return SECData(
        ticker=ticker_upper,
        company_name=company_name,
        cik=cik_str,
        insider_summary=insider_summary,
        risk_factors=risk_factors,
        earnings_guidance=earnings_guidance,
        data_quality=quality,
    )


# ---------------------------------------------------------------------------
# Public async entry point
# ---------------------------------------------------------------------------


async def fetch(ticker: str) -> SourceResult:
    """
    Async entry point — drop-in for AltBrief's source pipeline.

    Parameters
    ----------
    ticker : str
        Equity ticker symbol (e.g. "NVDA", "XOM", "WMT").

    Returns
    -------
    SourceResult
        Standard AltBrief envelope with `data` as a SECData dict.
    """
    t0 = time.monotonic()

    if not ticker or not isinstance(ticker, str):
        return SourceResult(
            source="sec",
            status=SourceStatus.ERROR,
            error_msg="ticker must be a non-empty string",
            latency_ms=0,
        )

    if not _HAS_EDGARTOOLS:
        return SourceResult(
            source="sec",
            status=SourceStatus.ERROR,
            error_msg=(
                f"edgartools not installed. Run: pip install 'edgartools>=5.31,<6'. "
                f"Detail: {_EDGARTOOLS_ERR}"
            ),
            latency_ms=0,
        )

    loop = asyncio.get_event_loop()
    try:
        sec_data: SECData = await loop.run_in_executor(
            _EXECUTOR,
            _fetch_all_sync,
            ticker,
        )
    except Exception as exc:
        latency_ms = int((time.monotonic() - t0) * 1000)
        logger.exception("SEC fetch failed for %s: %s", ticker, exc)
        return SourceResult(
            source="sec",
            status=SourceStatus.ERROR,
            error_msg=str(exc),
            latency_ms=latency_ms,
        )

    latency_ms = int((time.monotonic() - t0) * 1000)

    # Map data quality to status
    if sec_data.company_name == "NOT_IN_EDGAR":
        return SourceResult(
            source="sec",
            status=SourceStatus.ERROR,
            error_msg=f"Ticker '{ticker}' not found in EDGAR (foreign listing or OTC?)",
            latency_ms=latency_ms,
        )

    status = SourceStatus.OK if sec_data.data_quality in ("full", "partial") else SourceStatus.ERROR

    return SourceResult(
        source="sec",
        status=status,
        data=sec_data.model_dump(),
        latency_ms=latency_ms,
        cached=False,
    )


# ---------------------------------------------------------------------------
# Convenience: synthesize a Signal (for AltBrief brief assembler)
# ---------------------------------------------------------------------------


def insider_to_signal(sec_data: SECData) -> dict | None:
    """
    Convert InsiderSummary into a bullish/bearish/neutral Signal dict
    compatible with backend.schemas.Signal.

    Returns None if sentiment is insufficient_data.
    """
    if not sec_data.insider_summary:
        return None
    s = sec_data.insider_summary
    if s.sentiment == "insufficient_data":
        return None

    sentiment_map = {
        "net_buy": "bullish",
        "net_sell": "bearish",
        "neutral": "neutral",
    }
    direction = sentiment_map.get(s.sentiment, "neutral")

    net_usd = s.net_buy_volume_usd - s.net_sell_volume_usd
    abs_net = abs(net_usd)
    sign = "+" if net_usd >= 0 else "-"

    summary = (
        f"{s.unique_insiders} insider(s) had net {s.sentiment.replace('_', ' ')} "
        f"of ${abs_net:,.0f} over 90 days."
    )
    recent = s.transactions[0] if s.transactions else None
    raw_evidence = (
        f"{recent.insider_name} ({recent.role}): "
        f"{'bought' if recent.transaction_code == 'P' else 'sold'} "
        f"{recent.shares:,.0f} shares @ ${recent.price_per_share or 0:,.2f} "
        f"on {recent.transaction_date}"
        if recent else "No individual transaction detail available."
    )

    return {
        "source": "sec",
        "direction": direction,
        "summary": summary[:240],
        "confidence": 0.80,
        "raw_evidence": raw_evidence[:600],
        "citation_url": recent.filing_url if recent else None,
        "research_anchor": "Cohen-Malloy-Pomorski JoF 2012",  # seminal insider trading paper
    }


# ---------------------------------------------------------------------------
# CLI smoke-test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys

    logging.basicConfig(level=logging.INFO)
    ticker_arg = sys.argv[1] if len(sys.argv) > 1 else "NVDA"

    async def _main():
        result = await fetch(ticker_arg)
        print(f"\nStatus : {result.status}")
        print(f"Latency: {result.latency_ms}ms")
        if result.status == SourceStatus.OK:
            data = SECData(**result.data)
            print(f"Company: {data.company_name} (CIK {data.cik})")
            print(f"Quality: {data.data_quality}")
            if data.insider_summary:
                s = data.insider_summary
                print(f"\nInsider sentiment ({INSIDER_LOOKBACK_DAYS}d): {s.sentiment}")
                print(f"  Buy volume : ${s.net_buy_volume_usd:,.0f}")
                print(f"  Sell volume: ${s.net_sell_volume_usd:,.0f}")
                print(f"  Transactions: {len(s.transactions)}")
                for t in s.transactions[:3]:
                    print(f"    {t.insider_name} | {t.transaction_code} | "
                          f"{t.shares:,.0f} @ ${t.price_per_share or 0:.2f} | {t.transaction_date}")
            if data.risk_factors:
                print(f"\nRisk factors (top {len(data.risk_factors)}):")
                for rf in data.risk_factors:
                    print(f"  [{rf.rank}] {rf.text[:120]}...")
            if data.earnings_guidance:
                eg = data.earnings_guidance
                print(f"\nGuidance source: {eg.source_form} ({eg.filing_date})")
                for snip in eg.guidance_snippets[:3]:
                    print(f"  • {snip[:120]}")
        else:
            print(f"Error: {result.error_msg}")

    asyncio.run(_main())
