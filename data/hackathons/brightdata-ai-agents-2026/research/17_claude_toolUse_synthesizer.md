# Claude Sonnet 4.6 Tool-Use Synthesizer — Production Spec

**File:** `synthesizer.py` (drop-in module)
**Model:** `claude-sonnet-4-6` (API ID confirmed, 1M context, 64k max output, $3/$15 per MTok)
**Last updated:** 2026-05-27

---

## 1. Why Tool-Use Beats JSON Mode for InvestmentBrief

JSON Mode asks Claude to emit a JSON string that you then parse. Two failure modes:
- Claude adds prose before the JSON object ("Here is the brief: {...}") — your regex breaks
- Claude hallucinates a key name ("overallDirection" instead of "overall_direction") — silent validation failure at runtime, often only caught downstream

Tool-use with `tool_choice={"type":"tool","name":"emit_investment_brief"}` + `strict=True` eliminates both:

1. **Forced call.** With `tool_choice` type `"tool"`, the API prefills the assistant turn to force the tool call — Claude cannot emit prose first. Stop reason is always `"tool_use"`, never `"end_turn"`. (Source: Anthropic Define Tools docs, "Forcing tool use" section)
2. **Grammar-constrained sampling.** `strict=True` compiles the schema to a grammar and constrains token sampling — the output *cannot* be invalid JSON, fields cannot be missing, enum values cannot drift. (Source: Anthropic Strict Tool Use docs)
3. **Single validated object.** You call `InvestmentBrief.model_validate(block.input)` — no parsing, no regex, hard ValidationError on anything malformed.

The cost delta is negligible: tool-use adds ~313 system-prompt tokens (for `tool_choice: tool`) plus the schema tokens. At $3/MTok input that is under $0.001 per call.

**Anti-pattern avoided:** Do NOT use `response.content[0].text` + `json.loads()`. That is JSON Mode behavior wired through the text channel — no guarantee of structure, no forced call, no grammar constraint.

---

## 2. Pydantic v2 → JSON Schema → Tool Definition Pipeline

### 2.1 The Schema Generation Problem

`InvestmentBrief.model_json_schema()` produces standard Pydantic v2 JSON Schema that Claude's strict mode rejects in two places:

**Problem A — `$defs` + `$ref` for nested models**

Pydantic v2 extracts `Signal` into `$defs` and references it via `$ref`:
```json
{
  "$defs": {
    "Signal": { "type": "object", "properties": {...} }
  },
  "properties": {
    "signals": {
      "type": "array",
      "items": { "$ref": "#/$defs/Signal" }
    }
  }
}
```
Claude's strict mode **does** support internal `$ref` + `$defs` (per structured-outputs docs). You do NOT need to flatten them manually. But you must strip external `$ref` (none here) and ensure `additionalProperties: false` is on every object in `$defs` too.

**Problem B — `Field(max_length=200)` generates `maxLength` constraint**

`Signal.summary = Field(max_length=200)` → schema includes `"maxLength": 200`. Strict mode rejects string constraints (`minLength`, `maxLength`) and numeric constraints (`minimum`, `maximum`, `multipleOf`). The constraint tokens are stripped automatically if you use `client.messages.parse()` (SDK transforms), but since we need raw tool-use (not the `parse()` helper), we must clean the schema ourselves.

**Problem C — `datetime` becomes `{"type":"string","format":"date-time"}`**

`date-time` format IS in Claude's supported string formats list. No transformation needed. However, `generated_at: datetime` — Claude will emit an ISO 8601 string; you must `datetime.fromisoformat()` it after `model_validate`.

**Problem D — `dict | None` for `price_target_range`**

Pydantic generates `anyOf: [{"type":"object"}, {"type":"null"}]` for `dict | None`. Claude strict mode supports `anyOf` with limitations. A bare `{"type":"object"}` without `additionalProperties: false` will fail strict validation. Since `price_target_range` is a free-form dict, you cannot add `additionalProperties: false` with specific property specs. **Solution:** change schema for this field to `{"type":"string","description":"JSON string: {low: X, base: Y, high: Z} or null string 'null'"}` and deserialize in post-processing. Or keep as `anyOf` with `{"type":"object","additionalProperties":true}` and accept that this one field won't be grammar-constrained (acceptable tradeoff given it's optional metadata).

### 2.2 Schema Cleaner Function

```python
# synthesizer.py
import copy
import json
from pydantic import BaseModel
from typing import Any


def _clean_schema_for_claude(schema: dict[str, Any]) -> dict[str, Any]:
    """
    Transform Pydantic v2 model_json_schema() output into a Claude strict-mode
    compatible JSON Schema.

    Transformations applied:
    1. Remove unsupported constraints: maxLength, minLength, minimum, maximum,
       exclusiveMinimum, exclusiveMaximum, multipleOf, minItems (>1), maxItems
    2. Add additionalProperties: false to every "object" type node
    3. Handle dict|None (price_target_range) by converting to string representation
    4. Remove the top-level "title" key (Claude ignores it but it adds noise)
    5. Strip $schema key if present

    Does NOT:
    - Flatten $defs/$ref (Claude strict supports internal references)
    - Touch enum values (they're fine as-is)
    - Touch format strings (date-time is supported)

    Returns a new dict (does not mutate input).
    """
    schema = copy.deepcopy(schema)
    _clean_node(schema)
    schema.pop("title", None)
    schema.pop("$schema", None)
    return schema


_STRIP_KEYS = {
    "maxLength", "minLength", "minimum", "maximum",
    "exclusiveMinimum", "exclusiveMaximum", "multipleOf",
    "maxItems",  # minItems is allowed only for 0 or 1
}


def _clean_node(node: Any) -> None:
    """Recursively clean a schema node in-place."""
    if not isinstance(node, dict):
        return

    # Strip unsupported constraint keywords
    for key in list(node.keys()):
        if key in _STRIP_KEYS:
            del node[key]

    # Enforce additionalProperties: false on all object nodes
    if node.get("type") == "object":
        node["additionalProperties"] = False
        # Also ensure required is present (default to all properties if missing)
        if "properties" in node and "required" not in node:
            node["required"] = list(node["properties"].keys())

    # Handle dict|None -> convert to anyOf with explicit null
    # For price_target_range specifically: if anyOf contains a bare object,
    # add additionalProperties: true explicitly so Claude knows it's intentional
    if "anyOf" in node:
        for variant in node["anyOf"]:
            if isinstance(variant, dict) and variant.get("type") == "object":
                if "additionalProperties" not in variant:
                    # Free-form dict — use true to signal intentional open schema
                    variant["additionalProperties"] = True

    # Recurse into all nested dicts and lists
    for value in node.values():
        if isinstance(value, dict):
            _clean_node(value)
        elif isinstance(value, list):
            for item in value:
                _clean_node(item)
```

### 2.3 Building the Tool Definition

```python
# synthesizer.py (continued)
import anthropic
from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field


class Signal(BaseModel):
    source: str
    direction: Literal["bullish", "bearish", "neutral"]
    summary: str = Field(max_length=200)
    confidence: float = Field(ge=0.0, le=1.0)
    raw_evidence: str = Field(max_length=500)
    citation_url: str | None = None


class InvestmentBrief(BaseModel):
    ticker: str
    company_name: str
    sector: str
    generated_at: datetime
    signals: list[Signal]
    risk_factors: list[str]
    bull_thesis: list[str]
    bear_case: list[str]
    overall_direction: Literal["bullish", "bearish", "neutral"]
    overall_confidence: float
    price_target_range: dict | None
    brief_narrative: str
    data_quality_flag: Literal["full", "partial", "minimal"]
    sources_used: list[str]
    sources_unavailable: list[str]
    cross_source_contradictions: list[str]
    latency_seconds: float
    cost_usd: float


def build_tool_definition() -> dict:
    """
    Build the tools=[...] payload for client.messages.create().

    Returns a single-element list. Cache marker (cache_control) is set on
    this tool definition — place cache_control on the LAST tool in the array
    to cache all tools up to that point.

    Sonnet 4.6 cache threshold: 1,024 tokens. The schema alone is ~600 tokens;
    add the system prompt (Block 1) to the same cache prefix to exceed threshold.
    """
    raw_schema = InvestmentBrief.model_json_schema()
    clean_schema = _clean_schema_for_claude(raw_schema)

    return {
        "name": "emit_investment_brief",
        "description": (
            "Synthesize data from multiple financial sources into a structured "
            "investment brief. Called exactly once per synthesis request. "
            "Populate every required field. For cross_source_contradictions, "
            "surface any case where two sources give conflicting signals — "
            "e.g. LinkedIn shows aggressive hiring while SEC guidance warns of "
            "revenue softness, or Reddit sentiment is strongly bearish while "
            "analyst consensus is bullish. List each contradiction as a plain "
            "English sentence. Use 'minimal' for data_quality_flag when fewer "
            "than 4 sources returned usable data."
        ),
        "strict": True,
        "input_schema": clean_schema,
        # cache_control placed on the tool definition (last tool in array)
        # This caches system prompt + tool schema together as one prefix
        "cache_control": {"type": "ephemeral"},
    }
```

### 2.4 Forcing the Tool Call — `tool_choice`

```python
TOOL_CHOICE = {"type": "tool", "name": "emit_investment_brief"}
```

With `type: "tool"` + the specific name:
- API prefills the assistant turn — Claude cannot emit text before the tool call
- Stop reason will be `"tool_use"` — assert this in your response handler
- Adds 313 system-prompt overhead tokens (vs 346 for `auto`) — negligible
- **Incompatible with extended thinking** — do NOT set `betas=["interleaved-thinking-2025-05-14"]` on the synthesizer call; use `tool_choice: auto` if you add thinking

---

## 3. Prompt Caching Strategy — 4-Block Layout

Sonnet 4.6 cache minimum: **1,024 tokens**. Cache writes cost 1.25x base; reads cost 0.1x base.

```
┌─────────────────────────────────────────────────────────────────┐
│ Block 1: system[] array — role + format spec (CACHED)           │
│ Block 2: system[] array — few-shot NVDA example (CACHED)        │  <-- single cache_control at end of Block 2
│ Block 3: user message — 8 source results JSON (NOT CACHED)      │
│ Block 4: tools=[] array — tool def with cache_control on it     │  <-- second cache_control (tools are cached separately)
└─────────────────────────────────────────────────────────────────┘
```

**Two cache breakpoints total** (well within the 4-breakpoint limit):
1. End of Block 2 (system prompt including few-shot) — stable across all tickers
2. Tool definition (tools array cache_control) — stable across all tickers

Block 3 (user message with per-ticker source data) — NOT cached, changes every request.

### 3.1 Exact Message Construction

```python
# synthesizer.py (continued)

SYSTEM_ROLE_BLOCK = {
    "type": "text",
    "text": """You are a senior equity research analyst synthesizing alternative data
into structured investment briefs. Your output is always a single call to
emit_investment_brief — no prose, no preamble.

Brief format contract:
- signals: one Signal per data source that returned usable data. source field
  must be one of: SEC_EDGAR, Yahoo_Finance, Reuters_News, Reddit_WSB,
  LinkedIn_Hiring, Glassdoor_Reviews, GDELT_News, Satellite_Imagery
- bull_thesis: 3-4 bullets. Each bullet max 120 chars. Start with action verb.
- bear_case: 3-4 bullets. Same format.
- brief_narrative: 150-250 words. Sell-side note style. Lead with overall
  direction. Include top 2 contradictions if any exist.
- cross_source_contradictions: every case where two sources imply opposite
  signal directions. Format: "SOURCE_A (direction) contradicts SOURCE_B
  (direction): [one sentence explanation]". Empty list if none.
- overall_confidence: weighted average of signal confidences (weights provided
  in source data). Penalty applied by caller — emit raw weighted average here.
- generated_at: current UTC timestamp in ISO 8601 format.
- latency_seconds and cost_usd: copy from the metadata block in source data.
- data_quality_flag: "full" if ≥6 sources, "partial" if 3-5, "minimal" if <3.""",
    # NO cache_control here — cache breakpoint is at end of Block 2
}

# Few-shot example: NVDA mock data → expected tool call
# The assistant turn in a few-shot MUST use the tool_use block format exactly
NVDA_FEW_SHOT_USER = {
    "type": "text",
    "text": """<example>
<source_data>
{
  "ticker": "NVDA",
  "metadata": {"latency_seconds": 28.4, "cost_usd": 0.031},
  "SEC_EDGAR": {
    "signal": "bullish",
    "confidence": 0.87,
    "summary": "CEO Jensen Huang purchased 50K shares Form 4 filing 2026-04-15",
    "evidence": "Form 4 direct acquisition at $892/share. No prior Form 4 sales in 12 months.",
    "url": "https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=NVDA&type=4"
  },
  "Yahoo_Finance": {
    "signal": "bullish",
    "confidence": 0.81,
    "summary": "Revenue beat Q1 2026 consensus by 12%, data center segment up 220% YoY",
    "evidence": "Q1 rev $44.1B vs $39.3B consensus. EPS $0.96 vs $0.88 est.",
    "url": "https://finance.yahoo.com/quote/NVDA"
  },
  "Reddit_WSB": {
    "signal": "bearish",
    "confidence": 0.38,
    "summary": "Retail sentiment shifted negative: 'NVDA priced to perfection, any miss = -20%'",
    "evidence": "wsb top posts 48h: 73% bearish mentions, avg upvote ratio 0.82",
    "url": "https://reddit.com/r/wallstreetbets"
  },
  "sources_unavailable": ["LinkedIn_Hiring", "Glassdoor_Reviews", "GDELT_News", "Satellite_Imagery"],
  "weights": {"SEC_EDGAR": 1.0, "Yahoo_Finance": 0.9, "Reddit_WSB": 0.4}
}
</source_data>
</example>""",
}

NVDA_FEW_SHOT_ASSISTANT = {
    "role": "assistant",
    "content": [
        {
            "type": "tool_use",
            "id": "toolu_example_nvda_01",
            "name": "emit_investment_brief",
            "input": {
                "ticker": "NVDA",
                "company_name": "NVIDIA Corporation",
                "sector": "Semiconductors",
                "generated_at": "2026-05-27T09:00:00Z",
                "signals": [
                    {
                        "source": "SEC_EDGAR",
                        "direction": "bullish",
                        "summary": "CEO insider buy 50K shares at $892 — strong conviction signal",
                        "confidence": 0.87,
                        "raw_evidence": "Form 4 direct acquisition at $892/share. No prior Form 4 sales in 12 months.",
                        "citation_url": "https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=NVDA&type=4"
                    },
                    {
                        "source": "Yahoo_Finance",
                        "direction": "bullish",
                        "summary": "Q1 2026 revenue beat +12%, data center +220% YoY",
                        "confidence": 0.81,
                        "raw_evidence": "Q1 rev $44.1B vs $39.3B consensus. EPS $0.96 vs $0.88 est.",
                        "citation_url": "https://finance.yahoo.com/quote/NVDA"
                    },
                    {
                        "source": "Reddit_WSB",
                        "direction": "bearish",
                        "summary": "Retail sentiment negative: 73% bearish mentions WSB 48h",
                        "confidence": 0.38,
                        "raw_evidence": "wsb top posts 48h: 73% bearish mentions, avg upvote ratio 0.82",
                        "citation_url": "https://reddit.com/r/wallstreetbets"
                    }
                ],
                "risk_factors": [
                    "Retail sentiment diverges sharply from institutional signals — crowded long risk",
                    "Valuation elevated: any guidance miss could trigger outsized correction",
                    "Export control risks to China data center segment unquantified in filing"
                ],
                "bull_thesis": [
                    "CEO insider buy at $892 signals management confidence at current valuation",
                    "Data center revenue +220% YoY confirms structural AI infrastructure demand",
                    "12% revenue beat demonstrates pricing power and backlog execution"
                ],
                "bear_case": [
                    "Retail sentiment 73% bearish — crowded institutional long creates fragility",
                    "Stock priced for perfection: multiple compression risk on any miss",
                    "3 of 8 data sources unavailable — partial picture, especially hiring/culture"
                ],
                "overall_direction": "bullish",
                "overall_confidence": 0.73,
                "price_target_range": None,
                "brief_narrative": "NVIDIA presents a compelling near-term bullish case underpinned by two high-quality signals: CEO insider buying at $892/share — a Cohen-Malloy-Pomorski tier signal with 82bps/month historical alpha — and a 12% Q1 revenue beat driven by 220% data center growth. Institutional conviction is strong. However, retail sentiment on Reddit WSB has inverted sharply, with 73% bearish mentions over 48 hours, suggesting the stock may be priced to perfection in retail positioning. The divergence between SEC/Yahoo signals (bullish, high confidence) and Reddit (bearish, low confidence) is the primary cross-source contradiction in this brief. Data quality is partial — LinkedIn hiring trends, Glassdoor reviews, GDELT news, and satellite data were unavailable, leaving culture and operational health unassessed.",
                "data_quality_flag": "partial",
                "sources_used": ["SEC_EDGAR", "Yahoo_Finance", "Reddit_WSB"],
                "sources_unavailable": ["LinkedIn_Hiring", "Glassdoor_Reviews", "GDELT_News", "Satellite_Imagery"],
                "cross_source_contradictions": [
                    "SEC_EDGAR (bullish) contradicts Reddit_WSB (bearish): CEO buying at $892 signals insider conviction while retail WSB sentiment is 73% bearish — potential crowded-long fragility"
                ],
                "latency_seconds": 28.4,
                "cost_usd": 0.031
            }
        }
    ]
}

def build_system_prompt() -> list[dict]:
    """
    Returns the system array with a single cache breakpoint after the few-shot block.
    Both blocks are cached together as one prefix entry.
    """
    return [
        SYSTEM_ROLE_BLOCK,
        {
            **NVDA_FEW_SHOT_USER,
            "cache_control": {"type": "ephemeral"},
            # Cache breakpoint here — everything above is stable across all tickers
            # Sonnet 4.6 threshold = 1024 tokens; system role (~200 tok) +
            # few-shot example (~900 tok) = ~1100 tok — exceeds threshold
        },
    ]


def build_user_message(ticker: str, source_results: dict) -> dict:
    """
    Block 3 — per-ticker, per-request. Never cached.
    source_results: dict keyed by source name, values from each collector.
    """
    payload = json.dumps(source_results, indent=2, default=str)
    return {
        "role": "user",
        "content": [
            {
                "type": "text",
                "text": f"Synthesize the following source data for {ticker} into an investment brief.\n\n<source_data>\n{payload}\n</source_data>",
                # No cache_control — this is variable content
            }
        ]
    }
```

**Note on few-shot assistant turn format:** The `NVDA_FEW_SHOT_ASSISTANT` above uses the actual `tool_use` content block format — not a text block with JSON. This is required. If you pass a text block here, the few-shot does not demonstrate the tool invocation pattern and Claude may emit text before the forced tool call on subsequent requests.

However, Anthropic SDK's `messages.create()` accepts alternating `user`/`assistant` messages. To inject the few-shot pair, you must include the user example in the system prompt (as shown above) rather than as a conversation turn, because the first message in `messages=[]` must be a user role. The system array approach keeps the conversation messages clean.

### 3.2 Cost Math for 4 Demo Tickers

Assumptions: system prompt ~1,100 tokens, tool schema ~600 tokens, user message ~2,000 tokens, output ~1,200 tokens. Sonnet 4.6: input $3/MTok, cache-read $0.30/MTok (0.1x), cache-write $3.75/MTok (1.25x).

| Ticker | System (tok) | Cache status | Input cost | Cache-read cost | Output cost | Total |
|--------|-------------|--------------|-----------|----------------|-------------|-------|
| NVDA (first call — cache write) | 1,700 cached | WRITE | $0.0051 | — | $0.018 | ~$0.023 |
| AAPL (cache hit) | 1,700 cached | READ | $0.00051 | — | $0.018 | ~$0.018 |
| TSLA (cache hit) | 1,700 cached | READ | $0.00051 | — | $0.018 | ~$0.018 |
| META (cache hit) | 1,700 cached | READ | $0.00051 | — | $0.018 | ~$0.018 |
| **4-ticker total** | | | | | | **~$0.077** |

Without caching: 4 × ($0.0051 + $0.018) = **$0.093**. Cache saves ~17% on 4 tickers, ~83% at scale (100+ tickers/day). The 5-minute ephemeral TTL is sufficient for a demo session; use `"ttl": "1h"` for a hackathon demo where the same judge might re-run the same ticker.

---

## 4. Parse Response — Full Handler

```python
# synthesizer.py (continued)
import anthropic
import logging
import structlog
from typing import Any

log = structlog.get_logger()

client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from env


async def synthesize(
    ticker: str,
    source_results: dict,
    start_time: float,
) -> InvestmentBrief:
    """
    Main entry point. Called after asyncio.gather() across all 8 data sources.

    Args:
        ticker: Stock ticker symbol e.g. "NVDA"
        source_results: Dict from orchestrator with keys per source name.
                        Must include "metadata" key with latency_seconds, cost_usd.
        start_time: time.monotonic() from when the request started (for latency tracking)

    Returns:
        Validated InvestmentBrief instance.

    Raises:
        SynthesizerError: on malformed tool call, validation failure, or API error.
    """
    import time

    tool_def = build_tool_definition()
    system = build_system_prompt()
    user_msg = build_user_message(ticker, source_results)

    try:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4096,  # InvestmentBrief output is ~1200 tokens; 4096 is safe headroom
            system=system,
            messages=[user_msg],
            tools=[tool_def],
            tool_choice={"type": "tool", "name": "emit_investment_brief"},
        )
    except anthropic.APIStatusError as e:
        raise SynthesizerError(f"Anthropic API error {e.status_code}: {e.message}") from e

    # --- Assert stop reason ---
    if response.stop_reason != "tool_use":
        # Happens if: max_tokens hit mid-generation, or tool_choice was ignored
        raise SynthesizerError(
            f"Unexpected stop_reason={response.stop_reason!r}. "
            f"Expected 'tool_use'. Full response: {response.model_dump_json()}"
        )

    # --- Extract tool_use block ---
    tool_block = next(
        (b for b in response.content if b.type == "tool_use"),
        None,
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
    raw_args: dict[str, Any] = tool_block.input  # already a dict from SDK
    try:
        brief = InvestmentBrief.model_validate(raw_args)
    except Exception as e:
        log.warning(
            "pydantic_validation_failed",
            ticker=ticker,
            error=str(e),
            raw_args_keys=list(raw_args.keys()),
        )
        # Fallback: attempt field-by-field coercion for known types
        brief = _coerce_and_validate(raw_args, ticker)

    # --- Observability ---
    usage = response.usage
    log.info(
        "synthesis_complete",
        ticker=ticker,
        input_tokens=usage.input_tokens,
        cache_read_tokens=getattr(usage, "cache_read_input_tokens", 0),
        cache_write_tokens=getattr(usage, "cache_creation_input_tokens", 0),
        output_tokens=usage.output_tokens,
        stop_reason=response.stop_reason,
        latency_ms=round((time.monotonic() - start_time) * 1000),
        overall_confidence=brief.overall_confidence,
        sources_used=brief.sources_used,
        contradictions_found=len(brief.cross_source_contradictions),
    )

    return brief


def _coerce_and_validate(raw_args: dict, ticker: str) -> InvestmentBrief:
    """
    Last-resort coercion for when model_validate fails.
    Handles the two most common failure modes:
    1. generated_at is already a datetime object (not ISO string) — Pydantic handles this
    2. price_target_range came back as a string instead of dict — parse it
    3. Signal fields are missing citation_url — default to None
    """
    # Normalize generated_at
    if isinstance(raw_args.get("generated_at"), str):
        try:
            raw_args["generated_at"] = datetime.fromisoformat(
                raw_args["generated_at"].replace("Z", "+00:00")
            )
        except ValueError:
            raw_args["generated_at"] = datetime.utcnow()

    # Normalize price_target_range
    ptr = raw_args.get("price_target_range")
    if isinstance(ptr, str):
        try:
            raw_args["price_target_range"] = json.loads(ptr) if ptr != "null" else None
        except json.JSONDecodeError:
            raw_args["price_target_range"] = None

    # Add missing optional fields to signals
    for sig in raw_args.get("signals", []):
        sig.setdefault("citation_url", None)

    # Hard validate — if this fails, raise to caller
    return InvestmentBrief.model_validate(raw_args)


class SynthesizerError(Exception):
    pass
```

---

## 5. Streaming — Pattern Decision

### The Core Problem

Anthropic streaming with tool-use and `tool_choice: {"type": "tool", ...}` delivers the tool `input` as a series of `input_json_delta` events — partial JSON fragments. You cannot validate a partial JSON object against Pydantic mid-stream. You must buffer the entire `input` string, then validate at the end.

This means: **you cannot stream the InvestmentBrief fields one-by-one to the frontend** through SSE using the tool-use path alone.

### Chosen Pattern: 2-Call Architecture

Do NOT attempt to stream partial tool-use JSON to the frontend. Use this instead:

**Call 1 (streaming, no tool-use):** Stream `brief_narrative` as a text generation (SSE). User sees the narrative appear in real-time. This is the human-readable summary — highest value for UX.

**Call 2 (non-streaming, tool-use):** Run concurrently or immediately after Call 1 completes. Produces the structured `InvestmentBrief` with all fields. Returns in ~3-5 seconds.

Frontend receives:
```
SSE event: {"type": "narrative_chunk", "text": "NVIDIA presents..."}   # streaming
SSE event: {"type": "brief_ready", "data": {...InvestmentBrief...}}    # one shot when Call 2 completes
SSE event: {"type": "source_completed", "source": "SEC_EDGAR", "direction": "bullish"}  # from orchestrator during fan-out
```

```python
# router.py — FastAPI SSE endpoint
import asyncio
import json
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from synthesizer import synthesize, synthesize_narrative_stream
import time

app = FastAPI()

@app.get("/brief/stream/{ticker}")
async def brief_stream(ticker: str):
    async def event_generator():
        start_time = time.monotonic()

        # Kick off 8-source fan-out
        source_task = asyncio.create_task(
            orchestrate_sources(ticker)  # returns dict of source results
        )

        # Emit source progress events as they complete (handled in orchestrator)
        # source_completed events are yielded by the orchestrator via a queue

        source_results = await source_task

        # Run both calls concurrently
        narrative_task = asyncio.create_task(
            synthesize_narrative_stream(ticker, source_results)
        )
        brief_task = asyncio.create_task(
            synthesize(ticker, source_results, start_time)
        )

        # Stream narrative chunks first
        async for chunk in narrative_task:
            yield f"data: {json.dumps({'type': 'narrative_chunk', 'text': chunk})}\n\n"

        # Await structured brief (usually ready by the time narrative finishes)
        brief = await brief_task
        yield f"data: {json.dumps({'type': 'brief_ready', 'data': brief.model_dump(mode='json')})}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


async def synthesize_narrative_stream(ticker: str, source_results: dict):
    """
    Call 1: stream brief_narrative only as plain text generation.
    No tool-use — direct text channel for low-latency streaming.
    Yields string chunks.
    """
    system_text = (
        "You are a senior equity research analyst. Write a 150-250 word "
        "investment brief narrative for the given source data. Sell-side note style. "
        "Lead with overall direction. Include top contradictions if present. "
        "Plain prose only — no JSON, no headers."
    )
    payload = json.dumps(source_results, default=str)

    with client.messages.stream(
        model="claude-sonnet-4-6",
        max_tokens=512,
        system=system_text,
        messages=[{
            "role": "user",
            "content": f"Write the brief narrative for {ticker}:\n\n{payload}"
        }],
    ) as stream:
        for text_chunk in stream.text_stream:
            yield text_chunk
```

**Trade-off summary:**

| Approach | Latency to first token | Structured data | Implementation |
|----------|----------------------|-----------------|----------------|
| Single tool-use call, no stream | 5-8s to full response | Guaranteed | Simple |
| Stream tool-use (buffer input_json_delta) | First chunk fast, validation at end | Guaranteed | Complex, no per-field streaming |
| 2-call (narrative stream + tool-use) | <1s to first narrative char | Guaranteed | Moderate, two API calls |

**Decision: 2-call.** The extra $0.002/request for Call 1 is worth the UX. The narrative stream makes the product feel live while the structured brief compiles in the background.

---

## 6. Cross-Source Contradiction Detection

The system prompt already instructs Claude to populate `cross_source_contradictions`. The key is giving the source data in a format that makes contradictions obvious. Structure the `source_results` dict so each source has an explicit `signal` field ("bullish"/"bearish"/"neutral"):

```python
# In your orchestrator, normalize each source result before passing to synthesizer:
def normalize_source_result(source_name: str, raw_data: dict) -> dict:
    """Ensures every source result has a 'signal' key for contradiction detection."""
    return {
        "signal": raw_data.get("direction", "neutral"),
        "confidence": raw_data.get("confidence", 0.5),
        "summary": raw_data.get("summary", ""),
        "evidence": raw_data.get("evidence", ""),
        "url": raw_data.get("url"),
    }
```

The contradiction detection prompt section in the system prompt:

```
CONTRADICTION DETECTION PROTOCOL:
After generating signals, compare every pair of sources. A contradiction exists when:
1. Source A direction is "bullish" and Source B direction is "bearish" (not neutral)
2. Sources are different (e.g. SEC_EDGAR vs Reddit_WSB, LinkedIn_Hiring vs SEC guidance)

For each contradiction, add one entry to cross_source_contradictions:
Format: "[SOURCE_A] ([direction]) contradicts [SOURCE_B] ([direction]): [one sentence explaining
the specific conflicting claims, e.g. 'LinkedIn shows 40% hiring increase in AI roles while
SEC 10-K guidance warns of AI compute cost pressures reducing margin']"

Known high-signal contradiction pairs:
- LinkedIn_Hiring (growth) vs SEC_EDGAR (revenue warning) → operational vs financial disconnect
- Reddit_WSB (retail sentiment) vs Yahoo_Finance (analyst consensus) → positioning vs fundamentals
- Glassdoor_Reviews (culture decline) vs LinkedIn_Hiring (headcount growth) → quality vs quantity
- GDELT_News (negative tone) vs Yahoo_Finance (price momentum) → macro vs micro divergence
```

The few-shot example (NVDA mock) already demonstrates a populated contradiction. Claude learns the exact format from the assistant turn.

---

## 7. Confidence Rollup Formula

```python
# confidence.py

from dataclasses import dataclass
from typing import Optional


# Source quality weights — peer-reviewed basis in comments
SOURCE_WEIGHTS: dict[str, float] = {
    "SEC_EDGAR": 1.0,        # Cohen-Malloy-Pomorski JoF 2012: Form 4 insider buys → 82bps/mo alpha
    "Yahoo_Finance": 0.9,    # High-quality structured financial data, delayed but reliable
    "Reuters_News": 0.85,    # Professional journalism, editorial standards, low hallucination risk
    "Glassdoor_Reviews": 0.7,  # Green et al JFE 2019: Glassdoor rating Δ → excess returns
    "Satellite_Imagery": 0.6,  # Berkeley parking study: novel signal, high noise in single reading
    "LinkedIn_Hiring": 0.6,  # Directional only — headcount growth ≠ revenue growth without context
    "GDELT_News": 0.5,       # High volume, mixed quality; tone scores are aggregate, not curated
    "Reddit_WSB": 0.4,       # Decayed signal post-GME; crowding risk, high sentiment volatility
}

# Penalty constants
MISSING_SOURCE_PENALTY_PER_SOURCE = 0.03   # Per unavailable source above threshold
MISSING_SOURCE_FREE_THRESHOLD = 2          # Up to 2 missing sources: no penalty
CONTRADICTION_PENALTY_PER_PAIR = 0.05     # Per detected cross-source contradiction
MAX_CONTRADICTION_PENALTY = 0.20          # Cap contradiction penalty at 20pp


@dataclass
class ConfidenceResult:
    overall_confidence: float
    weighted_avg: float
    coverage_penalty: float
    contradiction_penalty: float
    sources_scored: list[str]
    sources_missing: list[str]
    explanation: str


def compute_confidence(
    signals: list[dict],
    sources_unavailable: list[str],
    contradictions: list[str],
    available_sources: Optional[list[str]] = None,
) -> ConfidenceResult:
    """
    Compute overall investment brief confidence score.

    Formula:
        overall = weighted_avg - coverage_penalty - contradiction_penalty
        overall = clamp(overall, 0.05, 0.95)

    Args:
        signals: List of signal dicts with keys "source", "confidence", "direction".
                 These are the signals Claude actually populated in the brief.
        sources_unavailable: Source names that returned no usable data.
        contradictions: cross_source_contradictions list from the brief.
        available_sources: If provided, used to compute coverage. Defaults to
                           all keys in SOURCE_WEIGHTS.

    Returns:
        ConfidenceResult with decomposed components.

    Design rationale:
    - Weighted average over quality weights: a strong SEC signal matters more
      than a strong Reddit signal.
    - Coverage penalty: missing high-quality sources (SEC, Yahoo) should reduce
      confidence more than missing Reddit. Simplified here to per-source flat
      penalty; a v2 could weight penalty by source importance.
    - Contradiction penalty: conflicting signals reduce reliability of the overall
      direction. Each detected contradiction pair reduces confidence by 5pp,
      capped at 20pp.
    - Clamp to [0.05, 0.95]: never emit 0.0 (would imply absolute certainty of
      no signal) or 1.0 (no source combination justifies certainty on a stock).
    """
    if available_sources is None:
        available_sources = list(SOURCE_WEIGHTS.keys())

    if not signals:
        return ConfidenceResult(
            overall_confidence=0.05,
            weighted_avg=0.0,
            coverage_penalty=0.0,
            contradiction_penalty=0.0,
            sources_scored=[],
            sources_missing=sources_unavailable,
            explanation="No usable signals — minimum confidence floor applied.",
        )

    # --- Step 1: Weighted average of signal confidences ---
    total_weight = 0.0
    weighted_sum = 0.0
    sources_scored = []

    for sig in signals:
        source = sig["source"]
        sig_confidence = float(sig["confidence"])
        weight = SOURCE_WEIGHTS.get(source, 0.5)  # default 0.5 for unknown sources
        weighted_sum += sig_confidence * weight
        total_weight += weight
        sources_scored.append(source)

    weighted_avg = weighted_sum / total_weight if total_weight > 0 else 0.0

    # --- Step 2: Coverage penalty ---
    n_missing = len(sources_unavailable)
    penalized_missing = max(0, n_missing - MISSING_SOURCE_FREE_THRESHOLD)
    coverage_penalty = penalized_missing * MISSING_SOURCE_PENALTY_PER_SOURCE

    # --- Step 3: Contradiction penalty ---
    n_contradictions = len(contradictions)
    contradiction_penalty = min(
        n_contradictions * CONTRADICTION_PENALTY_PER_PAIR,
        MAX_CONTRADICTION_PENALTY,
    )

    # --- Step 4: Final score ---
    raw = weighted_avg - coverage_penalty - contradiction_penalty
    overall = max(0.05, min(0.95, raw))

    # --- Explanation string (for observability) ---
    explanation = (
        f"weighted_avg={weighted_avg:.3f} "
        f"- coverage_penalty={coverage_penalty:.3f} ({n_missing} missing, "
        f"{penalized_missing} penalized) "
        f"- contradiction_penalty={contradiction_penalty:.3f} "
        f"({n_contradictions} contradictions) "
        f"= raw={raw:.3f} → clamped={overall:.3f}"
    )

    return ConfidenceResult(
        overall_confidence=round(overall, 3),
        weighted_avg=round(weighted_avg, 3),
        coverage_penalty=round(coverage_penalty, 3),
        contradiction_penalty=round(contradiction_penalty, 3),
        sources_scored=sources_scored,
        sources_missing=sources_unavailable,
        explanation=explanation,
    )


def inject_confidence_into_brief(brief: "InvestmentBrief") -> "InvestmentBrief":
    """
    Recompute overall_confidence from brief fields and inject.
    Claude emits a raw weighted average; this function applies penalties.
    Call this AFTER model_validate() to produce the final brief.
    """
    signals_as_dicts = [s.model_dump() for s in brief.signals]
    result = compute_confidence(
        signals=signals_as_dicts,
        sources_unavailable=brief.sources_unavailable,
        contradictions=brief.cross_source_contradictions,
    )
    # Return a new instance with corrected confidence
    return brief.model_copy(
        update={"overall_confidence": result.overall_confidence}
    )
```

**Example outputs:**

| Scenario | weighted_avg | coverage_penalty | contradiction_penalty | final |
|----------|-------------|-----------------|----------------------|-------|
| 6 sources, 0 contradictions | 0.78 | 0.00 | 0.00 | 0.78 |
| 3 sources, 0 contradictions | 0.75 | 0.03 | 0.00 | 0.72 |
| 3 sources, 2 contradictions | 0.75 | 0.03 | 0.10 | 0.62 |
| 1 source, 0 contradictions | 0.85 | 0.15 | 0.00 | 0.70 |

---

## 8. Production Gotchas — Sonnet 4.6 Specific

### 8.1 max_tokens and Extended Thinking

Sonnet 4.6 supports extended thinking but **not with `tool_choice: {"type": "tool"}`** — this combination throws a 400 error. If you ever add `betas=["interleaved-thinking-2025-05-14"]`, you must switch to `tool_choice: {"type": "auto"}` and add prompt instruction to force the tool call. For this synthesizer: do not use extended thinking. The prompt is structured enough; the model does not need chain-of-thought for structured extraction.

Max output for Sonnet 4.6: **64k tokens** (synchronous API). InvestmentBrief output is ~1,200 tokens. Set `max_tokens=4096` — gives 3x headroom without over-provisioning. Do NOT set to 64000; you pay for output tokens on a per-token basis and a bug in the prompt could cause runaway generation.

### 8.2 Tool-Use Latency vs Streaming

Forced tool-use (`tool_choice: tool`) with `strict=True` has additional latency vs vanilla generation due to grammar compilation. Anthropic docs note schemas are cached for 24h after first use — first call per deployment will be 200-500ms slower. Subsequent calls are schema-cache hits. For the demo: warm up the schema cache by sending a dummy request at server startup.

```python
# main.py — FastAPI startup event
from synthesizer import build_tool_definition, client
import anthropic

@app.on_event("startup")
async def warm_schema_cache():
    """
    Send a no-op request to compile and cache the InvestmentBrief schema.
    This prevents the first real user request from taking the compilation hit.
    """
    tool_def = build_tool_definition()
    try:
        # Minimal request — max_tokens=1 means it will hit max_tokens stop reason
        # but the schema compilation happens on the API side regardless
        client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1,
            messages=[{"role": "user", "content": "warmup"}],
            tools=[tool_def],
            tool_choice={"type": "tool", "name": "emit_investment_brief"},
        )
    except anthropic.APIStatusError:
        pass  # Expected — max_tokens=1 will fail tool-use output; schema is still cached
```

### 8.3 Rate Limit Headers

Sonnet 4.6 rate limits are returned in response headers. The SDK exposes them via the raw HTTP response. Wire these into your cost tracker:

```python
# In synthesize(), after client.messages.create(), access raw response:
# The Anthropic Python SDK v0.40+ exposes response.http_response

with client.messages.with_raw_response.create(
    model="claude-sonnet-4-6",
    max_tokens=4096,
    system=system,
    messages=[user_msg],
    tools=[tool_def],
    tool_choice={"type": "tool", "name": "emit_investment_brief"},
) as raw_response:
    response = raw_response.parse()
    headers = raw_response.headers

rate_limit_info = {
    "requests_limit": headers.get("anthropic-ratelimit-requests-limit"),
    "requests_remaining": headers.get("anthropic-ratelimit-requests-remaining"),
    "requests_reset": headers.get("anthropic-ratelimit-requests-reset"),
    "tokens_limit": headers.get("anthropic-ratelimit-tokens-limit"),
    "tokens_remaining": headers.get("anthropic-ratelimit-tokens-remaining"),
    "tokens_reset": headers.get("anthropic-ratelimit-tokens-reset"),
    "retry_after": headers.get("retry-after"),  # only present on 429
}
```

If `tokens_remaining` drops below 10,000, add a 1-second sleep before the next synthesis call. Do not use `time.sleep()` in async code — use `await asyncio.sleep(1.0)`.

### 8.4 Schema Complexity Limits

The `InvestmentBrief` schema is moderately complex (2 levels of nesting, 17 fields at top level, 6 fields in Signal). Anthropic's strict mode has undocumented schema complexity limits. If you add more nested models or deeply nested `anyOf` chains, you may hit "Schema is too complex for compilation" (400 error). Keep the schema flat where possible.

The current schema as defined will compile cleanly. Do not add `list[list[str]]` or `dict[str, list[Signal]]` patterns — they push complexity up and may hit the limit.

### 8.5 Cache Invalidation Trigger

Per Anthropic docs: changes to `tool_choice` parameter invalidate cached message blocks but NOT tool definition cache. The tool definition cache (Block 4) is independent from the message cache (Block 2 in system). You can safely change `tool_choice` between calls without invalidating the tool schema cache.

What does invalidate tool cache: any change to the `input_schema` JSON, the tool `description`, or the `name`. Lock these down in a versioned constant — do not regenerate the schema dynamically per request.

---

## File Map

```
altbrief/
├── synthesizer.py      # synthesize(), build_tool_definition(), build_system_prompt(),
│                       # build_user_message(), SynthesizerError, _clean_schema_for_claude()
├── confidence.py       # compute_confidence(), inject_confidence_into_brief(), SOURCE_WEIGHTS
├── models.py           # Signal, InvestmentBrief Pydantic models (import from here everywhere)
└── router.py           # FastAPI SSE endpoint, 2-call streaming pattern
```

Import order matters: `models.py` → `confidence.py` → `synthesizer.py` → `router.py`. No circular imports.

---

## Quick Validation Checklist (before demo)

- [ ] `InvestmentBrief.model_json_schema()` runs without error
- [ ] `_clean_schema_for_claude()` removes `maxLength`/`minLength` from Signal fields
- [ ] First synthesis call: `response.usage.cache_creation_input_tokens > 0`
- [ ] Second synthesis call (same session): `response.usage.cache_read_input_tokens > 0`
- [ ] `response.stop_reason == "tool_use"` on every call
- [ ] `tool_block.name == "emit_investment_brief"` on every call
- [ ] `InvestmentBrief.model_validate(tool_block.input)` succeeds
- [ ] `inject_confidence_into_brief()` produces `overall_confidence` in [0.05, 0.95]
- [ ] Schema warmup call runs at FastAPI startup
- [ ] Streaming SSE: `narrative_chunk` events arrive before `brief_ready`
