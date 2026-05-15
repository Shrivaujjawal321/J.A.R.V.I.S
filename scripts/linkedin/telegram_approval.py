"""
Telegram batch-approval flow for the LinkedIn morning pipeline.

Flow:
  1. daily_runner.py drafts the full batch (connections + messages + post)
  2. Calls send_morning_batch() here
  3. This module formats + sends the batch to Boss via Telegram
  4. Stores the batch in data/linkedin/drafts/<date>_pending.json
  5. Bot commands implemented in bridge/telegram_bridge.py:
       /lp_approve_all                 — approves everything
       /lp_approve <ids>               — approves only listed item ids (comma-sep)
       /lp_reject <ids>                — rejects listed items, rest remain pending
       /lp_status                      — shows current pending batch status
  6. Boss's decision writes data/linkedin/drafts/<date>_decisions.json
  7. executor.py reads decisions + executes approved items only

Approval semantics:
  - Anything NOT explicitly rejected and NOT explicitly approved at execution
    time defaults to REJECT (safer than auto-approve).
  - /lp_approve_all is the lazy path — Boss accepts the whole batch.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from . import _auto_mode, _telegram_notify

JARVIS_ROOT = Path(__file__).resolve().parents[2]
DRAFTS_DIR = JARVIS_ROOT / "data" / "linkedin" / "drafts"
IST = ZoneInfo("Asia/Kolkata")

MAX_PREVIEW_PER_TYPE = 5  # Telegram message length cap; full batch in stored file


def _today_str() -> str:
    return datetime.now(IST).strftime("%Y-%m-%d")


def _format_connection(idx: int, item: dict) -> str:
    name = item.get("name") or item["profile_id"]
    cat = item.get("category_id", "?")
    note = item.get("note") or "(draft failed)"
    return f"`#c{idx}` *{name}* (cat {cat})\n  → {note}"


def _format_message(idx: int, item: dict) -> str:
    name = item.get("name") or item["profile_id"]
    template = item.get("template", "?")
    msg = item.get("message") or "(draft failed)"
    snippet = msg[:280] + ("…" if len(msg) > 280 else "")
    return f"`#m{idx}` *{name}* — `{template}`\n  → {snippet}"


def _format_post(post: dict) -> str:
    if post.get("skip_reason"):
        return f"_Post skipped: {post['skip_reason']}_"
    body = post.get("post") or "(draft failed)"
    snippet = body[:600] + ("…" if len(body) > 600 else "")
    theme = post.get("theme", "?")
    return f"`#p1` *Post — {theme}*\n```\n{snippet}\n```"


def _format_follow(idx: int, item: dict) -> str:
    name = item.get("name") or item["profile_id"]
    cat = item.get("category_id", "?")
    headline = (item.get("headline") or "")[:80]
    return f"`#f{idx}` *{name}* (cat {cat}) — {headline}"


def send_morning_batch(
    connections: list[dict] | None = None,
    messages: list[dict] | None = None,
    post: dict | None = None,
    *,
    follows: list[dict] | None = None,
    inmails: list[dict] | None = None,
) -> str:
    """
    Stores the batch on disk and sends a Telegram preview to Boss.
    Returns the batch_id.
    """
    DRAFTS_DIR.mkdir(parents=True, exist_ok=True)
    today = _today_str()
    batch_id = f"lp-{today}"
    pending_path = DRAFTS_DIR / f"{today}_pending.json"

    follows = follows or []
    connections = connections or []
    messages = messages or []
    inmails = inmails or []

    batch = {
        "batch_id": batch_id,
        "date": today,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "follows": [{"id": f"f{i}", **f} for i, f in enumerate(follows)],
        "connections": [{"id": f"c{i}", **c} for i, c in enumerate(connections)],
        "messages": [{"id": f"m{i}", **m} for i, m in enumerate(messages)],
        "inmails": [{"id": f"i{i}", **n} for i, n in enumerate(inmails)],
        "post": post,
        "status": "pending_approval",
    }
    pending_path.write_text(json.dumps(batch, indent=2, ensure_ascii=False))

    # Build Telegram preview
    parts = [
        f"🤖 *LinkedIn morning batch — {today}*",
        "",
    ]

    if follows:
        parts.append(f"👁️ *{len(follows)} follows*")
        for i, f in enumerate(follows[:MAX_PREVIEW_PER_TYPE]):
            parts.append(_format_follow(i, f))
        if len(follows) > MAX_PREVIEW_PER_TYPE:
            parts.append(f"_…and {len(follows) - MAX_PREVIEW_PER_TYPE} more_")
        parts.append("")

    if connections:
        parts.append(f"📤 *{len(connections)} connection requests*")
        for i, c in enumerate(connections[:MAX_PREVIEW_PER_TYPE]):
            parts.append(_format_connection(i, c))
        if len(connections) > MAX_PREVIEW_PER_TYPE:
            parts.append(f"_…and {len(connections) - MAX_PREVIEW_PER_TYPE} more (full list in {pending_path.name})_")
        parts.append("")

    if messages:
        parts.append(f"💬 *{len(messages)} DMs to 1st-degree*")
        for i, m in enumerate(messages[:MAX_PREVIEW_PER_TYPE]):
            parts.append(_format_message(i, m))
        if len(messages) > MAX_PREVIEW_PER_TYPE:
            parts.append(f"_…and {len(messages) - MAX_PREVIEW_PER_TYPE} more_")
        parts.append("")

    if inmails:
        parts.append(f"✉️ *{len(inmails)} InMails (Premium credits)*")
        for i, n in enumerate(inmails):
            parts.append(_format_message(i, n))
        parts.append("")

    parts.append("📝 *Today's post*")
    if post:
        parts.append(_format_post(post))
    else:
        parts.append("_No post scheduled_")

    parts.append("")
    parts.append("─" * 18)

    if _auto_mode.is_fullauto():
        # Auto-approve the entire batch; Telegram is informational only.
        record_decision("approve_all")
        parts.append("🤖 *fullauto mode — auto-approved entire batch.*")
        parts.append("Execute scheduled for 10:00 IST. To veto, reply:")
        parts.append("`/lp_reject c0,c2,m4` before then (also accepts f# / p1 ids)")
    else:
        parts.append("*Reply to act:*")
        parts.append("`/lp_approve_all` — send everything as drafted")
        parts.append("`/lp_reject c0,c2,m4` — reject specific items, rest still pending")
        parts.append("`/lp_approve c0,c1,m0,p1` — approve only listed items")
        parts.append("`/lp_status` — see what's pending")

    full_text = "\n".join(parts)
    _telegram_notify.send(full_text)
    return batch_id


def record_decision(decision_type: str, item_ids: list[str] | None = None) -> dict:
    """
    Called by the Telegram bridge when Boss runs /lp_approve* or /lp_reject.
    decision_type ∈ {approve_all, approve, reject}
    item_ids: list like ['c0', 'm3', 'p1'] — required for approve/reject.
    """
    today = _today_str()
    pending_path = DRAFTS_DIR / f"{today}_pending.json"
    decisions_path = DRAFTS_DIR / f"{today}_decisions.json"

    if not pending_path.exists():
        return {"error": f"No pending batch for {today}"}

    batch = json.loads(pending_path.read_text())
    decisions = (
        json.loads(decisions_path.read_text()) if decisions_path.exists()
        else {"batch_id": batch["batch_id"], "approved": [], "rejected": []}
    )

    if decision_type == "approve_all":
        all_ids = (
            [f["id"] for f in batch.get("follows", [])]
            + [c["id"] for c in batch["connections"]]
            + [m["id"] for m in batch["messages"]]
            + [n["id"] for n in batch.get("inmails", [])]
            + (["p1"] if batch.get("post") and not batch["post"].get("skip_reason") else [])
        )
        decisions["approved"] = list(set(decisions["approved"]) | set(all_ids))
    elif decision_type == "approve":
        decisions["approved"] = list(set(decisions["approved"]) | set(item_ids or []))
    elif decision_type == "reject":
        decisions["rejected"] = list(set(decisions["rejected"]) | set(item_ids or []))
    else:
        return {"error": f"Unknown decision_type: {decision_type}"}

    decisions["last_updated"] = datetime.now(timezone.utc).isoformat()
    decisions_path.write_text(json.dumps(decisions, indent=2))
    return {
        "ok": True,
        "approved_count": len(decisions["approved"]),
        "rejected_count": len(decisions["rejected"]),
    }


def status() -> str:
    today = _today_str()
    pending_path = DRAFTS_DIR / f"{today}_pending.json"
    decisions_path = DRAFTS_DIR / f"{today}_decisions.json"

    if not pending_path.exists():
        return f"No batch for {today} yet."
    batch = json.loads(pending_path.read_text())
    total = (
        len(batch.get("follows", []))
        + len(batch["connections"])
        + len(batch["messages"])
        + len(batch.get("inmails", []))
        + (1 if batch.get("post") else 0)
    )

    if not decisions_path.exists():
        return f"📋 Batch {batch['batch_id']}: {total} items, *0 approved, 0 rejected* — waiting."

    d = json.loads(decisions_path.read_text())
    pending = total - len(d["approved"]) - len(d["rejected"])
    return (
        f"📋 Batch *{batch['batch_id']}*\n"
        f"  Approved: {len(d['approved'])}\n"
        f"  Rejected: {len(d['rejected'])}\n"
        f"  Pending: {pending}"
    )


if __name__ == "__main__":
    print(status())
