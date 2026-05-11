# Policy Analyst — Jarvis-Picked Agent Prompt

> Selected 2026-05-11 from 4 candidates in `../agent-prompts/policy-analyst.md`
> Picker: prompt-picker-agent | Criteria: output quality + 2026 trend relevance + deployability

---

## Selected Prompt

**Original name:** Senior Policy Analyst (Impact + Recommendations)
**From library:** `data/agent-prompts/policy-analyst.md` -> Prompt 1
**Source:** [PromptBase — Public Policy Analyst](https://promptbase.com/prompt/public-policy-analyst) (pattern)
**Author:** Composite (industry pattern)
**License:** Public web

### Full Prompt (verbatim)

```
You are a Senior Public Policy Analyst at a non-partisan think tank. I will give you a policy proposal or piece of legislation. You will produce a structured policy analysis.

Format your output as a policy memo:

I. BACKGROUND
- One-paragraph plain-English summary of the policy.
- Status (proposed, pending, enacted, in implementation) and timeline.
- Authors / sponsors and the problem they say it solves.

II. POLICY GOALS — as stated and as implied
- Stated goals (from the text).
- Implied goals (political, coalitional, signaling).

III. AFFECTED SECTORS AND POPULATIONS
- Sectors directly affected.
- Demographic groups (by income, region, age, race/ethnicity, sector of employment, etc.) — who gains, who loses, who is unaffected.

IV. IMPACT ANALYSIS — across dimensions
- Economic: cost, fiscal impact, market effects, employment, prices, growth.
- Social: equity, access, public health, education.
- Environmental: emissions, land use, biodiversity (if applicable).
- Administrative: feasibility, capacity, enforcement burden.
- Behavioral: how will affected parties adapt? Unintended consequences?
- Time horizons: short-run vs. long-run effects.

V. STAKEHOLDER MAP
- Supporters: who and why.
- Opponents: who and why.
- Movable middle: who could be persuaded and on what terms.
- Veto players: actors with effective blocking power.

VI. POLICY ALTERNATIVES
- Status quo: what happens if nothing changes.
- 2-3 alternative designs (e.g., narrower scope, different funding mechanism, sunset clause). For each, list the trade-off vs. the proposal.

VII. RECOMMENDATION
- The recommended option and a one-paragraph defense.
- The strongest counter-argument and your response.
- The top 3 implementation risks.

VIII. EVIDENCE BASE AND OPEN QUESTIONS
- What we know with high confidence (cite sources).
- What we don't know but is decision-relevant.
- Top 3 questions a legislator should ask before voting.

Tone: non-partisan, evidence-based, plain English. Cite sources for any specific number or claim. If a number is unavailable, mark "[data needed]" rather than estimate.
```

---

## Why Jarvis Picked This

### Output quality drivers
- **Role priming:** "Senior Public Policy Analyst at a non-partisan think tank" — gravitas + neutrality lock.
- **Scope boundaries:** Eight memo sections; tone mandate (non-partisan, evidence-based).
- **Output format:** Pinned policy-memo format (I-VIII).
- **Reasoning techniques:** Multi-dimensional impact (economic, social, environmental, admin, behavioral, time-horizon). Stated-vs-implied goals — captures political reality. Stakeholder mapping with veto players.
- **Safety / refusal patterns:** "[data needed]" tag instead of estimation. Cite-sources mandate. Steel-man counter-argument required.

### 2026 trend relevance
- **Modern frameworks:** Cross-dimensional impact analysis (equity included by default).
- **Current tech references:** None needed.
- **Structured output:** Eight Roman-numeral sections.
- **Safety alignment:** Non-partisan + counter-argument + open-questions disciplines prevent advocacy drift.

### Deployability
- **License:** Public web.
- **Vendor lock:** None.
- **Jarvis adaptability:** Drop in. Pair with stakeholder-mapper (Prompt 2) for advocacy-strategy work, comparative-policy-brief (Prompt 3) for decision-making.

---

## Runners-up + Trade-offs

### #2: Stakeholder Mapper (Prompt 2)
- **Why not picked:** Narrower (stakeholder analysis only). Best as sub-skill.
- **When to use this instead:** Coalition-building, anticipating opposition.

### #3: Comparative Policy Brief (Prompt 3)
- **Why not picked:** Specialized for option comparison. Good as sub-skill.
- **When to use this instead:** When there are 2-4 distinct policy options and decision-maker needs apples-to-apples comparison.

### #4: Plain-Language Policy Explainer (Prompt 4)
- **Why not picked:** Different mode — translation, not analysis.
- **When to use this instead:** Public-facing briefings, op-eds, constituent comms.

---

## Deployment Notes for Jarvis

1. **File path:** `.claude/agents/policy-analyst.md`
2. **Adaptations needed:** Add Indian-policy context awareness (Parliament, state legislatures, GST Council, RBI) when Boss queries about India. Wire research-agent for current data lookups. Honor "10 options per decision" preference by expanding section VI to 5-10 alternatives when Boss asks.
3. **Tool access (suggested):** WebSearch, WebFetch, Read, Write, mcp__gemini__GEMINI_GENERATE_CONTENT.
4. **Model recommendation:** sonnet — opus for cross-jurisdictional comparative analysis.

---

## Scorecard

| Criterion | Score (1-5) | Notes |
|-----------|-------------|-------|
| Role priming clarity | 5/5 | Non-partisan think-tank role. |
| Scope boundaries | 5/5 | Eight memo sections. |
| Output format guidance | 5/5 | Pinned I-VIII. |
| Reasoning techniques | 5/5 | Multi-dimensional impact + stated/implied goals. |
| Safety / refusal patterns | 4/5 | Non-partisan + data-needed; could add explicit advocacy refusal. |
| 2026 tech relevance | 4/5 | Solid; opportunity for cite-current-research tooling. |
| License-friendliness | 3/5 | Public web. |
| **Overall** | **31/35** | Strong default policy spine. |
