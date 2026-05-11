# Writing Tutor — Jarvis-Picked Agent Prompt

> Selected 2026-05-11 from 4 candidates in `../agent-prompts/writing-tutor.md`
> Picker: prompt-picker-agent | Criteria: output quality + 2026 trend relevance + deployability

---

## Selected Prompt

**Original name:** Socratic Writing Tutor (adapted from bramses)
**From library:** `data/agent-prompts/writing-tutor.md` -> Prompt 1
**Source:** [bramses/chatgpt-md-templates](https://github.com/bramses/chatgpt-md-templates/blob/main/socratic-tutor.md) — Socratic base + writing specialization
**Author:** Bram Adams (Socratic frame); writing specialization custom
**License:** MIT (base template)

### Full Prompt (verbatim)

```
You are a writing tutor that always responds in the Socratic style. You *never* rewrite the student's prose for them, but always ask just the right question to help them see what to revise themselves.

Process for any draft the student shares:
1. First read silently. Then ask: "In one sentence, what are you trying to say here? What's the ONE thing you want the reader to take away?" Wait for their answer.
2. Compare their stated intent to what's on the page. Ask: "Where in the draft does that idea land hardest? Where does it get lost?"
3. Have them identify their own strongest sentence and weakest sentence. Ask them WHY each is strong or weak.
4. For weak passages, ask narrowing questions: "Is the problem with the verb, the noun, or the structure?" Make them point to the exact word.
5. Never edit the sentence yourself. If they're stuck, give them two options and let them choose: "Would 'X' or 'Y' fit better here? Why?"
6. End every session with: "What's one writing habit you'll watch for in your next draft?"

Tune to the student's level. A 10th grader gets simpler questions than an MFA candidate.
```

---

## Why Jarvis Picked This

### Output quality drivers
- **Role priming:** "Writing tutor in Socratic style" — clear.
- **Scope boundaries:** Absolute "never rewrite" rule. The two-option fallback (Rule 5) is a precise safety valve for stuck students.
- **Output format:** Process is a 6-step pipeline — first read, then intent-vs-page comparison, then strongest/weakest identification.
- **Reasoning techniques:** Socratic + intent-vs-execution gap diagnosis + targeted narrowing questions (verb/noun/structure) + multiple-choice fallback for stuck moments.
- **Safety / refusal patterns:** Hard refusal on rewriting. Two-option fallback prevents answer-leak escalation.

### 2026 trend relevance
- **Modern frameworks:** Intent-vs-execution gap is the modern editorial diagnostic move. Strongest/weakest sentence identification is a workshop staple now built into AI prompts.
- **Current tech references:** Vendor-neutral.
- **Structured output:** Step-numbered process; session-end question pins a takeaway.
- **Safety alignment:** Level-tuning ("10th grader vs MFA candidate") prevents condescension and overcomplication.

### Pedagogical quality (tutoring-specific)
- **Socratic vs. answer-dumping:** Strongly Socratic. Best in class for writing because it specifically refuses to edit prose — the biggest failure mode in LLM writing tutors.
- **Adapts to student level:** Explicit closing instruction.
- **Builds understanding vs. dependence:** Forces editorial judgment. Step 3 (identify own strongest/weakest) builds the writer's critic, not just polishes one essay.

### Deployability
- **License:** MIT base — clean.
- **Vendor lock:** None.
- **Jarvis adaptability:** Generalizes across essay types. Add College-Essay branch (Prompt 4) for high-school seniors. Add "polish mode" handoff to Prompt 3 for after-teaching line edits.

---

## Runners-up + Trade-offs

### #2: College Essay Coach (Prompt 4)
- **Why not picked:** Highly genre-specific (Common App / supplemental). Excellent within scope, but a default writing tutor needs to handle blog posts, essays, term papers, and personal statements equally.
- **When to use this instead:** Boss helping a high-school senior with Common App essays. Sharper than Prompt 1 for that exact use case because it bakes in the "scene vs summary" and "trying-to-sound-mature voice" drills.

### #3: Anthropic Socratic Sage (Prompt 2)
- **Why not picked:** General-purpose Socratic — works, but lacks the writing-specific moves (strongest/weakest, verb/noun/structure narrowing).
- **When to use this instead:** Argumentative essay where the thesis itself is the problem, not the prose.

### #4: Anthropic Prose Polisher (Prompt 3)
- **Why not picked:** Anti-pedagogical — it rewrites. Useful AFTER the teaching is done.
- **When to use this instead:** Boss's own writing when he wants quick edits, not learning.

---

## Deployment Notes for Jarvis

1. **File path:** `.claude/agents/writing-tutor.md`
2. **Adaptations needed:**
   - Add Hinglish register and mirror student's language.
   - Add genre router: if student says "Common App" / "personal statement" -> branch to college-essay drills. If "thesis" / "argument" -> add Socratic-Sage thesis-stress moves.
   - Add explicit handoff: "If user says 'just edit it' or 'polish this' -> tell them I teach, but they can use the editor-proofreader agent for polish."
   - Add a draft-comparison capability: support side-by-side draft v1 vs v2 with "what changed and why" prompts.
3. **Tool access (suggested):** File Read (to load drafts from disk). No Write — student writes every word.
4. **Model recommendation:** sonnet (good prose taste + patience). opus for MFA-level work.

---

## Scorecard

| Criterion | Score (1-5) | Notes |
|-----------|-------------|-------|
| Role priming clarity | 5/5 | Tutor + Socratic + no-rewrite. |
| Scope boundaries | 5/5 | Hard no-edit rule; two-option fallback bounded. |
| Output format guidance | 5/5 | 6-step pipeline + session-end question. |
| Reasoning techniques | 5/5 | Intent-vs-execution + strongest/weakest + narrowing. |
| Safety / refusal patterns | 4/5 | Strong on rewrite refusal; doesn't address plagiarism / AI-disclosure norms (add). |
| 2026 tech relevance | 4/5 | Mature editorial methodology, vendor-neutral. |
| License-friendliness | 5/5 | MIT. |
| **Overall** | **33/35** | |
