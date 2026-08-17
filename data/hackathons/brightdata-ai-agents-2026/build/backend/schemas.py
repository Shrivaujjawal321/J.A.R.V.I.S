"""Pydantic v2 schemas for AltBrief — single source of truth for shapes."""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field


class SourceStatus(str, Enum):
    OK = "ok"
    TIMEOUT = "timeout"
    RATE_LIMITED = "rate_limited"
    BLOCKED = "blocked"
    CACHED = "cached"
    ERROR = "error"


class SourceResult(BaseModel):
    source: str
    status: SourceStatus
    data: dict | list | None = None
    error_msg: str | None = None
    latency_ms: int = 0
    cached: bool = False


class Signal(BaseModel):
    source: str = Field(description="Source identifier: sec, yahoo, reddit, linkedin, glassdoor, news, gdelt, satellite")
    direction: Literal["bullish", "bearish", "neutral"]
    summary: str = Field(max_length=240, description="One-sentence interpretation")
    confidence: float = Field(ge=0.0, le=1.0)
    raw_evidence: str = Field(max_length=600, description="Verbatim datum supporting the signal")
    citation_url: str | None = None
    research_anchor: str | None = Field(
        default=None,
        description="Academic citation if peer-reviewed (e.g. 'Cohen-Malloy-Pomorski JoF 2012')",
    )
    # Tier for UI: gold=peer-reviewed alpha, standard=buy-side alt-data, caution=low-alpha
    alpha_tier: Literal["gold", "standard", "caution"] = "standard"


class Contradiction(BaseModel):
    """
    A detected cross-source contradiction between two signals.
    Populated by detect_contradictions() in contradictions.py.
    Richer than a plain string — carries severity + type for UI rendering.
    """
    signal_a_source: str = Field(description="Name of the first source (e.g. 'SEC EDGAR')")
    signal_a_brief: str = Field(description="One-line summary of what signal A says")
    signal_b_source: str = Field(description="Name of the second source (e.g. 'LinkedIn Hiring')")
    signal_b_brief: str = Field(description="One-line summary of what signal B says")
    severity: Literal["high", "medium", "low"] = Field(
        description="high=opposing signals from high-quality sources; medium=one low-quality source; low=could be timing lag"
    )
    explanation: str = Field(description="One sentence in plain English explaining the contradiction")
    contradiction_type: Literal[
        "guidance_vs_hiring",
        "sentiment_divergence",
        "insider_vs_crowd",
        "operational_vs_guided",
        "employee_vs_growth",
        "other",
    ] = Field(description="Semantic category of the contradiction")

    def to_string(self) -> str:
        """Plain-text representation for synthesis prompt injection."""
        return (
            f"[{self.severity.upper()}] {self.signal_a_source} vs {self.signal_b_source}: "
            f"{self.explanation}"
        )


class InvestmentBrief(BaseModel):
    ticker: str
    company_name: str = ""
    sector: str = ""
    generated_at: datetime = Field(default_factory=datetime.utcnow)

    bull_thesis: list[str] = Field(default_factory=list, description="3-4 bullets")
    bear_case: list[str] = Field(default_factory=list, description="3-4 bullets")
    signals: list[Signal] = Field(default_factory=list)
    risk_factors: list[str] = Field(default_factory=list)

    # Structured contradiction objects (richer than list[str])
    contradictions: list[Contradiction] = Field(
        default_factory=list,
        description="NOVELTY ANCHOR — cross-source contradiction objects with severity + type",
    )
    # Backward-compat plain-text view (derived, not stored separately)
    cross_source_contradictions: list[str] = Field(
        default_factory=list,
        description="Plain-text version for backward-compat and synthesis prompt",
    )

    overall_direction: Literal["bullish", "bearish", "neutral"] = "neutral"
    overall_confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    price_target_range: dict | None = None  # {"low": float, "base": float, "high": float}

    brief_narrative: str = Field(default="", max_length=1200)
    data_quality_flag: Literal["full", "partial", "minimal"] = "full"
    sources_used: list[str] = Field(default_factory=list)
    sources_unavailable: list[str] = Field(default_factory=list)

    latency_seconds: float = 0.0
    cost_usd: float = 0.0

    def sync_contradiction_strings(self) -> "InvestmentBrief":
        """Populate cross_source_contradictions from structured contradictions list."""
        strings = [c.to_string() for c in self.contradictions]
        return self.model_copy(update={"cross_source_contradictions": strings})


class BriefEvent(BaseModel):
    """SSE event payload to frontend."""
    event_type: Literal[
        "started", "source_done", "source_failed", "synthesis_start",
        "narrative_chunk", "contradiction", "brief_ready", "done", "error",
    ]
    source: str | None = None
    progress: int = 0  # 0-100
    message: str | None = None
    data: dict | None = None


class SSEEvent(BaseModel):
    """Raw SSE event yielded by synthesize_brief()."""
    event_type: Literal[
        "source_done", "narrative_chunk", "contradiction", "brief", "done", "error"
    ]
    data: dict | str | None = None
