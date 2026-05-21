# Spec: Auto-capture Layer

**Status:** active
**Owner:** `scripts/auto_capture.py`
**Last reviewed:** 2026-05-13

## Purpose

Every 30 minutes, summarise new conversation turns from `data/logs/conversations.jsonl` and ingest the distilled facts back into the ChromaDB vector store. This is what feeds Phase A's recall layer with fresh memory — without it, recall only knows what was bootstrapped on day one.

Concretely: Boss tells Jarvis something on Tuesday. The auto-capture job runs that day, summarises that conversation, extracts 1-5 atomic facts ("Boss prefers X", "Anisha's birthday is Y"), and writes each fact as a new chunk into the vector store. On Friday, Boss asks something tangentially related — Phase A's recall layer finds the Tuesday fact and surfaces it before the reply is generated.

## Inputs

| Name | Type | Source | Notes |
|------|------|--------|-------|
| `conversations.jsonl` | JSONL log | `data/logs/conversations.jsonl` — appended by daemon `/chat` | One line per turn |
| `marker` | JSON state | `data/markers/auto_capture_state.json` | Tracks last-processed byte offset + run timestamps |
| Claude API | LLM | via `jarvis_core.orchestrator.run_worker` | Used for summarisation; Haiku-class |

## Outputs

| Name | Type | Consumer | Notes |
|------|------|----------|-------|
| Vector chunks | ChromaDB inserts | `Recaller.gather()` reads these | Source = `conversations/{YYYY-MM-DD}/{user_id}/batch_{idx}` |
| `data/markers/auto_capture_state.json` | JSON | Self (next run) | last_offset, last_ts, lifetime_chunks_added |
| `data/logs/auto_capture.jsonl` | JSONL log | Observability | Per-run summary |

## Behavioural contract

- MUST be idempotent: re-running on the same input must NOT double-ingest (deduplication via content hash already in EpisodicMemory)
- MUST advance offset only after successful summarisation + ingestion
- MUST batch turns by user_id, max 8 turns per batch
- MUST extract at most 5 atomic facts per batch
- MUST tag every chunk with `source="conversations/{YYYY-MM-DD}/{user_id}/batch_{idx}"` so Phase E can prune later
- MUST honour `JARVIS_AUTOCAPTURE_ENABLED=0` kill-switch
- MUST cap LLM calls per run at 10 (cost guard)
- MUST NOT raise on individual batch failure — log + continue with next batch
- MUST NOT block longer than 5 minutes total — hard timeout
- SHOULD skip batches where all turns have `confidence == "low"` (likely garbage)
- SHOULD skip batches where total user+reply chars < 200 (noise threshold)

## Failure modes

| Failure | Detection | Response |
|---------|-----------|----------|
| LLM call fails | Exception | Log batch_id + error, leave offset un-advanced (retry next run) |
| Malformed JSONL line | json.JSONDecodeError | Skip line, log warning, advance past it |
| Chroma write fails | Exception | Same as LLM fail — un-advance, retry next run |
| Marker file corrupt | json.JSONDecodeError | Reset to offset=0 (will re-process from start; dedup protects) |
| `conversations.jsonl` missing | FileNotFoundError | Exit cleanly with `nothing_to_capture` log entry |

## Eval cases

`data/evals/auto_capture/test_cases.jsonl` covers:

1. **Empty log → no-op**
2. **Single turn → 1 chunk, batch_0**
3. **8+ turns same user → at least 1 batch, max 5 facts**
4. **Mixed users → separate batches per user**
5. **Low-confidence turns → batch skipped**
6. **LLM error → offset un-advanced, retry succeeds next run**
7. **Marker reset → safe re-processing, no duplicates due to content hash**

## Non-goals

- Does NOT read or modify `data/memory/*.md` files (those are hand-curated)
- Does NOT do graph-relationship extraction (Memory MCP / Phase E may add)
- Does NOT delete old conversations (Phase E prune does)
- Does NOT do real-time capture — strictly batch every 30 min
- Does NOT run on `voice/` audio — text only (transcription happens upstream)

## Dependencies

- Code: `scripts/episodic_memory.py:EpisodicMemory.add_chunks()`
- Code: `jarvis_core/orchestrator.py:run_worker()`
- Data: `data/logs/conversations.jsonl` — written by daemon `/chat`
- Env vars: `JARVIS_AUTOCAPTURE_ENABLED` (default: 1), `JARVIS_AUTOCAPTURE_BATCH_SIZE` (default: 8), `JARVIS_AUTOCAPTURE_MAX_LLM_CALLS` (default: 10)

## Changelog

- 2026-05-13: Initial draft (Phase C)
