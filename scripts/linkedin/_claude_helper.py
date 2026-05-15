"""
Thin wrapper around `claude -p` subprocess calls.

Used by all LinkedIn pipeline drafters/orchestrators to invoke Claude Code
in headless mode. Reuses Boss's OAuth subscription — no API key needed.

Two modes:
  - text(prompt)  -> str             one-shot text generation
  - json(prompt)  -> dict            asks Claude to reply with strict JSON
  - tools(prompt) -> str             allows tool use (Bash, Read, Write, MCP)

Why subprocess instead of jarvis-core HTTP:
  - Cron-driven scripts must work even if daemon is down.
  - Each LinkedIn batch is short-lived — no need for persistent session.
  - Telegram bridge already has the daemon path; this is the offline fallback.
"""
from __future__ import annotations

import asyncio
import json
import os
import re
import subprocess
from pathlib import Path

JARVIS_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_TIMEOUT = int(os.getenv("LP_CLAUDE_TIMEOUT", "180"))
DEFAULT_MAX_TURNS = int(os.getenv("LP_CLAUDE_MAX_TURNS", "8"))


def _run_claude(
    prompt: str,
    *,
    timeout: int = DEFAULT_TIMEOUT,
    max_turns: int = DEFAULT_MAX_TURNS,
    allow_tools: bool = False,
    output_format: str = "text",
) -> str:
    cmd = [
        "claude",
        "-p", prompt,
        "--output-format", output_format,
        "--max-turns", str(max_turns),
        "--permission-mode", "bypassPermissions",
    ]
    if not allow_tools:
        cmd.extend(["--disallowed-tools", "Bash,Edit,Write,WebFetch,WebSearch"])

    try:
        proc = subprocess.run(
            cmd,
            cwd=str(JARVIS_ROOT),
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired:
        raise RuntimeError(f"claude -p timed out after {timeout}s")

    if proc.returncode != 0:
        raise RuntimeError(
            f"claude -p exited {proc.returncode}: {proc.stderr.strip()[:500]}"
        )

    return proc.stdout


def text(prompt: str, **kwargs) -> str:
    """Plain text completion."""
    out = _run_claude(prompt, output_format="text", **kwargs)
    return out.strip()


def json_call(prompt: str, **kwargs) -> dict | list:
    """
    Asks Claude to reply with strict JSON (one object/array, no prose).
    Tolerates ```json fences. Raises on parse failure with the raw output.
    """
    enforced = (
        prompt
        + "\n\n---\n"
        + "Reply with ONLY valid JSON. No prose, no preamble, no fences. "
        + "Single object or array as instructed above."
    )
    out = _run_claude(enforced, output_format="text", **kwargs).strip()

    fenced = re.search(r"```(?:json)?\s*(.+?)\s*```", out, re.DOTALL)
    raw = fenced.group(1) if fenced else out

    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        raise RuntimeError(
            f"claude returned invalid JSON: {e}\n--- raw ---\n{out[:1500]}"
        )


def with_tools(prompt: str, **kwargs) -> str:
    """
    Run a Claude prompt that's allowed to use tools (browser MCP, file writes, etc.).
    Used by executor.py to drive Chrome.
    """
    return _run_claude(prompt, allow_tools=True, **kwargs).strip()


if __name__ == "__main__":
    print(text("Reply with one short sentence to confirm Claude headless works."))
