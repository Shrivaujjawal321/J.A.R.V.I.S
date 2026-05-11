# Screenwriter — Jarvis-Picked Agent Prompt

> Selected 2026-05-11 from 4 candidates in `../agent-prompts/screenwriter.md`
> Picker: prompt-picker-agent | Criteria: output quality + 2026 trend relevance + deployability

---

## Selected Prompt

**Original name:** Screenplay-Formatted Scene Writer
**From library:** `data/agent-prompts/screenwriter.md` -> Prompt 3
**Source:** Composite — based on industry-standard screenplay formatting (WGA / Final Draft conventions), framing adapted from [Anthropic Storytelling Sidekick](https://docs.anthropic.com/en/prompt-library/storytelling-sidekick)
**Author:** Composite original; format conventions are industry-standard
**License:** Composite original prompt (effectively CC0 for Jarvis use)

### Full Prompt (verbatim)

```
You are a professional screenwriter. Write scenes in proper feature-screenplay format following these strict conventions:

FORMAT RULES:
- Slug line: INT./EXT. LOCATION - TIME (e.g., "INT. SUBWAY CAR - NIGHT")
- Action lines: present tense, third person, ≤4 lines per paragraph. Visual only — never describe what cannot be filmed.
- Character cue: CAPS, centered (you can left-align in text output)
- Dialogue: under the character cue
- Parentheticals: only when essential for delivery (e.g., "(whispering)"). Never use for emotion the actor can perform.
- Transitions (CUT TO:, SMASH CUT TO:): sparingly, only for effect.

CRAFT RULES:
- Show, don't tell. Action lines describe what we see and hear, never what characters think.
- No on-the-nose dialogue. Characters rarely say what they actually mean.
- Subtext over text. The conflict is what's not being said.
- Enter scenes late, leave early.
- Every scene must have a turn — something must change between the start and end.
- Limit each scene to one core conflict or beat.

When given a scene description or beat, output formatted screenplay pages only — no commentary, no markdown headers, no explanation.
```

---

## Why Jarvis Picked This

### Output quality drivers
- **Role priming:** "Professional screenwriter" + named industry conventions (WGA / Final Draft).
- **Scope boundaries:** Scene-level output only; banned commentary/headers.
- **Output format:** Pinned hard — slug line, action lines, character cues, dialogue, parentheticals, transitions. The most prescriptive format spec in the library.
- **Reasoning techniques:** Implicit via craft rules (every scene must have a turn; enter late, leave early).
- **Safety / refusal patterns:** Format anti-patterns (no thoughts in action; parentheticals reserved). No content-safety, but screenwriting rarely needs it at the prompt layer.
- **Examples / few-shot:** Inline slugline example ("INT. SUBWAY CAR - NIGHT") and parenthetical example ("(whispering)").

### 2026 trend relevance
- **Modern frameworks:** Format rules match WGA/Final Draft; craft rules match what working showrunners teach in 2024-2026.
- **Current tech references:** Plain-text screenplay format is parseable by Highland, Fountain, Final Draft import.
- **Structured output:** Output is directly importable into screenplay tools — composable with downstream production agents.
- **Safety alignment:** Strong anti-amateur-pattern rules (anti-on-the-nose, anti-overuse of parentheticals).

### Deployability
- **License:** Composite original prompt — effectively unrestricted for Jarvis. Industry-standard formatting is not copyrightable.
- **Vendor lock:** None.
- **Jarvis adaptability:** High. Pairs with Save the Cat (Prompt 2) for outline-then-draft workflow.

---

## Runners-up + Trade-offs

### #2: Save the Cat Beat Sheet Architect (Prompt 2)
- **Why not picked:** Excellent feature-outline tool with 15-beat scaffold, but it stops at the blueprint — does not write scenes. Wire as `screenwriter-outliner` sibling agent for the pre-draft pass.
- **When to use this instead:** Outlining a feature before drafting any pages.

### #3: Storytelling Sidekick (Prompt 4)
- Useful for early-stage brainstorming and "what if" exploration. Conversational, not deliverable-shaped — wire as `story-collaborator` agent for pre-outline ideation.

---

## Deployment Notes for Jarvis

1. **File path:** `.claude/agents/screenwriter.md`
2. **Adaptations needed:**
   - Add Fountain markup output option (so the script imports clean into Highland / Final Draft).
   - Optional: pair with outliner agent in a chained workflow (Save the Cat -> Scene Writer).
   - Add Indian/regional setting awareness if Boss is writing scripts in that context.
3. **Tool access (suggested):** Read (outline/beats from `data/notes/`), Write (formatted pages to `data/notes/scripts/`).
4. **Model recommendation:** opus (best for dialogue subtext and craft); sonnet for first drafts.

---

## Scorecard

| Criterion | Score (1-5) | Notes |
|-----------|-------------|-------|
| Role priming clarity | 5/5 | Professional screenwriter, named conventions. |
| Scope boundaries | 5/5 | Scene-level, no commentary. |
| Output format guidance | 5/5 | Format rules + craft rules. |
| Reasoning techniques | 4/5 | Craft rules act as implicit CoT. |
| Safety / refusal patterns | 4/5 | Strong anti-amateur-pattern rules. |
| 2026 tech relevance | 4/5 | Fountain-importable plain text. |
| License-friendliness | 5/5 | Composite original; industry format is open. |
| **Overall** | **32/35** | |
