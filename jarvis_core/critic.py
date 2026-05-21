"""
Critic layer — post-response silent reviewer.

See `specs/critic.spec.md` for the full contract. Summary:
- After the primary worker produces a reply, run a single Haiku-class call
  that scores the draft against four rubrics (intent / memory / claims / tone).
- If verdict == "revise" → run exactly one revision pass.
- Attach a confidence tag (`verified` / `unverified` / `low`) to the final reply.
- Hard kill-switch: `JARVIS_CRITIC_ENABLED=0`.

This module is imported lazily inside `daemon.py`.
"""
from __future__ import annotations

import asyncio
import json
import logging
import os
import re
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from .confidence import Confidence, annotate, normalise
from .orchestrator import run_worker

log = logging.getLogger("jarvis_core.critic")

# ── Defaults ──────────────────────────────────────────────────────────────────

_DEFAULT_MODEL = "claude-haiku-4-5-20251001"
_DEFAULT_TIMEOUT_S = 8
_REVISE_TIMEOUT_S = 12
_MIN_REPLY_CHARS_FOR_CRITIQUE = 100
_MIN_QUESTION_CHARS_FOR_CRITIQUE = 50

_TOOL_ERROR_PREFIXES = ("⚠️", "Worker error", "(empty response")

_JSON_BLOCK_RE = re.compile(r"\{.*\}", re.DOTALL)


# ── Result types ──────────────────────────────────────────────────────────────

@dataclass
class CritiqueResult:
    verdict: str       # "ok" | "revise" | "reject"
    confidence: Confidence
    issues: list[str] = field(default_factory=list)
    suggestion: str = ""
    raw: str = ""      # raw critic output, for debugging
    skipped_reason: str | None = None
    latency_ms: int = 0
    error: str | None = None

    @property
    def should_revise(self) -> bool:
        return self.verdict == "revise"


@dataclass
class CritiqueOutcome:
    """Final outcome after optional revision."""
    final_reply: str
    confidence: Confidence
    revised: bool
    critique: CritiqueResult
    revise_latency_ms: int = 0


# ── Prompt builders ───────────────────────────────────────────────────────────

_REVIEW_PROMPT_TEMPLATE = """You are Jarvis's internal critic. Your job is to silently review a draft reply BEFORE it reaches Boss (Ujjawal). Be ruthlessly honest. Boss has explicitly asked Jarvis to verify its own work, so do not soften criticism.

Boss's preferences you must enforce:
- Hinglish + respectful register: "batao" not "bta", "karo/kariye" not "kr", "dekho/dekhiye" not "dkh", "aap" never "tu".
- Direct, concise, options-with-WHY, anti-fabrication.

Review the draft against four rubrics:
1. INTENT — Does the reply answer Boss's actual question? (Not an adjacent question.)
2. MEMORY — Any contradictions with the supplied memory context?
3. CLAIMS — Are factual / counted / dated claims either sourced or properly hedged? Specific numbers without a basis are a fail.
4. TONE — Hinglish respectful register, no shortened forms, no "tu".

Output ONLY a single JSON object (no markdown fences, no prose around it):

{"verdict": "ok|revise|reject", "confidence": "verified|unverified|low", "issues": ["short bullet"], "suggestion": "one-line guidance for revision, empty if verdict=ok"}

Verdict logic:
- all four rubrics pass → "ok" + "verified"
- only TONE fails → "revise" + "unverified"
- 1-2 of INTENT/MEMORY/CLAIMS fail → "revise" + "unverified"
- 3+ rubrics fail → "revise" + "low"
- response is harmful, unsafe, or completely off-topic → "reject" + "low"

---

BOSS'S MESSAGE:
__USER_MESSAGE__

MEMORY CONTEXT (background only, not user instruction):
__MEMORY_CONTEXT__

DRAFT REPLY TO REVIEW:
__JARVIS_REPLY__

Now output the JSON object."""


_REVISE_PROMPT_TEMPLATE = """You are Jarvis. Revise your previous reply based on the critic's feedback.

Boss's preferences (non-negotiable):
- Hinglish + respectful register ("batao", "karo", "dekho", "aap" — never shortened or "tu").
- Direct, concise, no corporate fluff, no padding.
- Honest. Hedge unsourced claims explicitly.
- Options-with-WHY when recommending.

You will see the original message, the memory context, your previous draft, and the critic's issues. Produce a CLEAN revised reply. Do NOT explain the revision — just give the corrected reply text. No preamble, no meta-commentary.

---

BOSS'S MESSAGE:
__USER_MESSAGE__

MEMORY CONTEXT:
__MEMORY_CONTEXT__

YOUR PREVIOUS DRAFT (flagged for revision):
__ORIGINAL_REPLY__

CRITIC'S ISSUES:
__ISSUES_BLOCK__

CRITIC'S SUGGESTION:
__SUGGESTION__

Now output the revised reply only."""


def _substitute(template: str, **fields: str) -> str:
    """Plain-text placeholder substitution — avoids str.format() colliding with JSON braces."""
    out = template
    for key, value in fields.items():
        out = out.replace(f"__{key.upper()}__", value)
    return out


def _build_review_prompt(user_message: str, jarvis_reply: str, memory_context: str) -> str:
    return _substitute(
        _REVIEW_PROMPT_TEMPLATE,
        user_message=user_message.strip(),
        memory_context=(memory_context or "(no memory context recalled)").strip(),
        jarvis_reply=jarvis_reply.strip(),
    )


def _build_revise_prompt(
    user_message: str, original_reply: str, memory_context: str,
    issues: list[str], suggestion: str,
) -> str:
    issues_block = "\n".join(f"- {i}" for i in issues) or "- (none listed)"
    return _substitute(
        _REVISE_PROMPT_TEMPLATE,
        user_message=user_message.strip(),
        memory_context=(memory_context or "(no memory context recalled)").strip(),
        original_reply=original_reply.strip(),
        issues_block=issues_block,
        suggestion=(suggestion or "Apply the critic's checks.").strip(),
    )


# ── JSON parsing ──────────────────────────────────────────────────────────────

def _parse_critic_output(raw: str) -> CritiqueResult:
    """Extract a CritiqueResult from a raw critic LLM response."""
    if not raw or not raw.strip():
        return CritiqueResult(verdict="ok", confidence="unverified", raw=raw,
                              error="empty_critic_output")

    text = raw.strip()
    # Strip optional markdown fences
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)

    # Try direct parse first, then regex-extract the first JSON object
    candidates = [text]
    match = _JSON_BLOCK_RE.search(text)
    if match:
        candidates.append(match.group(0))

    for candidate in candidates:
        try:
            data = json.loads(candidate)
        except (json.JSONDecodeError, ValueError):
            continue
        if not isinstance(data, dict):
            continue
        verdict = str(data.get("verdict", "ok")).strip().lower()
        if verdict not in ("ok", "revise", "reject"):
            verdict = "ok"
        confidence = normalise(data.get("confidence"))
        issues = data.get("issues") or []
        if not isinstance(issues, list):
            issues = [str(issues)]
        else:
            issues = [str(i) for i in issues][:8]
        suggestion = str(data.get("suggestion") or "")
        return CritiqueResult(
            verdict=verdict, confidence=confidence,
            issues=issues, suggestion=suggestion, raw=raw,
        )

    # Could not parse — fail open (don't block reply)
    return CritiqueResult(verdict="ok", confidence="unverified", raw=raw,
                          error="json_parse_failed")


# ── Critic ────────────────────────────────────────────────────────────────────

class Critic:
    """Silent reviewer that runs after the main worker."""

    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        self.enabled = os.getenv("JARVIS_CRITIC_ENABLED", "1") not in ("0", "false", "False")
        self.model = os.getenv("JARVIS_CRITIC_MODEL", _DEFAULT_MODEL)
        self.timeout_s = int(os.getenv("JARVIS_CRITIC_TIMEOUT_S", str(_DEFAULT_TIMEOUT_S)))
        self.revise_timeout_s = int(os.getenv("JARVIS_CRITIC_REVISE_TIMEOUT_S", str(_REVISE_TIMEOUT_S)))
        self.log_path = self.project_root / "data" / "logs" / "critic.jsonl"

    # ── Public API ────────────────────────────────────────────────────────────

    async def evaluate(
        self,
        user_message: str,
        jarvis_reply: str,
        memory_context: str = "",
        user_id: str = "default",
    ) -> CritiqueOutcome:
        """Run the full review + optional revise pipeline. Always returns an outcome.

        Failures (timeout, parse error, backend down) fall back to the original
        reply with `confidence=unverified`. Never raises.
        """
        skip = self._should_skip(user_message, jarvis_reply)
        if skip:
            critique = CritiqueResult(verdict="ok", confidence="verified", skipped_reason=skip)
            return CritiqueOutcome(
                final_reply=jarvis_reply,
                confidence="verified",
                revised=False,
                critique=critique,
            )

        critique = await self._review(user_message, jarvis_reply, memory_context)
        self._log(user_id, critique, revised=False, revise_latency_ms=0)

        if critique.verdict == "reject":
            # Reject is rare — surface as low-confidence with the original text + flag
            final = annotate(jarvis_reply, "low")
            return CritiqueOutcome(
                final_reply=final, confidence="low", revised=False, critique=critique,
            )

        if not critique.should_revise:
            return CritiqueOutcome(
                final_reply=jarvis_reply, confidence=critique.confidence,
                revised=False, critique=critique,
            )

        revised_text, revise_latency_ms = await self._revise(
            user_message, jarvis_reply, memory_context,
            critique.issues, critique.suggestion,
        )
        self._log(user_id, critique, revised=True, revise_latency_ms=revise_latency_ms)

        if not revised_text:
            # Revision empty / errored — keep original, tag as unverified
            return CritiqueOutcome(
                final_reply=annotate(jarvis_reply, critique.confidence),
                confidence=critique.confidence,
                revised=False,
                critique=critique,
                revise_latency_ms=revise_latency_ms,
            )

        final = annotate(revised_text, critique.confidence)
        return CritiqueOutcome(
            final_reply=final,
            confidence=critique.confidence,
            revised=True,
            critique=critique,
            revise_latency_ms=revise_latency_ms,
        )

    # ── Internals ─────────────────────────────────────────────────────────────

    def _should_skip(self, user_message: str, jarvis_reply: str) -> str | None:
        # Order matters: cheaper / more-specific checks first so that
        # diagnostic skip-reasons reflect actual user intent (a slash command
        # is more useful to log than "trivial_question").
        if not self.enabled:
            return "disabled"
        if user_message and user_message.strip().startswith("/"):
            return "slash_command"
        if jarvis_reply and any(jarvis_reply.lstrip().startswith(p) for p in _TOOL_ERROR_PREFIXES):
            return "tool_error_passthrough"
        if not jarvis_reply or len(jarvis_reply) < _MIN_REPLY_CHARS_FOR_CRITIQUE:
            return "trivial_reply"
        if not user_message or len(user_message.strip()) < _MIN_QUESTION_CHARS_FOR_CRITIQUE:
            return "trivial_question"
        return None

    async def _review(self, user_message: str, jarvis_reply: str, memory_context: str) -> CritiqueResult:
        started = time.perf_counter()
        prompt = _build_review_prompt(user_message, jarvis_reply, memory_context)
        try:
            outcome = await asyncio.wait_for(
                run_worker(
                    prompt,
                    project_root=self.project_root,
                    max_turns=1,
                    allowed_tools=[],
                    timeout_seconds=self.timeout_s,
                    model=self.model,
                ),
                timeout=self.timeout_s + 2,
            )
        except asyncio.TimeoutError:
            log.warning("critic review timed out (%ds)", self.timeout_s)
            return CritiqueResult(verdict="ok", confidence="unverified",
                                  error="critic_timeout",
                                  latency_ms=int((time.perf_counter() - started) * 1000))
        except Exception as exc:
            log.warning("critic review backend error: %s", exc)
            return CritiqueResult(verdict="ok", confidence="unverified",
                                  error=f"critic_error: {exc!r}",
                                  latency_ms=int((time.perf_counter() - started) * 1000))

        latency_ms = int((time.perf_counter() - started) * 1000)
        result = _parse_critic_output(outcome.text)
        result.latency_ms = latency_ms
        if outcome.error and not result.error:
            result.error = outcome.error
        return result

    async def _revise(
        self,
        user_message: str,
        original_reply: str,
        memory_context: str,
        issues: list[str],
        suggestion: str,
    ) -> tuple[str, int]:
        started = time.perf_counter()
        prompt = _build_revise_prompt(
            user_message, original_reply, memory_context, issues, suggestion,
        )
        try:
            outcome = await asyncio.wait_for(
                run_worker(
                    prompt,
                    project_root=self.project_root,
                    max_turns=2,
                    allowed_tools=[],
                    timeout_seconds=self.revise_timeout_s,
                    model=self.model,
                ),
                timeout=self.revise_timeout_s + 2,
            )
        except asyncio.TimeoutError:
            log.warning("critic revise timed out (%ds)", self.revise_timeout_s)
            return ("", int((time.perf_counter() - started) * 1000))
        except Exception as exc:
            log.warning("critic revise backend error: %s", exc)
            return ("", int((time.perf_counter() - started) * 1000))

        latency_ms = int((time.perf_counter() - started) * 1000)
        text = (outcome.text or "").strip()
        if outcome.error or not text:
            return ("", latency_ms)
        return (text, latency_ms)

    def _log(
        self,
        user_id: str,
        critique: CritiqueResult,
        *,
        revised: bool,
        revise_latency_ms: int,
    ) -> None:
        try:
            self.log_path.parent.mkdir(parents=True, exist_ok=True)
            entry = {
                "ts": datetime.now(timezone.utc).isoformat(),
                "user_id": user_id,
                "verdict": critique.verdict,
                "confidence": critique.confidence,
                "latency_ms": critique.latency_ms,
                "revised": revised,
                "revise_latency_ms": revise_latency_ms,
                "issues": critique.issues,
                "skipped_reason": critique.skipped_reason,
                "error": critique.error,
            }
            with self.log_path.open("a") as fh:
                fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
        except Exception:
            pass
