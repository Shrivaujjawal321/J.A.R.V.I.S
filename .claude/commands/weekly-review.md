# /weekly-review — Weekly Review & Planning

End-of-week reflection + next-week setup. Sunday evening usually.

## Workflow

### 1. Look Back (last 7 days)

Gather data from:
- `data/conversations/` — last week's daily summaries
- `data/tasks.md` — completed and incomplete tasks
- `data/briefings/` — last week's briefings
- `data/plans/` — what was planned vs. what happened

### 2. Look Forward (next 7 days)

Check:
- **Calendar (delegate to calendar-agent):** next week's commitments
- **Tasks (delegate to task-agent):** what's due, what's important
- **Projects (from projects.md):** any milestones approaching

### 3. Synthesize Review

```markdown
# 🗓️ Weekly Review — Week of {start_date}

## ⏪ Last week

### Wins 🏆
- {Accomplishment 1}
- {Accomplishment 2}
- {Smaller win that mattered}

### Completed Tasks ({count})
**By priority:**
- P1: {count}/{count due}
- P2: {count}/{count due}
- P3: {count}/{count due}

**By tag:**
- #work: {count}
- #personal: {count}
- #health: {count}

### What didn't get done
- {Task} — {reason if known}
- {Task} — {reason}

**Patterns:** {observation about what didn't happen — e.g., "all #personal tasks slipped — work week was heavy"}

### Energy / Mood patterns
{Based on conversation tone last week:}
- {Day} felt: {energy level}
- {Best day for focus:} {observation}
- {Stress signals:} {if any noticed}

### Time spent (estimated from calendar)
- Meetings: {hours}
- Focus work: {hours}
- Personal: {hours}
- Sleep deficit?: {if patterns suggest}

## ⏭️ Next week

### Calendar load
- Total meetings: {count}
- Heavy days: {which days}
- Light days: {which days}
- Free blocks for deep work: {hours total}

### Critical commitments
- {Important meeting/event 1}
- {Important meeting/event 2}
- {Deadline}

### Tasks needing attention
- {P1 task with deadline}
- {Project milestone}
- {Follow-up that can't slip}

### Project status
{From projects.md — surface anything stuck or needing attention}

## 💡 Insights

**Patterns this week:**
- {Observed pattern 1}
- {Observed pattern 2}

**What worked:**
- {Pattern that produced results}

**What didn't:**
- {Pattern that hurt}

**Suggestion for next week:**
{Concrete actionable change based on patterns}

## 🎯 Next week's intentions

**Top 3 priorities (suggest based on data):**
1. {Highest impact thing}
2. {Important commitment}
3. {Personal/health priority}

**One thing to NOT do:**
{What to deliberately skip to make room}

**Habit to focus on:**
{One small behavior change}

## 📝 Memory updates suggested

{If anything from this week should update memory:}
- New project starting → projects.md
- Recurring pattern → habits.md
- New person frequently mentioned → people.md

Approve any of these?

---

How does this read? Anything you'd adjust for next week?
```

### 4. Save Review
Save to `data/reviews/{week_start}.md`

### 5. Update Memory
Based on review, update relevant memory files (with user confirmation):
- New habits forming → habits.md
- Project status changes → projects.md
- New important people → people.md

## Smart Behaviors

### Be honest, not harsh
- "You didn't complete X" → just stating, not judging
- "You skipped workouts 3 days in a row" → fact, possibly worth attention
- Don't moralize. User is adult.

### Notice positive patterns too
- "You finished all your P1s this week — good prioritization"
- "First full week without skipping morning routine"
- These matter.

### Surface trends across weeks
- Compare to previous weeks if data available
- "Third week in a row of high meeting load"
- "Exercise consistency improving"

### Account for context
- Was user sick? On vacation? Major event?
- Don't compare apples to oranges across weeks

## When run via cron (Sunday evening)

- Run silently
- Save to file
- Send digest version to Telegram
- Don't ask follow-up questions (save those for when user is interactive)

## When run interactively

- Engage with user on insights
- Ask "what worked this week?" — let them reflect
- Help shape next week's priorities together

---

**Goal:** User ends each week with closure and starts next week with intention.
