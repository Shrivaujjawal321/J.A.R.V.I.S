# Component 17 — Backend Architecture, Streaming & Robustness
**Tata Steel AI Hackathon 2026 | Round 2 | Maintenance Wizard**
**Research date: 2026-06-06 | Status: FINAL**

---

## 1. Recommended Approach

**FastAPI 0.136.x (ASGI/asyncio) + native `EventSourceResponse` (fastapi.sse, added in 0.135.0) + APScheduler 3.x AsyncIOScheduler (lifespan-managed) + tenacity 9.x async retry + pybreaker 1.x circuit breaker + structlog + asgi-correlation-id middleware.**

This is not a hedged recommendation. This is the single correct architecture for a solo, CPU-only, pip-installable, demo-must-not-crash hackathon backend that also needs to score on latency, efficiency, and explainability.

The heart of the decision: FastAPI 0.135.0 merged native SSE support via `fastapi.sse.EventSourceResponse` — eliminating the sse-starlette dependency that previously added complexity, version coupling, and disconnect-handling bugs. The new native implementation handles keep-alive pings (every 15 seconds), `X-Accel-Buffering: no` for Nginx, `Cache-Control: no-cache`, and `Last-Event-ID` resume — all zero-config. Combined with asyncio's cooperative scheduling (one process, no thread pool overhead for I/O-bound LLM calls), the result is a backend that is simultaneously the simplest and most robust option available in mid-2026.

---

## 2. Why This Stack Wins — Evidence-Based

### 2a. Native SSE in FastAPI 0.135.0 is the decisive version milestone

FastAPI merged native SSE support (PR merged, released in 0.135.0, current stable is **0.136.3** as of May 23, 2026). The import path is `from fastapi.sse import EventSourceResponse, ServerSentEvent`. Pydantic serialization of event `data` happens on the Rust side (via pydantic-core), meaning typed model objects can be yielded directly — no manual JSON serialization step. This is materially different from the sse-starlette 3.4.4 approach where every event is a raw dict.

Key built-in behaviors (from official docs, confirmed):
- Keep-alive `ping` comment every 15 seconds when stream is idle → prevents proxy disconnects without any code.
- `X-Accel-Buffering: no` set automatically → SSE works behind Nginx without manual `proxy_buffering off` config.
- `Cache-Control: no-cache` auto-set → browsers won't cache the stream.
- `Last-Event-ID` header support → clients can resume streams after reconnect.
- POST endpoints supported (not just GET) → the chat endpoint can be `POST /v1/chat/stream` with a body, which is idiomatic for LLM streaming.

### 2b. Async cooperative scheduling = zero thread pool overhead

Every component in the Maintenance Wizard is I/O-bound: LLM API calls, vector DB queries, sensor data reads, SQLite checkpoint reads. FastAPI's async event loop handles these with a single OS thread using `await`. The alternative (threading) would require a thread pool, thread-safe state management, and adds ~0.5-2ms context-switch latency per concurrent request. At hackathon demo scale (1-3 judges, sequential queries) this is irrelevant — but the architecture is correct for real steel-plant scale too.

Benchmark reference: FastAPI + Starlette 0.18.0+ achieves ~15,000 req/s at p95 < 20ms for JSON endpoints (dasroot.net 2026 benchmark). For SSE streaming endpoints with LLM calls, the bottleneck is network I/O to the LLM provider, not server throughput — async handles this correctly by not blocking the event loop during the await.

### 2c. tenacity 9.x is the correct retry library for async LLM calls

tenacity is Apache 2.0, has 5,300+ GitHub stars, and is the default retry library for LangChain, LlamaIndex, and most production LLM wrappers. The `@retry` decorator composes with `async def` transparently. For LLM calls, the correct configuration is: exponential backoff with jitter, 3 attempts max, retry on 429/500/502/503/504, fail-fast on 400/401/403/422. Community production consensus (confirmed by portkey.ai and getmaxim.ai 2025 production guides) is: start at 1s, double each retry, cap at 30s, jitter ±20% to prevent thundering herd.

### 2d. pybreaker for circuit breaker — prevents demo crashes on LLM provider outages

pybreaker (latest release: September 21, 2025, Python ≥3.9) implements the Nygard circuit breaker pattern. Default config: trip open after 5 consecutive failures, 60-second cooldown. For the hackathon, the circuit protects the Claude/Anthropic API call path. When the circuit is open, the endpoint returns a graceful `503 Service Temporarily Unavailable` with a structured error envelope rather than hanging or throwing an unhandled exception. This directly serves the "demo must not crash" judging criterion.

### 2e. APScheduler 3.x AsyncIOScheduler for proactive sensor checks

The proactive alert requirement (functional requirement 7: real-time abnormal alerts) requires a background scheduler that runs anomaly checks against incoming sensor data on a configurable interval (e.g., every 60 seconds). APScheduler 3.x with `AsyncIOScheduler` runs jobs in the same asyncio event loop as FastAPI — no threads, no subprocesses. The scheduler is initialized in the FastAPI `lifespan` context manager (the modern API, replacing deprecated `@app.on_event`), which guarantees clean shutdown. APScheduler 4.0 exists but requires SQLAlchemy data stores and is more complex; 3.x is the correct choice for a solo 9-day build.

### 2f. structlog + asgi-correlation-id for explainable, traceable logs

Judges score on "explainable and traceable outputs grounded to sources." This applies not just to LLM outputs but to the system's own behavior. structlog produces JSON-structured logs that include: `correlation_id` (per-request UUID from `asgi-correlation-id` middleware), `agent_step`, `tool_called`, `equipment_id`, `latency_ms`, `llm_provider`, `retry_count`. This makes every request traceable during the demo — judges can see the exact reasoning chain in logs in real time.

---

## 3. Exact Stack

| Library | Version | Role |
|---|---|---|
| `fastapi` | 0.136.3 | ASGI framework, routing, dependency injection, native SSE |
| `uvicorn[standard]` | 0.34.x | ASGI server (httptools + uvloop for max performance) |
| `pydantic` | v2.x (bundled with fastapi) | Request/response validation, error envelopes, schema generation |
| `sse-starlette` | NOT used | Superseded by native fastapi.sse in 0.135.0 |
| `apscheduler` | 3.11.x | Asyncio-native proactive alert scheduler (interval jobs) |
| `tenacity` | 9.x | Async retry with exponential backoff + jitter on LLM calls |
| `pybreaker` | 1.x | Circuit breaker around Anthropic/Claude API calls |
| `httpx` | 0.27.x | Async HTTP client for any external API calls |
| `structlog` | 24.x | Structured JSON logging with contextvars support |
| `asgi-correlation-id` | 4.x | Per-request correlation ID middleware, bound to structlog context |
| `python-dotenv` | 1.x | Environment variable loading from `.env` |
| `anyio` | 4.x | Async primitives (cancel scopes, task groups) for disconnect handling |

**Full pip install line (one command, no Docker):**
```
pip install "fastapi[standard]" uvicorn[standard] apscheduler tenacity pybreaker httpx structlog asgi-correlation-id python-dotenv anyio
```

---

## 4. Alternatives Considered and Why Each Lost

### Alternative A: sse-starlette 3.4.4 as the SSE layer

**Tradeoff that made it lose:** Redundant since FastAPI 0.135.0. sse-starlette is a third-party library that wraps Starlette's `StreamingResponse` with SSE formatting. FastAPI now ships this natively. Using sse-starlette on top of FastAPI 0.136.x adds a dependency with no benefit, and its `EventSourceResponse` conflicts with FastAPI's own `EventSourceResponse` import path. For projects pinned to FastAPI < 0.135.0 it remains useful; for this build it is dead weight.

### Alternative B: WebSockets instead of SSE

**Tradeoff that made it lose:** WebSockets are bidirectional and require a handshake protocol. SSE is a unidirectional server-push mechanism — which is exactly what the Maintenance Wizard needs for streaming LLM tokens and proactive alerts. SSE runs over plain HTTP/1.1, works through corporate proxies and firewalls (common in steel-plant IT environments), has native browser `EventSource` API support without any client library, and reconnects automatically. WebSockets would require a WS client library on the frontend, state management for reconnection, and add complexity with no functional gain. The only scenario where WebSockets win is bidirectional real-time communication (e.g., collaborative editing) — not applicable here.

### Alternative C: Litestar 2.x instead of FastAPI

**Tradeoff that made it lose:** Litestar's msgspec serialization is 10-20x faster than Pydantic V2 in synthetic benchmarks (byteiota.com 2026). In production, this gap disappears in database/LLM I/O-bound workloads. More critically: Litestar has a smaller ecosystem, fewer Stack Overflow answers, and the judge is more likely to be familiar with FastAPI's Swagger UI at `/docs`. FastAPI has 4.5M daily downloads vs. Litestar's ~80K. For a hackathon demo, ecosystem familiarity and ecosystem-integrated libraries (LangGraph has FastAPI examples, not Litestar examples) matter more than 12x faster JSON serialization that never shows up in a demo.

### Alternative D: Flask + Flask-SSE / aiohttp

**Tradeoff that made it lose:** Flask is synchronous by default (WSGI). Flask-SSE requires Redis. aiohttp has no automatic OpenAPI generation. Both lack FastAPI's dependency injection, Pydantic integration, and type-driven documentation. These are 2019-tier choices that would cost points on the "technical implementation & innovation" judging axis. Anti-pattern tier.

---

## 5. Anti-Patterns — What Screams "Amateur / 2022-Tier"

1. **Using `@app.on_event("startup")`** — deprecated since FastAPI 0.95.0. The modern API is `@asynccontextmanager` lifespan. Judges who know FastAPI will notice immediately.

2. **Returning raw exceptions to the client** — `raise HTTPException(detail=str(e))` where `e` is an internal `openai.RateLimitError`. Never expose provider error messages, stack traces, or internal model names in 5xx responses.

3. **Synchronous blocking calls inside `async def`** — `requests.get(...)` inside an `async def` route blocks the entire event loop. Any LLM client, HTTP call, or file I/O inside an async handler must use an async equivalent (`httpx.AsyncClient`, `aiofiles`, `asyncio.to_thread` for CPU-bound ops).

4. **No idempotency for the POST /chat endpoint** — if the judge hits refresh during a demo crash and the same query fires twice, a naive implementation creates two LangGraph runs with duplicate state. The chat endpoint must accept a `session_id` and resume from SQLite checkpoint if the session already exists.

5. **Polling instead of streaming** — returning `{"status": "processing"}` and making the client poll `/results/{id}` is the 2020-tier pattern. SSE streaming with progressive tokens is the 2026 standard and directly scores on latency and user experience.

6. **`app.add_middleware(CORSMiddleware, allow_origins=["*"])` with no rate limiting** — CORS wildcard in production is a security anti-pattern. For a hackathon, `allow_origins=["http://localhost:3000", "http://localhost:5173"]` is correct.

7. **Using threading.Timer or `time.sleep` for scheduled tasks** — blocks threads, doesn't integrate with asyncio's event loop. APScheduler AsyncIOScheduler or `asyncio.create_task` with a `while True: await asyncio.sleep(interval)` loop are the correct patterns.

8. **No structured error envelope** — returning `{"detail": "Internal Server Error"}` (FastAPI's default) gives judges nothing to debug during the demo. Every error must carry `code`, `message`, `type`, `request_id`, and optionally `doc_url`.

---

## 6. Integration Notes

### Inputs consumed

- **From Component 01 (LangGraph Orchestrator):** The backend wraps the LangGraph graph as a service. The `/v1/chat/stream` endpoint accepts `{session_id, equipment_id, query}`, invokes `graph.astream(input, config={"configurable": {"thread_id": session_id}})`, and yields each LangGraph chunk as an SSE event. The graph's TypedDict state is transparently streamed — each node transition emits a `ServerSentEvent(data=chunk, event="agent_step")`.
- **From Component 08/09/10 (RUL/Anomaly/Failure Prediction):** The APScheduler background job calls the anomaly and RUL modules every N seconds (configurable, default 60s). These are in-process Python function calls — no HTTP overhead. The scheduler job constructs an alert payload if thresholds are breached and pushes it to an in-memory `asyncio.Queue` that the SSE alert stream endpoint drains.
- **From Component 04 (RAG):** RAG retrieval is called synchronously within the LangGraph node — the backend never calls RAG directly, it goes through the graph.
- **From Component 15/16 (Risk + Maintenance Recommendation):** These are LangGraph nodes. The backend streams their output as SSE events with `event="risk_update"` and `event="recommendation_ready"` event types.

### Outputs produced

- `POST /v1/chat/stream` → `text/event-stream` response; events typed as `agent_step | tool_call | token | risk_update | recommendation_ready | error | done`
- `GET /v1/alerts/stream` → persistent SSE stream; events typed as `anomaly_alert | rul_warning | critical_failure` pushed by the APScheduler background job
- `GET /v1/session/{session_id}/state` → JSON; the full LangGraph checkpoint state for explainability / "show your reasoning" demo moments
- `POST /v1/feedback` → JSON; records engineer thumbs-up/down + correction on a recommendation (feeds Component feedback loop)
- `GET /v1/health` → JSON; liveness probe including circuit breaker state and scheduler job status
- `GET /docs` → Swagger UI (auto-generated by FastAPI)

### Components it talks to

| Component | Direction | Transport |
|---|---|---|
| LangGraph Orchestrator (01) | Backend calls | In-process `graph.astream()` |
| RUL Predictor (08) | Scheduler calls | In-process function call |
| Anomaly Detector (09) | Scheduler calls | In-process function call |
| Failure Predictor (10) | Scheduler calls | In-process function call |
| Frontend (React/Vite or Streamlit) | Frontend connects | HTTP SSE |
| Anthropic Claude API | Backend calls (with retry + circuit breaker) | HTTPS via httpx |
| SQLite checkpoint (LangGraph) | Read by session state endpoint | In-process sqlite3 |

### Error envelope schema (Pydantic)

```python
class ErrorDetail(BaseModel):
    code: str          # machine-readable: "LLM_UNAVAILABLE", "INVALID_SESSION", etc.
    message: str       # human-readable
    type: Literal["validation", "auth", "server", "upstream", "rate_limit"]
    request_id: str    # correlation_id from asgi-correlation-id middleware
    doc_url: str | None = None

class ErrorEnvelope(BaseModel):
    error: ErrorDetail
```

All exception handlers (including the global catch-all) emit this envelope with the appropriate HTTP status code.

### SSE event schema (Pydantic, yielded from graph.astream)

```python
class AgentStepEvent(BaseModel):
    event_type: Literal["agent_step", "tool_call", "token", "risk_update",
                        "recommendation_ready", "alert", "error", "done"]
    session_id: str
    equipment_id: str | None
    payload: dict          # varies by event_type; typed sub-models in practice
    timestamp_utc: str     # ISO 8601
    source_node: str | None  # LangGraph node name for explainability
```

### Lifespan pattern (canonical)

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    scheduler = AsyncIOScheduler()
    scheduler.add_job(run_proactive_checks, "interval", seconds=60, id="sensor_watchdog")
    scheduler.start()
    app.state.scheduler = scheduler
    app.state.alert_queue = asyncio.Queue()
    yield
    # Shutdown
    scheduler.shutdown(wait=False)

app = FastAPI(lifespan=lifespan)
```

---

## 7. Open Risks and Unknowns

1. **`request.receive()` for cancel-on-disconnect is not public FastAPI API.** The `cancel_on_disconnect` pattern that uses `await request.receive()` to detect HTTP disconnect works with uvicorn but is not guaranteed across all ASGI servers. For the hackathon (uvicorn), this is safe. Tag: [unverified for non-uvicorn deployments].

2. **APScheduler 4.0 AsyncScheduler vs. 3.x AsyncIOScheduler API break.** APScheduler 4.0 introduced a completely new API (requires SQLAlchemy data stores, different trigger syntax). `pip install apscheduler` currently installs 3.11.x. If this resolves to 4.0 in the future, the lifespan code will break. Pin explicitly: `apscheduler==3.11.*` in requirements.txt.

3. **pybreaker thread-safety with asyncio.** pybreaker's `CircuitBreaker` uses threading locks internally. In a pure asyncio context, these locks are safe (GIL-protected single-threaded execution for CPU-bound sections), but if the backend ever spawns threads via `asyncio.to_thread`, there is a theoretical lock contention risk. For this build: [low risk, acceptable].

4. **FastAPI native SSE `Last-Event-ID` resume semantics.** The native `EventSourceResponse` supports `Last-Event-ID` header for stream resumption, but the resume logic (re-yielding events after the given ID) must be implemented in the generator function itself — FastAPI does not buffer events. For LangGraph streams, this means replaying from SQLite checkpoint. Implementation is straightforward but must be explicitly coded. [unverified: not tested in this research — needs 30-minute implementation spike].

5. **Alert stream backpressure.** The `asyncio.Queue` used for proactive alerts has no size limit by default. If the anomaly detector fires faster than the frontend consumes events (e.g., all sensors breach simultaneously), the queue grows unbounded. For the demo: `asyncio.Queue(maxsize=100)` with `put_nowait` + drop-oldest policy is sufficient. [unverified: not load-tested].

6. **Streaming response buffering by judge's local setup.** If the judge runs the frontend via a reverse proxy or some corporate network tool that buffers HTTP responses, SSE events will appear batched rather than streaming. The `X-Accel-Buffering: no` header handles Nginx specifically; `fastapi.sse` sets it automatically. But other proxies (Caddy, Apache without configuration) may still buffer. Mitigation: document in the README that the demo runs best direct to `http://localhost:8000`. [risk: low for local demo, medium for any proxied judge environment].

---

## Summary Table

| Decision | Choice | Version |
|---|---|---|
| Web framework | FastAPI | 0.136.3 |
| ASGI server | uvicorn[standard] | 0.34.x |
| SSE streaming | fastapi.sse native | (built-in 0.135.0+) |
| Scheduler | APScheduler AsyncIOScheduler | 3.11.x (pinned) |
| Retry logic | tenacity async | 9.x |
| Circuit breaker | pybreaker | 1.x |
| Structured logging | structlog + asgi-correlation-id | 24.x + 4.x |
| Async HTTP client | httpx | 0.27.x |
| Data validation | pydantic v2 | bundled |
| Install method | pip only, no Docker | — |
