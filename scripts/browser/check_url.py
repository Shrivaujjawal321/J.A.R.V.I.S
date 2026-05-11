#!/usr/bin/env python3
"""
check_url.py — Health check + screenshot for a URL.

Usage:
    python check_url.py --url <url> [--mobile] [--headed]

Output:
    JSON to stdout with keys:
        url, status, load_time_ms, title, page_size_kb,
        console_errors, failed_requests, final_url

Screenshot saved to:
    data/browser/screenshots/check-{slug}-{timestamp}.png

Exit codes:
    0 — success
    1 — error (page failed to load, timeout, etc.)
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCREENSHOTS_DIR = REPO_ROOT / "data" / "browser" / "screenshots"
TIMEOUT_MS = 30_000
OVERALL_TIMEOUT = 60  # seconds — watchdog


def slugify(url: str) -> str:
    """Turn a URL into a safe filename fragment."""
    url = re.sub(r"https?://", "", url)
    url = re.sub(r"[^\w\-]", "-", url)
    return url.strip("-")[:60]


def main() -> int:
    parser = argparse.ArgumentParser(description="URL health check with screenshot")
    parser.add_argument("--url", required=True, help="URL to check")
    parser.add_argument("--mobile", action="store_true", help="Use mobile viewport")
    parser.add_argument("--headed", action="store_true", help="Run with visible browser")
    args = parser.parse_args()

    SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

    from playwright.sync_api import sync_playwright, Error as PlaywrightError

    # Headless chromium args: disable WebGL/GPU to prevent screenshot hangs on
    # Three.js / WebGL-heavy pages (Linux headless has no real GPU anyway)
    headless_args = ["--disable-webgl", "--disable-gpu"] if not args.headed else []

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    slug = slugify(args.url)
    screenshot_path = SCREENSHOTS_DIR / f"check-{slug}-{timestamp}.png"

    console_errors: list[str] = []
    failed_requests: list[str] = []
    result: dict = {
        "url": args.url,
        "status": None,
        "load_time_ms": None,
        "title": None,
        "page_size_kb": None,
        "console_errors": console_errors,
        "failed_requests": failed_requests,
        "final_url": None,
        "screenshot": None,
        "error": None,
    }

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=not args.headed, args=headless_args)

            context_kwargs: dict = {}
            if args.mobile:
                context_kwargs["viewport"] = {"width": 390, "height": 844}
                context_kwargs["user_agent"] = (
                    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
                    "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 "
                    "Mobile/15E148 Safari/604.1"
                )
            else:
                context_kwargs["viewport"] = {"width": 1440, "height": 900}

            context = browser.new_context(**context_kwargs)
            page = context.new_page()

            # Capture console errors
            page.on(
                "console",
                lambda msg: console_errors.append(f"[{msg.type}] {msg.text}")
                if msg.type in ("error", "warning")
                else None,
            )

            # Capture failed network requests
            page.on(
                "requestfailed",
                lambda req: failed_requests.append(
                    f"{req.method} {req.url} — {req.failure}"
                ),
            )

            total_bytes = 0

            def on_response(response):
                nonlocal total_bytes
                try:
                    # Only count document/script/style/image
                    headers = response.headers
                    content_length = headers.get("content-length", "0")
                    total_bytes += int(content_length) if content_length.isdigit() else 0
                except Exception:
                    pass

            page.on("response", on_response)

            t0 = time.perf_counter()
            # Try networkidle; fall back to domcontentloaded for WebGL/animation-heavy pages
            try:
                response = page.goto(args.url, wait_until="networkidle", timeout=TIMEOUT_MS)
            except Exception:
                response = page.goto(args.url, wait_until="domcontentloaded", timeout=TIMEOUT_MS)
                page.wait_for_timeout(2000)
            load_time_ms = int((time.perf_counter() - t0) * 1000)

            result["status"] = response.status if response else None
            result["load_time_ms"] = load_time_ms
            result["title"] = page.title()
            result["page_size_kb"] = round(total_bytes / 1024, 1)
            result["final_url"] = page.url

            # Screenshot — try full-page first, fall back to viewport clip
            # Heavy WebGL/Three.js pages can hang screenshot; clip is a reliable fallback
            for ss_attempt in ("full_page", "clip"):
                try:
                    if ss_attempt == "full_page":
                        page.screenshot(
                            path=str(screenshot_path),
                            full_page=True,
                            animations="disabled",
                            timeout=15_000,
                        )
                    else:
                        # Clip to visible viewport — always works even on WebGL pages
                        vp = context_kwargs.get("viewport", {"width": 1440, "height": 900})
                        page.screenshot(
                            path=str(screenshot_path),
                            clip={"x": 0, "y": 0, "width": vp["width"], "height": vp["height"]},
                            animations="disabled",
                            timeout=15_000,
                        )
                    result["screenshot"] = str(screenshot_path)
                    result["screenshot_method"] = ss_attempt
                    break
                except Exception as ss_exc:
                    if ss_attempt == "clip":
                        # Both attempts failed — non-fatal
                        result["screenshot"] = None
                        result["screenshot_error"] = str(ss_exc)

            browser.close()

    except PlaywrightError as exc:
        result["error"] = str(exc)
        print(json.dumps(result, indent=2))
        return 1
    except Exception as exc:
        result["error"] = f"Unexpected error: {exc}"
        print(json.dumps(result, indent=2))
        return 1

    # Exit 1 only if the page itself failed to load (no status)
    exit_code = 0 if result.get("status") is not None else 1
    print(json.dumps(result, indent=2))
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
