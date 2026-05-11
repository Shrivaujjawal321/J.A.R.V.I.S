"""Set up Composio MCPs that need custom OAuth credentials (e.g. Google Contacts/Forms/Chat).

Reads GCP_CLIENT_ID and GCP_CLIENT_SECRET from .env. Creates auth_config with
`use_custom_auth`, MCP server, and OAuth link.

Usage:
    python scripts/setup_custom_oauth_mcp.py <toolkit_slug> <mcp_name>
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
client_id = os.getenv("GCP_CLIENT_ID")
client_secret = os.getenv("GCP_CLIENT_SECRET")

if len(sys.argv) != 3:
    print(__doc__, file=sys.stderr)
    sys.exit(1)

toolkit_slug, mcp_name = sys.argv[1], sys.argv[2]

if not all([api_key, user_id, client_id, client_secret]):
    print("ERROR: Need COMPOSIO_API_KEY, USER_ID, GCP_CLIENT_ID, GCP_CLIENT_SECRET in .env", file=sys.stderr)
    sys.exit(1)

client = Composio(api_key=api_key)
BASE = "https://backend.composio.dev"
H = {"x-api-key": api_key, "Content-Type": "application/json"}


def find_named(items, name):
    for it in items or []:
        if getattr(it, "name", None) == name:
            return it
    return None


# auth_config — custom OAuth
acs = client.auth_configs.list(toolkit_slug=toolkit_slug)
ac_items = getattr(acs, "items", None) or getattr(acs, "data", None) or []
existing_ac = find_named(ac_items, mcp_name)
if existing_ac:
    auth_config_id = existing_ac.id
    print(f"[ac] reuse {auth_config_id}", file=sys.stderr)
else:
    ac_resp = client.auth_configs.create(
        toolkit={"slug": toolkit_slug},
        auth_config={
            "type": "use_custom_auth",
            "auth_scheme": "OAUTH2",
            "name": mcp_name,
            "credentials": {
                "client_id": client_id,
                "client_secret": client_secret,
            },
        },
    )
    auth_config_id = ac_resp.auth_config.id if hasattr(ac_resp, "auth_config") else ac_resp.id
    print(f"[ac] create {auth_config_id}", file=sys.stderr)

# MCP
mcps = client.mcp.list()
mcp_items = getattr(mcps, "items", None) or getattr(mcps, "data", None) or []
existing_mcp = find_named(mcp_items, mcp_name)
if existing_mcp:
    mcp_url = getattr(existing_mcp, "mcp_url", None) or getattr(existing_mcp, "url", None)
    print(f"[mcp] reuse {existing_mcp.id}", file=sys.stderr)
else:
    mcp_resp = client.mcp.create(
        name=mcp_name,
        auth_config_ids=[auth_config_id],
        managed_auth_via_composio=False,
        ttl="no expiration",
    )
    mcp_url = getattr(mcp_resp, "mcp_url", None) or getattr(mcp_resp, "url", None)
    print(f"[mcp] create", file=sys.stderr)

# Connection
conns = client.connected_accounts.list(user_ids=[user_id], auth_config_ids=[auth_config_id])
c_items = getattr(conns, "items", None) or getattr(conns, "data", None) or []
active = [a for a in c_items if getattr(a, "status", None) == "ACTIVE"]
if active:
    print(json.dumps({
        "toolkit": toolkit_slug, "mcp_name": mcp_name,
        "auth_config_id": auth_config_id, "mcp_url": mcp_url,
        "connection_id": active[0].id, "oauth_redirect": None,
        "status": "ALREADY_ACTIVE",
    }, indent=2))
    sys.exit(0)

r = requests.post(
    f"{BASE}/api/v3/connected_accounts/link",
    headers=H,
    json={"auth_config_id": auth_config_id, "user_id": user_id},
    timeout=30,
)
r.raise_for_status()
data = r.json()
print(json.dumps({
    "toolkit": toolkit_slug, "mcp_name": mcp_name,
    "auth_config_id": auth_config_id, "mcp_url": mcp_url,
    "connection_id": data["connected_account_id"],
    "oauth_redirect": data["redirect_url"],
    "status": "NEEDS_OAUTH",
}, indent=2))
