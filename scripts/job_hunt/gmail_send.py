#!/usr/bin/env python3
"""
Direct Gmail API sender for the job-outreach engine.
Bypasses Composio entirely — uses the GCP OAuth client in .env + Google's own
OAuth (Google is up even when Composio is down). Token cached locally and
reused, so daily sends are fully automated after a one-time consent.

Usage:
  python scripts/job_hunt/gmail_send.py auth                 # one-time consent
  python scripts/job_hunt/gmail_send.py whoami               # show authed email
  python scripts/job_hunt/gmail_send.py send-json batch.json # send a list, paced
batch.json = [{"to": "...", "subject": "...", "body": "..."}, ...]
"""
import os
import sys
import json
import time
import base64
from email.mime.text import MIMEText

from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

load_dotenv()

SCOPES = ["https://www.googleapis.com/auth/gmail.send",
          "https://www.googleapis.com/auth/gmail.readonly"]
TOKEN_PATH = os.path.join(os.path.dirname(__file__), ".gmail_token.json")
REDIRECT_PORT = 8753


def _client_config():
    cid = os.getenv("GCP_CLIENT_ID")
    csec = os.getenv("GCP_CLIENT_SECRET")
    if not cid or not csec:
        sys.exit("ERROR: GCP_CLIENT_ID / GCP_CLIENT_SECRET missing in .env")
    return {"installed": {
        "client_id": cid,
        "client_secret": csec,
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "redirect_uris": ["http://localhost"],
    }}


def get_creds(interactive=False):
    creds = None
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    if creds and creds.valid:
        return creds
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        _save(creds)
        return creds
    if not interactive:
        sys.exit("NOT AUTHENTICATED — run: python scripts/job_hunt/gmail_send.py auth")
    flow = InstalledAppFlow.from_client_config(_client_config(), SCOPES)
    # open_browser False: print URL so Boss can open it; local server captures redirect
    creds = flow.run_local_server(port=REDIRECT_PORT, open_browser=False,
                                  authorization_prompt_message="OPEN THIS URL TO AUTHORISE:\n{url}",
                                  success_message="Done — Gmail send authorised. Aap is tab ko band kar sakte ho.")
    _save(creds)
    return creds


def _save(creds):
    with open(TOKEN_PATH, "w") as f:
        f.write(creds.to_json())
    os.chmod(TOKEN_PATH, 0o600)


def service(interactive=False):
    return build("gmail", "v1", credentials=get_creds(interactive), cache_discovery=False)


def whoami():
    prof = service().users().getProfile(userId="me").execute()
    print("AUTHED AS:", prof.get("emailAddress"))
    return prof.get("emailAddress")


def send_one(svc, to, subject, body):
    msg = MIMEText(body)
    msg["to"] = to
    msg["subject"] = subject
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    sent = svc.users().messages().send(userId="me", body={"raw": raw}).execute()
    return sent.get("id")


def send_json(path):
    with open(path) as f:
        items = json.load(f)
    svc = service()
    who = svc.users().getProfile(userId="me").execute().get("emailAddress")
    print(f"Sending {len(items)} emails from {who}\n")
    results = []
    for i, it in enumerate(items, 1):
        try:
            mid = send_one(svc, it["to"], it["subject"], it["body"])
            print(f"  [{i}/{len(items)}] ✅ {it['to']:<35} id={mid}")
            results.append({"to": it["to"], "ok": True, "id": mid})
        except Exception as e:
            print(f"  [{i}/{len(items)}] ❌ {it['to']:<35} {e}")
            results.append({"to": it["to"], "ok": False, "error": str(e)})
        if i < len(items):
            time.sleep(20)  # gentle pacing between sends
    ok = sum(1 for r in results if r["ok"])
    print(f"\nDONE: {ok}/{len(items)} sent.")
    print(json.dumps(results))


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "auth":
        get_creds(interactive=True)
        whoami()
    elif cmd == "whoami":
        whoami()
    elif cmd == "send-json":
        send_json(sys.argv[2])
    else:
        print(__doc__)
        sys.exit(1)
