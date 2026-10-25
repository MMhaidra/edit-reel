#!/usr/bin/env python3
"""
generate_expanded_icons.py - Generates an extensive suite of high-contrast icons
and emotional badges across Academia, Science, Finance, Tech, AI, and Reactions.
"""

import os
import subprocess
from pathlib import Path

SKILL_ICON_DIR = Path(__file__).resolve().parent.parent / "motion_library" / "icons"
PROJECT_ICON_DIR = Path.home() / "Desktop" / "projects" / "reels_IG" / "motion_assets" / "icons"

SKILL_ICON_DIR.mkdir(parents=True, exist_ok=True)
PROJECT_ICON_DIR.mkdir(parents=True, exist_ok=True)

# Color constants
CYAN = "#00F0FF"
MINT = "#00FFA3"
GOLD = "#FFD700"
CORAL = "#FF3B30"
VIOLET = "#A855F7"
BLUE = "#3B82F6"
DEEP_CYAN = "#06B6D4"
ORANGE = "#FF9500"
WHITE = "#FFFFFF"

# SVG definitions (viewBox 0 0 24 24, stroke-width 2.2, clean vectors)
ICONS_DEF = {
    # Academia & Science
    "flask": {
        "color": CYAN,
        "svg": '<path d="M9 3h6v3l4 8.5A3 3 0 0 1 16.3 19H7.7A3 3 0 0 1 5 14.5L9 6V3Z"/><line x1="9" y1="6" x2="15" y2="6"/><line x1="7" y1="14" x2="17" y2="14"/>'
    },
    "test-tube": {
        "color": MINT,
        "svg": '<path d="M14.5 2v17.5c0 1.4-1.1 2.5-2.5 2.5s-2.5-1.1-2.5-2.5V2"/><line x1="8.5" y1="2" x2="15.5" y2="2"/><line x1="9.5" y1="12" x2="14.5" y2="12"/>'
    },
    "citation": {
        "color": GOLD,
        "svg": '<path d="M3 21c3 0 7-1 7-8V5c0-1.1-.9-2-2-2H4c-1.1 0-2 .9-2 2v6c0 1.1.9 2 2 2 0 4-1 6-1 8Z"/><path d="M15 21c3 0 7-1 7-8V5c0-1.1-.9-2-2-2h-4c-1.1 0-2 .9-2 2v6c0 1.1.9 2 2 2 0 4-1 6-1 8Z"/>'
    },
    "file-text": {
        "color": CYAN,
        "svg": '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/>'
    },
    "binary": {
        "color": CYAN,
        "svg": '<rect x="14" y="14" width="4" height="6" rx="2"/><rect x="6" y="4" width="4" height="6" rx="2"/><path d="M6 20h4"/><path d="M14 10h4"/><path d="M6 14h2v6"/><path d="M14 4h2v6"/>'
    },
    "sigma": {
        "color": GOLD,
        "svg": '<path d="M18 4H6l7 8-7 8h12"/><line x1="6" y1="4" x2="18" y2="4"/><line x1="6" y1="20" x2="18" y2="20"/>'
    },
    "globe": {
        "color": BLUE,
        "svg": '<circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>'
    },
    "bookmark": {
        "color": VIOLET,
        "svg": '<path d="m19 21-7-4-7 4V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2v16z"/>'
    },
    "medal": {
        "color": GOLD,
        "svg": '<circle cx="12" cy="15" r="6"/><path d="M8.21 13.89 7 2l5 3 5-3-1.21 11.89"/>'
    },
    "layers": {
        "color": CYAN,
        "svg": '<polygon points="12 2 2 7 12 12 22 7 12 2"/><polyline points="2 17 12 22 22 17"/><polyline points="2 12 12 17 22 12"/>'
    },

    # Emotions & High-Impact Visual Anchors
    "mind-blown": {
        "color": GOLD,
        "svg": '<circle cx="12" cy="14" r="8"/><line x1="9" y1="13" x2="9.01" y2="13"/><line x1="15" y1="13" x2="15.01" y2="13"/><circle cx="12" cy="17" r="2"/><path d="M6 8c-1-2 0-5 3-5 2 0 3 2 3 2s1-2 3-2c3 0 4 3 3 5"/><line x1="12" y1="2" x2="12" y2="4"/><line x1="4" y1="4" x2="6" y2="6"/><line x1="20" y1="4" x2="18" y2="6"/>'
    },
    "skull": {
        "color": CORAL,
        "svg": '<path d="m12.5 17-.5-1-.5 1h1z"/><path d="M15 22a1 1 0 0 0 1-1v-1a2 2 0 0 0 1.56-3.25A8 8 0 1 0 6.44 16.75 2 2 0 0 0 8 20v1a1 1 0 0 0 1 1z"/><circle cx="9" cy="12" r="1"/><circle cx="15" cy="12" r="1"/>'
    },
    "trophy": {
        "color": GOLD,
        "svg": '<path d="M6 9H4.5a2.5 2.5 0 0 1 0-5H6"/><path d="M18 9h1.5a2.5 2.5 0 0 0 0-5H18"/><path d="M4 22h16"/><path d="M10 14.66V17c0 .55-.45.98-.97 1.21C7.85 18.75 7 20.24 7 22"/><path d="M14 14.66V17c0 .55.45.98.97 1.21C16.15 18.75 17 20.24 17 22"/><path d="M18 2H6v7a6 6 0 0 0 12 0V2Z"/>'
    },
    "star": {
        "color": GOLD,
        "svg": '<polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>'
    },
    "heart": {
        "color": CORAL,
        "svg": '<path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z"/>'
    },
    "eye": {
        "color": CYAN,
        "svg": '<path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z"/><circle cx="12" cy="12" r="3"/>'
    },
    "crosshair": {
        "color": CYAN,
        "svg": '<circle cx="12" cy="12" r="10"/><line x1="22" y1="12" x2="18" y2="12"/><line x1="6" y1="12" x2="2" y2="12"/><line x1="12" y1="6" x2="12" y2="2"/><line x1="12" y1="22" x2="12" y2="18"/>'
    },
    "compass": {
        "color": MINT,
        "svg": '<circle cx="12" cy="12" r="10"/><polygon points="16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76"/>'
    },
    "infinity": {
        "color": VIOLET,
        "svg": '<path d="M18.178 8c5.096 0 5.096 8 0 8-5.095 0-7.267-8-12.356-8-5.096 0-5.096 8 0 8 5.09 0 7.261-8 12.356-8Z"/>'
    },
    "bomb": {
        "color": CORAL,
        "svg": '<circle cx="11" cy="13" r="9"/><path d="m19.5 4.5-3.5 3.5"/><path d="m18 1.5 2 2"/><path d="m21.5 4-2 2"/><path d="m21 2-4 4"/>'
    },
    "shield-lock": {
        "color": BLUE,
        "svg": '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10"/><rect x="9.5" y="10" width="5" height="4" rx="1"/><path d="M10.5 10V8.5a1.5 1.5 0 0 1 3 0V10"/>'
    },

    # Financial & Market & Tech Connectors
    "wallet-cards": {
        "color": MINT,
        "svg": '<rect width="18" height="18" x="3" y="3" rx="2"/><path d="M3 9a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2"/><line x1="3" y1="11" x2="21" y2="11"/><circle cx="16.5" cy="16.5" r="1.5"/>'
    },
    "receipt": {
        "color": GOLD,
        "svg": '<path d="M4 2v20l2-1 2 1 2-1 2 1 2-1 2 1 2-1 2 1V2l-2 1-2-1-2 1-2-1-2 1-2-1-2 1Z"/><path d="M16 8h-6a2 2 0 1 0 0 4h4a2 2 0 1 1 0 4H8"/><path d="M12 6v2m0 8v2"/>'
    },
    "banknote": {
        "color": MINT,
        "svg": '<rect width="20" height="12" x="2" y="6" rx="2"/><circle cx="12" cy="12" r="2"/><path d="M6 12h.01M18 12h.01"/>'
    },
    "piggy-bank": {
        "color": GOLD,
        "svg": '<path d="M19 5c-1.5 0-2.8 1.4-3 2-3.5-1.5-11-.3-11 5 0 1.8 0 3 2 4.5V20h4v-2h3v2h4v-4c1-.5 1.7-1 2-2h2v-4h-2c0-1-.5-1.5-1-2V5z"/><path d="M16 9h.01"/><path d="M2 10s1.5-1 3-1"/>'
    },
    "gem": {
        "color": CYAN,
        "svg": '<path d="M6 3h12l4 6-10 13L2 9Z"/><path d="M11 3 8 9l4 13 4-13-3-6"/><path d="M2 9h20"/>'
    },
    "database": {
        "color": CYAN,
        "svg": '<ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/><path d="M3 12c0 1.66 4 3 9 3s9-1.34 9-3"/>'
    },
    "cloud": {
        "color": BLUE,
        "svg": '<path d="M17.5 19H9a7 7 0 1 1 6.71-9h1.79a4.5 4.5 0 1 1 0 9Z"/>'
    },
    "git-branch": {
        "color": VIOLET,
        "svg": '<line x1="6" y1="3" x2="6" y2="15"/><circle cx="18" cy="6" r="3"/><circle cx="6" cy="18" r="3"/><path d="M18 9a9 9 0 0 1-9 9"/>'
    },
    "arrow-up-right": {
        "color": MINT,
        "svg": '<line x1="7" y1="17" x2="17" y2="7"/><polyline points="7 7 17 7 17 17"/>'
    },
    "arrow-right": {
        "color": CYAN,
        "svg": '<line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/>'
    },
    "check-circle": {
        "color": MINT,
        "svg": '<path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/>'
    },
    "x-circle": {
        "color": CORAL,
        "svg": '<circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/>'
    }
}

print(f"Generating {len(ICONS_DEF)} new icons...")

for name, meta in ICONS_DEF.items():
    color = meta["color"]
    svg_body = meta["svg"]
    svg_content = f'''<svg
  xmlns="http://www.w3.org/2000/svg"
  width="512"
  height="512"
  viewBox="0 0 24 24"
  fill="none"
  stroke="{color}"
  stroke-width="2.2"
  stroke-linecap="round"
  stroke-linejoin="round"
>
  {svg_body}
</svg>
'''
    # Save SVG to skill icon dir
    svg_path = SKILL_ICON_DIR / f"{name}.svg"
    with open(svg_path, "w") as f:
        f.write(svg_content)
    
    # Mirror SVG to project icon dir
    with open(PROJECT_ICON_DIR / f"{name}.svg", "w") as f:
        f.write(svg_content)

# Now rasterize all new SVGs to 512x512 transparent PNGs using qlmanage
print("Rasterizing SVGs with qlmanage...")
for name in ICONS_DEF.keys():
    svg_file = SKILL_ICON_DIR / f"{name}.svg"
    out_dir = SKILL_ICON_DIR
    subprocess.run(["qlmanage", "-t", "-s", "512", "-o", str(out_dir), str(svg_file)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # qlmanage names it {name}.svg.png
    gen_png = out_dir / f"{name}.svg.png"
    target_png = out_dir / f"{name}.png"
    if gen_png.exists():
        gen_png.rename(target_png)
    
    # Mirror PNG to project icons
    if target_png.exists():
        with open(target_png, "rb") as src, open(PROJECT_ICON_DIR / f"{name}.png", "wb") as dst:
            dst.write(src.read())

print(f"Successfully generated and mirrored {len(ICONS_DEF)} new icons!")
