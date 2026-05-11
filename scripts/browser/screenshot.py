#!/usr/bin/env python3
"""
screenshot.py — Capture a full-page or clipped screenshot of any URL.

Usage:
    python screenshot.py --url <url> [--full-page] [--viewport WxH] [--mobile] [--headed]

Output:
    Prints saved path to stdout.

Screenshot saved to:
    data/browser/screenshots/{slug}-{timestamp}.png

Exit codes:
    0 — success
    1 — error
"""

from __future__ import annotations

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCREENSHOTS_DIR = REPO_ROOT / "data" / "browser" / "screenshots"
TIMEOUT_MS = 30_000


def slugify(url: str) -> str:
    url = re.sub(r"https?://", "", url)
    url = re.sub(r"[^\w\-]", "-", url)
    return url.strip("-")[:60]


def parse_viewport(spec: str) -> dict[str, int]:
    """Parse 'WxH' string into {'width': W, 'height': H}."""
    try:
        w, h = spec.lower().split("x")
        return {"width": int(w), "height": int(h)}
    except Exception:
        raise ValueError(f"Invalid viewport spec '{spec}'. Use format WxH e.g. 1440x900")


def main() -> int:
    parser = argparse.ArgumentParser(description="Full-page screenshot of a URL")
    parser.add_argument("--url", required=True, help="URL to screenshot")
    parser.add_argument(
        "--full-page",
        action="store_true",
        default=True,
        help="Capture full scrollable page (default: true)",
    )
    parser.add_argument(
        "--no-full-page",
        dest="full_page",
        action="store_false",
        help="Capture only visible viewport",
    )
    parser.add_argument(
        "--viewport",
        default=None,
        help="Viewport size as WxH (e.g. 1440x900). Overrides --mobile.",
    )
    parser.add_argument(
        "--mobile",
        action="store_true",
        help="Use iPhone-sized viewport (390x844) with mobile UA",
    )
    parser.add_argument("--headed", action="store_true", help="Run with visible browser")
    args = parser.parse_args()

    SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

    from playwright.sync_api import sync_playwright, Error as PlaywrightError

    # Disable WebGL/GPU in headless mode to prevent screenshot render hangs
    headless_args = ["--disable-webgl", "--disable-gpu"] if not args.headed else []

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    slug = slugify(args.url)
    suffix = "-mobile" if args.mobile else ""
    screenshot_path = SCREENSHOTS_DIR / f"{slug}{suffix}-{timestamp}.png"

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=not args.headed, args=headless_args)

            context_kwargs: dict = {}

            if args.viewport:
                context_kwargs["viewport"] = parse_viewport(args.viewport)
            elif args.mobile:
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

            page.goto(args.url, wait_until="networkidle", timeout=TIMEOUT_MS)

            page.screenshot(
                path=str(screenshot_path),
                full_page=args.full_page,
                animations="disabled",
                timeout=25_000,
            )
            browser.close()

    except PlaywrightError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"ERROR: Unexpected — {exc}", file=sys.stderr)
        return 1

    print(str(screenshot_path))
    return 0


if __name__ == "__main__":
    sys.exit(main())
