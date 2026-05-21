"""
Confidence tag helpers.

A response from `/chat` carries a confidence label set by the critic:
- `verified`   — passed all critic checks (or critique was skipped). Tag is silent.
- `unverified` — critic raised issues; revised once; ship with visible tag.
- `low`        — critic raised many/severe issues; ship with visible tag flagging caution.

Visible-only tags are appended to long replies as a single italic line so Boss
can see at a glance which responses were softened.
"""
from __future__ import annotations

from typing import Literal

Confidence = Literal["verified", "unverified", "low"]

VALID_LEVELS: tuple[Confidence, ...] = ("verified", "unverified", "low")

# Boss-facing labels (short, scannable)
_LABELS: dict[Confidence, str] = {
    "verified": "verified",
    "unverified": "unverified — light hedge",
    "low": "low confidence — please double-check",
}


def normalise(value: str | None) -> Confidence:
    """Coerce arbitrary critic output to a valid Confidence literal."""
    if not value:
        return "unverified"
    v = value.strip().lower()
    if v in VALID_LEVELS:
        return v  # type: ignore[return-value]
    # Common alias handling
    if v in ("ok", "good", "pass", "passed", "high"):
        return "verified"
    if v in ("medium", "mid", "warn", "warning", "soft"):
        return "unverified"
    if v in ("fail", "failed", "bad", "poor", "weak"):
        return "low"
    return "unverified"


def is_silent(level: Confidence) -> bool:
    """Whether this confidence level should be hidden from the user (default = good)."""
    return level == "verified"


def annotate(reply: str, level: Confidence) -> str:
    """Append a visible tag for non-silent levels. Returns reply unchanged for `verified`.

    Skips annotation if the reply is already < 60 chars (would dominate the message).
    """
    if is_silent(level) or len(reply or "") < 60:
        return reply
    label = _LABELS.get(level, level)
    suffix = f"\n\n_[{label}]_"
    # Avoid double-tagging if upstream already appended one
    if reply.rstrip().endswith("_]_") and "[" in reply.rsplit("_[", 1)[-1]:
        return reply
    return reply + suffix
