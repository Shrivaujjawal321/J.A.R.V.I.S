#!/usr/bin/env python3
"""
test_login_flow.py — SAFETY-AWARE login form inspector.

SAFETY CONTRACT:
  - NEVER submits forms. Stops at fill step, never clicks submit.
  - NEVER persists real credentials. Uses placeholder text only.
  - NEVER stores any session cookies or auth tokens.
  - Clears all filled fields before closing browser.

Usage:
    python test_login_flow.py --url <url>
        [--username-selector <css>]
        [--password-selector <css>]
        [--submit-selector <css>]
        [--headed]

Output:
    Markdown report at data/browser/login-tests/{slug}-{timestamp}.md
    Screenshots at each step saved to data/browser/screenshots/

Exit codes:
    0 — success
    1 — error
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path
import re

REPO_ROOT = Path(__file__).resolve().parents[2]
SCREENSHOTS_DIR = REPO_ROOT / "data" / "browser" / "screenshots"
LOGIN_TESTS_DIR = REPO_ROOT / "data" / "browser" / "login-tests"
TIMEOUT_MS = 30_000

# Placeholder credentials — never real, never reused
PLACEHOLDER_USERNAME = "test_user_placeholder@example.com"
PLACEHOLDER_PASSWORD = "***PLACEHOLDER_NEVER_REAL***"

# Blocked domains — refuse to test on financial/sensitive sites
BLOCKED_DOMAIN_PATTERNS = [
    r"bank", r"paypal", r"stripe", r"coinbase", r"robinhood",
    r"fidelity", r"schwab", r"vanguard", r"chase", r"wellsfargo",
    r"gmail", r"google\.com", r"facebook\.com", r"apple\.com",
    r"amazon\.com", r"twitter\.com", r"x\.com",
    r"gov\.", r"\.gov",
]


def slugify(url: str) -> str:
    url = re.sub(r"https?://", "", url)
    url = re.sub(r"[^\w\-]", "-", url)
    return url.strip("-")[:60]


def is_blocked_domain(url: str) -> str | None:
    """Return matched pattern if URL is on a blocked domain, else None."""
    url_lower = url.lower()
    for pattern in BLOCKED_DOMAIN_PATTERNS:
        if re.search(pattern, url_lower):
            return pattern
    return None


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Safety-aware login form inspector (NEVER submits)"
    )
    parser.add_argument("--url", required=True, help="URL containing login form")
    parser.add_argument(
        "--username-selector",
        default=None,
        help="CSS selector for username/email field (auto-detected if not provided)",
    )
    parser.add_argument(
        "--password-selector",
        default=None,
        help="CSS selector for password field (auto-detected if not provided)",
    )
    parser.add_argument(
        "--submit-selector",
        default=None,
        help="CSS selector for submit button (only inspected, NEVER clicked)",
    )
    parser.add_argument("--headed", action="store_true", help="Run with visible browser")
    args = parser.parse_args()

    # Safety check: refuse blocked domains
    blocked = is_blocked_domain(args.url)
    if blocked:
        print(
            f"REFUSED: URL matches blocked domain pattern '{blocked}'.\n"
            f"This tool WILL NOT test login flows on financial, major social, or government sites.\n"
            f"Boss should handle this manually.",
            file=sys.stderr,
        )
        return 1

    LOGIN_TESTS_DIR.mkdir(parents=True, exist_ok=True)
    SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

    from playwright.sync_api import sync_playwright, Error as PlaywrightError

    headless_args = ["--disable-webgl", "--disable-gpu"] if not args.headed else []

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    slug = slugify(args.url)
    report_path = LOGIN_TESTS_DIR / f"{slug}-{timestamp}.md"

    console_errors: list[str] = []
    steps: list[dict] = []
    report_lines: list[str] = []

    def add_step(name: str, status: str, detail: str, screenshot: str | None = None):
        steps.append({"name": name, "status": status, "detail": detail, "screenshot": screenshot})

    def screenshot_step(page, label: str) -> str:
        path = SCREENSHOTS_DIR / f"login-{slug}-{label}-{timestamp}.png"
        page.screenshot(path=str(path))
        return str(path)

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=not args.headed, args=headless_args)
            context = browser.new_context(
                viewport={"width": 1440, "height": 900},
                # No storage state — fresh context, no cookies persisted
            )
            page = context.new_page()

            # Collect console errors
            page.on(
                "console",
                lambda msg: console_errors.append(f"[{msg.type}] {msg.text}")
                if msg.type in ("error", "warning")
                else None,
            )

            # Step 1: Navigate
            try:
                page.goto(args.url, wait_until="networkidle", timeout=TIMEOUT_MS)
                ss = screenshot_step(page, "01-loaded")
                add_step("Page Load", "PASS", f"Loaded: {page.url}", ss)
            except PlaywrightError as exc:
                add_step("Page Load", "FAIL", str(exc))
                raise

            # Step 2: Detect / locate username field
            username_sel = args.username_selector
            if not username_sel:
                # Auto-detect common patterns
                candidates = [
                    'input[type="email"]',
                    'input[name="email"]',
                    'input[name="username"]',
                    'input[name="user"]',
                    'input[name="login"]',
                    'input[autocomplete="username"]',
                    'input[autocomplete="email"]',
                ]
                for candidate in candidates:
                    try:
                        if page.locator(candidate).count() > 0:
                            username_sel = candidate
                            break
                    except Exception:
                        continue

            if username_sel:
                try:
                    page.fill(username_sel, PLACEHOLDER_USERNAME, timeout=5000)
                    ss = screenshot_step(page, "02-username-filled")
                    add_step("Username Field", "PASS", f"Selector: {username_sel} — filled with placeholder", ss)
                except PlaywrightError as exc:
                    add_step("Username Field", "FAIL", f"Selector: {username_sel} — {exc}")
            else:
                add_step("Username Field", "WARN", "Could not auto-detect username field. Provide --username-selector.")

            # Step 3: Detect / locate password field
            password_sel = args.password_selector
            if not password_sel:
                candidates = [
                    'input[type="password"]',
                    'input[name="password"]',
                    'input[name="pass"]',
                    'input[autocomplete="current-password"]',
                ]
                for candidate in candidates:
                    try:
                        if page.locator(candidate).count() > 0:
                            password_sel = candidate
                            break
                    except Exception:
                        continue

            if password_sel:
                try:
                    page.fill(password_sel, PLACEHOLDER_PASSWORD, timeout=5000)
                    ss = screenshot_step(page, "03-password-filled")
                    add_step("Password Field", "PASS", f"Selector: {password_sel} — filled with placeholder", ss)
                except PlaywrightError as exc:
                    add_step("Password Field", "FAIL", f"Selector: {password_sel} — {exc}")
            else:
                add_step("Password Field", "WARN", "Could not auto-detect password field. Provide --password-selector.")

            # Step 4: Inspect submit button (DO NOT CLICK)
            submit_sel = args.submit_selector
            if not submit_sel:
                candidates = [
                    'button[type="submit"]',
                    'input[type="submit"]',
                    'button:has-text("Sign in")',
                    'button:has-text("Log in")',
                    'button:has-text("Login")',
                    'button:has-text("Continue")',
                ]
                for candidate in candidates:
                    try:
                        if page.locator(candidate).count() > 0:
                            submit_sel = candidate
                            break
                    except Exception:
                        continue

            if submit_sel:
                try:
                    locator = page.locator(submit_sel).first
                    is_visible = locator.is_visible(timeout=3000)
                    is_enabled = locator.is_enabled(timeout=3000)
                    btn_text = locator.text_content(timeout=3000) or ""
                    ss = screenshot_step(page, "04-submit-inspected")
                    add_step(
                        "Submit Button (INSPECT ONLY — NOT CLICKED)",
                        "PASS" if is_visible and is_enabled else "WARN",
                        f"Selector: {submit_sel}  visible={is_visible}  enabled={is_enabled}  text='{btn_text.strip()}'",
                        ss,
                    )
                except PlaywrightError as exc:
                    add_step("Submit Button", "FAIL", f"Selector: {submit_sel} — {exc}")
            else:
                add_step("Submit Button", "WARN", "Could not detect submit button. Provide --submit-selector.")

            # SAFETY: Clear filled fields before closing
            if username_sel:
                try:
                    page.fill(username_sel, "", timeout=3000)
                except Exception:
                    pass
            if password_sel:
                try:
                    page.fill(password_sel, "", timeout=3000)
                except Exception:
                    pass

            browser.close()

    except PlaywrightError as exc:
        # Non-fatal if we already recorded steps
        if not steps:
            print(f"ERROR: {exc}", file=sys.stderr)
            return 1

    # Build markdown report
    report_lines.append(f"# Login Flow Test Report")
    report_lines.append(f"")
    report_lines.append(f"**URL:** {args.url}")
    report_lines.append(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append(f"**Safety Contract:** NEVER submitted form. Placeholder credentials only. No session persisted.")
    report_lines.append(f"")
    report_lines.append(f"## Steps")
    report_lines.append(f"")

    for step in steps:
        icon = {"PASS": "PASS", "FAIL": "FAIL", "WARN": "WARN"}.get(step["status"], step["status"])
        report_lines.append(f"### [{icon}] {step['name']}")
        report_lines.append(f"{step['detail']}")
        if step.get("screenshot"):
            report_lines.append(f"Screenshot: `{step['screenshot']}`")
        report_lines.append(f"")

    if console_errors:
        report_lines.append(f"## Console Errors / Warnings")
        report_lines.append(f"")
        for err in console_errors:
            report_lines.append(f"- `{err}`")
        report_lines.append(f"")

    report_lines.append(f"## Summary")
    passed = sum(1 for s in steps if s["status"] == "PASS")
    failed = sum(1 for s in steps if s["status"] == "FAIL")
    warned = sum(1 for s in steps if s["status"] == "WARN")
    report_lines.append(f"- PASS: {passed}")
    report_lines.append(f"- FAIL: {failed}")
    report_lines.append(f"- WARN: {warned}")
    report_lines.append(f"- Console errors/warnings: {len(console_errors)}")

    report_content = "\n".join(report_lines)
    report_path.write_text(report_content)

    print(report_content)
    print(f"\n---\nReport saved: {report_path}")
    return 0 if not any(s["status"] == "FAIL" for s in steps) else 1


if __name__ == "__main__":
    sys.exit(main())
