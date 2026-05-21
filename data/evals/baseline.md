# Jarvis Evaluation Baseline

**Generated:** 2026-05-13 (by `scripts/eval_baseline.py`)
**Overall:** 0/0 passed (0.0%)

This file aggregates the latest per-agent reports under `data/evals/reports/`. 
It is the reference Phase E (`self_growth_weekly.py`) compares against when 
auto-applying Tier-1 prompt tweaks. Drops below the recorded rate trigger a halt.

## Per-agent results

| Agent | Passed | Failed | Pending | Total | Pass Rate | Report |
|-------|-------:|-------:|--------:|------:|----------:|--------|
| `career-coach` | 0 | 0 | 0 | 0 | — | — |
| `code-reviewer` | 0 | 0 | 0 | 0 | — | — |
| `critic` | 0 | 0 | 0 | 0 | — | — |
| `customer-support` | 0 | 0 | 0 | 0 | — | — |
| `prompt-engineer` | 0 | 0 | 0 | 0 | — | — |
| `recall` | 0 | 0 | 0 | 0 | — | — |
| `research-analyst` | 0 | 0 | 0 | 0 | — | — |

## Methodology

- Each agent's most-recent file under `data/evals/reports/` is parsed.
- Pass rate = (passed) / (total). Pending tests don't count as failures.
- Markdown reports parse via `X/Y passed` heuristic + status-emoji fallback.
- JSON reports parse the `status` field of each entry.
- A baseline drop > 5pp in any agent triggers a regression alert.

## Regression policy

- Tier-1 prompt tweaks proposed by Phase E require baseline pass rate to hold or improve.
- If `--check` exits non-zero, Phase E falls back to drafting only — no auto-apply.