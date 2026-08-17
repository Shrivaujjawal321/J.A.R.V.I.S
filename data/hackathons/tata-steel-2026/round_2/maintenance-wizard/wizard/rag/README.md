# wizard.rag — RAG Layer

LanceDB-backed hybrid RAG for the Maintenance Wizard system.

## Architecture

```
PDF / Markdown / Text
        │
        ▼ pymupdf4llm
 Markdown text
        │
        ▼ MarkdownHeaderTextSplitter (## / ###)
 Section-aligned chunks
        │
        ▼ RecursiveCharacterTextSplitter (512 chars / 64 overlap)
 Token-bounded sub-chunks
        │
        ▼ (optional) LLM contextual prefix injection (HyDE-like, one-time)
 Prefixed chunks
        │
        ▼ bge-small-en-v1.5 (ONNX, 384-dim, L2-normalized)
 Embedding vectors
        │
        ▼ LanceDB insert (Lance columnar format, disk-backed)
 LanceDB chunks table (dense + BM25 FTS)

Query time:
  engineer query
       │
       ▼ HyDE (if query <= 12 tokens, one LLM call → hypothetical answer)
  embedded query vector
       │
       ▼ LanceDB hybrid search (query_type="hybrid")
       │   dense (cosine) + BM25 Tantivy FTS + SQL prefilter on equipment_id / doc_type
       ▼
  top-20 candidate chunks
       │
       ▼ FlashRank (ms-marco-MiniLM-L-12-v2, ONNX, ~15-30ms for 30 candidates)
       ▼
  top-5 RetrievedChunk objects
       │
       ▼ format_context_block → "Source [N]" injection into LLM prompt
       │
       ▼ LLM generates answer with inline [N] citations
       │
       ▼ NLI faithfulness gate (cross-encoder/nli-deberta-v3-small)
         per-claim entailment scoring; flag_for_retry if overall < threshold
```

## Files

| File | Purpose |
|---|---|
| `store.py` | LanceDB connection + PyArrow schema + FTS index management |
| `embedder.py` | bge-small-en-v1.5 (ONNX) singleton; `embed_texts()`, `embed_single()` |
| `ingestion.py` | PDF/MD/text → chunk → embed → LanceDB insert (idempotent) |
| `retriever.py` | Hybrid query + HyDE + FlashRank → `list[RetrievedChunk]` |
| `faithfulness.py` | NLI gate: per-claim entailment scoring, `FaithfulnessResult` |
| `tools.py` | LangGraph-compatible tool wrappers: `retrieve_context`, `search_manuals`, `search_incident_log` |
| `__init__.py` | Clean public surface re-export |
| `smoke_rag.py` | Self-contained smoke test (5 toy docs → query → assert citations) |

## Integration Contract

```python
# Agents import these exact names:
from wizard.rag import retrieve, ingest_text, ingest_directory
from wizard.rag import run_faithfulness_gate, apply_faithfulness_scores
from wizard.rag import format_context_block, chunks_to_cited_sources
from wizard.rag import RetrievedChunk, ContextResult, FaithfulnessResult
from wizard.rag import retrieve_context, search_manuals, search_incident_log, RAG_TOOLS
from wizard.rag import get_store, get_table, ensure_fts_index
```

### Key function signatures

```python
# Retrieval (main entry point)
def retrieve(
    query: str,
    equipment_id: Optional[str] = None,    # SQL prefilter
    doc_types: Optional[list[str]] = None, # SQL prefilter
    top_k: int = 5,                         # final ranked count
    use_hyde: Optional[bool] = None,        # override settings
    db=None,                                # LanceDB connection (auto-opens if None)
) -> list[RetrievedChunk]: ...

# Ingestion
def ingest_text(
    text: str,
    doc_name: str,
    asset_id: str = "unknown",
    equipment_id: str = "unknown",
    equipment_type: str = "unknown",
    doc_type: str = "manual",
    criticality: str = "medium",
    revision: str = "",
    source_entity_id: str = "",
    source_entity_type: str = "knowledge_doc",
    use_contextual_prefix: bool = False,    # LLM prefix injection
    db=None,
) -> int: ...                               # number of new chunks inserted

# NLI gate
def run_faithfulness_gate(
    answer_text: str,
    retrieved_chunks: list[RetrievedChunk],
    threshold: float = 0.5,
) -> FaithfulnessResult: ...

# LangGraph tool
def retrieve_context(
    query: str,
    equipment_id: Optional[str] = None,
    doc_types: Optional[list[str]] = None,
    top_k: int = 5,
) -> dict: ...   # returns ContextResult.model_dump()
```

### RetrievedChunk fields
```python
@dataclass
class RetrievedChunk:
    chunk_id: str
    text: str
    doc_name: str
    section: str
    page_or_step: str
    doc_type: str
    equipment_id: str
    asset_id: str
    criticality: str
    rerank_score: float
    hybrid_score: float
    faithfulness_score: float  # filled by NLI gate
```

## Smoke Test

```bash
cd maintenance-wizard
python -m wizard.rag.smoke_rag
```

Expected output (9 tests, all PASS):
- Store created
- Empty store returns [] gracefully
- 5 toy docs ingested (N total chunks)
- General query returns chunks with required fields
- Equipment-scoped query filters correctly
- Source [N] context block generated
- retrieve_context tool returns ContextResult dict
- NLI gate runs and returns valid FaithfulnessResult
- Re-ingest returns 0 new chunks (idempotent)

## Dependencies (heavy — note in needed_deps)

| Package | Version | Role |
|---|---|---|
| `lancedb` | >=0.20.0 | Embedded vector store + native hybrid BM25+dense |
| `sentence-transformers` | >=3.0 | bge-small-en-v1.5 embedder + NLI CrossEncoder |
| `onnxruntime` | >=1.18 | ONNX inference backend (1.4–3× CPU speedup) |
| `flashrank` | 0.2.10 | CPU cross-encoder reranker (ms-marco-MiniLM-L-12-v2) |
| `pymupdf4llm` | >=0.0.17 | PDF → Markdown with layout preservation |
| `langchain-text-splitters` | 0.3.x | MarkdownHeaderTextSplitter + RecursiveCharacterTextSplitter |
| `pyarrow` | >=15.0 | LanceDB data format (auto-installed with lancedb) |

All are pip-installable. No Docker required. CPU-only. No GPU needed.
