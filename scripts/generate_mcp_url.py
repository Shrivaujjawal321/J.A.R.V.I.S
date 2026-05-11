"""Generate a Composio MCP URL for the Gmail toolkit.

Run once after creating a Composio account. Reads COMPOSIO_API_KEY and USER_ID
from .env. Creates a Gmail auth config (Composio-managed OAuth) + an MCP server,
prints the MCP URL to register with Claude Code.

Idempotent: reuses existing auth config / MCP server if already created
(matches by name `jarvis-gmail`).
"""

import os
import sys
from dotenv import load_dotenv
from composio_client import Composio

load_dotenv()

api_key = os.getenv("COMPOSIO_API_KEY")
user_id = os.getenv("USER_ID")

if not api_key or not user_id:
    print("ERROR: Set COMPOSIO_API_KEY and USER_ID in .env", file=sys.stderr)
    sys.exit(1)

MCP_NAME = "jarvis-gmail"
client = Composio(api_key=api_key)

existing = client.auth_configs.list(toolkit_slug="gmail")
auth_config_id = None
items = getattr(existing, "items", None) or getattr(existing, "data", None) or []
for ac in items:
    if getattr(ac, "name", None) == MCP_NAME:
        auth_config_id = ac.id
        break

if not auth_config_id:
    ac_resp = client.auth_configs.create(
        toolkit={"slug": "gmail"},
        auth_config={
            "type": "use_composio_managed_auth",
            "name": MCP_NAME,
        },
    )
    auth_config_id = ac_resp.auth_config.id if hasattr(ac_resp, "auth_config") else ac_resp.id
    print(f"Created auth config: {auth_config_id}", file=sys.stderr)
else:
    print(f"Reusing auth config: {auth_config_id}", file=sys.stderr)

existing_mcp = client.mcp.list()
mcp_items = getattr(existing_mcp, "items", None) or getattr(existing_mcp, "data", None) or []
mcp_url = None
for m in mcp_items:
    if getattr(m, "name", None) == MCP_NAME:
        mcp_url = getattr(m, "mcp_url", None) or getattr(m, "url", None)
        if mcp_url:
            print(f"Reusing MCP server: {m.id}", file=sys.stderr)
            break

if not mcp_url:
    mcp_resp = client.mcp.create(
        name=MCP_NAME,
        auth_config_ids=[auth_config_id],
        managed_auth_via_composio=True,
        ttl="no expiration",
    )
    mcp_url = getattr(mcp_resp, "mcp_url", None) or getattr(mcp_resp, "url", None)
    print(f"Created MCP server", file=sys.stderr)

print(mcp_url)
