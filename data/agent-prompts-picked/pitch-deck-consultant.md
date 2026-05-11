# Pitch Deck Consultant — Jarvis-Picked Agent Prompt

> Selected 2026-05-11 from 5 candidates in `../agent-prompts/pitch-deck-consultant.md`
> Picker: prompt-picker-agent | Criteria: output quality + 2026 trend relevance + deployability

---

## Selected Prompt

**Original name:** Narrative-First Story Architect
**From library:** `data/agent-prompts/pitch-deck-consultant.md` → Prompt 2
**Source:** [Stunspot — One Sane Prompt for Pitch Deck Creation (Medium)](https://medium.com/@stunspot/one-sane-prompt-for-pitch-deck-creation-7f97905d69e3)
**Author:** stunspot
**License:** Medium article (cite + adapt)

### Full Prompt (verbatim)

```
You are a pitch consultant who has helped 100+ founders shape their
fundraising story. Before any slide, we build the narrative.

Walk me through a 6-part story arc:
  1. The world before — what unfair thing exists today that nobody is
     fixing?
  2. The shift — what's changing in technology / behaviour / regulation
     that creates an opening NOW?
  3. The protagonist — who is the founder, and why is this their fight?
     (Specific personal credential, not generic passion.)
  4. The promise — what becomes true for the customer when we win?
  5. The mechanism — how do we deliver this (one sentence, no jargon)?
  6. The stakes — what does the world lose if we don't exist?

For each section, ask me ONE question at a time. After all 6, output:
  - A 90-second verbal pitch (spoken script)
  - A one-line tagline
  - The single slide title that should appear right after the cover

Start with question 1.
```

---

## Why Jarvis Picked This

### Output quality drivers
- **Role priming:** "100+ founders" credential anchors the model in real-pitch heuristics.
- **Scope boundaries:** 6-part story arc; each section bounded to a single question.
- **Output format:** 90-second verbal pitch + tagline + first slide title — three composable artifacts.
- **Reasoning techniques:** Story-arc-before-slides forces narrative coherence; one-question-at-a-time matches Boss's MEMORY.md preference perfectly.
- **Safety / refusal patterns:** Implicit — "specific personal credential, not generic passion" prevents puffery. Library-level guardrail rejects fabricated traction/market size/team credentials.
- **Examples / few-shot:** Per-section descriptors serve as schema.

### 2026 trend relevance
- **Modern frameworks:** Narrative-first pitching is the dominant Sequoia / a16z / YC pattern in 2026.
- **Current tech references:** "Shift" question explicitly asks about tech/behavior/regulation changes — captures AI-era narrative opportunity.
- **Structured output:** 6-part arc + 3 final deliverables.
- **Safety alignment:** Anti-puffery + anti-fabrication.

### Deployability
- **License:** Medium article — cite stunspot on reuse.
- **Vendor lock:** None.
- **Jarvis adaptability:** PERFECT match to Boss's one-question-at-a-time preference.

---

## Runners-up + Trade-offs

### #2: 10-Slide Investor Deck Outline (Prompt 1)
- **Why not picked:** Excellent structured outline but requires narrative first to produce a good deck. Run AFTER narrative is clear.
- **When to use this instead:** Boss has story locked in and needs the slide framework.

### #3: Investor "So What?" Stress Test (Prompt 3)
- **Why not picked:** Brilliant late-stage QA tool; specialized for review, not creation.
- **When to use this instead:** Two days before a pitch — pressure-test a "done" deck.

### #4: Elevator Pitch + One-Liner Crafter (Prompt 4)
- **Why not picked:** Specialized for one-liner work; narrative-arc produces this as a byproduct.
- **When to use this instead:** Cold investor intro, deck cover, conference badge.

### #5: Post-Meeting Investor Update Email (Prompt 5)
- **Why not picked:** Different workflow (monthly updates, not pitch creation).
- **When to use this instead:** Monthly investor newsletter.

---

## Deployment Notes for Jarvis

1. **File path:** `.claude/agents/pitch-deck-agent.md`
2. **Adaptations needed:**
   - Already aligned to Boss's one-question-at-a-time preference — no modification needed.
   - Add library-level ethics guardrail: REJECT requests to fabricate traction, market size, team credentials.
   - Wire in projects.md context for Boss's own pitch work.
3. **Tool access (suggested):** Read access to memory; research-agent for market-size verification; no autonomous deck-publishing.
4. **Model recommendation:** opus (narrative craft + story coherence over many turns); sonnet acceptable for follow-up iterations.

### Ethics note
Library header explicitly rejects fabricated traction/market size/team credentials. Carry this forward into the agent's system prompt — investors verify, founders go to jail.

---

## Scorecard

| Criterion | Score (1-5) | Notes |
|-----------|-------------|-------|
| Role priming clarity | 5/5 | 100+ founders, specific persona |
| Scope boundaries | 5/5 | 6-part arc; one question at a time |
| Output format guidance | 5/5 | 90-sec script + tagline + first slide |
| Reasoning techniques | 5/5 | Narrative-before-slides; one-question pacing |
| Safety / refusal patterns | 4/5 | Implicit; needs explicit anti-fabrication carry-over |
| 2026 tech relevance | 5/5 | "Shift" question captures AI-era opportunity |
| License-friendliness | 4/5 | Cite stunspot on reuse |
| **Overall** | **33/35** | Best one-question pacing match in entire set |
