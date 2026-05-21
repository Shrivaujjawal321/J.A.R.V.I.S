# Spec: Intent Classifier

**Status:** active
**Owner:** `jarvis_core/intent.py`
**Last reviewed:** 2026-05-15

## Purpose

Before Jarvis decides how to respond to a `/chat` message, this layer classifies the message into one of eight standard categories with a priority and confidence score. The classification is then attached to the worker prompt as an `<intent>` block, and surfaced on `ChatResponse.intent` so downstream consumers (Telegram bridge, future sentinels, future routing rules) can branch on it.

This closes the gap Boss flagged after the Ratnesh's-Jarvis comparison (2026-05-15): the missing orchestrator-first pipeline. Today recall + critic run on every turn, but **classification is implicit**, derived ad-hoc by the worker. With this module, every turn carries an explicit, logged, evalable intent tag — the foundation for sentinels, routing, and metabolism.

This is the lightweight analogue of Ratnesh's 8-layer orchestrator. We deliberately split classification (here) from recall (separate spec) so each layer can be evaluated, killed, or upgraded independently.

## Inputs

| Name | Type | Source | Notes |
|------|------|--------|-------|
| `user_message` | `str` | `ChatRequest.message` from `/chat` endpoint | The raw text Boss sent |
| `user_id` | `str` | `ChatRequest.user_id` | Logged only |

## Outputs

| Name | Type | Consumer | Notes |
|------|------|----------|-------|
| `IntentResult.category` | `str` (enum, 8 values) | `daemon.py:chat()` → worker prompt + `ChatResponse.intent` | The classification |
| `IntentResult.priority` | `str` (`low\|normal\|high\|urgent`) | Same | Derived from category + keywords |
| `IntentResult.confidence` | `float` in [0, 1] | Same | Self-reported by classifier |
| `IntentResult.rationale` | `str` | Logged only, not surfaced to worker | One-line "why this category" |
| `intent_log` entry | `dict` | `data/logs/intent.jsonl` | One line per call |

## Categories (8, exhaustive + non-overlapping)

| Category | Definition | Examples |
|----------|-----------|----------|
| `task` | Action Boss wants done — build, edit, draft, send, fix | "draft an email to X", "fix the bug in Y", "deploy the site" |
| `question` | Information request — fact, opinion, how-to, status | "what's the time", "how does X work", "kya kar rahe ho" |
| `feedback` | Boss reacting to prior work — praise, correction, refinement | "this is wrong", "perfect, save this", "the tone is off" |
| `strategic` | High-level thinking, planning, decision-making | "should I focus on X or Y", "what's the next 30-day plan" |
| `emotional` | Mood / wellbeing / vent — not transactional | "tired hu", "kuch samajh nahi aa raha", "frustrating day" |
| `correction` | Direct rule update — "from now on do X", "stop doing Y" | "remember karo always to use full forms", "stop summarising" |
| `greeting` | Pure social glue, no payload | "hi", "namaste", "thanks", "gn" |
| `unknown` | Cannot confidently classify after one pass | Garbled, ambiguous, or new shape |

## Behavioural contract

- MUST return a valid `IntentResult` within the deadline (default 3s) for every call
- MUST skip classification (return synthetic `greeting` or `task` with confidence=1.0) when:
  - Message starts with `/` (slash command → synthetic `task`, priority `normal`)
  - Message length < 4 characters (→ `greeting` if matches greeting regex, else `unknown`)
- MUST use Haiku-class model (default `claude-haiku-4-5-20251001`) — cheapest fast model
- MUST cap classifier turns at 1 (single completion, no tool use)
- MUST output a single JSON object — same parsing pattern as `critic.py`
- MUST append one JSONL line per call to `data/logs/intent.jsonl` with: `ts, user_id, msg_hash, msg_len, category, priority, confidence, latency_ms, skipped_reason, error`
- MUST honour `JARVIS_INTENT_ENABLED=0` kill-switch → return synthetic `unknown` with `skipped_reason="disabled"`, daemon proceeds as before
- MUST NOT raise on backend failure → fall back to synthetic `unknown`, log the error
- MUST NOT mutate any external state
- SHOULD prefer category `correction` over `feedback` when message contains imperatives like "always", "never", "from now on", "yaad rakhna"
- SHOULD prefer `task` over `question` when message contains action verbs ("kar", "banao", "send", "fix", "deploy")

## Priority derivation

The model self-reports priority, but we override to enforce floor/ceiling:

- `urgent` permitted only when message contains explicit urgency markers: `urgent`, `asap`, `now`, `abhi`, `jaldi`, `emergency`, `down`, `broken`, `prod`
- `greeting` and `unknown` are always `low`
- `correction` is always at least `high` (Boss is updating a rule — must not be ignored)
- `emotional` is always at least `normal` (treat gently, never spam follow-ups)
- Default fallback: `normal`

## Failure modes

| Failure | Detection | Response |
|---------|-----------|----------|
| Haiku call times out | `asyncio.wait_for` raises | Log `intent_timeout`, return synthetic `unknown` |
| Backend / network error | Exception from `run_worker` | Log `intent_error`, return synthetic `unknown` |
| Malformed JSON output | `json.loads` fails on all candidates | Log `json_parse_failed`, return synthetic `unknown` |
| Unrecognised category string | Not in 8-enum | Coerce to `unknown` |
| Kill-switch off | `JARVIS_INTENT_ENABLED=0` | Synthetic `unknown` with `skipped_reason="disabled"` |

## Eval cases

`data/evals/intent/test_cases.jsonl` covers:

1. **Task — build**: "Anisha ke liye ek message draft karo" → `task` / `normal`
2. **Task — fix**: "the daemon is throwing 500s, fix it" → `task` / `high` (`broken` keyword)
3. **Question — factual**: "what is the airspeed velocity of an unladen swallow" → `question` / `low`
4. **Question — status**: "kal ka briefing kya tha" → `question` / `normal`
5. **Feedback — praise**: "this is solid, perfect" → `feedback` / `low`
6. **Feedback — correction-flavoured praise**: "good but next time use Hinglish" → `feedback` (NOT `correction`, since past-tense)
7. **Strategic**: "should I commit to Tata Steel or DevNetwork AI for the next month?" → `strategic` / `normal`
8. **Emotional**: "yaar kuch ho nahi raha, frustrating hai" → `emotional` / `normal`
9. **Correction — always**: "from now on always use respectful forms" → `correction` / `high`
10. **Correction — never**: "kabhi mat send karo without confirmation" → `correction` / `high`
11. **Greeting**: "namaste boss" → `greeting` / `low`
12. **Slash command**: "/plan-day" → synthetic `task` (skip)
13. **Trivial**: "ok" → `greeting` / `low`
14. **Urgency override**: "abhi fix karo prod is down" → `task` / `urgent`
15. **Ambiguous**: gibberish → `unknown` / `low`

## Non-goals

- Does NOT route to specific subagents — that is the worker's job (the intent is an input hint, not a hard route)
- Does NOT decide auto-mode tier — `auto-mode` skill owns that decision
- Does NOT do entity extraction — keep this layer narrow and fast
- Does NOT cache classifications across calls — every message classified fresh

## Dependencies

- Code: `jarvis_core/orchestrator.py:run_worker()` — used to invoke Haiku
- Code: `jarvis_core/confidence.py` — for parse-output JSON discipline (shared regex pattern)
- Data: `data/logs/intent.jsonl` — append-only audit
- Env vars:
  - `JARVIS_INTENT_ENABLED` (default `1`)
  - `JARVIS_INTENT_MODEL` (default `claude-haiku-4-5-20251001`)
  - `JARVIS_INTENT_TIMEOUT_S` (default `3`)

## Changelog

- 2026-05-15: Initial draft. Added after Ratnesh's-Jarvis comparison surfaced the missing explicit-classification gap.
