"""WAVE 1 foundation tests — config, loaders, and the LLM provider ladder.

Network-independent tests run by default. The live-Claude round-trip is gated
behind VULCAN_TEST_LIVE=1 so CI / offline runs don't depend on the subscription.

    PY=/home/ujjwal/Documents/J.A.R.V.I.S./.venv/bin/python
    $PY -m pytest tests/test_foundation.py -v
    VULCAN_TEST_LIVE=1 $PY -m pytest tests/test_foundation.py -v   # + live Claude
"""

from __future__ import annotations

import hashlib
import importlib
import json
import os
from pathlib import Path

import pytest

import vulcan.config as cfg
import vulcan.llm as llm
from vulcan.data.loaders import get_datastore


# ---------------------------------------------------------------------------
# config
# ---------------------------------------------------------------------------
def test_anthropic_api_key_scrubbed_at_import():
    assert "ANTHROPIC_API_KEY" not in os.environ


def test_settings_paths_exist():
    s = cfg.get_settings()
    assert s.dataset_root.is_dir()
    assert s.spine_path.is_file()
    assert s.llm_mode in ("cache_first", "live", "off")
    assert s.llm_provider in ("subscription", "local_slm", "template")


def test_oauth_walk_up_finds_token():
    # Repo-root .env carries the token; walk-up must resolve it.
    assert cfg.load_oauth_token(), "OAuth token should resolve from repo-root .env"


# ---------------------------------------------------------------------------
# loaders
# ---------------------------------------------------------------------------
def test_spine_loads_15_assets_51_scenarios():
    sp = get_datastore().spine()
    assert len(sp.assets) == 15
    assert len(sp.scenarios) == 51
    assert sp.asset("HSM.F3.WR.BRG01") is not None


def test_sensor_to_asset_index():
    sp = get_datastore().spine()
    a = sp.asset_for_sensor("JSR.HR.STD3.WR.BRG01.VIB.DE.H.RMS")
    assert a is not None and a.asset_id == "HSM.F3.WR.BRG01"


def test_dataset_summary_nonzero():
    summ = get_datastore().summary()
    for key in ("assets", "scenarios", "spare_catalog", "incidents", "equipment_manuals"):
        assert summ[key] > 0


def test_eval_sets_present():
    ds = get_datastore()
    assert len(ds.nl_queries()) == 150
    assert len(ds.multiturn_conversations()) == 50


# ---------------------------------------------------------------------------
# LLM ladder
# ---------------------------------------------------------------------------
def test_l0_cache_hit_is_instant(tmp_path, monkeypatch):
    sysmsg, usermsg = "SYS", "Q?"
    key = hashlib.sha256(f"{sysmsg}\x00{usermsg}".encode()).hexdigest()
    cache_file = tmp_path / "cache.json"
    cache_file.write_text(json.dumps({"entries": [{"key": key, "response": "CACHED"}]}))
    monkeypatch.setenv("VULCAN_DEMO_CACHE", str(cache_file))
    cfg.get_settings.cache_clear()
    llm._DEMO_CACHE = None
    r = llm.subscription_llm(sysmsg, usermsg, return_result=True)
    assert r.rung == "cache" and r.text == "CACHED" and r.latency_ms < 100
    cfg.get_settings.cache_clear()
    llm._DEMO_CACHE = None


def test_template_floor_when_no_token(monkeypatch):
    # Force every live rung to fail -> must return template, never raise.
    monkeypatch.setattr(llm, "load_oauth_token", lambda: None)
    monkeypatch.setattr(llm, "_slm_rung", lambda *a, **k: None)
    r = llm.subscription_llm(
        "You are EDITH.", "Diagnose bearing.", task="diagnosis",
        context="VIB = 6.0 mm/s", return_result=True,
    )
    assert r.rung == "template" and r.is_template is True
    assert "VULCAN" in r.text and "6.0" in r.text


def test_subscription_llm_never_raises(monkeypatch):
    # If the Claude rung blows up internally, the chokepoint must still return text.
    def _boom(*a, **k):
        raise RuntimeError("simulated SDK explosion")
    monkeypatch.setattr(llm, "_claude_collect", _boom)
    monkeypatch.setattr(llm, "_slm_rung", lambda *a, **k: None)
    out = llm.subscription_llm("S", "U")
    assert isinstance(out, str) and out


def test_ladder_status_shape():
    st = llm.ladder_status()
    assert st["product"] == "VULCAN" and st["persona"] == "EDITH"
    assert st["anthropic_api_key_scrubbed"] is True


@pytest.mark.skipif(os.getenv("VULCAN_TEST_LIVE") != "1",
                    reason="set VULCAN_TEST_LIVE=1 to hit the live Claude subscription")
def test_live_claude_roundtrip_no_key():
    assert "ANTHROPIC_API_KEY" not in os.environ
    r = llm.subscription_llm(
        "You are a terse assistant.", "Reply with exactly the word PONG.",
        task="diagnosis", return_result=True,
    )
    # Could be cache/claude depending on state; if claude, it proves keyless OAuth works.
    assert r.text and r.rung in ("claude", "cache")
