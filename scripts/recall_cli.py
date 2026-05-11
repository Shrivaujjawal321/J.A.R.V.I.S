"""
recall_cli.py — CLI interface for episodic memory recall.

Used by the /recall slash command and for ad-hoc querying.

Usage:
    .venv/bin/python scripts/recall_cli.py "what did we discuss about resume"
    .venv/bin/python scripts/recall_cli.py "Anisha birthday" --k 8
    .venv/bin/python scripts/recall_cli.py "resume research" --json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.episodic_memory import EpisodicMemory

SNIPPET_LEN = 300


def _snippet(text: str) -> str:
    """First SNIPPET_LEN characters, with ellipsis if truncated."""
    text = text.strip().replace("\n", " ")
    if len(text) <= SNIPPET_LEN:
        return text
    return text[:SNIPPET_LEN].rstrip() + " ..."


def main() -> None:
    parser = argparse.ArgumentParser(description="Recall from Jarvis episodic memory")
    parser.add_argument("query", help="Natural-language search query")
    parser.add_argument("--k", type=int, default=5, help="Number of results (default 5)")
    parser.add_argument("--json", action="store_true", dest="as_json", help="Output raw JSON")
    args = parser.parse_args()

    mem = EpisodicMemory()
    results = mem.recall(args.query, k=args.k)

    if args.as_json:
        print(json.dumps(results, indent=2, ensure_ascii=False))
        return

    if not results:
        print("[recall] No results found. Run bootstrap_memory.py to seed the database.")
        return

    print(f"\n[recall] Query: \"{args.query}\"")
    print(f"         Top {len(results)} results:\n")
    print("-" * 70)

    for i, r in enumerate(results, 1):
        score_pct = int(r["score"] * 100)
        source = r["source"]
        section = r.get("section", "")
        location = f"{source}" + (f" § {section}" if section else "")
        snippet = _snippet(r["text"])

        print(f"[{i}] Score: {score_pct}%  |  {location}")
        print(f"     {snippet}")
        print()

    print("-" * 70)
    print("\nWant me to use this context for your next message? (yes/no)")


if __name__ == "__main__":
    main()
