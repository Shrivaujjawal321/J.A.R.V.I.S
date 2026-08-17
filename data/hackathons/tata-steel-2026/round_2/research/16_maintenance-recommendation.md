# Component 16: Maintenance Recommendation Generation
**Tata Steel AI Hackathon 2026 — Round 2 Research Brief**
*Research date: 2026-06-06 | Constraint: CPU-only, solo build, ~9 days, pip-install-first*

---

## 1. Recommended Approach — The Single Winner

**Two-Pass SOP-Grounded Generation: Tool-Forced Structured Draft + Citation-Pass Enrichment + Instructor v1.15 Validation**

The winning architecture for component 16 is a two-pass LLM pipeline that separates the concern of *structured output integrity* (Pass 1) from *source traceability* (Pass 2), because Anthropic's API enforces a hard constraint: Citations API and Structured Outputs are mutually exclusive (400 error if both are enabled simultaneously). Trying to get both in one pass from the API is the primary architectural trap that must be avoided.

**Pass 1 — Structured Plan Generation (Instructor + tool-forced JSON):**

A single LLM call (Claude Haiku-3.5 via `instructor.from_anthropic(client, mode=instructor.Mode.ANTHROPIC_TOOLS)`) takes the upstream `RCAOutput` (from Component 11), retrieved SOP/manual chunks (from Component 04), spare parts availability lookup (from a lightweight in-memory YAML store), and a severity-to-urgency mapping table. It generates a fully validated `MaintenanceRecommendation` Pydantic model with these top-level fields:

```python
class ActionStep(BaseModel):
    step_number: int
    action: str                    # imperative verb, max 120 chars
    responsible_role: str          # "Maintenance Technician", "Safety Officer", etc.
    estimated_duration_minutes: int
    tools_required: list[str]
    safety_precautions: list[str]
    sop_ref: str                   # e.g. "SOP-HYD-03 §4.2"
    evidence_basis: str            # free-text, 1 sentence citing RCA finding or SOP clause

class SparePart(BaseModel):
    part_name: str
    part_number: str | None
    quantity: int
    procurement_lead_days: int
    in_stock: bool
    urgency_override: str | None   # "CRITICAL - order immediately" if lead > shutdown tolerance

class MaintenanceRecommendation(BaseModel):
    recommendation_id: str         # UUID
    equipment_id: str
    fault_ref: str                 # links to RCA fault_id
    urgency: Literal["IMMEDIATE", "WITHIN_24H", "WITHIN_72H", "SCHEDULED", "MONITOR"]
    risk_classification: Literal["CRITICAL", "HIGH", "MEDIUM", "LOW"]
    executive_summary: str         # max 3 sentences, plain English for shift manager
    immediate_actions: list[ActionStep]   # steps to take now (safety, shutdown, containment)
    repair_steps: list[ActionStep]        # full corrective maintenance sequence
    post_repair_checks: list[ActionStep]  # validation/commissioning steps
    long_term_monitoring: list[str]       # ongoing sensor thresholds or inspection intervals
    spare_parts: list[SparePart]
    procurement_strategy: str      # narrative: order now vs. await scheduled window, justification
    optimized_maintenance_window: str     # "Next planned shutdown or within 48h if deterioration"
    estimated_total_downtime_hours: float
    sources_used: list[str]        # chunk IDs / SOP doc names; used in Pass 2 for citation fetch
    confidence_score: float        # 0.0–1.0 based on RCA confidence * retrieval score
    feedback_id: str | None        # filled in after engineer approves/edits for feedback loop
```

Instructor automatically validates the output against this schema, auto-retries up to `max_retries=3` with the validation error injected back into the conversation, and raises a typed exception if validation fails after retries. This gives ~99.5% valid JSON in production (per Instructor's documented performance with `ANTHROPIC_TOOLS` mode).

**Pass 2 — Citation Enrichment Pass (Anthropic Citations API, narrative only):**

After Pass 1 returns a valid `MaintenanceRecommendation`, Pass 2 makes a second API call using the Citations API (`citations.enabled=True`) — but this call is NOT a JSON call. It asks Claude to produce a *human-readable narrative justification* block: "Explain why steps 1–3 are recommended, citing the retrieved SOPs and historical records." The Citations API returns interleaved text blocks with `char_location` or `content_block_location` citations pointing back to the document blocks injected into the prompt. This narrative block is attached to the `MaintenanceRecommendation` as a `narrative_justification: str` and `inline_citations: list[CitationRef]` field that is populated post-hoc (not validated by Instructor, just appended).

This two-pass design is the correct production-grade pattern. It gives:
- Pass 1: machine-readable, validated, deterministic structure (for agentic downstream use, report rendering, spare-parts lookup)
- Pass 2: human-readable, citation-grounded narrative (for explainability score from judges, for engineer comprehension)

Total latency: Pass 1 (~1.5–3s Haiku) + Pass 2 (~1–2s Haiku) = ~3–5s end-to-end. Within the 5s budget for interactive queries.

**Prompt caching on SOPs:** All retrieved SOP/manual chunks that are stable documents are passed as `document` blocks with `cache_control: {type: "ephemeral"}` in both passes. Since the same SOP sections will be retrieved repeatedly across many queries, cache hits reduce cost by ~80% and latency by ~60% from the second query onward.

**Feedback loop integration:** Every `MaintenanceRecommendation` gets a `feedback_id` UUID written to `data/feedback/recommendations.jsonl`. When an engineer marks a recommendation as "Helpful", "Partially Correct", or "Incorrect" via the UI, the record is updated. A weekly batch job reads these records and constructs few-shot examples for the system prompt (positive examples from "Helpful" verdicts, negative examples with correction notes from "Incorrect" verdicts). This directly implements FR6 (feedback-driven improvement).

---

## 2. Why This Wins — Evidence Chain

### 2a. Instructor v1.15 + ANTHROPIC_TOOLS mode: the production-proven approach for structured LLM output

Instructor is the dominant production library for structured LLM outputs: 3M+ monthly downloads, 11k stars, deployed by LSEG in market surveillance. Version 1.15.1 (latest as of research date) supports Anthropic's tools mode natively. The key insight from the DEV Community write-up (Jan 2026): "Claude models don't support structured output the way OpenAI does, but you can achieve the same effect by using tool-based structured output with schema validation... tool_use with tool_choice forced to a specific tool achieves approximately 99.5% valid output in production when combined with Pydantic validation and a retry loop." This is exactly what `instructor.Mode.ANTHROPIC_TOOLS` implements.

Instructor's semantic validation (released 2025) allows field-level validators like `@field_validator('urgency')` that check domain logic — e.g., "if risk_classification is CRITICAL, urgency must be IMMEDIATE or WITHIN_24H." These validators run locally and trigger the auto-retry loop without an extra API call, keeping latency low.

### 2b. PARAM (arXiv 2508.04714): direct precedent for three-tiered prescriptive maintenance architecture

PARAM (Prescriptive Agents based on RAG for Automated Maintenance, Harbola et al., Aug 2025) is the closest published system to this component's design. Its prescriptive layer "begins with anomaly contextualization, where the system evaluates fault severity in conjunction with equipment criticality" before generating recommendations including "precise action sequences, required tools and materials, safety considerations, and validation procedures with full decision pathway documentation." PARAM reported **40–60% mean-time-to-repair reductions** when using Gemini Flash for real-time alerts vs. baseline manual lookup. The benchmark in Table II showed Gemini-1.5-Flash achieving 5.0/5 completeness at 2.4s latency — validating Haiku-class models as sufficient for recommendation generation.

PARAM's key design lesson adopted here: the three tiers (anomaly contextualization → risk assessment → intervention generation) map exactly to this component's (RCA input → urgency/risk mapping → structured plan generation). The evidence that generic recommendation (no grounding) scored only 3.5/5 vs. 5.0/5 with full RAG grounding confirms that SOP-retrieval-first is mandatory, not optional.

### 2c. PHMForge (arXiv 2604.01532, April 2026): Claude + sequential reasoning outperforms Plan-Execute for maintenance actions

PHMForge benchmarked leading frameworks and LLMs on industrial asset maintenance tasks (75 scenarios, 5 task categories). Key finding: **Claude Code with Sonnet 4.0 achieved 68% task completion** (best of all tested), specifically excelling at cost-benefit analysis (80% completion) through sequential reasoning: RUL prediction → fleet ranking → threshold application → cost modeling → ROI. The Plan-Execute paradigm dropped from 65% to 46% on the same tasks, confirming that step-by-step sequential generation with state persistence beats the "plan everything upfront" approach for maintenance recommendations. This validates generating the `MaintenanceRecommendation` in a single structured call (not decomposed into multiple plan-then-execute steps which would add latency and coordination overhead).

PHMForge also confirmed that "no model exceeds 70% completion rate across the full benchmark" in the AssetOpsBench study (IBM Research, arXiv 2506.03828), meaning the bottleneck is tool orchestration (23% incorrect sequencing) — which the Instructor-enforced schema directly mitigates by guaranteeing the output structure the orchestrator consumes.

### 2d. Anthropic Citations API: the traceability standard as of 2025

The Citations API (launched Jan 2025, GA confirmed June 2025 on Amazon Bedrock) provides "character-level pointers back to source documents" with "better citation reliability than prompt-based approaches" — in Anthropic's internal evaluations, it was "significantly more likely to cite the most relevant quotes." The critical production detail confirmed in the official docs: `cited_text` does not count against output tokens, providing cost savings vs. prompt-based quoting. The incompatibility with Structured Outputs is explicitly documented as a 400 error when both `output_config.format` and `citations.enabled` are set — confirming the two-pass design is the only correct approach.

The `context` field on each document block (not counted toward cited text, but visible to the model) is used to inject metadata: `"context": '{"doc_id": "SOP-HYD-03", "section": "4.2", "last_revised": "2024-11"}'`. This metadata is then available in the narrative justification pass to help Claude construct proper references like "per Section 4.2 of SOP-HYD-03 (revised Nov 2024)."

### 2e. GraphRAG + CoT for structured maintenance document generation: 2026 ScienceDirect validation

The 2025 ScienceDirect paper "A stepwise intelligence generative method for structured maintenance guidance documents based on knowledge graph augmented LLM" (doi: 10.1016/j.aei.2025.004161) directly validates the design: "Current LLM applications in generating industrial documents have issues with inaccurate content and structure that does not match professional requirements." The solution — "professional knowledge graph retrieval augmented generation (GraphRAG) and chain-of-thought (CoT) prompts to guide LLMs to intelligently generate structured maintenance guidance documents step by step" — is what the system prompt's `<reasoning_steps>` block implements. The CoT structure in the prompt forces the model to reason: evidence summary → urgency classification → immediate safety actions → repair sequence → spares assessment → monitoring plan. This matches the expert-authored maintenance guidance structure, reducing structural mismatch.

### 2f. Feedback-driven few-shot improvement: validated pattern

The LogSyn paper (arXiv 2511.18727, Nov 2025) demonstrated few-shot LLM extraction from unstructured aviation maintenance logs — "few-shot prompting is cost-effective for extracting structured insights." The feedback loop design (positive/negative few-shot examples from engineer verdicts) directly implements FR6. Storing raw feedback in `recommendations.jsonl` and re-injecting as few-shot examples in the next system prompt update is the lowest-friction implementation: no fine-tuning, no retraining, just prompt update. The system prompt already has prompt caching enabled so the updated few-shot block gets cached on first use.

---

## 3. Exact Stack

| Library / Tool | Version | Role |
|---|---|---|
| `anthropic` | 0.40.0+ | LLM API client for both structured (tools) and citation calls |
| `instructor` | 1.15.1 | Wraps Anthropic client with `Mode.ANTHROPIC_TOOLS`, Pydantic validation, auto-retry |
| `pydantic` | 2.7.x | Schema definition, field validators, serialization to JSON |
| `langchain-core` | 0.3.x | Message formatting, prompt templates (used only for prompt assembly, not for LLM calls) |
| `arize-phoenix` | 4.x (pip) | Trace UI — records both Pass 1 and Pass 2 spans with prompt, output, token counts |
| `openinference-instrumentation-anthropic` | latest | Auto-instruments `anthropic` client → Phoenix spans |
| `sentence-transformers` | 3.x | NLI cross-encoder for post-hoc claim faithfulness check (reused from Component 06) |
| `cross-encoder/nli-deberta-v3-small` | HuggingFace model (~80MB) | Faithfulness gate: claim-vs-source entailment scoring |
| `PyYAML` | 6.x | Spare parts YAML store (in-memory, no DB needed for demo) |
| `uuid` | stdlib | Recommendation ID and feedback ID generation |

---

## 4. Alternatives Considered

### Alt A — LangChain `with_structured_output()` + LCEL chain

**Tradeoff that made it lose:** `with_structured_output()` for Anthropic uses `bind_tools` under the hood, which is functionally equivalent to Instructor's `ANTHROPIC_TOOLS` mode — but with more abstraction layers. LangChain's deprecation of `LLMChain`/`SequentialChain` in favor of LCEL pipes means any tutorial-sourced patterns are likely outdated. More importantly, LangChain adds 3-5 additional failure points (LCEL runnable composition, message conversion, parser mismatch) compared to Instructor's single-abstraction-layer design. For a solo 9-day build where demo stability is scored, the fewer abstraction layers the better. Instructor's retry mechanism is also more transparent than LangChain's output parser error handling.

### Alt B — Anthropic Native Structured Outputs (`output_config.format`)

**Tradeoff that made it lose:** Anthropic's native structured outputs (public beta as of late 2025, using constrained decoding where "the model cannot produce tokens that would violate your schema") are not yet available on all models in all regions [unverified for Haiku-3-5 specifically]. More critically, native structured outputs are **incompatible with Citations API** — this is a hard API constraint, not a soft recommendation. Since citation traceability is a judging criterion (FR4: explainable + traceable outputs), abandoning citations to get native structured outputs would be a net loss. Instructor's tool-use approach achieves 99.5% valid output and is fully compatible with the two-pass design.

### Alt C — DSPy compiled signatures for recommendation generation

**Tradeoff that made it lose:** DSPy (v2.5+) with a compiled `MaintenanceRecommendationSignature` would optimize the prompt via bootstrap few-shot automatically and reduce prompt engineering time. However, DSPy compilation requires an eval dataset and a teleprompter run that takes 20–60 minutes on CPU (if using `BootstrapFewShot`) and adds `pip install dspy` plus a compile step that breaks the "pip install + run" judge experience. DSPy is the right choice if you have 3+ weeks and a labeled eval set — for a 9-day solo build targeting a judge's machine, Instructor with manually crafted few-shot examples in the system prompt achieves comparable structure quality with zero compilation overhead.

### Alt D — Single-pass with manual JSON Mode (no Instructor)

**Tradeoff that made it lose:** Prompting Claude to output raw JSON without tool-use enforcement has a 5–15% malformed output rate for complex schemas (12+ fields with nested objects). Manual retry logic adds ~50 lines of boilerplate. Without Instructor's `@field_validator` hooks, domain-logic violations (CRITICAL risk with MONITOR urgency) silently pass through to the UI. This is "2022-tier" pattern — acceptable for a quick prototype, not for a hackathon that scores "error-free" and "accurate."

---

## 5. Anti-Patterns (What Screams Amateur / 2022-Tier)

- **Free-form text recommendation:** "Replace the seal" with no step number, no tool list, no SOP reference, no urgency field. A judge reads this and sees a chatbot, not a maintenance system.
- **Single LLM call trying to do both citations AND structured JSON:** This throws a 400 error from the Anthropic API. Any submission that does this crashes on the judge's machine.
- **Hardcoded recommendations:** A lookup table like `if fault_type == "bearing_failure" → print(BEARING_REPAIR_STEPS)`. No LLM reasoning, no SOP grounding, no adaptation to severity or spare availability. Screams pre-LLM era.
- **No validation retry:** If the first LLM call returns malformed JSON, the demo crashes. Instructor's retry loop is non-optional for demo stability.
- **Ignoring spare parts availability:** Recommending "replace pump impeller immediately" when lead time is 14 days and the current maintenance window is 2 days is not actionable. The `SparePart.procurement_lead_days` field and `procurement_strategy` narrative exist specifically to prevent this.
- **No urgency classification:** All recommendations listed as "HIGH priority" regardless of whether the equipment is about to fail catastrophically or just needs a lubrication check next month. The `Literal["IMMEDIATE", "WITHIN_24H", "WITHIN_72H", "SCHEDULED", "MONITOR"]` enum forces the model to make the distinction.
- **No feedback loop artifacts:** `feedback_id: None` on every recommendation = no FR6 implementation. Even a stub JSONL logger with a UI button counts; absence is a zero.
- **Hallucinated tool names and part numbers:** Without SOP-grounded retrieval, the LLM invents tool names like "Model X-400 pressure gauge" that don't exist. The `evidence_basis` field in `ActionStep` and the citation pass force grounding to retrieved text.

---

## 6. Integration Notes

### Inputs consumed

| Source Component | Data | Format |
|---|---|---|
| Component 11 (RCA) | `RCAOutput` with fault_id, symptom, rca_chain, root_cause, risk_level, confidence, sop_reference | Pydantic model / JSON |
| Component 04 (RAG) | Top-5 retrieved SOP/manual chunks for the fault type | List of `RetrievedChunk(text, doc_name, section, page, score)` |
| Component 08 (RUL) | `RULPrediction(equipment_id, rul_hours, rul_confidence)` | Pydantic model |
| Component 09/10 (Anomaly/Failure) | Current severity classification, sensor anomaly flags | Dict |
| Spare Parts Store | YAML file: `data/knowledge/spare_parts.yaml` listing part names, numbers, stock status, lead times | In-memory dict loaded at startup |

### Outputs produced

| Downstream Consumer | Data | Format |
|---|---|---|
| Orchestrator (Component 01) | `MaintenanceRecommendation` Pydantic object | JSON via `model.model_dump()` |
| Report Generator | `MaintenanceRecommendation` + `narrative_justification` + `inline_citations` | Combined JSON for PDF/HTML rendering |
| UI (chat panel) | `executive_summary` + `immediate_actions` rendered as numbered list | Markdown string |
| Feedback Store | `feedback_id` → `data/feedback/recommendations.jsonl` | JSONL append |
| Explainability Component (06) | `sources_used` list + `inline_citations` list | Passed to `ExplainabilityRecord` |
| Alert System (Component 07) | If `urgency == "IMMEDIATE"` → trigger alert with `executive_summary` | Event bus message |

### LangGraph node placement

The recommendation generator sits as node `generate_recommendations` in the main agentic graph, downstream of `run_rca` and `lookup_spares`, upstream of `generate_report` and `check_urgency_alert`. It is a single-shot node (not a loop) with a `retry_count` state field that the Instructor retry mechanism populates automatically.

```
[retrieve_context] → [run_rca] → [lookup_spares] → [generate_recommendations] → [generate_narrative_citations] → [generate_report]
                                                                                       ↓ (if urgency=IMMEDIATE)
                                                                               [trigger_alert]
```

---

## 7. Open Risks and Unknowns

- **[unverified] Haiku-3-5 availability on Instructor 1.15 ANTHROPIC_TOOLS mode:** The Instructor docs show integration for `claude-haiku-3-5-20241022` but the exact model ID string must be verified against the current Anthropic models endpoint. If Haiku-3-5 is unavailable, fall back to `claude-3-haiku-20240307` — older but confirmed working.

- **[unverified] Pass 2 latency with large SOP documents:** If the Retrieved chunks total >8000 tokens, Pass 2 (citations pass) may hit 3–4s latency on Haiku. This is within a 5s budget but if latency becomes an issue, the citation pass can be made async (fire-and-forget, results appended when available) to keep the UI responsive.

- **Schema complexity vs. retry budget:** The `MaintenanceRecommendation` schema has 15+ fields with nested models. Instructor's `max_retries=3` should cover typical validation failures (missing field, wrong enum value), but a pathologically ambiguous fault description might exhaust retries. Mitigation: add `@model_validator(mode='before')` to fill defaults (e.g., `spare_parts=[]` if not mentioned, `long_term_monitoring=["Monitor per standard inspection schedule"]`) so the model never has to hallucinate lists for truly unknown values.

- **Spare parts YAML coverage gap:** The demo spare parts YAML will only cover equipment types in the synthetic knowledge base (hydraulics, bearings, motors, pumps). If a judge asks about an equipment type not in the YAML, `SparePart.in_stock` defaults to `False` and `procurement_lead_days` defaults to 14 with a flag "Verify with procurement." This is safer than hallucinating a part number.

- **Feedback loop cold-start:** On day 1 of the demo, there are zero engineer feedback records, so the few-shot block in the system prompt is empty. This is fine — Instructor's base output quality without few-shot examples is sufficient. The feedback examples only matter for the "improvement loop" framing in the presentation, not for output quality on day 1.

- **Citations API regional availability:** As of June 2025, the Citations API is GA on Anthropic API and Amazon Bedrock. Direct API access is fine. If the judge's machine has no internet, both passes fail — but this is a general internet dependency for any cloud LLM demo, not specific to this component.

---

*Sources consulted: [PARAM arXiv 2508.04714](https://arxiv.org/abs/2508.04714) · [PHMForge arXiv 2604.01532](https://arxiv.org/abs/2604.01532) · [AssetOpsBench arXiv 2506.03828](https://arxiv.org/abs/2506.03828) · [Anthropic Citations Docs](https://platform.claude.com/docs/en/docs/build-with-claude/citations) · [Instructor PyPI 1.15.1](https://pypi.org/project/instructor/) · [Instructor Anthropic Integration](https://python.useinstructor.com/integrations/anthropic/) · [ScienceDirect Stepwise Maintenance Guidance 2025](https://www.sciencedirect.com/science/article/abs/pii/S1474034625004161) · [Generative LLM Predictive Maintenance ScienceDirect 2026](https://www.sciencedirect.com/science/article/abs/pii/S0360835226002962) · [Anthropic Citations API Announcement](https://claude.com/blog/introducing-citations-api) · [Simon Willison Citations Analysis](https://simonwillison.net/2025/Jan/24/anthropics-new-citations-api/)*
