"""
bootstrap_memory.py — One-time ingestion of all Jarvis knowledge files
into the episodic memory vector DB.

Run once to seed the database:
    .venv/bin/python scripts/bootstrap_memory.py

Safe to re-run — duplicate chunks are detected via content hash and skipped.
"""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.episodic_memory import EpisodicMemory

# Directories and globs to ingest
INGEST_TARGETS: list[tuple[Path, str]] = [
    (PROJECT_ROOT / "data" / "memory",        "*.md"),
    (PROJECT_ROOT / "data" / "notes",         "*.md"),
    (PROJECT_ROOT / "data" / "conversations", "*.md"),
    (PROJECT_ROOT / "data" / "briefings",     "*.md"),
]


def main() -> None:
    print("=" * 60)
    print("  Jarvis Episodic Memory — Bootstrap Ingestion")
    print("=" * 60)

    mem = EpisodicMemory()

    total_added = 0
    dir_summary: dict[str, dict[str, int]] = {}

    for target_dir, pattern in INGEST_TARGETS:
        dir_label = str(target_dir.relative_to(PROJECT_ROOT))

        if not target_dir.exists():
            print(f"\n[SKIP] {dir_label}/ — directory not found")
            continue

        files = sorted(target_dir.glob(pattern))
        if not files:
            print(f"\n[SKIP] {dir_label}/ — no {pattern} files found")
            continue

        print(f"\n[DIR] {dir_label}/ ({len(files)} files)")
        dir_total = 0
        dir_summary[dir_label] = {}

        for file in files:
            added = mem.add_file(file)
            label = file.name
            status = f"+{added} chunks" if added > 0 else "(already indexed)"
            print(f"  {label:50s}  {status}")
            dir_total += added
            dir_summary[dir_label][file.name] = added

        print(f"  → subtotal: {dir_total} new chunks from {dir_label}/")
        total_added += dir_total

    # Final stats
    stats = mem.stats()
    print("\n" + "=" * 60)
    print("  Bootstrap Complete")
    print("=" * 60)
    print(f"  New chunks added this run : {total_added}")
    print(f"  Total chunks in DB        : {stats['total_chunks']}")
    print(f"  Unique source files       : {stats['unique_sources']}")
    print(f"  Last added timestamp      : {stats['last_added']}")
    print("=" * 60)


if __name__ == "__main__":
    main()
