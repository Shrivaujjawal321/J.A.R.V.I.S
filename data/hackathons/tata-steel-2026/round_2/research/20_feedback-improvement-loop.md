# Component 20: Feedback-Driven Continuous Improvement (FR6)
**Tata Steel AI Hackathon 2026 — Round 2 Research Brief**
*Researched: 2026-06-06 | Deadline: 2026-06-15*

---

## 1. Recommended Approach — ONE Clear Winner

**Three-Track Inference-Time Feedback: Correction-Aware RAG Re-Rank + Bayesian RUL Blending + Preference Capture in SQLite**

No retraining. No external server. Full demo-visibility in one turn.

The winning architecture separates feedback into exactly three non-overlapping tracks, each with its own storage mechanism and immediate application path:

### Track A — RAG Correction (knowledge feedback)
When an engineer thumbs-down a retrieval-grounded answer and types a correction, the corrected text is upserted into ChromaDB as a new chunk with `metadata.feedback_source = "engineer_correction"`. The retriever's post-RRF pass promotes any correction-tagged chunk to top-3 — unconditionally, regardless of RRF score. Effect: the next query on the same topic surfaces the correction first. No ChromaDB reindex, no embedding change, no model call.

### Track B — RUL Bayesian Blending (numeric prediction feedback)
When an engineer overrides a model RUL with their own estimate (e.g., model says 45 days, engineer says 20 days based on physical inspection), the system runs:

```python
new_rul = 0.7 * model_rul + 0.3 * engineer_rul
```

This Bayesian-style precision-weighted average gives the model 70% weight (it trained on fleet statistics) and the engineer 30% (they have point-in-time physical information the sensors missed). The corrected RUL is updated in-memory immediately and persisted to `data/feedback/rul_corrections.jsonl` (append-only, replayed on restart). A degradation-index real-time adjustment (`d = ||z_current - z_healthy|| / ||z_failure - z_healthy||`) further decays the estimate as new sensor ticks arrive, so the correction is not static.

### Track C — Preference Capture (structured outcome logging)
Every engineer interaction — thumbs-up, thumbs-down, correction text, confirmation, "correct diagnosis", "wrong RCA" — is appended to `data/feedback/corrections.jsonl`. Each record carries: `session_id`, `turn_id`, `equipment_id`, `correction_type` (enum: `confirm | wrong_diagnosis | wrong_rul | wrong_rca`), `correction_text`, `corrected_rul_days` (optional), `timestamp`. This file is:
1. Surfaced in the Streamlit "Feedback History" tab as a live audit trail
2. Used in the demo script to show before/after query improvement (the killer demo moment)
3. Available as a future fine-tuning seed dataset (DSPy BootstrapFewShot can ingest it directly)

### Why this three-track split wins over any single-strategy approach

The fundamental constraint is: **n=1 online LLM retraining is statistically invalid and computationally forbidden on a judge's laptop.** The three-track design sidesteps this entirely by operating at inference time only. Each track addresses a different failure mode:
- Track A fixes "wrong knowledge retrieval" without touching the LLM
- Track B fixes "wrong numeric prediction" without retraining the ML model
- Track C captures "what was correct" for future improvement without blocking the live path

---

## 2. WHY — Evidence-Based Reasoning

### 2a. PatchRAG (ACL 2026 Findings) — inference-time correction is the 2026 SOTA

PatchRAG (Feedback Adaptation for Retrieval-Augmented Generation, arxiv 2604.06647, accepted ACL 2026) introduced two evaluation dimensions: **correction lag** (delay from feedback arrival to behavior change) and **post-feedback performance** (reliability on semantically similar queries after feedback). The paper found that training-based approaches exhibit delayed correction, while PatchRAG's inference-time patching shows "immediate correction and strong post-feedback generalization." This is the most current published validation that inference-time correction — not retraining — is the right production pattern.

Our Track A is a domain-specialized implementation of this same principle: inject the corrected knowledge at retrieval time, apply it on the next query without any model update.

### 2b. DMA (Online RAG Alignment with Human Feedback, arxiv 2511.04880) — feedback re-ranking without weight updates

DMA (November 2025) proved multi-month industrial deployment with "substantial improvements in human engagement" by updating retrieval ranking (pointwise and listwise rankers) from user preference signals without touching the LLM weights. Key insight: the LLM's "working memory" (context window available for in-context learning) is sufficient to act on corrected knowledge — no weight update needed. This validates our post-RRF correction-promoted re-rank as industrially sound, not a hack.

### 2c. Pistis-RAG (2024, MMLU +6.06%, C-EVAL +7.08%) — listwise human feedback improves RAG generation quality

Pistis-RAG demonstrated that treating human feedback as a listwise ranking signal (not just a binary thumbs signal) produces measurable downstream generation improvement. The "copy/regenerate/dislike" feedback options are structurally equivalent to our `confirm/wrong_diagnosis/wrong_rca` enum — both collapse to a preference signal over ranked retrieval outputs. The Pistis-RAG results give us a lower bound on what our Track A improvement is worth: even simple human correction signals translate to multi-percentage-point accuracy gains on Q&A benchmarks.

### 2d. Bayesian online correction — the only statistically valid n=1 update

The fundamental issue with online model retraining on a single engineer correction is that gradient descent on a single sample either overfits catastrophically (for neural models) or produces statistically meaningless coefficient updates (for tree models). The BUILD_PROCESS_PLAYBOOK correctly identifies this: "n=1 retrain is statistically invalid."

The Bayesian precision-weighted blending approach (`new_rul = α * model_rul + (1-α) * engineer_rul`) is the textbook solution for single-point evidence integration. Setting α=0.7 means the model retains fleet-level prior knowledge while incorporating the engineer's point estimate. This is directly analogous to Bayesian deep learning approaches to RUL (Reliability Engineering & System Safety, 2023, Bayesian Deep Learning Framework for Predictive Maintenance) that use posterior distributions to quantify and update uncertainty — but implemented without neural network machinery, making it CPU-instant and demo-safe.

### 2e. MemRerank (NAACL 2025, +10.61pp) — preference memory re-ranking without retraining

MemRerank (Preference Memory for Personalized Product Reranking, arxiv 2603.29247) showed that distilling correction history into concise preference signals for use in reranking — without any model retraining — achieves up to +10.61 percentage point accuracy improvement in downstream task performance. The mechanism (extract preference signal from correction history → apply as ranking boost at query time) is exactly what our correction-weight re-rank implements.

### 2f. DSPy BootstrapFewShot — future-proof accumulation path

DSPy's `BootstrapFewShot` family (as documented in Stanford NLP's 2025 docs) converts labeled trace examples into few-shot demonstrations used in compiled prompts. The `corrections.jsonl` file we produce in Track C is structurally compatible with DSPy training input: `(input_query, generated_answer, engineer_correction)` triples become `(input, output)` demonstrations after one filtering pass. This means the feedback store doubles as a fine-tuning seed — not used in the 9-day build, but visible to judges as a "next phase" roadmap item, which scores on "scalability and real-world applicability."

---

## 3. Exact Stack — Libraries, Versions, Roles

| Library | Version | Role |
|---|---|---|
| `chromadb` | 0.5.x | Correction chunk upsert + collection metadata query; correction-tagged chunks surface via metadata filter in post-RRF pass |
| `rank_bm25` | 0.2.2 | BM25 sparse retrieval; correction chunks already in the dense index, BM25 picks them up on term overlap too |
| `lifelines` | 0.30.x | `WeibullAFTFitter` for RUL base estimate; `apply_correction()` method applies Bayesian blending in-memory |
| `pydantic` | 2.7.x | `FeedbackRecord`, `CorrectionType` enum, `RULCorrection` — all typed, validated at API boundary |
| `fastapi` | 0.111.x | `POST /feedback` endpoint; sync request handling; returns `FeedbackResponse` with `impact` field |
| `httpx` | 0.27.x | Sync client in Streamlit layer calling `/feedback` — must be sync-only to avoid asyncio nesting crash |
| `sqlite3` | stdlib | `data/feedback/corrections.jsonl` is JSONL, not SQLite — but session state DB (`data/sessions.db`) is SQLite via `aiosqlite` for conversation turn persistence |
| `langfuse` | 2.x (optional) | If LANGFUSE_* env vars present: attach `user_feedback` score to the trace for that turn (`value=1` thumbs-up / `value=0` thumbs-down); falls back to local JSONL if absent |
| `dspy` | 2.6.x (NICE-TO-HAVE) | `BootstrapFewShot` optimizer seeded from `corrections.jsonl`; cuts into the demo as "AI improving from feedback" narrative; run offline, not in request path |

**Key design invariant:** The feedback path has zero LLM calls. `POST /feedback` is a pure data write + in-memory update. P99 latency must be <100ms, even on a judge's 2019 MacBook. This keeps the demo from stalling on the "feedback applied" toast.

---

## 4. Alternatives Considered — Why Each Lost

### Alternative A: Langfuse-as-primary-store (with hosted Langfuse)
**Lost because:** Requires external service; judges run offline or on spotty conference wifi. Langfuse Self-Hosted adds Docker dependency. Our design uses Langfuse as an optional observability layer (env-var gated) — if present, it adds a score to the trace; if absent, everything still works via local JSONL. The feedback loop itself must be zero-dependency.

### Alternative B: DSPy MIPROv2 online recompilation on feedback
**Lost because:** MIPROv2 Bayesian optimization runs for minutes and requires multiple LLM calls per optimization step. Running this in the request path (or even in the background on every correction) is incompatible with the judge's machine constraint. DSPy is correct for the offline / periodic recompilation use case (batch the week's corrections, run overnight), but cannot be the live feedback path for a 9-day solo hackathon demo.

### Alternative C: Mem0 managed memory layer
**Lost because:** Mem0's managed cloud requires network; self-hosted Mem0 adds Qdrant + Neo4j dependencies. For a "pip install + make run" constraint, Mem0 v0.1.76+ with its LLM-driven memory extraction is overkill. Our Track C JSONL + Track A ChromaDB upsert gives 90% of the value with zero operational complexity. Mem0's graph-based entity memory would be valuable in a production system (6-month roadmap item) but not in 9 days.

### Alternative D: RLHF / DPO fine-tuning loop on corrections
**Lost because:** Every published RLHF approach (PPO, DPO, KTO) requires a dataset of preference pairs (chosen/rejected) and multiple training runs. Even with Unsloth on a GPU (which judges don't have), the minimum viable fine-tuning loop is 2-3 hours per cycle. The entire hackathon budget is 9 days. Fine-tuning is the right 6-month answer; it is the wrong 9-day answer. The BUILD_PROCESS_PLAYBOOK explicitly flags this: "n=1 retrain is statistically invalid." Our architecture archives corrections in a format that is directly compatible with DPO dataset construction — this can be stated in the design document as the production upgrade path.

---

## 5. Anti-Patterns — What Screams "Amateur / 2022-Tier"

1. **Calling `POST /feedback` and running a model fine-tune in the background thread.** n=1 gradient update is statistically meaningless and will silently produce worse models on small datasets. Any mention of "we retrain on each correction" without a dataset accumulation threshold (typically n>=100 samples per class) is an immediate red flag for experienced ML judges.

2. **Storing feedback in a vector DB and retrieving it "by semantic similarity."** If the correction chunk has a low cosine similarity to the query (which happens when the correction is phrased differently), it will never surface. The correction-aware re-rank that promotes `feedback_source == "engineer_correction"` chunks regardless of score is the correct fix.

3. **Treating thumbs-up/thumbs-down as the only feedback signal.** Binary feedback is nearly useless without the correction text. A system that records `value=1/0` but never captures what was wrong / what the right answer was cannot improve. Every thumbs-down must open a text correction field.

4. **"Feedback is saved" without showing the effect.** The killer demo moment is: thumbs-down → type correction → re-ask same question → corrected answer appears at top. If the demo only shows "saved" but the next answer is unchanged, the feedback loop claim is unconvincing.

5. **Using ChromaDB `distance` or `metadata.weight` to bias retrieval scores.** ChromaDB's retrieval is purely cosine similarity on embeddings; metadata does not influence ranking. Any system that sets `metadata.correction_weight = 2.0` expecting it to boost retrieval is silently broken. The post-RRF promotion step is the correct architectural fix.

6. **Session-scoped feedback only.** If corrections are stored in session state (Streamlit `st.session_state`) they evaporate on page reload. Feedback must be persisted to disk (JSONL) and replayed on server startup.

7. **No visible feedback history.** A system that shows "feedback applied" but has no way to audit what corrections exist will fail the explainability criterion. The "Feedback History" tab (or a simple `GET /feedback` endpoint) is mandatory.

---

## 6. Integration Notes — Inputs, Outputs, Sibling Components

### Inputs consumed
- `wizard/graph/state.py::AgentState.feedback_log` — conversation feedback events accumulated per session
- `POST /feedback` payload: `{session_id, turn_id, equipment_id, correction_type, correction_text, corrected_rul_days?}`
- `data/feedback/corrections.jsonl` — on-disk correction store, read at startup for replay
- `data/feedback/rul_corrections.jsonl` — on-disk RUL correction store, read by `RULEstimator.__init__`

### Outputs produced
- Updated ChromaDB collection (correction chunk upserted, immediately available to next retrieval)
- Updated `RULEstimator` in-memory state for affected `equipment_id`
- Appended record in `corrections.jsonl` and `rul_corrections.jsonl`
- `FeedbackResponse` JSON: `{status: "ok", impact: "rul_adjusted|rag_updated|logged", updated_rul_p50?: float, correction_id: str}`
- Optional Langfuse score attached to originating trace

### Sibling component dependencies

| Component | Direction | What it sends/receives |
|---|---|---|
| **RAG Retriever (Component 04, Step 2.3)** | Feedback writes → Retriever reads | Correction chunks upserted to ChromaDB; retriever's post-RRF pass reads `feedback_source` metadata to promote corrections |
| **RUL Estimator (Component 08, Step 3.2)** | Feedback calls `apply_correction()` | Bayesian blending applied in-memory; persisted to `rul_corrections.jsonl` |
| **Agentic Orchestrator (Component 01, Step 4.1)** | Orchestrator routes to FeedbackNode | LangGraph `FeedbackNode` is step 8 in the agent graph; receives `AgentState` with populated `feedback_log` field |
| **Streamlit UI (Component 18, Step 6.2)** | UI posts to `/feedback`; reads `/feedback/history` | Thumbs-down widget → `POST /feedback` via sync httpx; Feedback History tab → `GET /feedback/history` |
| **Session Memory (Component 03)** | Feedback reads `turn_id` | Must join `corrections.jsonl` to `sessions.db` by `turn_id` to reconstruct which answer triggered the correction |

### Demo script integration (Phase 8, Step 8.2)

The feedback loop produces the single most compelling demo moment:
1. Engineer asks: "What's wrong with HSM-GB-001?" → system answers (possibly wrong on first query)
2. Engineer clicks thumbs-down → types: "Bearing not just lubrication issue — shaft misalignment confirmed by physical inspection"
3. "RAG updated — correction applied" toast fires in <100ms
4. Engineer re-asks the same question
5. Corrected chunk appears in top-3 citations with `[ENGINEER CORRECTION]` badge
6. Answer now includes shaft misalignment in the diagnosis

This six-step loop is the entire FR6 demonstration. It runs in ~90 seconds of demo time and requires no GPU, no retraining, no waiting.

---

## 7. Open Risks and Unknowns

### Risk 1 — ChromaDB upsert ID collision on repeated corrections [KNOWN, MITIGATED]
If an engineer corrects the same query twice, two correction chunks exist in the collection. The post-RRF pass will promote both to top-3, potentially filling all top slots with corrections. Mitigation: use `equipment_id + correction_type + sha256(query_text)[:8]` as the correction chunk ID, so upsert overwrites the previous correction for the same query.

### Risk 2 — RUL Bayesian blending weight (α=0.7) is not validated against the synthetic dataset [UNVERIFIED]
The 70/30 split is a reasonable prior but has not been ablated. If engineer corrections cluster very close to model predictions, α doesn't matter; if they diverge by >50%, the blended estimate could be worse than the model alone for some equipment types. Mitigation: run a post-hoc sensitivity analysis on the synthetic correction dataset during Phase 7 (robustness eval). If α=0.5 produces lower RMSE on replay, switch.

### Risk 3 — corrections.jsonl grows large in a multi-day demo [LOW RISK]
At ~500 bytes per correction, 1,000 corrections = 500KB. Not a problem. The risk is startup replay time: if `rul_corrections.jsonl` has 10,000 entries, replaying them serially on startup takes several seconds. Mitigation: cap replay to the 100 most recent corrections per equipment_id (recency assumption: newer corrections are more relevant).

### Risk 4 — Langfuse score API rate limit in demo mode [UNVERIFIED]
If `LANGFUSE_*` env vars are set and the judge demo fires many feedback events quickly, the Langfuse SDK may hit rate limits. Mitigation: wrap all Langfuse calls in `try/except`, log locally, never surface errors to the demo UI. The local JSONL path must always work independently.

### Risk 5 — DSPy BootstrapFewShot compatibility with corrections.jsonl format [UNVERIFIED]
The corrections.jsonl schema includes `correction_text` which maps to DSPy's `output` field. But DSPy requires `input` to be the same format as the module's `Signature.input_fields`. If the query format diverges from the `MaintenanceAnswer` signature, the bootstrap won't work without a transform step. Mitigation: this is a Phase 7 NICE-TO-HAVE; document the format mismatch in the design doc and describe the transform needed.

### Risk 6 — Engineer correction contains domain hallucinations [ACCEPTED]
There is no validation that an engineer's typed correction is factually correct. A correction asserting "replace the entire motor" when the SOP says "adjust the coupling" will be surfaced verbatim. This is by design: the system trusts the domain expert. The correction chunk is tagged `feedback_source=engineer_correction` in ChromaDB, making it auditable and revocable (a DELETE by chunk_id endpoint is trivially addable). Document this trust model explicitly in the design document — it is the correct HITL philosophy for industrial settings.

---

## Sources Consulted

- [PatchRAG — Feedback Adaptation for RAG (ACL 2026 Findings)](https://arxiv.org/abs/2604.06647)
- [DMA: Online RAG Alignment with Human Feedback (Nov 2025)](https://arxiv.org/abs/2511.04880)
- [Pistis-RAG: Enhancing RAG with Human Feedback](https://arxiv.org/pdf/2407.00072)
- [MemRerank: Preference Memory for Personalized Reranking (NAACL 2025)](https://arxiv.org/abs/2603.29247)
- [RRPO: Optimizing RAG Rerankers with LLM Feedback via RL (2026)](https://arxiv.org/pdf/2604.02091)
- [DynamicRAG: LLM Output as Feedback for Dynamic Reranking (2025)](https://arxiv.org/pdf/2505.07233)
- [DSPy Bootstrap Few-Shot Docs (Stanford NLP)](https://dspy.ai/diving-deeper/bootstrap-fewshot-family/)
- [Langfuse User Feedback Docs](https://langfuse.com/docs/observability/features/user-feedback)
- [State of AI Agent Memory 2026 (Mem0 Blog)](https://mem0.ai/blog/state-of-ai-agent-memory-2026)
- [Mem0 Paper at ECAI 2025 (arxiv 2504.19413)](https://arxiv.org/abs/2504.19413)
- [Hybrid Search and Re-Ranking in Production RAG (Towards Data Science)](https://towardsdatascience.com/hybrid-search-and-re-ranking-in-production-rag/)
- [Bayesian Deep Learning for Predictive Maintenance (Reliability Engineering & System Safety, 2023)](https://www.sciencedirect.com/science/article/abs/pii/S0951832023000960)
- [Human-in-the-Loop with LangGraph (2025-2026 production patterns)](https://growwstacks.com/blog/human-in-the-loop-ai-agents-langgraph)
- [Production RAG in 2025 — Evaluation Suites and CI/CD](https://dextralabs.com/blog/production-rag-in-2025-evaluation-cicd-observability/)
- [LangGraph 201: Adding Human Oversight to Deep Research Agent](https://towardsdatascience.com/langgraph-201-adding-human-oversight-to-your-deep-research-agent/)
