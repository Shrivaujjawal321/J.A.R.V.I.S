# Customer Success Manager — Jarvis-Picked Agent Prompt

> Selected 2026-05-11 from 5 candidates in `../agent-prompts/customer-success-manager.md`
> Picker: prompt-picker-agent | Criteria: output quality + 2026 trend relevance + deployability

---

## Selected Prompt

**Original name:** Churn-Risk Triage from Usage Signals
**From library:** `data/agent-prompts/customer-success-manager.md` → Prompt 2
**Source:** [Vitally — 23 AI Prompts for Customer Success](https://www.vitally.io/post/ai-prompts-for-cs)
**Author:** Vitally
**License:** Free blog content (cite)

### Full Prompt (verbatim)

```
Act as a senior Customer Success Manager doing a Monday morning book
review. Below is a snapshot of accounts with usage signals. For each
account:
  1. Assign a churn-risk score (Low / Medium / High / Critical) with
     1-sentence reasoning tied to specific signals.
  2. Identify the single most likely root cause (adoption, value gap,
     stakeholder change, product fit, support friction).
  3. Recommend the next best action (email / call / exec sponsor /
     escalation) and who should own it.
  4. Draft the first message if action is "email" or "call agenda."

Output as a markdown table, then a "do these 3 first" priority list at
the bottom.

Accounts:
[PASTE — name, ARR, license utilisation %, last login, recent ticket
count, NPS, renewal date]
```

---

## Why Jarvis Picked This

### Output quality drivers
- **Role priming:** Senior CSM persona + specific ritual ("Monday morning book review") gives the model a concrete mental model.
- **Scope boundaries:** Four numbered steps per account — exhaustive without bloat.
- **Output format:** Markdown table + priority list at bottom — directly paste-able to Slack/Notion.
- **Reasoning techniques:** Forces root-cause classification from a closed set (adoption / value / stakeholder / fit / friction) — prevents vague "they're not engaged" outputs.
- **Safety / refusal patterns:** Implicit only (drafts a message, doesn't send). Could be stronger.
- **Examples / few-shot:** None; relies on input schema.

### 2026 trend relevance
- **Modern frameworks:** Churn-risk triage is the highest-frequency CSM workflow in 2026 PLG/SaaS land.
- **Current tech references:** Usage-signal-first thinking matches modern product-led CS motion.
- **Structured output:** Table-based output is dashboard-ready, agent-friendly.
- **Safety alignment:** Doesn't auto-send; outputs drafts for human review. Add explicit no-autonomous-send rule on adaptation.

### Deployability
- **License:** Vitally blog content — citation required; free for adaptation.
- **Vendor lock:** None.
- **Jarvis adaptability:** Pairs naturally with Boss's weekly review ritual.

---

## Runners-up + Trade-offs

### #2: Renewal Forecast Checklist (Prompt 5)
- **Why not picked:** Higher fidelity for renewal-specific moments, but narrower window (120/90/60/30 days pre-renewal). Picked Prompt 2 because triage is the everyday tool.
- **When to use this instead:** 120 days before any renewal — run quarterly.

### #3: QBR Prep Builder (Prompt 3)
- **Why not picked:** Specialized artifact for QBR moments; less reusable week-over-week.
- **When to use this instead:** 48 hours before any executive QBR.

### #4: CSM Persona + Context Anchor (Prompt 1)
- **Why not picked:** Excellent foundational prompt for one-off comms but doesn't produce a portfolio-scale artifact.
- **When to use this instead:** Single high-stakes account communication.

---

## Deployment Notes for Jarvis

1. **File path:** `.claude/agents/csm-agent.md`
2. **Adaptations needed:**
   - Add explicit "never send draft autonomously" rule per Jarvis safety constraint.
   - Wire usage-signal schema (Boss's specific product metrics) into the input expectations.
   - Add Hinglish toggle for Indian-market customers.
3. **Tool access (suggested):** Read access to CRM/analytics; no autonomous email; optional handoff to email-agent for sends after approval.
4. **Model recommendation:** sonnet (table-heavy structured output, classification).

---

## Scorecard

| Criterion | Score (1-5) | Notes |
|-----------|-------------|-------|
| Role priming clarity | 5/5 | Senior CSM + ritual anchor |
| Scope boundaries | 5/5 | 4-step deterministic loop |
| Output format guidance | 5/5 | Table + priority list |
| Reasoning techniques | 4/5 | Closed-set root-cause classification |
| Safety / refusal patterns | 3/5 | Implicit only — add explicit refusal rules on adaptation |
| 2026 tech relevance | 5/5 | Usage-signal-led, modern CS motion |
| License-friendliness | 4/5 | Cite Vitally on reuse |
| **Overall** | **31/35** | Highest-frequency artifact; weekly leverage |
