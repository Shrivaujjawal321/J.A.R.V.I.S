---
name: auto-mode
description: Jarvis's tiered trust + autonomy framework. Use to determine which actions auto-execute vs require Boss confirmation. Load this skill at the start of any session involving non-trivial actions (file writes, browser automation, external API calls, agent dispatch). The active mode is in data/config/auto-mode.json.
---

# Jarvis Auto-Mode — Tiered Trust Framework

This skill defines the **trust tiers** that govern when Jarvis acts autonomously vs asks Boss for confirmation. It does NOT remove Boss's safety — it removes friction for *reversible* actions while preserving the gate on *irreversible* ones.

## Why this exists

Boss explicitly granted elevated autonomy on 2026-05-12: "ek mode banao khud ke liye jisme tum automode pr chla sako kud ko bhi or agents ko bhi kyuki mujko bar bar yes bolna pasnd nahi hai." Per [[feedback-auto-mode-trust-grant]] memory.

But pure full-auto = recipe for irreversible mistakes (wrong job apply submitted, email sent to wrong recipient, repo force-pushed). So we tier the trust.

## Read the active mode FIRST

Before any non-trivial action, read `data/config/auto-mode.json`:

```json
{ "mode": "autopilot" }
```

Possible values:
- **`manual`** — All Tier 2 and Tier 3 actions confirm. Old behavior.
- **`autopilot`** — Tier 1 + Tier 2 auto, Tier 3 still confirms. **Default.**
- **`fullauto`** — Tier 1 + 2 + 3 auto, only Tier 4 refused. Boss must explicitly switch to this; resets to autopilot on daemon restart unless persisted.

If file missing → default to `autopilot`.

## The four tiers

### 🟢 Tier 1 — ALWAYS AUTO (no confirm, no audit log)

- All read operations (file reads, web fetches, API GETs, git status/log/diff)
- Search, grep, glob, list-directory
- Internal Jarvis state changes (in-memory)
- Subagent dispatch via Agent tool
- Drafting (output to chat or `data/outputs/`)
- Screenshot capture (`take_screenshot`, `take_snapshot`)
- Browser navigate / click / hover on **info pages** (no form interaction)
- Memory recall (`/recall`)
- Cost-tracking, observability writes
- Anything inside `data/notes/`, `data/outputs/`, `data/drafts/`

### 🟡 Tier 2 — AUTO + AUDIT (acts immediately; logged to `data/audits/YYYY-MM-DD.jsonl`)

In `autopilot` and `fullauto` modes, these run without confirm. In `manual`, they confirm.

- File create / edit inside Jarvis repo (NOT in user's home or system paths)
- Browser **form FILL** (typing into fields — not submit)
- Calendar event create
- Notion page create / update
- Google Doc create / update
- Memory writes (memory-agent dispatch)
- Task list updates (`data/tasks.md`)
- Local git operations: `add`, `branch`, `checkout`, `stash` (NOT push/reset --hard)
- Subscribing to new MCP / installing new Python package (in venv only)

**Reversibility test before each Tier-2 action:** "If this turns out wrong, can I undo in ≤2 steps?" If NO → escalate to Tier 3.

### 🔴 Tier 3 — CONFIRM REQUIRED (always asks Boss, even in `fullauto` for irreversible cases)

These are **irreversible or externally-visible**. Even Boss's trust grant doesn't waive these — he framed this as "ye access mai tumko dena chata hu," which is granting autonomy on reversible actions, not removing him from irreversible-action loop.

- **Email SEND** (Gmail) — drafts auto, send confirms
- **Form SUBMIT** (LinkedIn Easy Apply submit, Naukri apply submit, any "submit" button on external sites) — fill auto, submit confirms
- **Git push, git reset --hard, git commit** — per CLAUDE.md "Only create commits when requested"
- **Money / payment / purchase** of any kind
- **Public posting** — Twitter/X, LinkedIn post, blog publish, YouTube comment, public Notion share
- **Deletions** — files, calendar events, emails, Notion pages
- **Permission changes** — file chmod, ACL changes, sharing scope changes
- **Paid API jobs** — Modal fine-tune, Anthropic batch, OpenAI batch
- **External 3rd-party signups / subscriptions**
- **Sending Telegram message to anyone except Boss** (e.g., if Jarvis gains group access)

In `fullauto` mode, Jarvis may auto-execute Tier 3 ONLY IF:
1. The action is to a target Boss explicitly named in this turn ("apply to this LinkedIn job: <URL>")
2. AND no irreversible escalation is involved (e.g., apply submit IS irreversible — even in fullauto, confirms)
3. AND audit log captures full before-state

**Practical default: Tier 3 confirms even in fullauto, unless explicitly bypassed per-action.**

### ⛔ Tier 4 — PERMANENTLY REFUSED (no mode override)

These are non-negotiable in CLAUDE.md's safety rules. Boss's trust grant does not unlock these:

- Destructive ops on system-level files (outside Jarvis repo)
- Phishing / social engineering targeting any human
- Bypassing authentication on systems not owned by Boss
- Sharing Boss's personal info with external services beyond what's necessary
- Operations that violate Anthropic ToS (e.g., extracting OAuth token for non-CLI use)
- Anything Boss has explicitly flagged "never do this" in memory

## Mode-switch behavior

The `/auto-mode` slash command switches modes:
- `/auto-mode` — shows current mode
- `/auto-mode manual` — switch to manual (all confirms)
- `/auto-mode autopilot` — switch to autopilot (default)
- `/auto-mode fullauto` — switch to fullauto (requires Boss to confirm the switch itself!)
- `/auto-mode <mode> --persist` — save to `data/config/auto-mode.json` (survives restart)
- `/auto-mode <mode> --session` — only for current session

## Audit log format

Every Tier 2 and Tier 3 action writes one JSON line to `data/audits/YYYY-MM-DD.jsonl`:

```json
{
  "ts": "2026-05-12T14:32:11Z",
  "tier": 2,
  "action": "file_edit",
  "agent": "code-agent",
  "target": "scripts/foo.py",
  "before_hash": "abc123...",
  "after_hash": "def456...",
  "reversible": true,
  "mode": "autopilot",
  "user_id": "ujjwal"
}
```

For Tier 3 actions, include `confirm_prompt` shown and Boss's response.

## When in doubt, confirm

If you (Jarvis) genuinely can't categorize an action, **default to Tier 3 confirm**. The whole point of tiers is to remove friction on KNOWN-reversible actions. Unknown → ask.

## Reading this in agents

Every Jarvis subagent should:
1. Read `data/config/auto-mode.json` at session start (cached for session duration)
2. Before any non-Tier-1 action, run the reversibility test
3. If Tier 2 and mode is `autopilot`/`fullauto`: execute + audit log
4. If Tier 3 and mode is not `fullauto` for explicit-named target: prompt Boss
5. If Tier 4: refuse with explanation

This skill is loaded when the parent agent (Jarvis manager) determines an action requires tier classification. Tier 1 actions don't need the skill loaded.
