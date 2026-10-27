"""
Main Streamlit Application for TravelResolve.
Premium Futuristic AI Operations Command Center & Case Management Suite.
Developed by Keyura Motegaonkar.
"""

import os
import sys
from pathlib import Path

# Add project root to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st
from app.config import settings
from app.database import init_db, SessionLocal, Booking
from app.seed_data import generate_seed_data

from app.ui.components.branding import (
    render_sidebar_branding,
    render_header_brandmark,
    get_favicon_path
)

from app.ui.views.dashboard import render_dashboard
from app.ui.views.ticket_workspace import render_ticket_workspace
from app.ui.views.booking_explorer import render_booking_explorer
from app.ui.views.review_queue import render_review_queue
from app.ui.views.execution_trace import render_execution_trace
from app.ui.views.quality_lab import render_quality_lab
from app.ui.views.benchmarks import render_benchmarks

# Page configuration with custom TravelResolve icon
st.set_page_config(
    page_title="TravelResolve — AI Operations Command Center",
    page_icon=get_favicon_path(),
    layout="wide",
    initial_sidebar_state="expanded"
)

# Premium Futuristic Styling & Floating Universe System
st.markdown("""
<style>
    /* Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

    /* Global Typography & Palette */
    html, body, [class*="css"], .stMarkdown, p, label, input, textarea, button, select {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
        color: #F4F5FF;
        letter-spacing: -0.01em;
    }

    code, pre, .stCodeBlock, [data-testid="stCode"] {
        font-family: 'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace !important;
    }

    /* Dark Deep Canvas */
    .stApp {
        background-color: #080B18 !important;
        color: #F4F5FF;
    }

    /* Ambient Floating Background Layer (Non-interactive) */
    .ambient-universe {
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        pointer-events: none;
        z-index: 0;
        overflow: hidden;
    }
    .ambient-orb {
        position: absolute;
        border-radius: 50%;
        filter: blur(80px);
        opacity: 0.16;
        pointer-events: none;
    }
    .orb-1 {
        width: 480px;
        height: 480px;
        background: radial-gradient(circle, #8275FF 0%, rgba(130, 117, 255, 0.08) 70%);
        top: -120px;
        right: 8%;
        animation: pulseOrb 12s ease-in-out infinite alternate;
    }
    .orb-2 {
        width: 420px;
        height: 420px;
        background: radial-gradient(circle, #38C9FF 0%, rgba(56, 201, 255, 0.05) 70%);
        bottom: -90px;
        left: 8%;
        animation: pulseOrb 16s ease-in-out infinite alternate-reverse;
    }
    .orb-3 {
        width: 320px;
        height: 320px;
        background: radial-gradient(circle, #6352FF 0%, rgba(99, 82, 255, 0.05) 70%);
        top: 38%;
        left: 45%;
        opacity: 0.12;
        animation: pulseOrb 14s ease-in-out infinite alternate;
    }
    .floating-ring {
        position: absolute;
        border-radius: 50%;
        border: 1px dashed rgba(130, 117, 255, 0.12);
        pointer-events: none;
    }
    .ring-1 {
        width: 320px;
        height: 320px;
        top: 6%;
        right: 4%;
        animation: spinRing 60s linear infinite;
    }
    .ring-2 {
        width: 200px;
        height: 200px;
        bottom: 10%;
        left: 10%;
        border-color: rgba(56, 201, 255, 0.1);
        animation: spinRing 45s linear infinite reverse;
    }

    @keyframes pulseOrb {
        0% { transform: scale(0.9) translate(0, 0); opacity: 0.12; }
        50% { transform: scale(1.1) translate(15px, -15px); opacity: 0.22; }
        100% { transform: scale(0.9) translate(0, 0); opacity: 0.12; }
    }
    @keyframes spinRing {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
    @media (prefers-reduced-motion: reduce) {
        .ambient-orb, .floating-ring {
            animation: none !important;
        }
    }

    /* Container Glassmorphism Cards */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: rgba(20, 26, 50, 0.75) !important;
        backdrop-filter: blur(14px) !important;
        -webkit-backdrop-filter: blur(14px) !important;
        border: 1px solid rgba(130, 117, 255, 0.16) !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.45);
        transition: transform 0.25s cubic-bezier(0.16, 1, 0.3, 1), border-color 0.25s ease, box-shadow 0.25s ease;
    }
    div[data-testid="stVerticalBlockBorderWrapper"]:hover {
        border-color: rgba(130, 117, 255, 0.32) !important;
        box-shadow: 0 8px 30px -4px rgba(130, 117, 255, 0.12);
    }

    /* Metric Cards */
    [data-testid="stMetric"] {
        background: rgba(20, 26, 50, 0.85) !important;
        backdrop-filter: blur(10px) !important;
        border: 1px solid rgba(130, 117, 255, 0.20) !important;
        border-radius: 12px !important;
        padding: 16px 18px !important;
        min-height: 104px !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
        transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
    }
    [data-testid="stMetric"]:hover {
        transform: translateY(-2px);
        border-color: rgba(130, 117, 255, 0.45) !important;
        box-shadow: 0 8px 24px -4px rgba(130, 117, 255, 0.2);
    }
    [data-testid="stMetricLabel"] p {
        color: #A2AAC7 !important;
        font-size: 0.76rem !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
    }
    [data-testid="stMetricValue"] {
        color: #F4F5FF !important;
        font-weight: 700 !important;
        font-size: 1.7rem !important;
        letter-spacing: -0.02em !important;
    }
    [data-testid="stMetricDelta"] svg {
        fill: #35D49A !important;
    }

    /* Top Header Bar (Non-Clipping, Auto-Expanding, Fully Responsive) */
    .hero-header, .top-header-bar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 24px;
        min-height: 88px;
        height: auto;
        padding: 20px 28px;
        box-sizing: border-box;
        background: rgba(20, 26, 50, 0.75);
        backdrop-filter: blur(14px);
        -webkit-backdrop-filter: blur(14px);
        border: 1px solid rgba(130, 117, 255, 0.18);
        border-radius: 12px;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.35);
    }
    .hero-header__content {
        display: flex;
        align-items: center;
        gap: 16px;
        flex: 1 1 auto;
        min-width: 0;
    }
    .hero-header__text {
        flex: 1 1 auto;
        min-width: 0;
    }
    .hero-header__title, .brand-title {
        margin: 0 0 6px 0 !important;
        font-size: 22px !important;
        font-weight: 700 !important;
        color: #F4F5FF !important;
        letter-spacing: -0.02em !important;
        line-height: 1.35 !important;
        overflow-wrap: break-word !important;
        word-break: break-word !important;
    }
    .hero-header__subtitle, .brand-tagline {
        margin: 0 !important;
        font-size: 14px !important;
        color: #A2AAC7 !important;
        line-height: 1.6 !important;
        white-space: normal !important;
        overflow-wrap: anywhere !important;
        word-break: normal !important;
    }
    .hero-header__badges, .header-right-pills {
        display: flex;
        flex: 0 0 auto;
        align-items: center;
        gap: 10px;
        flex-wrap: wrap;
    }
    .status-pill {
        display: inline-flex;
        align-items: center;
        gap: 7px;
        background: rgba(53, 212, 154, 0.12);
        color: #35D49A;
        font-size: 0.76rem;
        font-weight: 600;
        padding: 6px 14px;
        border-radius: 9999px;
        border: 1px solid rgba(53, 212, 154, 0.3);
        white-space: nowrap;
    }
    .status-dot {
        width: 7px;
        height: 7px;
        background-color: #35D49A;
        border-radius: 50%;
        box-shadow: 0 0 8px #35D49A;
        animation: pulseDot 2s infinite;
    }
    @keyframes pulseDot {
        0%, 100% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.4; transform: scale(0.85); }
    }
    .developer-pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(130, 117, 255, 0.12);
        color: #C0B7FF;
        font-size: 0.76rem;
        font-weight: 600;
        padding: 6px 14px;
        border-radius: 9999px;
        border: 1px solid rgba(130, 117, 255, 0.3);
        white-space: nowrap;
    }

    @media (max-width: 992px) {
        .hero-header, .top-header-bar {
            flex-direction: column;
            align-items: flex-start;
            gap: 16px;
            padding: 16px 20px;
            min-height: auto;
        }
        .hero-header__content {
            width: 100%;
        }
        .hero-header__badges, .header-right-pills {
            width: 100%;
            justify-content: flex-start;
        }
    }

    /* Buttons */
    .stButton>button {
        border-radius: 8px !important;
        font-weight: 600 !important;
        font-size: 0.88rem !important;
        padding: 0.5rem 1.2rem !important;
        transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1) !important;
    }
    .stButton>button[kind="primary"] {
        background: linear-gradient(135deg, #8275FF 0%, #6352FF 100%) !important;
        border: 1px solid rgba(130, 117, 255, 0.4) !important;
        color: #FFFFFF !important;
        box-shadow: 0 4px 15px rgba(130, 117, 255, 0.35) !important;
    }
    .stButton>button[kind="primary"]:hover {
        background: linear-gradient(135deg, #968BFF 0%, #7565FF 100%) !important;
        box-shadow: 0 6px 22px rgba(130, 117, 255, 0.55) !important;
        transform: translateY(-1px) !important;
    }
    .stButton>button[kind="secondary"] {
        background: rgba(27, 34, 64, 0.8) !important;
        border: 1px solid rgba(130, 117, 255, 0.25) !important;
        color: #F4F5FF !important;
    }
    .stButton>button[kind="secondary"]:hover {
        background: rgba(130, 117, 255, 0.18) !important;
        border-color: #8275FF !important;
        transform: translateY(-1px) !important;
    }

    /* Form Controls & Inputs */
    input, textarea, [data-baseweb="select"] {
        background-color: #10152B !important;
        color: #F4F5FF !important;
        border: 1px solid rgba(130, 117, 255, 0.25) !important;
        border-radius: 8px !important;
    }
    input:focus, textarea:focus {
        border-color: #8275FF !important;
        box-shadow: 0 0 0 2px rgba(130, 117, 255, 0.35) !important;
    }
    div[data-baseweb="popover"], div[data-baseweb="menu"], ul[role="listbox"] {
        background-color: #141A32 !important;
        border: 1px solid rgba(130, 117, 255, 0.25) !important;
    }
    li[role="option"] {
        color: #F4F5FF !important;
    }
    li[role="option"]:hover, li[aria-selected="true"] {
        background-color: rgba(130, 117, 255, 0.22) !important;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        width: 260px !important;
        min-width: 260px !important;
        background-color: #0D1124 !important;
        border-right: 1px solid rgba(130, 117, 255, 0.15) !important;
    }

    /* Sidebar Navigation Items */
    [data-testid="stSidebar"] [data-testid="stRadio"] > div {
        gap: 6px;
    }
    [data-testid="stSidebar"] [data-testid="stRadio"] label {
        padding: 9px 12px !important;
        border-radius: 8px !important;
        color: #A2AAC7 !important;
        font-weight: 500 !important;
        font-size: 0.88rem !important;
        transition: all 0.2s ease !important;
        cursor: pointer !important;
        border-left: 3px solid transparent !important;
    }
    [data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
        background: rgba(130, 117, 255, 0.09) !important;
        color: #F4F5FF !important;
    }
    [data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) {
        background: linear-gradient(90deg, rgba(130, 117, 255, 0.2) 0%, rgba(56, 201, 255, 0.04) 100%) !important;
        color: #FFFFFF !important;
        font-weight: 600 !important;
        border-left: 3px solid #8275FF !important;
        box-shadow: inset 0 0 12px rgba(130, 117, 255, 0.1) !important;
    }

    /* System Status Card in Sidebar */
    .sidebar-status-card {
        margin-top: 1.8rem;
        padding: 12px 14px;
        background: rgba(20, 26, 50, 0.8);
        border: 1px solid rgba(130, 117, 255, 0.16);
        border-radius: 10px;
    }
    .status-card-header {
        font-size: 0.68rem;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: #A2AAC7;
        font-weight: 600;
        margin-bottom: 5px;
    }
    .status-card-body {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 0.85rem;
        font-weight: 600;
        color: #35D49A;
    }
    .pulsing-emerald-dot {
        width: 8px;
        height: 8px;
        background-color: #35D49A;
        border-radius: 50%;
        box-shadow: 0 0 8px #35D49A;
        animation: pulseDot 2s infinite;
    }

    /* Developer Profile Card in Sidebar */
    .developer-sidebar-card {
        margin-top: 1rem;
        padding: 12px 14px;
        background: rgba(27, 34, 64, 0.7);
        border: 1px solid rgba(130, 117, 255, 0.16);
        border-radius: 10px;
    }
    .developer-label {
        font-size: 0.66rem;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: #8275FF;
        font-weight: 600;
        margin-bottom: 3px;
    }
    .developer-name {
        font-size: 0.88rem;
        font-weight: 600;
        color: #F4F5FF;
    }
    .developer-role {
        font-size: 0.75rem;
        color: #A2AAC7;
    }

    /* Expanders & Tabs */
    [data-testid="stExpander"] {
        background: rgba(20, 26, 50, 0.7) !important;
        border: 1px solid rgba(130, 117, 255, 0.16) !important;
        border-radius: 10px !important;
    }
    button[data-baseweb="tab"] {
        color: #A2AAC7 !important;
        font-weight: 500 !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #8275FF !important;
        font-weight: 600 !important;
        border-bottom-color: #8275FF !important;
    }

    /* Page Bottom Universal Footer */
    .app-footer {
        margin-top: 3.5rem;
        padding-top: 1.4rem;
        border-top: 1px solid rgba(130, 117, 255, 0.14);
        text-align: center;
        font-size: 0.82rem;
        color: #A2AAC7;
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 12px;
    }
    .app-footer strong {
        color: #F4F5FF;
        font-weight: 600;
    }

    /* Main Block Container */
    .block-container {
        padding-top: 1rem;
        padding-bottom: 3rem;
        max-width: 1280px;
        position: relative;
        z-index: 1;
    }
</style>

<!-- Non-interactive Deep Ambient Background Layer -->
<div class="ambient-universe">
    <div class="ambient-orb orb-1"></div>
    <div class="ambient-orb orb-2"></div>
    <div class="ambient-orb orb-3"></div>
    <div class="floating-ring ring-1"></div>
    <div class="floating-ring ring-2"></div>
</div>
""", unsafe_allow_html=True)


def ensure_system_initialized():
    """Initializes SQLite database and seeds records if freshly launched."""
    init_db()
    with SessionLocal() as db:
        if db.query(Booking).count() == 0:
            generate_seed_data(db)


def render_top_header(title: str, subtitle: str):
    """Renders a sleek, translucent command bar with the official TravelResolve brandmark."""
    brandmark = render_header_brandmark()
    st.markdown(f"""
    <div class="hero-header top-header-bar">
        <div class="hero-header__content">
            {brandmark}
            <div class="hero-header__text">
                <div class="hero-header__title brand-title">{title}</div>
                <div class="hero-header__subtitle brand-tagline">{subtitle}</div>
            </div>
        </div>
        <div class="hero-header__badges header-right-pills">
            <div class="status-pill">
                <span class="status-dot"></span>
                Operational
            </div>
            <div class="developer-pill">
                ◈ Keyura Motegaonkar
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_footer():
    """Renders the official signature footer."""
    st.markdown("""
    <div class="app-footer">
        <span>TravelResolve AI Operations Platform</span>
        <span>•</span>
        <span>Developed by <strong>Keyura Motegaonkar</strong></span>
    </div>
    """, unsafe_allow_html=True)


NAV_ITEMS = [
    "◈ Overview",
    "✈ Ticket Workspace",
    "⌖ Booking Explorer",
    "◎ Execution Trace",
    "✓ Review Queue",
    "◉ Quality Lab",
    "↗ Performance & Benchmarks",
]


def main():
    ensure_system_initialized()

    # Session State for interactive inter-page navigation
    if "nav_menu" not in st.session_state:
        st.session_state.nav_menu = "◈ Overview"

    # Sidebar Navigation Panel
    with st.sidebar:
        # Render the official compact vector logo at the top of the sidebar
        render_sidebar_branding()

        current_idx = NAV_ITEMS.index(st.session_state.nav_menu) if st.session_state.nav_menu in NAV_ITEMS else 0
        menu = st.radio(
            "Navigation Menu",
            NAV_ITEMS,
            index=current_idx,
            label_visibility="collapsed"
        )
        st.session_state.nav_menu = menu

        st.markdown("---")

        # System Status Card
        st.markdown("""
        <div class="sidebar-status-card">
            <div class="status-card-header">SYSTEM STATUS</div>
            <div class="status-card-body">
                <span class="pulsing-emerald-dot"></span>
                Operational
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Developer Attribution
        st.markdown("""
        <div class="developer-sidebar-card">
            <div class="developer-label">LEAD AI ENGINEER</div>
            <div class="developer-name">Keyura Motegaonkar</div>
            <div class="developer-role">Architecture & Workflows</div>
        </div>
        """, unsafe_allow_html=True)

    # Route to selected page with contextual headers
    if menu == "◈ Overview":
        render_top_header("AI Operations Command Center", "Live inquiry volumes, autonomous resolution rates, and transit workflow feed.")
        render_dashboard()
    elif menu == "✈ Ticket Workspace":
        render_top_header("Support Ticket Workspace", "Receive traveler inquiries, verify reservations in real-time, and run deterministic policy audits.")
        render_ticket_workspace()
    elif menu == "⌖ Booking Explorer":
        render_top_header("Bookings Directory", "Search customer reservations, inspect fare terms, and evaluate real-time cancellation calculations.")
        render_booking_explorer()
    elif menu == "◎ Execution Trace":
        render_top_header("Agent Execution Trace & Audit Log", "Inspect state transitions, policy retrieval, auditor checks, and routing decisions across each DAG node.")
        render_execution_trace()
    elif menu == "✓ Review Queue":
        render_top_header("Supervisor Review Queue", "Inspect tickets flagged for supervisory policy review, unauthorized rate overrides, or financial exposure.")
        render_review_queue()
    elif menu == "◉ Quality Lab":
        render_top_header("Quality Lab & Model Diagnostics", "Evaluate intent classification precision/recall, confusion matrix, and deterministic auditor verification rules.")
        render_quality_lab()
    elif menu == "↗ Performance & Benchmarks":
        render_top_header("Performance & System Benchmarks", "Quantitative architectural comparison across 100 standardized test cases evaluating Grounding, Policy Compliance, and Safety Escalation.")
        render_benchmarks()

    # Universal Footer
    render_footer()


if __name__ == "__main__":
    main()
