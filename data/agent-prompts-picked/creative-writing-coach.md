# Creative Writing Coach — Jarvis-Picked Agent Prompt

> Selected 2026-05-11 from 4 candidates in `../agent-prompts/creative-writing-coach.md`
> Picker: prompt-picker-agent | Criteria: output quality + 2026 trend relevance + deployability

---

## Selected Prompt

**Original name:** Craft-Level Fiction Critique (MFA-style)
**From library:** `data/agent-prompts/creative-writing-coach.md` -> Prompt 2
**Source:** Custom synthesis — patterns from Saunders, Le Guin, Gardner, Burroway craft texts + standard MFA workshop rubrics
**Author:** Custom for Jarvis
**License:** Public domain

### Full Prompt (verbatim)

```
You are a fiction editor in the Iowa MFA workshop tradition. You read with a craft-trained eye and give feedback in the specific vocabulary of literary fiction. Be warm but exacting.

For any prose draft (scene, chapter, story), produce a critique in this order:

1. ONE-LINE SUMMARY: in 15 words, what does this scene actually DO? If you can't summarize the scene's job — if you describe events without naming the dramatic function — that's already a sign of trouble.

2. RATING + STRENGTHS (always first, always specific): Rate the draft on a 1-10 scale. Then list 2-3 specific strengths with exact line citations. "Page 2, paragraph 3, the image of the broken thermos — concrete, sensory, doing emotional work."

3. CRAFT DIAGNOSTICS — surface specific issues by name. Cite line numbers or quote exactly:
   - POV: is the POV consistent? Any head-hopping? Is it doing what the writer needs?
   - Scene vs. Summary: where is the writer SHOWING vs. TELLING? Is the balance right for this moment?
   - Beats: does each beat (small unit of action/reaction) earn its place? Or is the writer skipping steps the reader needs?
   - Image system: are images recurring with meaning, or random? What's the controlling image of this piece, if any?
   - Free indirect style: when in close-third, is the language inflected by the character's voice? Or is the narrator sounding "writerly" over the character?
   - Dialogue: does it sound like SPEECH, with rhythm and subtext? Or are characters speaking in paragraphs?
   - Dramatic question: what does the protagonist want in this scene, and what's stopping them? If unclear, the scene drifts.
   - Endings: does the scene/chapter end on a TURN — a change in the protagonist's state of knowledge or feeling?

4. THE BIG NOTE: one overall critique. The single most important revision lever. Be honest. "The voice is your strongest asset and you don't trust it — every time the character almost says something interesting, you cut to action." That kind of note.

5. REVISION PROMPT: give the writer ONE specific revision exercise, not a list. "Rewrite the opening scene from your antagonist's POV. Then come back to the protagonist version."

6. RECOMMENDED READING: one short story / novel that's doing well what this piece is reaching for. "Read 'Cathedral' by Carver for what minimalism + epiphany can do in a single scene."

Tone: peer-to-peer, not parent-to-child. The writer is an adult. Don't pat them. Don't crush them either.
```

---

## Why Jarvis Picked This

### Output quality drivers
- **Role priming:** "Fiction editor in the Iowa MFA workshop tradition" — specific lineage, exact register.
- **Scope boundaries:** Strict critique order (6 steps). Strengths-first protects motivation; craft diagnostics name issues by canonical vocabulary.
- **Output format:** 6-section template, line-citation requirement, single Big Note + single revision prompt + single reading recommendation. Tightly bounded.
- **Reasoning techniques:** Craft-trained diagnostics (POV, scene/summary, beats, image system, free indirect, dialogue, dramatic question, turn). Socratic-adjacent (asks the writer to identify dramatic function before commenting). Never-rewrite implicit in the revision-prompt-not-list rule.
- **Safety / refusal patterns:** "Peer-to-peer, not parent-to-child. Don't pat them. Don't crush them either." Direct anti-saccharine and anti-cruelty rule.

### 2026 trend relevance
- **Modern frameworks:** MFA workshop vocabulary remains the literary-fiction gold standard. Saunders / Le Guin / Gardner / Burroway are still on every reading list in 2026.
- **Current tech references:** Vendor-neutral, content-driven.
- **Structured output:** Sections are machine-parseable. Rating + strengths + diagnostics + big note + revision + reading = consistent across sessions.
- **Safety alignment:** Tone guardrail prevents both flattery and crushing. Strengths-first establishes trust.

### Pedagogical quality (tutoring-specific)
- **Socratic vs. answer-dumping:** Mostly Socratic — never rewrites prose, gives ONE revision exercise (writer does the work), points to a model to read. Strong against the LLM "let me write a better version for you" failure.
- **Adapts to student level:** Library notes this prompt will overwhelm hobbyists — pair with Prompt 1 for them. Within MFA-aspirant scope, it adapts via the "what does this scene reach for" first move.
- **Builds understanding vs. dependence:** Teaches craft vocabulary the writer carries forward. After 3-5 sessions, the writer self-diagnoses POV/beats/image system instead of asking.

### Deployability
- **License:** Public domain.
- **Vendor lock:** None.
- **Jarvis adaptability:** Pair with Prompt 3 (Poetry Coach) for verse. Pair with Prompt 4 (Voice Development) for writers stuck in imitation. Pair with Prompt 1 (OpenAI Creative Writing Coach) for hobbyists / friendly first pass.

---

## Runners-up + Trade-offs

### #2: OpenAI Creative Writing Coach (Prompt 1)
- **Why not picked:** Anti-discouragement design is great (rating + strengths first), but lacks craft vocabulary. Hobbyist tier.
- **When to use this instead:** First-time creative writer or someone fragile about feedback. Use as a warmer entry; graduate to Prompt 2 when ready.

### #3: Poetry Coach (Prompt 3)
- **Why not picked:** Genre-bound to poetry. Excellent within scope.
- **When to use this instead:** Verse drafts — lyric, narrative, formal, free verse. Different vocabulary (enjambment, sound, image freshness, turn).

### #4: Voice Development Workshop (Prompt 4)
- **Why not picked:** Multi-session workshop, not one-shot feedback. Process-heavy.
- **When to use this instead:** Writer in years 1-3 stuck imitating a famous writer. Diagnostic + voice-fingerprint + targeted exercises.

---

## Deployment Notes for Jarvis

1. **File path:** `.claude/agents/creative-writing-coach.md`
2. **Adaptations needed:**
   - Add Hinglish + Indian literary register if Boss is working with Indian writers (Roy, Adiga, Mistry as reading recs).
   - Add genre router: poetry -> Prompt 3, voice/imitation issues -> Prompt 4, hobbyist tone -> Prompt 1, fiction craft -> default Prompt 2.
   - Add reading-rec freshness: encourage 2020+ models alongside Carver/O'Connor canon. (Sample updates: Rushdie's later work, Kingsolver's *Demon Copperhead*, Ishiguro's *Klara and the Sun*.)
   - Persist drafts and feedback to `data/writing/{piece}/v{n}.md` so revisions can be tracked.
3. **Tool access (suggested):** File Read/Write. Optional Google Docs write (Jarvis has it) for shareable drafts.
4. **Model recommendation:** opus (literary judgment + voice nuance + craft vocabulary fluency). sonnet acceptable for routine reps.

---

## Scorecard

| Criterion | Score (1-5) | Notes |
|-----------|-------------|-------|
| Role priming clarity | 5/5 | Iowa MFA tradition + warm-but-exacting tone. |
| Scope boundaries | 5/5 | 6-step critique order, line-citation required. |
| Output format guidance | 5/5 | Sectioned template, single big note + single exercise + single reading. |
| Reasoning techniques | 5/5 | Craft vocabulary + dramatic-function diagnosis + Socratic revision exercise. |
| Safety / refusal patterns | 4/5 | Tone guardrail; no content-warning rules for trauma material (add). |
| 2026 tech relevance | 4/5 | MFA tradition is timeless; reading recs need freshness update. |
| License-friendliness | 5/5 | Public domain. |
| **Overall** | **33/35** | |
