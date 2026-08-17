"""VULCAN · EDITH — Chat (the agentic front door).

Streamlit entry point. An engineer asks natural-language questions; EDITH answers
with inline [N] citations, a RUL + risk badge, and an expandable REASONING TRACE
(FR4 show-your-work). Multi-turn focus is preserved across the session (FR3).
The demo chips let a judge drive the whole thing without typing.

    streamlit run vulcan/ui/app.py
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# --- import bootstrap: make `vulcan` importable when run as a bare script ---
# `streamlit run .../vulcan/ui/app.py` executes this file directly, so the
# package root (the dir CONTAINING the `vulcan/` package) must be on sys.path.
_PKG_ROOT = Path(__file__).resolve().parents[2]   # .../vulcan/  (contains vulcan/)
if str(_PKG_ROOT) not in sys.path:
    sys.path.insert(0, str(_PKG_ROOT))
os.environ.pop("ANTHROPIC_API_KEY", None)          # belt-and-braces: keyless only

import streamlit as st  # noqa: E402

from vulcan.ui import _shared as S  # noqa: E402


def main() -> None:
    S.page_setup("EDITH · Chat", icon="⚡")

    st.markdown("### ⚡ EDITH — ask the maintenance wizard")
    st.caption(
        "Natural-language diagnosis, root-cause, remaining-useful-life, risk & "
        "spare-procurement — grounded in the plant dataset, every claim cited."
    )

    # ---- session state ----
    if "messages" not in st.session_state:
        st.session_state.messages = []          # list[dict(role, content, turn)]
    if "pending_query" not in st.session_state:
        st.session_state.pending_query = None

    # ---- demo chips (cold-start: judge clicks, doesn't type) ----
    if not st.session_state.messages:
        st.markdown("**Try one of these (real dataset scenarios):**")
        cols = st.columns(len(S.DEMO_CHIPS))
        for col, chip in zip(cols, S.DEMO_CHIPS):
            if col.button(chip["label"], width="stretch", key="chip_" + chip["label"]):
                st.session_state.pending_query = chip["query"]
                st.rerun()
        st.divider()

    # ---- render history ----
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"], avatar="⚡" if msg["role"] == "assistant" else "👷"):
            st.markdown(msg["content"])
            if msg["role"] == "assistant" and msg.get("turn"):
                _render_assistant_extras(msg["turn"])

    # ---- input (chat box OR a pending chip click) ----
    typed = st.chat_input("Describe a symptom, ask about an asset, or follow up…")
    query = typed or st.session_state.pending_query
    st.session_state.pending_query = None

    if query:
        _handle_turn(query)


def _handle_turn(query: str) -> None:
    """Run one EDITH turn and append it to the transcript."""
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user", avatar="👷"):
        st.markdown(query)

    with st.chat_message("assistant", avatar="⚡"):
        with st.spinner("EDITH is reasoning over the plant data…"):
            turn = S.safe_handle_query(query, session_id="chat")
        if turn is None:
            return
        answer = getattr(turn, "answer", "_no answer_")
        st.markdown(answer)
        _render_assistant_extras(turn)

    # persist a compact mirror so reruns redraw without re-calling the core
    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
        "turn": _turn_view(turn),
    })


def _turn_view(turn) -> dict:
    """A lightweight, picklable view of a TurnResult for redraw + feedback."""
    return {
        "asset_id": getattr(turn, "asset_id", None),
        "scenario_id": getattr(turn, "scenario_id", None),
        "intent": getattr(turn, "intent", None),
        "risk_band": getattr(turn, "risk_band", None),
        "rul": getattr(turn, "rul", None),
        "sources": getattr(turn, "sources", []) or [],
        "confidence": getattr(turn, "confidence", "unverified"),
        "faithfulness": getattr(turn, "faithfulness", None),
        "llm_rung": getattr(turn, "llm_rung", "?"),
        "llm_latency_ms": getattr(turn, "llm_latency_ms", 0),
        "unfaithful": getattr(turn, "unfaithful", []) or [],
        "trace": getattr(turn, "trace", None).to_dict() if getattr(turn, "trace", None) else None,
    }


class _Obj:
    """Tiny attr shim so the renderers accept both a live TurnResult and the
    dict view stored in session_state."""
    def __init__(self, d: dict): self.__dict__.update(d)


def _render_assistant_extras(turn) -> None:
    """Badges (risk + RUL + confidence) + citations + the trace expander."""
    tv = turn if isinstance(turn, dict) else _turn_view(turn)

    # --- badges row ---
    c1, c2, c3 = st.columns([1.2, 1.4, 2.2])
    with c1:
        st.markdown("**Risk**  \n" + S.risk_badge(tv.get("risk_band")), unsafe_allow_html=True)
    with c2:
        rul = tv.get("rul") or {}
        if rul and rul.get("rul_cycles") is not None:
            st.markdown(
                f"**RUL**  \n`{rul.get('rul_cycles')}` cycles "
                f"(~{rul.get('rul_days_estimate')} d)"
            )
        else:
            st.markdown("**RUL**  \n_n/a_")
    with c3:
        asset = tv.get("asset_id") or "—"
        scn = tv.get("scenario_id")
        st.markdown(f"**Asset**  \n`{asset}`" + (f" · scenario `{scn}`" if scn else ""))

    st.caption(S.confidence_caption(_Obj(tv)))

    # --- citations ---
    S.render_citations(tv.get("sources", []))

    # --- the show-your-work expander (FR4) ---
    trace = tv.get("trace")
    if trace:
        with st.expander("🧠 Show EDITH's reasoning (trace + sources)", expanded=False):
            S.render_trace(_TraceView(trace))

    # --- engineer-in-the-loop feedback (FR6) ---
    if tv.get("asset_id"):
        _feedback_widget(tv)


def _feedback_widget(tv: dict) -> None:
    """Inline FR6: thumbs + correction that nudges the priority weight live."""
    asset = tv["asset_id"]
    scn = tv.get("scenario_id")
    key = f"fb_{asset}_{scn}_{abs(hash(tv.get('confidence',''))) % 99999}"
    with st.expander("👍/👎 Was this right? (teach EDITH — FR6)", expanded=False):
        c1, c2 = st.columns(2)
        verdict = None
        if c1.button("👍 Confirm diagnosis", key=key + "_up", width="stretch"):
            verdict = "confirm"
        if c2.button("👎 Wrong / re-prioritise", key=key + "_down", width="stretch"):
            verdict = "correct"
        if verdict:
            try:
                store = S.get_feedback_store()
                res = store.submit(asset_id=asset, scenario_id=scn, verdict=verdict,
                                   risk_band_at_time=tv.get("risk_band"),
                                   engineer="demo-engineer")
                d = res.to_dict()
                st.success(
                    f"Recorded. Priority weight for `{asset}` moved "
                    f"{d['weight_before']} → {d['weight_after']} ({d['direction']} "
                    f"{d['delta']:+}). This re-weights future risk scoring — no retrain.",
                    icon="✅",
                )
            except Exception as exc:  # noqa: BLE001
                st.warning(f"Could not record feedback ({type(exc).__name__}).")


class _TraceView:
    """Adapt a trace.to_dict() back into the duck-type render_trace expects."""
    def __init__(self, d: dict):
        self.query = d.get("query", "")
        self._total = d.get("total_latency_ms", 0)
        self.steps = [_Obj(s) for s in d.get("steps", [])]

    def total_latency_ms(self) -> int:
        return self._total


if __name__ == "__main__" or True:
    # Streamlit executes the module top-to-bottom; calling main() unconditionally
    # is the idiomatic entry for `streamlit run`.
    main()
