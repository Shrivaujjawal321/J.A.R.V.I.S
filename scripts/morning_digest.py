#!/usr/bin/env python3
"""
Morning digest — summarize overnight Jarvis autonomous activity.

Runs at 06:30 IST (via systemd timer). Fetches /digest from jarvis-core daemon,
formats as Telegram-ready markdown, sends to Boss.

Output sections:
- Goals completed (with final output preview + cost)
- Awaiting approval (Tier-3 actions queued for morning nod)
- Failed / cancelled (with reason)
- Active / still running (long goals spanning multiple days)
- Cost summary

Run manually for testing:
    .venv/bin/python scripts/morning_digest.py [--hours 24] [--telegram | --stdout]
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import httpx
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

JARVIS_CORE_URL = os.getenv("JARVIS_CORE_URL", "http://127.0.0.1:8765")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
BOSS_TELEGRAM_ID = os.getenv("BOSS_TELEGRAM_ID") or (
    os.getenv("ALLOWED_USER_IDS", "").split(",")[0] if os.getenv("ALLOWED_USER_IDS") else None
)


def fetch_digest(hours: int = 24) -> dict:
    """GET /digest from jarvis-core daemon."""
    response = httpx.get(f"{JARVIS_CORE_URL}/digest", params={"hours": hours}, timeout=15)
    response.raise_for_status()
    return response.json()


def render_markdown(digest: dict) -> str:
    """Format the digest as Telegram markdown."""
    out: list[str] = []
    out.append("🌅 *Morning Digest — Overnight Jarvis*")
    out.append(f"_window: last {digest.get('window_hours', 24)}h | as-of: {digest.get('as_of', '?')}_")
    out.append("")

    totals = digest.get("totals", {})
    goals_n = totals.get("goals_in_window", 0)
    cost = totals.get("cost_usd", 0)
    out.append(f"📊 {goals_n} goals touched · ${cost:.3f} spent")
    out.append("")

    by_status = digest.get("by_status", {})

    completed = by_status.get("completed", [])
    if completed:
        out.append(f"✅ *Completed ({len(completed)})*")
        for g in completed[:10]:
            preview = (g.get("plan_summary") or g.get("description", ""))[:120]
            out.append(f"• `{g['goal_id']}` · ${g.get('cost_usd', 0):.3f} · {preview}")
        out.append("")

    pending = digest.get("pending_approvals", [])
    if pending:
        out.append(f"🔐 *Awaiting Boss approval ({len(pending)})*")
        for a in pending[:10]:
            risks = " · ".join(a.get("risk_notes") or [])
            out.append(f"• `{a['approval_id']}` → {a['action_summary']}")
            if risks:
                out.append(f"   _risk: {risks}_")
        out.append("")
        out.append("_Reply `/goal_approve <id>` to approve, or `/goal_reject <id>`._")
        out.append("")

    awaiting = by_status.get("awaiting_approval", [])
    if awaiting and not pending:
        out.append(f"⏳ *Goals paused for approval ({len(awaiting)})*")
        for g in awaiting[:5]:
            out.append(f"• `{g['goal_id']}` · {g.get('description', '')[:100]}")
        out.append("")

    failed = by_status.get("failed", [])
    if failed:
        out.append(f"⚠️ *Failed ({len(failed)})*")
        for g in failed[:5]:
            err = (g.get("error") or "unknown")[:120]
            out.append(f"• `{g['goal_id']}` · {err}")
        out.append("")

    running = by_status.get("running", []) + by_status.get("planning", []) + by_status.get("queued", [])
    if running:
        out.append(f"🏃 *Still active ({len(running)})*")
        for g in running[:5]:
            out.append(f"• `{g['goal_id']}` · {g.get('description', '')[:100]}")
        out.append("")

    if not (completed or pending or failed or running or awaiting):
        out.append("_(no autonomous activity in window — Jarvis slept too 😴)_")
        out.append("")

    out.append("---")
    out.append("_Endpoints: `/goals` list · `/goal <id>` detail · `/approvals/pending` queue_")

    return "\n".join(out)


def send_to_telegram(text: str, chat_id: str | None = None, token: str | None = None) -> bool:
    """Send markdown text to Boss's Telegram. Returns True on success."""
    token = token or TELEGRAM_BOT_TOKEN
    chat_id = chat_id or BOSS_TELEGRAM_ID
    if not token or not chat_id:
        print("WARN: TELEGRAM_BOT_TOKEN or BOSS_TELEGRAM_ID missing — printing instead")
        print(text)
        return False
    try:
        r = httpx.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"},
            timeout=10,
        )
        r.raise_for_status()
        return True
    except Exception as e:
        print(f"ERROR sending to Telegram: {e}", file=sys.stderr)
        return False


def main() -> int:
    p = argparse.ArgumentParser(description="Morning digest of overnight Jarvis activity")
    p.add_argument("--hours", type=int, default=24, help="Look-back window in hours")
    p.add_argument("--telegram", action="store_true", help="Send to Telegram (default if invoked from cron)")
    p.add_argument("--stdout", action="store_true", help="Print to stdout instead")
    args = p.parse_args()

    try:
        digest = fetch_digest(args.hours)
    except Exception as e:
        print(f"ERROR fetching digest: {e}", file=sys.stderr)
        return 1

    text = render_markdown(digest)

    # Always also write to disk for archive
    archive_dir = ROOT / "data" / "digests"
    archive_dir.mkdir(parents=True, exist_ok=True)
    from datetime import datetime
    archive_path = archive_dir / f"{datetime.now().strftime('%Y-%m-%d')}.md"
    archive_path.write_text(text + "\n")

    if args.stdout or (not args.telegram and not TELEGRAM_BOT_TOKEN):
        print(text)
    else:
        ok = send_to_telegram(text)
        if not ok:
            print(text)  # fallback to stdout
            return 2

    # Also save JSON form for downstream processing
    json_path = archive_dir / f"{datetime.now().strftime('%Y-%m-%d')}.json"
    json_path.write_text(json.dumps(digest, indent=2, default=str))

    return 0


if __name__ == "__main__":
    sys.exit(main())
