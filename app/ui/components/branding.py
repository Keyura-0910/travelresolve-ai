"""
Reusable Brand Identity & Logo Rendering Component for TravelResolve.
Developed by Keyura Motegaonkar.
"""

from pathlib import Path
import streamlit as st

ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"


def get_logo_svg(variant: str = "primary") -> str:
    """Reads and returns the SVG markup for the specified logo variant."""
    filename_map = {
        "primary": "primary_logo.svg",
        "compact": "compact_logo.svg",
        "icon": "icon_only.svg",
        "monochrome": "monochrome_logo.svg",
    }
    file_path = ASSETS_DIR / filename_map.get(variant, "primary_logo.svg")
    if file_path.exists():
        return file_path.read_text(encoding="utf-8")
    return ""


def get_favicon_path() -> str:
    """Returns absolute path to icon_only.svg for page_icon configuration."""
    fav = ASSETS_DIR / "icon_only.svg"
    return str(fav) if fav.exists() else "✈"


def render_sidebar_branding():
    """Renders the official compact logo inside the Streamlit sidebar with 24px padding."""
    svg_code = get_logo_svg("compact")
    st.markdown(f"""
    <div style="padding: 22px 12px 20px 12px; border-bottom: 1px solid rgba(130, 117, 255, 0.16); margin-bottom: 1.4rem;">
        <div style="filter: drop-shadow(0 0 16px rgba(130, 117, 255, 0.28)); display: flex; align-items: center; justify-content: flex-start;">
            {svg_code}
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_header_brandmark():
    """Renders a prominent 38x38 icon mark for the top header bar."""
    svg_code = get_logo_svg("icon")
    return f"""<div style="width: 38px; height: 38px; filter: drop-shadow(0 0 10px rgba(130, 117, 255, 0.4)); flex-shrink: 0; display: flex; align-items: center;">{svg_code}</div>"""
