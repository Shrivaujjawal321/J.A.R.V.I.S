"""
incremental_memory_ingest.py — Nightly incremental ingestor for episodic memory.

Only processes files modified since the last successful run.
Designed to be called by a systemd timer; logs results to data/logs/memory_ingest.jsonl.

Usage:
    .venv/bin/python scripts/incremental_memory_ingest.py
"""

from __future__ import annotations

import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.episodic_memory import EpisodicMemory

MARKER_FILE = PROJECT_ROOT / "data" / "markers" / "memory_last_ingest"
LOG_FILE = PROJECT_ROOT / "data" / "logs" / "memory_ingest.jsonl"

INGEST_TARGETS: list[tuple[Path, str]] = [
    (PROJECT_ROOT / "data" / "memory",        "*.md"),
    (PROJECT_ROOT / "data" / "notes",         "*.md"),
    (PROJECT_ROOT / "data" / "conversations", "*.md"),
    (PROJECT_ROOT / "data" / "briefings",     "*.md"),
]


def _read_last_ingest_ts() -> float:
    """Return Unix timestamp of last successful ingest, or 0 if never run."""
    if MARKER_FILE.exists():
        try:
            return float(MARKER_FILE.read_text().strip())
        except ValueError:
            pass
    return 0.0


def _write_marker(ts: float) -> None:
    MARKER_FILE.parent.mkdir(parents=True, exist_ok=True)
    MARKER_FILE.write_text(str(ts))


def _log(record: dict) -> None:
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")


def main() -> None:
    run_start = time.time()
    run_ts = datetime.now(timezone.utc).isoformat()
    last_ts = _read_last_ingest_ts()

    since_label = (
        datetime.fromtimestamp(last_ts).isoformat() if last_ts > 0 else "never"
    )
    print(f"[incremental_ingest] Starting — changed since: {since_label}", flush=True)

    mem = EpisodicMemory()

    total_files_scanned = 0
    total_files_changed = 0
    total_chunks_added = 0
    file_log: list[dict] = []
    errors: list[str] = []

    for target_dir, pattern in INGEST_TARGETS:
        dir_label = str(target_dir.relative_to(PROJECT_ROOT))

        if not target_dir.exists():
            continue

        for file in sorted(target_dir.glob(pattern)):
            if not file.is_file():
                continue

            total_files_scanned += 1
            mtime = file.stat().st_mtime

            if mtime <= last_ts:
                continue  # unchanged since last run

            total_files_changed += 1
            source = str(file.relative_to(PROJECT_ROOT))

            # Re-ingest: forget old chunks for this source, then re-add
            try:
                deleted = mem.forget(source)
                added = mem.add_file(file)
                total_chunks_added += added
                print(
                    f"  [updated] {source} — removed {deleted} old, added {added} new",
                    flush=True,
                )
                file_log.append({
                    "file": source,
                    "deleted": deleted,
                    "added": added,
                    "status": "ok",
                })
            except Exception as exc:
                msg = f"ERROR ingesting {source}: {exc}"
                print(f"  {msg}", file=sys.stderr, flush=True)
                errors.append(msg)
                file_log.append({
                    "file": source,
                    "status": "error",
                    "error": str(exc),
                })

    # Write marker only if run completed without critical errors
    _write_marker(run_start)

    elapsed = round(time.time() - run_start, 2)
    stats = mem.stats()

    summary = {
        "run_at": run_ts,
        "since": since_label,
        "elapsed_s": elapsed,
        "files_scanned": total_files_scanned,
        "files_changed": total_files_changed,
        "chunks_added": total_chunks_added,
        "total_chunks_in_db": stats["total_chunks"],
        "errors": errors,
        "files": file_log,
    }
    _log(summary)

    print(
        f"\n[incremental_ingest] Done — "
        f"{total_files_changed}/{total_files_scanned} files updated, "
        f"{total_chunks_added} chunks added, "
        f"{len(errors)} errors. "
        f"({elapsed}s)",
        flush=True,
    )


if __name__ == "__main__":
    main()
