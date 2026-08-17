# Maintenance Wizard

**Agentic AI Maintenance Decision-Support for Steel Plants**
Tata Steel AI Hackathon 2026 · Round 2 · Solo submission

> An agentic maintenance co-pilot that fires a full, source-cited maintenance plan *before* the engineer asks — because the best recommendation is the one that arrives before the failure, not after.

---

## 5-Command Install

```bash
# 1. Clone and enter the repository
git clone <repo-url> maintenance-wizard && cd maintenance-wizard

# 2. Create venv, install CPU-only PyTorch, install the package in editable mode
make setup

# 3. Configure environment (set GEMINI_API_KEY at minimum; leave blank for deterministic fallback)
cp .env.example .env && nano .env

# 4. Generate synthetic data, train 46 ML model artifacts, ingest 1,186 RAG chunks
make gen-data && make train && make ingest

# 5. Launch backend (port 8000) and Streamlit UI (port 8501)
make run
```

Open `http://localhost:8501` in your browser.

At the 90-second mark the system auto-fires a CRITICAL alert for EAF-04 with zero user input. This is the primary proof of the "agentic" claim.

### What `make setup` does

```bash
python3 -m venv .venv
.venv/bin/pip install --upgrade pip setuptools wheel
.venv/bin/pip install torch==2.3.1+cpu --index-url https://download.pytorch.org/whl/cpu
.venv/bin/pip install -e ".[dev]"
```

CPU-only PyTorch is installed first because the main `requirements.txt` pins `numpy<2`, and the CPU wheel must be resolved before numpy's upper-bound constraint is evaluated.

### Offline / no-API-key mode

```bash
# Install Ollama (one-time): https://ollama.com/download
ollama pull qwen2.5:3b

# In .env:
LLM_PROVIDER=ollama
LLM_MODEL_PRIMARY=qwen2.5:3b

make run
```

All Pydantic models, citation arrays, and agent traces are identical in offline mode. Only narrative text is deterministic-template rather than LLM-generated.

---

## Quickstart Demo Flow

After `make run`:

1. Open `http://localhost:8501` → Chat page.
2. **Wait 90 seconds** — a CRITICAL alert for EAF-04 fires automatically. No input required.
   - The sidebar ticker shows: `Prevented Downtime Cost ₹8,55,000`.
   - The Alerts page shows the full alert with WRPS score, RUL estimate, and spare-parts warning.
3. **Type a query** — e.g. `What is the root cause for EAF-04?`
   - The response streams agent-step by agent-step (Diagnosis → RCA → RUL → Prioritization → Plan → Report).
   - Expand the `Sources` expander to see the full traceable chain: sensor → SOP section → incident → agent step.
4. **Inject a fault** — Open the Settings page → Demo Controls → click `Inject Fault (BF-FAN-A)`.
   - A HIGH alert fires within 5 seconds.
5. **Test the feedback loop** — Click thumbs-down on any response → type a correction → re-query.
   - The next response shows `[ENGINEER CORRECTION APPLIED]` badge at the top.

---

## Architecture Overview

```
Engineer (NL, multi-turn)       Sensor Stream (playback)
         │                              │
  Streamlit 1.58               APScheduler 5 s tick
  (5 pages, SSE streaming)      proactive evaluator
         │ httpx.Client (sync)          │
         └──────────── FastAPI 0.136.3 ──┘
                            │
               LangGraph 1.2.4 Supervisor
         (Plan → Execute(ReAct) → Validate)
              │   │   │   │   │   │
           DIAG RCA RUL RISK PLAN REPORT
                        │
              ┌──────────────────────┐
           LanceDB          NetworkX FMEA
           (RAG hybrid)     (290 nodes)
           1,186 chunks      489 edges
              │                  │
           SQLite wizard.db  (shared)
           46 ML model artifacts
```

See `docs/ARCHITECTURE.md` for the full 8-section design document including the real compiled LangGraph mermaid topology, complete data flow, and per-model design rationale.

---

## Stack Summary

| Layer | Library | Installed Version |
|---|---|---|
| Orchestration | langgraph | 1.2.4 |
| Schema + validation | pydantic | 2.13.4 |
| Persistence | sqlmodel | 0.0.38 |
| Vector store | lancedb (hybrid dense+BM25) | 0.33.0 |
| Embeddings | sentence-transformers (bge-small ONNX) | 5.5.1 |
| Reranker | flashrank (ms-marco-MiniLM) | 0.2.10 |
| Knowledge graph | networkx | 3.6.1 |
| RUL | lifelines (WeibullAFT) | 0.30.3 |
| Anomaly | scikit-learn (IsolationForest) | 1.9.0 |
| Anomaly | torch (LSTM-AE, CPU) | 2.3.1+cpu |
| Anomaly | river (Half-Space Trees) | 0.21.2 |
| Failure prediction | lightgbm (calibrated 4-class) | 4.6.0 |
| Feature engineering | tsfresh | 0.21.2 |
| RCA | dowhy (GCM causal attribution) | 0.12 |
| LLM gateway | litellm | 1.87.1 |
| Backend | fastapi | 0.136.3 |
| Scheduler | apscheduler | 3.11.2 |
| Logging | structlog | 26.1.0 |
| Frontend | streamlit | 1.58.0 |
| Charts | plotly | 6.8.0 |

All layers installable via `pip install -e .` — no Docker, no GPU required.

---

## Requirements Mapping Table

The official problem statement defines 7 Functional Requirements (FR1–FR7). Each maps directly to one or more implementation components.

| FR | Requirement (verbatim from §6) | Where implemented |
|---|---|---|
| **FR1** | Contextual reasoning using LLMs/SLMs — integrate LLM/SLM; extra merit for domain-specific fine-tune | `wizard/agents/nodes.py`: `_llm_complete()` calls LiteLLM → Gemini 2.5 Flash (primary) or Qwen2.5-3B Ollama (fallback). Every node uses LLM for structured output with deterministic fallback. Domain fine-tune (Qwen2.5-3B QLoRA on synthetic corpus) is the stretch goal documented in `pyproject.toml [project.optional-dependencies.finetune]`. |
| **FR2** | Knowledge integration — reason over manuals, SOPs, historical records, failure reports, operational logs | `wizard/rag/`: LanceDB 1,186-chunk hybrid retrieval (dense + BM25 + SQL prefilter) over synthetic KB (500 docs: manuals, SOPs, failure reports, spare-parts). `wizard/knowledge/`: 290-node NetworkX FMEA ontology used by RCA Layer-1. Both are populated by `make gen-data`. |
| **FR3** | Natural language interaction — NL queries + multi-turn context-aware conversation | `wizard/ui/pages/01_Chat.py`: multi-turn Streamlit chat with session state. `wizard/agents/graph.py`: `AsyncSqliteSaver` checkpoints `MaintenanceState` per `session_id` — subsequent turns resume from the last checkpoint, preserving the full conversation context for time-travel debugging. |
| **FR4** | Explainable recommendations — outputs traceable to input data, records, rules, and docs | Every `DiagnosisReport`, `RCAResult`, and `MaintenanceRecommendation` carries `cited_sources: list[str]` (chunk IDs). The Streamlit Chat page renders these as a collapsible `st.expander` showing sensor → SOP§ → incident → agent-step lineage. `report_node` appends `[N]` citation markers to the narrative. |
| **FR5** | Abnormality detection and failure prediction — dynamic anomaly detection, early warning, failure prediction | `wizard/ml/anomaly_detector.py`: ensemble (0.4×IsolationForest + 0.4×LSTM-AE + 0.2×River HST). `wizard/ml/rul_estimator.py`: WeibullAFTFitter P10/P50/P90. `wizard/ml/failure_predictor.py`: LightGBM calibrated 4-class. `wizard/backend/alerting.py`: APScheduler 5 s evaluator with severity-tiered cooldown. |
| **FR6** | Feedback-driven improvement — corrections/confirmations improve future recommendations | `wizard/backend/wrps.py`: `apply_feedback_to_weights()` — EMA update (`w_new = 0.9 × w_old + 0.1 × gradient`) persisted to `data/feedback/wrps_weights.json`. `wizard/ml/rul_estimator.py`: `apply_engineer_correction()` — Bayesian blend (`0.7 × model + 0.3 × engineer`) persisted to `data/feedback/rul_corrections.jsonl`, replayed on startup. `POST /v1/feedback` endpoint wires both. |
| **FR7** | Real-time alerting capability — real-time abnormal alert reports + user-specific notifications | `wizard/backend/alerting.py`: `AlertBroadcaster` fan-out to per-client `asyncio.Queue`. `GET /v1/alerts/stream`: native FastAPI `EventSourceResponse`. Streamlit receives via `st.fragment(run_every=5)` polling. Cooldown registry prevents alert spam (CRITICAL: 120 s, HIGH: 300 s). Demo EAF-04 trigger at t=90 s is the scripted proof. |

---

## Project Layout

```
maintenance-wizard/
├── wizard/
│   ├── core/
│   │   ├── schemas.py    # single source of truth — all Pydantic + SQLModel entities
│   │   ├── config.py     # pydantic-settings .env loader
│   │   └── db.py         # SQLite WAL init, get_session(), session_scope()
│   ├── data/
│   │   ├── gen_synthetic.py  # ISO 14224 ontology → 500 synthetic KB docs
│   │   ├── gen_datasets.py   # NASA C-MAPSS + AI4I 2020 loaders + steel framing
│   │   └── dataset_framing.py # cosmetic column aliasing
│   ├── knowledge/
│   │   ├── fmea_graph.py     # builds 290-node NetworkX FMEA ontology
│   │   ├── ontology.py       # ISO 14224 seed ontology
│   │   └── build_kg.py       # entrypoint: python wizard/knowledge/build_kg.py
│   ├── rag/
│   │   ├── embedder.py       # BAAI/bge-small-en-v1.5 ONNX embedder
│   │   ├── store.py          # LanceDB table create/upsert
│   │   ├── ingestion.py      # chunk → embed → upsert pipeline
│   │   ├── retriever.py      # hybrid search + HyDE + FlashRank rerank
│   │   ├── tools.py          # LangGraph tool wrappers: rag_retrieve, rag_search_*
│   │   └── faithfulness.py   # NLI entailment gate (nli-deberta-v3-small, optional)
│   ├── ml/
│   │   ├── feature_utils.py  # shared sensor vector builder + degradation index
│   │   ├── registry.py       # ModelRegistry — loads joblib artifacts on demand
│   │   ├── rul_estimator.py  # WeibullAFTFitter inference + Bayesian correction
│   │   ├── anomaly_detector.py # IF + LSTM-AE + River HST ensemble
│   │   ├── failure_predictor.py # LightGBM 4-class + tsfresh features
│   │   ├── rca_engine.py     # 3-layer RCA (NetworkX + DoWhy + LLM)
│   │   ├── train_rul.py      # offline training: WeibullAFT + scalers + centroids
│   │   ├── train_anomaly.py  # offline training: IF + LSTM-AE + River HST thresholds
│   │   └── train_failure.py  # offline training: LightGBM + isotonic calibration
│   ├── agents/
│   │   ├── graph.py          # LangGraph StateGraph + AsyncSqliteSaver + public API
│   │   ├── nodes.py          # 6 domain nodes + supervisor_route + fallback helpers
│   │   ├── tools.py          # tool wrappers consumed by nodes
│   │   └── alerting.py       # WRPS + alert graph integration tools
│   ├── backend/
│   │   ├── app.py            # FastAPI application (10 endpoints + lifespan)
│   │   ├── alerting.py       # AlertBroadcaster + DedupRegistry + APScheduler jobs
│   │   ├── wrps.py           # WRPS 4+1 factor engine + EMA weight update
│   │   ├── schemas.py        # backend-only request/response schemas
│   │   ├── middleware.py     # CorrelationIdMiddleware + circuit breaker + structlog
│   │   └── demo.py           # /demo router (inject_fault, reset_demo, cost_ticker)
│   └── ui/
│       ├── app.py            # Streamlit entry point (multi-page layout)
│       ├── _http.py          # httpx.Client sync wrapper for all API calls
│       ├── _demo_seed.py     # pre-seed demo data for cold-start presentation
│       └── pages/
│           ├── 01_Chat.py    # multi-turn chat with streaming + citation expander
│           ├── 02_Dashboard.py # sensor gauges + health heatmap + cost ticker
│           ├── 03_Alerts.py  # SSE alert feed + acknowledge + WRPS breakdown
│           ├── 04_Logbook.py # automatic digital logbook (maintenance records)
│           └── 05_Settings.py # WRPS weight sliders + demo controls + LLM config
├── data/
│   ├── wizard.db          # SQLite entity store (created by make gen-data)
│   ├── lancedb/           # LanceDB vector store (1,186 chunks after make ingest)
│   ├── models/            # 46 trained model artifacts (after make train)
│   ├── kg/                # FMEA graph JSON export
│   ├── synthetic/         # generated KB documents
│   ├── feedback/          # wrps_weights.json + rul_corrections.jsonl
│   └── demo/              # cost_events.jsonl + session_summary.json
├── docs/
│   ├── ARCHITECTURE.md    # 8-section design document (this submission's primary doc)
│   ├── BUSINESS_IMPACT.md # Tata Steel KPI-anchored ROI analysis
│   └── SAMPLE_IO.md       # 3 complete query → response pairs with citation JSON
├── tests/
│   ├── conftest.py
│   ├── test_db.py
│   └── test_schemas.py
├── scripts/
│   └── train_ml_models.py # convenience wrapper for make train
├── Makefile
├── pyproject.toml
├── requirements.txt
└── .env.example
```

---

## Key Demo Moments

| Moment | What happens | Evaluation axis |
|---|---|---|
| **t=90 s: proactive CRITICAL alert** | APScheduler fires EAF-04 CRITICAL with zero user input. Full plan in ~30 s. | Agentic AI use (CR2), Technical implementation (CR3) |
| **Live Cost-Avoidance Ticker** | Sidebar ₹ metric accumulates on every confirmed CRITICAL/HIGH event | Business impact (CR6) |
| **Traceable Diagnosis Chain** | Every answer expands to sensor → SOP§ → incident → agent step | Explainability (CR3, CR4) |
| **Spare-parts warning** | "SKF-6310-2RS1 out of stock, 14-day lead time — ORDER NOW" | Real-world applicability (CR4) |
| **Feedback in one turn** | Thumbs-down → correction → `[ENGINEER CORRECTION APPLIED]` badge | Technical innovation (CR3) |

---

## Business Impact

Anchored to Tata Steel's own published results:

- **15% unplanned downtime reduction** on rolling mills
- **₹45 Crore/year** savings per blast furnace (coke reduction AI)
- **₹1.4 billion** total AI-enabled savings
- **40% maintenance planning time** reduction at Jamshedpur

Projected for a 10-equipment-line plant: **₹1.98 Crore/year** in prevented downtime + ₹28.8 Lakh/year in planning efficiency savings.

See `docs/BUSINESS_IMPACT.md` for the full calculation with sources.

---

## Screen Recording

[PLACEHOLDER — YouTube unlisted link: to be added after recording]

Duration: 3–4 minutes · Resolution: 1920×1080 · Narrated

---

## License

MIT License. See `LICENSE`.

IP remains with the author per HackerEarth competition terms.
