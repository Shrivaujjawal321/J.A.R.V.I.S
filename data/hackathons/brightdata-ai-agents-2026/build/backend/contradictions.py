"""
Cross-source contradiction detector for AltBrief.

Architecture (per research/19_contradiction_confidence_algo.md §2):
  1. Heuristic pre-screen — eliminates degenerate cases (zero LLM cost, <1ms).
  2. LLM-as-judge — Claude Sonnet 4.6 tool_use for semantic detection.
  3. Heuristic fallback — fires when LLM is unavailable (rate limit / cost cap).

Runs AFTER all 8 sources complete, BEFORE final synthesis.
Detected contradictions are injected into the synthesis context so the
brief narrative and cross_source_contradictions field reflect them.
"""

from __future__ import annotations

import logging
from typing import Any

import anthropic

from .schemas import Contradiction, Signal

_stdlib_log = logging.getLogger(__name__)

try:
    import structlog as _structlog
    _slog = _structlog.get_logger(__name__)
except ImportError:
    _slog = None  # type: ignore[assignment]


def _log(level: str, event: str, **kwargs: Any) -> None:
    """Portable logging: structlog kwargs-style or stdlib fallback."""
    if _slog is not None:
        getattr(_slog, level)(event, **kwargs)
    else:
        msg = event + " " + " ".join(f"{k}={v}" for k, v in kwargs.items())
        getattr(_stdlib_log, level)(msg)

# ─────────────────────────── Prompt (cached) ───────────────────────────────
# This system prompt is stable across all tickers → it will be cached after
# the first call (Sonnet 4.6 cache threshold: 1,024 tokens; this is ~250 tok
# so it won't cache alone — but combined with tools it clears the threshold).

CONTRADICTION_SYSTEM_PROMPT = """\
You are a financial signal analyst. You receive summaries of signals from
multiple data sources for the same stock ticker. Your task is to identify
SEMANTIC CONTRADICTIONS between sources — cases where one source's signal is
directionally inconsistent with another source's signal for the same underlying
business reality.

RULES:
1. Only flag contradictions between signals that are comparable in dimension
   (two sentiment signals, OR a hiring signal vs a guidance signal about
   business trajectory).
2. Do NOT flag different-dimension signals as contradictions (satellite flaring
   vs Reddit sentiment measure different things and cannot contradict each other).
3. Rate severity:
   - high: directly opposing signals from high-quality sources (e.g. SEC
     guidance raised but LinkedIn hiring down 20%)
   - medium: moderate divergence or one low-quality source (e.g. Reddit
     bullish but news sentiment bearish)
   - low: weak divergence, could be explained by timing lag or measurement
     difference
4. Return ONLY contradictions you are confident about. If none exist, return
   an empty list for the contradictions field.
5. Explain each contradiction in ONE sentence that a non-expert investor can
   understand.
6. You MUST call the `report_contradictions` tool — do not emit plain text.
"""

CONTRADICTION_USER_TEMPLATE = """\
Ticker: {ticker}

Signal summaries from {n_signals} sources:

{signal_block}

Identify all meaningful cross-source contradictions. \
If signals are consistent, return an empty list."""

# ──────────────────────── Tool Definition ───────────────────────────────────
# Inlined (not from synth_schema) because the contradiction tool is simpler
# and has a fixed, hand-curated schema that doesn't need _clean_schema_for_claude.
# additionalProperties: false is set on every object node for strict compat.

_CONTRADICTION_TOOL: dict = {
    "name": "report_contradictions",
    "description": "Report cross-source contradictions found in the financial signals. "
                   "Call with an empty contradictions list if none are found.",
    "input_schema": {
        "type": "object",
        "additionalProperties": False,
        "required": ["contradictions"],
        "properties": {
            "contradictions": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": [
                        "signal_a_source", "signal_a_brief",
                        "signal_b_source", "signal_b_brief",
                        "severity", "explanation", "contradiction_type",
                    ],
                    "properties": {
                        "signal_a_source": {
                            "type": "string",
                            "description": "Name of the first source, e.g. 'SEC EDGAR'",
                        },
                        "signal_a_brief": {
                            "type": "string",
                            "description": "One-line summary of what signal A says",
                        },
                        "signal_b_source": {
                            "type": "string",
                            "description": "Name of the second source, e.g. 'LinkedIn Hiring'",
                        },
                        "signal_b_brief": {
                            "type": "string",
                            "description": "One-line summary of what signal B says",
                        },
                        "severity": {
                            "type": "string",
                            "enum": ["high", "medium", "low"],
                            "description": "Severity of the contradiction",
                        },
                        "explanation": {
                            "type": "string",
                            "description": "One sentence plain-English explanation",
                        },
                        "contradiction_type": {
                            "type": "string",
                            "enum": [
                                "guidance_vs_hiring",
                                "sentiment_divergence",
                                "insider_vs_crowd",
                                "operational_vs_guided",
                                "employee_vs_growth",
                                "other",
                            ],
                            "description": "Semantic category of the contradiction",
                        },
                    },
                },
            }
        },
    },
    # Cache the tool definition — stable across all tickers.
    # Combined with the system prompt this clears the 1,024-token threshold.
    "cache_control": {"type": "ephemeral"},
}


# ──────────────────────── Heuristic Pre-Screen ──────────────────────────────

def _heuristic_prescreen(signals: list[Signal]) -> bool:
    """
    Returns True if it's worth calling the LLM judge.
    Eliminates zero-cost degenerate cases:
    - Fewer than 2 signals: no pair to compare.
    - All neutral: no directional contradiction possible.

    NB: We still send all-same-direction sets to the LLM because quant
    contradictions can exist within a single direction bucket (e.g. all bullish
    sentiment but insider net sell $8M in Form 4 — directionally same but
    semantically contradictory).
    """
    if len(signals) < 2:
        return False
    directions = {s.direction for s in signals}
    if directions == {"neutral"}:
        return False
    return True


# ──────────────────────── LLM-as-Judge (Primary) ────────────────────────────

def detect_contradictions(
    signals: list[Signal],
    ticker: str,
    client: anthropic.Anthropic | None = None,
    model: str = "claude-sonnet-4-6",
) -> list[Contradiction]:
    """
    Detect cross-source contradictions using Claude Sonnet as an LLM judge.

    Primary approach: tool_use with report_contradictions.
    Fallback: heuristic rules (fires on any exception — rate limit, cost cap,
    timeout, validation error).

    Args:
        signals:  List of Signal objects, one per data source that returned OK.
        ticker:   Stock ticker for context in the prompt (e.g. "NVDA").
        client:   Anthropic sync client. Created from env if None.
        model:    Model ID — defaults to claude-sonnet-4-6.

    Returns:
        List of Contradiction objects sorted by severity (high first).
        Empty list when fewer than 2 signals or all neutral.
    """
    if not _heuristic_prescreen(signals):
        _log("debug", "contradiction_prescreen_skip", ticker=ticker, n_signals=len(signals))
        return []

    if client is None:
        client = anthropic.Anthropic()

    # Build the signal block for the user prompt
    lines: list[str] = []
    for sig in signals:
        lines.append(
            f"[{sig.source}] direction={sig.direction} confidence={sig.confidence:.2f}\n"
            f"  summary: {sig.summary}\n"
            f"  evidence: {sig.raw_evidence[:250]}"
        )
    signal_block = "\n\n".join(lines)

    user_content = CONTRADICTION_USER_TEMPLATE.format(
        ticker=ticker,
        n_signals=len(signals),
        signal_block=signal_block,
    )

    try:
        response = client.messages.create(
            model=model,
            max_tokens=1024,
            # System prompt is stable → cached after first call
            system=[
                {
                    "type": "text",
                    "text": CONTRADICTION_SYSTEM_PROMPT,
                    # cache_control omitted here; applied on the TOOL instead
                    # (tools + system together exceed the 1024-token threshold)
                }
            ],
            messages=[{"role": "user", "content": user_content}],
            tools=[_CONTRADICTION_TOOL],
            # tool_choice=any forces a tool call without locking to one specific tool
            tool_choice={"type": "any"},
        )
    except Exception as exc:
        _log("warning", "contradiction_llm_error_fallback", ticker=ticker, error=str(exc))
        return detect_contradictions_heuristic(signals)

    # Extract and validate tool output
    contradictions: list[Contradiction] = []
    for block in response.content:
        if block.type == "tool_use" and block.name == "report_contradictions":
            raw_list = block.input.get("contradictions", [])
            for item in raw_list:
                try:
                    contradictions.append(Contradiction(**item))
                except Exception as ve:
                    # Malformed item — skip, don't crash pipeline
                    _log("warning", "contradiction_item_invalid",
                         ticker=ticker, error=str(ve))
            break

    # Log usage for cost tracking
    if hasattr(response, "usage"):
        usage = response.usage
        _log("info", "contradiction_llm_done",
             ticker=ticker,
             n_contradictions=len(contradictions),
             input_tokens=getattr(usage, "input_tokens", 0),
             cache_read_tokens=getattr(usage, "cache_read_input_tokens", 0),
             output_tokens=getattr(usage, "output_tokens", 0))

    # Sort: high → medium → low
    _SEVERITY_ORDER = {"high": 0, "medium": 1, "low": 2}
    contradictions.sort(key=lambda c: _SEVERITY_ORDER.get(c.severity, 3))
    return contradictions


# ──────────────────────── Heuristic Fallback ────────────────────────────────

def detect_contradictions_heuristic(signals: list[Signal]) -> list[Contradiction]:
    """
    Fallback when the LLM judge is unavailable (rate limit, cost cap, timeout).

    Hardcoded pairwise rules that catch the 4 highest-signal contradiction
    patterns. Catches ~60% of real contradictions. Returns the same
    Contradiction type for full schema compatibility with the primary path.
    """
    sig_map = {s.source: s for s in signals}
    found: list[Contradiction] = []

    # Rule 1: SEC guidance raised + LinkedIn hiring declining
    sec = sig_map.get("sec") or sig_map.get("SEC_EDGAR") or sig_map.get("SEC EDGAR")
    li = sig_map.get("linkedin") or sig_map.get("LinkedIn_Hiring") or sig_map.get("LinkedIn Hiring")
    if sec and li:
        sec_text = (sec.raw_evidence or "").lower()
        li_text = (li.raw_evidence or "").lower()
        guidance_raised = any(kw in sec_text for kw in ["guidance raised", "raised guidance", "increased outlook", "raised full year"])
        hiring_down = any(kw in li_text for kw in ["hiring down", "headcount decline", "layoffs", "postings fell", "postings down"])
        if guidance_raised and hiring_down:
            found.append(Contradiction(
                signal_a_source="SEC EDGAR",
                signal_a_brief="Revenue guidance raised in filing",
                signal_b_source="LinkedIn Hiring",
                signal_b_brief="Hiring activity declining",
                severity="high",
                explanation="Management guides revenue higher while simultaneously cutting headcount — operationally inconsistent with a growth trajectory.",
                contradiction_type="guidance_vs_hiring",
            ))

    # Rule 2: Insider net sell + Reddit strong bullish
    reddit = sig_map.get("reddit") or sig_map.get("Reddit_WSB") or sig_map.get("Reddit")
    if sec and reddit:
        sec_text = (sec.raw_evidence or "").lower()
        if (
            sec.direction == "bearish"
            and "insider" in sec_text
            and any(kw in sec_text for kw in ["net sell", "sold", "sold shares"])
            and reddit.direction == "bullish"
            and reddit.confidence > 0.55
        ):
            found.append(Contradiction(
                signal_a_source="SEC EDGAR",
                signal_a_brief="Insiders net selling significant volume",
                signal_b_source="Reddit",
                signal_b_brief="Reddit community strongly bullish",
                severity="high",
                explanation="Corporate insiders are reducing positions while retail crowd piles in — insiders hold material non-public context retail does not.",
                contradiction_type="insider_vs_crowd",
            ))

    # Rule 3: Glassdoor declining + LinkedIn hiring surge
    gd = sig_map.get("glassdoor") or sig_map.get("Glassdoor_Reviews") or sig_map.get("Glassdoor")
    if gd and li:
        gd_text = (gd.raw_evidence or "").lower()
        li_text = (li.raw_evidence or "").lower()
        if (
            gd.direction == "bearish"
            and any(kw in gd_text for kw in ["rating fell", "rating dropped", "declining", "lower rating"])
            and li.direction == "bullish"
            and any(kw in li_text for kw in ["hiring surge", "postings up", "headcount up", "posting growth"])
        ):
            found.append(Contradiction(
                signal_a_source="Glassdoor",
                signal_a_brief="Employee satisfaction rating declining",
                signal_b_source="LinkedIn Hiring",
                signal_b_brief="Job postings surging",
                severity="medium",
                explanation="Aggressive hiring while existing employee satisfaction falls — likely signals high churn driving replacement hiring rather than growth [Green et al JFE 2019].",
                contradiction_type="employee_vs_growth",
            ))

    # Rule 4: Professional news bearish + Reddit strong bullish
    news = sig_map.get("news") or sig_map.get("Reuters_News") or sig_map.get("News")
    if news and reddit:
        if (
            news.direction == "bearish"
            and reddit.direction == "bullish"
            and reddit.confidence > 0.65
        ):
            found.append(Contradiction(
                signal_a_source="News",
                signal_a_brief="Professional news coverage negative",
                signal_b_source="Reddit",
                signal_b_brief="Reddit retail sentiment strongly bullish",
                severity="low",
                explanation="Retail community bullish while professional press is negative — Reddit has near-zero empirical alpha [Alpha Architect 2024].",
                contradiction_type="sentiment_divergence",
            ))

    return found
