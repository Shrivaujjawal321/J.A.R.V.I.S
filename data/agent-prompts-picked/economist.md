# Economist — Jarvis-Picked Agent Prompt

> Selected 2026-05-11 from 4 candidates in `../agent-prompts/economist.md`
> Picker: prompt-picker-agent | Criteria: output quality + 2026 trend relevance + deployability

---

## Selected Prompt

**Original name:** Policy Impact Economist (with frameworks)
**From library:** `data/agent-prompts/economist.md` -> Prompt 2
**Source:** Composite based on [Jesse Lastunen — AI for Economists](https://sites.google.com/view/lastunen/ai-for-economists)
**Author:** Composite formulation
**License:** Public web reference

### Full Prompt (verbatim)

```
You are a senior policy economist. I will give you a policy proposal. You will analyze its likely economic impact.

For every analysis, you will:

1. Restate the policy in one sentence and identify the markets it directly affects.
2. Apply the relevant micro frameworks: supply/demand shift, elasticity (price and income), incidence (who bears the cost), externalities, market failure addressed, deadweight loss.
3. Identify first-order effects (direct, intended) and second-order effects (substitution, behavioral response, unintended consequences). Estimate direction and rough magnitude for each.
4. Distinguish short-run vs. long-run effects.
5. Identify the distributional impact: which groups gain, which lose, by income / region / sector.
6. Apply the relevant macro framing if applicable (fiscal multiplier, crowding out, monetary transmission, balance of payments).
7. List the top 3 empirical assumptions your analysis depends on, and what data would falsify your conclusion.
8. End with: "On balance, this policy is likely to [improve / worsen / be ambiguous for] aggregate welfare because [one-sentence reason]." Be honest if the sign is genuinely ambiguous.

Be neutral. Do not advocate. Do not soften unpopular conclusions.
```

---

## Why Jarvis Picked This

### Output quality drivers
- **Role priming:** "Senior policy economist" — specific seniority and domain.
- **Scope boundaries:** Eight numbered steps; analysis only, no advocacy.
- **Output format:** Pinned 8-section structure with mandatory closing verdict line.
- **Reasoning techniques:** Forces application of named economic frameworks (elasticity, incidence, deadweight loss, multiplier, crowding out). Separates first/second-order effects and short/long run.
- **Safety / refusal patterns:** "Be honest if the sign is ambiguous" + "do not soften unpopular conclusions" — anti-sycophancy. Top-3 falsifying assumptions in every output.

### 2026 trend relevance
- **Modern frameworks:** Canonical micro + macro toolkit; framework names current and complete.
- **Current tech references:** None needed.
- **Structured output:** Eight sections, mandatory verdict line.
- **Safety alignment:** Neutrality and falsifiability discipline. Excellent.

### Deployability
- **License:** Public web — usable.
- **Vendor lock:** None.
- **Jarvis adaptability:** Drop in. Pair with policy-analyst (sibling agent) for political analysis; with research-agent for current data.

---

## Runners-up + Trade-offs

### #2: Market & Sector Analyst (Prompt 3)
- **Why not picked:** More forecasting-oriented; less rigorous on frameworks.
- **When to use this instead:** Sector outlooks for investment/strategy decisions (note: pair with non-advice disclaimer per financial-analyst).

### #3: Plain-English Economic Explainer (Prompt 4)
- **Why not picked:** Different mode — translation, not analysis.
- **When to use this instead:** Briefing non-economist stakeholders.

---

## Deployment Notes for Jarvis

1. **File path:** `.claude/agents/economist.md`
2. **Adaptations needed:** Add an "if asked for personal investment advice, refuse and redirect" guard. Honor Hinglish register when Boss writes Hinglish. Add Indian-economy context awareness (RBI, GST, fiscal calendar) if relevant.
3. **Tool access (suggested):** WebSearch, WebFetch, Read, Write, mcp__gemini__GEMINI_GENERATE_CONTENT for data lookup.
4. **Model recommendation:** sonnet — opus for cross-disciplinary policy + macro analysis.

---

## Scorecard

| Criterion | Score (1-5) | Notes |
|-----------|-------------|-------|
| Role priming clarity | 5/5 | Senior policy economist scoped. |
| Scope boundaries | 5/5 | Eight steps, no advocacy. |
| Output format guidance | 5/5 | Pinned verdict line + sections. |
| Reasoning techniques | 5/5 | Full micro + macro toolkit. |
| Safety / refusal patterns | 4/5 | Anti-sycophancy; advice refusal could be added. |
| 2026 tech relevance | 4/5 | Solid framework set. |
| License-friendliness | 3/5 | Public web (verify). |
| **Overall** | **31/35** | Strong policy-economist scaffold. |
