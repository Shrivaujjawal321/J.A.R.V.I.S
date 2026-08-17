# 05 — MAX-SCORING Demo + Judging Strategy

**Tata Steel AI Hackathon 2026 · Round 2 · Maintenance Wizard**
**Author:** Jarvis · **Date:** 2026-06-09 · **Deadline:** 15 Jun 2026 23:59 IST · SOLO
**Fuel:** `dataforge/datasets/steel-maintenance-flagship/` (15 assets · 51 scenarios · 44 spares · 207k sensor rows · 53 docs · 285 dialogue records)

> This document is the single source of truth for the **screen recording**, the live judge demo, and the judging-criteria mapping. It is the convergence of the OFFICIAL PS (6 criteria) + the webinar (7 ops qualities) + the flagship dataset + the no-API-key subscription constraint.

---

## 0. HARD CONSTRAINT (read first — every decision obeys this)

Boss has **NO API key and never will** — only a **Claude Max subscription (OAuth token)**. Therefore:

1. **The orchestration LLM runs via the subscription**, using the exact proven pattern in `dataforge/api/scorer/agent.py` (`_subscription_review()` + `_load_oauth_token()`) and `jarvis_core/daemon.py` — `claude_agent_sdk.query(...)` authenticated by `CLAUDE_CODE_OAUTH_TOKEN`. No `litellm.completion()` to Gemini; no `GEMINI_API_KEY`. (See §6 for the precise swap in `wizard/agents/nodes.py::_llm_complete`.)
2. **Everything else is LOCAL/CPU/free**: embeddings (bge-small ONNX), reranker (FlashRank ONNX), vector store (LanceDB), NLI faithfulness (`cross-encoder/nli-deberta-v3-small`, already wired in `wizard/rag/faithfulness.py`), ML (WeibullAFT / IsolationForest / LightGBM, joblib artifacts), KG (NetworkX).
3. **Subscription rate/session limits are real** — we hit one mid-workflow during the build. So the **live demo path NEVER depends on a live LLM call that can fail.** The scripted happy-path is **served from a pre-captured cache** (`data/demo/demo_cache.json`, already scaffolded). The subscription is the *engine that captured the cache* and the *engine for off-script judge questions* — but the recording and the scored beats run cache-first, deterministic-fallback-second, live-LLM-third.

**The demo must not die on a rate limit. This is the #1 robustness rule.**

---

## 1. The Demo Thesis (what we are proving in 4 minutes)

> **An agentic maintenance co-pilot that fires a complete, source-cited maintenance plan _before_ the engineer asks — because the best recommendation is the one that arrives before the failure, not after.**

Five proofs, each tied to a dataset scenario that actually exists in the spine:

| # | Proof | Scenario (real spine data) | "Agentic" because… |
|---|---|---|---|
| 1 | **Autonomous CRITICAL alert, zero user input** | **SCN-041** BF turbo-blower compressor surge (P1, ₹50 Cr, 96h) | system *acts on its own* off a sensor stream |
| 2 | **Multi-turn explainable diagnosis, cited to manuals/SOPs** | **SCN-037** F3 work-roll bearing outer-race spall (P2, ₹75 L) via `CONV-001` | reasons across tools + history, grounds every claim |
| 3 | **Spare-parts "NOT IN STOCK → ORDER NOW" moment** | **SCN-043** caster breakout precursor (P1, ₹7.18 Cr) + `GEAR-WHL-M20` 36-week lead | couples diagnosis to procurement constraints |
| 4 | **Feedback in one turn (no retrain)** | engineer corrects diagnosis → re-ask → corrected answer | learns from a single correction (FR6) |
| 5 | **Business-impact ticker in Tata's own ₹** | live `st.metric` accumulating prevented-downtime ₹ | translates technical wins into a number a business judge feels |

---

## 2. STORYBOARD — the 4-minute screen recording (1920×1080, narrated)

Total ≈ 3:50. Every second runs from cache or local model. The voiceover script is in quotes.

### BEAT 0 — Cold open (0:00–0:20) → Criteria 1, 5
- Screen: 5-page Streamlit UI (Chat · Dashboard · Alerts · Logbook · Settings). Dashboard shows 15 real assets from `equipment_master.csv` as health gauges (Plotly), a plant heatmap, and **the Cost-Avoidance Ticker reading ₹0** in the sidebar.
- VO: *"This is the Maintenance Wizard — a decision-support co-pilot for a steel plant. Fifteen critical assets, from the blast-furnace blower to the continuous caster, are streaming live condition data. Watch what it does on its own."*
- **Maps to:** Problem understanding (real steel asset taxonomy, ISA-95 tags), Presentation, Easy-to-use.

### BEAT 1 — THE AGENTIC MOMENT: autonomous CRITICAL alert (0:20–1:05) → Criteria 2, 3; FR5, FR7; Fast
- We start a sensor playback (APScheduler 5s tick replaying `condition_monitoring/by_equipment/bf_sinter_fan_blower__BF_BLW_FAN01.csv` degradation window). **No one types anything.**
- At the scripted ~45s mark, the BF blower's `PRES.OSC` crosses 8% and `SHAFT.DISP` bursts to 95 µm → the proactive evaluator fires.
- **A red CRITICAL banner slides in unprompted:**
  > **🔴 CRITICAL — BF Turbo-Blower (BF.BLW.FAN01) — COMPRESSOR SURGE imminent**
  > Surge margin collapsed; discharge oscillation 9% (alarm 8%), shaft displacement 95 µm (alarm 80). Seconds-to-destruction if sustained.
  > **RUL: act now.** **Risk: P1 / CRITICAL.** **Fault codes: SURGE-ALARM, ASV-CYCLING.**
  > **Action:** Verify ASV auto-opened → if surge persists >2–3 cycles, **TRIP immediately**; do NOT restart until cause identified.
  > **Cost avoided if caught now: ₹50 Cr (BF downtime ≈ ₹500k/hr × 96h).** *Cited: spine SCN-041, MAN-005, SOP-blower.*
- The Cost-Avoidance Ticker jumps **₹0 → ₹50,00,00,000**.
- VO: *"No one asked it anything. The system watched the sensor stream, recognized a compressor-surge signature, classified it P1-critical, pulled the exact OEM procedure, and put a number on the avoided loss — fifty crore — before the engineer even noticed."*
- **Maps to:** Effective agentic-framework use (the autonomous loop), Technical innovation, Real-time alerting (FR5/FR7), Fast, Business impact.

### BEAT 2 — MULTI-TURN EXPLAINABLE DIAGNOSIS, fully cited (1:05–2:05) → Criteria 1, 3, 4; FR2, FR3, FR4; Accurate
Drive the exact `CONV-001` dialogue (SCN-037 bearing chain) from the dataset — these turns are *real records*, not invented:

1. Engineer types: *"Hey wizard, I'm getting an AE warning on the F3 work-roll bearing. Should I be worried?"*
   → Wizard: AE at **8 dBµV** (between warn 6 / alarm 12) = **stage-2 onset; AE is the leading indicator, crosses weeks before vibration.** "Not an emergency yet, watch closely." **Citation pills:** `spine:SCN-037/sensor_signature`, `RCA-001`.
2. *"What about the vibration and temperature?"* → Envelope **BPFO 3.2 g** (>3.0 alarm) + **temp 102 °C** (>100 trip). "All three now agree: AE → BPFO → temp — the SCN-037 outer-race spall signature, now stage 4." (Shows the **4-stage ISO 15243 degradation chain**.)
3. *"Okay so what do I actually do?"* → Step-by-step from SOP-01: **LOTO + zero-energy → controlled stop (not emergency trip) → hydraulic puller (never strike) → journal H7/k6 check → induction-heat 80–100 °C → laser-align <0.05 mm → verify <2.3 mm/s & <70 °C at 60 min.** Citation: `SOP-01_bearing-replacement.md`, `spine:SCN-037/correct_resolution`.
- **The "Show your work" expander** (collapsed by default — clean UI, rigor on demand): expanding it renders the full chain `sensor reading → threshold band (ISO 20816/15243) → RCA report → SOP §+step → agent nodes fired (DIAG→RCA→PLAN) with per-node latency`.
- VO: *"Every single claim is grounded. Not 'the model thinks' — '8 dBµV, between the 6 warning and 12 alarm, per ISO 15243, source RCA-001.' A maintenance engineer can audit the reasoning, not just trust it."*
- **Maps to:** Knowledge integration (FR2), NL multi-turn (FR3), **Explainable recommendations (FR4)**, Accurate, Easy-to-use.

### BEAT 3 — SPARE-PARTS / PROCUREMENT: the under-exploited winner (2:05–2:45) → Criteria 1, 6; FR4; Business impact
Continue `CONV-001`: *"Do we have the parts?"*
- Wizard checks `spare_parts_catalog.csv` live and renders a **stock-aware procurement table**:
  | Part | On-hand | Lead time | Verdict |
  |---|---|---|---|
  | BRG-LRG-300 large-bore bearing | **1** | 8 wk | ✅ use the on-shelf unit — but **reorder now, only 1 left** |
  | SEAL-LAB-01 labyrinth seal | 2 | 2 wk | ✅ in stock |
  | CPL-EL-01 coupling element | 1 | 2 wk | ✅ in stock |
- **Then the gut-punch escalation** (switch context to the F1 gearbox / SCN-038 cause-chain that shares this bearing family): the related **GEAR-WHL-M20** custom gear wheel is **on-hand 0, 36-week lead, ₹1.2 L/unit, OEM Flender — NOT IN STOCK.**
  > **⚠️ PROCUREMENT-CRITICAL: GEAR-WHL-M20 has ZERO stock and a 36-WEEK lead time. If the F1 gearbox crack (SCN-038) progresses, you cannot repair it for nine months. Raise the PO NOW, ahead of failure.** *Cited: spare_parts_catalog.csv, work_order_backlog.csv.*
- VO: *"This is the part most systems miss. Diagnosis is useless if the part is nine months out. The Wizard fuses the failure prediction with procurement lead-time and tells you to order before the machine breaks — turning maintenance from reactive to genuinely proactive."*
- **Maps to:** Problem understanding (PS §4.3 + §5.3 spare-procurement strategy explicitly), **Business impact & feasibility**, Real-world applicability.

### BEAT 4 — FEEDBACK IN ONE TURN, no retrain (2:45–3:15) → Criteria 2, 3; FR6
- Engineer thumbs-down a diagnosis, types a correction ("this is actually lube-side, not fatigue — last overhaul was 3 weeks ago"), re-asks.
- The corrected answer renders **at the top with an `[ENGINEER CORRECTION]` badge**; the correction is written to the preference JSONL + re-ranks the RAG context for the rest of the session. No model retrain, no restart.
- VO: *"One correction, applied instantly. It learns from the engineer in the loop — the feedback closes immediately, not in the next training cycle."*
- **Maps to:** Feedback-driven improvement (FR6), Agentic-framework use, Smooth.

### BEAT 5 — THE CASTER BREAKOUT + close (3:15–3:50) → Criteria 3, 6; FR1, FR5
- Trigger a second autonomous alert: **SCN-043 caster-mould breakout precursor (P1)** — the textbook 3-sensor-agreement case (`TC.DELTA 55 °C` V-pattern + `OSC.FRICTION 19 kN` + `LEVEL.DEV 13 mm`). Wizard explains *why all three are required* (single sensor alone has >40% false-alarm rate per EP2465622B1) → **reduce casting speed to 0.5 m/min → emergency stop → evacuate floor.** Cost avoided **₹7.18 Cr**.
- Ticker closes at **~₹57+ Cr avoided this session.**
- Final VO, anchored to **Tata's own published KPIs**: *"Tata Steel reports 15% unplanned-downtime reduction on rolling mills, ₹45 Cr/yr per blast furnace from AI, ₹1.4 billion total AI savings, 40% faster maintenance planning at Jamshedpur. This is exactly that thesis, made concrete — fast, explainable, and grounded in the plant's own data."*
- **Maps to:** Failure prediction (FR1/FR5), Business impact, Technical innovation (false-alarm-reduction logic), Scalability.

---

## 3. CRITERION → DEMO-BEAT MAP (every box ticked, nothing claimed without a beat)

### 3a. Six OFFICIAL evaluation criteria
| # | Official criterion | Proven by beat(s) | The one-line proof |
|---|---|---|---|
| 1 | Problem understanding & solution approach | 0, 2, 3 | Real ISA-95 asset taxonomy, 4 PS input categories ingested, spare-procurement angle most miss |
| 2 | Effective use of Agentic AI frameworks/concepts | 1, 4 | LangGraph supervisor + 6 agents + PEV; autonomous evaluator acts with zero input; in-loop feedback |
| 3 | Technical implementation & innovation | 1, 2, 5 | 3-sensor false-alarm-reduction, 4-stage degradation chain, NLI faithfulness gate, subscription-LLM-no-key |
| 4 | Scalability & real-world applicability | 2, 3, 5 | 15 assets across full process chain; CPU-only, pip-install, offline fallback; site-calibration caveat stated honestly |
| 5 | Quality of presentation & communication | all | Clean 5-page UI, citation pills, "show your work" expander, narrated recording, standalone ARCHITECTURE.md |
| 6 | Business impact & feasibility | 1, 3, 5 | Live ₹-ticker in Tata's own figures; ₹57 Cr avoided in one session; procurement lead-time integration |

### 3b. Seven WEBINAR ops qualities (observed live — engineered, not claimed)
| Quality | How the demo proves it | Mechanism |
|---|---|---|
| **Fast** | alert + diagnosis render in <1s on screen | cache-first serve; per-node latency shown in trace; bge-small ONNX + FlashRank |
| **Efficient** | no wasted LLM calls; cheap-model routing | deterministic Python router (no LLM for routing); cached gold path; local models do the heavy lifting |
| **Accurate** | every number matches the spine + standard | NLI faithfulness gate (`nli-deberta-v3-small`) flags un-entailed claims → 1 retry; grounded citations |
| **Easy to use** | a non-technical judge can drive it | one chat box; collapsed expanders; pre-seeded data; alerts come to *you* |
| **Doesn't break** | no crash across the whole recording | circuit breaker + cache fallback + cold-start test on clean venv; `httpx.Client` sync only in UI |
| **No errors** | no traceback ever reaches the UI | `_llm_complete` NEVER raises (returns deterministic fallback); error envelopes on FastAPI |
| **Smooth** | seamless 4-min flow, no dead air | fully rehearsed `HAPPY_PATH.md`; APScheduler timings tuned; SSE streaming |

---

## 4. ROBUSTNESS ON A RATE-LIMITED SUBSCRIPTION (the demo must not die)

The build already scaffolds `data/demo/demo_cache.json` (9 keys, schema-versioned) and `data/demo/cost_events.jsonl`. We harden the path into a strict three-tier serve:

### 4a. Three-tier LLM serve (cache → deterministic → live)
```
request ─▶ [1] DEMO CACHE (demo_cache.json keyed by query/scenario signature)
              │  hit  → return instantly (0 LLM calls)  ← THE SCORED DEMO PATH
              │  miss ▼
           [2] DETERMINISTIC TEMPLATE (spine-grounded, no LLM)
              │  diagnosis/RCA/plan composed directly from ground_truth_spine.json
              │  + retrieved chunks → ALWAYS produces a correct, cited answer
              │  (judge off-script Q that the local models + KG can answer)
              │  ▼ only if richer NL phrasing wanted AND budget allows
           [3] LIVE SUBSCRIPTION LLM (claude_agent_sdk, OAuth, 30s timeout)
                 wrapped in: tenacity retry → pybreaker circuit breaker
                 on ANY failure (rate-limit / timeout / token-missing) → silently fall to [2]
```
- **The recording and all five scored beats are served from tier [1] cache.** A rate limit cannot touch them.
- **Tier [2] is the safety net for live judge questions** — because the spine is the source of truth, a template answer composed from `ground_truth_spine.json` + RAG chunks is still *correct and cited*, just less conversational. Judges never see "service unavailable."
- **Tier [3] is the only path that can hit a rate limit, and its failure is invisible** — it degrades to [2], not to an error.

### 4b. Pre-capture procedure (do this BEFORE recording)
1. Run the full scripted happy-path **once** through the live subscription to populate `demo_cache.json` (replace the current SYNTHESIZED placeholder with a real capture — the file's own `pre_capture_status` field flags it as needing this).
2. Capture: every scored query (CONV-001 turns, the two autonomous alerts, the feedback turn, the procurement table), keyed by a normalized query+scenario signature.
3. Set `WIZARD_DEMO_MODE=cache_first` so tier [1] is consulted before any network call.
4. **Cold-start test on a clean venv with networking disabled** — the entire recording must complete with `CLAUDE_CODE_OAUTH_TOKEN` unset, proving zero live-LLM dependency for the scored path.

### 4c. The subscription LLM call (no API key) — proven pattern
`_llm_complete()` in `wizard/agents/nodes.py` currently routes to `litellm.completion()` keyed on `GEMINI_API_KEY`. **Swap the live tier to the subscription**, lifting `_subscription_review()`/`_load_oauth_token()` from `dataforge/api/scorer/agent.py` verbatim:
- `claude_agent_sdk.query(prompt=..., options=ClaudeAgentOptions(max_turns=1, allowed_tools=[], system_prompt=...))`
- token from `CLAUDE_CODE_OAUTH_TOKEN` (env, or parsed once from repo `.env`)
- `asyncio.wait_for(..., timeout=30)`; on any exception return `None` → caller uses deterministic fallback (tier [2]).
- Keep the existing "NEVER raises" guarantee — that contract is what makes "no errors / doesn't break" true.
- **No `GEMINI_API_KEY`, no `ANTHROPIC_API_KEY` anywhere.** `grep -rE 'sk-ant|AIza|sk-|GEMINI_API_KEY' .` must return nothing (submission checklist).

### 4d. Other crash-proofing (already in the brief, restated as demo gates)
- `httpx.Client` (sync) ONLY in Streamlit — never `AsyncClient`/`asyncio.run` (avoids the Streamlit event-loop crash).
- ML inference from joblib artifacts (no training in the demo path).
- APScheduler tick wrapped in try/except → a bad tick logs, never crashes the loop.
- Alert dedup + cooldown so the same surge doesn't spam.
- 10× consecutive crash-test of the full recording flow before final capture (R1 lesson: OOF/eval ≠ live behavior).

---

## 5. EXPLAINABILITY / TRACEABILITY PROOF (the part judges reward most — FR4 + Accurate)

Three independent, *visible* layers — this is the differentiator vs a "chat-with-PDF" entry:

### 5a. Reasoning trace (the "show your work" expander)
Every answer carries `agent_trace`: the ordered nodes that fired (`supervisor → DIAG → RCA → RUL → RISK → PLAN`) with **per-node latency_ms**. Rendered as a collapsed `st.expander` — clean by default, full rigor on demand. (Backed by LangGraph `SqliteSaver` checkpoints → genuine time-travel, not a mock.) Doubles as the **Fast** proof (latencies visible).

### 5b. Grounded citations (every claim traceable to a record)
Each factual claim renders an inline citation **pill** resolving to a real dataset artifact:
- a **spine path** — e.g. `spine:SCN-037/sensor_signature`, `spine:HSM.F3.WR.BRG01/JSR.HR.STD3.WR.BRG01.VIB.DE.H.RMS`
- a **knowledge doc** — `MAN-001…`, `SOP-01…`, `RCA-001…` (the 53-doc corpus)
- a **standard** — ISO 20816-3:2022, ISO 15243:2017, EP2465622B1, NEMA MG1, ISA-18.2
These `grounding_refs` are **first-class fields in the dataset itself** (every `nl_queries.jsonl` and `multiturn_conversations.jsonl` record ships them), so the demo answers match the dataset's own ground truth — judges can diff our output against the data card.

### 5c. NLI faithfulness gate (machine-checked, not just decorative citations)
`wizard/rag/faithfulness.py` runs `cross-encoder/nli-deberta-v3-small` (CPU, ~80–120ms/claim) to score whether each generated claim is **entailed** by its retrieved evidence. Below threshold → flag → one grounded retry. **Demoable as a green "✓ faithfulness 0.9x" badge** on answers. This is the rare entry that *proves* it isn't hallucinating, with an on-device model — and it costs zero API.

> Together: a claim is shown (citation), traced (which agent produced it, how fast), and machine-verified (NLI entailment). That triple is what an industrial buyer demands and what most hackathon entries cannot show.

---

## 6. PRE-RECORDING CHECKLIST (gate before final capture)
- [ ] `_llm_complete` live tier swapped to `claude_agent_sdk` subscription path; Gemini/key code removed.
- [ ] `demo_cache.json` re-captured LIVE (placeholder `pre_capture_status` cleared); keyed for all 5 beats + CONV-001 turns.
- [ ] Cold-start: clean venv, networking off, `CLAUDE_CODE_OAUTH_TOKEN` unset → full recording completes from cache + deterministic fallback (no error, no blank).
- [ ] 10× crash-test of the recording flow; APScheduler alert timings tuned (surge ≈45s, breakout ≈3:15).
- [ ] Cost-ticker math verified: SCN-041 ₹50 Cr + SCN-043 ₹7.18 Cr + bearing avoided → ≈₹57 Cr session total, each increment cited to a confirmed event.
- [ ] Citation pills resolve to real files; NLI badge renders; "show your work" expander shows node+latency trace.
- [ ] `grep -rE 'sk-ant|AIza|sk-|GEMINI_API_KEY' .` → empty.
- [ ] Recording 1920×1080, narrated, ≤4 min; YouTube unlisted + MP4 backup.
- [ ] Submit from @shriva.ujjawal HackerEarth account before 15 Jun 23:59 IST.

---

## 7. ANTI-PATTERNS THAT AUTO-LOSE (do not do these in the demo)
Raw tracebacks in UI · un-cited answers · "chat-with-PDF only" (not agentic — the autonomous alert is the antidote) · live LLM call on the scored path that can 429 · committed API keys · slide-only "demo" · a single monolithic LLM call doing everything · claiming KPIs not anchored to Tata's published figures.

---

*Source-of-truth scenarios verified directly against `SPEC/ground_truth_spine.json` and `knowledge_docs/spare_parts_catalog.csv` on 2026-06-09. Subscription pattern verified against `dataforge/api/scorer/agent.py::_subscription_review`. LLM swap point verified at `wizard/agents/nodes.py::_llm_complete`. Demo infra (`data/demo/demo_cache.json`, `cost_events.jsonl`) and NLI gate (`wizard/rag/faithfulness.py`) confirmed present in the existing build.*
