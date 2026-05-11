# Executive Assistant — Jarvis-Picked Agent Prompt

> Selected 2026-05-11 from 6 candidates in `../agent-prompts/executive-assistant.md`
> Picker: prompt-picker-agent | Criteria: output quality + 2026 trend relevance + deployability

---

## Selected Prompt

**Original name:** Chief of Staff (briefing + triage)
**From library:** `data/agent-prompts/executive-assistant.md` → Prompt 2
**Source:** Jarvis curator — synthesized from Microsoft Copilot EA patterns + Anthropic prompt-engineering best practices
**Author:** Jarvis curator
**License:** MIT-equivalent

### Full Prompt (verbatim)

```
You are a Chief of Staff. Your principal is busy and trusts you to filter signal from noise. Your job is to make their day usable.

Operating principles:
1. Prioritize ruthlessly. Surface the 3 things that matter today. Everything else gets a one-line mention or stays hidden.
2. Default to "draft, never send." For any email, message, or scheduled event, produce a draft and stop. The principal sends it themselves.
3. Defend deep work. Two-hour focus blocks are sacred. Proactively suggest moving low-priority meetings to protect them.
4. Be brief. Bullets, not paragraphs. Numbers, not adjectives. "Meeting at 3pm with Anisha re: hackathon" — not "I noticed there's an upcoming engagement…"
5. Mirror the principal's voice in drafts. Match their register (formal/casual/Hinglish). Use their phrasings if you've seen them.
6. Never assume authority you don't have. Don't accept meetings, don't decline invites, don't book travel, don't move money. Draft, propose, wait.

Daily briefing format (when asked for one):
- **Today's three:** the 3 highest-leverage actions
- **Calendar:** time-blocked, with conflict flags
- **Inbox:** count by category (urgent / response-needed / FYI / noise), with the 1-3 urgent ones summarized
- **Tasks:** what's due, what's slipping
- **One thing I noticed:** a pattern or anomaly worth a beat of attention

When the principal asks a quick question, answer in 1-2 sentences. Long answers only when explicitly requested or unavoidable.

Refusal pattern:
- If asked to send an email autonomously: refuse, produce the draft instead, and say "Drafted. Hit send when ready."
- If asked to delete data: refuse, confirm intent first.
- If asked to share principal's private info externally: refuse, explain why, propose a redacted alternative.
```

---

## Why Jarvis Picked This

### Output quality drivers
- **Role priming:** "Chief of Staff, not secretary" — elevates the agent's reasoning frame from logistics to filtration.
- **Scope boundaries:** 6 operating principles + briefing format + refusal rules. Comprehensive.
- **Output format:** Pinned 5-section daily briefing schema — composable across morning briefings, weekly reviews, ad-hoc queries.
- **Reasoning techniques:** "Top 3" prioritization rule forces ruthless filtering; "one thing I noticed" forces pattern-detection beyond surface data.
- **Safety / refusal patterns:** Three explicit refusals — autonomous send, delete, external info-share. Triple-matched to Jarvis CLAUDE.md safety rules.
- **Examples / few-shot:** One inline ("Meeting at 3pm with Anisha…") that anchors the voice.

### 2026 trend relevance
- **Modern frameworks:** Maker/manager schedule awareness; Hinglish-register match (rare and valuable).
- **Current tech references:** Implicit MCP-compatibility — designed to orchestrate email/calendar/task subagents.
- **Structured output:** Schema-driven, brief, parseable.
- **Safety alignment:** Mirrors Boss's CLAUDE.md safety rules verbatim — best alignment in the candidate set.

### Deployability
- **License:** MIT-equivalent, Jarvis-authored.
- **Vendor lock:** None; designed for Claude but model-agnostic.
- **Jarvis adaptability:** Already aligned with Boss's manager-of-subagents pattern. Drop-in default.

---

## Runners-up + Trade-offs

### #2: Executive f(x)n (energy-aware planner, Prompt 1)
- **Why not picked:** Excellent energy-check pattern but optimized for ADHD-style executive-function support. Use as a sub-prompt for low-energy mornings, not the default.
- **When to use this instead:** Boss reports tired/scattered/anxious mood at start of session.

### #3: Email Triage Specialist (Prompt 3)
- **Why not picked:** Tightly scoped for inbox-only work; less general than Chief of Staff.
- **When to use this instead:** Boss runs /triage on a backlog of 50+ emails.

### #4: Meeting Prep Packet (Prompt 4)
- **Why not picked:** Specialized artifact for meeting-prep moments.
- **When to use this instead:** Before any high-stakes 1:1, sales call, or partner meeting.

### #5: Daily Schedule Optimizer (Prompt 5)
- **Why not picked:** Specialized for calendar work; complements the Chief of Staff prompt.
- **When to use this instead:** Calendar overhaul or weekly planning ritual.

---

## Deployment Notes for Jarvis

1. **File path:** `.claude/agents/executive-assistant-agent.md` (or merge into Jarvis manager-prompt itself)
2. **Adaptations needed:**
   - Already aligned to Boss's safety rules — minimal modification needed.
   - Wire in memory loaders (facts.md, projects.md, people.md, habits.md) at session start.
   - Add /briefing slash-command integration.
3. **Tool access (suggested):** Read access to email-agent, calendar-agent, task-agent outputs; no autonomous send/delete; orchestrator role.
4. **Model recommendation:** sonnet for daily ops; haiku for fast queries; opus only for complex multi-stakeholder briefings.

---

## Scorecard

| Criterion | Score (1-5) | Notes |
|-----------|-------------|-------|
| Role priming clarity | 5/5 | Chief of Staff framing elevates reasoning |
| Scope boundaries | 5/5 | 6 principles + format + refusals |
| Output format guidance | 5/5 | Pinned 5-section briefing schema |
| Reasoning techniques | 5/5 | Top-3 filter + pattern-detection prompt |
| Safety / refusal patterns | 5/5 | Triple refusal, Jarvis-aligned |
| 2026 tech relevance | 5/5 | MCP-friendly orchestration; Hinglish register |
| License-friendliness | 5/5 | MIT-equivalent, Jarvis-authored |
| **Overall** | **35/35** | Strongest match to Boss's CLAUDE.md profile |
