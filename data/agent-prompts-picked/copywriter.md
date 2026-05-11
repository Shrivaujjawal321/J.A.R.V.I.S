# Copywriter — Jarvis-Picked Agent Prompt

> Selected 2026-05-11 from 6 candidates in `../agent-prompts/copywriter.md`
> Picker: prompt-picker-agent | Criteria: output quality + 2026 trend relevance + deployability

---

## Selected Prompt

**Original name:** AIDA-Structured Copy Generator
**From library:** `data/agent-prompts/copywriter.md` -> Prompt 5
**Source:** [dair-ai/Prompt-Engineering-Guide](https://github.com/dair-ai/Prompt-Engineering-Guide)
**Author:** Pattern composed for Jarvis; AIDA is public-domain (E. St. Elmo Lewis, c. 1898)
**License:** CC0

### Full Prompt (verbatim)

```
You are a senior direct-response copywriter trained in the AIDA framework. Convert a product brief into structured copy where each block is labeled by AIDA stage.

Step 1 — Diagnose (before writing):
- Target reader in one sentence: who, job-to-be-done, frustration.
- Single most important pain. Pick ONE — copy addressing everything addresses nothing.

Step 2 — Write with AIDA labels:

**[ATTENTION]** — 1-2 lines, headline. Stops the scroll. Mentions pain, contrast, or a specific number. No vague benefit-speak.

**[INTEREST]** — 2-4 lines. Expand pain or insight. Show you understand them better than they understand themselves.

**[DESIRE]** — 3-6 lines or bullets. Paint after-state vividly. Name the mechanism. Include 1 specific proof point (number/logo/testimonial fragment) if provided.

**[ACTION]** — 1-2 lines. Specific verb. Reduce friction. State what happens next ("Free 14-day trial. No card. 60-second signup.").

Rules:
- Match brand voice. Default: clear, plain English, 7th-grade level.
- No corporate jargon ("leverage", "synergize") unless brand-required.
- Specific verbs > generic ("Cut weekly reporting from 4h to 20min" > "Save time").
- If a stage can't be filled from the brief, ask one clarifying question.
- Provide 2 variants per block for A/B testing.
```

---

## Why Jarvis Picked This

### Output quality drivers
- **Role priming:** "Senior direct-response copywriter trained in the AIDA framework" — narrow seniority + named methodology.
- **Scope boundaries:** Inputs scoped to a product brief; output scoped to four labeled blocks.
- **Output format:** Pinned with explicit AIDA labels in brackets, line/word budgets per block, 2 variants per block for A/B.
- **Reasoning techniques:** Explicit chain-of-thought (Step 1 Diagnose -> Step 2 Write). Forces single-pain selection before writing.
- **Safety / refusal patterns:** "Ask one clarifying question if stage can't be filled" — refuses to fabricate. Implicit ban on jargon and vague benefit-speak.
- **Examples / few-shot:** Inline example of specific-vs-generic ("Cut weekly reporting from 4h to 20min" > "Save time").

### 2026 trend relevance
- **Modern frameworks:** Combines a timeless framework (AIDA) with 2024+ prompt-engineering patterns (CoT, structured tagged blocks, clarification fallback).
- **Current tech references:** Default conversion-ready ("Free 14-day trial. No card.") matches modern SaaS funnel norms.
- **Structured output:** Tagged blocks (`[ATTENTION]`, `[INTEREST]`, etc.) parse cleanly into downstream automations (Notion, A/B testing tools, multi-variant pipelines).
- **Safety alignment:** No fabrication of proof; asks instead of inventing.

### Deployability
- **License:** CC0 — fully usable, modifiable, redistributable. Best-case for Jarvis.
- **Vendor lock:** None — model-agnostic.
- **Jarvis adaptability:** High. Easy to wrap with brand-voice memory file injection and to chain with PAS variant (Prompt 6) for sales pages.

---

## Runners-up + Trade-offs

### #2: PAS Long-Form Sales Letter (Prompt 6)
- **Why not picked:** Excellent and CC0, but scope is long-form sales pages — narrower than AIDA. AIDA is the better default for headlines, hero, ads, emails, and LP openers.
- **When to use this instead:** Long-form sales pages, info-product launches, paid-traffic landing pages, cold-email sequences where the reader is cold and needs full agitation.

### #3: CoppieGPT (Prompt 1)
- Strong on framework variety (232 formulas, 6 variants per run), but Unknown license and no diagnostic step. Use as a complement when you want maximum variant breadth, not as the canonical agent.

---

## Deployment Notes for Jarvis

1. **File path:** `.claude/agents/copywriter.md`
2. **Adaptations needed:**
   - Inject `data/memory/preferences.md` brand-voice section at runtime.
   - Add Boss-specific defaults: Hinglish-friendly tone available, no fake urgency.
   - Optional: wire a second pass with PAS for long-form when input asks for "sales page."
3. **Tool access (suggested):** Read (for brand-voice memory); Write (to draft into `data/notes/`); optional Notion MCP to push variants for review.
4. **Model recommendation:** sonnet (best for nuanced copy with brand voice); haiku for bulk variant generation.

---

## Scorecard

| Criterion | Score (1-5) | Notes |
|-----------|-------------|-------|
| Role priming clarity | 5/5 | Senior direct-response, named framework. |
| Scope boundaries | 5/5 | Product brief in, AIDA blocks out. |
| Output format guidance | 5/5 | Tagged labels, line budgets, A/B variants. |
| Reasoning techniques | 5/5 | Explicit 2-step CoT with diagnose-first. |
| Safety / refusal patterns | 4/5 | Clarify rather than invent; no fabrication. |
| 2026 tech relevance | 4/5 | Tagged structured output, model-agnostic. |
| License-friendliness | 5/5 | CC0. |
| **Overall** | **33/35** | |
