# /briefing — Morning Briefing

Generate a comprehensive morning briefing for the user.

## Workflow

Execute these steps in order:

### 1. Load Context
- Read `data/memory/facts.md`, `preferences.md`, `projects.md`, `habits.md`
- Read yesterday's `data/conversations/{yesterday}.md` if exists
- Note current date and time

### 2. Email Triage (delegate to email-agent)
Ask email-agent to:
- Fetch unread emails from last 24 hours
- Categorize: urgent / important / fyi / newsletter
- Extract action items
- Return structured triage report

### 3. Calendar Overview (delegate to calendar-agent)
Ask calendar-agent to:
- Today's events with times and prep needs
- Free time blocks identified
- Conflicts or back-to-back meetings flagged
- First "must do" of the day highlighted

### 4. Task Status (delegate to task-agent)
Ask task-agent to:
- Overdue tasks (red flag)
- Today's due tasks
- This week's important tasks (P1)
- Recommend top 3 to focus on today

### 5. News (delegate to research-agent, optional)
If user wants daily news (check preferences):
- Top 3 tech/AI headlines
- Top 1 India-specific news
- Anything user is following (from interests in preferences.md)
- Brief summaries only (1 line each)

### 6. Synthesize Briefing

Create a markdown briefing with this structure:

```markdown
# 🌅 Morning Briefing — {date}

{Time-appropriate greeting based on hour and user's preferences}

## ☀️ The day at a glance

**Today's vibe:** {1-line take based on calendar+tasks load}
**Top priority:** {single most important thing}

## 📧 Inbox ({count} new)

{Email-agent's triage output, condensed}

**Drafts to review:** {count if any drafts pending}

## 📅 Schedule

{Calendar-agent's today output}

**First thing:** {first event or task with time}

## ✅ Tasks

{Task-agent's relevant output}

**Recommended focus today:**
1. {Task 1}
2. {Task 2}
3. {Task 3}

## 🌐 News (optional)

{Brief headlines if included}

## 💡 Heads up

{Anything noticed:}
- Birthday coming up for someone
- Project deadline approaching
- User's habit reminders ("you usually work out Tuesday")
- Pattern alerts ("3rd late night this week — rest?")

---

What would you like to start with?
```

### 7. Save Briefing
Save full briefing to `data/briefings/{date}.md` for archive.

### 8. (If invoked from cron/Telegram)
Send formatted version to Telegram (handled by bridge service).

## Important

- **Keep tone warm but efficient.** Don't be cheerful in a fake way.
- **Adapt to user's mood signals** if visible from yesterday's conversation.
- **Don't be exhaustive** — surface most important things.
- **Make it scannable.** User reads this groggy. Make sense in 30 seconds.
- **End with a question** that invites engagement, not a wall of options.

## Examples

### Casual morning
"Good morning! Coffee in hand? Quick rundown..."

### Heavy day
"Heads up — today's stacked. Let's prioritize..."

### Light day
"Easy day ahead. Good chance to catch up on..."

### After a tough day yesterday
"Hope you got some rest. Today looks more manageable..."

---

**Goal:** User reads this in 60 seconds and knows exactly what matters today.
