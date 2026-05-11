# Pricing Strategist — Jarvis-Picked Agent Prompt

> Selected 2026-05-11 from 5 candidates in `../agent-prompts/pricing-strategist.md`
> Picker: prompt-picker-agent | Criteria: output quality + 2026 trend relevance + deployability

---

## Selected Prompt

**Original name:** Value-Based Price Point Calculator
**From library:** `data/agent-prompts/pricing-strategist.md` → Prompt 2
**Source:** [Medium — 10 ChatGPT Prompts for Pricing Strategy (Shushant Lakhyani)](https://medium.com/@slakhyani20/10-chatgpt-prompts-for-pricing-strategy-creation-8ecb05e47d68)
**Author:** Shushant Lakhyani
**License:** Medium article (cite + adapt)

### Full Prompt (verbatim)

```
You are a value-based pricing consultant. Calculate the optimal price
point for [PRODUCT] based on the value delivered, not on cost.

Step 1: Quantify customer benefit. List every measurable outcome our
product creates for a typical customer per month / per year. Convert
each to dollars (or flag "NEEDS DATA").

Step 2: Sum the gross value created.

Step 3: Apply a value-capture rule of thumb. For B2B SaaS, capture 10-30%
of measurable value created (state where in that band this product
should sit and why).

Step 4: Compute price range — the low end (10% capture), midpoint, and
high end (30% capture). Convert to monthly / annual / per-seat as
relevant.

Step 5: Sanity-check against:
  - Competitive prices (paste if I provided them)
  - Cost to serve (must leave a healthy gross margin)
  - The "no-brainer" test: is the price obviously low compared to value?

Output: recommended price, why, and the assumption that would change
the answer most if it's wrong.

Customer value inputs:
[PASTE — time saved, revenue gained, cost avoided, risk reduced, with
hours/$ values per customer]
```

---

## Why Jarvis Picked This

### Output quality drivers
- **Role priming:** Value-based pricing consultant — explicitly anti-cost-plus.
- **Scope boundaries:** 5 numbered steps; closed-set value categories (time, revenue, cost, risk).
- **Output format:** Step-by-step calculation → recommended price + the assumption-most-likely-wrong (sensitivity analysis).
- **Reasoning techniques:** Forces value quantification → capture-rule → sanity check. Multi-step CoT with NEEDS DATA flags.
- **Safety / refusal patterns:** NEEDS DATA pattern prevents fabricated pricing; library-level guardrail rejects hidden fees / auto-renew traps / misleading anchors.
- **Examples / few-shot:** Capture-rule heuristic (10-30%) inline.

### 2026 trend relevance
- **Modern frameworks:** Value-based pricing is the dominant 2026 SaaS pricing pattern; cost-plus is widely rejected.
- **Current tech references:** Per-seat / per-usage / per-outcome adaptability.
- **Structured output:** Auditable calculation flow.
- **Safety alignment:** Sensitivity analysis (the assumption-most-wrong) is intellectually honest — distinguishes the prompt from confidence-theater AI outputs.

### Deployability
- **License:** Medium article — cite Lakhyani on reuse.
- **Vendor lock:** None.
- **Jarvis adaptability:** Pairs naturally with Three-Tier Architect (Prompt 1) for downstream tier design.

---

## Runners-up + Trade-offs

### #2: Three-Tier Pricing Architect (Prompt 1)
- **Why not picked:** Excellent tier design but requires value-based price established first. Use AFTER Prompt 2.
- **When to use this instead:** SaaS product graduating from single plan to tiered.

### #3: Willingness-to-Pay Persona Map (Prompt 3)
- **Why not picked:** Persona-driven WTP map; complement to value-based price.
- **When to use this instead:** Before launching new SKU or entering new segment.

### #4: Discount Governance Policy (Prompt 4)
- **Why not picked:** Operational policy, not pricing strategy. Specialized downstream artifact.
- **When to use this instead:** When AE team is asking for ad-hoc discount approval more than weekly.

### #5: Price Experiment Design (Prompt 5)
- **Why not picked:** A/B test design; requires high traffic. Different workflow.
- **When to use this instead:** Validating a price change at 10k+ monthly pricing-page visitors.

---

## Deployment Notes for Jarvis

1. **File path:** `.claude/agents/pricing-strategist-agent.md`
2. **Adaptations needed:**
   - Carry library-level ethics guardrail: REJECT hidden fees, auto-renew traps, anchoring designed to mislead.
   - Reinforce NEEDS DATA pattern with Jarvis's never-fabricate directive.
   - For consumer pricing, adjust value-capture heuristic (10-30% is B2B; B2C is much lower).
3. **Tool access (suggested):** Read access to product memory; research-agent for competitor price verification; no autonomous pricing-page changes.
4. **Model recommendation:** sonnet (numeric reasoning + structured output); opus for repricing decisions worth $1M+ ARR.

---

## Scorecard

| Criterion | Score (1-5) | Notes |
|-----------|-------------|-------|
| Role priming clarity | 5/5 | Value-based consultant, anti-cost-plus |
| Scope boundaries | 5/5 | 5 steps, closed-set categories |
| Output format guidance | 5/5 | Step-flow + sensitivity analysis |
| Reasoning techniques | 5/5 | Multi-step CoT with NEEDS DATA flag |
| Safety / refusal patterns | 4/5 | NEEDS DATA + library guardrails |
| 2026 tech relevance | 5/5 | Value-based pricing dominant in 2026 SaaS |
| License-friendliness | 4/5 | Cite Lakhyani on reuse |
| **Overall** | **33/35** | Highest-leverage pricing shift for B2B SaaS |
