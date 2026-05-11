# Novelist — Jarvis-Picked Agent Prompt

> Selected 2026-05-11 from 4 candidates in `../agent-prompts/novelist.md`
> Picker: prompt-picker-agent | Criteria: output quality + 2026 trend relevance + deployability

---

## Selected Prompt

**Original name:** Chapter-by-Chapter Drafting Partner
**From library:** `data/agent-prompts/novelist.md` -> Prompt 4
**Source:** Composite — based on community practice patterns (Bookfox, IrisMarshEdits) and standard novel writing methodology
**Author:** Composite original
**License:** Composite original prompt (effectively CC0 for Jarvis use)

### Full Prompt (verbatim)

```
You are a novelist drafting one chapter at a time from an outline. Adhere to these craft constraints on every chapter:

POV & VOICE
- Stay in the chosen POV (first / close third / third omniscient). Never head-hop within a scene.
- Match the established character voice in dialogue and internal monologue (I will provide a voice sample).
- Match the established world rules and continuity (I will provide a bible).

SCENE STRUCTURE (Dwight Swain)
- Each scene has: a clear goal (what the POV character wants), conflict (what blocks them), and a disaster or shift (what changes by scene's end).
- Each sequel beat (reflection between scenes) has: reaction, dilemma, decision.

PROSE CRAFT
- Show, don't tell. Externalize internal states through action, dialogue, and physical sensation.
- Sensory grounding: each scene must include at least 3 senses beyond sight.
- Cut filter words ("she felt", "he saw", "she realized") unless intentional.
- Vary sentence rhythm. Avoid 3 sentences in a row of the same length.
- Dialogue beats over speech tags ("said" is invisible; use action beats to attribute and characterize).

DELIVERABLE
- Word count target: [SPECIFY, default 2500-4000]
- End the chapter on a hook, decision, or unanswered question that pulls into the next chapter.
- After the chapter prose, append: a one-sentence chapter summary, the bible updates (any new world facts introduced), and any continuity flags ("This contradicts X from chapter Y").
```

---

## Why Jarvis Picked This

### Output quality drivers
- **Role priming:** "Novelist drafting one chapter at a time from an outline" — narrow, deliverable-shaped.
- **Scope boundaries:** Per-chapter scope; explicit POV, voice, and bible inputs; word count target.
- **Output format:** Chapter prose + one-sentence summary + bible updates + continuity flags. Memory-friendly across sessions.
- **Reasoning techniques:** Dwight Swain's scene/sequel structure acts as embedded CoT per scene.
- **Safety / refusal patterns:** Continuity-flag mechanism ("This contradicts X from chapter Y") — explicit anti-fabrication for world-consistency.
- **Examples / few-shot:** Filter-word examples ("she felt"), continuity-flag phrasing.

### 2026 trend relevance
- **Modern frameworks:** Combines Swain (classic) with modern long-context LLM patterns (bible feeding, continuity flags, session-to-session memory).
- **Current tech references:** "Bible" and "voice sample" feed cleanly into 1M-context Claude workflows — exactly the pattern that distinguishes 2026 novel drafting from 2023 hallucination-prone drafts.
- **Structured output:** Prose + structured metadata (summary, bible updates, flags) parses for downstream archival.
- **Safety alignment:** Strong anti-head-hop, anti-filter-word, anti-fabrication continuity rules.

### Deployability
- **License:** Composite original — unrestricted for Jarvis.
- **Vendor lock:** None.
- **Jarvis adaptability:** Highest. Designed for repeated chapter-by-chapter sessions with persistent bible — fits Jarvis's file-based memory perfectly.

---

## Runners-up + Trade-offs

### #2: Three-Act Novel Architect (Prompt 2)
- **Why not picked:** Excellent outline-first tool with 15-beat scaffold, but it stops at the blueprint — does not draft prose. Wire as `novelist-outliner` sibling agent for the pre-draft pass.
- **When to use this instead:** Outlining a novel before drafting any chapters.

### #3: Storytelling Sidekick (Prompt 3)
- Anthropic-published collaborative brainstorming tool. Wire as `story-collaborator` agent for mid-draft unsticking.

---

## Deployment Notes for Jarvis

1. **File path:** `.claude/agents/novelist.md`
2. **Adaptations needed:**
   - Bible storage path: `data/notes/novels/{slug}/bible.md` (auto-load on session start).
   - Chapter archive path: `data/notes/novels/{slug}/chapters/`.
   - Voice-sample slot pulled from project memory.
   - Add Hindi/Hinglish dialogue option if Boss writes regional fiction.
3. **Tool access (suggested):** Read (bible, prior chapters), Write (chapter to archive, append bible updates), Edit (continuity flag follow-ups).
4. **Model recommendation:** opus (best for sustained voice + craft); sonnet for first-draft volume.

---

## Scorecard

| Criterion | Score (1-5) | Notes |
|-----------|-------------|-------|
| Role priming clarity | 5/5 | Chapter-by-chapter novelist, outline-driven. |
| Scope boundaries | 5/5 | Per-chapter, POV, bible, word count. |
| Output format guidance | 5/5 | Prose + summary + bible-updates + flags. |
| Reasoning techniques | 5/5 | Swain scene/sequel structure embedded. |
| Safety / refusal patterns | 5/5 | Continuity flags + anti-head-hop. |
| 2026 tech relevance | 5/5 | Long-context bible + session memory. |
| License-friendliness | 5/5 | Composite original. |
| **Overall** | **35/35** | |
