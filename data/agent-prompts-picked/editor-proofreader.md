# Editor / Proofreader — Jarvis-Picked Agent Prompt

> Selected 2026-05-11 from 5 candidates in `../agent-prompts/editor-proofreader.md`
> Picker: prompt-picker-agent | Criteria: output quality + 2026 trend relevance + deployability

---

## Selected Prompt

**Original name:** Developmental Editor (three-layer feedback)
**From library:** `data/agent-prompts/editor-proofreader.md` -> Prompt 4
**Source:** Composite — adapted from the developmental editing tradition documented at [Zane Dickens' Substack](https://zane.substack.com/p/developmental-editing-with-chatgpt) and standard editorial practice
**Author:** Composite original
**License:** Composite original prompt (effectively CC0 for Jarvis use)

### Full Prompt (verbatim)

```
You are an award-winning developmental editor working on a [GENRE / FORMAT — e.g., literary novel, business book, longform essay]. Your job is structural and substantive feedback, not line-level edits.

When given a chapter, section, or full manuscript, produce feedback in three layers:

LAYER 1 — TEXT (what is happening)
- Summarize what literally occurs in this section, beat by beat.
- Note any plot, argument, or logical gaps.

LAYER 2 — SUBTEXT (what is happening underneath)
- What is the section *actually* about — emotionally, thematically, or politically?
- What does the writer seem to want the reader to feel by the end of this section?
- Where does intended subtext fail to land, or where does unintended subtext sneak in?

LAYER 3 — FUNCTION (what this section adds to the whole)
- What does this section contribute to the larger work — character arc, theme, argument escalation, world-building?
- If you removed this section, what would be lost?
- Is the section earning its space, or is it indulgent?

After the three layers, output:
- TOP 3 ACTIONABLE REVISIONS (specific, not vague — "cut the second flashback in chapter 4" not "tighten chapter 4")
- ONE QUESTION to ask the writer that would unlock the biggest improvement
- ONE THING THE WRITER IS DOING WELL that they should protect even in revision

Do not rewrite the prose. Do not fix typos. This is a structural pass.
```

---

## Why Jarvis Picked This

### Output quality drivers
- **Role priming:** "Award-winning developmental editor" — narrow seniority + specialty (not generic editor).
- **Scope boundaries:** Explicit non-scope: "Do not rewrite the prose. Do not fix typos." Forces structural focus.
- **Output format:** Three labeled layers + Top 3 revisions + one question + one strength — fully pinned.
- **Reasoning techniques:** Text -> Subtext -> Function is a powerful three-pass CoT for structural reading.
- **Safety / refusal patterns:** Anti-vague-feedback ("cut the second flashback" not "tighten") forces specificity. Anti-rewrite preserves writer voice.
- **Examples / few-shot:** Inline specificity example (the "cut flashback vs. tighten" contrast).

### 2026 trend relevance
- **Modern frameworks:** Three-layer text/subtext/function model is contemporary editorial practice — taught at Iowa Writers' Workshop, Tin House, modern MFA programs.
- **Current tech references:** Composes with novelist agent (Prompt 4 of novelist library) for outline-draft-edit loop.
- **Structured output:** Layer-based output is consumable by downstream revision agents.
- **Safety alignment:** Strong anti-rewrite rule preserves author agency — critical for AI-assisted writing in 2026.

### Deployability
- **License:** Composite original — unrestricted for Jarvis.
- **Vendor lock:** None.
- **Jarvis adaptability:** High. The structural-editing gap is the hardest one for LLMs; this prompt closes it for Boss.

---

## Runners-up + Trade-offs

### #2: Adaptive Editor (Prompt 1)
- **Why not picked:** Anthropic-published, versatile, preserves voice while fixing line-level issues. Loses to Prompt 4 only because line editing is the easier pass to do well; Boss benefits more from a developmental specialist.
- **When to use this instead:** Line-level pass after structural revisions land. Wire as `line-editor` sibling agent.

### #3: Style Guide Consistency Auditor (Prompt 5)
- Excellent for long-document consistency hunts (build style sheet, then audit). Wire as `style-auditor` sibling agent for book-length work.

---

## Deployment Notes for Jarvis

1. **File path:** `.claude/agents/editor-proofreader.md`
2. **Adaptations needed:**
   - Default genre/format pulled from project context (Boss's current writing project).
   - Add a `mode` flag: `developmental` | `line` | `proofread` | `style-audit` — each routes to the appropriate prompt template.
   - For Hinglish/Hindi work, note that subtext/function reads still apply but linguistic patterns may differ.
3. **Tool access (suggested):** Read (manuscript + bible/voice profile), Write (notes to `data/notes/edits/`).
4. **Model recommendation:** opus (best for nuanced structural reading); sonnet for line-edit pass.

---

## Scorecard

| Criterion | Score (1-5) | Notes |
|-----------|-------------|-------|
| Role priming clarity | 5/5 | Award-winning developmental editor, scope-bounded. |
| Scope boundaries | 5/5 | Explicit "do not rewrite, do not fix typos." |
| Output format guidance | 5/5 | Three layers + revisions + question + strength. |
| Reasoning techniques | 5/5 | Text/Subtext/Function CoT. |
| Safety / refusal patterns | 4/5 | Anti-vague, anti-rewrite. |
| 2026 tech relevance | 4/5 | Modern MFA-aligned framework. |
| License-friendliness | 5/5 | Composite original. |
| **Overall** | **33/35** | |
