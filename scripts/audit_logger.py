#!/usr/bin/env python3
"""
Jarvis audit logger — appends one JSON line per Tier-2 / Tier-3 action.

Used by:
- browser-autopilot skill (form fills, submits)
- auto-mode slash command (mode switches)
- Any agent that needs to record an autonomous action

Format (one JSON line per action, append-only):
{
  "ts": "2026-05-12T14:32:11Z",
  "tier": 2,
  "action": "file_edit",
  "agent": "code-agent",
  "target": "scripts/foo.py",
  "mode": "autopilot",
  "user_id": "ujjwal",
  "reversible": true,
  "extra": { ... }                // free-form per-action context
}

CLI usage:
  python scripts/audit_logger.py --tier 2 --action file_edit \\
    --agent code-agent --target scripts/foo.py [--extra '{...}']

Python import:
  from audit_logger import log_action
  log_action(tier=2, action="form_fill", agent="browser-autopilot",
             target="https://linkedin.com/jobs/12345", extra={"field_count": 8})
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
AUDIT_DIR = ROOT / "data" / "audits"


def _today_log_path() -> Path:
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    return AUDIT_DIR / f"{datetime.now(timezone.utc).date().isoformat()}.jsonl"


def _read_active_mode() -> str:
    """Read current auto-mode from config; default to 'autopilot' if missing."""
    cfg_path = ROOT / "data" / "config" / "auto-mode.json"
    try:
        return json.loads(cfg_path.read_text()).get("mode", "autopilot")
    except Exception:
        return "autopilot"


def log_action(
    *,
    tier: int,
    action: str,
    agent: str,
    target: str,
    user_id: str = "ujjwal",
    reversible: bool | None = None,
    extra: dict[str, Any] | None = None,
) -> Path:
    """Append one audit entry. Returns the log file path."""
    if tier not in {2, 3}:
        # Tier 1 is not logged (too noisy); Tier 4 actions are refused before reaching here.
        raise ValueError(f"audit log accepts tier 2 or 3, got {tier}")
    if action == "" or agent == "" or target == "":
        raise ValueError("action, agent, and target are required")

    entry: dict[str, Any] = {
        "ts": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "tier": tier,
        "action": action,
        "agent": agent,
        "target": target,
        "user_id": user_id,
        "mode": _read_active_mode(),
    }
    if reversible is not None:
        entry["reversible"] = reversible
    if extra:
        entry["extra"] = extra

    path = _today_log_path()
    with path.open("a") as fp:
        fp.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return path


def tail_log(limit: int = 20) -> list[dict[str, Any]]:
    """Return the last `limit` entries from today's log."""
    path = _today_log_path()
    if not path.exists():
        return []
    lines = path.read_text().splitlines()
    out: list[dict[str, Any]] = []
    for ln in lines[-limit:]:
        try:
            out.append(json.loads(ln))
        except json.JSONDecodeError:
            continue
    return out


def main() -> int:
    p = argparse.ArgumentParser(description="Append a Jarvis audit log entry.")
    p.add_argument("--tier", type=int, required=True, choices=[2, 3])
    p.add_argument("--action", required=True, help="snake_case action name")
    p.add_argument("--agent", required=True, help="agent or skill that performed the action")
    p.add_argument("--target", required=True, help="what was acted on (file path, URL, email, etc.)")
    p.add_argument("--user", default=os.getenv("JARVIS_USER", "ujjwal"))
    p.add_argument("--reversible", choices=["true", "false"], default=None)
    p.add_argument("--extra", default=None, help="JSON object with free-form context")
    p.add_argument("--tail", type=int, default=0, help="Show last N entries instead of writing")
    args = p.parse_args()

    if args.tail:
        for entry in tail_log(limit=args.tail):
            print(json.dumps(entry, ensure_ascii=False))
        return 0

    extra = json.loads(args.extra) if args.extra else None
    rev = {"true": True, "false": False, None: None}[args.reversible]
    path = log_action(
        tier=args.tier,
        action=args.action,
        agent=args.agent,
        target=args.target,
        user_id=args.user,
        reversible=rev,
        extra=extra,
    )
    print(str(path))
    return 0


if __name__ == "__main__":
    sys.exit(main())
