# Chief of Staff — Jarvis-Picked Agent Prompt

> Selected 2026-05-11 from 5 candidates in `../agent-prompts/chief-of-staff.md`
> Picker: prompt-picker-agent | Criteria: output quality + 2026 trend relevance + deployability

---

## Selected Prompt

**Original name:** Weekly Brain-Dump Triage
**From library:** `data/agent-prompts/chief-of-staff.md` → Prompt 1
**Source:** [The AI Break — Turn ChatGPT Into Your Chief of Staff](https://theaibreak.substack.com/p/tutorial-turn-chatgpt-into-your-chief)
**Author:** The AI Break (substack)
**License:** Free newsletter content (cite)

### Full Prompt (verbatim)

```
You are my Chief of Staff. I'm going to paste a messy weekly brain dump.
Your job:

  1. Extract every task, commitment, meeting, open loop, and unresolved
     decision. Nothing is too small.
  2. Categorise them into: Revenue/Growth, Delivery/Client work, Ops/Admin,
     Team/Hiring, Content/Brand, Personal, Learning/Research.
  3. For each item, tag: priority (P0 critical / P1 important / P2 nice),
     time-cost estimate, dependency (who/what unblocks it), and "is this
     mine to do or to delegate?"
  4. Surface contradictions and over-commitments — where am I doing
     two P0s in the same hour?
  5. Propose a top-3 for the week. Defend them in 2 sentences each, tied
     to my stated goals.
  6. List what I should explicitly NOT do this week and why.

Be direct. Ask me one clarifying question only if the dump is missing
something critical for triage.

Brain dump:
[PASTE]
```

---

## Why Jarvis Picked This

### Output quality drivers
- **Role priming:** "My Chief of Staff" first-person framing — invokes a thinking partner, not a transcriptionist.
- **Scope boundaries:** 6 numbered tasks; closed-set categories; closed-set priorities.
- **Output format:** Categorized tagged items + contradictions + top-3 + explicit NOT-do list.
- **Reasoning techniques:** Two reasoning forcing functions: (1) contradictions surface ("two P0s in the same hour"), (2) explicit NOT-do list (negative goal-setting).
- **Safety / refusal patterns:** Implicit only ("ask one clarifying question only if critical"); aligns with Boss's MEMORY.md "ask one question at a time" preference.
- **Examples / few-shot:** Category list serves as a few-shot schema.

### 2026 trend relevance
- **Modern frameworks:** Brain-dump triage matches Tiago Forte's PARA / Maker-Manager schedule thinking.
- **Current tech references:** Mine-to-do-or-delegate flag matches modern AI-augmented work where delegation includes agents.
- **Structured output:** Categorized + tagged, parseable.
- **Safety alignment:** Honors Boss's one-question-at-a-time preference.

### Deployability
- **License:** Free newsletter content — cite The AI Break on reuse.
- **Vendor lock:** None.
- **Jarvis adaptability:** Categories may need tuning for Boss's life (current set leans toward founder; "Research/Learning" is already there which fits Boss).

---

## Runners-up + Trade-offs

### #2: Weekly Principal Review (Prompt 5)
- **Why not picked:** Excellent end-of-week ritual but narrower (Friday review). Triage is the more general gateway.
- **When to use this instead:** End-of-week ritual; pair with /weekly-review slash command.

### #3: Executive Briefing Note (Prompt 2)
- **Why not picked:** Specialized one-pager artifact; narrower than triage.
- **When to use this instead:** Before any meeting where Boss is the most senior person.

### #4: Meeting Agenda + Pre-Read (Prompt 3)
- **Why not picked:** Specialized agenda artifact.
- **When to use this instead:** Leadership team meetings, 1:1s, recurring reviews.

### #5: Follow-Up & Accountability Tracker (Prompt 4)
- **Why not picked:** Post-meeting tracking artifact.
- **When to use this instead:** Immediately after meetings where commitments were made.

---

## Deployment Notes for Jarvis

1. **File path:** `.claude/agents/chief-of-staff-agent.md` (NOTE: overlap with executive-assistant winner — consider merging or scoping separately)
2. **Adaptations needed:**
   - Tune category list to Boss's life: keep Revenue/Growth, Delivery/Client, Ops/Admin, Team/Hiring, Content/Brand, Personal, Learning/Research — solid match already.
   - Wire in tasks.md and projects.md memory loaders.
   - Add Hinglish-mirror rule.
3. **Tool access (suggested):** Read access to tasks.md, projects.md, calendar; no autonomous task creation (draft then confirm).
4. **Model recommendation:** sonnet for daily triage; opus for hard weeks with conflicting priorities.

### Note on overlap with Executive Assistant
The Executive Assistant winner (Chief of Staff briefing prompt) and this Chief of Staff winner (Brain-dump triage prompt) are complementary, not duplicate: the EA prompt is daily orchestration; this CoS prompt is weekly triage. Wire both into Jarvis's slash commands (/briefing for EA, /weekly-review or "I have a brain dump" for CoS).

---

## Scorecard

| Criterion | Score (1-5) | Notes |
|-----------|-------------|-------|
| Role priming clarity | 5/5 | First-person CoS partner |
| Scope boundaries | 5/5 | 6 numbered tasks, closed-set categories |
| Output format guidance | 5/5 | Categorized + tagged + top-3 + NOT-do |
| Reasoning techniques | 5/5 | Contradiction-surfacing + negative goal-setting |
| Safety / refusal patterns | 3/5 | Implicit; could add explicit "no autonomous calendar mutation" |
| 2026 tech relevance | 4/5 | Modern delegation-aware; Maker/Manager-friendly |
| License-friendliness | 4/5 | Cite The AI Break on reuse |
| **Overall** | **31/35** | Gateway prompt for weekly leverage |
