# Agentic Orchestration Patterns — Alt-Data Investment Brief Agent

## Decision Summary (TL;DR)

| Decision | Winner | Reason |
|---|---|---|
| Orchestration | **Pure asyncio + Claude synthesis** | Lowest code, no framework overhead, 5-day build |
| Streaming | **FastAPI SSE `EventSourceResponse`** | Simpler than WebSocket, enough for agent events |
| Caching | **File-based JSON TTL** | Zero infra, survives restarts, demo-perfect |
| Synthesis | **Claude tool-use + Pydantic v2** | Reliable structured JSON |
| Observability | **Langfuse OSS (free cloud)** | OTel-native, per-call trace + cost |
| Deployment | **Fly.io (free hobby)** | Always-on, no cold start, 1-command deploy |
| Degradation | **Partial brief + `[Source unavailable]`** | Never fail whole brief for one bad source |

---

## Architecture Comparison

### Option A — Pure asyncio + Claude synthesis [RECOMMENDED]

6-8 Python `async def` tool functions (one per data source). Fan out with `asyncio.gather(return_exceptions=True)`. Feed all results into single Claude call via tool-use for synthesis. Claude SDK only at synthesis step.

- **Latency:** Bounded by slowest source. 8 sources × 8-12s parallel → **18-25s total**. Within 45s target.
- **Debug:** Excellent. Each tool = plain Python function. Exceptions surface directly.
- **Streaming:** `asyncio.as_completed()` yields SSE events as sources finish.
- **Complexity:** ~150-200 lines core orchestrator. Lowest.
- **Pick when:** 5-day build, 1-2 person team, I/O-bound sources, no multi-turn state. **This is the one.**

### Option B — LangGraph
- Native `astream_events()` clean SSE
- Reducer required (`Annotated[list, operator.add]`) for parallel writes — #1 LangGraph parallel bug
- ~300 lines boilerplate for 8 sources
- **Pick for V2** when need checkpointing/resume, human-in-loop, multi-turn

### Option C — CrewAI [SKIP]
Each agent makes own LLM call to decide tool usage. +3-5s per source. Overkill for scraping where sources are predetermined.

### Option D — DSPy
Not orchestrator — prompt optimizer. Use AFTER hackathon to compile synthesis prompt against golden set.

### Option E — n8n / Pipedream [REJECT]
Judges want code. Latency control limited.

---

## Parallel Tool Calling — Claude API Gotcha

When Claude returns multiple `tool_use` blocks, **must return ALL results in single user message** with multiple `tool_result` blocks. Split = `invalid_request_error`.

```python
user_message = {
    "role": "user",
    "content": [
        {"type": "tool_result", "tool_use_id": "tu_1", "content": reddit_result},
        {"type": "tool_result", "tool_use_id": "tu_2", "content": linkedin_result},
    ]
}
```

**Why skip Claude-native parallel for fan-out:** Adds extra LLM round-trip (decide → parallel calls → synthesize) = ~3s + ~$0.01 on orchestration reasoning we'd hardcode. We know which 8 sources to call — hardcode it.

---

## Streaming Partial Results — SSE Pattern

```python
from sse_starlette.sse import EventSourceResponse
import asyncio

async def generate_brief_events(ticker: str):
    sources = [
        ("reddit", scrape_reddit_wsb),
        ("linkedin", scrape_linkedin_jobs),
        ("sec", scrape_sec_filings),
        ("news", scrape_news_headlines),
        ("earnings", scrape_earnings_transcript),
        ("github", scrape_github_activity),
    ]

    tasks = [(name, asyncio.create_task(safe_scrape(ticker, name, fn)))
             for name, fn in sources]

    results = {}
    for i, (name, task) in enumerate(asyncio.as_completed_with_names(tasks)):
        result = await task
        results[name] = result
        progress = int((i + 1) / len(sources) * 80)
        yield f"data: {BriefEvent(event_type='source_done', source=name, progress=progress).model_dump_json()}\n\n"

    yield f"data: {BriefEvent(event_type='synthesis_start', progress=80).model_dump_json()}\n\n"
    brief = await synthesize_brief(ticker, results)
    yield f"data: {BriefEvent(event_type='brief_ready', data=brief.model_dump(), progress=100).model_dump_json()}\n\n"

@app.get("/brief/stream/{ticker}")
async def stream_brief(ticker: str):
    return EventSourceResponse(
        generate_brief_events(ticker),
        headers={"X-Accel-Buffering": "no"}
    )
```

`as_completed` is key — Reddit finishing at 3s triggers SSE immediately even if LinkedIn takes 12s. Live progress, not blank-then-everything.

---

## Caching — File-based JSON

```python
import time, json
from pathlib import Path
from functools import wraps

CACHE_DIR = Path(".cache")
CACHE_DIR.mkdir(exist_ok=True)
CACHE_TTL = 3600  # 1 hour

def ttl_cache(fn):
    @wraps(fn)
    async def wrapper(ticker: str, *args, **kwargs):
        key = f"{fn.__name__}_{ticker}.json"
        cache_path = CACHE_DIR / key
        if cache_path.exists():
            data = json.loads(cache_path.read_text())
            if time.time() - data["ts"] < CACHE_TTL:
                return data["result"]
        result = await fn(ticker, *args, **kwargs)
        cache_path.write_text(json.dumps({"ts": time.time(), "result": result}))
        return result
    return wrapper
```

Survives process restarts. NVDA queried 15× during demo = 14 instant responses. Judges notice.

---

## Failure Modes + Graceful Degradation

**Golden rule:** Never fail brief for one bad source. 7/8-source brief beats no brief.

```python
from pydantic import BaseModel
from enum import Enum

class SourceStatus(str, Enum):
    OK = "ok"
    TIMEOUT = "timeout"
    RATE_LIMITED = "rate_limited"
    BLOCKED = "blocked"
    ERROR = "error"

class SourceResult(BaseModel):
    source: str
    status: SourceStatus
    data: dict | None = None
    error_msg: str | None = None
    latency_ms: int = 0
    cached: bool = False

async def safe_scrape(ticker: str, source_name: str, fn, timeout_s: float = 15.0) -> SourceResult:
    start = time.monotonic()
    try:
        async with asyncio.timeout(timeout_s):
            data = await fn(ticker)
            return SourceResult(source=source_name, status=SourceStatus.OK,
                                data=data, latency_ms=int((time.monotonic()-start)*1000))
    except asyncio.TimeoutError:
        return SourceResult(source=source_name, status=SourceStatus.TIMEOUT,
                            error_msg=f"Timed out after {timeout_s}s")
    except Exception as e:
        return SourceResult(source=source_name, status=SourceStatus.ERROR, error_msg=str(e))
```

**Retry + confidence penalty:**
- TIMEOUT: 1 retry with 2s backoff, then mark unavailable
- RATE_LIMITED: skip, penalize confidence
- BLOCKED: alert observability (billing issue)
- 3+ unavailable: `PARTIAL_DATA` flag, cap `overall_confidence` at 0.50

Synthesis instruction: *"For any source with `status != ok`, write `[Source unavailable: {reason}]` in relevant section. Reduce overall_confidence proportionally."*

---

## Cost Guardrails

**Per-request budget:**
- Sonnet 4.6: $3/M input, $15/M output
- 8 sources × 500 tokens = 4K + 1.5K system = ~5.5K input + ~800 output = **~$0.029/request**
- With prompt caching: **~$0.012/request**

**Hard token cap:**

```python
MAX_INPUT_TOKENS = 12_000

def build_synthesis_content(results: list[SourceResult]) -> list[str]:
    blocks = []
    total_chars = 0
    priority_order = ["sec", "earnings", "linkedin", "news", "github", "reddit", "twitter"]
    sorted_results = sorted(results, key=lambda r: priority_order.index(r.source)
                             if r.source in priority_order else 99)
    for r in sorted_results:
        if r.status == SourceStatus.OK and r.data:
            blob = json.dumps(r.data)[:2000]  # 2000 chars/source max
            total_chars += len(blob)
            if total_chars > MAX_INPUT_TOKENS * 4:
                break
            blocks.append(f"<source name='{r.source}'>\n{blob}\n</source>")
    return blocks
```

**Per-day spend cap (file ledger):**

```python
from datetime import date

DAILY_CAP_USD = 5.0

def check_and_record_cost(cost_usd: float) -> bool:
    today = str(date.today())
    path = Path("data/cost_tracker.json")
    data = json.loads(path.read_text()) if path.exists() else {}
    if data.get(today, 0.0) + cost_usd > DAILY_CAP_USD:
        return False
    data[today] = data.get(today, 0.0) + cost_usd
    path.write_text(json.dumps(data))
    return True
```

---

## Observability — Langfuse via OTel

```python
import structlog
log = structlog.get_logger()

log.info("synthesis_complete",
    ticker=ticker,
    model="claude-sonnet-4-6",
    input_tokens=response.usage.input_tokens,
    cached_tokens=response.usage.cache_read_input_tokens,
    output_tokens=response.usage.output_tokens,
    cache_hit_rate=response.usage.cache_read_input_tokens / max(response.usage.input_tokens, 1),
    latency_ms=latency_ms,
    cost_usd=compute_cost(response.usage),
    sources_ok=sum(1 for r in results if r.status == SourceStatus.OK),
    overall_confidence=brief.overall_confidence,
)
```

```python
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from base64 import b64encode

provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(
    endpoint=f"{LANGFUSE_HOST}/api/public/otel",
    headers={"Authorization": f"Basic {b64encode((PUBLIC_KEY + ':' + SECRET_KEY).encode()).decode()}"}
)))
```

**Show Langfuse dashboard during demo** — judges love live observability.

---

## Claude Synthesizer — Tool Use + Pydantic

```python
from pydantic import BaseModel, Field
from typing import Literal

class Signal(BaseModel):
    source: str
    direction: Literal["bullish", "bearish", "neutral"]
    summary: str = Field(max_length=200)
    confidence: float = Field(ge=0.0, le=1.0)
    raw_evidence: str = Field(max_length=500)

class InvestmentBrief(BaseModel):
    ticker: str
    signals: list[Signal]
    risk_factors: list[dict]
    overall_direction: Literal["bullish", "bearish", "neutral"]
    overall_confidence: float = Field(ge=0.0, le=1.0)
    brief_narrative: str = Field(max_length=800)
    data_quality_flag: Literal["full", "partial", "minimal"]
    sources_used: list[str]
    sources_unavailable: list[str]
```

Pass `InvestmentBrief.model_json_schema()` as tool `input_schema`. Set `tool_choice: {type: "tool", name: ...}`.

**Synthesis system prompt (cache-friendly with `cache_control: {"type": "ephemeral"}`):**
- Role (senior sell-side analyst)
- Rules (cite only what data says, never invent statistics)
- Source quality weights (SEC 1.0, earnings 0.9, LinkedIn 0.7, news 0.65, GitHub 0.5, Reddit 0.4)
- One complete NVDA few-shot example (also cached)
- `[Source unavailable]` formatting instruction

---

## Confidence Scoring

```python
QUALITY_WEIGHTS = {"sec": 1.0, "earnings": 0.9, "linkedin": 0.7,
                   "news": 0.65, "github": 0.5, "reddit": 0.4, "twitter": 0.35}

def compute_overall_confidence(signals: list[Signal], sources_ok: int, total_sources: int) -> float:
    if not signals:
        return 0.10
    weighted_sum = sum(s.confidence * QUALITY_WEIGHTS.get(s.source, 0.5) for s in signals)
    weight_total = sum(QUALITY_WEIGHTS.get(s.source, 0.5) for s in signals)
    base = weighted_sum / weight_total if weight_total > 0 else 0.3
    coverage = sources_ok / total_sources
    penalty = 1.0 if coverage >= 0.85 else (0.75 if coverage >= 0.60 else 0.50)
    return round(min(base * penalty, 0.97), 3)
```

**Frontend:** 0.80+ → green "High Conviction" | 0.60-0.79 → yellow "Moderate" | <0.60 → red "Weak — verify"

---

## Eval Harness (Promptfoo)

```yaml
providers:
  - id: claude-sonnet-4-6
prompts:
  - file://prompts/synthesis_system.txt
tests:
  - description: "NVDA earnings beat → bullish"
    vars: {ticker: NVDA, source_data: "{{mocks.nvda_beat}}"}
    assert:
      - type: python
        value: "output['overall_direction'] == 'bullish'"
      - type: python
        value: "output['overall_confidence'] >= 0.75"
      - type: is-json
  - description: "Partial sources → confidence capped"
    vars: {ticker: META, source_data: "{{mocks.meta_partial}}"}
    assert:
      - type: python
        value: "output['data_quality_flag'] == 'partial'"
      - type: python
        value: "output['overall_confidence'] <= 0.75"
```

Run: `npx promptfoo eval --config promptfoo.yaml`

**CI gate:** Any prompt change → run golden set → fail PR if direction_match drops below 90%.

---

## Deployment — Fly.io

```toml
[http_service]
  auto_stop_machines = false   # CRITICAL — keep warm for demo
  auto_start_machines = true
  min_machines_running = 1
primary_region = "sjc"         # San Francisco — low latency to BrightData
```

Without `auto_stop_machines = false`, dyno sleeps after 30min idle → 30s cold start on stage.

| Platform | Free | Async | Cold Start |
|---|---|---|---|
| **Fly.io** | 3 VMs 256MB | Yes always-on | None |
| Render | 1 web service | Yes but spins down | 30s after idle |
| Modal | $30/mo credits | Serverless | <1s CPU |
| Vercel Functions | Generous | No 60s timeout | ~200ms |

---

## Code Structure

```
altdata-brief-agent/
├── main.py                   # FastAPI + SSE endpoint
├── orchestrator.py           # asyncio fan-out, safe_scrape, as_completed
├── sources/
│   ├── reddit.py             # BrightData MCP → r/wallstreetbets
│   ├── linkedin.py           # BrightData job postings
│   ├── sec.py                # BrightData SEC filing scrape
│   ├── earnings.py           # BrightData earnings transcript
│   ├── github.py             # BrightData GitHub activity
│   └── news.py               # BrightData news headlines
├── synthesizer.py            # Claude tool-use synthesis
├── schemas.py                # InvestmentBrief, Signal, SourceResult
├── cache.py                  # File-based TTL cache decorator
├── confidence.py             # Weighted confidence rollup
├── cost_tracker.py           # Per-day spend ledger
├── observability.py          # structlog + OTEL → Langfuse
├── prompts/synthesis_system.txt
├── data/evals/brief_agent/
│   ├── golden_set.yaml       # 30+ test cases
│   └── mocks/                # Pre-recorded responses
├── promptfoo.yaml
├── fly.toml
└── Dockerfile
```

---

## Sources

- [Anthropic Programmatic Tool Calling](https://platform.claude.com/docs/en/agents-and-tools/tool-use/programmatic-tool-calling)
- [Claude Agent SDK Structured Outputs](https://code.claude.com/docs/en/agent-sdk/structured-outputs)
- [LangGraph Parallel Fan-Out](https://markaicode.com/langgraph-parallel-fan-out-fan-in/)
- [FastAPI SSE Streaming](https://dev.to/kasi_viswanath/streaming-ai-agent-with-fastapi-langgraph-2025-26-guide-1nkn)
- [Semantic Caching FastAPI + Redis 2026](https://pyimagesearch.com/2026/04/27/semantic-caching-for-llms-fastapi-redis-and-embeddings/)
- [Langfuse OTel Integration](https://langfuse.com/integrations/native/opentelemetry)
- [Promptfoo](https://github.com/promptfoo/promptfoo)
- [Fly.io FastAPI](https://fly.io/docs/python/frameworks/fastapi/)
- [DSPy vs LangGraph 2026](https://www.respan.ai/market-map/compare/dspy-vs-langgraph)
- [Token-Based Rate Limiting 2026](https://zuplo.com/learning-center/token-based-rate-limiting-ai-agents)
