#!/usr/bin/env python3
"""
pre_render_library.py - Pre-renders the full suite of 17 standard Motion Library animations
as transparent .mov (qtrle) video clips with light glassy background, embedded vector icons,
and domain color palettes.
"""

import sys
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw

SKILL_ROOT = Path(__file__).resolve().parent.parent
if str(SKILL_ROOT) not in sys.path:
    sys.path.insert(0, str(SKILL_ROOT))

from motion_library.catalog import MOTION_CATALOG
from motion_library.renderers import TEMPLATE_MAP, draw_hud_progress_filament
from scripts.motion_engine import get_fonts

SKILL_ASSETS_DIR = SKILL_ROOT / "motion_library" / "assets"
PROJECT_ASSETS_DIR = Path.home() / "Desktop" / "projects" / "reels_IG" / "motion_assets"

SKILL_ASSETS_DIR.mkdir(parents=True, exist_ok=True)
PROJECT_ASSETS_DIR.mkdir(parents=True, exist_ok=True)

canvas_w = 1080
canvas_h = 320
fps = 24
duration = 6.0
total_frames = int(duration * fps)
fade_frames = int(fps * 0.28)

fonts = get_fonts(is_arabic=False)

print(f"Pre-rendering {len(MOTION_CATALOG)} motion graphics clips ({duration}s @ {fps}fps)...")

for domain_key, item in MOTION_CATALOG.items():
    template_name = item["template"]
    asset_name = item["asset_name"]
    renderer_fn = TEMPLATE_MAP.get(template_name)
    if not renderer_fn:
        print(f"Warning: No renderer found for template '{template_name}'")
        continue

    skill_out_path = SKILL_ASSETS_DIR / asset_name
    project_out_path = PROJECT_ASSETS_DIR / asset_name

    print(f"Rendering '{asset_name}' (template: {template_name}, icon: {item.get('icon')})...")

    cmd = [
        "ffmpeg", "-y",
        "-f", "rawvideo",
        "-pix_fmt", "rgba",
        "-s", f"{canvas_w}x{canvas_h}",
        "-r", str(fps),
        "-i", "-",
        "-c:v", "qtrle",
        str(skill_out_path)
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    for f_idx in range(total_frames):
        t_norm = f_idx / float(total_frames)

        if f_idx < fade_frames:
            alpha_factor = f_idx / float(fade_frames)
        elif f_idx > total_frames - fade_frames:
            alpha_factor = (total_frames - f_idx) / float(fade_frames)
        else:
            alpha_factor = 1.0

        img = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Call renderer + HUD progress filament
        renderer_fn(draw, t_norm, f_idx, item, fonts)
        draw_hud_progress_filament(draw, t_norm, item)

        if alpha_factor < 0.98:
            r, g, b, a = img.split()
            a = a.point(lambda p: int(p * alpha_factor))
            img = Image.merge("RGBA", (r, g, b, a))

        proc.stdin.write(img.tobytes())

    proc.stdin.close()
    proc.wait()

    # Mirror to project motion_assets
    if skill_out_path.exists():
        with open(skill_out_path, "rb") as src, open(project_out_path, "wb") as dst:
            dst.write(src.read())

print("All 17 motion graphics clips successfully rendered and mirrored!")
