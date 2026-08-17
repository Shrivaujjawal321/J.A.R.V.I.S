"""
backend/sources/brightdata.py
==============================
BrightData MCP subprocess wrapper.

Manages a long-lived `npx -y @brightdata/mcp` child process over stdin/stdout
JSON-RPC 2.0. Each per-tool coroutine sends a request and awaits the response.

Architecture
------------
- ONE subprocess per Python process (module-level singleton via asyncio.Lock +
  lazy init). Avoids npx startup overhead (~1.5s) per request.
- Re-spawns automatically if the process crashes or exits.
- Degraded mode: if BRIGHT_DATA_API_KEY is not set, every tool returns a
  BrightDataError with status BLOCKED so upstream sources return gracefully.
- Per-call timeout: 25s (BrightData web_data_* tools poll up to 20s internally).

Environment variables
---------------------
    BRIGHT_DATA_API_KEY   (required for live calls)
    BD_GROUPS             comma-separated tool groups (default: social,finance,business,research)
    BD_MAX_RETRIES        int, default 1
    BD_CALL_TIMEOUT       float seconds, default 25.0

JSON-RPC 2.0 over stdio
------------------------
The MCP server reads newline-delimited JSON from stdin and writes newline-
delimited JSON to stdout. Each request has a unique `id`; responses include
that id for matching.

Request format:
    {"jsonrpc": "2.0", "id": "1", "method": "tools/call",
     "params": {"name": "<tool>", "arguments": {...}}}

Response format (success):
    {"jsonrpc": "2.0", "id": "1",
     "result": {"content": [{"type": "text", "text": "..."}]}}

Response format (error):
    {"jsonrpc": "2.0", "id": "1",
     "error": {"code": -32600, "message": "..."}}
"""
from __future__ import annotations

import asyncio
import json
import logging
import os
import time
from contextlib import asynccontextmanager
from typing import Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
_API_KEY: str = os.getenv("BRIGHT_DATA_API_KEY", "")
_GROUPS: str = os.getenv("BD_GROUPS", "social,finance,business,research")
_MAX_RETRIES: int = int(os.getenv("BD_MAX_RETRIES", "1"))
_CALL_TIMEOUT: float = float(os.getenv("BD_CALL_TIMEOUT", "25.0"))

_DEGRADED = not _API_KEY  # no key → all calls return BLOCKED gracefully


# ---------------------------------------------------------------------------
# Custom exception
# ---------------------------------------------------------------------------

class BrightDataError(Exception):
    """Raised when BrightData MCP returns an error or is unavailable."""

    def __init__(self, message: str, code: int = -1) -> None:
        super().__init__(message)
        self.code = code


# ---------------------------------------------------------------------------
# Subprocess manager (singleton)
# ---------------------------------------------------------------------------

class _MCPProcess:
    """
    Singleton wrapper around the `npx @brightdata/mcp` subprocess.
    Thread-safe via asyncio.Lock.
    """

    def __init__(self) -> None:
        self._proc: asyncio.subprocess.Process | None = None
        self._lock = asyncio.Lock()
        self._request_id = 0
        self._pending: dict[str, asyncio.Future[dict]] = {}
        self._reader_task: asyncio.Task | None = None

    async def _start(self) -> None:
        """Spawn the npx process. Called under self._lock."""
        env = {
            **os.environ,
            "API_TOKEN": _API_KEY,
            "GROUPS": _GROUPS,
            "BASE_MAX_RETRIES": str(_MAX_RETRIES),
            "BASE_TIMEOUT": "22",  # slightly under our per-call timeout
        }
        logger.info("Starting BrightData MCP subprocess")
        self._proc = await asyncio.create_subprocess_exec(
            "npx", "-y", "@brightdata/mcp",
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=env,
        )
        # Send MCP initialize handshake
        await self._send_raw({
            "jsonrpc": "2.0",
            "id": "init",
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "clientInfo": {"name": "altbrief", "version": "1.0.0"},
                "capabilities": {},
            },
        })
        # Start background reader
        self._reader_task = asyncio.create_task(self._read_loop(), name="bd-reader")
        # Wait briefly for init response
        await asyncio.sleep(0.5)
        logger.info("BrightData MCP process started (pid=%s)", self._proc.pid)

    async def _send_raw(self, payload: dict) -> None:
        """Write a newline-delimited JSON message to stdin."""
        if not self._proc or not self._proc.stdin:
            raise BrightDataError("MCP process not running")
        line = json.dumps(payload) + "\n"
        self._proc.stdin.write(line.encode())
        await self._proc.stdin.drain()

    async def _read_loop(self) -> None:
        """Background coroutine: reads stdout lines and resolves pending futures."""
        if not self._proc or not self._proc.stdout:
            return
        try:
            while True:
                line = await self._proc.stdout.readline()
                if not line:
                    break  # process exited
                try:
                    msg = json.loads(line.decode().strip())
                except json.JSONDecodeError:
                    continue

                msg_id = str(msg.get("id", ""))
                fut = self._pending.pop(msg_id, None)
                if fut and not fut.done():
                    fut.set_result(msg)
        except Exception as exc:
            logger.error("BrightData reader loop crashed: %s", exc)
            # Mark all pending futures as errored
            for fut in self._pending.values():
                if not fut.done():
                    fut.set_exception(BrightDataError(f"Reader crashed: {exc}"))
            self._pending.clear()

    async def _ensure_running(self) -> None:
        """Start the process if it's not running. Re-entrant safe via lock."""
        async with self._lock:
            if self._proc is None or self._proc.returncode is not None:
                # Process died — cancel old reader, restart
                if self._reader_task and not self._reader_task.done():
                    self._reader_task.cancel()
                await self._start()

    async def call_tool(self, tool_name: str, arguments: dict) -> dict:
        """
        Call a BrightData MCP tool and return the parsed result dict.

        Returns a dict with key 'text' for text results.
        Raises BrightDataError on tool error or timeout.
        """
        if _DEGRADED:
            raise BrightDataError(
                "BRIGHT_DATA_API_KEY not set — running in degraded mode",
                code=0,
            )

        await self._ensure_running()

        self._request_id += 1
        req_id = str(self._request_id)

        loop = asyncio.get_event_loop()
        fut: asyncio.Future[dict] = loop.create_future()
        self._pending[req_id] = fut

        payload = {
            "jsonrpc": "2.0",
            "id": req_id,
            "method": "tools/call",
            "params": {"name": tool_name, "arguments": arguments},
        }

        try:
            await self._send_raw(payload)
        except Exception as exc:
            self._pending.pop(req_id, None)
            raise BrightDataError(f"Failed to send request: {exc}")

        try:
            response = await asyncio.wait_for(fut, timeout=_CALL_TIMEOUT)
        except asyncio.TimeoutError:
            self._pending.pop(req_id, None)
            raise BrightDataError(
                f"Tool '{tool_name}' timed out after {_CALL_TIMEOUT}s",
                code=-32000,
            )

        # Parse JSON-RPC response
        if "error" in response:
            err = response["error"]
            raise BrightDataError(
                err.get("message", "Unknown error"),
                code=err.get("code", -1),
            )

        # Extract text content from result
        result = response.get("result", {})
        content = result.get("content", [])
        for block in content:
            if block.get("type") == "text":
                return {"text": block["text"]}

        # If no text block found, return raw result
        return {"raw": result}

    async def shutdown(self) -> None:
        """Gracefully terminate the subprocess."""
        if self._reader_task and not self._reader_task.done():
            self._reader_task.cancel()
        if self._proc and self._proc.returncode is None:
            try:
                self._proc.terminate()
                await asyncio.wait_for(self._proc.wait(), timeout=3.0)
            except Exception:
                self._proc.kill()
        self._proc = None


# Module-level singleton — initialized lazily on first call
_mcp: _MCPProcess | None = None
_mcp_lock = asyncio.Lock()


async def _get_mcp() -> _MCPProcess:
    global _mcp
    async with _mcp_lock:
        if _mcp is None:
            _mcp = _MCPProcess()
    return _mcp


async def shutdown_mcp() -> None:
    """Call during FastAPI lifespan shutdown to clean up the subprocess."""
    global _mcp
    if _mcp is not None:
        await _mcp.shutdown()
        _mcp = None


# ---------------------------------------------------------------------------
# Per-tool public methods (used by reddit.py, linkedin.py, glassdoor.py, news.py)
# ---------------------------------------------------------------------------

async def search_engine(query: str, engine: str = "google") -> str:
    """
    SERP search. Returns markdown-formatted results.
    Tool: search_engine (free tier)
    """
    mcp = await _get_mcp()
    result = await mcp.call_tool("search_engine", {"query": query, "engine": engine})
    return result.get("text", "")


async def scrape_as_markdown(url: str) -> str:
    """
    Scrape a URL to clean Markdown. Handles CAPTCHA + bot protection.
    Tool: scrape_as_markdown (free tier)
    """
    mcp = await _get_mcp()
    result = await mcp.call_tool("scrape_as_markdown", {"url": url})
    return result.get("text", "")


async def web_data_reddit_posts(
    query: str, subreddits: list[str] | None = None, limit: int = 20
) -> str:
    """
    Structured Reddit post data.
    Tool: web_data_reddit_posts (social group)
    """
    mcp = await _get_mcp()
    args: dict[str, Any] = {"query": query, "limit": limit}
    if subreddits:
        args["subreddits"] = subreddits
    result = await mcp.call_tool("web_data_reddit_posts", args)
    return result.get("text", "")


async def web_data_linkedin_company_profile(url: str) -> str:
    """
    Structured LinkedIn company data: headcount, description, follower count.
    Tool: web_data_linkedin_company_profile (social group)
    """
    mcp = await _get_mcp()
    result = await mcp.call_tool("web_data_linkedin_company_profile", {"url": url})
    return result.get("text", "")


async def web_data_linkedin_job_listings(company_name: str, limit: int = 25) -> str:
    """
    Active job listings for a company.
    Tool: web_data_linkedin_job_listings (social group)
    """
    mcp = await _get_mcp()
    result = await mcp.call_tool(
        "web_data_linkedin_job_listings",
        {"keyword": company_name, "limit": limit},
    )
    return result.get("text", "")


async def web_data_reuter_news(query: str, limit: int = 10) -> str:
    """
    Structured Reuters news articles.
    Tool: web_data_reuter_news (research group)
    """
    mcp = await _get_mcp()
    result = await mcp.call_tool("web_data_reuter_news", {"query": query, "limit": limit})
    return result.get("text", "")


async def scrape_glassdoor(company_name: str, ticker: str) -> str:
    """
    Glassdoor reviews via scrape_as_markdown (no native BD tool for Glassdoor).
    Falls back to search + scrape pattern.
    """
    mcp = await _get_mcp()
    # First: search for the Glassdoor page
    search_result = await mcp.call_tool(
        "search_engine",
        {"query": f"site:glassdoor.com {company_name} reviews ratings", "engine": "google"},
    )
    search_text = search_result.get("text", "")

    # Extract first Glassdoor URL from search results
    glassdoor_url: str | None = None
    for line in search_text.split("\n"):
        if "glassdoor.com" in line and ("overview" in line or "reviews" in line):
            # Try to extract URL from markdown link or plain text
            import re
            m = re.search(r'https?://[^\s\)\"]+glassdoor\.com[^\s\)\"]+', line)
            if m:
                glassdoor_url = m.group(0).rstrip(".,)")
                break

    if not glassdoor_url:
        glassdoor_url = f"https://www.glassdoor.com/Search/results.htm?keyword={company_name}"

    # Scrape the Glassdoor page
    scrape_result = await mcp.call_tool("scrape_as_markdown", {"url": glassdoor_url})
    return scrape_result.get("text", "")
