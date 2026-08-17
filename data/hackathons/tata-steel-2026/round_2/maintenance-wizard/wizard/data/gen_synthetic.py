"""
wizard/data/gen_synthetic.py
============================
Entrypoint: generate ~200 synthetic knowledge-base documents (offline/template-only,
no LLM key needed) and ingest them into the LanceDB RAG store.

Idempotent — LanceDB chunk deduplication via content-hash means re-running skips
already-ingested chunks.  The data/synthetic/ directory is also written atomically.

Usage::
    python wizard/data/gen_synthetic.py [--count N] [--seed S]
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

# Ensure repo root is on sys.path when run as a script
_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("gen_synthetic")


def main(count: int = 200, seed: int = 42) -> int:
    """
    Generate `count` synthetic documents and ingest into LanceDB.
    Returns number of RAG chunks inserted.
    """
    from wizard.core.db import init_db
    from wizard.knowledge.generator import KnowledgeBaseGenerator
    from wizard.rag.ingestion import ingest_text
    from wizard.rag.store import get_store

    # ---------- 1. Init DB (idempotent) ----------
    log.info("Initialising wizard.db …")
    init_db()

    # ---------- 2. Generate synthetic docs ----------
    log.info("Generating %d synthetic documents (offline/template-only, seed=%d) …", count, seed)
    gen = KnowledgeBaseGenerator(
        seed=seed,
        noise_fraction=0.15,
        use_llm=False,
    )
    docs = gen.run(total=count)
    log.info(
        "Generation complete: %d docs | by_type=%s | noise=%d | entities_persisted=%d",
        len(docs),
        gen.stats.by_type,
        gen.stats.noise_injected,
        gen.stats.entities_persisted,
    )

    # ---------- 3. Ingest into LanceDB RAG store ----------
    log.info("Ingesting generated docs into LanceDB RAG store …")
    db = get_store()

    total_chunks = 0
    for doc in docs:
        try:
            n = ingest_text(
                text=doc.content_markdown,
                doc_name=doc.title,
                asset_id=doc.asset_id,
                equipment_id=doc.asset_id,
                equipment_type=doc.equipment_class,
                doc_type=doc.doc_type,
                criticality="high" if "critical" in doc.equipment_class else "medium",
                revision=doc.revision,
                source_entity_id=doc.doc_id,
                source_entity_type="knowledge_doc",
                use_contextual_prefix=False,   # no LLM key required
                db=db,
            )
            total_chunks += n
        except Exception as exc:
            log.warning("Ingest failed for doc %s: %s", doc.doc_id, exc)

    log.info("RAG ingest complete: %d chunks inserted across %d docs", total_chunks, len(docs))
    return total_chunks


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate synthetic KB docs + ingest into RAG store")
    parser.add_argument("--count", type=int, default=200,
                        help="Number of documents to generate (default: 200)")
    parser.add_argument("--seed", type=int, default=42,
                        help="Random seed (default: 42)")
    args = parser.parse_args()

    chunks = main(count=args.count, seed=args.seed)
    log.info("Done. Total RAG chunks in store: %d", chunks)
    sys.exit(0)
