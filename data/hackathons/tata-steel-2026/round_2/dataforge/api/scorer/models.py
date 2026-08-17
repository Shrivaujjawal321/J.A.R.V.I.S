"""Pydantic models for DataForge audit results."""

from __future__ import annotations
from typing import Any, Dict, List, Optional, Literal
from pydantic import BaseModel, Field
import uuid


class DimensionResult(BaseModel):
    score: float = Field(ge=0.0, le=100.0)
    weight: float
    detail: str
    severity: Literal["ok", "info", "warning", "critical"]
    raw: Optional[Dict[str, Any]] = None  # internal diagnostics, not sent to frontend


class SubScores(BaseModel):
    completeness: DimensionResult
    class_balance: DimensionResult
    label_quality: DimensionResult
    duplicates: DimensionResult
    outliers: DimensionResult
    schema_validity: DimensionResult
    leakage: DimensionResult
    temporal_coverage: DimensionResult
    feature_redundancy: DimensionResult
    distribution_sanity: DimensionResult
    # Domain-specific PdM check — populated only for time_series datasets with 5+ numeric cols.
    # Null for plain tabular datasets. Frontend must treat this as optional.
    domain_pdm: Optional[DimensionResult] = None


class ReadinessPenalties(BaseModel):
    label_noise: float = 0.0
    imbalance: float = 0.0
    temporal_gaps: float = 0.0


class ReadinessResult(BaseModel):
    readiness_pct: float
    baseline_auc: float
    target_auc: float = 0.80
    penalties: ReadinessPenalties


class Improvement(BaseModel):
    dimension: str
    priority: Literal["P0", "P1", "P2"]
    title: str
    description: str
    estimated_score_delta: float
    effort: Literal["low", "medium", "high"]


class ColumnPreview(BaseModel):
    name: str
    dtype: str
    null_pct: float


class Preview(BaseModel):
    columns: List[ColumnPreview]
    sample_rows: List[Dict[str, Any]]


class RelevanceResult(BaseModel):
    """Relevance gate outcome included in AuditResult."""
    relevance_score: float = Field(ge=0.0, le=100.0)
    accepted: bool
    gate_message: str
    relevance_reasons: List[str] = Field(default_factory=list)
    relevance_against: List[str] = Field(default_factory=list)
    kb_match_score: float = 0.0
    embed_sim: Optional[float] = None


class RankingResult(BaseModel):
    """Ranking factors and overall score included in AuditResult."""
    overall_score: float = Field(ge=0.0, le=100.0, default=0.0)
    rank: int = 0          # 0 = rejected/unranked
    feature_richness: float = 0.0
    ps_alignment: float = 0.0
    status: Literal["accepted", "rejected"] = "accepted"


class AuditResult(BaseModel):
    audit_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    dataset_id: str
    filename: str
    dataset_type: Literal["tabular", "time_series"]
    n_rows: int
    n_cols: int
    composite_score: float
    grade: Literal["Excellent", "Good", "Fair", "Needs Work", "Poor"]
    sub_scores: SubScores
    readiness: Optional[ReadinessResult]
    review: str
    improvements: List[Improvement]
    preview: Preview
    reasoning_trace: Optional[List[str]] = None  # agentic decision log
    # v2 additions
    relevance: Optional[RelevanceResult] = None
    ranking: Optional[RankingResult] = None


class AuditSummary(BaseModel):
    """Lightweight record stored in JSONL for leaderboard."""
    audit_id: str
    dataset_id: str
    filename: str
    composite_score: float
    grade: str
    n_rows: int
    n_cols: int
    download_count: int = 0
    created_at: str
    dataset_type: str
    # v2 additions (optional for backward compat with existing JSONL records)
    relevance_score: float = 0.0
    overall_score: float = 0.0
    rank: int = 0
    status: str = "accepted"
