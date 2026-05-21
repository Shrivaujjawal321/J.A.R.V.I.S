"""Unit tests for jarvis_core/recall.py.

Strategy: stub out EpisodicMemory so the tests are deterministic and don't
require the embedding model / ChromaDB. We test the Recaller's behavioural
contract from specs/recall.spec.md, not the underlying vector backend.
"""
from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import patch

import pytest

from jarvis_core.recall import (
    Recaller,
    RecallResult,
    SkipReason,
    build_block_from_hits,
)


# ── Fixtures ──────────────────────────────────────────────────────────────────


@pytest.fixture
def project_root(tmp_path: Path) -> Path:
    (tmp_path / "data" / "logs").mkdir(parents=True, exist_ok=True)
    return tmp_path


class _FakeMemory:
    """Stand-in for EpisodicMemory. Returns whatever hits we set."""

    def __init__(self, hits: list[dict] | Exception | None = None):
        self._hits = hits or []

    def recall(self, query: str, k: int = 5) -> list[dict]:
        if isinstance(self._hits, Exception):
            raise self._hits
        return list(self._hits)


def _hit(text: str, score: float, source: str = "memory/preferences.md", section: str = "") -> dict:
    return {"text": text, "score": score, "source": source, "section": section, "metadata": {}}


def _recaller(project_root: Path, hits) -> Recaller:
    """Construct a Recaller with EpisodicMemory replaced by a stub."""
    r = Recaller(project_root=project_root)
    r._mem = _FakeMemory(hits)
    return r


# ── Skip-case tests ───────────────────────────────────────────────────────────


def test_skips_short_message(project_root: Path):
    r = _recaller(project_root, hits=[_hit("anything", 0.9)])
    out = r.gather("hi", "boss")
    assert out.context == ""
    assert out.skipped_reason == SkipReason.TOO_SHORT
    assert out.n_chunks == 0


def test_skips_pure_greeting(project_root: Path):
    r = _recaller(project_root, hits=[_hit("anything", 0.9)])
    # Must be > 30 chars (otherwise too_short fires first) AND consist
    # entirely of greeting + filler tokens
    out = r.gather("Hello Jarvis good morning everyone sir!", "boss")
    assert out.context == ""
    assert out.skipped_reason == SkipReason.GREETING


def test_does_not_skip_greeting_with_real_content(project_root: Path):
    r = _recaller(project_root, hits=[_hit("preferences hit", 0.85)])
    out = r.gather("Hello Jarvis what is on my schedule today?", "boss")
    assert out.skipped_reason is None
    assert out.n_chunks == 1


def test_skips_slash_command(project_root: Path):
    r = _recaller(project_root, hits=[_hit("anything", 0.9)])
    out = r.gather("/recall what did we discuss about anisha", "boss")
    assert out.context == ""
    assert out.skipped_reason == SkipReason.SLASH_COMMAND


def test_skips_when_disabled(project_root: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("JARVIS_RECALL_ENABLED", "0")
    r = Recaller(project_root=project_root)
    r._mem = _FakeMemory([_hit("anything", 0.9)])
    out = r.gather("Boss kya plan hai aaj resume update karne ka?", "boss")
    assert out.context == ""
    assert out.skipped_reason == SkipReason.DISABLED


# ── Hit / threshold tests ─────────────────────────────────────────────────────


def test_returns_block_with_hits_above_threshold(project_root: Path):
    hits = [
        _hit("Boss prefers Hinglish + respectful register", 0.92,
             source="memory/preferences.md", section="Communication"),
        _hit("Anisha is Boss's girlfriend", 0.78, source="memory/people.md"),
    ]
    r = _recaller(project_root, hits=hits)
    out = r.gather("What is Boss's communication style preference?", "boss")
    assert out.skipped_reason is None
    assert out.n_chunks == 2
    assert "<jarvis_memory_context>" in out.context
    assert "</jarvis_memory_context>" in out.context
    assert "Hinglish" in out.context
    assert "Anisha" in out.context
    assert "memory/preferences.md" in out.context


def test_filters_below_threshold(project_root: Path):
    hits = [
        _hit("strong hit", 0.80),
        _hit("weak hit", 0.42),
        _hit("very weak", 0.10),
    ]
    r = _recaller(project_root, hits=hits)
    out = r.gather("What does Boss prefer for daily standups?", "boss")
    assert out.n_chunks == 1
    assert "strong hit" in out.context
    assert "weak hit" not in out.context


def test_no_hits_above_threshold_returns_empty(project_root: Path):
    hits = [_hit("loose match", 0.30)]
    r = _recaller(project_root, hits=hits)
    out = r.gather("Random question that has no useful memory match", "boss")
    assert out.context == ""
    assert out.skipped_reason == SkipReason.NO_HITS_ABOVE_THRESHOLD


def test_empty_db_returns_empty(project_root: Path):
    r = _recaller(project_root, hits=[])
    out = r.gather("This vector DB is empty so we get nothing back", "boss")
    assert out.context == ""
    assert out.skipped_reason == SkipReason.EMPTY_DB


# ── Robustness ────────────────────────────────────────────────────────────────


def test_backend_error_does_not_raise(project_root: Path):
    r = _recaller(project_root, hits=RuntimeError("chroma exploded"))
    out = r.gather("Boss what should I prioritise this morning for jobs?", "boss")
    assert out.context == ""
    assert out.skipped_reason == SkipReason.BACKEND_ERROR


def test_score_threshold_env_override(project_root: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("JARVIS_RECALL_SCORE_MIN", "0.30")
    r = Recaller(project_root=project_root)
    r._mem = _FakeMemory([_hit("loose match", 0.35)])
    out = r.gather("Boss explain why anisha matters in our planning", "boss")
    assert out.n_chunks == 1


def test_format_emits_score_attribute():
    block = build_block_from_hits([
        _hit("alpha", 0.873, source="memory/projects.md", section="LinkedIn"),
    ])
    assert 'score="0.87"' in block
    assert 'source="memory/projects.md"' in block
    assert 'section="LinkedIn"' in block
    assert "alpha" in block


def test_token_budget_trims_low_scoring_chunks(project_root: Path,
                                                monkeypatch: pytest.MonkeyPatch):
    # Set very small budget so only one chunk fits
    monkeypatch.setenv("JARVIS_RECALL_TOKEN_BUDGET", "20")
    long_text = "x" * 200  # 200 chars ≈ 50 tokens — exceeds 20-token budget on its own
    hits = [
        _hit(long_text + " HIGH", 0.95),
        _hit(long_text + " LOW", 0.60),
    ]
    r = Recaller(project_root=project_root)
    r._mem = _FakeMemory(hits)
    out = r.gather("Question that warrants recall and is long enough", "boss")
    assert out.n_chunks == 1
    assert "HIGH" in out.context
    assert "LOW" not in out.context


def test_writes_log_jsonl(project_root: Path):
    r = _recaller(project_root, hits=[_hit("something", 0.80)])
    r.gather("Boss what is on our LinkedIn pipeline for this week?", "boss")
    log_file = project_root / "data" / "logs" / "recall.jsonl"
    assert log_file.exists()
    content = log_file.read_text()
    assert '"user_id": "boss"' in content
    assert '"n_chunks": 1' in content
