# 01_tata_r2_judge_intel.md
## Tata Steel AI Hackathon 2026 — Round 2: Judge Intelligence Deep-Dive
**Hackathon-Intel-Researcher output | Generated: 2026-06-08**
**Sources: official_PS/OFFICIAL_PS.md · WEBINAR_NOTES_AND_JUDGING.md · MASTER_BRIEF.md · research/23_judging-optimization.md · research/24_differentiation-wow.md · web search**

---

## 0. EXECUTIVE THESIS

This is an industrial-AI hiring hackathon disguised as a technical competition. Judges are Tata Steel's own AI leadership team — people who operate 800+ deployed models, 8+ years of production industrial AI, and have personally signed off on the 1.4B USD AI savings program. They are not impressed by novel architectures. They are impressed by systems that feel deployable to their plant floor TODAY.

The actual selection function, synthesized across all sources:

> "Does this submission look like something we could hand to a Jamshedpur maintenance engineer on Monday morning — and trust that it would not hallucinate, not crash, and would surface the right alarm before the furnace trips?"

Every scoring decision flows from that sentence. Technical cleverness is table stakes. Domain credibility, demo stability, and honest business framing are the differentiators.

---

## 1. COMPETITION STRUCTURE (CONFIRMED FACTS)

| Field | Value | Source |
|---|---|---|
| Round | 2 of N (R1 = tabular ML scoring, R2 = agentic build) | OFFICIAL_PS.md |
| Window | Jun 5 2026 18:00 IST → Jun 15 2026 23:59 IST | OFFICIAL_PS.md |
| Mode | Individual (team size = 1) | HackerEarth page |
| Registrations | 109 as of Jun 6 2026 | HackerEarth page |
| Submissions | Multiple allowed; last = final | OFFICIAL_PS.md |
| IP | Participant retains | OFFICIAL_PS.md |
| DQ triggers | Copied ideas; code built before hackathon start | OFFICIAL_PS.md |
| Data provision | None confirmed; working assumption = generate synthetic | Discussion thread |
| Prize | ₹1L joining bonus + Pre-Placement Internship / offer for top performers | talentd.in |

---

## 2. VERBATIM PROBLEM STATEMENT (DO NOT PARAPHRASE)

From the official microsite (scraped 2026-06-06):

> "Develop an intelligent AI-powered maintenance decision-support system for industrial equipment in steel manufacturing environments. The solution should help maintenance engineers diagnose equipment issues, identify root causes, predict failures, assess risks, prioritize maintenance actions, and generate actionable recommendations using data from equipment logs, sensor alerts, manuals, SOPs, and historical maintenance records.
>
> The system should support natural language interactions, provide explainable insights, enable proactive maintenance planning, and continuously improve through feedback and historical learning. Teams are encouraged to leverage LLMs/SLMs, predictive analytics, anomaly detection, and knowledge retrieval techniques to build a practical and scalable solution for industrial operations."

From the full PS PDF (Section 2 — Objective):

> "Design & develop an intelligent Maintenance Wizard acting as a decision-support platform that enables: Faster, more accurate diagnosis of equipment issues · Identification of probable root causes of failures · Prediction of equipment degradation and remaining useful life · Proactive detection of abnormalities and catastrophic failure risks · Prioritization of maintenance actions (operational + procurement constraints) · Generation of structured maintenance insights and reports. Support BOTH reactive troubleshooting AND proactive maintenance planning."

---

## 3. THE 7 FUNCTIONAL REQUIREMENTS — JUDGE PERSPECTIVE (GREAT vs MEDIOCRE)

### FR1 — Contextual Reasoning using LLMs/SLMs

**What the PS says verbatim:** "Integrate LLM/SLM. Extra merit for creating/fine-tuning a domain-specific model. Public APIs allowed."

**What "great" looks like to a judge:**
- The LLM is not doing the work alone — it is the synthesis layer on top of structured ML outputs (RUL, anomaly score, WRPS risk score) and retrieved documents. The judge sees: sensor data → ML model → structured output → LLM narrative → citation-grounded answer.
- The LLM's role is clearly bounded: it explains, synthesizes, and narrates. It does not hallucinate equipment specs because those come from the RAG layer.
- Extra merit path: a QLoRA fine-tuned Qwen/Phi on synthetic steel-maintenance corpus that demonstrably outperforms base on a 50-ex held-out eval. Must show the eval numbers. Fine-tuning on synthetic data without a benchmark comparison is weaker than a well-prompted base model — judges who run 800 models know the difference.
- Multi-model routing: cheap/fast model for routing, strong model for diagnosis and plan generation. Demonstrates architectural maturity.

**What "mediocre" looks like:**
- Single monolithic GPT/Claude call: "Given this sensor data, tell me what is wrong." No ML layer, no RAG, no agent routing.
- Fine-tuning claimed but not evidenced (no eval numbers in the doc).
- LLM generating equipment specifications or SOP text from memory (hallucination risk visible to judges who know the actual steel plant SOPs).
- Ollama-only (offline) with no quality grounding — answers will be vague and the judge knows it.

**Key insight:** Judges care that the LLM is the *narrator*, not the *oracle*. The oracle is the knowledge base + the ML models. If the LLM is doing both, it will hallucinate and the judge will notice.

---

### FR2 — Knowledge Integration (RAG over manuals, SOPs, logs, failure reports)

**What the PS says verbatim:** "Reason over manuals, SOPs, historical records, failure reports + operational logs."

**What "great" looks like:**
- Hybrid retrieval: dense (semantic) + sparse (BM25/keyword) + SQL metadata filter. Not just cosine similarity over embeddings.
- Source diversity: at minimum 3 distinct document types indexed (SOPs, failure reports, manuals). Not a single document type.
- Per-chunk provenance: retrieved result carries document name, section header, page number. Not just "found in knowledge base."
- Reranking: FlashRank or similar cross-encoder reranker lifts relevant but low-similarity chunks. Demonstrates awareness of retrieval quality.
- Chunking strategy visible in the design doc: semantic chunking with overlapping context windows, not naive 512-token splits.
- Knowledge graph overlay (FMEA ontology): shows the system understands equipment failure causality, not just text retrieval. Even a hand-authored NetworkX graph with 50-100 nodes covering the demo equipment family is a massive differentiator.

**What "mediocre" looks like:**
- "Chat with PDF" — one PDF, one vector store, top-k retrieval, LLM answers. This was novel in 2023. In 2026 it is the baseline that every competitor will implement.
- No reranking — top-k cosine retrieval only.
- No provenance in output — "Based on documentation..." with no citation.
- Single document type (just the maintenance manual, no failure history, no SOPs).

**Key insight:** The PS explicitly lists 4 distinct input categories (operational/failure, condition monitoring, knowledge/documentation, user interaction). A submission that only handles one category (documentation) misses 75% of the stated input space.

---

### FR3 — Natural Language Interaction (multi-turn, context-aware)

**What the PS says verbatim:** "NL queries + multi-turn context-aware conversation."

**What "great" looks like:**
- Persistent session memory: the system remembers "we were discussing EAF-04" from turn 1 when the engineer asks "what's its bearing temperature trend?" in turn 5. No context re-paste required.
- Pronoun resolution and follow-up handling: "what about the pump?" after discussing a bearing is routed correctly.
- Context-aware re-ask after feedback: engineer corrects RUL → re-asks same question → answer reflects the correction. This is the intersection of FR3 and FR6 — a powerful demo moment.
- Graceful out-of-scope handling: if the engineer asks something outside the steel-maintenance domain, the system declines politely with a domain explanation.
- Session thread IDs with time-travel: judges can ask "show me what you knew at turn 3" and the agent can reconstruct that state (LangGraph SQLite checkpoint enables this).

**What "mediocre" looks like:**
- Stateless query-response: every turn is independent, engineer must re-state context.
- Multi-turn simulated by appending the full chat history to every prompt (works but is token-wasteful and observable in token counts).
- "How can I help you today?" generic chatbot UX with no maintenance-domain intent routing.

---

### FR4 — Explainable and Traceable Outputs

**What the PS says verbatim:** "Outputs traceable to input data / records / rules / docs."

**What "great" looks like (and this is the highest-weight criterion for judges who are AI engineers themselves):**
- Inline [N] citations in every answer: "The bearing failure pattern [1] matches SOP-BF-007 §3.2 which states [2]..." with expandable source cards showing the exact chunk.
- NLI faithfulness gate: before the answer reaches the engineer, each claim is scored for entailment against its cited source. Claims with entailment < 0.6 are flagged as LOW CONFIDENCE. Judges who understand RAG hallucination will specifically look for this.
- Structured `DiagnosisReport` / `MaintenanceState` TypedDict: every output is a Pydantic schema with explicit fields (equipment_id, fault_codes, diagnosis, rca, rul_estimate, risk_level, maintenance_plan, cited_sources, faithfulness_scores). Not a freeform text blob.
- Agent trace visibility: Arize Phoenix local UI (or equivalent) showing every LangGraph node fired, latency per node, prompt sent, retrieved docs, output received. Judges with AI leadership backgrounds will open this UI.
- Collapsible reasoning chain in the Streamlit UI: sensor reading → retrieved SOP → historical incident → agent step → final answer. Clean by default, full detail on expand.
- FMEA knowledge graph path: "BF Tuyere → Cooling Failure → Burnout → CRITICAL" rendered as a cause chain, cited to specific KB entry.

**What "mediocre" looks like:**
- "Based on my analysis, the equipment likely has a bearing issue." — no source, no trace, no citation.
- Showing the raw ReAct chain as a wall of text. This is not explainability; it is logging.
- Citing "maintenance manual" without section/page numbers.
- No audit trail — the system cannot explain a past decision when asked.

**Key insight:** Tata Steel's judges run production AI systems where engineers must justify every maintenance action in a safety log. A system that cannot show its work is undeployable to them. Explainability is not a nice-to-have; it is a deployment prerequisite. Treat FR4 as the #1 differentiator, not a checkbox.

---

### FR5 — Abnormality Detection and Failure Prediction

**What the PS says verbatim:** "Dynamic anomaly detection, early warning, failure prediction for critical equipment."

**What "great" looks like:**
- Layered hybrid detector, not a single model: Isolation Forest (fast point anomalies) + LSTM Autoencoder (temporal pattern degradation) + adaptive threshold (percentile-based, recalibrates from feedback).
- Per-sensor SHAP explainability: "Sensor T-12 (Temperature) is the primary anomaly driver (SHAP = 0.42), followed by V-08 (Vibration, SHAP = 0.31)." Judges who understand SHAP will immediately appreciate this.
- RUL with uncertainty quantification: WeibullAFT giving P50/P90 estimates, not a point estimate. "Bearing expected to fail in 11h (P50) to 18h (P90)" is more trustworthy and more industrial than "bearing will fail in 14.3 hours."
- Failure prediction separate from anomaly detection: 4-class ordinal failure predictor (no fault / tool wear / heat dissipation / power failure) is a different model from the anomaly detector — shows domain understanding of ISO 14224 failure taxonomy.
- Proactive firing without user input: the system detects the degradation pattern and fires the alert autonomously, BEFORE the engineer asks. This is the proof of "agentic" for FR5.
- Degradation index trend: showing the D-index trajectory from 0 (healthy) to 1 (failure) over the last N sensor ticks as a mini-chart.

**What "mediocre" looks like:**
- Simple threshold alert: temperature > 850°C → alert. Any junior engineer can write this.
- Single model (Isolation Forest only or LSTM AE only) with no explanation of what drove the anomaly.
- Point RUL estimate with no uncertainty: "14.3 hours remaining." Overconfident, not industrial.
- Anomaly detection that only works when the user submits data — no autonomous background polling.
- No fault taxonomy — every failure is just "anomaly detected."

---

### FR6 — Feedback-Driven Improvement

**What the PS says verbatim:** "Feedback loop (corrections/confirmations/outcomes) improves future recs."

**What "great" looks like:**
- Visible in the demo in one turn: thumbs-down → engineer types correction → re-ask → answer is corrected with `[ENGINEER CORRECTION]` badge. The judge watches behavior change in real time.
- Three-track architecture: (a) RAG correction — corrected text upserted to vector store, promoted to top-3 on next retrieval; (b) Bayesian RUL blend — `new_rul = 0.7 × model_rul + 0.3 × engineer_rul`; (c) preference JSONL — structured audit trail for future fine-tuning.
- Inference-time only (no retraining): judges who understand ML know that n=1 retraining is statistically invalid. A team that says "we retrain the model on each correction" does not understand the problem.
- Design document mentions DSPy BootstrapFewShot compatibility of the corrections.jsonl file — shows awareness of the production roadmap beyond the hackathon.
- Engineer feedback history tab in the dashboard: visible audit of what was corrected, when, and how it affected subsequent responses.

**What "mediocre" looks like:**
- FR6 unimplemented — thumbs up/down captured but behavior unchanged on the next query.
- "We log feedback for future retraining" — deferred improvement that cannot be demoed.
- Feedback only on the LLM answer, not on the ML prediction (misses the RUL correction use case).
- No visible behavior change in the demo — the correction is silent.

---

### FR7 — Real-Time Alerting Capability

**What the PS says verbatim:** "Real-time abnormal alert reports + user-specific notifications."

**What "great" looks like:**
- Proactive autonomous alert firing at ~90 seconds into the demo with ZERO user input. This is the single highest-impact demo moment and the clearest proof of "agentic" behavior per the PS definition.
- Alert carries a complete maintenance plan, not just a notification: severity + RUL estimate + RCA chain + recommended actions + spare parts availability. "CRITICAL: EAF-04 bearing failure predicted in 11h. Root cause: cooling water flow degradation [SOP-BF-007 §3.2]. Replacement bearing in stock at Jamshedpur. Recommended: schedule replacement now. Cost avoided: ₹3.75L."
- Alert deduplication and cooldown: the same alert does not fire 10 times in 5 minutes. Judges who have seen alert fatigue in production will immediately test this.
- Priority queue: CRITICAL alerts surface before HIGH before MEDIUM — queue ordering is visible in the dashboard.
- SSE streaming to the UI: alert appears as a `st.toast` notification and simultaneously updates the Alerts page without page reload. Real-time, not polling-visible.
- Tiered severity with multi-factor scoring (WRPS): criticality = f(RUL risk, anomaly severity, equipment criticality, spare availability). Not a single-threshold trigger.

**What "mediocre" looks like:**
- Alert only when the engineer asks "are there any alerts?" — reactive, not proactive. Violates the "agentic" criterion.
- Simple threshold trigger: T > 850 → email. No ML inference, no RCA, no action plan attached.
- Alert floods: same alert fires every 5 seconds. Alert fatigue is a well-known production AI failure mode.
- No deduplication or cooldown — demonstrates no awareness of operational realities.
- Alert page refreshes only on manual page reload.

---

## 4. THE 6 OFFICIAL JUDGING CRITERIA — WHAT EVIDENCE WINS

### Criterion A — Problem Understanding and Solution Approach
**What judges score:** Did the team actually understand why steel-plant maintenance is hard, or are they treating it as a generic "maintenance AI" problem?

**Winning evidence:**
- Opening the design document with Tata Steel's own published KPIs: 22% downtime reduction via Asset Sphere, ₹1.4B total AI savings, 40% maintenance-planning-time reduction at Jamshedpur, 50% unplanned downtime reduction at Kalinganagar via IoT + AI.
- Explicitly naming the fragmentation problem: engineers currently check manuals, SOPs, sensor dashboards, failure logs, and spare-parts systems separately. The wizard consolidates them.
- Naming the safety dimension: unplanned failures in a blast furnace environment involve molten metal at 1400°C+ — false negatives have safety consequences, not just cost consequences.
- Honest assumptions/limitations section written from Day 1: "We simulate sensor data using NASA C-MAPSS mapped to steel-plant equipment; real deployment would require integration with the plant's existing sensor infrastructure (OPC-UA/Modbus)." Judges respect honesty more than overclaiming.
- Naming both use modes: reactive troubleshooting (engineer reports a fault) AND proactive maintenance planning (system fires autonomous alert). The PS explicitly requires both.

**Losing move:** Generic "maintenance is important" framing. Saying "downtime costs money" without citing Tata Steel's own documented figures.

---

### Criterion B — Effective Use of Agentic AI Frameworks and Concepts
**What judges score:** Is this actually agentic — autonomous decision-making, multi-step reasoning, tool use — or is it a chatbot with a maintenance theme?

**Winning evidence:**
- LangGraph supervisor topology with named, typed agents (Diagnosis, RCA, RUL, Prioritization, Maintenance Plan, Alert). The graph is visible as a Mermaid diagram in the architecture doc AND live in the Arize Phoenix UI.
- The 90-second autonomous alert: no user input → system detects degradation → fires CRITICAL alert with full maintenance plan. This is agentic by definition: the system is setting its own objectives (monitor equipment health), making decisions (this is CRITICAL), and executing a plan (alert + recommendation + spare check).
- PEV reasoning pattern (Plan → Execute(ReAct) → Validate): shows awareness of structured agent reasoning, not just chain-of-thought.
- SQLite checkpoint: judges can observe mid-conversation state. "Show me what the system knew after the Diagnosis agent but before the RCA agent" — demonstrable via graph.get_state().
- Multi-agent handoff visible in the streaming output: "Routing to Diagnosis agent... → Routing to RCA agent... → Generating maintenance plan..." shown in real time in the UI.

**Losing move:** "We used LangChain for RAG chaining and call it agentic." The PS specifically says "intelligent agents capable of understanding objectives, making decisions, and adapting to dynamic environments." A static RAG pipeline is not this.

---

### Criterion C — Technical Implementation and Innovation
**What judges score:** Is this production-grade or prototype-grade? Is there anything here that required real engineering depth?

**Winning evidence:**
- FMEA knowledge graph (NetworkX, ISO 14224 grounded): a hand-authored graph covering the demo equipment families shows domain research depth that generic competitors cannot match. Traversal-based RCA (Layer 1) + DoWhy GCM causal attribution (Layer 2) + LLM 5-whys narrative (Layer 3) = a 3-layer RCA no one else will build.
- NLI faithfulness gate (cross-encoder/nli-deberta-v3-small): ~80ms CPU, catches hallucinated citations before they reach the engineer. This is 2026 RAG SOTA, not a common hackathon feature.
- WeibullAFT RUL with Bayesian correction: statistically sound, industrially motivated (survival analysis is the correct model for time-to-failure, not point regression). Degradation index adds a second-layer real-time estimate.
- LiteLLM gateway + Ollama fallback: demonstrates production thinking (what if the API is down during judge demo?).
- DeepEval golden set with regression gate: shows eval discipline. Judges who run 800 production models live by eval gates.
- Arize Phoenix local trace UI: shows the system is observable, not a black box.
- Fine-tuned domain SLM (Qwen2.5-3B QLoRA on synthetic corpus, if shipped): the PS grants extra merit for this. Even a small model trained on steel-maintenance synthetic data and evaluated against a 50-ex golden set is a meaningful differentiator — but only if the eval numbers are shown. Fine-tuning without benchmark comparison is weaker than strong prompting.

**Losing move:** Complexity theater — e.g., "we used GraphRAG and Docker Compose and a Kafka stream." Judges who have debugged industrial AI systems know that complexity = fragility. The winning signal is depth + reliability, not breadth.

---

### Criterion D — Scalability and Real-World Applicability
**What judges score:** Could this actually run in a Tata Steel plant? What would need to change?

**Winning evidence:**
- Explicit integration roadmap in the design doc: "Current version uses simulated sensor playback. Production integration path: OPC-UA adapter for SCADA data; Modbus adapter for PLC data; API bridge to SAP PM for spare-parts lookup." Shows the team understands the real integration surface without overclaiming current capability.
- Architecture choices that don't require infrastructure: pip install only (no Docker), CPU-only (no GPU required at the plant edge), SQLite (no Postgres/Redis administration). These choices are explicitly scalable to a judge's laptop AND defensible as a production starting point with stated upgrade paths.
- Modular design: new equipment families can be added by (a) adding FMEA graph nodes, (b) adding synthetic KB documents, (c) retraining on new sensor profiles. The system is not hardcoded to EAF-04.
- Spare-parts and procurement lead-time integration: explicitly named in the PS as a prioritization input. Any submission that shows "Bearing in stock: YES — Lead time if not: 14 days — Recommended: order backup NOW" demonstrates real-world operational awareness.
- Multi-equipment-family design: blast-furnace fans, centrifugal pumps, roller bearings, hydraulic units, hot-strip-mill conveyors — naming these specifically (vs. "industrial equipment generally") signals steel-plant domain knowledge.

**Losing move:** "This is a prototype; scalability would require future work." — vague deferral. The correct answer names the specific production integration path.

---

### Criterion E — Quality of Presentation and Communication
**What judges score:** Can a non-technical Tata Steel business leader understand what this does in 30 seconds? Can a technical judge reconstruct the full system from the documents without the narrator?

**Winning evidence:**
- Screen recording: 3-4 minutes, narrated (voiceover or captions), 1920×1080. Opens with the problem framing anchored to Tata Steel's own numbers (first 20 seconds). First wow moment (proactive CRITICAL alert) within 90 seconds. Each section labeled with the feature it demonstrates.
- Design document written from Day 1 (not Day 8): covers all 8 required sections with domain context, not just implementation details. Architecture diagram is auto-generated from the actual LangGraph graph (not hand-drawn), so it is accurate.
- Architecture doc is self-sufficient: a judge who does not watch the video can reconstruct the full system — problem → architecture → data flow → model design → alerting logic → assumptions → install → sample I/O.
- Business Impact section with Tata Steel's own published numbers: not generic "maintenance AI saves money" — specific "Tata Steel's own deployment achieved 15% reduction in unplanned downtime on rolling mills; our Wizard targets similar impact at ₹X Crore/year per plant."
- README.md with a 5-command install sequence that actually works on a clean Python 3.10/3.11/3.12 environment.

**Losing move:** Screen recording with no narration (mouse clicking silently). Design doc written as a technical README without business context. Architecture diagram that is hand-drawn and does not match the actual system.

---

### Criterion F — Business Impact and Feasibility
**What judges score:** Is this framed as a cost-avoidance and productivity platform, or as an AI research project?

**Winning evidence:**
- Live Cost-Avoidance Ticker in the Streamlit sidebar: accumulates `avoided_hours × ₹75,000/hr` per confirmed CRITICAL/HIGH event during the demo. At demo end: "Total prevented downtime cost this session: ₹11.25L." The judge sees the number grow live — this is not a slide projection.
- Steel-plant-specific downtime costs cited and sourced: blast furnace blower trip = ₹500K/day (Cypag analysis); continuous caster breakout = ₹2M equipment damage (OxMaint); industry average = ₹50,000–₹150,000/hr.
- Tata Steel's own documented AI savings used as the benchmark: ₹40 Crore/year savings from IoT + AI at one plant; 50% unplanned downtime reduction at Kalinganagar.
- MTTR improvement framing: "Current MTTR 4.2 hours → target 1.8 hours with pre-staged parts and advance notice" (OxMaint benchmark). Reduce MTTR = reduce production loss.
- Procurement/spares angle: "CRITICAL bearing failure in 11h. Replacement bearing NOT IN STOCK. Lead time: 14 days. Order immediately via procurement route X." This specific narrative is in the PS and nearly no competitor will model it.
- ROI formula in the design doc: `14 unplanned events/year × avg. 4.2h MTTR × ₹75,000/hr × 0.45 avoidance rate = ₹19.8 Crore/year` — calculated from published benchmarks, not invented.

**Losing move:** "Predictive maintenance reduces downtime by 30%" on a static slide. Percentages without rupees, without Tata Steel's own numbers, without a session-scoped live accumulator.

---

## 5. THE 7 OPERATIONAL QUALITIES (WEBINAR-ONLY, OBSERVED AS FACTS NOT CLAIMS)

These are scored during demo review as observed behavior, not document claims. A system that crashes loses all 7 simultaneously.

| Quality | What earns it | What kills it |
|---|---|---|
| **Fast** | First token streams within 1-2s. `st.write_stream` starts before full response arrives. Cached gold responses for demo path (<1s). Agent trace shows per-node latency. | Blank screen + spinner for 8+ seconds on first query. Full response batch-rendered after full generation. |
| **Efficient** | Small model routing for cheap tasks (Gemini Flash for intent, Sonnet for diagnosis). Token counts visible in Phoenix. No over-calling the LLM on deterministic ML outputs. | Every query calls GPT-4 class model for all sub-tasks including routing. 4000-token prompts for simple classification tasks. |
| **Accurate** | NLI gate catches citation drift. Golden set eval report in the design doc (e.g., "RAG faithfulness: 0.89, answer relevancy: 0.92 on 50-ex golden set"). Confidence badges on LOW-confidence outputs. | LLM answers unchecked against source. No eval suite, no accuracy metric in the design doc. |
| **Easy to use** | Non-technical engineer can drive the demo without knowing what a SHAP value is. "Simulate Fault" button. Pre-seeded EAF-04 scenario. Color-coded severity (CRITICAL=red/HIGH=orange). One-click "Confirm" / "Override" on alerts. | UI requires understanding of anomaly detection internals. SHAP waterfall charts, cosine similarity scores, or embedding distances shown to the maintenance engineer. |
| **Doesn't break** | Circuit breaker pattern (pybreaker): LLM failure → cached gold response, not traceback. Cold-start test on clean venv confirmed working. 10x crash test run before recording. Ollama fallback when Gemini quota exhausted. | Raw Python traceback visible in the Streamlit UI during the screen recording. |
| **No errors** | Global FastAPI exception handler: every error returns `AgentResult(status='error', message='human-readable message')`. All Pydantic schemas validate on input. Input sanitization (SQL injection on equipment_id). | `AttributeError`, `KeyError`, `ValidationError` visible in the UI or logs. |
| **Smooth** | Demo follows a scripted HAPPY_PATH.md. Pre-seeded database with EAF-04 scenario data. `demo_cache.json` pre-computed gold responses for the scripted path. Sensor playback deterministic. Streamlit pages load without flicker. | Improvised demo that depends on LLM API availability and random sensor data. Any pause where the judge is watching a spinner for more than 3 seconds. |

---

## 6. WHAT TATA STEEL ACTUALLY CARES ABOUT IN MAINTENANCE

### 6.1 Downtime Economics (Confirmed Figures)

| Metric | Value | Source |
|---|---|---|
| Unplanned downtime cost (blast furnace blower trip) | $500,000+/day (~₹4.2 Cr/day) | Cypag industry analysis |
| Continuous caster breakout equipment damage | $2,000,000 per event | OxMaint ROI analysis |
| Industry average unplanned downtime cost | $50,000–$150,000/hr | AssetWatch (2025) |
| Tata Steel Kalinganagar AI deployment result | 50% reduction in unplanned downtime, ₹40 Cr/year savings | ifactoryapp.com |
| Tata Steel Jamshedpur prescriptive system | 40% reduction in maintenance planning time, 92% on-time execution rate | oxmaint.com |
| Tata Steel total AI program savings | $1.4B | AIExpert Network case study |
| Steel industry total unplanned downtime cost (2024) | $4.2B globally | OxMaint / AssetWatch |
| US DOE documented maintenance ROI | 10:1 average | oxmaint.com |
| Optimal predictive maintenance ROI vs reactive | 25–30% reduction in breakdowns, 70–75% elimination of failures | Industry benchmark |

### 6.2 Tata Steel's AI Maturity Level (Why This Matters for Judging)

- 800+ AI models and agents deployed (8+ years of industrial AI)
- Bimodal AI strategy: Narrow AI (metallurgy, defect analysis, PdM) + Agentic AI (decision support, conversational interfaces)
- 3 plants recognized as WEF Advanced 4IR Global Lighthouses (Jamshedpur, Kalinganagar, IJmuiden)
- 260+ AI algorithms running simultaneously at Kalinganagar plant
- Next chapter: "moving from intelligence to decision autonomy" — this is the mandate judges are operating under

**Implication:** Judges are not impressed by RAG or LangChain. They have deployed both. They are impressed by systems that show judgment — knowing when not to act, surfacing uncertainty honestly, integrating procurement constraints, understanding that a false CRITICAL alert in a steel plant causes actual operational disruption. They will score a system that says "MEDIUM confidence — recommend visual inspection before scheduling downtime" higher than one that always says "CRITICAL" confidently.

### 6.3 Steel-Plant Maintenance Realities (Domain Signal)

These are facts that separate a submission that read the PS from one that researched the domain:

1. **OEE is the master metric.** Overall Equipment Effectiveness = Availability × Performance × Quality. Judges think in OEE. A system that calculates and displays OEE impact of the maintenance decision is speaking their language.

2. **Integrated plants = cascading failures.** A blast furnace tuyere failure does not just affect the BF — it affects the hot metal supply to the BOF, which affects the continuous caster, which affects hot strip rolling. Maintenance prioritization must account for this cascade. The WRPS prioritization formula's "process criticality" weight is this.

3. **Shift handover is a known information black hole.** Maintenance records not captured before shift change are lost. The "automatic digital logbook" optional feature in the PS addresses this directly. Any submission that names this problem explicitly will resonate with plant-floor judges.

4. **Spare-parts lead times in India's steel supply chain are 2–14+ days for critical components.** A bearing that can be ordered from the Jamshedpur warehouse in 2 hours vs. one that needs 14 days from Germany requires a completely different maintenance response. The PS explicitly names spares + lead time as a prioritization factor. Most competitors will not model this.

5. **Safety certification matters more than accuracy.** A maintenance recommendation that causes a furnace trip or a safety incident is worse than no recommendation. Judges will look for: uncertainty quantification (P50/P90 RUL, not a point estimate), explicit confidence scores, the ability for engineers to override, and a "LOW CONFIDENCE — recommend manual inspection" fallback. Systems that always act confidently are not deployable to a safety-critical environment.

6. **ISA-95 / ISO 14224 vocabulary.** Using correct industrial terminology — RUL, MTTF, MTBF, MTTR, FMEA, criticality class, corrective/preventive/predictive maintenance, OEE — signals domain competence. Using generic terms ("machine health", "AI-powered monitoring") signals surface-level engagement.

---

## 7. JUDGING PANEL INTELLIGENCE

### 7.1 Confirmed and Inferred Judges [unverified: formal roles, not all names confirmed]

**Sarajit Jha** (confirmed LinkedIn involvement in promoting the hackathon):
- Tata Steel AI leadership team (exact title [unverified])
- Published post framing hackathon as targeting "tough residual problems that over 850 AI/ML models could not solve"
- Signal: He cares about problems that existing AI has not cracked. A submission that is just "better RAG" will not impress him. He wants to see autonomous decision-making that handles the residual complexity.
- LinkedIn: linkedin.com/in/sarajitjha

**Judging panel composition (inferred from "Tata Steel AI leadership team" description):**
- Mix of technical AI engineers (who built the 800 models) and business stakeholders (who measure downtime cost). [unverified]
- The 6 official criteria map to this split: criteria A/B/C are technical (AI engineers judge them), criteria D/E/F are strategic (business stakeholders judge them). [unverified — no formal weight distribution published]
- Given the WEF 4IR Lighthouse recognition, there may be external industry judges familiar with industrial AI best practices. [unverified]

### 7.2 Known Biases From Webinar Intelligence

From the direct webinar attendance (June 4, 2026):
- Judges specifically named the 7 operational qualities (fast/efficient/accurate/easy/robust/error-free/smooth) — these are scored from watching the demo, not from reading the document.
- The webinar tone was: "show us something we can deploy, not something we can be impressed by."
- Latency was mentioned first in the quality list — this is a signal that demo lag is a visible negative.

---

## 8. PAST WINNER PATTERNS (ANALOGOUS HACKATHONS — NO DIRECT TATA R2 HISTORICAL DATA)

No Round 2 historical data exists (this is the second running of the hackathon in its current agentic format). Inferences from analogous industrial AI hackathons:

### GitLab AI Hackathon 2026 — Winner: LORE
- "This feels like a product, not a hackathon project" — judge April Guo
- Won with: 43 automated tests, production-grade engineering, working system in the judge's hands.
- Lesson: Test discipline and production quality differentiate from prototype flair.

### Great Agent Hack 2025 — Winner: Zarks.AI (Track B)
- Won by building "a real-time observability framework that captures full execution traces and human-interpretable reasoning chains"
- Not the most technically complex entry, but the one that made its reasoning visible.
- Lesson: Trace visibility in agentic AI is a winning feature, not a debug tool.

### Microsoft AI Agents Hackathon 2025
- "The most technically impressive solution lost to the one with the most intuitive interface."
- Rubric explicitly required "actual demo (not Figma or presentation)."
- Lesson: Demo stability and UX beat technical complexity.

### Kong Agentic AI Hackathon 2025
- "Every winning entry had a working demo. Real code. Real impact."
- Submissions without a runnable demo were not considered.
- Lesson: Runnable > elegant.

**Synthesized pattern across 4 analogous winners:**
1. Working demo, runnable by the judge, on the judge's machine.
2. Visible reasoning chains (not opaque outputs).
3. Production-quality engineering signals (tests, error handling, typed schemas).
4. Intuitive interface — non-technical judges can drive the demo.
5. Problem framing before technical architecture.

---

## 9. COMMON FAILURE MODES — WHY MAINTENANCE/PDM PROJECTS FAIL TO IMPRESS

Based on research/23_judging-optimization.md anti-patterns + domain analysis:

### Failure Mode 1: "Chat with PDF" Masquerading as Agentic AI
The system is RAG over a maintenance manual with a chat interface. Zero ML, zero autonomous action, zero proactive alerting. This satisfies FR1 (partly), FR2 (partly), FR3 — and fails FR4, FR5, FR6, FR7. Judges who see the demo will recognize it in 30 seconds.

### Failure Mode 2: Generic Industrial Framing
Opening with "industrial equipment maintenance is critical for operational efficiency" rather than "Tata Steel operates 35 million TPA across 4 countries; their own AI team documented 22% downtime reduction through predictive maintenance." Judges are Tata Steel employees. They know their numbers. Generic framing signals shallow research.

### Failure Mode 3: Threshold-Only Anomaly Detection
T > 850°C → fire CRITICAL alert. This is what they already have in their SCADA system. The innovation judges are looking for is multi-sensor fusion, temporal pattern detection (the failure that ramps gradually over 48 hours, not the one that spikes), and integration with the knowledge base (the alert includes the RCA and the maintenance plan, not just the sensor reading).

### Failure Mode 4: Confident LLM Hallucination
The LLM generates a plausible-sounding SOP procedure that does not exist in the knowledge base. Judges who work in a plant where engineers follow AI recommendations know that a hallucinated procedure can cause a safety incident. Any output not traceable to a source document is a red flag, not a feature.

### Failure Mode 5: Demo Crash or Traceback Visible
A Python AttributeError during the screen recording kills all 7 operational quality axes simultaneously. Teams that record under time pressure, without rehearsal, without a cold-start test on a clean environment, routinely ship recordings with errors. This is the most common failure mode by frequency.

### Failure Mode 6: Missing the Spare-Parts Angle
The PS names it explicitly: "prioritize on {process criticality, delay severity, spares availability, procurement lead time}." Competitors who do not read the PS carefully will implement anomaly detection and skip the procurement constraint. Surfacing "CRITICAL bearing — NOT IN STOCK — lead time 14 days — ORDER NOW" is a free differentiator that most competitors will miss.

### Failure Mode 7: Overclaiming the Fine-Tune
"We fine-tuned a domain-specific model on steel-plant data." If the fine-tuning is on synthetic data with no benchmark comparison, this claim weakens the submission — it signals the team does not understand what fine-tuning validates. The correct claim: "We fine-tuned Qwen2.5-3B on a 500-document synthetic steel-maintenance corpus. On a 50-example held-out eval, the fine-tuned model outperforms the base on maintenance-specific Q&A (73.8% vs 61.2% accuracy)." Numbers or silence.

### Failure Mode 8: Architecture Document as an Afterthought
Design doc written on Day 8 reads like a technical README: implementation details, no business story, no design rationale, no assumptions, no integration roadmap. Judges reading 109 submissions will process the document in 3–5 minutes. A document without a business framing, written without the context of the full 9-day build journey, will not carry the problem understanding axis.

### Failure Mode 9: No Feedback Loop Visible in Demo
FR6 is a functional requirement. If the screen recording does not show: (a) engineer provides correction, (b) system applies correction, (c) re-query returns corrected answer — FR6 is unmet. Many teams will log feedback and call it done. The demo must show behavior change.

### Failure Mode 10: Designing for AI Researchers, Not Maintenance Engineers
SHAP waterfall charts in the main UI. Cosine similarity scores. Embedding distance visualizations. Loss curves. These are invisible to the maintenance shift supervisor who will actually use the system. The technical detail belongs in collapsible expanders. The main UI should show: equipment name, severity (color-coded), recommended action, time-to-failure, one-click confirm/override.

---

## 10. WHAT MAKES A JUDGE SAY "THIS TEAM UNDERSTANDS STEEL-PLANT MAINTENANCE"

A synthesized list of statements/features that signal genuine domain comprehension vs. surface-level PS reading:

1. **Uses OEE vocabulary:** "This bearing failure would reduce OEE from 87% to 71% during the 4.2h MTTR window."
2. **Names specific equipment families and their failure modes:** blast furnace blower (tuyere cooling failure → burnout), centrifugal pump (seal degradation → cavitation), hot-strip-mill conveyor (roller bearing spall), hydraulic power unit (contamination-driven valve failure).
3. **Models cascade failure risk:** "BF-01 tuyere alert — if not addressed, expect cascade to BOF hot metal shortage within 6 hours."
4. **Procurement-aware recommendations:** spare part lead time explicitly displayed; "out of stock" scenario triggers "order immediately" recommendation, not just "schedule repair."
5. **Uses ISA-95 / ISO 14224 taxonomy:** FMEA, failure mode, failure cause, failure effect, criticality class. Not "equipment health" — "remaining useful life in operating hours."
6. **Acknowledges the simulated-data gap honestly:** "This demo uses NASA C-MAPSS data mapped to steel-plant equipment families. Real deployment requires OPC-UA integration with plant SCADA. We have designed the data interface to be adapter-swappable."
7. **Shift-handover angle:** automatic digital logbook that captures every alert, diagnosis, action, and outcome in a timestamped log that persists across shift changes. Names this as solving a known pain point.
8. **Safety language:** "We recommend MEDIUM confidence alerts trigger visual inspection before scheduling downtime, not autonomous action." Understands that false CRITICAL alerts in a safety-critical environment have operational consequences.
9. **Cites Tata Steel's actual plants:** Jamshedpur, Kalinganagar, IJmuiden — not "steel plant X."
10. **Business framing in rupees, not percentages:** every percentage metric translated to ₹/year at a specific plant scale.

---

## 11. SCORING RUBRIC (INFERRED — NOT PUBLISHED) [unverified]

No numerical weights are published for the 6 official criteria or 7 webinar qualities. The following is inferred from the hackathon structure and analogous industrial AI competitions.

| Criterion | Inferred Weight | Primary Evidence Mechanism |
|---|---|---|
| Problem Understanding (A) | ~15% | Design document opening + business framing in demo |
| Agentic Framework Use (B) | ~20% | Proactive alert + multi-agent routing visible in demo |
| Technical Implementation (C) | ~20% | Code quality + eval report + Phoenix trace + depth |
| Scalability (D) | ~15% | Integration roadmap + modular design + honest limitations |
| Presentation (E) | ~15% | Screen recording quality + narration + doc completeness |
| Business Impact (F) | ~15% | Cost ticker + Tata Steel KPIs + ROI formula |
| Operational qualities (7) | Multiplier | Crash/error during demo = multiplier drop across all 6 axes |

[unverified: weights inferred from criterion ordering, webinar tone, and analogous hackathon rubrics. Actual weights may differ significantly.]

The operational qualities function as a multiplier, not additive points: a system that crashes during the demo loses on Agentic Framework Use (B), Technical Implementation (C), Scalability (D), and Presentation (E) simultaneously — because a crashed demo is evidence against claims in all four.

---

## 12. DATASET INTELLIGENCE

### 12.1 No Official Dataset Provided [CONFIRMED]

The discussion thread on HackerEarth (as of June 8, 2026) shows a participant asking about datasets — no official answer from Tata Steel yet. The working assumption confirmed by the build playbook: **generate realistic synthetic data**.

### 12.2 Public Datasets In-Scope

| Dataset | Use | Domain bridge |
|---|---|---|
| NASA C-MAPSS FD001+FD003 | RUL ground truth + anomaly labels | engine→equipment, cycle→operating_hours, sensors→temp/pressure/vibration |
| AI4I 2020 (UCI, CC BY 4.0) | Fault classification (4-class) | TWF/HDF/PWF/OSF → steel fault taxonomy |
| Synthetic KB (500 docs) | RAG knowledge base | Jinja2 + Instructor on ISO 14224 ontology; 5 equipment families |

### 12.3 Key Data Framing Decision

Using real public datasets (NASA C-MAPSS) and being transparent about the domain bridge (engine → steel-plant equipment via column aliasing) is STRONGER than claiming proprietary steel plant data that does not exist. Judges know no synthetic dataset perfectly models Jamshedpur blast furnace sensor dynamics. Honesty about this + a clean integration roadmap showing how real plant data would slot in = the correct approach.

---

## 13. SUBMISSION CHECKLIST (WHAT JUDGES WILL OPEN)

1. `README.md` — First thing opened. 5-command install, YouTube link, requirements table. Must work.
2. `docs/ARCHITECTURE.md` — Second artifact judged. 8 sections. Business framing at top.
3. `docs/BUSINESS_IMPACT.md` — Tata Steel KPIs anchored. ROI formula.
4. Screen recording — YouTube unlisted (no friction). 3-4 min, narrated. Proactive alert at ~90s.
5. `src/` runnable code — `pip install -e . && make run` must succeed on a clean Python 3.10+ env.
6. `docs/SAMPLE_IO.md` — 3 query→response pairs with citation JSON.
7. No secrets in ZIP — mandatory `grep -rE 'sk-ant|AIza|sk-'` before submission.

---

## 14. OPEN QUESTIONS

1. **Official judge names and roles** — not published on HackerEarth. Sarajit Jha is confirmed involved; other panel members [unverified].
2. **Numerical scoring weights** — the 6 criteria and 7 operational qualities have no published weights. Treat equally until confirmed.
3. **"Extra merit for fine-tuning"** — unknown whether this creates a meaningful scoring gap or is a minor bonus. [unverified]
4. **Whether judges will run the code** — with 109 submissions, review time is limited. Some judges may evaluate video + document only. Design doc and screen recording must be self-sufficient.
5. **Official dataset availability** — Tata Steel discussion thread has not been answered. Watch for answer before June 10.
6. **Final round structure** — what advances from R2? PPIs / ₹1L bonus for top 3? No Round 3 structure published.
7. **Judging timeline** — results expected when? Not published.

---

## 15. DATAFORGE RELEVANCE — HOW TO MAKE THE DATASET QUALITY PLATFORM DOMAIN-RELEVANT

The existing DataForge platform (round_2/dataforge/) audits datasets for ML readiness. Its relevance to the Maintenance Wizard submission:

**Current DataForge dimensions:** completeness, duplicates, distribution sanity, feature redundancy, temporal coverage, schema validity, outliers, label quality, class balance, leakage.

**How to make it domain-relevant for the Maintenance Wizard narrative:**

1. **Run DataForge on the AI4I 2020 and C-MAPSS datasets** before using them. Show the audit results in the design document. "We validated our training data with a ML readiness audit: temporal coverage 97%, class balance 0.82 (imbalanced — mitigated with isotonic calibration), label quality 0.94." This demonstrates ML discipline that generic competitors skip.

2. **Demo integration angle:** Add a "Data Quality" tab to the Streamlit dashboard that shows live DataForge-style metrics on the ingested sensor stream — schema validity, outlier rate, missing values rate. When the alert fires, the judge can see that the anomaly detection is running on validated, audited data — not garbage.

3. **Business framing:** "The Maintenance Wizard includes a data quality gate: sensor readings with >15% missing values or schema violations are flagged before entering the prediction pipeline, preventing garbage-in-garbage-out failures." This is a production concern that Tata Steel's engineers will recognize as realistic.

4. **WRPS (Weighted Risk Priority Score):** DataForge's scoring framework is structurally analogous to WRPS. Both compute a composite score from multiple weighted dimensions. The DataForge UI could be the frontend for showing data quality as a dimension in the maintenance risk score — "equipment with poor-quality sensor data gets a data-quality risk penalty in the WRPS."

---

## Sources

- Official PS: https://www.hackerearth.com/community/challenges/hackathon/ai-hackathon-round-2-agentic-ai-challenge/
- Tata Steel LinkedIn (Sarajit Jha): https://www.linkedin.com/posts/sarajitjha_tatasteel-ai-agentic-activity-7462753188836941824-drSi
- Tata Steel AI transformation case study: https://aiexpert.network/case-study-tata-steels-ai-transformation/
- iFactory case study (Tata Steel digital twin savings): https://ifactoryapp.com/industries/manufacturing-plant/steel-plant-maintenance-predictive-ai-monitoring
- OxMaint predictive maintenance trends 2026: https://oxmaint.com/industries/steel-plant/predictive-maintenance-trends-steel-industry-2026-ai-iiot
- AssetOpsBench (industrial asset maintenance AI benchmark): https://arxiv.org/pdf/2506.03828
- Condition Insight Agent (arxiv 2603.08171): https://arxiv.org/pdf/2603.08171
- Cypag blast furnace downtime cost: https://cypag.com/en/thats-about-what-every-hour-a-blast-furnaces-downtime-may-cost-to-a-company/
- OxMaint ROI steel plant: https://oxmaint.com/industries/steel-plant/ai-predictive-maintenance-steel-plants-implementation-roadmap
- AssetWatch steel mill AI: https://www.assetwatch.com/blog/steel-and-metal-ai-predictive-maintenance
- Local sources: round_2/official_PS/OFFICIAL_PS.md · round_2/WEBINAR_NOTES_AND_JUDGING.md · round_2/MASTER_BRIEF.md · round_2/BUILD_PROCESS_PLAYBOOK.md · round_2/research/23_judging-optimization.md · round_2/research/24_differentiation-wow.md · round_2/research/01_agentic-orchestration.md · round_2/research/06_explainability-traceability.md · round_2/research/20_feedback-improvement-loop.md · round_2/research/22_realtime-alerting.md · round_2/research/09_anomaly-detection.md
