"""VULCAN NL entity + intent resolver — keyless, deterministic.

Turns a free-text engineer query (FR3) into the structured slots the supervisor
needs: which asset, which scenario (if named), and what the engineer wants
(diagnosis / rca / rul / risk / recommend / report / general). Resolution is
deterministic (regex + alias maps + spine lookups) so it costs ~0 ms and never
hits a rate limit — the LLM is reserved for prose synthesis, not parsing.

Falls back to the conversation *focus* (last asset/scenario) so follow-up turns
like "and how long do I have?" inherit the previously-discussed machine (FR3
multi-turn context).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from functools import lru_cache
from typing import Optional

from ..data.loaders import get_datastore
from .memory import Focus

# intent keyword maps (checked in priority order)
_INTENT_RULES: list[tuple[str, tuple[str, ...]]] = [
    ("report",     ("report", "summary", "write up", "document", "work order", "handover")),
    ("rca",        ("root cause", "why did", "why is", "rca", "cause of", "what caused",
                    "reason", "analysis")),
    ("rul",        ("how long", "remaining life", "rul", "time left", "before it fails",
                    "lifespan", "when will", "days left")),
    ("procurement",("spare", "part", "order", "stock", "procure", "lead time", "supplier")),
    ("risk",       ("risk", "priority", "how urgent", "critical", "severity", "how bad")),
    ("recommend",  ("what should", "what do i do", "how do i fix", "recommend", "action",
                    "steps", "procedure", "repair", "replace", "next step", "fix")),
    ("diagnosis",  ("diagnose", "what's wrong", "whats wrong", "what is wrong", "fault",
                    "problem", "symptom", "vibration", "temperature", "noise", "alarm",
                    "trip", "leak", "smell", "overheat")),
]

_SCN_RE = re.compile(r"\bSCN[-_ ]?(\d{1,3})\b", re.I)
_PART_RE = re.compile(r"\b([A-Z]{2,5}-[A-Z0-9]{1,6}(?:-[A-Z0-9]{1,6})?)\b")


@dataclass
class ResolvedQuery:
    raw: str
    intent: str = "diagnosis"
    asset_id: Optional[str] = None
    scenario_id: Optional[str] = None
    part_id: Optional[str] = None
    symptom: str = ""
    inherited_asset: bool = False        # True if asset came from conversation focus
    notes: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Asset alias index — equipment-class words + asset-id fragments -> canonical id.
# ---------------------------------------------------------------------------
@lru_cache(maxsize=1)
def _asset_alias_index() -> dict[str, str]:
    """Map keyword tokens -> canonical asset_id. Built from the spine once."""
    sp = get_datastore().spine()
    idx: dict[str, str] = {}
    for a in sp.assets:
        # canonical id and a few normalized variants
        idx[a.asset_id.lower()] = a.asset_id
        idx[a.asset_id.replace(".", "").lower()] = a.asset_id
        idx[a.asset_id.replace(".", "-").lower()] = a.asset_id
        # equipment-class words (e.g. "mill gearbox", "ladle crane")
        cls_words = a.equipment_class.replace("_", " ").lower()
        idx.setdefault(cls_words, a.asset_id)
        # description-derived hints (first strong noun phrase)
        for tok in re.findall(r"[a-z]{4,}", a.equipment_class.lower()):
            idx.setdefault(tok, a.asset_id)
    return idx


# equipment-class phrases that should win over single-token matches
@lru_cache(maxsize=1)
def _class_phrases() -> list[tuple[str, str]]:
    sp = get_datastore().spine()
    pairs = []
    for a in sp.assets:
        phrase = a.equipment_class.replace("_", " ").lower()
        pairs.append((phrase, a.asset_id))
    # longest phrase first so "continuous caster mould" beats "continuous caster segment"
    pairs.sort(key=lambda p: len(p[0]), reverse=True)
    return pairs


def _detect_asset(q: str) -> Optional[str]:
    ql = q.lower()
    # 1. explicit asset-id-ish token
    sp = get_datastore().spine()
    for a in sp.assets:
        for variant in (a.asset_id.lower(), a.asset_id.replace(".", "").lower(),
                        a.asset_id.replace(".", "-").lower()):
            if variant in ql.replace(".", "").replace("-", "") or a.asset_id.lower() in ql:
                return a.asset_id
    # 2. multi-word equipment-class phrase (longest first)
    for phrase, aid in _class_phrases():
        if phrase in ql:
            return aid
    # 3. single distinctive token
    idx = _asset_alias_index()
    for tok in re.findall(r"[a-z]{4,}", ql):
        if tok in idx:
            return idx[tok]
    return None


# symptom words that, when present, mean the engineer is reporting a FAULT — these
# should route to the full diagnosis pipeline (the superset) even if the sentence
# also contains an action ask like "what do I do".
_SYMPTOM_WORDS = (
    "vibrat", "noise", "noisy", "overheat", "temperature", "leak", "smell", "trip",
    "alarm", "spall", "bpfo", "bpfi", "crack", "seiz", "surge", "cavitat", "chatter",
    "broken", "knock", "grind", "smoke", "burn", "contaminat", "starv", "imbalance",
    "what's wrong", "whats wrong", "what is wrong",
)


def _detect_intent(q: str) -> str:
    ql = q.lower()
    matched: list[str] = []
    for intent, kws in _INTENT_RULES:
        if any(k in ql for k in kws):
            matched.append(intent)
    if not matched:
        return "diagnosis"
    # If a symptom is being reported, run the full diagnosis pipeline (it also yields
    # rca/rul/risk/actions), UNLESS the query is purely a single narrow ask.
    has_symptom = any(w in ql for w in _SYMPTOM_WORDS)
    if has_symptom and matched[0] in ("recommend", "diagnosis", "risk"):
        return "diagnosis"
    return matched[0]


def resolve(query: str, focus: Optional[Focus] = None) -> ResolvedQuery:
    """Resolve a free-text query into structured slots, inheriting from `focus`."""
    rq = ResolvedQuery(raw=query, symptom=query.strip())
    rq.intent = _detect_intent(query)

    m = _SCN_RE.search(query)
    if m:
        rq.scenario_id = f"SCN-{int(m.group(1)):03d}"
        rq.notes.append(f"scenario {rq.scenario_id} named explicitly")

    pm = _PART_RE.search(query)
    if pm and rq.intent == "procurement":
        rq.part_id = pm.group(1).upper()

    asset = _detect_asset(query)
    if asset:
        rq.asset_id = asset
    elif focus and focus.asset_id:
        rq.asset_id = focus.asset_id
        rq.inherited_asset = True
        rq.notes.append(f"asset inherited from conversation: {focus.asset_id}")

    # scenario inheritance for follow-ups
    if not rq.scenario_id and focus and focus.scenario_id and rq.inherited_asset:
        rq.scenario_id = focus.scenario_id
        rq.notes.append(f"scenario inherited from conversation: {focus.scenario_id}")

    return rq
