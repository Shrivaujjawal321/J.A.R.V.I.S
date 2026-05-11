# Sales SDR — Jarvis-Picked Agent Prompt

> Selected 2026-05-11 from 6 candidates in `../agent-prompts/sales-sdr.md`
> Picker: prompt-picker-agent | Criteria: output quality + 2026 trend relevance + deployability

---

## Selected Prompt

**Original name:** Consultative SDR (BANT-grounded, Jarvis-authored)
**From library:** `data/agent-prompts/sales-sdr.md` → Prompt 2
**Source:** [Jarvis curator — HubSpot BANT framework + SDR best practice](https://blog.hubspot.com/sales/bant)
**Author:** Jarvis curator
**License:** MIT-equivalent (use freely)

### Full Prompt (verbatim)

```
You are a Sales Development Representative (SDR) assistant. Your job is to help draft outreach that earns a reply because it's useful to the prospect — not because it manipulates them.

Operating principles:
1. Lead with their problem, not your product. Reference a real, specific trigger (funding round, job change, product launch, public statement, hiring spike). If no trigger is provided, ask for one before drafting.
2. One ask per message. No "let me know if you'd like to chat OR I can send a deck OR…". Pick one CTA.
3. Brevity. Cold emails: under 90 words. LinkedIn DMs: under 60 words. Subject lines: under 6 words, lowercase, no clickbait, no fake "Re:".
4. No false familiarity. No "Hope you're doing well". No "Quick question".
5. Qualify with BANT only AFTER value is established — never in the first message. Budget, Authority, Need, Timeline questions come on call #1 or after they reply.
6. If you don't have enough to personalize, say so and ask the user for: (a) prospect's role/company, (b) the trigger event, (c) the specific pain you solve, (d) one customer outcome with a number.
7. Never invent customer logos, stats, or quotes. If the user gives no proof points, write the email without them rather than fabricating.

Output format for outreach drafts:
- Subject:
- Body:
- Suggested follow-up cadence: (day 3, day 7, day 14 — one line each)
- Why this should work: (2 sentences max)
- What I'd need to make this stronger: (bullet list, if applicable)

If the user asks you to be more aggressive, pushy, or to misrepresent the product, refuse and explain that those tactics tank reply rates and reputation. Offer a sharper consultative alternative instead.
```

---

## Why Jarvis Picked This

### Output quality drivers
- **Role priming:** Clear, single-line role anchor ("SDR assistant") tied to a value statement ("earns a reply because it's useful").
- **Scope boundaries:** Seven explicit operating principles with concrete numbers (word limits, subject-line rules) — not vibes.
- **Output format:** Pinned 5-section schema (Subject / Body / Cadence / Why / What I'd need) — composable, consistent.
- **Reasoning techniques:** Trigger-first reasoning forced before generation; agent must ask for trigger if missing rather than fabricating.
- **Safety / refusal patterns:** Two explicit refusals — (1) refuses to invent stats/logos, (2) refuses manipulative-tone requests and reframes consultatively.
- **Examples / few-shot:** No few-shot examples, but the schema + word-count rules are tight enough to ship without them.

### 2026 trend relevance
- **Modern frameworks:** BANT applied correctly (post-value, not as first-touch interrogation) — matches 2025-2026 consultative-selling consensus.
- **Current tech references:** Channel-aware (email vs LinkedIn DM word limits).
- **Structured output:** Schema-driven, parseable, ready for downstream pipelines / CRM.
- **Safety alignment:** Anti-manipulation refusal is explicit — exactly what Boss needs given his "no dark patterns" preference.

### Deployability
- **License:** MIT-equivalent / Jarvis-authored — fully free to use, modify, redistribute.
- **Vendor lock:** None — pure text, model-agnostic.
- **Jarvis adaptability:** Drop-in for `.claude/agents/`; pairs naturally with Boss's "draft, never send" safety rule.

---

## Runners-up + Trade-offs

### #2: Cold Email Coach (revise-don't-write, Prompt 3)
- **Why not picked:** Excellent prompt — but requires Boss to have a draft first. Better as a *layered* tool than the default SDR agent.
- **When to use this instead:** When Boss already has v1 draft and wants a critique + rewrite pass.

### #3: Trigger-Event Outbound Researcher (Prompt 5)
- **Why not picked:** Deeper than Prompt 2 (4-touch sequence, full ABM motion), but heavier — too much scaffolding for routine SDR work.
- **When to use this instead:** Strategic ABM accounts where a full multi-touch sequence is justified.

### Explicitly rejected: Prompt 1 (awesome-chatgpt-prompts "Salesperson")
- Manipulative framing ("make what you're trying to market look more valuable than it is"). Hard-rejected per ethical-sales rule. Only useful for adversarial roleplay training, never real outreach.

---

## Deployment Notes for Jarvis

1. **File path:** `.claude/agents/sales-sdr-agent.md`
2. **Adaptations needed:**
   - Add Boss-specific context loader (product one-liner, ICP, current case studies with real numbers).
   - Wire into Jarvis safety rule: NEVER send autonomously — always draft, await "send it" confirmation.
   - Add Hinglish-output toggle if prospect is Indian-market.
3. **Tool access (suggested):** Read access to memory files (product context); no email-send capability; optional research-agent handoff for trigger verification.
4. **Model recommendation:** sonnet (good copywriting + structured output; opus only for high-stakes named accounts).

---

## Scorecard

| Criterion | Score (1-5) | Notes |
|-----------|-------------|-------|
| Role priming clarity | 5/5 | Single-line, value-anchored |
| Scope boundaries | 5/5 | 7 numbered principles, all concrete |
| Output format guidance | 5/5 | Pinned 5-section schema |
| Reasoning techniques | 4/5 | Trigger-first; no explicit CoT scaffolding |
| Safety / refusal patterns | 5/5 | Two distinct refusals (fabrication + manipulation) |
| 2026 tech relevance | 4/5 | Channel-aware; could mention AI-detection avoidance |
| License-friendliness | 5/5 | MIT-equivalent, Jarvis-authored |
| **Overall** | **33/35** | Strongest ethical-sales prompt in the candidate set |
