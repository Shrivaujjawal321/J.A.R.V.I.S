"""
jarvis-core — Super-agent orchestrator daemon.

Long-running FastAPI service that uses Claude Agent SDK to dispatch
Claude Code workers (single or parallel). Authenticates via Max-subscription
OAuth token (CLAUDE_CODE_OAUTH_TOKEN env var) — no developer API key needed.

Modules:
- models.py        Pydantic request/response schemas
- state.py         In-memory conversation + task state with disk persistence
- orchestrator.py  Agent SDK dispatcher (single + parallel modes)
- recall.py        Phase A — pre-response semantic memory recall
- critic.py        Phase B — post-response silent reviewer + revise loop
- confidence.py    Phase B — confidence tag helpers (verified/unverified/low)
- daemon.py        FastAPI service exposing /chat, /task, /health, /state

Phase 1 scope: text-only via Telegram bridge. Voice + cron migrate in Phase 2.
"""

__version__ = "0.2.0"  # bumped for Phase A+B (recall + critic)

from .confidence import Confidence, annotate, is_silent, normalise
from .critic import Critic, CritiqueOutcome, CritiqueResult
from .recall import Recaller, RecallResult, SkipReason

__all__ = [
    "__version__",
    "Recaller",
    "RecallResult",
    "SkipReason",
    "Critic",
    "CritiqueOutcome",
    "CritiqueResult",
    "Confidence",
    "annotate",
    "is_silent",
    "normalise",
]
