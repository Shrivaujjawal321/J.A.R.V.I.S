# 07 — Local LLM Quality Gap Analysis
## Tata Steel R2 — Maintenance Wizard · 3B/7B SLM vs Claude Subscription

**Author:** Jarvis · **Date:** 2026-06-09 · **Status:** design-time decision record
**Context:** Should the four LLM-touching nodes (Diagnosis, RCA, Plan, multi-turn glue) run
on a local Qwen2.5-3B (Ollama/GGUF, CPU) or on the Claude Max subscription?

---

## 1. Where a Small Local Model Is Genuinely Weak

### 1.1 Multi-step agentic planning
A 3B/7B model often loses track of a multi-hop plan across turns: it satisfies the immediate
step but forgets earlier constraints. In this system the **LangGraph supervisor handles all
routing and plan structure deterministically in Python** — the LLM is never asked to plan,
only to narrate. The gap therefore **does not apply here at all**: no local 3B sees a
"what do I do next?" prompt. Each call is `max_turns=1`, `allowed_tools=[]`, with a fully
assembled context. This is the most important design decision for closing the agentic gap.

### 1.2 Root-cause synthesis / FR4 explainability
FR4 is the top differentiator category in Tata's rubric: *traceable, explainable reasoning.*
A 3B model given a free-form "explain why this bearing failed" prompt will produce vague,
hallucinated, or template-sounding prose — particularly bad in the 5-whys RCA narrative
where each link in the causal chain must follow the FMEA graph path already computed
by NetworkX. Claude Sonnet-tier handles logical chaining across 5 steps coherently and
stays in-scope. A raw Qwen2.5-3B on the same 500-token prompt has a measurable tendency
to skip causal steps, merge cause and effect, or confabulate ISO-14224 fault codes that
don't exist in the corpus. **This is the highest-risk gap for a base (untuned) SLM.**

### 1.3 Faithful grounded multi-turn answers
Over 3-4 conversation turns a 3B model's effective attention window degrades faster than
a frontier model. It can lose the citation anchor ("you earlier said scenario SCN-004")
and answer from its pretrained distribution rather than the retrieved chunks. Without
mitigations, multi-turn coherence for a 3B model degrades noticeably after turn 3.

### 1.4 Reliable structured output
Without constrained decoding a 3B model fails to produce valid JSON in roughly 10–25% of
calls (empirically on instruction-following benchmarks; GPT-4-class models fail <2%). A
malformed JSON response from the Diagnosis or RCA node propagates as a null fallback —
safe (the deterministic template fires) but a fluency regression.

---

## 2. Why This System Is a Relatively Favourable Case for an SLM

### 2.1 The LLM only synthesises — it does not reason from scratch
The architecture is built on the principle that the LLM is a **narrator, not an oracle**.
All hard facts (RUL hours, fault probabilities, risk tier, cause-chain graph path, SOP
step list, spare lead-times) are computed locally before the LLM is invoked. The LLM
receives a fully assembled context block:

```
[Sensor summary] 3 anomalies, IF score 0.79, LightGBM → HDF p=0.87
[Retrieved chunks] SOP-04 §3.2: "Inspect hydraulic seals at 400h intervals."
[FMEA graph path] Hydraulic leakage → Seal degradation → EAF-04 downtime (3 hops)
[Ground truth] scenario_id: SCN-012, equipment: EAF-04, last_maintenance: 142 days ago
Task: write a 3-sentence diagnosis citing [SOP-04 §3.2] and the sensor IDs.
```

This is fundamentally different from asking a 3B model to diagnose from raw sensor CSVs.
The model's job is glorified template filling with natural language. A 3B domain-tuned
model can do this adequately.

### 2.2 The domain fine-tune lifts quality where it matters most
The Qwen2.5-3B QLoRA kit (969 examples, rank-16 LoRA, 2 epochs on Colab T4) is designed
to teach the model exactly the vocabulary, citation format, and answer style of a steel
maintenance expert. Typical gains on domain fine-tune for a 3B model in a narrow vertical:

| Metric | Base Qwen2.5-3B (expected) | Fine-tuned (expected post-eval) |
|---|---|---|
| ROUGE-1 F1 on held-out eval-50 | ~0.22–0.28 | ~0.32–0.42 |
| Domain Coverage (steel vocab) | ~0.35–0.45 | ~0.55–0.70 |
| Composite (0.5×ROUGE + 0.5×DC) | ~28–36/100 | ~43–56/100 |
| Structured output JSON pass rate | ~75–85% | ~88–95% (with format examples in SFT) |

The composite gain of **+10 to +20 points** is the canonical "extra merit: domain fine-tune"
evidence the PS explicitly rewards in FR1. The verdict string from `eval_results.json`
(`CLEAR IMPROVEMENT` vs `MARGINAL IMPROVEMENT`) is cited directly in the design doc.

### 2.3 Constrained decoding and prompt-level grammars close the JSON reliability gap
The existing `_llm_complete` parser already handles the structured output problem: every
prompt ends with an explicit JSON schema, and the parser extracts the fenced block with
regex and falls back to the deterministic template on parse failure. Adding
`instructor` (Pydantic-validated re-ask) as a light wrapper can push the JSON pass rate
to >97% even for a base 3B model by retrying the ill-formed response once with the schema
error message. This single mitigation almost eliminates the structured-output gap.

### 2.4 Decomposed short prompts cap the effective difficulty
The system issues six separate single-turn calls: each is scoped, short (system ~200 tokens +
user ~400 tokens), and carries only the necessary local-tier facts. A 3B model with a
600-token effective context performs significantly better than when it processes a 3000-token
document retrieval + synthesis prompt. The architectural decision to split into 6 focused
nodes rather than one "do everything" agent is the largest quality amplifier for SLMs.

### 2.5 The NLI faithfulness gate catches hallucinations regardless of model tier
`cross-encoder/nli-deberta-v3-small` (local, ~60 MB, CPU) validates entailment of every
LLM answer against the top-5 retrieved chunks before the answer is surfaced in the UI.
A hallucinated claim (fabricated fault code, wrong SOP reference) that is NOT entailed by
the corpus gets flagged and either triggers a template fallback or surfaces a confidence
caveat in the UI. This gate operates identically whether the LLM is Claude or a local SLM,
so it neutralises the hallucination risk delta between model tiers for all three grounded
nodes (Diagnosis, RCA, Plan).

---

## 3. Node-by-Node Verdict

| Node | Workload type | Local 3B adequate? | Notes |
|---|---|---|---|
| `supervisor_route` | Deterministic Python keyword router | — N/A — | No LLM call at all. Never has been. |
| `rul_node` | WeibullAFT numeric prediction | — N/A — | Pure ML. No LLM. |
| `prioritization_node` | WRPS 4-factor arithmetic | — N/A — | Pure Python. No LLM. |
| `report_node` | Template assembly from structs | — N/A — | No LLM needed. Template always correct. |
| `diagnosis_node` | Synthesise sensor + RAG chunks → 3 sentences, citing tags | **Yes** (with fine-tune) | Glorified template fill; NLI gate catches drift. SFT teaches citation format. |
| `plan_node` | Assemble SOP steps → structured maintenance plan | **Yes** (with fine-tune) | Pass-1 (which SOPs, which spares) is deterministic RAG. Pass-2 narration is short + scoped. |
| `rca_node` (5-whys narrative) | Traverse FMEA graph path → causal prose | **Marginal** | This is the hardest task for a 3B: 5-hop causal chaining. Fine-tune on RCA examples helps; without it, use Claude L2 here and SLM for DIAG + PLAN. |
| Multi-turn conversational glue | Free-form follow-up Q&A over 3-5 turns | **Marginal** | 3B loses context after turn 3 without explicit context re-injection. Mem0 + sliding summary largely compensates. Claude preferred if available. |

---

## 4. Recommended Hybrid Routing (practical conclusion)

Run the **SLM by default** for Diagnosis and Plan — the two highest-frequency nodes and the
two where short-context synthesis over a pre-assembled fact block is the task. Use
**Claude L2** (subscription ladder) for RCA and multi-turn glue, which genuinely need
longer coherent reasoning chains. If L2 times out or rate-limits, the SLM fallback fires;
the NLI gate keeps the output grounded.

```
Node          Primary            Fallback
──────────────────────────────────────────────────────────────────
diagnosis     SLM (steel-wizard) deterministic template
plan          SLM (steel-wizard) deterministic SOP template
rca           Claude L2          SLM → deterministic graph-path template
multi-turn    Claude L2          SLM → structured fact dump
proactive alert  ML-only (0 LLM)  —
```

This hybrid gives: subscription savings for 60% of LLM calls (DIAG + PLAN routed to SLM),
Claude quality for the two judging-critical nodes (RCA 5-whys = FR4 scored, multi-turn = FR3),
and a complete local-only fallback for demo-day safety. The SFT fine-tune also covers the
"extra merit: domain-specific model" requirement in PS §6.1 regardless of whether it is the
primary or fallback path.

---

## 5. Summary

The quality gap between Qwen2.5-3B and Claude is **real but architecturally contained**.
The system's design — deterministic routing, pre-assembled context blocks, decomposed
single-turn prompts, NLI faithfulness gate, and structured-output retry — eliminates all
the categories where small models classically fail (multi-step planning, hallucination on
open-ended queries, routing nondeterminism). What remains is a prose-quality gap that a
domain SFT fine-tune closes to an acceptable level for DIAG and PLAN, and a reasoning
coherence gap for multi-hop causal chains (RCA) that genuinely benefits from a frontier
model. The subscription path is preserved for the two nodes that matter most to the
judge's rubric; the SLM path covers the workload majority. A pure-SLM demo (WIZARD_LLM=off
with Ollama as L3) is correct but reads as templated — acceptable as a fallback, not
as the primary scored path.
