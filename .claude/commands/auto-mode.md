# /auto-mode — Switch Jarvis trust/autonomy mode

Show or change which actions Jarvis auto-executes vs confirms. Backed by the tiered trust framework in `.claude/skills/auto-mode/SKILL.md`.

## Usage

```
/auto-mode                           # Show current mode + tier summary
/auto-mode manual                    # All Tier 2 and Tier 3 confirm (old behavior)
/auto-mode autopilot                 # Tier 1+2 auto, Tier 3 confirms (default)
/auto-mode fullauto                  # Tier 1+2+3 auto except Tier 4 — POWER MODE
/auto-mode <mode> --persist          # Save to data/config/auto-mode.json (survives restart)
/auto-mode <mode> --session          # In-memory only, resets on daemon restart
/auto-mode log [N]                   # Show last N audit entries (default 20)
```

## What This Does

### Mode: show current

1. Read `data/config/auto-mode.json`
2. Show: current mode, when it was set, by whom
3. Show tier summary:
   - Tier 1 (always auto): reads, drafts, screenshots, subagent dispatch
   - Tier 2 (auto + audit in current mode): files, browser fill, calendar create, memory writes
   - Tier 3 (always confirms): email send, form submit, git push, deletions, public posts
   - Tier 4 (refused): system destruction, phishing, ToS violations
4. Last 3 audit-log entries from `data/audits/YYYY-MM-DD.jsonl` for context

### Mode: switch

1. Validate target mode (`manual` / `autopilot` / `fullauto`)
2. **If switching TO `fullauto`:** ALWAYS confirm with Boss first, regardless of current mode — this is the one switch that itself requires confirmation. Show what unlocks in fullauto and what stays gated (Tier 4 refusals).
3. Update `data/config/auto-mode.json` (if `--persist`) or process-local state (if `--session`)
4. Log the switch event to `data/audits/{today}.jsonl` with tier=meta, action=mode_change
5. Telegram-confirm: "Mode → {new}. {one-line summary of what changed}"

### Mode: log

1. Tail last N lines from `data/audits/{today}.jsonl`
2. Format as a readable table: timestamp | tier | agent | action | target
3. If empty: "No tier-2 or tier-3 actions today yet."

## Hard Rules

- **NEVER auto-switch to fullauto** — always confirm with Boss explicitly. The "auto" granted by trust applies to action execution, NOT to elevating own trust level.
- **NEVER modify Tier 4 refusals** via this command. Those are CLAUDE.md-level safety, not mode-controlled.
- Mode switch is itself a Tier 2 action (auto + audit log). Mode switch TO fullauto is a Tier 3 (confirm) regardless.
- If `data/config/auto-mode.json` is malformed, log warning and default to `autopilot`. Don't silently switch to `manual` (that breaks Boss's expectations) and don't switch to `fullauto` (unsafe default).

## Telegram output format

```
Mode: autopilot  (set 2026-05-12 by /auto-mode --persist)

Tier 1 (auto):       reads · drafts · screenshots · subagent dispatch
Tier 2 (auto+log):   file edits · form fill · memory writes · calendar create
Tier 3 (confirm):    email send · form submit · git push · public posts · deletions
Tier 4 (refused):    system destruction · phishing · ToS violations

Recent (last 3):
2026-05-12 14:32  T2  code-agent           file_edit       scripts/foo.py
2026-05-12 14:30  T2  browser-autopilot    form_fill       linkedin.com/jobs/...
2026-05-12 13:11  T2  memory-agent         memory_write    facts.md
```
