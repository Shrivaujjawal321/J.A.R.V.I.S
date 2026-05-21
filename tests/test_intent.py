"""Unit tests for jarvis_core/intent.py.

Strategy: monkeypatch `jarvis_core.intent.run_worker` to return canned
JSON outputs. This isolates classification, parsing, priority rules,
and the skip-cases from the live LLM.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

import pytest

from jarvis_core import intent as intent_mod
from jarvis_core.intent import (
    CATEGORIES,
    PRIORITIES,
    IntentClassifier,
    IntentResult,
    _apply_priority_rules,
    _looks_like_correction,
    parse_output_for_test,
)


# ── Fixtures ──────────────────────────────────────────────────────────────────


@pytest.fixture
def project_root(tmp_path: Path) -> Path:
    (tmp_path / "data" / "logs").mkdir(parents=True, exist_ok=True)
    return tmp_path


@dataclass
class _StubOutcome:
    text: str
    session_id: str | None = None
    cost_usd: float | None = None
    duration_ms: int = 30
    error: str | None = None


def _patch_run_worker(monkeypatch, *responses: str):
    queue = list(responses)

    async def fake(prompt, **kwargs):
        if not queue:
            return _StubOutcome(text="(exhausted)")
        return _StubOutcome(text=queue.pop(0))

    monkeypatch.setattr(intent_mod, "run_worker", fake)


# ── Parser ────────────────────────────────────────────────────────────────────


def test_parse_clean_json():
    raw = '{"category": "task", "priority": "high", "confidence": 0.9, "rationale": "fix bug"}'
    r = parse_output_for_test(raw)
    assert r.category == "task"
    assert r.priority == "high"
    assert r.confidence == 0.9
    assert "fix bug" in r.rationale
    assert r.error is None


def test_parse_strips_markdown_fence():
    raw = '```json\n{"category": "question", "priority": "low", "confidence": 0.7}\n```'
    r = parse_output_for_test(raw)
    assert r.category == "question"
    assert r.priority == "low"


def test_parse_unknown_category_coerced():
    raw = '{"category": "weather", "priority": "normal", "confidence": 0.5}'
    r = parse_output_for_test(raw)
    assert r.category == "unknown"


def test_parse_invalid_priority_falls_back():
    raw = '{"category": "task", "priority": "yesterday", "confidence": 0.8}'
    r = parse_output_for_test(raw)
    assert r.priority == "normal"


def test_parse_malformed_json():
    raw = "not json at all"
    r = parse_output_for_test(raw)
    assert r.category == "unknown"
    assert r.error == "json_parse_failed"


def test_parse_empty():
    r = parse_output_for_test("")
    assert r.category == "unknown"
    assert r.error == "empty_classifier_output"


def test_parse_confidence_clamped():
    raw = '{"category": "task", "priority": "normal", "confidence": 5.0}'
    r = parse_output_for_test(raw)
    assert r.confidence == 1.0

    raw2 = '{"category": "task", "priority": "normal", "confidence": -0.5}'
    r2 = parse_output_for_test(raw2)
    assert r2.confidence == 0.0


# ── Priority rules ────────────────────────────────────────────────────────────


def test_urgency_keyword_escalates_to_urgent():
    assert _apply_priority_rules("task", "normal", "abhi fix karo prod down hai") == "urgent"
    assert _apply_priority_rules("question", "low", "is the API broken") == "urgent"


def test_greeting_capped_at_low():
    assert _apply_priority_rules("greeting", "high", "namaste") == "low"


def test_correction_floored_at_high():
    assert _apply_priority_rules("correction", "low", "always use respectful forms") == "high"


def test_emotional_floored_at_normal():
    assert _apply_priority_rules("emotional", "low", "tired hu yaar") == "normal"


def test_correction_hint_detector():
    assert _looks_like_correction("always use full forms") is True
    assert _looks_like_correction("from now on don't summarize") is True
    assert _looks_like_correction("good work") is False


# ── Skip-cases (no LLM call) ──────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_slash_command_skips_to_synthetic_task(project_root: Path, monkeypatch):
    monkeypatch.setenv("JARVIS_INTENT_ENABLED", "1")
    # No run_worker patch — slash commands must not invoke LLM
    monkeypatch.setattr(intent_mod, "run_worker", _crash_run_worker)
    c = IntentClassifier(project_root=project_root)
    r = await c.classify("/plan-day")
    assert r.category == "task"
    assert r.skipped_reason == "slash_command"
    assert r.confidence == 1.0


@pytest.mark.asyncio
async def test_trivial_greeting_skips(project_root: Path, monkeypatch):
    monkeypatch.setenv("JARVIS_INTENT_ENABLED", "1")
    monkeypatch.setattr(intent_mod, "run_worker", _crash_run_worker)
    c = IntentClassifier(project_root=project_root)
    r = await c.classify("hi")
    assert r.category == "greeting"
    assert r.skipped_reason == "trivial"


@pytest.mark.asyncio
async def test_kill_switch_returns_unknown(project_root: Path, monkeypatch):
    monkeypatch.setenv("JARVIS_INTENT_ENABLED", "0")
    monkeypatch.setattr(intent_mod, "run_worker", _crash_run_worker)
    c = IntentClassifier(project_root=project_root)
    r = await c.classify("Anisha ke liye message draft karo please")
    assert r.category == "unknown"
    assert r.skipped_reason == "disabled"


@pytest.mark.asyncio
async def test_empty_message_skips(project_root: Path, monkeypatch):
    monkeypatch.setenv("JARVIS_INTENT_ENABLED", "1")
    monkeypatch.setattr(intent_mod, "run_worker", _crash_run_worker)
    c = IntentClassifier(project_root=project_root)
    r = await c.classify("   ")
    assert r.skipped_reason == "empty"


async def _crash_run_worker(*args, **kwargs):  # pragma: no cover — used as a guard
    raise AssertionError("run_worker must not be invoked for skip-case messages")


# ── Live-classify path (mocked LLM) ───────────────────────────────────────────


@pytest.mark.asyncio
async def test_task_classification_path(project_root: Path, monkeypatch):
    monkeypatch.setenv("JARVIS_INTENT_ENABLED", "1")
    _patch_run_worker(
        monkeypatch,
        '{"category": "task", "priority": "normal", "confidence": 0.9, "rationale": "draft request"}',
    )
    c = IntentClassifier(project_root=project_root)
    r = await c.classify("Anisha ke liye ek sweet message draft karo")
    assert r.category == "task"
    assert r.priority == "normal"
    assert r.confidence == 0.9
    assert r.skipped_reason is None


@pytest.mark.asyncio
async def test_feedback_upgraded_to_correction_via_hint(project_root: Path, monkeypatch):
    """Model returns 'feedback' but message contains 'always' → upgrade to correction + priority high."""
    monkeypatch.setenv("JARVIS_INTENT_ENABLED", "1")
    _patch_run_worker(
        monkeypatch,
        '{"category": "feedback", "priority": "normal", "confidence": 0.8, "rationale": "tone note"}',
    )
    c = IntentClassifier(project_root=project_root)
    r = await c.classify("good but always use full Hinglish forms from now on")
    assert r.category == "correction"
    assert r.priority == "high"
    assert "correction" in r.rationale  # rationale annotated


@pytest.mark.asyncio
async def test_classifier_timeout_falls_back_to_unknown(project_root: Path, monkeypatch):
    monkeypatch.setenv("JARVIS_INTENT_ENABLED", "1")

    async def slow_worker(*args, **kwargs):
        import asyncio
        await asyncio.sleep(10)
        return _StubOutcome(text="never reached")

    monkeypatch.setattr(intent_mod, "run_worker", slow_worker)
    c = IntentClassifier(project_root=project_root)
    c.timeout_s = 0  # forces immediate timeout (still +2 in wait_for, but very short)
    r = await c.classify("a strategic question about next quarter planning")
    # asyncio.wait_for with 0+2=2s; the slow_worker sleeps 10s so this WILL time out
    assert r.category == "unknown"
    assert r.error and "timeout" in r.error


@pytest.mark.asyncio
async def test_classifier_backend_error_falls_back(project_root: Path, monkeypatch):
    monkeypatch.setenv("JARVIS_INTENT_ENABLED", "1")

    async def crashing_worker(*args, **kwargs):
        raise RuntimeError("backend exploded")

    monkeypatch.setattr(intent_mod, "run_worker", crashing_worker)
    c = IntentClassifier(project_root=project_root)
    r = await c.classify("kya hua aapke saath bhai itna lambaa silence kyu")
    assert r.category == "unknown"
    assert r.error and "intent_error" in r.error


# ── Log writing ───────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_log_file_appended(project_root: Path, monkeypatch):
    monkeypatch.setenv("JARVIS_INTENT_ENABLED", "1")
    _patch_run_worker(
        monkeypatch,
        '{"category": "question", "priority": "normal", "confidence": 0.85, "rationale": "info"}',
    )
    c = IntentClassifier(project_root=project_root)
    await c.classify("how does the daemon resumability work")
    log_path = project_root / "data" / "logs" / "intent.jsonl"
    assert log_path.exists()
    lines = log_path.read_text().strip().split("\n")
    assert len(lines) == 1
    import json
    entry = json.loads(lines[0])
    assert entry["category"] == "question"
    assert entry["priority"] == "normal"
    assert "msg_hash" in entry


# ── XML block rendering ───────────────────────────────────────────────────────


def test_intent_to_block_format():
    r = IntentResult(category="task", priority="urgent", confidence=0.92)
    block = r.to_block()
    assert 'category="task"' in block
    assert 'priority="urgent"' in block
    assert 'confidence="0.92"' in block


def test_all_categories_present_in_enum():
    assert set(CATEGORIES) == {
        "task", "question", "feedback", "strategic",
        "emotional", "correction", "greeting", "unknown",
    }


def test_all_priorities_present_in_enum():
    assert set(PRIORITIES) == {"low", "normal", "high", "urgent"}
