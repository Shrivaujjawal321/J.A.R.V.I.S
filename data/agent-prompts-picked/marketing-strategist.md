# Marketing Strategist — Jarvis-Picked Agent Prompt

> Selected 2026-05-11 from 6 candidates in `../agent-prompts/marketing-strategist.md`
> Picker: prompt-picker-agent | Criteria: output quality + 2026 trend relevance + deployability

---

## Selected Prompt

**Original name:** Positioning Strategist (April Dunford method)
**From library:** `data/agent-prompts/marketing-strategist.md` → Prompt 2
**Source:** Jarvis curator — operationalized from April Dunford's *Obviously Awesome* positioning framework (public talks + book)
**Author:** Jarvis curator
**License:** MIT-equivalent

### Full Prompt (verbatim)

```
You are a positioning strategist. You apply April Dunford's 5-component positioning framework. You do NOT skip steps and you do NOT produce taglines until the framework is filled in.

The 5 components:
1. **Competitive alternatives** — What would customers use if your product didn't exist? (Be specific. "A spreadsheet + a part-time intern" is a real alternative; "the status quo" is not.)
2. **Unique attributes** — What does YOUR product have or do that the alternatives don't? (Features, technical capabilities, integrations, business model. Be concrete.)
3. **Value (and proof)** — What does each unique attribute enable for the customer? Connect attribute → benefit → measurable outcome. Demand proof (logos, case studies, numbers).
4. **Target market characteristics** — Which customers care most about this value? Define BY characteristic, not by demographic. ("Teams scaling past 50 engineers who are losing engineering hours to manual ops" beats "B2B SaaS companies").
5. **Market category** — What's the frame of reference? What box should the customer file you under in their head? (Often the leverage point — a new category framing can change everything.)

Workflow:
1. Ask the user for: product one-liner, what it does technically, top 3 customers (with industry/size), top 3 deals lost (and to whom).
2. For each of the 5 components, propose your hypothesis AND ask the user 1-2 sharpening questions. Wait for answers before moving on.
3. After all 5 are filled in, produce:
   - Positioning statement (one sentence, no buzzwords)
   - 3 alternative category framings, ranked, with pros/cons for each
   - Customer-language messaging hierarchy: top-level promise → 3 supporting proof points → call to action
   - What this positioning is NOT for (the customer segments and use cases you're deliberately ignoring)

REFUSALS:
- If the user can't name competitive alternatives, stop and dig — every product has alternatives.
- If the user gives demographic-only target descriptions ("startups", "SMBs"), push back and ask for characteristic-based segmentation.
- Never produce final positioning without all 5 components answered.
```

---

## Why Jarvis Picked This

### Output quality drivers
- **Role priming:** Anchored to a recognized framework (April Dunford's *Obviously Awesome*) — auditable, citation-friendly.
- **Scope boundaries:** Five components, each defined with a concrete counterexample. Cannot drift.
- **Output format:** Workflow → 4 final deliverables (positioning statement, 3 category framings, messaging hierarchy, "not for" segments).
- **Reasoning techniques:** Interactive sharpening (model proposes hypothesis, then asks questions) — anti-hallucination by design.
- **Safety / refusal patterns:** Three explicit refusals: (1) won't skip steps, (2) won't accept "status quo" alternatives, (3) won't accept demographic-only segments.
- **Examples / few-shot:** Inline counterexamples ("a spreadsheet + a part-time intern" vs "the status quo") teach the model the bar.

### 2026 trend relevance
- **Modern frameworks:** April Dunford's framework is the dominant B2B positioning playbook in 2026.
- **Current tech references:** Implicit GTM thinking.
- **Structured output:** Multi-deliverable but composable.
- **Safety alignment:** Refusal rules prevent shallow outputs.

### Deployability
- **License:** MIT-equivalent, Jarvis-authored.
- **Vendor lock:** None.
- **Jarvis adaptability:** Pairs naturally with research-agent (competitor lookups) and product memory.

---

## Runners-up + Trade-offs

### #2: GTM Launch Planner (Prompt 3)
- **Why not picked:** Excellent sequenced rollout prompt, but requires positioning as input. Run AFTER positioning is locked.
- **When to use this instead:** Boss has positioning + ICP and needs a launch plan.

### #3: JTBD Interview Synthesizer (Prompt 5)
- **Why not picked:** Excellent customer-research tool but narrower scope (synthesis, not strategy).
- **When to use this instead:** After 5+ customer interviews; outputs feed positioning.

### #4: Competitive Teardown (Prompt 4)
- **Why not picked:** Hypothesis-grade strategic intel, pairs with positioning but is upstream.
- **When to use this instead:** Quarterly competitive review.

### Explicitly downgraded: Prompt 1 (awesome-chatgpt-prompts "Advertiser")
- Too shallow on its own; useful as a sketch kickoff but produces generic output.

---

## Deployment Notes for Jarvis

1. **File path:** `.claude/agents/marketing-strategist-agent.md`
2. **Adaptations needed:**
   - Ensure "ask one question at a time" preference (per Boss's MEMORY.md) is honored — current prompt batches sharpening questions, may need tightening.
   - Wire in research-agent handoff for competitor verification.
3. **Tool access (suggested):** Read access to product memory + customer research; research-agent for competitor data.
4. **Model recommendation:** sonnet (good framework application); opus for high-stakes repositioning.

---

## Scorecard

| Criterion | Score (1-5) | Notes |
|-----------|-------------|-------|
| Role priming clarity | 5/5 | Framework-anchored persona |
| Scope boundaries | 5/5 | 5 components, counterexamples included |
| Output format guidance | 5/5 | 4 final deliverables |
| Reasoning techniques | 5/5 | Interactive sharpening, anti-hallucination |
| Safety / refusal patterns | 5/5 | 3 explicit refusals |
| 2026 tech relevance | 4/5 | Framework still dominant; could add LLM-era positioning notes |
| License-friendliness | 5/5 | MIT-equivalent, Jarvis-authored |
| **Overall** | **34/35** | Strongest strategic-marketing prompt |
