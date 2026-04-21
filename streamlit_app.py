"""
AI News Intelligence Dashboard — Streamlit UI

A polished, recruiter-friendly news intelligence dashboard that
analyses real-time news from 25+ sources across topic, sentiment,
geography, and trend dimensions.

Run with:
    streamlit run streamlit_app.py
"""

from __future__ import annotations

import logging
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timezone
import streamlit.components.v1 as components

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
)

# ---------------------------------------------------------------------------
# Page config — must be first Streamlit call
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="AI News Intelligence Dashboard",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Theme state
# ---------------------------------------------------------------------------
if "theme" not in st.session_state:
    st.session_state.theme = "dark"

_is_dark = st.session_state.theme == "dark"

# ---------------------------------------------------------------------------
# Custom CSS for a polished, premium look
# ---------------------------------------------------------------------------

# -- Theme-specific variable block ------------------------------------------
if _is_dark:
    _theme_vars = """
    :root {
        --bg-primary: #0b0b1a;
        --bg-card: #111127;
        --bg-card-hover: #191940;
        --bg-surface: #161633;
        --border-subtle: rgba(99,102,241,0.12);
        --border-medium: rgba(99,102,241,0.25);
        --border-accent: rgba(139,92,246,0.35);
        --text-primary: #f1f5f9;
        --text-secondary: #cbd5e1;
        --text-muted: #94a3b8;
        --text-accent: #a5b4fc;
        --accent-indigo: #6366f1;
        --accent-violet: #8b5cf6;
        --accent-soft: #c4b5fd;
        --positive: #34d399;
        --negative: #f87171;
        --neutral-sent: #94a3b8;
        --shadow-sm: 0 2px 8px rgba(0,0,0,0.2);
        --shadow-md: 0 4px 20px rgba(0,0,0,0.25);
        --shadow-lg: 0 8px 40px rgba(0,0,0,0.3);
        --radius-sm: 8px;
        --radius-md: 12px;
        --radius-lg: 16px;
        --sidebar-bg: linear-gradient(180deg, #0a0a1e 0%, #111127 100%);
        --summary-card-bg: linear-gradient(135deg, #111127 0%, #1a1145 60%, #161633 100%);
    }
    """
else:
    _theme_vars = """
    :root {
        --bg-primary: #f4f5f9;
        --bg-card: #ffffff;
        --bg-card-hover: #f0f1f6;
        --bg-surface: #eaecf3;
        --border-subtle: rgba(99,102,241,0.10);
        --border-medium: rgba(99,102,241,0.18);
        --border-accent: rgba(139,92,246,0.22);
        --text-primary: #1e293b;
        --text-secondary: #475569;
        --text-muted: #64748b;
        --text-accent: #4f46e5;
        --accent-indigo: #6366f1;
        --accent-violet: #8b5cf6;
        --accent-soft: #6d28d9;
        --positive: #16a34a;
        --negative: #dc2626;
        --neutral-sent: #64748b;
        --shadow-sm: 0 1px 4px rgba(0,0,0,0.06);
        --shadow-md: 0 4px 12px rgba(0,0,0,0.07);
        --shadow-lg: 0 8px 24px rgba(0,0,0,0.09);
        --radius-sm: 8px;
        --radius-md: 12px;
        --radius-lg: 16px;
        --sidebar-bg: linear-gradient(180deg, #eaecf5 0%, #dfe1ec 100%);
        --summary-card-bg: linear-gradient(135deg, #ffffff 0%, #f0edff 60%, #eaecf3 100%);
    }
    """

st.markdown(f"<style>{_theme_vars}</style>", unsafe_allow_html=True)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* ---- Variables are injected dynamically above ---- */

/* ---- Global ---- */
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
#MainMenu, footer { visibility: hidden; }
header[data-testid="stHeader"] { background: transparent !important; border: none !important; }
.stDeployButton, [data-testid="stToolbar"] { display: none !important; }
.stApp { background-color: var(--bg-primary) !important; }

/* ---- Main container spacing ---- */
.stMainBlockContainer { padding-top: 2rem; }
section[data-testid="stSidebar"] > div { padding-top: 1.5rem; }

/* ---- Metric cards ---- */
div[data-testid="stMetric"] {
    background: var(--bg-card);
    border: 1px solid var(--border-medium);
    border-radius: var(--radius-md);
    padding: 18px 22px;
    box-shadow: var(--shadow-sm);
    transition: border-color 0.2s ease, box-shadow 0.2s ease;
}
div[data-testid="stMetric"]:hover {
    border-color: var(--accent-indigo);
    box-shadow: var(--shadow-md);
}
div[data-testid="stMetric"] label {
    color: var(--text-accent) !important;
    font-weight: 500;
    font-size: 0.82rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}
div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
    color: var(--text-primary) !important;
    font-weight: 700;
    font-size: 1.6rem;
}

/* ---- Sidebar ---- */
section[data-testid="stSidebar"] {
    background: var(--sidebar-bg);
    border-right: 1px solid var(--border-subtle);
}
section[data-testid="stSidebar"] .stMarkdown p,
section[data-testid="stSidebar"] .stMarkdown li,
section[data-testid="stSidebar"] .stMarkdown h2,
section[data-testid="stSidebar"] .stMarkdown h3,
section[data-testid="stSidebar"] label {
    color: var(--text-secondary) !important;
}
section[data-testid="stSidebar"] .stTextInput input {
    background: var(--bg-surface);
    border: 1px solid var(--border-medium);
    color: var(--text-primary);
    border-radius: var(--radius-sm);
}
section[data-testid="stSidebar"] .stTextInput input::placeholder {
    color: var(--text-muted);
}

/* ---- Expander ---- */
details[data-testid="stExpander"] {
    background: var(--bg-card);
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-md);
    margin-bottom: 10px;
    transition: border-color 0.2s ease;
}
details[data-testid="stExpander"]:hover {
    border-color: var(--border-medium);
}
details[data-testid="stExpander"] summary span {
    color: var(--text-primary) !important;
    font-weight: 600;
}
details[data-testid="stExpander"] div[data-testid="stExpanderDetails"] p,
details[data-testid="stExpander"] div[data-testid="stExpanderDetails"] li {
    color: var(--text-secondary) !important;
}

/* ---- Custom cards ---- */
.summary-card {
    background: var(--summary-card-bg);
    border: 1px solid var(--border-accent);
    border-radius: var(--radius-lg);
    padding: 28px 32px;
    margin: 16px 0 24px 0;
    box-shadow: var(--shadow-lg);
}
.summary-meta-row {
    display: flex;
    align-items: center;
    gap: 16px;
    margin-bottom: 18px;
}
.summary-sentiment {
    font-size: 0.82rem;
    font-weight: 600;
}
.summary-topics-section {
    margin-bottom: 16px;
}
.summary-topics-label {
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    font-weight: 600;
    color: var(--text-muted);
    display: block;
    margin-bottom: 8px;
}
.summary-topics-row {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
}
.summary-topic-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(99,102,241,0.10);
    color: var(--text-accent);
    border: 1px solid var(--border-medium);
    padding: 6px 14px;
    border-radius: 20px;
    font-size: 0.82rem;
    font-weight: 500;
    transition: background 0.15s ease;
}
.summary-topic-pill:hover { background: rgba(99,102,241,0.20); }
.summary-topic-count {
    background: rgba(99,102,241,0.20);
    padding: 2px 8px;
    border-radius: 12px;
    font-size: 0.72rem;
    font-weight: 700;
}
.summary-narrative {
    color: var(--text-muted) !important;
    font-size: 0.88rem !important;
    line-height: 1.6 !important;
    margin: 0 !important;
}
/* ---- Theme toggle ---- */
.theme-toggle-btn {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: var(--bg-surface);
    color: var(--text-secondary);
    border: 1px solid var(--border-medium);
    padding: 6px 14px;
    border-radius: 20px;
    font-size: 0.78rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s ease;
}
.theme-toggle-btn:hover {
    border-color: var(--accent-indigo);
    color: var(--text-primary);
}
.summary-card p {
    color: var(--text-secondary);
    line-height: 1.75;
    font-size: 0.95rem;
    margin: 8px 0 0 0;
}
.summary-card strong {
    color: var(--text-primary);
}
.summary-badge {
    display: inline-block;
    background: rgba(99,102,241,0.15);
    color: var(--text-accent);
    padding: 3px 12px;
    border-radius: 20px;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.4px;
    text-transform: uppercase;
}

/* ---- Headline card ---- */
.headline-card {
    background: var(--bg-card);
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-md);
    padding: 16px 20px;
    margin: 8px 0;
    transition: all 0.2s ease;
}
.headline-card:hover {
    border-color: var(--accent-indigo);
    box-shadow: 0 4px 20px rgba(99, 102, 241, 0.12);
    transform: translateY(-1px);
}
.headline-card a {
    color: var(--text-accent);
    text-decoration: none;
    font-weight: 600;
    font-size: 0.93rem;
    line-height: 1.4;
}
.headline-card a:hover { color: var(--accent-soft); text-decoration: underline; }
.headline-meta {
    color: var(--text-muted);
    font-size: 0.78rem;
    margin-top: 6px;
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 4px;
}
.sent-positive { color: var(--positive); font-weight: 600; }
.sent-negative { color: var(--negative); font-weight: 600; }
.sent-neutral  { color: var(--neutral-sent); font-weight: 500; }

/* ---- Topic badge ---- */
.topic-badge {
    display: inline-block;
    background: linear-gradient(135deg, #4f46e5, #7c3aed);
    color: #fff;
    padding: 3px 12px;
    border-radius: 20px;
    font-size: 0.72rem;
    font-weight: 600;
    margin-left: 6px;
    letter-spacing: 0.3px;
    vertical-align: middle;
}

/* ---- Section header ---- */
.section-header {
    font-size: 1.25rem;
    font-weight: 700;
    color: var(--text-primary);
    margin: 36px 0 16px 0;
    padding-bottom: 10px;
    border-bottom: 2px solid var(--border-medium);
    letter-spacing: -0.2px;
}

/* ---- Keyword pill ---- */
.kw-pill {
    display: inline-block;
    background: rgba(99, 102, 241, 0.12);
    color: var(--text-accent);
    border: 1px solid var(--border-medium);
    padding: 5px 14px;
    border-radius: 20px;
    font-size: 0.78rem;
    margin: 4px;
    font-weight: 500;
    transition: background 0.15s ease;
}
.kw-pill:hover { background: rgba(99, 102, 241, 0.22); }

/* ---- Status bar ---- */
.status-bar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 12px;
    background: var(--bg-card);
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-md);
    padding: 12px 20px;
    margin-bottom: 20px;
    font-size: 0.82rem;
}
.status-bar .status-item {
    color: var(--text-muted);
}
.status-bar .status-item strong {
    color: var(--text-secondary);
}
.status-live {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    color: var(--positive);
    font-weight: 600;
    font-size: 0.78rem;
}
.status-live::before {
    content: '';
    width: 7px;
    height: 7px;
    background: var(--positive);
    border-radius: 50%;
    animation: pulse 2s ease-in-out infinite;
}
@keyframes pulse {
    0%, 100% { opacity: 1; box-shadow: 0 0 0 0 rgba(52,211,153,0.4); }
    50% { opacity: 0.7; box-shadow: 0 0 0 6px rgba(52,211,153,0); }
}

/* ---- Empty state ---- */
.empty-state {
    text-align: center;
    padding: 48px 24px;
    color: var(--text-muted);
    font-size: 0.95rem;
}
.empty-state .empty-icon {
    font-size: 2.5rem;
    margin-bottom: 12px;
    opacity: 0.5;
}

/* ---- Chart containers ---- */
.stPlotlyChart { border-radius: var(--radius-md); overflow: hidden; }

/* ---- Tab styling ---- */
.stTabs [data-baseweb="tab-list"] { gap: 6px; }
.stTabs [data-baseweb="tab"] {
    border-radius: var(--radius-sm);
    padding: 8px 18px;
    font-weight: 500;
    font-size: 0.85rem;
}

/* ---- Streamlit elements contrast fixes ---- */
.stMarkdown p, .stMarkdown li { color: var(--text-secondary); }
.stMarkdown h1, .stMarkdown h2, .stMarkdown h3 { color: var(--text-primary); }
.stMarkdown strong { color: var(--text-primary); }
.stMarkdown a { color: var(--text-accent); }

/* ---- Button overrides ---- */
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, var(--accent-indigo), var(--accent-violet));
    border: none;
    color: #fff;
    font-weight: 600;
    border-radius: var(--radius-sm);
    transition: opacity 0.15s ease;
}
.stButton > button[kind="primary"]:hover { opacity: 0.9; }

/* ---- Dataframe ---- */
.stDataFrame { border-radius: var(--radius-md); overflow: hidden; }

/* ---- Sidebar collapse/expand controls ---- */
[data-testid="stExpandSidebarButton"] {
    z-index: 999999 !important;
    display: flex !important;
    visibility: visible !important;
    opacity: 1 !important;
}
[data-testid="stExpandSidebarButton"] button {
    background: var(--bg-card) !important;
    color: var(--text-primary) !important;
    border: 1px solid var(--border-medium) !important;
    border-radius: var(--radius-sm) !important;
    box-shadow: var(--shadow-md) !important;
    padding: 8px !important;
    width: 38px !important;
    height: 38px !important;
    min-width: 38px !important;
    min-height: 38px !important;
    display: flex !important;
    visibility: visible !important;
    opacity: 1 !important;
    align-items: center;
    justify-content: center;
}
[data-testid="stExpandSidebarButton"] button:hover {
    border-color: var(--accent-indigo) !important;
    box-shadow: var(--shadow-lg) !important;
}
[data-testid="stExpandSidebarButton"] svg {
    fill: var(--text-primary) !important;
    color: var(--text-primary) !important;
    width: 18px !important;
    height: 18px !important;
}
/* Hide our custom JS toggle when sidebar is expanded (Streamlit adds the collapsed control only when collapsed) */
section[data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"] button {
    color: var(--text-secondary) !important;
    background: transparent !important;
}
section[data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"] button:hover {
    color: var(--text-primary) !important;
}

/* ---- Non-primary buttons ---- */
.stButton > button:not([kind="primary"]) {
    background: var(--bg-surface) !important;
    color: var(--text-secondary) !important;
    border: 1px solid var(--border-medium) !important;
    border-radius: var(--radius-sm);
}
.stButton > button:not([kind="primary"]):hover {
    background: var(--bg-card-hover) !important;
    color: var(--text-primary) !important;
    border-color: var(--accent-indigo) !important;
}

/* ---- Selectbox / Multiselect ---- */
.stSelectbox [data-baseweb="select"],
.stMultiSelect [data-baseweb="select"] {
    background: var(--bg-surface) !important;
}
.stSelectbox [data-baseweb="select"] div,
.stMultiSelect [data-baseweb="select"] div {
    color: var(--text-primary) !important;
}
.stSelectbox [data-baseweb="select"],
.stMultiSelect [data-baseweb="select"] {
    border-color: var(--border-medium) !important;
}
[data-baseweb="popover"] [data-baseweb="menu"],
[data-baseweb="popover"] ul {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-medium) !important;
}
[data-baseweb="popover"] li {
    color: var(--text-secondary) !important;
}
[data-baseweb="popover"] li:hover,
[data-baseweb="popover"] li[aria-selected="true"] {
    background: var(--bg-card-hover) !important;
    color: var(--text-primary) !important;
}

/* ---- Multiselect tags ---- */
.stMultiSelect [data-baseweb="tag"] {
    background: rgba(99,102,241,0.15) !important;
    color: var(--text-accent) !important;
    border: none !important;
}
.stMultiSelect [data-baseweb="tag"] span {
    color: var(--text-accent) !important;
}

/* ---- Slider ---- */
.stSlider [data-baseweb="slider"] div[role="slider"] {
    background: var(--accent-indigo) !important;
    border-color: var(--accent-indigo) !important;
}
.stSlider [data-testid="stTickBarMin"],
.stSlider [data-testid="stTickBarMax"] {
    color: var(--text-muted) !important;
}
.stSlider div[data-testid="stThumbValue"] {
    color: var(--text-primary) !important;
}

/* ---- Tab styling (extended) ---- */
.stTabs [data-baseweb="tab"] {
    color: var(--text-muted) !important;
}
.stTabs [data-baseweb="tab"][aria-selected="true"] {
    color: var(--text-primary) !important;
}
.stTabs [data-baseweb="tab-highlight"] {
    background-color: var(--accent-indigo) !important;
}

/* ---- Text input in main area ---- */
.stTextInput input,
.stNumberInput input {
    background: var(--bg-surface) !important;
    color: var(--text-primary) !important;
    border: 1px solid var(--border-medium) !important;
}
.stTextInput input::placeholder,
.stNumberInput input::placeholder {
    color: var(--text-muted) !important;
}

/* ---- Labels ---- */
.stSelectbox label, .stMultiSelect label,
.stSlider label, .stTextInput label,
.stNumberInput label, .stRadio label,
.stCheckbox label {
    color: var(--text-secondary) !important;
}

/* ---- Alert messages (info/warning/success/error) ---- */
div[data-testid="stAlert"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-medium) !important;
    color: var(--text-secondary) !important;
}
div[data-testid="stAlert"] p,
div[data-testid="stAlert"] span {
    color: var(--text-secondary) !important;
}

/* ---- Caption ---- */
.stCaption, [data-testid="stCaptionContainer"] {
    color: var(--text-muted) !important;
}

/* ---- Spinner ---- */
.stSpinner > div { color: var(--text-secondary) !important; }

/* ---- Warning/Info bar ---- */
.stWarning, .stInfo, .stSuccess, .stError {
    background: var(--bg-card) !important;
}
</style>
""", unsafe_allow_html=True)


def get_plotly_layout():
    """Return Plotly layout dict matching the current theme."""
    if st.session_state.get("theme", "dark") == "dark":
        return dict(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter, sans-serif", color="#c7d2fe"),
            margin=dict(l=40, r=20, t=40, b=40),
        )
    else:
        return dict(
            template="plotly_white",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter, sans-serif", color="#334155"),
            margin=dict(l=40, r=20, t=40, b=40),
        )

COLOUR_PALETTE = [
    "#6366f1", "#8b5cf6", "#a78bfa", "#c4b5fd",
    "#34d399", "#2dd4bf", "#38bdf8", "#818cf8",
    "#f472b6", "#fb923c", "#facc15", "#4ade80",
]


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
def render_sidebar():
    """Render the sidebar controls and return user settings."""
    with st.sidebar:
        # ---- Theme toggle ----
        theme_label = "☀️ Switch to Light" if st.session_state.theme == "dark" else "🌙 Switch to Dark"
        if st.button(theme_label, key="theme_toggle", use_container_width=True):
            st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"
            st.rerun()

        st.markdown("## 🌐 News Intelligence")
        st.markdown("---")

        query = st.text_input(
            "🔍 Search topic or sector",
            placeholder="e.g. AI, crypto, geopolitics, energy…",
            key="search_query",
        )

        st.markdown("### Quick Sectors")
        sectors = ["AI", "Crypto", "Stocks", "Geopolitics", "Economy",
                    "Energy", "Elections", "Defense", "Healthcare", "Tech"]
        cols = st.columns(2)
        selected_sector = None
        for i, sector in enumerate(sectors):
            with cols[i % 2]:
                if st.button(sector, key=f"sector_{sector}", use_container_width=True):
                    selected_sector = sector

        st.markdown("---")
        st.markdown("### ⚙️ Filters")

        lookback = st.slider("Lookback (days)", 1, 14, 7, key="lookback_days")

        sentiment_filter = st.multiselect(
            "Sentiment",
            ["positive", "neutral", "negative"],
            default=["positive", "neutral", "negative"],
            key="sentiment_filter",
        )

        st.markdown("---")

        # Watchlist
        st.markdown("### 📌 Watchlist")
        if "watchlist" not in st.session_state:
            st.session_state.watchlist = ["AI", "Markets / Stocks"]

        new_item = st.text_input("Add topic to watchlist", key="watchlist_input")
        if new_item and st.button("Add", key="add_watchlist"):
            if new_item not in st.session_state.watchlist:
                st.session_state.watchlist.append(new_item)

        for item in st.session_state.watchlist:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"• {item}")
            with col2:
                if st.button("✕", key=f"rm_{item}"):
                    st.session_state.watchlist.remove(item)
                    st.rerun()

        st.markdown("---")
        st.markdown(
            "<div style='text-align:center; color:var(--text-muted); font-size:0.75rem;'>"
            "Built with Python · Streamlit · scikit-learn<br>"
            "v1.0.0 · No paid APIs required"
            "</div>",
            unsafe_allow_html=True,
        )

    return {
        "query": selected_sector or query,
        "lookback_days": lookback,
        "sentiment_filter": sentiment_filter,
    }


# ---------------------------------------------------------------------------
# Main dashboard sections
# ---------------------------------------------------------------------------

def render_header(result):
    """Render the top header with key metrics."""
    st.markdown(
        "<h1 style='text-align:center; font-weight:800; "
        "background: linear-gradient(90deg, #6366f1, #a78bfa, #c4b5fd); "
        "-webkit-background-clip: text; -webkit-text-fill-color: transparent; "
        "font-size: 2.2rem; margin-bottom: 4px;'>"
        "🌐 AI News Intelligence Dashboard</h1>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p style='text-align:center; color:var(--text-muted); margin-top:0; margin-bottom:24px;'>"
        "Real-time multi-source news analysis · Topic clustering · Sentiment · Trends"
        "</p>",
        unsafe_allow_html=True,
    )

    # Metrics row
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Articles", result.article_count)
    c2.metric("Sources", result.source_count)
    c3.metric("Topics", result.topic_count)

    avg_sent = result.articles["sentiment_score"].mean() if not result.articles.empty else 0
    sent_emoji = "😊" if avg_sent > 0.05 else ("😟" if avg_sent < -0.05 else "😐")
    c4.metric("Avg Sentiment", f"{avg_sent:.2f} {sent_emoji}")
    c5.metric("Pipeline", f"{result.elapsed_seconds}s")


def render_summary(result):
    """Render a clean, structured executive summary."""
    st.markdown('<div class="section-header">Executive Summary</div>', unsafe_allow_html=True)

    # Sentiment assessment
    avg_sent = (
        result.articles["sentiment_score"].mean()
        if not result.articles.empty and "sentiment_score" in result.articles.columns
        else 0
    )
    if avg_sent > 0.1:
        sent_label, sent_class = "Positive", "sent-positive"
    elif avg_sent < -0.1:
        sent_label, sent_class = "Cautious", "sent-negative"
    else:
        sent_label, sent_class = "Balanced", "sent-neutral"

    method = "AI-Enhanced" if result.llm_used else "Statistical"

    # Top topics
    top_topics = sorted(
        result.trend_report.topic_counts.items(),
        key=lambda x: x[1], reverse=True,
    )[:5]
    topic_pills = "".join(
        f'<span class="summary-topic-pill">{t} '
        f'<span class="summary-topic-count">{c}</span></span>'
        for t, c in top_topics
    )

    st.markdown(
        f'<div class="summary-card">'
        f'<div class="summary-meta-row">'
        f'<span class="summary-badge">{method}</span>'
        f'<span class="summary-sentiment {sent_class}">Overall Tone: {sent_label}</span>'
        f'</div>'
        f'<div class="summary-topics-section">'
        f'<span class="summary-topics-label">Top Topics</span>'
        f'<div class="summary-topics-row">{topic_pills}</div>'
        f'</div>'
        f'<p class="summary-narrative">'
        f'Analysed <strong>{result.article_count} articles</strong> from '
        f'<strong>{result.source_count} sources</strong> across '
        f'{result.topic_count} topic categories. '
        f'Scroll down for detailed breakdowns by topic, sentiment, region, and trend.'
        f'</p></div>',
        unsafe_allow_html=True,
    )


def render_trends(result):
    """Render trend visualisations."""
    st.markdown('<div class="section-header">📈 Trends & Insights</div>', unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Topic Distribution", "💹 Sentiment Map",
        "🕐 Timeline", "🔑 Top Keywords"
    ])

    with tab1:
        if result.trend_report.topic_counts:
            topic_df = pd.DataFrame(
                list(result.trend_report.topic_counts.items()),
                columns=["Topic", "Count"],
            ).sort_values("Count", ascending=True)

            fig = px.bar(
                topic_df, x="Count", y="Topic", orientation="h",
                color="Count",
                color_continuous_scale=["#4f46e5", "#8b5cf6", "#c4b5fd"],
            )
            fig.update_traces(hovertemplate="%{y} — %{x} articles<extra></extra>")
            fig.update_layout(**get_plotly_layout(), showlegend=False, coloraxis_showscale=False)
            fig.update_layout(height=max(350, len(topic_df) * 35))
            st.plotly_chart(fig, use_container_width=True)

            # Rising topics
            if result.trend_report.rising_topics:
                st.markdown("**🔥 Rising Topics** (over-represented in last 12h)")
                for topic, ratio in result.trend_report.rising_topics[:5]:
                    st.markdown(f"- **{topic}** — {ratio:.1f}× recent growth")
        else:
            st.info("Not enough data to display topic distribution.")

    with tab2:
        sent_data = result.trend_report.sentiment_by_topic
        if sent_data:
            sent_df = pd.DataFrame(
                list(sent_data.items()),
                columns=["Topic", "Avg Sentiment"],
            ).sort_values("Avg Sentiment")

            colors = ["#f87171" if v < -0.05 else "#34d399" if v > 0.05 else "#9ca3af"
                       for v in sent_df["Avg Sentiment"]]

            fig = go.Figure(go.Bar(
                x=sent_df["Avg Sentiment"],
                y=sent_df["Topic"],
                orientation="h",
                marker_color=colors,
                hovertemplate="%{y} — Avg Sentiment: %{x:.2f}<extra></extra>"
            ))
            fig.update_layout(**get_plotly_layout(), height=max(350, len(sent_df) * 35))
            fig.update_xaxes(range=[-1, 1])
            st.plotly_chart(fig, use_container_width=True)

            # Sentiment pie
            if not result.articles.empty and "sentiment_label" in result.articles.columns:
                pie_data = result.articles["sentiment_label"].value_counts()
                fig_pie = px.pie(
                    names=pie_data.index,
                    values=pie_data.values,
                    color=pie_data.index,
                    color_discrete_map={
                        "positive": "#34d399",
                        "negative": "#f87171",
                        "neutral": "#6b7280",
                    },
                    hole=0.45,
                )
                fig_pie.update_traces(hovertemplate="%{label} — %{value} articles<extra></extra>")
                fig_pie.update_layout(**get_plotly_layout(), height=300)
                st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("Sentiment data not available.")

    with tab3:
        if result.trend_report.hourly_volume:
            vol_df = pd.DataFrame(result.trend_report.hourly_volume, columns=["Hour", "Count"])
            fig = px.area(
                vol_df, x="Hour", y="Count",
                color_discrete_sequence=["#6366f1"],
            )
            fig.update_traces(hovertemplate="Hour %{x} — %{y} articles<extra></extra>")
            fig.update_layout(**get_plotly_layout(), height=300)
            fig.update_traces(fill="tozeroy", fillcolor="rgba(99,102,241,0.15)")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Not enough timestamped articles for a timeline.")

        # Source concentration
        if result.trend_report.source_concentration:
            st.markdown("**📰 Source Coverage**")
            src_df = pd.DataFrame(
                list(result.trend_report.source_concentration.items()),
                columns=["Source", "Articles"],
            ).sort_values("Articles", ascending=True).tail(10)

            fig = px.bar(
                src_df, x="Articles", y="Source", orientation="h",
                color_discrete_sequence=["#8b5cf6"],
            )
            fig.update_traces(hovertemplate="%{y} — %{x} articles<extra></extra>")
            fig.update_layout(**get_plotly_layout(), height=350)
            st.plotly_chart(fig, use_container_width=True)

    with tab4:
        if result.trend_report.top_keywords:
            kws = result.trend_report.top_keywords[:20]
            pills_html = " ".join(
                f'<span class="kw-pill">{kw} ({w:.3f})</span>'
                for kw, w in kws
            )
            st.markdown(pills_html, unsafe_allow_html=True)

            kw_df = pd.DataFrame(kws, columns=["Keyword", "TF-IDF Weight"])
            fig = px.treemap(
                kw_df, path=["Keyword"], values="TF-IDF Weight",
                color="TF-IDF Weight",
                color_continuous_scale=["#1a1a2e", "#6366f1", "#c4b5fd"],
            )
            fig.update_traces(hovertemplate="%{label} — Weight: %{value:.3f}<extra></extra>")
            fig.update_layout(**get_plotly_layout(), height=400, coloraxis_showscale=False)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Not enough data for keyword analysis.")


def render_geo(result):
    """Render geography / region section."""
    df = result.articles
    if df.empty or "primary_country" not in df.columns:
        return

    geo_articles = df[df["primary_country"] != ""]
    if geo_articles.empty:
        return

    st.markdown('<div class="section-header">🌍 Geographic Coverage</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        country_counts = geo_articles["primary_country"].value_counts().head(12)
        fig = px.bar(
            x=country_counts.values,
            y=country_counts.index,
            orientation="h",
            labels={"x": "Articles", "y": "Country"},
            color_discrete_sequence=["#6366f1"],
        )
        fig.update_traces(hovertemplate="%{y} — %{x} articles<extra></extra>")
        fig.update_layout(**get_plotly_layout(), height=350)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        if "primary_region" in df.columns:
            region_counts = geo_articles["primary_region"].value_counts()
            region_counts = region_counts[region_counts.index != ""]
            if not region_counts.empty:
                fig = px.pie(
                    names=region_counts.index,
                    values=region_counts.values,
                    color_discrete_sequence=COLOUR_PALETTE,
                    hole=0.4,
                )
                fig.update_traces(hovertemplate="%{label} — %{value} articles<extra></extra>")
                fig.update_layout(**get_plotly_layout(), height=350)
                st.plotly_chart(fig, use_container_width=True)


def render_topic_panels(result):
    """Render per-topic narrative panels."""
    st.markdown('<div class="section-header">🗂️ Topic Narratives</div>', unsafe_allow_html=True)

    if not result.cluster_summaries:
        st.info("No topic clusters to display.")
        return

    # Sort by article count descending
    sorted_topics = sorted(
        result.cluster_summaries.items(),
        key=lambda x: result.trend_report.topic_counts.get(x[0], 0),
        reverse=True,
    )

    for topic, summary in sorted_topics:
        count = result.trend_report.topic_counts.get(topic, 0)
        avg_sent = result.trend_report.sentiment_by_topic.get(topic, 0)
        sent_emoji = "🟢" if avg_sent > 0.05 else ("🔴" if avg_sent < -0.05 else "⚪")

        with st.expander(f"{topic}  ·  {count} articles  ·  {sent_emoji} {avg_sent:+.2f}", expanded=False):
            st.markdown(summary)

            # Show top 5 headlines in this topic
            topic_df = result.articles[result.articles["topic"] == topic].head(5)
            for _, row in topic_df.iterrows():
                sent_class = f"sent-{row.get('sentiment_label', 'neutral')}"
                pub = ""
                if pd.notna(row.get("published")):
                    pub = pd.Timestamp(row["published"]).strftime("%b %d, %H:%M")
                st.markdown(
                    f'<div class="headline-card">'
                    f'<a href="{row["url"]}" target="_blank">{row["title"]}</a>'
                    f'<div class="headline-meta">'
                    f'{row["source"]} · {pub} · '
                    f'<span class="{sent_class}">{row.get("sentiment_label", "")}</span>'
                    f'</div></div>',
                    unsafe_allow_html=True,
                )


def render_headlines(result, sentiment_filter):
    """Render the full headline list with filters."""
    st.markdown('<div class="section-header">📰 All Headlines</div>', unsafe_allow_html=True)

    df = result.articles.copy()
    if df.empty:
        st.info("No articles to display.")
        return

    # Apply sentiment filter
    if "sentiment_label" in df.columns and sentiment_filter:
        df = df[df["sentiment_label"].isin(sentiment_filter)]

    # Source filter
    sources = sorted(df["source"].unique())
    selected_sources = st.multiselect(
        "Filter by source", sources, default=sources[:], key="source_filter_main"
    )
    if selected_sources:
        df = df[df["source"].isin(selected_sources)]

    st.markdown(f"Showing **{len(df)}** articles")

    for _, row in df.head(50).iterrows():
        sent_class = f"sent-{row.get('sentiment_label', 'neutral')}"
        pub = ""
        if pd.notna(row.get("published")):
            pub = pd.Timestamp(row["published"]).strftime("%b %d, %H:%M")

        topic_badge = ""
        if row.get("topic"):
            topic_badge = f'<span class="topic-badge">{row["topic"]}</span>'

        country = row.get("primary_country", "")
        geo_badge = f" · 📍 {country}" if country else ""

        score = row.get("relevance_score")
        rel_badge = f" · 🎯 {score:.2f}" if score and score > 0 else ""

        st.markdown(
            f'<div class="headline-card">'
            f'<a href="{row["url"]}" target="_blank">{row["title"]}</a>'
            f'<div class="headline-meta">'
            f'{row["source"]} · {pub} · '
            f'<span class="{sent_class}">{row.get("sentiment_label", "")}</span>'
            f'{geo_badge}{rel_badge} {topic_badge}'
            f'</div></div>',
            unsafe_allow_html=True,
        )


def render_explainability(result):
    """Show how the dashboard reached its conclusions."""
    st.markdown('<div class="section-header">🔍 How This Works</div>', unsafe_allow_html=True)

    with st.expander("Methodology & Explainability", expanded=False):
        st.markdown("""
**Data Pipeline:**
1. **Fetch** — Articles pulled from 25+ RSS feeds (Reuters, BBC, NYT, TechCrunch, etc.) in real-time
2. **Clean** — Deduplicated via content fingerprinting (MD5 of normalised text)
3. **Classify** — Keyword-matching assigns topics; TF-IDF cosine-similarity handles edge cases
4. **Sentiment** — VADER (Valence Aware Dictionary and sEntiment Reasoner) scores each headline
5. **Geography** — Keyword-based country/region extraction from a curated 28-country dictionary
6. **Trends** — TF-IDF keyword extraction + temporal frequency analysis + growth-ratio detection
7. **Summarise** — Extractive summarisation via TF-IDF centrality (or optional LLM if configured)

**Why these choices:**
- **Keyword-first classification** is fast, explainable, and doesn't need a GPU
- **VADER** is specifically tuned for social media / news text and works well without fine-tuning
- **TF-IDF** provides a lightweight but effective similarity measure for clustering and search
- **No black boxes** — every score, label, and cluster can be traced back to specific keywords and counts

**Limitations:**
- Sentiment is headline-level (not full-article); some nuance is lost
- Geo extraction uses keyword matching, not NER — it may miss novel entities
- Topic classification favours recall over precision in the fallback path
        """)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Classification method breakdown:**")
            if "topic_confidence" in result.articles.columns:
                conf_counts = result.articles["topic_confidence"].value_counts()
                st.dataframe(conf_counts.reset_index().rename(
                    columns={"index": "Method", "topic_confidence": "Method", "count": "Count"}
                ), hide_index=True)
        with col2:
            st.markdown("**Data freshness:**")
            if not result.articles.empty and "published" in result.articles.columns:
                dated = result.articles.dropna(subset=["published"])
                if not dated.empty:
                    newest = dated["published"].max()
                    oldest = dated["published"].min()
                    st.write(f"Newest: {newest}")
                    st.write(f"Oldest: {oldest}")


# ---------------------------------------------------------------------------
# Main app
# ---------------------------------------------------------------------------
def main():
    settings = render_sidebar()
    query = settings["query"]
    lookback = settings["lookback_days"]
    sentiment_filter = settings["sentiment_filter"]

    # ---- Floating sidebar toggle button (always visible) ----
    _tbg = "#111127" if _is_dark else "#ffffff"
    _tcol = "#f1f5f9" if _is_dark else "#1e293b"
    _tbdr = "rgba(99,102,241,0.25)" if _is_dark else "rgba(99,102,241,0.18)"
    _tshd = "rgba(0,0,0,0.25)" if _is_dark else "rgba(0,0,0,0.10)"
    components.html(f"""
    <script>
    (function() {{
        var existing = window.parent.document.getElementById('sidebar-toggle-btn');
        if (existing) existing.remove();
        var btn = document.createElement('button');
        btn.id = 'sidebar-toggle-btn';
        btn.innerHTML = '&#9776;';
        btn.title = 'Toggle sidebar';
        btn.style.cssText = 'position:fixed;top:14px;left:14px;z-index:1000000;'
            + 'width:38px;height:38px;border-radius:8px;'
            + 'border:1px solid {_tbdr};background:{_tbg};color:{_tcol};'
            + 'font-size:18px;cursor:pointer;display:flex;align-items:center;'
            + 'justify-content:center;box-shadow:0 2px 8px {_tshd};'
            + 'transition:all 0.2s ease;padding:0;line-height:1;';
        btn.onmouseover = function() {{ this.style.borderColor='#6366f1'; }};
        btn.onmouseout = function() {{ this.style.borderColor='{_tbdr}'; }};
        btn.onclick = function() {{
            var openBtn = window.parent.document.querySelector('[data-testid="collapsedControl"]');
            if (openBtn) {{
                openBtn.click();
            }} else {{
                var closeBtn = window.parent.document.querySelector('[data-testid="stSidebarCollapseButton"] button') || window.parent.document.querySelector('[data-testid="stSidebarCollapseButton"]');
                if (closeBtn) closeBtn.click();
            }}
        }};
        window.parent.document.body.appendChild(btn);
    }})();
    </script>
    """, height=0)

    # Refresh button in main area
    col_refresh, col_query_display = st.columns([1, 4])
    with col_refresh:
        refresh = st.button("🔄 Refresh Data", use_container_width=True, type="primary")
    with col_query_display:
        if query:
            st.markdown(
                f"<p style='color:var(--text-accent); padding-top:8px;'>"
                f"Searching: <strong>{query}</strong></p>",
                unsafe_allow_html=True,
            )

    # Run pipeline (cached unless refresh is pressed)
    cache_key = f"{query}_{lookback}"

    if refresh or "last_result" not in st.session_state or st.session_state.get("cache_key") != cache_key:
        with st.spinner("⚡ Fetching & analysing news from 25+ sources…"):
            from news_intel.pipeline import run_pipeline
            result = run_pipeline(query=query, lookback_days=lookback)
            st.session_state["last_result"] = result
            st.session_state["cache_key"] = cache_key
    else:
        result = st.session_state["last_result"]

    if result.article_count == 0:
        st.warning("No articles found. Try a different query or increase the lookback period.")
        return

    # Render all sections
    render_header(result)
    render_summary(result)
    render_trends(result)
    render_geo(result)
    render_topic_panels(result)
    render_headlines(result, sentiment_filter)
    render_explainability(result)


if __name__ == "__main__":
    main()
