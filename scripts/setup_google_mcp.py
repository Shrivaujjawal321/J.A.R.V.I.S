"""Set up a Composio MCP server + OAuth link for any Google toolkit.

Usage:
    python scripts/setup_google_mcp.py <toolkit_slug> <mcp_name>

Example:
    python scripts/setup_google_mcp.py googlecalendar jarvis-calendar
    python scripts/setup_google_mcp.py googledrive    jarvis-drive

Idempotent: reuses existing auth_config / MCP server / connection if present.
Prints MCP URL + OAuth redirect URL + connection ID.
"""

import os
import sys
import json
import requests
from dotenv import load_dotenv
from composio_client import Composio

load_dotenv()

api_key = os.getenv("COMPOSIO_API_KEY")
user_id = os.getenv("USER_ID")

if len(sys.argv) != 3:
    print(__doc__, file=sys.stderr)
    sys.exit(1)

toolkit_slug, mcp_name = sys.argv[1], sys.argv[2]

if not api_key or not user_id:
    print("ERROR: Set COMPOSIO_API_KEY and USER_ID in .env", file=sys.stderr)
    sys.exit(1)

client = Composio(api_key=api_key)
BASE = "https://backend.composio.dev"
H = {"x-api-key": api_key, "Content-Type": "application/json"}


def find_named(items, name):
    for it in items or []:
        if getattr(it, "name", None) == name:
            return it
    return None


# 1. auth_config
acs = client.auth_configs.list(toolkit_slug=toolkit_slug)
ac_items = getattr(acs, "items", None) or getattr(acs, "data", None) or []
existing_ac = find_named(ac_items, mcp_name)
if existing_ac:
    auth_config_id = existing_ac.id
    print(f"[ac] reuse {auth_config_id}", file=sys.stderr)
else:
    ac_resp = client.auth_configs.create(
        toolkit={"slug": toolkit_slug},
        auth_config={"type": "use_composio_managed_auth", "name": mcp_name},
    )
    auth_config_id = ac_resp.auth_config.id if hasattr(ac_resp, "auth_config") else ac_resp.id
    print(f"[ac] create {auth_config_id}", file=sys.stderr)

# 2. MCP server
mcps = client.mcp.list()
mcp_items = getattr(mcps, "items", None) or getattr(mcps, "data", None) or []
existing_mcp = find_named(mcp_items, mcp_name)
mcp_url = None
if existing_mcp:
    mcp_url = getattr(existing_mcp, "mcp_url", None) or getattr(existing_mcp, "url", None)
    print(f"[mcp] reuse {existing_mcp.id}", file=sys.stderr)
else:
    mcp_resp = client.mcp.create(
        name=mcp_name,
        auth_config_ids=[auth_config_id],
        managed_auth_via_composio=True,
        ttl="no expiration",
    )
    mcp_url = getattr(mcp_resp, "mcp_url", None) or getattr(mcp_resp, "url", None)
    print(f"[mcp] create", file=sys.stderr)

# 3. Connection — check existing first
conns = client.connected_accounts.list(
    user_ids=[user_id],
    auth_config_ids=[auth_config_id],
)
c_items = getattr(conns, "items", None) or getattr(conns, "data", None) or []
active = [a for a in c_items if getattr(a, "status", None) == "ACTIVE"]
if active:
    print(f"[conn] already ACTIVE id={active[0].id}", file=sys.stderr)
    redirect = None
    conn_id = active[0].id
else:
    r = requests.post(
        f"{BASE}/api/v3/connected_accounts/link",
        headers=H,
        json={"auth_config_id": auth_config_id, "user_id": user_id},
        timeout=30,
    )
    r.raise_for_status()
    link_data = r.json()
    redirect = link_data["redirect_url"]
    conn_id = link_data["connected_account_id"]
    print(f"[conn] link created id={conn_id}", file=sys.stderr)

print()
print(json.dumps({
    "toolkit": toolkit_slug,
    "mcp_name": mcp_name,
    "auth_config_id": auth_config_id,
    "mcp_url": mcp_url,
    "user_id": user_id,
    "connection_id": conn_id,
    "oauth_redirect": redirect,
}, indent=2))
