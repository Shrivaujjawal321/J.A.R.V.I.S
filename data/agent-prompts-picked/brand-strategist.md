# Brand Strategist — Jarvis-Picked Agent Prompt

> Selected 2026-05-11 from 4 candidates in `../agent-prompts/brand-strategist.md`
> Picker: prompt-picker-agent | Criteria: output quality + 2026 trend relevance + deployability

---

## Selected Prompt

**Original name:** Brand Positioning Strategist
**From library:** `data/agent-prompts/brand-strategist.md` -> Prompt 3
**Source:** Composite — based on the [Geoffrey Moore positioning template](https://en.wikipedia.org/wiki/Crossing_the_Chasm) and [ClickUp branding prompts](https://clickup.com/templates/ai-prompts/branding-and-positioning)
**Author:** Composite original
**License:** Composite original prompt; framework based on industry-standard positioning canon

### Full Prompt (verbatim)

```
You are a brand positioning strategist trained in the Geoffrey Moore positioning framework and Al Ries / Jack Trout positioning theory.

Given a brand brief, produce:

1. POSITIONING STATEMENT (Moore template)
   "For [target customer]
    who [statement of need or opportunity],
    [product/brand name] is a [product category]
    that [statement of key benefit / compelling reason to buy].
    Unlike [primary competitive alternative],
    [statement of primary differentiation]."

   Produce 3 variants exploring different categories the brand could occupy (e.g., the same product could be positioned as "the X for Y" or "the anti-X" or "the premium version of Z"). Explain the tradeoffs.

2. CATEGORY DESIGN
   - What category is this brand entering vs. creating?
   - If creating: what is the category name, and who is excluded by it?
   - If entering: who is the current category king, and how does this brand reframe?

3. MESSAGING PILLARS (3-5 pillars)
   For each pillar: name, one-sentence claim, proof points, and a customer-facing tagline option.

4. COMPETITIVE LANDSCAPE TABLE
   | Competitor | Positioning | Strengths | Weaknesses | How we win against them |

5. RISK FLAGS
   - Positioning claims that are not yet defensible (need product proof)
   - Audiences this positioning *excludes* — is that intended?
   - Likely competitor counter-moves
```

---

## Why Jarvis Picked This

### Output quality drivers
- **Role priming:** "Brand positioning strategist" + named canon (Geoffrey Moore, Ries/Trout) — narrow seniority and methodology.
- **Scope boundaries:** Five mandatory output sections; strategic only (no logo/color noise).
- **Output format:** Pinned Moore-template fill-in + table + bullet structure.
- **Reasoning techniques:** Three positioning variants force option-thinking. Category design forces enter-vs-create thinking. Risk flags force adversarial thinking.
- **Safety / refusal patterns:** Risk flags include "claims not yet defensible" — explicit anti-fabrication. "Audiences this excludes" surfaces unintended impact.
- **Examples / few-shot:** Inline category-framing examples ("the X for Y", "the anti-X", "the premium version of Z").

### 2026 trend relevance
- **Modern frameworks:** Geoffrey Moore positioning is still the canon for B2B/SaaS in 2026. Ries/Trout positioning theory remains the consumer-brand reference.
- **Current tech references:** Aligns with Boss's hackathon/AI-developer context — positioning matters for pitch decks and project narratives.
- **Structured output:** Composes with messaging pillar -> copywriter handoff, competitor table -> research-agent handoff.
- **Safety alignment:** Anti-fabrication on defensibility; exclusion-awareness on positioning.

### Deployability
- **License:** Composite original — unrestricted for Jarvis.
- **Vendor lock:** None.
- **Jarvis adaptability:** High. Chains with brand-builder (full identity), brand voice chart, and ghostwriter for the copy execution layer.

---

## Runners-up + Trade-offs

### #2: Brand Builder (Anthropic, Prompt 1)
- **Why not picked:** Anthropic-published holistic brief covering name, logo direction, color, typography, voice — but single-shot and missing the strategic positioning foundation. Use after positioning lands.
- **When to use this instead:** Greenfield identity work once positioning is settled.

### #3: Brand Voice Chart Builder (Prompt 2)
- Excellent operational voice document. Wire as `brand-voice` sibling agent once positioning is locked.

---

## Deployment Notes for Jarvis

1. **File path:** `.claude/agents/brand-strategist.md`
2. **Adaptations needed:**
   - Wire `research-agent` for competitive landscape data before producing the table.
   - Add Boss-specific use case: positioning Jarvis itself, hackathon project pitches, personal-brand positioning.
   - Add an "Indian market context" flag — naming, category-king dynamics differ from US/Western markets.
3. **Tool access (suggested):** WebSearch / WebFetch (competitive intel), Read (project memory), Write (brand brief to `data/notes/`).
4. **Model recommendation:** opus (best for strategic nuance and variant exploration); sonnet for follow-on iterations.

---

## Scorecard

| Criterion | Score (1-5) | Notes |
|-----------|-------------|-------|
| Role priming clarity | 5/5 | Positioning strategist + named canon. |
| Scope boundaries | 5/5 | Five mandatory outputs; strategic only. |
| Output format guidance | 5/5 | Moore template + table + pillars. |
| Reasoning techniques | 5/5 | Three variants + category design + risk flags. |
| Safety / refusal patterns | 4/5 | Anti-fabrication on defensibility. |
| 2026 tech relevance | 4/5 | Canonical 2024+ B2B/consumer framework. |
| License-friendliness | 5/5 | Composite original. |
| **Overall** | **33/35** | |
