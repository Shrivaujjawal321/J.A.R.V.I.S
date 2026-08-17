"""
wizard.core.schemas
===================
Single source-of-truth entity model for the Maintenance Wizard system.

All sub-packages import their typed entities from here. No `any` types.
Entity validation is always Pydantic v2; persistence is SQLModel + SQLite.

Entity hierarchy:
  EntityBase (shared fields)
    ├── AssetProfile       (table)  – master asset registry
    ├── SensorSummary      (table)  – aggregated sensor windows
    ├── FaultLog           (table)  – single fault/error events
    ├── MaintenanceRecord  (table)  – maintenance events
    ├── KnowledgeDocument  (table)  – manuals, SOPs, failure reports
    ├── SparePart          (table)  – spare parts catalog + procurement
    └── AnomalyAlert       (table)  – proactive alerts from ML pipeline

  DocumentRecord  (BaseModel, NOT a table) – RAG bridge for ChromaDB/LanceDB

Cross-agent output models:
  DiagnosisReport, RCAResult, CauseChainStep,
  RULResult, RiskScore, MaintenanceRecommendation, ActionStep,
  AlertEvent (with AlertSeverity StrEnum)

Discriminated union:
  WizardEntity = Union[all table entities] discriminated on entity_type

Entry-point:
  ingest_entity(raw: dict) -> WizardEntity   # raises ValidationError → quarantine
"""

from __future__ import annotations

import enum
from datetime import datetime
from typing import Annotated, Literal, Optional, Union

from pydantic import BaseModel, Field, TypeAdapter, computed_field
from sqlmodel import Column, Field as SQLField, SQLModel
from sqlalchemy import JSON, Text

# ---------------------------------------------------------------------------
# ULID factory (python-ulid package)
# Usage: entity_id defaults to a new ULID string
# ---------------------------------------------------------------------------
def _new_ulid() -> str:  # pragma: no cover
    """Generate a new ULID string. Falls back to UUID4 if python-ulid missing."""
    try:
        from ulid import ULID
        return str(ULID())
    except ImportError:
        import uuid
        return str(uuid.uuid4())


# ===========================================================================
# 1.  SHARED BASE
# ===========================================================================

class EntityBase(SQLModel):
    """
    Four fields shared by every entity — the join key across all consumers.
    ISA-95 alignment: asset_id traces up the equipment hierarchy.
    """
    entity_id: str = SQLField(
        default_factory=_new_ulid,
        primary_key=True,
        index=True,
        description="ULID — lexicographically sortable unique entity id",
    )
    asset_id: str = SQLField(
        index=True,
        description="FK → AssetProfile.entity_id (logical; not DB-enforced in SQLite)",
    )
    plant_area: str = SQLField(
        default="unspecified",
        description="ISA-95 Area level (e.g. 'BF-Area-1', 'HSM-Bay-3')",
    )
    ingested_at: datetime = SQLField(
        default_factory=datetime.utcnow,
        index=True,
        description="UTC timestamp of ingest",
    )
    source_system: str = SQLField(
        default="manual",
        description="Origin: 'scada' | 'erp' | 'manual' | 'generated'",
    )
    schema_version: str = SQLField(
        default="1.0",
        description="Schema version for forward-compat detection",
    )


# ===========================================================================
# 2.  SEVEN ENTITY TABLE MODELS
# ===========================================================================

class AssetProfile(EntityBase, table=True):
    """
    Master entity — every other entity references this via asset_id.
    ISA-95 Work Unit / Equipment level.
    ISO 14224 equipment classification.
    """
    __tablename__ = "asset_profile"

    entity_type: str = SQLField(default="asset")
    equipment_name: str = SQLField(description="Human name, e.g. 'BF-2 Fan A'")
    equipment_class: str = SQLField(
        description="ISO 14224: 'pump'|'fan'|'conveyor'|'bearing'|'hydraulic_unit'"
    )
    manufacturer: str = SQLField(default="unknown")
    installation_date: datetime = SQLField(default_factory=datetime.utcnow)
    design_rpm: Optional[float] = SQLField(default=None)
    design_pressure_bar: Optional[float] = SQLField(default=None)
    criticality_tier: str = SQLField(
        default="medium",
        description="'critical'|'high'|'medium'|'low'",
    )
    subsystem: str = SQLField(
        default="main",
        description="ISO 14224 sub-unit (e.g. 'impeller', 'bearing-set')",
    )
    iso14224_taxonomy: str = SQLField(
        default="",
        description="e.g. 'rotating.centrifugal_pump.impeller'",
    )
    work_center: str = SQLField(
        default="",
        description="ISA-95 Work Center label (e.g. 'Rolling-Mill-1')",
    )


class SensorSummary(EntityBase, table=True):
    """
    Aggregated sensor window (15-min or 1-hour).
    ML pipeline writes anomaly_score and rul_days_p50 back here after inference.
    """
    __tablename__ = "sensor_summary"

    entity_type: str = SQLField(default="sensor_summary")
    window_start: datetime = SQLField(default_factory=datetime.utcnow, index=True)
    window_end: datetime = SQLField(default_factory=datetime.utcnow)
    sensor_readings: dict = SQLField(
        default_factory=dict,
        sa_column=Column(JSON),
        description=(
            "Keys: temperature_c, pressure_bar, vibration_mm_s, rpm, "
            "torque_nm, current_a — all float or null"
        ),
    )
    anomaly_score: Optional[float] = SQLField(
        default=None,
        description="IsolationForest/LSTM-AE score in [0,1]; null until computed",
    )
    rul_days_p50: Optional[float] = SQLField(
        default=None,
        description="WeibullAFT p50 RUL in days; null until computed",
    )
    operating_condition: Optional[str] = SQLField(
        default=None,
        description="'normal'|'degraded'|'severe' (FD001-style operating mode)",
    )
    operating_hours: Optional[float] = SQLField(
        default=None,
        description="Cumulative operating hours at window_end (C-MAPSS 'cycle' equivalent)",
    )


class FaultLog(EntityBase, table=True):
    """
    Single fault/error event. Derived from sensor anomaly or operator report.
    """
    __tablename__ = "fault_log"

    entity_type: str = SQLField(default="fault_log")
    fault_code: str = SQLField(
        index=True,
        description="e.g. 'BRG-WEAR-001', 'TWF-TOOL-002'",
    )
    fault_description: str = SQLField(default="")
    severity: str = SQLField(
        default="medium",
        description="'low'|'medium'|'high'|'critical'",
    )
    delay_hours: Optional[float] = SQLField(
        default=None,
        description="Actual production delay (hours) caused by this fault — WRPS F2 input",
    )
    detected_at: datetime = SQLField(default_factory=datetime.utcnow, index=True)
    source: str = SQLField(
        default="sensor",
        description="'sensor'|'operator'|'scada'|'erp'",
    )
    confirmed: bool = SQLField(default=False)
    related_sensor_summary_id: Optional[str] = SQLField(
        default=None,
        description="FK → SensorSummary.entity_id",
    )


class MaintenanceRecord(EntityBase, table=True):
    """
    Completed or planned maintenance event.
    ISO 14224-grounded fields for maintenance type and outcome.
    """
    __tablename__ = "maintenance_record"

    entity_type: str = SQLField(default="maintenance_record")
    work_order_id: str = SQLField(index=True, default="")
    maintenance_type: str = SQLField(
        default="preventive",
        description="'corrective'|'preventive'|'predictive'|'emergency'",
    )
    description: str = SQLField(default="", sa_column=Column(Text))
    performed_at: Optional[datetime] = SQLField(default=None)
    planned_at: Optional[datetime] = SQLField(default=None)
    technician_id: str = SQLField(default="")
    duration_hours: Optional[float] = SQLField(default=None)
    parts_used: list = SQLField(
        default_factory=list,
        sa_column=Column(JSON),
        description="List of part_number strings",
    )
    outcome: str = SQLField(
        default="pending",
        description="'resolved'|'partial'|'escalated'|'pending'",
    )
    rca_summary: Optional[str] = SQLField(
        default=None,
        sa_column=Column(Text),
        description="Free-text root cause — also indexed to DocumentRecord for RAG",
    )


class KnowledgeDocument(EntityBase, table=True):
    """
    Manual section, SOP, or failure analysis report.
    content_markdown is chunked into DocumentRecord at ingest for RAG.
    """
    __tablename__ = "knowledge_document"

    entity_type: str = SQLField(default="knowledge_doc")
    doc_type: str = SQLField(
        default="manual",
        description="'manual'|'sop'|'failure_analysis'|'incident_summary'",
    )
    title: str = SQLField(index=True, default="")
    section: str = SQLField(
        default="",
        description="e.g. '4.2 — Descaler Valve Replacement'",
    )
    content_markdown: str = SQLField(
        default="", sa_column=Column(Text),
        description="Full text — chunked into DocumentRecord at ingest"
    )
    revision: str = SQLField(
        default="",
        description="e.g. '2024-Q3'",
    )
    applicable_equipment_classes: list = SQLField(
        default_factory=list,
        sa_column=Column(JSON),
        description="List of equipment class strings this doc applies to",
    )


class SparePart(EntityBase, table=True):
    """
    Spare parts catalog entry with procurement data.
    lead_time_days is a first-class field — critical for prioritization scoring.
    """
    __tablename__ = "spare_part"

    entity_type: str = SQLField(default="spare_part")
    part_number: str = SQLField(index=True, default="")
    part_name: str = SQLField(default="")
    compatible_equipment: list = SQLField(
        default_factory=list,
        sa_column=Column(JSON),
        description="List of asset_id or equipment_class strings",
    )
    stock_qty: int = SQLField(default=0)
    min_stock_qty: int = SQLField(
        default=1,
        description="Reorder point",
    )
    unit_cost_inr: float = SQLField(default=0.0)
    lead_time_days: int = SQLField(
        default=7,
        description="Procurement lead time in days — key input to WRPS prioritization",
    )
    supplier: str = SQLField(default="")
    criticality_override: str = SQLField(
        default="standard",
        description="'critical'|'standard' — overrides asset criticality for ordering",
    )
    last_updated: datetime = SQLField(default_factory=datetime.utcnow)

    # ── PS-spec aliases (4.3) ────────────────────────────────────────────────
    # These computed properties surface the PS-mandated names in serialized
    # output (model_dump / model_dump_json) WITHOUT renaming the DB columns.
    @computed_field(description="PS alias for stock_qty — quantity currently in warehouse")  # type: ignore[misc]
    @property
    def in_stock(self) -> int:
        return self.stock_qty

    @computed_field(description="PS alias for lead_time_days — procurement lead time in days")  # type: ignore[misc]
    @property
    def procurement_lead_days(self) -> int:
        return self.lead_time_days


class AnomalyAlert(EntityBase, table=True):
    """
    Proactive alert generated by the ML anomaly/RUL pipeline.
    The APScheduler evaluator queries acknowledged=False rows to fan-out via SSE.
    """
    __tablename__ = "anomaly_alert"

    entity_type: str = SQLField(default="anomaly_alert")
    triggered_at: datetime = SQLField(
        default_factory=datetime.utcnow,
        index=True,
    )
    alert_type: str = SQLField(
        default="sensor_anomaly",
        description=(
            "'sensor_anomaly'|'rul_critical'|'pattern_match'|'threshold_breach'"
        ),
    )
    risk_level: str = SQLField(
        default="medium",
        index=True,
        description="'low'|'medium'|'high'|'critical'",
    )
    description: str = SQLField(default="", sa_column=Column(Text))
    triggering_sensor_summary_id: Optional[str] = SQLField(
        default=None,
        description="FK → SensorSummary.entity_id",
    )
    estimated_rul_days: Optional[float] = SQLField(default=None)
    recommended_action: Optional[str] = SQLField(default=None, sa_column=Column(Text))
    acknowledged: bool = SQLField(default=False, index=True)
    acknowledged_by: Optional[str] = SQLField(default=None)
    cooldown_key: Optional[str] = SQLField(
        default=None,
        index=True,
        description="Dedup key: f'{asset_id}:{alert_type}' — prevents duplicate alerts",
    )


# ===========================================================================
# 3.  DOCUMENT RECORD  (RAG bridge — NOT a DB table)
# ===========================================================================

class DocumentRecord(BaseModel):
    """
    NOT persisted to SQLite.
    Metadata envelope for ChromaDB / LanceDB chunk ingest.
    source_entity_id links back to the originating EntityBase row.
    """
    chunk_id: str = Field(default_factory=_new_ulid)
    source_entity_id: str = Field(description="FK → EntityBase.entity_id")
    source_entity_type: str = Field(
        description="Reverse-lookup discriminator (e.g. 'knowledge_doc')"
    )
    asset_id: str = Field(description="Propagated from source entity for prefilter")
    text: str = Field(description="The chunk text that is embedded")
    doc_type: str = Field(
        default="manual",
        description="'manual'|'sop'|'maintenance_record'|'failure_analysis'|...",
    )
    section: str = Field(default="")
    page_or_step: Optional[str] = Field(default=None)
    embedding_model: str = Field(default="BAAI/bge-small-en-v1.5")
    char_count: int = Field(default=0)

    def model_post_init(self, __context: object) -> None:  # type: ignore[override]
        if not self.char_count and self.text:
            object.__setattr__(self, "char_count", len(self.text))


# ===========================================================================
# 4.  DISCRIMINATED UNION + INGEST ENTRY POINT
# ===========================================================================

WizardEntity = Union[
    AssetProfile,
    SensorSummary,
    FaultLog,
    MaintenanceRecord,
    KnowledgeDocument,
    SparePart,
    AnomalyAlert,
]

# SQLModel table classes cannot carry a Literal column, so we dispatch by the
# `entity_type` tag manually rather than via a Pydantic discriminated union.
_ENTITY_BY_TYPE: dict[str, type] = {
    "asset": AssetProfile,
    "sensor_summary": SensorSummary,
    "fault_log": FaultLog,
    "maintenance_record": MaintenanceRecord,
    "knowledge_doc": KnowledgeDocument,
    "spare_part": SparePart,
    "anomaly_alert": AnomalyAlert,
}


def ingest_entity(raw: dict) -> WizardEntity:
    """
    Single entry point for all entity ingest.

    Dispatches on ``raw["entity_type"]`` to the correct table class, then
    validates. Raises ``pydantic.ValidationError`` on invalid data, or
    ``ValueError`` on an unknown/missing entity_type — callers catch and write
    to ``data/quarantine/invalid_entities.jsonl``.

    Example::

        entity = ingest_entity({"entity_type": "asset", "asset_id": "EAF-04", ...})
    """
    etype = raw.get("entity_type")
    model = _ENTITY_BY_TYPE.get(etype)
    if model is None:
        raise ValueError(
            f"unknown entity_type {etype!r}; expected one of {sorted(_ENTITY_BY_TYPE)}"
        )
    return model.model_validate(raw)


# ===========================================================================
# 5.  CROSS-AGENT OUTPUT MODELS
# ===========================================================================

class AlertSeverity(str, enum.Enum):
    """Severity levels used across agents and the alerting engine."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertEvent(BaseModel):
    """
    Emitted by the proactive alerting engine (APScheduler evaluator).
    Fanned out via SSE to connected Streamlit clients.
    """
    alert_id: str = Field(default_factory=_new_ulid)
    asset_id: str
    equipment_name: str
    severity: AlertSeverity
    alert_type: str
    description: str
    estimated_rul_days: Optional[float] = None
    recommended_action: Optional[str] = None
    triggered_at: datetime = Field(default_factory=datetime.utcnow)
    source_alert_entity_id: Optional[str] = Field(
        default=None,
        description="FK → AnomalyAlert.entity_id for full detail lookup",
    )
    cost_avoidance_inr: Optional[float] = Field(
        default=None,
        description="Estimated avoided cost in INR for the live cost-avoidance ticker",
    )


class DiagnosisReport(BaseModel):
    """
    Output of the Diagnosis agent.
    Cited sources link to DocumentRecord.chunk_id or KnowledgeDocument.entity_id.
    """
    report_id: str = Field(default_factory=_new_ulid)
    asset_id: str
    probable_fault_codes: list[str] = Field(default_factory=list)
    probable_fault_description: str
    confidence: float = Field(ge=0.0, le=1.0, description="Diagnosis confidence 0-1")
    supporting_sensor_ids: list[str] = Field(
        default_factory=list,
        description="SensorSummary.entity_id values used",
    )
    cited_sources: list[str] = Field(
        default_factory=list,
        description="chunk_id or entity_id of [N] citation sources",
    )
    diagnosis_reasoning: str = Field(
        default="",
        description="Agent chain-of-thought for the 'show your work' expander",
    )
    # PS §5.1 — process-level defects that contribute to the equipment issue.
    # Populated by diagnosis_node from sensor pattern + fault context.
    process_related_defects: list[str] = Field(
        default_factory=list,
        description=(
            "PS §5.1: Process-level defects contributing to the equipment fault. "
            "e.g. 'Thermal cycling from irregular tapping schedule accelerating refractory wear', "
            "'Misaligned roll gap inducing eccentric bearing load'. "
            "Maps sensor signatures → plausible upstream process causes."
        ),
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)


class CauseChainStep(BaseModel):
    """One step in the root-cause cause chain (graph path)."""
    node_id: str = Field(description="NetworkX node ID in the FMEA graph")
    node_label: str
    edge_relation: str = Field(
        default="causes",
        description="e.g. 'causes', 'contributes_to', 'results_in'",
    )
    cited_source: Optional[str] = Field(
        default=None,
        description="DocumentRecord.chunk_id or SOP section reference",
    )
    layer: str = Field(
        default="graph",
        description="'graph'|'gcm'|'llm' — which RCA layer produced this step",
    )


class RCAResult(BaseModel):
    """
    Output of the RCA agent (3-layer: graph traversal + DoWhy GCM + LLM 5-whys).
    """
    rca_id: str = Field(default_factory=_new_ulid)
    asset_id: str
    fault_log_id: str = Field(description="FK → FaultLog.entity_id")
    cause_chain: list[CauseChainStep] = Field(
        default_factory=list,
        description="Ordered list of cause steps from proximate to root",
    )
    root_cause_summary: str = Field(description="NL summary of root cause")
    five_whys: list[str] = Field(
        default_factory=list,
        description="LLM-generated 5-whys list (validated by NLI gate)",
    )
    gcm_attributions: dict = Field(
        default_factory=dict,
        description="DoWhy GCM node attribution scores {node_id: float}",
    )
    cited_sources: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class RULResult(BaseModel):
    """
    Output of the RUL/Prediction agent.
    WeibullAFT p10/p50/p90 quantiles + degradation index.
    """
    rul_id: str = Field(default_factory=_new_ulid)
    asset_id: str
    sensor_summary_id: str = Field(description="FK → SensorSummary.entity_id")
    rul_days_p10: float = Field(description="Pessimistic RUL (10th percentile)")
    rul_days_p50: float = Field(description="Median RUL (50th percentile)")
    rul_days_p90: float = Field(description="Optimistic RUL (90th percentile)")
    degradation_index: float = Field(
        ge=0.0, le=1.0,
        description="Normalized degradation [0=healthy, 1=critical]",
    )
    anomaly_score: float = Field(ge=0.0, le=1.0)
    failure_class: str = Field(
        default="no_failure",
        description="LightGBM 4-class: 'no_failure'|'tool_wear'|'heat'|'power'|'overstrain'",
    )
    failure_probability: float = Field(ge=0.0, le=1.0)
    model_used: str = Field(
        default="weibull_aft",
        description="'weibull_aft'|'weibull_fitter_fallback'",
    )
    bayesian_correction_applied: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)


class RiskScore(BaseModel):
    """
    Output of the Prioritization agent.
    WRPS (Weighted Risk Priority Score) 4-factor model.
    """
    risk_id: str = Field(default_factory=_new_ulid)
    asset_id: str
    wrps: float = Field(description="Composite WRPS in [0, 100]")
    risk_tier: AlertSeverity
    severity_factor: float = Field(ge=0.0, le=10.0)
    probability_factor: float = Field(ge=0.0, le=10.0)
    detectability_factor: float = Field(ge=0.0, le=10.0)
    business_impact_factor: float = Field(ge=0.0, le=10.0)
    spares_risk: str = Field(
        default="ok",
        description="'ok'|'low_stock'|'critical_stockout'|'long_lead_time'",
    )
    critical_parts_out_of_stock: list[str] = Field(
        default_factory=list,
        description="part_number strings that are stockout + critical",
    )
    estimated_downtime_hours: Optional[float] = None
    cost_avoidance_inr: Optional[float] = Field(
        default=None,
        description="avoided_hours × 75000 INR/hr for the cost ticker",
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ActionStep(BaseModel):
    """One step in a structured maintenance plan."""
    step_number: int
    action: str
    responsible_role: str = Field(
        default="maintenance_technician",
        description="Who performs this step",
    )
    estimated_duration_hours: Optional[float] = None
    parts_required: list[str] = Field(default_factory=list)
    safety_precautions: list[str] = Field(default_factory=list)
    cited_sop_section: Optional[str] = Field(
        default=None,
        description="SOP section reference, e.g. 'BF-SOP-001 §3.4'",
    )


class MaintenanceRecommendation(BaseModel):
    """
    Output of the Maintenance Plan agent.
    Two-pass: Instructor structured draft + cited narrative.
    """
    recommendation_id: str = Field(default_factory=_new_ulid)
    asset_id: str
    diagnosis_report_id: str
    rca_result_id: Optional[str] = None
    rul_result_id: Optional[str] = None
    risk_score_id: Optional[str] = None
    priority: AlertSeverity
    maintenance_type: str = Field(
        default="corrective",
        description="'corrective'|'preventive'|'predictive'|'emergency'",
    )
    action_steps: list[ActionStep] = Field(
        default_factory=list,
        description="Ordered step-by-step maintenance plan",
    )
    estimated_total_hours: float = 0.0
    parts_bill_of_materials: list[str] = Field(
        default_factory=list,
        description="All part_numbers needed across all steps",
    )
    narrative_summary: str = Field(
        default="",
        description="NL plan summary with inline [N] citations",
    )
    cited_sources: list[str] = Field(
        default_factory=list,
        description="Source chunk_id / entity_id for every [N] in narrative",
    )
    spares_procurement_warning: Optional[str] = Field(
        default=None,
        description=(
            "e.g. 'CRITICAL: SKF-6310-2RS1 out of stock, 14-day lead time — ORDER NOW'"
        ),
    )
    cost_avoidance_inr: Optional[float] = None
    # Surfaced predictive context (populated by report_node from state['rul_estimate'])
    estimated_rul_days_p10: Optional[float] = Field(
        default=None, description="Pessimistic RUL estimate in days (P10)"
    )
    estimated_rul_days_p50: Optional[float] = Field(
        default=None, description="Median RUL estimate in days (P50)"
    )
    estimated_rul_days_p90: Optional[float] = Field(
        default=None, description="Optimistic RUL estimate in days (P90)"
    )
    degradation_index: Optional[float] = Field(
        default=None, description="Physics-informed degradation index [0,1] driving the RUL"
    )
    cited_sources_faithfulness: Optional[dict[str, float]] = Field(
        default=None,
        description="chunk_id → NLI entailment score from the faithfulness gate (FR4 traceability)",
    )
    # PS §5.1 — process-level defects surfaced from DiagnosisReport
    process_related_defects: list[str] = Field(
        default_factory=list,
        description=(
            "PS §5.1: Process-level defects (copied from DiagnosisReport) so the "
            "recommendation document carries the full causal context."
        ),
    )
    # PS §5.3 — long-term monitoring recommendations
    long_term_monitoring: list[str] = Field(
        default_factory=list,
        description=(
            "PS §5.3: 2-4 concrete long-term monitoring actions grounded in the diagnosis "
            "and equipment type. e.g. 'Trend bearing vibration weekly vs ISO 10816 baseline', "
            "'Quarterly lubrication-oil particle analysis', "
            "'Add EAF-04 to monthly thermography route'."
        ),
    )
    # PS §5.4 — role-differentiated decision summaries
    decision_summary_engineer: Optional[str] = Field(
        default=None,
        description=(
            "PS §5.4: Technical decision summary for the maintenance engineer — "
            "fault identity, RCA, exact repair steps, parts required, safety precautions."
        ),
    )
    decision_summary_supervisor: Optional[str] = Field(
        default=None,
        description=(
            "PS §5.4: Business decision summary for the shift supervisor / plant manager — "
            "risk tier, estimated downtime, production impact, cost-avoidance figure, "
            "spare-procurement go/no-go, recommended action window."
        ),
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)


# ---------------------------------------------------------------------------
# 6.  LangGraph MaintenanceState TypedDict
# ---------------------------------------------------------------------------
# Imported by wizard.agents.graph — defined here so agent code never diverges.

from typing import TypedDict


class MaintenanceState(TypedDict, total=False):
    """
    Typed state threaded through the LangGraph supervisor graph.
    Checkpointed to SQLite per session thread_id for time-travel.
    """
    thread_id: str
    equipment_id: str                        # = asset_id
    sensor_snapshot: dict                    # latest SensorSummary.sensor_readings
    fault_codes: list[str]
    user_query: str
    diagnosis: Optional[DiagnosisReport]
    rca: Optional[RCAResult]
    rul_estimate: Optional[RULResult]
    risk_level: Optional[RiskScore]
    priority_score: float
    maintenance_plan: Optional[MaintenanceRecommendation]
    cited_sources: list[str]
    feedback_corrections: list[dict]
    alert_events: list[AlertEvent]
    agent_trace: list[dict]                  # [{agent, node, latency_ms, timestamp}]
    error: Optional[str]
    # FR3: Multi-turn conversation context (Fix #5)
    # Compact turn summaries: [{turn, query, diagnosis_summary, rca_summary, recommendation_summary}]
    # Accumulated across turns — never reset. Passed forward via aget_state() before each new turn.
    conversation_history: list[dict]
    # FR4: Raw ContextChunk dicts from all RAG calls this turn (for NLI faithfulness gate, Fix #8)
    # Reset to [] at the start of each turn; each RAG node appends its retrieved chunks.
    retrieved_chunks_raw: list[dict]
    # FR4: NLI faithfulness scores per chunk (Fix #8): {chunk_id: entailment_probability}
    # Populated by report_node after running run_faithfulness_gate(). Reset each turn.
    faithfulness_scores: dict


# ---------------------------------------------------------------------------
# 7.  QUARANTINE RECORD  (written to data/quarantine/invalid_entities.jsonl)
# ---------------------------------------------------------------------------

class QuarantineRecord(BaseModel):
    """Written when ingest_entity() raises ValidationError."""
    quarantine_id: str = Field(default_factory=_new_ulid)
    raw_payload: dict
    validation_error: str
    quarantined_at: datetime = Field(default_factory=datetime.utcnow)


# ---------------------------------------------------------------------------
# 8.  PUBLIC EXPORT LIST (agents import these verbatim)
# ---------------------------------------------------------------------------

__all__ = [
    # Base
    "EntityBase",
    # Table entities
    "AssetProfile",
    "SensorSummary",
    "FaultLog",
    "MaintenanceRecord",
    "KnowledgeDocument",
    "SparePart",
    "AnomalyAlert",
    # Non-table
    "DocumentRecord",
    "QuarantineRecord",
    # Union + ingest
    "WizardEntity",
    "ingest_entity",
    # Cross-agent outputs
    "AlertSeverity",
    "AlertEvent",
    "DiagnosisReport",
    "CauseChainStep",
    "RCAResult",
    "RULResult",
    "RiskScore",
    "ActionStep",
    "MaintenanceRecommendation",
    # State
    "MaintenanceState",
    # Helpers
    "_new_ulid",
]
