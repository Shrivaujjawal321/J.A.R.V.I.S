# wizard.backend

FastAPI 0.136 backend service for the Maintenance Wizard.
Real-time SSE alerting, WRPS risk scoring, chat endpoint with graph_placeholder stub.

## Files

| File | Purpose |
|---|---|
| `app.py` | FastAPI app factory, lifespan, all route handlers |
| `schemas.py` | API-level request/response Pydantic models (ErrorEnvelope, ChatRequest, etc.) |
| `middleware.py` | CorrelationIdMiddleware, structlog config, AsyncCircuitBreaker |
| `alerting.py` | AlertBroadcaster (per-client SSE queues), APScheduler evaluator, demo EAF-04 trigger |
| `wrps.py` | WRPS 4+1 factor risk scoring engine, LLM narrative, weight feedback |
| `graph_placeholder.py` | Typed stub returning MaintenanceRecommendation (replace with real graph) |
| `smoke_backend.py` | Self-contained smoke test |

## Endpoints

```
POST /v1/chat              → ChatResponse (sync, graph_placeholder)
POST /v1/chat/stream       → SSE EventSourceResponse (streaming, graph_placeholder)
GET  /v1/alerts/stream     → SSE persistent stream (AlertBroadcaster fan-out)
GET  /v1/alerts            → AlertListResponse (cursor-paginated history)
POST /v1/alerts/{id}/ack   → AlertAckResponse
GET  /v1/sensor/state      → SensorStateResponse (all assets snapshot)
POST /v1/feedback          → FeedbackResponse (WRPS EMA weight update)
GET  /v1/session/{id}/state → SessionStateResponse (LangGraph checkpoint)
GET  /v1/health            → HealthResponse
GET  /docs                 → Swagger UI
```

## Alert Pipeline

```
APScheduler (5s)
  → evaluate_alerts()
    → SensorSummary + AnomalyAlert from wizard.db
    → DedupRegistry cooldown check
    → persist AnomalyAlert row
    → AlertBroadcaster.broadcast(AlertEvent)
      → per-client asyncio.Queue (max 100 items)
        → SSE EventSourceResponse drains queue
          → browser EventSource API
```

Demo EAF-04 CRITICAL alert fires at T+90s from server start (scripted wow moment).

## WRPS Engine

```
score_maintenance_priority(asset_id: str) -> RiskScore   # sync, for LangGraph tool
score_maintenance_priority_async(asset_id: str) -> RiskScore  # async, for FastAPI routes

4+1 weighted factors:
  F1 process_criticality  (0.35) → AssetProfile.criticality_tier
  F2 delay_severity       (0.25) → FaultLog.severity (proxy for delay_hours)
  F3 spare_availability   (0.20) → SparePart.stock_qty / min_stock_qty
  F4 lead_time            (0.12) → SparePart.lead_time_days
  F5 ml_signal            (0.08) → SensorSummary.rul_days_p50 + AnomalyAlert.risk_level

Weights persist to data/feedback/wrps_weights.json.
EMA update on every POST /v1/feedback with corrected_risk_level.
```

## Agentic-Core Integration Point

`graph_placeholder.py` exports two functions with fixed signatures:

```python
async def run_graph(request: ChatRequest) -> tuple[MaintenanceRecommendation, list[dict]]:
    ...

async def stream_graph(request: ChatRequest) -> AsyncGenerator[dict, None]:
    ...
```

The agentic-core wave replaces the bodies of these two functions with real
`graph.astream()` calls. `app.py` never changes — it always imports and calls
`run_graph` / `stream_graph`.

## Running

```bash
# Development
cd maintenance-wizard
WIZARD_TESTING=1 python -m wizard.backend.smoke_backend

# Server
uvicorn wizard.backend.app:app --host 127.0.0.1 --port 8000

# Via Makefile
make run
```
