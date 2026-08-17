"""
tests/test_backend_gaps.py
==========================
Tests for Track-B backend gap closures:
  §5.2 — GET /v1/bottlenecks (plant-wide WRPS ranking)
  §4.1 — fault_log delay_hours population + SCADA/control_system source coverage
  §4.4 — GET /v1/scenarios + POST /v1/scenarios/{id}/start

All tests use an isolated in-memory DB (isolated_engine fixture from test_db.py
pattern) so they are hermetic — no shared wizard.db state.
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="function")
def isolated_engine(tmp_path):
    """
    Fresh SQLite DB + cleared engine cache per test function.
    Mirrors the pattern in test_db.py.
    """
    import wizard.core.db as _db

    _db._engines.clear()
    db_file = str(tmp_path / "test_gaps.db")

    from wizard.core.db import init_db
    init_db(db_file)

    yield db_file

    _db._engines.clear()


@pytest.fixture(scope="function")
def populated_engine(isolated_engine):
    """
    Extends isolated_engine by seeding demo assets + fault_log rows so
    the WRPS bottleneck endpoint has real data to compute over.
    """
    from wizard.core.db import session_scope
    from wizard.core.schemas import AssetProfile, SensorSummary, SparePart, FaultLog

    with session_scope(isolated_engine) as session:
        # Seed two assets: one critical, one high
        assets = [
            AssetProfile(
                asset_id="EAF-TEST",
                plant_area="EAF-Bay-T",
                equipment_name="EAF Test Fan",
                equipment_class="fan",
                manufacturer="ABB",
                criticality_tier="critical",
            ),
            AssetProfile(
                asset_id="PUMP-TEST",
                plant_area="Utility-T",
                equipment_name="Test Cooling Pump",
                equipment_class="pump",
                manufacturer="KSB",
                criticality_tier="high",
            ),
        ]
        session.add_all(assets)

        # Seed sensor summaries
        sensor_rows = [
            SensorSummary(
                asset_id="EAF-TEST",
                plant_area="EAF-Bay-T",
                window_start=datetime.utcnow() - timedelta(hours=1),
                window_end=datetime.utcnow(),
                sensor_readings={"temperature_c": 95.0, "vibration_mm_s": 6.5},
                rul_days_p50=8.0,
                anomaly_score=0.82,
            ),
            SensorSummary(
                asset_id="PUMP-TEST",
                plant_area="Utility-T",
                window_start=datetime.utcnow() - timedelta(hours=1),
                window_end=datetime.utcnow(),
                sensor_readings={"temperature_c": 72.0, "vibration_mm_s": 2.1},
                rul_days_p50=30.0,
                anomaly_score=0.25,
            ),
        ]
        session.add_all(sensor_rows)

        # Seed spare parts for EAF-TEST (out-of-stock critical part → high WRPS)
        spare = SparePart(
            asset_id="EAF-TEST",
            plant_area="EAF-Bay-T",
            part_number="TEST-BRG-001",
            part_name="Test Bearing",
            stock_qty=0,
            min_stock_qty=2,
            lead_time_days=30,
            criticality_override="critical",
        )
        session.add(spare)

        # Seed fault_log with realistic delay_hours + SCADA sources (§4.1)
        faults = [
            FaultLog(
                asset_id="EAF-TEST",
                plant_area="EAF-Bay-T",
                fault_code="BRG-TEMP-HIGH-T01",
                fault_description="SCADA: bearing temperature 112°C.",
                severity="critical",
                delay_hours=18.5,
                source="scada",
                confirmed=True,
            ),
            FaultLog(
                asset_id="PUMP-TEST",
                plant_area="Utility-T",
                fault_code="PUMP-CAV-T01",
                fault_description="PLC: suction pressure low. Cavitation suspected.",
                severity="medium",
                delay_hours=4.0,
                source="control_system",
                confirmed=True,
            ),
            FaultLog(
                asset_id="EAF-TEST",
                plant_area="EAF-Bay-T",
                fault_code="VIB-HIGH-T01",
                fault_description="Operator: vibration elevated.",
                severity="high",
                delay_hours=6.5,
                source="operator",
                confirmed=True,
            ),
        ]
        session.add_all(faults)

    return isolated_engine


@pytest.fixture(scope="function")
def api_client(populated_engine, monkeypatch):
    """
    TestClient backed by a FastAPI app wired to the isolated populated DB.
    Overrides wizard.core.config.settings.db_path so the DB path is our
    test DB without touching the real wizard.db.
    """
    # Monkeypatch the engine cache so get_session uses our test DB
    import wizard.core.db as _db
    from wizard.core.db import get_engine, get_session

    def _patched_get_session():
        engine = get_engine(populated_engine)
        with Session(engine) as session:
            yield session

    # Import app AFTER patching session
    from wizard.backend.app import app
    from wizard import core as _core

    # Override the FastAPI dependency
    app.dependency_overrides[get_session] = _patched_get_session

    with TestClient(app, raise_server_exceptions=True) as client:
        yield client

    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# §5.2 — GET /v1/bottlenecks (plant-wide WRPS ranking)
# ---------------------------------------------------------------------------

class TestBottlenecks:
    def test_returns_200(self, api_client):
        resp = api_client.get("/v1/bottlenecks")
        assert resp.status_code == 200

    def test_response_schema_keys(self, api_client):
        resp = api_client.get("/v1/bottlenecks")
        body = resp.json()
        assert "items" in body
        assert "total" in body
        assert "computed_at" in body
        assert "note" in body

    def test_items_is_non_empty_list(self, api_client):
        resp = api_client.get("/v1/bottlenecks")
        body = resp.json()
        assert isinstance(body["items"], list)
        assert body["total"] > 0

    def test_items_have_required_fields(self, api_client):
        resp = api_client.get("/v1/bottlenecks")
        item = resp.json()["items"][0]
        for field in (
            "asset_id", "equipment_name", "wrps_score", "risk_tier",
            "process_criticality", "delay_severity",
            "spares_availability", "procurement_lead_factor", "top_reason",
        ):
            assert field in item, f"Missing field: {field}"

    def test_ranked_descending_by_wrps(self, api_client):
        resp = api_client.get("/v1/bottlenecks")
        items = resp.json()["items"]
        if len(items) >= 2:
            scores = [i["wrps_score"] for i in items]
            assert scores == sorted(scores, reverse=True), (
                f"Items not ranked descending: {scores}"
            )

    def test_wrps_score_in_valid_range(self, api_client):
        resp = api_client.get("/v1/bottlenecks")
        for item in resp.json()["items"]:
            assert 0.0 <= item["wrps_score"] <= 100.0, (
                f"WRPS out of [0,100]: {item['wrps_score']} for {item['asset_id']}"
            )

    def test_risk_tier_valid_enum(self, api_client):
        valid_tiers = {"low", "medium", "high", "critical"}
        resp = api_client.get("/v1/bottlenecks")
        for item in resp.json()["items"]:
            assert item["risk_tier"] in valid_tiers, (
                f"Invalid risk_tier: {item['risk_tier']}"
            )

    def test_factor_scores_in_unit_interval(self, api_client):
        resp = api_client.get("/v1/bottlenecks")
        for item in resp.json()["items"]:
            for field in ("process_criticality", "delay_severity",
                          "spares_availability", "procurement_lead_factor"):
                v = item[field]
                assert 0.0 <= v <= 1.0, f"{field}={v} out of [0,1] for {item['asset_id']}"

    def test_top_reason_is_non_empty_string(self, api_client):
        resp = api_client.get("/v1/bottlenecks")
        for item in resp.json()["items"]:
            assert isinstance(item["top_reason"], str)
            assert len(item["top_reason"]) > 0


# ---------------------------------------------------------------------------
# §4.1 — fault_log delay_hours + SCADA/control_system sources (WRPS F2 data)
# ---------------------------------------------------------------------------

class TestFaultLogData:
    def test_delay_hours_non_null_count_positive(self, populated_engine):
        """At least one fault_log row has delay_hours populated (§4.1 MET)."""
        from wizard.core.db import session_scope
        from wizard.core.schemas import FaultLog

        with session_scope(populated_engine) as session:
            all_faults = session.exec(select(FaultLog)).all()
            non_null = [f for f in all_faults if f.delay_hours is not None]
        assert len(non_null) > 0, "No fault_log rows have delay_hours set"

    def test_scada_source_rows_exist(self, populated_engine):
        """At least one fault_log row has source in ('scada', 'control_system') (§4.1 MET)."""
        from wizard.core.db import session_scope
        from wizard.core.schemas import FaultLog

        with session_scope(populated_engine) as session:
            all_faults = session.exec(select(FaultLog)).all()
            control_rows = [f for f in all_faults if f.source in ("scada", "control_system")]
        assert len(control_rows) > 0, "No fault_log rows with scada/control_system source"

    def test_delay_hours_realistic_range(self, populated_engine):
        """delay_hours values are in a sensible range (2–48h)."""
        from wizard.core.db import session_scope
        from wizard.core.schemas import FaultLog

        with session_scope(populated_engine) as session:
            faults = session.exec(select(FaultLog)).all()
            hours_values = [f.delay_hours for f in faults if f.delay_hours is not None]

        for h in hours_values:
            assert 0.0 < h <= 48.0, f"delay_hours={h} outside expected range"

    def test_wrps_uses_delay_hours_not_zero(self, populated_engine):
        """WRPS F2 factor (delay_severity) is non-zero when delay_hours is set."""
        from wizard.backend.wrps import score_maintenance_priority_for_session
        from wizard.core.db import session_scope

        with session_scope(populated_engine) as session:
            score, breakdown = score_maintenance_priority_for_session("EAF-TEST", session)
        # EAF-TEST has delay_hours=18.5 → delay_severity = 18.5/72 ≈ 0.257
        assert breakdown.get("delay_severity", 0.0) > 0.0, (
            f"delay_severity is zero despite delay_hours=18.5: {breakdown}"
        )


# ---------------------------------------------------------------------------
# §4.1 — seed_fault_log idempotency
# ---------------------------------------------------------------------------

class TestSeedFaultLog:
    def test_seed_fault_log_inserts_rows(self, isolated_engine):
        """seed_fault_log inserts >0 rows into a fresh DB."""
        from wizard.data.db_ingest import seed_fault_log
        n = seed_fault_log(isolated_engine)
        assert n > 0

    def test_seed_fault_log_idempotent(self, isolated_engine):
        """Re-seeding does not insert duplicate rows."""
        from wizard.data.db_ingest import seed_fault_log
        n1 = seed_fault_log(isolated_engine)
        n2 = seed_fault_log(isolated_engine)
        assert n1 > 0
        assert n2 == 0, f"Second seed inserted {n2} rows (expected 0)"

    def test_seed_fault_log_has_delay_hours(self, isolated_engine):
        """After seeding, delay_hours is non-null for at least some rows."""
        from wizard.data.db_ingest import seed_fault_log
        from wizard.core.db import session_scope
        from wizard.core.schemas import FaultLog

        seed_fault_log(isolated_engine)
        with session_scope(isolated_engine) as session:
            all_f = session.exec(select(FaultLog)).all()
            nn = [f for f in all_f if f.delay_hours is not None]
        assert len(nn) > 0

    def test_seed_fault_log_has_scada_rows(self, isolated_engine):
        """After seeding, at least one row has source='scada' or 'control_system'."""
        from wizard.data.db_ingest import seed_fault_log
        from wizard.core.db import session_scope
        from wizard.core.schemas import FaultLog

        seed_fault_log(isolated_engine)
        with session_scope(isolated_engine) as session:
            all_f = session.exec(select(FaultLog)).all()
            ctrl = [f for f in all_f if f.source in ("scada", "control_system")]
        assert len(ctrl) > 0


# ---------------------------------------------------------------------------
# §4.4 — GET /v1/scenarios
# ---------------------------------------------------------------------------

class TestScenarios:
    def test_scenarios_endpoint_200(self, api_client):
        resp = api_client.get("/v1/scenarios")
        assert resp.status_code == 200

    def test_scenarios_response_schema(self, api_client):
        resp = api_client.get("/v1/scenarios")
        body = resp.json()
        assert "scenarios" in body
        assert "total" in body

    def test_scenarios_non_empty(self, api_client):
        resp = api_client.get("/v1/scenarios")
        body = resp.json()
        assert body["total"] > 0
        assert len(body["scenarios"]) > 0

    def test_scenario_item_required_fields(self, api_client):
        resp = api_client.get("/v1/scenarios")
        for scenario in resp.json()["scenarios"]:
            for field in ("id", "title", "equipment_class", "equipment_id",
                          "prompt", "difficulty"):
                assert field in scenario, f"Missing field '{field}' in scenario"

    def test_scenario_prompt_is_substantive(self, api_client):
        """Each scenario prompt is at least 100 characters."""
        resp = api_client.get("/v1/scenarios")
        for s in resp.json()["scenarios"]:
            assert len(s["prompt"]) >= 100, (
                f"Scenario {s['id']} prompt too short: {len(s['prompt'])} chars"
            )

    def test_equipment_class_filter(self, api_client):
        resp = api_client.get("/v1/scenarios?equipment_class=fan")
        body = resp.json()
        if body["total"] > 0:
            for s in body["scenarios"]:
                assert s["equipment_class"] == "fan"

    def test_difficulty_filter(self, api_client):
        resp = api_client.get("/v1/scenarios?difficulty=hard")
        body = resp.json()
        if body["total"] > 0:
            for s in body["scenarios"]:
                assert s["difficulty"] == "hard"

    def test_difficulty_values_are_valid(self, api_client):
        valid = {"easy", "medium", "hard"}
        resp = api_client.get("/v1/scenarios")
        for s in resp.json()["scenarios"]:
            assert s["difficulty"] in valid


# ---------------------------------------------------------------------------
# §4.4 — POST /v1/scenarios/{id}/start
# ---------------------------------------------------------------------------

class TestScenarioStart:
    def test_start_valid_scenario_200(self, api_client):
        # First get a valid scenario id
        scenarios = api_client.get("/v1/scenarios").json()["scenarios"]
        if not scenarios:
            pytest.skip("No scenarios loaded")
        scenario_id = scenarios[0]["id"]
        resp = api_client.post(f"/v1/scenarios/{scenario_id}/start")
        assert resp.status_code == 200

    def test_start_response_schema(self, api_client):
        scenarios = api_client.get("/v1/scenarios").json()["scenarios"]
        if not scenarios:
            pytest.skip("No scenarios loaded")
        scenario_id = scenarios[0]["id"]
        body = api_client.post(f"/v1/scenarios/{scenario_id}/start").json()
        for field in ("scenario_id", "title", "equipment_id",
                      "chat_seed_query", "suggested_session_id", "note"):
            assert field in body, f"Missing field: {field}"

    def test_start_chat_seed_query_matches_scenario_prompt(self, api_client):
        scenarios = api_client.get("/v1/scenarios").json()["scenarios"]
        if not scenarios:
            pytest.skip("No scenarios loaded")
        s = scenarios[0]
        body = api_client.post(f"/v1/scenarios/{s['id']}/start").json()
        assert body["chat_seed_query"] == s["prompt"]

    def test_start_returns_unique_session_ids(self, api_client):
        scenarios = api_client.get("/v1/scenarios").json()["scenarios"]
        if not scenarios:
            pytest.skip("No scenarios loaded")
        scenario_id = scenarios[0]["id"]
        body1 = api_client.post(f"/v1/scenarios/{scenario_id}/start").json()
        body2 = api_client.post(f"/v1/scenarios/{scenario_id}/start").json()
        assert body1["suggested_session_id"] != body2["suggested_session_id"]

    def test_start_unknown_scenario_404(self, api_client):
        resp = api_client.post("/v1/scenarios/SCN-DOES-NOT-EXIST/start")
        assert resp.status_code == 404
        # Should be our error envelope
        body = resp.json()
        assert "error" in body


# ---------------------------------------------------------------------------
# §5.2 — WRPS engine unit tests
# ---------------------------------------------------------------------------

class TestWRPS:
    def test_score_returns_risk_score_for_known_asset(self, populated_engine):
        from wizard.backend.wrps import score_maintenance_priority_for_session
        from wizard.core.db import session_scope

        with session_scope(populated_engine) as session:
            score, breakdown = score_maintenance_priority_for_session("EAF-TEST", session)

        assert score.wrps >= 0.0
        assert score.wrps <= 100.0
        assert score.asset_id == "EAF-TEST"
        assert set(breakdown.keys()) == {
            "process_criticality", "delay_severity",
            "spare_availability", "lead_time", "ml_signal",
        }

    def test_score_critical_asset_higher_than_high_asset(self, populated_engine):
        """EAF-TEST (critical) should score >= PUMP-TEST (high)."""
        from wizard.backend.wrps import score_maintenance_priority_for_session
        from wizard.core.db import session_scope

        with session_scope(populated_engine) as session:
            score_eaf, _ = score_maintenance_priority_for_session("EAF-TEST", session)
            score_pump, _ = score_maintenance_priority_for_session("PUMP-TEST", session)

        assert score_eaf.wrps >= score_pump.wrps, (
            f"EAF WRPS={score_eaf.wrps} should >= PUMP WRPS={score_pump.wrps}"
        )

    def test_score_unknown_asset_returns_low(self, populated_engine):
        from wizard.backend.wrps import score_maintenance_priority_for_session
        from wizard.core.db import session_scope
        from wizard.core.schemas import AlertSeverity

        with session_scope(populated_engine) as session:
            score, breakdown = score_maintenance_priority_for_session(
                "DOES-NOT-EXIST", session
            )

        assert score.wrps == 0.0
        assert score.risk_tier == AlertSeverity.LOW
        assert breakdown == {}
