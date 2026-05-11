# Public Speaking Coach — Jarvis-Picked Agent Prompt

> Selected 2026-05-11 from 4 candidates in `../agent-prompts/public-speaking-coach.md`
> Picker: prompt-picker-agent | Criteria: output quality + 2026 trend relevance + deployability

---

## Selected Prompt

**Original name:** Speech Architect (custom, structure-first)
**From library:** `data/agent-prompts/public-speaking-coach.md` -> Prompt 2
**Source:** Custom synthesis — Monroe's Motivated Sequence + classical rhetoric (ethos/pathos/logos) + TED talk patterns
**Author:** Custom for Jarvis
**License:** Public domain

### Full Prompt (verbatim)

```
You are a speech architect. The user has a speech to write or rehearse. Before they write a single line, walk them through this structure.

Step 1 — The ONE thing
Ask: "If your audience forgets everything else, what is the ONE sentence they should remember?" Refuse to proceed until they give you a single, concrete sentence (not "AI is important" but "Every company will have an AI agent on the payroll by 2027"). This is the THESIS.

Step 2 — Audience
Ask: Who is in the room? What do they already believe? What do they fear? What's the action you want them to take after the talk?

Step 3 — The Hook (first 30 seconds)
Force them to draft an opening that is one of: a story, a shocking statistic, a question, or a vivid image. NOT "Hi, my name is..." Ask: "Why would a busy person in the third row keep listening past your first 30 seconds?"

Step 4 — Structure (pick one)
- Monroe's: Attention → Need → Satisfaction → Visualization → Action
- Story arc: Setup → Conflict → Resolution → Lesson
- Rule of three: Three points, each with one example
Help them pick the right one for their thesis and audience.

Step 5 — Evidence
For each main point, ask: "What's your ONE concrete example, story, or data point? Specific names, numbers, places. Not 'studies show...' but 'In 2024, Anthropic shipped...'"

Step 6 — The Close
Ask: "Does your last line echo your first line? Does it command an action? Don't just stop — land it."

Step 7 — Cut
After they have a draft: "Read it out loud and time it. Cut 20% of the words. The 20% you don't need are the 20% your audience will tune out on."

Throughout: never write the speech for them. Ask, force, refine. They write every word.
```

---

## Why Jarvis Picked This

### Output quality drivers
- **Role priming:** "Speech architect" — frames the work as structural engineering, not wordsmithing.
- **Scope boundaries:** "Never write the speech for them. Ask, force, refine." Closes the LLM "let me draft your speech" trap door.
- **Output format:** 7-step pipeline, refuses to proceed at Step 1 until thesis is concrete (one sentence, specific, falsifiable).
- **Reasoning techniques:** Socratic + structural template selection (Monroe's / Story arc / Rule of three) + evidence specificity drill + "cut 20%" post-draft tightening.
- **Safety / refusal patterns:** Hard refusal to write prose. Forces concreteness ("not 'AI is important' but 'Every company will have an AI agent on the payroll by 2027'").

### 2026 trend relevance
- **Modern frameworks:** Monroe's Motivated Sequence is the dominant persuasive-speech framework taught in 2026 (still). Story-arc (Setup-Conflict-Resolution-Lesson) is TED-talk canonical. Rule of three is timeless.
- **Current tech references:** Embeds a 2024 timestamp ("In 2024, Anthropic shipped...") — feels current. Vendor-neutral.
- **Structured output:** Each step has a refusal-condition or success-condition. Step 7 produces a tight, timed draft.
- **Safety alignment:** No persuasion-manipulation guardrails baked in — would benefit from a "no dark patterns" rider for political/marketing speech.

### Pedagogical quality (tutoring-specific)
- **Socratic vs. answer-dumping:** Strongly Socratic for a coaching prompt. Never writes the speech. Forces the speaker to commit to thesis, hook, structure, evidence, close in order.
- **Adapts to student level:** Implicit — works for keynotes, demo days, lightning talks. Library notes it's overkill for casual toasts (use Prompt 1 for those).
- **Builds understanding vs. dependence:** Teaches the structural reflex — after one full pass, the speaker knows the questions to ask themselves on the next speech.

### Deployability
- **License:** Public domain.
- **Vendor lock:** None.
- **Jarvis adaptability:** Pair with Prompt 3 (Delivery Coach) for rehearsal, Prompt 4 (Stage Fright) for morning-of. Three-stage pipeline.

---

## Runners-up + Trade-offs

### #2: Delivery Coach (Prompt 3)
- **Why not picked:** Best at delivery feedback, but needs a draft first. Speech Architect produces the draft. Delivery Coach is Stage 2.
- **When to use this instead:** After Prompt 2 has produced a draft. Filler words, signposts, rule of three, pauses, opener/closer — ruthless rehearsal layer.

### #3: Stage Fright Manager (Prompt 4)
- **Why not picked:** Different problem — nervous-system regulation, not speech-craft. Critical for stage day but not the daily-driver coach.
- **When to use this instead:** Morning of or night before a high-stakes talk. CBT-style reframing + pre-stage routine.

### #4: Public Speaking Coach (Prompt 1, awesome-chatgpt-prompts)
- **Why not picked:** Generic, no structural enforcement. The library itself recommends layering Prompt 2 on top.
- **When to use this instead:** First conversation with someone — let them dump context. Then switch to Speech Architect for the structural work.

---

## Deployment Notes for Jarvis

1. **File path:** `.claude/agents/public-speaking-coach.md`
2. **Adaptations needed:**
   - Add Hinglish + Indian-English speaker context (Boss-relevant for pitch decks, demo days).
   - Add genre router: keynote/TED -> full 7-step. Hackathon demo day -> compress to thesis + hook + 3-slide arc + close. Wedding toast -> story-arc only.
   - Add ethics line: "If the goal is manipulation (false data, hidden agenda), refuse. Persuasion requires honesty."
   - Pair-call: at end of Stage 1, offer to hand off to Delivery Coach (Prompt 3) for rehearsal.
3. **Tool access (suggested):** File Read/Write to persist drafts and revision history under `data/speeches/{name}/v{n}.md`.
4. **Model recommendation:** sonnet (rhetoric judgment + structural rigor). opus for keynotes where the stakes are very high.

---

## Scorecard

| Criterion | Score (1-5) | Notes |
|-----------|-------------|-------|
| Role priming clarity | 5/5 | "Architect" frame is sharp. |
| Scope boundaries | 5/5 | 7-step pipeline; never-write-it rule. |
| Output format guidance | 5/5 | Sequenced refusal conditions, draft tightening at end. |
| Reasoning techniques | 5/5 | Socratic + structural template + concreteness drill. |
| Safety / refusal patterns | 3/5 | No anti-manipulation guardrail (add one). |
| 2026 tech relevance | 5/5 | Monroe + TED arc remain canonical 2026 frameworks. |
| License-friendliness | 5/5 | Public domain. |
| **Overall** | **33/35** | |
