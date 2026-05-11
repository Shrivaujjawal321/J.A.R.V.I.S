# Jarvis Phase 5 — Agent Eval Framework

Automated regression testing for Jarvis agent prompts.

---

## Quick Start

```bash
# Run eval for one agent (generates evaluator packages in design-mode)
.venv/bin/python scripts/eval_runner.py code-reviewer

# Run all agents
.venv/bin/python scripts/eval_runner.py --all

# Regression check (compare today vs last run)
.venv/bin/python scripts/eval_runner.py --regression

# With Telegram notification on regressions
.venv/bin/python scripts/eval_runner.py --all --notify

# Headless mode (experimental — see Limitations below)
EVAL_MODE=headless .venv/bin/python scripts/eval_runner.py code-reviewer
```

---

## Directory Structure

```
data/evals/
├── {agent-slug}/
│   ├── test-cases.yaml          # Test inputs + expected qualities + rubric
│   └── reports/
│       └── {YYYY-MM-DD}.md      # Per-run eval reports
├── _packages/
│   └── {YYYY-MM-DD}/
│       └── {agent}_{tc-id}_eval.md   # Design-mode evaluator packages (temp)
└── reports/
    └── summary-{YYYY-MM-DD}.md  # Cross-agent summary (generated with --all)
```

---

## Two Modes of Operation

### Design-Mode (default, recommended)

The runner does NOT call Claude directly. Instead, it generates **evaluator-ready
prompt packages** — self-contained markdown files with:

1. The extracted agent system prompt
2. The test input
3. A scoring rubric with min scores per dimension
4. Instructions for manual evaluation

You paste these into a Claude Code session yourself, score the output, and
record scores in the report file.

**When to use:** Always, unless you have an Anthropic API key (not subscription).

### Headless-Mode (experimental)

Set `EVAL_MODE=headless` to attempt `claude -p` (Claude Code headless mode) with
the agent system prompt and test input.

**Limitations:**
- Requires Claude Code to be authenticated with a subscription
- `claude -p` spawns a full Claude Code session — resource-intensive
- Auto-mode classifier may block nested `claude` invocations in certain contexts
  (specifically `--dangerously-skip-permissions` is blocked in auto-mode)
- Even if output is captured, **automated scoring still requires an API key**
  for LLM-as-judge. Without it, headless mode captures output but leaves
  scoring as PENDING_MANUAL
- **Bottom line:** headless mode is useful for capturing agent outputs for
  manual review. True automated LLM-as-judge scoring needs `ANTHROPIC_API_KEY`.

**Headless mode verdict (tested 2026-05-11):**
`claude -p` binary exists and supports `--system-prompt`. However, when running
inside Claude Code auto-mode, nested `claude` invocations with
`--dangerously-skip-permissions` are blocked by the auto-mode classifier for safety.
Running from a plain terminal session (outside Claude Code) should work.
The missing piece for full automation remains: automated scoring requires the
Anthropic API (not the subscription/OAuth flow).

---

## Test Case Format

```yaml
agent: {agent-slug}
agent_file: data/agent-prompts-final/{agent-slug}.md   # optional, inferred if omitted

test_cases:
  - id: tc-001
    name: "Short descriptive name"
    input: |
      The exact input you would send to the agent.
      Can be multi-line. Use realistic but synthetic data.
    expected_qualities:
      - "What the response should do — phrased as observable behavior"
      - "Another observable quality"
      - "Use positive assertions: 'flags X as BLOCKER', not 'does not miss X'"
    rubric_dimensions:
      - name: "Dimension Name"
        description: "What Excellent (5) looks like for this dimension"
        min_score: 4       # 1-5, default 4
    min_score_per_dim: 4   # fallback if dimension-level not set
    tags: [optional, tags, for-filtering]
```

**Tips for writing good test cases:**
- Use realistic but synthetic inputs (no real PII, no real private data)
- Each test case should exercise a specific failure mode or quality dimension
- Target 2-4 test cases per agent — enough to catch regressions, not so many
  that eval runs become expensive
- `expected_qualities` are human-readable checklists for manual scoring
- `rubric_dimensions` should map directly to the agent's self-evaluation rubric

---

## How to Add Test Cases for a New Agent

1. Create the directory: `data/evals/{agent-slug}/`
2. Copy `data/evals/code-reviewer/test-cases.yaml` as a template
3. Set `agent` and `agent_file` to point at the right prompt file
4. Write 2-4 test cases with realistic inputs
5. Run: `.venv/bin/python scripts/eval_runner.py {agent-slug}`

---

## How to Interpret Reports

Each report at `data/evals/{agent}/reports/{YYYY-MM-DD}.md` contains:

- **PASS** — all rubric dimensions scored >= min_score (automated scoring only)
- **FAIL** — at least one dimension below min_score
- **PENDING_MANUAL** — output captured or package generated; needs human scoring
- **ERROR** — runner encountered an exception (check error field)

In design-mode, all results start as PENDING_MANUAL. After manually evaluating
via the generated package, edit the report to record actual scores.

---

## Agents with Test Cases (bootstrapped)

| Agent | Test Cases | File |
|-------|-----------|------|
| code-reviewer | 2 | `data/evals/code-reviewer/test-cases.yaml` |
| research-analyst | 2 | `data/evals/research-analyst/test-cases.yaml` |
| customer-support | 2 | `data/evals/customer-support/test-cases.yaml` |
| prompt-engineer | 2 | `data/evals/prompt-engineer/test-cases.yaml` |
| career-coach | 2 | `data/evals/career-coach/test-cases.yaml` |

---

## Nightly Eval Cron (Phase 5+ Roadmap)

To automate evals nightly:

```bash
# Example crontab entry (add via: crontab -e)
# Runs at 02:00 daily, logs to data/logs/eval-cron.log
0 2 * * * .venv/bin/python scripts/eval_runner.py --all --notify >> data/logs/eval-cron.log 2>&1
```

**Prerequisites for full automation:**
1. **Anthropic API key** — for LLM-as-judge automated scoring. Without it, the runner
   generates packages but cannot score them. Add `ANTHROPIC_API_KEY` to bridge/.env
   and enable the scoring pass in eval_runner.py.
2. **Headless mode working** — `claude -p` works from cron (outside Claude Code auto-mode).
   Test with: `EVAL_MODE=headless .venv/bin/python scripts/eval_runner.py code-reviewer`
3. **Telegram bridge running** — jarvis-bridge.service must be active for regression alerts.

**Integration points:**
- `send_telegram()` in eval_runner.py reads from `bridge/.env` (TELEGRAM_BOT_TOKEN,
  ALLOWED_USER_IDS) — same pattern as existing bridge
- Reports land in `data/evals/{agent}/reports/` — same structure as `data/briefings/`
- Regression detection compares pass/fail counts vs the previous report file

**LLM-as-judge scaffold (add when API key is available):**
Replace the scoring stub in `run_agent()` with a call to the Anthropic SDK:
```python
from anthropic import Anthropic
client = Anthropic()  # reads ANTHROPIC_API_KEY from env
score_response = client.messages.create(
    model="claude-haiku-4-x",
    system=JUDGE_SYSTEM_PROMPT,
    messages=[{"role": "user", "content": judge_input}],
)
```
Where `JUDGE_SYSTEM_PROMPT` instructs the model to score against the rubric dimensions
and return a structured JSON score object.

---

## Maintenance

- Add test cases as new agents are promoted to `data/agent-prompts-final/`
- Update `min_score` when you raise the quality bar for an agent
- Archive reports older than 30 days: `find data/evals/*/reports/ -name "*.md" -mtime +30`
- The `_packages/` directory is transient — safe to clean up after scoring

---

*Phase 5 eval framework — built 2026-05-11*
