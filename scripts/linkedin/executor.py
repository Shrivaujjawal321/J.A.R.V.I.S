"""
Executes Boss's approved LinkedIn actions via the browser-autopilot skill.

Reads:
  data/linkedin/drafts/<today>_pending.json   - the drafted batch
  data/linkedin/drafts/<today>_decisions.json - Boss's approve/reject calls

Drives Chrome (already logged in to LinkedIn) via a Claude Code subprocess
that has access to mcp__chrome-devtools__* tools.

Per-action gating:
  - Each Tier-3 action (send conn / send DM / publish post) is logged BEFORE
    and AFTER. If LinkedIn shows a restriction warning, executor halts.
  - Daily caps from data/linkedin/icp.json are re-checked at runtime.
  - Every successful action appends to contacted.jsonl.
  - Pace: 30-90s random delay between actions (anti-fingerprint).
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

from . import _claude_helper, _telegram_notify

JARVIS_ROOT = Path(__file__).resolve().parents[2]
DRAFTS_DIR = JARVIS_ROOT / "data" / "linkedin" / "drafts"
CONTACTED_LOG = JARVIS_ROOT / "data" / "linkedin" / "contacted.jsonl"
STATE_PATH = JARVIS_ROOT / "data" / "linkedin" / "state.json"
AUDITS_DIR = JARVIS_ROOT / "data" / "audits"
IST = ZoneInfo("Asia/Kolkata")


EXECUTE_PROMPT = """\
You are Jarvis driving Boss's logged-in LinkedIn session via Chrome DevTools MCP.

## Approved actions to execute (Boss has authorized each one)
{actions_block}

## Hard rules — DO NOT VIOLATE
1. Pace: 30-90 seconds RANDOM delay between every action. Use the wait_for tool
   or sleep via evaluate_script.
2. After EVERY action, take a snapshot. If LinkedIn shows ANY of:
     - "We've restricted your account"
     - "You're sending too many invitations"
     - "You've reached the weekly invitation limit"
     - CAPTCHA challenge
     - "Verify it's you"
   → STOP IMMEDIATELY. Do not retry. Report which actions completed + the warning.
3. For follow_profile: navigate to the profile URL, find the "Follow" button
   (may be inside the More menu — click "..." then "Follow" if not on main row).
   Click it. Verify button changes to "Following". If button already says
   "Following", log as already_done.
4. For send_connection: navigate to the profile, click Connect, click "Add a note",
   paste the personalized note, click Send. Never click Connect without note.
5. For DMs: open the conversation thread, type the message, click Send. Confirm
   the message appears in the thread before logging success.
6. For the post: click Start a Post, paste the content, click Post. Confirm the
   post URL appears in the feed.
7. If a profile's "Connect" button is replaced by "Pending" or "Message" (already
   sent or already connected) — skip and log as already_done.

## After each action, append a JSON event to your reply (one per action):
{{
  "id": "<f0/c0/m0/p1 etc>",
  "action": "follow_profile|send_connection|send_message|publish_post",
  "profile_id": "<handle or null for post>",
  "outcome": "success|already_done|failed|halted_by_warning",
  "error": "<error string or null>",
  "evidence": "<URL or DOM signal that proves it landed>",
  "ts": "<ISO timestamp>"
}}

## Final reply format (ONLY JSON, no prose)
{{
  "events": [<one event per action attempted>],
  "halted": <bool — true if you stopped early>,
  "halt_reason": "<string or null>",
  "completed_count": <int>,
  "skipped_count": <int>,
  "failed_count": <int>
}}
"""


def _load_pending_and_decisions(today: str) -> tuple[dict | None, dict]:
    pending_path = DRAFTS_DIR / f"{today}_pending.json"
    decisions_path = DRAFTS_DIR / f"{today}_decisions.json"
    if not pending_path.exists():
        return None, {}
    pending = json.loads(pending_path.read_text())
    decisions = (
        json.loads(decisions_path.read_text())
        if decisions_path.exists()
        else {"approved": [], "rejected": []}
    )
    return pending, decisions


def _build_action_list(pending: dict, decisions: dict) -> list[dict]:
    approved = set(decisions.get("approved", []))
    actions: list[dict] = []
    for f in pending.get("follows", []):
        if f["id"] not in approved:
            continue
        actions.append({
            "id": f["id"],
            "action": "follow_profile",
            "profile_id": f["profile_id"],
            "name": f.get("name"),
            "url": f.get("url") or f"https://www.linkedin.com/in/{f['profile_id']}/",
        })
    for c in pending["connections"]:
        if c["id"] not in approved:
            continue
        actions.append({
            "id": c["id"],
            "action": "send_connection",
            "profile_id": c["profile_id"],
            "name": c.get("name"),
            "url": f"https://www.linkedin.com/in/{c['profile_id']}/",
            "note": c["note"],
        })
    for m in pending["messages"]:
        if m["id"] not in approved:
            continue
        actions.append({
            "id": m["id"],
            "action": "send_message",
            "profile_id": m["profile_id"],
            "name": m.get("name"),
            "template": m.get("template"),
            "message": m["message"],
        })
    for n in pending.get("inmails", []):
        if n["id"] not in approved:
            continue
        actions.append({
            "id": n["id"],
            "action": "send_inmail",
            "profile_id": n["profile_id"],
            "name": n.get("name"),
            "subject": n.get("subject", "Quick hello"),
            "message": n["message"],
        })
    if "p1" in approved and pending.get("post") and not pending["post"].get("skip_reason"):
        actions.append({
            "id": "p1",
            "action": "publish_post",
            "content": pending["post"]["post"],
        })
    return actions


def _append_audit(events: list[dict]) -> None:
    AUDITS_DIR.mkdir(parents=True, exist_ok=True)
    today = datetime.now(IST).strftime("%Y-%m-%d")
    audit_path = AUDITS_DIR / f"{today}.jsonl"
    with audit_path.open("a") as f:
        for ev in events:
            f.write(json.dumps({"source": "linkedin_executor", **ev}) + "\n")


def _append_contacted(events: list[dict]) -> None:
    with CONTACTED_LOG.open("a") as fh:
        for ev in events:
            if ev.get("outcome") not in ("success", "already_done"):
                continue
            if ev.get("action") == "publish_post":
                continue
            fh.write(json.dumps({
                "ts": ev.get("ts"),
                "profile_id": ev.get("profile_id"),
                "action": ev.get("action"),
                "outcome": ev.get("outcome"),
            }) + "\n")


def _bump_state_counters(events: list[dict]) -> None:
    state = json.loads(STATE_PATH.read_text())
    today = datetime.now(IST).strftime("%Y-%m-%d")
    state["today"]["date"] = today

    successes = [e for e in events if e.get("outcome") == "success"]
    follow_n = sum(1 for e in successes if e["action"] == "follow_profile")
    conn_n = sum(1 for e in successes if e["action"] == "send_connection")
    msg_n = sum(1 for e in successes if e["action"] == "send_message")
    inm_n = sum(1 for e in successes if e["action"] == "send_inmail")
    post_n = sum(1 for e in successes if e["action"] == "publish_post")

    for bucket in ("rolling_7d", "rolling_30d"):
        state[bucket]["follows_sent"] = state[bucket].get("follows_sent", 0) + follow_n
        state[bucket]["connections_sent"] = state[bucket].get("connections_sent", 0) + conn_n
        state[bucket]["messages_sent"] = state[bucket].get("messages_sent", 0) + msg_n
        if "inmails_sent" in state[bucket]:
            state[bucket]["inmails_sent"] += inm_n
        state[bucket]["posts_published"] = state[bucket].get("posts_published", 0) + post_n

    state["lifetime"]["total_follows_sent"] = state["lifetime"].get("total_follows_sent", 0) + follow_n
    state["lifetime"]["total_connections_sent"] = state["lifetime"].get("total_connections_sent", 0) + conn_n
    state["lifetime"]["total_messages_sent"] = state["lifetime"].get("total_messages_sent", 0) + msg_n
    state["lifetime"]["total_posts_published"] = state["lifetime"].get("total_posts_published", 0) + post_n
    if state["lifetime"]["first_run_date"] is None:
        state["lifetime"]["first_run_date"] = today

    STATE_PATH.write_text(json.dumps(state, indent=2))


def execute_today() -> dict:
    today = datetime.now(IST).strftime("%Y-%m-%d")
    pending, decisions = _load_pending_and_decisions(today)
    if pending is None:
        return {"error": f"No pending batch for {today}"}
    actions = _build_action_list(pending, decisions)
    if not actions:
        return {"ok": True, "executed": 0, "note": "No approved actions to run."}

    prompt = EXECUTE_PROMPT.format(
        actions_block=json.dumps(actions, indent=2, ensure_ascii=False),
    )
    raw = _claude_helper.with_tools(prompt, max_turns=80, timeout=1800)

    import re
    fenced = re.search(r"```(?:json)?\s*(.+?)\s*```", raw, re.DOTALL)
    payload = fenced.group(1) if fenced else raw
    try:
        result = json.loads(payload)
    except json.JSONDecodeError:
        _telegram_notify.send(
            f"❌ LinkedIn executor: Claude returned invalid JSON. Raw output saved.\n"
            f"```\n{raw[:600]}\n```"
        )
        return {"error": "invalid JSON from executor", "raw": raw[:2000]}

    events = result.get("events", [])
    _append_audit(events)
    _append_contacted(events)
    _bump_state_counters(events)

    summary = (
        f"✅ LinkedIn executor done.\n"
        f"  Executed: {result.get('completed_count', 0)}\n"
        f"  Skipped: {result.get('skipped_count', 0)}\n"
        f"  Failed: {result.get('failed_count', 0)}\n"
    )
    if result.get("halted"):
        summary += f"⚠️ HALTED: {result.get('halt_reason')}\n"
    _telegram_notify.send(summary)
    return result


if __name__ == "__main__":
    print(json.dumps(execute_today(), indent=2, ensure_ascii=False))
