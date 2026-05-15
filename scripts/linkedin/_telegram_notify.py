"""
Outbound Telegram notifier for the LinkedIn pipeline.

The Telegram bridge handles INCOMING messages. This module sends OUTGOING ones
(morning batch for approval, nightly report, error alerts).

Reads TELEGRAM_BOT_TOKEN + ALLOWED_USER_IDS from .env (same as bridge).
Retries 3x on network errors with exponential backoff.
"""
from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Iterable

import httpx
from dotenv import load_dotenv

JARVIS_ROOT = Path(__file__).resolve().parents[2]
# bridge/.env holds TELEGRAM_BOT_TOKEN by convention; load both, bridge wins
load_dotenv(JARVIS_ROOT / ".env")
load_dotenv(JARVIS_ROOT / "bridge" / ".env", override=True)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ALLOWED_USER_IDS = [
    int(x) for x in os.getenv("ALLOWED_USER_IDS", "").split(",") if x.strip()
]
TELEGRAM_API = "https://api.telegram.org"
MAX_LEN = 4000  # Telegram limit is 4096; leave headroom for markdown


def _chunks(text: str, size: int = MAX_LEN) -> Iterable[str]:
    """Split long messages on paragraph/line boundaries to stay under limit."""
    if len(text) <= size:
        yield text
        return
    buf: list[str] = []
    cur = 0
    for line in text.splitlines(keepends=True):
        if cur + len(line) > size and buf:
            yield "".join(buf)
            buf, cur = [line], len(line)
        else:
            buf.append(line)
            cur += len(line)
    if buf:
        yield "".join(buf)


def send(text: str, *, parse_mode: str = "Markdown", silent: bool = False) -> list[dict]:
    """
    Send `text` to all ALLOWED_USER_IDS. Returns list of Telegram API responses.
    Splits into chunks if over 4000 chars.
    """
    if not TELEGRAM_BOT_TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN not set in .env")
    if not ALLOWED_USER_IDS:
        raise RuntimeError("ALLOWED_USER_IDS empty — nobody to notify")

    url = f"{TELEGRAM_API}/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    responses = []
    with httpx.Client(timeout=30) as client:
        for chunk in _chunks(text):
            for uid in ALLOWED_USER_IDS:
                payload: dict = {
                    "chat_id": uid,
                    "text": chunk,
                    "disable_notification": silent,
                    "disable_web_page_preview": True,
                }
                if parse_mode:
                    payload["parse_mode"] = parse_mode
                resp = _post_with_retry(client, url, payload)
                if not resp.get("ok") and "parse" in str(resp.get("description", "")).lower():
                    payload.pop("parse_mode", None)
                    resp = _post_with_retry(client, url, payload)
                responses.append(resp)
    return responses


def _post_with_retry(client: httpx.Client, url: str, payload: dict, *, attempts: int = 4) -> dict:
    """Retry on transient network errors. Returns last response or error dict."""
    last_err = None
    for i in range(attempts):
        try:
            r = client.post(url, json=payload)
            return r.json()
        except (httpx.ConnectError, httpx.ReadTimeout, httpx.RemoteProtocolError) as e:
            last_err = e
            if i < attempts - 1:
                time.sleep(2 ** i)  # 1s, 2s, 4s
    return {"ok": False, "description": f"network: {last_err}"}


def safe_send(text: str, **kwargs) -> bool:
    """Like send() but never raises. Returns True if at least one message landed."""
    try:
        results = send(text, **kwargs)
        return any(r.get("ok") for r in results)
    except Exception as e:
        print(f"[telegram_notify] safe_send swallowed: {e}")
        return False


def send_silent(text: str, **kwargs) -> list[dict]:
    return send(text, silent=True, **kwargs)


if __name__ == "__main__":
    print(send("LinkedIn pipeline notify test ✅"))
