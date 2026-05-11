# /triage — Email Inbox Triage

Process the user's inbox systematically. Reduce email anxiety. Extract action items.

## Workflow

### 1. Delegate to email-agent
Ask email-agent to:
- Fetch all unread emails from last 24-48 hours
- Categorize each: urgent / important / fyi / newsletter / spam / suspicious
- For each: extract sender, subject, 1-line summary, action_required
- Return structured list

### 2. Auto-extract tasks (delegate to task-agent)
For every email marked `action_required: yes`:
- Create a task with appropriate priority
- Source: "from email '{subject}' from {sender}"
- Due date: extract if mentioned, else suggest based on urgency

### 3. Identify drafts needed
For emails that need replies:
- Group by recipient
- Note which are critical vs. routine

### 4. Suggest batch actions
- "Unsubscribe from {n} newsletters" if many
- "Mark all newsletters as read" 
- "Archive old fyi emails"

### 5. Output Format

```markdown
# 📧 Inbox Triage — {timestamp}

## Summary
- Total processed: {n}
- Urgent: {count}
- Important: {count}
- FYI: {count}
- Newsletters/Promo: {count}
- Suspicious: {count}

## 🔴 Urgent — Need attention now

### From: {sender} — "{subject}"
**Summary:** {1 line}
**Action:** {what to do}
**Suggested response time:** {within X hours}

[Repeat for each urgent]

## 🟡 Important — This week

### From: {sender} — "{subject}"
**Summary:** {1 line}
**Action:** {what to do}
**Task created:** ✅ (P2, due {date})

[Repeat for each important]

## 🟢 FYI — No action needed
- {sender}: {brief}
- {sender}: {brief}

## 📰 Newsletters/Promo ({count})
[Grouped: just senders and counts]

Recommend: Unsubscribe from {senders consistently low value}?

## ⚠️ Suspicious / Possible Phishing ({count})
- {sender}: {why flagged}

⚠️ DO NOT click links. Recommend: report and delete.

## 📝 Tasks Created ({count})
{List of new tasks added to task-agent}

## ✏️ Drafts Suggested ({count})
For these emails, I can draft replies:
1. {sender} — {subject} → quick reply needed
2. {sender} — {subject} → detailed response

Want me to draft any?
```

### 6. Update memory
- If new important contact emerged → suggest adding to people.md
- If pattern noticed (always urgent emails from X) → flag for habit
- Update last triage timestamp in `data/last_triage.txt`

## Important

- **Work in single pass.** Don't re-fetch repeatedly.
- **Be ruthless with categorization.** Most emails are FYI or newsletter.
- **Don't over-explain low-priority stuff.** One-liner is enough.
- **Surface patterns.** "5 emails from X this week" is signal.
- **Never delete emails autonomously.**
- **Never auto-mark as read** (user might want to revisit).

## Auto-trigger (cron)

When run from cron without user present:
- Process silently
- If urgent items found → push notification via Telegram
- If only routine → save digest, no notification
- Always save full report to `data/triages/{date}_{time}.md`

## When invoked manually

Show all the detail. User wants to actually triage now.

---

**Goal:** Inbox goes from "anxiety-inducing pile" to "clear list of decisions" in 5 minutes.
