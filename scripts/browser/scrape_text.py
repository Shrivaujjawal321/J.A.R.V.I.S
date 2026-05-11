#!/usr/bin/env python3
"""
scrape_text.py — Extract clean text content from a URL.

Strips nav, footer, scripts, styles. Useful for reading blog posts,
job descriptions, form fields, article content.

Usage:
    python scrape_text.py --url <url> [--selector <css>] [--headed]

Args:
    --url        URL to scrape (required)
    --selector   CSS selector to target (default: smart main-content detection)
    --headed     Run with visible browser

Output:
    Clean text to stdout.

Exit codes:
    0 — success
    1 — error
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

TIMEOUT_MS = 30_000

# JS to extract clean readable text — strips noise elements
EXTRACT_TEXT_JS = """
(selector) => {
    // Remove noisy elements
    const noiseSelectors = [
        'script', 'style', 'noscript', 'iframe',
        'nav', 'footer', 'header',
        '[role="navigation"]', '[role="banner"]', '[role="contentinfo"]',
        '.cookie-banner', '.cookie-consent', '.ad', '.advertisement',
        '.sidebar', '.widget', '.popup', '.modal',
        '[class*="nav"]', '[class*="footer"]', '[class*="header"]',
        '[id*="nav"]', '[id*="footer"]', '[id*="header"]',
    ];

    // Work on a clone to avoid modifying the live DOM
    const clone = document.cloneNode(true);
    noiseSelectors.forEach(sel => {
        try {
            clone.querySelectorAll(sel).forEach(el => el.remove());
        } catch(e) {}
    });

    let target;
    if (selector) {
        target = clone.querySelector(selector);
        if (!target) {
            return { error: `Selector '${selector}' not found`, text: null, selector_used: selector };
        }
    } else {
        // Smart detection: prefer semantic main content elements
        const candidates = ['main', 'article', '[role="main"]', '.content', '#content', '.post', '#main'];
        for (const sel of candidates) {
            target = clone.querySelector(sel);
            if (target) break;
        }
        if (!target) {
            target = clone.body || clone.documentElement;
        }
    }

    // Get text, collapse whitespace
    let text = target.innerText || target.textContent || '';
    // Normalize: collapse multiple blank lines to max 2
    text = text.replace(/\\n{3,}/g, '\\n\\n').trim();

    return {
        error: null,
        text: text,
        selector_used: selector || 'auto-detected',
        char_count: text.length,
        word_count: text.split(/\\s+/).filter(w => w.length > 0).length,
    };
}
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract clean text from a URL")
    parser.add_argument("--url", required=True, help="URL to scrape")
    parser.add_argument(
        "--selector",
        default=None,
        help="CSS selector (optional). Default: auto-detect main content.",
    )
    parser.add_argument("--headed", action="store_true", help="Run with visible browser")
    args = parser.parse_args()

    from playwright.sync_api import sync_playwright, Error as PlaywrightError

    headless_args = ["--disable-webgl", "--disable-gpu"] if not args.headed else []

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=not args.headed, args=headless_args)
            context = browser.new_context(viewport={"width": 1440, "height": 900})
            page = context.new_page()

            page.goto(args.url, wait_until="domcontentloaded", timeout=TIMEOUT_MS)

            # Wait a moment for any JS-rendered content
            page.wait_for_timeout(1500)

            result = page.evaluate(EXTRACT_TEXT_JS, args.selector)
            browser.close()

    except PlaywrightError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"ERROR: Unexpected — {exc}", file=sys.stderr)
        return 1

    if result.get("error"):
        print(f"ERROR: {result['error']}", file=sys.stderr)
        return 1

    text = result.get("text", "")
    word_count = result.get("word_count", 0)
    char_count = result.get("char_count", 0)
    selector_used = result.get("selector_used", "unknown")

    # Print metadata header to stderr so stdout is clean text only
    print(f"[scrape_text] selector={selector_used}  words={word_count}  chars={char_count}", file=sys.stderr)

    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
