"""
Intent classifier — pre-recall classification of every /chat message.

See `specs/intent-classifier.spec.md` for the full contract. Summary:
- Classify each message into one of 8 categories (task/question/feedback/
  strategic/emotional/correction/greeting/unknown), with a priority and
  confidence score.
- Skip-cases: slash commands (synthetic `task`), trivial messages.
- Kill-switch: `JARVIS_INTENT_ENABLED=0`.

This is the lightweight analogue of Ratnesh-Jarvis's 8-layer orchestrator.
Daemon wiring: `daemon.py:chat()` calls `classifier.classify()` BEFORE recall,
so downstream layers (worker prompt, ChatResponse) can see the intent tag.

Imported lazily inside `daemon.py`.
"""
from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import os
import re
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from .orchestrator import run_worker

log = logging.getLogger("jarvis_core.intent")

# ── Constants ─────────────────────────────────────────────────────────────────

_DEFAULT_MODEL = "claude-haiku-4-5-20251001"
_DEFAULT_TIMEOUT_S = 3
_MIN_LEN_FOR_LLM = 4

CATEGORIES = (
    "task",
    "question",
    "feedback",
    "strategic",
    "emotional",
    "correction",
    "greeting",
    "unknown",
)
PRIORITIES = ("low", "normal", "high", "urgent")

# Word-bounded so "from now on" doesn't trip "now"; "shutdown" doesn't trip "down".
_URGENCY_TOKENS = frozenset({
    "urgent", "asap", "abhi", "jaldi", "emergency",
    "broken", "fire", "critical",
})
# Phrase-level urgency markers (regex word-boundary applied at call-site).
_URGENCY_PHRASES = (
    r"\bprod(uction)?\b.*\b(down|broken|fail|fire)\b",
    r"\b(down|broken|fail|fire)\b.*\bprod(uction)?\b",
    r"\bright now\b",
    r"\bdo it now\b",
)

_CORRECTION_HINTS = frozenset({
    "always", "never", "from now on", "yaad rakhna", "stop doing",
    "stop ", "kabhi mat", "remember", "henceforth",
})

_GREETING_LEAD_TOKENS = frozenset({
    "hi", "hello", "hey", "namaste", "namaskar", "hola", "salaam", "salam",
    "yo", "sup", "gn", "gm", "thanks", "thank", "thx",
    "ok", "okay", "cool", "nice", "bye", "tata",
})

_WORD_RE = re.compile(r"[A-Za-z']+")
_JSON_BLOCK_RE = re.compile(r"\{.*\}", re.DOTALL)


class SkipReason:
    DISABLED = "disabled"
    SLASH_COMMAND = "slash_command"
    TRIVIAL = "trivial"
    EMPTY = "empty"


# ── Result dataclass ──────────────────────────────────────────────────────────


@dataclass
class IntentResult:
    category: str          # one of CATEGORIES
    priority: str          # one of PRIORITIES
    confidence: float      # in [0, 1]
    rationale: str = ""    # one-line "why" — logged only, not surfaced
    raw: str = ""          # raw classifier output, for debugging
    skipped_reason: str | None = None  # None when LLM actually ran
    latency_ms: int = 0
    error: str | None = None

    def to_block(self) -> str:
        """Render as an <intent> XML block for injection into the worker prompt."""
        return (
            f'<intent category="{self.category}" priority="{self.priority}" '
            f'confidence="{self.confidence:.2f}" />'
        )


# ── Prompt builder ────────────────────────────────────────────────────────────


_CLASSIFY_PROMPT_TEMPLATE = """You are Jarvis's intent classifier. Boss (Ujjawal) just sent a message. Classify it into exactly one of these 8 categories:

- task: Action Boss wants done — build, edit, draft, send, fix, deploy.
- question: Information request — fact, opinion, how-to, status query.
- feedback: Boss reacting to prior work — praise, criticism, refinement.
- strategic: High-level thinking, planning, multi-week decision.
- emotional: Mood / wellbeing / vent — not transactional.
- correction: Direct rule update — "from now on do X", "stop doing Y", "always".
- greeting: Pure social glue, no payload.
- unknown: Cannot confidently classify.

Tie-breakers:
- "correction" beats "feedback" when the message contains imperatives like "always", "never", "from now on", "yaad rakhna".
- "task" beats "question" when the message contains action verbs ("kar", "banao", "send", "fix", "deploy").
- "emotional" requires actual affect language — frustration, tiredness, sadness, excitement. Don't classify a calm strategic question as emotional just because it mentions feelings.

Also assign:
- priority: "low" | "normal" | "high" | "urgent". Use "urgent" ONLY if the message contains explicit urgency markers (urgent / asap / now / abhi / jaldi / emergency / down / broken / prod).
- confidence: float in [0.0, 1.0]. Be honest — low confidence is fine, drives the unknown bucket.

Output ONLY a single JSON object, no markdown fences, no prose:

{"category": "...", "priority": "...", "confidence": 0.0, "rationale": "one short sentence"}

---

BOSS'S MESSAGE:
__USER_MESSAGE__

Now output the JSON object."""


def _substitute(template: str, **fields: str) -> str:
    out = template
    for key, value in fields.items():
        out = out.replace(f"__{key.upper()}__", value)
    return out


def _build_prompt(user_message: str) -> str:
    return _substitute(_CLASSIFY_PROMPT_TEMPLATE, user_message=user_message.strip())


# ── Parser ────────────────────────────────────────────────────────────────────


def _parse_output(raw: str) -> tuple[str, str, float, str, str | None]:
    """Return (category, priority, confidence, rationale, error)."""
    if not raw or not raw.strip():
        return ("unknown", "low", 0.0, "", "empty_classifier_output")

    text = raw.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)

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
        category = str(data.get("category", "unknown")).strip().lower()
        if category not in CATEGORIES:
            category = "unknown"
        priority = str(data.get("priority", "normal")).strip().lower()
        if priority not in PRIORITIES:
            priority = "normal"
        try:
            confidence = float(data.get("confidence", 0.5))
        except (TypeError, ValueError):
            confidence = 0.5
        confidence = max(0.0, min(1.0, confidence))
        rationale = str(data.get("rationale", "")).strip()[:200]
        return (category, priority, confidence, rationale, None)

    return ("unknown", "low", 0.0, "", "json_parse_failed")


# ── Priority overrides ────────────────────────────────────────────────────────


def _apply_priority_rules(category: str, priority: str, msg: str) -> str:
    """Enforce floors/ceilings on priority per spec."""
    msg_low = msg.lower()
    tokens = set(_WORD_RE.findall(msg_low))

    # Urgency: word-boundary match against keyword set OR phrase pattern.
    if _URGENCY_TOKENS & tokens:
        return "urgent"
    if any(re.search(p, msg_low) for p in _URGENCY_PHRASES):
        return "urgent"

    # Greeting/unknown: cap at low
    if category in ("greeting", "unknown"):
        return "low"

    # Correction: floor at high (Boss is updating a rule)
    if category == "correction":
        return "high" if priority not in ("urgent",) else priority

    # Emotional: floor at normal
    if category == "emotional" and priority == "low":
        return "normal"

    return priority


def _looks_like_correction(msg: str) -> bool:
    msg_low = msg.lower()
    return any(hint in msg_low for hint in _CORRECTION_HINTS)


def _is_pure_greeting_short(msg: str) -> bool:
    """Heuristic: <=3 tokens, first token is a real greeting."""
    tokens = [t.lower() for t in _WORD_RE.findall(msg)]
    if not tokens or len(tokens) > 3:
        return False
    return tokens[0] in _GREETING_LEAD_TOKENS


# ── Classifier ────────────────────────────────────────────────────────────────


class IntentClassifier:
    """Stateless wrapper around a single Haiku call."""

    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        self.enabled = os.getenv("JARVIS_INTENT_ENABLED", "1") not in ("0", "false", "False")
        self.model = os.getenv("JARVIS_INTENT_MODEL", _DEFAULT_MODEL)
        self.timeout_s = int(os.getenv("JARVIS_INTENT_TIMEOUT_S", str(_DEFAULT_TIMEOUT_S)))
        self.log_path = self.project_root / "data" / "logs" / "intent.jsonl"

    # ── Public API ────────────────────────────────────────────────────────────

    async def classify(self, user_message: str, user_id: str = "default") -> IntentResult:
        """Always returns an IntentResult — never raises."""
        started = time.perf_counter()
        skip = self._should_skip(user_message)
        if skip:
            result = self._synthetic_for_skip(user_message, skip)
            self._log(user_id, user_message, result)
            return result

        prompt = _build_prompt(user_message)
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
            log.warning("intent classify timed out (%ds)", self.timeout_s)
            result = IntentResult(
                category="unknown", priority="low", confidence=0.0,
                error="intent_timeout",
                latency_ms=int((time.perf_counter() - started) * 1000),
            )
            self._log(user_id, user_message, result)
            return result
        except Exception as exc:
            log.warning("intent classify backend error: %s", exc)
            result = IntentResult(
                category="unknown", priority="low", confidence=0.0,
                error=f"intent_error: {exc!r}",
                latency_ms=int((time.perf_counter() - started) * 1000),
            )
            self._log(user_id, user_message, result)
            return result

        category, priority, confidence, rationale, parse_err = _parse_output(outcome.text)

        # Tie-breaker: if model said `feedback` but message has correction-language,
        # upgrade to `correction`.
        if category == "feedback" and _looks_like_correction(user_message):
            category = "correction"
            rationale = (rationale + " | upgraded to correction by hint rule").strip(" |")

        priority = _apply_priority_rules(category, priority, user_message)

        latency_ms = int((time.perf_counter() - started) * 1000)
        result = IntentResult(
            category=category,
            priority=priority,
            confidence=confidence,
            rationale=rationale,
            raw=outcome.text or "",
            latency_ms=latency_ms,
            error=parse_err or (outcome.error or None),
        )
        self._log(user_id, user_message, result)
        return result

    # ── Internals ─────────────────────────────────────────────────────────────

    def _should_skip(self, msg: str) -> str | None:
        if not self.enabled:
            return SkipReason.DISABLED
        stripped = (msg or "").strip()
        if not stripped:
            return SkipReason.EMPTY
        if stripped.startswith("/"):
            return SkipReason.SLASH_COMMAND
        if len(stripped) < _MIN_LEN_FOR_LLM:
            return SkipReason.TRIVIAL
        return None

    def _synthetic_for_skip(self, msg: str, skip: str) -> IntentResult:
        if skip == SkipReason.SLASH_COMMAND:
            return IntentResult(
                category="task", priority="normal", confidence=1.0,
                rationale="slash command — treated as task by default",
                skipped_reason=skip,
            )
        if skip == SkipReason.TRIVIAL:
            if _is_pure_greeting_short(msg):
                return IntentResult(
                    category="greeting", priority="low", confidence=1.0,
                    rationale="trivial greeting", skipped_reason=skip,
                )
            return IntentResult(
                category="unknown", priority="low", confidence=0.0,
                rationale="too short to classify", skipped_reason=skip,
            )
        # DISABLED / EMPTY
        return IntentResult(
            category="unknown", priority="low", confidence=0.0,
            rationale=f"skipped: {skip}", skipped_reason=skip,
        )

    def _log(self, user_id: str, msg: str, result: IntentResult) -> None:
        """Best-effort append — never raises."""
        try:
            self.log_path.parent.mkdir(parents=True, exist_ok=True)
            entry = {
                "ts": datetime.now(timezone.utc).isoformat(),
                "user_id": user_id,
                "msg_hash": hashlib.sha256((msg or "").encode("utf-8")).hexdigest()[:12],
                "msg_len": len(msg or ""),
                "category": result.category,
                "priority": result.priority,
                "confidence": round(result.confidence, 3),
                "latency_ms": result.latency_ms,
                "skipped_reason": result.skipped_reason,
                "error": result.error,
            }
            with self.log_path.open("a") as fh:
                fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
        except Exception:
            pass


# ── Convenience for tests ─────────────────────────────────────────────────────


def parse_output_for_test(raw: str) -> IntentResult:
    """Pure parser — exposed for unit tests."""
    category, priority, confidence, rationale, err = _parse_output(raw)
    return IntentResult(
        category=category, priority=priority, confidence=confidence,
        rationale=rationale, error=err,
    )
