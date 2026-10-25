#!/usr/bin/env python3
"""
preview_reel_stills.py - Canonical Still Preview Generator for Instagram Reels

Generates contact sheets across all 8 conceptual scenes with:
  - State 1: Natural room background for hook / outro
  - State 2: Lowered cutout speaker on warm paper with lowered notebook cutoffs (y=165) + objects
  - State 3: Full-screen paper infographics (parallel graphs & country comparison)
"""

import sys, math, subprocess
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw
import mediapipe as mp
from mediapipe.tasks import python as mpp
from mediapipe.tasks.python import vision

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from motion_library import paper_objects as V

OUT = Path(sys.argv[1] if len(sys.argv) > 1 else "/tmp/reel_previews")
OUT.mkdir(parents=True, exist_ok=True)

SRC = {
    "en": str(Path.home() / "Desktop" / "projects" / "reels_IG" / "C7BAE170-9BB5-4BEC-8458-460D29B3C1B7.MP4"),
    "ar": str(Path.home() / "Desktop" / "projects" / "reels_IG" / "2E1174BB-9D62-4DD0-B768-1A579C686590.MP4"),
}
seg = vision.ImageSegmenter.create_from_options(vision.ImageSegmenterOptions(
    base_options=mpp.BaseOptions(model_asset_path=str(ROOT / "models" / "selfie_segmenter.tflite")),
    output_confidence_masks=True, output_category_mask=False))


def grab(tag, t):
    p = OUT / f"_raw_{tag}.png"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", str(t), "-i", SRC[tag], "-vframes", "1",
                    "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
                           "eq=contrast=1.05:brightness=0.02:saturation=1.06,unsharp=5:5:0.5:5:5:0.2", str(p)], check=True)
    im = Image.open(p).convert("RGB")
    m = V.person_mask(im, seg, mp)
    return im, V.cutout_layer(im, m), m


def head_top(mask):
    rows = np.where((mask > 0.5).sum(axis=1) > 40)[0]
    return int(rows[0]) if len(rows) else 0


def speaker_canvas(cut, mask, lowered=True):
    c = V.paper_background()
    sc = 0.90
    im = cut.resize((int(V.W * sc), int(V.H * sc)), Image.LANCZOS)
    x = (V.W - im.width) // 2
    y = 800 - int(head_top(mask) * sc)
    c.alpha_composite(im, (x, y))
    return c


F = V.tw_font
NOTE_Y = 165
TAG_TOP = 265
STRING_TO = 245


def scene_hook_real_bg(raw_rgb, sub):
    c = raw_rgb.convert("RGBA")
    V.draw_subtitle(c, sub, 1560)
    return c


def scene_tag75(cut, mask, sub):
    c = speaker_canvas(cut, mask, True)
    note = V.notebook_cutoff("PNAS (MARCH 2023) • CONFLICT RESOLVED", "Daniel Kahneman & Matthew Killingsworth", "Testing the $75,000 Plateau Hypothesis", w=560, h=145)
    V._place(c, note, 540, NOTE_Y, rot=-1.0)
    V.hang_tag(c, 540, TAG_TOP, 440, 520, ["$75,000", "STOPS?"], [F(96), F(64)], [V.INK, V.RED], rot=-2.0, string_to=STRING_TO)
    V.draw_subtitle(c, sub, 1560)
    return c


def scene_rise(cut, mask, sub):
    c = speaker_canvas(cut, mask, True)
    note = V.notebook_cutoff("PENN & PRINCETON COLLABORATION", "Killingsworth & Kahneman (2023)", "N = 33,391 US Adults • 1.7M Real-Time Check-Ins", w=560, h=145)
    V._place(c, note, 540, NOTE_Y, rot=1.0)

    stack = V.draw_coin_stack(7, 95)
    V._place(c, stack, 250, 560, rot=-3)
    arrow = V.draw_arrow(180, True, V.GREEN)
    V._place(c, arrow, 540, 460, rot=4)
    V.text_c(c, 800, 570, "$500K+", F(108), V.GREEN, shadow=True)
    V.text_c(c, 800, 670, "STILL RISING", F(42), V.INK)
    V.draw_subtitle(c, sub, 1560)
    return c


def scene_log_parallel(sub):
    c = V.paper_background()
    note = V.notebook_cutoff("PNAS RESEARCH (2023) • LOGARITHMIC UTILITY", "Daniel Kahneman & Matthew Killingsworth", "Happiness = Log(Income) // Equal Doublings For Equal Joy", w=680, h=145)
    V._place(c, note, 540, 210, rot=-1.0)
    V.draw_two_parallel_graphs(c, anim_p=1.0)
    V.draw_subtitle(c, sub, 1710, dark=True)
    return c


def scene_corr(cut, mask, sub):
    c = speaker_canvas(cut, mask, True)
    note = V.notebook_cutoff("STATISTICAL EFFECT SIZE // PNAS 2023", "Synthesized in PWL Capital / Ben Felix", "Correlation with Daily Happiness: r = 0.09", w=560, h=145)
    V._place(c, note, 540, NOTE_Y, rot=-1.0)

    V.hang_tag(c, 270, TAG_TOP, 360, 480, ["0.09", "CORRELATION"], [F(110), F(32)], [V.INK, V.INK_SOFT], rot=2.0, string_to=STRING_TO)
    up = V.draw_arrow(95, True, V.GREEN)
    ch1 = V.label_chip(up, "80%  RISES", F(44), w=490, h=140)
    V._place(c, ch1, 780, 350, rot=-1.5)
    flat = V.draw_arrow(95, False, V.RED)
    ch2 = V.label_chip(flat, "20%  FLAT", F(44), w=490, h=140)
    V._place(c, ch2, 780, 540, rot=1.5)
    V.draw_subtitle(c, sub, 1560)
    return c


def scene_country(sub):
    c = V.paper_background()
    note = V.notebook_cutoff("WORLD HAPPINESS REPORT (2024)", "Oxford Wellbeing Research Centre & Gallup Poll", "Social Connection & Time Affluence Beat Raw GDP", w=680, h=145)
    V._place(c, note, 540, 210, rot=-1.0)

    slip = V.paper_slip("MONEY vs HAPPINESS", F(56))
    V._place(c, slip, 540, 400, rot=-2)

    V._place(c, V.draw_flag_badge("CR", 130), 290, 730)
    V._place(c, V.draw_flag_badge("US", 85), 740, 690)
    V._place(c, V.draw_flag_badge("SG", 85), 880, 780)
    V._place(c, V.paper_slip("VS", F(50), pad=(24, 10)), 540, 740, rot=4)

    V.text_c(c, 290, 1020, "~$16K", F(110), V.GREEN, shadow=True)
    V.text_c(c, 810, 1020, "$80K+", F(110), V.RED, shadow=True)
    V.text_c(c, 290, 1120, "PER PERSON / YEAR", F(32), V.INK_SOFT)
    V.text_c(c, 810, 1120, "PER PERSON / YEAR", F(32), V.INK_SOFT)

    V._place(c, V.label_chip(V.draw_heart(140), "HAPPIER", F(42), w=450, h=140), 290, 1330, rot=-1.5)
    V._place(c, V.label_chip(V.draw_arrow(95, False, V.RED), "LESS HAPPY", F(38), w=450, h=140), 810, 1330, rot=1.5)
    V.draw_subtitle(c, sub, 1710, dark=True)
    return c


def scene_hedonic(cut, mask, sub):
    c = speaker_canvas(cut, mask, True)
    note = V.notebook_cutoff("JOURNAL OF PERSONALITY & SOCIAL PSYCH", "Brickman & Campbell (1971) • Lucas et al. (2004)", "Hedonic Adaptation: Material Upgrades Adapt Fast", w=600, h=145)
    V._place(c, note, 540, NOTE_Y, rot=-1.0)

    V._place(c, V.paper_slip("THE HEDONIC TREADMILL", F(52)), 540, 290, rot=1.0)

    d = ImageDraw.Draw(c)
    base_y, x0, x1 = 700, 120, 960
    d.line([(x0, base_y), (x1, base_y)], fill=V.GOLD + (255,), width=6)
    V.text_c(c, 330, base_y + 36, "HAPPINESS BASELINE", F(32), V.GOLD)

    pts = []
    for k in range(80):
        u = k / 79.0
        px = x0 + 20 + u * (x1 - x0 - 40)
        if u < 0.22:
            py = base_y - math.sin(u / 0.22 * math.pi / 2.0) * 270.0
        else:
            py = base_y - math.exp(-(u - 0.22) * 6.5) * 270.0
        pts.append((px, py))
    V.ink_line(c, pts, V.GREEN, 12)

    V._place(c, V.label_chip(None, "NEW CAR!", F(38), w=300, h=90), 330, 370, rot=-3)
    V._place(c, V.label_chip(None, "BACK TO NORMAL", F(32), w=390, h=86), 790, 620, rot=2)
    V.draw_subtitle(c, sub, 1560)
    return c


def scene_pillars(cut, mask, sub):
    c = speaker_canvas(cut, mask, True)
    note = V.notebook_cutoff("HARVARD 85-YEAR STUDY & ELIZABETH DUNN", "Science (2008) • PNAS (2017) • Waldinger", "How to Actually Convert Money Into Happiness", w=620, h=145)
    V._place(c, note, 540, NOTE_Y, rot=1.0)

    items = [(190, V.draw_clock(70), "TIME", -2.5), (540, V.draw_plane(136), "EXPERIENCES", 1.5), (890, V.draw_heart(132), "GIVING", -1.5)]
    for cx, icon, name, rot in items:
        V.hang_tag(c, cx, TAG_TOP, 290, 430, [" ", " ", " ", name], [F(46), F(46), F(36), F(30 if len(name) > 7 else 40)], [V.INK] * 4, rot=rot, string_to=STRING_TO)
        V._place(c, icon, cx, TAG_TOP + 160, rot=rot * 2, shadow=True)
    V.draw_subtitle(c, sub, 1560)
    return c


def main():
    raw_en, cut_en, m_en = grab("en", 2.5)
    raw_en2, cut_en2, m_en2 = grab("en", 12.0)

    jobs = [
        ("1_hook_real_bg", scene_hook_real_bg, (raw_en, "CAN MONEY BUY HAPPINESS?")),
        ("2_tag75_loaded", scene_tag75, (cut_en2, m_en2, "STOPS AT $75,000?")),
        ("3_rise_loaded", scene_rise, (cut_en, m_en, "IT KEEPS RISING TO $500K+")),
        ("4_log_parallel_graphs", scene_log_parallel, ("DOUBLE INCOME, SAME BOOST",)),
        ("5_corr", scene_corr, (cut_en2, m_en2, "THE CORRELATION IS JUST 0.09")),
        ("6_country", scene_country, ("COSTA RICA BEATS THEM",)),
        ("7_hedonic_clean", scene_hedonic, (cut_en, m_en, "THEN YOU ADAPT AND RESET")),
        ("8_pillars", scene_pillars, (cut_en2, m_en2, "TIME, EXPERIENCES, GIVING")),
    ]

    for name, fn, args in jobs:
        img = fn(*args).convert("RGB")
        img.save(OUT / f"{name}.png")

    names = [n for n, _, _ in jobs]
    tiles = [Image.open(OUT / f"{n}.png").resize((405, 720), Image.LANCZOS) for n in names]
    cols, rows = 4, 2
    m = Image.new("RGB", (cols * 405, rows * 720), (255, 255, 255))
    for i, t in enumerate(tiles):
        m.paste(t, ((i % cols) * 405, (i // cols) * 720))
    m.save(OUT / "preview_montage.png")
    print(f"✓ Saved canonical previews to {OUT / 'preview_montage.png'}")


if __name__ == "__main__":
    main()
