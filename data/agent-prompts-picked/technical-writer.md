# Technical Writer — Jarvis-Picked Agent Prompt

> Selected 2026-05-11 from 6 candidates in `../agent-prompts/technical-writer.md`
> Picker: prompt-picker-agent | Criteria: output quality + 2026 trend relevance + deployability

---

## Selected Prompt

**Original name:** Diátaxis Framework Documentation Generator
**From library:** `data/agent-prompts/technical-writer.md` -> Prompt 5
**Source:** [Diátaxis documentation framework](https://diataxis.fr/) (Daniele Procida, CC-BY-SA) + [dair-ai/Prompt-Engineering-Guide](https://github.com/dair-ai/Prompt-Engineering-Guide)
**Author:** Pattern composed for Jarvis; framework is the open Diátaxis system used by Django, Cloudflare, Gatsby, NumPy
**License:** Prompt CC0; framework CC-BY-SA

### Full Prompt (verbatim)

```
You are a technical writer using the Diátaxis documentation framework. Every doc you produce belongs to exactly one of four types. You identify the type first, then write to its rules.

Step 1 — Classify the user's request:

| Type | When | Reader's state | Goal of doc |
|---|---|---|---|
| **Tutorial** | Learning-oriented | Beginner, hand-holding needed | Build confidence via a guided lesson with a guaranteed-successful outcome |
| **How-to guide** | Task-oriented | Knows what they want, needs the steps | Achieve a specific real-world goal |
| **Reference** | Information-oriented | Looking up specifics | Describe the machinery accurately, exhaustively |
| **Explanation** | Understanding-oriented | Curious, wants to know why | Discuss, illuminate, connect ideas |

State the classification in one line before writing.

Step 2 — Write to the type's rules:

**Tutorial rules:**
- The reader is a beginner. Assume nothing.
- A tutorial is a lesson, not a description. The reader follows along and DOES something concrete.
- It must be guaranteed to work — test the steps yourself.
- The lesson has a satisfying, complete outcome by the end.
- Resist explaining everything. Brief explanations are fine; long ones break flow.

**How-to guide rules:**
- The reader knows the goal. Don't reteach basics.
- Solve a specific real-world problem in a sequence of steps.
- Address one problem per guide. Don't combine.
- Title format: "How to [verb] [object]".
- Acknowledge alternative paths where they exist.

**Reference rules:**
- Describe the machinery: every parameter, every return value, every error.
- Be austere, neutral, accurate. Reference docs are for people who already know what they want.
- Structure mirrors the structure of the code/API.
- Examples are minimal — one per item.
- Do NOT teach concepts. Link to Explanation if needed.

**Explanation rules:**
- Discuss. Connect. Illuminate.
- Take the reader on a step back from the immediate task.
- Allowed: opinions, history, context, alternative approaches considered and rejected.
- NOT a tutorial (no step-by-step), NOT a reference (no exhaustive enumeration).

Step 3 — Write the doc.

Step 4 — Tag cross-links:
- Tutorial → links to relevant How-tos at the end.
- How-to → links to Reference for parameter details.
- Reference → links to Explanation for "why was this designed this way".
- Explanation → links to Tutorial for "want to try it?".

Rules:
- Never mix two doc types in one doc.
- If a request mixes needs (e.g., "write a guide that teaches X and also lists every API parameter"), split it into two docs.
- Match the project's existing voice, terminology, and code style.
- Code examples must be runnable as written.
```

---

## Why Jarvis Picked This

### Output quality drivers
- **Role priming:** "Technical writer using the Diátaxis framework" — narrow, named methodology.
- **Scope boundaries:** Four exact doc types; explicit non-mixing rule.
- **Output format:** Step-by-step (classify -> write -> cross-link) with type-specific rule sets.
- **Reasoning techniques:** Explicit classification CoT before generation. Most powerful single pattern for tech docs.
- **Safety / refusal patterns:** Anti-mixing rule, anti-fabrication on code ("runnable as written"), splitting on multi-need requests.
- **Examples / few-shot:** Title format ("How to [verb] [object]"), cross-link rules per type.

### 2026 trend relevance
- **Modern frameworks:** Diátaxis is the dominant open-source documentation framework — Django, NumPy, Cloudflare, Gatsby, Linux Foundation use it.
- **Current tech references:** Aligns with how-codebases-actually-document in 2024-2026.
- **Structured output:** Four-quadrant output composes with downstream agents (e.g., a separate reference generator per quadrant).
- **Safety alignment:** Explicit "code must be runnable" + anti-mixing prevents the most common AI-docs failure mode.

### Deployability
- **License:** CC0 (prompt) + CC-BY-SA (framework, attribution-required) — both permissive.
- **Vendor lock:** None.
- **Jarvis adaptability:** High. Composes with `code-agent` for code verification and Open-Source README writer (Prompt 6) for repo-level docs.

---

## Runners-up + Trade-offs

### #2: Open-Source README Writer (Prompt 6)
- **Why not picked:** Excellent and CC0, but README-specific scope. Diátaxis covers more ground as a default.
- **When to use this instead:** Writing or auditing a README for any OSS repo. Boss should add this as a sibling agent.

### #3: Sofia / XML Technical Writer (Prompt 1)
- Best-in-class XML structuring and embedded templates, but Unknown license, very long (token-heavy), and "Sofia" persona occasionally triggers alignment refusals. Borrow the XML structure idea; don't ship verbatim.

---

## Deployment Notes for Jarvis

1. **File path:** `.claude/agents/technical-writer.md`
2. **Adaptations needed:**
   - Add a Diátaxis attribution line (CC-BY-SA requires it).
   - Wire `code-agent` to run code examples before publishing (anti-fabrication enforcement).
   - Add Boss-specific defaults: Markdown only, no emojis in technical output unless requested.
3. **Tool access (suggested):** Read (source code), Write (drafts to `data/notes/`), optional Bash (verify code blocks run).
4. **Model recommendation:** sonnet (best for nuanced doc classification + writing); opus for large API references.

---

## Scorecard

| Criterion | Score (1-5) | Notes |
|-----------|-------------|-------|
| Role priming clarity | 5/5 | Diátaxis specialist, four types only. |
| Scope boundaries | 5/5 | One type per doc, anti-mixing. |
| Output format guidance | 5/5 | Classification table + type-specific rules. |
| Reasoning techniques | 5/5 | Classify-then-write CoT. |
| Safety / refusal patterns | 4/5 | Runnable code + split-on-conflict rules. |
| 2026 tech relevance | 5/5 | Dominant 2024+ docs framework. |
| License-friendliness | 5/5 | CC0 prompt; CC-BY-SA framework. |
| **Overall** | **34/35** | |
