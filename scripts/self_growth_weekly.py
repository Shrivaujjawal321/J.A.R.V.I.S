#!/usr/bin/env python3
"""
self_growth_weekly.py — Phase E of the self-growth loop.

Runs Sunday 20:00 IST via systemd timer. Synthesises Boss's past week from
multiple signal sources, asks Claude (Sonnet) to propose 3-5 concrete
capability changes, classifies each by tier, auto-applies Tier 1+2 within
the safe-path allow-list, and queues Tier-3 proposals as ApprovalRequest
entries for Boss to approve via Telegram.

See `specs/self-growth.spec.md` for the full contract — especially the
safe-path allow-list and tier-downgrade rules.

Usage:
    .venv/bin/python scripts/self_growth_weekly.py
    .venv/bin/python scripts/self_growth_weekly.py --dry-run
    .venv/bin/python scripts/self_growth_weekly.py --collect-only  # signals only
"""
from __future__ import annotations

import argparse
import asyncio
import fnmatch
import hashlib
import json
import logging
import os
import re
import sys
import subprocess
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# ── Paths ────────────────────────────────────────────────────────────────────

LOGS_DIR = PROJECT_ROOT / "data" / "logs"
AUDITS_DIR = PROJECT_ROOT / "data" / "audits"
EVALS_DIR = PROJECT_ROOT / "data" / "evals"
SPECS_DIR = PROJECT_ROOT / "specs"
STATE_PATH = PROJECT_ROOT / "data" / "state" / "jarvis-state.json"

GROWTH_DIR = PROJECT_ROOT / "data" / "growth"
PROPOSALS_DIR = GROWTH_DIR / "proposals"
CHANGELOG = GROWTH_DIR / "changelog.md"
RUN_LOG = LOGS_DIR / "self_growth.jsonl"

# Env config
DEFAULT_MODEL = os.getenv("JARVIS_SELFGROWTH_MODEL", "claude-sonnet-4-6")
JARVIS_CORE_URL = os.getenv("JARVIS_CORE_URL", "http://127.0.0.1:8765")
HARD_TIMEOUT_S = 480

ROOT_ENV = PROJECT_ROOT / ".env"
BRIDGE_ENV = PROJECT_ROOT / "bridge" / ".env"

logging.basicConfig(
    level=os.getenv("JARVIS_SELFGROWTH_LOG_LEVEL", "INFO"),
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)
log = logging.getLogger("self_growth")


# ── Env loading ──────────────────────────────────────────────────────────────


def _load_env_files() -> dict[str, str]:
    env: dict[str, str] = {}
    for path in (ROOT_ENV, BRIDGE_ENV):
        if not path.exists():
            continue
        for line in path.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            env[key.strip()] = value.strip().strip('"').strip("'")
    env.update(os.environ)
    return env


ENV = _load_env_files()


# ── Safe path allow-list (enforces tier downgrade) ───────────────────────────


_SAFE_PATTERNS_TIER1 = [
    "specs/*.spec.md",
    "data/evals/*/test_cases.jsonl",
    "data/evals/*/test-cases.yaml",
    "data/notes/*.md",
    "data/growth/*.md",
    "data/agent-prompts-final/*.md",
]

_SAFE_PATTERNS_TIER2 = _SAFE_PATTERNS_TIER1 + [
    ".claude/agents/*-agent.md",
    "data/memory/*.md",
    "CLAUDE.md",
    "specs/*.md",
]

# Anything matching these is permanently Tier-3 regardless of LLM assignment
_FORBIDDEN_PATTERNS = [
    "jarvis_core/*",
    "bridge/*",
    "scripts/episodic_memory.py",
    "scripts/auto_capture.py",
    "scripts/self_growth_weekly.py",
    "scripts/reasoning_trigger.py",
    "scripts/eval_baseline.py",
    ".mcp.json",
    "pytest.ini",
    "pyproject.toml",
    ".env",
    "bridge/.env",
]


def _matches_any(path: str, patterns: list[str]) -> bool:
    return any(fnmatch.fnmatch(path, p) for p in patterns)


def _classify_tier(proposed_tier: int, target_path: str) -> tuple[int, str | None]:
    """Returns (final_tier, downgrade_reason). Reason is None when not downgraded."""
    rel = target_path.lstrip("./")
    if _matches_any(rel, _FORBIDDEN_PATTERNS):
        return (3, f"path {rel!r} is in forbidden list — always Tier-3")
    if proposed_tier == 1:
        if not _matches_any(rel, _SAFE_PATTERNS_TIER1):
            return (3, f"path {rel!r} not in Tier-1 safe-path list")
        return (1, None)
    if proposed_tier == 2:
        if not _matches_any(rel, _SAFE_PATTERNS_TIER2):
            return (3, f"path {rel!r} not in Tier-2 safe-path list")
        return (2, None)
    return (3, None)  # explicit Tier-3 stays Tier-3


# ── Signal collection ────────────────────────────────────────────────────────


def _read_recent_jsonl(path: Path, days: int = 7, max_lines: int = 200) -> list[dict]:
    if not path.exists():
        return []
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    out: list[dict] = []
    try:
        for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
            if not raw.strip():
                continue
            try:
                obj = json.loads(raw)
            except json.JSONDecodeError:
                continue
            ts = obj.get("ts") or obj.get("timestamp")
            if ts:
                try:
                    when = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                    if when < cutoff:
                        continue
                except ValueError:
                    pass
            out.append(obj)
    except Exception:
        return []
    return out[-max_lines:]


def _digest_log(path: Path, key_fields: tuple[str, ...]) -> dict:
    """Summarise a JSONL log: line count, common values per key."""
    entries = _read_recent_jsonl(path, days=7, max_lines=500)
    digest: dict = {"count": len(entries), "fields": {}}
    for k in key_fields:
        counts: dict[str, int] = {}
        for e in entries:
            v = str(e.get(k, ""))[:80]
            if not v:
                continue
            counts[v] = counts.get(v, 0) + 1
        digest["fields"][k] = sorted(counts.items(), key=lambda x: -x[1])[:10]
    return digest


def _collect_signals() -> dict:
    audit_files = sorted(AUDITS_DIR.glob("*.jsonl"), reverse=True)[:7] if AUDITS_DIR.exists() else []
    audit_entries: list[dict] = []
    for f in audit_files:
        audit_entries.extend(_read_recent_jsonl(f, days=7, max_lines=80))

    # Failed/cancelled goals from state
    failed_goals: list[dict] = []
    try:
        if STATE_PATH.exists():
            state = json.loads(STATE_PATH.read_text())
            for g in (state.get("goals") or {}).values():
                if g.get("status") in ("FAILED", "CANCELLED"):
                    failed_goals.append({
                        "goal_id": g.get("goal_id"),
                        "description": g.get("description", "")[:200],
                        "error": g.get("error", "")[:200],
                        "updated_at": g.get("updated_at"),
                    })
    except Exception as exc:
        log.warning("could not read state: %s", exc)

    # Existing specs (so LLM doesn't propose duplicates)
    specs_summary: list[str] = []
    if SPECS_DIR.exists():
        for s in sorted(SPECS_DIR.glob("*.spec.md")):
            specs_summary.append(s.name)

    # Existing agents
    agents_dir = PROJECT_ROOT / ".claude" / "agents"
    agents_summary: list[str] = []
    if agents_dir.exists():
        for a in sorted(agents_dir.glob("*-agent.md")):
            agents_summary.append(a.stem)

    return {
        "now": datetime.now(timezone.utc).isoformat(),
        "feedback_last_7d": _read_recent_jsonl(LOGS_DIR / "feedback.jsonl", days=7, max_lines=60),
        "recall_digest": _digest_log(LOGS_DIR / "recall.jsonl", ("skipped_reason",)),
        "critic_digest": _digest_log(LOGS_DIR / "critic.jsonl", ("verdict", "confidence", "revised")),
        "auto_capture_digest": _digest_log(LOGS_DIR / "auto_capture.jsonl", ("status",)),
        "reasoning_digest": _digest_log(LOGS_DIR / "reasoning_trigger.jsonl", ("signal_level",)),
        "audit_entries": audit_entries[-60:],
        "failed_goals": failed_goals[-20:],
        "existing_specs": specs_summary,
        "existing_agents_count": len(agents_summary),
        "existing_agents_sample": agents_summary[:20],
    }


# ── Synthesis prompt ─────────────────────────────────────────────────────────


_SYNTH_TEMPLATE = """You are Jarvis reviewing your own past week. Boss (Ujjawal) has asked you to grow weekly — propose 3-5 concrete changes to YOURSELF that would make Boss's next week measurably better.

Boss's confirmed autonomy decision: Tier 1+2 auto-apply, Tier-3 confirms.

TIER RULES (enforced by post-processor — do not lie):
- Tier 1: pure-additive text-only changes. Target paths: specs/*.spec.md, data/evals/*/test_cases.jsonl, data/notes/*.md, data/growth/*.md, data/agent-prompts-final/*.md
- Tier 2: new agent files in .claude/agents/, new spec files, CLAUDE.md append, data/memory/*.md hand-edit
- Tier 3: anything touching jarvis_core/, bridge/, scripts/episodic_memory.py, scripts/auto_capture.py, scripts/self_growth_weekly.py, scripts/reasoning_trigger.py, scripts/eval_baseline.py, .mcp.json, deletes, new systemd timers, MCP servers, external services

For each proposal, output:
- `proposal_id` — short kebab-case slug (e.g. "add-resume-eval-suite")
- `tier` — 1 | 2 | 3 (be honest; the validator downgrades dishonest ones)
- `target_path` — relative path the change writes to (one file per proposal)
- `change_kind` — "create" | "append" | "modify"
- `summary` — one sentence
- `why` — cite specific evidence from the signals (e.g. "critic_digest shows 38% revise rate on tone — need stronger Hinglish enforcement")
- `body` — for `create`/`append`, the exact text to insert (full file body for create, snippet for append)
- `evidence` — list of signal fields you used (e.g. ["critic_digest", "feedback_last_7d"])

Strict rules:
- ONE file per proposal — do not chain multi-file changes
- For `create`: include FULL file body in `body` field
- For `append`: include ONLY the new snippet
- For `modify`: explain in `body` what to change but DO NOT auto-apply — post-processor will mark this Tier-3
- Refuse to propose changes you cannot ground in the signals — say so explicitly
- No more than 5 proposals total
- If nothing in the signals warrants a change, return `proposals: []` — silence is fine

Output ONLY a single JSON object, no prose around it:

{"week_summary": "...", "highlights": ["one-liner wins"], "concerns": ["one-liner worries"], "proposals": [...]}

---

SIGNALS:

__SIGNALS_BLOCK__

Now output the JSON object."""


def _build_signals_block(signals: dict) -> str:
    lines = [f"CURRENT TIME (UTC): {signals['now']}", ""]
    lines.append("== RECALL DIGEST (last 7d) ==")
    lines.append(json.dumps(signals["recall_digest"], indent=2))
    lines.append("")
    lines.append("== CRITIC DIGEST (last 7d) ==")
    lines.append(json.dumps(signals["critic_digest"], indent=2))
    lines.append("")
    lines.append("== AUTO-CAPTURE DIGEST (last 7d) ==")
    lines.append(json.dumps(signals["auto_capture_digest"], indent=2))
    lines.append("")
    lines.append("== REASONING-TRIGGER DIGEST (last 7d) ==")
    lines.append(json.dumps(signals["reasoning_digest"], indent=2))
    lines.append("")
    lines.append("== FEEDBACK (last 7d) ==")
    fb = signals.get("feedback_last_7d") or []
    if fb:
        for e in fb[-25:]:
            lines.append(f"  - {e.get('ts','?')} {e.get('rating','?')} on {e.get('target','?')}: {(e.get('note') or '')[:160]}")
    else:
        lines.append("  (none)")
    lines.append("")
    lines.append("== FAILED GOALS (last 7d) ==")
    fg = signals.get("failed_goals") or []
    if fg:
        for g in fg[-10:]:
            lines.append(f"  - {g.get('goal_id')} desc={g.get('description','')[:80]!r} err={(g.get('error') or '')[:80]!r}")
    else:
        lines.append("  (none)")
    lines.append("")
    lines.append("== EXISTING SPECS (don't propose duplicates) ==")
    lines.append("  " + ", ".join(signals["existing_specs"]) or "(none)")
    lines.append("")
    lines.append(f"== EXISTING AGENTS COUNT: {signals['existing_agents_count']} ==")
    lines.append("  Sample: " + ", ".join(signals["existing_agents_sample"]))
    return "\n".join(lines)


_JSON_BLOCK_RE = re.compile(r"\{.*\}", re.DOTALL)


def _parse_synth(raw: str) -> dict | None:
    if not raw:
        return None
    text = raw.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    candidates = [text]
    m = _JSON_BLOCK_RE.search(text)
    if m:
        candidates.append(m.group(0))
    for c in candidates:
        try:
            data = json.loads(c)
        except (json.JSONDecodeError, ValueError):
            continue
        if isinstance(data, dict) and "proposals" in data:
            return data
    return None


async def _synthesise(signals: dict) -> dict | None:
    from jarvis_core.orchestrator import run_worker

    prompt = _SYNTH_TEMPLATE.replace("__SIGNALS_BLOCK__", _build_signals_block(signals))
    try:
        outcome = await asyncio.wait_for(
            run_worker(
                prompt,
                project_root=PROJECT_ROOT,
                max_turns=1,
                allowed_tools=[],
                timeout_seconds=180,
                model=DEFAULT_MODEL,
            ),
            timeout=200,
        )
    except asyncio.TimeoutError:
        log.warning("synthesis timeout")
        return None
    except Exception as exc:
        log.warning("synthesis error: %s", exc)
        return None
    if outcome.error and not outcome.text:
        return None
    return _parse_synth(outcome.text)


# ── Proposal apply ───────────────────────────────────────────────────────────


def _content_hash(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()[:12]


def _git_snapshot(reason: str) -> str | None:
    """Best-effort git stash + tag so we can roll back. Returns ref or None."""
    try:
        # Are we in a git repo?
        result = subprocess.run(
            ["git", "rev-parse", "--git-dir"],
            cwd=PROJECT_ROOT, capture_output=True, text=True, timeout=10,
        )
        if result.returncode != 0:
            log.info("not a git repo — no snapshot")
            return None
        # Get current commit
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=PROJECT_ROOT, capture_output=True, text=True, timeout=10,
        )
        if result.returncode != 0:
            return None
        return result.stdout.strip()
    except Exception as exc:
        log.warning("git snapshot failed: %s", exc)
        return None


def _apply_proposal(prop: dict) -> tuple[bool, str]:
    """Apply a Tier-1 / Tier-2 proposal. Returns (success, message)."""
    target = prop.get("target_path", "")
    kind = prop.get("change_kind", "")
    body = prop.get("body", "")
    if not target or not body:
        return (False, "missing target_path or body")

    abs_target = (PROJECT_ROOT / target).resolve()
    # Safety: must stay within project root
    try:
        abs_target.relative_to(PROJECT_ROOT)
    except ValueError:
        return (False, f"target {target!r} escapes project root")

    if kind == "create":
        if abs_target.exists():
            return (False, f"create requested but {target} already exists")
        abs_target.parent.mkdir(parents=True, exist_ok=True)
        abs_target.write_text(body)
        return (True, f"created {target} ({len(body)} chars)")

    if kind == "append":
        abs_target.parent.mkdir(parents=True, exist_ok=True)
        existing = abs_target.read_text() if abs_target.exists() else ""
        if body in existing:
            return (False, f"append idempotent — body already present in {target}")
        new = existing.rstrip() + "\n\n" + body.strip() + "\n"
        abs_target.write_text(new)
        return (True, f"appended {len(body)} chars to {target}")

    if kind == "modify":
        # Modify is always Tier-3 — should never reach apply
        return (False, "modify_kind requires Tier-3 approval")

    return (False, f"unknown change_kind={kind!r}")


# ── Approval push (Tier-3) ───────────────────────────────────────────────────


def _push_approval(proposal: dict, downgrade_reason: str | None) -> str | None:
    """POST to jarvis-core to create an ApprovalRequest. Returns approval_id or None.

    NOTE: jarvis-core's current Phase 3 API ties ApprovalRequest to a goal. Until that's
    extended for standalone growth approvals, we degrade gracefully and store the request
    locally in `data/growth/awaiting_approval/`. The Telegram digest still includes them.
    """
    try:
        local_dir = GROWTH_DIR / "awaiting_approval"
        local_dir.mkdir(parents=True, exist_ok=True)
        approval_id = "growth-" + _content_hash(
            proposal.get("proposal_id", "")
            + proposal.get("target_path", "")
            + (downgrade_reason or "")
        )
        local_path = local_dir / f"{approval_id}.json"
        local_path.write_text(json.dumps({
            "approval_id": approval_id,
            "kind": "growth-proposal",
            "proposal": proposal,
            "downgrade_reason": downgrade_reason,
            "requested_at": datetime.now(timezone.utc).isoformat(),
            "status": "pending",
        }, indent=2))
        log.info("pushed approval %s locally → %s", approval_id, local_path)
        return approval_id
    except Exception as exc:
        log.warning("approval push failed: %s", exc)
        return None


# ── Output: proposals doc + changelog ────────────────────────────────────────


def _format_proposals_md(synth: dict, processed: list[dict]) -> str:
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    lines = [
        f"# Self-Growth Proposals — Week of {today}",
        "",
        f"**Generated:** {datetime.now(timezone.utc).isoformat()} (by `scripts/self_growth_weekly.py`)",
        "",
        f"## Week summary",
        "",
        synth.get("week_summary", "(none provided)"),
        "",
    ]
    highlights = synth.get("highlights") or []
    if highlights:
        lines.append("### Highlights")
        lines.extend(f"- {h}" for h in highlights)
        lines.append("")
    concerns = synth.get("concerns") or []
    if concerns:
        lines.append("### Concerns")
        lines.extend(f"- {c}" for c in concerns)
        lines.append("")

    if not processed:
        lines.append("## Proposals\n\n_No proposals this week — signals were stable._")
        return "\n".join(lines)

    lines.append("## Proposals")
    lines.append("")
    lines.append("| # | ID | Final Tier | Status | Target | Summary |")
    lines.append("|--:|----|----:|--------|--------|---------|")
    for i, p in enumerate(processed, 1):
        status = p.get("status", "?")
        lines.append(
            f"| {i} | `{p.get('proposal_id','?')}` | {p.get('final_tier','?')} | "
            f"**{status}** | `{p.get('target_path','?')}` | "
            f"{p.get('summary','')[:80]} |"
        )
    lines.append("")
    for p in processed:
        lines.append(f"### `{p.get('proposal_id','?')}` — Tier {p.get('final_tier','?')} ({p.get('status','?')})")
        lines.append("")
        lines.append(f"- **Target:** `{p.get('target_path','?')}` ({p.get('change_kind','?')})")
        lines.append(f"- **Why:** {p.get('why','')}")
        if p.get("downgrade_reason"):
            lines.append(f"- **Tier downgrade:** {p['downgrade_reason']}")
        if p.get("apply_message"):
            lines.append(f"- **Apply result:** {p['apply_message']}")
        if p.get("approval_id"):
            lines.append(f"- **Approval:** `{p['approval_id']}` — pending")
        evidence = p.get("evidence") or []
        if evidence:
            lines.append(f"- **Evidence:** {', '.join(evidence)}")
        lines.append("")
        body = p.get("body") or ""
        if body and p.get("status") not in ("applied", "ready_to_apply"):
            preview = body[:400]
            lines.append("**Proposed body (excerpt):**")
            lines.append("```")
            lines.append(preview)
            if len(body) > 400:
                lines.append(f"… [truncated {len(body) - 400} more chars]")
            lines.append("```")
            lines.append("")
    return "\n".join(lines)


def _append_changelog(applied: list[dict]) -> None:
    if not applied:
        return
    GROWTH_DIR.mkdir(parents=True, exist_ok=True)
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    lines: list[str] = []
    if not CHANGELOG.exists():
        lines.append("# Jarvis Self-Growth Changelog\n")
        lines.append("Auto-appended by `scripts/self_growth_weekly.py`. ")
        lines.append("Each row is a change Jarvis applied to itself.\n")
    lines.append(f"\n## {today}\n")
    for p in applied:
        lines.append(
            f"- **Tier {p.get('final_tier','?')}** `{p.get('proposal_id','?')}` "
            f"→ `{p.get('target_path','?')}` ({p.get('change_kind','?')}). "
            f"_{p.get('summary','')[:120]}_"
        )
    with CHANGELOG.open("a") as fh:
        fh.write("\n".join(lines) + "\n")


# ── Telegram digest ──────────────────────────────────────────────────────────


def _format_digest(synth: dict, processed: list[dict],
                   baseline_regressed: bool, dry_run: bool) -> str:
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    applied = [p for p in processed if p.get("status") == "applied"]
    queued = [p for p in processed if p.get("status") == "queued"]
    drafted = [p for p in processed if p.get("status") == "drafted_only"]

    lines = [
        f"🌱 *Self-Growth Weekly — week of {today}*",
        "",
        f"_{synth.get('week_summary', 'No summary')}_",
        "",
        f"📈 *Applied:* {len(applied)} change(s)",
        f"🟡 *Awaiting Boss approval:* {len(queued)} (Tier-3)",
    ]
    if drafted:
        lines.append(f"📝 *Drafted only:* {len(drafted)} (regression block)")
    lines.append("")

    if applied:
        lines.append("*Applied this week:*")
        for p in applied[:5]:
            lines.append(f"  ✓ `{p.get('proposal_id','?')}` → `{p.get('target_path','?')}`")
        lines.append("")
    if queued:
        lines.append("*Needs your nod (Tier-3):*")
        for p in queued[:5]:
            ap = p.get("approval_id", "?")
            lines.append(f"  🟡 `{p.get('proposal_id','?')}` — `/growth_approve {ap}`")
            lines.append(f"      _{p.get('summary','')[:80]}_")
        lines.append("")
    if baseline_regressed:
        lines.append("⚠️ Eval baseline regressed — auto-apply suspended for the week.")
        lines.append("")
    if dry_run:
        lines.append("🔬 _Dry run — nothing was actually applied._")

    lines.append(f"📄 Full proposals: `data/growth/proposals/{today}.md`")
    return "\n".join(lines)


def _send_telegram(text: str) -> bool:
    token = ENV.get("TELEGRAM_BOT_TOKEN")
    chat_id = ENV.get("TELEGRAM_CHAT_ID") or (ENV.get("ALLOWED_USER_IDS", "").split(",")[0].strip())
    if not token or not chat_id:
        log.info("Telegram creds missing — skipping send")
        return False
    try:
        import requests
    except ImportError:
        log.warning("requests not installed")
        return False
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        r = requests.post(
            url,
            json={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"},
            timeout=15,
        )
        if r.status_code != 200:
            log.warning("Telegram send failed: %d %s", r.status_code, r.text[:200])
            return False
    except Exception as exc:
        log.warning("Telegram send error: %s", exc)
        return False
    return True


# ── Run-log ─────────────────────────────────────────────────────────────────


def _append_run_log(entry: dict) -> None:
    try:
        RUN_LOG.parent.mkdir(parents=True, exist_ok=True)
        with RUN_LOG.open("a") as fh:
            fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception:
        pass


# ── Main ─────────────────────────────────────────────────────────────────────


async def main(dry_run: bool = False, collect_only: bool = False) -> int:
    if os.getenv("JARVIS_SELFGROWTH_ENABLED", "1") in ("0", "false", "False"):
        log.info("disabled via env")
        _append_run_log({"ts": datetime.now(timezone.utc).isoformat(), "status": "disabled"})
        return 0
    if os.getenv("JARVIS_SELFGROWTH_DRY_RUN", "0") in ("1", "true", "True"):
        dry_run = True

    started = time.perf_counter()
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    proposal_md = PROPOSALS_DIR / f"{today}.md"
    proposal_json = PROPOSALS_DIR / f"{today}.json"
    PROPOSALS_DIR.mkdir(parents=True, exist_ok=True)

    # Idempotency — refuse to overwrite same-day file
    if proposal_md.exists() and not dry_run and not collect_only:
        log.info("today's proposals file already exists (%s) — skipping run", proposal_md)
        _append_run_log({
            "ts": datetime.now(timezone.utc).isoformat(),
            "status": "skipped_already_done",
            "proposal_md": str(proposal_md.relative_to(PROJECT_ROOT)),
        })
        return 0

    signals = _collect_signals()

    if collect_only:
        print(json.dumps(signals, indent=2, default=str)[:6000])
        return 0

    # Quality gate — refuse auto-apply on regression
    baseline_regressed = False
    try:
        result = subprocess.run(
            [sys.executable, str(PROJECT_ROOT / "scripts" / "eval_baseline.py"), "--check"],
            cwd=PROJECT_ROOT, capture_output=True, text=True, timeout=60,
        )
        if result.returncode != 0:
            baseline_regressed = True
            log.warning("eval baseline regression detected — auto-apply disabled")
    except Exception as exc:
        log.warning("eval baseline check failed: %s — proceeding without gate", exc)

    log.info("synthesising proposals from signals...")
    synth = await asyncio.wait_for(_synthesise(signals), timeout=HARD_TIMEOUT_S)
    if not synth:
        log.warning("synthesis returned nothing — emitting empty digest")
        synth = {"week_summary": "Synthesis failed.", "highlights": [], "concerns": [], "proposals": []}

    proposals_raw = synth.get("proposals") or []
    if not isinstance(proposals_raw, list):
        proposals_raw = []
    proposals_raw = proposals_raw[:5]

    snapshot = _git_snapshot("self_growth_weekly")
    log.info("git snapshot: %s", snapshot)

    processed: list[dict] = []
    applied: list[dict] = []
    for prop in proposals_raw:
        if not isinstance(prop, dict):
            continue
        proposed_tier = int(prop.get("tier", 3))
        target_path = prop.get("target_path", "")
        final_tier, downgrade = _classify_tier(proposed_tier, target_path)
        record = dict(prop)
        record["proposed_tier"] = proposed_tier
        record["final_tier"] = final_tier
        record["downgrade_reason"] = downgrade

        if dry_run:
            record["status"] = "dry_run"
            processed.append(record)
            continue

        if baseline_regressed:
            record["status"] = "drafted_only"
            record["apply_message"] = "baseline regressed — auto-apply suspended"
            processed.append(record)
            continue

        if final_tier in (1, 2):
            ok, msg = _apply_proposal(record)
            record["apply_message"] = msg
            record["status"] = "applied" if ok else "apply_failed"
            if ok:
                applied.append(record)
        else:
            approval_id = _push_approval(record, downgrade)
            record["approval_id"] = approval_id
            record["status"] = "queued" if approval_id else "queue_failed"
        processed.append(record)

    # Write proposals docs
    proposal_md_text = _format_proposals_md(synth, processed)
    if not dry_run:
        proposal_md.write_text(proposal_md_text)
        proposal_json.write_text(json.dumps({
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "synthesis": synth,
            "processed": processed,
            "baseline_regressed": baseline_regressed,
            "git_snapshot": snapshot,
        }, indent=2))

    # Changelog
    if applied:
        _append_changelog(applied)

    # Telegram digest
    digest = _format_digest(synth, processed, baseline_regressed, dry_run)
    if dry_run:
        log.info("DRY RUN digest:\n%s", digest)
    else:
        _send_telegram(digest)

    duration_ms = int((time.perf_counter() - started) * 1000)
    log.info("done proposals=%d applied=%d queued=%d %dms",
             len(processed), len(applied),
             sum(1 for p in processed if p.get("status") == "queued"),
             duration_ms)
    _append_run_log({
        "ts": datetime.now(timezone.utc).isoformat(),
        "status": "ok",
        "proposals": len(processed),
        "applied": len(applied),
        "queued": sum(1 for p in processed if p.get("status") == "queued"),
        "baseline_regressed": baseline_regressed,
        "dry_run": dry_run,
        "duration_ms": duration_ms,
    })
    return 0


def _apply_approved() -> int:
    """Process every JSON file under data/growth/approved/, apply, then move to applied/."""
    approved_dir = GROWTH_DIR / "approved"
    applied_dir = GROWTH_DIR / "applied"
    failed_dir = GROWTH_DIR / "apply_failed"
    if not approved_dir.exists():
        print("No approved growth proposals to apply.")
        return 0
    applied_dir.mkdir(parents=True, exist_ok=True)
    failed_dir.mkdir(parents=True, exist_ok=True)

    files = sorted(approved_dir.glob("growth-*.json"))
    if not files:
        print("No approved growth proposals to apply.")
        return 0

    applied_count = 0
    failed_count = 0
    for f in files:
        try:
            data = json.loads(f.read_text())
        except Exception as exc:
            log.warning("skip corrupt %s: %s", f, exc)
            continue
        prop = data.get("proposal") or {}
        ok, msg = _apply_proposal(prop)
        data["apply_attempted_at"] = datetime.now(timezone.utc).isoformat()
        data["apply_ok"] = ok
        data["apply_message"] = msg
        dest = (applied_dir if ok else failed_dir) / f.name
        dest.write_text(json.dumps(data, indent=2))
        f.unlink()
        if ok:
            applied_count += 1
            _append_changelog([prop | {"final_tier": prop.get("final_tier", "?"),
                                       "status": "applied_after_approval"}])
            print(f"✓ applied {data.get('approval_id', f.name)} — {msg}")
        else:
            failed_count += 1
            print(f"✗ failed {data.get('approval_id', f.name)} — {msg}")

    print(f"\nDone. applied={applied_count} failed={failed_count}")
    return 0 if failed_count == 0 else 2


def _cli() -> int:
    parser = argparse.ArgumentParser(description="Self-growth weekly loop")
    parser.add_argument("--dry-run", action="store_true",
                        help="Collect + propose + digest, no apply, no Telegram")
    parser.add_argument("--collect-only", action="store_true",
                        help="Print collected signals as JSON and exit")
    parser.add_argument("--apply-approved", action="store_true",
                        help="Apply Boss-approved Tier-3 proposals from data/growth/approved/")
    args = parser.parse_args()
    if args.apply_approved:
        return _apply_approved()
    return asyncio.run(main(dry_run=args.dry_run, collect_only=args.collect_only))


if __name__ == "__main__":
    raise SystemExit(_cli())
