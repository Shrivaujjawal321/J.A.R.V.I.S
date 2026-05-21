# Spec: Telegram Bridge

**Status:** active
**Owner:** `bridge/telegram_bridge.py`
**Last reviewed:** 2026-05-13

## Purpose

The Telegram bot is Boss's primary mobile UI for Jarvis. The bridge process runs as a systemd service, polls Telegram for messages addressed to `@jarvis_Ujjawal_Bot`, and forwards them to the jarvis-core daemon's `/chat` endpoint. Replies stream back to the originating chat. Slash commands map to dedicated handlers (goal management, LinkedIn approvals, growth proposals).

The bridge MUST be the only Telegram-facing process — multiple `getUpdates` pollers cause message duplication and lost replies.

## Inputs

| Name | Source | Notes |
|------|--------|-------|
| Telegram updates | long-poll via python-telegram-bot | Bot token, allowed user list from `bridge/.env` |
| Slash commands | user-typed | `/goal_add`, `/goals`, `/lp_approve`, `/growth_*`, `/digest_now` |
| Voice messages | Telegram voice files | Forwarded to STT subprocess, then routed as text |

## Outputs

| Name | Destination | Notes |
|------|-------------|-------|
| `/chat` calls | jarvis-core daemon @ 127.0.0.1:8765 | Subprocess fallback if daemon down |
| Goal/approval calls | jarvis-core `/goal*`, `/approval*` | For Phase 3 lifecycle |
| Telegram replies | originating chat | Markdown-formatted by default |
| TTS audio | optional | Only if `/voice on` mode active |

## Behavioural contract

- MUST verify `from_user.id in ALLOWED_USER_IDS` before processing any update
- MUST never auto-send unsolicited messages outside its own command/reply cycle
  (cron-driven scripts may push via the Bot HTTP API — that's separate, not the bridge)
- MUST treat `/chat` daemon as primary path, fall back to subprocess `claude` CLI only if daemon `/health` fails
- MUST always log raw inbound + outbound for audit (`data/logs/bridge.log`)
- MUST cap inbound message size at 20_000 chars (mirrors `ChatRequest.message` limit)
- MUST reply with a clear error message — never silently drop a message
- MUST honour `JARVIS_USE_DAEMON=0` env to force legacy subprocess path

## Failure modes

| Failure | Detection | Response |
|---------|-----------|----------|
| Daemon `/health` fails | HTTP 5xx / connect refuse | Fall back to subprocess `claude` CLI, log path-switch |
| Telegram polling 401 | `getUpdates` returns auth error | Exit non-zero so systemd restarts; manual fix needed |
| Voice STT subprocess error | non-zero exit | Reply with "voice transcription failed — please type" |
| Subprocess `claude` CLI absent | FileNotFoundError | Reply with daemon-required error, exit cleanly |
| Network resolution failure | `httpx.ConnectError` | Auto-retry per python-telegram-bot built-ins |

## Eval cases

No automated suite — manual smoke: type `/health` (should respond OK), type a question (should reply within 30s), type a slash command for each handler at least once after deploys.

## Non-goals

- Does NOT support webhook mode (long-poll only, simpler ops)
- Does NOT do per-message rate limiting (Telegram does enough)
- Does NOT manage Boss's voice profile (`/voice` skill does)
- Does NOT proxy to non-Jarvis services

## Dependencies

- Python: `python-telegram-bot`, `requests`, `python-dotenv`
- Code: `jarvis_core.daemon` (HTTP target), subprocess `claude` CLI (fallback)
- Data: `bridge/.env` (`TELEGRAM_BOT_TOKEN`, `ALLOWED_USER_IDS`, `JARVIS_USE_DAEMON`)
- Systemd: `systemd/jarvis-bridge.service`

## Changelog

- 2026-05-13: Initial draft (Phase F backfill — module pre-existed)
