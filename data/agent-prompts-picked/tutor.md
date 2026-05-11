# Tutor — Jarvis-Picked Agent Prompt

> Selected 2026-05-11 from 6 candidates in `../agent-prompts/tutor.md`
> Picker: prompt-picker-agent | Criteria: output quality + 2026 trend relevance + deployability

---

## Selected Prompt

**Original name:** Socratic Tutor (canonical short form)
**From library:** `data/agent-prompts/tutor.md` -> Prompt 1
**Source:** [bramses/chatgpt-md-templates](https://github.com/bramses/chatgpt-md-templates/blob/main/socratic-tutor.md), also [mustvlad/ChatGPT-System-Prompts](https://github.com/mustvlad/ChatGPT-System-Prompts/blob/main/prompts/educational/socratic-tutor.md)
**Author:** Bram Adams (bramses); also widely circulated
**License:** mustvlad: MIT; bramses: unlicensed (use mustvlad copy for clean license)

### Full Prompt (verbatim)

```
You are a tutor that always responds in the Socratic style. You *never* give the student the answer, but always try to ask just the right question to help them learn to think for themselves. You should always tune your question to the interest & knowledge of the student, breaking down the problem into simpler parts until it's at just the right level for them.
```

---

## Why Jarvis Picked This

### Output quality drivers
- **Role priming:** Tight role lock — "Socratic tutor." No ambiguity.
- **Scope boundaries:** Single hard rule ("never give the answer") that flips LLM default behavior. Without this rule the model defaults to answer-dumping.
- **Output format:** Free-form questions, tuned to learner level — appropriate for tutoring (not a fixed template).
- **Reasoning techniques:** Two engineering instructions: (1) ask the *right* question, (2) decompose into simpler parts until at-level. That's the entire Socratic loop in one sentence.
- **Safety / refusal patterns:** Doesn't need a refusal pattern — Socratic stance itself is the safety mechanism (no answer-dumping = no homework cheating, no expert overreach).

### 2026 trend relevance
- **Modern frameworks:** Aligned with Khanmigo, Duolingo Max, and most 2026 ed-tech tutor designs.
- **Current tech references:** Vendor-neutral, model-agnostic.
- **Structured output:** Intentionally unstructured — tutor adapts to learner.
- **Safety alignment:** Inherent — tutor cannot harm by refusing to give answers.

### Deployability
- **License:** MIT (via mustvlad mirror) — clean.
- **Vendor lock:** None. The smallest, most portable prompt in the library.
- **Jarvis adaptability:** Wrap with Boss's Hinglish preference, add a fallback hint mechanism (from Prompt 2 — Khanmigo pattern), and a fallback worked-example mode (from Prompt 3) triggered only on explicit learner request.

---

## Runners-up + Trade-offs

### #2: Khanmigo-Style Coding Tutor (Prompt 2)
- **Why not picked:** Proprietary provenance (leaked). The Socratic core is identical; Prompt 2 adds warmth + "how did you figure out that step?" pattern, which is excellent.
- **When to use this instead:** When learner is younger or shuts down on harsh feedback. Layer the warmth pattern onto Prompt 1 instead of redistributing leaked text.

### #3: Concept Explainer (Prompt 6 — Feynman ladder)
- **Why not picked:** Different mode — answer-giving, not Socratic. Best as a fallback tool, not the default.
- **When to use this instead:** Learner is stuck on a true unknown and needs anchor explanation before Socratic dialogue resumes.

---

## Deployment Notes for Jarvis

1. **File path:** `.claude/agents/tutor.md` (or as `.claude/agents/learning-agent.md` matching existing roster)
2. **Adaptations needed:** Add Hinglish-mirror clause for Boss's preference. Append "When the learner is truly stuck after 2-3 hint cycles, offer one small concrete clue, then ask them to take the next step." Add explicit hand-off to Feynman ladder (Prompt 6) on request.
3. **Tool access (suggested):** Read, Write (for saving practice progress), Edit. Read-only for learning materials.
4. **Model recommendation:** haiku (default) — sonnet for complex domains (math proofs, advanced CS). Tutoring is high-volume, low-token; cheap models work well.

---

## Scorecard

| Criterion | Score (1-5) | Notes |
|-----------|-------------|-------|
| Role priming clarity | 5/5 | Crisp role lock. |
| Scope boundaries | 5/5 | "Never give the answer" inverts LLM default. |
| Output format guidance | 4/5 | Unstructured but appropriate for tutoring. |
| Reasoning techniques | 5/5 | Whole Socratic loop in one sentence. |
| Safety / refusal patterns | 5/5 | Inherent via Socratic stance. |
| 2026 tech relevance | 5/5 | Matches Khanmigo et al. |
| License-friendliness | 5/5 | MIT via mirror. |
| **Overall** | **34/35** | Best-in-class minimalism. |
