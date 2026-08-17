# MASTER BUILD BRIEF — Maintenance Wizard
## Tata Steel AI Hackathon 2026 · Round 2 · Agentic AI Challenge
**Synthesized by Jarvis from 24 deep-research component reports · 2026-06-06 · Deadline: 15 Jun 2026 23:59 IST · SOLO build**

> This is the authoritative build spec. Every decision below is sourced from `round_2/research/NN_*.md`. The builder agents receive this verbatim as `<locked_architecture>` context. Read `official_PS/OFFICIAL_PS.md` for the requirements this satisfies.

---

## 0. The One-Line Thesis
**An agentic maintenance co-pilot that fires a full, source-cited maintenance plan _before_ the engineer asks — because the best recommendation is the one that arrives before the failure, not after.** Every output is explainable (graph path + citation), every prediction adapts in real time, and the system learns from one engineer correction without retraining.

The single highest-impact demo moment (judges score this most): **at ~90 seconds into a scripted sensor playback, a CRITICAL alert auto-fires for equipment EAF-04 with a complete RUL + RCA + step-by-step plan — with zero user input.** That is the proof of "agentic."

---

## 1. LOCKED SYSTEM ARCHITECTURE

```
                          ENGINEER (NL, multi-turn)            SENSOR STREAM (playback)
                                   │                                    │
                          ┌────────▼─────────┐              ┌───────────▼───────────┐
                          │  Streamlit 1.58  │              │  APScheduler 5s tick  │
                          │  (5 pages, SSE)  │              │  proactive evaluator  │
                          └────────┬─────────┘              └───────────┬───────────┘
                                   │ httpx (sync)                       │
                          ┌────────▼────────────────────────────────────▼──────────┐
                          │              FastAPI 0.136 (async, native SSE)          │
                          │     error envelopes · tenacity retry · pybreaker        │
                          └────────────────────────┬────────────────────────────────┘
                                                   │ graph.astream()
                        ┌──────────────────────────▼───────────────────────────┐
                        │      LangGraph 1.2 SUPERVISOR  (PEV pattern)          │
                        │   Plan → Execute(ReAct) → Validate → Python router    │
                        │   typed MaintenanceState · SqliteSaver checkpoint     │
                        └───┬────────┬────────┬────────┬────────┬────────┬──────┘
                            │        │        │        │        │        │
                        ┌───▼──┐ ┌──▼───┐ ┌──▼───┐ ┌──▼───┐ ┌──▼────┐ ┌─▼─────┐
                        │DIAG  │ │ RCA  │ │ RUL  │ │ RISK │ │ PLAN  │ │ALERT  │
                        └───┬──┘ └──┬───┘ └──┬───┘ └──┬───┘ └──┬────┘ └─┬─────┘
   ┌────────────────────────┴───────┴────────┴────────┴───────┴─────────┴────────┐
   │  SHARED SERVICES (in-process, pip-only, CPU)                                 │
   │  • RAG: LanceDB hybrid (bge-small ONNX) + FlashRank + HyDE + [N] citations   │
   │  • KG:  NetworkX FMEA ontology (+ optional LightRAG dynamic layer)           │
   │  • ML:  WeibullAFT (RUL) · IsolationForest+LSTM-AE (anomaly) · LightGBM (fail)│
   │  • LLM: LiteLLM → Gemini 2.5 Flash (primary) | Qwen2.5-3B Ollama (fallback)   │
   │  • DATA: wizard.db (SQLModel) + ChromaDB(Mem0) + LanceDB(RAG)                 │
   │  • OBS: Arize Phoenix local trace UI + DeepEval golden-set gate              │
   └─────────────────────────────────────────────────────────────────────────────┘
```

**Constraints honored everywhere:** pip-install only (no Docker), CPU-only, demo-must-not-crash, latency-scored, fully offline-capable fallback.

---

## 2. UNIFIED TECH STACK (exact versions — pinned)

| Layer | Choice | Version | Source report |
|---|---|---|---|
| **Orchestration** | LangGraph + langgraph-supervisor + checkpoint-sqlite | 1.2.4 / 0.0.31 / 3.1.0 | 01, 03 |
| **Reasoning pattern** | PEV hybrid (Plan→Execute(ReAct)→Validate→Python router) | — | 02 |
| **Conversation memory** | LangGraph SqliteSaver + Mem0 + sliding-window summary | mem0ai 2.0.4 | 03 |
| **RAG store + search** | **LanceDB** (native hybrid: dense+BM25+SQL filter) | lancedb 0.20+ | 04, 07 |
| **Embeddings** | BAAI/bge-small-en-v1.5 (ONNX backend) | sentence-transformers 3.x | 07 |
| **Reranker** | FlashRank (ms-marco-MiniLM-L-12-v2, ONNX, no torch) | flashrank 0.2 | 04 |
| **Chunking** | pymupdf4llm → MarkdownHeaderSplitter → Recursive 512/64 + contextual prefix | — | 04 |
| **Knowledge graph** | NetworkX FMEA ontology (ISO 14224) + optional LightRAG | networkx 3.3 / lightrag-hku 1.5 | 05 |
| **Explainability** | inline [N] citations + NLI gate + Pydantic report + **Arize Phoenix** | arize-phoenix 4.x / nli-deberta-v3-small | 06 |
| **RUL** | lifelines WeibullAFTFitter + degradation index + Bayesian correction | lifelines 0.30 | 08 |
| **Anomaly** | IsolationForest + LSTM-AE + River HST + adaptive threshold + SHAP | sklearn 1.5 / torch 2.3 cpu / river 0.21 | 09 |
| **Failure prediction** | LightGBM calibrated 4-class ordinal + tsfresh + isotonic | lightgbm 4.6 / tsfresh 0.21 | 10 |
| **RCA** | 3-layer: NetworkX traversal + DoWhy GCM + LLM 5-whys (validated) | dowhy 0.12 | 11 |
| **Risk / prioritization** | Weighted Risk Priority Score (WRPS) 4-factor + LLM narrative | numpy + pyDecision 5.1 | 15 |
| **Recommendation** | Two-pass: Instructor structured draft + Citations narrative | instructor 1.15 | 16 |
| **Synthetic knowledge data** | Ontology seed + Jinja2 + Instructor/Pydantic + dedup gate | mimesis 19 / faker 26 | 12 |
| **Public datasets** | NASA C-MAPSS FD001+FD003 (RUL/anomaly) + AI4I 2020 (fault classes) | — | 13 |
| **Data schema** | Pydantic v2 discriminated union + SQLModel + SQLite (`wizard.db`) | sqlmodel 0.0.21 | 14 |
| **Backend** | FastAPI + native SSE + APScheduler + tenacity + pybreaker + structlog | fastapi 0.136 / apscheduler 3.11 | 17, 22 |
| **Frontend** | Streamlit + Plotly + httpx(sync) + st.fragment(run_every) | streamlit 1.58 / plotly 5.22 | 18 |
| **LLM (primary/fallback)** | LiteLLM → Gemini 2.5 Flash (free) / Qwen2.5-3B Ollama | litellm 1.45 / ollama 0.18 | 19 |
| **Domain fine-tune (extra merit)** | Qwen2.5-3B QLoRA via Unsloth on synthetic corpus | unsloth 2025.12 | 19 |
| **Feedback loop** | 3-track: RAG re-rank + Bayesian RUL blend + preference JSONL | — | 20 |
| **Eval / robustness** | DeepEval + Ragas testset + circuit breaker + cached gold | deepeval 4.0 / ragas 0.2 | 21 |
| **Runtime** | Python 3.12 (test on 3.10/3.11), `pip install -e .`, Makefile | — | all |

---

## 3. CROSS-COMPONENT CONFLICT RESOLUTIONS (Jarvis decisions)

The 24 reports had a few overlaps/tensions. Resolved here so builders don't collide:

1. **Vector store — FAISS+BM25 (04) vs LanceDB (07).** → **LanceDB only.** Report 07 explicitly recommends replacing FAISS+rank_bm25 with LanceDB's native hybrid (dense + Tantivy BM25 + SQL prefilter) for a solo build — one store, two fewer deps. Keep Report 04's chunking + FlashRank rerank + HyDE on top of LanceDB.
2. **Embedding model — bge-base (04) vs bge-small (07) vs MiniLM (Mem0, 03).** → **bge-small-en-v1.5 (ONNX) everywhere** for the RAG path; Mem0 may keep all-MiniLM internally (isolated). One model to download.
3. **Observability — Langfuse (01,21) vs Arize Phoenix (06).** → **Arize Phoenix as primary local trace UI** (zero-Docker, `px.launch_app()`, auto-instruments LangGraph — best "explainability screen" for judges). Langfuse SDK optional/off by default.
4. **SSE — native fastapi.sse (17) vs sse-starlette (22).** → **Native `fastapi.sse` (0.135+)** primary; sse-starlette only if a version pin forces it.
5. **GraphRAG depth — full LightRAG (05) vs skip-for-simplicity (23).** → **Hand-authored NetworkX FMEA graph is MUST-HAVE** (cheap, 4-6h, powers RCA Layer-1 + explainable cause chains). **LightRAG dynamic layer is STRETCH** (only after all MUST-HAVEs stable).
6. **Primary LLM — Claude Sonnet (01) vs Gemini Flash (19).** → **LiteLLM gateway makes it swappable.** Default primary = **Gemini 2.5 Flash free tier** ($0 for judges, 1M context); local fallback = **Qwen2.5-3B via Ollama** (offline safety). Claude can be slotted as primary if a key is present. The **fine-tune for extra merit = Qwen2.5-3B**.
7. **Fine-tune — do it (19) vs risky (23).** → **Build it gated.** Train Qwen2.5-3B QLoRA Days 4-5; ship ONLY if it beats base on a 200-ex held-out eval (else ship base). It's the scored differentiator vs 108 other solo entries — but never at the cost of demo stability.

---

## 4. THE 6 DOMAIN AGENTS (LangGraph supervisor topology)

| Agent | Model | Job | Key tools |
|---|---|---|---|
| **Supervisor/Router** | Gemini Flash (cheap) | Route query → agent(s); deterministic Python fallback | — |
| **Diagnosis** | Gemini Flash / Sonnet | Probable fault from sensors + logs + fault codes | `retrieve_context`, `get_sensor_data` |
| **RCA** | Sonnet-class | 3-layer root-cause: graph traversal + DoWhy + 5-whys | `kg_traverse`, `gcm_attribute`, `retrieve_context` |
| **RUL/Prediction** | Haiku-class | Calls WeibullAFT + degradation index; wraps in NL | `predict_rul`, `get_anomaly_score` |
| **Prioritization** | Haiku-class | WRPS 4-factor score → risk tier + ranked queue | `score_priority`, `check_spares` |
| **Maintenance Plan** | Sonnet-class | Two-pass structured plan + cited narrative | `retrieve_context`, `lookup_spares` |

State = typed `MaintenanceState` TypedDict (equipment_id, sensor_snapshot, fault_codes, diagnosis, rca, rul_estimate, risk_level, priority_score, maintenance_plan, cited_sources, feedback_corrections). Checkpointed to SQLite per session thread_id → full time-travel for the "show your reasoning" demo beat.

---

## 5. DATA PLAN (HYBRID — locked)

| Need | Source | Use |
|---|---|---|
| RUL ground truth + degradation trajectories | **NASA C-MAPSS FD001 (+FD003)** | Train WeibullAFT; piecewise-linear RUL cap=125; per-engine normalize |
| Fault taxonomy + classification + SHAP | **AI4I 2020 (UCI, CC BY 4.0)** | LightGBM 4-class; map TWF/HDF/PWF/OSF→steel faults; convert K→°C |
| Anomaly labels | Derived (last 30 cycles before failure = anomaly window) | IsolationForest + LSTM-AE |
| **Manuals, SOPs, maintenance logs, failure reports, spare-parts** | **Self-generated synthetic** | Ontology seed (ISO 14224, 5 asset families) → Jinja2 + Instructor/Pydantic → ~500 docs, 15-20% noise-injected, dedup-gated (<0.85 cosine) |
| Steel re-framing | `dataset_framing.py` cosmetic column aliasing | engine→equipment, cycle→operating_hours, sensors→temp/pressure/vibration |

**Equipment families:** blast-furnace fans, centrifugal pumps, roller/conveyor bearings, hydraulic power units, hot-strip-mill conveyors (+ EAF-04 as the scripted demo asset). **State the simulated-data domain-gap honestly in the design doc** (judges score honesty).

---

## 6. BUILD SEQUENCE (≈9 days, MUST-HAVE first)

| Phase | Days | Deliverable |
|---|---|---|
| **0 — Foundation** | D1 AM | Repo, `pip install -e .`, Pydantic schemas + SQLModel `wizard.db`, JUDGE_MATRIX.md, golden.jsonl stub, Makefile, `.env` |
| **1 — Data** | D1 PM–D2 | C-MAPSS+AI4I loaders + framing; synthetic KB generator (500 docs); ontology JSON; FMEA NetworkX graph |
| **2 — Knowledge/RAG** | D2–D3 | LanceDB ingest, hybrid+rerank+HyDE retriever, [N] citations, NLI gate |
| **3 — ML models** | D3 | WeibullAFT RUL + degradation index; IsolationForest+LSTM-AE anomaly; LightGBM failure (offline-trained, joblib) |
| **4 — Agentic core** | D3–D6 (highest risk, 30h) | LangGraph supervisor + 6 agents + PEV + tools + checkpointer; RCA 3-layer; WRPS engine; recommendation two-pass |
| **5 — Alerting** | D6 | APScheduler evaluator + PriorityQueue + SSE fan-out + dedup/cooldown + SQLite store |
| **6 — UX/Dashboard** | D6–D7 | 5 Streamlit pages: Chat, Dashboard (gauges/heatmap), Alerts, Logbook, Settings; st.write_stream; citation pills; pre-seeded data |
| **7 — Eval/Robustness** | D7–D8 | DeepEval golden set + Ragas testset; circuit breaker + cached gold; cold-start test; thresholds met |
| **8 — Submission** | D8–D9 | ARCHITECTURE.md (8 sections), BUSINESS_IMPACT.md, SAMPLE_IO.md, README (5-cmd install), screen recording (3-4min), ZIP, `grep -r sk-ant` secret check |
| **(stretch) Fine-tune** | D4–D5 parallel | Qwen2.5-3B QLoRA; ship only if beats base on eval |

---

## 7. JUDGING OPTIMIZATION (13 axes = 6 official + 7 webinar)

**6 official:** problem understanding · agentic-framework use · technical impl+innovation · scalability+real-world · presentation+communication · business impact+feasibility.
**7 webinar (observed live, not claimed):** fast · efficient · accurate · easy-to-use · doesn't break · no-errors · smooth.

**Method (Report 23):** every build decision maps to ≥1 axis via `JUDGE_MATRIX.md`; demo is a scripted deterministic `HAPPY_PATH.md`; `ARCHITECTURE.md` must stand alone as a second judge.

**Wow moments to script into the recording:**
1. **90-second proactive CRITICAL alert** (EAF-04) with zero input → proves "agentic" (Axis B). *Highest impact.*
2. **Live Cost-Avoidance Ticker** (Report 24): persistent sidebar `st.metric` that accumulates prevented-downtime ₹ across the session — increments only on CRITICAL/HIGH confirmed events via `avoided_hours × ₹75,000/hr`. Converts technical wins into a number a Tata business-judge feels instantly. *Session-scoped (grows live), not a slide.*
3. **Traceable Diagnosis Chain** ("show your work"): every answer renders sensor→SOP(§+page)→historical-incident→agent-step as a collapsed `st.expander`, human-readable label. Clean by default, rigor on demand → Explainability + Axis C.
4. **Live agent trace** via Phoenix / in-UI expander showing nodes fired + latency → Explainability + FAST.
5. **Feedback loop in one turn:** thumbs-down → type correction → re-ask → corrected answer at top with `[ENGINEER CORRECTION]` badge → proves FR6.
6. **Source-cited RCA cause-chain** (graph path: BF Tuyere→Cooling Failure→Burnout→CRITICAL, cited to SOP §3.4) → Explainability.
7. **Spare-parts/procurement angle** (under-exploited differentiator — most competitors miss it): "CRITICAL: bearing fails in 11h. Replacement out of stock, 14-day lead — order NOW." The PS names spares+lead-time explicitly; surfacing it = free points.
8. **Business framing open** anchored to Tata's OWN published KPIs: 15% unplanned-downtime reduction on rolling mills · ₹45 Cr/yr per blast furnace (coke reduction) · ₹1.4B total AI savings · 40% maintenance-planning-time cut at Jamshedpur. Always translate % → ₹.

**Anti-patterns that auto-lose:** raw tracebacks in UI · un-cited answers · "chat-with-PDF" only (not agentic) · Docker dependency · committed API keys · slide-only · single monolithic LLM call.

---

## 8. TOP RISKS + MITIGATIONS (carry into build)

| Risk | Mitigation |
|---|---|
| Demo crash on judge machine | circuit breaker + `demo_cache.json` gold responses + cold-start test on clean venv; offline Ollama fallback |
| Gemini free-tier 429 / no internet | LiteLLM auto-fallback to Qwen2.5-3B Ollama in <2s |
| Synthetic data looks fake | ISO-14224 ontology grounding + 15-20% noise + dedup gate + ≥15 distinct manuals |
| Agentic core overruns (30h, highest risk) | build MUST-HAVE path first; LightRAG + fine-tune are stretch only |
| RUL on synthetic too few episodes | ≥30 fault episodes/equipment type; WeibullFitter fallback if AFT won't converge |
| Streamlit asyncio crash | **httpx.Client (sync) ONLY** in UI — never AsyncClient/asyncio.run |
| OOF/eval ≠ live behavior | run DeepEval cold + 10× crash test before recording (lesson from R1) |
| Python version mismatch | pin `python_requires>=3.10`; test deps on 3.10/3.11 |

---

## 9. SUBMISSION CHECKLIST (single ZIP)
- [ ] `src/` runnable prototype (`pip install -e . && make run`)
- [ ] `docs/ARCHITECTURE.md` (architecture · stack · data flow · model design · alerting/prediction logic · assumptions+limitations · install/run · sample I/O)
- [ ] `docs/BUSINESS_IMPACT.md` (Tata KPIs anchored)
- [ ] `docs/SAMPLE_IO.md` (3 query→response pairs with citation JSON)
- [ ] Screen recording 1920×1080, 3-4 min, narrated, YouTube unlisted + MP4 backup
- [ ] `README.md` 5-command install + requirements-mapping table
- [ ] `grep -rE 'sk-ant|AIza|sk-' .` returns nothing (no secrets)
- [ ] Submit from **@shriva.ujjawal HackerEarth account** before 15 Jun 23:59 IST

---

*Built from 24 specialist research reports (65k+ words) in `round_2/research/`. Each component's full rationale, alternatives-considered, anti-patterns, and integration notes live there. This brief is the convergent decision layer.*
