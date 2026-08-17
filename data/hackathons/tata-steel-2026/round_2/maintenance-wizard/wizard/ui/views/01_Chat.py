"""
wizard.ui.pages.01_Chat
=======================
Multi-turn maintenance co-pilot chat interface.

Features:
- st.chat_input (pinned via st.bottom conceptual pattern)
- st.write_stream: typewriter LLM streaming via character generator
- BLUF summary card: STATUS -> ACT BY -> WHAT'S WRONG -> HOW URGENT -> WHAT TO DO
- Citation pills via st.badge per source
- "Show details" expander: steps, parts, cost, root cause, monitoring,
  nested "Technical details" sub-section for engineers
- Thumbs up/down feedback buttons with correction text input
- Equipment selector in sidebar to bind context
- st.status during agent graph traversal ("Routing to agents...")
- Backend graceful degradation — cached gold response when backend offline

CRITICAL: httpx.Client (sync) ONLY — see wizard.ui._http module.
"""

from __future__ import annotations

import math
import time
from datetime import datetime
from typing import Generator

import streamlit as st

from wizard.ui._http import get_client, safe_get, safe_post
from wizard.ui._demo_seed import DEMO_EQUIPMENT
from wizard.ui._ui import (
    inject_global_css, status_badge, asset_id, page_header,
    render_hero_header, render_agent_pipeline,
)

inject_global_css()

# ---------------------------------------------------------------------------
# BLUF card CSS — dark glass variants
# ---------------------------------------------------------------------------
st.markdown(
    """
<style>
.bluf-card {
    background: #161B27;
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 0.75rem;
    position: relative;
    overflow: hidden;
}
.bluf-card--STOP-NOW  { border-left: 3px solid #F87171; }
.bluf-card--ACT-SOON  { border-left: 3px solid #FB923C; }
.bluf-card--SCHEDULE  { border-left: 3px solid #FBBF24; }
.bluf-card--HEALTHY   { border-left: 3px solid #34D399; }
.bluf-row {
    display: flex;
    align-items: baseline;
    gap: 0.5rem;
    margin-bottom: 0.4rem;
    line-height: 1.5;
    min-width: 0;
}
.bluf-label {
    font-family: 'IBM Plex Sans', sans-serif;
    font-size: 0.6875rem;
    font-weight: 700;
    color: #5E6080;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    min-width: 120px;
    flex-shrink: 0;
}
.bluf-value {
    font-family: 'IBM Plex Sans', sans-serif;
    font-size: 0.9rem;
    color: #E8E8F2;
    min-width: 0;
    word-break: break-word;
}
.bluf-status-STOP-NOW {
    font-size: 0.875rem;
    font-weight: 700;
    color: #F87171;
    background: rgba(248,113,113,0.12);
    border: 1px solid rgba(248,113,113,0.25);
    border-radius: 6px;
    padding: 2px 12px;
    display: inline-block;
    letter-spacing: 0.03em;
}
.bluf-status-ACT-SOON {
    font-size: 0.875rem;
    font-weight: 700;
    color: #FB923C;
    background: rgba(251,146,60,0.12);
    border: 1px solid rgba(251,146,60,0.25);
    border-radius: 6px;
    padding: 2px 12px;
    display: inline-block;
    letter-spacing: 0.03em;
}
.bluf-status-SCHEDULE {
    font-size: 0.875rem;
    font-weight: 700;
    color: #FBBF24;
    background: rgba(251,191,36,0.12);
    border: 1px solid rgba(251,191,36,0.25);
    border-radius: 6px;
    padding: 2px 12px;
    display: inline-block;
    letter-spacing: 0.03em;
}
.bluf-status-HEALTHY {
    font-size: 0.875rem;
    font-weight: 700;
    color: #34D399;
    background: rgba(52,211,153,0.12);
    border: 1px solid rgba(52,211,153,0.25);
    border-radius: 6px;
    padding: 2px 12px;
    display: inline-block;
    letter-spacing: 0.03em;
}
</style>
""",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Page header
# ---------------------------------------------------------------------------
render_hero_header(
    "Maintenance Chat",
    "Ask about any equipment — diagnosis, root cause, remaining life, maintenance plan. "
    "Responses are source-cited.",
    badge="AI CO-PILOT",
)

# ---------------------------------------------------------------------------
# Helper: new session id  (MUST be defined before sidebar uses it)
# ---------------------------------------------------------------------------
def _new_session_id() -> str:
    import uuid
    return f"session-{uuid.uuid4().hex[:12]}"


# ---------------------------------------------------------------------------
# Equipment selector (sidebar inject)
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown(
        "<p style='font-size:0.6875rem;font-weight:600;color:#94A3B8;"
        "text-transform:uppercase;letter-spacing:0.06em;margin:0 0 8px;'>Equipment</p>",
        unsafe_allow_html=True,
    )
    equipment_options = {eq["name"]: eq["asset_id"] for eq in DEMO_EQUIPMENT}
    selected_name = st.selectbox(
        "Equipment",
        options=list(equipment_options.keys()),
        index=0,
        key="chat_equipment_select",
        label_visibility="collapsed",
        help="Focuses agent context on this equipment. Queries reference its sensor data, history, and spares.",
    )
    selected_asset_id = equipment_options[selected_name]

    st.markdown(
        asset_id(selected_asset_id),
        unsafe_allow_html=True,
    )
    st.markdown("")

    if st.button("Clear Chat", key="clear_chat_btn", use_container_width=True):
        st.session_state["messages"] = []
        st.session_state["session_id"] = _new_session_id()
        st.rerun()


# ---------------------------------------------------------------------------
# Equipment acronym expansion map
# ---------------------------------------------------------------------------
_EQUIPMENT_NAMES: dict[str, str] = {
    "EAF": "Electric Arc Furnace",
    "BF": "Blast Furnace",
    "HSM": "Hot Strip Mill",
    "CCS": "Continuous Casting System",
    "CONV": "Conveyor",
    "HPU": "Hydraulic Power Unit",
    "PUMP": "Pump",
    "FAN": "Fan",
    "BRG": "Bearing",
}


def _expand_equipment_id(eq_id: str) -> str:
    """
    Turn 'EAF-04' into 'EAF-04 (Electric Arc Furnace)'.
    Matches the first token against the known acronym map.
    Falls back to the raw ID if no match found.
    """
    parts = eq_id.split("-")
    prefix = parts[0].upper()
    expansion = _EQUIPMENT_NAMES.get(prefix)
    if expansion:
        return f"{eq_id} ({expansion})"
    # Try second token for compound IDs like BF-FAN-02
    if len(parts) >= 2:
        second = parts[1].upper()
        expansion2 = _EQUIPMENT_NAMES.get(second)
        if expansion2:
            return f"{eq_id} ({expansion2})"
    return eq_id


# ---------------------------------------------------------------------------
# Priority -> plain-English severity word
# ---------------------------------------------------------------------------
_PRIORITY_TO_STATUS: dict[str, str] = {
    "critical": "STOP NOW",
    "high":     "ACT SOON",
    "medium":   "SCHEDULE",
    "low":      "HEALTHY",
}

_STATUS_CSS_CLASS: dict[str, str] = {
    "STOP NOW": "bluf-status-STOP-NOW",
    "ACT SOON": "bluf-status-ACT-SOON",
    "SCHEDULE": "bluf-status-SCHEDULE",
    "HEALTHY":  "bluf-status-HEALTHY",
}


def _priority_to_act_by(priority: str, rul_p50: float | None = None) -> str:
    """
    Translate priority tier into a plain time-frame sentence.
    Uses RUL p50 when available to give a concrete window.
    """
    p = (priority or "medium").lower()
    if p == "critical":
        return "Within 24 hours"
    if p == "high":
        if rul_p50 is not None and rul_p50 < 4:
            return "Within 2 days"
        return "Within 2-3 days"
    if p == "medium":
        return "At next maintenance window"
    return "Next scheduled service"


# ---------------------------------------------------------------------------
# Number formatting helpers
# ---------------------------------------------------------------------------
def _round_days(days: float) -> str:
    """
    Format a float number of days as plain rounded text.
    < 1 day  -> 'about X hours'
    < 14 days -> 'about X days'
    >= 14 days -> 'about X weeks'
    """
    if days < 1.0:
        hours = math.ceil(days * 24)
        return f"about {hours} hour{'s' if hours != 1 else ''}"
    if days < 14.0:
        d = round(days)
        return f"about {d} day{'s' if d != 1 else ''}"
    weeks = round(days / 7)
    return f"about {weeks} week{'s' if weeks != 1 else ''}"


def _round_inr(amount: float) -> str:
    """
    Convert a raw INR amount to a plain rounded Indian-unit string.
    e.g. 5_229_000 -> 'about 52 lakh'
        825_000   -> 'about 8 lakh'
          75_000  -> 'about 75 thousand'
    """
    if amount >= 1_00_00_000:  # 1 crore+
        crore = round(amount / 1_00_00_000)
        return f"about {crore} crore"
    if amount >= 1_00_000:  # 1 lakh+
        lakh = round(amount / 1_00_000)
        return f"about {lakh} lakh"
    if amount >= 1_000:
        k = round(amount / 1_000)
        return f"about {k} thousand"
    return f"about {round(amount)}"


# ---------------------------------------------------------------------------
# Plain-text extraction helpers
# ---------------------------------------------------------------------------
def _plain_diagnosis(rec: dict) -> str:
    """
    Pull a short, jargon-free 1-2 line description from available fields.
    Strips known ML jargon words before returning.
    """
    jargon = [
        "WeibullAFT", "IsolationForest", "LightGBM", "LSTM-AE",
        "P10", "P50", "P90", "degradation_index", "anomaly_score",
        "DoWhy", "GCM", "WRPS", "ISO 10816",
    ]

    # Prefer the clean, direct fault description; fall back to the engineer
    # summary or narrative. Always strip any "[LABEL — ID]" prefix and leading
    # "Fault:" label so the card shows a plain sentence, never a raw field header.
    diag = rec.get("diagnosis") or {}
    text = (
        (diag.get("probable_fault_description") if isinstance(diag, dict) else None)
        or rec.get("decision_summary_engineer")
        or rec.get("narrative_summary", "")
        or ""
    )
    import re as _re
    text = _re.sub(r"^\s*\[[^\]]*\]\s*", "", text)        # drop "[ENGINEER DECISION SUMMARY — EAF-04]"
    text = _re.sub(r"(?im)^\s*fault:\s*", "", text)        # drop leading "Fault:"

    for word in jargon:
        text = text.replace(word, "")

    # Trim to first 2 sentences (period-terminated) for the brief card
    sentences = [s.strip() for s in text.replace("\n", " ").split(".") if s.strip()]
    brief = ". ".join(sentences[:2])
    if brief and not brief.endswith("."):
        brief += "."
    return brief or "No diagnosis detail available."


def _plain_what_to_do(rec: dict) -> str:
    """Extract the single most important next action in plain language."""
    steps = rec.get("action_steps", [])
    if steps:
        first = steps[0]
        if isinstance(first, dict):
            # Handle both ActionStep shapes (real schema vs gold cache shape)
            return first.get("action") or first.get("action", "See step 1 in the details below.")
    # Fall back to decision_summary_supervisor first sentence
    supervisor = rec.get("decision_summary_supervisor", "") or ""
    if supervisor:
        first_sentence = supervisor.split(".")[0].strip()
        if first_sentence:
            return first_sentence + "."
    return "Review the step-by-step plan in the details below."


# ---------------------------------------------------------------------------
# Streaming generator from full text (fallback when no SSE)
# ---------------------------------------------------------------------------
def _stream_text(text: str, delay_ms: int = 8) -> Generator[str, None, None]:
    """
    Yield characters from text with a small delay to create typewriter effect.
    st.write_stream() calls this generator.
    delay_ms is per-character; 8ms approximately 125 chars/sec — visible but not sluggish.
    """
    for ch in text:
        yield ch
        time.sleep(delay_ms / 1000.0)


# ---------------------------------------------------------------------------
# BLUF summary card (always visible)
# ---------------------------------------------------------------------------
def _render_bluf_card(rec: dict) -> None:
    """
    Render the always-visible BLUF summary card above the expander.
    MACHINE / STATUS / ACT BY / WHAT'S WRONG / HOW URGENT / WHAT TO DO
    No jargon. All numbers rounded. Color-coded status word.
    """
    eq_id = rec.get("asset_id", "Unknown")
    eq_display = _expand_equipment_id(eq_id)

    priority_raw = (rec.get("priority") or "medium")
    if hasattr(priority_raw, "value"):
        priority_raw = priority_raw.value
    priority_raw = str(priority_raw).lower()
    status_word = _PRIORITY_TO_STATUS.get(priority_raw, "SCHEDULE")
    status_class = _STATUS_CSS_CLASS.get(status_word, "bluf-status-SCHEDULE")

    # RUL values
    p10 = rec.get("estimated_rul_days_p10")
    p50 = rec.get("estimated_rul_days_p50")
    p90 = rec.get("estimated_rul_days_p90")

    # Also check nested rul dict (from gold response / agent trace)
    rul_dict = rec.get("rul") or {}
    if isinstance(rul_dict, dict):
        if p10 is None:
            p10 = rul_dict.get("rul_days_p10")
        if p50 is None:
            p50 = rul_dict.get("rul_days_p50")
        if p90 is None:
            p90 = rul_dict.get("rul_days_p90")

    act_by = _priority_to_act_by(priority_raw, p50)

    # HOW URGENT line
    if p10 is not None and p50 is not None:
        worst = _round_days(float(p10))
        likely = _round_days(float(p50))
        urgency_text = f"Worst case {worst} — Most likely {likely}"
        if p90 is not None:
            best = _round_days(float(p90))
            urgency_text += f" — Best case {best}, don't rely on it"
    else:
        urgency_text = "Exact timeline not available — treat as urgent."

    what_wrong = _plain_diagnosis(rec)
    what_to_do = _plain_what_to_do(rec)

    machine_html  = f'<span class="bluf-value">{eq_display}</span>'
    status_html   = f'<span class="{status_class}">{status_word}</span>'
    act_by_html   = f'<span class="bluf-value">{act_by}</span>'
    wrong_html    = f'<span class="bluf-value">{what_wrong}</span>'
    urgency_html  = f'<span class="bluf-value">{urgency_text}</span>'
    todo_html     = f'<span class="bluf-value">{what_to_do}</span>'

    # Left-border accent class driven by status word
    _border_map: dict[str, str] = {
        "STOP NOW": "bluf-card--STOP-NOW",
        "ACT SOON": "bluf-card--ACT-SOON",
        "SCHEDULE": "bluf-card--SCHEDULE",
        "HEALTHY":  "bluf-card--HEALTHY",
    }
    border_class = _border_map.get(status_word, "bluf-card--SCHEDULE")

    card = f"""
<div class="bluf-card {border_class}">
  <div class="bluf-row">
    <span class="bluf-label">MACHINE</span>{machine_html}
  </div>
  <div class="bluf-row">
    <span class="bluf-label">STATUS</span>{status_html}
  </div>
  <div class="bluf-row">
    <span class="bluf-label">ACT BY</span>{act_by_html}
  </div>
  <div class="bluf-row">
    <span class="bluf-label">WHAT'S WRONG</span>{wrong_html}
  </div>
  <div class="bluf-row">
    <span class="bluf-label">HOW URGENT</span>{urgency_html}
  </div>
  <div class="bluf-row">
    <span class="bluf-label">WHAT TO DO</span>{todo_html}
  </div>
</div>
"""
    st.markdown(card, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# "Show details" expander
# ---------------------------------------------------------------------------
def _render_details_expander(rec: dict, cited_sources_display: list[dict]) -> None:
    """
    Collapsible expander with all deeper information.
    Sections:
      1. Step-by-step actions
      2. Parts needed
      3. Cost impact
      4. Root cause
      5. Long-term monitoring
      6. Technical details (nested, for engineers)
    """
    # Determine if there is anything worth showing
    action_steps    = rec.get("action_steps", []) or []
    parts_bom       = rec.get("parts_bill_of_materials", []) or []
    spares_warn     = rec.get("spares_procurement_warning")
    supervisor_text = rec.get("decision_summary_supervisor") or ""
    cost_inr        = rec.get("cost_avoidance_inr")
    process_defects = rec.get("process_related_defects", []) or []
    monitoring      = rec.get("long_term_monitoring", []) or []
    cited_sources   = cited_sources_display or []
    agent_trace     = rec.get("agent_trace", []) or []

    # RCA nested (may come from backend_resp directly rather than rec)
    rca_dict = rec.get("rca") or {}
    diag_dict = rec.get("diagnosis") or {}
    rul_dict  = rec.get("rul") or {}

    # Raw RUL values for technical section
    p10 = rec.get("estimated_rul_days_p10") or (rul_dict.get("rul_days_p10") if isinstance(rul_dict, dict) else None)
    p50 = rec.get("estimated_rul_days_p50") or (rul_dict.get("rul_days_p50") if isinstance(rul_dict, dict) else None)
    p90 = rec.get("estimated_rul_days_p90") or (rul_dict.get("rul_days_p90") if isinstance(rul_dict, dict) else None)
    deg_idx = rec.get("degradation_index")

    has_content = any([
        action_steps, parts_bom, spares_warn, supervisor_text, cost_inr,
        process_defects, monitoring, cited_sources, rca_dict, diag_dict,
        rul_dict, p10, p50, p90,
    ])

    if not has_content:
        return

    with st.expander("Show details", expanded=False):

        # ------------------------------------------------------------------
        # 1. Step-by-step actions
        # ------------------------------------------------------------------
        if action_steps:
            st.markdown("**Step-by-step actions**")
            for step in action_steps:
                if not isinstance(step, dict):
                    continue
                num = step.get("step_number", "")
                action = step.get("action", "")
                # Support both ActionStep shapes
                sop = step.get("cited_sop_section") or step.get("sop_reference") or ""
                role = step.get("responsible_role") or step.get("assigned_to") or ""
                duration_h = step.get("estimated_duration_hours") or step.get("estimated_hours")
                parts = step.get("parts_required", [])

                line = f"{num}. {action}"
                if sop:
                    line += f"  (Refer: {sop})"
                st.markdown(line)
                meta_parts: list[str] = []
                if role:
                    meta_parts.append(f"Assigned to: {role}")
                if duration_h:
                    hrs = float(duration_h)
                    if hrs < 1:
                        meta_parts.append(f"Time needed: about {round(hrs * 60)} minutes")
                    else:
                        meta_parts.append(f"Time needed: about {hrs:.1f} hours")
                if parts:
                    meta_parts.append(f"Parts: {', '.join(parts)}")
                if meta_parts:
                    st.caption("  |  ".join(meta_parts))
            st.divider()

        # ------------------------------------------------------------------
        # 2. Parts needed
        # ------------------------------------------------------------------
        if parts_bom or spares_warn:
            st.markdown("**Parts needed**")
            if parts_bom:
                for p in parts_bom:
                    st.markdown(f"- {p}")
            if spares_warn:
                # Plain display — no jargon, just the warning text
                st.warning(f"Procurement note: {spares_warn}")
            st.divider()

        # ------------------------------------------------------------------
        # 3. Cost impact
        # ------------------------------------------------------------------
        if cost_inr or supervisor_text:
            st.markdown("**Cost impact**")
            if cost_inr and float(cost_inr) > 0:
                rounded = _round_inr(float(cost_inr))
                st.markdown(
                    f"Potential cost avoided if you act now: **{rounded}**"
                )
            if supervisor_text:
                # Strip any numbers that look like raw INR amounts and jargon
                clean = supervisor_text
                for jargon_word in ["WRPS", "WeibullAFT", "LightGBM", "P50", "P10", "P90"]:
                    clean = clean.replace(jargon_word, "")
                st.markdown(clean.strip())
            st.divider()

        # ------------------------------------------------------------------
        # 4. Root cause
        # ------------------------------------------------------------------
        root_cause_shown = False
        if process_defects:
            st.markdown("**Root cause — process factors**")
            for defect in process_defects:
                st.markdown(f"- {defect}")
            root_cause_shown = True

        if isinstance(rca_dict, dict) and rca_dict:
            if not root_cause_shown:
                st.markdown("**Root cause**")
            root_summary = rca_dict.get("root_cause_summary", "")
            if root_summary:
                st.info(root_summary)
            five_whys = rca_dict.get("five_whys", [])
            if five_whys:
                st.markdown("Why it happened (traced back step by step):")
                for i, why in enumerate(five_whys, 1):
                    st.markdown(f"  {i}. {why}")
            root_cause_shown = True

        if root_cause_shown:
            st.divider()

        # ------------------------------------------------------------------
        # 5. Long-term monitoring
        # ------------------------------------------------------------------
        if monitoring:
            st.markdown("**Long-term monitoring**")
            for item in monitoring:
                st.markdown(f"- {item}")
            st.divider()

        # ------------------------------------------------------------------
        # 6. Technical details (for engineers)
        # ------------------------------------------------------------------
        _render_technical_details(
            rec=rec,
            cited_sources=cited_sources,
            rul_dict=rul_dict,
            diag_dict=diag_dict,
            agent_trace=agent_trace,
            p10=p10,
            p50=p50,
            p90=p90,
            deg_idx=deg_idx,
        )


def _render_technical_details(
    rec: dict,
    cited_sources: list[dict],
    rul_dict: dict,
    diag_dict: dict,
    agent_trace: list,
    p10: float | None,
    p50: float | None,
    p90: float | None,
    deg_idx: float | None,
) -> None:
    """
    Nested technical section — the only place jargon and raw numbers are allowed.
    Always inside the outer "Show details" expander, so it's never the first thing a user sees.
    """
    has_tech = any([p10, p50, p90, deg_idx, rul_dict, diag_dict, agent_trace, cited_sources])
    if not has_tech:
        return

    st.markdown("---")
    st.markdown("**Technical details (for engineers)**")

    # RUL quantiles with plain labels
    if p10 is not None or p50 is not None or p90 is not None:
        st.markdown("*Remaining Useful Life (RUL) estimates:*")
        cols = st.columns(3)
        if p10 is not None:
            cols[0].metric("Earliest likely failure (P10)", f"{float(p10):.1f} days")
        if p50 is not None:
            cols[1].metric("Most likely failure (P50)", f"{float(p50):.1f} days")
        if p90 is not None:
            cols[2].metric("Latest likely failure (P90)", f"{float(p90):.1f} days")

    # Degradation index
    if deg_idx is not None:
        label = "Degradation index (0=healthy, 1=critical)"
        st.metric(label, f"{float(deg_idx):.2f}")

    # Nested RUL model info
    if isinstance(rul_dict, dict) and rul_dict:
        model_used = rul_dict.get("model_used", "")
        anomaly_score = rul_dict.get("anomaly_score")
        failure_class = rul_dict.get("failure_class", "")
        failure_prob = rul_dict.get("failure_probability")
        bayesian = rul_dict.get("bayesian_correction_applied", False)

        meta_lines: list[str] = []
        if model_used:
            meta_lines.append(f"Model: {model_used}")
        if anomaly_score is not None:
            meta_lines.append(f"Anomaly score: {float(anomaly_score):.2f} (threshold 0.65)")
        if failure_class:
            meta_lines.append(f"Failure class: {failure_class}")
        if failure_prob is not None:
            meta_lines.append(f"Failure probability: {float(failure_prob):.0%}")
        if bayesian:
            meta_lines.append("Bayesian correction applied")
        if meta_lines:
            st.caption("  |  ".join(meta_lines))

    # Diagnosis details
    if isinstance(diag_dict, dict) and diag_dict:
        fault_codes = diag_dict.get("probable_fault_codes", [])
        confidence = diag_dict.get("confidence")
        reasoning = diag_dict.get("diagnosis_reasoning", "")

        if fault_codes:
            st.markdown(f"*Fault codes:* `{'`, `'.join(fault_codes)}`")
        if confidence is not None:
            st.markdown(f"*Diagnosis confidence:* {float(confidence):.0%}")
        if reasoning:
            st.markdown(
                f"*Reasoning:* {reasoning[:400]}{'...' if len(reasoning) > 400 else ''}"
            )

    # Cited sources
    if cited_sources:
        st.markdown(f"*Sources cited:* {len(cited_sources)} document(s)")
        for i, src in enumerate(cited_sources):
            label = src.get("label", f"[{i+1}]")
            doc_name = src.get("doc_name", "Unknown")
            section = src.get("section", "")
            chunk_text = src.get("chunk_text", "")
            confidence = src.get("confidence", "")
            equipment_ref = src.get("equipment_id", "")

            header = f"{label}: {doc_name}"
            if section:
                header += f" — {section}"

            with st.expander(header, expanded=False):
                if chunk_text:
                    st.markdown(f"> {chunk_text[:400]}{'...' if len(chunk_text) > 400 else ''}")
                meta: list[str] = []
                if equipment_ref:
                    meta.append(f"Equipment: {equipment_ref}")
                if confidence:
                    conf_str = (
                        f"{float(confidence):.2f}"
                        if isinstance(confidence, float)
                        else str(confidence)
                    )
                    meta.append(f"Relevance: {conf_str}")
                if meta:
                    st.caption("  |  ".join(meta))

    # Agent execution pipeline
    if agent_trace:
        render_agent_pipeline(agent_trace, compact=True)


# ---------------------------------------------------------------------------
# Citation pills renderer
# ---------------------------------------------------------------------------
def _render_citation_pills(cited_sources: list[dict]) -> None:
    """
    Render one st.badge pill per cited source.
    Each pill: [N] doc_name section
    """
    if not cited_sources:
        return

    st.markdown("**Sources:**")
    cols = st.columns(min(len(cited_sources), 4))
    for i, src in enumerate(cited_sources):
        col = cols[i % 4]
        label = src.get("label", f"[{i + 1}]")
        doc_name = src.get("doc_name", src.get("chunk_id", "Source"))
        section = src.get("section", "")
        pill_text = f"{label}: {doc_name}"
        if section:
            pill_text += f" {section}"
        with col:
            st.badge(pill_text[:40], color="blue")


# ---------------------------------------------------------------------------
# Feedback widget
# ---------------------------------------------------------------------------
def _render_feedback_widget(msg_idx: int, msg: dict) -> None:
    """
    Thumbs up/down + optional correction text.
    Uses st.button with unique key=f"fb_{msg_idx}_..." to avoid form wipe.
    """
    if msg.get("role") != "assistant":
        return

    fb_key = f"fb_state_{msg_idx}"
    if fb_key not in st.session_state:
        st.session_state[fb_key] = None

    col1, col2, col3 = st.columns([1, 1, 8])
    with col1:
        if st.button("Correct", key=f"fb_{msg_idx}_up", icon=":material/thumb_up:", help="Correct diagnosis"):
            st.session_state[fb_key] = "positive"
            _submit_feedback(msg, "positive", "")
    with col2:
        if st.button("Report error", key=f"fb_{msg_idx}_down", icon=":material/thumb_down:", help="Incorrect — provide correction"):
            st.session_state[fb_key] = "negative"

    if st.session_state[fb_key] == "positive":
        st.success("Feedback recorded.", icon=":material/check_circle:")

    elif st.session_state[fb_key] == "negative":
        correction = st.text_input(
            "Correction:",
            key=f"fb_{msg_idx}_correction",
            placeholder="e.g. Fault was electrical, not mechanical",
        )
        corrected_rul = st.number_input(
            "Corrected RUL estimate (days, optional):",
            min_value=0.0,
            max_value=365.0,
            step=0.5,
            value=0.0,
            key=f"fb_{msg_idx}_rul",
        )
        if st.button("Save Correction", key=f"fb_{msg_idx}_submit"):
            _submit_feedback(msg, "negative", correction, corrected_rul or None)
            st.session_state[fb_key] = "submitted"
            st.success(
                "Correction saved. Next response will reflect this.",
                icon=":material/edit:",
            )
            st.rerun()

    elif st.session_state[fb_key] == "submitted":
        st.info("Correction applied.", icon=":material/edit:")


def _submit_feedback(
    msg: dict,
    correction_type: str,
    correction_text: str,
    corrected_rul_days: float | None = None,
) -> None:
    """POST /v1/feedback to backend (fire-and-forget, no crash on failure).

    FeedbackRequest fields (from backend/schemas.py):
      session_id, equipment_id, recommendation_id, thumbs_up,
      correction (optional), corrected_risk_level (optional AlertSeverity)
    """
    thumbs_up = correction_type == "positive"
    # Map corrected_rul_days -> corrected_risk_level heuristic
    corrected_risk_level: str | None = None
    if not thumbs_up and corrected_rul_days is not None and corrected_rul_days > 0:
        if corrected_rul_days < 1:
            corrected_risk_level = "critical"
        elif corrected_rul_days < 7:
            corrected_risk_level = "high"
        elif corrected_rul_days < 30:
            corrected_risk_level = "medium"
        else:
            corrected_risk_level = "low"

    payload = {
        "session_id": st.session_state.get("session_id", ""),
        "equipment_id": msg.get("equipment_id", selected_asset_id),
        "recommendation_id": msg.get("recommendation_id", ""),
        "thumbs_up": thumbs_up,
        "correction": correction_text or None,
        "corrected_risk_level": corrected_risk_level,
    }
    safe_post("/v1/feedback", payload)


# ---------------------------------------------------------------------------
# Gold cached response for demo safety when backend offline.
# Shape matches the REAL ChatResponse from backend/schemas.py:
#   { session_id, equipment_id, recommendation: MaintenanceRecommendation,
#     agent_trace, latency_ms }
# MaintenanceRecommendation has: recommendation_id, asset_id, priority,
#   narrative_summary, cited_sources, action_steps, spares_procurement_warning,
#   parts_bill_of_materials, estimated_total_hours, diagnosis_report_id, ...
# ---------------------------------------------------------------------------
_GOLD_RESPONSE = {
    "session_id": "session-demo-gold",
    "equipment_id": "EAF-04",
    "latency_ms": 4200.0,
    "recommendation": {
        "recommendation_id": "REC-DEMO-GOLD-001",
        "asset_id": "EAF-04",
        "diagnosis_report_id": "DIAG-DEMO-001",
        "priority": "critical",
        "maintenance_type": "emergency",
        "estimated_rul_days_p10": 0.25,
        "estimated_rul_days_p50": 0.46,
        "estimated_rul_days_p90": 0.83,
        "degradation_index": 0.92,
        "narrative_summary": (
            "EAF-04 Electrode Cooling System: Critical failure pattern detected.\n\n"
            "The cooling manifold O-ring has degraded. Coolant flow is restricted. "
            "This has caused the electrode temperature to climb above the safe limit.\n\n"
            "Bearing wear accounts for most of the vibration increase. "
            "Thermal expansion accounts for the rest.\n\n"
            "The O-ring degraded faster than expected because lubrication intervals were too long.\n\n"
            "Steps:\n"
            "1. Inspect the electrode cooling manifold right now. Follow procedure BF-SOP-007 section 3.4.\n"
            "2. Confirm the spare SKF-6310-2RS1 is at the Jamshedpur warehouse (currently in stock).\n"
            "3. Replace the O-ring seal on the cooling manifold.\n"
            "4. After the repair, check vibration. Target: below 6 mm/s.\n\n"
            "Spare status: SKF-6310-2RS1 is in stock (2 units). If used, lead time to reorder is 14 days."
        ),
        "decision_summary_engineer": (
            "Bearing badly worn. Vibration is 53% above the safe limit. "
            "Electrode temperature is 1847 C — that is 47 C above the maximum safe operating temperature. "
            "The cooling manifold O-ring must be replaced before the next heat cycle."
        ),
        "decision_summary_supervisor": (
            "Emergency bearing and O-ring replacement needed on EAF-04. "
            "Estimated downtime: 3.5 hours. Cost if this fails unplanned: about 8 lakh. "
            "Spare part is in stock. Authorise the work order now."
        ),
        "cited_sources": [
            "SOP BF-SOP-007 3.4",
            "Incident Report #1847",
            "Sensor Summary T-12",
        ],
        "action_steps": [
            {
                "step_number": 1,
                "action": "Inspect electrode cooling manifold. Follow BF-SOP-007 section 3.4.",
                "sop_reference": "BF-SOP-007 3.4",
                "estimated_hours": 0.5,
                "assigned_to": "Maintenance Team Alpha",
                "parts_required": [],
            },
            {
                "step_number": 2,
                "action": "Confirm spare SKF-6310-2RS1 is at the Jamshedpur warehouse.",
                "sop_reference": None,
                "estimated_hours": 0.25,
                "assigned_to": "Stores",
                "parts_required": ["SKF-6310-2RS1"],
            },
            {
                "step_number": 3,
                "action": "Replace O-ring seal on the cooling manifold.",
                "sop_reference": "BF-SOP-007 3.4",
                "estimated_hours": 3.5,
                "assigned_to": "TECH-047",
                "parts_required": ["SKF-6310-2RS1", "SEAL-014"],
            },
            {
                "step_number": 4,
                "action": "After repair: check vibration. Target is below 6 mm/s.",
                "sop_reference": None,
                "estimated_hours": 0.25,
                "assigned_to": "Instrumentation",
                "parts_required": [],
            },
        ],
        "estimated_total_hours": 3.5,
        "parts_bill_of_materials": ["SKF-6310-2RS1", "SEAL-014"],
        "spares_procurement_warning": None,
        "cost_avoidance_inr": 825000.0,
        "process_related_defects": [
            "Lubrication intervals were too long — O-ring degraded faster than the design schedule.",
            "Irregular heat-cycle timing increased thermal stress on the cooling manifold.",
        ],
        "long_term_monitoring": [
            "Check bearing vibration every week. Compare against the baseline (below 6 mm/s).",
            "Run lubrication-oil particle analysis every quarter.",
            "Add EAF-04 to the monthly thermography route.",
            "Review the lubrication schedule. Shorten the interval by 30%.",
        ],
    },
    "agent_trace": [
        {"agent": "Supervisor", "node": "route", "latency_ms": 42, "model": "gemini-2.5-flash"},
        {"agent": "Diagnosis", "node": "retrieve+diagnose", "latency_ms": 1840, "model": "gemini-2.5-flash"},
        {"agent": "RCA", "node": "graph+gcm+5whys", "latency_ms": 2210, "model": "gemini-2.5-flash"},
        {"agent": "RUL", "node": "weibull_aft", "latency_ms": 380, "model": "gemini-2.5-flash"},
        {"agent": "Risk", "node": "wrps_score", "latency_ms": 290, "model": "gemini-2.5-flash"},
        {"agent": "Plan", "node": "two_pass_plan", "latency_ms": 1950, "model": "gemini-2.5-flash"},
    ],
}


# ---------------------------------------------------------------------------
# Chat message renderer
# ---------------------------------------------------------------------------
def _render_message(idx: int, msg: dict) -> None:
    """Render a single chat message with BLUF card and details expander."""
    role = msg.get("role", "user")

    with st.chat_message(role):
        if role == "user":
            st.markdown(msg.get("content", ""))
            return

        # assistant message
        rec = msg.get("_rec", {})

        if rec:
            # BLUF card (always visible)
            _render_bluf_card(rec)

            # Citation pills (below card, above expander)
            cited = msg.get("cited_sources", [])
            _render_citation_pills(cited)

            # Details expander
            # Pass agent_trace from the outer message dict into rec for the
            # technical details sub-section
            rec_with_trace = dict(rec)
            if "agent_trace" not in rec_with_trace or not rec_with_trace["agent_trace"]:
                rec_with_trace["agent_trace"] = msg.get("agent_trace", [])

            _render_details_expander(rec_with_trace, cited)
        else:
            # Fallback: render raw markdown if no structured data available
            st.markdown(msg.get("content", ""))

        # Spares warning (surfaced outside expander if critical)
        spares_warn = msg.get("spares_procurement_warning")
        if spares_warn:
            st.error(f"Procurement alert: {spares_warn}")

        # Feedback widget
        _render_feedback_widget(idx, msg)


# ---------------------------------------------------------------------------
# Empty state — no messages yet
# ---------------------------------------------------------------------------
messages = st.session_state.get("messages", [])

if not messages:
    st.markdown(
        "<div style='text-align:center;padding:4rem 1rem;'>"
        "<p style='font-size:0.8125rem;font-weight:600;color:#E8E8F2;"
        "margin-bottom:6px;'>Ask about any equipment</p>"
        "<p style='font-size:0.8125rem;color:#5E6080;max-width:380px;margin:0 auto;'>"
        "Example: <em>What is the status of EAF-04?</em><br>"
        "or: <em>When should Conveyor CONV-12 be serviced?</em>"
        "</p></div>",
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------------------------
# Render conversation history
# ---------------------------------------------------------------------------
for idx, msg in enumerate(messages):
    _render_message(idx, msg)


# ---------------------------------------------------------------------------
# Chat input
# ---------------------------------------------------------------------------
prompt = st.chat_input(
    "Describe equipment, ask about fault, request maintenance plan...",
    key="chat_input_main",
)

if prompt:
    # Add user message
    user_msg = {
        "role": "user",
        "content": prompt,
        "timestamp": datetime.utcnow().isoformat(),
    }
    messages.append(user_msg)
    st.session_state["messages"] = messages

    with st.chat_message("user"):
        st.markdown(prompt)

    # --- Call backend ---
    with st.chat_message("assistant"):
        with st.status("Routing to agents...", expanded=True) as status_box:
            st.markdown(
                f"<p style='font-size:0.8125rem;color:#9B9CB5;margin:0 0 6px;'>"
                f"Equipment: <code>{selected_asset_id}</code></p>"
                f"<p style='font-size:0.75rem;color:#5E6080;margin:0;'>"
                f"Diagnosis &#8594; RCA &#8594; RUL &#8594; Prioritization &#8594; Plan</p>",
                unsafe_allow_html=True,
            )

            payload = {
                "session_id": st.session_state.get("session_id", _new_session_id()),
                "query": prompt,
                "equipment_id": selected_asset_id,
            }

            backend_resp: dict | None = None
            try:
                client = get_client()
                resp = client.post("/v1/chat", json=payload, timeout=45.0)
                resp.raise_for_status()
                backend_resp = resp.json()
                status_box.update(label="Agents complete", state="complete", expanded=False)
            except Exception:
                status_box.update(label="Backend offline — using demo cache", state="error", expanded=False)
                st.warning(
                    "Backend offline — showing cached response for demo.",
                    icon=":material/cloud_off:",
                )
                backend_resp = _GOLD_RESPONSE

        # Extract recommendation from ChatResponse
        # ChatResponse shape: {session_id, equipment_id, recommendation: {...}, agent_trace, latency_ms}
        rec: dict = backend_resp.get("recommendation") or {}

        # Propagate agent_trace from outer response into rec for the technical details section
        if "agent_trace" not in rec or not rec.get("agent_trace"):
            rec["agent_trace"] = backend_resp.get("agent_trace", [])

        # Stream only the one-line headline (keeps the chat feel) — the brief
        # answer is the BLUF card below; the full summary lives in the expander.
        narrative = rec.get("narrative_summary", "") or "No response received."
        headline = (narrative.split("\n", 1)[0].strip() or narrative[:160])
        streamed_content = st.write_stream(_stream_text(headline, delay_ms=6))

        # Render BLUF card — the brief, scannable answer
        _render_bluf_card(rec)

        # Agent pipeline — compact view shows agentic work after BLUF
        _pipeline_trace = backend_resp.get("agent_trace", [])
        if _pipeline_trace:
            with st.expander("Agent pipeline — how the answer was produced", expanded=True):
                render_agent_pipeline(_pipeline_trace, compact=True)

        # Citation pills — cited_sources is list[str] chunk IDs in the real schema
        cited_source_ids: list = rec.get("cited_sources", [])
        cited_sources_display: list[dict] = [
            {"label": f"[{i + 1}]", "doc_name": src if isinstance(src, str) else str(src)}
            for i, src in enumerate(cited_source_ids)
        ]
        _render_citation_pills(cited_sources_display)

        # Details expander
        _render_details_expander(rec, cited_sources_display)

        # Spares warning surfaced outside expander if present
        spares_warn: str | None = rec.get("spares_procurement_warning")
        if spares_warn:
            st.error(f"Procurement alert: {spares_warn}")

        # Build assistant message record for history
        assistant_msg: dict = {
            "role": "assistant",
            "content": narrative,
            "equipment_id": backend_resp.get("equipment_id", selected_asset_id),
            "recommendation_id": rec.get("recommendation_id", ""),
            "cited_sources": cited_sources_display,
            "spares_procurement_warning": spares_warn,
            "agent_trace": backend_resp.get("agent_trace", []),
            "timestamp": datetime.utcnow().isoformat(),
            # Store the full rec dict so _render_message can re-render
            # the BLUF card and expander on history replay
            "_rec": rec,
        }

        # Feedback widget (initial state = neutral)
        _render_feedback_widget(len(messages), assistant_msg)

        messages.append(assistant_msg)
        st.session_state["messages"] = messages
