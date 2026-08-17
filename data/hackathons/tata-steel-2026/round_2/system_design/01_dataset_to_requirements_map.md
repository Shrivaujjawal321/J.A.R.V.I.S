# Dataset → Requirements Map
## Tata Steel R2 — Maintenance Wizard
**Produced:** 2026-06-09  
**Scope:** Maps every functional requirement (FR1–FR7) and every judging criterion (JC1–JC6 + 7 webinar qualities) to exact flagship-dataset files, with a concrete "max output" tactic for each.  
**Hard constraint throughout:** No paid API key. LLM = Claude Max subscription via `CLAUDE_CODE_OAUTH_TOKEN` + claude-agent-sdk (`_subscription_review` pattern from `dataforge/api/scorer/agent.py`). All embeddings, ML models, and vector DB are local/CPU.

---

## Part 1 — Functional Requirements (FR1–FR7)

### FR1 — Contextual Reasoning using LLMs/SLMs (extra merit for domain fine-tune)

| Dimension | Dataset files | How to use | Max-output tactic |
|---|---|---|---|
| Primary LLM calls | All modalities (RAG retrieval → LLM synthesis) | `wizard.agents.nodes` calls claude-agent-sdk / `subprocess claude -p`; structured output via Instructor + Pydantic `MaintenanceRecommendation` | Replace every Gemini call in `wizard/core/config.py` with the `_subscription_review` / `_load_oauth_token` pattern from `dataforge/api/scorer/agent.py`. Single swap; LangGraph supervisor stays intact. |
| Haiku-class routing | `nl_queries.jsonl` (150 queries with intent tags) | Supervisor routing node classifies intent cheaply — use a deterministic Python router first; LLM only for ambiguous cases | Deterministic Python router for 80% of cases → LLM called only for complex queries → rate-limit budget preserved. |
| Domain fine-tune (extra merit) | All 53 Markdown docs (manuals + SOPs + 25 RCA reports) + `multiturn_conversations.jsonl` (50 dialogues) + `troubleshooting_prompts.jsonl` (60 prompts with reasoning chains) | Assemble as Alpaca-style instruction pairs: `(system=domain-expert persona, user=query, assistant=grounded_answer)` using `grounding_refs` + `correct_resolution` from spine | Train Qwen2.5-3B QLoRA (Unsloth) on this corpus → `finetune/` directory already scaffolded in build. Gate: only ship if beats base on 50-ex held-out eval drawn from `nl_queries.jsonl`. |
| Cache-heavy LLM sparingness | `golden.jsonl` (existing golden set in `data/`) | Pre-compute cached responses for the 10 scripted demo queries | Demo never hits a live LLM for scripted beats → rate-limit proof. |

---

### FR2 — Knowledge Integration (manuals, SOPs, historical records, failure reports, operational logs)

| Input type | Dataset files | How to use | Max-output tactic |
|---|---|---|---|
| Equipment manuals | `knowledge_docs/equipment_manuals/MAN-001…013-*.md` (13 docs) | Ingest into LanceDB via `wizard/rag/ingestion.py`; chunk with pymupdf4llm → MarkdownHeaderSplitter → Recursive 512/64 + contextual prefix | Every manual has ISA-95 asset tags + physics-grounded thresholds — ensure chunk metadata carries `asset_id`, `equipment_class`, `section_title` for LanceDB SQL prefilter. |
| Maintenance SOPs | `knowledge_docs/maintenance_sops/SOP-01…13-*.md` (13 docs) | Same ingest pipeline; SOP section headings become retrieval labels | Tag each chunk with `doc_type=SOP`, `step_number` → enables "show me step 3 only" queries. |
| RCA reports | `operational_failure/failure_analysis_reports/RCA-001…025-*.md` (25 docs) + `index.jsonl` | Ingest as RAG + seed NetworkX FMEA graph edges (cause → effect) | Use `index.jsonl` to pre-build KG edges without parsing full Markdown; 25 RCA reports = 25 validated cause-chains for the graph layer. |
| Historical maintenance records | `knowledge_docs/historical_maintenance_records.csv` (625 rows) | Join to `equipment_master.csv` on `asset_id`; expose via `wizard/rag/tools.py` `lookup_history` | Enables "how many times has this bearing been replaced in the past 2 years?" — a natural demo question judges love. |
| Operational failure logs | `operational_failure/incident_records.csv` (150) + `equipment_delay_logs.csv` (800) + `fault_error_messages.csv` (1,000) | Load into `wizard.db` via SQLModel; query via `get_fault_history(asset_id)` tool in `wizard/agents/tools.py` | Full 1,950-row combined log → rich failure-pattern queries across 15 spine assets. |
| OEM bulletins + shift handover | `additional/oem_service_bulletins.md` + `additional/shift_handover_notes.md` | Ingest into RAG with `doc_type=OEM_BULLETIN` / `doc_type=SHIFT_HANDOVER` | Shift-handover notes are an under-exploited differentiator — most competitors miss this modality entirely. |
| Spares | `knowledge_docs/spare_parts_catalog.csv` (118 parts) | Expose via `lookup_spares(part_id, equipment_class)` tool | Key demo beat: "bearing fails in 11h → replacement lead time 14 days → ORDER NOW." Spares + lead time explicitly named in PS §4.3. |

**FMEA Knowledge Graph seeding:**  
`additional/alarm_rationalization.csv` (125 rows, ISA-18.2 alarm DB) maps equipment → alarm tag → priority tier (P1–P4) → hazard. Use these rows as graph edge weights in the NetworkX FMEA layer (`wizard/agents/graph.py` KG traversal). Enables causality chains like `{caster breakout → P1 safety → immediate stop}` with cited alarm ID.

---

### FR3 — Natural Language Multi-Turn Interaction

| Dataset files | How to use | Max-output tactic |
|---|---|---|
| `user_interaction/multiturn_conversations.jsonl` (50 dialogues) | Load as the DeepEval / eval test suite for multi-turn coherence; also use as few-shot examples in the system prompt for the supervisor node | Each dialogue has `session_id`, `turns[]` with `user`/`assistant`, `equipment_id`, `final_diagnosis`, `grounding_refs` — perfect eval harness. |
| `user_interaction/nl_queries.jsonl` (150 queries) | Seed the Streamlit Chat page with 3 pre-populated example queries (low/med/high complexity) + run as smoke tests on startup | Include `intent_category` from the JSONL as the supervisor routing hint → eliminates LLM routing call for typed queries. |
| `user_interaction/troubleshooting_prompts.jsonl` (60 prompts) | Build the "Troubleshooting" Streamlit page around these — each has a `scenario_id`, `prompt`, `reasoning_chain`, `resolution_options[graded]` | Use `resolution_options` (graded 1–3) as the inline feedback target for FR6; judge taps correct → feedback written immediately. |
| LangGraph SqliteSaver checkpointer | `data/sessions.db` (already wired in build) | Per-session `thread_id` → full conversation history; multi-turn context is structural, not prompt-pasted | Turn-2+ always resumes from checkpoint → no context truncation. |

---

### FR4 — Explainable + Traceable Recommendations

| Dataset files | How to use | Max-output tactic |
|---|---|---|
| `SPEC/ground_truth_spine.json` — `correct_resolution` steps + `root_cause` + `spares_required` | Spine is the citation anchor; every LLM answer must cite a `scenario_id`, a `doc_id` (manual/SOP/RCA), and a `sensor_tag` | Pydantic `MaintenanceRecommendation.cited_sources: list[Citation]` (already in `wizard/core/schemas.py`) — enforce non-empty; refuse to emit a recommendation without ≥1 citation. |
| `failure_analysis_reports/RCA-001…025-*.md` + `index.jsonl` | RCA reports contain exact section headings → retrieve the relevant §N and embed as `[1]` footnote in the UI | Each RCA answer renders as: `sensor spike (§2.1 of RCA-017) → root cause bearing spall (ISO 15243:2017 Stage 3) → repair step 3 of SOP-05 §4.2`. |
| Arize Phoenix local trace | `wizard/backend/app.py` Phoenix auto-instrument | `px.launch_app()` shows every LangGraph node fired + tool calls + latency in a local trace UI | In the demo recording, cut to the Phoenix trace view for 15 seconds — judges see the full agent reasoning chain visually. |
| NLI faithfulness gate | `wizard/rag/faithfulness.py` (existing module) | Post-retrieval NLI check: does the LLM answer entail the retrieved chunk? If not, suppress or flag `[unverified]` | No hallucinated citations ship — the faithfulness gate is the last filter before SSE fan-out to UI. |

---

### FR5 — Anomaly Detection + Failure Prediction

| Dataset files | How to use | Max-output tactic |
|---|---|---|
| `condition_monitoring/sensor_timeseries_long.csv` (585,312 rows, 0% null, cols: `timestamp, asset_id, equipment_class, sensor, value, unit, fault_label, rul_cycles, severity`) | Primary training source for IsolationForest + LSTM-AE anomaly and LightGBM failure predictor | Long format → tsfresh feature extraction per window; `fault_label` is the classification target; `rul_cycles` is the regression target. |
| `condition_monitoring/by_equipment/*.csv` (15 dense tables, 8,736 rows each, 0% null, DataForge composite 89–93) | Model-ready per-equipment classification tables — no reshaping needed | Train one LightGBM per equipment class (15 models, joblib-serialised); ensemble via `wizard/ml/registry.py`; this is the "15 specialist models" differentiator vs one generic model. |
| `condition_monitoring/rul_trajectories_long.csv` (81,336 rows, run-to-failure windows) | WeibullAFTFitter training: RUL regression using degradation index as covariate | Long format with RTF trajectories → direct WeibullAFT fit; piecewise-linear RUL cap; per-asset normalize. |
| `condition_monitoring/anomaly_alerts.csv` (19,918 rows) | Threshold-calibration ground truth: align IsolationForest adaptive thresholds to match the spine warning/alarm bands (confirmed 0 disagreement) | Use pre-computed alert thresholds from spine `warning_threshold` / `alarm_threshold` as the River HST baseline; IsolationForest is the online adaptation layer on top. |
| `condition_monitoring/process_condition_indicators.csv` (5,460 rows) | Multi-variate process context (pressure, flow, temperature at process level) | Feed as additional features into LightGBM failure predictor; process-context features distinguish operating regime → reduces false positives. |
| `SPEC/ground_truth_spine.json` — `degradation_timeline` + `sensor_signature` per failure scenario | Labelled per-stage anomaly ground truth (AE +6dB = Stage 1, BPFO 1.0→3.0g = Stage 3) | Use `sensor_signature.threshold_crossed=True` rows as the anomaly label seed for LSTM-AE evaluation; Stage-tagged labels enable staged-alert logic (warn early, alarm late). |
| `additional/alarm_rationalization.csv` — ISA-18.2 priority tiers | Validates that ML anomaly scores above P1/P2 thresholds trigger the right alert tier | Hard-wire P1 events (caster breakout, compressor surge, conveyor fire-risk, ladle crane wire-rope) to CRITICAL tier regardless of ML score → safety floor. |

**Demo automation beat (highest-scoring moment):** APScheduler 5s tick replays `sensor_timeseries_long.csv` from `t=0`; at the pre-seeded EAF-04 breakout window (~90s into playback), the anomaly score crosses the threshold → auto-fires CRITICAL alert with RUL + RCA + plan, zero user input. This beat is the proof of "agentic."

---

### FR6 — Feedback-Driven Improvement

| Dataset files | How to use | Max-output tactic |
|---|---|---|
| `user_interaction/troubleshooting_prompts.jsonl` — `resolution_options[graded]` | Each resolution option has a `grade` (1=correct, 2=acceptable, 3=wrong). Engineer thumbs-down selects the correct grade → write to `data/feedback/` as JSONL preference pair | One-turn feedback loop: wrong answer → thumbs-down → type correction → re-ask → corrected answer with `[ENGINEER CORRECTION]` badge. Judges see it live. |
| `data/feedback/` (existing dir in build) | Store `{query, wrong_answer, correct_answer, asset_id, timestamp}` as preference JSONL | 3-track feedback: (1) RAG re-rank boost (bump cited doc score +0.2 for 30 days), (2) Bayesian RUL blend (blend engineer-stated remaining life into WeibullAFT posterior), (3) preference JSONL for fine-tune next epoch |
| `additional/work_order_backlog.csv` (43 rows) | When engineer confirms a maintenance action, create a corresponding work-order row in `wizard.db` → the Logbook page shows actioned items | Auto-digital-logbook: PS §7 optional enhancement but trivially demoed and scores presentation points. |
| `data/golden.jsonl` | After 5+ feedback corrections accumulate, re-run DeepEval golden-set gate; if pass-rate holds or improves → auto-accept; else flag to engineer | Continuous-improvement gate with a number judges can see in the Eval page. |

---

### FR7 — Real-Time Alerting Capability

| Dataset files | How to use | Max-output tactic |
|---|---|---|
| `condition_monitoring/anomaly_alerts.csv` (19,918 rows) | Pre-seeded alert backlog shown on the Alerts Streamlit page at startup; demonstrates populated alert queue immediately | Judges see a full alert history table on first load — no "empty state" credibility gap. |
| `condition_monitoring/sensor_timeseries_long.csv` (live replay) | APScheduler 5s tick streams rows chronologically; each tick calls `proactive_evaluator` → IsolationForest score → if above threshold, create alert in `wizard.db` + push via FastAPI SSE | SSE fan-out to `st.fragment(run_every=5)` in Alerts page → live badge counter increments. |
| `SPEC/ground_truth_spine.json` — `safety_class` (ISA-18.2) per scenario | Determines alert tier (P1=CRITICAL, P2=HIGH, P3=MEDIUM, P4=LOW) | P1 events trigger a Streamlit `st.error()` banner (red, full-width) + sound-effect emoji in the sidebar ticker — unmissable for judges. |
| `additional/alarm_rationalization.csv` — `operator_response_time_min`, `nuisance_alarm_flag` | Deduplicate repeat alerts (same asset + same alarm within cooldown window); suppress nuisance alarms flagged in this table | Alarm rationalization is a scored differentiator: judges from Tata know ISA-18.2; showing dedup/cooldown signals industrial maturity. |
| `additional/equipment_master.csv` — `responsible_engineer`, `notification_group` | Route alerts to role-specific views (ops engineer vs maintenance manager) | Role-based alert routing = PS §7 optional enhancement "user-role-based alerts" — cheap to add, high presentation impact. |

---

## Part 2 — Judging Criteria (JC1–JC6 + 7 Webinar Qualities)

### JC1 — Problem Understanding and Solution Approach

**Dataset leverage:** Open the `ARCHITECTURE.md` doc with the PS §4.1–4.4 coverage table copied from `MANIFEST.md` — shows judges that all four stated input categories are handled, with exact file counts (207K rows tabular, 285 JSONL records, 53 documents). The spine's 15-asset, 13-class coverage spanning the full process chain (raw-material → iron-making → sintering → steelmaking → casting → reheating → hot rolling → cold rolling) maps directly to Tata's integrated steel plant structure. State explicitly that `TATA_JSR` is a Jamshedpur-style reference plant. Judges will recognise the process stages.

**Max-output tactic:** `ARCHITECTURE.md` §1 must include the PS-to-dataset coverage table. `BUSINESS_IMPACT.md` must anchor to Tata's own published KPIs: 15% unplanned-downtime reduction on rolling mills, ₹45 Cr/yr per blast furnace, ₹1.4B total AI savings (sourced from `research/domain/01_tata_r2_judge_intel.md`).

---

### JC2 — Effective Use of Agentic AI Frameworks and Concepts

**Dataset leverage:** The 6-agent LangGraph supervisor topology (Diagnosis → RCA → RUL → Prioritization → Plan → Report) maps one-to-one to the PS §5.1–5.4 expected outputs. Each agent has a dedicated tool set (`wizard/agents/tools.py`) that queries a specific dataset modality. The checkpointed `MaintenanceState` TypedDict carries the full reasoning trace across agents.

**Max-output tactic:** The 90-second EAF-04 proactive CRITICAL alert is the #1 demo beat proving "agentic." Wire it to the sensor playback from `sensor_timeseries_long.csv`. The pre-seeded scenario in `ground_truth_spine.json` (`eaf_bof_auxiliary` breakout scenario) provides exact sensor signatures and timing. Ensure the demo recording captures the Arize Phoenix trace showing all 6 agent nodes firing with latency — this is the visual proof of the agentic pipeline.

---

### JC3 — Technical Implementation and Innovation

**Dataset leverage:** Three differentiators most competitors will not have:
1. **15 per-equipment dense ML models** (from `by_equipment/*.csv`, DataForge composite 89–93) — not one generic model.
2. **Physics-grounded alarm thresholds** (from spine `warning_threshold`/`alarm_threshold` backed by ISO 10816-3, ISO 15243, NEMA MG1, ISA-18.2) — not arbitrary percentiles.
3. **ISA-18.2 alarm rationalization** (from `alarm_rationalization.csv`) — nuisance-alarm dedup, a real industrial practice.

**Max-output tactic:** In `ARCHITECTURE.md`, include a table: "Why our ML is not a black box" — cite each standard, each `by_equipment` table, each DataForge score. Fine-tuned Qwen2.5-3B (if it passes the 50-ex eval gate) is the stretch differentiator — FR1 extra-merit clause.

---

### JC4 — Scalability and Real-World Applicability

**Dataset leverage:** `equipment_master.csv` (15 assets, 13 classes) + spine's ISA-95 tag hierarchy shows the system handles a heterogeneous fleet, not one asset type. The `additional/` tier (CMMS work orders, alarm DB, shift handovers, OEM bulletins) mimics the data landscape of a real CMMS (SAP PM / Maximo).

**Max-output tactic:** `ARCHITECTURE.md` §Scalability: "Adding a new equipment class = one new `by_equipment/*.csv` + one new manual + one new SOP. The RAG pipeline, ML registry, and LangGraph agents are equipment-agnostic by design." State the synthetic-data disclaimer honestly (per `datacard.md` §7) — judges score honesty; hiding it would be worse.

---

### JC5 — Quality of Presentation and Communication

**Dataset leverage:** `user_interaction/nl_queries.jsonl` — use 3 high-quality queries as the scripted demo beats (one diagnostic, one predictive, one spares/procurement). Each has `expected_output` and `grounding_refs` → the demo answers match these exactly (no hallucination, no awkward pauses).

**Max-output tactic:** The 8 scripted demo wow-moments from `MASTER_BRIEF.md §7` map to specific dataset files:
- Live Cost-Avoidance Ticker → `cost_impact` from spine scenarios (₹ per event).
- Traceable Diagnosis Chain → `cited_sources` from `RCA-*.md` section headings.
- Spares/procurement angle → `spare_parts_catalog.csv` `lead_time_weeks` × `unit_cost_inr`.
- Business framing → Tata KPIs from `research/domain/01`.

The Streamlit recording must show the Alerts page counter incrementing live, the cost ticker growing, and the Phoenix trace — three visual proofs of a running system, not a slide deck.

---

### JC6 — Business Impact and Feasibility

**Dataset leverage:** `SPEC/ground_truth_spine.json` `cost_impact` field on each failure scenario (sourced from `research/machinery/20_cost_downtime_economics.md`) — caster breakout $860k/event, BF blower failure $4–8M+, roll change unplanned vs planned 16.4× multiplier, CRM cobble ~₹21 L/hr.

**Max-output tactic:** `BUSINESS_IMPACT.md` must compute: "If the Wizard catches 1 caster breakout/year → ₹7.2 Cr saved. If it reduces roll-change unplanned rate by 20% → ₹X Cr/yr." Use the `cost_impact` + `downtime_hours` fields from spine scenarios as the calculation inputs. Anchor to Tata's published ₹1.4B AI savings goal. The live Cost-Avoidance Ticker in the UI translates this into a number a business judge feels in real time.

---

### 7 Webinar Qualities

| Quality | Dataset + build tactic |
|---|---|
| **Fast** | Deterministic Python router for intent classification (no LLM for typed queries). LanceDB hybrid retrieval (ONNX embeddings, no GPU). Demo golden cache in `data/golden.jsonl` → scripted beats never hit live LLM → sub-2s response on demo machine. |
| **Efficient** | LLM called only for synthesis (final answer generation), not for retrieval or routing. bge-small ONNX (not bge-base) → 3× faster embedding. 15 per-equipment LightGBM models at inference are 5–10ms each. |
| **Accurate** | `ground_truth_spine.json` exact thresholds (ISO-backed) feed the anomaly detector; faithfulness NLI gate (`wizard/rag/faithfulness.py`) blocks hallucinated citations; DeepEval golden-set gate enforces ≥80% pass before demo recording. |
| **Easy to use** | `nl_queries.jsonl` 3 pre-populated example queries in the Chat sidebar lower the barrier to first interaction. Troubleshooting page uses `troubleshooting_prompts.jsonl` scenario cards with one-click launch. |
| **Doesn't break** | Circuit breaker (pybreaker) + tenacity retry in `wizard/backend/app.py`. Gemini 429 / no internet → LiteLLM auto-fallback to Qwen2.5-3B Ollama in <2s. Golden-cache responses for all 10 demo beats. Cold-start test on clean venv before recording. |
| **No errors** | Pydantic v2 discriminated-union schemas enforce all I/O contracts; `MaintenanceRecommendation` rejects empty `cited_sources`. All 15 `by_equipment` tables are 0%-null → no NaN-handling crashes during inference. `work_order_backlog.csv` and `alarm_rationalization.csv` pre-validated (zero orphans). |
| **Smooth** | `HAPPY_PATH.md` scripted deterministic demo (per `MASTER_BRIEF.md §7`). SSE streaming + `st.write_stream` + `st.fragment(run_every=5)` give the UI continuous motion. Cost ticker sidebar increments smoothly via `st.metric`. |

---

## Part 3 — Gaps and Extension Recommendations

### Gap 1 — No EAF-04 specific demo asset in the dataset
**Problem:** `MASTER_BRIEF.md` scripts the #1 demo beat around "EAF-04" but the spine uses `eaf_bof_auxiliary` as an equipment class, not an asset ID named EAF-04.  
**Fix:** In `SPEC/ground_truth_spine.json`, add a spine asset with `asset_id: EAF.AUX.HYD01` aliased as `EAF-04` in `equipment_master.csv`. The `eaf_bof_auxiliary.csv` dense table already exists; add a `demo_asset_alias=EAF-04` column to `equipment_master.csv`. Cost: 30 min.

### Gap 2 — No streaming sensor playback format
**Problem:** The APScheduler demo beat needs a pre-sequenced sensor stream for EAF-04 timed to trigger at ~90s. The current `sensor_timeseries_long.csv` is a flat export, not a demo-ordered sequence.  
**Fix:** Create `data/demo/eaf04_breakout_replay.csv` — a 200-row subset of `sensor_timeseries_long.csv` filtered to `asset_id=EAF.AUX.HYD01`, sorted chronologically, with the breakout anomaly window at rows 90–110 (so the APScheduler 5s tick fires the CRITICAL alert at ~t=90s). This is a view, not new data. Cost: 1 Python script, 20 min.

### Gap 3 — DeepEval golden set is a stub
**Problem:** `data/golden.jsonl` exists but is flagged as a stub in the build. The eval gate in JC3/JC7 (webinar "accurate") requires ≥20 graded pairs.  
**Fix:** Derive 20 golden QA pairs directly from `user_interaction/nl_queries.jsonl` (150 queries, each has `expected_output` + `grounding_refs`). Take the top 20 by `complexity_score` desc → write to `data/golden.jsonl`. Each pair is already grounded in the spine → faithfulness ≥1.0 by construction. Cost: 1 Python script, 30 min.

### Gap 4 — Feedback loop has no pre-seeded preference JSONL for demo
**Problem:** FR6 demo beat ("thumbs-down → correction → badge") requires at least 1 pre-seeded correction to show the `[ENGINEER CORRECTION]` badge without live input.  
**Fix:** Write `data/feedback/seed_corrections.jsonl` with 3 pre-seeded corrections (one per equipment class: bearing / pump / gearbox) derived from the `resolution_options[graded]` in `troubleshooting_prompts.jsonl`. Load on startup → the Logbook page shows "3 engineer corrections applied" immediately. Cost: 10 min.

### Gap 5 — LLM migration from Gemini to Claude subscription not yet done
**Problem:** `wizard/core/config.py` and `wizard/agents/nodes.py` still reference Gemini/LiteLLM. The hard constraint is Claude Max subscription only.  
**Fix:** Adopt the exact `_load_oauth_token` + `_subscription_review` pattern from `dataforge/api/scorer/agent.py` (lines 354–420). Replace `litellm.acompletion(model="gemini/gemini-2.5-flash", ...)` calls in `nodes.py` with the subscription pattern. LiteLLM gateway stays as the interface layer so Ollama fallback still works. The subscription path is `claude-agent-sdk` → `query()` async generator → collect text. Cost: 2–3h, highest priority, must-fix before any demo.

### Gap 6 — No role-based alert routing wired
**Problem:** `equipment_master.csv` has `responsible_engineer` and `notification_group` columns but the alert routing in `wizard/backend/app.py` ignores them.  
**Fix (stretch, 30 min):** On alert creation, query `equipment_master` for `responsible_engineer` → prepend to the SSE alert payload → the Alerts page shows "Assigned to: [Name]." Scores PS §7 "user-role-based alerts" optional enhancement.

---

## Summary Table — Dataset Files by Requirement

| Requirement | Primary files | Secondary / enrichment |
|---|---|---|
| FR1 LLM reasoning | All 53 Markdown docs + `nl_queries.jsonl` (fine-tune corpus) | `golden.jsonl` (cache), `multiturn_conversations.jsonl` |
| FR2 Knowledge integration | `equipment_manuals/*` + `maintenance_sops/*` + `RCA-001…025-*.md` + `historical_maintenance_records.csv` + `spare_parts_catalog.csv` | `oem_service_bulletins.md` + `shift_handover_notes.md` + `alarm_rationalization.csv` |
| FR3 Multi-turn NL | `multiturn_conversations.jsonl` + `nl_queries.jsonl` + `troubleshooting_prompts.jsonl` | `sessions.db` (LangGraph checkpoint) |
| FR4 Explainability | `ground_truth_spine.json` (citation anchors) + `failure_analysis_reports/index.jsonl` | Arize Phoenix trace + `faithfulness.py` NLI gate |
| FR5 Anomaly + prediction | `sensor_timeseries_long.csv` + `by_equipment/*.csv` + `rul_trajectories_long.csv` + `anomaly_alerts.csv` | `process_condition_indicators.csv` + spine `degradation_timeline` + `alarm_rationalization.csv` |
| FR6 Feedback loop | `troubleshooting_prompts.jsonl` (graded resolutions) + `data/feedback/` | `work_order_backlog.csv` + `golden.jsonl` |
| FR7 Real-time alerting | `anomaly_alerts.csv` + `sensor_timeseries_long.csv` (live replay) | `alarm_rationalization.csv` (dedup/cooldown) + `equipment_master.csv` (routing) |
| JC1 Problem understanding | `MANIFEST.md` coverage table + spine process chain | `MASTER_BRIEF.md` PS-anchored intro |
| JC2 Agentic use | 6-agent LangGraph topology + spine `failure_scenario_catalog` | Arize Phoenix trace + SqliteSaver checkpoint |
| JC3 Technical innovation | `by_equipment/*.csv` (15 specialist models) + spine ISO thresholds | `alarm_rationalization.csv` (ISA-18.2) + fine-tuned Qwen2.5-3B |
| JC4 Scalability | `equipment_master.csv` (15 assets, 13 classes) + CMMS `additional/` tier | `ARCHITECTURE.md` §Scalability |
| JC5 Presentation | `nl_queries.jsonl` (demo scripts) + spine `cost_impact` | 8 scripted wow-moments in `HAPPY_PATH.md` |
| JC6 Business impact | Spine `cost_impact` + `downtime_hours` + `research/domain/01` Tata KPIs | Live Cost-Avoidance Ticker (₹/session) |
| W1–W7 (Webinar) | `golden.jsonl` (fast/no-break) + `by_equipment/*.csv` 0%-null (no errors) + `troubleshooting_prompts.jsonl` (easy-to-use) | `HAPPY_PATH.md` + circuit breaker + Ollama fallback |
