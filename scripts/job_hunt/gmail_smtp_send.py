#!/usr/bin/env python3
"""
Bulletproof Gmail sender via SMTP + App Password (no OAuth, no Composio, no browser).
Reads GMAIL_ADDRESS + GMAIL_APP_PASSWORD from .env. Works headless, forever.

Setup (one-time): create a Gmail App Password at
  https://myaccount.google.com/apppasswords  (needs 2-Step Verification ON)
Then add to .env:
  GMAIL_ADDRESS=shriva.ujjawal@gmail.com
  GMAIL_APP_PASSWORD=xxxxxxxxxxxxxxxx   (16 chars, no spaces)

Usage:
  python scripts/job_hunt/gmail_smtp_send.py test        # send a test email to yourself
  python scripts/job_hunt/gmail_smtp_send.py send batch.json
batch.json = [{"to": "...", "subject": "...", "body": "..."}, ...]
"""
import os
import sys
import ssl
import json
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.utils import formataddr
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()
ADDR = os.getenv("GMAIL_ADDRESS")
APP_PW = (os.getenv("GMAIL_APP_PASSWORD") or "").replace(" ", "")
SENDER_NAME = os.getenv("GMAIL_SENDER_NAME", "Ujjawal Shrivastav")


def _check():
    if not ADDR or not APP_PW:
        sys.exit("ERROR: set GMAIL_ADDRESS and GMAIL_APP_PASSWORD in .env")


def _connect():
    ctx = ssl.create_default_context()
    server = smtplib.SMTP_SSL("smtp.gmail.com", 465, context=ctx, timeout=30)
    server.login(ADDR, APP_PW)
    return server


def send_one(server, to, subject, body, attachments=None):
    """attachments: optional list of file paths to attach (e.g. resume PDF)."""
    if attachments:
        msg = MIMEMultipart()
        msg.attach(MIMEText(body, "plain", "utf-8"))
        for path in attachments:
            p = Path(path)
            part = MIMEApplication(p.read_bytes(), Name=p.name)
            part["Content-Disposition"] = f'attachment; filename="{p.name}"'
            msg.attach(part)
    else:
        msg = MIMEText(body, "plain", "utf-8")
    msg["From"] = formataddr((SENDER_NAME, ADDR))
    msg["To"] = to
    msg["Subject"] = subject
    server.sendmail(ADDR, [to], msg.as_string())


def cmd_test():
    _check()
    s = _connect()
    send_one(s, ADDR, "Jarvis SMTP test ✅",
             "If you can read this, the job-outreach engine can send mail. — Jarvis")
    s.quit()
    print(f"✅ test email sent to {ADDR} (check your inbox)")


def cmd_send(path):
    _check()
    with open(path) as f:
        items = json.load(f)
    s = _connect()
    print(f"Sending {len(items)} emails from {ADDR}\n")
    results = []
    for i, it in enumerate(items, 1):
        try:
            send_one(s, it["to"], it["subject"], it["body"])
            print(f"  [{i}/{len(items)}] ✅ {it['to']:<35} sent")
            results.append({"to": it["to"], "ok": True})
        except Exception as e:
            print(f"  [{i}/{len(items)}] ❌ {it['to']:<35} {e}")
            results.append({"to": it["to"], "ok": False, "error": str(e)})
        if i < len(items):
            time.sleep(20)  # gentle pacing
    s.quit()
    ok = sum(1 for r in results if r["ok"])
    print(f"\nDONE: {ok}/{len(items)} sent.")
    print("RESULTS_JSON " + json.dumps(results))


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "test":
        cmd_test()
    elif cmd == "send":
        cmd_send(sys.argv[2])
    else:
        print(__doc__)
        sys.exit(1)
