#!/usr/bin/env python3
"""
eval_baseline.py — Phase F of the self-growth loop.

Aggregates the most-recent per-agent eval reports into a single published
baseline at `data/evals/baseline.md`. With `--check`, compares the latest
results against the saved baseline and exits non-zero on regression — used
by `self_growth_weekly.py` to gate Tier-1 prompt-tweak auto-applies.

Design:
- Source of truth = per-agent report files in `data/evals/reports/` (already
  written by `scripts/eval_runner.py`).
- We do NOT re-run agents; we summarise existing reports.
- Baseline is a markdown file Boss can read, version-control, and diff.

Usage:
    .venv/bin/python scripts/eval_baseline.py                 # publish baseline
    .venv/bin/python scripts/eval_baseline.py --check         # exit non-zero on regression
    .venv/bin/python scripts/eval_baseline.py --summary       # print without writing
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
EVALS_DIR = PROJECT_ROOT / "data" / "evals"
REPORTS_DIR = EVALS_DIR / "reports"
BASELINE_PATH = EVALS_DIR / "baseline.md"
BASELINE_JSON = EVALS_DIR / "baseline.json"


# ── Report parsing ───────────────────────────────────────────────────────────


def _list_agent_dirs() -> list[Path]:
    """Each subdir of data/evals/ except _packages/, reports/, baseline_*."""
    if not EVALS_DIR.exists():
        return []
    return sorted(
        d for d in EVALS_DIR.iterdir()
        if d.is_dir() and d.name not in ("_packages", "reports")
    )


def _latest_report_for_agent(agent: str) -> Path | None:
    """Look in reports/ for the newest file mentioning this agent."""
    if not REPORTS_DIR.exists():
        return None
    candidates = list(REPORTS_DIR.glob(f"*{agent}*.md")) + list(REPORTS_DIR.glob(f"*{agent}*.json"))
    if not candidates:
        return None
    return max(candidates, key=lambda p: p.stat().st_mtime)


_PASS_RE = re.compile(r"(?i)(pass|ok|✅|true|good)")
_FAIL_RE = re.compile(r"(?i)(fail|error|❌|false|bad)")
_PENDING_RE = re.compile(r"(?i)(pending|skip|manual|🟡)")
_NUM_RE = re.compile(r"(\d+)\s*/\s*(\d+)")


def _parse_report(path: Path) -> dict:
    """Extract pass/fail counts from a report file (md or json)."""
    text = path.read_text(encoding="utf-8", errors="replace")

    if path.suffix == ".json":
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            return _parse_markdown(text)
        if isinstance(data, list):
            passes = sum(1 for r in data if str(r.get("status", "")).lower() in ("pass", "ok"))
            fails = sum(1 for r in data if str(r.get("status", "")).lower() in ("fail", "error"))
            pending = sum(1 for r in data if str(r.get("status", "")).lower() in ("pending", "pending_manual"))
            total = len(data)
            return {
                "passed": passes,
                "failed": fails,
                "pending": pending,
                "total": total,
                "pass_rate": (passes / total) if total else 0.0,
            }
        return _parse_markdown(text)

    return _parse_markdown(text)


def _parse_markdown(text: str) -> dict:
    """Best-effort parse — look for 'N/M passed' patterns or count emoji status markers."""
    # Try explicit "X/Y passed" anywhere
    nums = _NUM_RE.findall(text)
    if nums:
        passed, total = int(nums[0][0]), int(nums[0][1])
        return {
            "passed": passed,
            "failed": max(0, total - passed),
            "pending": 0,
            "total": total,
            "pass_rate": (passed / total) if total else 0.0,
        }

    # Fallback: count status markers
    lines = text.splitlines()
    passed = sum(1 for ln in lines if _PASS_RE.search(ln) and not _FAIL_RE.search(ln))
    failed = sum(1 for ln in lines if _FAIL_RE.search(ln))
    pending = sum(1 for ln in lines if _PENDING_RE.search(ln))
    total = passed + failed + pending
    return {
        "passed": passed,
        "failed": failed,
        "pending": pending,
        "total": total,
        "pass_rate": (passed / total) if total else 0.0,
    }


# ── Aggregation ──────────────────────────────────────────────────────────────


def _collect() -> dict:
    """Walk each agent dir, find latest report, parse stats."""
    out: dict[str, dict] = {}
    for agent_dir in _list_agent_dirs():
        report = _latest_report_for_agent(agent_dir.name)
        if not report:
            out[agent_dir.name] = {"status": "no_report", "passed": 0, "failed": 0,
                                   "pending": 0, "total": 0, "pass_rate": 0.0,
                                   "report_path": None}
            continue
        stats = _parse_report(report)
        stats["status"] = "ok"
        stats["report_path"] = str(report.relative_to(PROJECT_ROOT))
        out[agent_dir.name] = stats
    return out


def _format_baseline_md(stats: dict[str, dict]) -> str:
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    total_passed = sum(s.get("passed", 0) for s in stats.values())
    total_total = sum(s.get("total", 0) for s in stats.values())
    overall_rate = (total_passed / total_total) if total_total else 0.0

    lines: list[str] = [
        "# Jarvis Evaluation Baseline",
        "",
        f"**Generated:** {today} (by `scripts/eval_baseline.py`)",
        f"**Overall:** {total_passed}/{total_total} passed ({overall_rate:.1%})",
        "",
        "This file aggregates the latest per-agent reports under `data/evals/reports/`. ",
        "It is the reference Phase E (`self_growth_weekly.py`) compares against when ",
        "auto-applying Tier-1 prompt tweaks. Drops below the recorded rate trigger a halt.",
        "",
        "## Per-agent results",
        "",
        "| Agent | Passed | Failed | Pending | Total | Pass Rate | Report |",
        "|-------|-------:|-------:|--------:|------:|----------:|--------|",
    ]

    for agent in sorted(stats):
        s = stats[agent]
        passed = s.get("passed", 0)
        failed = s.get("failed", 0)
        pending = s.get("pending", 0)
        total = s.get("total", 0)
        rate = s.get("pass_rate", 0.0)
        rate_pct = f"{rate:.0%}" if total else "—"
        report = s.get("report_path") or "—"
        lines.append(
            f"| `{agent}` | {passed} | {failed} | {pending} | {total} | {rate_pct} | "
            f"{'`' + report + '`' if report != '—' else '—'} |"
        )

    lines.extend([
        "",
        "## Methodology",
        "",
        "- Each agent's most-recent file under `data/evals/reports/` is parsed.",
        "- Pass rate = (passed) / (total). Pending tests don't count as failures.",
        "- Markdown reports parse via `X/Y passed` heuristic + status-emoji fallback.",
        "- JSON reports parse the `status` field of each entry.",
        "- A baseline drop > 5pp in any agent triggers a regression alert.",
        "",
        "## Regression policy",
        "",
        "- Tier-1 prompt tweaks proposed by Phase E require baseline pass rate to hold or improve.",
        "- If `--check` exits non-zero, Phase E falls back to drafting only — no auto-apply.",
    ])
    return "\n".join(lines)


# ── Regression check ─────────────────────────────────────────────────────────


def _load_previous_json() -> dict | None:
    if not BASELINE_JSON.exists():
        return None
    try:
        return json.loads(BASELINE_JSON.read_text())
    except Exception:
        return None


def _detect_regressions(current: dict, previous: dict, threshold_pp: float = 0.05) -> list[str]:
    """Return list of regression descriptions (empty = no regression)."""
    alerts: list[str] = []
    prev_agents = previous.get("agents", {})
    for agent, cur_stats in current.items():
        prev_stats = prev_agents.get(agent)
        if not prev_stats:
            continue
        cur_rate = float(cur_stats.get("pass_rate", 0.0))
        prev_rate = float(prev_stats.get("pass_rate", 0.0))
        if cur_rate + threshold_pp < prev_rate:
            alerts.append(
                f"{agent}: {prev_rate:.0%} → {cur_rate:.0%} "
                f"(drop {prev_rate - cur_rate:.0%})"
            )
    return alerts


# ── Main ─────────────────────────────────────────────────────────────────────


def main() -> int:
    parser = argparse.ArgumentParser(description="Aggregate eval reports → published baseline")
    parser.add_argument("--check", action="store_true",
                        help="Compare current results vs saved baseline; exit 1 on regression")
    parser.add_argument("--summary", action="store_true",
                        help="Print baseline to stdout without writing files")
    parser.add_argument("--threshold", type=float, default=0.05,
                        help="Regression threshold in fractional points (default 0.05 = 5 pp)")
    args = parser.parse_args()

    current = _collect()

    if not current:
        print("No agent eval dirs found under data/evals/. Run eval_runner first.")
        return 0

    if args.check:
        previous = _load_previous_json()
        if not previous:
            print("No prior baseline to check against. Run without --check first to publish one.")
            return 0
        regressions = _detect_regressions(current, previous, threshold_pp=args.threshold)
        if regressions:
            print("REGRESSIONS detected:")
            for r in regressions:
                print(f"  - {r}")
            return 1
        print("No regressions detected.")
        return 0

    md = _format_baseline_md(current)

    if args.summary:
        print(md)
        return 0

    EVALS_DIR.mkdir(parents=True, exist_ok=True)
    BASELINE_PATH.write_text(md)
    BASELINE_JSON.write_text(json.dumps(
        {"generated_at": datetime.now(timezone.utc).isoformat(), "agents": current},
        indent=2,
    ))
    print(f"Wrote {BASELINE_PATH.relative_to(PROJECT_ROOT)}")
    print(f"Wrote {BASELINE_JSON.relative_to(PROJECT_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
