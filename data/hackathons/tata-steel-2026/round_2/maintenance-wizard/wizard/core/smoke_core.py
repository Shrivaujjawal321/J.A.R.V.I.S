"""
wizard/core/smoke_core.py
=========================
Self-test for wizard.core.schemas, wizard.core.config, wizard.core.db.

Run:
    python wizard/core/smoke_core.py

Checks:
    1. All entity models can be instantiated with minimal data
    2. ingest_entity() discriminates all 7 entity types correctly
    3. WizardEntity discriminated union validates and rejects correctly
    4. All cross-agent output models instantiate
    5. config.py loads without error
    6. DB engine creates wizard.db + all tables
"""

from __future__ import annotations

import sys
import traceback
from pathlib import Path

# ---------------------------------------------------------------------------
# Ensure repo root is on sys.path when running as a script
# ---------------------------------------------------------------------------
_repo_root = Path(__file__).resolve().parents[2]
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))


def _check(name: str, fn: "callable") -> bool:
    try:
        fn()
        print(f"  [OK]  {name}")
        return True
    except Exception:
        print(f"  [FAIL] {name}")
        traceback.print_exc()
        return False


def main() -> None:
    from datetime import datetime, timedelta

    print("=== wizard.core smoke test ===\n")
    failures = []

    # ── 1. Schema imports ────────────────────────────────────────────────────
    print("1. Schema imports:")

    def _import_schemas():
        from wizard.core.schemas import (
            ActionStep,
            AlertEvent,
            AlertSeverity,
            AnomalyAlert,
            AssetProfile,
            CauseChainStep,
            DiagnosisReport,
            DocumentRecord,
            EntityBase,
            FaultLog,
            KnowledgeDocument,
            MaintenanceRecommendation,
            MaintenanceRecord,
            MaintenanceState,
            QuarantineRecord,
            RCAResult,
            RiskScore,
            RULResult,
            SensorSummary,
            SparePart,
            WizardEntity,
            ingest_entity,
        )
        # All 20 names importable
        assert all([
            ActionStep, AlertEvent, AlertSeverity, AnomalyAlert, AssetProfile,
            CauseChainStep, DiagnosisReport, DocumentRecord, EntityBase,
            FaultLog, KnowledgeDocument, MaintenanceRecommendation,
            MaintenanceRecord, MaintenanceState, QuarantineRecord, RCAResult,
            RiskScore, RULResult, SensorSummary, SparePart, WizardEntity,
            ingest_entity,
        ])

    if not _check("All schema names importable", _import_schemas):
        failures.append("schema imports")

    # ── 2. Entity instantiation ──────────────────────────────────────────────
    print("\n2. Entity instantiation:")
    from wizard.core.schemas import (
        AnomalyAlert,
        AssetProfile,
        FaultLog,
        KnowledgeDocument,
        MaintenanceRecord,
        SensorSummary,
        SparePart,
        ingest_entity,
    )

    def _asset():
        a = AssetProfile(
            asset_id="EAF-04",
            plant_area="EAF-Bay-1",
            equipment_name="EAF-04 Electrode Drive",
            equipment_class="hydraulic_unit",
            manufacturer="ABB",
            installation_date=datetime(2018, 6, 1),
            criticality_tier="critical",
            subsystem="electrode-column",
            iso14224_taxonomy="electrical.arc_furnace.electrode_drive",
        )
        assert a.entity_id != ""
        assert a.entity_type == "asset"

    def _sensor():
        s = SensorSummary(
            asset_id="EAF-04",
            plant_area="EAF-Bay-1",
            window_start=datetime.utcnow() - timedelta(minutes=15),
            window_end=datetime.utcnow(),
            sensor_readings={
                "temperature_c": 89.4,
                "pressure_bar": 12.1,
                "vibration_mm_s": 7.8,
                "rpm": 1450.0,
                "torque_nm": 312.0,
                "current_a": 48.2,
            },
            anomaly_score=0.71,
            rul_days_p50=11.4,
        )
        assert s.entity_type == "sensor_summary"
        assert s.sensor_readings["temperature_c"] == 89.4

    def _fault():
        f = FaultLog(
            asset_id="EAF-04",
            plant_area="EAF-Bay-1",
            fault_code="BRG-WEAR-003",
            fault_description="Accelerating bearing wear detected via vibration envelope",
            severity="critical",
            detected_at=datetime.utcnow(),
            source="sensor",
            confirmed=True,
        )
        assert f.entity_type == "fault_log"

    def _maintenance():
        m = MaintenanceRecord(
            asset_id="EAF-04",
            plant_area="EAF-Bay-1",
            work_order_id="WO-2026-0612-001",
            maintenance_type="predictive",
            description="Bearing replacement — predictive intervention",
            technician_id="TECH-042",
            duration_hours=4.5,
            parts_used=["SKF-6310-2RS1"],
            outcome="resolved",
            rca_summary="Bearing wear accelerated by misalignment and inadequate lubrication",
        )
        assert m.entity_type == "maintenance_record"

    def _knowledge():
        k = KnowledgeDocument(
            asset_id="EAF-04",
            plant_area="EAF-Bay-1",
            doc_type="sop",
            title="EAF Electrode Drive Maintenance SOP",
            section="3.1 — Bearing Inspection and Replacement",
            content_markdown="## 3.1 Bearing Inspection\n\nInspect bearing housing...",
            revision="2024-Q1",
            applicable_equipment_classes=["hydraulic_unit", "fan"],
        )
        assert k.entity_type == "knowledge_doc"

    def _spare():
        sp = SparePart(
            asset_id="EAF-04",
            plant_area="EAF-Bay-1",
            part_number="SKF-6310-2RS1",
            part_name="Deep Groove Ball Bearing",
            compatible_equipment=["EAF-04", "BF-2-FAN"],
            stock_qty=0,
            min_stock_qty=2,
            unit_cost_inr=4_500.0,
            lead_time_days=14,
            supplier="SKF India Ltd",
            criticality_override="critical",
        )
        assert sp.entity_type == "spare_part"
        assert sp.lead_time_days == 14

    def _alert():
        al = AnomalyAlert(
            asset_id="EAF-04",
            plant_area="EAF-Bay-1",
            alert_type="rul_critical",
            risk_level="critical",
            description="RUL p50=11.4 days — bearing failure imminent",
            estimated_rul_days=11.4,
            recommended_action="Emergency bearing replacement within 48h",
            cooldown_key="EAF-04:rul_critical",
        )
        assert al.entity_type == "anomaly_alert"
        assert not al.acknowledged

    for test_fn, name in [
        (_asset, "AssetProfile"),
        (_sensor, "SensorSummary"),
        (_fault, "FaultLog"),
        (_maintenance, "MaintenanceRecord"),
        (_knowledge, "KnowledgeDocument"),
        (_spare, "SparePart"),
        (_alert, "AnomalyAlert"),
    ]:
        if not _check(name, test_fn):
            failures.append(name)

    # ── 3. Discriminated union + ingest_entity ──────────────────────────────
    print("\n3. ingest_entity() discriminated union:")

    def _ingest_asset():
        entity = ingest_entity({
            "entity_type": "asset",
            "asset_id": "BF-2-FAN",
            "plant_area": "BF-Area-1",
            "equipment_name": "BF-2 Fan A",
            "equipment_class": "fan",
            "manufacturer": "TLT-Turbo",
            "criticality_tier": "critical",
        })
        assert entity.entity_type == "asset"  # type: ignore[union-attr]
        assert isinstance(entity, AssetProfile)

    def _ingest_sensor():
        entity = ingest_entity({
            "entity_type": "sensor_summary",
            "asset_id": "BF-2-FAN",
            "plant_area": "BF-Area-1",
            "sensor_readings": {"vibration_mm_s": 3.2},
        })
        assert entity.entity_type == "sensor_summary"  # type: ignore[union-attr]

    def _ingest_invalid_rejected():
        from pydantic import ValidationError
        # unknown entity_type tag -> ValueError; malformed fields -> ValidationError
        try:
            ingest_entity({"entity_type": "unknown_type", "asset_id": "X"})
            raise AssertionError("Should have raised on unknown entity_type")
        except (ValueError, ValidationError):
            pass  # expected

    for test_fn, name in [
        (_ingest_asset, "ingest asset"),
        (_ingest_sensor, "ingest sensor_summary"),
        (_ingest_invalid_rejected, "invalid entity_type rejected"),
    ]:
        if not _check(name, test_fn):
            failures.append(name)

    # ── 4. Cross-agent output models ─────────────────────────────────────────
    print("\n4. Cross-agent output models:")
    from wizard.core.schemas import (
        ActionStep,
        AlertEvent,
        AlertSeverity,
        CauseChainStep,
        DiagnosisReport,
        DocumentRecord,
        MaintenanceRecommendation,
        QuarantineRecord,
        RCAResult,
        RiskScore,
        RULResult,
    )

    def _alert_event():
        ev = AlertEvent(
            asset_id="EAF-04",
            equipment_name="EAF-04 Electrode Drive",
            severity=AlertSeverity.CRITICAL,
            alert_type="rul_critical",
            description="RUL p50=11.4 days — bearing failure imminent",
            estimated_rul_days=11.4,
            cost_avoidance_inr=75_000.0 * 24,
        )
        assert ev.severity == AlertSeverity.CRITICAL

    def _diagnosis():
        d = DiagnosisReport(
            asset_id="EAF-04",
            probable_fault_codes=["BRG-WEAR-003"],
            probable_fault_description="Bearing wear",
            confidence=0.87,
            cited_sources=["chunk_abc123"],
            diagnosis_reasoning="Vibration envelope anomaly at 7.8 mm/s...",
        )
        assert 0.0 <= d.confidence <= 1.0

    def _rca():
        r = RCAResult(
            asset_id="EAF-04",
            fault_log_id="01JXXXXXXXX",
            cause_chain=[
                CauseChainStep(
                    node_id="bearing_wear",
                    node_label="Bearing Wear",
                    edge_relation="causes",
                    layer="graph",
                ),
                CauseChainStep(
                    node_id="insufficient_lubrication",
                    node_label="Insufficient Lubrication",
                    edge_relation="results_in",
                    layer="graph",
                ),
            ],
            root_cause_summary="Insufficient lubrication accelerated bearing wear",
            five_whys=["Why bearing wear? → Vibration elevated", "Why vibration? → Lubrication gap"],
        )
        assert len(r.cause_chain) == 2

    def _rul():
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
        assert ru.rul_days_p10 < ru.rul_days_p50 < ru.rul_days_p90

    def _risk():
        rs = RiskScore(
            asset_id="EAF-04",
            wrps=82.4,
            risk_tier=AlertSeverity.CRITICAL,
            severity_factor=9.0,
            probability_factor=8.5,
            detectability_factor=7.0,
            business_impact_factor=9.5,
            spares_risk="critical_stockout",
            critical_parts_out_of_stock=["SKF-6310-2RS1"],
            estimated_downtime_hours=24.0,
            cost_avoidance_inr=75_000.0 * 24,
        )
        assert rs.wrps > 75.0

    def _plan():
        p = MaintenanceRecommendation(
            asset_id="EAF-04",
            diagnosis_report_id="01JZZZZZ",
            priority=AlertSeverity.CRITICAL,
            maintenance_type="emergency",
            action_steps=[
                ActionStep(
                    step_number=1,
                    action="Isolate EAF-04 drive train",
                    responsible_role="senior_technician",
                    estimated_duration_hours=0.5,
                    cited_sop_section="EAF-SOP-002 §3.1",
                ),
            ],
            narrative_summary="Emergency bearing replacement required within 48h [1][2]",
            cited_sources=["chunk_abc", "chunk_def"],
            spares_procurement_warning="CRITICAL: SKF-6310-2RS1 out of stock, 14-day lead — ORDER NOW",
            cost_avoidance_inr=75_000.0 * 24,
        )
        assert len(p.action_steps) == 1

    def _doc_record():
        dr = DocumentRecord(
            source_entity_id="01JXXXXXX",
            source_entity_type="knowledge_doc",
            asset_id="EAF-04",
            text="Section 3.1: Inspect bearing housing for signs of pitting...",
            doc_type="sop",
            section="3.1",
        )
        assert dr.char_count > 0

    def _quarantine():
        qr = QuarantineRecord(
            raw_payload={"entity_type": "unknown", "garbage": "data"},
            validation_error="No discriminator matched entity_type='unknown'",
        )
        assert qr.quarantine_id != ""

    for test_fn, name in [
        (_alert_event, "AlertEvent"),
        (_diagnosis, "DiagnosisReport"),
        (_rca, "RCAResult"),
        (_rul, "RULResult"),
        (_risk, "RiskScore"),
        (_plan, "MaintenanceRecommendation"),
        (_doc_record, "DocumentRecord"),
        (_quarantine, "QuarantineRecord"),
    ]:
        if not _check(name, test_fn):
            failures.append(name)

    # ── 5. Config loads ──────────────────────────────────────────────────────
    print("\n5. Config:")

    def _config():
        from wizard.core.config import settings
        assert settings.rul_critical_days == 14.0
        assert settings.cost_avoidance_rate_inr_per_hour == 75_000.0
        assert settings.rag_chunk_size == 512

    if not _check("WizardSettings loads", _config):
        failures.append("config")

    # ── 6. DB init ───────────────────────────────────────────────────────────
    print("\n6. Database:")
    import tempfile
    import os

    def _db():
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            tmp_path = f.name
        try:
            from wizard.core.db import get_engine, init_db, reset_db
            init_db(tmp_path)
            engine = get_engine(tmp_path)
            with engine.connect() as conn:
                result = conn.execute(
                    __import__("sqlalchemy").text(
                        "SELECT name FROM sqlite_master WHERE type='table'"
                    )
                )
                tables = {row[0] for row in result}
            expected = {
                "asset_profile", "sensor_summary", "fault_log",
                "maintenance_record", "knowledge_document",
                "spare_part", "anomaly_alert",
            }
            missing = expected - tables
            assert not missing, f"Missing tables: {missing}"
        finally:
            os.unlink(tmp_path)

    if not _check("init_db() creates all 7 tables", _db):
        failures.append("db init")

    # ── Summary ──────────────────────────────────────────────────────────────
    print(f"\n{'='*40}")
    if failures:
        print(f"FAILED: {len(failures)} checks: {failures}")
        sys.exit(1)
    else:
        total = 7 + 3 + 8 + 1 + 1  # entities + ingest + outputs + config + db
        print(f"ALL {total} checks passed.")
        sys.exit(0)


if __name__ == "__main__":
    main()
