# /hackathon-radar — Current AI/ML hackathon situation + strategic picks

Surface what's open, what's relevant, what Boss should commit to.

## Workflow

### 1. Load current data
- Latest `data/hackathons/radar-*.md` (curated by research)
- Latest `data/hackathons/radar-*.json` (auto-scraped by hackathon_radar.py)
- `data/tasks.md` — already-registered hackathons (don't double-promote)
- `data/markers/trigger_state.json` — what's been alerted recently

If radar data is missing or > 3 days old → dispatch research-agent first.

### 2. Triage (delegate to hackathon-agent)
Ask hackathon-agent to:
- Score every open hackathon for Boss (career outcome, solo feasibility, skill leverage, prize, urgency)
- Produce top 2-3 picks
- Flag skips with reasons

### 3. Deadline urgency
Compute days-to-deadline for everything in tasks.md + radar:
- 🔥 < 7 days → "act now"
- ⏰ 7–14 days → "register this week"
- 📅 14–30 days → "on the radar"
- 🗓️ > 30 days → "future"

### 4. Output
```markdown
# 🏁 Hackathon Radar — {date}

## 🔥 Closes this week (act now)
- **{Hackathon}** — deadline {date} ({N} days) — {1-line pitch}
  Status: [Registered ✓ / Not registered]
  Next action: ...

## ⏰ Closes next week
...

## 📅 Coming up (14–30 days)
...

## 🎯 My recommendation
**Commit to:** {1-2 hackathons} — {reasoning}
**Skip:** {hackathon} — {reasoning}
**Ignore:** {everything else for now}

## ❓ Need decisions from you
- [ ] Register for {X}? (deadline {date})
- [ ] Confirm eligibility for {Y}?

## Build calendar
If you commit to {top pick}, here's the rough build window:
- Register by: {date}
- Idea brainstorm: {date}
- Build sprint: {dates}
- Submission: {date}
```

### 5. Ask one decision question
End with the single highest-priority question — usually "register for X right now? (takes 5 min)". Per Boss's preference: one question per turn.

## Hard Rules

- **Don't auto-register.** Boss confirms each one.
- **Honest eligibility.** If Boss is borderline-eligible, flag the risk before he wastes time.
- **Push back on hackathon-hoarding.** If he's already on 5, don't add 5 more. Quality > quantity.
- **Update tasks.md** if Boss says "register me for X" — but only after registration is confirmed by him.

---

**End-state:** Boss knows in 60 seconds which hackathon(s) deserve his attention this week and what the next action is.
