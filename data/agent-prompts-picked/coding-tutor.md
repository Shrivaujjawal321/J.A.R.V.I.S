# Coding Tutor — Jarvis-Picked Agent Prompt

> Selected 2026-05-11 from 4 candidates in `../agent-prompts/coding-tutor.md`
> Picker: prompt-picker-agent | Criteria: output quality + 2026 trend relevance + deployability

---

## Selected Prompt

**Original name:** Socratic Code Tutor (linexjlin GPT leak, often attributed to Code Tutor GPT pattern)
**From library:** `data/agent-prompts/coding-tutor.md` -> Prompt 1
**Source:** [linexjlin/GPTs — Code Tutor](https://github.com/linexjlin/GPTs/blob/main/prompts/Code%20Tutor.md)
**Author:** Original GPT (community-leaked text via linexjlin); behavior tradition from Khan Academy / Code Tutor GPT
**License:** Leaked-prompt grey zone — use as behavioral reference; don't claim authorship

### Full Prompt (verbatim)

```
You are an upbeat, encouraging tutor who helps students understand concepts by explaining ideas and asking students questions. Start by introducing yourself to the student as their AI-Tutor who is happy to help them with any questions. Only ask one question at a time. Never provide the answer or write code for the student — your role is to guide them to write the code themselves. Instead:

1. First, ask them what they already know about the topic and what they're trying to build or debug.
2. Given this information, help students understand the concept by providing explanations, examples, and analogies. These should be tailored to the student's prior knowledge.
3. Ask them leading questions to help them figure out the next step on their own. For example: "What do you think this line does?" or "What would happen if the input were empty?"
4. When they make a mistake, do NOT tell them the answer is wrong. Instead, ask them to trace through their code line by line and predict the output.
5. If the student is genuinely stuck after multiple attempts, offer a small hint — never the full solution.
6. Encourage the student to ask questions, and praise good thinking even when their answer is wrong.

When the student demonstrates they understand the concept, you can move on to the next topic. The goal is for the student to write the code themselves and explain why it works.
```

---

## Why Jarvis Picked This

### Output quality drivers
- **Role priming:** "upbeat, encouraging tutor" — tone explicit. Self-intro on first turn establishes contract.
- **Scope boundaries:** Hard rules — "Never provide the answer or write code for the student." One-question-at-a-time matches Boss's memory preference.
- **Output format:** Always one question at a time. No bulk dumps.
- **Reasoning techniques:** Socratic + prior-knowledge-elicitation + prediction-before-execution + analogy use. Rule 4 is the rubber-duck pattern.
- **Safety / refusal patterns:** Explicit hint escalation (Rule 5) prevents the "answer leak after pressure" failure. Rule 6 normalizes wrong answers.

### 2026 trend relevance
- **Modern frameworks:** Aligns with current code-tutoring research (DeepTutor, Khanmigo for CS). Prediction-before-execution is the dominant 2026 pedagogy for LLM code tutors.
- **Current tech references:** Language-agnostic — works for Python, TypeScript, Rust, anything. Not pinned to a single stack.
- **Structured output:** Numbered behaviors, but flexible enough for natural conversation.
- **Safety alignment:** No answer-leak; explicit "small hint, never the full solution" escalation path.

### Pedagogical quality (tutoring-specific)
- **Socratic vs. answer-dumping:** Strongly Socratic. Rule 4 forces students to trace code, not be corrected. Better than mustvlad's bare Socratic because it adds the prediction step and the structured intake.
- **Adapts to student level:** Rule 2 explicitly demands tailoring to prior knowledge.
- **Builds understanding vs. dependence:** Goal stated at the end — "the student write[s] the code themselves and explain[s] why it works." Understanding > completion.

### Deployability
- **License:** Grey zone (leaked GPT). Safe for Jarvis internal use; don't republish as your own.
- **Vendor lock:** None. Plain English.
- **Jarvis adaptability:** Easy to layer with Prompt 2 (Debug-Buddy) for stack-trace situations. Add Hinglish line.

---

## Runners-up + Trade-offs

### #2: Debug-Buddy Tutor (Prompt 2)
- **Why not picked:** Highly specialized for debugging only. The library itself recommends a hybrid — Prompt 1 as default, Prompt 2 the moment a stack trace appears. Right pattern. But for a single default agent, Prompt 1 covers more ground.
- **When to use this instead:** Student pastes a stack trace or "my code doesn't work." Spawn this as a sub-mode of the coding-tutor agent. MIT base license (bramses) makes it the cleanest to redistribute.

### #3: Programming Concept Explainer (Prompt 3)
- **Why not picked:** Generic Socratic — works, but doesn't have the code-specific moves (prediction, line-tracing) that Prompt 1 builds in.
- **When to use this instead:** Pure concept questions ("what is a closure?") without code to anchor on.

### #4: Code-Reading Tutor (Prompt 4)
- **Why not picked:** Needs a code snippet to anchor on — useless for "teach me Python from scratch." Specialized.
- **When to use this instead:** Onboarding to a new codebase or open-source contribution prep.

---

## Deployment Notes for Jarvis

1. **File path:** `.claude/agents/coding-tutor.md`
2. **Adaptations needed:**
   - Add Hinglish trigger: "Mirror the student's register; if Hinglish, respond Hinglish."
   - Add "give-up override": after 3 failed attempts, give ONE structured hint (point to the file/function, not the line). Still never paste the fix.
   - Add a stack-trace branch: "If the student pastes an error message or traceback, switch to Debug-Buddy protocol — ask EXPECTED vs ACTUAL behavior first."
   - Add explicit boundary vs `code-agent`: "If the user says 'just write it for me' or is clearly trying to ship code (not learn), gently hand off to code-agent. This tutor only teaches."
3. **Tool access (suggested):** Read-only file access (so student can paste code paths); no Edit/Write — the student writes the code.
4. **Model recommendation:** sonnet for general tutoring. haiku for fast, drill-style sessions on basics.

---

## Scorecard

| Criterion | Score (1-5) | Notes |
|-----------|-------------|-------|
| Role priming clarity | 5/5 | Tone + role + self-intro contract. |
| Scope boundaries | 5/5 | Hard no-answer rule, numbered behaviors. |
| Output format guidance | 5/5 | One question at a time enforced. |
| Reasoning techniques | 5/5 | Socratic + predict + trace + analogy + hint-escalation. |
| Safety / refusal patterns | 4/5 | Strong on answer-leak; doesn't address harmful-code requests. |
| 2026 tech relevance | 4/5 | Language-agnostic, aligned with current CS-tutor research. Not agentic. |
| License-friendliness | 3/5 | Leaked GPT origin — use as behavioral reference, not for redistribution. |
| **Overall** | **31/35** | |
