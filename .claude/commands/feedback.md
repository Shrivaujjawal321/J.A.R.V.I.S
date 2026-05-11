# /feedback — Rate what just happened

Quick capture of Boss's feedback on Jarvis's most recent output, so the system learns over time.

## Usage

```
/feedback                              # Interactive: ask what + rating + note
/feedback <thumbs_up|thumbs_down|⭐N>   # Quick rating on most recent action
/feedback <target> <rating> [note]     # Targeted, e.g., "/feedback resume-agent thumbs_down took too long"
```

## What this captures

For each feedback:
- **Target** — agent / slash command / response being rated
- **Rating** — thumbs_up / thumbs_down / star_1-5
- **Note** — optional free-text reason
- **Session context** — what task was happening
- **Timestamp**

## Workflow

### Quick mode (most common)
If Boss says `/feedback thumbs_up` or `/feedback thumbs_down [note]`:
1. Identify what the rating applies to from current conversation context:
   - Last agent invoked
   - Last major output produced
   - Last slash command run
2. Append entry to `data/logs/feedback.jsonl` via `scripts/feedback.py log` (or write directly if script not yet present)
3. One-line confirmation: "👍 Logged — {target} marked good. Saved to feedback.jsonl"

### Targeted mode
If Boss says `/feedback resume-agent thumbs_down "skipped my Hinglish preference"`:
1. Parse target + rating + note
2. Log it
3. Confirm + acknowledge: "Got it. Logged thumbs_down on resume-agent. I'll surface this in the next weekly review."

### Interactive mode (no args)
If Boss types just `/feedback`:
1. Ask ONE question: "What are you rating? (last response / specific agent / a slash command)"
2. After he picks, ask: "👍 or 👎? (or 1-5 star?)"
3. Optional: "Add a note? (or just hit enter to skip)"
4. Log + confirm.

## Surface feedback in weekly review

The `/weekly-review` slash command should read `data/logs/feedback.jsonl` for the past 7 days and include:
- 👍 count vs 👎 count per agent/command
- All thumbs-down notes (these are gold for prompt improvement)
- Trend: is the same agent getting flagged repeatedly?

## Hard Rules

- **Never auto-rate Jarvis's own output as positive.** Boss is the only rater.
- **Don't ask twice.** If Boss is in a hurry and uses quick mode, log + confirm in one line. Don't quiz him.
- **Keep logs append-only.** Never edit past feedback entries.

## File format

`data/logs/feedback.jsonl` — one JSON object per line:
```json
{"ts": "2026-05-11T20:34:12+05:30", "target": "resume-agent", "rating": "thumbs_down", "note": "missed Hinglish", "context": {"task": "resume review"}}
```

## Why this matters

Without feedback collection, Jarvis can't improve session-to-session. Every 👍/👎 with a note becomes signal for:
- Identifying agents that need prompt updates
- Spotting when a workflow stops working
- Validating that recent changes were good
- Generating the weekly self-review's "what got better / worse" section

---

**End-state:** Boss can give a single-keystroke reaction after any Jarvis output, and it gets captured for compounding system improvement.
