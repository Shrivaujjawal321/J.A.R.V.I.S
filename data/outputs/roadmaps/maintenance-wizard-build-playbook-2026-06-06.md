# Maintenance Wizard — Solo 9-Day Build Playbook
**Tata Steel AI Hackathon 2026 | Round 2 | Deadline: 2026-06-15 23:59 IST**

---

## Conflict Resolutions (stated upfront)

| Conflict | Resolution |
|---|---|
| Vector store: ChromaDB vs Qdrant | **ChromaDB in-process** (no Docker dep, zero judge friction) |
| Embedding: BGE-M3 vs all-MiniLM-L6-v2 | **all-MiniLM-L6-v2** (CPU-safe, no GPU required, fast; BGE-M3 only if GPU confirmed on demo machine) |
| Frontend: Streamlit vs React | **Streamlit 1.35 only** (React costs 2+ days, zero judging upside) |
| SSE vs WebSocket for alerts | **SSE** (works over HTTP/1.1, no upgrade, Streamlit-compatible) |
| Docker Compose: include vs exclude | **Exclude** (adds judge setup friction; Makefile + venv is sufficient) |
| LLM provider primary | **Anthropic claude-sonnet-4-6** (already running model); Gemini Flash 2.0 free-tier for intent; Ollama llama3.2:3b offline fallback |
| Fine-tuned domain SLM | **Cut** (L effort, 0 reliable ROI in 9 days, document as planned enhancement) |
| Critic/verifier pass: sync vs async | **Async only** — stream answer first, append verification badge post-render; never block response |

---

## Phase Timeline Overview

| Phase | Name | Days | Effort |
|---|---|---|---|
| 0 | Foundation | Day 1 morning (~3h) | S |
| 1 | Synthetic Data | Day 1 afternoon–Day 2 (~10h) | M |
| 2 | Knowledge/RAG Layer | Day 2–3 (~12h) | M |
| 3 | Predictive ML Models | Day 3 (~6h) | M |
| 4 | Agentic Core | Day 3–5 (~20h) | L |
| 5 | Alerting Engine | Day 5 (~6h) | M |
| 6 | UX/Dashboard | Day 5–6 (~14h) | M |
| 7 | Robustness & Eval | Day 7 (~8h) | M |
| 8 | Demo & Submission | Day 8–9 (~12h) | M |

---

## PHASE 0 — Foundation
*Day 1 morning. Do this before writing a single agent or data file.*

### Step 0.1 — Problem narrative + judge coverage matrix
**MUST-HAVE**

**What:** Write a 200-word problem framing document anchored to Tata Steel's own published KPIs (22% downtime reduction via Asset Sphere, 1:10 cost-benefit ratio on their 800-model program, INR 1.4B cumulative savings). Narrative: maintenance engineers carry fragmented tribal knowledge across manuals, fault logs, and shift handovers; one unplanned EAF outage costs INR 2–5 crore/hour. This framing goes in `README.md`, `docs/ARCHITECTURE.md` lede, and the first 20s of the demo video. Also create `docs/JUDGE_MATRIX.md`: a table with rows = 13 judging axes (6 email + 7 webinar), columns = features/screens, cells = Y/N + one-line demo moment. Any axis with zero Y cells triggers a build task. Any feature column with fewer than 2 Y cells gets cut.

**Judging axes:** Problem Understanding & Approach, Business Impact & Feasibility

**Tech:** Markdown only.

**Effort:** S

---

### Step 0.2 — Error envelope contract + project scaffold
**MUST-HAVE**

**What:** Before any LLM or agent code, define a typed `AgentResult` envelope in `wizard/core/envelope.py`: `{status: ok|error|degraded, data, error_code: str, message: str, latency_ms: int, tokens_used: int, source_refs: list[SourceRef], fallback_used: bool}`. Register a global FastAPI exception handler that catches all unhandled exceptions and returns this envelope as JSON — never a raw Python traceback. Create the full directory scaffold: `wizard/{core,data,rag,ml,graph,alerts,feedback,reports,api,ui}/`.

**Judging axes:** DOESN'T-BREAK, NO-ERRORS

**Tech:** Python 3.12, FastAPI 0.111, Pydantic v2, structlog 24.x

**Effort:** S

---

### Step 0.3 — Equipment taxonomy YAML — single source of truth
**MUST-HAVE**

**What:** Write `data/synthetic/equipment_taxonomy.yaml`. Define exactly 6 equipment types: (1) HSM finishing-stand gearbox, (2) Blast Furnace blower, (3) Continuous Caster withdrawal-roll bearing, (4) EAF electrode assembly, (5) Raw-material conveyor drive, (6) Hydraulic descaling pump. For each: canonical `equipment_id`, 3–4 failure modes, characteristic sensor signatures (which sensors, drift direction, rate), MTTF (days), degradation shape (linear/exponential/sudden), and canonical fault codes (e.g. `HSM-GB-VIB-HH`). This YAML is the master truth — every generator, RAG document, and model must reference it. Run a validation script that asserts consistency before any downstream step.

**Judging axes:** ACCURATE, SMOOTH, DOESN'T-BREAK

**Tech:** YAML, Pydantic v2 for schema validation.

**Effort:** S

---

## PHASE 1 — Synthetic Data
*Day 1 afternoon – Day 2. Critical path. Nothing downstream works without this.*

### Step 1.1 — Sensor time-series generator with injected fault episodes
**MUST-HAVE**

**What:** `data/synthetic/generate_sensor_data.py`. 12 months of hourly readings per equipment unit. Sensors per type: vibration RMS (mm/s), bearing temperature (°C), lube-oil differential pressure (bar), motor current (A), acoustic emission (dB). Model each with: (a) healthy Gaussian baseline, (b) degradation ramp starting at seeded `t_fault` (numpy `random_state=42`), (c) single-point spike anomalies, (d) failure at `t_fail = t_fault + TTF` drawn from `scipy.stats.weibull_min(shape=1.8, scale=MTTF)`. Inject at least 3 fault episodes per unit. Output: Parquet files in `data/synthetic/sensor_timeseries/` partitioned by `equipment_id`. Seed one unit so its RUL crosses 72h exactly 90 seconds into the demo — this triggers the proactive alert on cue (Step 4.7). Commit generated files to repo so judges never need to re-run.

**Judging axes:** ACCURATE, SMOOTH, Abnormality detection & failure prediction

**Tech:** numpy 1.26, scipy 1.13, pandas 2.2, pyarrow/Parquet, matplotlib (sanity check only)

**Effort:** M

---

### Step 1.2 — Event log + spare parts catalog
**MUST-HAVE**

**What:** `data/synthetic/generate_event_logs.py`. Produces ~500 structured events across all units: `{equipment_id, timestamp, event_type: ALARM|TRIP|MAINTENANCE|INSPECTION|REPAIR, fault_code, duration_hours, shift_team, operator_id, downstream_impact_tons}`. Every `fault_code` is validated against `equipment_taxonomy.yaml`. Also generates `spare_parts_catalog.csv`: 50 parts with `part_id, equipment_id, part_name, unit_cost_INR, lead_time_days (7–120), current_stock_qty, reorder_point`. Realistic Indian industrial procurement: critical spare lead times 45–90 days, common consumables 7–14 days.

**Judging axes:** ACCURATE, EASY-TO-USE, Scalability & Real-World Applicability

**Tech:** Python, Faker 24.x, pandas, numpy

**Effort:** S

---

### Step 1.3 — RAG knowledge corpus generator
**MUST-HAVE**

**What:** Use Claude Haiku (API) with a strict system prompt that injects the taxonomy YAML as a constraint block: "You are generating a maintenance document. The following fault codes and thresholds are CANONICAL — do not invent others." Generate: 6 equipment manuals (5–8 pages each, Markdown, fault-code tables, operating limits, maintenance intervals), 8 SOPs (gearbox oil change, bearing replacement, electrode swap, lockout/tagout, lubrication schedule, cooling system flush, alignment check, emergency shutdown), 8 incident reports (RCA format: date, equipment, fault sequence, 5-Why, corrective action — each cross-referencing a real event from the event log), 6 last-inspection maintenance records. Frontmatter on every file: `equipment_id, doc_type, date`. Post-generation validation: assert no doc introduces a fault code absent from the taxonomy YAML. Store under `data/rag_corpus/`.

**Judging axes:** ACCURATE, DOESN'T-BREAK, Knowledge Integration

**Tech:** Anthropic API (claude-haiku), PyYAML, Markdown files

**Effort:** M

---

## PHASE 2 — Knowledge / RAG Layer
*Day 2–3. Build and index before wiring to agents.*

### Step 2.1 — Structure-aware chunking pipeline
**MUST-HAVE**

**What:** `wizard/rag/chunker.py`. Chunking rules by doc type: manuals/SOPs chunk at Markdown H2/H3 boundaries (400–600 tokens), preserving section titles as context; incident reports and maintenance records are one record = one chunk (atomic units, no overlap); sensor summaries group by equipment + 1h window. Every chunk carries metadata: `chunk_id (UUID), parent_doc_id, doc_type, equipment_id, section_title, token_count`. Validate token counts with `tiktoken` (cl100k_base) — reject any chunk > 800 tokens. Overlap (64 tokens) for manual/SOP chunks only, none for structured records. Output: `data/index/chunks.jsonl` with Pydantic `ChunkManifest` schema.

**Judging axes:** ACCURATE, FAST, EFFICIENT, Knowledge Integration

**Tech:** LangChain `MarkdownHeaderTextSplitter`, custom JSON record splitter, tiktoken, Pydantic v2

**Effort:** S

---

### Step 2.2 — Embed corpus + build dual index (ChromaDB dense + BM25)
**MUST-HAVE**

**What:** `wizard/rag/indexer.py`. Embed all chunks with `sentence-transformers all-MiniLM-L6-v2` (local, CPU, ~50ms per encode). Store dense vectors in ChromaDB (in-process, `persistent=True, path='./data/chroma_db'`). Build BM25 index (`rank_bm25 BM25Okapi`) over the same chunks stored as a Python pickle. Pre-warm the ChromaDB collection at server startup with a dummy embed call so the first judge query is never cold. Commit the `data/chroma_db/` and `data/bm25_index.pkl` artifacts to the repo — judges never rebuild the index.

**Judging axes:** FAST, EFFICIENT, ACCURATE, DOESN'T-BREAK

**Tech:** sentence-transformers 3.x `all-MiniLM-L6-v2`, chromadb 0.5.x (in-process), rank_bm25 0.2.2

**Effort:** M

---

### Step 2.3 — Hybrid retrieval with RRF fusion + cross-encoder reranker
**NICE-TO-HAVE** *(cut if Day 3 is at risk — plain hybrid RRF without reranker is acceptable)*

**What:** `wizard/rag/retriever.py`. At query time: run BM25 (top-50) and ChromaDB dense (top-50) in parallel. Merge via Reciprocal Rank Fusion (RRF, k=60, ~15 lines Python). Then pass top-20 candidates to a `CrossEncoder` (`BAAI/bge-reranker-base`, 65M params, CPU-safe, ~100ms for 20 pairs) and trim to top-8. Return `list[RetrievedDoc]` with `{chunk_id, doc_title, section, equipment_id, chunk_text, rrf_score, reranker_score}`. This is the final interface for all agents.

**Judging axes:** ACCURATE, Explainable Recommendations, Technical Implementation & Innovation

**Tech:** rank_bm25, sentence-transformers CrossEncoder, chromadb

**Effort:** S

---

### Step 2.4 — Citation-grounded prompt architecture with structured output
**MUST-HAVE**

**What:** `wizard/rag/prompts.py`. System prompt structure (cached prefix, ~800 tokens stable): role + equipment registry + 7 mandatory-requirement map + citation rule ("every factual claim must reference at least one [SOURCE-N]; if no source supports a claim, say so explicitly — do not fabricate"). Retrieved chunks formatted as numbered `[SOURCE-1]` through `[SOURCE-N]` blocks with metadata header (doc_name, section, equipment_id). Structured output via Pydantic `MaintenanceAnswer`: `{answer_text, recommendations: list[Recommendation], citations: list[Citation], confidence: float, risk_level: Literal['low','medium','high','critical']}`. Citation schema: `{chunk_id, doc_name, section, equipment_id, relevant_excerpt: str ≤100 chars}`. Apply `cache_control: {type: 'ephemeral'}` on the system prompt block.

**Judging axes:** ACCURATE, NO-ERRORS, Explainable Recommendations, SMOOTH

**Tech:** Anthropic SDK 0.26+ with `cache_control`, Pydantic v2, structured tool_use output

**Effort:** M

---

## PHASE 3 — Predictive ML Models
*Day 3. Pre-train and commit artifacts — never train at demo time.*

### Step 3.1 — Anomaly detection: IsolationForest + SHAP explainability
**MUST-HAVE**

**What:** `wizard/ml/anomaly_detector.py`. Per-equipment-type `IsolationForest` (`n_estimators=200, contamination=0.05`, sklearn 1.5). Feature engineering on sensor windows: `rolling_mean_temp_60s, rolling_std_vibration_60s, current_A, delta_temp_1h, cumulative_runtime_h, equipment_age_days`. SHAP `TreeExplainer` for `feature_importance_top3` per prediction. Output: `AnomalyResult(equipment_id, anomaly_score: float, is_anomaly: bool, feature_importance_top3: list[str])`. Train on healthy-only data windows (pre `t_fault`) from the synthetic Parquet. Persist with joblib to `data/models/anomaly_{equipment_type}.pkl`. Load as singleton at server startup.

**Judging axes:** ACCURATE, FAST, EFFICIENT, Abnormality detection & failure prediction

**Tech:** scikit-learn 1.5 IsolationForest, shap 0.45 TreeExplainer, joblib 1.4

**Effort:** M

---

### Step 3.2 — RUL estimator: Weibull proportional hazards + degradation index
**MUST-HAVE**

**What:** `wizard/ml/rul_estimator.py`. Two-stage per equipment type: Stage 1 = `lifelines WeibullAFTFitter` trained on synthetic fault episode records (time_to_failure, sensor_features_at_onset). Stage 2 = degradation index correction: compute normalized distance from healthy centroid in sensor space, adjust baseline RUL estimate. Output: `RULResult(equipment_id, rul_days_p50, rul_days_p10, rul_days_p90, failure_probability_30d, risk_class: LOW|MEDIUM|HIGH|CRITICAL, confidence_pct)`. Risk class thresholds: >90d = LOW, 30–90d = MEDIUM, 7–30d = HIGH, <7d = CRITICAL. Train one model per equipment type (6 models). Persist with joblib.

**Judging axes:** ACCURATE, FAST, EASY-TO-USE, Abnormality detection & failure prediction

**Tech:** lifelines 0.29 WeibullAFTFitter, numpy, scipy, sklearn StandardScaler, joblib

**Effort:** S

---

### Step 3.3 — Train all models offline, commit artifacts
**MUST-HAVE**

**What:** `scripts/train_models.py` — single script that trains all 6 IsolationForest + 6 Weibull models, validates outputs (assert non-null predictions on 3 test rows), and writes all 12 joblib files to `data/models/`. Commit these artifacts to the repo. `make train` in the Makefile runs this script. The demo NEVER triggers retraining — models load from disk as singletons.

**Judging axes:** FAST, SMOOTH, DOESN'T-BREAK

**Tech:** joblib, Python script, Makefile target

**Effort:** S

---

## PHASE 4 — Agentic Core
*Day 3–5. The largest phase. Parallel-build nodes after graph scaffold is set.*

### Step 4.1 — LangGraph StateGraph + typed AgentState schema
**MUST-HAVE**

**What:** `wizard/graph/state.py` — `AgentState` TypedDict with all graph fields: `session_id, turn_id, equipment_id, raw_query, intent, sensor_snapshot, retrieved_docs, diagnosis_result, rul_result, rca_result, maintenance_plan, active_alerts, feedback_log, final_response, citations, confidence, error`. Every sub-type is a Pydantic v2 `BaseModel`. Each node owns exactly one state slice (prevents race conditions under `Send()` parallel dispatch). `wizard/graph/graph.py` — compile with `checkpointer = SqliteSaver.from_conn_string('data/sessions.db')`. Every node write validated by Pydantic at write time.

**Judging axes:** ACCURATE, NO-ERRORS, Technical Implementation & Innovation

**Tech:** langgraph 0.2.x, langgraph-checkpoint-sqlite, Pydantic v2, Python 3.12 TypedDict

**Effort:** S

---

### Step 4.2 — Supervisor + 6 specialist nodes (the agentic graph)
**MUST-HAVE**

**What:** `wizard/graph/nodes.py`. Build order: (1) `IntentClassifierNode` — Gemini Flash 2.0 free-tier (or Ollama llama3.2:3b offline fallback), 7-class intent, <200 token prompt, cached system prefix; (2) `RAGNode` — calls `retriever.query_rag()`, writes `retrieved_docs + citations`, no LLM; (3) `MLNode` — calls `AnomalyDetector.predict()` + `RULEstimator.predict()`, no LLM; (4) `DiagnosisNode` — claude-sonnet-4-6 with cached system prompt (~800 tokens), structured `DiagnosisResult` output; (5) `RCANode` — same pattern, outputs 5-Why chain grounded in retrieved incident reports; (6) `MaintenancePlannerNode` — takes `DiagnosisResult + spare_parts_catalog + maintenance_records`, outputs `MaintenancePlan` with numbered repair steps + parts checklist + urgency score formula: `0.4*(1-RUL_norm) + 0.3*anomaly_score_norm + 0.3*production_impact_norm`; (7) `AlertNode` — rule-based, no LLM; (8) `FeedbackNode` — writes to ChromaDB + feedback log. Supervisor uses conditional edges routing on `state.intent`. `RAGNode + MLNode` always dispatch in parallel via `Send()` API. Nodes 4–6 fire sequentially only for complex diagnostic queries. `max_iterations=10` hard cap.

**Judging axes:** FAST, EFFICIENT, ACCURATE, NO-ERRORS, Effective Use of Agentic-AI Frameworks, Technical Implementation & Innovation

**Tech:** langgraph 0.2.x StateGraph + Send() API, anthropic SDK 0.26+, google-generativeai 0.7, ollama as fallback

**Effort:** L

---

### Step 4.3 — Multi-turn session memory via SqliteSaver + FastAPI chat endpoint
**MUST-HAVE**

**What:** `wizard/api/server.py`. `POST /chat` accepts `{session_id: UUID, message: str, equipment_id: str, sensor_snapshot?: dict}`. Graph compiled with SqliteSaver — `graph.stream(input, config={'configurable': {'thread_id': session_id}})` automatically persists and restores `AgentState`. If `thread_id` exists, conversation resumes from last state including previous diagnoses and feedback. `GET /session/{session_id}/history` returns full turn list. Run with `uvicorn --workers 1` for demo (SqliteSaver single-writer pattern). `GET /health` validates all 6 datasets readable and all 12 joblib models loadable before accepting requests.

**Judging axes:** DOESN'T-BREAK, Natural-language multi-turn interaction, SMOOTH, Scalability & Real-World Applicability

**Tech:** langgraph-checkpoint-sqlite, FastAPI 0.111, uvicorn 0.29, python-ulid for session IDs

**Effort:** S

---

### Step 4.4 — Async hallucination verifier/critic pass
**NICE-TO-HAVE** *(cut if Phase 4 is running over; citations alone satisfy req 4)*

**What:** `wizard/graph/verifier.py`. After primary LLM produces `MaintenanceAnswer`, fire a background Haiku 4.x verifier that checks each recommendation against its cited chunks. Verifier prompt: `{claim, source_excerpt} → {supported: bool, confidence: float, issue: str|null}`. If any claim `supported=False`, tag it `[UNVERIFIED]` in the UI response — never block or re-generate. Hard timeout 3s. Log to `data/logs/verifier.jsonl`. Use `asyncio.gather` for parallel verification of all claims.

**Judging axes:** ACCURATE, DOESN'T-BREAK, Explainable Recommendations

**Tech:** claude-haiku, asyncio.gather, Pydantic v2 VerifierResult

**Effort:** S

---

### Step 4.5 — Prompt caching + small-model routing
**MUST-HAVE**

**What:** `wizard/routing/budget.py`. Mark stable system prompt prefix (role + equipment registry + citation instructions, ≥1024 tokens — pad with taxonomy table if shorter) with `cache_control: {type: 'ephemeral'}`. Route: `simple fact queries (intent=status_lookup|sop_lookup)` → Gemini Flash 2.0 (<200ms); `diagnostic/rca/maintenance_plan` → claude-sonnet-4-6 with cached prefix. Per-call accounting: log `{input_tokens, cached_input_tokens, output_tokens, latency_ms, model_used, cache_hit}` to `data/logs/llm_calls.jsonl`. Hard `asyncio.wait_for` timeout: 2.5s for intent/Gemini, 8s for Sonnet. On timeout: return last cached state with `fallback_used=True`. Note: inject engineer corrections as a prepended user-turn message, NOT into the system prompt (would bust the cache).

**Judging axes:** FAST, EFFICIENT, Technical Implementation & Innovation

**Tech:** Anthropic SDK cache_control, google-generativeai Gemini Flash, asyncio.wait_for

**Effort:** S

---

### Step 4.6 — Feedback ingestion and RAG hot-update loop
**MUST-HAVE**

**What:** `wizard/feedback/loop.py`. `POST /feedback` accepts `{session_id, turn_id, correction_type: Literal['wrong_diagnosis','wrong_rul','wrong_rca','confirm'], correction_text: str}`. Actions: (1) Append `FeedbackRecord` to `state.feedback_log` and `data/feedback/corrections.jsonl`. (2) If `correction_type` in `['wrong_diagnosis','wrong_rca']`: `chromadb.collection.upsert()` with new doc tagged `feedback_source=engineer_correction, correction_weight=2.0` — RAG hot-update visible on the next query. (3) If `correction_type == 'wrong_rul'`: append corrected label to sensor CSV and queue async LightGBM retrain via `FastAPI BackgroundTask` (writes to temp file, atomic `os.rename()` swap on completion — never corrupt the serving model mid-query). (4) Return `{accepted: True, impact: 'rag_updated'|'model_retraining_queued'|'logged'}`. Demo flow: engineer corrects once → same question next turn uses the correction → SMOOTH + req 6 visibly satisfied.

**Judging axes:** ACCURATE, SMOOTH, Feedback-driven improvement, Business Impact & Feasibility

**Tech:** chromadb collection.upsert(), FastAPI BackgroundTasks, lightgbm for async retrain, os.rename for atomic swap

**Effort:** M

---

### Step 4.7 — Proactive maintenance planner (autonomous trigger)
**MUST-HAVE** *(this is the differentiation feature — do not cut)*

**What:** `wizard/graph/proactive.py`. Background `asyncio` task (APScheduler 30s tick) polls all equipment RUL from the in-memory model cache. When any equipment's `rul_days_p50 < 3` (72h threshold): autonomously trigger the full Diagnosis + MaintenancePlannerNode chain without user prompt. Check `spare_parts_catalog` for part availability and procurement lead time. Check a simulated shift schedule (CSV, lowest-downtime window). Push a structured `ProactiveAlert` to the SSE stream and to the logbook. Demo seeding: one equipment unit's sensor playback is seeded so RUL crosses 72h exactly 90 seconds after demo start. This fires the proactive alert on-camera without any user input — the "agentic" proof moment. `ProactiveAlert` carries full citations, repair steps, urgency score, and recommended maintenance window.

**Judging axes:** Effective Use of Agentic-AI Frameworks, Technical Implementation & Innovation, Business Impact & Feasibility, ACCURATE, SMOOTH

**Tech:** APScheduler 3.10, asyncio, langgraph conditional edge trigger, Pydantic ProactiveAlert model

**Effort:** M

---

## PHASE 5 — Alerting Engine
*Day 5. Builds on ML models from Phase 3.*

### Step 5.1 — Rule-based alert engine with tiered severity
**MUST-HAVE**

**What:** `wizard/alerts/engine.py`. `AlertEngine` evaluates on every ML prediction. Rules (no LLM): CRITICAL if `anomaly_score > 0.85` OR `rul_days_p50 < 7`; HIGH if `anomaly_score > 0.65` OR `rul_days_p50 < 30`; MEDIUM if `anomaly_score > 0.45` OR `rul_days_p50 < 90`; LOW otherwise. Each triggered alert: `Alert(alert_id, equipment_id, severity, title, body, triggered_at, rule_id, rul_p50, recommended_action_brief)`. Write to `data/alerts.jsonl` (append-only, line-buffered flush) and to SQLite `alerts.db`. Pre-seed `alerts.db` with one CRITICAL alert before recording — belt-and-suspenders for the demo proactive trigger.

**Judging axes:** FAST, ACCURATE, Real-time alerting, DOESN'T-BREAK

**Tech:** Python dataclass-based rule predicates, sqlite3 (stdlib), APScheduler 3.10

**Effort:** S

---

### Step 5.2 — SSE alert stream + role-based notification routing
**MUST-HAVE**

**What:** `wizard/alerts/stream.py`. FastAPI `GET /alerts/stream` — SSE endpoint (sse-starlette 1.8) tailing `data/alerts.jsonl`. `GET /alerts/active` — returns unacknowledged alerts from SQLite. On new WS/SSE connection: immediately push historical unresolved alerts so reconnects never lose state. Role-based routing: CRITICAL+HIGH push to `data/notifications/maintenance_engineer.jsonl`; HIGH+ to `data/notifications/plant_manager.jsonl`; CRITICAL to `data/notifications/safety_officer.jsonl`. Demo: show 3 role views in the UI — each sees a different alert subset.

**Judging axes:** FAST, SMOOTH, DOESN'T-BREAK, Real-time alerting, Scalability & Real-World Applicability

**Tech:** sse-starlette 1.8, SQLite, FastAPI

**Effort:** S

---

## PHASE 6 — UX / Dashboard
*Day 5–6. Streamlit only. No React.*

### Step 6.1 — Streamlit app structure + session state initialization
**MUST-HAVE**

**What:** `wizard/ui/app.py` — Streamlit 1.35, `layout='wide'`, `page_icon='🔧'`. Five pages via `st.navigation`: `01_Chat.py, 02_Dashboard.py, 03_Alerts.py, 04_Logbook.py, 05_Settings.py`. Centralize ALL session state keys in `wizard/ui/state.py`, initialized at app startup before any page renders (`session_id, equipment_id, messages, alerts, unread_alerts, feedback, demo_mode`). Sidebar: active equipment selector, unread-alert badge count (reads from `st.session_state['unread_alerts']`), system health dot (green/amber/red from `GET /health`), last-updated timestamp. `.streamlit/config.toml`: `server.maxUploadSize=50, server.requestTimeout=120`.

**Judging axes:** EASY-TO-USE, SMOOTH, DOESN'T-BREAK

**Tech:** streamlit 1.35, streamlit-extras 0.4, python-dotenv

**Effort:** S

---

### Step 6.2 — Chat interface: streaming + citation pills + confidence badges + agent trace
**MUST-HAVE**

**What:** `wizard/ui/pages/01_Chat.py`. `st.chat_input` + `st.chat_message` conversation history from `st.session_state['messages']`. On submit: `st.status('Routing to agents...')` spinner → call `POST /chat` via `httpx.Client` (sync) → stream response via `st.write_stream`. Per assistant message render: (1) Citation pills — small `st.badge` per source doc/SOP/log, clickable to `st.expander` with raw chunk text + doc name + section; (2) Confidence badge: `verified` (green), `unverified` (amber), `low` (red) from `confidence` field; (3) Agent trace expander (collapsed by default) showing which nodes fired + latency_ms per node; (4) Feedback widget: thumbs-up/thumbs-down button pair with unique `key=f'fb_{message_id}'`, thumbs-down reveals `st.text_input('Correct this')` → `POST /feedback` on submit → `st.toast('Correction applied — RAG updated')`. Never use `st.form` for feedback (clears entire chat on submit).

**Judging axes:** FAST, ACCURATE, EASY-TO-USE, SMOOTH, Explainable Recommendations

**Tech:** streamlit, httpx 0.27, st.write_stream, st.badge (streamlit-extras), st.toast

**Effort:** M

---

### Step 6.3 — Equipment health dashboard: heatmap + RUL gauges + Simulate Fault button
**MUST-HAVE**

**What:** `wizard/ui/pages/02_Dashboard.py`. Top row: 3 `st.metric` KPI tiles (Active Alerts count with delta, Equipment at Risk count, Avg RUL days). Middle: Plotly heatmap (12 equipment × 7-day health score 0–100, green/amber/red color scale). Below: RUL gauge cluster — one `go.Indicator` gauge per critical equipment, red zone below 14 days, using `plotly make_subplots` (render once not in loop). Bottom: anomaly timeline — Plotly scatter + line chart of last 24h sensor readings vs normal band, anomaly points as red crosses. All charts `@st.cache_data(ttl=30)`. Single "Simulate Fault" button — sets `st.session_state['simulate_fault'] = equipment_id` which the alert engine polling loop picks up to inject a spike into sensor data.

**Judging axes:** EASY-TO-USE, ACCURATE, SMOOTH, FAST

**Tech:** plotly 5.22 (go.Indicator, go.Heatmap, go.Scatter, make_subplots), st.cache_data, st.metric

**Effort:** M

---

### Step 6.4 — Alert feed: severity tiers + acknowledge-to-logbook + notification toast
**MUST-HAVE**

**What:** `wizard/ui/pages/03_Alerts.py`. Filterable alert list from `st.session_state['alerts']`. Each card: severity badge (CRITICAL=red, HIGH=orange, MEDIUM=yellow, LOW=gray), equipment ID, plain-English description, timestamp, estimated downtime impact hours, "Recommended Action" button that deeplinks to Chat page with query pre-filled via `st.query_params`. Role dropdown filter (Maintenance Engineer / Plant Manager / Safety Officer). "Acknowledge" button per alert: marks alert resolved in SQLite, appends logbook entry, decrements `st.session_state['unread_alerts']`. `st.toast` fires on new alert regardless of active page — use `st.session_state['last_toast_time']` to debounce (minimum 5s between toasts).

**Judging axes:** EASY-TO-USE, SMOOTH, DOESN'T-BREAK, NO-ERRORS

**Tech:** streamlit, st.toast, st.query_params (Streamlit 1.30+ API), st.badge

**Effort:** S

---

### Step 6.5 — Explainability drill-down panel
**NICE-TO-HAVE** *(cut if Day 6 is at risk — citation pills in chat are sufficient for req 4)*

**What:** `wizard/ui/components/explainability_panel.py`. Reusable component called from both Chat and Alerts pages. On "Why?" button click: `st.dialog` modal (3-column layout): left = retrieved doc excerpt with relevant sentence highlighted in yellow (`st.markdown` with `unsafe_allow_html=True`), source filename + section; center = Plotly `go.Bar` of top-3 retrieval confidence scores (displayed as percentages, never raw floats); right = agent reasoning chain (which nodes fired, what was returned, critic verdict if available). "View full document" expander below. Call signature: `show_explainability_panel(citations: list[Citation], agent_trace: dict)`.

**Judging axes:** ACCURATE, EASY-TO-USE, SMOOTH

**Tech:** st.dialog (Streamlit 1.31+), plotly go.Bar, streamlit-extras

**Effort:** M

---

### Step 6.6 — UI error envelopes + input validation
**MUST-HAVE**

**What:** All backend calls in UI wrapped in `try/except` with human-readable `st.warning` or `st.error` — never a Python traceback. Error messages: timeout → "Agent took too long — showing cached analysis"; RAG failure → "Knowledge base lookup failed — please rephrase"; model error → "Prediction unavailable — showing last known RUL". Chat input validation: minimum 5 chars, maximum 500 chars, strip whitespace, reject pure-whitespace. Settings page: validate API key format (`ANTHROPIC` key starts `sk-ant-`, Gemini starts `AIza`) before saving. Global health check at app startup: call `GET /health`, if unhealthy show banner "Backend agents are starting up — first response may take 10s". Never call `st.stop()` inside a callback.

**Judging axes:** DOESN'T-BREAK, NO-ERRORS, SMOOTH

**Tech:** try/except, st.warning/st.error, st.query_params, .streamlit/config.toml

**Effort:** S

---

## PHASE 7 — Robustness & Eval
*Day 7. This phase exists to prevent demo-day failures.*

### Step 7.1 — Hardened LLM client: timeouts + exponential backoff + circuit-breaker
**MUST-HAVE**

**What:** `wizard/core/llm_client.py`. Single `LLMClient` class wrapping all provider calls: per-call timeout (8s Sonnet, 2.5s Haiku/Gemini), 3-attempt exponential backoff with jitter on 429/500/503 (`tenacity` library), circuit-breaker (5 failures in 60s → open for 120s). On circuit open: return canned `AgentResult(status='degraded', message='Service temporarily unavailable — cached analysis shown', fallback_used=True)`. Expose `token_in, token_out, latency_ms, cache_hit` on every response. Apply to all four provider paths (Sonnet, Haiku, Gemini Flash, Ollama).

**Judging axes:** FAST, DOESN'T-BREAK, NO-ERRORS, EFFICIENT

**Tech:** tenacity 8.x, httpx 0.27 with timeout param, anthropic SDK 0.26+

**Effort:** M

---

### Step 7.2 — Input validation at conversation boundary
**MUST-HAVE**

**What:** `wizard/api/validation.py`. `ConversationTurn` Pydantic model: `message (str, max 2000 chars, strip HTML)`, `session_id (UUID4)`, `equipment_id (Literal of canonical IDs from taxonomy YAML)`. Prompt-injection guard: reject messages matching narrow patterns (`re` check: starts with "ignore", contains "system prompt", contains "you are now") with graceful 400 + user-friendly message. Never block legitimate maintenance queries. Log every rejection to `data/logs/audit.jsonl`.

**Judging axes:** NO-ERRORS, DOESN'T-BREAK, SMOOTH

**Tech:** Pydantic v2 field_validator, bleach 6.x for HTML strip, re (narrow injection patterns), FastAPI 422 automatic on schema mismatch

**Effort:** S

---

### Step 7.3 — Per-agent graceful degradation tiers
**MUST-HAVE**

**What:** `wizard/core/degradation.py`. For each specialist node, define 3-tier degradation: Tier 1 = full answer with source citations; Tier 2 = partial answer from cached `AgentState` last-known values with "Based on last known data as of [timestamp]" disclaimer; Tier 3 = "Insufficient live data — here is the standard SOP for this fault class" pulled from pinned knowledge base. Tool failures (ChromaDB timeout, joblib load error, sensor file missing) always route to Tier 2 or 3 — never to an error screen. Always pass `equipment_id` through the fallback path so the SOP lookup is contextually correct.

**Judging axes:** DOESN'T-BREAK, NO-ERRORS, SMOOTH, ACCURATE

**Tech:** asyncio.wait_for per tool call, shelve/in-memory cache for Tier-2 state, structlog for degradation events

**Effort:** M

---

### Step 7.4 — Performance instrumentation + latency budget enforcement
**MUST-HAVE**

**What:** `wizard/core/metrics.py`. Wrap `/chat` endpoint in `TurnMetrics` context manager: record `wall_clock_ms, llm_tokens_in, llm_tokens_out, cached_tokens, rag_latency_ms, ml_latency_ms, agent_hops, degradation_tier`. Emit to `data/logs/metrics.jsonl` (structured JSON via structlog). Budget thresholds (log warnings, never block): P95 end-to-end 4s, max tokens out 1500, max agent hops 3. Expose `GET /metrics` returning P50/P95 per-node over last 100 turns. Display live latency indicator in Streamlit sidebar (P50 ms). Show cache hit rate in Dashboard tab.

**Judging axes:** FAST, EFFICIENT, SMOOTH, Technical Implementation & Innovation

**Tech:** time.perf_counter, structlog 24.x, FastAPI GET /metrics

**Effort:** M

---

### Step 7.5 — Golden eval suite + regression runner
**MUST-HAVE**

**What:** `scripts/eval_run.py` + `data/evals/golden.jsonl`. Create 25 golden Q&A pairs written BEFORE running the full system (no bias): 5 diagnostic queries, 5 SOP-lookup queries, 5 RCA queries, 5 RUL queries, 5 adversarial (equipment not in corpus → expected "Insufficient data" response). Per golden item: `{question, expected_answer_contains: list[str], expected_citations: list[str], expected_risk_level: str, max_latency_ms: 5000}`. Pytest runner: sends each to running FastAPI, checks HTTP 200, `source_refs` non-empty for RAG questions, answer contains any keyword from `expected_answer_contains` (OR logic), latency under budget. Emit colored pass/fail to console + `data/evals/regression_report.md`. `--check` flag exits non-zero if pass rate < 88% (22/25). Run before every demo rehearsal and before final ZIP.

**Judging axes:** ACCURATE, DOESN'T-BREAK, NO-ERRORS, Technical Implementation & Innovation

**Tech:** pytest 8.x, pytest-asyncio, httpx, Rich console output, pandas for score reporting

**Effort:** M

---

## PHASE 8 — Demo & Submission
*Day 8–9. Do not add new features after Day 7.*

### Step 8.1 — Pre-baked demo happy path + demo mode
**MUST-HAVE**

**What:** `demo/HAPPY_PATH.md` — exact 5-step script with target timestamps: (0:00–0:20) open Dashboard, point to seeded equipment in red gauge; (0:20–0:50) Simulate Fault fires → watch alert badge increment + CRITICAL toast appear; (0:50–1:20) click "Recommended Action" on alert (pre-fills Chat: "EAF-04 shows bearing wear fault — what is the RUL and recommended repair procedure including spare parts?"); (1:20–2:00) agent streams response with citation pills; (2:00–2:30) proactive maintenance plan appears without user input (the agentic wow); (2:30–3:00) thumbs-down correction → "RAG updated" toast → re-ask same question → corrected answer; (3:00–3:30) switch to ARCHITECTURE.md, narrate LangGraph diagram. `demo/demo_reset.py` — resets all session state, clears SQLite transient alerts (keeps one pre-seeded CRITICAL), resets sensor playback pointer. `?demo=true` URL param enables response caching mode: backend checks `data/demo_cache.json` (pre-computed JSON responses for the 5 scripted queries) before hitting LLM API — guarantees <1s responses during recording.

**Judging axes:** SMOOTH, EASY-TO-USE, DOESN'T-BREAK, NO-ERRORS

**Tech:** demo_reset.py (Python), data/demo_cache.json (pre-computed), st.query_params

**Effort:** S

---

### Step 8.2 — Architecture document (8 required sections)
**MUST-HAVE** *(write section-by-section during build, finalize Day 8)*

**What:** `docs/ARCHITECTURE.md`. Eight sections: (1) System architecture — Mermaid diagram auto-generated via `graph.get_graph().draw_mermaid()` showing all LangGraph nodes + edges; (2) Tech stack table — layer, library, version, justification; (3) Data flow — sequence diagram for one complete query end-to-end; (4) Model design — IsolationForest params, Weibull RUL formula, hybrid RAG retrieval mechanics, prompt caching structure; (5) Alerting + prediction logic — rule thresholds, severity classification, proactive trigger logic; (6) Assumptions + limitations — synthetic data boundaries, single-machine deployment, no real SCADA, English only; (7) Install + run — exactly 5 commands: `git clone → cp .env.example .env → make setup → make train → make run`; (8) Sample I/O — 3 complete query-response pairs with citations visible. Include `KNOWN_FAILURE_MODES.md`: 5 edge cases with exact fallback behavior (unknown equipment ID, sensor data gap, empty history, LLM timeout, missing spare part).

**Judging axes:** Problem Understanding & Approach, Technical Implementation & Innovation, Presentation & Communication Quality, Scalability & Real-World Applicability

**Tech:** Mermaid, Markdown, langgraph draw_mermaid()

**Effort:** M

---

### Step 8.3 — Business impact narrative
**MUST-HAVE**

**What:** `docs/BUSINESS_IMPACT.md`. Sections: (1) Current-state pain anchored to Tata Steel's own published KPIs (22% downtime reduction via Asset Sphere, 1:10 cost-benefit ratio, INR 1.4B cumulative savings from 800-model program — all attributable, none fabricated); (2) System contribution — early warning shifts reactive to predictive maintenance; (3) Scalability — adding a new equipment type requires only a new SOP + sensor schema extension, no code change; (4) Deployment path — FastAPI containerizable, Streamlit deployable on internal Kubernetes; (5) Cost estimate — LLM cost per query ~$0.003 (Gemini Flash pricing) at 500 queries/day = $1.50/day = $547/year (cite current Gemini Flash pricing). NEEDS INPUT: verify per-minute downtime cost figure from a published Tata Steel source before including absolute cost — use 22% downtime reduction as the anchor if unverifiable.

**Judging axes:** Business Impact & Feasibility, Scalability & Real-World Applicability, Problem Understanding & Approach

**Tech:** Markdown only.

**Effort:** S

---

### Step 8.4 — Demo video (3.5 minutes, scripted, cached LLM responses)
**MUST-HAVE**

**What:** OBS Studio screen recording, 1920×1080, 30fps, H.264 MP4. Use `demo_cache.json` for all LLM calls during recording (guaranteed sub-1s responses, no latency variance). Video structure: 0:00–0:10 problem statement voiceover; 0:10–0:30 fault alert fires live on Dashboard; 0:30–1:30 full happy path (3 chat turns with citations, proactive planner fires); 1:30–2:00 feedback correction + corrected answer; 2:00–2:30 architecture diagram narration (point to LangGraph nodes, name each); 2:30–3:30 business impact numbers. Add captions (Kapwing or DaVinci Resolve free). Text overlay throughout: "[All data is synthetic — generated for demonstration]". Use OBS window capture (not screen capture) so browser address bar is hidden. Upload to YouTube unlisted; include link in README. Keep under 3:30 total.

**Judging axes:** SMOOTH, EASY-TO-USE, Presentation & Communication Quality, Problem Understanding & Approach

**Tech:** OBS Studio, Kapwing/DaVinci for captions, ffmpeg for compression to <80MB

**Effort:** M

---

### Step 8.5 — Submission ZIP assembly + final smoke test
**MUST-HAVE**

**What:** ZIP structure: `src/` (all Python source), `data/` (committed synthetic datasets + committed model artifacts + committed chroma_db), `docs/` (ARCHITECTURE.md + BUSINESS_IMPACT.md + KNOWN_FAILURE_MODES.md + SAMPLE_IO.md), `README.md` (5-command install + YouTube link + problem statement + requirements mapping), `requirements.txt` (pinned via `pip freeze`), `.env.example` (all keys documented with placeholders, no real values). Pre-submission checklist (`SMOKE_TEST.md`, 20 items): fresh venv install succeeds; `make setup` + `make train` + `make run` completes without error; all 7 mandatory requirements demonstrable via 8 scripted demo questions; eval suite passes ≥22/25; no console errors in browser; Chrome DevTools Fast 3G throttle test (streaming still starts within 2s); gibberish query returns graceful 400; LLM kill test triggers Tier-3 fallback; architecture doc renders in PDF; video plays without audio sync issues. Run smoke test from a second machine or fresh Docker context (not developer machine). Mandatory pre-ZIP grep: `grep -r 'sk-ant-'` and `grep -r 'AIza'` — any hit = do not zip.

**Judging axes:** SMOOTH, DOESN'T-BREAK, NO-ERRORS, Presentation & Communication Quality

**Tech:** Makefile, pip freeze, grep, SMOKE_TEST.md

**Effort:** S

---

## MUST-HAVE vs NICE-TO-HAVE Summary

| Step | Label | Cut Order (if time-pressed) |
|---|---|---|
| 0.1 Problem narrative + matrix | MUST | Never cut |
| 0.2 Error envelope + scaffold | MUST | Never cut |
| 0.3 Taxonomy YAML | MUST | Never cut |
| 1.1 Sensor generator | MUST | Never cut |
| 1.2 Event log + spare parts | MUST | Never cut |
| 1.3 RAG corpus generator | MUST | Never cut |
| 2.1 Structure-aware chunking | MUST | Never cut |
| 2.2 Dual index ChromaDB + BM25 | MUST | Never cut |
| **2.3 Reranker (cross-encoder)** | **NICE** | **Cut 1st if Day 3 at risk** |
| 2.4 Citation-grounded prompts | MUST | Never cut |
| 3.1 Anomaly detection + SHAP | MUST | Never cut |
| 3.2 RUL estimator Weibull | MUST | Never cut |
| 3.3 Pre-train + commit models | MUST | Never cut |
| 4.1 LangGraph state + schema | MUST | Never cut |
| 4.2 Supervisor + 6 nodes | MUST | Never cut |
| 4.3 Multi-turn SqliteSaver | MUST | Never cut |
| **4.4 Async verifier/critic** | **NICE** | **Cut 2nd if Day 5 at risk** |
| 4.5 Prompt caching + routing | MUST | Never cut |
| 4.6 Feedback RAG hot-update | MUST | Never cut |
| 4.7 Proactive planner trigger | MUST | Never cut |
| 5.1 Rule-based alert engine | MUST | Never cut |
| 5.2 SSE stream + role routing | MUST | Never cut |
| 6.1 Streamlit page routing | MUST | Never cut |
| 6.2 Chat interface streaming | MUST | Never cut |
| 6.3 Health dashboard | MUST | Never cut |
| 6.4 Alert feed | MUST | Never cut |
| **6.5 Explainability drill-down** | **NICE** | **Cut 3rd if Day 6 at risk** |
| 6.6 UI error envelopes | MUST | Never cut |
| 7.1 Hardened LLM client | MUST | Never cut |
| 7.2 Input validation | MUST | Never cut |
| 7.3 Degradation tiers | MUST | Never cut |
| 7.4 Performance instrumentation | MUST | Never cut |
| **7.5 Golden eval suite** | **NICE** | **Cut 4th if Day 7 at risk** — keep 10 manual smoke-test Q&As |
| 8.1 Demo happy path + cache | MUST | Never cut |
| 8.2 Architecture doc | MUST | Never cut |
| 8.3 Business impact doc | MUST | Never cut |
| 8.4 Demo video | MUST | Never cut |
| 8.5 ZIP + smoke test | MUST | Never cut |

**Explicit cut list (never build):** fine-tuned domain SLM, React/Next.js frontend, Docker Compose, real SCADA/OPC-UA integration, PostgreSQL, mobile app/PWA, WebSocket (use SSE), conversational onboarding, multi-language support.

---

## Judging-Axis Coverage Matrix

| Axis | Primary Steps | Secondary Steps |
|---|---|---|
| **A. Problem Understanding & Approach** | 0.1, 8.2, 8.3 | 0.3, 1.3, 8.4 |
| **B. Effective Use of Agentic-AI Frameworks** | 4.1, 4.2, 4.3, 4.7 | 4.4, 4.5, 4.6, 5.2 |
| **C. Technical Implementation & Innovation** | 4.2, 4.5, 2.3, 3.1, 3.2 | 2.4, 4.4, 7.4, 7.5 |
| **D. Scalability & Real-World Applicability** | 4.3, 8.3, 5.2 | 0.3, 1.1, 1.2, 1.3 |
| **E. Presentation & Communication Quality** | 8.2, 8.4, 8.5 | 0.1, 6.1, 6.2 |
| **F. Business Impact & Feasibility** | 8.3, 4.7, 4.6 | 0.1, 5.1, 5.2 |
| **G. FAST** | 4.5, 7.1, 6.2, 3.1, 3.2 | 2.2, 5.1, 7.4 |
| **H. EFFICIENT** | 4.5, 2.2, 3.1, 3.2, 7.1 | 2.3, 4.2, 7.4 |
| **I. ACCURATE** | 2.4, 3.1, 3.2, 4.4, 7.5 | 1.1, 2.3, 4.6, 0.3 |
| **J. EASY-TO-USE** | 6.2, 6.3, 6.4, 6.5, 8.4 | 6.1, 3.2, 5.2 |
| **K. DOESN'T-BREAK** | 4.3, 7.1, 7.3, 8.1, 0.2 | 3.3, 4.2, 6.6, 8.5 |
| **L. NO-ERRORS** | 0.2, 4.1, 7.2, 6.6, 8.5 | 2.4, 7.1, 7.3 |
| **M. SMOOTH** | 8.1, 8.4, 4.7, 1.1, 6.3 | 4.6, 5.1, 6.2, 6.4 |

---

## Top 8 Build Risks + Mitigations

| Risk | Mitigation |
|---|---|
| Taxonomy YAML not enforced — synthetic data contradicts documents, ACCURATE axis collapses | Run validation script asserting all fault codes and equipment IDs consistent before any downstream step (Step 0.3) |
| LLM API latency in demo recording fails FAST axis | demo_cache.json with pre-computed responses for 5 scripted queries; Gemini Flash for intent (free, fast) (Step 8.1) |
| Proactive alert fires at wrong time during demo | Seed sensor playback so RUL crossing is deterministic at ~90s; pre-seed one CRITICAL in SQLite as fallback (Step 4.7) |
| SqliteSaver concurrent-write crash with multiple uvicorn workers | Always run `--workers 1` for demo; document in ARCHITECTURE.md (Step 4.3) |
| ChromaDB cold start takes 3–5s on first judge query | Pre-warm at server startup with dummy embed call (Step 2.2); startup health check confirms index loaded (Step 4.3) |
| Feedback loop visibly changes nothing in next query — judges probe this | Verify ChromaDB upsert with `correction_weight=2.0` shifts RRF rank before demo day; test explicitly with the scripted correction query (Step 4.6) |
| Secret API key committed to ZIP | Mandatory `grep -r 'sk-ant-'` + `grep -r 'AIza'` before zipping; `.env` in `.gitignore` and ZIP exclusion list (Step 8.5) |
| Install fails on judge's clean machine due to global env vars on dev machine | Mandatory fresh-venv test on Day 9 with `.env` copied from `.env.example`, only `requirements.txt` installed (Step 8.5) |
