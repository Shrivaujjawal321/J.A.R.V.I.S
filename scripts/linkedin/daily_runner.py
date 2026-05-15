"""
Top-level orchestrator for the LinkedIn daily growth pipeline.

Schedule (cron-driven, see scripts/linkedin/systemd/):
  08:00 IST  → daily_runner.py morning   (search, draft, send Telegram batch)
  10:00 IST  → daily_runner.py execute   (run executor on approved items)
  18:00 IST  → daily_runner.py afternoon (lighter mini-batch — 5 conns + 10 msgs)
  21:00 IST  → reporter.py               (nightly Telegram report)

Sub-commands:
  morning    — full morning batch flow
  execute    — execute today's approved batch
  afternoon  — smaller batch run
  status     — print today's state
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from . import (
    _telegram_notify,
    connection_drafter,
    executor,
    icp_search,
    intro_messager,
    message_drafter,
    post_generator,
    preflight,
    telegram_approval,
)

JARVIS_ROOT = Path(__file__).resolve().parents[2]
ICP_PATH = JARVIS_ROOT / "data" / "linkedin" / "icp.json"
STATE_PATH = JARVIS_ROOT / "data" / "linkedin" / "state.json"
IST = ZoneInfo("Asia/Kolkata")


def _load_targets() -> dict:
    icp = json.loads(ICP_PATH.read_text())
    return icp["daily_targets"]


def cmd_morning(args) -> None:
    """Full morning batch: search ICP for follows + connections, draft post, send to Telegram."""
    pf = preflight.run_preflight()
    if not pf.ok:
        print(f"[morning] Preflight failed — aborting. {pf.note}", file=sys.stderr)
        sys.exit(1)
    print(f"[morning] Preflight ok. {pf.note}")

    targets = _load_targets()
    if getattr(args, "small", False):
        n_follow = 3
        n_conn = 2
        n_msg = 2
    else:
        n_follow = targets.get("follows", 50)
        n_conn = targets["connection_requests"]
        n_msg = targets.get("intro_dms", 10)

    flavor = " (DRY-RUN small)" if getattr(args, "small", False) else ""
    _telegram_notify.safe_send(
        f"LinkedIn morning batch starting{flavor} — searching ICP "
        f"for {n_follow} follows + {n_conn} connections + {n_msg} Jarvis-intro DMs...",
        parse_mode=None,
    )

    # 1. Find ICP profiles to follow (broader pool, no notes needed)
    try:
        follow_profiles = icp_search.search_all_categories(daily_target=n_follow)
    except Exception as e:
        _telegram_notify.safe_send(f"⚠️ Follow search failed: {e}. Skipping follows.")
        follow_profiles = []
    follows = [
        {
            "profile_id": p["id"],
            "name": p.get("name"),
            "headline": p.get("headline"),
            "category_id": p.get("category_id"),
            "url": p.get("url"),
        }
        for p in follow_profiles
    ]

    # 2. Find ICP profiles for connection requests (smaller, higher-priority pool)
    try:
        conn_profiles = icp_search.search_all_categories(daily_target=n_conn)
    except Exception as e:
        _telegram_notify.safe_send(f"⚠️ Connection search failed: {e}. Skipping connections.")
        conn_profiles = []
    conn_drafts = connection_drafter.draft_batch(conn_profiles) if conn_profiles else []

    # 3. Draft Jarvis-intro DMs to 1st-degree recruiters/founders
    try:
        msg_drafts = intro_messager.draft_intros(n=n_msg)
    except Exception as e:
        _telegram_notify.safe_send(f"⚠️ Intro-DM drafting failed: {e}. Skipping DMs.")
        msg_drafts = []

    # 4. Draft today's post
    try:
        post = post_generator.generate_today()
    except Exception as e:
        _telegram_notify.safe_send(f"⚠️ Post drafting failed: {e}.")
        post = None

    # 5. Send to Telegram for approval (fullauto auto-approves; autopilot waits for /lp_approve_all)
    batch_id = telegram_approval.send_morning_batch(
        follows=follows,
        connections=conn_drafts,
        messages=msg_drafts,
        post=post,
    )
    print(f"Batch sent: {batch_id}")


def cmd_execute(args) -> None:
    """Execute the approved items from today's morning batch."""
    pf = preflight.run_preflight()
    if not pf.ok:
        print(f"[execute] Preflight failed — aborting. {pf.note}", file=sys.stderr)
        sys.exit(1)
    print(f"[execute] Preflight ok. {pf.note}")

    result = executor.execute_today()
    print(json.dumps(result, indent=2, ensure_ascii=False))


def cmd_afternoon(args) -> None:
    """Lighter afternoon batch — 20 follows + 5 conns, no post."""
    pf = preflight.run_preflight()
    if not pf.ok:
        print(f"[afternoon] Preflight failed — aborting. {pf.note}", file=sys.stderr)
        sys.exit(1)
    print(f"[afternoon] Preflight ok. {pf.note}")

    n_follow = 20
    n_conn = 5
    _telegram_notify.safe_send(
        f"LinkedIn afternoon mini-batch — {n_follow} follows + {n_conn} connections",
        parse_mode=None,
    )
    follow_profiles = icp_search.search_all_categories(daily_target=n_follow)
    follows = [
        {"profile_id": p["id"], "name": p.get("name"), "headline": p.get("headline"),
         "category_id": p.get("category_id"), "url": p.get("url")}
        for p in follow_profiles
    ]
    conn_profiles = icp_search.search_all_categories(daily_target=n_conn)
    conn_drafts = connection_drafter.draft_batch(conn_profiles) if conn_profiles else []
    telegram_approval.send_morning_batch(
        follows=follows,
        connections=conn_drafts,
        messages=[],
        post=None,
    )


def cmd_status(args) -> None:
    state = json.loads(STATE_PATH.read_text()) if STATE_PATH.exists() else {}
    print(json.dumps(state, indent=2))
    print()
    print(telegram_approval.status())


def main() -> None:
    parser = argparse.ArgumentParser(prog="linkedin.daily_runner")
    sub = parser.add_subparsers(dest="cmd", required=True)
    morning = sub.add_parser("morning")
    morning.add_argument("--small", action="store_true", help="Dry-run small batch: 3 conns + 3 msgs + 1 post")
    morning.set_defaults(func=cmd_morning)
    sub.add_parser("execute").set_defaults(func=cmd_execute)
    sub.add_parser("afternoon").set_defaults(func=cmd_afternoon)
    sub.add_parser("status").set_defaults(func=cmd_status)
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
