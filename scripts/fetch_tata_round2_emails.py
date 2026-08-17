"""
Fetch Tata Steel Round 2 / hackathon emails from Gmail via Composio.
Searches last 7 days for relevant keywords, returns full content.
"""

import os
import sys
import json
from dotenv import load_dotenv

load_dotenv("/home/ujjwal/Documents/J.A.R.V.I.S./.env")

api_key = os.getenv("COMPOSIO_API_KEY")
user_id = os.getenv("USER_ID")

if not api_key or not user_id:
    print("ERROR: Missing COMPOSIO_API_KEY or USER_ID", file=sys.stderr)
    sys.exit(1)

try:
    from composio_client import Composio
except ImportError:
    print("ERROR: composio_client not installed", file=sys.stderr)
    sys.exit(1)

client = Composio(api_key=api_key)

# Search queries to run — multiple to maximize coverage
SEARCH_QUERIES = [
    "Tata Steel hackathon round 2",
    "Tata Steel second round shortlist",
    "hackathon next round qualified",
    "Tata Steel 2026 hackathon",
]

def search_gmail(query, max_results=10):
    """Search Gmail using GMAIL_SEARCH_EMAILS tool."""
    try:
        result = client.tools.execute(
            "GMAIL_SEARCH_EMAILS",
            user_id=user_id,
            arguments={
                "query": query,
                "max_results": max_results,
            }
        )
        return result
    except Exception as e:
        print(f"Search error for '{query}': {e}", file=sys.stderr)
        return None

def get_email_content(message_id):
    """Fetch full email content by message ID."""
    try:
        result = client.tools.execute(
            "GMAIL_GET_ATTACHMENT",
            user_id=user_id,
            arguments={
                "message_id": message_id,
            }
        )
        return result
    except Exception as e:
        # Try alternative tool name
        try:
            result2 = client.tools.execute(
                "GMAIL_FETCH_EMAILS",
                user_id=user_id,
                arguments={
                    "message_id": message_id,
                    "include_body": True,
                }
            )
            return result2
        except Exception as e2:
            print(f"Fetch error for message {message_id}: {e} / {e2}", file=sys.stderr)
            return None

def get_message_by_id(message_id):
    """Fetch a specific Gmail message by ID."""
    try:
        result = client.tools.execute(
            "GMAIL_GET_MESSAGE",
            user_id=user_id,
            arguments={
                "message_id": message_id,
            }
        )
        return result
    except Exception as e:
        try:
            result2 = client.tools.execute(
                "GMAIL_FETCH_MESSAGE_BY_ID",
                user_id=user_id,
                arguments={"message_id": message_id}
            )
            return result2
        except Exception as e2:
            print(f"Get message error for {message_id}: {e} / {e2}", file=sys.stderr)
            return None

print("=" * 70)
print("TATA STEEL ROUND 2 EMAIL SEARCH")
print("=" * 70)

# First, let's list available Gmail tools to know what we can use
print("\n[1] Listing available Gmail tools...")
try:
    tools_list = client.tools.list(toolkit_slug="gmail", limit="30")
    tools_items = getattr(tools_list, "items", None) or getattr(tools_list, "data", None) or []
    print(f"Available Gmail tools ({len(tools_items)}):")
    for t in tools_items:
        slug = getattr(t, "slug", None) or getattr(t, "name", None)
        desc = getattr(t, "description", "")
        print(f"  - {slug}: {desc[:80] if desc else ''}")
except Exception as e:
    print(f"Could not list tools: {e}", file=sys.stderr)

print("\n[2] Searching for Tata Steel Round 2 emails...")

# Run searches
all_messages = {}
for query in SEARCH_QUERIES:
    print(f"\nQuery: '{query}'")
    result = search_gmail(query, max_results=10)
    if result:
        raw = vars(result) if hasattr(result, '__dict__') else result
        print(f"Raw result type: {type(result)}")
        # Try to extract message list
        data = None
        if hasattr(result, 'data'):
            data = result.data
        elif hasattr(result, 'response_data'):
            data = result.response_data
        elif isinstance(result, dict):
            data = result

        print(f"Result data: {json.dumps(data if isinstance(data, (dict, list)) else str(data)[:500], indent=2, default=str)}")

        # Collect message IDs
        if isinstance(data, dict):
            messages = data.get('messages', data.get('threads', data.get('items', [])))
            if messages:
                for msg in messages:
                    if isinstance(msg, dict):
                        mid = msg.get('id') or msg.get('message_id')
                        if mid and mid not in all_messages:
                            all_messages[mid] = msg
    else:
        print("  No result")

print(f"\n[3] Found {len(all_messages)} unique messages. Fetching full content...")

for mid, msg_meta in all_messages.items():
    print(f"\n{'='*70}")
    print(f"Message ID: {mid}")
    print(f"Meta: {json.dumps(msg_meta, indent=2, default=str)[:300]}")

    # Try to get full message
    full_msg = get_message_by_id(mid)
    if full_msg:
        data = None
        if hasattr(full_msg, 'data'):
            data = full_msg.data
        elif hasattr(full_msg, 'response_data'):
            data = full_msg.response_data
        elif isinstance(full_msg, dict):
            data = full_msg
        print(f"Full message: {json.dumps(data if isinstance(data, (dict, list)) else str(data)[:2000], indent=2, default=str)}")
