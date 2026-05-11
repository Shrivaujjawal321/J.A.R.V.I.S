# Content Writer — Jarvis-Picked Agent Prompt

> Selected 2026-05-11 from 6 candidates in `../agent-prompts/content-writer.md`
> Picker: prompt-picker-agent | Criteria: output quality + 2026 trend relevance + deployability

---

## Selected Prompt

**Original name:** Long-form EEAT Blog Writer
**From library:** `data/agent-prompts/content-writer.md` -> Prompt 5
**Source:** [dair-ai/Prompt-Engineering-Guide](https://github.com/dair-ai/Prompt-Engineering-Guide) — structured output; EEAT from Google Search Quality Evaluator Guidelines (public)
**Author:** Pattern composed for Jarvis
**License:** CC0

### Full Prompt (verbatim)

```
You are a long-form content writer producing in-depth EEAT-aligned articles. Your goal is content that genuinely helps the reader and meets Google's Search Quality Evaluator Guidelines.

Inputs required (ask if missing):
- Topic and primary keyword
- Target reader and level (beginner/intermediate/expert)
- Author's credentials justifying them writing this
- 3-5 trustworthy sources to cite
- Word count target

Structure:

## [Title] — Specific, benefit-driven, primary keyword natural. NOT clickbait.

**Author note:** "Written by [name], who [specific experience]." If not provided: `[CREDENTIALS NEEDED]`.

### Why this matters / who this is for (100-150 words)
- Problem in reader's language.
- Promise of what they'll learn.
- Establish writer's qualification.

### [Section N]
- Lead with concrete claim.
- Support: personal example (Experience), citation (Authoritativeness), data.
- Specific scenarios > generic "you" statements.

### Common mistakes / what doesn't work
Counter-section. Naming failures builds Trust.

### Summary + next step
One paragraph, then 3-5 "what to do tomorrow" bullets.

### Sources
Inline `[^1]` citations. Real URLs only.

Rules:
- Concrete > abstract. Cite numbers, dates, study names, prices.
- First-person experience > generic advice.
- Plain English, 8th-10th grade level.
- Don't stuff keywords. Primary 4-8 times in 2000 words.
- If a claim can't be cited, soften ("in our experience") or remove.
- Never invent statistics. Use `[STAT NEEDED: ...]` placeholders.
```

---

## Why Jarvis Picked This

### Output quality drivers
- **Role priming:** "Long-form content writer producing in-depth EEAT-aligned articles" — narrow, professional, anchored to a real evaluation rubric.
- **Scope boundaries:** Required inputs explicit; output structure mandated; word count enforced.
- **Output format:** Six labeled sections with line/word budgets and citation footnotes.
- **Reasoning techniques:** Implicit CoT via required-inputs check; each section forces a claim -> support pattern (claim, experience, citation, data).
- **Safety / refusal patterns:** Strong. "Never invent statistics," `[STAT NEEDED]` and `[CREDENTIALS NEEDED]` placeholders, soften-or-remove uncited claims.
- **Examples / few-shot:** Author-note template, summary-bullet pattern, citation footnote syntax.

### 2026 trend relevance
- **Modern frameworks:** Google EEAT (Experience, Expertise, Authoritativeness, Trust) — the canonical 2024-2026 ranking framework that explicitly distinguishes human-experience content from AI-slop.
- **Current tech references:** Placeholder syntax aligns with downstream automation (fact-check agents, citation lookup).
- **Structured output:** Heading hierarchy + footnote citations parse cleanly to Markdown CMS pipelines (Ghost, WordPress, Notion).
- **Safety alignment:** Anti-fabrication rules are state-of-the-art for 2026 LLM content workflows.

### Deployability
- **License:** CC0 — no restrictions.
- **Vendor lock:** None.
- **Jarvis adaptability:** High. Composes with research-agent for citation gathering and fact-checker for verification before publish.

---

## Runners-up + Trade-offs

### #2: Newsletter Issue Writer (Prompt 6)
- **Why not picked:** Excellent and CC0, but narrower scope (single-voice email newsletters). Not the best default for general long-form.
- **When to use this instead:** Substack/Beehiiv/ConvertKit issues, founder-led newsletters where opinion and voice are the product.

### #3: All-around Writer Advanced (Prompt 1)
- Outline-first pattern is genuinely valuable, but Unknown license + emoji-leaky output + no anti-fabrication rules. Useful concept; not the canonical agent.

---

## Deployment Notes for Jarvis

1. **File path:** `.claude/agents/content-writer.md`
2. **Adaptations needed:**
   - Add Jarvis-original anti-AI-tell rules (no "delve into," "tapestry," "in the realm of").
   - Wire `research-agent` for source gathering and `fact-checker` for citation verification.
   - Default author credentials pulled from `data/memory/facts.md` when Boss is the named author.
3. **Tool access (suggested):** Read (memory + sources), WebFetch / WebSearch (live citations), Write (drafts to `data/notes/`).
4. **Model recommendation:** sonnet (best quality/cost for 2000-word EEAT pieces); opus only for YMYL topics.

---

## Scorecard

| Criterion | Score (1-5) | Notes |
|-----------|-------------|-------|
| Role priming clarity | 5/5 | EEAT-aligned long-form specialist. |
| Scope boundaries | 5/5 | Required inputs + word count + structure. |
| Output format guidance | 5/5 | Heading hierarchy, footnotes, bullets. |
| Reasoning techniques | 4/5 | Claim-support-citation pattern per section. |
| Safety / refusal patterns | 5/5 | Explicit anti-fabrication placeholders. |
| 2026 tech relevance | 5/5 | EEAT is current Google quality rubric. |
| License-friendliness | 5/5 | CC0. |
| **Overall** | **34/35** | |
