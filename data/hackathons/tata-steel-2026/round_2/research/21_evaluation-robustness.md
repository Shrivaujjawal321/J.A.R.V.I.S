# Component 21: Evaluation Suite & Demo Robustness
## Tata Steel AI Hackathon 2026 — Round 2 — Research Report

**Date:** 2026-06-06
**Component:** Eval harness (Ragas for RAG, golden set for diagnosis/RCA), accuracy + latency measurement, 7 operational qualities (fast/efficient/accurate/robust/error-free/smooth). Guardrails so nothing breaks live.

---

## 1. Recommended Approach (Single Winner)

**DeepEval v4.x as the primary eval harness, layered with Ragas v0.2+ for RAG-specific metrics, Langfuse for live observability, and a circuit-breaker + cached-fallback pattern for demo robustness.**

This is not a neutral menu — this is the exact combo that covers (a) agentic tool-call evaluation, (b) RAG faithfulness/precision/recall, (c) multi-turn conversation quality, (d) real-time cost/latency tracing, and (e) live-demo safety — all from pip install, no Docker required, runs locally on a judge's CPU-constrained machine.

The architecture has three execution contexts:

- **Offline (pre-demo):** Run the full DeepEval + Ragas golden-set suite as pytest. Gate: all critical metrics must pass thresholds before demo. Takes ~5-10 minutes against 50-100 test cases.
- **Online (during demo):** Langfuse traces every LLM call live. Shows judges per-call latency, token cost, and the cited source chunks. This is the "explainability screen" judges score.
- **Safety net (runtime guardrails):** circuit breaker + cached gold responses + input/output validators prevent any crash or hallucinated advice in front of judges.

---

## 2. WHY — Evidence-Based Reasoning

### DeepEval v4.0.5 (released May 28, 2026) — the decisive pick

DeepEval is the only framework in 2026 that covers all three dimensions this system needs in one pip install:

1. **RAG metrics** — Answer Relevancy, Faithfulness, Contextual Precision, Contextual Recall — identical to Ragas semantics but with better debugging output (score + reason per assertion).
2. **Agent metrics** — Tool Correctness, Task Completion, Step Efficiency, Argument Correctness, Plan Adherence. These are native; Ragas has zero agentic coverage.
3. **Multi-turn metrics** — Conversation Completeness, Knowledge Retention — critical for the NL multi-turn requirement in the PS.
4. **pytest-native CI gate** — `deepeval test run` integrates into any CI runner without rewriting test logic. Single command: `deepeval test run test_maintenance_wizard.py --exit-on-first-failure`.
5. **Local execution** — metrics run on-machine via LLM-as-judge calling a small judge model (configurable). No cloud dependency during offline eval.

The Confident AI comparison with Ragas (deepeval.com/blog/deepeval-vs-ragas) confirms: Ragas lacks explainability per metric (no per-assertion reasoning), lacks agentic workflow metrics, and offers no pytest integration. Ragas is better for data-science exploration notebooks; DeepEval is for engineering pipelines.

### Ragas v0.2+ — used as specialist supplement only

Ragas brings one unique thing: **`testset_generation`** — the knowledge-graph-based synthetic QA generation from your documents. For this hackathon (no real dataset, synthetic SOPs/manuals), Ragas's `generate_testset()` against your synthetic steel-plant documents produces 30-50 realistic QA pairs in minutes. This is faster than handwriting 50 golden cases. After generating, ingest into DeepEval test cases for execution.

Ragas's evolved testset generator (Evol-Instruct-style transformations) produces simple, multi-context, reasoning, and conditional queries — exactly the variety a judges' adversarial demo needs coverage on.

### Langfuse v3.x — observability layer

Langfuse (19K+ GitHub stars, MIT license, YC W23) is the only observability tool that is:
- Self-hostable in one command (`pip install langfuse` + local mode)
- Natively integrated with LangChain, LlamaIndex, raw OpenAI SDK
- Provides per-call breakdown: tokens in/out/cached, latency ms, cost $, eval score
- Shows this as a visual trace tree — exactly what judges see when you share screen

The LLM-as-a-Judge execution tracing feature (released 2025-10-16) links every evaluator run back to its source trace, so the judge can inspect "why did this get a 0.8 faithfulness score" in real time.

### Circuit Breaker + Cached Gold Responses — demo crash prevention

Production evidence (from gitplumbers.com): after implementing circuit breaker + fallback: p95 latency dropped 8.4s → 3.1s, fallback rate stabilized <6%, MTTR from 47m → 9m. For a hackathon, the goal is simpler: zero crashes in a 10-minute demo.

Pattern: wrap every LLM call with a `tenacity`-based retry (3 attempts, exponential backoff) + a circuit breaker that trips after 2 consecutive failures and serves a pre-cached gold response for the 3 most common demo queries. This means even an OpenAI outage (the largest occurred June 2025, 34 hours) cannot crash a demo that has good fallback design.

### OWASP LLM 2025 Guardrails — mandatory for industrial safety

OWASP LLM01:2025 (Prompt Injection) and LLM09:2025 (Misinformation) are the two risks that would be catastrophically bad in a steel-plant maintenance context — wrong repair advice could imply physical danger. Judges at industrial hackathons notice when a system gives confident wrong answers. Input/output validators (NeMo Guardrails or a lightweight custom filter) catch:
- Out-of-domain queries (e.g., someone types "write me a poem" during demo)
- Hallucinated part numbers or torque specs without a retrieved source
- Responses that lack a citation when they should have one

---

## 3. Exact Stack

| Library / Tool | Version | Role |
|---|---|---|
| `deepeval` | 4.0.5 (May 2026) | Primary eval harness: RAG + agent + multi-turn metrics, pytest CI gate |
| `ragas` | 0.2.x (stable) | Synthetic testset generation from synthetic steel-plant docs; supplement for RAG metric double-check |
| `langfuse` | 3.x | Live observability: trace every LLM call, token/cost/latency breakdown, eval score overlay for demo |
| `tenacity` | 9.x | Retry logic (3 attempts, exponential backoff) wrapping every LLM call |
| `pytest` | 8.x | Test runner; DeepEval integrates natively via `deepeval test run` |
| `pydantic` | 2.x | Output schema validation — every LLM output is parsed into a typed model before serving |
| NeMo Guardrails OR custom validator | 0.11.x / custom | Input classification (in-domain check) + output citation-presence check |
| `time` / `statistics` (stdlib) | stdlib | P50/P95/P99 latency tracking per endpoint — no extra dep |
| `prometheus_client` (optional) | 0.21.x | If a local Prometheus instance is shown in demo for real-time latency dashboard |

All installable via `pip`. No Docker required. CPU-friendly — DeepEval's LLM-as-judge uses the same API your system already calls; no local GPU model needed for eval.

---

## 4. Alternatives Considered — Why They Lost

### Alternative A: Ragas as primary eval (not just testset generation)

Ragas covers RAG metrics well (Faithfulness, Context Precision, Context Recall, Noise Sensitivity). **Why it loses:** Zero coverage for tool-call correctness and agent trajectory, which is half of what this system does. The PS explicitly requires "effective use of agentic AI frameworks" — if your eval suite doesn't test agent behavior, judges see a gap. Ragas also has no pytest CI integration (data-science API, not engineering API). Keep it as a supplementary testset generator only.

### Alternative B: Promptfoo as primary eval

Promptfoo (used by OpenAI and Anthropic) is excellent for prompt regression testing and red-teaming. **Why it loses:** Its strength is adversarial/red-team scenarios and prompt A/B comparison — not production metrics across an agentic RAG pipeline. It requires a YAML config for each test, which is less composable than pytest test cases for a solo builder with 9 days. Better used as a one-off red-team sweep (run once before submission) than as the primary harness.

### Alternative C: Anthropic Inspect (Inspect AI)

UK AISI's Inspect framework is the new gold standard for LLM safety evaluations and government-level AI auditing. **Why it loses:** Designed for capability and safety research benchmarks, not production agentic pipelines. The solver/task architecture is powerful but has more boilerplate than DeepEval for custom metrics. Appropriate if you were fine-tuning and needed standardized capability evals; overkill for a 9-day hackathon.

### Alternative D: Custom scoring scripts only (no framework)

Some teams hand-roll BLEU/ROUGE + custom substring checks. **Why it loses:** BLEU/ROUGE are notoriously bad at measuring LLM answer quality — they penalize paraphrase, which LLMs do by design. Hand-rolled scripts also have no standard test-report format to show judges, no CI integration story, and no explainability per assertion. This is the 2022-tier anti-pattern.

---

## 5. Anti-Patterns — What Screams "Amateur / 2022-tier"

1. **BLEU/ROUGE as primary eval metrics.** These are n-gram overlap metrics designed for machine translation in 2002. Using them for LLM faithfulness evaluation in 2026 signals unfamiliarity with the field.

2. **"We'll evaluate after the demo."** Any submission without a pre-run eval suite is a vibes-based submission. Judges who understand AI engineering immediately ask "how did you measure accuracy?"

3. **Eval only on the happy path.** Testing exclusively on queries your system was designed for, with no adversarial cases, edge cases, or out-of-domain rejection tests.

4. **No latency SLOs.** Saying "it's fast" with no numbers. The operational qualities require you to measure and show: P50 < 2s for RAG queries, P95 < 5s. If you can't show a histogram, it's not real.

5. **No source citation in outputs.** Generating maintenance recommendations with no traceability to the retrieved chunk / manual section. This violates PS Requirement 4 (Explainable + Traceable) and is detectable by judges during live demo.

6. **Using LLM-as-judge with GPT-4o evaluating GPT-4o outputs (same-model judge).** Self-preference bias invalidates scores. Either use a different model as judge (e.g., Claude as judge for GPT outputs or vice versa) or use reference-based metrics (FactScore-style) where the claim is checked against the retrieved document directly.

7. **No graceful degradation plan.** A crash during the live demo is a hard negative signal. Any system that hasn't been smoke-tested with a cold start on a fresh machine is a risk.

8. **Manual only "eval."** Showing a human-judged scorecard without any automated metric is not sufficient. The judges expect at least some programmatic rigor.

---

## 6. Integration Notes

### Inputs Consumed

- **From RAG pipeline (Component ~5-8):** retrieved chunks + generated answers for RAG metrics (Faithfulness, Contextual Precision/Recall)
- **From agent orchestrator (Component ~10-15):** agent traces — sequence of tool calls, arguments, outputs — for Tool Correctness and Step Efficiency metrics
- **From multi-turn chat handler:** conversation history for Conversation Completeness and Knowledge Retention
- **From anomaly/RUL prediction module:** predicted labels vs. known golden labels for standard ML metrics (F1, RMSE, MAE for RUL)
- **From synthetic data generator:** generated QA pairs for golden set bootstrapping

### Outputs Produced

- **Pass/fail eval report** — `deepeval test run` JSON report, shown in console + optionally pushed to Langfuse dataset runs
- **Metric scores per test case** — Faithfulness ∈ [0,1], Contextual Precision ∈ [0,1], Tool Correctness ∈ {0,1}, Task Completion ∈ [0,1], P50/P95 latency per query type
- **Live Langfuse dashboard** — shown during demo: real-time trace tree with token breakdown, latency histogram, eval score overlays
- **Eval summary for design doc** — a human-readable table of metric thresholds + actual scores goes into the required submission document
- **Guardrail verdict** — PASS (in-domain, citation present, safe) or BLOCK (out-of-domain, no citation, flagged) per response — surfaced in the UI as a small indicator

### Components It Talks To

| Component | Integration Point |
|---|---|
| LLM Gateway / API wrapper | Langfuse SDK wraps every `client.chat.completions.create()` call; zero code change beyond `Langfuse()` init |
| RAG retriever | Passes `(query, retrieved_chunks, generated_answer)` tuple to DeepEval `LLMTestCase` |
| Agent orchestrator | Passes tool call log as `tool_calls` list to DeepEval's `ToolCorrectnessMetric` |
| Anomaly/RUL model | sklearn-style `classification_report` / `mean_absolute_error` — no special framework needed |
| Frontend / demo UI | Langfuse trace URL surfaced as a "Debug trace" link in the UI for judge inspection |
| Feedback loop | Thumbs up/down feedback from engineer → stored as Langfuse score annotation → used to tag low-scoring traces for review |

---

## 7. Open Risks / Unknowns

1. **LLM-as-judge API cost during offline eval.** Running 50-100 test cases through DeepEval calls the judge LLM N×M times (one per assertion). At GPT-4o-mini prices (~$0.15/1M input tokens) this is negligible, but if the judge is a large model, costs add up. Mitigate: use a cheap judge model (GPT-4o-mini or Claude Haiku) and cache eval results with `deepeval`'s built-in caching.

2. **Langfuse local mode stability.** Langfuse in "local mode" (no server, file-based) is not as battle-tested as the hosted version. [unverified: whether Langfuse 3.x local mode fully supports all dashboard features without a running server.] Mitigation: spin up a lightweight Langfuse instance via `langfuse-lite` or simply log to a local SQLite + display formatted console output if the full dashboard fails.

3. **DeepEval's LLM-as-judge judge-bias.** Faithfulness scores from LLM judges can vary 10-15% depending on prompt phrasing and model temperature. The 2025 CCRS paper (arxiv 2506.20128) shows zero-shot LLM judges systematically inflate scores on verbose outputs. Mitigate: pin judge temperature to 0, use low-temperature DeepEval defaults, and calibrate against 5 hand-labeled cases to confirm scores are directionally correct.

4. **Ragas testset quality on synthetic steel-plant text.** Ragas testset generation uses the knowledge graph to create multi-hop questions. Quality degrades on short/repetitive documents. [unverified: exact behavior on synthetic steel-plant SOPs of 500-1000 words each.] Mitigation: generate 2x the needed test cases, manually review and discard low-quality ones, keep the best 50.

5. **Circuit breaker state during demo.** If the demo starts in a degraded state (breaker tripped from a previous test run), all queries serve cached fallbacks. Implement a `reset_circuit_breaker()` call in the demo startup script.

6. **Tool Correctness metric requires ground-truth tool sequence.** For agent eval, you need a labeled "expected tool sequence" per test case. For a hackathon, this means manually writing 15-20 agent trajectory golden cases. Not hard, but takes 2-3 hours and is often skipped. Skipping it means your agent eval is incomplete.

7. **RMSE for RUL on C-MAPSS data.** The standard benchmark RMSE on C-MAPSS FD001 is 12-15 cycles for deep learning models. If your model significantly exceeds this (RMSE > 30), the anomaly/prediction component will be the weakest link in the eval story. Mitigate with a piecewise linear RUL target (cap at 125 cycles) — this is the standard literature practice and substantially improves RMSE.

---

## Quick-Start Implementation Plan (solo, 9 days)

```
Day 1-2 (data + RAG pipeline):
  - ragas.testset.generate() on synthetic steel-plant docs → 80 QA pairs
  - Keep 50 as golden set (manual review pass)

Day 3-5 (core system build):
  - Langfuse init in LLM gateway (3 lines of code)
  - Pydantic output schemas for all response types

Day 6-7 (eval harness):
  - Write test_maintenance_wizard.py with DeepEval assertions
  - Run: deepeval test run test_maintenance_wizard.py
  - Fix anything below threshold (Faithfulness < 0.8, Tool Correctness < 0.9)

Day 8 (hardening):
  - Add circuit breaker around LLM calls (tenacity)
  - Pre-cache 5 gold demo responses
  - Add input validator (domain check: "is this a maintenance query?")
  - Cold-start test on a clean venv

Day 9 (polish):
  - Screenshot Langfuse trace for design doc
  - Run full eval suite one final time, capture scores
  - Embed scores table in design doc
  - Record screen recording showing eval panel + live trace
```

### Recommended Metric Thresholds (gate for submission)

| Metric | Tool | Threshold |
|---|---|---|
| Faithfulness | DeepEval | ≥ 0.80 |
| Contextual Precision | DeepEval | ≥ 0.75 |
| Contextual Recall | DeepEval | ≥ 0.70 |
| Tool Correctness | DeepEval | ≥ 0.90 |
| Task Completion | DeepEval | ≥ 0.85 |
| RUL RMSE (C-MAPSS FD001) | sklearn | ≤ 25 cycles |
| Anomaly Detection F1 | sklearn | ≥ 0.80 |
| P50 query latency | stdlib timer | ≤ 2.5s |
| P95 query latency | stdlib timer | ≤ 6.0s |
| Demo crash rate (10 cold runs) | manual | 0 / 10 |

---

*Research complete. Stack is pip-installable, CPU-friendly, solo-buildable in 9 days, and directly addresses all 6 judging criteria plus the 7 operational qualities.*
