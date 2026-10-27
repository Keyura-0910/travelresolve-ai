"""
Script to generate official vector SVG logo assets for TravelResolve.
Redesigned with prominent, well-balanced proportions:
  - Brand mark: 48-52 px
  - Wordmark: 22 px
  - Tagline: 11 px
  - Tight bounding boxes (no wasted transparent padding)
Developed by Keyura Motegaonkar.
"""

from pathlib import Path

ASSETS_DIR = Path(__file__).resolve().parent

ICON_ONLY_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="64" height="64" fill="none">
  <defs>
    <linearGradient id="trv-grad-p" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#38C9FF"/>
      <stop offset="45%" stop-color="#8275FF"/>
      <stop offset="100%" stop-color="#6352FF"/>
    </linearGradient>
    <linearGradient id="trv-grad-s" x1="0%" y1="100%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#8275FF"/>
      <stop offset="100%" stop-color="#38C9FF"/>
    </linearGradient>
    <radialGradient id="trv-glow-rad" cx="50%" cy="38%" r="52%">
      <stop offset="0%" stop-color="#8275FF" stop-opacity="0.45"/>
      <stop offset="100%" stop-color="#8275FF" stop-opacity="0"/>
    </radialGradient>
    <filter id="trv-shdw" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="2.5" stdDeviation="3" flood-color="#8275FF" flood-opacity="0.45"/>
    </filter>
  </defs>
  
  <!-- Subtle Ambient Glow -->
  <circle cx="32" cy="27" r="27" fill="url(#trv-glow-rad)"/>

  <!-- Orbital Travel Route Arc -->
  <path d="M 8 38 C 6 22, 18 8, 32 8 C 48 8, 58 20, 56 34 C 54 44, 42 54, 30 54 C 20 54, 12 46, 13 38" 
        stroke="url(#trv-grad-p)" stroke-width="3" stroke-linecap="round" stroke-dasharray="68 18" opacity="0.6"/>

  <!-- Aerodynamic Travel Location Pin -->
  <path d="M 32 5 C 20 5 12 14.5 12 25.5 C 12 37.5 28 53.5 32 58 C 36 53.5 52 37.5 52 25.5 C 52 14.5 44 5 32 5 Z" 
        fill="none" stroke="url(#trv-grad-p)" stroke-width="3.8" stroke-linejoin="round" filter="url(#trv-shdw)"/>

  <!-- Dynamic Transit Route Vector (Ascending Resolution Path) -->
  <path d="M 20 34 Q 31 18 47 13" stroke="#38C9FF" stroke-width="2.8" stroke-linecap="round"/>
  <polygon points="49,13 42,12 45,18" fill="#38C9FF"/>

  <!-- Central AI Sparkle / Resolution Core -->
  <path d="M 32 17 L 34.5 22.8 L 40.5 25 L 34.5 27.2 L 32 33 L 29.5 27.2 L 23.5 25 L 29.5 22.8 Z" 
        fill="url(#trv-grad-s)"/>
  
  <!-- Core Brilliant Node -->
  <circle cx="32" cy="25" r="2.4" fill="#FFFFFF"/>
</svg>"""

COMPACT_LOGO_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 255 56" width="255" height="56" fill="none">
  <defs>
    <linearGradient id="trv-c-prim" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#38C9FF"/>
      <stop offset="45%" stop-color="#8275FF"/>
      <stop offset="100%" stop-color="#6352FF"/>
    </linearGradient>
    <linearGradient id="trv-c-txt" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#8275FF"/>
      <stop offset="100%" stop-color="#38C9FF"/>
    </linearGradient>
    <filter id="trv-c-shdw" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="2" stdDeviation="2.5" flood-color="#8275FF" flood-opacity="0.4"/>
    </filter>
  </defs>

  <!-- Prominent 48x48 Icon Mark -->
  <g transform="translate(2, 4) scale(0.84)">
    <circle cx="30" cy="27" r="24" fill="#8275FF" fill-opacity="0.18"/>
    <path d="M 9 38 C 7 23, 18 9, 31 9 C 46 9, 56 20, 54 33 C 52 43, 41 53, 29 53 C 19 53, 12 45, 13 38" 
          stroke="url(#trv-c-prim)" stroke-width="3" stroke-linecap="round" stroke-dasharray="64 16" opacity="0.65"/>
    <path d="M 31 6 C 20 6 12 15 12 25.5 C 12 37 27 52 31 56 C 35 52 50 37 50 25.5 C 50 15 42 6 31 6 Z" 
          fill="none" stroke="url(#trv-c-prim)" stroke-width="3.8" stroke-linejoin="round" filter="url(#trv-c-shdw)"/>
    <path d="M 20 34 Q 30 19 45 14" stroke="#38C9FF" stroke-width="2.8" stroke-linecap="round"/>
    <polygon points="47,14 41,13 44,18" fill="#38C9FF"/>
    <path d="M 31 18 L 33.3 23.2 L 39 25.2 L 33.3 27.2 L 31 32.5 L 28.7 27.2 L 23 25.2 L 28.7 23.2 Z" fill="url(#trv-c-txt)"/>
    <circle cx="31" cy="25.2" r="2.2" fill="#FFFFFF"/>
  </g>

  <!-- Distinctive Wordmark Text (22px) -->
  <g transform="translate(56, 30)">
    <text font-family="'Inter', -apple-system, sans-serif" font-weight="800" font-size="22" fill="#F4F5FF" letter-spacing="-0.35">Travel<tspan fill="url(#trv-c-txt)">Resolve</tspan></text>
  </g>

  <!-- Clear Supporting Tagline (11px) -->
  <g transform="translate(57, 46)">
    <text font-family="'Inter', -apple-system, sans-serif" font-weight="600" font-size="10.5" fill="#A2AAC7" letter-spacing="1.2">AI-POWERED OPERATIONS</text>
  </g>
</svg>"""

PRIMARY_LOGO_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 310 64" width="310" height="64" fill="none">
  <defs>
    <linearGradient id="trv-p-prim" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#38C9FF"/>
      <stop offset="45%" stop-color="#8275FF"/>
      <stop offset="100%" stop-color="#6352FF"/>
    </linearGradient>
    <linearGradient id="trv-p-txt" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#8275FF"/>
      <stop offset="100%" stop-color="#38C9FF"/>
    </linearGradient>
    <filter id="trv-p-shdw" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="3" stdDeviation="3.5" flood-color="#8275FF" flood-opacity="0.4"/>
    </filter>
  </defs>

  <!-- Prominent 52x52 Icon Mark -->
  <g transform="translate(4, 6) scale(0.92)">
    <circle cx="32" cy="27" r="26" fill="#8275FF" fill-opacity="0.2"/>
    <path d="M 8 38 C 6 22, 18 8, 32 8 C 48 8, 58 20, 56 34 C 54 44, 42 54, 30 54 C 20 54, 12 46, 13 38" 
          stroke="url(#trv-p-prim)" stroke-width="3" stroke-linecap="round" stroke-dasharray="68 18" opacity="0.6"/>
    <path d="M 32 5 C 20 5 12 14.5 12 25.5 C 12 37.5 28 53.5 32 58 C 36 53.5 52 37.5 52 25.5 C 52 14.5 44 5 32 5 Z" 
          fill="none" stroke="url(#trv-p-prim)" stroke-width="3.8" stroke-linejoin="round" filter="url(#trv-p-shdw)"/>
    <path d="M 20 34 Q 31 18 47 13" stroke="#38C9FF" stroke-width="2.8" stroke-linecap="round"/>
    <polygon points="49,13 42,12 45,18" fill="#38C9FF"/>
    <path d="M 32 17 L 34.5 22.8 L 40.5 25 L 34.5 27.2 L 32 33 L 29.5 27.2 L 23.5 25 L 29.5 22.8 Z" fill="url(#trv-p-txt)"/>
    <circle cx="32" cy="25" r="2.4" fill="#FFFFFF"/>
  </g>

  <!-- Wordmark Text (26px) -->
  <g transform="translate(68, 36)">
    <text font-family="'Inter', -apple-system, sans-serif" font-weight="800" font-size="26" fill="#F4F5FF" letter-spacing="-0.4">Travel<tspan fill="url(#trv-p-txt)">Resolve</tspan></text>
  </g>

  <!-- Tagline (11px) -->
  <g transform="translate(69, 52)">
    <text font-family="'Inter', -apple-system, sans-serif" font-weight="600" font-size="11" fill="#A2AAC7" letter-spacing="2.2">AI OPERATIONS PLATFORM</text>
  </g>
</svg>"""

MONOCHROME_LOGO_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="64" height="64" fill="none">
  <path d="M 8 38 C 6 22, 18 8, 32 8 C 48 8, 58 20, 56 34 C 54 44, 42 54, 30 54 C 20 54, 12 46, 13 38" 
        stroke="#FFFFFF" stroke-width="2.8" stroke-linecap="round" stroke-dasharray="68 18" opacity="0.6"/>
  <path d="M 32 5 C 20 5 12 14.5 12 25.5 C 12 37.5 28 53.5 32 58 C 36 53.5 52 37.5 52 25.5 C 52 14.5 44 5 32 5 Z" 
        fill="none" stroke="#FFFFFF" stroke-width="3.8" stroke-linejoin="round"/>
  <path d="M 20 34 Q 31 18 47 13" stroke="#FFFFFF" stroke-width="2.8" stroke-linecap="round"/>
  <polygon points="49,13 42,12 45,18" fill="#FFFFFF"/>
  <path d="M 32 17 L 34.5 22.8 L 40.5 25 L 34.5 27.2 L 32 33 L 29.5 27.2 L 23.5 25 L 29.5 22.8 Z" fill="#FFFFFF"/>
  <circle cx="32" cy="25" r="2.4" fill="#080B18"/>
</svg>"""


def generate_all_logos():
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    
    (ASSETS_DIR / "icon_only.svg").write_text(ICON_ONLY_SVG, encoding="utf-8")
    (ASSETS_DIR / "primary_logo.svg").write_text(PRIMARY_LOGO_SVG, encoding="utf-8")
    (ASSETS_DIR / "compact_logo.svg").write_text(COMPACT_LOGO_SVG, encoding="utf-8")
    (ASSETS_DIR / "monochrome_logo.svg").write_text(MONOCHROME_LOGO_SVG, encoding="utf-8")
    print(f"Generated 4 refined SVG logo assets in {ASSETS_DIR}")


if __name__ == "__main__":
    generate_all_logos()
