"""
Direct Gmail search for Tata Steel Round 2 emails via Composio REST API.
Uses requests directly against the Composio v3 API.
"""

import os
import sys
import json
import requests
from dotenv import load_dotenv

load_dotenv("/home/ujjwal/Documents/J.A.R.V.I.S./.env")

API_KEY = os.getenv("COMPOSIO_API_KEY")
USER_ID = os.getenv("USER_ID")
BASE = "https://backend.composio.dev"

HEADERS = {
    "x-api-key": API_KEY,
    "Content-Type": "application/json",
}

def execute_tool(tool_slug, arguments):
    """Execute a Composio tool via REST API."""
    url = f"{BASE}/api/v3/tools/execute/{tool_slug}"
    payload = {
        "user_id": USER_ID,
        "arguments": arguments,
    }
    resp = requests.post(url, headers=HEADERS, json=payload, timeout=30)
    if resp.status_code == 200:
        return resp.json()
    else:
        print(f"HTTP {resp.status_code} for {tool_slug}: {resp.text[:300]}", file=sys.stderr)
        return None

def list_gmail_tools():
    """List available Gmail tools."""
    url = f"{BASE}/api/v3/tools"
    params = {"toolkit_slug": "gmail", "limit": "50"}
    resp = requests.get(url, headers=HEADERS, params=params, timeout=15)
    if resp.status_code == 200:
        return resp.json()
    else:
        print(f"HTTP {resp.status_code}: {resp.text[:300]}", file=sys.stderr)
        return None

print("=" * 70)
print("GMAIL TOOL DISCOVERY")
print("=" * 70)

tools_data = list_gmail_tools()
if tools_data:
    items = tools_data.get("items", [])
    print(f"Available Gmail tools ({len(items)}):")
    for t in items:
        slug = t.get("slug", t.get("name", ""))
        desc = t.get("description", "")[:100]
        print(f"  {slug}: {desc}")
else:
    print("Could not list tools")

print("\n" + "=" * 70)
print("SEARCHING FOR TATA STEEL ROUND 2 EMAILS")
print("=" * 70)

# Search 1: Main search
queries = [
    "Tata Steel hackathon round 2",
    "Tata Steel second round",
    "shortlisted round 2 hackathon",
    "qualified next round Tata",
]

all_email_ids = set()
emails_found = []

for q in queries:
    print(f"\nSearching: '{q}'")

    # Try GMAIL_SEARCH_EMAILS
    result = execute_tool("GMAIL_SEARCH_EMAILS", {
        "query": q,
        "max_results": 10,
    })

    if result:
        print(f"Result keys: {list(result.keys()) if isinstance(result, dict) else type(result)}")

        # Navigate response structure
        data = result.get("data", result.get("response", result))
        if isinstance(data, dict):
            messages = (
                data.get("messages") or
                data.get("threads") or
                data.get("items") or
                data.get("emails") or
                []
            )
            print(f"  Found {len(messages)} messages")
            for msg in messages:
                mid = msg.get("id") or msg.get("message_id") or msg.get("messageId")
                if mid and mid not in all_email_ids:
                    all_email_ids.add(mid)
                    emails_found.append(msg)
                    subject = msg.get("subject", msg.get("Subject", ""))
                    sender = msg.get("from", msg.get("From", msg.get("sender", "")))
                    date = msg.get("date", msg.get("Date", ""))
                    print(f"  + [{mid[:12]}] From: {sender} | Subject: {subject} | Date: {date}")
        else:
            print(f"  Data: {str(data)[:300]}")

    # Also try GMAIL_FETCH_EMAILS
    result2 = execute_tool("GMAIL_FETCH_EMAILS", {
        "query": q,
        "max_results": 10,
    })
    if result2:
        data2 = result2.get("data", result2.get("response", result2))
        if isinstance(data2, dict):
            messages2 = (
                data2.get("messages") or
                data2.get("emails") or
                []
            )
            if messages2:
                print(f"  GMAIL_FETCH_EMAILS found {len(messages2)} additional")
                for msg in messages2:
                    mid = msg.get("id") or msg.get("message_id")
                    if mid and mid not in all_email_ids:
                        all_email_ids.add(mid)
                        emails_found.append(msg)

print(f"\n{'='*70}")
print(f"TOTAL UNIQUE EMAILS FOUND: {len(all_email_ids)}")
print("=" * 70)

# Now fetch full content of each email
for i, msg in enumerate(emails_found, 1):
    mid = msg.get("id") or msg.get("message_id")
    subject = msg.get("subject", msg.get("Subject", "(no subject)"))
    sender = msg.get("from", msg.get("From", msg.get("sender", "")))

    print(f"\n{'='*70}")
    print(f"EMAIL {i}/{len(emails_found)}")
    print(f"ID: {mid}")
    print(f"Subject: {subject}")
    print(f"From: {sender}")

    # Try to get full body
    # First check if body is already in the search result
    body = (
        msg.get("body") or
        msg.get("snippet") or
        msg.get("content") or
        msg.get("text") or
        msg.get("html") or
        ""
    )

    if body and len(body) > 100:
        print(f"\nBODY (from search result):\n{body}")
    else:
        # Fetch full message
        full = execute_tool("GMAIL_GET_MESSAGE", {"message_id": mid})
        if not full:
            full = execute_tool("GMAIL_FETCH_MESSAGE_BY_ID", {"message_id": mid})
        if not full:
            full = execute_tool("GMAIL_GET_THREAD", {"thread_id": msg.get("threadId", mid)})

        if full:
            print(f"\nFULL MESSAGE DATA:")
            print(json.dumps(full, indent=2, default=str)[:5000])
        else:
            print(f"\n[Could not fetch full content. Snippet: {body[:200]}]")
