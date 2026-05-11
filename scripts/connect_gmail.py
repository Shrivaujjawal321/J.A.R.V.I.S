"""Initiate Gmail OAuth via Composio.

Prints a redirect URL — open it in a browser and sign in with the Google
account you want Jarvis to use. After consent, Composio captures the token
and the MCP tools become live for this user_id.

Idempotent: if a connection already exists for (auth_config, user_id), prints
its status instead of starting a new flow.
"""

import os
import sys
import time
from dotenv import load_dotenv
from composio_client import Composio

load_dotenv()

api_key = os.getenv("COMPOSIO_API_KEY")
user_id = os.getenv("USER_ID")

if not api_key or not user_id:
    print("ERROR: Set COMPOSIO_API_KEY and USER_ID in .env", file=sys.stderr)
    sys.exit(1)

client = Composio(api_key=api_key)

acs = client.auth_configs.list(toolkit_slug="gmail")
items = getattr(acs, "items", None) or getattr(acs, "data", None) or []
auth_config_id = None
for ac in items:
    if getattr(ac, "name", None) == "jarvis-gmail":
        auth_config_id = ac.id
        break

if not auth_config_id:
    print("ERROR: jarvis-gmail auth config not found. Run generate_mcp_url.py first.", file=sys.stderr)
    sys.exit(1)

existing = client.connected_accounts.list(
    user_ids=[user_id],
    auth_config_ids=[auth_config_id],
)
ex_items = getattr(existing, "items", None) or getattr(existing, "data", None) or []
active = [a for a in ex_items if getattr(a, "status", None) == "ACTIVE"]
if active:
    print(f"Already connected. status=ACTIVE id={active[0].id}", file=sys.stderr)
    print("DONE")
    sys.exit(0)

resp = client.connected_accounts.create(
    auth_config={"id": auth_config_id},
    connection={"user_id": user_id},
)

redirect = getattr(resp, "redirect_url", None) or getattr(resp, "redirect_uri", None)
conn_id = getattr(resp, "id", None)

print(f"Connection ID: {conn_id}", file=sys.stderr)
print()
print("OPEN THIS URL IN YOUR BROWSER (sign in with Boss's Google account):")
print()
print(redirect)
print()
print("Polling for completion (up to 5 min)...", file=sys.stderr)

deadline = time.time() + 300
while time.time() < deadline:
    time.sleep(3)
    try:
        cur = client.connected_accounts.retrieve(conn_id)
        status = getattr(cur, "status", None)
        if status == "ACTIVE":
            print(f"\n✅ Connected! status=ACTIVE", file=sys.stderr)
            sys.exit(0)
        if status in ("FAILED", "EXPIRED"):
            print(f"\n❌ Connection failed: {status}", file=sys.stderr)
            sys.exit(1)
    except Exception as e:
        print(f"poll error: {e}", file=sys.stderr)

print("\n⏱  Timeout waiting for OAuth — check status with `connected_accounts.retrieve`", file=sys.stderr)
sys.exit(1)
