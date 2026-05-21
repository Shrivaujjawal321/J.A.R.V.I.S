# Spec: Critic Layer

**Status:** active
**Owner:** `jarvis_core/critic.py`, `jarvis_core/confidence.py`
**Last reviewed:** 2026-05-13

## Purpose

After the primary worker produces a reply, a silent critic agent reviews the draft against four dimensions (intent-match, memory-contradiction, claim-sourcing, tone). If the verdict is `revise`, exactly one revision pass runs. The final reply carries a confidence tag (`verified` / `unverified` / `low`).

Without this layer, Jarvis can silently hallucinate, contradict memory, ignore Boss's question, or drop into casual/disrespectful register. Boss has to catch these manually. The critic closes that loop.

## Inputs

| Name | Type | Source | Notes |
|------|------|--------|-------|
| `user_message` | `str` | original `/chat` input | The question the critic checks intent against |
| `jarvis_reply` | `str` | worker output | The draft being reviewed |
| `memory_context` | `str` | `Recaller.gather()` output | Used to detect contradictions |
| `project_root` | `Path` | daemon constant | Passed to `run_worker` for the critic sub-call |

## Outputs

| Name | Type | Consumer | Notes |
|------|------|----------|-------|
| `final_reply` | `str` | `ChatResponse.reply` | Either original or revised, with optional confidence suffix |
| `confidence` | `Literal["verified", "unverified", "low"]` | `ChatResponse.confidence` (new field) | Surfaced to user via inline tag on long replies |
| `critique_log` | `dict` | `data/logs/critic.jsonl` | One line per non-skipped invocation |

## Behavioural contract

- MUST skip critique (return original reply + `verified`) when:
  - Reply length < 100 characters
  - User message length < 50 characters (trivial question)
  - User message starts with `/` (slash commands self-validate)
  - Reply is a pure tool-error message starting with `⚠️`
- MUST emit critic prompt as a single string to a Haiku-class worker (no tool use, `max_turns=1`, `allowed_tools=[]`)
- MUST parse critic output as JSON `{verdict, confidence, issues, suggestion}`. On parse failure, log and treat as `verdict=ok, confidence=unverified`
- MUST cap revision at exactly ONE pass — never recurse
- MUST append confidence tag visibly only for `unverified` / `low` (verified is silent; assumed default)
- MUST append one JSONL line per non-skipped call to `data/logs/critic.jsonl` with: ts, user_id, verdict, confidence, latency_ms, revised (bool), issues (list)
- MUST honour `JARVIS_CRITIC_ENABLED=0` kill-switch — returns original reply with `verified` tag, no LLM call
- MUST NOT raise on critic-call failure — log, return original reply with `unverified`
- MUST NOT block the main response longer than 8s — timeout falls back to original reply
- SHOULD use Haiku 4.5 (`claude-haiku-4-5-20251001`) for cost/latency; fall back to Sonnet 4.6 on Haiku error

## Critique rubric (passed to critic LLM)

The critic prompt asks four binary checks:

1. **INTENT** — Does the reply answer Boss's actual question? (Not: did it answer some adjacent question?)
2. **MEMORY** — Any contradictions with the supplied memory context? (e.g., reply says "Boss prefers English" but memory says "Hinglish")
3. **CLAIMS** — Are factual / counted / dated claims either sourced or properly hedged? (Unsourced "Boss has 12 hackathons coming up" is a fail; "Boss recently mentioned hackathons" is a pass)
4. **TONE** — Hinglish respectful register? No shortened forms ("bta", "kr", "dkh")? Uses "aap" never "tu"?

Verdict logic:
- All 4 pass → `ok` + `verified`
- 1 fails on TONE only → `revise` + `unverified`
- 1-2 fail on INTENT/MEMORY/CLAIMS → `revise` + `unverified`
- 3+ fail → `revise` + `low`

## Failure modes

| Failure | Detection | Response |
|---------|-----------|----------|
| Critic LLM call times out | `asyncio.wait_for` 8s | Return original reply + `unverified` tag |
| Critic returns non-JSON | `json.loads` exception | Log raw output, return original + `unverified` |
| Revision pass times out | Same 8s timeout on revise | Return ORIGINAL reply (not partial revision) + `unverified` |
| Revision yields empty text | Result text strip = empty | Return original reply + `unverified` |
| Backend down (network) | Exception | Return original reply + `unverified`, log error |

## Eval cases

`data/evals/critic/test_cases.jsonl` covers:

1. **Catches memory contradiction**: reply contradicts injected memory ctx → verdict=revise
2. **Catches tone violation**: reply uses "bta", "kr" → verdict=revise (tone), confidence=unverified
3. **Catches intent miss**: question asks X, reply answers Y → verdict=revise
4. **Catches unsourced claim**: reply states specific number with no source → verdict=revise
5. **Passes clean reply**: well-formed reply that respects memory, intent, register → verdict=ok
6. **Skips trivial**: reply < 100 chars → no critic call (verified silent)
7. **Skips slash command**: input is `/triage` → no critic call
8. **Revises once**: revise verdict → one new reply produced, no second revise call

## Non-goals

- Does NOT fact-check the WEB (would need web tool, expensive — Phase F may add)
- Does NOT measure latency / cost (observability layer's job)
- Does NOT write its own feedback to `feedback.jsonl` (that's Boss-driven only)
- Does NOT loop / iterate / multi-revise — exactly one revision attempt max
- Does NOT enforce style beyond the four rubric checks
- Does NOT block low-confidence replies — they still ship with the tag, Boss decides

## Dependencies

- Code: `jarvis_core/orchestrator.py:run_worker()` — used for critic sub-call
- Code: `jarvis_core/confidence.py` — tag formatting helpers
- Code: `jarvis_core/recall.py:Recaller` — provides `memory_context` input
- Env vars: `JARVIS_CRITIC_ENABLED` (default: 1), `JARVIS_CRITIC_MODEL` (default: haiku-4-5), `JARVIS_CRITIC_TIMEOUT_S` (default: 8)
- Cost budget: ~1 extra LLM call per non-skipped chat → ~$0.05/day at 50 chats

## Changelog

- 2026-05-13: Initial draft (Phase B MVP)
