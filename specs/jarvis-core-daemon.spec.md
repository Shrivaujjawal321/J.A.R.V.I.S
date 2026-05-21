# Spec: jarvis-core daemon

**Status:** active
**Owner:** `jarvis_core/daemon.py`
**Last reviewed:** 2026-05-13

## Purpose

Long-running localhost FastAPI service that owns all `/chat`, `/task`, `/goal` orchestration for Jarvis. Authenticates via `CLAUDE_CODE_OAUTH_TOKEN` (Max subscription, no developer API key). Other Jarvis surfaces (Telegram bridge, voice loop, cron-driven scripts) hit this daemon over HTTP instead of spawning the `claude` CLI directly.

## Inputs

| Name | Source | Notes |
|------|--------|-------|
| HTTP requests | localhost:8765 | `/chat`, `/task`, `/goal*`, `/approval*`, `/health`, `/state` |
| Project root | `JARVIS_PROJECT_PATH` env | Working dir for spawned Claude Code workers |
| OAuth token | `CLAUDE_CODE_OAUTH_TOKEN` env | Required; daemon logs warning + degrades if missing |
| State snapshot | `data/state/jarvis-state.json` | Restored on boot, written every 5 min + on shutdown |

## Outputs

| Name | Type | Consumer | Notes |
|------|------|----------|-------|
| HTTP responses | JSON | callers | `ChatResponse`, `TaskStateView`, `GoalStateView` |
| State snapshot | JSON | self next boot | Atomic writes via tmp file |
| Conversation log | JSONL | `auto_capture.py` | `data/logs/conversations.jsonl` (one line per `/chat`) |
| Recall/Critic logs | JSONL | observability | Written by `jarvis_core/recall.py` + `critic.py` |
| Goal/task records | in-memory + state file | `/goal*` endpoints, scheduler | Survives daemon restarts |

## Behavioural contract

- MUST bind 127.0.0.1 only (no public exposure)
- MUST restore RUNNING/PLANNING goals to QUEUED on cold start (orphan recovery)
- MUST flush state to disk on SIGTERM with up to 30s timeout
- MUST run recall → worker → critic pipeline on every `/chat` (skip-cases honoured)
- MUST never auto-execute Tier-3 actions — they queue as `ApprovalRequest`
- MUST honour per-goal `max_budget_usd` and `max_duration_seconds`
- MUST emit one conversation-log line per completed `/chat` (even on critic skip)
- MUST log warning if `CLAUDE_CODE_OAUTH_TOKEN` is missing but still boot
- MUST NOT skip the critic on `/task` workers (Phase 2 may extend)
- MUST NOT mutate `data/memory/*.md` files directly — those are hand-curated

## Failure modes

| Failure | Detection | Response |
|---------|-----------|----------|
| OAuth token expired | SDK error | Worker returns error, daemon still serves health |
| Recall init fails | Recaller logs | Recall skipped (empty context); chat continues |
| Critic backend fails | Critic logs | Original reply ships with `unverified` tag |
| State file corrupt | json.JSONDecodeError | Boot with empty state, log error |
| Port already in use | uvicorn bind error | Exit non-zero so systemd restarts |

## Eval cases

Live smoke (no automated eval suite; manual): `curl POST /chat`, verify response shape includes `confidence`, `memory_hits`, `revised`.

## Non-goals

- Does NOT expose public endpoints (use Telegram bridge for external traffic)
- Does NOT authenticate per-user (single Boss assumption)
- Does NOT run inside Docker / containers (laptop-bound)
- Does NOT manage Claude OAuth token lifecycle (manual `claude setup-token` only)

## Dependencies

- Code: `jarvis_core/orchestrator.py` (worker dispatch)
- Code: `jarvis_core/recall.py` + `critic.py` (Phase A + B layers)
- Code: `jarvis_core/scheduler.py` + `decomposer.py` (Phase 3 goals)
- Code: `jarvis_core/state.py` (persistence)
- Env vars: `CLAUDE_CODE_OAUTH_TOKEN`, `JARVIS_PROJECT_PATH`, `JARVIS_STATE_PATH`,
  `JARVIS_CORE_HOST`, `JARVIS_CORE_PORT`, `JARVIS_STATE_SYNC_SECONDS`,
  `JARVIS_GOAL_POLL_SECONDS`, `JARVIS_GOAL_MAX_CONCURRENT`
- Systemd: `systemd/jarvis-core.service`

## Changelog

- 2026-05-13: Initial draft (Phase F backfill)
