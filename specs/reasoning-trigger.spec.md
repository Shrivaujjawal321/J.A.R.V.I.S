# Spec: Reasoning-Trigger Layer

**Status:** active
**Owner:** `scripts/reasoning_trigger.py`
**Last reviewed:** 2026-05-13

## Purpose

Every 4 hours, synthesise Boss's current state across signals (tasks, markers, feedback, audit log, LinkedIn pipeline state, hackathon deadlines, sleep markers) and produce up to 3 prioritised action proposals. Send to Telegram only if the overall signal is `medium` or higher — otherwise log silently.

Replaces (but does not delete) the dumb rule-based `scripts/trigger_watcher.py`. That script still runs and catches mechanical conditions (deadline-in-N-days, gap-of-N-days). The reasoning trigger adds an LLM synthesis layer that connects multiple weak signals into one stronger nudge.

## Inputs

| Name | Type | Source | Notes |
|------|------|--------|-------|
| Tasks | markdown | `data/tasks.md` | Open tasks, priorities, deadlines |
| Markers | files | `data/markers/*` | mtime-driven gap signals |
| Feedback | JSONL | `data/logs/feedback.jsonl` | Last 14 days, focus on negatives |
| Audit log | JSONL | `data/audits/{date}.jsonl` | Last 7 days of Tier-2/3 actions |
| LinkedIn state | JSONL | `data/linkedin/*.jsonl` | Approval queue, throttle status |
| Hackathon list | files | `data/hackathons/` | Upcoming deadlines |
| Habits | markdown | `data/memory/habits.md` | Sleep, focus patterns |
| Claude API | LLM | via `run_worker` | Haiku for synthesis |

## Outputs

| Name | Type | Consumer | Notes |
|------|------|----------|-------|
| Telegram message | HTTP POST | Bridge → Boss | Sent only if signal ≥ medium |
| `data/logs/reasoning_trigger.jsonl` | JSONL | Observability | One line per run |
| `data/markers/reasoning_state.json` | JSON | Self (next run) | Tracks alert cooldown per topic |

## Behavioural contract

- MUST run idempotently — a re-run with no state change produces no Telegram message
- MUST cap LLM calls per run at 2 (synthesis + optional follow-up)
- MUST cool-down identical-topic alerts for 12 hours (prevent spam)
- MUST output proposals as JSON: `{signal_level, proposals: [{topic, why, action, urgency}]}`
- MUST send Telegram only for `signal_level in (medium, high)`
- MUST exit 0 even on partial failure (log + continue)
- MUST honour `JARVIS_REASONING_ENABLED=0` kill-switch
- MUST NOT mutate any source data (read-only)
- MUST NOT exceed 90s total runtime
- SHOULD prefer short messages (< 800 chars) for the Telegram digest
- SHOULD reference specific evidence (e.g., "data/markers/last_resume_edit") in `why`

## Failure modes

| Failure | Detection | Response |
|---------|-----------|----------|
| LLM call fails | Exception | Log + skip Telegram + exit 0 |
| Telegram send fails | HTTP error | Log raw message + exit 0 |
| Source file missing | FileNotFoundError | Use empty default for that signal |
| Marker corrupt | json.JSONDecodeError | Reset cooldown state |

## Eval cases

`data/evals/reasoning_trigger/test_cases.jsonl` covers:

1. **No signals** → no Telegram
2. **Single weak signal** (resume gap 2 days) → no Telegram
3. **Single strong signal** (hackathon deadline tomorrow) → Telegram
4. **Multiple weak signals** that compound into medium → Telegram
5. **Repeated same-topic within 12h** → cooldown suppresses
6. **LLM returns garbage JSON** → fail-open, exit 0

## Non-goals

- Does NOT execute proposed actions — pure surfacing
- Does NOT replace `trigger_watcher.py` (runs alongside)
- Does NOT track ROI of past suggestions (Phase E self-growth does)
- Does NOT do per-user reasoning — single Boss only

## Dependencies

- Code: `jarvis_core/orchestrator.py:run_worker()`
- Code: Telegram bridge sender (HTTP API or bridge `.env` token)
- Data: `data/tasks.md`, `data/markers/*`, `data/logs/feedback.jsonl`, `data/audits/`, `data/linkedin/*`, `data/memory/habits.md`
- Env vars: `JARVIS_REASONING_ENABLED` (default: 1), `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`

## Changelog

- 2026-05-13: Initial draft (Phase D)
