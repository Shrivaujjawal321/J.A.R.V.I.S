#!/usr/bin/env python3
"""
Feedback collector for Jarvis.

Provides FeedbackLogger to record ratings/notes on agent outputs.
Also exposes a CLI viewer for querying feedback.

Usage (module):
    from feedback import FeedbackLogger
    fb = FeedbackLogger()
    fb.log(
        target="resume-agent",
        rating="thumbs_up",
        note="Good catch on the AI-detection point",
        session_context={"task": "resume review"}
    )

Usage (CLI):
    .venv/bin/python scripts/feedback.py --summary 30d
    .venv/bin/python scripts/feedback.py --negatives week
    .venv/bin/python scripts/feedback.py --top-rated 30d
"""

import argparse
import fcntl
import json
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOGS_DIR = ROOT / "data" / "logs"
FEEDBACK_FILE = LOGS_DIR / "feedback.jsonl"

POSITIVE_RATINGS = {"thumbs_up", "star_5", "star_4", "good", "positive"}
NEGATIVE_RATINGS = {"thumbs_down", "star_1", "star_2", "bad", "negative"}


class FeedbackLogger:
    """Append feedback records to a single JSONL file."""

    def __init__(self, feedback_file=None):
        self.feedback_file = feedback_file or FEEDBACK_FILE

    def log(self, target, rating, note=None, session_context=None, run_id=None):
        """Append one feedback record. Thread-safe via fcntl advisory lock."""
        entry = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "target": target,
            "rating": rating,
            "note": note or "",
            "context": session_context or {},
        }
        if run_id is not None:
            entry["run_id"] = run_id

        self.feedback_file.parent.mkdir(parents=True, exist_ok=True)

        with self.feedback_file.open("a") as fh:
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


def _iter_feedback(since, feedback_file=None):
    if feedback_file is None:
        feedback_file = FEEDBACK_FILE
    if not feedback_file.exists():
        return
    with feedback_file.open() as fh:
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


def cmd_summary(window):
    since = _parse_window(window)
    stats = defaultdict(lambda: {"total": 0, "positive": 0, "negative": 0, "neutral": 0})
    for r in _iter_feedback(since):
        target = r.get("target", "unknown")
        rating = r.get("rating", "")
        stats[target]["total"] += 1
        if rating in POSITIVE_RATINGS:
            stats[target]["positive"] += 1
        elif rating in NEGATIVE_RATINGS:
            stats[target]["negative"] += 1
        else:
            stats[target]["neutral"] += 1
    if not stats:
        _print_info("No feedback found for window: " + window)
        return
    rows = []
    for target in sorted(stats, key=lambda t: stats[t]["total"], reverse=True):
        s = stats[target]
        total = s["total"]
        pos = s["positive"]
        neg = s["negative"]
        neu = s["neutral"]
        score = str(100 * pos // total) + "%" if total > 0 else "n/a"
        rows.append([target, str(total), str(pos), str(neg), str(neu), score])
    _print_table(
        "Feedback Summary - " + window,
        ["Target", "Total", "Positive", "Negative", "Neutral", "Positive Rate"],
        rows,
    )


def cmd_negatives(window):
    since = _parse_window(window)
    records = [r for r in _iter_feedback(since)
               if r.get("rating", "") in NEGATIVE_RATINGS]
    if not records:
        _print_info("No negative feedback found for window: " + window)
        return
    rows = []
    for r in records:
        ts = r.get("ts", "")[:19].replace("T", " ")
        target = r.get("target", "?")
        rating = r.get("rating", "?")
        note = r.get("note", "")[:100]
        rows.append([ts, target, rating, note])
    _print_table(
        "Negative Feedback - " + window + " (" + str(len(rows)) + " entries)",
        ["Time (UTC)", "Target", "Rating", "Note"],
        rows,
    )


def cmd_top_rated(window):
    since = _parse_window(window)
    counts = Counter()
    pos_counts = Counter()
    for r in _iter_feedback(since):
        target = r.get("target", "unknown")
        counts[target] += 1
        if r.get("rating", "") in POSITIVE_RATINGS:
            pos_counts[target] += 1
    if not counts:
        _print_info("No feedback found for window: " + window)
        return
    rated = [(t, counts[t], pos_counts[t]) for t in counts]
    rated.sort(key=lambda x: (x[2] / x[1] if x[1] > 0 else 0), reverse=True)
    rows = []
    for target, total, pos in rated:
        rate = str(100 * pos // total) + "%" if total > 0 else "n/a"
        rows.append([target, str(total), str(pos), rate])
    _print_table(
        "Top Rated - " + window,
        ["Target", "Total Feedback", "Positive", "Positive Rate"],
        rows,
    )


def main():
    parser = argparse.ArgumentParser(
        description="Jarvis Feedback - view collected feedback"
    )
    parser.add_argument("--summary", metavar="WINDOW",
                        help="Aggregate feedback by target (today | week | <N>d)")
    parser.add_argument("--negatives", metavar="WINDOW",
                        help="Recent thumbs-down entries with notes")
    parser.add_argument("--top-rated", metavar="WINDOW",
                        help="Best-performing agents by positive rate")
    args = parser.parse_args()

    if args.summary:
        cmd_summary(args.summary)
    elif args.negatives:
        cmd_negatives(args.negatives)
    elif args.top_rated:
        cmd_top_rated(args.top_rated)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
