# Maintenance Wizard — Definitive Build Playbook v2
**Tata Steel AI Hackathon 2026 | Round 2 | Agentic AI Challenge | Deadline: 2026-06-15 23:59 IST**

---

## Orientation

**What we are building:** An agentic AI decision-support system for steel-plant maintenance engineers — multi-turn RAG + predictive ML + autonomous proactive alerting, deployed as a FastAPI backend with Streamlit UI.

**The 9-day solo reality:** ~60 usable hours (gaps for sleep/review). Phase 4 (agentic core) is the highest-risk phase and has been budgeted at 30h in this version. Every NICE-TO-HAVE step is explicitly sequenced after all MUST-HAVEs so time pressure produces a complete working system, not a polished but broken one.

**The one-line winning thesis:** A LangGraph multi-agent system that autonomously fires a full maintenance plan before the engineer asks — because the best maintenance recommendation is the one that arrives before the failure, not after.

---

## Conflict Resolutions

| Decision | Chosen | Reason |
|---|---|---|
| Vector store | ChromaDB in-process | No Docker dep; judges run pip install, not docker-compose |
| Embedding model | all-MiniLM-L6-v2 | CPU-safe; ~50ms encode; no GPU required |
| Frontend | Streamlit 1.35 only | React costs 2+ days with zero judging upside |
| Streaming to UI | SSE (sse-starlette) + st_autorefresh polling | SSE for server-push; Streamlit has no native push model, must poll |
| Alert consumption in Streamlit | streamlit-autorefresh (3s) + GET /alerts/active | Solves Streamlit's re-run model; no background threads |
| Orchestration scheduler | asyncio.create_task() inside FastAPI lifespan | Replaces APScheduler BackgroundScheduler; eliminates asyncio/thread deadlock risk |
| Docker | Excluded | Adds judge setup friction; Makefile + venv is sufficient |
| LLM primary | claude-sonnet-4-6 (Anthropic) | Already running; structured output via tool_use |
| LLM intent/routing | Gemini Flash 2.0 free-tier | <200ms; 15 RPM limit known risk |
| LLM fallback tier 2 | Ollama llama3.2:3b | For Gemini exhaustion; needs install verification |
| LLM fallback tier 3 | Regex keyword classifier | Zero external dependency; 30-line Python; always available |
| Feedback RUL correction | Bayesian in-memory adjustment | Replaces LightGBM retrain; n=1 retrain is invalid; Bayesian update is correct + immediate |
| Feedback RAG correction | Explicit post-RRF re-rank on correction_weight | ChromaDB metadata alone does not affect retrieval ranking |
| Evaluation timing | golden.jsonl written in Phase 0 | Prevents bias from writing tests after implementation |
| PYTHONPATH | pip install -e . in make setup | Eliminates ModuleNotFoundError on judge machines |
| Streamlit HTTP calls | httpx.Client (sync) only, never AsyncClient | Prevents asyncio nesting crash in Streamlit callbacks |

---

## Phase Timeline

| Phase | Name | Days | Effort | Added/Changed Steps |
|---|---|---|---|---|
| 0 | Foundation | Day 1 AM (~4h) | S | Steps 0.1–0.6 (0.4, 0.5, 0.6 are new) |
| 1 | Synthetic Data | Day 1 PM–Day 2 (~10h) | M | Step 1.4 new |
| 2 | Knowledge/RAG Layer | Day 2–3 (~12h) | M | Step 2.3 updated |
| 3 | Predictive ML Models | Day 3 (~6h) | M | Step 3.2 updated |
| 4 | Agentic Core | Day 3–6 (~30h) | L | Steps 4.2, 4.6, 4.7 updated; budget +10h |
| 5 | Alerting Engine | Day 6 (~6h) | M | Steps 5.1, 5.2 updated; Step 5.3 new |
| 6 | UX / Dashboard | Day 6–7 (~14h) | M | Steps 6.1, 6.4 updated; Steps 6.7, 6.8 new |
| 7 | Robustness & Eval | Day 7–8 (~8h) | M | Steps 7.5, 7.6 updated |
| 8 | Demo & Submission | Day 8–9 (~12h) | M | Steps 8.2, 8.5 updated |

**Total estimated active hours: ~102h. Solo 9-day achievable at 11–12h/day for AI-native developer using parallel code generation.**

---

## PHASE 0 — Foundation
*Day 1 morning. Complete this entire phase before writing a single data generator or agent.*

### Step 0.1 — Architecture doc stub + problem framing
MUST | FAST | SMOOTH | Problem Understanding & Approach | Business Impact & Feasibility | S

Write `docs/ARCHITECTURE.md` with all 8 section headers pre-populated and placeholder content. Writing on Day 8 under time pressure produces a two-hour document; writing the skeleton on Day 1 produces an eight-day document. Sections: (1) System Architecture, (2) Tech Stack, (3) Data Flow, (4) Model Design, (5) Alerting + Prediction Logic, (6) Assumptions + Limitations, (7) Install + Run (5-command sequence), (8) Sample I/O. Populate Section 6 (Assumptions) immediately — it forces honest scoping before you build scope-wrong. Add a Mermaid placeholder under Section 1 labeled `[REPLACE: run graph.get_graph().draw_mermaid() in Phase 4]`. Sections 1 and 3 get Mermaid diagrams after Phase 4 compiles. Sections 2, 4, 5, 6, 7 can be updated after each phase. Section 8 populated from the golden eval output (Phase 0, Step 0.4). Also write 200-word problem framing anchored to Tata Steel's own published KPIs (22% downtime reduction via Asset Sphere, 1:10 cost-benefit, INR 1.4B savings from 800-model program). All three figures are attributable; do not add per-minute downtime cost unless you find a published source. This framing appears verbatim in README.md, the architecture doc lede, and the first 20s of the demo narration.

---

### Step 0.2 — Project scaffold + Makefile + .env.example + pyproject.toml
MUST | DOESN'T-BREAK | NO-ERRORS | SMOOTH | S

**[CRITIQUE FIX — critical gaps: undefined Makefile targets + missing .env wiring + missing pip install -e .]**

Full directory scaffold: `wizard/{core,data,rag,ml,graph,alerts,feedback,reports,api,ui}/`. Add `__init__.py` in every package. Create `pyproject.toml` (minimal: `name="wizard", version="0.1.0", packages=["wizard"]`, `python_requires=">=3.12"`). Create `.python-version` pinned to `3.12`. This makes `pip install -e .` work and eliminates `ModuleNotFoundError` on every judge machine.

Makefile targets defined here and never changed:
```makefile
setup:
    python -m venv .venv && .venv/bin/pip install --upgrade pip
    .venv/bin/pip install -r requirements.txt
    .venv/bin/pip install -e .

train:
    .venv/bin/python scripts/train_models.py

run:
    .venv/bin/uvicorn wizard.api.server:app --port 8000 --workers 1 &
    .venv/bin/streamlit run wizard/ui/app.py --server.port 8501

stop:
    pkill -f "uvicorn wizard.api.server" || true
    pkill -f "streamlit run wizard" || true

reset:
    rm -f data/sessions.db data/alerts.jsonl data/feedback/corrections.jsonl
    python demo/demo_reset.py

smoke:
    .venv/bin/pytest scripts/eval_run.py -v --check
```

Create `.env.example` with every required key documented:
```
ANTHROPIC_API_KEY=sk-ant-api03-...
GEMINI_API_KEY=AIzaSy...
OLLAMA_BASE_URL=http://localhost:11434   # optional; falls back to keyword classifier if absent
LOG_LEVEL=INFO
DEMO_MODE=false
```

Create `wizard/core/config.py`: calls `load_dotenv()` at module import; raises `ConfigError` with actionable message if `ANTHROPIC_API_KEY` is missing or does not start with `sk-ant-`; treats `GEMINI_API_KEY` and `OLLAMA_BASE_URL` as optional with a startup warning log. Every other module imports config from this single location. The FastAPI health endpoint calls `config.validate()` synchronously before accepting any request.

---

### Step 0.3 — Error envelope contract
MUST | NO-ERRORS | DOESN'T-BREAK | SMOOTH | S

Define typed `AgentResult` in `wizard/core/envelope.py`:
```python
class AgentResult(BaseModel):
    status: Literal["ok", "error", "degraded"]
    data: Any
    error_code: str | None
    message: str
    latency_ms: int
    tokens_used: int
    source_refs: list[SourceRef]
    fallback_used: bool
    degradation_tier: int  # 1=full, 2=cached, 3=sop_only
```
Register a global FastAPI exception handler that catches all unhandled exceptions and returns this envelope as JSON. Never let a raw Python traceback reach the Streamlit layer or the judge's browser console.

---

### Step 0.4 — Golden evaluation suite (write BEFORE any code)
MUST | ACCURATE | NO-ERRORS | Technical Implementation & Innovation | S

**[CRITIQUE FIX — high severity: eval bias from writing tests after implementation.]**

Write `data/evals/golden.jsonl` now, from the problem requirements and taxonomy YAML, before any system code exists. The 25 questions are derived from the 7 mandatory functional requirements + the 13 judging axes — not from what the system can currently answer. Commit the file. Treat it as a frozen specification.

Distribution: 5 diagnostic queries (equipment + fault codes from taxonomy), 5 SOP-lookup queries (procedure names from the SOP list), 5 RCA queries (incident types from event log spec), 5 RUL queries (equipment IDs + threshold scenarios), 5 adversarial (unknown equipment, empty corpus, language injection attempt, no history, conflicting fault codes).

Each record:
```json
{
  "id": "golden_001",
  "question": "...",
  "equipment_id": "HSM-GB-001",
  "expected_answer_contains": ["vibration", "bearing"],
  "expected_citations_min": 1,
  "expected_risk_level": "HIGH",
  "max_latency_ms": 5000,
  "adversarial": false
}
```

After writing, review: does each question have a plausible answer in the data we plan to generate? If yes, the question is well-specified. If no, refine the data generation plan, not the question.

---

### Step 0.5 — Equipment taxonomy YAML (single source of truth)
MUST | ACCURATE | DOESN'T-BREAK | SMOOTH | S

Write `data/synthetic/equipment_taxonomy.yaml`. Define exactly 6 equipment types: (1) HSM finishing-stand gearbox, (2) Blast Furnace blower, (3) Continuous Caster withdrawal-roll bearing, (4) EAF electrode assembly, (5) Raw-material conveyor drive, (6) Hydraulic descaling pump. For each: canonical `equipment_id`, 3–4 failure modes, sensor signatures (which sensors, drift direction, drift rate), MTTF in days, degradation shape (linear/exponential/sudden), canonical fault codes (e.g., `HSM-GB-VIB-HH`). Write a validation script `scripts/validate_taxonomy.py` that runs on import and asserts all cross-references are internally consistent. Every downstream generator imports from this YAML — if a fault code is not in this file, it cannot appear anywhere in the corpus.

---

### Step 0.6 — Judge coverage matrix
MUST | Problem Understanding & Approach | S

Write `docs/JUDGE_MATRIX.md`. Rows = 13 judging axes (6 email criteria + 7 webinar axes). Columns = planned system features. Cells = Y/N + one-line "demo moment" description (what the judge sees on screen). Any axis with zero Y cells triggers an immediate build task. Any feature column with fewer than 2 Y cells is a candidate for cutting. Review this matrix at the start of each phase and mark completed cells. Print and pin it — this is the checklist that survives phase pressure.

---

## PHASE 1 — Synthetic Data
*Day 1 PM – Day 2. Critical path. All downstream phases depend on this.*

### Step 1.1 — Sensor time-series generator with injected fault episodes
MUST | ACCURATE | SMOOTH | Abnormality detection & failure prediction | M

`scripts/generate_sensor_data.py`. Twelve months of hourly readings per equipment unit. Sensors per type: vibration RMS (mm/s), bearing temperature (°C), lube-oil differential pressure (bar), motor current (A), acoustic emission (dB). Model each as: (a) healthy Gaussian baseline, (b) degradation ramp starting at seeded `t_fault` (`numpy random_state=42`), (c) single-point spike anomalies (3 per unit), (d) failure at `t_fail = t_fault + TTF` drawn from `scipy.stats.weibull_min(shape=1.8, scale=MTTF_from_taxonomy)`. Output: Parquet files in `data/synthetic/sensor_timeseries/` partitioned by `equipment_id`.

**Demo seeding requirement:** Unit `EAF-04` must be seeded so its computed RUL crosses 72h at exactly 90 seconds of elapsed sensor playback (Step 1.4 defines playback; coordinate here so the seed is consistent). Use `random_state=42` + a single `t_fault_override` parameter in the generator. Add a comment in code: `# DEMO SEED: EAF-04 RUL crosses 72h at playback_second=90`. Commit all generated Parquet files to the repo — judges never regenerate.

Tech: numpy 1.26, scipy 1.13, pandas 2.2, pyarrow.

---

### Step 1.2 — Event log + spare parts catalog + production impact table
MUST | ACCURATE | EASY-TO-USE | Scalability & Real-World Applicability | S

**[CRITIQUE FIX — low severity: production_impact_norm in urgency formula was undefined.]**

`scripts/generate_event_logs.py`. Produces ~500 structured events: `{equipment_id, timestamp, event_type: ALARM|TRIP|MAINTENANCE|INSPECTION|REPAIR, fault_code, duration_hours, shift_team, operator_id, downstream_impact_tons}`. All `fault_code` values validated against `equipment_taxonomy.yaml` at generation time (raise `ValueError` on unknown code — do not silently write invalid data).

Also generate `data/static/spare_parts_catalog.csv`: 50 parts, `{part_id, equipment_id, part_name, unit_cost_INR, lead_time_days, current_stock_qty, reorder_point}`. Realistic Indian industrial procurement: critical spares 45–90 days, consumables 7–14 days.

Also generate `data/static/impact_table.csv`: one row per equipment type, `{equipment_type, max_downtime_tons_per_hour, criticality_rank}`. This is the `production_impact_norm` source for the urgency score formula in Step 4.2. Normalization: divide by `max(max_downtime_tons_per_hour)` across all equipment. This file is static — loaded once at server startup.

Tech: Python, Faker 24.x, pandas, numpy.

---

### Step 1.3 — RAG knowledge corpus generator
MUST | ACCURATE | DOESN'T-BREAK | Knowledge Integration | M

`scripts/generate_rag_corpus.py`. Uses Claude Haiku with a strict system prompt injecting the taxonomy YAML as a constraint block: "You are generating a maintenance document. The following fault codes and thresholds are CANONICAL — do not invent others." Generate: 6 equipment manuals (5–8 pages each, Markdown), 8 SOPs (gearbox oil change, bearing replacement, electrode swap, LOTO, lubrication schedule, cooling system flush, alignment check, emergency shutdown), 8 incident reports (RCA format: date, equipment, fault sequence, 5-Why, corrective action — each cross-referencing a real fault code from the event log), 6 last-inspection maintenance records. Frontmatter on every file: `{equipment_id, doc_type, date}`. Post-generation: assert zero fault codes appear in any document that are absent from the taxonomy YAML. Store under `data/rag_corpus/`. Commit generated files.

Requires `ANTHROPIC_API_KEY` set in `.env` (Step 0.2 wires this). The config validation in `wizard/core/config.py` will raise `ConfigError` before this script can fail mid-run.

Tech: Anthropic SDK (claude-haiku), PyYAML, Markdown.

---

### Step 1.4 — Sensor playback engine
MUST | SMOOTH | DOESN'T-BREAK | Effective Use of Agentic-AI Frameworks | S

**[CRITIQUE FIX — critical gap: no mechanism to feed Parquet data into ML inference loop at demo time, breaking the proactive alert entirely.]**

`wizard/data/sensor_player.py`. Maintains a `PlaybackState` dataclass: `{current_row_index: int, equipment_snapshots: dict[str, SensorSnapshot], speed_multiplier: float}`. On server startup (FastAPI lifespan), loads all Parquet files into memory as a dict of `{equipment_id: pd.DataFrame}`. A background `asyncio.create_task(playback_loop())` advances `current_row_index` by 1 every `real_seconds_per_tick` (default 3s; set `speed_multiplier=100` in demo mode to reach the 90s trigger). Each tick: read one row per equipment from the in-memory DataFrame at `current_row_index`, update `equipment_snapshots[equipment_id]`. The MLNode (Step 4.2) reads from `sensor_player.get_snapshot(equipment_id)` instead of a live sensor API. The ProactivePlanner (Step 4.7) also reads from `sensor_player.get_snapshot`. This creates the live-feeling data flow from static Parquet.

`GET /sensor/state` returns current `PlaybackState` for the dashboard. `POST /sensor/reset` resets `current_row_index=0` (called by `demo_reset.py`). `POST /sensor/speed` sets `speed_multiplier` (called at demo start to set multiplier=100 for the 90s trigger).

**Interface contract:** `SensorSnapshot = {equipment_id: str, timestamp: datetime, readings: dict[str, float], row_index: int}`. MLNode, ProactivePlanner, and AlertEngine all import and use only this type — never raw Parquet directly.

Tech: pandas 2.2, asyncio, FastAPI lifespan, Pydantic v2 `SensorSnapshot`.

---

## PHASE 2 — Knowledge / RAG Layer
*Day 2–3. Build and index before wiring to agents.*

### Step 2.1 — Structure-aware chunking pipeline
MUST | ACCURATE | FAST | EFFICIENT | Knowledge Integration | S

`wizard/rag/chunker.py`. Rules by doc type: manuals/SOPs chunk at Markdown H2/H3 boundaries (400–600 tokens), preserve section titles as context prefix; incident reports and maintenance records are one record = one chunk (atomic); sensor summaries group by equipment + 1h window. Every chunk: `{chunk_id (UUID), parent_doc_id, doc_type, equipment_id, section_title, token_count}`. Validate with `tiktoken` (cl100k_base) — reject chunks > 800 tokens. 64-token overlap for manual/SOP chunks only. Output: `data/index/chunks.jsonl` with Pydantic `ChunkManifest` schema.

Tech: LangChain `MarkdownHeaderTextSplitter`, tiktoken, Pydantic v2.

---

### Step 2.2 — Embed corpus + dual index (ChromaDB dense + BM25)
MUST | FAST | EFFICIENT | ACCURATE | DOESN'T-BREAK | M

`wizard/rag/indexer.py`. Embed all chunks with `sentence-transformers all-MiniLM-L6-v2` (local, CPU, ~50ms per encode). Store in ChromaDB (`persistent=True, path='./data/chroma_db'`). Build BM25 index (`rank_bm25 BM25Okapi`) pickle at `data/bm25_index.pkl`. Pre-warm ChromaDB at server startup with a dummy query call. Commit both `data/chroma_db/` and `data/bm25_index.pkl` to repo — judges never rebuild.

Tech: sentence-transformers 3.x, chromadb 0.5.x (in-process), rank_bm25 0.2.2.

---

### Step 2.3 — Hybrid retrieval with RRF fusion + correction-aware re-ranking
MUST | ACCURATE | Explainable Recommendations | Feedback-driven improvement | S

**[CRITIQUE FIX — critical gap: ChromaDB `correction_weight` metadata does not affect retrieval ranking. Fixed by explicit post-RRF re-rank step.]**

`wizard/rag/retriever.py`. At query time: run BM25 (top-50) and ChromaDB dense (top-50) in parallel. Merge via Reciprocal Rank Fusion (RRF, k=60). After RRF merge, apply correction-aware re-ranking: any chunk with `metadata.feedback_source == "engineer_correction"` is moved to the top of the result list, capped at rank 3, regardless of RRF score. This makes engineer corrections immediately and visibly effective on the next query — no model retrain, no ChromaDB scoring change required. Return `list[RetrievedDoc]` with `{chunk_id, doc_title, section, equipment_id, chunk_text, rrf_score, correction_promoted: bool}`.

Optionally: pass top-20 RRF results through `CrossEncoder (BAAI/bge-reranker-base)` before correction promotion. Mark NICE-TO-HAVE — cut if Day 3 is at risk. The correction-aware re-rank is MUST regardless.

Add a unit test `tests/test_retrieval_correction.py` asserting: (1) ingest a correction chunk, (2) run retriever on the same query, (3) assert correction chunk appears in top-3. This test must pass before Step 4.6 is started.

Tech: rank_bm25, chromadb, sentence-transformers CrossEncoder (optional), pytest.

---

### Step 2.4 — Citation-grounded prompt architecture + structured output
MUST | ACCURATE | NO-ERRORS | Explainable Recommendations | SMOOTH | M

`wizard/rag/prompts.py`. System prompt (cached prefix, ~800 tokens stable, padded to ≥1024 tokens with taxonomy table if shorter): role + equipment registry + 7 mandatory-requirement map + citation rule: "Every factual claim must cite at least one [SOURCE-N]. If no source supports a claim, say so explicitly — do not fabricate." Retrieved chunks formatted as numbered `[SOURCE-1]...[SOURCE-N]` blocks with metadata header. Structured output via Pydantic `MaintenanceAnswer`: `{answer_text, recommendations: list[Recommendation], citations: list[Citation], confidence: float, risk_level: Literal['low','medium','high','critical']}`. Citation schema: `{chunk_id, doc_name, section, equipment_id, relevant_excerpt: str ≤100 chars}`. Apply `cache_control: {type: 'ephemeral'}` on the system prompt block. Engineer corrections injected as a prepended user-turn message (never into the system prompt — would bust the 1024-token cache anchor).

Tech: Anthropic SDK 0.26+ `cache_control`, Pydantic v2.

---

## PHASE 3 — Predictive ML Models
*Day 3. Pre-train and commit all artifacts. Never train at demo time.*

### Step 3.1 — Anomaly detection: IsolationForest + SHAP
MUST | ACCURATE | FAST | EFFICIENT | Abnormality detection & failure prediction | M

`wizard/ml/anomaly_detector.py`. Per-equipment-type `IsolationForest` (`n_estimators=200, contamination=0.05`, sklearn 1.5). Feature engineering on `SensorSnapshot`: `rolling_mean_temp_60s, rolling_std_vibration_60s, current_A, delta_temp_1h, cumulative_runtime_h, equipment_age_days`. SHAP `TreeExplainer` for `feature_importance_top3` per prediction. Output: `AnomalyResult(equipment_id, anomaly_score: float, is_anomaly: bool, feature_importance_top3: list[str])`. Train on healthy-only data windows (pre `t_fault`) from Parquet. Persist with joblib to `data/models/anomaly_{equipment_type}.pkl`. Load as singleton at server startup.

Tech: scikit-learn 1.5 IsolationForest, shap 0.45 TreeExplainer, joblib 1.4.

---

### Step 3.2 — RUL estimator: Weibull + Bayesian online correction
MUST | ACCURATE | FAST | Abnormality detection & failure prediction | S

**[CRITIQUE FIX — critical gap: LightGBM retrain on n=1 correction is statistically invalid and will crash silently. Replaced with Bayesian in-memory correction that is correct, immediate, and visible to judges.]**

`wizard/ml/rul_estimator.py`. Two-stage per equipment type: Stage 1 = `lifelines WeibullAFTFitter` trained on synthetic fault episode records (time_to_failure, sensor features at onset). Stage 2 = degradation index correction (normalized distance from healthy centroid in sensor space adjusts baseline RUL estimate). Output: `RULResult(equipment_id, rul_days_p50, rul_days_p10, rul_days_p90, failure_probability_30d, risk_class: LOW|MEDIUM|HIGH|CRITICAL, confidence_pct)`. Thresholds: >90d = LOW, 30–90d = MEDIUM, 7–30d = HIGH, <7d = CRITICAL.

Online correction mechanism (replaces LightGBM retrain): `RULEstimator.apply_correction(equipment_id, engineer_rul_days)` performs a Bayesian weighted update: `new_rul = 0.7 * model_rul + 0.3 * engineer_rul`. Updates the in-memory estimate for that equipment. Persists the correction to `data/feedback/rul_corrections.jsonl` (append-only). On server restart, replays corrections from file to restore adjusted estimates. Returns `impact='rul_adjusted'` immediately — the feedback response is instant, visible, and correct.

No LightGBM dependency. No `requirements.txt` addition required. No retraining. No silent background task failures.

Tech: lifelines 0.29 WeibullAFTFitter, numpy, scipy, sklearn StandardScaler, joblib.

---

### Step 3.3 — Train all models offline, commit artifacts
MUST | FAST | SMOOTH | DOESN'T-BREAK | S

`scripts/train_models.py` — trains all 6 IsolationForest + 6 Weibull models, validates outputs (non-null predictions on 3 test rows), writes 12 joblib files to `data/models/`. `make train` runs this. Commit artifacts. Demo never triggers retraining.

---

## PHASE 4 — Agentic Core
*Day 3–6. The highest-risk phase. Budget 30h here. Parallel-build nodes after graph scaffold.*

### Step 4.1 — LangGraph StateGraph + typed AgentState schema
MUST | ACCURATE | NO-ERRORS | Technical Implementation & Innovation | S

`wizard/graph/state.py` — `AgentState` TypedDict with all graph fields: `session_id, turn_id, equipment_id, raw_query, intent, sensor_snapshot, retrieved_docs, diagnosis_result, rul_result, rca_result, maintenance_plan, active_alerts, feedback_log, final_response, citations, confidence, error`. Every sub-type is a Pydantic v2 `BaseModel`. Each node owns exactly one state slice (prevents race conditions under `Send()` parallel dispatch).

`wizard/graph/graph.py` — compile with `checkpointer = SqliteSaver.from_conn_string('data/sessions.db')`. Every node write validated by Pydantic at write time. `max_iterations=10` hard cap on the graph to prevent runaway loops.

`GET /health` stub added here (returns `503 Not Ready` until fully initialized) — this allows Phase 6 UI sidebar health dot to be built immediately, filled in properly at Step 4.3.

Tech: langgraph 0.2.x, langgraph-checkpoint-sqlite, Pydantic v2, Python 3.12 TypedDict.

---

### Step 4.2 — Supervisor + 7 specialist nodes (the agentic graph)
MUST | FAST | EFFICIENT | ACCURATE | NO-ERRORS | Effective Use of Agentic-AI Frameworks | Technical Implementation & Innovation | L

**[CRITIQUE FIX — low severity: production_impact_norm lookup now defined; urgency formula complete.]**

`wizard/graph/nodes.py`. Build order:

(1) `IntentClassifierNode` — Gemini Flash 2.0 free-tier. 7 classes: `diagnosis | rul_query | sop_lookup | rca_query | maintenance_plan | status_lookup | unknown`. Cached system prefix (<200 tokens). Fallback chain: Gemini timeout/429 → Ollama llama3.2:3b → keyword regex classifier (30-line, zero deps). The keyword classifier is the guaranteed floor: maps "RUL" → rul_query, "fault/error" → diagnosis, "SOP/procedure/how to" → sop_lookup, "why/root cause" → rca_query, "maintenance plan/schedule" → maintenance_plan, unknown → diagnosis (safe default).

(2) `RAGNode` — calls `retriever.query_rag()`, writes `retrieved_docs + citations`, no LLM call.

(3) `MLNode` — calls `AnomalyDetector.predict(sensor_player.get_snapshot(equipment_id))` + `RULEstimator.predict()`. Also looks up `production_impact_norm` from the static `impact_table.csv` singleton (loaded at startup). Computes urgency score: `0.4*(1-RUL_norm) + 0.3*anomaly_score_norm + 0.3*production_impact_norm`. Writes results to `AgentState`. Calls `AlertEngine.evaluate()` (stub in Phase 3, real in Phase 5 — see Step 5.3 for wiring).

(4) `DiagnosisNode` — claude-sonnet-4-6 with cached system prompt, structured `DiagnosisResult` output.

(5) `RCANode` — same pattern, outputs 5-Why chain grounded in retrieved incident reports.

(6) `MaintenancePlannerNode` — takes `DiagnosisResult + spare_parts_catalog + maintenance_records`, outputs `MaintenancePlan` with numbered repair steps + parts checklist + urgency score.

(7) `AlertNode` — rule-based, no LLM, calls `AlertEngine`.

(8) `FeedbackNode` — writes to ChromaDB correction collection + feedback log.

Supervisor uses conditional edges routing on `state.intent`. `RAGNode + MLNode` always dispatch in parallel via `Send()` API. Nodes 4–6 fire sequentially only for complex diagnostic queries.

Tech: langgraph 0.2.x StateGraph + Send() API, anthropic SDK 0.26+, google-generativeai 0.7.

---

### Step 4.3 — Multi-turn session memory + FastAPI server
MUST | DOESN'T-BREAK | Natural-language multi-turn interaction | SMOOTH | S

`wizard/api/server.py`. `POST /chat`: accepts `{session_id: UUID, message: str, equipment_id: str}`. Graph compiled with SqliteSaver — `graph.stream(input, config={'configurable': {'thread_id': session_id}})` automatically persists and restores `AgentState`. `GET /session/{session_id}/history` returns full turn list. `GET /health`: validates 6 datasets readable + 12 joblib models loadable + ChromaDB collection accessible + config valid. Returns `{status: ok|degraded, checks: dict}` — replaces the Phase 4.1 stub 503. `uvicorn --workers 1` for demo (SqliteSaver single-writer).

Tech: langgraph-checkpoint-sqlite, FastAPI 0.111, uvicorn 0.29, python-ulid.

---

### Step 4.4 — Async hallucination verifier (NICE-TO-HAVE)
NICE | ACCURATE | DOESN'T-BREAK | Explainable Recommendations | S

`wizard/graph/verifier.py`. After primary LLM produces `MaintenanceAnswer`, fire a background Haiku 4.x verifier checking each recommendation against its cited chunks. If any claim is `supported=False`, tag `[UNVERIFIED]` in the UI — never block or re-generate. Hard timeout 3s. Cut if Phase 4 is running over budget; citation pills alone satisfy requirement 4.

Tech: claude-haiku, asyncio.gather, Pydantic v2 VerifierResult.

---

### Step 4.5 — Prompt caching + small-model routing
MUST | FAST | EFFICIENT | Technical Implementation & Innovation | S

`wizard/routing/budget.py`. Mark stable system prompt prefix (role + equipment registry + citation instructions, ≥1024 tokens padded with taxonomy table) with `cache_control: {type: 'ephemeral'}`. Routing: simple fact queries (`status_lookup | sop_lookup`) → Gemini Flash; diagnostic/rca/maintenance_plan → claude-sonnet-4-6 with cached prefix. Per-call accounting: log `{input_tokens, cached_input_tokens, output_tokens, latency_ms, model_used, cache_hit}` to `data/logs/llm_calls.jsonl`. Hard `asyncio.wait_for` timeouts: 2.5s Gemini/intent, 8s Sonnet. On timeout: return last cached state with `fallback_used=True`.

Tech: Anthropic SDK `cache_control`, google-generativeai Gemini Flash, asyncio.wait_for.

---

### Step 4.6 — Feedback ingestion and RAG/RUL correction loop
MUST | ACCURATE | SMOOTH | Feedback-driven improvement | Business Impact & Feasibility | M

**[CRITIQUE FIX — critical gaps: (a) ChromaDB correction_weight unsound → fixed in Step 2.3; (b) LightGBM n=1 retrain → replaced with Bayesian correction in Step 3.2; this step wires both into the API.]**

`wizard/feedback/loop.py`. `POST /feedback` accepts `{session_id, turn_id, correction_type: Literal['wrong_diagnosis','wrong_rul','wrong_rca','confirm'], correction_text: str, corrected_rul_days?: float}`.

Actions:
- Always: append `FeedbackRecord` to `data/feedback/corrections.jsonl`.
- If `wrong_diagnosis` or `wrong_rca`: call `chromadb.collection.upsert()` with new chunk tagged `feedback_source=engineer_correction`. The retriever (Step 2.3) will surface this in top-3 on the next query due to correction-aware re-ranking.
- If `wrong_rul` + `corrected_rul_days` present: call `RULEstimator.apply_correction(equipment_id, corrected_rul_days)` (Bayesian update from Step 3.2). Immediate in-memory adjustment. Persisted to `rul_corrections.jsonl`.
- If `confirm`: log positive signal, no model change.
- Return: `{accepted: True, impact: 'rag_updated' | 'rul_adjusted' | 'logged'}`.

Demo flow: engineer corrects once → same question next turn surfaces corrected chunk at top → SMOOTH + requirement 6 visibly satisfied within one turn. No retraining. No background task risk.

Tech: chromadb collection.upsert(), wizard/ml/rul_estimator.py Bayesian update, FastAPI.

---

### Step 4.7 — Proactive maintenance planner (autonomous trigger)
MUST — do not cut | Effective Use of Agentic-AI Frameworks | Technical Implementation & Innovation | Business Impact & Feasibility | ACCURATE | SMOOTH | M

**[CRITIQUE FIX — high severity: APScheduler BackgroundScheduler creates asyncio deadlock. Replaced with asyncio.create_task() inside FastAPI lifespan.]**

`wizard/graph/proactive.py`. Background asyncio task started inside FastAPI `@asynccontextmanager lifespan` (not APScheduler BackgroundScheduler — that creates thread/asyncio deadlocks when calling `graph.ainvoke`). Pattern:

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(proactive_poll_loop())
    yield
    task.cancel()

async def proactive_poll_loop():
    while True:
        await asyncio.sleep(30)  # 30s poll interval
        for equipment_id in EQUIPMENT_IDS:
            snapshot = sensor_player.get_snapshot(equipment_id)
            rul = rul_estimator.predict(snapshot)
            if rul.rul_days_p50 < 3:  # 72h threshold
                await trigger_proactive_plan(equipment_id, snapshot)
```

When triggered: `await graph.ainvoke(ProactiveInput(...))` — fully async, no thread boundaries crossed. Checks `spare_parts_catalog` for availability and lead time. Checks simulated shift schedule (CSV). Pushes `ProactiveAlert` to SSE stream (Step 5.2) and to logbook.

Demo seeding: at demo start, call `POST /sensor/speed` with `multiplier=100`. At 90 elapsed real seconds, the sensor playback (Step 1.4) has advanced ~3000 rows. `EAF-04`'s degradation curve (seeded in Step 1.1) crosses `rul_p50 < 3 days` at this row. The proactive poll fires, autonomously invokes the full graph, pushes `CRITICAL ProactiveAlert` to the SSE stream, which the Streamlit alert page picks up via the autorefresh poller (Step 6.8).

Tech: asyncio.create_task(), FastAPI lifespan context manager, LangGraph `graph.ainvoke`, Pydantic ProactiveAlert.

---

## PHASE 5 — Alerting Engine
*Day 6. Wires ML predictions to the UI alert layer.*

### Step 5.1 — Rule-based alert engine with tiered severity
MUST | FAST | ACCURATE | Real-time alerting | DOESN'T-BREAK | S

`wizard/alerts/engine.py`. `AlertEngine.evaluate(anomaly_result, rul_result)` — pure rule evaluation, no LLM. Rules: CRITICAL if `anomaly_score > 0.85 OR rul_days_p50 < 7`; HIGH if `anomaly_score > 0.65 OR rul_days_p50 < 30`; MEDIUM if `anomaly_score > 0.45 OR rul_days_p50 < 90`; LOW otherwise. Each triggered alert: `Alert(alert_id, equipment_id, severity, title, body, triggered_at, rule_id, rul_p50, recommended_action_brief)`. Write to `data/alerts.jsonl` (append-only, line-buffered flush) and to SQLite `alerts.db`. Pre-seed `alerts.db` with one CRITICAL alert for `EAF-04` before recording — belt-and-suspenders backup if sensor playback is slow.

Tech: Python dataclass-based predicates, sqlite3 (stdlib).

---

### Step 5.2 — SSE alert stream + role-based routing
MUST | FAST | SMOOTH | DOESN'T-BREAK | Real-time alerting | Scalability & Real-World Applicability | S

`wizard/alerts/stream.py`. FastAPI `GET /alerts/stream` — SSE endpoint (`sse-starlette 1.8`) tailing `data/alerts.jsonl`. `GET /alerts/active` — returns unacknowledged alerts from SQLite. On new connection: immediately push historical unresolved alerts so reconnects never lose state. Role-based routing: CRITICAL+HIGH → `data/notifications/maintenance_engineer.jsonl`; HIGH+ → `data/notifications/plant_manager.jsonl`; CRITICAL → `data/notifications/safety_officer.jsonl`. Demo: show 3 role views — each sees a different alert subset.

Tech: sse-starlette 1.8, SQLite, FastAPI.

---

### Step 5.3 — AlertEngine stub → MLNode wiring (ordering fix)
MUST | DOESN'T-BREAK | Real-time alerting | S

**[CRITIQUE FIX — medium severity: MLNode (Phase 4) built before AlertEngine (Phase 5) exists; predictions never route to alerts without explicit wiring step.]**

Two-step resolution: (a) In Step 4.2, MLNode imports `AlertEngine` from `wizard/alerts/engine.py` but calls a stub: `class AlertEngine: def evaluate(self, a, r): return None`. This means MLNode compiles and runs in Phase 4 without the real engine. (b) This step replaces the stub with the real `AlertEngine` (now built in Step 5.1). The import path does not change. MLNode calls `AlertEngine.evaluate()` at the end of every ML inference. If the result is non-None (an alert was triggered), the alert is appended to `data/alerts.jsonl` and the SSE stream fires. Zero changes to MLNode code — only the imported class changes.

Tech: Python stub pattern, wizard/alerts/engine.py.

---

## PHASE 6 — UX / Dashboard
*Day 6–7. Streamlit only. All backend calls use httpx.Client (sync) — never AsyncClient, never asyncio.run().*

### Step 6.1 — Streamlit app structure + sync HTTP constraint
MUST | EASY-TO-USE | SMOOTH | DOESN'T-BREAK | S

**[CRITIQUE FIX — high severity: asyncio nesting crash if any Streamlit page uses AsyncClient or asyncio.run().]**

`wizard/ui/app.py` — Streamlit 1.35, `layout='wide'`. Five pages via `st.navigation`: `01_Chat.py, 02_Dashboard.py, 03_Alerts.py, 04_Logbook.py, 05_Settings.py`.

`wizard/ui/state.py` — initializes ALL session state keys before any page renders. Also defines `_http_client` singleton: `httpx.Client(base_url='http://localhost:8000', timeout=15.0)` initialized once at session start via `st.session_state.setdefault('http_client', httpx.Client(...))`. This singleton is used by every page for every backend call. No `httpx.AsyncClient` anywhere in the UI layer. No `asyncio.run()` anywhere in any Streamlit callback. This is a hard constraint — add a comment to `state.py`: `# CONSTRAINT: All HTTP calls use httpx.Client (sync). asyncio.run() in Streamlit causes RuntimeError: cannot run nested event loops.`

Sidebar: active equipment selector, unread-alert badge count, system health dot (green/amber/red from `GET /health`), last-updated timestamp. `.streamlit/config.toml`: `server.maxUploadSize=50, server.requestTimeout=120`.

Tech: streamlit 1.35, httpx 0.27 (sync only), python-dotenv.

---

### Step 6.2 — Chat interface: streaming + citation pills + feedback widget
MUST | FAST | ACCURATE | EASY-TO-USE | SMOOTH | Explainable Recommendations | M

`wizard/ui/pages/01_Chat.py`. `st.chat_input` + `st.chat_message` history from session state. On submit: `st.status('Routing to agents...')` → call `POST /chat` via sync `httpx.Client` → `st.write_stream`. Per assistant message: (1) citation pills — `st.badge` per source, clickable `st.expander` with chunk text + doc name + section; (2) confidence badge (verified/unverified/low); (3) agent trace expander (collapsed, shows nodes fired + latency_ms); (4) feedback widget — thumbs-up/down with `key=f'fb_{message_id}'`, thumbs-down reveals correction text input, submit calls `POST /feedback` via sync HTTP → `st.toast('Correction applied — RAG updated')`. Never use `st.form` for feedback — it clears the entire chat on submit.

Tech: streamlit, httpx 0.27 (sync), st.write_stream, st.toast.

---

### Step 6.3 — Equipment health dashboard
MUST | EASY-TO-USE | ACCURATE | SMOOTH | FAST | M

`wizard/ui/pages/02_Dashboard.py`. Top: 3 `st.metric` tiles (Active Alerts, Equipment at Risk, Avg RUL days). Middle: Plotly heatmap (6 equipment × 7-day health score). Below: RUL gauge cluster (one `go.Indicator` per critical equipment, `plotly make_subplots`, rendered once). Anomaly timeline: Plotly scatter of last 24h readings vs normal band, anomaly points as red crosses. All charts `@st.cache_data(ttl=30)`. "Simulate Fault" button sets `st.session_state['simulate_fault']` which the alert engine polling loop reads to inject a sensor spike.

Tech: plotly 5.22, st.cache_data, st.metric.

---

### Step 6.4 — Alert feed: severity tiers + acknowledge-to-logbook
MUST | EASY-TO-USE | SMOOTH | DOESN'T-BREAK | NO-ERRORS | S

`wizard/ui/pages/03_Alerts.py`. Filterable alert list. Each card: severity badge, equipment ID, description, timestamp, downtime impact, "Recommended Action" button (deeplinks to Chat via `st.query_params`). Role dropdown filter. "Acknowledge" button: marks resolved in SQLite, appends logbook entry, decrements unread count. `st.toast` on new alert with 5s debounce via `st.session_state['last_toast_time']`.

Alert list populated from `st.session_state['alerts']`, which is kept current by the autorefresh poller (Step 6.8 — built immediately after this step).

Tech: streamlit, st.toast, st.query_params.

---

### Step 6.5 — Explainability drill-down panel (NICE-TO-HAVE)
NICE | ACCURATE | EASY-TO-USE | SMOOTH | M

`wizard/ui/components/explainability_panel.py`. `st.dialog` modal on "Why?" click: retrieved doc excerpt + Plotly confidence bar + agent reasoning chain. Cut if Day 7 is at risk — citation pills satisfy requirement 4.

---

### Step 6.6 — UI error envelopes + input validation
MUST | DOESN'T-BREAK | NO-ERRORS | SMOOTH | S

All backend calls wrapped in `try/except` with human-readable `st.warning` / `st.error` — never a traceback. Error messages: timeout → "Agent took too long — showing cached analysis"; RAG failure → "Knowledge base lookup failed — please rephrase"; model error → "Prediction unavailable — showing last known RUL". Chat input validation: 5–500 chars, strip whitespace, reject pure-whitespace. Global health check at app startup: if `GET /health` returns unhealthy, show banner "Backend agents starting up — first response may take 10s". Never call `st.stop()` inside a callback.

Tech: try/except, st.warning/st.error, st.query_params.

---

### Step 6.7 — Logbook + Settings pages
MUST | EASY-TO-USE | NO-ERRORS | DOESN'T-BREAK | S

**[CRITIQUE FIX — critical gap: both nav pages listed in Step 6.1 but never built, causing NameError or blank import when judges click through navigation.]**

`wizard/ui/pages/04_Logbook.py`: table of all acknowledged alerts + repair actions from SQLite `acknowledged_alerts` table. Filterable by equipment ID and date range (`st.date_input`). "Export CSV" button writes `st.download_button` from pandas `DataFrame.to_csv()`. Each row: alert ID, equipment, severity, acknowledged at, acknowledged by (role), notes. Pre-populated with 5 historical entries in `data/logbook_seed.json` so the page is never empty on first load.

`wizard/ui/pages/05_Settings.py`: read-only display of current `.env` values (keys masked: show only first 8 chars + `...`). API key format validation on display (green checkmark if prefix matches). Button "Run health check now" calls `GET /health` and shows result. Button "Reset demo state" calls `POST /sensor/reset` and `make reset`. No editable fields — settings are env-file managed. This prevents judges accidentally breaking a running demo by changing a setting in the UI.

Tech: streamlit, pandas, sqlite3, st.download_button.

---

### Step 6.8 — Real-time alert polling (Streamlit autorefresh)
MUST | SMOOTH | DOESN'T-BREAK | NO-ERRORS | Real-time alerting | S

**[CRITIQUE FIX — critical gap: SSE stream from server cannot push to Streamlit; Streamlit has no native push model. Without polling, alert toasts never fire.]**

Add `streamlit-autorefresh` to `requirements.txt`. In `wizard/ui/app.py` main layout (runs on every page), add:

```python
from streamlit_autorefresh import st_autorefresh
st_autorefresh(interval=3000, key="alert_poller")  # 3s interval
```

On each refresh tick, call `GET /alerts/active` via the sync `httpx.Client` singleton. Compare returned alert IDs against `st.session_state['alerts']` (previously seen). For each new alert: append to `st.session_state['alerts']`, increment `st.session_state['unread_alerts']`, call `st.toast(f"[{severity}] {alert.title}", icon="🔴" if severity=="CRITICAL" else "⚠️")`. This is the mechanism that makes the CRITICAL toast appear on screen at 90s into the demo without any user action.

Add `streamlit-autorefresh>=0.1.0` to `requirements.txt`. Verify it installs cleanly on Python 3.12.

Tech: streamlit-autorefresh 0.1.x, httpx 0.27 (sync), st.toast.

---

## PHASE 7 — Robustness & Eval
*Day 7–8. This phase exists to prevent demo-day failures.*

### Step 7.1 — Hardened LLM client: timeouts + backoff + circuit-breaker
MUST | FAST | DOESN'T-BREAK | NO-ERRORS | EFFICIENT | M

`wizard/core/llm_client.py`. Per-call timeout (8s Sonnet, 2.5s Haiku/Gemini), 3-attempt exponential backoff with jitter on 429/500/503 (`tenacity`), circuit-breaker (5 failures in 60s → open for 120s). On circuit open: return canned `AgentResult(status='degraded', fallback_used=True)`. Expose `token_in, token_out, latency_ms, cache_hit` on every response.

Tech: tenacity 8.x, httpx 0.27 timeout, anthropic SDK 0.26+.

---

### Step 7.2 — Input validation at conversation boundary
MUST | NO-ERRORS | DOESN'T-BREAK | SMOOTH | S

`wizard/api/validation.py`. `ConversationTurn` Pydantic model: `message (str, max 2000 chars, strip HTML)`, `session_id (UUID4)`, `equipment_id (Literal of canonical IDs from taxonomy)`. Prompt-injection guard: reject narrow patterns (`re` check: starts with "ignore", contains "system prompt", contains "you are now") with graceful 400 + user-friendly message. Log every rejection to `data/logs/audit.jsonl`.

Tech: Pydantic v2 field_validator, bleach 6.x, re, FastAPI 422.

---

### Step 7.3 — Per-agent graceful degradation tiers
MUST | DOESN'T-BREAK | NO-ERRORS | SMOOTH | ACCURATE | M

`wizard/core/degradation.py`. Three tiers per node: Tier 1 = full answer with citations; Tier 2 = partial answer from cached `AgentState` last-known values with "Based on data as of [timestamp]" disclaimer; Tier 3 = "Insufficient live data — here is the standard SOP for this fault class" from pinned knowledge base. Tool failures always route to Tier 2 or 3 — never error screen. Always pass `equipment_id` through fallback for contextually correct SOP lookup.

Tech: asyncio.wait_for per tool call, structlog.

---

### Step 7.4 — Performance instrumentation
MUST | FAST | EFFICIENT | SMOOTH | Technical Implementation & Innovation | M

`wizard/core/metrics.py`. `TurnMetrics` context manager on `/chat`: record `wall_clock_ms, llm_tokens_in, llm_tokens_out, cached_tokens, rag_latency_ms, ml_latency_ms, agent_hops, degradation_tier`. Budget thresholds (warn, never block): P95 end-to-end 4s, max tokens out 1500, max hops 3. `GET /metrics` returns P50/P95 per-node over last 100 turns. Live latency shown in Streamlit sidebar. Cache hit rate shown in Dashboard.

Tech: time.perf_counter, structlog 24.x.

---

### Step 7.5 — Fallback tier verification + Ollama install check
MUST | DOESN'T-BREAK | NO-ERRORS | S

**[CRITIQUE FIX — high severity: Ollama fallback cited in Step 4.2 but never installed, tested, or gracefully degraded. Added explicit verification step.]**

`scripts/verify_fallbacks.py`. Sequentially tests: (1) Call `POST /chat` with Gemini key blanked in env → assert intent classification returns a result (Ollama path fires); (2) Call `POST /chat` with both Gemini and Ollama unavailable → assert keyword regex classifier fires and returns one of the 7 intents; (3) Call `POST /chat` with Anthropic key blanked → assert `status='degraded'` with `fallback_used=True` and no traceback; (4) Call `POST /chat` with ChromaDB path deleted → assert Tier-3 degradation (SOP fallback) activates. Document the keyword regex classifier explicitly in `docs/ARCHITECTURE.md` Section 5 as the guaranteed last-resort fallback — judges assessing DOESN'T-BREAK need to see this documented.

If Ollama is not installed on the demo machine: the keyword regex tier still works. Add a note to `README.md`: "Ollama is optional. Install for offline fallback: `curl https://ollama.ai/install.sh | sh && ollama pull llama3.2:3b`".

Tech: pytest, httpx, subprocess for Ollama check.

---

### Step 7.6 — Golden eval suite runner
MUST | ACCURATE | DOESN'T-BREAK | NO-ERRORS | Technical Implementation & Innovation | M

**[CRITIQUE FIX — high severity: eval suite was in Phase 7 with the note "write before running system." golden.jsonl is now frozen in Phase 0 Step 0.4. This step only runs it.]**

`scripts/eval_run.py`. Reads `data/evals/golden.jsonl` (frozen since Phase 0 — no changes allowed). Sends each query to `POST /chat` via httpx. Checks: HTTP 200, `source_refs` non-empty for RAG questions, answer contains any keyword from `expected_answer_contains`, latency under `max_latency_ms`. Emit pass/fail to console via Rich + `data/evals/regression_report.md`. `--check` flag exits non-zero if pass rate < 88% (22/25). Run before every demo rehearsal and before final ZIP assembly.

Tech: pytest 8.x, httpx, Rich, pandas.

---

## PHASE 8 — Demo & Submission
*Day 8–9. No new features after Day 7. Polish, record, package.*

### Step 8.1 — Pre-baked demo happy path + demo mode
MUST | SMOOTH | EASY-TO-USE | DOESN'T-BREAK | NO-ERRORS | S

`demo/HAPPY_PATH.md` — 5-step script with target timestamps:
- 0:00–0:20 — Open Dashboard, point to `EAF-04` in red gauge (pre-seeded from Step 5.1).
- 0:20–0:50 — Call `POST /sensor/speed` with `multiplier=100` (or click "Start Demo" button). Watch playback advance. At 90s elapsed, alert badge increments + CRITICAL toast appears without user action.
- 0:50–1:30 — Click "Recommended Action" on the CRITICAL alert (pre-fills Chat with EAF-04 bearing fault query). Agent streams response with citation pills.
- 1:30–2:00 — Proactive maintenance plan appears as a second message (no user input — the agentic proof moment).
- 2:00–2:30 — Thumbs-down on a recommendation → type correction → "RAG updated" toast → re-ask same question → corrected answer at top.
- 2:30–3:00 — Switch to Architecture tab, narrate LangGraph diagram (nodes, edges, SqliteSaver).

`demo/demo_reset.py` — resets SQLite transient alerts (keeps one pre-seeded CRITICAL), clears session state, calls `POST /sensor/reset`. Idempotent — can run between rehearsal takes.

`?demo=true` URL param enables response caching mode: backend checks `data/demo_cache.json` (pre-computed JSON responses for 5 scripted queries) before hitting LLM API — guarantees <1s responses during recording. Populate `demo_cache.json` during final rehearsal.

Tech: demo_reset.py, data/demo_cache.json, st.query_params.

---

### Step 8.2 — Architecture document (finalize all 8 sections)
MUST | Problem Understanding & Approach | Technical Implementation & Innovation | Presentation & Communication Quality | Scalability & Real-World Applicability | M

Finalize `docs/ARCHITECTURE.md` (stub created in Phase 0 Step 0.1, updated incrementally through the build). Replace the Mermaid placeholder with the actual diagram from `graph.get_graph().draw_mermaid()`. Add `SAMPLE_IO.md` as a subsection in Section 8 or as a separate `docs/SAMPLE_IO.md`: 3 complete query-response pairs with full citation JSON visible. Include `docs/KNOWN_FAILURE_MODES.md`: 5 edge cases with exact fallback behavior (unknown equipment ID, sensor data gap, empty history, LLM timeout, missing spare part). Both files are required ZIP artifacts.

Tech: LangGraph draw_mermaid(), Mermaid, Markdown.

---

### Step 8.3 — Business impact narrative
MUST | Business Impact & Feasibility | Scalability & Real-World Applicability | Problem Understanding & Approach | S

`docs/BUSINESS_IMPACT.md`. Anchored to Tata Steel's published KPIs. Cost estimate: Gemini Flash pricing × 500 queries/day = ~$1.50/day = $547/year. Deployment path: FastAPI containerizable, Streamlit deployable on internal Kubernetes. Scalability: new equipment type requires only a new SOP + sensor schema extension. NEEDS INPUT: verify per-minute downtime cost from a published source before including absolute cost.

---

### Step 8.4 — Demo video (3.5 minutes)
MUST | SMOOTH | EASY-TO-USE | Presentation & Communication Quality | M

OBS Studio, 1920×1080, 30fps, H.264 MP4. Use `demo_cache.json` for all LLM calls during recording. Follow `HAPPY_PATH.md` timestamps. Text overlay throughout: "[All data is synthetic — generated for demonstration]". Add captions (Kapwing/DaVinci). Upload YouTube unlisted; link in README. Compress with ffmpeg to <80MB.

---

### Step 8.5 — Submission ZIP assembly + smoke test
MUST | SMOOTH | DOESN'T-BREAK | NO-ERRORS | Presentation & Communication Quality | S

**[CRITIQUE FIX — medium severity: SAMPLE_IO.md now explicitly required in Step 8.2 and listed here. PYTHONPATH fixed via pyproject.toml in Step 0.2. Secret key grep mandatory.]**

ZIP structure:
```
src/           — all Python source (wizard/ + scripts/ + demo/)
data/          — committed synthetic datasets + model artifacts + chroma_db + bm25_index.pkl
docs/          — ARCHITECTURE.md + BUSINESS_IMPACT.md + KNOWN_FAILURE_MODES.md + SAMPLE_IO.md
README.md      — 5-command install + YouTube link + problem statement + requirements mapping
requirements.txt  — pinned via pip freeze
pyproject.toml
.env.example   — all keys documented, no real values
Makefile
.python-version
```

`docs/SMOKE_TEST.md` — 20-item checklist:
1. Fresh venv + `make setup` + `make train` + `make run` succeeds on Python 3.12
2. `GET /health` returns `status: ok`
3. All 7 mandatory requirements demonstrable via 8 scripted demo questions
4. Eval suite passes ≥22/25 (`make smoke`)
5. No Python traceback in browser console
6. Chrome DevTools Fast 3G throttle: streaming starts within 2s
7. Gibberish query returns graceful 400 with human-readable message
8. LLM kill test (blank ANTHROPIC_API_KEY) triggers Tier-3 degradation, not crash
9. Feedback correction → re-ask → corrected answer in top-3 (retrieval test)
10. RUL correction → re-query → updated RUL returned
11. `POST /sensor/speed multiplier=100` + wait 90s → CRITICAL alert toast fires
12. Role dropdown changes visible alert set
13. Acknowledge alert → alert disappears from active list → logbook entry appears
14. Chat history persists across browser refresh (SqliteSaver test)
15. Architecture doc renders correctly as PDF
16. Demo video plays without audio sync issues
17. All 5 nav pages load without error (Chat, Dashboard, Alerts, Logbook, Settings)
18. `?demo=true` param enables cache mode (responses < 1s)
19. `make reset` returns system to clean state for next demo run
20. ZIP extracts cleanly; no hidden files

Mandatory pre-ZIP security grep:
```bash
grep -r 'sk-ant-api' . --include="*.py" --include="*.json" --include="*.env"
grep -r 'AIzaSy' . --include="*.py" --include="*.json" --include="*.env"
```
Any hit = do not zip. Fix, then re-run.

---

## Judging Axis Coverage Matrix

| Axis | Covering Steps | Demo Moment |
|---|---|---|
| **A — Problem Understanding & Approach** | 0.1, 0.6, 8.2, 8.3 | Architecture doc lede + business impact numbers |
| **B — Effective Use of Agentic-AI Frameworks** | 4.1, 4.2, 4.7, 5.3 | Proactive alert fires at 90s with no user input |
| **C — Technical Implementation & Innovation** | 2.3, 2.4, 3.1, 3.2, 4.1, 4.2, 4.5, 7.4 | LangGraph Send() parallel + Weibull RUL + prompt caching dashboard |
| **D — Scalability & Real-World Applicability** | 1.2, 4.3, 5.2, 8.3 | Multi-role alert routing + session persistence + deployment path |
| **E — Presentation & Communication Quality** | 0.1, 8.1, 8.2, 8.3, 8.4 | Architecture Mermaid diagram narrated on camera |
| **F — Business Impact & Feasibility** | 0.1, 4.7, 8.3 | 22% downtime reduction anchor + $547/year LLM cost estimate |
| **G — FAST** | 2.1, 2.2, 4.5, 7.1, 7.4, 8.1 | P50 latency shown live in sidebar; demo_cache.json for recording |
| **H — EFFICIENT** | 2.2, 4.5, 7.4 | Cache hit rate on Dashboard; token spend logged per turn |
| **I — ACCURATE** | 0.4, 0.5, 2.3, 2.4, 3.1, 3.2, 4.6, 7.6 | Citation pills per claim; correction improves next answer |
| **J — EASY-TO-USE** | 6.1, 6.2, 6.3, 6.4, 6.7 | All 5 nav pages functional; deeplink from alert to pre-filled chat |
| **K — DOESN'T-BREAK** | 0.2, 0.3, 3.3, 4.7, 5.3, 7.1, 7.3, 7.5 | Fallback tiers documented; health endpoint green before demo |
| **L — NO-ERRORS** | 0.2, 0.3, 4.6, 6.6, 7.2, 7.5, 8.5 | 20-point smoke test; secret-key grep; graceful 400 on bad input |
| **M — SMOOTH** | 1.4, 4.7, 5.2, 6.8, 8.1 | Proactive alert toast at 90s; correction toast; demo_cache.json |

**Previously failing axes and their fixes:**
- I (ACCURATE): golden.jsonl written in Phase 0 (unbiased); correction-aware re-rank verifiable in one turn.
- J (EASY-TO-USE): Logbook + Settings pages added in Step 6.7.
- K (DOESN'T-BREAK): APScheduler replaced with asyncio.create_task() in Step 4.7; Ollama fallback + regex tier in Step 7.5.
- L (NO-ERRORS): .env wiring + config validation in Step 0.2; pip install -e . in Step 0.2; LightGBM removed in Step 3.2.
- M (SMOOTH): sensor playback engine in Step 1.4; SSE-to-Streamlit wiring via autorefresh in Step 6.8; asyncio-safe proactive trigger in Step 4.7.

---

## MVP Cut Order — Solo 9-Day Build

Cut strictly in this order when time pressure forces a choice. Stop cutting when the remaining system satisfies all 7 mandatory functional requirements and all 13 judging axes have at least one Y cell.

| Priority | Step | What is Lost | Acceptable? |
|---|---|---|---|
| Cut 1st | 2.3 CrossEncoder reranker | Slightly lower retrieval precision | Yes — RRF + correction-aware re-rank is sufficient |
| Cut 2nd | 4.4 Async hallucination verifier | No [UNVERIFIED] tags on claims | Yes — citation pills satisfy requirement 4 |
| Cut 3rd | 6.5 Explainability drill-down modal | No "Why?" dialog | Yes — citation pills cover explainability |
| Cut 4th | 7.5/7.6 full 25-question eval | Smaller regression suite | Yes — run 10 manual smoke-test Q&As instead |
| **Never cut** | 0.2 Makefile + .env | Judges cannot run it | Fatal |
| **Never cut** | 1.4 Sensor playback | Proactive alert never fires | Fatal |
| **Never cut** | 4.7 Proactive planner | Agentic proof moment gone | Fatal (criterion B) |
| **Never cut** | 5.3 AlertEngine wiring | ML predictions never alert | Fatal |
| **Never cut** | 6.7 Logbook + Settings pages | Broken nav — judges see errors | Fatal |
| **Never cut** | 6.8 Autorefresh poller | Alert toasts never fire | Fatal |
| **Never cut** | 8.5 Smoke test + secret grep | Risk of key leak; broken ZIP | Fatal |

---

## Final Submission / ZIP Checklist

Run through this checklist in order on submission day. Check off each item. Do not skip.

**Code quality**
- [ ] `grep -r 'sk-ant-api'` on full directory returns zero results
- [ ] `grep -r 'AIzaSy'` on full directory returns zero results
- [ ] `make smoke` exits 0 (≥22/25 golden eval)
- [ ] `make reset && make run` starts cleanly on a second machine or fresh virtualenv

**Artifacts committed**
- [ ] `data/synthetic/` — all Parquet files present
- [ ] `data/models/` — all 12 joblib files present
- [ ] `data/chroma_db/` — ChromaDB persistent store committed
- [ ] `data/bm25_index.pkl` — BM25 index committed
- [ ] `data/evals/golden.jsonl` — frozen, unchanged since Phase 0

**Documentation**
- [ ] `docs/ARCHITECTURE.md` — all 8 sections complete, Mermaid diagram renders
- [ ] `docs/BUSINESS_IMPACT.md` — present, KPIs sourced
- [ ] `docs/KNOWN_FAILURE_MODES.md` — 5 edge cases documented
- [ ] `docs/SAMPLE_IO.md` — 3 complete query-response pairs with citations
- [ ] `README.md` — 5-command install (git clone → cp .env.example .env → make setup → make train → make run) + YouTube link + requirements mapping
- [ ] `.env.example` — all keys present, all values are placeholders

**Demo readiness**
- [ ] YouTube video unlisted, link in README, audio in sync
- [ ] `data/demo_cache.json` populated for all 5 scripted queries
- [ ] `demo/HAPPY_PATH.md` followed exactly during dry run with recording
- [ ] CRITICAL pre-seeded alert visible in Dashboard before demo starts
- [ ] `POST /sensor/speed` confirmed triggers EAF-04 proactive alert at ~90s

**ZIP**
- [ ] ZIP extracts to a single top-level directory (not a flat archive)
- [ ] ZIP size < 100MB (model artifacts + chroma_db are the risk)
- [ ] Total file count sanity: `unzip -l submission.zip | wc -l` > 50 (not accidentally empty)
