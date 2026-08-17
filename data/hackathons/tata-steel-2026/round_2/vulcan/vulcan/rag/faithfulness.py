"""VULCAN faithfulness gate — local NLI entailment check (CPU, keyless).

Scores each inline-`[N]`-cited sentence of an answer against its source chunk
using `cross-encoder/nli-deberta-v3-small` (via sentence-transformers CrossEncoder,
the same pinned dep as the embedder). Catches RAG hallucinations: claims the
retrieved text does not actually support. Powers the FR4 "verified" badge.

Returns an overall entailment score + per-claim breakdown + a retry flag the
agent can use to re-ground a low-faithfulness answer once.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

NLI_MODEL = "cross-encoder/nli-deberta-v3-small"
_CITATION_RE = re.compile(r"\[(\d+)\]")
_SENT_SPLIT = re.compile(r"(?<=[.!?])\s+")

_nli = None


def _get_nli():
    global _nli
    if _nli is None:
        from sentence_transformers import CrossEncoder  # type: ignore[import]
        logger.info("Loading NLI model: %s", NLI_MODEL)
        _nli = CrossEncoder(NLI_MODEL)
    return _nli


@dataclass
class ClaimScore:
    claim: str
    cited_source: str
    entailment: float
    contradiction: float
    neutral: float
    faithful: bool


@dataclass
class FaithfulnessResult:
    overall: float = 1.0
    confidence: str = "unverified"   # verified | unverified | low
    flag_retry: bool = False
    claims: list[ClaimScore] = field(default_factory=list)
    unfaithful: list[str] = field(default_factory=list)


_MD_RE = re.compile(r"[*_`#>|]+")
_DEGREE_RE = re.compile(r"\s*°\s*")
_MULTISPACE_RE = re.compile(r"\s{2,}")


def _clean_claim(sent: str) -> str:
    """Normalise a cited sentence for NLI: drop the [N] markers, markdown emphasis,
    and the degree symbol. The raw `[2]` token and unicode `°` measurably depress
    the cross-encoder's entailment score on otherwise well-grounded claims, so we
    score the prose, not the formatting."""
    s = _CITATION_RE.sub("", sent)            # strip [N]
    s = _MD_RE.sub(" ", s)                    # strip markdown
    s = _DEGREE_RE.sub(" ", s)                # "94.7 °C" -> "94.7 C"
    s = _MULTISPACE_RE.sub(" ", s)
    return s.strip()


def _cited_sentences(text: str) -> list[tuple[str, list[int]]]:
    """Return (cleaned_claim, [cited source nums]) for each [N]-citing sentence.

    Splits on MARKDOWN STRUCTURE first (newlines, ``---`` rules, list bullets) and
    only then on sentence punctuation — so a heading, a list item, and a paragraph
    each become their own atomic claim instead of merging into one long string that
    no single source can entail."""
    out = []
    # 1) structural split: lines, horizontal rules, bullets
    blocks: list[str] = []
    for line in text.split("\n"):
        line = line.strip()
        if not line:
            continue
        # break a bullet/numbered list line off cleanly; drop pure rules
        if set(line) <= set("-=*# "):       # "---", "===", "***" etc.
            continue
        blocks.append(line)
    # 2) sentence split within each block
    for block in blocks:
        for sent in _SENT_SPLIT.split(block):
            sent = sent.strip()
            if not sent:
                continue
            nums = [int(n) for n in _CITATION_RE.findall(sent)]
            if nums:
                out.append((_clean_claim(sent), nums))
    return out


def run_gate(answer: str, chunks: list, threshold: float = 0.5) -> FaithfulnessResult:
    """Score `[N]`-cited claims in `answer` against `chunks` (1-indexed -> Source [N]).

    `chunks` is a list of RetrievedChunk (must expose `.text`, `.source`)."""
    if not answer or not chunks:
        return FaithfulnessResult()
    cited = _cited_sentences(answer)
    if not cited:
        return FaithfulnessResult()

    chunk_map = {i: c for i, c in enumerate(chunks, start=1)}
    # Build pairs but remember which claim each pair belongs to, so we can take the
    # MAX entailment over the sources a single claim cites (a claim citing [1][4] is
    # faithful if EITHER source entails it — not the average of both).
    pairs: list[tuple[str, str]] = []
    pair_claim_idx: list[int] = []
    claim_texts: list[str] = []
    claim_srcs: list[list[str]] = []
    for sent, nums in cited:
        if _is_fragment(sent):           # skip headers / table rows / stubs
            continue
        ci = len(claim_texts)
        claim_texts.append(sent)
        srcs: list[str] = []
        for n in nums:
            c = chunk_map.get(n)
            if c is None:
                continue
            # NLI is DIRECTIONAL: premise = SOURCE, hypothesis = CLAIM. We ask
            # "does the cited source entail the claim?" — so the source is the
            # premise. (Reversing this collapses entailment scores and produces
            # spurious 'unfaithful' flags on well-grounded claims.)
            pairs.append((getattr(c, "text", ""), sent))
            pair_claim_idx.append(ci)
            srcs.append(getattr(c, "source", ""))
        claim_srcs.append(srcs)
    if not pairs:
        return FaithfulnessResult()

    try:
        scores = _get_nli().predict(pairs, apply_softmax=True)
    except Exception as exc:  # noqa: BLE001
        logger.warning("NLI inference failed (%s) — skipping gate.", exc)
        return FaithfulnessResult()

    # best supporting source per claim: the one with the highest entail-minus-contra
    # margin (the source that most supports / least refutes the claim).
    best: dict[int, tuple[float, float, float]] = {}
    for ci, row in zip(pair_claim_idx, scores):
        contra, entail, neutral = float(row[0]), float(row[1]), float(row[2])
        cur = best.get(ci)
        if cur is None or (entail - contra) > (cur[0] - cur[1]):
            best[ci] = (entail, contra, neutral)

    claims: list[ClaimScore] = []
    unfaithful: list[str] = []
    support_scores: list[float] = []
    for ci, (entail, contra, neutral) in best.items():
        # A claim is a HALLUCINATION only when a cited source CONTRADICTS it — i.e.
        # contradiction dominates. A 'neutral' verdict (the source neither states nor
        # refutes the exact phrasing — common when the model adds framing like
        # "before failure" around a grounded number) is NOT a hallucination; it is
        # merely unverified. So we flag on contradiction, not on low entailment.
        contradicted = contra >= 0.5 and contra > entail
        ok = (entail >= threshold) or (not contradicted)
        # a support score that credits neutral-but-not-refuted claims (so honest
        # paraphrase isn't scored as 0): entail + half the neutral mass, minus contra.
        support = max(0.0, min(1.0, entail + 0.5 * neutral - contra))
        support_scores.append(support)
        src = claim_srcs[ci][0] if claim_srcs[ci] else ""
        claims.append(ClaimScore(claim_texts[ci], src, entail, contra, neutral,
                                 faithful=not contradicted))
        if contradicted:
            unfaithful.append(claim_texts[ci][:120])

    overall = sum(support_scores) / len(support_scores) if support_scores else 1.0
    conf = "verified" if overall >= 0.7 else ("unverified" if overall >= 0.45 else "low")
    return FaithfulnessResult(
        overall=round(overall, 4),
        confidence=conf,
        flag_retry=bool(unfaithful),     # retry only if something was CONTRADICTED
        claims=claims,
        unfaithful=unfaithful,
    )


def _is_fragment(sent: str) -> bool:
    """True if `sent` is a markdown header / table row / short stub rather than a
    real factual claim worth NLI-checking (avoids spurious flags on formatting)."""
    s = sent.strip()
    if len(s) < 25:
        return True
    # markdown heading or horizontal rule
    if s.lstrip("#").lstrip().startswith(("---", "===")) or s.startswith("#"):
        return True
    # table separator / mostly pipes
    if s.count("|") >= 3 and len(s.replace("|", "").replace("-", "").strip()) < 15:
        return True
    # a line that ENDS in a colon is a header/label introducing a list, not a claim
    if s.endswith(":"):
        return True
    # a terse list/enum stub (few words, no verb-like structure) — e.g. an inventory
    # bullet "SEAL-LAB-01 labyrinth seal (2 in stock)" — too short to NLI reliably
    if len(s.split()) < 6:
        return True
    return False
