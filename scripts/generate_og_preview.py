#!/usr/bin/env python3
"""
generate_og_preview.py
Generates a crisp 1200x630 Open Graph (social preview) card for edit-reel.
Optimal for Twitter/X cards, LinkedIn, Discord, Reddit, and GitHub social preview.
"""

from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

W, H = 1200, 630
BG = (13, 17, 23)           # #0D1117 (GitHub Dark)
CARD_BG = (22, 27, 34)      # #161B22
BORDER = (48, 54, 61)       # #30363D
TEXT_MAIN = (240, 246, 252)
TEXT_MUTED = (139, 148, 158)

# Colors
BLUE = (59, 130, 246)
CYAN = (6, 182, 212)
PURPLE = (168, 85, 247)
AMBER = (245, 158, 11)
GREEN = (16, 185, 129)
PINK = (236, 72, 153)

try:
    font_hero = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 46)
    font_subhero = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 22)
    font_tagline = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 16)
    font_badge = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 13)
    font_card_title = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 16)
    font_card_desc = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 13)
except Exception:
    font_hero = font_subhero = font_tagline = font_badge = font_card_title = font_card_desc = ImageFont.load_default()

im = Image.new("RGB", (W, H), BG)
draw = ImageDraw.Draw(im)

# Subtle grid pattern on background
for x in range(0, W, 40):
    draw.line([(x, 0), (x, H)], fill=(20, 24, 32), width=1)
for y in range(0, H, 40):
    draw.line([(0, y), (W, y)], fill=(20, 24, 32), width=1)

# Subtle outer border
draw.rounded_rectangle([12, 12, W - 12, H - 12], radius=16, outline=(36, 41, 48), width=2)

# Top Bar Badge
draw.rounded_rectangle([60, 48, 220, 78], radius=6, fill=(31, 111, 235), outline=None)
draw.text((75, 55), "OPEN-SOURCE AI", fill=(255, 255, 255), font=font_badge)

draw.rounded_rectangle([230, 48, 415, 78], radius=6, fill=(35, 134, 54), outline=None)
draw.text((245, 55), "100% LOCAL & FREE", fill=(255, 255, 255), font=font_badge)

draw.rounded_rectangle([425, 48, 620, 78], radius=6, fill=(137, 87, 229), outline=None)
draw.text((440, 55), "CLAUDE & CURSOR SKILL", fill=(255, 255, 255), font=font_badge)

# Main Title
draw.text((60, 100), "edit-reel", fill=(255, 255, 255), font=font_hero)
draw.text((280, 114), "|  Autonomous AI Video Editor & Auto Subtitles", fill=BLUE, font=font_subhero)

# Subtitle / Pitch
pitch_text = "Transform raw talking-head videos into viral 9:16 vertical Reels & TikToks autonomously."
draw.text((60, 160), pitch_text, fill=TEXT_MAIN, font=font_tagline)

pitch_sub = "Tactile Paper & Objects aesthetic  *  Faster-Whisper speech cutting  *  MediaPipe vision  *  -11.5 LUFS audio"
draw.text((60, 185), pitch_sub, fill=TEXT_MUTED, font=font_tagline)

# 3 Feature Showcase Cards in the middle
cards = [
    {
        "title": "01 | Physical Objects Aesthetic",
        "desc": "Warm paper canvas #E2DDD1, hanging cream price tags on strings, 3D coin stacks, and authentic academic notebook cutoffs with Scotch tape.",
        "col": AMBER,
        "x": 60, "y": 235, "w": 340, "h": 220
    },
    {
        "title": "02 | Word-Level Speech Cutting",
        "desc": "Faster-Whisper millisecond forced alignment. Automatically cuts false starts, stumbles, and pauses while preserving natural cadence.",
        "col": CYAN,
        "x": 430, "y": 235, "w": 340, "h": 220
    },
    {
        "title": "03 | Agentic Coding Integration",
        "desc": "Native skill for Claude Code, Cursor, Windsurf, Codex, and Google Antigravity. Zero-interaction automated video production.",
        "col": PURPLE,
        "x": 800, "y": 235, "w": 340, "h": 220
    }
]

for c in cards:
    x0, y0, w, h = c["x"], c["y"], c["w"], c["h"]
    x1, y1 = x0 + w, y0 + h

    # Card background and border
    draw.rounded_rectangle([x0, y0, x1, y1], radius=12, fill=CARD_BG, outline=BORDER, width=2)
    # Accent top stripe
    draw.rounded_rectangle([x0 + 1, y0 + 1, x1 - 1, y0 + 6], radius=3, fill=c["col"])

    # Title
    draw.text((x0 + 18, y0 + 24), c["title"], fill=(255, 255, 255), font=font_card_title)

    # Description (simple line wrap)
    words = c["desc"].split()
    lines = []
    curr = []
    for word in words:
        curr.append(word)
        if len(" ".join(curr)) > 36:
            lines.append(" ".join(curr))
            curr = []
    if curr:
        lines.append(" ".join(curr))

    line_y = y0 + 60
    for l in lines[:5]:
        draw.text((x0 + 18, line_y), l, fill=TEXT_MUTED, font=font_card_desc)
        line_y += 22

# Bottom Tech Badges Bar
badge_items = [
    ("Python 3.9+", (40, 46, 54), (200, 210, 225)),
    ("Faster-Whisper", (40, 46, 54), (200, 210, 225)),
    ("MediaPipe AI", (40, 46, 54), (200, 210, 225)),
    ("FFmpeg Mastered", (40, 46, 54), (200, 210, 225)),
    ("Claude Code Ready", (40, 46, 54), (200, 210, 225)),
    ("Cursor Ready", (40, 46, 54), (200, 210, 225)),
    ("Google Antigravity", (40, 46, 54), (200, 210, 225)),
    ("MIT License", (40, 46, 54), (200, 210, 225)),
]

bx = 60
by = 485
for label, fill_c, text_c in badge_items:
    bbox = font_badge.getbbox(label)
    bw = (bbox[2] - bbox[0]) + 20
    draw.rounded_rectangle([bx, by, bx + bw, by + 28], radius=6, fill=fill_c, outline=(56, 63, 72), width=1)
    draw.text((bx + 10, by + 6), label, fill=text_c, font=font_badge)
    bx += bw + 12

# Repository link at bottom right
draw.text((60, 545), "https://github.com/MMhaidra/edit-reel", fill=BLUE, font=font_subhero)
draw.text((780, 548), "Autonomous 9:16 Video Editor Agent", fill=TEXT_MUTED, font=font_card_desc)

out_path = Path("/Users/mhaidra/.gemini/antigravity/scratch/edit-reel/assets/og_preview.png")
im.save(out_path, "PNG", optimize=True)
print(f"Generated {out_path} ({out_path.stat().st_size / 1024:.1f} KB)")
