# MASTER ARCHITECTURE + BUILD PLAN
## Tata Steel R2 — Maintenance Wizard, on a Claude SUBSCRIPTION (NO API KEY), powered by the flagship dataset, tuned for max judging score

**Author:** Jarvis · **Date:** 2026-06-09 · **Deadline:** 15 Jun 2026 23:59 IST · SOLO
**Status:** authoritative master plan — convergence of the five system-design analyses (01–05), the OFFICIAL PS (6 criteria + 7 FR), the webinar (7 ops qualities), the flagship dataset, and the existing ~22.6k-LOC wizard build.
**Inputs synthesised:** `01_dataset_to_requirements_map.md`, `02_subscription_only_architecture.md`, `03_local_no_api_stack.md`, `04_wizard_audit_and_change_plan.md`, `05_demo_and_judging_strategy.md`.

> **HARD CONSTRAINT (governs every decision below).** Boss has **no API key and never will** — only a **Claude Max subscription** (OAuth token from `claude setup-token`). The orchestration LLM runs via the Claude Agent SDK on `CLAUDE_CODE_OAUTH_TOKEN` (the *exact* pattern proven in `jarvis_core/orchestrator.py` and `dataforge/api/scorer/agent.py::_subscription_review`). Everything else — embeddings, rerank, vector DB, ML (anomaly/RUL/fault), optional fine-tuned SLM — is **local, CPU-only, free**. The subscription has real session/rate limits (we hit one mid-build). So the design is **local-first, LLM-sparing, cache-heavy**, and the **live demo must never die on a rate limit.**
>
> **MEASURED LATENCY REALITY (not an estimate — re-baselined 2026-06-09).** The Agent SDK is **not** a lightweight completion API: each `query()` call spawns a full `claude` CLI subprocess. A single trivial one-sentence `subscription_llm()` call measured **11.78 s** end-to-end (cold, no retrieval context). A cold uncached diagnostic turn touches ~3.5 sequential LLM nodes → **realistically 30–45 s**. The old `1.8–2.2 s`/node figures in earlier drafts were copied from the gemini-2.5-flash UI mock and are **false for the subscription path by ~5–6×.** Every latency claim, demo beat, and cache policy below is rebuilt around the 10–12 s/call reality. The consequence: the recorded demo is served **100% cache-first (0 live LLM)**, and live judge interaction is **constrained to pre-warmed queries** so no cache-miss 30–45 s stall can ever happen on camera.
>
> **TOKEN HYGIENE (governs the deliverable).** The OAuth token (`sk-ant-oat01-…`) is resolved at runtime by `_load_oauth_token()` walking UP to the gitignored repo-root `.env` (verified working, token len 94). It therefore **must never live in any `.env` that could be zipped.** The wizard `.env` ships as `.env.example` only; the secret-grep gate matches `sk-ant-oat`, `sk-ant`, AND `AIza`, and runs against the **actual ZIP contents**, not just the repo tree.

---

## 1. EXECUTIVE SUMMARY — the one-paragraph answer

The Maintenance Wizard is a 6-agent LangGraph supervisor (Diagnosis → RCA → RUL → Prioritization → Plan → Report) whose intelligence is **overwhelmingly local and deterministic**: hybrid RAG over the 53-doc flagship corpus (LanceDB + bge-small ONNX + FlashRank, all CPU), a NetworkX FMEA graph seeded from the ground-truth spine, WeibullAFT RUL, IsolationForest + LSTM-AE anomaly, 15 per-equipment LightGBM fault models, and a WRPS risk prioritizer — none of which need a key or can ever rate-limit. The **subscription LLM is the conductor, not the orchestra**: it touches only ~3.5 of 6 nodes (diagnosis prose, RCA 5-whys narrative, plan write-up, multi-turn glue), each as a single-turn (`max_turns=1`, `allowed_tools=[]`) text generation routed through **one chokepoint** — `wizard/core/llm.py::subscription_llm()` — that authenticates with `CLAUDE_CODE_OAUTH_TOKEN` via the Agent SDK and degrades through a four-level ladder: **L0 pre-baked demo cache → L1 semantic response cache → L2 subscription (one backoff retry) → L3 local Qwen2.5-3B Ollama / deterministic template.** A measured subscription call is **~10–12 s** (the SDK spawns a `claude` CLI subprocess per call), so a cold uncached turn is **30–45 s** — this is exactly why the design is cache-first to the point of dogma: the recorded demo makes **zero live LLM calls** and live judge interaction is constrained to pre-warmed example queries. Because every LLM call also has a deterministic spine-grounded fallback that already exists in `nodes.py`, **a rate limit degrades fluency, never function** — the system stays correct and demoable with the LLM fully offline. The flagship dataset (15 assets, 51 scenarios, 44 spares, 207k sensor rows, 53 docs, 285 dialogue records) is the fuel that covers all four PS input categories (4.1–4.4) with one consistent ISA-95 spine, so every recommendation cites a real `scenario_id`, `doc_id`, and `sensor_tag`, and an NLI faithfulness gate (local DeBERTa) machine-verifies entailment before any answer ships. The demo is a 4-minute narrated recording whose five scored beats are served **cache-first (zero live LLM calls)**: an autonomous P1 CRITICAL alert fired off a sensor replay with no user input (the "agentic" proof), a multi-turn cited diagnosis, a spares "ORDER NOW / 36-week lead" procurement moment, one-turn engineer feedback, and a live ₹-cost-avoidance ticker anchored to Tata's own published KPIs. This is the maximum-output answer to "no API key, subscription-only": **local-first correctness + subscription-only fluency + cache-proof demo = a system that is fast, efficient, accurate, easy to use, doesn't break, errors never reach the UI, and runs smoothly — the exact 7-axis webinar bar.**

---

## 2. SYSTEM ARCHITECTURE (diagram-in-text)

```
┌───────────────────────────────────────────────────────────────────────────────────────┐
│  USERS / INPUTS                                                                          │
│   ENGINEER (NL, multi-turn) ──httpx sync──┐         SENSOR STREAM (5s APScheduler replay) │
│                                            │          from flagship sensor_timeseries.csv  │
└────────────────────────────────────────────┼─────────────────────────────┬──────────────┘
                                              ▼                             ▼
                            ┌─────────────────────────────┐   ┌──────────────────────────┐
                            │   STREAMLIT 1.58 (5 pages)   │   │ APScheduler proactive eval │
                            │ Chat·Dashboard·Alerts·Log·Set│   │  (0 LLM calls — ML only)   │
                            └──────────────┬───────────────┘   └────────────┬─────────────┘
                                           │ httpx.Client (sync only)        │
                            ┌──────────────▼─────────────────────────────────▼──────────────┐
                            │       FASTAPI 0.136  (async · native SSE · pybreaker)          │
                            └──────────────────────────────┬─────────────────────────────────┘
                                                           │  LangGraph supervisor (PEV)
                                                           │  DETERMINISTIC Python router (no LLM routing)
          ┌──────────────┬──────────────┬─────────────────┼──────────────┬──────────────┬───────────┐
        DIAG           RCA            RUL              PRIORITIZE        PLAN          REPORT       ALERT
       (LLM*)        (LLM*)        (local)             (local WRPS)    (LLM*)        (template)    (0 LLM)
          │              │             │                   │              │             │            │
          └──────────────┴─────────────┴───────────────────┴──────────────┴─────────────┴────────────┘
                                                   │
   ┌───────────────────────────────────────────────▼────────────────────────────────────────────────┐
   │  REASONING TIER →  wizard/core/llm.py :: subscription_llm()   (the ONLY door to the LLM)          │
   │   L0  demo_cache.json (gold, scripted beats)   → sub-ms,  0 LLM calls  ← THE SCORED DEMO PATH      │
   │   L1  semantic response cache (SQLite+bge-small) → <50ms; PRE-WARMED from 260 user_interaction      │
   │        prompts + the demo script; cos≥0.88 in DEMO build (≥0.94 prod) so judge ad-libs HIT not miss │
   │   L2  Claude Agent SDK query()  [CLAUDE_CODE_OAUTH_TOKEN, NO API KEY, max_turns=1, tools=[]]       │
   │        └─ MEASURED ~10–12s/call (spawns claude CLI subprocess); event-loop-safe (see §4.6)         │
   │        └─ on 429 / session-limit / timeout → ONE exponential backoff retry → else fall to L3       │
   │   L3  local fallback: Ollama Qwen2.5-3B (optional, domain-tuned) → else node's deterministic       │
   │        template composed from ground_truth_spine.json + retrieved chunks (ALWAYS correct + cited)  │
   │   (L2.5 safety net: `claude -p --output-format json` subprocess if SDK import itself fails)        │
   └───────────────────────────────────────────────────────────────────────────────────────────────┘
   ┌───────────────────────────────────────────────────────────────────────────────────────────────┐
   │  LOCAL-ONLY TIER — CPU · free · never rate-limited — THE SYSTEM'S CORRECTNESS                     │
   │   RAG:   LanceDB hybrid (dense+BM25+SQL prefilter) + bge-small ONNX + FlashRank ONNX + NLI gate    │
   │   KG:    NetworkX FMEA graph (ISO-14224) seeded from ground_truth_spine.json                      │
   │   RUL:   lifelines WeibullAFT (joblib)        Anomaly: IsolationForest + LSTM-AE + River HST       │
   │   Fault: 15 per-equipment LightGBM (joblib)   Risk: WRPS 4-factor   Spares: SQL on catalog.csv     │
   │   Memory: LangGraph SqliteSaver (sessions.db) + Mem0/ChromaDB (isolated)                           │
   └───────────────────────────────────────────────────────────────────────────────────────────────┘
   ┌───────────────────────────────────────────────────────────────────────────────────────────────┐
   │  DATA TIER — flagship/steel-maintenance-flagship/  (15 assets · 51 scn · 44 spares · 207k rows)   │
   │   knowledge_docs/ (manuals·SOPs·history·spares)  operational_failure/ (RCA·incidents·logs·faults) │
   │   condition_monitoring/ (sensor·by_equipment·rul·anomaly·process)  user_interaction/ (queries·conv)│
   │   SPEC/ground_truth_spine.json  (citation anchor + threshold source + scenario catalog)           │
   └───────────────────────────────────────────────────────────────────────────────────────────────┘
                       * LLM nodes are single-turn, cache-gated, with deterministic fallback.
```

**Data flow, one diagnostic turn (cold):** engineer query → Streamlit → FastAPI → LangGraph deterministic router classifies intent (no LLM) → DIAG node: LanceDB hybrid retrieve top-20 → FlashRank top-5 → NLI gate → `subscription_llm()` synthesises prose (or fallback) → RCA node: NetworkX graph walk + `subscription_llm()` 5-whys narrative → RUL node: WeibullAFT (local, no LLM) → PRIORITIZE: WRPS 4-factor (local) + spares SQL → PLAN node: deterministic SOP-step retrieval + `subscription_llm()` write-up → REPORT: template assembly → SSE stream to UI with citation pills + "show your work" trace. **A warm/scripted turn makes 0 LLM calls; a cold turn ≤3 LLM calls; the 5s alert loop always 0.** Latency: warm/cached turn <300 ms; the **0-LLM deterministic-template path ~200–400 ms**; a fully-cold ≤3-call turn is **30–45 s** at the measured 10–12 s/call (this is why cold turns are never on the scored path — see §4.4–4.6 and §7).

---

## 3. REQUIREMENT-BY-REQUIREMENT COVERAGE (7 FR + 6 criteria + 7 ops qualities)

### 3a. Functional Requirements (PS §6)

| FR | Requirement | Dataset (fuel) | Component (engine) | LLM? |
|---|---|---|---|---|
| **FR1** | Contextual reasoning (LLM/SLM); **extra merit: domain fine-tune** | 53 docs + `multiturn_conversations.jsonl` + `troubleshooting_prompts.jsonl` (Alpaca pairs) | `subscription_llm()` for synthesis — **this alone fully satisfies FR1.** The Qwen2.5-3B QLoRA (Unsloth, GGUF→Ollama) is a **pure stretch / extra-merit** deliverable, gated on beating base on a 50-ex held-out eval; if the Colab run slips, FR1 still passes and the live demo is unaffected (it is **not** load-bearing — see §9 + §4.4 note 5) | YES (subscription) + optional local SLM |
| **FR2** | Knowledge integration (manuals, SOPs, history, failure reports, logs) | `equipment_manuals/*` (13) + `maintenance_sops/*` (13) + `RCA-001…025` (25) + `historical_maintenance_records.csv` (625) + `incident_records.csv`/`equipment_delay_logs.csv`/`fault_error_messages.csv` (1,950) + `oem_service_bulletins.md` + `shift_handover_notes.md` + `spare_parts_catalog.csv` (118) | LanceDB hybrid RAG (ingest all md) + SQLModel `wizard.db` for tabular logs; tools `lookup_history`, `get_fault_history`, `lookup_spares` | No (retrieval local) |
| **FR3** | NL multi-turn interaction | `multiturn_conversations.jsonl` (50, few-shot + eval) + `nl_queries.jsonl` (150, seed examples) + `troubleshooting_prompts.jsonl` (60) | LangGraph `SqliteSaver` per-`thread_id` (structural multi-turn, no transcript re-send) + `subscription_llm()` conversational glue | YES (glue only) |
| **FR4** | Explainable + traceable recommendations | `ground_truth_spine.json` (`correct_resolution`, `root_cause`, `spares_required`, `grounding_refs`) + RCA `index.jsonl` | Pydantic `MaintenanceRecommendation.cited_sources` (non-empty enforced) + Arize Phoenix local trace + **NLI faithfulness gate** (`nli-deberta-v3-small`, CPU) | No (gate local) |
| **FR5** | Anomaly detection + failure prediction | `sensor_timeseries_long.csv` (585k) + `by_equipment/*.csv` (15 dense, 0% null) + `rul_trajectories_long.csv` (81k) + `anomaly_alerts.csv` (19,918) + spine `degradation_timeline`/`sensor_signature` + `alarm_rationalization.csv` (ISA-18.2) | IsolationForest + LSTM-AE + River HST ensemble; **15 per-equipment LightGBM** (the "15 specialist models" differentiator); WeibullAFT RUL; ISO-backed thresholds from spine; P1 events hard-wired CRITICAL | No (ML local) |
| **FR6** | Feedback-driven improvement | `troubleshooting_prompts.jsonl` `resolution_options[graded]` + `data/feedback/` + `work_order_backlog.csv` (43) + `golden.jsonl` | 3-track: RAG re-rank boost (+0.2/30d) + Bayesian RUL blend + preference JSONL; one-turn `[ENGINEER CORRECTION]` badge; auto-logbook work-order row | No |
| **FR7** | Real-time alerting | `anomaly_alerts.csv` (pre-seeded queue) + `sensor_timeseries_long.csv` (live replay) + spine `safety_class` (ISA-18.2 tier) + `alarm_rationalization.csv` (dedup/cooldown/nuisance) + `equipment_master.csv` (`responsible_engineer`, `notification_group`) | APScheduler 5s tick → proactive evaluator → `wizard.db` AlertEvent → FastAPI SSE → `st.fragment(run_every=5)`; P1 → red `st.error()` banner; role-based routing | **No (this loop is 0 LLM by design — must never rate-limit)** |

### 3b. Six OFFICIAL evaluation criteria (each tied to dataset + demo beat)

| # | Criterion | Dataset leverage | Component / demo proof |
|---|---|---|---|
| **JC1** | Problem understanding & solution approach | `MANIFEST.md` PS-§4.1–4.4 coverage table; spine's full process-chain (raw-material→…→cold-rolling) maps to integrated steel plant; `TATA_JSR` Jamshedpur-style reference | `ARCHITECTURE.md` §1 coverage table; Beats 0/2/3 (real ISA-95 taxonomy + under-exploited spares/procurement angle) |
| **JC2** | Effective use of agentic frameworks/concepts | spine `failure_scenario_catalog` (51) drives the autonomous loop | 6-agent LangGraph PEV supervisor + checkpointed `MaintenanceState` + **autonomous P1 alert with zero user input (Beat 1)** + Phoenix trace showing all 6 nodes firing |
| **JC3** | Technical implementation & innovation | `by_equipment/*.csv` (15 models) + ISO-backed spine thresholds + `alarm_rationalization.csv` (ISA-18.2) | 15 specialist LightGBM (not one generic), physics-grounded thresholds, 3-sensor false-alarm-reduction logic, NLI faithfulness gate, **subscription-LLM-no-key**, optional fine-tuned Qwen |
| **JC4** | Scalability & real-world applicability | `equipment_master.csv` (15 assets/13 classes) + `additional/` CMMS tier (work orders, alarm DB, handovers) mimics SAP PM / Maximo | "Add a class = 1 CSV + 1 manual + 1 SOP" (equipment-agnostic by design); CPU-only pip-install; offline fallback; **honest synthetic-data caveat stated** (judges score honesty) |
| **JC5** | Quality of presentation & communication | `nl_queries.jsonl` scripted beats with `expected_output` + `grounding_refs` (answers match ground truth exactly) | Clean 5-page UI, citation pills, "show your work" expander, live ₹-ticker, narrated ≤4-min recording, standalone `ARCHITECTURE.md` |
| **JC6** | Business impact & feasibility | spine `cost_impact` + `downtime_hours` (caster breakout ₹7.18 Cr, BF surge ₹50 Cr) + Tata KPIs (`research/domain/01`) | Live Cost-Avoidance Ticker → ₹57+ Cr/session; anchored to Tata's published 15% downtime cut, ₹45 Cr/yr/BF, ₹1.4B AI savings |

### 3c. Seven webinar ops qualities (engineered, observed live)

| Quality | Mechanism |
|---|---|
| **Fast** | deterministic Python router (no LLM for routing) · cache-first serve (sub-ms L0, <50ms L1) · 0-LLM template path ~200–400ms · bge-small ONNX + FlashRank · per-node latency shown in trace. **"Fast" is engineered on the cache/template paths, NOT the cold subscription path** (10–12s/call) — the demo and live judge Q&A run cache-first by construction so the slow path is never user-visible. |
| **Efficient** | LLM only for synthesis (3.5/6 nodes) · `max_turns=1`, `allowed_tools=[]` · semantic cache reuses near-dups · 15 LightGBM at 5–10ms each |
| **Accurate** | ISO-backed spine thresholds feed ML · NLI faithfulness gate blocks un-entailed claims (1 retry) · DeepEval golden gate ≥80% before recording |
| **Easy to use** | one chat box · 3 pre-populated example queries · collapsed expanders · alerts come *to* the user · non-technical judge can drive it |
| **Doesn't break** | pybreaker circuit breaker + tenacity retry · L0–L3 fallback ladder · cold-start test on clean venv with token unset · `httpx.Client` sync only in UI |
| **No errors** | `_llm_complete`/`subscription_llm` NEVER raises (returns None→template) · Pydantic v2 contracts · 0%-null `by_equipment` tables · FastAPI error envelopes |
| **Smooth** | rehearsed `HAPPY_PATH.md` · APScheduler timings tuned · SSE + `st.write_stream` + `st.fragment(run_every=5)` · cost ticker increments via `st.metric` |

---

## 4. THE SUBSCRIPTION LLM INTEGRATION (concrete pattern, rate-limit handling, fallbacks)

### 4.1 Auth — OAuth token, never a key
- One-time on Boss's machine: `claude setup-token` → `sk-ant-oat01-…` → store as `CLAUDE_CODE_OAUTH_TOKEN` in the wizard `.env` **and** repo-root `.env` (the walk-up fallback).
- At import, `os.environ.pop("ANTHROPIC_API_KEY", None)` — if both an OAuth token and a key were present, some SDK builds prefer the key (which Boss doesn't have). This guarantees the subscription path.
- `_load_oauth_token()` is **ported verbatim** from `dataforge/api/scorer/agent.py:358` — env first, else walk up to the Jarvis repo-root `.env`. Critical because a uvicorn process launched from `maintenance-wizard/` won't inherit the repo-root token.

### 4.2 Call shape — single-turn, tool-less text generation (proven precedent)
The four LLM tasks (diagnosis prose, RCA narrative, plan write-up, conversational glue) are **structured-text generation, not agentic tool loops**. Every call uses the SDK exactly as `jarvis_core/orchestrator.py::run_worker` and `agent.py::_subscription_review` do:
```python
from claude_agent_sdk import ClaudeAgentOptions, query
options = ClaudeAgentOptions(max_turns=1, allowed_tools=[], system_prompt=role_prompt)
async for msg in query(prompt=user, options=options):
    # accumulate block.text and msg.result
# all wrapped in asyncio.wait_for(timeout_s); returns None on ANY failure
```
- `max_turns=1` — no ReAct loop, no surprise cost. **Routing/tool-selection is deterministic Python; the LLM never decides which tool to call** (the single biggest token-sparing decision).
- `allowed_tools=[]` — model only writes text; safe on a judge's machine.
- **`TypeError` retry** kept from `run_worker`: if the installed SDK build rejects a kwarg (e.g. `model`), drop it and retry — survives SDK version drift on the judge's machine.
- **Structured output** via fenced-JSON-in-prompt + defensive `re.search(r"```(?:json)?\s*(\{.*?\})\s*```", …)` parse (the version-proof path EDITH already uses). On parse failure → `None` → deterministic fallback. The LLM never owns a field a local model computed (RUL hours, fault class, risk tier all come from ML/WRPS; LLM only narrates them).
- **Measured cost (not estimated):** one such call = **~10–12 s** wall-clock (the SDK launches a `claude` CLI subprocess; this is the dominant cost, not token generation). `timeout_s` is therefore set to **45 s** for synthesis nodes (not the 8–10 s a hosted API would use), and every node has a hard `asyncio.wait_for` so a hung subprocess falls to L3 rather than stalling the request.

### 4.3 The one chokepoint — `wizard/core/llm.py::subscription_llm()`
Full four-level ladder (verbatim design in `02_subscription_only_architecture.md` §4). `nodes._llm_complete` becomes a thin adapter over it; the 3 other runtime sites repoint to it. **Never raises, returns `None` to signal the caller to use its template.**

### 4.4 Rate-limit + latency handling (we WILL hit a session limit AND each live call is ~10–12 s — treat both as certainty)
Five layers absorb it:
1. **L0 pre-baked `demo_cache.json`** — scripted `HAPPY_PATH.md` beats served sub-ms, **0 LLM calls**. The scored demo path cannot 429, time out, vary, or incur the 10–12 s subprocess cost.
2. **L1 semantic cache** (SQLite + bge-small, LRU ~500) — judge ad-libs reuse a prior answer in <50ms. **Pre-warmed before any demo/recording** by embedding all 260 `user_interaction` prompts (150 `nl_queries` + 50 multiturn + 60 troubleshooting) + the demo script, and the cosine threshold is **lowered to cos≥0.88 in the demo build** (≥0.94 stays the production default) so near-paraphrase ad-libs HIT instead of falling through to a 30–45 s cold turn. Keeps interactive Q&A under budget AND off the slow path.
3. **LLM-sparing by construction** — proactive 5s loop 0 calls; routing/RUL/fault/risk/spares 0 calls; HyDE + contextual-prefix **OFF** (highest-volume lowest-value LLM calls, biggest 429 risk); sliding-window conversation summary (no full-transcript re-send).
4. **Backoff + token-bucket** — one exponential retry (2s→~5s) inside the wrapper; an in-process token-bucket (~8 calls/min) gates L2 so a runaway loop can't burn quota; empty bucket → straight to L3 + a quiet "offline mode" badge.
5. **L3 graceful degradation** — the node's deterministic spine-grounded template is the **true floor** (always available, 0 deps). Ollama Qwen2.5-3B is an **optional** fluency upgrade *if* it is pre-pulled and running on the box; it adds ~2–3 GB RAM + first-token latency on a CPU judge machine, and if Ollama isn't running the rung **silently no-ops to the template** — which is fine because the template, not the SLM, is the load-bearing floor. **The app never shows `[LLM unavailable]` or a traceback.**

### 4.5 Fallbacks (in order)
`L0 demo cache → L1 semantic cache → L2 Agent SDK (1 retry) → L2.5 claude -p subprocess (only if SDK import fails) → L3 Ollama Qwen2.5-3B (optional) → deterministic template from ground_truth_spine.json + RAG chunks`. Every step fail-soft; the worst case is correct, cited, template prose. **The template (not the SLM) is the floor** — the Ollama rung is a bonus that may not exist on the judge box.

### 4.6 Event-loop bridge — sync graph nodes calling an async SDK (the "doesn't break" hazard, resolved explicitly)
This is a real concurrency hazard, not a one-liner. LangGraph nodes `diagnosis_node` / `rca_node` / `plan_node` are **sync `def`**, but they execute *inside* FastAPI's already-running asyncio event loop (LangGraph runs sync nodes in a threadpool worker), and the Agent SDK's `query()` is **fundamentally async** (`async for msg in query(...)`). Naively calling `asyncio.run()` from a sync node raises `RuntimeError: asyncio.run() cannot be called from a running event loop` whenever the executor happens to run on the loop thread — version/executor-dependent and untested if left to chance.

**Resolution (implemented in `subscription_llm()`, the sync chokepoint):**
```python
def subscription_llm(prompt, system, timeout_s=45) -> str | None:
    coro = _asubscription_llm(prompt, system, timeout_s)   # the async core
    try:
        loop = asyncio.get_running_loop()                   # are we ON a loop thread?
    except RuntimeError:
        loop = None
    if loop is None:
        return asyncio.run(coro)                            # plain sync context — safe
    # We ARE inside a running loop (LangGraph threadpool under uvicorn):
    # bounce the coroutine onto a dedicated worker thread that owns its own loop.
    import anyio
    return anyio.from_thread.run(lambda: asyncio.run(coro)) \
        if anyio.from_thread.threadlocals... else \
        _run_in_fresh_thread(coro)                          # threading.Thread + new loop + queue
```
The robust primitive is **`_run_in_fresh_thread(coro)`**: spawn a `threading.Thread`, call `asyncio.run(coro)` inside it (fresh loop, no conflict), join with `timeout_s`, return the result via a `queue.Queue`. Async-native callers (`wrps.py`, `middleware.py`) instead `await asubscription_llm()` directly — no bridge needed there. **`asubscription_llm()` is the single source of truth; `subscription_llm()` is only the thread-safe sync shim over it.**

**Mandatory test (WAVE 1, before GATE 1):** `tests/test_event_loop_bridge.py` drives a **cold diagnostic turn through the FULL path under uvicorn** — `httpx` POST → FastAPI → `run_graph` (async) → threadpool → sync `diagnosis_node` → `subscription_llm()` → real Claude text — and asserts no `RuntimeError`, a non-empty answer, and clean fallback when the token is unset. This is a real integration test, not an isolated `asyncio.run()` smoke. "Doesn't break" is a scored axis, so this is non-negotiable.

---

## 5. THE LOCAL NO-API STACK (embeddings / rerank / vectorDB / ML / optional SLM)

All CPU, free, no key, joblib/ONNX-serialised, loaded once at startup. (Full table in `03_local_no_api_stack.md` §9.)

| Layer | Library / model | Notes |
|---|---|---|
| **Embeddings** | `sentence-transformers` + `BAAI/bge-small-en-v1.5` (ONNX) | 384-dim, ~90 MB, ~ms; same model reused by the L1 semantic cache (zero extra deps). Fallback `bge-micro-v2` if demo HW slow. |
| **Reranker** | `flashrank` + `ms-marco-MiniLM-L-12-v2` (ONNX) | top-20→top-5 in ~8–12ms, no torch |
| **Vector DB (RAG)** | `lancedb` (embedded) | native hybrid dense+BM25+SQL prefilter (`WHERE equipment_class=…`); chunk metadata carries `asset_id`/`equipment_class`/`doc_type`/`standard_ref` |
| **Vector DB (memory)** | `chromadb` (Mem0 backend, isolated) — **EXTRA, unpinned** | per-session corrections injected as `<memory_context>`; **falls back to LangGraph `SqliteSaver` thread memory (core) if chromadb/mem0 absent** |
| **NLI faithfulness** | `cross-encoder/nli-deberta-v3-small` via `sentence-transformers` `CrossEncoder` — **PINNED (core dep)** | ~80–120ms/claim; entailment gate before answer ships; demoable "✓ faithfulness 0.9x" badge. **Safe: rides the pinned `sentence-transformers`, not an extra** — model weights cached at build time. |
| **KG / FMEA** | `networkx` (ISO-14224, **PINNED core**) + `dowhy` GCM (**EXTRA, unpinned**) | seeded from `ground_truth_spine.json`; cause-chains match the data; 0 orphans. NetworkX graph walk is the load-bearing path; dowhy GCM is an optional causal-attribution enhancement that no-ops gracefully. |
| **RUL** | `lifelines` WeibullAFT (joblib) — **PINNED core** | retargeted to `rul_trajectories_long.csv` (`rul_cycles`); C-MAPSS as secondary corroboration |
| **Anomaly** | `sklearn` IsolationForest + `torch`(cpu) LSTM-AE (**PINNED core**) + `river` HST (**EXTRA, unpinned**) | ensemble `0.5·IF + 0.3·AE + 0.2·HST`; **degrades to `IF + AE` (both core) if `river` absent**; SHAP top-3 sensor tags (`shap` is an **EXTRA** — falls back to IsolationForest feature importances if absent); River = online 5s tick |
| **Fault prediction** | `lightgbm` — **15 per-equipment models** | trained on `by_equipment/*.csv` (0% null, `fault_label`); isotonic-calibrated; SHAP; the "15 specialists" differentiator |
| **Risk** | WRPS 4-factor (pure Python) | {process-criticality, delay-severity, spares-availability, lead-time} → LOW/MED/HIGH/CRITICAL — exactly PS §5.2 |
| **Optional SLM (extra merit, NOT load-bearing)** | `Qwen2.5-3B-Instruct` QLoRA via `unsloth` (Colab T4, one-shot) → GGUF Q4_K_M → `ollama` | trained on flagship corpus + 260 QA pairs; **gated**: ship only if it beats base on 50–200-ex held-out eval (exact-match + BERTScore F1>0.82). Serves as the *optional* L3 fluency rung AND the FR1 extra-merit deliverable. **Adds ~2–3 GB RAM + first-token latency on a CPU judge box; if Ollama isn't pre-pulled/running it silently no-ops to the deterministic template — which is the true floor. The plan does NOT bank on the SLM for the live demo or for FR1 scoring.** |
| **Orchestration** | `langgraph` PEV + `langgraph-checkpoint-sqlite` SqliteSaver | `sessions.db` per `thread_id` → genuine time-travel for "show your work" |
| **Backend / UI / sched** | `fastapi`+`uvicorn` (SSE) · `streamlit`+`plotly` (5 pages) · `apscheduler` (5s) · `sqlmodel`+`sqlite` (`wizard.db`) | |
| **Resilience / obs / eval** | `tenacity`+`pybreaker` (**PINNED core**) · `arize-phoenix` (local trace, **EXTRA**) · `deepeval`+`ragas` (golden gate, **EXTRA**) | **Phoenix trace falls back to LangGraph `SqliteSaver` checkpoint rendering (core) if absent; DeepEval/Ragas gate falls back to pinned `sentence-transformers` exact-match + BERTScore.** No scored screen depends on an unpinned import succeeding. |

**RAM budget (worst case, all running incl. Ollama):** ~4.3 GB RSS — fits 8 GB; +300 MB if Phoenix on a 16 GB box. **Without the optional SLM the floor is ~1.3–1.6 GB** (the SLM is the single biggest RAM line and is non-load-bearing).

**Dependency-tier honesty:** the install splits into **pinned core** (everything in `requirements.txt` proper — embeddings, rerank, LanceDB, NLI-via-`sentence-transformers`, NetworkX, lifelines, sklearn, LightGBM, torch-cpu, LangGraph + SqliteSaver, FastAPI/Streamlit, `claude-agent-sdk==0.1.81`, `anyio`) and **best-effort extras** (`chromadb`/`mem0ai`, `dowhy`, `river`, `shap`, `arize-phoenix`, `deepeval`/`ragas`). Every extra that backs a scored demo screen has a **core-dep fallback** (table above) so a silent no-op on the judge's box degrades the screen, never blanks it. An `assert_imports.py` run at GATE 1 prints exactly which tier loaded on the target machine.

---

## 6. THE WIZARD CHANGE-PLAN (ordered file changes: drop the API key + wire the dataset)

The heavy ML/RAG/graph stack is **already local + free** (built, ~22.6k LOC). Only the **LLM generation calls** are wired to a Gemini key — that is the entire surface area. Two workstreams, both surgical.

### 6a. Workstream A — route LLM through the subscription (one shim, single chokepoint)
**Verified state (2026-06-09):** `claude_agent_sdk` is **NOT** in `maintenance-wizard/.venv` (only in repo `.venv` @ v0.1.81) → must install. Every LLM call funnels through `nodes.py::_llm_complete` (LiteLLM→`gemini/gemini-2.0-flash`) + 6 other sites.

1. **`requirements.txt`** — add `claude-agent-sdk>=0.1` **and pin it** (`claude-agent-sdk==0.1.81`, the version proven in the repo `.venv`) as the **literal first build step** — it is currently NOT installed in `maintenance-wizard/.venv` (`pip show` → not found), so **every subscription LLM path is non-functional until this lands.** Also add `anyio>=4` (already transitive via FastAPI but pin it for the event-loop bridge in §4.6). Keep `litellm` only as the Ollama-offline transport. Add `pytest-asyncio` (already present) for the §4.6 integration test.
2. **NEW `wizard/core/llm.py`** — port `_load_oauth_token()` (verbatim from `agent.py:358`, walk-up to repo-root `.env`) + `asubscription_llm()` (async core) + `subscription_llm()` (the **event-loop-safe sync shim** per §4.6 — detects a running loop and bounces onto a fresh-loop worker thread; **NOT** a bare `asyncio.run()`) with the L0–L3 ladder; at module top, `os.environ.pop("ANTHROPIC_API_KEY", None)` so no stray key beats the OAuth token. **NEW `wizard/core/response_cache.py`** (semantic cache, reuses bge-small; pre-warm loader for the 260 user_interaction prompts).
3. **`wizard/core/config.py`** — extend `llm_provider` Literal with `"subscription"`; set **default `llm_provider="subscription"`**; add `claude_oauth_token`, `wizard_llm`, `wizard_llm_model`, `wizard_llm_timeout_s`; keep Gemini/Ollama fields optional.
4. **`wizard/agents/nodes.py:52` `_llm_complete`** — rewrite body to call `subscription_llm()` when provider=subscription; on `None` → existing deterministic fallback (unchanged). Callers + fallbacks untouched.
5. **`wizard/ml/rca_engine.py:425`** — swap `litellm.completion` → `subscription_llm()` (same `[],[]` fallback).
6. **`wizard/backend/wrps.py:327`** & **`middleware.py:213`** — swap `await litellm.acompletion` → `await asubscription_llm()`, keep `llm_circuit_breaker.call(...)` wrapper.
7. **`wizard/rag/retriever.py` (HyDE)** & **`wizard/rag/ingestion.py` (contextual prefix)** — **disable, don't port** (`RAG_HYDE_ENABLED=false`, `use_contextual_prefix=False`): highest-volume lowest-value calls, biggest 429 risk; local hybrid+rerank already covers retrieval.
8. **`.env` / `.env.example`** — `LLM_PROVIDER=subscription`; **DELETE the live `GEMINI_API_KEY=AIzaSy…` from `maintenance-wizard/.env` NOW** (it is currently sitting in working-tree line 2 — gitignored and verified NOT in git history, so it has not been pushed, but it WILL ship to judges if `.env` is zipped). Because it was never in history, no Google-side rotation is strictly required, but rotate it anyway as hygiene. The `.env` is already covered by `.gitignore`; **add an explicit `.env` zip-exclude** to the packaging script and ship `.env.example` only. **The OAuth token stays OUT of the wizard `.env` entirely** — `_load_oauth_token()` walks up to the gitignored repo-root `.env` (verified, len 94), so the token never needs to live anywhere zippable.
9. **`os.environ.pop("ANTHROPIC_API_KEY", None)` at module import of `wizard/core/llm.py`** — guarantees no stray key is ever preferred over the OAuth token (some SDK builds prefer a key if both are present, and Boss has no key).
10. **Verify:** install + pin `claude-agent-sdk` (step 1) FIRST; then run `scripts/verify_demo.py` + `smoke_agents.py` with `LLM_PROVIDER=subscription` and the Gemini key absent → assert real Claude text (**not** `[LLM unavailable]`), confirming the entire FR1 LLM path is live. Then `scripts/capture_demo_cache.py` to pre-bake `data/demo/demo_cache.json` (0 live calls in the recording).

### 6b. Workstream B — wire in the flagship dataset
The flagship replaces today's `data/synthetic/docs/` + C-MAPSS/AI4I framing with one consistent 15-asset spine covering all four PS input categories.

1. **`config.py`** — add `flagship_root` pointing at `dataforge/datasets/steel-maintenance-flagship/` (env-overridable).
2. **RAG** — `ingest_directory()` at `knowledge_docs/` + `RCA-*.md` + `breakdown_summaries.md` + `oem_service_bulletins.md` + `shift_handover_notes.md` → rebuild LanceDB (`use_contextual_prefix=False`); load `spare_parts_catalog.csv` for spares tools.
3. **DB** — point `wizard/data/db_ingest.py` to load the 4.1 CSVs + `equipment_master.csv` + `work_order_backlog.csv` + `alarm_rationalization.csv` into `wizard.db`.
4. **ML retrain (offline, local, no LLM)** — `train_failure.py` → `by_equipment/*.csv` (15 models, `fault_label`); `train_rul.py` + `train_anomaly.py` → `rul_trajectories_long.csv` / `sensor_timeseries_long.csv`. Re-emit joblib to `data/models/`.
5. **KG** — seed `build_kg.py` from `ground_truth_spine.json`; assert 0 orphans.
6. **Scenarios + demo — EAF-04 PHANTOM-ASSET REWIRE (WAVE 1, BLOCKING, not a "gap fix").** Verified 2026-06-09: the existing build's `_demo_seed.py` + `.env` `DEMO_EAF04_TRIGGER_SECONDS` reference asset **`EAF-04`, which does NOT exist** anywhere in the flagship spine or `equipment_master` (grep = 0 hits; the spine's BF asset is `BF.BLW.FAN01`, confirmed present, scenario `SCN-041`). Until rewired, the **autonomous P1-alert demo beat — the #1 JC2/JC3 "agentic" proof — fires on a phantom asset.** So this is WAVE-1 critical-path work: (a) regenerate `scenarios.json` from the spine's 51 scenarios; (b) repoint `_demo_seed.py` + alerting playback to the **real** `BF.BLW.FAN01` / `SCN-041` surge (≈45 s) and `SCN-043` caster breakout (≈3:15); (c) rename `eaf04_breakout_replay.csv` → a spine-asset replay derived from `sensor_timeseries_long.csv` rows for `BF.BLW.FAN01`; (d) add a thin `EAF-04 → BF.BLW.FAN01` alias in `equipment_master.csv` *only* so legacy `.env`/seed references resolve, never as a real asset; (e) **smoke-test that the autonomous P1 CRITICAL alert actually fires on the real spine asset** before WAVE 2; (f) re-bake `demo_cache.json`.
7. **Eval** — load `user_interaction/*.jsonl` as DeepEval/Ragas golden set; derive top-20 by complexity into `data/golden.jsonl`; run `scripts/run_eval.py`. (DeepEval/Ragas are unpinned extras — see step 9; if either fails to import on the box, the eval **gate** is enforced via the pinned `sentence-transformers` exact-match + BERTScore path instead, and the "eval gate" demo screen is down-ranked rather than left blank.)
8. **Other small gaps** (from 01 §Part 3): 3 pre-seeded `data/feedback/seed_corrections.jsonl` (10 min) for the FR6 feedback beat. (The EAF-04 rewire that was previously listed here is **promoted to step 6 / WAVE 1** above — it is blocking, not 30-min cosmetic.)
9. **Pin + install-verify the scored-claim "extras"** — several differentiators that occupy a scored demo screen currently depend on best-effort extras that "degrade gracefully if missing," which means they can **silently no-op and blank a scored screen.** Resolve per-claim: **(a) NLI faithfulness badge (FR4 / Accurate)** is actually safe — it uses `CrossEncoder("cross-encoder/nli-deberta-v3-small")` from `sentence-transformers`, which **is** a pinned core dep; assert the model downloads/caches at build time and the badge renders. **(b) Phoenix reasoning-trace expander (JC2/JC5 "show your work")** — `arize-phoenix` + `openinference-instrumentation-langchain` are unpinned; either pin working versions and assert import, OR fall back to rendering the trace from the **always-present LangGraph `SqliteSaver` checkpoint** (node list + per-node latency) so the expander is never empty even with Phoenix absent. **(c) DeepEval/Ragas golden gate (Accurate)** — pin or fall back to the pinned-deps eval path (step 7). **(d) `river`/`shap` (anomaly online-update + SHAP attributions)** — pin them or have the anomaly ensemble degrade to `IsolationForest + LSTM-AE` (both pinned) with SHAP replaced by IsolationForest feature importances. **(e) `chromadb`/`mem0ai` (per-session memory)** — pin or fall back to the LangGraph `SqliteSaver` thread memory (already core). **Rule: any extra that backs a scored screen is either pinned-and-import-asserted at build, or its screen is explicitly down-ranked so a silent no-op never blanks the demo.** Run an `assert_imports.py` on the target box during GATE 1.
10. **Docs** — update `ARCHITECTURE.md` + `BUSINESS_IMPACT.md` to state spine-consistent flagship; drop the C-MAPSS domain-gap caveat (now steel-native); keep the synthetic-disclaimer per datacard §7; **add the measured ~10–12 s/call latency note + the cache-first demo policy** so the doc's own numbers match reality.
11. **Confirm `wizard/knowledge/generator.py` is data-GEN-time only** — it uses `instructor.from_litellm` + a key, but is invoked **only** via `python -m wizard.knowledge.generator --use-llm` / `gen_synthetic.py` (offline corpus generation), **never on the runtime or demo path** (verified: no runtime importer). Acceptable to leave as-is, but the demo/CI must never invoke it, and its key field stays out of `.env.example`.

---

## 7. THE MAX-SCORING DEMO PLAN

**Thesis (4 minutes):** *An agentic maintenance co-pilot that fires a complete, source-cited plan **before** the engineer asks.* Five proofs, each a real spine scenario, all served **cache-first (0 live LLM)**:

| Beat | Time | Proof | Spine scenario | Criteria |
|---|---|---|---|---|
| 0 | 0:00–0:20 | Cold open: 5-page UI, 15 real assets, ₹0 ticker | `equipment_master.csv` | JC1, JC5 |
| **1** | 0:20–1:05 | **Autonomous P1 CRITICAL alert, zero user input** (sensor replay → red banner at ~45s) | **SCN-041** BF blower surge (₹50 Cr) | **JC2, JC3**; FR5/FR7; Fast |
| 2 | 1:05–2:05 | Multi-turn cited diagnosis (AE→BPFO→temp, ISO 15243 4-stage chain) + "show your work" expander | **SCN-037** F3 bearing via `CONV-001` | JC1/3/4; FR2/3/4; Accurate |
| 3 | 2:05–2:45 | Spares "NOT IN STOCK → ORDER NOW" (36-week lead) — the under-exploited winner | **SCN-043** + `GEAR-WHL-M20` | JC1/6; FR4; Business impact |
| 4 | 2:45–3:15 | Feedback in ONE turn, `[ENGINEER CORRECTION]` badge, no retrain | engineer correction | JC2/3; FR6; Smooth |
| 5 | 3:15–3:50 | Caster breakout (3-sensor agreement, false-alarm logic) + ₹57+ Cr ticker close, Tata KPIs | **SCN-043** | JC3/6; FR1/5 |

**Three visible explainability layers** (the differentiator vs chat-with-PDF): reasoning trace (nodes + per-node latency, from SqliteSaver) · grounded citation pills (spine path / doc id / standard) · NLI faithfulness badge (machine-verified entailment).

**Robustness (the #1 rule — demo must not die):** strict three-tier serve `[1] demo cache → [2] deterministic spine template → [3] live subscription (degrades to [2] on any failure)`. **Live judge interaction is constrained to 3 pre-populated example-query chips; the L1 semantic cache is pre-warmed from all 260 user_interaction prompts at cos≥0.88 (demo build)** so a near-paraphrase ad-lib HITS the cache in <50ms instead of dropping to a measured 30–45s cold turn. Any free-text miss falls to the ~200–400ms deterministic template, never a live 10–12s+ LLM stall on camera. Pre-capture procedure: run the scripted path once live to populate `demo_cache.json`, set `WIZARD_DEMO_MODE=cache_first`, then **cold-start test on a clean venv with networking off and `CLAUDE_CODE_OAUTH_TOKEN` unset** — the full recording must complete with 0 live-LLM dependency.

**Anti-patterns that auto-lose:** raw tracebacks in UI · un-cited answers · chat-with-PDF only (the autonomous alert is the antidote) · a live LLM call on the scored path that can 429 **or eat 10–12s on camera** · committed/zipped API keys (incl. the OAuth `sk-ant-oat` token) · a demo beat firing on a phantom asset (the EAF-04 trap — must be the real `BF.BLW.FAN01`) · slide-only demo · unanchored KPI claims.

---

## 8. PRIORITIZED, ORDERED BUILD CHECKLIST (AI-native cadence — hours not days, parallel-default)

Active time is **hours/minutes**, not human-team "days." Run independent tracks in **parallel workers**; gates are Boss-approval latency, not calendar. Ordered so a demo-safe state exists as early as possible, then quality compounds.

**GATE 0 — Unblock the subscription path + scrub the live key (do FIRST, blocks everything LLM).** ~30 min.
- [ ] `cd maintenance-wizard && .venv/bin/pip install claude-agent-sdk==0.1.81`; **pin in `requirements.txt`** (currently NOT installed in the wizard venv → every LLM path is dead until this lands).
- [ ] Confirm `CLAUDE_CODE_OAUTH_TOKEN` resolves via `_load_oauth_token()` walk-up from the wizard dir (it does NOT need to live in the wizard `.env`).
- [ ] **DELETE the live `GEMINI_API_KEY=AIzaSy…` from `maintenance-wizard/.env` NOW** (line 2; gitignored + NOT in history, but ships if `.env` is zipped). Rotate at Google as hygiene. Ship `.env.example` only.
- [ ] Add `os.environ.pop("ANTHROPIC_API_KEY", None)` at import of `wizard/core/llm.py`; verify a real Claude text response (not `[LLM unavailable]`) with the Gemini key absent.

**WAVE 1 — Two parallel tracks (Workstream A + B core) + the two BLOCKING fixes.** ~3–4 h active.
- *Track A (LLM swap):* [ ] write `wizard/core/llm.py` (with **event-loop-safe `subscription_llm()` per §4.6** — running-loop detection + fresh-thread bounce, NOT bare `asyncio.run()`) + `response_cache.py` → [ ] config `subscription` default → [ ] rewrite `_llm_complete` → [ ] repoint rca_engine/wrps/middleware → [ ] disable HyDE + contextual-prefix → [ ] `.env`/`.env.example`.
- *Track A BLOCKING test (before GATE 1):* [ ] `tests/test_event_loop_bridge.py` — drive a **cold diagnostic turn through the FULL async `run_graph` → sync node → `subscription_llm()` path under uvicorn** (real `httpx` POST, not isolated `asyncio.run()`); assert no `RuntimeError`, non-empty answer, clean fallback when token unset.
- *Track B (dataset wire):* [ ] `flagship_root` in config → [ ] re-ingest LanceDB from flagship docs → [ ] `db_ingest.py` load 4.1 CSVs + master + work orders → [ ] retrain 15 LightGBM + RUL + anomaly offline → [ ] seed KG from spine (0 orphans).
- *Track B BLOCKING — EAF-04 phantom-asset rewire (NOT a 30-min cosmetic gap):* [ ] regenerate `scenarios.json` from spine → [ ] repoint `_demo_seed.py` + alerting playback to **real** `BF.BLW.FAN01`/`SCN-041` (surge ≈45s) + `SCN-043` (caster ≈3:15) → [ ] spine-asset replay CSV → [ ] thin `EAF-04→BF.BLW.FAN01` alias for legacy refs only → [ ] **smoke-test the autonomous P1 CRITICAL alert fires on the REAL spine asset** (the #1 JC2/JC3 agentic proof must not point at a phantom).
- *Track B small gaps (parallel):* [ ] `seed_corrections.jsonl`.

**GATE 1 — Demo-safe baseline.** ~1 h. **This is the "never lose" checkpoint.**
- [ ] `WIZARD_LLM=off` → full 5-beat happy path runs on deterministic templates (proves offline correctness, ~200–400ms/turn).
- [ ] `WIZARD_LLM=on` + token → prose upgrades (expect ~10–12s/cold-call), semantic cache warms.
- [ ] Smoke `verify_demo.py` + `smoke_agents.py`: diagnosis/rca/plan return real Claude text, never `[LLM unavailable]`; Gemini key absent.
- [ ] `python assert_imports.py` on the target box → prints pinned-core vs extras tier; confirm every scored-screen extra either imports OR its core-dep fallback is active (NLI badge, Phoenix→SqliteSaver trace, eval gate, anomaly ensemble).
- [ ] Event-loop bridge test green (above).

**WAVE 2 — Quality + scored differentiators (parallel).** ~3–4 h.
- [ ] Eval: load `user_interaction/*.jsonl` → DeepEval/Ragas golden set → run gate (target ≥80%).
- [ ] NLI faithfulness badge rendering on answers; Phoenix trace wired into the "show your work" expander.
- [ ] Cost-ticker math verified (SCN-041 ₹50 Cr + SCN-043 ₹7.18 Cr + bearing → ≈₹57 Cr); each increment cited.
- [ ] Role-based alert routing (`responsible_engineer` in SSE payload) — cheap JC4 win.
- [ ] *(Stretch, separate Colab worker, runs async)* Qwen2.5-3B QLoRA fine-tune → eval gate → ship only if beats base.

**WAVE 3 — Demo capture + hardening.** ~2–3 h.
- [ ] Extend `capture_demo_cache.py` to `(system,user)`-hash keys; run the scripted path once LIVE to bake `demo_cache.json` for all 5 beats + CONV-001 turns.
- [ ] **Pre-warm the L1 semantic cache** by embedding all 260 `user_interaction` prompts (150 nl_queries + 50 multiturn + 60 troubleshooting) + the demo script, and **lower the cache threshold to cos≥0.88 for the demo build** (≥0.94 prod default) so judge ad-libs HIT instead of triggering a 30–45s cold turn.
- [ ] **Constrain live judge interaction to the 3 pre-populated example queries** (UI surfaces only those as one-click chips); any free-text that misses L0+L1 shows the deterministic template path (~200–400ms), never a live 10–12s+ stall on camera.
- [ ] **Cold-start test:** clean venv, networking off, token unset → full recording completes from cache + template (no error, no blank).
- [ ] Tune APScheduler timings (surge ≈45s, breakout ≈3:15) **against the real `BF.BLW.FAN01`/`SCN-041` replay** (post-EAF-04-rewire); 10× crash-test the recording flow.
- [ ] Record 1920×1080 narrated ≤4 min; YouTube unlisted + MP4 backup.

**GATE 2 — Submission.** ~1 h.
- [ ] Build the ZIP first, then `grep -rIE 'sk-ant-oat|sk-ant|AIza|GEMINI_API_KEY=AIza' <unzipped-zip-dir>/` → **empty, run against the ACTUAL ZIP CONTENTS, not just the repo tree** (the OAuth `sk-ant-oat…` token must NOT be inside the ZIP — it lives only in the gitignored repo-root `.env` resolved at runtime; ship `.env.example`). Confirm `.env` is zip-excluded.
- [ ] `ARCHITECTURE.md` complete (arch · stack · data+system flow · model design · alerting/prediction logic · assumptions/limits incl. honest synthetic + subscription-dependency caveat · install/run · sample I/O).
- [ ] Single ZIP: runnable source + doc + recording link. Submit from @shriva.ujjawal HackerEarth before **15 Jun 23:59 IST** (multiple submissions allowed, last = final).

**Critical-path summary:** GATE 0 (SDK install + pin + **live-key scrub**) → WAVE 1 (A∥B, including the **EAF-04 phantom-asset rewire** and the **event-loop-bridge integration test** — both blocking) → **GATE 1 (demo-safe floor + `assert_imports` extras check — bank this)** → WAVE 2 (quality ∥ fine-tune) → WAVE 3 (cache pre-warm + constrained live interaction + cold-start) → GATE 2 (secret-grep against ZIP contents + ZIP). The fine-tune is the **only true stretch and is not banked for scoring**; everything before GATE 1 — including the key scrub, the SDK install, the event-loop bridge, and the EAF-04 rewire — is the non-negotiable spine.

---

## 9. HONEST LIMITATIONS (state in ARCHITECTURE.md — judges score honesty)
- **Measured LLM latency is ~10–12s/call, not ~2s.** The Agent SDK spawns a `claude` CLI subprocess per call, so a cold uncached turn is 30–45s. We do **not** hide this: the demo is 100% cache-first (0 live calls), live judge interaction is constrained to pre-warmed queries, and the cache threshold is lowered for the demo build so near-paraphrases hit. The slow path exists but is engineered to never be user-visible on the scored path. **The 200–400ms numbers you see are the cache/template paths; the 10–12s number is the cold subscription path.**
- **Throughput is the subscription's, not an API tier's.** Heavy concurrent interactive use can hit a session limit; absorbed by cache + local fallback, but raw LLM-prose throughput is bounded. The LiteLLM-shaped seam means swapping the L2 layer for a hosted endpoint in production is a one-file change. **We WILL hit a session limit under sustained ad-lib use — and the system stays correct because every LLM call has a deterministic spine-grounded fallback.**
- **Determinism vs fluency trade:** under fallback, answers are correct but read as templated — accepted consciously (correctness + uptime > fluency for maintenance decision-support).
- **Optional SLM is not load-bearing.** The Qwen2.5-3B QLoRA / Ollama rung is a fluency bonus that needs Ollama pre-pulled (~2–3GB RAM); if it isn't running on the judge box it silently no-ops to the deterministic template, which is the true floor. The FR1 "extra merit" fine-tune is a stretch — if the Colab run slips, FR1 still passes via the subscription LLM and the demo is unaffected. **We do not bank the SLM for scoring.**
- **Some observability/eval components are best-effort extras** (`chromadb`/`mem0`, `dowhy`, `river`, `shap`, `arize-phoenix`, `deepeval`/`ragas`). Each that backs a scored screen has a pinned-core fallback (Phoenix→SqliteSaver trace, eval gate→`sentence-transformers` exact-match+BERTScore, river→IF+AE, shap→IF feature-importances, chroma/mem0→SqliteSaver memory). `assert_imports.py` reports exactly which tier loaded on the target box. So a missing extra degrades a screen, never blanks it.
- **Synthetic data:** the flagship is synthetic-but-spine-consistent and physics-grounded (ISO/ISA-backed thresholds); a real Tata deployment needs site calibration. Stated per datacard §7.
- **`max_turns=1` means no LLM self-correction via tools** — by design; local layers are the source of truth, the LLM only narrates.

---

## 10. NO-API-KEY INTEGRITY STATEMENT (final, after all fixes)

**The system runs end-to-end with ZERO paid API keys.** Verified across every LLM call site:

1. **Orchestration LLM = Claude Max subscription only.** Every runtime LLM call (diagnosis prose, RCA 5-whys, plan write-up, multi-turn glue, and the swapped `rca_engine.py`/`wrps.py`/`middleware.py` sites) funnels through the single chokepoint `wizard/core/llm.py::subscription_llm()`/`asubscription_llm()`, which authenticates with `CLAUDE_CODE_OAUTH_TOKEN` (`sk-ant-oat01-…`) via the Claude Agent SDK — the proven `jarvis_core` / `dataforge/api/scorer/agent.py::_subscription_review` pattern. **No `ANTHROPIC_API_KEY`, no `GEMINI_API_KEY`, no `OPENAI_API_KEY` on any runtime path.** `os.environ.pop("ANTHROPIC_API_KEY", None)` at import guarantees no stray key out-ranks the OAuth token.
2. **The live Gemini key is scrubbed.** `GEMINI_API_KEY=AIzaSy…` is DELETED from `maintenance-wizard/.env` (it was gitignored and never in git history); `.env` is zip-excluded; only `.env.example` ships. The OAuth token lives only in the gitignored repo-root `.env`, resolved at runtime by `_load_oauth_token()` walk-up — it is **never** placed in any zippable file. GATE-2 secret-grep matches `sk-ant-oat`, `sk-ant`, AND `AIza` and runs against the actual ZIP contents.
3. **Everything else is local, CPU, free, keyless** — verified in the actual code: embeddings (`bge-small-en-v1.5` ONNX via `sentence-transformers`), reranker (`flashrank` ms-marco-MiniLM ONNX), NLI gate (`cross-encoder/nli-deberta-v3-small` via `CrossEncoder`), vector DBs (LanceDB embedded + optional Chroma), and all ML (IsolationForest, LSTM-AE, 15 LightGBM, WeibullAFT, NetworkX FMEA, WRPS). **None requires a key or can rate-limit.**
4. **The only non-runtime key surface** is `wizard/knowledge/generator.py` (`instructor.from_litellm`), a data-GEN-time corpus tool invoked solely via `python -m wizard.knowledge.generator --use-llm` / `gen_synthetic.py` — confirmed it is **never imported on the runtime or demo path**, its key field stays out of `.env.example`, and the demo/CI must not invoke it.
5. **The subscription's rate/session limit is treated as a certainty, not a risk** — the L0→L3 ladder guarantees correctness survives a full LLM outage; a rate limit degrades fluency, never function, and never reaches the UI as an error.

**Bottom line: keyless by construction. The subscription is the only LLM, the local tier is the correctness, the cache+template is the uptime — and a complete recording can be produced with networking off and the OAuth token unset.**
