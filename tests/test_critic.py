"""Unit tests for jarvis_core/critic.py + confidence.py.

Strategy: monkeypatch `jarvis_core.critic.run_worker` to return canned outputs.
This isolates the critic's parsing / verdict / revise-logic from the live LLM.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pytest

from jarvis_core import critic as critic_mod
from jarvis_core.confidence import annotate, is_silent, normalise
from jarvis_core.critic import (
    Critic,
    CritiqueOutcome,
    CritiqueResult,
    _parse_critic_output,
)


# ── Fixtures ──────────────────────────────────────────────────────────────────


@pytest.fixture
def project_root(tmp_path: Path) -> Path:
    (tmp_path / "data" / "logs").mkdir(parents=True, exist_ok=True)
    return tmp_path


@dataclass
class _StubOutcome:
    """Mirrors WorkerOutcome shape."""
    text: str
    session_id: str | None = None
    cost_usd: float | None = None
    duration_ms: int = 50
    error: str | None = None


def _patch_run_worker(monkeypatch: pytest.MonkeyPatch, *responses: str):
    """Queue a sequence of canned run_worker responses. Each call pops one."""
    queue = list(responses)

    async def fake(prompt, **kwargs):
        if not queue:
            return _StubOutcome(text="(no more canned responses)")
        return _StubOutcome(text=queue.pop(0))

    monkeypatch.setattr(critic_mod, "run_worker", fake)


# ── confidence.py ─────────────────────────────────────────────────────────────


def test_normalise_handles_aliases():
    assert normalise("ok") == "verified"
    assert normalise("HIGH") == "verified"
    assert normalise("medium") == "unverified"
    assert normalise("fail") == "low"
    assert normalise(None) == "unverified"
    assert normalise("unknown garbage") == "unverified"


def test_is_silent_only_for_verified():
    assert is_silent("verified") is True
    assert is_silent("unverified") is False
    assert is_silent("low") is False


def test_annotate_silent_for_verified():
    reply = "A" * 200
    assert annotate(reply, "verified") == reply


def test_annotate_appends_tag_for_low():
    reply = "A" * 200
    tagged = annotate(reply, "low")
    assert tagged.endswith("]_")
    assert "low confidence" in tagged
    # Original reply is preserved exactly, tag is appended
    assert tagged.startswith(reply)


def test_annotate_skips_short_reply():
    short = "ok"
    assert annotate(short, "low") == short


# ── _parse_critic_output ──────────────────────────────────────────────────────


def test_parse_clean_json():
    raw = '{"verdict":"ok","confidence":"verified","issues":[],"suggestion":""}'
    r = _parse_critic_output(raw)
    assert r.verdict == "ok"
    assert r.confidence == "verified"
    assert r.issues == []
    assert r.error is None


def test_parse_json_inside_markdown_fences():
    raw = '```json\n{"verdict":"revise","confidence":"unverified","issues":["tone fail"],"suggestion":"fix tone"}\n```'
    r = _parse_critic_output(raw)
    assert r.verdict == "revise"
    assert r.issues == ["tone fail"]


def test_parse_json_inside_prose():
    raw = "Here is my critique:\n\n{\"verdict\":\"revise\",\"confidence\":\"low\",\"issues\":[\"a\",\"b\"],\"suggestion\":\"rewrite\"}\n\nDone."
    r = _parse_critic_output(raw)
    assert r.verdict == "revise"
    assert r.confidence == "low"


def test_parse_garbage_falls_open():
    r = _parse_critic_output("totally not json at all")
    assert r.verdict == "ok"
    assert r.confidence == "unverified"
    assert r.error == "json_parse_failed"


def test_parse_empty():
    r = _parse_critic_output("")
    assert r.verdict == "ok"
    assert r.error == "empty_critic_output"


def test_parse_invalid_verdict_normalised():
    raw = '{"verdict":"perfect","confidence":"superb","issues":[],"suggestion":""}'
    r = _parse_critic_output(raw)
    assert r.verdict == "ok"  # invalid verdict → ok
    assert r.confidence == "unverified"  # alias not in VALID_LEVELS


# ── Critic.evaluate skip-cases ────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_skips_trivial_question(project_root: Path):
    c = Critic(project_root=project_root)
    out = await c.evaluate(
        user_message="hi",
        jarvis_reply="A" * 200,
        memory_context="",
    )
    assert out.confidence == "verified"
    assert out.revised is False
    assert out.critique.skipped_reason == "trivial_question"


@pytest.mark.asyncio
async def test_skips_trivial_reply(project_root: Path):
    c = Critic(project_root=project_root)
    out = await c.evaluate(
        user_message="Boss what is the deal with our LinkedIn pipeline this week?",
        jarvis_reply="ok",
        memory_context="",
    )
    assert out.confidence == "verified"
    assert out.critique.skipped_reason == "trivial_reply"


@pytest.mark.asyncio
async def test_skips_slash_command(project_root: Path):
    c = Critic(project_root=project_root)
    out = await c.evaluate(
        user_message="/triage",
        jarvis_reply="A" * 200,
        memory_context="",
    )
    assert out.critique.skipped_reason == "slash_command"


@pytest.mark.asyncio
async def test_skips_tool_error(project_root: Path):
    c = Critic(project_root=project_root)
    err_reply = "⚠️ Worker error: subprocess timed out after 300s — please retry"
    out = await c.evaluate(
        user_message="Boss tell me what the current state of our resume work is",
        jarvis_reply=err_reply,
        memory_context="",
    )
    assert out.critique.skipped_reason == "tool_error_passthrough"


@pytest.mark.asyncio
async def test_skips_when_disabled(project_root: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("JARVIS_CRITIC_ENABLED", "0")
    c = Critic(project_root=project_root)
    out = await c.evaluate(
        user_message="Boss kya plan hai aaj resume ke baare mein kuch karna chahiye?",
        jarvis_reply="A" * 200,
        memory_context="",
    )
    assert out.confidence == "verified"
    assert out.critique.skipped_reason == "disabled"


# ── Critic.evaluate happy paths ───────────────────────────────────────────────


@pytest.mark.asyncio
async def test_ok_verdict_passes_through(project_root: Path, monkeypatch: pytest.MonkeyPatch):
    _patch_run_worker(
        monkeypatch,
        '{"verdict":"ok","confidence":"verified","issues":[],"suggestion":""}',
    )
    c = Critic(project_root=project_root)
    original = "A clean, respectful Hinglish reply that answers the question correctly with sourced claims. " * 3
    out = await c.evaluate(
        user_message="Boss kya plan hai aaj resume ke baare mein kuch karna chahiye?",
        jarvis_reply=original,
        memory_context="<jarvis_memory_context>...</jarvis_memory_context>",
    )
    assert out.final_reply == original
    assert out.confidence == "verified"
    assert out.revised is False


@pytest.mark.asyncio
async def test_revise_verdict_triggers_one_revision(project_root: Path,
                                                   monkeypatch: pytest.MonkeyPatch):
    revised_text = "Boss, yeh raha sahi revised reply — Hinglish + respectful + claims hedged."
    _patch_run_worker(
        monkeypatch,
        # First call = critic review
        '{"verdict":"revise","confidence":"unverified","issues":["tone fail"],"suggestion":"use aap not tu"}',
        # Second call = revision pass
        revised_text,
    )
    c = Critic(project_root=project_root)
    out = await c.evaluate(
        user_message="Boss kya plan hai aaj resume update krne ka batao please?",
        jarvis_reply="Tu kar le bhai" + "x" * 200,  # deliberately tone-violating
        memory_context="",
    )
    assert out.revised is True
    assert out.confidence == "unverified"
    assert revised_text in out.final_reply
    assert "unverified" in out.final_reply  # tag appended


@pytest.mark.asyncio
async def test_revise_with_empty_revision_falls_back_to_original(
    project_root: Path, monkeypatch: pytest.MonkeyPatch,
):
    original = "Original reply with enough length to pass the trivial check. " * 4
    _patch_run_worker(
        monkeypatch,
        '{"verdict":"revise","confidence":"low","issues":["bad"],"suggestion":"fix"}',
        "",  # empty revision
    )
    c = Critic(project_root=project_root)
    out = await c.evaluate(
        user_message="Boss yeh resume mein kya gap hai check karke batao quickly please",
        jarvis_reply=original,
        memory_context="",
    )
    assert out.revised is False
    assert original.strip() in out.final_reply
    assert "low" in out.final_reply  # confidence tag still attached


@pytest.mark.asyncio
async def test_reject_verdict_low_confidence(project_root: Path,
                                             monkeypatch: pytest.MonkeyPatch):
    _patch_run_worker(
        monkeypatch,
        '{"verdict":"reject","confidence":"low","issues":["completely off-topic"],"suggestion":""}',
    )
    c = Critic(project_root=project_root)
    original = "Some long unrelated response that does not address the question. " * 4
    out = await c.evaluate(
        user_message="Boss aapka resume kab tak update karna hai bhai please confirm",
        jarvis_reply=original,
        memory_context="",
    )
    assert out.confidence == "low"
    assert out.revised is False
    assert "low" in out.final_reply


@pytest.mark.asyncio
async def test_writes_log_jsonl(project_root: Path, monkeypatch: pytest.MonkeyPatch):
    _patch_run_worker(
        monkeypatch,
        '{"verdict":"ok","confidence":"verified","issues":[],"suggestion":""}',
    )
    c = Critic(project_root=project_root)
    await c.evaluate(
        user_message="Boss yeh resume mein kya gap hai check karke batao quickly please",
        jarvis_reply="A clean Hinglish reply " * 10,
        memory_context="",
        user_id="boss",
    )
    log_file = project_root / "data" / "logs" / "critic.jsonl"
    assert log_file.exists()
    text = log_file.read_text()
    assert '"verdict": "ok"' in text
    assert '"user_id": "boss"' in text
