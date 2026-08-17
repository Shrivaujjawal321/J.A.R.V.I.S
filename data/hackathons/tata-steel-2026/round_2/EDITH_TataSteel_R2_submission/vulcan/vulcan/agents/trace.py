"""VULCAN reasoning trace — the transparent, judge-facing record of HOW EDITH thought.

FR4 (explainable + traceable) is the heaviest-scored requirement. Every supervisor
run produces a :class:`ReasoningTrace`: an ordered list of :class:`TraceStep`, each
one a (thought -> tool/agent -> result) triple with a wall-clock latency and the
dataset ``source`` refs that ground it. The UI renders this verbatim; the report
embeds it; the demo narrates it.

This module is pure data + formatting — no LLM, no I/O, never raises. It is the
single source of truth for "show your work".
"""

from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass, field
from typing import Any


def _now_ms() -> int:
    return int(time.time() * 1000)


@dataclass
class TraceStep:
    """One atomic reasoning step: a thought, the action it triggered, the result.

    ``kind`` is one of: ``plan`` | ``tool`` | ``agent`` | ``rag`` | ``ml`` |
    ``llm`` | ``gate`` | ``synthesis`` | ``note``. ``sources`` lists the dataset
    files this step's facts came from (drives inline citations)."""

    step: int
    kind: str
    thought: str                       # WHY this step — the reasoning
    action: str                        # WHAT was invoked (tool/agent/model name)
    result_summary: str                # short human-readable result
    sources: list[str] = field(default_factory=list)
    latency_ms: int = 0
    detail: dict[str, Any] = field(default_factory=dict)   # structured payload (optional)
    rung: str | None = None            # which LLM rung answered, if kind == llm

    def render(self) -> str:
        src = f"   sources: {', '.join(self.sources)}" if self.sources else ""
        rung = f" [{self.rung}]" if self.rung else ""
        lat = f" ({self.latency_ms}ms)" if self.latency_ms else ""
        head = f"  STEP {self.step} · {self.kind.upper()}{rung}{lat}"
        return "\n".join(
            [head,
             f"   thought : {self.thought}",
             f"   action  : {self.action}",
             f"   result  : {self.result_summary}"]
            + ([src] if src else [])
        )


@dataclass
class ReasoningTrace:
    """An ordered, timestamped reasoning trace for one supervisor turn."""

    query: str = ""
    steps: list[TraceStep] = field(default_factory=list)
    started_ms: int = field(default_factory=_now_ms)

    # internal timer for per-step latency
    _last_ms: int = field(default=0, repr=False)

    def __post_init__(self) -> None:
        self._last_ms = self.started_ms

    def add(
        self,
        kind: str,
        thought: str,
        action: str,
        result_summary: str,
        *,
        sources: list[str] | None = None,
        detail: dict[str, Any] | None = None,
        rung: str | None = None,
    ) -> TraceStep:
        now = _now_ms()
        step = TraceStep(
            step=len(self.steps) + 1,
            kind=kind,
            thought=thought.strip(),
            action=action.strip(),
            result_summary=result_summary.strip(),
            sources=_dedupe(sources or []),
            latency_ms=max(0, now - self._last_ms),
            detail=detail or {},
            rung=rung,
        )
        self._last_ms = now
        self.steps.append(step)
        return step

    # --- aggregate views -------------------------------------------------
    def all_sources(self) -> list[str]:
        seen: list[str] = []
        for s in self.steps:
            for src in s.sources:
                if src and src not in seen:
                    seen.append(src)
        return seen

    def total_latency_ms(self) -> int:
        return sum(s.latency_ms for s in self.steps)

    def render(self) -> str:
        lines = [
            "=" * 72,
            "VULCAN · EDITH — REASONING TRACE",
            "=" * 72,
            f"query: {self.query}",
            f"steps: {len(self.steps)}   total: {self.total_latency_ms()}ms",
            "-" * 72,
        ]
        for s in self.steps:
            lines.append(s.render())
            lines.append("")
        srcs = self.all_sources()
        if srcs:
            lines.append("-" * 72)
            lines.append("grounded in: " + ", ".join(srcs))
        lines.append("=" * 72)
        return "\n".join(lines)

    def to_dict(self) -> dict[str, Any]:
        return {
            "query": self.query,
            "step_count": len(self.steps),
            "total_latency_ms": self.total_latency_ms(),
            "sources": self.all_sources(),
            "steps": [asdict(s) for s in self.steps],
        }

    def to_json(self, indent: int | None = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, default=str)


def _dedupe(items: list[str]) -> list[str]:
    out: list[str] = []
    for x in items:
        if x and x not in out:
            out.append(x)
    return out
