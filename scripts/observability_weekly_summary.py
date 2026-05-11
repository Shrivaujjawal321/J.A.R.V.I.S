#!/usr/bin/env python3
"""
Observability weekly summary for Jarvis.

Aggregates last 7 days of agent invocations + feedback, produces a
Markdown summary, and sends it to Telegram.

Run manually:
    .venv/bin/python scripts/observability_weekly_summary.py

Scheduled as: ~/.config/systemd/user/jarvis-observability.timer
    Every Sunday at 19:00 IST (13:30 UTC).
"""

import json
import os
import sys
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
LOGS_DIR = ROOT / "data" / "logs"
BRIDGE_ENV = ROOT / "bridge" / ".env"
ROOT_ENV = ROOT / ".env"
FEEDBACK_FILE = LOGS_DIR / "feedback.jsonl"

POSITIVE_RATINGS = {"thumbs_up", "star_5", "star_4", "good", "positive"}
NEGATIVE_RATINGS = {"thumbs_down", "star_1", "star_2", "bad", "negative"}


def load_env_file(path):
    env = {}
    if not path.exists():
        return env
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        env[k.strip()] = v.strip()
    return env


def get_telegram_creds():
    bridge = load_env_file(BRIDGE_ENV)
    root_env = load_env_file(ROOT_ENV)
    token = (bridge.get("TELEGRAM_BOT_TOKEN")
             or root_env.get("TELEGRAM_BOT_TOKEN")
             or os.getenv("TELEGRAM_BOT_TOKEN") or "")
    raw_chat = (bridge.get("TELEGRAM_CHAT_ID")
                or root_env.get("TELEGRAM_CHAT_ID")
                or os.getenv("TELEGRAM_CHAT_ID") or "")
    if not raw_chat:
        allowed_raw = (bridge.get("ALLOWED_USER_IDS")
                       or root_env.get("ALLOWED_USER_IDS")
                       or os.getenv("ALLOWED_USER_IDS") or "")
        raw_chat = next((x.strip() for x in allowed_raw.split(",") if x.strip()), "")
    return token.strip(), raw_chat.strip()


def send_telegram(token, chat_id, text):
    url = "https://api.telegram.org/bot" + token + "/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
    try:
        resp = requests.post(url, json=payload, timeout=15)
        resp.raise_for_status()
        return True
    except requests.RequestException as exc:
        print("[observability_weekly_summary] Telegram send failed: " + str(exc),
              file=sys.stderr)
        return False


def iter_invocations(since):
    now = datetime.now(timezone.utc)
    cursor = since.date()
    end = now.date()
    while cursor <= end:
        stamp = cursor.strftime("%Y-%m-%d")
        path = LOGS_DIR / ("agent-invocations-" + stamp + ".jsonl")
        if path.exists():
            with path.open() as fh:
                for line in fh:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        rec = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    try:
                        rec_ts = datetime.fromisoformat(rec["ts"])
                    except (KeyError, ValueError):
                        yield rec
                        continue
                    if rec_ts >= since:
                        yield rec
        cursor = cursor + timedelta(days=1)


def iter_feedback(since):
    if not FEEDBACK_FILE.exists():
        return
    with FEEDBACK_FILE.open() as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            try:
                rec_ts = datetime.fromisoformat(rec["ts"])
            except (KeyError, ValueError):
                yield rec
                continue
            if rec_ts >= since:
                yield rec


def percentile(sorted_vals, pct):
    if not sorted_vals:
        return 0.0
    idx = min(int(len(sorted_vals) * pct / 100), len(sorted_vals) - 1)
    return sorted_vals[idx]


def build_summary():
    since = datetime.now(timezone.utc) - timedelta(days=7)
    week_label = since.strftime("%b %d") + " - " + datetime.now(timezone.utc).strftime("%b %d, %Y")

    # Collect invocations
    agent_counts = Counter()
    agent_failures = Counter()
    agent_durations = defaultdict(list)
    total_invocations = 0
    total_failures = 0

    for r in iter_invocations(since):
        agent = r.get("agent", "unknown")
        agent_counts[agent] += 1
        total_invocations += 1
        dur = r.get("duration_ms")
        if dur is not None:
            agent_durations[agent].append(float(dur))
        if not r.get("success", True):
            agent_failures[agent] += 1
            total_failures += 1

    # Collect feedback
    fb_counts = Counter()
    fb_positive = Counter()
    fb_negative = Counter()
    total_feedback = 0
    neg_notes = []

    for r in iter_feedback(since):
        target = r.get("target", "unknown")
        rating = r.get("rating", "")
        fb_counts[target] += 1
        total_feedback += 1
        if rating in POSITIVE_RATINGS:
            fb_positive[target] += 1
        elif rating in NEGATIVE_RATINGS:
            fb_negative[target] += 1
            note = r.get("note", "")
            if note:
                neg_notes.append((target, note[:80]))

    # Build message
    lines = [
        "*Jarvis - Weekly Observability Summary*",
        "_" + week_label + "_",
        "",
        "*Agent Invocations*",
        "Total: " + str(total_invocations) + " | Failures: " + str(total_failures),
    ]

    if agent_counts:
        lines.append("")
        lines.append("Top agents:")
        for agent, count in agent_counts.most_common(5):
            fails = agent_failures.get(agent, 0)
            durations = sorted(agent_durations.get(agent, []))
            p95 = percentile(durations, 95)
            p95_str = str(round(p95)) + "ms" if durations else "n/a"
            fail_str = (" | " + str(fails) + " fail") if fails else ""
            lines.append("  - `" + agent + "`: " + str(count) + " calls | p95=" + p95_str + fail_str)
    else:
        lines.append("No invocations recorded this week.")

    lines.append("")
    lines.append("*Feedback*")
    lines.append("Total: " + str(total_feedback))

    if fb_counts:
        lines.append("")
        lines.append("By target:")
        for target, total in fb_counts.most_common(5):
            pos = fb_positive.get(target, 0)
            neg = fb_negative.get(target, 0)
            rate = str(100 * pos // total) + "%" if total > 0 else "n/a"
            lines.append("  - `" + target + "`: " + str(total) + " (" + rate + " positive)")
        if neg_notes:
            lines.append("")
            lines.append("Recent negative feedback:")
            for target, note in neg_notes[:3]:
                lines.append("  - [" + target + "] " + note)
    else:
        lines.append("No feedback recorded this week.")

    lines.append("")
    lines.append("_Generated by Jarvis observability_weekly_summary.py_")

    return "\n".join(lines)


def main():
    token, chat_id = get_telegram_creds()
    if not token:
        print("[observability_weekly_summary] FATAL: TELEGRAM_BOT_TOKEN not found",
              file=sys.stderr)
        sys.exit(1)
    if not chat_id:
        print("[observability_weekly_summary] FATAL: chat_id not found",
              file=sys.stderr)
        sys.exit(1)

    summary = build_summary()
    print("[observability_weekly_summary] Summary built, sending to Telegram...")
    print(summary)
    print("---")

    ok = send_telegram(token, chat_id, summary)
    if ok:
        print("[observability_weekly_summary] Telegram message sent successfully.")
    else:
        print("[observability_weekly_summary] Telegram send failed — message printed above.",
              file=sys.stderr)


if __name__ == "__main__":
    main()
