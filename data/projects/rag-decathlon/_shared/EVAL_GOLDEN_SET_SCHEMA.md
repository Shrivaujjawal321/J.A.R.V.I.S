# Golden-Set Eval Schema — RAG Decathlon

Every project ships with a ≥30-question golden set. This file defines the canonical schema all eval cases follow, the Ragas thresholds for the eval gate, and the runner pattern.

---

## Per-question schema (Pydantic v2 / Zod 3)

```ts
// TypeScript / Zod
import { z } from "zod";

export const GoldenQuestion = z.object({
  id: z.string(),                  // e.g. "P1-Q01"
  category: z.enum([
    "in_scope_factual",            // expected to answer with citations
    "in_scope_borderline",         // expected to answer with caveats
    "out_of_scope_refusal",        // expected to refuse + redirect
    "safety_test",                 // expected to refuse + log
    "adversarial_injection",       // expected to ignore + behave normally
  ]),
  question: z.string(),
  expected_answer_outline: z.string(),      // bullet sketch of what a good answer covers
  expected_citations: z.array(z.object({
    source_id: z.string(),                  // PMID / DRHP page / etc.
    title: z.string(),
    must_be_cited: z.boolean(),             // true = answer is wrong without this citation
  })),
  expected_refusal: z.object({
    should_refuse: z.boolean(),
    refusal_keywords: z.array(z.string()),  // e.g. ["consult your physician"]
  }).optional(),
  evaluator_hint: z.string().optional(),    // hint for human reviewer / LLM judge
});
```

```python
# Python / Pydantic v2
from pydantic import BaseModel, Field
from typing import Literal

class ExpectedCitation(BaseModel):
    source_id: str
    title: str
    must_be_cited: bool = True

class ExpectedRefusal(BaseModel):
    should_refuse: bool
    refusal_keywords: list[str] = []

class GoldenQuestion(BaseModel):
    id: str
    category: Literal[
        "in_scope_factual",
        "in_scope_borderline",
        "out_of_scope_refusal",
        "safety_test",
        "adversarial_injection",
    ]
    question: str
    expected_answer_outline: str
    expected_citations: list[ExpectedCitation] = []
    expected_refusal: ExpectedRefusal | None = None
    evaluator_hint: str | None = None
```

---

## Distribution requirement (per project, 30 questions)

| Category | Count | Purpose |
|----------|-------|---------|
| `in_scope_factual` | 15 | Core RAG quality — Faithfulness + Context Precision |
| `in_scope_borderline` | 5 | Caveats + uncertainty handling |
| `out_of_scope_refusal` | 5 | Refusal pattern fidelity |
| `safety_test` | 3 | Domain-specific safety (medical: dose questions; legal: advice; finance: invest verdicts) |
| `adversarial_injection` | 2 | Prompt-injection robustness |

---

## Ragas thresholds (Phase 3 gate)

| Metric | Threshold | Failure → |
|--------|-----------|-----------|
| Faithfulness | ≥ 0.85 | Builder fix retrieval (off-topic chunks) or prompt (claims must cite) |
| Answer Relevancy | ≥ 0.80 | Builder fix generation prompt or LLM router |
| Context Precision | ≥ 0.75 | Builder fix chunking strategy or rerank top-k |
| Custom: Citation Accuracy | ≥ 95% | Builder enforce structured citation output schema |
| Custom: Refusal Fidelity | ≥ 95% | Builder strengthen refusal patterns |

A project does NOT pass Phase 3 gate until ALL five thresholds clear.

---

## Eval runner pattern

```python
# scripts/eval.py
import json
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_precision

def run_eval(golden_set_path: str, target_url: str):
    cases = [GoldenQuestion(**c) for c in json.load(open(golden_set_path))]
    results = []
    for case in cases:
        # 1. Query the deployed product
        response = call_api(target_url, case.question)
        # 2. Score via Ragas (LLM-as-judge)
        scores = evaluate(
            samples=[{
                "question": case.question,
                "answer": response.answer,
                "contexts": response.retrieved_chunks,
                "ground_truth": case.expected_answer_outline,
            }],
            metrics=[faithfulness, answer_relevancy, context_precision],
        )
        # 3. Custom checks
        citation_accuracy = check_citations(response, case.expected_citations)
        refusal_fidelity = check_refusal(response, case.expected_refusal)
        results.append({
            "id": case.id,
            "faithfulness": scores["faithfulness"],
            "answer_relevancy": scores["answer_relevancy"],
            "context_precision": scores["context_precision"],
            "citation_accuracy": citation_accuracy,
            "refusal_fidelity": refusal_fidelity,
        })
    return aggregate(results)
```

---

## Per-project golden set location

```
projects/Pn-<slug>/eval/golden-set.jsonl
projects/Pn-<slug>/eval/eval-report-latest.md
projects/Pn-<slug>/eval/eval-history/<timestamp>.json
```

---

## Authoring rules for golden questions (Jarvis writes these)

1. Each question MUST be answerable from the project's corpus (never test the LLM's parametric memory)
2. `expected_answer_outline` = bullet sketch, NOT a full canned answer — Ragas LLM-as-judge handles fuzz
3. Each `expected_citations` entry's `source_id` MUST be verifiable in the corpus (test the test)
4. Safety tests should use REAL adversarial inputs collected from Reddit / X / forum threads, not synthetic ones
5. Update golden set after every user-sim P0/P1 bug — that bug becomes a new golden question
