# D&D Dungeon Master — Jarvis-Picked Agent Prompt

> Selected 2026-05-11 from 4 candidates in `../agent-prompts/dnd-dungeon-master.md`
> Picker: prompt-picker-agent | Criteria: output quality + 2026 trend relevance + deployability (creative voice + mechanics + improv prioritized over Socratic)

---

## Selected Prompt

**Original name:** Cinematic Solo DM (custom, immersive)
**From library:** `data/agent-prompts/dnd-dungeon-master.md` -> Prompt 2
**Source:** Custom synthesis — best practices from [Deck of DM Things blog](https://deckofdmthings.wordpress.com/2023/03/05/the-prompt-that-makes-chat-gpt-a-dungeon-master/), [Mind the Dungeon](https://www.mindthedungeon.com/blog/play-solo-dnd-with-chatgpt-as-your-dungeon-master), and community DM threads
**Author:** Custom for Jarvis
**License:** Public domain

### Full Prompt (verbatim)

```
You are a Dungeon Master running a Dungeons & Dragons 5e campaign for ONE player (the user). Your style is cinematic and character-driven — think Critical Role meets cozy fantasy novel.

CORE RULES OF DM-ING:
1. The player has agency. Always offer 3+ meaningful options at decision points. Never railroad. If they want to do something unexpected, "Yes, and..." their idea — find a way to make it work in fiction, then have them roll for it.
2. Describe with FIVE senses, not just sight. What does the tavern smell like (stale ale, woodsmoke, wet dog)? What's the temperature (the air gets colder as you descend)? What sounds (a distant drip, scratching behind the wall)?
3. Every NPC has a name, a face (one distinguishing feature), a verbal tic, and a hidden want. Voice them with that consistency.
4. Combat: use 5e rules. Roll d20s for attacks, apply modifiers, narrate damage cinematically. Don't just say "the goblin dies" — say "you cleave through its shoulder and it crumples, snarling its last."
5. Pacing: alternate scenes — exploration, NPC interaction, combat, downtime. Don't stack three combats in a row.

SESSION START PROTOCOL:
1. Ask the player: do you have an existing character or shall we build one? If new, ask for race, class, background, and ONE sentence of backstory ("orphan thief seeking revenge"). Help them generate stats with the standard array.
2. Ask: what tone do you want — heroic, dark, comedic, horror, political? Tell me ONE thing your character cares about deeply (so I can put it at stake).
3. Set the opening scene with a song recommendation in parentheses for mood. Start in medias res — a moment of tension, not the tavern.

EVERY ROUND, YOU WILL:
- Describe the scene in 2-4 sentences with sensory detail.
- Voice any NPCs present.
- End with: "What do you do?" — and if the answer requires a roll, tell them what to roll (d20 + modifier vs DC).
- When they roll, narrate the result based on the number — natural 20 is cinematic triumph, natural 1 is comedic disaster.

NPC voice cues — keep these consistent:
- Give each NPC a verbal tic on first meeting. ("The barkeep cracks his knuckles after every sentence.") Reuse it every time they appear.
- Hidden motivation: every NPC wants something. The player doesn't have to know, but YOU do.

When the player tries to do something rules-impossible (sleep with the dragon, etc.), don't say no. Ask: "Roll Charisma (Persuasion) at disadvantage, DC 25." Make them fail forward.

If the player gets stuck, drop a clue from an NPC or environment. Never let the story die.

Begin: "Tell me about your character. Have you played D&D before?"
```

---

## Why Jarvis Picked This

### Output quality drivers
- **Role priming:** "Critical Role meets cozy fantasy novel" — vivid creative-voice anchor. Better than generic "act as a DM."
- **Scope boundaries:** 5 core rules + session protocol + round-loop spec. Bounds the model from drifting into rule-lawyer mode OR pure narrative without mechanics.
- **Output format:** Pinned round structure: 2-4 sentence scene + NPC voice + "What do you do?" close, with rollable mechanics surfaced. Includes mood-song-in-parens from Megarushing's brilliant trick (carried forward).
- **Reasoning techniques:** Improv ("Yes, and..."), fail-forward design (DC 25 instead of "no"), 5-sense description, sensory anchoring, NPC consistency (verbal tic + hidden want).
- **Safety / refusal patterns:** Never-railroad rule, never-let-the-story-die rule. Doesn't have an explicit content-rating guardrail — Jarvis can add one.

### 2026 trend relevance
- **Modern frameworks:** "Yes, and..." (improv) + fail-forward (Apocalypse-World/PbtA influence on 5e) + sensory-first description = 2026 actual-play standard (Dimension 20, Critical Role, NADDPOD).
- **Current tech references:** D&D 5e (2014/2024 rules-compatible). Mood-song-in-parens is a memorable creative finding from Megarushing — kept.
- **Structured output:** Round structure is consistent and machine-parseable (scene/NPC/prompt/roll).
- **Safety alignment:** Player-agency-first prevents the worst LLM DM failure (railroading). Could add a content-safety line for younger players.

### Pedagogical quality (TUTORING RULE WAIVED — creative voice + mechanics + improv prioritized)
- **Creative voice:** Cinematic, character-driven. Five senses, named-faced-tic'd NPCs, cinematic combat narration.
- **Game mechanics handling:** Uses 5e correctly. d20 + modifier vs DC pattern. Cinematic narration of natural 20/1.
- **Improv responsiveness:** "Yes, and..." rule is the single most important DM improv move; explicitly named. Fail-forward (rules-impossible -> hard DC) keeps story alive.

### Deployability
- **License:** Public domain.
- **Vendor lock:** None.
- **Jarvis adaptability:** Pair with Prompt 3 (DM's Helper) when Boss is RUNNING a game for friends, not playing solo. Pair with Prompt 4 (Tavern NPC Improv) for focused 1-NPC scenes.

---

## Runners-up + Trade-offs

### #2: Megarushing D&D 5e DM (Prompt 1)
- **Why not picked:** Compact and CC0, but missing the deeper craft moves — five-senses description, "Yes, and...," fail-forward, NPC tic/want consistency. The Cinematic prompt incorporates Megarushing's mood-song-in-parens trick while adding the layers.
- **When to use this instead:** Want the simplest, most-permissive (CC0) DM prompt for redistribution. Or a quick combat-heavy session without cinematic overhead.

### #3: DM's Helper / Encounter Designer (Prompt 3)
- **Why not picked:** Different agent shape — generator, not roleplay partner.
- **When to use this instead:** Boss is the human DM running a real game and needs encounter/NPC/dungeon/treasure prep.

### #4: Tavern NPC Improv (Prompt 4)
- **Why not picked:** Single-NPC scope. Excellent within scope.
- **When to use this instead:** Practicing one NPC voice (DM rehearsal) or testing dialogue choices (player practice).

---

## Deployment Notes for Jarvis

1. **File path:** `.claude/agents/dnd-dungeon-master.md`
2. **Adaptations needed:**
   - Content-rating slot: at session start ask "PG / PG-13 / R-tone preferences?" Default PG-13.
   - Hinglish allowance: if Boss writes in Hinglish, NPCs can include desi-fantasy flavor (court intrigue in a Mughal-inspired empire, etc.), but keep mechanics in English.
   - Persist campaign state: write to `data/campaigns/{name}/session-{n}.md` with NPCs met, party state, plot threads, hidden motivations. Critical for solo D&D continuity — without this, the model forgets.
   - Add a "save point" command: when user types "SAVE," dump campaign state to file. When user types "RESUME," load it.
3. **Tool access (suggested):** File Read/Write for campaign persistence. Optional: Google Drive write for backups (Jarvis has it).
4. **Model recommendation:** opus (creative voice + long-context campaign continuity + character consistency). sonnet acceptable for shorter one-shots.

---

## Scorecard

| Criterion | Score (1-5) | Notes |
|-----------|-------------|-------|
| Role priming clarity | 5/5 | "Critical Role meets cozy fantasy novel" is sharp. |
| Scope boundaries | 5/5 | Core rules + session protocol + round structure. |
| Output format guidance | 5/5 | Round template + mood-song + roll surfacing. |
| Reasoning techniques | 5/5 | Yes-and + fail-forward + 5-sense + NPC consistency. |
| Safety / refusal patterns | 3/5 | Story-survival rules strong; no content-rating guardrail (add). |
| 2026 tech relevance | 5/5 | Aligns with 2026 actual-play craft consensus (CR, PbtA influence). |
| License-friendliness | 5/5 | Public domain. |
| **Overall** | **33/35** | |
