"""
wizard.rag.tools
================
LangGraph ToolNode-compatible wrappers for the RAG retrieval pipeline.

These are the entry points that the agentic core (wizard.agents.graph) imports
and registers as tools in the LangGraph ReAct node.

Exported tools:
  - ``retrieve_context``  — main RAG tool called by Diagnosis, RCA, Plan agents.
  - ``search_manuals``    — alias with doc_type filter preset to ['manual', 'sop'].
  - ``search_incident_log`` — alias with doc_type filter preset to ['failure_analysis', 'incident_summary'].

All tools return a ``ContextResult`` Pydantic model so LangGraph can validate
tool outputs against the typed MaintenanceState.

Tool signature convention (LangGraph ToolNode-compatible):
  - Input: plain keyword arguments (str, list[str], int, bool)
  - Output: dict (JSON-serialisable) — LangGraph serialises tool outputs to state

Usage in agent graph::

    from wizard.rag.tools import retrieve_context, search_manuals
    tools = [retrieve_context, search_manuals]
    agent = create_react_agent(llm, tools=tools)
"""

from __future__ import annotations

import logging
from typing import Annotated, Optional

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Output schema (returned by all RAG tools)
# ---------------------------------------------------------------------------

class ContextChunk(BaseModel):
    """Single retrieved + reranked chunk with citation metadata."""
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
    faithfulness_score: float = 0.0


class ContextResult(BaseModel):
    """
    Structured output returned by all RAG tools.

    Agents read ``context_block`` for LLM prompt injection and
    ``cited_sources`` for DiagnosisReport / MaintenanceRecommendation population.
    """
    query: str
    equipment_id: Optional[str] = None
    chunks: list[ContextChunk] = Field(default_factory=list)
    context_block: str = Field(
        default="",
        description="Formatted 'Source [N]' block ready for prompt injection",
    )
    cited_sources: list[dict] = Field(
        default_factory=list,
        description="Citation dicts for DiagnosisReport.cited_sources",
    )
    chunk_count: int = 0
    retrieval_error: Optional[str] = None
    store_empty: bool = False


# ---------------------------------------------------------------------------
# Tool functions
# ---------------------------------------------------------------------------

def retrieve_context(
    query: str,
    equipment_id: Optional[str] = None,
    doc_types: Optional[list[str]] = None,
    top_k: int = 5,
) -> dict:
    """
    Retrieve relevant maintenance knowledge for a given query.

    Use this tool when you need to look up:
    - Maintenance procedures and SOPs
    - Equipment manuals and specifications
    - Historical failure analysis reports
    - Incident summaries and lessons learned

    Parameters
    ----------
    query:
        Natural-language question or search query. Be specific — include
        equipment codes, fault types, or procedure names when known.
    equipment_id:
        Optional equipment/asset ID to scope the search (e.g. 'EAF-04',
        'P80_BEARING'). If omitted, searches all equipment.
    doc_types:
        Optional list of document types to filter by.
        Valid values: 'manual', 'sop', 'failure_analysis', 'incident_summary'.
    top_k:
        Number of cited sources to return (default 5, max 10).

    Returns
    -------
    dict with keys:
        - context_block: formatted Source [N] text for prompt injection
        - cited_sources: list of citation dicts with doc_name, section, page
        - chunk_count: number of chunks returned
        - store_empty: True if the knowledge base has no documents yet
    """
    top_k = min(max(1, top_k), 10)  # clamp 1–10

    try:
        from wizard.rag.retriever import retrieve, format_context_block, chunks_to_cited_sources

        chunks = retrieve(
            query=query,
            equipment_id=equipment_id,
            doc_types=doc_types,
            top_k=top_k,
        )

        if not chunks:
            logger.debug("retrieve_context: no chunks for query '%s...'", query[:50])
            result = ContextResult(
                query=query,
                equipment_id=equipment_id,
                store_empty=True,
                context_block="[No relevant documents found in the knowledge base.]",
            )
            return result.model_dump()

        context_block = format_context_block(chunks)
        cited_sources = chunks_to_cited_sources(chunks)

        context_chunks = [
            ContextChunk(
                chunk_id=c.chunk_id,
                text=c.text,
                doc_name=c.doc_name,
                section=c.section,
                page_or_step=c.page_or_step,
                doc_type=c.doc_type,
                equipment_id=c.equipment_id,
                asset_id=c.asset_id,
                criticality=c.criticality,
                rerank_score=c.rerank_score,
                faithfulness_score=c.faithfulness_score,
            )
            for c in chunks
        ]

        result = ContextResult(
            query=query,
            equipment_id=equipment_id,
            chunks=context_chunks,
            context_block=context_block,
            cited_sources=cited_sources,
            chunk_count=len(chunks),
        )
        logger.debug("retrieve_context: returned %d chunks.", len(chunks))
        return result.model_dump()

    except Exception as exc:
        logger.error("retrieve_context failed: %s", exc, exc_info=True)
        error_result = ContextResult(
            query=query,
            equipment_id=equipment_id,
            retrieval_error=str(exc),
            context_block=f"[Retrieval error: {exc}]",
        )
        return error_result.model_dump()


def search_manuals(
    query: str,
    equipment_id: Optional[str] = None,
    top_k: int = 5,
) -> dict:
    """
    Search equipment manuals and SOPs for maintenance procedures.

    Scoped to doc_types=['manual', 'sop']. Use this when looking up
    specific procedures, specifications, or maintenance intervals.

    Parameters
    ----------
    query:
        Procedure or specification to look up.
    equipment_id:
        Optional equipment ID to scope the search.
    top_k:
        Number of results (default 5).

    Returns
    -------
    dict — same structure as retrieve_context.
    """
    return retrieve_context(
        query=query,
        equipment_id=equipment_id,
        doc_types=["manual", "sop"],
        top_k=top_k,
    )


def search_incident_log(
    query: str,
    equipment_id: Optional[str] = None,
    top_k: int = 5,
) -> dict:
    """
    Search historical failure analysis reports and incident summaries.

    Scoped to doc_types=['failure_analysis', 'incident_summary']. Use this
    for RCA support — finding similar past failures and their root causes.

    Parameters
    ----------
    query:
        Failure pattern or fault description to search.
    equipment_id:
        Optional equipment ID to narrow the search.
    top_k:
        Number of results (default 5).

    Returns
    -------
    dict — same structure as retrieve_context.
    """
    return retrieve_context(
        query=query,
        equipment_id=equipment_id,
        doc_types=["failure_analysis", "incident_summary"],
        top_k=top_k,
    )


# ---------------------------------------------------------------------------
# LangGraph tool list — import this in wizard.agents.graph
# ---------------------------------------------------------------------------

RAG_TOOLS = [retrieve_context, search_manuals, search_incident_log]
"""
All RAG tools in one list. Register in LangGraph::

    from wizard.rag.tools import RAG_TOOLS
    from langgraph.prebuilt import create_react_agent
    agent = create_react_agent(llm, tools=RAG_TOOLS)
"""
