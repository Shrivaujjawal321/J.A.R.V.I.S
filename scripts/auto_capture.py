#!/usr/bin/env python3
"""
auto_capture.py — Phase C of the self-growth loop.

Runs every 30 minutes via systemd timer. Reads new turns from
`data/logs/conversations.jsonl`, batches by user, summarises each batch with
a small Claude call, and ingests the distilled facts into ChromaDB so the
recall layer can find them later.

See `specs/auto-capture.spec.md` for the full contract.

Usage:
    .venv/bin/python scripts/auto_capture.py            # normal run
    .venv/bin/python scripts/auto_capture.py --dry-run  # no LLM, no ingest
"""
from __future__ import annotations

import argparse
import asyncio
import json
import logging
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.episodic_memory import EpisodicMemory  # noqa: E402

# ── Paths + defaults ──────────────────────────────────────────────────────────

CONV_LOG = PROJECT_ROOT / "data" / "logs" / "conversations.jsonl"
MARKER_DIR = PROJECT_ROOT / "data" / "markers"
MARKER = MARKER_DIR / "auto_capture_state.json"
RUN_LOG = PROJECT_ROOT / "data" / "logs" / "auto_capture.jsonl"

BATCH_SIZE = int(os.getenv("JARVIS_AUTOCAPTURE_BATCH_SIZE", "8"))
MAX_LLM_CALLS = int(os.getenv("JARVIS_AUTOCAPTURE_MAX_LLM_CALLS", "10"))
MIN_BATCH_CHARS = 200
HARD_TIMEOUT_S = 300
LLM_MODEL = os.getenv("JARVIS_AUTOCAPTURE_MODEL", "claude-haiku-4-5-20251001")

logging.basicConfig(
    level=os.getenv("JARVIS_AUTOCAPTURE_LOG_LEVEL", "INFO"),
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)
log = logging.getLogger("auto_capture")


# ── Marker I/O ────────────────────────────────────────────────────────────────


def _load_marker() -> dict:
    if not MARKER.exists():
        return {"last_offset": 0, "last_ts": None, "lifetime_chunks_added": 0}
    try:
        return json.loads(MARKER.read_text())
    except Exception as exc:
        log.warning("marker corrupt (%s) — resetting to offset=0", exc)
        return {"last_offset": 0, "last_ts": None, "lifetime_chunks_added": 0}


def _save_marker(marker: dict) -> None:
    MARKER_DIR.mkdir(parents=True, exist_ok=True)
    tmp = MARKER.with_suffix(".tmp")
    tmp.write_text(json.dumps(marker, indent=2))
    tmp.replace(MARKER)


def _append_run_log(entry: dict) -> None:
    try:
        RUN_LOG.parent.mkdir(parents=True, exist_ok=True)
        with RUN_LOG.open("a") as fh:
            fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception:
        pass


# ── Conversation log reader ──────────────────────────────────────────────────


def _read_new_turns(offset: int) -> tuple[list[dict], int]:
    """Read JSONL lines after `offset`. Returns (turns, new_offset)."""
    if not CONV_LOG.exists():
        return ([], offset)

    turns: list[dict] = []
    new_offset = offset
    with CONV_LOG.open("rb") as fh:
        fh.seek(offset)
        for raw in fh:
            new_offset += len(raw)
            try:
                obj = json.loads(raw.decode("utf-8", errors="replace"))
            except json.JSONDecodeError:
                log.warning("skip malformed jsonl line at offset %d", new_offset)
                continue
            if not isinstance(obj, dict):
                continue
            turns.append(obj)
    return (turns, new_offset)


# ── Batching ─────────────────────────────────────────────────────────────────


def _batch_turns(turns: list[dict]) -> list[list[dict]]:
    """Group turns by user_id, slice into BATCH_SIZE-sized batches preserving order."""
    by_user: dict[str, list[dict]] = {}
    for t in turns:
        uid = str(t.get("user_id", "default"))
        by_user.setdefault(uid, []).append(t)

    batches: list[list[dict]] = []
    for uid, group in by_user.items():
        for i in range(0, len(group), BATCH_SIZE):
            batches.append(group[i: i + BATCH_SIZE])
    return batches


def _is_noisy_batch(batch: list[dict]) -> bool:
    """Skip if all turns are low-confidence OR total chars too small."""
    if not batch:
        return True
    total_chars = sum(
        len(str(t.get("user_msg", ""))) + len(str(t.get("reply", "")))
        for t in batch
    )
    if total_chars < MIN_BATCH_CHARS:
        return True
    confidences = {str(t.get("confidence", "")).lower() for t in batch}
    if confidences and confidences.issubset({"low"}):
        return True
    return False


# ── Summarisation ────────────────────────────────────────────────────────────


_SUMMARY_TEMPLATE = """You are a memory extractor for Jarvis (Boss's personal AI). Read the conversation snippet below and emit a compact JSON object with the durable facts Boss would want Jarvis to remember WEEKS later.

Rules:
- Extract 1 to 5 ATOMIC facts (each fact is one independent statement)
- Each fact must include a `topic` (1-3 word tag) and a `fact` (a single sentence, ≤ 20 words)
- Include a one-sentence `summary` of the overall session
- Skip ephemeral chitchat ("hi", "ok thanks") — those are noise
- If nothing durable, return facts: []
- DO NOT include speculation, predictions, or anything the conversation doesn't directly state

Output ONLY the JSON object, no markdown fences, no surrounding prose:

{"summary": "...", "facts": [{"topic": "...", "fact": "..."}]}

---

CONVERSATION SNIPPET (newest last):

__SNIPPET__

Now output the JSON object."""


def _build_snippet(batch: list[dict]) -> str:
    parts: list[str] = []
    for t in batch:
        ts = t.get("ts", "")
        user_msg = (t.get("user_msg") or "").strip()
        reply = (t.get("reply") or "").strip()
        parts.append(f"[{ts}] USER: {user_msg}\n[{ts}] JARVIS: {reply}")
    return "\n\n".join(parts)


def _build_summary_prompt(batch: list[dict]) -> str:
    return _SUMMARY_TEMPLATE.replace("__SNIPPET__", _build_snippet(batch))


_JSON_BLOCK_RE = re.compile(r"\{.*\}", re.DOTALL)


def _parse_summary(raw: str) -> dict | None:
    if not raw:
        return None
    text = raw.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    candidates = [text]
    m = _JSON_BLOCK_RE.search(text)
    if m:
        candidates.append(m.group(0))
    for c in candidates:
        try:
            data = json.loads(c)
        except (json.JSONDecodeError, ValueError):
            continue
        if isinstance(data, dict) and "facts" in data:
            return data
    return None


# ── LLM dispatch ─────────────────────────────────────────────────────────────


async def _summarise_batch(batch: list[dict]) -> dict | None:
    """Call Claude to produce a summary + facts. Returns None on failure."""
    from jarvis_core.orchestrator import run_worker

    prompt = _build_summary_prompt(batch)
    try:
        outcome = await asyncio.wait_for(
            run_worker(
                prompt,
                project_root=PROJECT_ROOT,
                max_turns=1,
                allowed_tools=[],
                timeout_seconds=60,
                model=LLM_MODEL,
            ),
            timeout=70,
        )
    except asyncio.TimeoutError:
        log.warning("summary timeout for batch user=%s len=%d",
                    batch[0].get("user_id"), len(batch))
        return None
    except Exception as exc:
        log.warning("summary error: %s", exc)
        return None

    if outcome.error and not outcome.text:
        return None
    return _parse_summary(outcome.text)


# ── Ingestion ────────────────────────────────────────────────────────────────


def _ingest_summary(mem: EpisodicMemory, summary: dict, batch: list[dict],
                    batch_idx: int) -> int:
    """Write summary + atomic facts as separate chunks. Returns count added."""
    if not summary:
        return 0

    user_id = batch[0].get("user_id", "default")
    date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    source = f"conversations/{date}/{user_id}/batch_{batch_idx}"

    chunks: list[dict] = []

    # The session summary itself
    summary_text = (summary.get("summary") or "").strip()
    if summary_text:
        chunks.append({
            "text": f"Conversation summary ({date}, user={user_id}): {summary_text}",
            "source": source,
            "section": "summary",
            "kind": "summary",
            "captured_at": datetime.now(timezone.utc).isoformat(),
        })

    # Atomic facts
    facts = summary.get("facts") or []
    if not isinstance(facts, list):
        facts = []
    for i, fact in enumerate(facts[:5]):
        if not isinstance(fact, dict):
            continue
        topic = str(fact.get("topic") or "general").strip()
        text = str(fact.get("fact") or "").strip()
        if not text:
            continue
        chunks.append({
            "text": f"[{topic}] {text}",
            "source": source,
            "section": f"fact_{i}",
            "topic": topic,
            "kind": "fact",
            "captured_at": datetime.now(timezone.utc).isoformat(),
        })

    if not chunks:
        return 0
    return mem.add_chunks(chunks)


# ── Main ─────────────────────────────────────────────────────────────────────


async def main(dry_run: bool = False) -> int:
    """Returns process exit code (0 = success)."""
    if os.getenv("JARVIS_AUTOCAPTURE_ENABLED", "1") in ("0", "false", "False"):
        log.info("disabled via env — exit clean")
        _append_run_log({"ts": datetime.now(timezone.utc).isoformat(),
                         "status": "disabled"})
        return 0

    started = time.perf_counter()
    marker = _load_marker()
    offset = int(marker.get("last_offset", 0))
    turns, new_offset = _read_new_turns(offset)

    log.info("read %d new turns from offset=%d (file_size=%d)",
             len(turns), offset, new_offset)

    if not turns:
        _append_run_log({"ts": datetime.now(timezone.utc).isoformat(),
                         "status": "nothing_to_capture", "offset": offset})
        return 0

    batches = _batch_turns(turns)
    log.info("formed %d batches across %d users",
             len(batches), len({b[0].get("user_id") for b in batches}))

    if dry_run:
        log.info("DRY RUN — no LLM, no ingest")
        for i, b in enumerate(batches):
            log.info("  batch[%d] user=%s turns=%d noisy=%s",
                     i, b[0].get("user_id"), len(b), _is_noisy_batch(b))
        _append_run_log({"ts": datetime.now(timezone.utc).isoformat(),
                         "status": "dry_run", "batches": len(batches),
                         "turns": len(turns)})
        return 0

    mem = EpisodicMemory()
    llm_calls = 0
    chunks_added = 0
    successful_batches = 0
    failed_batches = 0

    for batch_idx, batch in enumerate(batches):
        if time.perf_counter() - started > HARD_TIMEOUT_S:
            log.warning("hard timeout exceeded (%ds), stopping early", HARD_TIMEOUT_S)
            break
        if llm_calls >= MAX_LLM_CALLS:
            log.warning("max LLM calls (%d) reached, deferring remaining %d batches",
                        MAX_LLM_CALLS, len(batches) - batch_idx)
            break
        if _is_noisy_batch(batch):
            log.debug("batch[%d] skipped (noisy)", batch_idx)
            continue

        llm_calls += 1
        summary = await _summarise_batch(batch)
        if not summary:
            failed_batches += 1
            continue
        added = _ingest_summary(mem, summary, batch, batch_idx)
        chunks_added += added
        if added > 0:
            successful_batches += 1
        log.info("batch[%d] user=%s turns=%d → %d chunks",
                 batch_idx, batch[0].get("user_id"), len(batch), added)

    # Only advance offset if we processed everything (otherwise we'd skip on next run)
    if failed_batches == 0:
        marker["last_offset"] = new_offset
    else:
        log.info("%d failed batches — leaving offset unchanged for retry", failed_batches)

    marker["last_ts"] = datetime.now(timezone.utc).isoformat()
    marker["lifetime_chunks_added"] = (
        int(marker.get("lifetime_chunks_added", 0)) + chunks_added
    )
    _save_marker(marker)

    duration_ms = int((time.perf_counter() - started) * 1000)
    log.info("done turns=%d batches=%d ok=%d failed=%d chunks=%d llm=%d %dms",
             len(turns), len(batches), successful_batches, failed_batches,
             chunks_added, llm_calls, duration_ms)
    _append_run_log({
        "ts": datetime.now(timezone.utc).isoformat(),
        "status": "ok" if failed_batches == 0 else "partial",
        "turns": len(turns),
        "batches_total": len(batches),
        "batches_ok": successful_batches,
        "batches_failed": failed_batches,
        "chunks_added": chunks_added,
        "llm_calls": llm_calls,
        "duration_ms": duration_ms,
        "offset_advanced": failed_batches == 0,
    })
    return 0 if failed_batches == 0 else 2


def _cli() -> int:
    parser = argparse.ArgumentParser(description="Auto-capture conversations into vector memory")
    parser.add_argument("--dry-run", action="store_true",
                        help="No LLM calls, no ingest — just batch + report")
    args = parser.parse_args()
    return asyncio.run(main(dry_run=args.dry_run))


if __name__ == "__main__":
    raise SystemExit(_cli())
