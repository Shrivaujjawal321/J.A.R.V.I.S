# Statistician — Jarvis-Picked Agent Prompt

> Selected 2026-05-11 from 4 candidates in `../agent-prompts/statistician.md`
> Picker: prompt-picker-agent | Criteria: output quality + 2026 trend relevance + deployability

---

## Selected Prompt

**Original name:** Rigorous A/B Test Architect (Extended)
**From library:** `data/agent-prompts/statistician.md` -> Prompt 3
**Source:** Industry-extended formulation per [LearnPrompt data-science prompts](https://learnprompt.org/chat-gpt-prompts-for-data-science/)
**Author:** Composite (LearnPrompt curation)
**License:** Public web reference

### Full Prompt (verbatim)

```
Act as a statistician. I want to test the hypothesis that [HYPOTHESIS]. Please help design an A/B test. Include:

1. Key metrics to track (primary and secondary, and any guardrail metrics).
2. How to calculate the required sample size — assume desired power of 80%, significance level alpha = 0.05, and minimum detectable effect of [MDE, e.g., 2% relative uplift]. State the baseline rate or mean and the assumed standard deviation. Show the formula and the resulting n per arm.
3. The statistical test to use for comparing results (e.g., two-proportion z-test, Welch's t-test, chi-squared, Mann-Whitney) and WHY that test fits the data type and assumptions.
4. How long to run the test, given expected traffic of [TRAFFIC PER DAY], and any rules to avoid peeking or sequential-testing inflation.
5. How to interpret the results: confidence interval, effect size, practical significance vs. statistical significance, and what would trigger a ship / no-ship / iterate decision.
6. List the top 3 assumptions and what would invalidate the analysis.
```

---

## Why Jarvis Picked This

### Output quality drivers
- **Role priming:** "Statistician" with operational context (A/B test design).
- **Scope boundaries:** Six numbered requirements; each is concrete and verifiable.
- **Output format:** Six-section structured response — every section is operationally actionable.
- **Reasoning techniques:** Forces sample-size math (power + alpha + MDE), test-choice justification, and assumption-listing.
- **Safety / refusal patterns:** Built-in assumption-flagging in step 6 — surfaces failure modes before analysis.

### 2026 trend relevance
- **Modern frameworks:** Power analysis, MDE, guardrail metrics — all 2026 industry standard.
- **Current tech references:** Test menu (z-test, Welch's, chi-sq, Mann-Whitney) is current and complete.
- **Structured output:** Six pinned sections.
- **Safety alignment:** Top-3 invalidating assumptions in every output prevents over-claiming.

### Deployability
- **License:** Public web — usable.
- **Vendor lock:** None.
- **Jarvis adaptability:** Drop in. Pair with data-analyst's A/B Test Analyzer (data-analyst Prompt 6) for post-experiment analysis.

---

## Runners-up + Trade-offs

### #2: Statistical Test Picker (Prompt 4)
- **Why not picked:** Narrower — only test selection, not full experiment design.
- **When to use this instead:** When you have data and just need to choose the right test.

### #3: Foundational Statistician (Prompt 1, awesome-chatgpt-prompts)
- **Why not picked:** Too thin — no structured output. Good for general Q&A but doesn't force rigor.
- **When to use this instead:** Quick definition lookups, terminology checks.

---

## Deployment Notes for Jarvis

1. **File path:** `.claude/agents/statistician.md`
2. **Adaptations needed:** Add explicit "if you cannot compute sample size from inputs, ask one clarifying question" clause. Add reminder for multi-arm / multivariate cases. Link to A/B Test Analyzer for post-experiment work.
3. **Tool access (suggested):** Read, Write, Bash (for Python/R stats computation if available).
4. **Model recommendation:** sonnet — opus for Bayesian power analysis.

---

## Scorecard

| Criterion | Score (1-5) | Notes |
|-----------|-------------|-------|
| Role priming clarity | 4/5 | Role clear; could be more specific (applied statistician). |
| Scope boundaries | 5/5 | Six numbered requirements. |
| Output format guidance | 5/5 | Pinned six sections. |
| Reasoning techniques | 5/5 | Forces sample-size math + test justification. |
| Safety / refusal patterns | 4/5 | Assumption-flagging; could add explicit refusal for under-specified inputs. |
| 2026 tech relevance | 4/5 | Strong; minor opportunity for sequential testing / Bayesian alternative. |
| License-friendliness | 3/5 | Public web (verify). |
| **Overall** | **30/35** | Solid working prompt. |
