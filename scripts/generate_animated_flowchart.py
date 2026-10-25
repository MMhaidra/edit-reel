#!/usr/bin/env python3
"""
generate_animated_flowchart.py
Generates a silky-smooth, colorful, looping animated GIF flowchart for edit-reel
demonstrating the autonomous pipeline flow from raw video to master reel delivery.
"""

import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from pathlib import Path

W, H = 1080, 500
FPS = 25
DURATION_SEC = 3.6
NUM_FRAMES = int(FPS * DURATION_SEC)  # 90 frames

BG_COLOR = (13, 17, 23)        # #0D1117 (GitHub Dark)
CARD_BG = (22, 27, 34)         # #161B22
CARD_BORDER = (48, 54, 61)     # #30363D
TEXT_MAIN = (240, 246, 252)    # #F0F6FC
TEXT_MUTED = (139, 148, 158)   # #8B949E
LINE_DEFAULT = (40, 46, 54)

# 6 Balanced Stages in an S-loop
STAGES = [
    {
        "id": "01",
        "badge": "INPUT INGEST",
        "title": "Raw Video & Companion Script",
        "script": "detect_cuts.py (discover)",
        "desc": "Video (.MP4/.MOV) + Script (.docx/.txt)",
        "color": (59, 130, 246),      # Electric Blue #3B82F6
        "x": 195, "y": 150, "w": 260, "h": 105
    },
    {
        "id": "02",
        "badge": "ACOUSTIC PERCEPTION",
        "title": "Speech Cutter & Forced Aligner",
        "script": "transcribe_align.py + detect_cuts.py",
        "desc": "Whisper word boundaries + anti-arm cutoff",
        "color": (6, 182, 212),       # Bright Cyan #06B6D4
        "x": 540, "y": 150, "w": 270, "h": 105
    },
    {
        "id": "03",
        "badge": "3-STATE RHYTHM",
        "title": "Storyboard Beat Planner",
        "script": "storyboard_planner.py",
        "desc": "Studio Cam A/B -> Cutout -> Full Infographic",
        "color": (168, 85, 247),      # Vivid Violet #A855F7
        "x": 885, "y": 150, "w": 260, "h": 105
    },
    {
        "id": "04",
        "badge": "PHYSICAL OBJECTS",
        "title": "MediaPipe Vision & Objects",
        "script": "paper_objects.py + selfie_segmenter",
        "desc": "Warm paper #E2DDD1, tags, coins, notebook slips",
        "color": (245, 158, 11),      # Warm Amber / Gold #F59E0B
        "x": 885, "y": 375, "w": 260, "h": 105
    },
    {
        "id": "05",
        "badge": "STUDIO AUDIO",
        "title": "Broadcast Audio Mastering",
        "script": "FFmpeg Vocal Chain + loudnorm",
        "desc": "-11.5 LUFS dialogue, 0.045 bed, motion SFX",
        "color": (16, 185, 129),      # Mint Green #10B981
        "x": 540, "y": 375, "w": 270, "h": 105
    },
    {
        "id": "06",
        "badge": "MASTER DELIVERABLE",
        "title": "Autonomous Reel Rendering",
        "script": "render_reel.py",
        "desc": "1080x1920 MP4 production output",
        "color": (236, 72, 153),      # Pink / Magenta #EC4899
        "x": 195, "y": 375, "w": 260, "h": 105
    }
]

# Fonts
try:
    font_title = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 14)
    font_sub = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 11)
    font_detail = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 10)
    font_badge = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 9)
    font_header = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 17)
    font_tagline = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 12)
except Exception:
    font_title = font_sub = font_detail = font_badge = font_header = font_tagline = ImageFont.load_default()

def draw_rounded_rect(draw, bbox, fill, outline=None, width=1, radius=8):
    x0, y0, x1, y1 = bbox
    draw.rounded_rectangle([x0, y0, x1, y1], radius=radius, fill=fill, outline=outline, width=width)

def get_connection_path():
    # Sequence of points linking Stage 1 -> 2 -> 3 -> 4 -> 5 -> 6 -> (back to 1)
    path = []
    # 1 -> 2 (rightward)
    for t in np.linspace(0, 1, 35):
        path.append((195 + (540 - 195) * t, 150))
    # 2 -> 3 (rightward)
    for t in np.linspace(0, 1, 35):
        path.append((540 + (885 - 540) * t, 150))
    # 3 -> 4 (clockwise curve down on the right)
    for t in np.linspace(0, 1, 40):
        angle = -math.pi / 2 + math.pi * t
        cx, cy = 885, (150 + 375) / 2
        rx, ry = 80, (375 - 150) / 2
        path.append((cx + rx * math.cos(angle), cy + ry * math.sin(angle)))
    # 4 -> 5 (leftward)
    for t in np.linspace(0, 1, 35):
        path.append((885 - (885 - 540) * t, 375))
    # 5 -> 6 (leftward)
    for t in np.linspace(0, 1, 35):
        path.append((540 - (540 - 195) * t, 375))
    # 6 -> 1 (clockwise curve up on the left)
    for t in np.linspace(0, 1, 40):
        angle = math.pi / 2 + math.pi * t
        cx, cy = 195, (150 + 375) / 2
        rx, ry = 80, (375 - 150) / 2
        path.append((cx + rx * math.cos(angle), cy + ry * math.sin(angle)))
    return path

PATH = get_connection_path()
TOTAL_PATH_LEN = len(PATH)

def render_frame(frame_idx):
    im = Image.new("RGB", (W, H), BG_COLOR)
    draw = ImageDraw.Draw(im)

    # Top header bar
    draw.text((45, 22), "AUTONOMOUS EDITORIAL PIPELINE FLOW", fill=(255, 255, 255), font=font_header)
    draw.text((45, 46), "Continuous Zero-Interaction Loop: Raw Footage -> Perception -> 3-State Rhythm -> Physical Objects -> Audio -> Delivery", fill=TEXT_MUTED, font=font_tagline)

    # Calculate active progress through the 6 stages (0.0 to 6.0)
    progress = (frame_idx / NUM_FRAMES) * 6.0
    active_stage_idx = int(progress) % 6
    stage_sub_progress = progress - int(progress)

    # Draw static base connection lines
    for i in range(len(PATH) - 1):
        x1, y1 = PATH[i]
        x2, y2 = PATH[i + 1]
        draw.line([(x1, y1), (x2, y2)], fill=LINE_DEFAULT, width=3)

    # Directional arrow indicators on the track
    # 1 -> 2
    draw.polygon([(365, 146), (375, 150), (365, 154)], fill=(60, 68, 77))
    # 2 -> 3
    draw.polygon([(710, 146), (720, 150), (710, 154)], fill=(60, 68, 77))
    # 3 -> 4
    draw.polygon([(968, 260), (965, 272), (962, 260)], fill=(60, 68, 77))
    # 4 -> 5
    draw.polygon([(715, 371), (705, 375), (715, 379)], fill=(60, 68, 77))
    # 5 -> 6
    draw.polygon([(370, 371), (360, 375), (370, 379)], fill=(60, 68, 77))
    # 6 -> 1
    draw.polygon([(112, 265), (115, 253), (118, 265)], fill=(60, 68, 77))

    # Energetic trailing particle comet moving along the path
    path_pos = int((frame_idx / NUM_FRAMES) * TOTAL_PATH_LEN) % TOTAL_PATH_LEN
    active_col = STAGES[active_stage_idx]["color"]

    for trail in range(24):
        idx = (path_pos - trail) % TOTAL_PATH_LEN
        pt = PATH[idx]
        alpha = max(0.0, 1.0 - (trail / 24.0))
        c_r = int(active_col[0] * alpha + BG_COLOR[0] * (1.0 - alpha))
        c_g = int(active_col[1] * alpha + BG_COLOR[1] * (1.0 - alpha))
        c_b = int(active_col[2] * alpha + BG_COLOR[2] * (1.0 - alpha))
        r = max(2, int(6.0 - trail * 0.22))
        draw.ellipse([pt[0] - r, pt[1] - r, pt[0] + r, pt[1] + r], fill=(c_r, c_g, c_b))

    # Secondary trailing packet offset by half a cycle
    p2 = (path_pos + TOTAL_PATH_LEN // 2) % TOTAL_PATH_LEN
    for trail in range(12):
        idx = (p2 - trail) % TOTAL_PATH_LEN
        pt = PATH[idx]
        alpha = max(0.0, 0.6 - (trail / 20.0))
        c_r = int(59 * alpha + BG_COLOR[0] * (1.0 - alpha))
        c_g = int(130 * alpha + BG_COLOR[1] * (1.0 - alpha))
        c_b = int(246 * alpha + BG_COLOR[2] * (1.0 - alpha))
        r = max(2, int(4.0 - trail * 0.2))
        draw.ellipse([pt[0] - r, pt[1] - r, pt[0] + r, pt[1] + r], fill=(c_r, c_g, c_b))

    # Draw Stage Cards
    for s_i, st in enumerate(STAGES):
        cx, cy, cw, ch = st["x"], st["y"], st["w"], st["h"]
        bx0 = cx - cw // 2
        by0 = cy - ch // 2
        bx1 = cx + cw // 2
        by1 = cy + ch // 2

        is_active = (s_i == active_stage_idx)
        col = st["color"]

        if is_active:
            # Active glowing card
            glow_intensity = 0.5 + 0.5 * math.sin(stage_sub_progress * math.pi)
            border_col = col
            card_fill = (
                int(CARD_BG[0] + col[0] * 0.16 * glow_intensity),
                int(CARD_BG[1] + col[1] * 0.16 * glow_intensity),
                int(CARD_BG[2] + col[2] * 0.16 * glow_intensity)
            )
            border_w = 2
            # Outer halo
            draw_rounded_rect(draw, [bx0 - 3, by0 - 3, bx1 + 3, by1 + 3], fill=None, outline=(col[0] // 3, col[1] // 3, col[2] // 3), width=1, radius=12)
        else:
            border_col = CARD_BORDER
            card_fill = CARD_BG
            border_w = 1

        # Card body
        draw_rounded_rect(draw, [bx0, by0, bx1, by1], fill=card_fill, outline=border_col, width=border_w, radius=10)

        # Stage number pill
        pill_w, pill_h = 100, 18
        pill_x = bx0 + 12
        pill_y = by0 + 11
        pill_bg = col if is_active else (33, 38, 45)
        pill_txt_col = (255, 255, 255) if is_active else (139, 148, 158)
        draw_rounded_rect(draw, [pill_x, pill_y, pill_x + pill_w, pill_y + pill_h], fill=pill_bg, radius=4)
        draw.text((pill_x + 6, pill_y + 3), f"{st['id']} | {st['badge']}", fill=pill_txt_col, font=font_badge)

        # Status indicator dot
        dot_x = bx1 - 18
        dot_y = by0 + 20
        dot_col = col if is_active else (48, 54, 61)
        draw.ellipse([dot_x - 4, dot_y - 4, dot_x + 4, dot_y + 4], fill=dot_col)
        if is_active:
            ring_r = 7 + int(3 * glow_intensity)
            draw.ellipse([dot_x - ring_r, dot_y - ring_r, dot_x + ring_r, dot_y + ring_r], outline=(col[0], col[1], col[2]), width=1)

        # Titles and description
        title_col = (255, 255, 255) if is_active else TEXT_MAIN
        draw.text((bx0 + 12, by0 + 36), st["title"], fill=title_col, font=font_title)
        draw.text((bx0 + 12, by0 + 58), st["script"], fill=st["color"] if is_active else (88, 166, 255), font=font_sub)
        draw.text((bx0 + 12, by0 + 78), st["desc"], fill=TEXT_MUTED, font=font_detail)

    return im

def main():
    out_dir = Path("/Users/mhaidra/.gemini/antigravity/scratch/edit-reel/assets")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_gif = out_dir / "pipeline_flow.gif"

    print(f"Generating {NUM_FRAMES} frames ({DURATION_SEC}s @ {FPS} FPS)...")
    frames = []
    for i in range(NUM_FRAMES):
        if i % 15 == 0:
            print(f"  Frame {i}/{NUM_FRAMES}...")
        f = render_frame(i)
        f_q = f.quantize(colors=128, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
        frames.append(f_q)

    print(f"Saving animated looping GIF to {out_gif}...")
    frames[0].save(
        out_gif,
        save_all=True,
        append_images=frames[1:],
        loop=0,
        duration=int(1000 / FPS),
        optimize=True
    )
    print(f"Done! File size: {out_gif.stat().st_size / 1024:.1f} KB")

if __name__ == "__main__":
    main()
