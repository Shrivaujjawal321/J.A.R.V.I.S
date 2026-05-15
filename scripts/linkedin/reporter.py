"""
Nightly LinkedIn report — sent to Boss via Telegram at 9pm IST.

Reads:
  data/linkedin/contacted.jsonl  - today's outbound activity
  data/linkedin/state.json       - rolling counters
  data/linkedin/posts/<date>_*.json - what got posted today
  data/audits/<date>.jsonl       - executor audit log

Sends:
  - Today's totals (connections sent, messages sent, post live URL)
  - Week-to-date cumulative
  - Approval pipeline backlog (anything pending Boss's nod)
  - Warnings: throttle state, low InMail credits, unused approved items
"""
from __future__ import annotations

import json
from collections import Counter
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from . import _telegram_notify, telegram_approval

JARVIS_ROOT = Path(__file__).resolve().parents[2]
CONTACTED_LOG = JARVIS_ROOT / "data" / "linkedin" / "contacted.jsonl"
STATE_PATH = JARVIS_ROOT / "data" / "linkedin" / "state.json"
POSTS_DIR = JARVIS_ROOT / "data" / "linkedin" / "posts"
INMAIL_PATH = JARVIS_ROOT / "data" / "linkedin" / "inmail_budget.json"
IST = ZoneInfo("Asia/Kolkata")


def _today_events() -> list[dict]:
    if not CONTACTED_LOG.exists():
        return []
    today = datetime.now(IST).strftime("%Y-%m-%d")
    out = []
    for line in CONTACTED_LOG.read_text().splitlines():
        if not line.strip():
            continue
        try:
            ev = json.loads(line)
        except json.JSONDecodeError:
            continue
        if (ev.get("ts") or "").startswith(today):
            out.append(ev)
    return out


def _today_post_url() -> str | None:
    today = datetime.now(IST).strftime("%Y-%m-%d")
    for p in POSTS_DIR.glob(f"{today}_*.json"):
        data = json.loads(p.read_text())
        if data.get("post_url"):
            return data["post_url"]
    return None


def build_report() -> str:
    today = datetime.now(IST).strftime("%Y-%m-%d (%A)")
    events = _today_events()
    counts = Counter(ev.get("action") for ev in events)
    state = json.loads(STATE_PATH.read_text()) if STATE_PATH.exists() else {}
    inmail = json.loads(INMAIL_PATH.read_text()) if INMAIL_PATH.exists() else {}
    post_url = _today_post_url()

    rolling7 = state.get("rolling_7d", {})
    rolling30 = state.get("rolling_30d", {})

    parts = [
        f"🌙 *LinkedIn nightly report — {today}*",
        "",
        "*Today*",
        f"  👁️ Follows sent: *{counts.get('follow_profile', 0)}*",
        f"  📤 Connections sent: *{counts.get('send_connection', 0)}*",
        f"  💬 Messages sent: *{counts.get('send_message', 0)}*",
        f"  ✉️ InMails sent: *{counts.get('send_inmail', 0)}*",
        f"  📝 Post: {'✅ live — ' + post_url if post_url else '❌ not posted'}",
        "",
        "*Rolling 7d*",
        f"  Follows: {rolling7.get('follows_sent', 0)} · Connections: {rolling7.get('connections_sent', 0)} · Messages: {rolling7.get('messages_sent', 0)} · Posts: {rolling7.get('posts_published', 0)}",
        "",
        "*Rolling 30d*",
        f"  Connections: {rolling30.get('connections_sent', 0)} (accept rate: {rolling30.get('acceptance_rate', 0.0):.0%})",
        f"  Messages: {rolling30.get('messages_sent', 0)} (reply rate: {rolling30.get('reply_rate', 0.0):.0%})",
        f"  Posts: {rolling30.get('posts_published', 0)} · Followers gained: {rolling30.get('new_followers', 0)}",
        "",
        f"*InMail credits this month:* {inmail.get('current_period', {}).get('credits_remaining', '?')}/5",
        "",
        telegram_approval.status(),
    ]

    throttle = state.get("throttle_state", {})
    if throttle.get("current_pace_modifier", 1.0) < 1.0:
        parts.append("")
        parts.append(f"⚠️ *Throttle active* — pace = {throttle['current_pace_modifier']}x. Last warning: {throttle.get('last_warning_received')}")

    return "\n".join(parts)


def send_report() -> None:
    _telegram_notify.send(build_report())


if __name__ == "__main__":
    send_report()
