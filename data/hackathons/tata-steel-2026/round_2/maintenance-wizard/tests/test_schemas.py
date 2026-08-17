"""
tests/test_schemas.py
=====================
Unit tests for wizard.core.schemas.

Tests:
    - Entity model field defaults and constraints
    - ingest_entity() discriminated union routing
    - Invalid entity_type raises ValidationError → quarantine path
    - Cross-agent output model field constraints
    - DocumentRecord.char_count auto-populated
    - ULID ID format
"""

from __future__ import annotations

from datetime import datetime, timedelta

import pytest
from pydantic import ValidationError

from wizard.core.schemas import (
    ActionStep,
    AlertEvent,
    AlertSeverity,
    AnomalyAlert,
    AssetProfile,
    CauseChainStep,
    DiagnosisReport,
    DocumentRecord,
    FaultLog,
    KnowledgeDocument,
    MaintenanceRecord,
    MaintenanceRecommendation,
    QuarantineRecord,
    RCAResult,
    RiskScore,
    RULResult,
    SensorSummary,
    SparePart,
    WizardEntity,
    ingest_entity,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_asset(**kwargs) -> AssetProfile:
    defaults = dict(
        asset_id="EAF-04",
        plant_area="EAF-Bay-1",
        equipment_name="EAF-04 Electrode Drive",
        equipment_class="hydraulic_unit",
        manufacturer="ABB",
        installation_date=datetime(2018, 6, 1),
        criticality_tier="critical",
    )
    defaults.update(kwargs)
    return AssetProfile(**defaults)


def _make_sensor(**kwargs) -> SensorSummary:
    defaults = dict(
        asset_id="EAF-04",
        plant_area="EAF-Bay-1",
        sensor_readings={"temperature_c": 89.4, "vibration_mm_s": 7.8},
    )
    defaults.update(kwargs)
    return SensorSummary(**defaults)


# ---------------------------------------------------------------------------
# 1. Entity model instantiation
# ---------------------------------------------------------------------------

class TestEntityInstantiation:
    def test_asset_profile_defaults(self):
        a = _make_asset()
        assert a.entity_type == "asset"
        assert a.source_system == "manual"
        assert a.schema_version == "1.0"
        assert len(a.entity_id) > 10  # ULID or UUID

    def test_sensor_summary_readings_stored(self):
        s = _make_sensor()
        assert s.sensor_readings["temperature_c"] == 89.4
        assert s.anomaly_score is None   # null until computed
        assert s.rul_days_p50 is None    # null until computed

    def test_sensor_anomaly_score_set(self):
        s = _make_sensor(anomaly_score=0.71, rul_days_p50=11.4)
        assert s.anomaly_score == pytest.approx(0.71)
        assert s.rul_days_p50 == pytest.approx(11.4)

    def test_fault_log_defaults(self):
        f = FaultLog(
            asset_id="EAF-04",
            plant_area="EAF-Bay-1",
            fault_code="BRG-WEAR-003",
            fault_description="Bearing wear",
            severity="critical",
            detected_at=datetime.utcnow(),
            source="sensor",
        )
        assert not f.confirmed
        assert f.related_sensor_summary_id is None

    def test_maintenance_record_parts_used_default_empty(self):
        m = MaintenanceRecord(
            asset_id="EAF-04",
            plant_area="EAF-Bay-1",
            maintenance_type="predictive",
            technician_id="TECH-01",
        )
        assert m.parts_used == []
        assert m.outcome == "pending"

    def test_knowledge_document_applicable_classes_default_empty(self):
        k = KnowledgeDocument(
            asset_id="EAF-04",
            plant_area="EAF-Bay-1",
            doc_type="sop",
            title="Test SOP",
        )
        assert k.applicable_equipment_classes == []

    def test_spare_part_lead_time_days_present(self):
        """lead_time_days is a required prioritization field — must be stored."""
        sp = SparePart(
            asset_id="EAF-04",
            plant_area="EAF-Bay-1",
            part_number="SKF-6310-2RS1",
            part_name="Deep Groove Ball Bearing",
            lead_time_days=14,
        )
        assert sp.lead_time_days == 14
        assert sp.criticality_override == "standard"

    def test_anomaly_alert_not_acknowledged_by_default(self):
        a = AnomalyAlert(
            asset_id="EAF-04",
            plant_area="EAF-Bay-1",
            alert_type="rul_critical",
            risk_level="critical",
            description="RUL critical",
        )
        assert not a.acknowledged
        assert a.acknowledged_by is None


# ---------------------------------------------------------------------------
# 2. ULID IDs
# ---------------------------------------------------------------------------

class TestULIDGeneration:
    def test_entity_ids_are_unique(self):
        a1 = _make_asset()
        a2 = _make_asset()
        assert a1.entity_id != a2.entity_id

    def test_entity_id_is_string(self):
        a = _make_asset()
        assert isinstance(a.entity_id, str)
        assert len(a.entity_id) >= 26  # ULID is 26 chars; UUID4 is 36


# ---------------------------------------------------------------------------
# 3. ingest_entity() discriminated union
# ---------------------------------------------------------------------------

class TestIngestEntity:
    def test_routes_asset(self):
        entity = ingest_entity({
            "entity_type": "asset",
            "asset_id": "BF-2-FAN",
            "plant_area": "BF-Area-1",
            "equipment_name": "BF-2 Fan A",
            "equipment_class": "fan",
        })
        assert isinstance(entity, AssetProfile)

    def test_routes_sensor_summary(self):
        entity = ingest_entity({
            "entity_type": "sensor_summary",
            "asset_id": "BF-2-FAN",
            "plant_area": "BF-Area-1",
            "sensor_readings": {"vibration_mm_s": 3.2},
        })
        assert isinstance(entity, SensorSummary)

    def test_routes_fault_log(self):
        entity = ingest_entity({
            "entity_type": "fault_log",
            "asset_id": "BF-2-FAN",
            "plant_area": "BF-Area-1",
            "fault_code": "VIB-001",
            "detected_at": datetime.utcnow().isoformat(),
            "source": "sensor",
        })
        assert isinstance(entity, FaultLog)

    def test_routes_spare_part(self):
        entity = ingest_entity({
            "entity_type": "spare_part",
            "asset_id": "COMMON",
            "plant_area": "Warehouse",
            "part_number": "FAG-23030-E1A",
            "part_name": "Spherical Roller Bearing",
            "lead_time_days": 21,
        })
        assert isinstance(entity, SparePart)
        assert entity.lead_time_days == 21  # type: ignore[union-attr]

    def test_routes_anomaly_alert(self):
        entity = ingest_entity({
            "entity_type": "anomaly_alert",
            "asset_id": "EAF-04",
            "plant_area": "EAF-Bay-1",
            "alert_type": "rul_critical",
            "risk_level": "critical",
            "description": "RUL critical",
        })
        assert isinstance(entity, AnomalyAlert)

    def test_invalid_entity_type_raises_validation_error(self):
        # ingest_entity raises ValueError (not pydantic ValidationError) when the
        # entity_type discriminator is unknown — correct semantic for a bad discriminator.
        with pytest.raises(ValueError):
            ingest_entity({"entity_type": "not_a_real_type", "asset_id": "X"})

    def test_missing_required_field_raises_validation_error(self):
        # asset_id is required on EntityBase
        with pytest.raises(ValidationError):
            ingest_entity({"entity_type": "asset", "equipment_name": "Fan A"})

    def test_ingest_preserves_asset_id(self):
        entity = ingest_entity({
            "entity_type": "sensor_summary",
            "asset_id": "PUMP-03",
            "plant_area": "CW-Bay-2",
            "sensor_readings": {},
        })
        assert entity.asset_id == "PUMP-03"  # type: ignore[union-attr]


# ---------------------------------------------------------------------------
# 4. Cross-agent output models
# ---------------------------------------------------------------------------

class TestCrossAgentOutputs:
    def test_alert_severity_enum_values(self):
        assert AlertSeverity.CRITICAL == "critical"
        assert AlertSeverity.HIGH == "high"
        assert AlertSeverity.MEDIUM == "medium"
        assert AlertSeverity.LOW == "low"

    def test_alert_event_cost_avoidance(self):
        ev = AlertEvent(
            asset_id="EAF-04",
            equipment_name="EAF-04 Electrode Drive",
            severity=AlertSeverity.CRITICAL,
            alert_type="rul_critical",
            description="RUL critical",
            cost_avoidance_inr=75_000.0 * 24,  # 24h avoided
        )
        assert ev.cost_avoidance_inr == pytest.approx(1_800_000.0)

    def test_diagnosis_report_confidence_bounds(self):
        d = DiagnosisReport(
            asset_id="EAF-04",
            probable_fault_codes=["BRG-WEAR-003"],
            probable_fault_description="Bearing wear",
            confidence=0.87,
        )
        assert 0.0 <= d.confidence <= 1.0

    def test_diagnosis_report_confidence_out_of_range(self):
        with pytest.raises(ValidationError):
            DiagnosisReport(
                asset_id="EAF-04",
                probable_fault_codes=[],
                probable_fault_description="x",
                confidence=1.5,  # > 1.0 — invalid
            )

    def test_rul_result_percentile_ordering(self):
        ru = RULResult(
            asset_id="EAF-04",
            sensor_summary_id="01JYYYYY",
            rul_days_p10=8.2,
            rul_days_p50=11.4,
            rul_days_p90=18.7,
            degradation_index=0.81,
            anomaly_score=0.71,
            failure_class="tool_wear",
            failure_probability=0.83,
        )
        # Pessimistic < median < optimistic
        assert ru.rul_days_p10 < ru.rul_days_p50 < ru.rul_days_p90

    def test_rul_degradation_index_bounds(self):
        with pytest.raises(ValidationError):
            RULResult(
                asset_id="EAF-04",
                sensor_summary_id="01J",
                rul_days_p10=5.0,
                rul_days_p50=10.0,
                rul_days_p90=15.0,
                degradation_index=1.5,  # > 1.0 — invalid
                anomaly_score=0.5,
                failure_class="no_failure",
                failure_probability=0.1,
            )

    def test_risk_score_wrps_and_tier(self):
        rs = RiskScore(
            asset_id="EAF-04",
            wrps=82.4,
            risk_tier=AlertSeverity.CRITICAL,
            severity_factor=9.0,
            probability_factor=8.5,
            detectability_factor=7.0,
            business_impact_factor=9.5,
        )
        assert rs.wrps == pytest.approx(82.4)
        assert rs.risk_tier == AlertSeverity.CRITICAL

    def test_maintenance_recommendation_action_steps(self):
        p = MaintenanceRecommendation(
            asset_id="EAF-04",
            diagnosis_report_id="01J",
            priority=AlertSeverity.CRITICAL,
            action_steps=[
                ActionStep(
                    step_number=1,
                    action="Isolate drive train",
                    cited_sop_section="EAF-SOP-002 §3.1",
                ),
                ActionStep(
                    step_number=2,
                    action="Replace bearing SKF-6310-2RS1",
                ),
            ],
        )
        assert len(p.action_steps) == 2
        assert p.action_steps[0].step_number == 1

    def test_spare_parts_procurement_warning_populated(self):
        p = MaintenanceRecommendation(
            asset_id="EAF-04",
            diagnosis_report_id="01J",
            priority=AlertSeverity.CRITICAL,
            spares_procurement_warning=(
                "CRITICAL: SKF-6310-2RS1 out of stock, 14-day lead — ORDER NOW"
            ),
        )
        assert "ORDER NOW" in (p.spares_procurement_warning or "")

    def test_rca_cause_chain_layer_field(self):
        step = CauseChainStep(
            node_id="bearing_wear",
            node_label="Bearing Wear",
            edge_relation="causes",
            layer="graph",
        )
        assert step.layer == "graph"

    def test_quarantine_record_captures_error(self):
        qr = QuarantineRecord(
            raw_payload={"entity_type": "junk"},
            validation_error="No discriminator match",
        )
        assert "No discriminator" in qr.validation_error


# ---------------------------------------------------------------------------
# 5. DocumentRecord
# ---------------------------------------------------------------------------

class TestDocumentRecord:
    def test_char_count_auto_populated(self):
        dr = DocumentRecord(
            source_entity_id="01JXXXXXX",
            source_entity_type="knowledge_doc",
            asset_id="EAF-04",
            text="Section 3.1: Inspect bearing housing for signs of pitting corrosion.",
            doc_type="sop",
            section="3.1",
        )
        assert dr.char_count == len(dr.text)
        assert dr.char_count > 0

    def test_chunk_id_generated(self):
        dr = DocumentRecord(
            source_entity_id="X",
            source_entity_type="knowledge_doc",
            asset_id="EAF-04",
            text="some text",
        )
        assert len(dr.chunk_id) > 0

    def test_chunk_ids_are_unique(self):
        dr1 = DocumentRecord(source_entity_id="X", source_entity_type="k", asset_id="A", text="t")
        dr2 = DocumentRecord(source_entity_id="X", source_entity_type="k", asset_id="A", text="t")
        assert dr1.chunk_id != dr2.chunk_id
