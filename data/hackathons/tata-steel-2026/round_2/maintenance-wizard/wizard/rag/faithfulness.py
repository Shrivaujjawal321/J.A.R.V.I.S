"""
wizard.rag.faithfulness
=======================
NLI (Natural Language Inference) faithfulness gate.

Uses ``cross-encoder/nli-deberta-v3-small`` to score entailment of each
claim against its cited source chunk. This catches RAG hallucinations where
the LLM makes a claim not supported by the retrieved text.

Model: cross-encoder/nli-deberta-v3-small (~80 MB, CPU-only, ~80–120ms/claim)
Threshold: configurable (default 0.5 — calibrate empirically; literature says 0.6
  but that is for general NLI; steel-plant text needs empirical calibration).

The three output classes from the CrossEncoder are:
  index 0 → contradiction
  index 1 → entailment
  index 2 → neutral

We use entailment probability (index 1) as the faithfulness score.

[unverified] The 0.6 threshold is calibrated for SNLI/MultiNLI.
Calibrate on 20 synthetic Q&A pairs from the synthetic corpus before setting final threshold.

Integration:
  Called after LLM generation, before returning DiagnosisReport to the agent.
  If overall_faithfulness < threshold → returns flag=True → agent does one retry
  with a tighter grounding instruction.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from typing import Optional

from wizard.core.config import settings

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# NLI singleton
# ---------------------------------------------------------------------------

_nli_model = None


def _get_nli():
    """Load and cache the NLI cross-encoder model."""
    global _nli_model
    if _nli_model is None:
        try:
            from sentence_transformers import CrossEncoder  # type: ignore[import]
        except ImportError as exc:
            raise ImportError(
                "sentence-transformers is required for the faithfulness gate. "
                "Run: pip install sentence-transformers"
            ) from exc
        logger.info("Loading NLI model: %s", settings.nli_model)
        _nli_model = CrossEncoder(settings.nli_model)
        logger.info("NLI model loaded.")
    return _nli_model


# ---------------------------------------------------------------------------
# Output schema
# ---------------------------------------------------------------------------

@dataclass
class ClaimScore:
    """Entailment score for a single (claim, source_chunk) pair."""
    claim_text: str
    cited_chunk_id: str        # which source chunk was cited
    cited_chunk_preview: str   # first 200 chars of the source chunk
    entailment_prob: float     # p(entailment) ∈ [0, 1]
    contradiction_prob: float  # p(contradiction) ∈ [0, 1]
    neutral_prob: float        # p(neutral) ∈ [0, 1]
    is_faithful: bool          # entailment_prob >= threshold


@dataclass
class FaithfulnessResult:
    """
    Result of the NLI faithfulness gate for a complete LLM response.

    Attributes
    ----------
    overall_faithfulness:
        Mean entailment probability across all cited claims.
        1.0 if no citations found (no gate to apply).
    claim_scores:
        Per-claim breakdown.
    flag_for_retry:
        True if overall_faithfulness < threshold → caller should retry generation.
    confidence:
        'verified' if ≥0.75, 'unverified' if ≥0.5, 'low' otherwise.
    unfaithful_claims:
        Claims that failed the gate (entailment < threshold).
    """
    overall_faithfulness: float = 1.0
    claim_scores: list[ClaimScore] = field(default_factory=list)
    flag_for_retry: bool = False
    confidence: str = "unverified"  # 'verified'|'unverified'|'low'
    unfaithful_claims: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Main gate function
# ---------------------------------------------------------------------------

def run_faithfulness_gate(
    answer_text: str,
    retrieved_chunks: list,  # list[RetrievedChunk] from retriever
    threshold: float = 0.5,
) -> FaithfulnessResult:
    """
    Score every [N]-cited claim in ``answer_text`` against its source chunk.

    Parameters
    ----------
    answer_text:
        The raw LLM-generated answer string containing inline [N] markers.
    retrieved_chunks:
        Ordered list of RetrievedChunk objects (index 0 = Source [1]).
    threshold:
        Minimum entailment probability to consider a claim "faithful".
        [unverified] 0.5 is conservative; calibrate upward after testing.

    Returns
    -------
    FaithfulnessResult
    """
    if not settings.rag_nli_gate_enabled:
        logger.debug("NLI gate disabled via settings.")
        return FaithfulnessResult(overall_faithfulness=1.0, confidence="unverified")

    if not answer_text or not retrieved_chunks:
        return FaithfulnessResult(overall_faithfulness=1.0, confidence="unverified")

    # Extract sentences that contain at least one [N] citation marker
    # Regex: captures sentence-like spans ending with . ! ? or end-of-string
    cited_sentences = _extract_cited_sentences(answer_text)
    if not cited_sentences:
        logger.debug("No cited sentences found in answer — skipping NLI gate.")
        return FaithfulnessResult(overall_faithfulness=1.0, confidence="unverified")

    # Build (claim, source_chunk_text) pairs for batch NLI prediction
    pairs: list[tuple[str, str]] = []
    meta: list[tuple[str, str, str]] = []  # (claim_text, chunk_id, chunk_preview)

    chunk_map: dict[int, object] = {}  # 1-indexed citation number → RetrievedChunk
    for i, chunk in enumerate(retrieved_chunks, start=1):
        chunk_map[i] = chunk

    for sentence, cite_nums in cited_sentences:
        for cite_num in cite_nums:
            chunk = chunk_map.get(cite_num)
            if chunk is None:
                continue
            chunk_text = getattr(chunk, "text", "")
            pairs.append((sentence, chunk_text))
            chunk_id = getattr(chunk, "chunk_id", "")
            meta.append((sentence, chunk_id, chunk_text[:200]))

    if not pairs:
        return FaithfulnessResult(overall_faithfulness=1.0, confidence="unverified")

    # Batch NLI inference
    try:
        nli = _get_nli()
        raw_scores = nli.predict(pairs, apply_softmax=True)
        # raw_scores shape: (N, 3) — [contradiction, entailment, neutral]
    except Exception as exc:
        logger.warning("NLI inference failed: %s — skipping gate.", exc)
        return FaithfulnessResult(overall_faithfulness=1.0, confidence="unverified")

    # Aggregate claim scores
    claim_scores: list[ClaimScore] = []
    unfaithful: list[str] = []

    for (claim_text, chunk_id, chunk_preview), score_row in zip(meta, raw_scores):
        contradiction_p = float(score_row[0])
        entailment_p = float(score_row[1])
        neutral_p = float(score_row[2])
        is_faithful = entailment_p >= threshold

        cs = ClaimScore(
            claim_text=claim_text,
            cited_chunk_id=chunk_id,
            cited_chunk_preview=chunk_preview,
            entailment_prob=entailment_p,
            contradiction_prob=contradiction_p,
            neutral_prob=neutral_p,
            is_faithful=is_faithful,
        )
        claim_scores.append(cs)
        if not is_faithful:
            unfaithful.append(claim_text[:120])

    overall = (
        sum(cs.entailment_prob for cs in claim_scores) / len(claim_scores)
        if claim_scores
        else 1.0
    )
    flag = overall < threshold
    if overall >= 0.75:
        confidence = "verified"
    elif overall >= 0.5:
        confidence = "unverified"
    else:
        confidence = "low"

    logger.debug(
        "NLI gate: overall_faithfulness=%.3f, flag=%s, %d claims scored.",
        overall, flag, len(claim_scores),
    )

    return FaithfulnessResult(
        overall_faithfulness=round(overall, 4),
        claim_scores=claim_scores,
        flag_for_retry=flag,
        confidence=confidence,
        unfaithful_claims=unfaithful,
    )


# ---------------------------------------------------------------------------
# Helper: extract cited sentences
# ---------------------------------------------------------------------------

_CITATION_PATTERN = re.compile(r"\[(\d+)\]")
_SENTENCE_SPLITTER = re.compile(r"(?<=[.!?])\s+")


def _extract_cited_sentences(text: str) -> list[tuple[str, list[int]]]:
    """
    Split ``text`` into sentences and return those that contain [N] markers.

    Returns list of (sentence_text, [citation_numbers]).
    """
    # Split on sentence boundaries (crude but fast)
    # Also consider newlines as possible sentence ends
    normalized = text.replace("\n", " ")
    sentences = _SENTENCE_SPLITTER.split(normalized)

    result: list[tuple[str, list[int]]] = []
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
        cite_matches = _CITATION_PATTERN.findall(sentence)
        if cite_matches:
            cite_nums = [int(n) for n in cite_matches]
            result.append((sentence, cite_nums))
    return result


# ---------------------------------------------------------------------------
# Convenience: update RetrievedChunk faithfulness scores in-place
# ---------------------------------------------------------------------------

def apply_faithfulness_scores(
    chunks: list,  # list[RetrievedChunk]
    result: FaithfulnessResult,
) -> list:
    """
    Update ``RetrievedChunk.faithfulness_score`` in-place based on NLI results.

    Per-chunk score = min entailment probability of all claims citing that chunk.
    If a chunk had no claims citing it, score stays 1.0 (benefit of doubt).

    Returns the updated chunks list.
    """
    # Aggregate scores per chunk_id
    chunk_scores: dict[str, list[float]] = {}
    for cs in result.claim_scores:
        chunk_scores.setdefault(cs.cited_chunk_id, []).append(cs.entailment_prob)

    for chunk in chunks:
        cid = getattr(chunk, "chunk_id", "")
        if cid in chunk_scores:
            chunk.faithfulness_score = round(min(chunk_scores[cid]), 4)
        else:
            chunk.faithfulness_score = 1.0

    return chunks
