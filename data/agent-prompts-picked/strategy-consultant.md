# Strategy Consultant — Jarvis-Picked Agent Prompt

> Selected 2026-05-11 from 4 candidates in `../agent-prompts/strategy-consultant.md`
> Picker: prompt-picker-agent | Criteria: output quality + 2026 trend relevance + deployability

---

## Selected Prompt

**Original name:** McKinsey Senior Engagement Manager
**From library:** `data/agent-prompts/strategy-consultant.md` -> Prompt 1
**Source:** [EQ4C Persona Prompts](https://tools.eq4c.com/persona-prompts/chatgpt-prompt-for-the-mckinsey-style-strategy-consultancy-services/)
**Author:** EQ4C Tools
**License:** Free use (persona-prompt directory; verify before commercial reuse)

### Full Prompt (verbatim)

```
You are a Senior Engagement Manager at McKinsey & Company, possessing world-class expertise in strategic problem solving, organizational change, and operational efficiency. Your communication style is top-down, hypothesis-driven, and relentlessly clear. You adhere strictly to the Minto Pyramid Principle—starting with the answer first, followed by supporting arguments grouped logically. You possess a deep understanding of global markets, financial modeling, and competitive dynamics. Your demeanor is professional, objective, and empathetic to the high-stakes nature of client challenges.

For every problem you address:

1. Begin with the SCQ Framework (Situation, Complication, Question) to frame the engagement.
2. Decompose the core question into an Issue Tree that is strictly MECE (Mutually Exclusive, Collectively Exhaustive).
3. Apply the most relevant strategic framework(s) — e.g., Porter's Five Forces, 3Cs, 4Ps, Profitability Tree, Value Chain — to each branch.
4. Generate working hypotheses for each branch and identify the analyses required to confirm or refute them.
5. Synthesize findings using the Pyramid Principle: governing thought first, then 3-5 supporting arguments, each with evidence.
6. Produce an executive-ready brief: action-oriented titles, board-level language, no jargon without definition, and explicit "so-what" implications.

When information is missing, state the assumption explicitly and proceed. Flag the top two risks to your recommendation. Close every response with a Next Steps section: specific actions, owners (placeholder), and a 30/60/90 timeline.
```

---

## Why Jarvis Picked This

### Output quality drivers
- **Role priming:** "Senior Engagement Manager at McKinsey" — strong, specific role with clear communication style mandates (top-down, hypothesis-driven).
- **Scope boundaries:** Six numbered steps; output is a board-ready brief, not a chat.
- **Output format:** SCQ -> Issue Tree -> Frameworks -> Hypotheses -> Pyramid synthesis -> Next Steps. Pinned and auditable.
- **Reasoning techniques:** MECE decomposition + Minto Pyramid + framework application. The canonical consulting toolkit.
- **Safety / refusal patterns:** "State assumptions explicitly when information is missing" — anti-hallucination. "Flag top two risks" — anti-confirmation-bias.

### 2026 trend relevance
- **Modern frameworks:** Frameworks named (Porter's, 3Cs, 4Ps, Value Chain) are timeless but listed explicitly so model applies them appropriately.
- **Current tech references:** None needed.
- **Structured output:** SCQ + MECE + Pyramid + Next Steps with 30/60/90 timeline.
- **Safety alignment:** Assumption-flagging and risk-flagging built in.

### Deployability
- **License:** Free use (verify for commercial — Jarvis personal use is fine).
- **Vendor lock:** None.
- **Jarvis adaptability:** Drop in as `.claude/agents/strategy-consultant.md`. For mock case practice, swap to Prompt 2 (interviewer mode). For quick decisions, fall back to Prompt 3.

---

## Runners-up + Trade-offs

### #2: Interviewer-Led Case Practice (Prompt 2)
- **Why not picked:** Different mode — adversarial interviewer, not analyst. Excellent for case-interview prep.
- **When to use this instead:** Boss preparing for case interviews; sharpening structuring instincts under pressure.

### #3: Strategic Problem Solver Hypothesis-Driven (Prompt 3)
- **Why not picked:** Lighter weight, less rigor. Useful as a quick-mode alternative.
- **When to use this instead:** Daily decisions where full McKinsey scaffolding is overkill.

### #4: Issue Tree Architect (Prompt 4)
- **Why not picked:** Single-step tool, not full workflow.
- **When to use this instead:** When you only need the decomposition step. Composable as a sub-skill.

---

## Deployment Notes for Jarvis

1. **File path:** `.claude/agents/strategy-consultant.md`
2. **Adaptations needed:** Add Boss-style Hinglish-friendly clause. Honor "10 options per decision" preference — modify step 5 to surface multiple option sets instead of pre-narrowing. Add explicit handoff to research-agent for market data.
3. **Tool access (suggested):** WebSearch, WebFetch, Read, Write, Edit. Optionally mcp__gemini__GEMINI_GENERATE_CONTENT for parallel option generation.
4. **Model recommendation:** sonnet (default) — opus for board-level briefs with deep market analysis.

---

## Scorecard

| Criterion | Score (1-5) | Notes |
|-----------|-------------|-------|
| Role priming clarity | 5/5 | Strong McKinsey role + style. |
| Scope boundaries | 5/5 | Six numbered steps. |
| Output format guidance | 5/5 | SCQ + MECE + Pyramid + Next Steps. |
| Reasoning techniques | 5/5 | Full canonical consulting toolkit. |
| Safety / refusal patterns | 4/5 | Assumption-flagging; could add explicit refusal for advice on regulated industries. |
| 2026 tech relevance | 4/5 | Timeless frameworks; minor MCP/agent upgrade possible. |
| License-friendliness | 3/5 | Free use, verify before commercial. |
| **Overall** | **31/35** | Strong, well-scoped. |
