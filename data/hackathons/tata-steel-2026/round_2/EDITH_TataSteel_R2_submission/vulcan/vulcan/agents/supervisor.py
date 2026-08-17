"""VULCAN supervisor — the agentic core (orchestrator + reasoning trace + synthesis).

Given an engineer query OR an alert, the supervisor:

  1. RESOLVES the query into {asset, scenario, intent} (keyless, deterministic).
  2. PLANS which domain agents to invoke for this intent (a transparent DAG).
  3. RUNS those agents, each grounding its finding in dataset sources, every move
     appended to a single :class:`ReasoningTrace` (FR4: show your work).
  4. SYNTHESISES one natural-language answer via the LLM chokepoint
     (`subscription_llm`) — the ONLY model call in the whole turn — feeding it the
     agents' grounded findings as numbered `Source [N]` context with inline `[N]`
     citations. Falls back to a deterministic grounded template if no model.
  5. GATES the answer through the local NLI faithfulness check; flags/repairs any
     claim the sources don't support (FR4: verified badge, no hallucination).
  6. PERSISTS the turn + conversation focus (FR3 multi-turn).

This is a clean custom orchestrator (lighter than LangGraph on a CPU box) but it
is genuinely agentic: dynamic per-intent planning, specialist delegation, tool
use, an auditable trace, and a faithfulness self-check.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Optional

from .. import rag
from ..llm import subscription_llm
from ..tools import data_tools as T
from .domain_agents import (
    DiagnosisAgent,
    Finding,
    PredictorAgent,
    PrioritizerAgent,
    RCAAgent,
    RecommenderAgent,
)
from .memory import ConversationStore, Focus, get_store
from .resolver import ResolvedQuery, resolve
from .trace import ReasoningTrace

log = logging.getLogger("vulcan.supervisor")

# per-intent agent plans (the DAG the supervisor executes)
# 'diagnosis' is the full pipeline; narrower intents run a focused subset but
# always include the upstream agents their answer depends on.
_PLANS: dict[str, list[str]] = {
    "diagnosis":   ["diagnosis", "predictor", "rca", "prioritizer", "recommender"],
    "rca":         ["diagnosis", "rca", "prioritizer"],
    "rul":         ["diagnosis", "predictor", "prioritizer"],
    "risk":        ["diagnosis", "predictor", "prioritizer"],
    "recommend":   ["diagnosis", "rca", "recommender", "prioritizer"],
    "procurement": ["diagnosis", "recommender"],
    "report":      ["diagnosis", "predictor", "rca", "prioritizer", "recommender"],
    "general":     ["diagnosis"],
}

@dataclass
class _ScoreSource:
    """A minimal source object the NLI faithfulness gate can score against.

    Mirrors the (.text, .source) duck-type the gate expects from a RetrievedChunk,
    so structured spine/ML facts are checkable on equal footing with RAG chunks."""
    text: str
    source: str


_SYS = (
    "You are EDITH, the conversational reasoning core of VULCAN — an agentic "
    "maintenance wizard for a steel plant. You speak to maintenance engineers. "
    "Answer ONLY from the numbered Source [N] evidence provided; cite the source "
    "number inline as [N] after every factual claim. Be concise, technical, and "
    "decisive. Never invent part numbers, costs, thresholds, or steps not in the "
    "sources. If evidence is missing, say so plainly."
)


@dataclass
class TurnResult:
    answer: str
    intent: str
    asset_id: Optional[str]
    scenario_id: Optional[str]
    risk_band: Optional[str]
    rul: Optional[dict]
    confidence: str                    # verified | unverified | low
    faithfulness: float
    llm_rung: str
    llm_latency_ms: int
    sources: list[str]
    trace: ReasoningTrace
    findings: dict[str, Finding] = field(default_factory=dict)
    unfaithful: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "answer": self.answer,
            "intent": self.intent,
            "asset_id": self.asset_id,
            "scenario_id": self.scenario_id,
            "risk_band": self.risk_band,
            "rul": self.rul,
            "confidence": self.confidence,
            "faithfulness": self.faithfulness,
            "llm_rung": self.llm_rung,
            "llm_latency_ms": self.llm_latency_ms,
            "sources": self.sources,
            "unfaithful_claims": self.unfaithful,
            "trace": self.trace.to_dict(),
        }


class Supervisor:
    """Plan -> delegate -> synthesise -> gate -> remember. Stateless except for the
    injected conversation store (FR3)."""

    def __init__(self, store: Optional[ConversationStore] = None) -> None:
        self.store = store or get_store()
        self.diagnosis = DiagnosisAgent()
        self.rca = RCAAgent()
        self.predictor = PredictorAgent()
        self.prioritizer = PrioritizerAgent()
        self.recommender = RecommenderAgent()

    # -- public entry points -------------------------------------------------
    def handle_query(self, query: str, *, session_id: str = "default",
                     run_gate: bool = True) -> TurnResult:
        """Handle a free-text engineer query within a conversation session."""
        focus = self.store.get_focus(session_id)
        rq = resolve(query, focus=focus)
        trace = ReasoningTrace(query=query)
        self._trace_plan(rq, trace, focus)
        return self._run(rq, trace, session_id, focus, run_gate, user_text=query)

    def handle_alert(self, *, asset_id: str, sensor: str = "", severity: str = "",
                     scenario_id: Optional[str] = None, session_id: str = "alerts",
                     run_gate: bool = True) -> TurnResult:
        """Handle an inbound condition-monitoring ALERT (FR7 real-time alerting).

        The supervisor treats an alert as a high-priority diagnosis trigger: it
        synthesises the same grounded diagnosis+risk+action answer, proactively."""
        sym = f"Alert on {sensor or asset_id}: severity {severity}".strip()
        rq = ResolvedQuery(raw=sym, intent="diagnosis", asset_id=asset_id,
                           scenario_id=scenario_id, symptom=sym)
        trace = ReasoningTrace(query=f"[ALERT] {sym}")
        trace.add("plan", "Inbound condition-monitoring alert — run a proactive "
                  "diagnosis, risk classification and action plan.",
                  "supervisor.handle_alert",
                  f"asset={asset_id} sensor={sensor} severity={severity}")
        return self._run(rq, trace, session_id, self.store.get_focus(session_id),
                         run_gate, user_text=sym)

    # -- core orchestration --------------------------------------------------
    def _trace_plan(self, rq: ResolvedQuery, trace: ReasoningTrace,
                    focus: Focus) -> None:
        plan = _PLANS.get(rq.intent, _PLANS["general"])
        notes = "; ".join(rq.notes) if rq.notes else "fresh query"
        trace.add(
            "plan",
            f"Classify intent='{rq.intent}', resolve target asset='{rq.asset_id}'"
            + (f", scenario='{rq.scenario_id}'" if rq.scenario_id else "")
            + f". Plan agent chain: {' -> '.join(plan)}.",
            "supervisor.plan",
            f"intent={rq.intent}; asset={rq.asset_id}; agents={plan}; {notes}",
        )

    def _run(self, rq: ResolvedQuery, trace: ReasoningTrace, session_id: str,
             focus: Focus, run_gate: bool, user_text: str) -> TurnResult:
        # Guard: no asset resolved -> ask for clarification (grounded, no LLM needed)
        if not rq.asset_id:
            ans = ("I could not identify which machine you mean. Please name the asset "
                   "(e.g. 'HSM.F3.WR.BRG01' or 'mill gearbox') or the scenario id "
                   "(e.g. SCN-037).")
            trace.add("note", "No asset could be resolved from the query or "
                      "conversation focus.", "supervisor.clarify", "asked for asset")
            self.store.add_turn(session_id, "user", user_text)
            self.store.add_turn(session_id, "assistant", ans, intent=rq.intent)
            return TurnResult(answer=ans, intent=rq.intent, asset_id=None,
                              scenario_id=None, risk_band=None, rul=None,
                              confidence="unverified", faithfulness=1.0,
                              llm_rung="none", llm_latency_ms=0, sources=[], trace=trace)

        plan = _PLANS.get(rq.intent, _PLANS["general"])
        findings: dict[str, Finding] = {}

        # window: the live trailing sensor window (drives ML)
        eq_class = T.get_asset(rq.asset_id).get("equipment_class")

        # 1. diagnosis (always first — establishes scenario + ML fault)
        if "diagnosis" in plan:
            f = self.diagnosis.run(asset_id=rq.asset_id, symptom=rq.symptom,
                                   scenario_hint=rq.scenario_id, window=None, trace=trace)
            findings["diagnosis"] = f
            # promote the matched scenario for downstream agents
            scn = f.data.get("matched_scenario", {})
            if scn.get("found"):
                rq.scenario_id = rq.scenario_id or scn.get("scenario_id")

        scn_detail = (findings.get("diagnosis").data.get("matched_scenario")
                      if "diagnosis" in findings else {}) or {}
        failure_mode = scn_detail.get("failure_mode", "")
        # the failure window the diagnosis agent selected — reused so the whole
        # turn (anomaly score etc.) reflects the SAME state the engineer reported.
        live_window = (findings["diagnosis"].data.get("live_window")
                       if "diagnosis" in findings else None)

        # 2. predictor
        if "predictor" in plan:
            findings["predictor"] = self.predictor.run(
                asset_id=rq.asset_id, window=live_window, trace=trace)

        # 3. rca
        if "rca" in plan:
            findings["rca"] = self.rca.run(
                asset_id=rq.asset_id, scenario_id=rq.scenario_id,
                failure_mode=failure_mode, eq_class=eq_class, trace=trace)

        # 4. recommender (needs scenario for spares)
        if "recommender" in plan:
            findings["recommender"] = self.recommender.run(
                asset_id=rq.asset_id, scenario_id=rq.scenario_id, eq_class=eq_class,
                scenario=scn_detail, trace=trace)

        # 5. prioritizer (synthesises criticality × spares × lead-time × ML × RUL)
        risk_band = None
        if "prioritizer" in plan:
            spares = (findings["recommender"].data.get("spares")
                      if "recommender" in findings else
                      (T.get_spares_for_scenario(rq.scenario_id) if rq.scenario_id else {}))
            ml_fault = (findings["diagnosis"].data.get("ml_fault", {})
                        if "diagnosis" in findings else {})
            rul_band = (findings["predictor"].data.get("rul_band", "monitor")
                        if "predictor" in findings else "monitor")
            f = self.prioritizer.run(
                asset=T.get_asset(rq.asset_id), scenario=scn_detail, spares=spares or {},
                ml_fault=ml_fault, rul_band=rul_band, trace=trace)
            findings["prioritizer"] = f
            risk_band = f.data.get("risk_band")

        # ---- assemble grounded numbered context for synthesis ----
        # `score_sources[i]` is exactly what the answer's [i+1] citation refers to —
        # structured spine/ML facts AND RAG chunks, on equal footing for the NLI gate.
        ctx_block, score_sources, source_list = self._build_context(rq, findings)

        # ---- the ONE LLM call: synthesis ----
        user_prompt = self._synthesis_prompt(rq, findings, ctx_block)
        res = subscription_llm(_SYS, user_prompt, task=rq.intent if rq.intent in
                               ("rca", "report") else "diagnosis",
                               context=ctx_block, return_result=True)
        trace.add("llm",
                  "Synthesise the grounded findings into one cited natural-language "
                  "answer (single model call; deterministic template floor if offline).",
                  "subscription_llm",
                  f"{res.rung} · {len(res.text)} chars", rung=res.rung,
                  detail={"model": res.model, "is_template": res.is_template})
        answer = res.text

        # ---- faithfulness gate (FR4) ----
        confidence, faithfulness, unfaithful = "unverified", 1.0, []
        if run_gate and score_sources and not res.is_template:
            gate = rag.run_gate(answer, score_sources, threshold=0.5)
            confidence, faithfulness, unfaithful = (
                gate.confidence, gate.overall, gate.unfaithful)
            trace.add("gate",
                      "Verify every cited claim entails its source via local NLI "
                      "(cross-encoder). Flag unsupported claims.",
                      "rag.run_gate(nli-deberta)",
                      f"faithfulness={gate.overall:.2f} -> {gate.confidence}"
                      + (f"; {len(unfaithful)} flagged" if unfaithful else ""),
                      detail={"unfaithful": unfaithful})
            if unfaithful:
                answer += ("\n\n> [VULCAN faithfulness note] The following claim(s) "
                           "were not fully supported by the cited sources and should "
                           "be treated as low-confidence: "
                           + "; ".join(f"\"{u}\"" for u in unfaithful))

        # ---- persist multi-turn state (FR3) ----
        new_focus = Focus(asset_id=rq.asset_id, scenario_id=rq.scenario_id,
                          last_intent=rq.intent, data=dict(focus.data))
        new_focus.update(risk_band=risk_band, failure_mode=failure_mode)
        self.store.add_turn(session_id, "user", user_text)
        self.store.add_turn(session_id, "assistant", answer, intent=rq.intent,
                            focus=new_focus)
        self.store.save_focus(session_id, new_focus)

        rul = findings["predictor"].data.get("rul") if "predictor" in findings else None
        return TurnResult(
            answer=answer, intent=rq.intent, asset_id=rq.asset_id,
            scenario_id=rq.scenario_id, risk_band=risk_band, rul=rul,
            confidence=confidence, faithfulness=faithfulness,
            llm_rung=res.rung, llm_latency_ms=res.latency_ms,
            sources=source_list, trace=trace, findings=findings,
            unfaithful=unfaithful,
        )

    # -- context assembly ----------------------------------------------------
    def _build_context(self, rq: ResolvedQuery, findings: dict[str, Finding]
                       ) -> tuple[str, list[Any], list[str]]:
        """Build a numbered `Source [N]` block from agent findings + RAG chunks.

        Returns (context_block, scoreable_sources, source_files). The KEY invariant:
        ``scoreable_sources[i]`` is the source the answer's ``[i+1]`` citation refers
        to — covering BOTH the structured spine/ML facts AND the RAG chunks. The NLI
        gate scores each cited claim against this list, so a ``[1]`` that cites a
        spine fact is checked against that fact's text (not the first RAG chunk)."""
        blocks: list[str] = []
        score_sources: list[_ScoreSource] = []   # 1:1 with the [N] numbering
        n = 0

        def _add(src_file: str, text: str, header: str) -> None:
            nonlocal n
            n += 1
            blocks.append(f"Source [{n}] ({header}):\n{text}")
            score_sources.append(_ScoreSource(text=text, source=src_file))

        # 1) structured spine/ML facts as numbered, scoreable sources
        d = findings.get("diagnosis")
        if d:
            scn = d.data.get("matched_scenario", {})
            if scn.get("found"):
                _add("SPEC/ground_truth_spine.json",
                     f"Scenario {scn.get('scenario_id')} on asset {scn.get('asset_id')}: "
                     f"failure_mode is {scn.get('failure_mode')}; safety_class is "
                     f"{scn.get('safety_class')}; root_cause: {scn.get('root_cause')} "
                     f"Downtime hours: {scn.get('downtime_hours')}. "
                     f"Cost impact: {scn.get('cost_impact')}.",
                     f"SPEC/ground_truth_spine.json — scenario {scn.get('scenario_id')}")
            br = d.data.get("threshold_breaches", [])
            mlf = d.data.get("ml_fault", {})
            br_txt = ("; ".join(f"{b['tag']} = {b['value']} ({b['status']}, "
                                f"warn {b.get('warning_threshold')}, alarm "
                                f"{b.get('alarm_threshold')})" for b in br)
                      if br else "no sensor threshold breaches")
            _add("condition_monitoring/by_equipment/*.csv",
                 f"The ML fault classifier predicts class {mlf.get('predicted_class')} "
                 f"with probabilities {mlf.get('probabilities')}. Sensor threshold "
                 f"status: {br_txt}.",
                 "condition_monitoring + ML fault classifier")

        p = findings.get("predictor")
        if p:
            _add("condition_monitoring/rul_trajectories_long.csv",
                 f"Estimated remaining useful life is approximately "
                 f"{p.data['rul'].get('rul_cycles')} cycles "
                 f"(~{p.data['rul'].get('rul_days_estimate')} days). RUL band is "
                 f"{p.data.get('rul_band')}. Anomaly score is "
                 f"{p.data['anomaly'].get('anomaly_score')} "
                 f"(is_anomaly={p.data['anomaly'].get('is_anomaly')}).",
                 "condition_monitoring/rul_trajectories_long.csv — ML RUL")

        rc = findings.get("rca")
        if rc and rc.data.get("root_cause"):
            res_steps = rc.data.get("correct_resolution") or []
            _add("SPEC/ground_truth_spine.json",
                 f"Root cause: {rc.data['root_cause']} "
                 f"Correct resolution steps: {res_steps}.",
                 "SPEC/ground_truth_spine.json — RCA")

        pr = findings.get("prioritizer")
        if pr:
            _add("SPEC/ground_truth_spine.json",
                 f"The risk classification is {pr.data['risk_band']} with a computed "
                 f"score of {pr.data['risk_score']:.0f}. The contributing factors are: "
                 f"{'; '.join(pr.data['factors'])}.",
                 "risk computation (criticality x safety x ML x RUL x spares)")

        rec = findings.get("recommender")
        if rec:
            steps = rec.data.get("resolution_steps") or []
            proc = rec.data.get("procurement_strategy") or []
            _add("knowledge_docs/spare_parts_catalog.csv",
                 f"Recommended action steps: {steps}. Spare-procurement strategy: "
                 f"{proc}. Total parts cost: INR "
                 f"{rec.data.get('total_parts_cost_inr')}.",
                 "SOP + spare_parts_catalog.csv")

        # 2) RAG document chunks as numbered, scoreable sources
        seen_chunk_ids: set[str] = set()
        for key in ("diagnosis", "rca", "recommender"):
            f = findings.get(key)
            if not f:
                continue
            for c in f.chunks:
                cid = getattr(c, "chunk_id", None)
                if cid and cid in seen_chunk_ids:
                    continue
                if cid:
                    seen_chunk_ids.add(cid)
                sec = f" § {c.section}" if getattr(c, "section", "") else ""
                _add(c.source, c.text[:700], f"{c.source}{sec}")

        # source list for the citation panel
        src_list: list[str] = []
        for f in findings.values():
            for s in f.sources:
                if s and s not in src_list:
                    src_list.append(s)
        return "\n\n".join(blocks), score_sources, src_list

    def _synthesis_prompt(self, rq: ResolvedQuery, findings: dict[str, Finding],
                          ctx_block: str) -> str:
        ask = {
            "diagnosis": ("Give the engineer: (1) the diagnosis (probable fault), "
                          "(2) the root cause, (3) the remaining useful life / lead-time, "
                          "(4) the risk classification, and (5) the prioritized next "
                          "actions including any spare to ORDER NOW."),
            "rca": "Explain the ROOT cause of this fault and the evidence chain behind it.",
            "rul": "State the remaining useful life and how much lead-time the engineer has.",
            "risk": "State the risk classification and justify it from the factors.",
            "recommend": ("Give the step-by-step recommended actions and the spare-"
                          "procurement strategy (ORDER NOW for any out-of-stock part)."),
            "procurement": "Give the spare-procurement strategy with availability + lead-time.",
            "report": ("Write a structured maintenance report: Diagnosis, Root Cause, "
                       "RUL, Risk, Recommended Actions, Spare Procurement, Cost."),
            "general": "Answer the engineer's question using the evidence.",
        }.get(rq.intent, "Answer the engineer's question using the evidence.")
        return (
            f"Engineer query: {rq.raw}\n"
            f"Target asset: {rq.asset_id}"
            + (f"\nScenario: {rq.scenario_id}" if rq.scenario_id else "")
            + f"\n\nEVIDENCE (cite these as [N]):\n{ctx_block}\n\n"
            f"TASK: {ask}\n"
            "Cite [N] inline after every fact. Keep it tight and decisive."
        )
