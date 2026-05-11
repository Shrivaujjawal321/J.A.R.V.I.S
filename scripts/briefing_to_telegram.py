"""Run /briefing via Claude headless and send the result to Boss on Telegram.

Used by cron for automated morning briefings.

Reads from bridge/.env: TELEGRAM_BOT_TOKEN, ALLOWED_USER_IDS (first id = chat).
"""

import os
import json
import subprocess
import sys
import textwrap
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_env(path: Path) -> dict:
    env = {}
    if not path.exists():
        return env
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        env[k.strip()] = v.strip()
    return env


env = load_env(ROOT / "bridge" / ".env")
token = env.get("TELEGRAM_BOT_TOKEN") or os.getenv("TELEGRAM_BOT_TOKEN")
allowed = (env.get("ALLOWED_USER_IDS") or os.getenv("ALLOWED_USER_IDS") or "").split(",")
chat_id = next((x.strip() for x in allowed if x.strip()), None)
prompt = sys.argv[1] if len(sys.argv) > 1 else "/briefing"
max_turns = os.getenv("BRIEFING_MAX_TURNS", "25")

if not token or not chat_id:
    print("ERROR: TELEGRAM_BOT_TOKEN / ALLOWED_USER_IDS not set", file=sys.stderr)
    sys.exit(1)


def tg_send(text: str):
    for chunk in textwrap.wrap(text, 3800, replace_whitespace=False, drop_whitespace=False) or [text]:
        data = urllib.parse.urlencode({
            "chat_id": chat_id,
            "text": chunk,
            "parse_mode": "Markdown",
        }).encode()
        req = urllib.request.Request(
            f"https://api.telegram.org/bot{token}/sendMessage",
            data=data,
            method="POST",
        )
        try:
            urllib.request.urlopen(req, timeout=20).read()
        except Exception as e:
            print(f"telegram send failed: {e}", file=sys.stderr)


tg_send(f"🌅 Generating: `{prompt}` ...")

start = time.time()
try:
    proc = subprocess.run(
        [
            "claude",
            "-p", prompt,
            "--output-format", "json",
            "--max-turns", str(max_turns),
        ],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=600,
    )
except subprocess.TimeoutExpired:
    tg_send("⏱ Briefing timed out after 10 min.")
    sys.exit(1)

elapsed = int(time.time() - start)

if proc.returncode != 0:
    tg_send(f"❌ Claude error (exit {proc.returncode}):\n```\n{proc.stderr[:1500]}\n```")
    sys.exit(1)

try:
    data = json.loads(proc.stdout)
    text = data.get("result") or data.get("response") or proc.stdout
except json.JSONDecodeError:
    text = proc.stdout

tg_send(f"✅ Done in {elapsed}s\n\n{text}")
