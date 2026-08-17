# Maintenance Wizard — Audit + Change Plan
## (a) Run fully on the Claude Max subscription (NO API key) · (b) Wire in the flagship dataset

**Audited:** 2026-06-09 · **Build:** `round_2/maintenance-wizard/` (~22.6k LOC in `wizard/`) · **Dataset:** `round_2/dataforge/datasets/steel-maintenance-flagship/`
**Hard constraint:** Boss has only a Claude Max **subscription** (`CLAUDE_CODE_OAUTH_TOKEN`), never an API key. Orchestration LLM runs via Claude Agent SDK / `claude -p`. Everything else stays local/CPU/free. Subscription has session/rate limits → design must be **local-first, LLM-sparing, cache-heavy**; the live demo must never die on a 429.

---

## 1. What is already built (verified by reading the source)

| Layer | Module | Status |
|---|---|---|
| **LangGraph supervisor** | `wizard/agents/graph.py`, `nodes.py`, `tools.py` | Built. PEV pattern, deterministic Python router (no LLM routing), 6 nodes: diagnosis → rca → rul → prioritization → plan → report. `MaintenanceState` typed, SqliteSaver checkpoint. |
| **RAG (local, free)** | `wizard/rag/` — `embedder.py` (bge-small **ONNX**), `retriever.py` (LanceDB hybrid + **FlashRank** rerank + **HyDE**), `ingestion.py` (`ingest_directory` globs `*.pdf/*.md/*.txt`), `faithfulness.py` (NLI gate `nli-deberta-v3-small`), `store.py`. | Built. Embeddings/rerank/NLI are all **local CPU** — no key needed. Only HyDE + contextual-prefix touch the LLM. |
| **Knowledge graph** | `wizard/knowledge/` — `fmea_graph.py`, `ontology.py`, `build_kg.py`. Output: `data/kg/steel_plant_fmea.json` + `_ontology.json`. | Built (hand-authored NetworkX FMEA). |
| **ML models** | `wizard/ml/` — `rul_estimator.py` (WeibullAFT), `anomaly_detector.py` (IsolationForest+LSTM-AE), `failure_predictor.py` (LightGBM), `degradation.py`, `rca_engine.py` (3-layer). Trainers: `train_rul.py` (C-MAPSS), `train_failure.py` (AI4I), `train_anomaly.py`. | Built. Trained from **C-MAPSS FD00x + AI4I** (`data/raw/cmapss`, `data/raw/ai4i`) via `dataset_framing.py` cosmetic aliasing. Inference is local joblib — no key. |
| **FastAPI backend** | `wizard/backend/` — `app.py`/`main.py`, SSE, `alerting.py` (APScheduler proactive evaluator + 90s EAF demo trigger), `wrps.py` (WRPS risk), `middleware.py` (pybreaker circuit breaker). | Built. |
| **Streamlit UI** | `wizard/ui/app.py` + `views/01_Chat…05_Settings.py`, `_demo_seed.py`, `_http.py` (sync httpx). | Built (5 pages). |
| **Demo safety** | `data/demo/demo_cache.json` (golden cached `beats`), circuit breaker, deterministic fallbacks in every node. | Built. |
| **Eval / finetune** | `tests/eval/`, `scripts/run_eval.py`, `finetune/` (Qwen2.5-3B QLoRA, stretch). | Built. |
| **Synthetic data (current corpus)** | `wizard/knowledge/generator.py` + `wizard/data/gen_synthetic.py` → `data/synthetic/docs/*.{md,json}` (~SOP/MANUAL/FAR/INC/LOG). This is the RAG corpus today. | Built — **to be replaced by flagship dataset.** |

**Bottom line:** the heavy ML/RAG/graph stack is already local + free. Only the **LLM generation calls** are wired to a paid key (Gemini). That is the entire surface area for change (a).

---

## 2. EXACT API-key call sites to replace (the only LLM egress)

Every LLM call funnels through **LiteLLM** with `model=settings.llm_model_*` (default `gemini/gemini-2.0-flash`) and a Gemini key. There are **7 call sites + 1 config + 2 env files**. No `google.generativeai`/`anthropic` SDK calls exist in `wizard/` (those only live in EDITH's `dataforge/api/scorer/agent.py`, already subscription-first).

| # | File : line | Call | Sync/Async | Notes |
|---|---|---|---|---|
| 1 | `wizard/agents/nodes.py:52-119` | `_llm_complete()` → `litellm.completion(**kwargs)` (line 98); key selected lines 73-78 | **sync** | **Primary entry point** — diagnosis, rca 5-whys enhance, plan two-pass, engineer/supervisor summaries all route here. Replace body. |
| 2 | `wizard/ml/rca_engine.py:425-439` | `litellm.completion(model=settings.llm_model_light, …)` | **sync** | RCA Layer-3 5-whys. |
| 3 | `wizard/rag/retriever.py:141-157` | `_generate_hyde()` → `litellm.completion(model=settings.llm_model_light, …)` | **sync** | HyDE query expansion. Already gracefully falls back to raw query. **Recommend: disable HyDE in demo** (`RAG_HYDE_ENABLED=false`) to save LLM calls — local retrieval is strong enough. |
| 4 | `wizard/rag/ingestion.py:335-358` | contextual-prefix → `litellm.completion(model=settings.llm_model_light, …)` | **sync** | One-time at ingest, per chunk. **Recommend: skip** (`use_contextual_prefix=False`) — 500+ chunks × 1 call each would burn the session budget. Local hybrid+rerank already covers retrieval. |
| 5 | `wizard/backend/wrps.py:327-351` | `await litellm.acompletion(model=settings.llm_model_light, …)` wrapped in `llm_circuit_breaker` | **async** | WRPS 2-sentence narrative. |
| 6 | `wizard/backend/middleware.py:213` | `litellm.acompletion(model=…, messages=…)` (circuit-breaker probe) | **async** | Health/breaker probe — point at shim or stub. |
| 7 | `wizard/knowledge/generator.py:1420-1438` | `instructor.from_litellm(litellm.completion)` | sync | **Data-generation only** (not runtime). Flagship dataset already exists → generator is no longer on the critical path; leave as-is or run once under subscription if regenerating. |
| C | `wizard/core/config.py:92-130` | `llm_provider` default `"gemini"`, `llm_model_*` default `gemini/gemini-2.0-flash`, `gemini_api_key`/`anthropic_api_key`/`openai_api_key` fields | — | Add `subscription` provider + token field. |
| E | `.env` + `.env.example` | `LLM_PROVIDER=gemini`, `GEMINI_API_KEY=…`, `LLM_MODEL_*=gemini/…` | — | Repoint to subscription. **`.env` currently holds a live Gemini key — scrub before ZIP** (PS secret-grep gate). |

**Reference implementation already in-repo:** `dataforge/api/scorer/agent.py:358-443` — `_load_oauth_token()` (env → walk-up to repo `.env`) + `_subscription_review()` (`from claude_agent_sdk import ClaudeAgentOptions, query` → `async for message in query(...)` → collect `block.text` + `message.result`, timeout-guarded, returns `None` on any failure). `jarvis_core/orchestrator.py:22,114` uses the identical `query()` loop. **Mirror this verbatim.**

⚠️ **Gap:** `claude_agent_sdk` is **NOT installed in `maintenance-wizard/.venv`** (only `litellm` + `google_genai` present). The repo-root `.venv` has it. → must `pip install claude-agent-sdk` into the wizard venv (and add to `requirements.txt`). `claude` CLI v2.1.169 is on PATH and `CLAUDE_CODE_OAUTH_TOKEN` is in repo `.env`.

---

## 3. Change list (a) — route LLM through the subscription. ORDERED.

**Strategy: one shim, single chokepoint.** Don't touch 7 sites individually for the transport — make a new `wizard/core/llm.py` that owns the subscription call, then make `_llm_complete` (site 1) and the 3 other runtime sites call it. This keeps the graceful-fallback contract intact.

1. **`requirements.txt`** — add `claude-agent-sdk>=0.1` ; keep `litellm` (still used as the Ollama-offline transport + for the async sites' interface). Remove nothing.
2. **NEW `wizard/core/llm.py`** — port `_load_oauth_token()` + a `subscription_complete(system, user, *, timeout_s=30, max_tokens) -> str | None` (sync wrapper that runs the async `query()` loop via `asyncio.run`/`anyio`, exactly like EDITH `_subscription_review`). Add `async def subscription_acomplete(...)` for the two async sites. **Add a disk cache** (`functools` + a JSON cache keyed on `sha256(system+user+model)` under `data/llm_cache/`) so repeated demo queries cost **zero** LLM calls after first warm — this is the rate-limit defence.
3. **`wizard/core/config.py`** — extend `llm_provider` `Literal[...]` with `"subscription"`; set **default `llm_provider="subscription"`**; add `claude_oauth_token: str = Field(default="", ...)`; keep `gemini_api_key` etc. as optional fallbacks. Leave `llm_model_*` strings (used only when provider≠subscription / Ollama path).
4. **`wizard/agents/nodes.py:52`** — rewrite `_llm_complete` body: if `settings.llm_provider == "subscription"` → call `wizard.core.llm.subscription_complete(system, user, …)`; on `None` → existing deterministic fallback (unchanged). Else keep current LiteLLM path (Gemini/Ollama). **Net: callers and fallbacks untouched.**
5. **`wizard/ml/rca_engine.py:425`** — replace the `litellm.completion` block with a call to `wizard.core.llm.subscription_complete` (provider-gated, same try/except → `[], []` fallback).
6. **`wizard/backend/wrps.py:327`** & **`middleware.py:213`** — swap `await litellm.acompletion(...)` for `await wizard.core.llm.subscription_acomplete(...)`, keeping the `llm_circuit_breaker.call(...)` wrapper and `CircuitOpenError` fallback.
7. **`wizard/rag/retriever.py` (HyDE)** & **`wizard/rag/ingestion.py` (contextual prefix)** — **don't port; disable.** Set `RAG_HYDE_ENABLED=false` in `.env` and call `ingest_directory(..., use_contextual_prefix=False)`. (If wanted later, gate behind the same shim.) Rationale: these are the highest-volume, lowest-value LLM calls — biggest 429 risk.
8. **`.env` / `.env.example`** — `LLM_PROVIDER=subscription`; comment out / delete `GEMINI_API_KEY`; add `# CLAUDE_CODE_OAUTH_TOKEN inherited from repo root .env (via _load_oauth_token walk-up)`. **Scrub the live Gemini key from `.env` now.**
9. **Verify:** `cd maintenance-wizard && .venv/bin/pip install claude-agent-sdk`; run `scripts/verify_demo.py` + `wizard/agents/smoke_agents.py` with `LLM_PROVIDER=subscription` and **no** `GEMINI_API_KEY` set → confirm diagnosis/rca/plan get real Claude text (not `[LLM unavailable]`). Then run `scripts/capture_demo_cache.py` to **pre-bake `data/demo/demo_cache.json`** so the recorded demo replays from cache (0 live calls).

**Net code touched for transport:** 1 new file + 4 runtime edits + config + env. The 7th site (generator) is offline/optional.

---

## 4. Change list (b) — wire in the flagship dataset

The flagship (`steel-maintenance-flagship/`) covers **all four PS input categories** with one consistent 15-asset spine, replacing today's `data/synthetic/docs/` + the C-MAPSS/AI4I framing. Mapping by Wizard subsystem:

| Wizard subsystem | Today | → Flagship source | Change |
|---|---|---|---|
| **RAG corpus** (4.3 + 4.1) | `data/synthetic/docs/*.md` | `knowledge_docs/equipment_manuals/*.md` (13), `knowledge_docs/maintenance_sops/*.md` (13), `operational_failure/failure_analysis_reports/RCA-*.md` (25), `breakdown_summaries.md`, `additional/oem_service_bulletins.md`, `shift_handover_notes.md` | Point `ingest_directory()` at these dirs (md-rich, citation-ready). Re-ingest LanceDB. Spares (`spare_parts_catalog.csv`, 118 rows w/ lead-time) → load as a structured table for the `lookup_spares`/`check_spares` tools (FR + the "order NOW" demo beat). |
| **ML — failure classification** (4.2) | AI4I 2020 via `ai4i_loader.py` | `condition_monitoring/by_equipment/*.csv` — 15 DENSE per-equipment tables, **0% null**, `[timestamp, asset_id, equipment_class, <sensors>, fault_label]`, DataForge composite 89–92 (Excellent) | Retarget `train_failure.py` to read these (label_col=`fault_label`). Drops the synthetic-domain-gap caveat — now steel-native. |
| **ML — RUL regression** (4.2) | C-MAPSS FD00x via `cmapss_loader.py` | `condition_monitoring/rul_trajectories_long.csv` (81,336 rows, run-to-failure, target `rul_cycles`, 0% null) + `sensor_timeseries_long.csv` | Retarget `train_rul.py` (WeibullAFT) + `train_anomaly.py` to the long tables. C-MAPSS can stay as a secondary corroboration set. |
| **Sensor playback / alerting** (4.2) | synthetic stream | `condition_monitoring/raw_sensor_timeseries.csv` (131,040 rows, 363 days hourly) + `anomaly_alerts.csv` (19,918) + `process_condition_indicators.csv` | Feed the APScheduler proactive evaluator + the 90s EAF demo trigger from real spine assets (pick one asset's run-to-failure window as the scripted CRITICAL). |
| **Operational/failure history** (4.1) | synthetic logs | `operational_failure/incident_records.csv` (150), `equipment_delay_logs.csv` (800), `fault_error_messages.csv` (1000) + `knowledge_docs/historical_maintenance_records.csv` (625) | Load into `wizard.db` via `wizard/data/db_ingest.py` so diagnosis can cite real prior incidents. |
| **FMEA / KG ground truth** | hand-authored `ontology.py` | `SPEC/ground_truth_spine.json` (15 assets · 51 scenarios · 44 spares · 69 sensor tags, threshold-aligned) | Seed/validate `build_kg.py` against the spine so graph cause-chains match the data. |
| **Demo scenarios** | `data/scenarios.json` (list, 8) + `_demo_seed.py` | 51 `failure_scenario_catalog` entries in the spine (each maps sensor spike → fault → playbook → spare) | Regenerate `scenarios.json` from the spine; pick 3-5 for `HAPPY_PATH.md` (incl. the EAF CRITICAL beat). |
| **Eval set** | `data/golden.jsonl` stub | `user_interaction/nl_queries.jsonl` (150), `multiturn_conversations.jsonl` (50), `troubleshooting_prompts.jsonl` (60) | These ARE the eval Q&A (PS §4.4). Convert to DeepEval/Ragas golden set + the demo's scripted multi-turn. Gives a real, answerable test set grounded in the same spine. |
| **Equipment master / CMMS** (enrichment) | — | `additional/equipment_master.csv` (15), `work_order_backlog.csv` (43), `alarm_rationalization.csv` (125) | Load into `wizard.db` for Dashboard + WRPS context. |

**Ordered steps (b):**
1. Add `flagship_root` path to `config.py` (point at `dataforge/datasets/steel-maintenance-flagship/`), default override-able via env.
2. **RAG:** `ingest_directory(flagship/knowledge_docs/...)` + RCA reports + breakdown/OEM/handover md → rebuild LanceDB (`use_contextual_prefix=False`). Load `spare_parts_catalog.csv` for spares tools.
3. **DB:** extend/point `wizard/data/db_ingest.py` to load the 4.1 CSVs + equipment_master + work-order backlog into `wizard.db`.
4. **ML retrain (offline, local — no LLM):** `train_failure.py` → `by_equipment/*.csv` (fault_label); `train_rul.py` + `train_anomaly.py` → `rul_trajectories_long.csv` / `sensor_timeseries_long.csv`. Re-emit joblib to `data/models/`.
5. **KG:** seed `build_kg.py` from `ground_truth_spine.json`; assert 0 orphans (spine already validates this).
6. **Scenarios + demo:** regenerate `scenarios.json` from the spine's 51 scenarios; rewire `_demo_seed.py` + alerting playback to a real spine asset; re-bake `demo_cache.json`.
7. **Eval:** load `user_interaction/*.jsonl` as the golden/Ragas set; run `scripts/run_eval.py`.
8. **Docs:** update `MASTER_BRIEF.md §5 DATA PLAN` + `docs/ARCHITECTURE.md` + `BUSINESS_IMPACT.md` to state the dataset is now the spine-consistent flagship (drop the "synthetic C-MAPSS domain-gap" honesty caveat — it's steel-native now; keep the synthetic-disclaimer per datacard §7).

---

## 5. Rate-limit / demo-stability design (non-negotiable per constraint)

1. **Cache-first:** `wizard/core/llm.py` disk cache on every prompt → repeated/replayed queries cost 0 calls.
2. **Pre-baked `demo_cache.json`:** record the demo against the cache; the live machine replays golden answers — **the recording cannot 429.**
3. **LLM-sparing:** HyDE + contextual-prefix OFF (sites 3-4). Only diagnosis/rca/plan/summary/wrps hit the model — and those are cached.
4. **Triple fallback:** subscription `None` → (optional Ollama) → deterministic template (already in every node). The app **never shows `[LLM unavailable]`** to a judge.
5. **Circuit breaker** (`middleware.py`) already trips after 5 fails → fast local-only mode.
6. **One model, one chokepoint** → easy to swap, easy to throttle.

---

## 6. Open items / risks
- Install `claude-agent-sdk` into `maintenance-wizard/.venv` (missing today) + pin in `requirements.txt`.
- Subscription throughput: keep `max_turns=1`, `allowed_tools=[]` for all generation calls (pure text) — matches EDITH; minimises session burn.
- Scrub live `GEMINI_API_KEY` from `.env` before any ZIP (PS `grep -rE 'sk-ant|AIza|sk-'` gate).
- `wizard/knowledge/generator.py` (site 7) stays off the runtime path now that the flagship exists — only re-run under subscription if regenerating data.
