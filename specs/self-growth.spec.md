# Spec: Self-Growth Weekly Loop

**Status:** active
**Owner:** `scripts/self_growth_weekly.py`
**Last reviewed:** 2026-05-13

## Purpose

Every Sunday at 20:00 IST, Jarvis reviews its own past week (feedback, audits, eval deltas, failed goals, conversation themes, recall/critic stats) and produces 3-5 concrete change proposals. Each proposal carries a tier (1/2/3). **Tier 1+2 auto-apply** within safe paths; **Tier 3 queues as `ApprovalRequest` for Boss's nod**. A Telegram digest summarises what was applied vs awaiting.

This is the meta-loop that turns Jarvis from a static assistant into something that grows weekly without Boss having to manually steer every change.

Boss's confirmed autonomy decision (2026-05-13): "Tier 1+2 auto, Tier-3 confirm". The script enforces this strictly via the `_SAFE_PATHS` allow-list — even a Tier-1 proposal that tries to modify daemon core code is downgraded to Tier-3 and queued for approval.

## Inputs

| Name | Source | Why it matters |
|------|--------|---------------|
| Feedback | `data/logs/feedback.jsonl` | Raw Boss corrections — the ground truth of "what hurt" |
| Recall log | `data/logs/recall.jsonl` | Hit rates, skipped reasons, top-score distribution |
| Critic log | `data/logs/critic.jsonl` | Verdict distribution, revise rate per week |
| Auto-capture log | `data/logs/auto_capture.jsonl` | Capture pipeline health, chunks added |
| Reasoning trigger log | `data/logs/reasoning_trigger.jsonl` | Were proactive nudges useful? |
| Audit log | `data/audits/*.jsonl` | Tier-2/3 actions taken |
| Eval baseline | `data/evals/baseline.json` | Quality gate — applies only if not regressed |
| Goals | jarvis-core state | Failed/cancelled goal patterns |
| Existing specs | `specs/*.md` | What already exists (avoid duplicate proposals) |
| Claude API | via `run_worker` | Sonnet-class for strategic synthesis |

## Outputs

| Name | Type | Notes |
|------|------|-------|
| Proposal doc | Markdown | `data/growth/proposals/{YYYY-MM-DD}.md` — human-readable |
| Proposal data | JSON | `data/growth/proposals/{YYYY-MM-DD}.json` — machine-readable |
| Changelog | Markdown (append-only) | `data/growth/changelog.md` — what was actually applied |
| Telegram digest | message | Summary of week + applied + awaiting approval |
| Approval records | `ApprovalRequest` entries | Pushed to jarvis-core state for Tier-3 proposals |
| Run log | JSONL | `data/logs/self_growth.jsonl` |

## Behavioural contract

- MUST run idempotently — same week's signals MUST produce the same proposal file
  (achieved via deterministic file naming + dedup on `proposal_id` content hash)
- MUST cap LLM calls per run at 4 (synthesis + 1 follow-up + safety check + digest format)
- MUST cap total runtime at 8 minutes
- MUST validate every proposed file path against `_SAFE_PATHS` allow-list
- MUST downgrade any proposal targeting a non-safe path to Tier-3 regardless of LLM-assigned tier
- MUST run `eval_baseline.py --check` before auto-applying any Tier-1 change
- MUST refuse to auto-apply if any baseline regression detected — propose only
- MUST git-snapshot project state before applying changes (best-effort, log if git not available)
- MUST append every applied change to `data/growth/changelog.md` with rationale + diff summary
- MUST push every Tier-3 proposal to jarvis-core as an `ApprovalRequest`
- MUST emit Telegram digest even if no proposals (so Boss knows the loop ran)
- MUST honour `JARVIS_SELFGROWTH_ENABLED=0` kill-switch
- MUST honour `JARVIS_SELFGROWTH_DRY_RUN=1` — collect + propose + digest, but no apply
- MUST NEVER auto-apply Tier-3
- MUST NEVER auto-apply within `jarvis_core/*` (always Tier-3)
- MUST NEVER auto-apply within `bridge/*` (always Tier-3)
- MUST NEVER delete files (apply == create or modify only; deletes are Tier-3)
- MUST NEVER apply outside the project repo

## Safe-path allow-list for auto-apply

Proposals whose `target_path` matches one of these prefixes are eligible for Tier-1 or Tier-2 auto-apply:

```
specs/*.spec.md
data/agent-prompts-final/*.md
data/evals/*/*.yaml
data/evals/*/*.jsonl
data/memory/*.md       (Tier-2 only — careful, hand-curated)
data/notes/*.md
data/growth/*.md
CLAUDE.md              (Tier-2 only — append section, no replace)
.claude/agents/*.md    (Tier-2 only — new files only, no modification)
```

Everything else is forced to Tier-3.

## Tier definitions (within this loop)

- **Tier 1** — pure-additive text-only changes:
  - New eval test case (`data/evals/*/test_cases.jsonl` append)
  - Spec doc edit
  - Append-only note in `data/notes/*.md` or `data/growth/*.md`
  - Adjustment to an agent prompt's existing text
- **Tier 2** — file-creation or careful insert:
  - New agent file (`.claude/agents/*-agent.md`)
  - New spec file
  - New eval suite for an existing agent
  - Append a new bullet section to `CLAUDE.md`
- **Tier 3** — anything else (gated by Boss approval)

## Failure modes

| Failure | Response |
|---------|----------|
| Synthesis LLM fails | Log; emit empty digest; exit 0 |
| Baseline regression detected | Skip auto-apply entirely; all proposals shipped as drafts; Telegram notes regression |
| Git snapshot fails | Continue without snapshot; log warning |
| File-write fails for one proposal | Skip that one; continue with rest; log error |
| Telegram send fails | Write digest to `data/growth/proposals/{date}.md` only; log |
| Approval push fails | Retry once; on second fail, fall back to recording in proposals doc |
| Same proposal file already exists today | Refuse to overwrite — re-runs produce one file per ISO date |

## Eval cases

`data/evals/self_growth/test_cases.jsonl` covers:

1. **Empty signals → empty proposals, digest still sent**
2. **Tier-1 proposal in safe path → auto-applied + changelog entry**
3. **Tier-1 proposal in unsafe path (jarvis_core/*) → downgraded to Tier-3 + queued**
4. **Baseline regression detected → all proposals become drafts, no apply**
5. **Tier-3 proposal → only queued, no apply, ApprovalRequest entry created**
6. **Duplicate run on same day → second run is no-op (file exists)**
7. **Boss approval received → Tier-3 proposal moves to applied state on next loop**

## Non-goals

- Does NOT delete files
- Does NOT modify load-bearing code (`jarvis_core/*`, `bridge/*`, `scripts/episodic_memory.py`)
- Does NOT add new MCP servers (always Tier-3 via decomposer + scheduler)
- Does NOT add new systemd timers (Tier-3 — needs manual `systemctl enable`)
- Does NOT touch external services (LinkedIn, Notion, Calendar, Gmail) — those flow through their respective skills
- Does NOT learn — there is no RL training. The "growth" is via prompt + capability proposals that the Tier-1/2 auto-apply rules let through.

## Dependencies

- Code: `jarvis_core/orchestrator.py:run_worker()` — LLM dispatch
- Code: `scripts/eval_baseline.py --check` — quality gate
- Data: read everything under `data/logs/`, `data/audits/`, `data/evals/`,
  `specs/`, `data/state/jarvis-state.json`
- Env vars: `JARVIS_SELFGROWTH_ENABLED` (default 1), `JARVIS_SELFGROWTH_DRY_RUN` (default 0),
  `JARVIS_SELFGROWTH_MODEL` (default `claude-sonnet-4-6` — strategic > Haiku here),
  `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`, `JARVIS_CORE_URL` (default `http://127.0.0.1:8765`)
- Systemd: `systemd/jarvis-self-growth.timer`

## Changelog

- 2026-05-13: Initial draft (Phase E)
