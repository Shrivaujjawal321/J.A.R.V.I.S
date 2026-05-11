#!/usr/bin/env python3
"""
Observability logger for Jarvis.

Provides AgentLogger to record agent invocations as JSONL lines.
Also exposes a CLI viewer for querying logs.

Usage (module):
    from observability import AgentLogger
    logger = AgentLogger()
    logger.log_invocation(
        agent="resume-agent",
        input_summary="Review resume diagnostic",
        output_summary="3 P0 issues found...",
        duration_ms=4523,
        success=True,
        metadata={"tier": "final", "model": "sonnet"}
    )

Usage (CLI):
    .venv/bin/python scripts/observability.py --view today
    .venv/bin/python scripts/observability.py --view week
    .venv/bin/python scripts/observability.py --top-agents 30d
    .venv/bin/python scripts/observability.py --failures week
    .venv/bin/python scripts/observability.py --latency-p99 week
"""

import argparse
import fcntl
import json
import sys
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
LOGS_DIR = ROOT / "data" / "logs"

INPUT_MAX = 200
OUTPUT_MAX = 500


class AgentLogger:
    """Append agent invocation records to daily-rotating JSONL files."""

    def __init__(self, logs_dir=None):
        self.logs_dir = logs_dir or LOGS_DIR

    def _log_file(self, date=None):
        if date is None:
            date = datetime.now(timezone.utc)
        stamp = date.strftime("%Y-%m-%d")
        return self.logs_dir / ("agent-invocations-" + stamp + ".jsonl")

    def log_invocation(self, agent, input_summary, output_summary,
                       duration_ms, success, metadata=None, run_id=None):
        """Append one invocation record. Thread-safe via fcntl advisory lock."""
        entry = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "agent": agent,
            "input_summary": input_summary[:INPUT_MAX],
            "output_summary": output_summary[:OUTPUT_MAX],
            "duration_ms": int(duration_ms),
            "success": success,
            "metadata": metadata or {},
        }
        if run_id is not None:
            entry["run_id"] = run_id

        self.logs_dir.mkdir(parents=True, exist_ok=True)
        log_file = self._log_file()

        with log_file.open("a") as fh:
            try:
                fcntl.flock(fh, fcntl.LOCK_EX)
                fh.write(json.dumps(entry) + "\n")
            finally:
                fcntl.flock(fh, fcntl.LOCK_UN)


def _parse_window(window):
    now = datetime.now(timezone.utc)
    if window == "today":
        return now.replace(hour=0, minute=0, second=0, microsecond=0)
    if window == "week":
        return now - timedelta(days=7)
    if window.endswith("d"):
        try:
            days = int(window[:-1])
            return now - timedelta(days=days)
        except ValueError:
            pass
    raise ValueError("Unknown window: " + repr(window) + ". Use 'today', 'week', or '<N>d'.")


def _iter_logs(since, logs_dir=None):
    if logs_dir is None:
        logs_dir = LOGS_DIR
    now = datetime.now(timezone.utc)
    cursor = since.date()
    end = now.date()
    while cursor <= end:
        stamp = cursor.strftime("%Y-%m-%d")
        path = logs_dir / ("agent-invocations-" + stamp + ".jsonl")
        if path.exists():
            with path.open() as fh:
                for line in fh:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        rec = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    try:
                        rec_ts = datetime.fromisoformat(rec["ts"])
                    except (KeyError, ValueError):
                        yield rec
                        continue
                    if rec_ts >= since:
                        yield rec
        from datetime import date as date_cls
        cursor = cursor + timedelta(days=1)


def _percentile(sorted_vals, pct):
    if not sorted_vals:
        return 0.0
    idx = int(len(sorted_vals) * pct / 100)
    idx = min(idx, len(sorted_vals) - 1)
    return sorted_vals[idx]


try:
    from rich.console import Console
    from rich.table import Table
    from rich import box as rich_box
    _RICH = True
    _console = Console()

    def _print_table(title, columns, rows):
        table = Table(title=title, box=rich_box.SIMPLE_HEAVY, show_lines=False)
        for col in columns:
            table.add_column(col, style="cyan", no_wrap=False)
        for row in rows:
            table.add_row(*[str(c) for c in row])
        _console.print(table)

    def _print_info(msg):
        _console.print("[dim]" + msg + "[/dim]")

except ImportError:
    _RICH = False

    def _print_table(title, columns, rows):
        print("\n=== " + title + " ===")
        widths = [max(len(col), max((len(str(r[i])) for r in rows), default=0))
                  for i, col in enumerate(columns)]
        header = "  ".join(col.ljust(w) for col, w in zip(columns, widths))
        print(header)
        print("-" * len(header))
        for row in rows:
            print("  ".join(str(c).ljust(w) for c, w in zip(row, widths)))

    def _print_info(msg):
        print(msg)


def cmd_view(window):
    since = _parse_window(window)
    records = list(_iter_logs(since))
    if not records:
        _print_info("No invocations found for window: " + window)
        return
    rows = []
    for r in records:
        ts = r.get("ts", "")[:19].replace("T", " ")
        agent = r.get("agent", "?")
        ok = "YES" if r.get("success", True) else "NO"
        dur = str(r.get("duration_ms", "?")) + "ms"
        inp = r.get("input_summary", "")[:60]
        out = r.get("output_summary", "")[:80]
        rows.append([ts, agent, ok, dur, inp, out])
    _print_table(
        "Agent Invocations - " + window + " (" + str(len(rows)) + " entries)",
        ["Time (UTC)", "Agent", "OK", "Duration", "Input", "Output"],
        rows,
    )


def cmd_top_agents(window):
    since = _parse_window(window)
    counts = Counter()
    success_counts = Counter()
    for r in _iter_logs(since):
        agent = r.get("agent", "unknown")
        counts[agent] += 1
        if r.get("success", True):
            success_counts[agent] += 1
    if not counts:
        _print_info("No invocations found for window: " + window)
        return
    rows = []
    for agent, total in counts.most_common():
        ok = success_counts[agent]
        fail = total - ok
        rate = str(100 * ok // total) + "%"
        rows.append([agent, str(total), str(ok), str(fail), rate])
    _print_table(
        "Top Agents - " + window,
        ["Agent", "Total", "Success", "Failures", "Success Rate"],
        rows,
    )


def cmd_failures(window):
    since = _parse_window(window)
    records = [r for r in _iter_logs(since) if not r.get("success", True)]
    if not records:
        _print_info("No failures found for window: " + window)
        return
    rows = []
    for r in records:
        ts = r.get("ts", "")[:19].replace("T", " ")
        agent = r.get("agent", "?")
        dur = str(r.get("duration_ms", "?")) + "ms"
        inp = r.get("input_summary", "")[:60]
        out = r.get("output_summary", "")[:80]
        rows.append([ts, agent, dur, inp, out])
    _print_table(
        "Failed Invocations - " + window + " (" + str(len(rows)) + " failures)",
        ["Time (UTC)", "Agent", "Duration", "Input", "Output"],
        rows,
    )


def cmd_latency(window):
    since = _parse_window(window)
    durations = defaultdict(list)
    for r in _iter_logs(since):
        agent = r.get("agent", "unknown")
        dur = r.get("duration_ms")
        if dur is not None:
            durations[agent].append(float(dur))
    if not durations:
        _print_info("No invocations found for window: " + window)
        return
    rows = []
    for agent in sorted(durations):
        vals = sorted(durations[agent])
        p50 = _percentile(vals, 50)
        p95 = _percentile(vals, 95)
        p99 = _percentile(vals, 99)
        rows.append([agent, str(len(vals)), str(round(p50)) + "ms",
                     str(round(p95)) + "ms", str(round(p99)) + "ms"])
    _print_table(
        "Latency (P50/P95/P99) - " + window,
        ["Agent", "Count", "P50", "P95", "P99"],
        rows,
    )


def main():
    parser = argparse.ArgumentParser(
        description="Jarvis Observability - view agent invocation logs"
    )
    parser.add_argument("--view", metavar="WINDOW",
                        help="Show all invocations (today | week | <N>d)")
    parser.add_argument("--top-agents", metavar="WINDOW",
                        help="Most-invoked agents in window")
    parser.add_argument("--failures", metavar="WINDOW",
                        help="Failed invocations in window")
    parser.add_argument("--latency-p99", metavar="WINDOW",
                        help="P50/P95/P99 latency per agent in window")
    args = parser.parse_args()

    if args.view:
        cmd_view(args.view)
    elif args.top_agents:
        cmd_top_agents(args.top_agents)
    elif args.failures:
        cmd_failures(args.failures)
    elif args.latency_p99:
        cmd_latency(args.latency_p99)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
