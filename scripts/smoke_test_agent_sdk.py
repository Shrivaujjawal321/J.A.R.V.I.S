#!/usr/bin/env python3
"""
Smoke test: verify Claude Agent SDK works with Max-subscription OAuth token
(no developer API key needed).

Reads CLAUDE_CODE_OAUTH_TOKEN from .env, makes a tiny query, prints result.
If this passes, the full jarvis-core daemon build will work.
"""
from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

if not os.getenv("CLAUDE_CODE_OAUTH_TOKEN"):
    print("FAIL: CLAUDE_CODE_OAUTH_TOKEN not found in .env")
    print("Run: claude setup-token  →  copy token  →  add to .env")
    sys.exit(1)


async def main() -> int:
    from claude_agent_sdk import query, ClaudeAgentOptions

    print("Sending minimal query to Claude via Agent SDK...")
    print("(uses Max-subscription OAuth, no API key)")
    print()

    options = ClaudeAgentOptions(
        cwd=str(ROOT),
        max_turns=1,
        allowed_tools=[],  # No tool use — pure text response, smallest possible
    )

    got_text = False
    total_cost = None

    try:
        async for message in query(
            prompt="Reply with exactly: 'super agent online'. Nothing else.",
            options=options,
        ):
            # Best-effort message handling — SDK message types vary slightly across versions
            msg_type = type(message).__name__

            # Try extracting text content
            if hasattr(message, "content"):
                content = message.content
                if isinstance(content, list):
                    for block in content:
                        if hasattr(block, "text") and block.text:
                            print(f"[{msg_type}] {block.text!r}")
                            got_text = True

            # Capture cost / usage from ResultMessage
            if hasattr(message, "total_cost_usd"):
                total_cost = message.total_cost_usd
                print(f"[{msg_type}] total_cost_usd = {total_cost}")
            if hasattr(message, "result") and message.result:
                print(f"[{msg_type}] result = {message.result!r}")
                got_text = True

    except Exception as e:
        print(f"FAIL: Exception during SDK call: {type(e).__name__}: {e}")
        return 2

    if not got_text:
        print("FAIL: No text response received from Claude")
        return 3

    print()
    print("✓ PASS: Claude Agent SDK works on Max-subscription OAuth")
    if total_cost is not None:
        print(f"  This call cost: ${total_cost} (charged against Max quota, not API)")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
