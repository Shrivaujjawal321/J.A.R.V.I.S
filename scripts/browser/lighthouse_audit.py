#!/usr/bin/env python3
"""
lighthouse_audit.py — Lite performance audit via Performance Observer JS injection.

LIMITATION: This is NOT real Lighthouse. Real Lighthouse requires Node.js + Chrome DevTools
Protocol in a specific configuration not easily replicated from Python. This script uses:
  - Playwright + Performance Observer API (injected JS) for FCP, LCP, CLS, TBT proxy
  - Resource Timing API for transfer sizes
  - Navigation Timing for load phases

For a v2 upgrade, run real Lighthouse via: `node --lighthouse-node-modules` subprocess.
That gives the canonical 0-100 score. See docs below.

Usage:
    python lighthouse_audit.py --url <url> [--headed]

Output:
    - Prints summary table to stdout
    - Saves metrics JSON to data/browser/audits/{slug}-{timestamp}.json

Exit codes:
    0 — success
    1 — error
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
AUDITS_DIR = REPO_ROOT / "data" / "browser" / "audits"
SCREENSHOTS_DIR = REPO_ROOT / "data" / "browser" / "screenshots"
TIMEOUT_MS = 30_000

# JS injected to collect perf metrics via Performance Observer + Navigation Timing
PERF_OBSERVER_JS = """
() => {
    return new Promise((resolve) => {
        const metrics = {
            fcp: null,
            lcp: null,
            cls: 0,
            tbt_proxy: 0,
            fid_proxy: null,
            navigation: {},
            resources: [],
        };

        // FCP
        const fcpObs = new PerformanceObserver((list) => {
            for (const entry of list.getEntries()) {
                if (entry.name === 'first-contentful-paint') {
                    metrics.fcp = Math.round(entry.startTime);
                }
            }
        });
        try { fcpObs.observe({ type: 'paint', buffered: true }); } catch(e) {}

        // LCP
        const lcpObs = new PerformanceObserver((list) => {
            const entries = list.getEntries();
            if (entries.length > 0) {
                metrics.lcp = Math.round(entries[entries.length - 1].startTime);
            }
        });
        try { lcpObs.observe({ type: 'largest-contentful-paint', buffered: true }); } catch(e) {}

        // CLS
        const clsObs = new PerformanceObserver((list) => {
            for (const entry of list.getEntries()) {
                if (!entry.hadRecentInput) {
                    metrics.cls += entry.value;
                }
            }
        });
        try { clsObs.observe({ type: 'layout-shift', buffered: true }); } catch(e) {}

        // Long Tasks (TBT proxy — sum of blocking time)
        const ltObs = new PerformanceObserver((list) => {
            for (const entry of list.getEntries()) {
                // TBT = time > 50ms per long task
                metrics.tbt_proxy += Math.max(0, entry.duration - 50);
            }
        });
        try { ltObs.observe({ type: 'longtask', buffered: true }); } catch(e) {}

        // Wait for page to settle, then collect Navigation + Resource Timing
        setTimeout(() => {
            // Navigation Timing
            const navEntries = performance.getEntriesByType('navigation');
            if (navEntries.length > 0) {
                const nav = navEntries[0];
                metrics.navigation = {
                    dns_ms: Math.round(nav.domainLookupEnd - nav.domainLookupStart),
                    connect_ms: Math.round(nav.connectEnd - nav.connectStart),
                    ttfb_ms: Math.round(nav.responseStart - nav.requestStart),
                    dom_content_loaded_ms: Math.round(nav.domContentLoadedEventEnd - nav.startTime),
                    load_event_ms: Math.round(nav.loadEventEnd - nav.startTime),
                    transfer_size_kb: Math.round(nav.transferSize / 1024),
                    decoded_body_size_kb: Math.round(nav.decodedBodySize / 1024),
                };
            }

            // Resource breakdown
            const resources = performance.getEntriesByType('resource');
            const breakdown = { script: 0, css: 0, img: 0, font: 0, fetch: 0, other: 0 };
            let totalTransfer = 0;
            resources.forEach(r => {
                const kb = Math.round((r.transferSize || 0) / 1024);
                totalTransfer += r.transferSize || 0;
                if (r.initiatorType in breakdown) {
                    breakdown[r.initiatorType] += kb;
                } else {
                    breakdown.other += kb;
                }
            });
            metrics.resources = {
                count: resources.length,
                total_transfer_kb: Math.round(totalTransfer / 1024),
                breakdown_kb: breakdown,
            };

            metrics.cls = Math.round(metrics.cls * 1000) / 1000;
            metrics.tbt_proxy = Math.round(metrics.tbt_proxy);

            resolve(metrics);
        }, 3000);  // 3s settle time for observers
    });
}
"""


def estimate_perf_score(fcp_ms: int | None, lcp_ms: int | None, cls: float, tbt: int) -> str:
    """
    Rough Lighthouse-style performance score estimate.
    NOT an official score — documented limitation. Based on public Lighthouse thresholds.
    """
    score = 100

    # FCP scoring (good <1.8s, needs improvement 1.8-3s, poor >3s)
    if fcp_ms is not None:
        if fcp_ms > 3000:
            score -= 25
        elif fcp_ms > 1800:
            score -= 12

    # LCP scoring (good <2.5s, needs improvement 2.5-4s, poor >4s)
    if lcp_ms is not None:
        if lcp_ms > 4000:
            score -= 30
        elif lcp_ms > 2500:
            score -= 15

    # CLS scoring (good <0.1, needs improvement 0.1-0.25, poor >0.25)
    if cls > 0.25:
        score -= 25
    elif cls > 0.1:
        score -= 10

    # TBT scoring (good <200ms, needs improvement 200-600ms, poor >600ms)
    if tbt > 600:
        score -= 20
    elif tbt > 200:
        score -= 10

    score = max(0, score)

    if score >= 90:
        return f"{score} (Good)"
    elif score >= 50:
        return f"{score} (Needs Improvement)"
    else:
        return f"{score} (Poor)"


def rating(value: float | None, good: float, poor: float, unit: str = "ms") -> str:
    """Return value with a Good/NI/Poor label."""
    if value is None:
        return "N/A"
    v = float(value)
    if v <= good:
        label = "Good"
    elif v <= poor:
        label = "Needs Improvement"
    else:
        label = "Poor"
    return f"{value}{unit}  [{label}]"


def main() -> int:
    parser = argparse.ArgumentParser(description="Lite performance audit (Performance Observer)")
    parser.add_argument("--url", required=True, help="URL to audit")
    parser.add_argument("--headed", action="store_true", help="Run with visible browser")
    args = parser.parse_args()

    AUDITS_DIR.mkdir(parents=True, exist_ok=True)
    SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

    from playwright.sync_api import sync_playwright, Error as PlaywrightError

    # Disable WebGL/GPU in headless to prevent screenshot render hangs
    headless_args = ["--disable-webgl", "--disable-gpu"] if not args.headed else []

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    slug = re.sub(r"https?://", "", args.url)
    slug = re.sub(r"[^\w\-]", "-", slug).strip("-")[:60]

    audit_path = AUDITS_DIR / f"{slug}-{timestamp}.json"
    screenshot_path = SCREENSHOTS_DIR / f"audit-{slug}-{timestamp}.png"

    print(f"Auditing: {args.url}")
    print("(Lite audit — Performance Observer + Navigation Timing, not real Lighthouse)\n")

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=not args.headed, args=headless_args)
            context = browser.new_context(viewport={"width": 1440, "height": 900})
            page = context.new_page()

            t0 = time.perf_counter()
            # Try networkidle first; fall back to domcontentloaded + wait
            # (Three.js / WebGL apps may never reach networkidle due to animation loops)
            try:
                page.goto(args.url, wait_until="networkidle", timeout=TIMEOUT_MS)
            except Exception:
                # Fallback: domcontentloaded is enough for Performance Observer
                page.goto(args.url, wait_until="domcontentloaded", timeout=TIMEOUT_MS)
                page.wait_for_timeout(3000)  # let resources settle
            load_time_ms = int((time.perf_counter() - t0) * 1000)

            # Run Performance Observer collection
            metrics = page.evaluate(PERF_OBSERVER_JS)

            # Screenshot for reference — fall back to viewport clip for WebGL/heavy pages
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
                        page.screenshot(
                            path=str(screenshot_path),
                            clip={"x": 0, "y": 0, "width": 1440, "height": 900},
                            animations="disabled",
                            timeout=15_000,
                        )
                    break
                except Exception:
                    if ss_attempt == "clip":
                        screenshot_path = None  # non-fatal
            browser.close()

    except PlaywrightError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"ERROR: Unexpected — {exc}", file=sys.stderr)
        return 1

    fcp = metrics.get("fcp")
    lcp = metrics.get("lcp")
    cls = metrics.get("cls", 0)
    tbt = metrics.get("tbt_proxy", 0)
    nav = metrics.get("navigation", {})
    resources = metrics.get("resources", {})

    perf_score = estimate_perf_score(fcp, lcp, cls, tbt)

    # Build full output record
    output = {
        "url": args.url,
        "timestamp": timestamp,
        "audit_type": "lite-performance-observer",
        "limitation": (
            "NOT real Lighthouse. Uses Performance Observer + Navigation Timing API. "
            "Perf score is an estimate only. Run real Lighthouse via Node.js for canonical scores."
        ),
        "perf_score_estimate": perf_score,
        "core_web_vitals": {
            "fcp_ms": fcp,
            "lcp_ms": lcp,
            "cls": cls,
            "tbt_proxy_ms": tbt,
        },
        "navigation_timing": nav,
        "resources": resources,
        "playwright_load_time_ms": load_time_ms,
        "screenshot": str(screenshot_path) if screenshot_path else None,
    }

    # Save JSON
    audit_path.write_text(json.dumps(output, indent=2))

    # Print summary table
    print("=" * 60)
    print(f"  LITE AUDIT: {args.url}")
    print("=" * 60)
    print(f"  Perf Score (estimate)  : {perf_score}")
    print(f"  FCP                    : {rating(fcp, 1800, 3000)}")
    print(f"  LCP                    : {rating(lcp, 2500, 4000)}")
    print(f"  CLS                    : {rating(cls, 0.1, 0.25, '')}")
    print(f"  TBT (proxy)            : {rating(tbt, 200, 600)}")
    print("-" * 60)
    print(f"  TTFB                   : {nav.get('ttfb_ms', 'N/A')}ms")
    print(f"  DOM Content Loaded     : {nav.get('dom_content_loaded_ms', 'N/A')}ms")
    print(f"  Load Event             : {nav.get('load_event_ms', 'N/A')}ms")
    print(f"  Playwright load time   : {load_time_ms}ms (networkidle)")
    print("-" * 60)
    print(f"  Resources (count)      : {resources.get('count', 'N/A')}")
    print(f"  Total transfer         : {resources.get('total_transfer_kb', 'N/A')} KB")
    breakdown = resources.get("breakdown_kb", {})
    for rtype, kb in breakdown.items():
        if kb > 0:
            print(f"    {rtype:<12}         : {kb} KB")
    print("=" * 60)
    print(f"\n  Audit saved : {audit_path}")
    print(f"  Screenshot  : {screenshot_path if screenshot_path else 'N/A (WebGL render timeout)'}")
    print()
    print("  NOTE: For canonical Lighthouse scores, install Node.js and run:")
    print("    npx lighthouse <url> --output=json --chrome-flags='--headless'")

    return 0


if __name__ == "__main__":
    sys.exit(main())
