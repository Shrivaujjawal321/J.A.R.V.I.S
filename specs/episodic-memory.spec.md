# Spec: Episodic Memory (Vector Store)

**Status:** active
**Owner:** `scripts/episodic_memory.py`
**Last reviewed:** 2026-05-13

## Purpose

Single canonical wrapper around the ChromaDB collection that backs Jarvis's semantic memory. Every component that wants to read or write to long-term memory goes through this class — `Recaller` (Phase A) reads via `recall()`, `incremental_memory_ingest.py` and `auto_capture.py` (Phase C) write via `add()` / `add_chunks()` / `add_file()`.

Centralising the embedding model + dedup + chunking here is what keeps the rest of the codebase free of vector-DB plumbing.

## Inputs

| Name | Type | Notes |
|------|------|-------|
| Text passages | `str` | Boss memory, conversation summaries, atomic facts |
| Markdown files | `Path` | Auto-chunked at heading + paragraph boundaries |
| Queries | `str` | Natural language, English or Hinglish |

## Outputs

| Name | Type | Notes |
|------|------|-------|
| Doc IDs | `str` | SHA-256 first-32 hex of (source, text). Stable + dedup-friendly |
| Recall hits | `list[dict]` | `{text, source, section, score, metadata}`, sorted by relevance |
| Stats | `dict` | total_chunks, unique_sources, last_added |

## Behavioural contract

- MUST persist to `data/memory/chroma/` (single collection name `jarvis`)
- MUST use embedding model `all-MiniLM-L6-v2` (sentence-transformers, ~80 MB)
- MUST dedup by `_content_hash(source, text)` — same text + source = same ID, no re-insert
- MUST cap individual file ingest at 1 MB
- MUST chunk markdown by heading boundaries first, falling back to double-newline, hard-splitting only if a section exceeds CHUNK_TARGET_TOKENS × 4 chars
- MUST return cosine-similarity scores in `[0, 1]` (Chroma distance → similarity = `1 - dist/2`)
- MUST handle empty collection (`count() == 0`) gracefully — return `[]`, never raise
- MUST allow filtering via `where=` clause (passed straight through to Chroma)
- MUST NOT load the embedding model until first use (lazy `_get_embedding_fn`)
- MUST NOT delete chunks except via explicit `forget(source)` call

## Failure modes

| Failure | Detection | Response |
|---------|-----------|----------|
| Chroma init fails | exception in `__init__` | Caller (Recaller) catches + logs, returns empty context |
| Embedding download fails | exception in `_get_embedding_fn` | Same as above |
| Add raises mid-batch | exception | Caller logs; partial batch may have been inserted; dedup makes retry safe |
| Disk full | OSError on persist | Chroma reports; caller continues with degraded service |

## Eval cases

`data/evals/recall/test_cases.jsonl` doubles as the eval suite — exercises `EpisodicMemory.recall()` indirectly through Phase A's `Recaller`.

## Non-goals

- Does NOT do graph-relationship extraction (Memory MCP handles that separately)
- Does NOT do automatic re-embedding when model changes (manual reindex job needed)
- Does NOT support multi-user partitioning (single Boss)
- Does NOT do TTL / age-based expiry — Phase E weekly prune is the planned mechanism

## Dependencies

- Python: `chromadb`, `sentence-transformers` (via chromadb extras)
- Data: `data/memory/chroma/` directory (persistent ChromaDB store)
- Env vars: none (embedding model path is fixed)

## Changelog

- 2026-05-13: Initial draft (Phase F backfill — module pre-existed)
