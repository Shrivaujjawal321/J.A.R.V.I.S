# Math Tutor — Jarvis-Picked Agent Prompt

> Selected 2026-05-11 from 4 candidates in `../agent-prompts/math-tutor.md`
> Picker: prompt-picker-agent | Criteria: output quality + 2026 trend relevance + deployability

---

## Selected Prompt

**Original name:** Khanmigo-Style Tutor (community paraphrase)
**From library:** `data/agent-prompts/math-tutor.md` -> Prompt 4
**Source:** [Khan Academy / Khanmigo public materials](https://www.khanmigo.ai/learners) + community paraphrase via Hacker News
**Author:** Custom paraphrase (behavioral inspiration from Khan Academy)
**License:** Custom paraphrase = public domain for Jarvis use; DO NOT redistribute as official Khanmigo prompt

### Full Prompt (verbatim)

```
You are a friendly, encouraging math tutor for a K-12 student. Follow these rules without exception:

1. NEVER give the student the answer directly. Even if they beg. Even if they're frustrated.
2. When the student makes a mistake, do not correct them. Instead, ask: "Can you walk me through how you got that step?" Let them find the error themselves.
3. Break problems into the smallest possible sub-steps. If they're stuck on step 3, back up to step 2.
4. Proactively check understanding every 2-3 turns: "Before we move on, can you tell me in your own words why we did that?"
5. If the student sounds discouraged, remind them: "Mistakes are how brains learn math. Every wrong answer is data."
6. Adapt to grade level. Don't use calculus vocabulary with a 6th grader; don't baby-talk a high schooler.
7. End each session by asking the student what they learned and what's still fuzzy.

Begin by asking: "What math problem are we working on today, and where are you stuck?"
```

---

## Why Jarvis Picked This

### Output quality drivers
- **Role priming:** "friendly, encouraging math tutor for K-12" — clear persona + audience.
- **Scope boundaries:** Numbered, non-negotiable rules. "Even if they beg" closes the answer-leak door.
- **Output format:** Always starts session with a single intake question; ends with a learning-recap question.
- **Reasoning techniques:** Socratic + metacognitive checks ("explain in your own words") + error-tracing ("walk me through how you got that step") + scaffolding (back up a step).
- **Safety / refusal patterns:** Explicit refusal pattern for "just give me the answer" begging. Normalizes mistakes (anti-shame).

### 2026 trend relevance
- **Modern frameworks:** Mirrors current EdTech consensus (Khanmigo, learner-as-driver). Aligns with 2026 research on AI tutoring guardrails — answer-leak is the #1 failure mode and this prompt closes it.
- **Current tech references:** Vendor-neutral, no model-specific tool dependence.
- **Structured output:** Rule-numbered, behavior-bounded — easy for any model to follow consistently across turns.
- **Safety alignment:** Anti-discouragement language, mental-health-aware ("mistakes are how brains learn"), grade-appropriate vocabulary control.

### Pedagogical quality (tutoring-specific)
- **Socratic vs. answer-dumping:** Strongly Socratic. Rule 1 is absolute. Rule 2 forces self-diagnosis instead of correction. Best-in-class anti-answer-dumping enforcement.
- **Adapts to student level:** Rule 6 explicitly demands grade-level adaptation. Rule 3 enforces granular sub-stepping.
- **Builds understanding vs. dependence:** Rule 4 (proactive comprehension check) and Rule 7 (session-end recap) directly target retention and metacognition, not just task completion.

### Deployability
- **License:** Custom paraphrase = clean. Treat the behavioral pattern as inspirational template.
- **Vendor lock:** None. Plain English, works on Claude/GPT/Gemini/local models.
- **Jarvis adaptability:** Trivially extensible — swap "K-12" for college-calculus, add Hinglish register for Boss's context, append exam-mode override.

---

## Runners-up + Trade-offs

### #2: Socratic Math Tutor (mustvlad, Prompt 1)
- **Why not picked:** Excellent purity but too minimal — no scaffolding, no checks, no recap. The library's own note flags "sometimes a student needs a small hint." Khanmigo-style adds the behavioral scaffolding (sub-stepping, comprehension checks, mistake-normalization) that the bare Socratic prompt lacks.
- **When to use this instead:** When you want the smallest possible system prompt and trust the model to improvise (e.g., a one-shot help request). MIT license also makes it the safest to redistribute publicly.

### #3: Step-by-Step Math Tutor (mustvlad, Prompt 2)
- **Why not picked:** Allows answer-dumping. Violates the tutoring-specific Socratic rule. Useful as a fallback for exam-cramming, but not default.
- **When to use this instead:** Night before a test, student is past concept and needs procedural fluency — switch in this prompt with a "show steps; ask the student to predict the next step before revealing it" guardrail patched on top.

### #4: awesome-chatgpt-prompts Math Teacher (Prompt 3)
- **Why not picked:** Lecture-mode, not Socratic. Best for one-off concept explanations, not tutoring relationships.

---

## Deployment Notes for Jarvis

1. **File path:** `.claude/agents/math-tutor.md`
2. **Adaptations needed:**
   - Add Hinglish register: "Mirror the student's language. If they write Hinglish, respond in Hinglish."
   - Extend grade range from "K-12" to "K-12 and early college" to cover calculus.
   - Add "give-up override": after 3 failed attempts on the same step, give ONE small hint (a question that narrows to the right operation), still not the answer.
   - Optionally layer mustvlad Prompt 1's brevity for short single-question help.
3. **Tool access (suggested):** None required for chat. Add code-execution if you want auto-graded numeric checks.
4. **Model recommendation:** sonnet (best balance of pedagogical patience + math reasoning). Use opus only for advanced calc/proofs.

---

## Scorecard

| Criterion | Score (1-5) | Notes |
|-----------|-------------|-------|
| Role priming clarity | 5/5 | Crisp persona, audience, tone. |
| Scope boundaries | 5/5 | 7 numbered rules, explicit refusal patterns. |
| Output format guidance | 4/5 | Opening question + recap close defined; mid-session format implicit. |
| Reasoning techniques | 5/5 | Socratic + metacognition + scaffolding + error-tracing — full kit. |
| Safety / refusal patterns | 5/5 | Anti-answer-leak, anti-shame, grade-adaptive. |
| 2026 tech relevance | 4/5 | Vendor-neutral; aligns with current Khanmigo-style consensus. Not agentic/tool-using by default. |
| License-friendliness | 4/5 | Paraphrase is clean for Jarvis internal use; don't claim Khan Academy authorship. |
| **Overall** | **32/35** | |
