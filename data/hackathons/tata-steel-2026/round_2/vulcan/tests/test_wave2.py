"""WAVE 2 tests — RAG, ML, and deterministic tools.

Heavy tests (RAG retrieval, ML inference) are skipped automatically if the
artifacts aren't built yet (ingest / train). Run them after:

    PY=/home/ujjwal/Documents/J.A.R.V.I.S./.venv/bin/python
    $PY -m vulcan.rag.store          # ingest corpus -> data/vectordb/
    $PY -c "from vulcan.ml.models import train_all; train_all()"   # train models
    $PY -m pytest tests/test_wave2.py -v
"""

from __future__ import annotations

import pytest

from vulcan.tools import data_tools as T
from vulcan.rag import collection_count
from vulcan.ml.registry import models_dir


# ===========================================================================
# TOOLS — pure deterministic, always runnable (no artifacts needed)
# ===========================================================================
def test_get_asset_real_value():
    a = T.get_asset("BF.BLW.FAN01")
    assert a["found"] is True
    assert a["equipment_class"] == "bf_sinter_fan_blower"
    assert a["criticality"] == 1
    assert a["sensor_count"] == 5
    assert a["source"].endswith("ground_truth_spine.json")


def test_get_asset_forgiving_resolution():
    assert T.get_asset("bf-blw-fan01")["found"] is True          # case/sep variant
    assert T.get_asset("JSR.BF.BLW.FAN01.VIB.1X")["found"] is True  # sensor tag


def test_get_asset_not_found():
    assert T.get_asset("NOPE.123")["found"] is False


def test_get_thresholds_iso_backed():
    th = T.get_thresholds("HSM.F3.WR.BRG01")
    assert th["found"] is True
    s0 = th["sensors"][0]
    assert s0["warning_threshold"] is not None
    assert s0["alarm_threshold"] is not None
    assert "ISO" in (s0["standard"] or "")


def test_get_scenario_p1_surge():
    scn = T.get_scenario("SCN-041")
    assert scn["found"] is True
    assert scn["safety_class"] == "P1"
    assert scn["failure_mode"] == "compressor_surge"
    assert scn["cost_impact"]["inr"] == 500_000_000


def test_get_spare_procurement_recommendation():
    sp = T.get_spare("ASV-VLV-01")
    assert sp["found"] is True
    assert "ORDER NOW" in sp["recommendation"]      # not in stock, 12-wk lead
    assert sp["lead_time_weeks"] >= 12


def test_get_spares_for_scenario_aggregates():
    out = T.get_spares_for_scenario("SCN-041")
    assert out["procurement_action_required"] is True
    assert out["max_lead_time_weeks"] >= 12
    assert out["total_parts_cost_inr"] > 0


def test_get_recent_alerts_and_history():
    al = T.get_recent_alerts("BF.BLW.FAN01", limit=5)
    assert al["found"] is True and al["total_alerts"] > 0
    h = T.search_history("BF.BLW.FAN01", limit=3)
    assert h["found"] is True and h["incident_count"] > 0


def test_get_sensor_reading_annotates_status():
    r = T.get_sensor_reading("BF.BLW.FAN01")
    assert r["found"] is True
    assert r["readings"], "should have sensor readings"
    assert all("status" in x for x in r["readings"])


# ===========================================================================
# RAG — requires ingested collection
# ===========================================================================
rag_ready = pytest.mark.skipif(collection_count() == 0, reason="RAG corpus not ingested")


@rag_ready
def test_rag_retrieve_bearing_query():
    from vulcan.rag import retrieve
    chunks = retrieve("bearing outer race BPFO vibration spall", top_k=5)
    assert len(chunks) >= 1
    # every chunk carries a source filename for citation
    assert all(c.source for c in chunks)
    # the bearing RCA or SOP should surface in the top results
    top_sources = " ".join(c.source.lower() for c in chunks)
    assert "brg" in top_sources or "bearing" in top_sources


@rag_ready
def test_rag_chunk_has_citation():
    from vulcan.rag import retrieve
    chunks = retrieve("compressor surge anti-surge valve", top_k=3)
    assert chunks and chunks[0].citation().startswith("[")


# ===========================================================================
# ML — requires trained artifacts
# ===========================================================================
def _ml_ready() -> bool:
    return (models_dir() / "fault_BFBLWFAN01.pkl").exists()


ml_ready = pytest.mark.skipif(not _ml_ready(), reason="ML artifacts not trained")


@ml_ready
def test_predict_fault_normal_on_latest():
    from vulcan.ml import predict_fault
    r = predict_fault("BF.BLW.FAN01")
    assert r["found"] is True
    assert r["predicted_class"] in ("NORMAL", "WARNING", "FAILURE")
    assert abs(sum(r["probabilities"].values()) - 1.0) < 0.05


@ml_ready
def test_predict_fault_fires_on_failure_window():
    import pandas as pd
    from vulcan.ml import predict_fault, anomaly_score
    from vulcan.ml.features import sensor_columns
    from vulcan.config import get_settings
    p = get_settings().condition_dir / "by_equipment" / "bf_sinter_fan_blower__BF_BLW_FAN01.csv"
    df = pd.read_csv(p)
    scols = sensor_columns(df)
    fail = df.index[df.fault_label == 2].tolist()
    assert fail, "dataset should contain failure rows"
    i = fail[len(fail) // 2]
    win = df[scols].iloc[max(0, i - 23): i + 1].to_dict("records")
    assert predict_fault("BF.BLW.FAN01", window=win)["predicted_class"] == "FAILURE"
    assert anomaly_score("BF.BLW.FAN01", window=win)["is_anomaly"] is True


@ml_ready
def test_shared_class_assets_dont_collide():
    # the two bf_sinter_fan_blower assets have different sensor counts (5 vs 4)
    from vulcan.ml import predict_fault
    assert predict_fault("BF.BLW.FAN01")["found"] is True
    assert predict_fault("SP.SINT.FAN01")["found"] is True


@ml_ready
def test_estimate_rul_returns_cycles():
    from vulcan.ml import estimate_rul
    r = estimate_rul("HSM.F3.WR.BRG01")
    assert r["found"] is True
    assert r["rul_cycles"] is not None and r["rul_cycles"] >= 0
