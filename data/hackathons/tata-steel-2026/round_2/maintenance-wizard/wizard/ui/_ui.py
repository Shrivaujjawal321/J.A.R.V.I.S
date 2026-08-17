"""
wizard.ui._ui
=============
Dark command-center design system for Maintenance Wizard.

Near-black intelligence console. Single accent (electric blue).
Status colors are the only other color in the UI. Depth via luminance
stepping. ISA-101 neutral-base status semantics preserved.

Call inject_global_css() as the first st.* call in every view and in app.py.
"""

from __future__ import annotations

import streamlit as st

# ---------------------------------------------------------------------------
# CSS injection
# ---------------------------------------------------------------------------

_CSS = """
<style>

/* ===== DESIGN TOKENS ===== */
:root {
    --bg-base:        #09090F;
    --bg-surface:     #0F1117;
    --bg-elevated:    #161B27;
    --bg-overlay:     #1E2638;

    --border-subtle:  rgba(255,255,255,0.07);
    --border-default: rgba(255,255,255,0.11);
    --border-strong:  rgba(255,255,255,0.20);

    --text-primary:   #E8E8F2;
    --text-secondary: #9B9CB5;
    --text-muted:     #5E6080;
    --text-mono:      #A0A5C0;

    --accent:         #3B82F6;
    --accent-dim:     rgba(59,130,246,0.12);
    --accent-glow:    rgba(59,130,246,0.25);

    --status-critical: #F87171;
    --status-high:     #FB923C;
    --status-warning:  #FBBF24;
    --status-normal:   #34D399;
    --status-info:     #3B82F6;
    --status-idle:     #5E6080;

    --status-critical-bg: rgba(248,113,113,0.12);
    --status-high-bg:     rgba(251,146,60,0.12);
    --status-warning-bg:  rgba(251,191,36,0.12);
    --status-normal-bg:   rgba(52,211,153,0.12);
    --status-info-bg:     rgba(59,130,246,0.12);
    --status-idle-bg:     rgba(94,96,128,0.12);

    --radius-card:  12px;
    --radius-chip:  999px;

    --transition-fast: 150ms ease-out;
    --transition-base: 200ms ease-out;
}

/* ===== HIDE ALL DEFAULT STREAMLIT CHROME ===== */
#MainMenu                            { display: none !important; }
/* Keep the header element (it hosts the sidebar expand arrow) but make it
   invisible as a bar. Hiding `header` outright removes the only control that
   re-opens a collapsed sidebar — so we make it transparent instead. */
header[data-testid="stHeader"]       { background: transparent !important; box-shadow: none !important; }
/* The sidebar collapse / expand control MUST stay visible so the sidebar can
   always be re-opened on narrow windows.
   IMPORTANT: stExpandSidebarButton lives deep inside stToolbar.
   We CANNOT use display:none on stToolbar or any of its container descendants —
   Streamlit's JS toggles those containers when the sidebar collapses.
   Instead: make stToolbar a transparent zero-height overlay (overflow:visible),
   and hide only the leaf items we don't want (deploy button, status widget,
   toolbar action buttons) using visibility+opacity so JS-driven display toggling
   on ancestor divs still works. */
[data-testid="stToolbar"] {
    background: transparent !important;
    box-shadow: none !important;
    border: none !important;
    height: 0 !important;
    min-height: 0 !important;
    overflow: visible !important;
    padding: 0 !important;
}
/* Hide leaf decorative items without touching structural containers */
[data-testid="stToolbar"] [data-testid="stStatusWidget"],
[data-testid="stToolbar"] .stToolbarActions,
[data-testid="stToolbar"] [data-testid="stToolbarActionButton"],
[data-testid="stToolbar"] [data-testid="stDeployButton"],
[data-testid="stToolbar"] [class*="stToolbarActions"] { visibility: hidden !important; pointer-events: none !important; }
/* But keep the sidebar expand/collapse controls fully interactive */
[data-testid="stSidebarCollapsedControl"],
[data-testid="stSidebarCollapseButton"],
[data-testid="stExpandSidebarButton"],
[data-testid="collapsedControl"]     { visibility: visible !important; opacity: 1 !important; z-index: 1000 !important; pointer-events: auto !important; }
footer                               { display: none !important; }
.stDeployButton                      { display: none !important; }
.stAppDeployButton                   { display: none !important; }
[data-testid="stStatusWidget"]       { display: none !important; }
[data-testid="stDecoration"]         { display: none !important; }
#stDecoration                        { display: none !important; }

/* ===== GLOBAL BASE ===== */
html, body, [class*="css"] {
    font-family: 'IBM Plex Sans', Inter, system-ui, sans-serif !important;
    background-color: var(--bg-base) !important;
    color: var(--text-primary) !important;
}

/* ===== CUSTOM SCROLLBAR ===== */
::-webkit-scrollbar              { width: 4px; height: 4px; }
::-webkit-scrollbar-track        { background: var(--bg-base); }
::-webkit-scrollbar-thumb        { background: var(--border-default); border-radius: 2px; }
::-webkit-scrollbar-thumb:hover  { background: var(--accent); }

/* ===== LAYOUT ===== */
.block-container {
    padding-top:    1.5rem !important;
    padding-bottom: 2rem !important;
    padding-left:   2rem !important;
    padding-right:  2rem !important;
    max-width:      1280px !important;
}

/* ===== TYPOGRAPHY ===== */
h1 {
    font-size: 1.25rem !important;
    font-weight: 600 !important;
    letter-spacing: -0.01em !important;
    color: var(--text-primary) !important;
    margin-bottom: 0.25rem !important;
    line-height: 1.3 !important;
}
h2 {
    font-size: 1rem !important;
    font-weight: 600 !important;
    letter-spacing: -0.005em !important;
    color: var(--text-primary) !important;
    margin-top: 1.5rem !important;
    margin-bottom: 0.5rem !important;
}
h3 {
    font-size: 0.875rem !important;
    font-weight: 600 !important;
    color: var(--text-primary) !important;
}
p {
    color: var(--text-primary) !important;
}

/* Mono text */
code, pre, [data-testid="stCode"],
.mono, .asset-id, .sensor-value {
    font-family: 'IBM Plex Mono', JetBrains Mono, monospace !important;
    color: var(--text-mono) !important;
}

/* ===== SIDEBAR ===== */
[data-testid="stSidebar"] {
    background-color: var(--bg-surface) !important;
    border-right: 1px solid var(--border-subtle) !important;
}
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span:not([style]),
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] div.stMarkdown p {
    color: var(--text-primary) !important;
}
[data-testid="stSidebar"] .stMarkdown a {
    color: #60A5FA !important;
}
[data-testid="stSidebar"] [data-testid="stMetricValue"] > div {
    color: var(--text-primary) !important;
    font-size: 1.4rem !important;
    font-weight: 700 !important;
}
[data-testid="stSidebar"] [data-testid="stMetricLabel"] > div {
    color: var(--text-secondary) !important;
    font-size: 0.6875rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.06em !important;
}
[data-testid="stSidebar"] [data-testid="stMetricDelta"] > div {
    color: var(--status-normal) !important;
}
[data-testid="stSidebar"] [data-testid="stMetric"] {
    background-color: var(--bg-elevated) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: 10px !important;
    padding: 0.875rem 1rem !important;
}
[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p {
    color: var(--text-muted) !important;
}
[data-testid="stSidebarNav"] li[aria-selected="true"] {
    background-color: var(--accent-dim) !important;
    border-radius: 8px !important;
}
[data-testid="stSidebarNav"] li[aria-selected="true"] span {
    color: var(--accent) !important;
    font-weight: 600 !important;
}
[data-testid="stSidebarNav"] li span {
    color: var(--text-secondary) !important;
    font-size: 0.875rem !important;
}
[data-testid="stSidebarNav"] li:hover {
    background-color: var(--bg-overlay) !important;
    border-radius: 8px !important;
}

/* ===== METRIC TILES (main area) ===== */
[data-testid="stMetric"] {
    background-color: var(--bg-elevated) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: var(--radius-card) !important;
    padding: 1rem 1.25rem !important;
}
[data-testid="stMetricLabel"] > div {
    font-size: 0.6875rem !important;
    font-weight: 600 !important;
    color: var(--text-muted) !important;
    text-transform: uppercase !important;
    letter-spacing: 0.07em !important;
}
[data-testid="stMetricValue"] > div {
    font-size: 1.75rem !important;
    font-weight: 700 !important;
    color: var(--text-primary) !important;
    line-height: 1.1 !important;
    letter-spacing: -0.02em !important;
}
[data-testid="stMetricDelta"] > div {
    font-size: 0.75rem !important;
    font-weight: 500 !important;
}

/* ===== BUTTONS ===== */
.stButton > button {
    font-family: 'IBM Plex Sans', sans-serif !important;
    font-weight: 500 !important;
    font-size: 0.875rem !important;
    border-radius: 8px !important;
    padding: 0.4rem 1rem !important;
    min-height: 36px !important;
    transition: all var(--transition-fast) !important;
    background-color: var(--bg-elevated) !important;
    border: 1px solid var(--border-default) !important;
    color: var(--text-primary) !important;
}
.stButton > button:hover {
    background-color: var(--bg-overlay) !important;
    border-color: var(--border-strong) !important;
    transform: translateY(-1px) !important;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #3B82F6, #2563EB) !important;
    border-color: transparent !important;
    color: #FFFFFF !important;
}
.stButton > button[kind="primary"]:hover {
    box-shadow: 0 0 16px var(--accent-glow) !important;
    border-color: transparent !important;
}
.stDownloadButton > button {
    background-color: var(--bg-elevated) !important;
    border: 1px solid var(--border-default) !important;
    color: var(--text-primary) !important;
    border-radius: 8px !important;
    font-size: 0.875rem !important;
    font-weight: 500 !important;
}
.stLinkButton > a {
    background-color: var(--bg-elevated) !important;
    border: 1px solid var(--border-default) !important;
    color: var(--text-primary) !important;
    border-radius: 8px !important;
    font-size: 0.875rem !important;
    font-weight: 500 !important;
    text-decoration: none !important;
}

/* ===== INPUTS / SELECTS ===== */
[data-testid="stTextInput"] input,
[data-testid="stSelectbox"] > div > div,
[data-testid="stMultiSelect"] > div > div,
[data-testid="stDateInput"] input,
[data-testid="stTextArea"] textarea {
    background-color: var(--bg-elevated) !important;
    border: 1px solid var(--border-default) !important;
    border-radius: 8px !important;
    color: var(--text-primary) !important;
    font-size: 0.875rem !important;
}
[data-testid="stTextInput"] input:focus,
[data-testid="stTextArea"] textarea:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 2px var(--accent-dim) !important;
    outline: none !important;
}

/* ===== CHAT INPUT ===== */
[data-testid="stChatInput"] textarea {
    background-color: var(--bg-elevated) !important;
    border: 1px solid var(--border-default) !important;
    border-radius: 10px !important;
    color: var(--text-primary) !important;
    font-family: 'IBM Plex Sans', sans-serif !important;
    font-size: 0.875rem !important;
    transition: border-color var(--transition-fast) !important;
}
[data-testid="stChatInput"] textarea:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 2px var(--accent-dim) !important;
}
[data-testid="stChatMessage"] {
    border-radius: 10px !important;
    margin-bottom: 0.5rem !important;
    background: transparent !important;
}

/* ===== CONTAINERS / CARDS ===== */
[data-testid="stVerticalBlock"] > [data-testid="stVerticalBlock"][data-border="true"],
[data-testid="stVerticalBlockBorderWrapper"] {
    background-color: var(--bg-elevated) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: var(--radius-card) !important;
    padding: 1rem 1.25rem !important;
}

/* ===== DATAFRAME / TABLE ===== */
[data-testid="stDataFrame"] {
    border: 1px solid var(--border-subtle) !important;
    border-radius: 10px !important;
    overflow: hidden !important;
}
[data-testid="stDataFrame"] table {
    font-size: 0.8125rem !important;
    background-color: var(--bg-surface) !important;
}
[data-testid="stDataFrame"] thead th {
    font-size: 0.6875rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.06em !important;
    color: var(--text-muted) !important;
    background-color: var(--bg-elevated) !important;
    border-bottom: 1px solid var(--border-subtle) !important;
}
[data-testid="stDataFrame"] tbody tr:hover {
    background-color: var(--bg-overlay) !important;
}
[data-testid="stDataFrame"] tbody td {
    color: var(--text-primary) !important;
    border-color: var(--border-subtle) !important;
}

/* ===== EXPANDER ===== */
[data-testid="stExpander"] {
    background-color: var(--bg-elevated) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: 10px !important;
    overflow: hidden !important;
}
[data-testid="stExpander"] summary,
.streamlit-expanderHeader {
    font-weight: 600 !important;
    font-size: 0.875rem !important;
    color: var(--text-primary) !important;
    background-color: var(--bg-elevated) !important;
    padding: 0.75rem 1rem !important;
}
[data-testid="stExpander"] .streamlit-expanderContent {
    background-color: var(--bg-elevated) !important;
    border-top: 1px solid var(--border-subtle) !important;
}

/* ===== STATUS COMPONENT (st.status) ===== */
[data-testid="stExpander"][data-type="status"] {
    background-color: var(--bg-elevated) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: 10px !important;
}

/* ===== ALERTS (info/warning/error/success) ===== */
[data-testid="stAlert"] {
    border-radius: 8px !important;
    border-left-width: 3px !important;
    border-left-style: solid !important;
    font-size: 0.875rem !important;
    padding: 0.75rem 1rem !important;
}
[data-testid="stAlert"][data-type="success"] {
    border-left-color: var(--status-normal) !important;
    background-color: var(--status-normal-bg) !important;
    color: var(--text-primary) !important;
}
[data-testid="stAlert"][data-type="info"] {
    border-left-color: var(--status-info) !important;
    background-color: var(--status-info-bg) !important;
    color: var(--text-primary) !important;
}
[data-testid="stAlert"][data-type="warning"] {
    border-left-color: var(--status-warning) !important;
    background-color: var(--status-warning-bg) !important;
    color: var(--text-primary) !important;
}
[data-testid="stAlert"][data-type="error"] {
    border-left-color: var(--status-critical) !important;
    background-color: var(--status-critical-bg) !important;
    color: var(--text-primary) !important;
}

/* ===== DIVIDER ===== */
hr {
    border: none !important;
    border-top: 1px solid var(--border-subtle) !important;
    margin: 1rem 0 !important;
}

/* ===== CAPTION ===== */
[data-testid="stCaptionContainer"] p {
    font-size: 0.6875rem !important;
    color: var(--text-muted) !important;
    line-height: 1.4 !important;
}

/* ===== PROGRESS BAR ===== */
[data-testid="stProgressBar"] > div {
    background-color: var(--bg-elevated) !important;
    border-radius: 999px !important;
}
[data-testid="stProgressBar"] > div > div {
    background: linear-gradient(90deg, var(--accent), #60A5FA) !important;
    border-radius: 999px !important;
}

/* ===== CHECKBOX / RADIO / LABEL ===== */
[data-testid="stCheckbox"] label,
[data-testid="stRadio"] label {
    color: var(--text-primary) !important;
    font-size: 0.875rem !important;
}

/* ===== CODE BLOCKS ===== */
[data-testid="stCode"] {
    background-color: var(--bg-elevated) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: 8px !important;
}

/* ===== STATUS BADGE CLASSES (dark glass) ===== */
.mw-badge {
    display: inline-block;
    border-radius: var(--radius-chip);
    padding: 2px 10px;
    font-family: 'IBM Plex Sans', sans-serif;
    font-size: 0.6875rem;
    font-weight: 600;
    line-height: 1.6;
    white-space: nowrap;
    border: 1px solid transparent;
    letter-spacing: 0.03em;
}
.mw-badge-normal   {
    background: var(--status-normal-bg);
    color: var(--status-normal);
    border-color: rgba(52,211,153,0.25);
}
.mw-badge-info     {
    background: var(--status-info-bg);
    color: var(--status-info);
    border-color: rgba(59,130,246,0.25);
}
.mw-badge-warning  {
    background: var(--status-warning-bg);
    color: var(--status-warning);
    border-color: rgba(251,191,36,0.25);
}
.mw-badge-high     {
    background: var(--status-high-bg);
    color: var(--status-high);
    border-color: rgba(251,146,60,0.25);
}
.mw-badge-critical {
    background: var(--status-critical-bg);
    color: var(--status-critical);
    border-color: rgba(248,113,113,0.25);
}
.mw-badge-idle     {
    background: var(--status-idle-bg);
    color: var(--status-idle);
    border-color: rgba(94,96,128,0.25);
}

/* ===== EQUIPMENT ID / MONO INLINE ===== */
.mw-id {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.8125rem;
    background: var(--bg-overlay);
    border: 1px solid var(--border-subtle);
    border-radius: 4px;
    padding: 1px 6px;
    color: var(--text-mono);
}

/* ===== STALE DATA INDICATOR ===== */
.mw-stale          { opacity: 0.55; }
.mw-stale-badge    {
    display: inline-block;
    font-size: 0.6875rem;
    font-weight: 600;
    color: var(--text-muted);
    background: var(--bg-elevated);
    border: 1px solid var(--border-subtle);
    border-radius: 4px;
    padding: 1px 6px;
}

/* ===== AGENT PIPELINE ===== */
.mw-pipeline {
    display: flex;
    flex-direction: column;
    gap: 0;
    font-family: 'IBM Plex Sans', sans-serif;
    max-width: 100%;
    overflow: hidden;
}
.mw-pipeline-step    { display: flex; flex-direction: column; }
.mw-pipeline-row {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 10px 14px;
    border: 1px solid var(--border-subtle);
    border-radius: 10px;
    min-width: 0;
    transition: border-color var(--transition-base), background-color var(--transition-base);
}
.mw-pipeline-row--pending { background: rgba(9,9,15,0.5); border-color: var(--border-subtle); }
.mw-pipeline-row--running { background: rgba(59,130,246,0.07); border-color: rgba(59,130,246,0.35); }
.mw-pipeline-row--done    { background: var(--bg-elevated); border-color: var(--border-subtle); }
.mw-pipeline-row--failed  { background: rgba(248,113,113,0.07); border-color: rgba(248,113,113,0.3); }

.mw-pipeline-dot           { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }
.mw-pipeline-dot--pending  { background: var(--status-idle); }
.mw-pipeline-dot--running  { background: var(--accent); animation: mw-pulse 1.4s ease-in-out infinite; }
.mw-pipeline-dot--done     { background: var(--status-normal); }
.mw-pipeline-dot--failed   { background: var(--status-critical); }

.mw-pipeline-name {
    font-weight: 600;
    font-size: 0.875rem;
    flex: 1;
    color: var(--text-primary);
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    min-width: 0;
}
.mw-pipeline-sub  {
    font-size: 0.75rem;
    color: var(--text-muted);
    margin-top: 1px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}
.mw-pipeline-latency {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.72rem;
    color: var(--text-muted);
    margin-left: auto;
    flex-shrink: 0;
}
.mw-pipeline-connector {
    width: 2px;
    height: 14px;
    margin-left: 18px;
    background: linear-gradient(to bottom, var(--border-subtle), transparent);
}

@keyframes mw-pulse {
    0%, 100% { box-shadow: 0 0 0 0 rgba(59,130,246,0.5); }
    50%       { box-shadow: 0 0 0 6px rgba(59,130,246,0); }
}

/* ===== REDUCED MOTION ===== */
@media (prefers-reduced-motion: reduce) {
    .mw-pipeline-dot--running { animation: none !important; }
    .stButton > button        { transition: none !important; }
    .stButton > button:hover  { transform: none !important; }
}

</style>
"""


def inject_global_css() -> None:
    """
    Inject the design system CSS.
    Must be called as the first st.* call in every view file and in app.py.
    """
    st.markdown(_CSS, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Status helpers
# ---------------------------------------------------------------------------

def _status_color(status: str) -> str:
    return {
        "normal":   "#34D399",
        "info":     "#3B82F6",
        "warning":  "#FBBF24",
        "high":     "#FB923C",
        "critical": "#F87171",
        "idle":     "#5E6080",
    }.get(status, "#5E6080")


def severity_to_variant(severity: str) -> str:
    """Map CRITICAL/HIGH/MEDIUM/LOW/HEALTHY/NORMAL to badge variant string."""
    return {
        "CRITICAL": "critical",
        "HIGH":     "high",
        "MEDIUM":   "warning",
        "WARNING":  "warning",
        "LOW":      "info",
        "NORMAL":   "normal",
        "HEALTHY":  "normal",
        "IDLE":     "idle",
        "STOPPED":  "idle",
    }.get(severity.upper(), "idle")


# ---------------------------------------------------------------------------
# Component helpers
# ---------------------------------------------------------------------------

def status_badge(level: str, label: str) -> str:
    """
    Return an HTML badge string (no emoji).
    level: normal | info | warning | high | critical | idle
    label: display text
    Caller must pass unsafe_allow_html=True to st.markdown.
    """
    variant = level if level in (
        "normal", "info", "warning", "high", "critical", "idle"
    ) else severity_to_variant(level)
    return f'<span class="mw-badge mw-badge-{variant}">{label}</span>'


def asset_id(text: str) -> str:
    """Return a monospace-styled equipment ID span."""
    return f'<span class="mw-id">{text}</span>'


def kpi_tile(title: str, value: str, subtitle: str = "", status: str = "idle") -> None:
    """
    Render a dark glass KPI card with top-border status accent.
    No emoji — color + text carry the status signal.
    status: normal | info | warning | high | critical | idle
    """
    accent = _status_color(status)
    sub_html = (
        f"<p style='margin:4px 0 0;font-size:0.72rem;color:#5E6080;"
        f"line-height:1.3;'>{subtitle}</p>"
    ) if subtitle else "<!-- -->"
    st.markdown(
        f"""<div style="
            background:#161B27;
            border:1px solid rgba(255,255,255,0.07);
            border-top:2px solid {accent};
            border-radius:12px;
            padding:1rem 1.25rem;
            margin-bottom:0.5rem;
        ">
          <p style="margin:0 0 6px;font-size:0.6875rem;font-weight:600;
                    color:#5E6080;text-transform:uppercase;letter-spacing:0.07em;">
              {title}
          </p>
          <p style="margin:0;font-size:1.75rem;font-weight:700;
                    color:#E8E8F2;line-height:1.1;letter-spacing:-0.02em;">
              {value}
          </p>
          {sub_html}
        </div>""",
        unsafe_allow_html=True,
    )


def render_hero_header(
    title: str,
    subtitle: str = "",
    badge: str = "",
    accent_color: str = "#3B82F6",
) -> None:
    """
    Dark gradient hero header for page tops.
    Replaces the plain page_header() for premium presentation.
    """
    badge_html = "<!-- -->"
    if badge:
        badge_html = (
            f"<span style='background:rgba(59,130,246,0.12);"
            f"color:#60A5FA;border:1px solid rgba(59,130,246,0.25);"
            f"padding:3px 10px;border-radius:999px;font-size:0.6875rem;"
            f"font-weight:600;letter-spacing:0.08em;text-transform:uppercase;"
            f"margin-bottom:10px;display:inline-block;'>{badge}</span>"
        )

    sub_html = (
        f"<p style='margin:4px 0 0;font-size:0.875rem;color:#5E6080;"
        f"line-height:1.5;'>{subtitle}</p>"
    ) if subtitle else "<!-- -->"

    # Parse accent color to RGB for glow
    try:
        ac = accent_color.lstrip("#")
        r, g, b = int(ac[0:2], 16), int(ac[2:4], 16), int(ac[4:6], 16)
    except Exception:
        r, g, b = 59, 130, 246

    st.markdown(f"""
<div style="
    background: linear-gradient(135deg, #0F1117 0%, #161B27 60%, rgba({r},{g},{b},0.08) 100%);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 16px;
    padding: 1.75rem 2rem;
    margin-bottom: 1.25rem;
    position: relative;
    overflow: hidden;
">
    <div style="
        position:absolute;top:-80px;right:-60px;
        width:300px;height:300px;
        background:radial-gradient(circle,rgba({r},{g},{b},0.12) 0%,transparent 70%);
        border-radius:50%;pointer-events:none;
    "></div>
    {badge_html}
    <h1 style="
        font-family:'IBM Plex Sans',sans-serif;
        font-size:1.375rem !important;
        font-weight:700 !important;
        color:#E8E8F2 !important;
        margin:{('8px 0 0' if badge else '0 0 0')} !important;
        letter-spacing:-0.015em;
        line-height:1.2;
    ">{title}</h1>
    {sub_html}
</div>
""", unsafe_allow_html=True)


def page_header(title: str, subtitle: str = "") -> None:
    """
    Backwards-compatible alias. Delegates to render_hero_header.
    """
    render_hero_header(title, subtitle)


def render_section_header(title: str, caption: str = "") -> None:
    """
    Lightweight inline section header — smaller than hero, no gradient.
    Used for Dashboard sections (RUL, Health Trend, Sensor Detail).
    """
    cap_html = (
        f"<p style='margin:2px 0 0;font-size:0.6875rem;color:#5E6080;"
        f"line-height:1.4;'>{caption}</p>"
    ) if caption else ""
    st.markdown(
        f"<div style='margin:1.5rem 0 0.75rem;'>"
        f"<p style='margin:0;font-size:0.875rem;font-weight:600;color:#E8E8F2;"
        f"letter-spacing:-0.005em;'>{title}</p>{cap_html}</div>",
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Agent pipeline renderer
# ---------------------------------------------------------------------------

_AGENT_DISPLAY_NAMES: dict[str, str] = {
    "supervisor":  "Supervisor",
    "route":       "Supervisor",
    "diagnosis":   "Diagnosis",
    "rca":         "Root Cause Analysis",
    "rul":         "Remaining Useful Life",
    "risk":        "Risk Prioritization",
    "plan":        "Maintenance Plan",
    "report":      "Report Writer",
}

_AGENT_NODE_LABELS: dict[str, str] = {
    "route":               "query routing",
    "retrieve+diagnose":   "sensor data + RAG retrieve",
    "graph+gcm+5whys":     "causal graph + 5-whys",
    "weibull_aft":         "Weibull AFT model",
    "wrps_score":          "risk prioritization score",
    "two_pass_plan":       "2-pass maintenance plan",
}


def render_agent_pipeline(
    trace: list,
    compact: bool = False,
) -> None:
    """
    Render the agent execution trace as a dark vertical pipeline stepper.

    trace: list of dicts, each with optional keys:
        agent       str   e.g. "Diagnosis"
        node        str   e.g. "retrieve+diagnose"
        latency_ms  int   e.g. 1840
        model       str   e.g. "gemini-2.5-flash"
        cache_hit   bool  optional

    compact=True: omit model sub-line, reduce padding — for expanders.
    """
    if not trace:
        return

    total_ms = 0
    for n in trace:
        lms = n.get("latency_ms")
        if isinstance(lms, (int, float)):
            total_ms += int(lms)

    total_label = f"{total_ms / 1000:.1f}s" if total_ms > 0 else ""

    header_html = ""
    if total_label and not compact:
        header_html = (
            f"<div style='display:flex;align-items:center;gap:8px;margin-bottom:10px;'>"
            f"<span style='font-size:0.6875rem;font-weight:600;color:#5E6080;"
            f"text-transform:uppercase;letter-spacing:0.07em;'>Agent Pipeline</span>"
            f"<span style='font-family:IBM Plex Mono,monospace;font-size:0.72rem;"
            f"color:#3B82F6;background:rgba(59,130,246,0.1);"
            f"border:1px solid rgba(59,130,246,0.2);border-radius:4px;padding:1px 7px;'>"
            f"{total_label} total</span>"
            f"<span style='font-size:0.6875rem;color:#5E6080;'>{len(trace)} agents</span>"
            f"</div>"
        )

    items_html = ""
    for i, node in enumerate(trace):
        agent_raw = str(node.get("agent", node.get("node", "Unknown")))
        node_raw  = str(node.get("node", ""))
        latency   = node.get("latency_ms")
        model     = str(node.get("model", ""))
        cache_hit = node.get("cache_hit", False)

        agent_key    = agent_raw.lower()
        display_name = _AGENT_DISPLAY_NAMES.get(agent_key, agent_raw.title())
        node_label   = _AGENT_NODE_LABELS.get(node_raw, node_raw.replace("_", " "))

        latency_str = ""
        if latency is not None:
            try:
                ms = int(latency)
                latency_str = f"{ms:,} ms"
                if cache_hit:
                    latency_str += " (cached)"
            except (ValueError, TypeError):
                latency_str = str(latency)

        is_last  = (i == len(trace) - 1)
        pad      = "8px 12px" if compact else "10px 14px"

        connector_html = "" if is_last else (
            '<div class="mw-pipeline-connector"></div>'
        )

        model_html = ""
        if not compact:
            if model and node_label:
                mdl = f"<span style='font-size:0.7rem;color:#5E6080;'>{model}</span>"
                model_html = (
                    f"<div class='mw-pipeline-sub'>"
                    f"{node_label} &middot; {mdl}</div>"
                )
            elif node_label:
                model_html = (
                    f"<div class='mw-pipeline-sub'>{node_label}</div>"
                )

        items_html += (
            f'<div class="mw-pipeline-step">'
            f'  <div class="mw-pipeline-row mw-pipeline-row--done" style="padding:{pad};">'
            f'    <div class="mw-pipeline-dot mw-pipeline-dot--done"></div>'
            f'    <div style="flex:1;min-width:0;">'
            f'      <div class="mw-pipeline-name">{display_name}</div>'
            f'      {model_html}'
            f'    </div>'
            f'    <span class="mw-pipeline-latency">{latency_str}</span>'
            f'  </div>'
            f'  {connector_html}'
            f'</div>'
        )

    st.markdown(
        f'<div class="mw-pipeline">{header_html}{items_html}</div>',
        unsafe_allow_html=True,
    )
