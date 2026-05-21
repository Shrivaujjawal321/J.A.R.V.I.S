# Spec: Recall Layer

**Status:** active
**Owner:** `jarvis_core/recall.py`
**Last reviewed:** 2026-05-13

## Purpose

Before Jarvis responds to any user message via `/chat`, this layer performs a semantic search across the persistent memory index (ChromaDB + sentence-transformers) and injects the top-matching chunks into the worker prompt as a `<jarvis_memory_context>` block.

Without this layer, `EpisodicMemory.recall()` exists but is only invoked when the user explicitly types `/recall` — so Jarvis behaves like a goldfish in every conversation despite having 155+ indexed chunks. This layer closes the wire.

## Inputs

| Name | Type | Source | Notes |
|------|------|--------|-------|
| `user_message` | `str` | `ChatRequest.message` from `/chat` endpoint | The raw text Boss sent |
| `user_id` | `str` | `ChatRequest.user_id` | Reserved for future per-user memory partitioning |
| `vector_db` | ChromaDB collection | `data/memory/chroma/` | Populated by `scripts/incremental_memory_ingest.py` |

## Outputs

| Name | Type | Consumer | Notes |
|------|------|----------|-------|
| `memory_context` | `str` | `jarvis_core/daemon.py:chat()` → `run_worker()` | Pre-formatted block; empty string when skipped |
| `recall_log` entry | `dict` | `data/logs/recall.jsonl` | One line per invocation, used for tuning |

## Behavioural contract

- MUST return within 500ms p95 (single-shot vector query + format)
- MUST skip recall (return empty string) when:
  - Message length < 30 characters
  - Message starts with `/` (slash command)
  - Message matches greeting regex: `^(hi|hello|hey|namaste|namaskar|hola|salaam)\b`
- MUST apply score threshold ≥ 0.55 (cosine similarity in `[0,1]`)
- MUST cap result count at k=5
- MUST cap total returned tokens at ~2000 (4 chars/token heuristic)
- MUST format output as XML-tagged block so the worker can detect and weight it:
  ```
  <jarvis_memory_context>
    <chunk score="0.87" source="memory/preferences.md" section="Communication">...</chunk>
    ...
  </jarvis_memory_context>
  ```
- MUST append one JSONL line per call to `data/logs/recall.jsonl` with: ts, user_id, msg_hash, n_chunks, top_score, latency_ms, skipped_reason
- MUST honour `JARVIS_RECALL_ENABLED=0` kill-switch — returns empty string unconditionally
- MUST NOT raise on backend failure (Chroma error, embedding model error) — log and return empty string
- MUST NOT mutate any external state (vector DB stays read-only here)
- SHOULD pull top-3 hits from auto-memory `MEMORY.md` via the same embedding model as a secondary source

## Failure modes

| Failure | Detection | Response |
|---------|-----------|----------|
| ChromaDB not initialised / corrupted | Exception on `EpisodicMemory()` construct | Log `chroma_init_error`, return empty string |
| Embedding model download fails | Exception on first `recall()` call | Log `embedding_error`, return empty string |
| Vector DB empty (0 chunks) | `recall()` returns `[]` | Return empty string silently |
| Total context exceeds 2000 tokens | Pre-format size check | Trim from lowest-score chunks down to budget |
| Latency exceeds 1s | Timing wrapper | Log warning, still return result |

## Eval cases

`data/evals/recall/test_cases.jsonl` covers:

1. **Hits relevant fact**: "what does Boss prefer for communication?" → recall finds `preferences.md` Hinglish/respectful chunk
2. **Hits person**: "kya plan karein Anisha ke liye" → recall finds `people.md` Anisha chunk
3. **Hits project**: "LinkedIn pipeline ka status" → recall finds `projects.md` linkedin chunk
4. **Skips greeting**: "hi" → empty context, skip reason = greeting
5. **Skips slash command**: "/recall foo" → empty context, skip reason = slash_command
6. **Skips short**: "ok" → empty context, skip reason = too_short
7. **No relevant memory**: "what is the airspeed of an unladen swallow" → empty context (all scores < 0.55)
8. **Multi-topic message**: "Anisha ke birthday plan aur resume update" → both topics surface

## Non-goals

- Does NOT write to vector DB (ingestion is `scripts/incremental_memory_ingest.py`'s job)
- Does NOT do conversation summarisation (Phase C `auto_capture.py`'s job)
- Does NOT do graph traversal of relationships (Memory MCP's job)
- Does NOT cache results across calls (low hit rate; each query is unique)
- Does NOT pull from Telegram history directly (auto-capture will index those separately)

## Dependencies

- Code: `scripts/episodic_memory.py:EpisodicMemory.recall()` — primitive
- Code: `jarvis_core/orchestrator.py:run_worker()` — consumer (via daemon)
- Data: `data/memory/chroma/` — persistent vector DB
- Data: `~/.claude/projects/-home-ujjwal-Documents-J-A-R-V-I-S-/memory/MEMORY.md` — auto-memory index
- Env vars: `JARVIS_RECALL_ENABLED` (default: 1), `JARVIS_RECALL_K` (default: 5), `JARVIS_RECALL_SCORE_MIN` (default: 0.55)

## Changelog

- 2026-05-13: Initial draft (Phase A MVP)
