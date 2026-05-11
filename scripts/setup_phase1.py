"""Set up Phase 1 Google MCPs in parallel via Composio.

Creates auth_config + MCP server + OAuth link for each toolkit.
Prints a JSON summary at the end with all OAuth links + MCP URLs.

Idempotent: reuses existing resources by name.
"""

import os
import sys
import json
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv
from composio_client import Composio

load_dotenv()

api_key = os.getenv("COMPOSIO_API_KEY")
user_id = os.getenv("USER_ID")
if not api_key or not user_id:
    print("ERROR: Set COMPOSIO_API_KEY and USER_ID in .env", file=sys.stderr)
    sys.exit(1)

PHASE1 = [
    ("googledocs",     "jarvis-docs"),
    ("googlesheets",   "jarvis-sheets"),
    ("googleslides",   "jarvis-slides"),
    ("googletasks",    "jarvis-tasks"),
    ("googlecontacts", "jarvis-contacts"),
    ("googlemeet",     "jarvis-meet"),
    ("googlephotos",   "jarvis-photos"),
    ("googleforms",    "jarvis-forms"),
    ("google_chat",    "jarvis-gchat"),
]

BASE = "https://backend.composio.dev"
H_JSON = {"x-api-key": api_key, "Content-Type": "application/json"}
H = {"x-api-key": api_key}


def find_named(items, name):
    for it in items or []:
        if getattr(it, "name", None) == name:
            return it
    return None


def setup_one(toolkit_slug: str, mcp_name: str) -> dict:
    client = Composio(api_key=api_key)

    # 1. auth_config (reuse-or-create)
    acs = client.auth_configs.list(toolkit_slug=toolkit_slug)
    ac_items = getattr(acs, "items", None) or getattr(acs, "data", None) or []
    existing_ac = find_named(ac_items, mcp_name)
    if existing_ac:
        auth_config_id = existing_ac.id
    else:
        ac_resp = client.auth_configs.create(
            toolkit={"slug": toolkit_slug},
            auth_config={"type": "use_composio_managed_auth", "name": mcp_name},
        )
        auth_config_id = ac_resp.auth_config.id if hasattr(ac_resp, "auth_config") else ac_resp.id

    # 2. MCP server (reuse-or-create)
    mcps = client.mcp.list()
    mcp_items = getattr(mcps, "items", None) or getattr(mcps, "data", None) or []
    existing_mcp = find_named(mcp_items, mcp_name)
    if existing_mcp:
        mcp_url = getattr(existing_mcp, "mcp_url", None) or getattr(existing_mcp, "url", None)
    else:
        mcp_resp = client.mcp.create(
            name=mcp_name,
            auth_config_ids=[auth_config_id],
            managed_auth_via_composio=True,
            ttl="no expiration",
        )
        mcp_url = getattr(mcp_resp, "mcp_url", None) or getattr(mcp_resp, "url", None)

    # 3. Connection (skip OAuth if already ACTIVE)
    conns = client.connected_accounts.list(
        user_ids=[user_id],
        auth_config_ids=[auth_config_id],
    )
    c_items = getattr(conns, "items", None) or getattr(conns, "data", None) or []
    active = [a for a in c_items if getattr(a, "status", None) == "ACTIVE"]
    if active:
        return {
            "toolkit": toolkit_slug,
            "mcp_name": mcp_name,
            "auth_config_id": auth_config_id,
            "mcp_url": mcp_url,
            "connection_id": active[0].id,
            "oauth_redirect": None,
            "status": "ALREADY_ACTIVE",
        }

    r = requests.post(
        f"{BASE}/api/v3/connected_accounts/link",
        headers=H_JSON,
        json={"auth_config_id": auth_config_id, "user_id": user_id},
        timeout=30,
    )
    r.raise_for_status()
    link_data = r.json()
    return {
        "toolkit": toolkit_slug,
        "mcp_name": mcp_name,
        "auth_config_id": auth_config_id,
        "mcp_url": mcp_url,
        "connection_id": link_data["connected_account_id"],
        "oauth_redirect": link_data["redirect_url"],
        "status": "NEEDS_OAUTH",
    }


results = []
with ThreadPoolExecutor(max_workers=6) as ex:
    futs = {ex.submit(setup_one, slug, name): (slug, name) for slug, name in PHASE1}
    for fut in as_completed(futs):
        slug, name = futs[fut]
        try:
            r = fut.result()
            results.append(r)
            print(f"  [ok] {name:20s} status={r['status']}", file=sys.stderr)
        except Exception as e:
            print(f"  [err] {name:20s} {e}", file=sys.stderr)
            results.append({"toolkit": slug, "mcp_name": name, "error": str(e)})

print(json.dumps(results, indent=2))
