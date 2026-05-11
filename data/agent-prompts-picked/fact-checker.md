# Fact-Checker — Jarvis-Picked Agent Prompt

> Selected 2026-05-11 from 4 candidates in `../agent-prompts/fact-checker.md`
> Picker: prompt-picker-agent | Criteria: output quality + 2026 trend relevance + deployability

---

## Selected Prompt

**Original name:** Chain-of-Verification Fact-Checker (Self-Interrogating)
**From library:** `data/agent-prompts/fact-checker.md` -> Prompt 2
**Source:** Composite per [The 4-Step Prompt That Forces ChatGPT to Fact-Check Itself](https://ai.plainenglish.io/the-4-step-prompt-that-forces-chatgpt-to-fact-check-itself-dd99d2c13554)
**Author:** Avijnan Chatterjee (pattern) / community
**License:** Public web article (pattern)

### Full Prompt (verbatim)

```
You are a Chain-of-Verification fact-checker. You operate in four strict phases. Do not skip a phase.

PHASE 1 — CLAIM EXTRACTION
Read the input text. List every factual claim as a numbered bullet. A "claim" is any assertion of fact, statistic, date, name, quote, or causal relationship. Exclude pure opinion.

PHASE 2 — VERIFICATION QUESTIONS
For each claim, generate 1-3 verification questions that, if answered, would confirm or refute the claim. Generate the questions WITHOUT looking back at the original text — write them independently.

PHASE 3 — INDEPENDENT ANSWERS
Answer each verification question using your best available knowledge or search. Cite sources where possible (publication, date, URL). If you cannot verify, mark UNVERIFIABLE — never guess.

PHASE 4 — REVISED REPORT
Produce a final report:
- Verified claims (keep as-is).
- Revised claims (with the correction and the source).
- Removed claims (claims that failed verification and have no defensible basis).
- A clean rewrite of the original text with all corrections applied.

At the end, include an Accuracy Table: Claim | Original | Verified Status (TRUE / FALSE / MIXED / UNVERIFIABLE) | Source.
```

---

## Why Jarvis Picked This

### Output quality drivers
- **Role priming:** Chain-of-Verification (CoVe) framing — research-backed hallucination-reduction technique.
- **Scope boundaries:** Four numbered phases, "do not skip a phase" hard rule.
- **Output format:** Four-phase artifact pipeline ending in Accuracy Table.
- **Reasoning techniques:** CoVe is the strongest known technique for self-checking factual output — model verifies each claim independently before final report. Forces independent question generation in Phase 2.
- **Safety / refusal patterns:** Explicit UNVERIFIABLE category; "never guess" rule; "claims that failed verification and have no defensible basis" -> removed.

### 2026 trend relevance
- **Modern frameworks:** CoVe is a 2024+ research-backed prompting technique; widely cited and benchmarked.
- **Current tech references:** Source citation discipline (publication, date, URL).
- **Structured output:** Four named phases + Accuracy Table.
- **Safety alignment:** Best in the library for catching LLM-generated hallucinations — explicitly designed for that purpose.

### Deployability
- **License:** Public web (pattern not exclusive).
- **Vendor lock:** None.
- **Jarvis adaptability:** Drop in. Pair with research-agent for source-finding in Phase 3. Critical for auditing other agents' output (e.g., research-analyst's notes).

---

## Runners-up + Trade-offs

### #2: Pulitzer Fact-Checker (Prompt 1)
- **Why not picked:** Balanced sourcing is excellent for politically sensitive claims, but doesn't include the independent-question technique that makes CoVe so effective at catching LLM hallucinations.
- **When to use this instead:** Politically or ideologically charged claims where source bias matters.

### #3: Quick Claim Triage (Prompt 3)
- **Why not picked:** Single-claim speed mode. Useful but doesn't beat CoVe for thoroughness.
- **When to use this instead:** Rapid one-claim checks in social-media or editorial workflow.

### #4: Document Audit (Prompt 4)
- **Why not picked:** Similar overall arc to CoVe but without the independent-question phase that's the secret sauce.
- **When to use this instead:** Full-document audits of long articles or AI essays.

---

## Deployment Notes for Jarvis

1. **File path:** `.claude/agents/fact-checker.md`
2. **Adaptations needed:** Add explicit instruction to use WebSearch in Phase 3. Add Hinglish-friendly clause. For Boss-curated content (his own drafts), default to gentle revision tone; for adversarial claims, default to neutral verdict tone.
3. **Tool access (suggested):** WebSearch (mandatory), WebFetch, Read, Write, mcp__gemini__GEMINI_GENERATE_CONTENT for source corroboration.
4. **Model recommendation:** sonnet — opus for high-stakes audits of long content.

---

## Scorecard

| Criterion | Score (1-5) | Notes |
|-----------|-------------|-------|
| Role priming clarity | 5/5 | Crisp CoVe role. |
| Scope boundaries | 5/5 | Four phases, no skip. |
| Output format guidance | 5/5 | Phases + Accuracy Table. |
| Reasoning techniques | 5/5 | CoVe is research-backed best practice. |
| Safety / refusal patterns | 5/5 | UNVERIFIABLE + never-guess. |
| 2026 tech relevance | 5/5 | CoVe is current SOTA for hallucination check. |
| License-friendliness | 4/5 | Public web pattern. |
| **Overall** | **34/35** | Best-in-class. |
