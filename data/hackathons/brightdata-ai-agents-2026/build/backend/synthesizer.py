"""
synthesizer.py — LLM synthesis layer for AltBrief.

Public API (imported by main.py / orchestrator):
    async def synthesize_brief(
        ticker: str,
        sources: dict[str, SourceResult],
    ) -> AsyncIterator[SSEEvent]:
        Yields: source_done, narrative_chunk (streaming), contradiction,
                brief (final), done events.

    async def warmup() -> None:
        Call at FastAPI startup to pre-compile the InvestmentBrief grammar
        on Anthropic's side. Saves 200-500ms on the first real request.

Architecture (per research/17_claude_toolUse_synthesizer.md §5):
    2-call design run concurrently with asyncio.gather:
    - Call A: streaming narrative text (no tool-use) → yields narrative_chunk SSE
    - Call B: non-streaming tool-use for structured InvestmentBrief → yields brief SSE

Caching layout (2 cache breakpoints):
    Block 1: system prompt text (synthesis_system.txt)             ─╮ cached together
    Block 2: NVDA few-shot user+assistant turn (nvda_few_shot.json) ─╯ (cache_control on Block 2)
    Block 3: per-ticker user message                               — NOT cached
    Block 4: tools array (INVESTMENT_BRIEF_TOOL)                  — cached separately on tool def

IMPORTANT: Extended thinking + tool_choice:{"type":"tool"} = 400 error.
Do NOT add betas=["interleaved-thinking-..."] to the tool-use call.
"""

from __future__ import annotations

import asyncio
import json
import logging
import time
from collections.abc import AsyncIterator
from datetime import datetime
from pathlib import Path
from typing import Any

import anthropic

from .contradictions import detect_contradictions, detect_contradictions_heuristic
from .cost_tracker import check_and_record, compute_cost
from .schemas import (
    Contradiction,
    InvestmentBrief,
    Signal,
    SourceResult,
    SourceStatus,
    SSEEvent,
)
from .synth_schema import INVESTMENT_BRIEF_TOOL

_stdlib_log = logging.getLogger(__name__)

# Use structlog if available; fall back to stdlib
try:
    import structlog
    log = structlog.get_logger(__name__)
except ImportError:
    log = None  # type: ignore[assignment]


def _log(level: str, event: str, **kwargs: Any) -> None:
    """Portable logging: structlog kwargs style or stdlib."""
    if log is not None:
        getattr(log, level)(event, **kwargs)
    else:
        msg = event + " " + " ".join(f"{k}={v}" for k, v in kwargs.items())
        getattr(_stdlib_log, level)(msg)

# ─────────────────────────── Constants ──────────────────────────────────────

MODEL = "claude-sonnet-4-6"
MAX_TOKENS_BRIEF = 4096      # InvestmentBrief output ~1200 tok; 4096 = safe headroom
MAX_TOKENS_NARRATIVE = 512   # brief_narrative is 150-250 words; 512 = sufficient

_PROMPTS_DIR = Path(__file__).parent / "prompts"
_SYSTEM_TEXT = (_PROMPTS_DIR / "synthesis_system.txt").read_text()
_NVDA_FEW_SHOT: list[dict] = json.loads((_PROMPTS_DIR / "nvda_few_shot.json").read_text())

# Tool choice that forces exactly one tool_use block per response.
# Per research 17 §2.4: type="tool" prefills the assistant turn so Claude
# cannot emit prose before the tool call. stop_reason will always be "tool_use".
_TOOL_CHOICE: dict = {"type": "tool", "name": "emit_investment_brief"}

# Source weight for ordering in the user prompt (highest-quality first)
_SOURCE_DISPLAY_ORDER = [
    "sec", "yahoo", "news", "glassdoor", "linkedin", "satellite", "gdelt", "reddit"
]


# ─────────────────────────── System Prompt ──────────────────────────────────

def _build_system_messages() -> list[dict[str, Any]]:
    """
    Returns the system[] array with 2 blocks:
    - Block 1: role + format spec (synthesis_system.txt) — no cache marker here
    - Block 2: NVDA few-shot user content — cache_control HERE

    WHY: cache breakpoint at end of Block 2 so BOTH blocks are cached together
    as a single prefix entry. Combined token count: ~1,100 tokens (system text
    ~500 tok + few-shot ~600 tok) which exceeds Sonnet 4.6's 1,024-token
    cache threshold.

    The NVDA assistant turn in the few-shot uses an actual tool_use block
    (not text JSON) to demonstrate the exact invocation pattern Claude must
    follow. This is required — text-based few-shots don't teach forced tool
    calls reliably.
    """
    # Extract the user content from the NVDA few-shot (first message = user)
    nvda_user_content = _NVDA_FEW_SHOT[0]["content"][0]["text"]

    return [
        {
            "type": "text",
            "text": _SYSTEM_TEXT,
            # No cache_control here — cache breakpoint is at end of Block 2
        },
        {
            "type": "text",
            "text": nvda_user_content,
            # Cache breakpoint 1 of 2 — everything above this is stable
            "cache_control": {"type": "ephemeral"},
        },
    ]


_SYSTEM_MESSAGES: list[dict[str, Any]] = _build_system_messages()


# ─────────────────────────── User Message Builder ───────────────────────────

def _sources_to_user_message(
    ticker: str,
    sources: dict[str, SourceResult],
    contradictions: list[Contradiction],
    confidence: float,
    data_quality_flag: str,
    start_time: float,
) -> dict[str, Any]:
    """
    Block 3 — per-ticker, per-request. Never cached.

    Structures source data so every source has an explicit signal field
    (required for reliable contradiction detection inside Claude).
    Injects pre-computed contradictions so the brief narrative reflects them.
    """
    sources_payload: dict[str, Any] = {}
    for src_name, result in sources.items():
        if result.status == SourceStatus.OK and result.data:
            sources_payload[src_name] = {
                "status": result.status.value,
                "latency_ms": result.latency_ms,
                "data": result.data,
            }
        else:
            sources_payload[src_name] = {
                "status": result.status.value,
                "error_msg": result.error_msg or "",
            }

    # Build contradiction context block (pre-computed by contradictions.py)
    contradiction_context = ""
    if contradictions:
        contradiction_lines = [
            f"  - [{c.severity.upper()}] {c.signal_a_source} vs {c.signal_b_source}: {c.explanation}"
            for c in contradictions
        ]
        contradiction_context = (
            "\n<pre_detected_contradictions>\n"
            + "\n".join(contradiction_lines)
            + "\n</pre_detected_contradictions>\n"
            + "INSTRUCTION: The contradictions above have already been verified by the "
            "analyst pipeline. Include them verbatim in cross_source_contradictions. "
            "You may add additional contradictions you identify, but do NOT omit these.\n"
        )

    metadata = {
        "latency_seconds": round(time.monotonic() - start_time, 2),
        "cost_usd": 0.0,  # synthesizer fills this after the call
        "confidence_score": confidence,
        "data_quality_flag": data_quality_flag,
    }

    payload = json.dumps(
        {"ticker": ticker, "metadata": metadata, **sources_payload},
        indent=2,
        default=str,
    )

    text = (
        f"Synthesize the following source data for {ticker} into an investment brief.\n"
        f"{contradiction_context}\n"
        f"<source_data>\n{payload}\n</source_data>"
    )

    return {
        "role": "user",
        "content": [{"type": "text", "text": text}],
        # No cache_control — variable content
    }


# ─────────────────────────── Few-Shot Messages ──────────────────────────────

def _nvda_few_shot_messages() -> list[dict[str, Any]]:
    """
    Returns the NVDA few-shot as a [user, assistant] message pair to prepend
    to the messages list.

    The assistant turn MUST be a tool_use content block — not a text block
    with JSON. This teaches Claude the exact format of a forced tool invocation.
    Using a text block here silently breaks the few-shot's teaching signal.
    """
    return _NVDA_FEW_SHOT  # already in [{role:user,...}, {role:assistant,...}] format


# ─────────────────────────── Narrative Streaming (Call A) ───────────────────

async def _stream_narrative(
    ticker: str,
    sources: dict[str, SourceResult],
    contradictions: list[Contradiction],
    async_client: anthropic.AsyncAnthropic,
) -> AsyncIterator[str]:
    """
    Call A — streaming plain-text narrative generation (no tool-use).

    WHY no tool-use here: tool_use with forced schema delivers structured output
    but streaming only yields partial JSON fragments (input_json_delta events)
    that cannot be validated mid-stream. The 2-call pattern uses this streaming
    call for UX (user sees text appearing) and Call B for structure.

    Uses a SHORTER, narrative-only system prompt to avoid paying for the full
    tool-schema overhead on this lightweight call.

    Yields string chunks as they arrive from the stream.
    """
    # Compact source summary for the narrative call (cheaper than full JSON dump)
    ok_sources = {k: v for k, v in sources.items() if v.status == SourceStatus.OK and v.data}
    summary_lines = []
    for src, result in ok_sources.items():
        data = result.data or {}
        direction = data.get("signal", data.get("direction", "unknown"))
        conf = data.get("confidence", "?")
        smy = data.get("summary", "")[:120]
        summary_lines.append(f"- {src}: {direction} (confidence={conf}) — {smy}")

    contradiction_lines = [
        f"  [{c.severity.upper()}] {c.signal_a_source} vs {c.signal_b_source}: {c.explanation}"
        for c in contradictions
    ]
    contradiction_block = "\n".join(contradiction_lines) if contradiction_lines else "  None detected."

    user_text = (
        f"Write a 150-250 word investment brief narrative for {ticker}.\n\n"
        f"Signals:\n{chr(10).join(summary_lines) or '  No data available.'}\n\n"
        f"Detected contradictions:\n{contradiction_block}\n\n"
        "Sell-side note style. Lead with overall direction. "
        "Include top contradictions if any. Cite peer-reviewed basis where relevant. "
        "Plain prose only — no JSON, no headers, no bullet points."
    )

    narrative_system = (
        "You are a senior equity research analyst. Write concise, accurate investment "
        "brief narratives. Sell-side note style. 150-250 words. Lead with direction. "
        "Cite academic basis for peer-reviewed signals (e.g. Cohen-Malloy-Pomorski JoF "
        "2012 for insider buys). If data is partial, say so honestly."
    )

    async with async_client.messages.stream(
        model=MODEL,
        max_tokens=MAX_TOKENS_NARRATIVE,
        system=narrative_system,
        messages=[{"role": "user", "content": user_text}],
    ) as stream:
        async for chunk in stream.text_stream:
            yield chunk


# ─────────────────────────── Structured Brief (Call B) ─────────────────────

async def _synthesize_structured(
    ticker: str,
    sources: dict[str, SourceResult],
    contradictions: list[Contradiction],
    confidence: float,
    data_quality_flag: str,
    start_time: float,
    async_client: anthropic.AsyncAnthropic,
) -> InvestmentBrief:
    """
    Call B — non-streaming, forced tool-use for structured InvestmentBrief.

    Uses tool_choice={"type":"tool","name":"emit_investment_brief"} so:
    - API prefills assistant turn — Claude cannot emit prose first
    - stop_reason is always "tool_use"
    - strict=True grammar-constrains sampling — output cannot be invalid JSON

    DO NOT add extended thinking (betas=[...]) here — incompatible with
    tool_choice:{"type":"tool"} → causes 400 error.

    Returns a validated InvestmentBrief with injected final confidence.
    """
    user_msg = _sources_to_user_message(
        ticker, sources, contradictions, confidence, data_quality_flag, start_time
    )

    # messages = few-shot pair + live user message
    messages = _nvda_few_shot_messages() + [user_msg]

    response = await async_client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS_BRIEF,
        system=_SYSTEM_MESSAGES,
        messages=messages,
        tools=[INVESTMENT_BRIEF_TOOL],  # cache_control on tool def (breakpoint 2 of 2)
        tool_choice=_TOOL_CHOICE,
    )

    # --- Assert stop reason ---
    if response.stop_reason != "tool_use":
        raise SynthesizerError(
            f"Unexpected stop_reason={response.stop_reason!r}. "
            f"Expected 'tool_use'. Full response: {response.model_dump_json()}"
        )

    # --- Extract tool_use block ---
    tool_block = next(
        (b for b in response.content if b.type == "tool_use"), None
    )
    if tool_block is None:
        raise SynthesizerError(
            f"No tool_use block in response. Content types: "
            f"{[b.type for b in response.content]}"
        )
    if tool_block.name != "emit_investment_brief":
        raise SynthesizerError(
            f"Wrong tool called: {tool_block.name!r}. Expected 'emit_investment_brief'."
        )

    # --- Validate with Pydantic ---
    raw_args: dict[str, Any] = tool_block.input
    try:
        brief = InvestmentBrief.model_validate(raw_args)
    except Exception as e:
        _log("warning", "pydantic_validation_failed",
             ticker=ticker, error=str(e), raw_keys=list(raw_args.keys()))
        brief = _coerce_and_validate(raw_args, ticker)

    # --- Inject pre-computed contradictions if Claude missed them ---
    if contradictions and not brief.contradictions:
        brief = brief.model_copy(update={"contradictions": contradictions})

    # Sync cross_source_contradictions string list from structured contradictions
    if brief.contradictions and not brief.cross_source_contradictions:
        brief = brief.sync_contradiction_strings()

    # --- Cost tracking ---
    usage = response.usage
    call_cost = compute_cost({
        "input_tokens": getattr(usage, "input_tokens", 0),
        "cache_read_input_tokens": getattr(usage, "cache_read_input_tokens", 0),
        "output_tokens": getattr(usage, "output_tokens", 0),
    })
    check_and_record(call_cost)

    # --- Observability ---
    _log("info", "synthesis_structured_done",
         ticker=ticker,
         input_tokens=getattr(usage, "input_tokens", 0),
         cache_read_tokens=getattr(usage, "cache_read_input_tokens", 0),
         cache_write_tokens=getattr(usage, "cache_creation_input_tokens", 0),
         output_tokens=getattr(usage, "output_tokens", 0),
         stop_reason=response.stop_reason,
         latency_ms=round((time.monotonic() - start_time) * 1000),
         overall_confidence=brief.overall_confidence,
         n_signals=len(brief.signals),
         n_contradictions=len(brief.contradictions),
         cost_usd=call_cost)

    # Patch cost_usd with actual cost
    return brief.model_copy(update={"cost_usd": call_cost})


# ─────────────────────────── Coercion Fallback ──────────────────────────────

def _coerce_and_validate(raw_args: dict[str, Any], ticker: str) -> InvestmentBrief:
    """
    Last-resort coercion when model_validate fails.
    Handles the two most common failure modes observed in production:
    1. generated_at as string that Pydantic can't parse due to Z suffix
    2. price_target_range as JSON string instead of dict
    3. signal items missing optional fields
    """
    # Normalize generated_at
    gat = raw_args.get("generated_at")
    if isinstance(gat, str):
        try:
            raw_args["generated_at"] = datetime.fromisoformat(gat.replace("Z", "+00:00"))
        except ValueError:
            raw_args["generated_at"] = datetime.utcnow()

    # Normalize price_target_range
    ptr = raw_args.get("price_target_range")
    if isinstance(ptr, str):
        try:
            raw_args["price_target_range"] = json.loads(ptr) if ptr.lower() != "null" else None
        except json.JSONDecodeError:
            raw_args["price_target_range"] = None

    # Add missing optional signal fields
    for sig in raw_args.get("signals", []):
        if isinstance(sig, dict):
            sig.setdefault("citation_url", None)
            sig.setdefault("research_anchor", None)
            sig.setdefault("alpha_tier", "standard")

    # Hard validate — if this fails, raise to caller
    return InvestmentBrief.model_validate(raw_args)


# ─────────────────────────── Confidence Rollup Helper ───────────────────────

def _compute_rollup(
    sources: dict[str, SourceResult],
    contradictions: list[Contradiction],
) -> tuple[float, str]:
    """
    Compute confidence + data_quality_flag BEFORE the synthesis call so we can
    inject them into the user message context.

    Imports confidence.py's rollup_confidence which implements the full formula
    from research/19_contradiction_confidence_algo.md §4.
    """
    from .confidence import rollup_confidence

    # Build minimal Signal objects from source data for the rollup formula
    signals: list[Signal] = []
    ok_sources = [
        (name, r) for name, r in sources.items()
        if r.status in (SourceStatus.OK, SourceStatus.CACHED) and r.data
    ]

    for name, result in ok_sources:
        data = result.data or {}
        direction = data.get("signal", data.get("direction", "neutral"))
        if direction not in ("bullish", "bearish", "neutral"):
            direction = "neutral"
        signals.append(Signal(
            source=name,
            direction=direction,
            summary=data.get("summary", ""),
            confidence=float(data.get("confidence", 0.5)),
            raw_evidence=str(data.get("evidence", data.get("raw_evidence", "")))[:500],
        ))

    return rollup_confidence(signals, contradictions)


# ─────────────────────────── Main Public API ────────────────────────────────

async def synthesize_brief(
    ticker: str,
    sources: dict[str, SourceResult],
) -> AsyncIterator[SSEEvent]:
    """
    Main synthesis entrypoint. Yields SSEEvent objects for SSE streaming.

    Event sequence:
    1. contradiction events (one per detected contradiction)
    2. narrative_chunk events (streaming text from Call A)
    3. brief event (structured InvestmentBrief from Call B)
    4. done event

    Call A (streaming narrative) and Call B (structured brief) run concurrently
    via asyncio.gather. Call B's tool-use result is typically available before
    or shortly after the narrative stream completes.

    Graceful degradation: if fewer than 3 sources OK, brief is still produced
    but data_quality_flag="minimal" and confidence is capped by coverage_cap.
    """
    start_time = time.monotonic()
    ticker = ticker.upper().strip()

    # Async client for concurrent calls
    async_client = anthropic.AsyncAnthropic()

    # --- Phase 0: Contradiction detection (runs BEFORE synthesis) ---
    ok_signals = _build_signals_list(sources)
    contradictions: list[Contradiction] = []
    if len(ok_signals) >= 2:
        try:
            # Run contradiction detection with sync client in executor to avoid
            # blocking the event loop (detect_contradictions is sync)
            loop = asyncio.get_event_loop()
            contradictions = await loop.run_in_executor(
                None,
                lambda: detect_contradictions(
                    ok_signals,
                    ticker,
                    client=anthropic.Anthropic(),
                )
            )
        except Exception as exc:
            _log("warning", "contradiction_detection_error", ticker=ticker, error=str(exc))
            contradictions = detect_contradictions_heuristic(ok_signals)

    # Yield contradiction events
    for c in contradictions:
        yield SSEEvent(
            event_type="contradiction",
            data={
                "signal_a_source": c.signal_a_source,
                "signal_b_source": c.signal_b_source,
                "severity": c.severity,
                "explanation": c.explanation,
                "contradiction_type": c.contradiction_type,
            },
        )

    # --- Phase 1: Compute confidence rollup ---
    confidence, data_quality_flag = _compute_rollup(sources, contradictions)

    # Graceful degradation flag
    n_ok = sum(
        1 for r in sources.values()
        if r.status in (SourceStatus.OK, SourceStatus.CACHED) and r.data
    )
    if n_ok < 3:
        data_quality_flag = "minimal"

    # --- Phase 2: Concurrent Call A + Call B ---
    narrative_chunks: list[str] = []
    brief_result: InvestmentBrief | None = None
    brief_error: Exception | None = None

    # Call B task (structured)
    brief_task = asyncio.create_task(
        _synthesize_structured(
            ticker, sources, contradictions, confidence, data_quality_flag,
            start_time, async_client
        )
    )

    # Call A (streaming narrative) — yield chunks as they arrive
    try:
        async for chunk in _stream_narrative(ticker, sources, contradictions, async_client):
            narrative_chunks.append(chunk)
            yield SSEEvent(event_type="narrative_chunk", data=chunk)
    except Exception as exc:
        _log("warning", "narrative_stream_error", ticker=ticker, error=str(exc))
        # Non-fatal — structured brief still coming from Call B

    # Await Call B
    try:
        brief_result = await brief_task
    except SynthesizerError as exc:
        _log("error", "synthesizer_structured_error", ticker=ticker, error=str(exc))
        brief_error = exc
    except Exception as exc:
        _log("error", "synthesizer_unexpected_error", ticker=ticker, error=str(exc))
        brief_error = exc

    # --- Phase 3: Emit final brief ---
    if brief_result is not None:
        # Patch narrative if Claude's was empty but we streamed one
        if not brief_result.brief_narrative and narrative_chunks:
            combined_narrative = "".join(narrative_chunks)
            brief_result = brief_result.model_copy(
                update={"brief_narrative": combined_narrative[:1200]}
            )

        # Final latency
        brief_result = brief_result.model_copy(
            update={"latency_seconds": round(time.monotonic() - start_time, 2)}
        )

        yield SSEEvent(
            event_type="brief",
            data=brief_result.model_dump(mode="json"),
        )
    else:
        # Emit error event with what we have
        yield SSEEvent(
            event_type="error",
            data={
                "error": str(brief_error),
                "ticker": ticker,
                "narrative": "".join(narrative_chunks),
            },
        )

    yield SSEEvent(event_type="done", data=None)


# ─────────────────────────── Warmup ─────────────────────────────────────────

async def warmup() -> None:
    """
    Pre-compile the InvestmentBrief JSON Schema grammar on Anthropic's side.

    Call this at FastAPI startup (before first real request). The first tool-use
    call with a new schema compiles the grammar and caches it for 24h —
    subsequent calls skip compilation (200-500ms latency saving).

    We send a max_tokens=1 request which will hit max_tokens stop reason, but
    the schema compilation happens on the API side regardless of output length.
    The APIStatusError from hitting max_tokens=1 is caught and swallowed.
    """
    _log("info", "synthesizer_warmup_start")
    try:
        async_client = anthropic.AsyncAnthropic()
        await async_client.messages.create(
            model=MODEL,
            max_tokens=1,
            messages=[{"role": "user", "content": "warmup"}],
            tools=[INVESTMENT_BRIEF_TOOL],
            tool_choice=_TOOL_CHOICE,
        )
    except anthropic.APIStatusError as exc:
        # Expected: max_tokens=1 will fail to produce valid tool output
        # Schema is still compiled and cached on Anthropic's side
        _log("info", "synthesizer_warmup_complete", note=f"Expected error: {exc.status_code}")
    except Exception as exc:
        # Non-fatal: warmup is best-effort
        _log("warning", "synthesizer_warmup_failed", error=str(exc))


# ─────────────────────────── Helpers ────────────────────────────────────────

def _build_signals_list(sources: dict[str, SourceResult]) -> list[Signal]:
    """Build Signal objects from source results for contradiction detection."""
    signals = []
    for name, result in sources.items():
        if result.status not in (SourceStatus.OK, SourceStatus.CACHED) or not result.data:
            continue
        data = result.data or {}
        direction = data.get("signal", data.get("direction", "neutral"))
        if direction not in ("bullish", "bearish", "neutral"):
            direction = "neutral"
        signals.append(Signal(
            source=name,
            direction=direction,
            summary=str(data.get("summary", ""))[:240],
            confidence=float(data.get("confidence", 0.5)),
            raw_evidence=str(data.get("evidence", data.get("raw_evidence", "")))[:500],
            citation_url=data.get("url"),
        ))
    return signals


# ─────────────────────────── Errors ─────────────────────────────────────────

class SynthesizerError(Exception):
    """Raised when the Anthropic API or Pydantic validation fails in a non-recoverable way."""
    pass
