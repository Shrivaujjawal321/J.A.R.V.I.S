"""
episodic_memory.py — Jarvis vector memory layer

Wraps ChromaDB + sentence-transformers (all-MiniLM-L6-v2) to give Jarvis
semantic recall over its markdown knowledge base.

Usage:
    from scripts.episodic_memory import EpisodicMemory

    mem = EpisodicMemory()
    mem.add("Boss prefers Hinglish", source="memory/preferences.md")
    results = mem.recall("how does Boss communicate", k=5)
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

# ── Constants ──────────────────────────────────────────────────────────────────

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CHROMA_DIR = PROJECT_ROOT / "data" / "memory" / "chroma"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
MAX_FILE_SIZE = 1 * 1024 * 1024  # 1 MB
CHUNK_TARGET_TOKENS = 500          # approximate; 1 token ≈ 4 chars
CHUNK_OVERLAP_CHARS = 100


# ── Lazy globals (loaded once, reused) ────────────────────────────────────────

_embedding_fn = None


def _get_embedding_fn():
    """Load sentence-transformer embedding function (downloads model on first call)."""
    global _embedding_fn
    if _embedding_fn is not None:
        return _embedding_fn

    try:
        from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
    except ImportError:
        # Older chroma API path
        from chromadb.utils.embedding_functions import (  # type: ignore
            SentenceTransformerEmbeddingFunction,
        )

    print(
        f"[episodic_memory] Loading embedding model '{EMBEDDING_MODEL}' "
        "(first run downloads ~80 MB to ~/.cache/) ...",
        flush=True,
    )
    _embedding_fn = SentenceTransformerEmbeddingFunction(model_name=EMBEDDING_MODEL)
    print("[episodic_memory] Embedding model ready.", flush=True)
    return _embedding_fn


# ── Chunking ──────────────────────────────────────────────────────────────────

def _chunk_markdown(text: str, source: str) -> list[dict[str, Any]]:
    """
    Split markdown text into ~500-token chunks at heading / blank-line boundaries.
    Returns list of dicts: {text, chunk_index, section, source}.
    """
    # Normalise line endings
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Split on heading lines or double blank lines (paragraph boundaries)
    # Keep the delimiter as the start of the next chunk
    pattern = re.compile(r"(?=^#{1,6}\s)", re.MULTILINE)
    raw_sections = pattern.split(text)

    # If no headings, fall back to splitting on double newlines
    if len(raw_sections) <= 1:
        raw_sections = re.split(r"\n\n+", text)

    chunks: list[dict[str, Any]] = []
    current_section = ""

    for section_text in raw_sections:
        section_text = section_text.strip()
        if not section_text:
            continue

        # Detect section heading for metadata
        heading_match = re.match(r"^(#{1,6})\s+(.*)", section_text)
        if heading_match:
            current_section = heading_match.group(2).strip()

        # If section is short enough, keep as one chunk
        if len(section_text) <= CHUNK_TARGET_TOKENS * 4:
            chunks.append({
                "text": section_text,
                "section": current_section,
                "source": source,
                "chunk_index": len(chunks),
            })
        else:
            # Hard-split long sections with overlap
            start = 0
            while start < len(section_text):
                end = start + CHUNK_TARGET_TOKENS * 4
                chunk_text = section_text[start:end].strip()
                if chunk_text:
                    chunks.append({
                        "text": chunk_text,
                        "section": current_section,
                        "source": source,
                        "chunk_index": len(chunks),
                    })
                start = end - CHUNK_OVERLAP_CHARS

    return chunks


# ── Core class ────────────────────────────────────────────────────────────────

class EpisodicMemory:
    """
    Semantic memory layer for Jarvis, backed by ChromaDB + sentence-transformers.

    All data is persisted to `data/memory/chroma/` in the project root.
    The embedding model runs fully locally — no API keys needed.
    """

    def __init__(self, collection_name: str = "jarvis"):
        import chromadb

        CHROMA_DIR.mkdir(parents=True, exist_ok=True)
        self._client = chromadb.PersistentClient(path=str(CHROMA_DIR))
        self._ef = _get_embedding_fn()
        self._col = self._client.get_or_create_collection(
            name=collection_name,
            embedding_function=self._ef,
            metadata={"hnsw:space": "cosine"},
        )

    # ── Public API ────────────────────────────────────────────────────────────

    def add(
        self,
        text: str,
        source: str = "manual",
        metadata: dict[str, Any] | None = None,
    ) -> str | None:
        """
        Add a single text passage to memory.

        Returns the document ID if added, None if it was a duplicate.
        """
        text = text.strip()
        if not text:
            return None

        doc_id = self._content_hash(text, source)

        # Deduplication — skip if this exact content is already indexed
        existing = self._col.get(ids=[doc_id])
        if existing["ids"]:
            return None

        meta = {
            "source": source,
            "added_at": datetime.utcnow().isoformat(),
            **(metadata or {}),
        }
        self._col.add(documents=[text], ids=[doc_id], metadatas=[meta])
        return doc_id

    def add_chunks(self, chunks: list[dict[str, Any]]) -> int:
        """
        Batch-add pre-split chunks. Each chunk must have 'text' and 'source' keys.
        Returns count of newly added chunks (skipping duplicates).
        """
        if not chunks:
            return 0

        ids, docs, metas = [], [], []
        for chunk in chunks:
            text = chunk.get("text", "").strip()
            if not text:
                continue
            source = chunk.get("source", "unknown")
            doc_id = self._content_hash(text, source)

            meta: dict[str, Any] = {
                "source": source,
                "section": chunk.get("section", ""),
                "chunk_index": chunk.get("chunk_index", 0),
                "added_at": datetime.utcnow().isoformat(),
            }
            # Carry through any extra metadata keys
            for k, v in chunk.items():
                if k not in ("text", "source", "section", "chunk_index"):
                    meta[k] = v

            ids.append(doc_id)
            docs.append(text)
            metas.append(meta)

        if not ids:
            return 0

        # Check which IDs already exist (bulk)
        existing = self._col.get(ids=ids)
        existing_set = set(existing["ids"])
        new_ids = [i for i in ids if i not in existing_set]

        if not new_ids:
            return 0

        # Only insert new ones
        mask = [ids.index(i) for i in new_ids]
        self._col.add(
            documents=[docs[i] for i in mask],
            ids=new_ids,
            metadatas=[metas[i] for i in mask],
        )
        return len(new_ids)

    def add_file(self, path: str | Path) -> int:
        """
        Ingest a single markdown file.
        Returns count of new chunks added (0 if file was unchanged/already indexed).
        """
        path = Path(path)
        if not path.exists():
            print(f"[episodic_memory] SKIP (not found): {path}", file=sys.stderr)
            return 0

        if path.stat().st_size > MAX_FILE_SIZE:
            print(f"[episodic_memory] SKIP (>1 MB): {path}", file=sys.stderr)
            return 0

        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except Exception as exc:
            print(f"[episodic_memory] SKIP (read error {exc}): {path}", file=sys.stderr)
            return 0

        source = str(path.relative_to(PROJECT_ROOT)) if path.is_relative_to(PROJECT_ROOT) else str(path)
        chunks = _chunk_markdown(text, source=source)
        added = self.add_chunks(chunks)
        return added

    def add_directory(self, path: str | Path, pattern: str = "*.md") -> dict[str, int]:
        """
        Bulk-ingest all files matching `pattern` under `path`.
        Returns {file_path: chunks_added} mapping.
        """
        path = Path(path)
        results: dict[str, int] = {}
        for file in sorted(path.glob(pattern)):
            if file.is_file():
                added = self.add_file(file)
                results[str(file)] = added
        return results

    def recall(
        self,
        query: str,
        k: int = 5,
        filter: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """
        Semantic search over memory.

        Returns list of:
            {text, source, section, score, metadata}
        Sorted by relevance (highest first).
        """
        count = self._col.count()
        if count == 0:
            return []

        k = min(k, count)

        query_params: dict[str, Any] = {
            "query_texts": [query],
            "n_results": k,
            "include": ["documents", "metadatas", "distances"],
        }
        if filter:
            query_params["where"] = filter

        res = self._col.query(**query_params)

        results = []
        for doc, meta, dist in zip(
            res["documents"][0],
            res["metadatas"][0],
            res["distances"][0],
        ):
            # Chroma cosine distance: 0 = identical, 2 = opposite
            # Convert to similarity score 0..1
            score = round(1.0 - dist / 2.0, 4)
            results.append({
                "text": doc,
                "source": meta.get("source", ""),
                "section": meta.get("section", ""),
                "score": score,
                "metadata": meta,
            })

        return results

    def forget(self, source: str) -> int:
        """
        Delete all chunks from a given source path (for re-ingestion after edits).
        Returns count of deleted chunks.
        """
        existing = self._col.get(where={"source": source})
        ids_to_delete = existing["ids"]
        if ids_to_delete:
            self._col.delete(ids=ids_to_delete)
        return len(ids_to_delete)

    def stats(self) -> dict[str, Any]:
        """Return quick stats: total chunks, unique sources, last-added timestamp."""
        all_metas = self._col.get(include=["metadatas"])["metadatas"]
        sources = {m.get("source", "") for m in all_metas}
        timestamps = [m.get("added_at", "") for m in all_metas if m.get("added_at")]
        last_added = max(timestamps) if timestamps else None

        return {
            "total_chunks": len(all_metas),
            "unique_sources": len(sources),
            "sources": sorted(sources),
            "last_added": last_added,
        }

    # ── Private helpers ───────────────────────────────────────────────────────

    @staticmethod
    def _content_hash(text: str, source: str) -> str:
        """Stable ID = SHA-256 of (source + text). Used for deduplication."""
        payload = f"{source}||{text}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:32]
