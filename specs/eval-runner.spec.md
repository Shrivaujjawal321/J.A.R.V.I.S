# Spec: Eval Runner

**Status:** active
**Owner:** `scripts/eval_runner.py` + `scripts/eval_baseline.py`
**Last reviewed:** 2026-05-13

## Purpose

Two-piece evaluation system:

1. `eval_runner.py` — per-agent regression harness with two modes:
   - **design-mode** (default): generates evaluator-ready markdown packages Boss pastes into a Claude Code session manually. Produces report files. Always works.
   - **headless-mode** (experimental): calls `claude -p` directly. May fail in some environments.
2. `eval_baseline.py` — aggregates the latest reports under `data/evals/reports/` into a published `data/evals/baseline.md` + `baseline.json`. Provides a `--check` mode that exits non-zero if any agent's pass rate drops > 5pp vs the saved baseline. Used as a quality gate by Phase E's self-growth loop before auto-applying Tier-1 prompt tweaks.

## Inputs

| Name | Type | Source | Notes |
|------|------|--------|-------|
| Test cases | YAML | `data/evals/{agent}/test-cases.yaml` | Per-agent scenario specs |
| Agent prompts | Markdown | `data/agent-prompts-final/{agent}.md` | Final tier prompts |
| Existing reports | Markdown/JSON | `data/evals/reports/` | Used by baseline + regression check |

## Outputs

| Name | Type | Notes |
|------|------|-------|
| Evaluator packages | Markdown | `data/evals/_packages/{date}/` — design-mode |
| Per-agent reports | Markdown/JSON | `data/evals/reports/{date}-{agent}.md` |
| Baseline aggregate | Markdown + JSON | `data/evals/baseline.md`, `baseline.json` |
| Telegram alerts | message | On regression with `--notify` |

## Behavioural contract

- MUST treat pending/manual cases as NOT failures (they count toward `pending`, not `failed`)
- MUST compute pass_rate = passed / total per agent
- MUST publish baseline as both `.md` (human) and `.json` (machine)
- MUST exit non-zero from `--check` if any agent drops > threshold (default 0.05)
- MUST be idempotent — re-running `--baseline` over same inputs produces same output
- MUST NOT re-run agents in `--check` mode (use existing reports only)
- SHOULD print regression details with prev → current rates

## Failure modes

| Failure | Response |
|---------|----------|
| Missing test-cases.yaml for an agent | Skip that agent silently |
| Missing report file | Mark agent `status=no_report` in baseline |
| Malformed report markdown | Best-effort regex parse; if total=0 the agent is excluded |
| No prior baseline.json on `--check` | Print warning, exit 0 (can't regress with nothing to compare) |

## Eval cases

Self-referential — this runner has no automated tests of itself. Verification: run `--baseline` then `--check` on the same inputs (must exit 0); modify a report to lower pass count, run `--check` again (must exit 1).

## Non-goals

- Does NOT run agents in headless mode by default — too brittle across environments
- Does NOT re-run failing tests automatically
- Does NOT modify agent prompts based on eval results (Phase E proposes; humans/Tier-1 apply)
- Does NOT support continuous-mode polling (one-shot per invocation)

## Dependencies

- Python: `pyyaml`, `requests` (optional for Telegram)
- Data: `data/evals/`, `data/agent-prompts-final/`, `bridge/.env` (for Telegram)
- Env vars: `EVAL_MODE` (design|headless), `EVAL_NOTIFY` (auto-send)

## Changelog

- 2026-05-13: Phase F — added `scripts/eval_baseline.py` companion + spec
