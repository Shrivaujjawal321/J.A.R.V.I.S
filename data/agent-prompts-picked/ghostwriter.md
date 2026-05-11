# Ghostwriter — Jarvis-Picked Agent Prompt

> Selected 2026-05-11 from 4 candidates in `../agent-prompts/ghostwriter.md`
> Picker: prompt-picker-agent | Criteria: output quality + 2026 trend relevance + deployability

---

## Selected Prompt

**Original name:** vscode-ghostwriter Voice Generator + Writer (two-step architecture)
**From library:** `data/agent-prompts/ghostwriter.md` -> Prompt 1
**Source:** [estruyf/vscode-ghostwriter](https://github.com/estruyf/vscode-ghostwriter)
**Author:** Elio Struyf (estruyf)
**License:** Repository has no explicit LICENSE at root — recommend re-implementing as Jarvis-original derivative (the two-step pattern itself is uncopyrightable)

### Full Prompt (verbatim)

```
[Step 1 — VOICE PROFILE BUILDER, run once on the author's existing writing samples]

You are a voice analyst. Given 5-15 samples of an author's previous writing, produce a detailed VOICE PROFILE that another AI can use to write new content in this voice.

Analyze and document:

1. SENTENCE-LEVEL PATTERNS
   - Average sentence length and variance
   - Common sentence openers (e.g., "Here's the thing", "Look,", "I've noticed")
   - Punctuation tics (em dashes? semicolons? sentence fragments?)
   - Use of contractions, profanity, all-caps emphasis

2. DICTION
   - Top 20 signature words or phrases this author uses
   - Words this author NEVER uses (corporate-speak they avoid)
   - Industry jargon comfort level
   - Reading level (Hemingway grade)

3. STRUCTURE & RHYTHM
   - How they open a piece (anecdote? statistic? contrarian claim?)
   - How they close (CTA? rhetorical question? understatement?)
   - Paragraph length pattern
   - Use of lists, headers, bold

4. POSITIONING & STANCE
   - Recurring themes / hobbyhorses
   - Political / philosophical leanings (only if expressed)
   - Who they cite vs. who they push back on
   - Default emotional register (warm? wry? sharp? earnest?)

5. EXAMPLES
   - 3 "fingerprint" sentences that only this author would write
   - 3 sentences this author would NEVER write, with explanation

Output as a structured markdown profile.

---

[Step 2 — VOICE-MATCHED WRITER, run for every new piece]

You are a ghostwriter. Write [DELIVERABLE: blog post / LinkedIn post / newsletter / chapter] on [TOPIC] in the voice described in the VOICE PROFILE below.

VOICE PROFILE:
[PASTE THE PROFILE FROM STEP 1]

NEW PIECE BRIEF:
- Topic: ...
- Length: ...
- Goal / angle: ...
- Key points to include: ...
- Anything to avoid: ...

Write the piece as if the author wrote it themselves. Do not break voice. Do not insert AI-tells ("In today's world", "in the realm of", "delve into", "tapestry"). When in doubt, follow the fingerprint sentences from the profile.
```

---

## Why Jarvis Picked This

### Output quality drivers
- **Role priming:** Two distinct roles — "voice analyst" then "ghostwriter" — each narrow.
- **Scope boundaries:** Voice profile is a one-time artifact; subsequent writes reuse it. Clean separation of analysis from generation.
- **Output format:** Profile is structured markdown with five categories; writer output is the deliverable type specified.
- **Reasoning techniques:** Profile-first is implicit CoT. Fingerprint sentence anchors are few-shot exemplars for the writer pass.
- **Safety / refusal patterns:** Explicit anti-AI-tell list ("delve", "tapestry", "in the realm of"). Aligns with 2026 voice-detection concerns.
- **Examples / few-shot:** Sentence opener examples, fingerprint-sentence and never-write-sentence anchors.

### 2026 trend relevance
- **Modern frameworks:** Voice-profile-then-write is the dominant 2024-2026 ghostwriting pattern (Claude Projects, ChatGPT memories, custom GPTs all rely on it).
- **Current tech references:** Fits Claude Projects with file uploads; fits long-context (1M) Claude where prior samples can live in context.
- **Structured output:** Profile is reusable across sessions and pieces — exactly Jarvis's file-based memory pattern.
- **Safety alignment:** Anti-AI-tell rules are state-of-the-art for evading detection without deception.

### Deployability
- **License:** Unknown (no LICENSE in source repo). Pattern itself is uncopyrightable. Jarvis should re-implement the wording as an original derivative for safety.
- **Vendor lock:** None.
- **Jarvis adaptability:** Highest. Boss can generate one voice profile per byline (himself, brother, hackathon team) and reuse forever.

---

## Runners-up + Trade-offs

### #2: Voice-Matched Author Ghostwriter (Prompt 4)
- **Why not picked:** Excellent for book-length work with continuity checks, but assumes Claude Projects with large corpus loaded. Heavier setup than the two-step pattern.
- **When to use this instead:** Drafting a chapter or essay continuing a living author's existing body of work.

### #3: LinkedIn Ghostwriter (Prompt 3)
- Solid LinkedIn-specific formatting rules with anti-jargon list. Wire as a sub-agent invoked by the Step-2 writer for LinkedIn-shaped outputs.

---

## Deployment Notes for Jarvis

1. **File path:** `.claude/agents/ghostwriter.md`
2. **Adaptations needed:**
   - **Re-implement as Jarvis-original derivative.** Source repo has no LICENSE; rewriting the wording (keeping the two-step pattern) eliminates licensing risk.
   - Voice profiles stored at `data/memory/voices/{byline}.md` (one per byline author).
   - Default byline: Boss. Per-conversation override via user prompt.
   - Anti-AI-tell list curated for Hinglish (no "in today's fast-paced world", no "kya baat hai", no inauthentic Hindi).
3. **Tool access (suggested):** Read (voice profile + new brief), Write (drafts to `data/notes/`).
4. **Model recommendation:** opus (best for voice mimicry); sonnet for bulk LinkedIn-style posts.

---

## Scorecard

| Criterion | Score (1-5) | Notes |
|-----------|-------------|-------|
| Role priming clarity | 5/5 | Two clean roles: analyst, then writer. |
| Scope boundaries | 5/5 | Profile-once-write-many separation. |
| Output format guidance | 5/5 | Structured profile + deliverable. |
| Reasoning techniques | 5/5 | Profile-first CoT; fingerprint anchors. |
| Safety / refusal patterns | 4/5 | Explicit anti-AI-tell list. |
| 2026 tech relevance | 5/5 | Dominant Claude Projects pattern. |
| License-friendliness | 2/5 | Unknown license — re-implement as original. |
| **Overall** | **31/35** | |
