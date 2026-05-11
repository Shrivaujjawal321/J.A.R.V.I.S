#!/usr/bin/env python3
"""
Trigger Watcher for Jarvis.

Runs every 6 hours via systemd timer. Checks:
  1. Upcoming hackathon deadlines (tasks.md, within 7 days)
  2. Job apply gap (data/markers/last_job_apply mtime > 2 days)
  3. Resume update gap (data/markers/resume_last_updated mtime > 7 days)

Sends Telegram alerts only when conditions are met, with 24h cooldown per
alert so it does not spam on repeated runs.

State is stored in data/markers/trigger_state.json.
Log is appended to data/logs/trigger_watcher.jsonl.

Usage:
    .venv/bin/python scripts/trigger_watcher.py
"""

import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[1]
TASKS_FILE = ROOT / "data" / "tasks.md"
MARKERS_DIR = ROOT / "data" / "markers"
STATE_FILE = MARKERS_DIR / "trigger_state.json"
LOGS_DIR = ROOT / "data" / "logs"
LOG_FILE = LOGS_DIR / "trigger_watcher.jsonl"
BRIDGE_ENV = ROOT / "bridge" / ".env"
ROOT_ENV = ROOT / ".env"

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
HACKATHON_ALERT_DAYS = 7    # alert if deadline is within this many days
JOB_APPLY_GAP_DAYS = 2      # flag if no apply recorded in this many days
RESUME_UPDATE_GAP_DAYS = 7  # flag if resume not updated in this many days
COOLDOWN_HOURS = 24         # suppress re-alerts for the same key within this window


# ---------------------------------------------------------------------------
# Env Loading
# ---------------------------------------------------------------------------

def load_env_file(path):
    """Parse a simple KEY=VALUE .env file into a dict."""
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
    """
    Resolve TELEGRAM_BOT_TOKEN and chat_id.
    Priority: bridge/.env > .env > environment variables.
    Chat ID may be stored as first entry in ALLOWED_USER_IDS.
    """
    bridge = load_env_file(BRIDGE_ENV)
    root_env = load_env_file(ROOT_ENV)

    token = (
        bridge.get("TELEGRAM_BOT_TOKEN")
        or root_env.get("TELEGRAM_BOT_TOKEN")
        or os.getenv("TELEGRAM_BOT_TOKEN")
        or ""
    )

    raw_chat = (
        bridge.get("TELEGRAM_CHAT_ID")
        or root_env.get("TELEGRAM_CHAT_ID")
        or os.getenv("TELEGRAM_CHAT_ID")
        or ""
    )
    if not raw_chat:
        allowed_raw = (
            bridge.get("ALLOWED_USER_IDS")
            or root_env.get("ALLOWED_USER_IDS")
            or os.getenv("ALLOWED_USER_IDS")
            or ""
        )
        raw_chat = next((x.strip() for x in allowed_raw.split(",") if x.strip()), "")

    return token.strip(), raw_chat.strip()


# ---------------------------------------------------------------------------
# State / Cooldown
# ---------------------------------------------------------------------------

def load_state():
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def save_state(state):
    MARKERS_DIR.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2))


def is_on_cooldown(state, key, cooldown_hours=COOLDOWN_HOURS):
    """Return True if this alert key was fired within cooldown_hours."""
    last_fired = state.get(key)
    if not last_fired:
        return False
    elapsed = time.time() - last_fired
    return elapsed < cooldown_hours * 3600


def mark_fired(state, key):
    state[key] = time.time()


# ---------------------------------------------------------------------------
# Telegram
# ---------------------------------------------------------------------------

def send_telegram(token, chat_id, text):
    """Send a message via Telegram Bot API. Returns True on success."""
    url = "https://api.telegram.org/bot" + token + "/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown",
    }
    try:
        resp = requests.post(url, json=payload, timeout=15)
        resp.raise_for_status()
        return True
    except requests.RequestException as exc:
        print("[trigger_watcher] Telegram send failed: " + str(exc), file=sys.stderr)
        return False


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

def log_run(flags_fired):
    """Append a JSONL line for this run."""
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    entry = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "flags": flags_fired if flags_fired else ["no_alerts"],
    }
    with LOG_FILE.open("a") as fh:
        fh.write(json.dumps(entry) + "\n")


# ---------------------------------------------------------------------------
# Deadline Parsing
# ---------------------------------------------------------------------------

def parse_hackathon_deadlines(tasks_path):
    """
    Scan tasks.md for unchecked tasks with *due: YYYY-MM-DD*.
    Returns list of dicts {name, due_date, days_left} for tasks due within
    HACKATHON_ALERT_DAYS from today.
    """
    if not tasks_path.exists():
        return []

    content = tasks_path.read_text()
    today = datetime.now(timezone.utc).date()
    results = []

    for line in content.splitlines():
        # Skip completed tasks
        if re.match(r"^\s*-\s*\[x\]", line, re.IGNORECASE):
            continue

        due_match = re.search(r"\*due:\s*(\d{4}-\d{2}-\d{2})\*", line)
        if not due_match:
            continue

        due_str = due_match.group(1)
        try:
            due_date = datetime.strptime(due_str, "%Y-%m-%d").date()
        except ValueError:
            continue

        days_left = (due_date - today).days
        if days_left < 0 or days_left > HACKATHON_ALERT_DAYS:
            continue

        # Extract task name
        name_match = re.search("\\*\\*\\[P\\d\\]\\*\\*\\s+(.+?)\\s+—", line)
        if not name_match:
            name_match = re.search(r"\*\*\[P\d\]\*\*\s+(.+?)\s+--", line)
        if name_match:
            name = name_match.group(1).strip()
        else:
            name = re.sub(r"\s*\*due:.*?\*", "", line).strip("- [x] ").strip()[:80]

        results.append({
            "name": name,
            "due_date": due_str,
            "days_left": days_left,
        })

    return results


# ---------------------------------------------------------------------------
# Marker Checks
# ---------------------------------------------------------------------------

def marker_age_days(marker_path):
    """
    Return how many days since the marker file was last modified.
    Returns None if the file does not exist.
    """
    if not marker_path.exists():
        return None
    mtime = marker_path.stat().st_mtime
    return (time.time() - mtime) / 86400.0


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    token, chat_id = get_telegram_creds()

    if not token:
        print("[trigger_watcher] FATAL: TELEGRAM_BOT_TOKEN not found in bridge/.env or .env",
              file=sys.stderr)
        sys.exit(1)
    if not chat_id:
        print("[trigger_watcher] FATAL: chat_id not found — set TELEGRAM_CHAT_ID or ALLOWED_USER_IDS",
              file=sys.stderr)
        sys.exit(1)

    state = load_state()
    flags_fired = []

    # -- 1. Hackathon deadline checks ------------------------------------------
    upcoming = parse_hackathon_deadlines(TASKS_FILE)
    for task in upcoming:
        task_name = task["name"]
        task_due = task["due_date"]
        days = task["days_left"]

        safe_name = re.sub(r"[^a-z0-9]+", "_", task_name.lower())[:40]
        cooldown_key = "hackathon_" + safe_name + "_" + task_due

        if is_on_cooldown(state, cooldown_key):
            print("[trigger_watcher] Skipping (cooldown): " + cooldown_key)
            continue

        if days == 0:
            urgency = "TODAY"
        elif days == 1:
            urgency = "tomorrow"
        else:
            urgency = "in " + str(days) + " days"

        message = (
            "*Jarvis - Hackathon Deadline Alert*\n\n"
            "*" + task_name + "*\n"
            "Due: `" + task_due + "` (" + urgency + ")\n\n"
            "Register before the deadline - check data/tasks.md for link."
        )

        if send_telegram(token, chat_id, message):
            mark_fired(state, cooldown_key)
            flags_fired.append(cooldown_key)
            print("[trigger_watcher] Alerted: " + cooldown_key)

    # -- 2. Job apply gap check ------------------------------------------------
    last_apply_path = MARKERS_DIR / "last_job_apply"
    apply_age = marker_age_days(last_apply_path)
    apply_key = "job_apply_gap"
    should_alert_apply = (apply_age is None) or (apply_age > JOB_APPLY_GAP_DAYS)

    if should_alert_apply and not is_on_cooldown(state, apply_key):
        if apply_age is None:
            detail = "No record of a recent job application found."
        else:
            detail = ("Last application logged " + str(round(apply_age, 1)) +
                      " days ago (threshold: " + str(JOB_APPLY_GAP_DAYS) + " days).")

        message = (
            "*Jarvis - Job Apply Gap*\n\n"
            + detail + "\n\n"
            "Time to apply to some AI/ML roles. "
            "Momentum matters more than perfection right now."
        )

        if send_telegram(token, chat_id, message):
            mark_fired(state, apply_key)
            flags_fired.append(apply_key)
            print("[trigger_watcher] Alerted: " + apply_key)

    # -- 3. Resume update gap check --------------------------------------------
    resume_path = MARKERS_DIR / "resume_last_updated"
    resume_age = marker_age_days(resume_path)
    resume_key = "resume_overhaul_gap"
    should_alert_resume = (resume_age is None) or (resume_age > RESUME_UPDATE_GAP_DAYS)

    if should_alert_resume and not is_on_cooldown(state, resume_key):
        if resume_age is None:
            detail = "No resume update marker found."
        else:
            detail = ("Resume last updated " + str(round(resume_age, 1)) +
                      " days ago (threshold: " + str(RESUME_UPDATE_GAP_DAYS) + " days).")

        message = (
            "*Jarvis - Resume Overhaul Gap*\n\n"
            + detail + "\n\n"
            "Resume overhaul is the highest-leverage thing right now. "
            "Even 30 min of targeted improvement today matters."
        )

        if send_telegram(token, chat_id, message):
            mark_fired(state, resume_key)
            flags_fired.append(resume_key)
            print("[trigger_watcher] Alerted: " + resume_key)

    # -- Persist state and log -------------------------------------------------
    save_state(state)
    log_run(flags_fired)

    if not flags_fired:
        print("[trigger_watcher] No alerts fired this run.")
    else:
        print("[trigger_watcher] Fired " + str(len(flags_fired)) + " alert(s): " + str(flags_fired))


if __name__ == "__main__":
    main()
