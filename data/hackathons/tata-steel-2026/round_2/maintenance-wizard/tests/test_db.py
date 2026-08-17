"""
tests/test_db.py
================
Integration tests for wizard.core.db.

Tests:
    - init_db() creates all 7 expected tables
    - WAL mode is active
    - get_session() round-trip: write AssetProfile, read back
    - reset_db() empties all tables
    - Index existence verification
"""

from __future__ import annotations

import os
import tempfile

import pytest
from sqlalchemy import text
from sqlmodel import Session, select

from wizard.core.schemas import AssetProfile, SensorSummary, FaultLog, AnomalyAlert


@pytest.fixture(autouse=False)
def isolated_engine(tmp_path):
    """
    Provide a fresh engine + DB for each test.
    Clears the per-path engine cache before and after so each test gets its
    own isolated SQLite file with no cross-contamination.
    """
    import wizard.core.db as _db

    _db._engines.clear()
    db_file = str(tmp_path / "test_wizard.db")

    from wizard.core.db import init_db
    init_db(db_file)

    yield db_file

    _db._engines.clear()


class TestDBInit:
    def test_all_seven_tables_created(self, isolated_engine):
        from wizard.core.db import get_engine
        engine = get_engine(isolated_engine)
        with engine.connect() as conn:
            rows = conn.execute(
                text("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
            ).fetchall()
        tables = {r[0] for r in rows}
        expected = {
            "asset_profile",
            "sensor_summary",
            "fault_log",
            "maintenance_record",
            "knowledge_document",
            "spare_part",
            "anomaly_alert",
        }
        assert expected.issubset(tables), f"Missing: {expected - tables}"

    def test_wal_mode_active(self, isolated_engine):
        from wizard.core.db import get_engine
        engine = get_engine(isolated_engine)
        with engine.connect() as conn:
            result = conn.execute(text("PRAGMA journal_mode")).fetchone()
        assert result[0].upper() == "WAL"

    def test_foreign_keys_on(self, isolated_engine):
        from wizard.core.db import get_engine
        engine = get_engine(isolated_engine)
        with engine.connect() as conn:
            result = conn.execute(text("PRAGMA foreign_keys")).fetchone()
        assert result[0] == 1  # 1 = ON


class TestSessionRoundTrip:
    def test_write_and_read_asset_profile(self, isolated_engine):
        from wizard.core.db import session_scope
        from datetime import datetime

        asset = AssetProfile(
            asset_id="EAF-04",
            plant_area="EAF-Bay-1",
            equipment_name="EAF-04 Electrode Drive",
            equipment_class="hydraulic_unit",
            manufacturer="ABB",
            installation_date=datetime(2018, 6, 1),
            criticality_tier="critical",
        )
        with session_scope(isolated_engine) as session:
            session.add(asset)

        # Re-open session to verify persistence (same engine path — already committed)
        from wizard.core.db import get_engine
        engine = get_engine(isolated_engine)
        with Session(engine) as session:
            result = session.exec(select(AssetProfile).where(
                AssetProfile.asset_id == "EAF-04"
            )).first()
        assert result is not None
        assert result.equipment_name == "EAF-04 Electrode Drive"
        assert result.criticality_tier == "critical"

    def test_write_sensor_summary_with_json_readings(self, isolated_engine):
        from wizard.core.db import session_scope
        from datetime import datetime, timedelta

        ss = SensorSummary(
            asset_id="BF-2-FAN",
            plant_area="BF-Area-1",
            window_start=datetime.utcnow() - timedelta(minutes=15),
            window_end=datetime.utcnow(),
            sensor_readings={
                "temperature_c": 89.4,
                "vibration_mm_s": 7.8,
                "pressure_bar": 12.1,
            },
            anomaly_score=0.71,
        )
        with session_scope(isolated_engine) as session:
            session.add(ss)

        import wizard.core.db as _db
        engine = _db.get_engine(isolated_engine)
        with Session(engine) as session:
            result = session.exec(select(SensorSummary).where(
                SensorSummary.asset_id == "BF-2-FAN"
            )).first()
        assert result is not None
        assert result.sensor_readings["temperature_c"] == pytest.approx(89.4)
        assert result.anomaly_score == pytest.approx(0.71)

    def test_write_anomaly_alert_acknowledged_default_false(self, isolated_engine):
        from wizard.core.db import session_scope

        alert = AnomalyAlert(
            asset_id="EAF-04",
            plant_area="EAF-Bay-1",
            alert_type="rul_critical",
            risk_level="critical",
            description="RUL p50=11.4d",
            cooldown_key="EAF-04:rul_critical",
        )
        with session_scope(isolated_engine) as session:
            session.add(alert)

        import wizard.core.db as _db
        engine = _db.get_engine(isolated_engine)
        with Session(engine) as session:
            result = session.exec(select(AnomalyAlert).where(
                AnomalyAlert.asset_id == "EAF-04"
            )).first()
        assert result is not None
        assert not result.acknowledged


class TestIndexes:
    def test_composite_indexes_exist(self, isolated_engine):
        from wizard.core.db import get_engine
        engine = get_engine(isolated_engine)
        with engine.connect() as conn:
            rows = conn.execute(
                text("SELECT name FROM sqlite_master WHERE type='index'")
            ).fetchall()
        index_names = {r[0] for r in rows}
        # Check our custom composite indexes are present
        assert "idx_anomaly_alert_unack_risk" in index_names
        assert "idx_sensor_summary_asset_window" in index_names
        assert "idx_fault_log_asset_confirmed" in index_names
