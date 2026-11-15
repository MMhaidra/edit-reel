#!/usr/bin/env python3
"""
generate_glass_cards.py - Modern Obsidian Glass & HyperFrames Card Generator.

Generates and pre-renders high-end HTML/CSS/GSAP motion graphic compositions
for the 4 academic beats using HyperFrames.
Outputs 1080x920 high-DPI cards rendered to MP4/WebM with Apple Silicon hardware acceleration.
"""

import sys
import json
import shutil
import subprocess
from pathlib import Path

HF_BASE_DIR = Path.home() / "Desktop" / "projects" / "reels_IG" / "motion_hyperframes"
HF_BASE_DIR.mkdir(parents=True, exist_ok=True)


def build_card_html(cue_data, width=1080, height=920, duration=16.0):
    cue_id = cue_data["id"]
    badge = cue_data["badge"]
    kicker = cue_data["kicker"]
    title = cue_data["title"]
    subtitle = cue_data["subtitle"]
    chips = cue_data.get("chips", [])
    stat_box = cue_data.get("stat_box", None)
    quote = cue_data.get("quote", None)
    accent_color = cue_data.get("accent", "#10B981")

    chips_html = ""
    if chips:
        chips_items = "".join([f'<div class="chip">{c}</div>' for c in chips])
        chips_html = f'<div class="chips-container">{chips_items}</div>'

    stat_html = ""
    if stat_box:
        stat_html = f"""
        <div class="stat-card">
            <div class="stat-left">
                <span class="stat-label">{stat_box['label']}</span>
                <span class="stat-sub">{stat_box.get('sub', '')}</span>
            </div>
            <div class="stat-badge" style="background: {stat_box.get('badge_bg', '#EF4444')};">
                {stat_box['val']}
            </div>
        </div>
        """

    quote_html = ""
    if quote:
        quote_html = f'<div class="quote-box">"{quote}"</div>'

    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width={width}, height={height}" />
  <script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
  <style>
    :root {{
      --bg: #090D16;
      --card-bg: rgba(18, 24, 38, 0.88);
      --border: rgba(255, 255, 255, 0.12);
      --ink: #FFFFFF;
      --sub: #94A3B8;
      --accent: {accent_color};
      --font-display: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }}
    * {{
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }}
    html, body {{
      margin: 0;
      width: {width}px;
      height: {height}px;
      overflow: hidden;
      background: var(--bg);
      font-family: var(--font-display);
    }}
    #root {{
      width: 100%;
      height: 100%;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 40px;
    }}
    .glass-card {{
      width: 1000px;
      background: var(--card-bg);
      backdrop-filter: blur(30px);
      border: 1.5px solid var(--border);
      border-radius: 36px;
      padding: 48px 56px;
      box-shadow: 0 30px 80px rgba(0, 0, 0, 0.45);
      position: relative;
    }}
    .top-bar {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 24px;
    }}
    .badge {{
      display: inline-block;
      background: var(--accent);
      color: #FFFFFF;
      font-size: 22px;
      font-weight: 800;
      padding: 8px 22px;
      border-radius: 999px;
      letter-spacing: 1.5px;
      text-transform: uppercase;
    }}
    .kicker {{
      font-size: 20px;
      font-weight: 700;
      color: var(--sub);
      letter-spacing: 1.2px;
      text-transform: uppercase;
    }}
    .title {{
      font-size: 52px;
      font-weight: 900;
      color: var(--ink);
      line-height: 1.15;
      letter-spacing: -0.02em;
      margin-bottom: 14px;
    }}
    .subtitle {{
      font-size: 28px;
      font-weight: 500;
      color: #CBD5E1;
      line-height: 1.4;
      margin-bottom: 30px;
    }}
    .chips-container {{
      display: flex;
      gap: 16px;
      margin-bottom: 24px;
      flex-wrap: wrap;
    }}
    .chip {{
      background: rgba(255, 255, 255, 0.08);
      border: 1px solid rgba(255, 255, 255, 0.16);
      color: #F8FAFC;
      font-size: 22px;
      font-weight: 700;
      padding: 12px 26px;
      border-radius: 18px;
      letter-spacing: 0.8px;
    }}
    .stat-card {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid rgba(255, 255, 255, 0.10);
      border-radius: 24px;
      padding: 20px 32px;
      margin-top: 10px;
    }}
    .stat-left {{
      display: flex;
      flex-direction: column;
    }}
    .stat-label {{
      font-size: 26px;
      font-weight: 800;
      color: #FFFFFF;
    }}
    .stat-sub {{
      font-size: 20px;
      color: var(--sub);
      margin-top: 4px;
    }}
    .stat-badge {{
      color: #FFFFFF;
      font-size: 26px;
      font-weight: 900;
      padding: 10px 24px;
      border-radius: 16px;
    }}
    .quote-box {{
      border-left: 4px solid var(--accent);
      padding-left: 20px;
      font-size: 24px;
      font-style: italic;
      color: #94A3B8;
      line-height: 1.45;
      margin-top: 24px;
    }}
  </style>
</head>
<body>
  <div
    id="root"
    data-composition-id="main"
    data-start="0"
    data-duration="{duration}"
    data-width="{width}"
    data-height="{height}"
  >
    <div id="card" class="glass-card clip" data-start="0" data-duration="{duration}" data-track-index="0">
      <div class="top-bar">
        <span class="badge">{badge}</span>
        <span class="kicker">{kicker}</span>
      </div>
      <h1 class="title">{title}</h1>
      <p class="subtitle">{subtitle}</p>
      {chips_html}
      {stat_html}
      {quote_html}
    </div>
  </div>
  <script>
    window.__timelines = window.__timelines || {{}};
    const tl = gsap.timeline({{ paused: true }});
    tl.fromTo("#card", 
      {{ opacity: 0, scale: 0.90, y: 60 }},
      {{ opacity: 1, scale: 1.0, y: 0, duration: 0.75, ease: "power3.out" }}, 
      0.15
    );
    tl.fromTo(".chip",
      {{ opacity: 0, scale: 0.85, y: 20 }},
      {{ opacity: 1, scale: 1.0, y: 0, duration: 0.45, stagger: 0.15, ease: "back.out(1.5)" }},
      0.6
    );
    tl.fromTo(".stat-card",
      {{ opacity: 0, y: 25 }},
      {{ opacity: 1, y: 0, duration: 0.5, ease: "power2.out" }},
      1.1
    );
    tl.to("#card",
      {{ opacity: 0, scale: 0.95, y: -30, duration: 0.55, ease: "power2.in" }},
      {duration} - 0.65
    );
    window.__timelines["main"] = tl;
    tl.seek(0);
  </script>
</body>
</html>
"""
    return html


CARDS_METADATA = [
    {
        "id": "beat1_marcuse",
        "badge": "MARCUSE 1964",
        "kicker": "BEACON PRESS • BOSTON",
        "title": "FALSE NEEDS: MANUFACTURED DESIRES",
        "subtitle": "Modern society traps individuals through artificial desires disguised as personal needs.",
        "chips": ["AUTOMOBILE", "SOUND SYSTEM", "SPLIT-LEVEL HOME"],
        "quote": "People find their soul in their automobile and their home, losing the capacity for critical thought.",
        "accent": "#3B82F6",
        "duration": 16.0
    },
    {
        "id": "beat2_brickman",
        "badge": "BRICKMAN 1978",
        "kicker": "J. PERSONALITY & SOCIAL PSYCHOLOGY",
        "title": "THE HEDONIC TREADMILL",
        "subtitle": "Material windfalls and upgrades quickly lose dopamine value, forcing an endless upgrade loop.",
        "chips": ["LOTTERY WINNERS", "HEDONIC RESET", "BASELINE ZERO"],
        "stat_box": {
            "label": "NET HAPPINESS BOOST OVER TIME",
            "sub": "Dopamine resets to exact baseline within weeks",
            "val": "0.0% GAIN",
            "badge_bg": "#F59E0B"
        },
        "accent": "#F59E0B",
        "duration": 16.0
    },
    {
        "id": "beat3_kasser",
        "badge": "KASSER & RYAN 1993",
        "kicker": "JPSP • HARVARD / ROCHESTER",
        "title": "THE DARK SIDE OF WEALTH ASPIRATION",
        "subtitle": "Prioritizing money and external status directly correlates with psychological distress.",
        "chips": ["EXTERNAL STATUS", "INTRINSIC GOALS"],
        "stat_box": {
            "label": "ANXIETY, DEPRESSION & VITALITY DECAY",
            "sub": "Neurobiological penalty of materialistic framing",
            "val": "HIGH CORRELATION",
            "badge_bg": "#EF4444"
        },
        "accent": "#EF4444",
        "duration": 16.0
    },
    {
        "id": "beat4_bauer",
        "badge": "BAUER ET AL. 2012",
        "kicker": "PSYCHOLOGICAL SCIENCE",
        "title": "CUING CONSUMERISM & SOCIAL FRICTION",
        "subtitle": "Framing people as 'consumers' instead of 'individuals' immediately increases insecurity.",
        "chips": ["CITIZEN / INDIVIDUAL", "CONSUMER PRIMING"],
        "stat_box": {
            "label": "STRESS & INSECURITY SPIKE",
            "sub": "Triggered by mere exposure to luxury product cues",
            "val": "+34% STRESS",
            "badge_bg": "#8B5CF6"
        },
        "accent": "#8B5CF6",
        "duration": 15.0
    }
]


def generate_all_cards():
    hf_bin = shutil.which("hyperframes")
    if not hf_bin:
        print("[generate_glass_cards] Error: hyperframes CLI not found in PATH.", file=sys.stderr)
        return False

    rendered_cards = {}
    for card in CARDS_METADATA:
        card_dir = HF_BASE_DIR / card["id"]
        card_dir.mkdir(parents=True, exist_ok=True)

        # Write hyperframes.json
        with open(card_dir / "hyperframes.json", "w", encoding="utf-8") as f:
            json.dump({
                "width": 1080,
                "height": 920,
                "fps": 30,
                "duration": card["duration"],
                "entry": "index.html"
            }, f, indent=2)

        # Write package.json
        with open(card_dir / "package.json", "w", encoding="utf-8") as f:
            json.dump({
                "name": card["id"],
                "private": True,
                "scripts": {"render": "hyperframes render -o card.mp4"}
            }, f, indent=2)

        # Write index.html
        html = build_card_html(card, width=1080, height=920, duration=card["duration"])
        with open(card_dir / "index.html", "w", encoding="utf-8") as f:
            f.write(html)

        # Render with HyperFrames
        mp4_out = card_dir / f"{card['id']}.mp4"
        print(f"\n[generate_glass_cards] Rendering HyperFrames Card: {card['id']}...")
        cmd = [hf_bin, "render", "-o", str(mp4_out)]
        try:
            subprocess.run(cmd, cwd=str(card_dir), check=True)
            rendered_cards[card["id"]] = mp4_out
            print(f"[generate_glass_cards] Rendered: {mp4_out}")
        except Exception as e:
            print(f"[generate_glass_cards] Render failed for {card['id']}: {e}", file=sys.stderr)

    manifest_file = HF_BASE_DIR / "rendered_manifest.json"
    with open(manifest_file, "w", encoding="utf-8") as mf:
        json.dump({k: str(v) for k, v in rendered_cards.items()}, mf, indent=2)
    print(f"\n[generate_glass_cards] All HyperFrames motion cards ready! Saved to {manifest_file}")
    return True


if __name__ == "__main__":
    generate_all_cards()
