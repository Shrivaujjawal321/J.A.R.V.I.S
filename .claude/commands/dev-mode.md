# /dev-mode — Focus mode for deep coding sessions

Boss is grinding on Claude Code. Mute distractions, surface only what matters, respect his peak focus window (night).

## Usage

```
/dev-mode                # Enter focus mode
/dev-mode off            # Exit focus mode
/dev-mode status         # Show current state
```

## What "On" Does

### 1. Mark session start
Touch `data/markers/dev_mode_active` with current timestamp. The trigger-watcher reads this — if active, it suppresses Telegram alerts (except true emergencies like deadlines < 24h).

### 2. Surface a tight context
Read these and present concisely:
- `data/memory/projects.md` — what's active
- `data/tasks.md` — what's P1
- Last commit on relevant project (if git initialized)
- Any failing CI / open errors in `data/logs/`

```markdown
# 🧠 Dev Mode On — {time}

**Current Claude Code session target:** {Boss's 5h/day yardstick}
**Time tracker started.** I'll nudge you only if:
- You're past 8h continuous (your overwork trigger)
- A P0 deadline hits < 24h
- You explicitly ask

## What you're likely working on
- {Active project from projects.md}
- {Open tasks P1}

## Last work signal
{Last commit message or last note in data/conversations/}

## Resources at hand
- code-agent — for review/debug/refactor
- research-agent — for "how do I X in Y"
- memory-agent — to save new learnings

Go build. I'm muted unless it's important.
```

### 3. Mute non-essential alerts
- Trigger-watcher continues but suppresses output (unless emergency level)
- Telegram non-urgent messages queue silently
- Email triage paused

### 4. Time tracking
Optionally start a background `data/markers/session_start` timestamp. On `/dev-mode off`, report duration.

## What "Off" Does

- Remove `data/markers/dev_mode_active`
- Compute session length (now - session_start)
- If session ≥ 5h → "Nailed your 5h target ✓"
- If session ≥ 8h → "8+ hours — please get water + 15min break"
- Resume normal alerts
- Replay queued non-urgent items

```markdown
# 🌙 Dev Mode Off — {time}

**Session length:** {duration}
**Status:** {target hit / overshot / undershot}

## Caught up while you were focused
- {queued alerts}
- {emails that came in}
- {anything time-sensitive}

## Want to log what you built?
Use /braindump or just tell me.
```

## What "Status" Does

Just show current mode + how long it's been on.

## Hard Rules

- **Respect mute.** Once active, do NOT spam updates unless emergency-tier.
- **Never auto-exit.** Boss controls when focus ends.
- **8h cap is firm.** Per habits.md, gently surface a break suggestion past 8h continuous — even if muted. Single ping, then back off.
- **Don't track keystroke-level activity.** Just session start/end.

---

**End-state:** Boss can hit `/dev-mode` and disappear into code without Jarvis pestering him. Comes back to a clean catchup.
