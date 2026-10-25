#!/usr/bin/env python3
"""
render_reel.py - Canonical Master Reel Renderer (Tactile "Paper & Objects" Edition)

Architecture & Aesthetics:
1. 3-State Dynamic Alternating Rhythm:
   - State 1 (Real Studio Camera Footage): Hook, conversational pauses, and outro keep the real room background.
   - State 2 (Lowered Cutout Speaker on Paper + Physical Objects Above): MediaPipe AI person segmentation isolates
     the speaker standing on warm paper (#E2DDD1) ONLY while a visual graphic is actively showing.
   - State 3 (Full-Screen Paper Infographics): Deep comparative parallel charts and global data (no speaker).
2. Pinned Academic Notebook Cutoffs:
   - Authentic torn notebook slips (faint ruled blue-gray lines, red margin line, top tape) positioned at a safe
     Instagram distance (y = 165 / 210) to display peer-reviewed citations (PNAS, Harvard, Gallup, Brickman & Campbell).
3. Two Parallel Comparative Graphs (Logarithmic Income Law):
   - Side-by-side plots: LINEAR (MYTH) flatlining vs LOGARITHMIC (REALITY) 2x doublings with equal boost steps.
4. Animated Loading Money Counters:
   - Rolling odometer counters loading from $0 to $75,000 on the tag (stamping STOPS?) and climbing to $500K+ STILL RISING.
5. Broadcast Audio Mastering:
   - -11.5 LUFS vocal isolation chain + 0.045 ambient music bed + motion-synced SFX.
"""

import os
import re
import sys
import math
import json
import time
import shutil
import argparse
import subprocess
from pathlib import Path
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter

import mediapipe as mp
from mediapipe.tasks import python as mpp
from mediapipe.tasks.python import vision

SKILL_ROOT = Path(__file__).resolve().parent.parent
if str(SKILL_ROOT) not in sys.path:
    sys.path.insert(0, str(SKILL_ROOT))

from motion_library import paper_objects as V
from motion_library.renderers import shape_text
from scripts.pipeline import find_sfx_path, get_synced_sfx_schedule_for_cue, verify_production_quality


def ease_out_cubic(x):
    x = max(0.0, min(1.0, float(x)))
    return 1.0 - (1.0 - x) ** 3


def ease_out_back(x, s=1.25):
    x = max(0.0, min(1.0, float(x)))
    c1 = s
    c3 = c1 + 1.0
    return 1.0 + c3 * ((x - 1.0) ** 3) + c1 * ((x - 1.0) ** 2)


def ease_in_out_cubic(x):
    x = max(0.0, min(1.0, float(x)))
    return 4.0 * x * x * x if x < 0.5 else 1.0 - ((-2.0 * x + 2.0) ** 3) / 2.0


def fast_cutout_rgba(frame_rgb_np, mask_f32):
    """Fast OpenCV + NumPy alpha matte cleanup."""
    m = cv2.GaussianBlur(mask_f32, (5, 5), 1.5)
    m = np.clip((m - 0.42) / 0.26, 0.0, 1.0)
    m = m * m * (3.0 - 2.0 * m)
    kernel = np.ones((3, 3), np.float32)
    m = cv2.erode(m, kernel, iterations=1)
    m = cv2.GaussianBlur(m, (3, 3), 1.0)
    alpha = (m * 255.0).astype(np.uint8)
    rgba = np.dstack([frame_rgb_np, alpha])
    return Image.fromarray(rgba)


def bake_sprite(obj_s2, rot=0.0, scale=1.0, shadow=True):
    im = obj_s2.resize(
        (max(1, int(obj_s2.width / V.S * scale)), max(1, int(obj_s2.height / V.S * scale))),
        Image.LANCZOS
    )
    if abs(rot) > 0.01:
        im = im.rotate(rot, resample=Image.BICUBIC, expand=True)
    if shadow:
        pad = 48
        padded = Image.new("RGBA", (im.width + pad * 2, im.height + pad * 2), (0, 0, 0, 0))
        padded.alpha_composite(im, (pad, pad))
        im = V._shadow(padded)
    return im


def paste_sprite(canvas, sprite, cx, cy, offset_y=0.0, opacity=1.0, scale=1.0):
    if opacity <= 0.01:
        return
    im = sprite
    if abs(scale - 1.0) > 0.015:
        im = im.resize(
            (max(1, int(im.width * scale)), max(1, int(im.height * scale))),
            Image.BILINEAR
        )
    if opacity < 0.99:
        a = im.split()[-1].point(lambda v: int(v * opacity))
        im = im.copy()
        im.putalpha(a)
    canvas.alpha_composite(im, (int(cx - im.width / 2), int(cy + offset_y - im.height / 2)))


def build_sprite_bank():
    F = V.tw_font
    bank = {}

    # Notebook cutoffs for each beat (authentic ruled paper with margin and tape)
    bank["note_b1"] = bake_sprite(V.notebook_cutoff("PNAS (MARCH 2023) • CONFLICT RESOLVED", "Daniel Kahneman & Matthew Killingsworth", "Testing the $75,000 Plateau Hypothesis", w=560, h=145), rot=-1.0)
    bank["note_b2"] = bake_sprite(V.notebook_cutoff("PENN & PRINCETON COLLABORATION", "Killingsworth & Kahneman (2023)", "N = 33,391 US Adults • 1.7M Real-Time Check-Ins", w=560, h=145), rot=1.0)
    bank["note_b3"] = bake_sprite(V.notebook_cutoff("PNAS RESEARCH (2023) • LOGARITHMIC UTILITY", "Daniel Kahneman & Matthew Killingsworth", "Happiness = Log(Income) // Equal Doublings For Equal Joy", w=680, h=145), rot=-1.0)
    bank["note_b4"] = bake_sprite(V.notebook_cutoff("STATISTICAL EFFECT SIZE // PNAS 2023", "Synthesized in PWL Capital / Ben Felix", "Correlation with Daily Happiness: r = 0.09", w=560, h=145), rot=-1.0)
    bank["note_b5"] = bake_sprite(V.notebook_cutoff("WORLD HAPPINESS REPORT (2024)", "Oxford Wellbeing Research Centre & Gallup Poll", "Social Connection & Time Affluence Beat Raw GDP", w=680, h=145), rot=-1.0)
    bank["note_b6"] = bake_sprite(V.notebook_cutoff("JOURNAL OF PERSONALITY & SOCIAL PSYCH", "Brickman & Campbell (1971) • Lucas et al. (2004)", "Hedonic Adaptation: Material Upgrades Adapt Fast", w=600, h=145), rot=-1.0)
    bank["note_b7"] = bake_sprite(V.notebook_cutoff("HARVARD 85-YEAR STUDY & ELIZABETH DUNN", "Science (2008) • PNAS (2017) • Waldinger", "How to Actually Convert Money Into Happiness", w=620, h=145), rot=1.0)

    # Beat 1: Tag blank template + eyelet info for dynamic loading numbers
    tag75_raw, (ex75, ey75) = V.draw_tag(440, 520, [" ", " "], [F(96), F(64)])
    bank["tag75_blank"] = bake_sprite(tag75_raw, rot=-2.0, shadow=True)
    bank["tag75_ey"] = ey75
    bank["tag75_h"] = tag75_raw.height / V.S

    # Beat 2: Coin stack + green arrow
    bank["coin_stack"] = bake_sprite(V.draw_coin_stack(7, 95), rot=-3.0)
    bank["arrow_up_big"] = bake_sprite(V.draw_arrow(180, True, V.GREEN), rot=4.0)

    # Beat 4: Correlation 0.09 tag + 80% / 20% chips
    tag09_raw, (ex09, ey09) = V.draw_tag(360, 480, ["0.09", "CORRELATION"], [F(110), F(32)], [V.INK, V.INK_SOFT])
    bank["tag09"] = bake_sprite(tag09_raw, rot=2.0)
    bank["tag09_ey"] = ey09
    bank["tag09_h"] = tag09_raw.height / V.S
    bank["chip_80"] = bake_sprite(V.label_chip(V.draw_arrow(95, True, V.GREEN), "80%  RISES", F(44), w=490, h=140), rot=-1.5)
    bank["chip_20"] = bake_sprite(V.label_chip(V.draw_arrow(95, False, V.RED), "20%  FLAT", F(44), w=490, h=140), rot=1.5)

    # Beat 5: Country comparison
    bank["slip_country"] = bake_sprite(V.paper_slip("MONEY vs HAPPINESS", F(56)), rot=-2.0)
    bank["flag_cr"] = bake_sprite(V.draw_flag_badge("CR", 130), rot=0.0)
    bank["flag_us"] = bake_sprite(V.draw_flag_badge("US", 85), rot=0.0)
    bank["flag_sg"] = bake_sprite(V.draw_flag_badge("SG", 85), rot=0.0)
    bank["slip_vs"] = bake_sprite(V.paper_slip("VS", F(50), pad=(24, 10)), rot=4.0)
    bank["chip_happier"] = bake_sprite(V.label_chip(V.draw_heart(140), "HAPPIER", F(42), w=450, h=140), rot=-1.5)
    bank["chip_less"] = bake_sprite(V.label_chip(V.draw_arrow(95, False, V.RED), "LESS HAPPY", F(38), w=450, h=140), rot=1.5)

    # Beat 6: Hedonic treadmill (clean, zero yellow hazard tape)
    bank["slip_hedonic"] = bake_sprite(V.paper_slip("THE HEDONIC TREADMILL", F(52)), rot=1.0)
    bank["chip_car"] = bake_sprite(V.label_chip(None, "NEW CAR!", F(38), w=300, h=90), rot=-3.0)
    bank["chip_norm"] = bake_sprite(V.label_chip(None, "BACK TO NORMAL", F(32), w=390, h=86), rot=2.0)

    # Beat 7: Three pillars tags
    pillar_defs = [
        ("p1", V.draw_clock(70), "TIME", -2.5),
        ("p2", V.draw_plane(136), "EXPERIENCES", 1.5),
        ("p3", V.draw_heart(132), "GIVING", -1.5),
    ]
    for key, icon_s2, name, rot in pillar_defs:
        t_raw, (ex, ey) = V.draw_tag(
            290, 430,
            [" ", " ", " ", name],
            [F(46), F(46), F(36), F(30 if len(name) > 7 else 40)],
            [V.INK] * 4
        )
        ic_baked = bake_sprite(icon_s2, rot=rot * 1.5, scale=1.0, shadow=True)
        ic_s2 = ic_baked.resize((ic_baked.width * V.S, ic_baked.height * V.S), Image.LANCZOS)
        t_raw.alpha_composite(ic_s2, ((t_raw.width - ic_s2.width) // 2, int(195 * V.S - ic_s2.height / 2)))
        bank[key] = bake_sprite(t_raw, rot=rot)
        bank[f"{key}_ey"] = ey
        bank[f"{key}_h"] = t_raw.height / V.S

    # Fonts
    bank["F120"] = F(120)
    bank["F110"] = F(110)
    bank["F108"] = F(108)
    bank["F96"] = F(96)
    bank["F64"] = F(64)
    bank["F56"] = F(56)
    bank["F52"] = F(52)
    bank["F46"] = F(46)
    bank["F44"] = F(44)
    bank["F42"] = F(42)
    bank["F38"] = F(38)
    bank["F36"] = F(36)
    bank["F34"] = F(34)
    bank["F32"] = F(32)

    return bank


def draw_hanging_tag_with_text(canvas, sprite, ey, tag_h, cx, top_y, drop_p, line1, line2, f1, f2, c1, c2, string_to=245, rot=-2.0):
    if drop_p <= 0.01:
        return
    ep = ease_out_back(drop_p, s=1.15)
    cur_top_y = top_y - (1.0 - ep) * 480.0
    d = ImageDraw.Draw(canvas)
    eyelet_y = cur_top_y + (ey - 10 / V.S)
    if eyelet_y > string_to:
        d.line([(int(cx), int(string_to)), (int(cx), int(eyelet_y))], fill=(70, 62, 54, 255), width=3)
    paste_sprite(canvas, sprite, cx, cur_top_y + tag_h / 2 - 10 / V.S, opacity=min(1.0, drop_p * 2.5))

    # Center text inside tag
    tag_center_y = cur_top_y + tag_h / 2 + 15
    if line1:
        V.text_c(canvas, cx, int(tag_center_y - 30), line1, f1, c1)
    if line2:
        V.text_c(canvas, cx, int(tag_center_y + 45), line2, f2, c2)


def render_beat_graphics(canvas, cue, cur_t, bank):
    st = float(cue.get("start_time", 0.0))
    et = float(cue.get("end_time", st + 8.0))
    dur = max(0.1, et - st)
    el = cur_t - st
    rem = et - cur_t
    fade_out = ease_out_cubic(min(1.0, rem / 0.28)) if rem < 0.28 else 1.0
    btype = cue.get("template") or cue.get("animation_type", "")

    # Notebook cutoff Y placement: lower down (y=165) for safe margin clearance
    NOTE_Y_SPEAKER = 165
    TAG_TOP_SPEAKER = 265
    STRING_TO_SPEAKER = 245

    if btype == "study_citation":
        # Beat 1: Notebook cutoff + $75K loading money tag
        p_note = ease_out_back(min(1.0, el / 0.40)) * fade_out
        paste_sprite(canvas, bank["note_b1"], 540, NOTE_Y_SPEAKER, offset_y=-(1.0 - p_note) * 40, opacity=min(1.0, p_note))

        p_tag = ease_out_cubic(min(1.0, max(0.0, (el - 0.15) / 0.55))) * fade_out
        sway = math.sin(el * 2.6) * 8.0 * math.exp(-el * 0.35)

        # Loading money counter $0 -> $75,000
        load_p = ease_out_cubic(min(1.0, max(0.0, (el - 0.20) / 0.90)))
        val = int(75000 * load_p)
        txt1 = f"${val:,}" if val < 75000 else "$75,000"
        txt2 = "STOPS?" if load_p >= 0.85 else "LOADING..."
        c2 = V.RED if load_p >= 0.85 else V.INK_SOFT
        draw_hanging_tag_with_text(canvas, bank["tag75_blank"], bank["tag75_ey"], bank["tag75_h"], 540 + sway, TAG_TOP_SPEAKER, p_tag, txt1, txt2, bank["F96"], bank["F64"], V.INK, c2, string_to=STRING_TO_SPEAKER)

    elif btype == "threshold_counter":
        # Beat 2: Notebook cutoff + Coin stack + green arrow + $500K+ STILL RISING
        p_note = ease_out_back(min(1.0, el / 0.40)) * fade_out
        paste_sprite(canvas, bank["note_b2"], 540, NOTE_Y_SPEAKER, offset_y=-(1.0 - p_note) * 40, opacity=min(1.0, p_note))

        p1 = ease_out_back(min(1.0, max(0.0, (el - 0.10) / 0.45))) * fade_out
        p2 = ease_out_back(min(1.0, max(0.0, (el - 0.25) / 0.45))) * fade_out
        p3 = ease_out_cubic(min(1.0, max(0.0, (el - 0.40) / 0.45))) * fade_out

        paste_sprite(canvas, bank["coin_stack"], 250, 560, offset_y=(1.0 - p1) * 80, opacity=min(1.0, p1), scale=0.85 + 0.15 * min(1.0, p1))
        paste_sprite(canvas, bank["arrow_up_big"], 540, 460, offset_y=(1.0 - p2) * 70, opacity=min(1.0, p2), scale=0.85 + 0.15 * min(1.0, p2))

        if p3 > 0.02:
            val_num = int(75 + (500 - 75) * ease_out_cubic(min(1.0, max(0.0, (el - 0.35) / 1.1))))
            label_str = f"${val_num}K+" if val_num >= 500 else f"${val_num}K"
            V.text_c(canvas, 800, int(570 + (1.0 - p3) * 35), label_str, bank["F108"], V.GREEN, shadow=True)
            V.text_c(canvas, 800, int(670 + (1.0 - p3) * 35), "STILL RISING", bank["F42"], V.INK)

    elif btype == "log_income_curve":
        # Beat 3: Full-screen Paper Infographic — TWO PARALLEL GRAPHS (Linear Myth vs Log Reality)
        p_note = ease_out_back(min(1.0, el / 0.40)) * fade_out
        paste_sprite(canvas, bank["note_b3"], 540, 210, offset_y=-(1.0 - p_note) * 40, opacity=min(1.0, p_note))
        curve_p = ease_in_out_cubic(min(1.0, max(0.0, (el - 0.20) / 1.8)))
        V.draw_two_parallel_graphs(canvas, anim_p=curve_p)

    elif btype == "correlation_split":
        # Beat 4: Notebook cutoff + 0.09 CORRELATION tag + 80% RISES / 20% FLAT chips
        p_note = ease_out_back(min(1.0, el / 0.40)) * fade_out
        paste_sprite(canvas, bank["note_b4"], 540, NOTE_Y_SPEAKER, offset_y=-(1.0 - p_note) * 40, opacity=min(1.0, p_note))

        p_tag = ease_out_cubic(min(1.0, max(0.0, (el - 0.15) / 0.50))) * fade_out
        p_c1 = ease_out_back(min(1.0, max(0.0, (el - 0.35) / 0.45))) * fade_out
        p_c2 = ease_out_back(min(1.0, max(0.0, (el - 0.55) / 0.45))) * fade_out

        ep = ease_out_back(p_tag, s=1.15)
        cur_top_y = TAG_TOP_SPEAKER - (1.0 - ep) * 480.0
        d = ImageDraw.Draw(canvas)
        eyelet_y = cur_top_y + (bank["tag09_ey"] - 10 / V.S)
        if eyelet_y > STRING_TO_SPEAKER:
            d.line([(270, STRING_TO_SPEAKER), (270, int(eyelet_y))], fill=(70, 62, 54, 255), width=3)
        paste_sprite(canvas, bank["tag09"], 270, cur_top_y + bank["tag09_h"] / 2 - 10 / V.S, opacity=min(1.0, p_tag * 2.5))

        paste_sprite(canvas, bank["chip_80"], 780, 350, offset_y=(1.0 - p_c1) * 50, opacity=min(1.0, p_c1))
        paste_sprite(canvas, bank["chip_20"], 780, 540, offset_y=(1.0 - p_c2) * 50, opacity=min(1.0, p_c2))

    elif btype == "country_comparison":
        # Beat 5: Full-screen Paper Infographic — Costa Rica vs US & Singapore
        p_note = ease_out_back(min(1.0, el / 0.40)) * fade_out
        paste_sprite(canvas, bank["note_b5"], 540, 210, offset_y=-(1.0 - p_note) * 40, opacity=min(1.0, p_note))

        p0 = ease_out_back(min(1.0, max(0.0, (el - 0.15) / 0.40))) * fade_out
        p1 = ease_out_back(min(1.0, max(0.0, (el - 0.30) / 0.45))) * fade_out
        p2 = ease_out_back(min(1.0, max(0.0, (el - 0.50) / 0.45))) * fade_out
        p3 = ease_out_back(min(1.0, max(0.0, (el - 0.80) / 0.45))) * fade_out

        paste_sprite(canvas, bank["slip_country"], 540, 400, offset_y=-(1.0 - p0) * 40, opacity=min(1.0, p0))
        paste_sprite(canvas, bank["flag_cr"], 290, 730, scale=0.85 + 0.15 * min(1.0, p1), opacity=min(1.0, p1))
        paste_sprite(canvas, bank["flag_us"], 740, 690, scale=0.85 + 0.15 * min(1.0, p2), opacity=min(1.0, p2))
        paste_sprite(canvas, bank["flag_sg"], 880, 780, scale=0.85 + 0.15 * min(1.0, p2), opacity=min(1.0, p2))
        paste_sprite(canvas, bank["slip_vs"], 540, 740, opacity=min(1.0, p2))

        if p1 > 0.1:
            V.text_c(canvas, 290, 1020, "~$16K", bank["F110"], V.GREEN, shadow=True)
            V.text_c(canvas, 290, 1120, "PER PERSON / YEAR", bank["F32"], V.INK_SOFT)
        if p2 > 0.1:
            V.text_c(canvas, 810, 1020, "$80K+", bank["F110"], V.RED, shadow=True)
            V.text_c(canvas, 810, 1120, "PER PERSON / YEAR", bank["F32"], V.INK_SOFT)

        paste_sprite(canvas, bank["chip_happier"], 290, 1330, offset_y=(1.0 - p3) * 50, opacity=min(1.0, p3))
        paste_sprite(canvas, bank["chip_less"], 810, 1330, offset_y=(1.0 - p3) * 50, opacity=min(1.0, p3))

    elif btype == "hedonic_treadmill":
        # Beat 6: Notebook cutoff + clean slip + spike-and-reset curve (NO YELLOW BANDS!)
        p_note = ease_out_back(min(1.0, el / 0.40)) * fade_out
        paste_sprite(canvas, bank["note_b6"], 540, NOTE_Y_SPEAKER, offset_y=-(1.0 - p_note) * 40, opacity=min(1.0, p_note))

        p0 = ease_out_cubic(min(1.0, max(0.0, (el - 0.15) / 0.40))) * fade_out
        paste_sprite(canvas, bank["slip_hedonic"], 540, 290, scale=0.92 + 0.08 * min(1.0, p0), opacity=min(1.0, p0))

        d = ImageDraw.Draw(canvas)
        base_y, x0, x1 = 700, 120, 960
        d.line([(x0, base_y), (x1, base_y)], fill=V.GOLD + (255,), width=6)
        V.text_c(canvas, 330, base_y + 36, "HAPPINESS BASELINE", bank["F32"], V.GOLD)

        curve_p = ease_in_out_cubic(min(1.0, max(0.0, (el - 0.25) / 1.6)))
        n_pts = max(2, int(80 * curve_p))
        if n_pts >= 2 and curve_p > 0.02:
            pts = []
            for k in range(n_pts):
                u = k / 79.0
                px = x0 + 20 + u * (x1 - x0 - 40)
                if u < 0.22:
                    py = base_y - math.sin(u / 0.22 * math.pi / 2.0) * 270.0
                else:
                    py = base_y - math.exp(-(u - 0.22) * 6.5) * 270.0
                pts.append((px, py))
            V.ink_line(canvas, pts, V.GREEN, 12)

        p_car = ease_out_back(min(1.0, max(0.0, (el - 0.55) / 0.40))) * fade_out
        p_norm = ease_out_back(min(1.0, max(0.0, (el - 1.25) / 0.45))) * fade_out
        paste_sprite(canvas, bank["chip_car"], 330, 370, offset_y=(1.0 - p_car) * 35, opacity=min(1.0, p_car))
        paste_sprite(canvas, bank["chip_norm"], 790, 620, offset_y=(1.0 - p_norm) * 35, opacity=min(1.0, p_norm))

    elif btype == "three_pillars":
        # Beat 7: Notebook cutoff + 3 hanging tags synced to step_timestamps
        p_note = ease_out_back(min(1.0, el / 0.40)) * fade_out
        paste_sprite(canvas, bank["note_b7"], 540, NOTE_Y_SPEAKER, offset_y=-(1.0 - p_note) * 40, opacity=min(1.0, p_note))

        steps = cue.get("step_timestamps", [])
        if len(steps) >= 3:
            t1, t2, t3 = float(steps[0]) - st, float(steps[1]) - st, float(steps[2]) - st
            t1 = min(t1, 1.2)
        else:
            t1, t2, t3 = 0.2, 2.2, 4.2

        p1 = ease_out_cubic(min(1.0, max(0.0, (el - t1) / 0.55))) * fade_out
        p2 = ease_out_cubic(min(1.0, max(0.0, (el - t2) / 0.55))) * fade_out
        p3 = ease_out_cubic(min(1.0, max(0.0, (el - t3) / 0.55))) * fade_out

        for p_val, key, cx in [(p1, "p1", 190), (p2, "p2", 540), (p3, "p3", 890)]:
            if p_val > 0.01:
                ep = ease_out_back(p_val, s=1.15)
                cur_top_y = TAG_TOP_SPEAKER - (1.0 - ep) * 480.0
                d = ImageDraw.Draw(canvas)
                eyelet_y = cur_top_y + (bank[f"{key}_ey"] - 10 / V.S)
                if eyelet_y > STRING_TO_SPEAKER:
                    d.line([(cx, STRING_TO_SPEAKER), (cx, int(eyelet_y))], fill=(70, 62, 54, 255), width=3)
                paste_sprite(canvas, bank[key], cx, cur_top_y + bank[f"{key}_h"] / 2 - 10 / V.S, opacity=min(1.0, p_val * 2.5))


def build_subtitle_chunks(transcript_data, total_duration, is_arabic=False):
    font_sub = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf" if is_arabic else "/System/Library/Fonts/Supplemental/Arial Black.ttf", 52 if is_arabic else 50)
    segments = transcript_data.get("segments", [])
    timed_words = []
    for seg in segments:
        for w in seg.get("words", []):
            timed_words.append(w)

    chunks = []
    spacing = 18
    curr_words = []
    curr_w = 0
    max_line_width = 860

    for w in timed_words:
        w_text = w["word"].upper() if not is_arabic else w["word"]
        disp = shape_text(w_text) if is_arabic else w_text
        bbox = font_sub.getbbox(disp)
        w_w = bbox[2] - bbox[0]
        needed_w = curr_w + (spacing if curr_words else 0) + w_w
        max_chunk = 3 if is_arabic else (3 if len(w_text) <= 4 or (curr_words and len(curr_words[0]["word"]) <= 3) else 2)
        if len(curr_words) >= max_chunk or (curr_words and needed_w > max_line_width):
            chunks.append({
                "words": curr_words,
                "start": curr_words[0]["start"],
                "end": curr_words[-1]["end"]
            })
            curr_words = [w]
            curr_w = w_w
        else:
            curr_words.append(w)
            curr_w = needed_w

    if curr_words:
        chunks.append({
            "words": curr_words,
            "start": curr_words[0]["start"],
            "end": curr_words[-1]["end"]
        })

    for i in range(len(chunks) - 1):
        gap = chunks[i + 1]["start"] - chunks[i]["end"]
        if 0.0 < gap < 0.24:
            chunks[i]["end"] = chunks[i + 1]["start"] - 0.01

    if chunks:
        chunks[-1]["end"] = min(total_duration - 0.15, chunks[-1]["end"] + 0.65)
    return chunks, font_sub


def draw_active_subtitle(canvas, chunks, cur_t, is_arabic, font_sub, dark_mode=False):
    active_chunk = None
    for c in chunks:
        if c["start"] <= cur_t <= c["end"] + 0.06:
            active_chunk = c
            break
    if not active_chunk:
        return

    active_word_idx = 0
    for w_i, w in enumerate(active_chunk["words"]):
        if w["start"] <= cur_t:
            active_word_idx = w_i

    words_list = [w["word"].upper() if not is_arabic else w["word"] for w in active_chunk["words"]]
    spacing = 18
    word_boxes = []
    total_w = 0
    for idx, w_str in enumerate(words_list):
        disp_str = shape_text(w_str) if is_arabic else w_str
        bbox = font_sub.getbbox(disp_str)
        w_w = bbox[2] - bbox[0]
        w_h = bbox[3] - bbox[1]
        word_boxes.append((w_str, disp_str, w_w, w_h))
        total_w += w_w
    total_w += spacing * (len(words_list) - 1)

    start_x = (V.W - total_w) // 2
    cy = 1710 if dark_mode else 1555
    d = ImageDraw.Draw(canvas)

    stroke_col = (250, 248, 243, 255) if dark_mode else (18, 16, 14, 255)
    shadow_col = (40, 35, 28, 90) if dark_mode else (10, 10, 10, 220)
    base_fill = V.INK + (255,) if dark_mode else (255, 255, 255, 255)
    active_fill = V.GREEN + (255,) if dark_mode else (250, 204, 21, 255)

    if is_arabic:
        cur_x = start_x + total_w
        for i, (w_str, disp_str, w_w, w_h) in enumerate(word_boxes):
            cur_x -= w_w
            fill_c = active_fill if i == active_word_idx else base_fill
            y_pos = cy - (4 if i == active_word_idx else 0)
            d.text((cur_x + 2, y_pos + 4), disp_str, font=font_sub, fill=shadow_col, stroke_width=5, stroke_fill=shadow_col)
            d.text((cur_x, y_pos), disp_str, font=font_sub, fill=fill_c, stroke_width=4, stroke_fill=stroke_col)
            cur_x -= spacing
    else:
        cur_x = start_x
        for i, (w_str, disp_str, w_w, w_h) in enumerate(word_boxes):
            fill_c = active_fill if i == active_word_idx else base_fill
            y_pos = cy - (4 if i == active_word_idx else 0)
            d.text((cur_x + 2, y_pos + 4), disp_str, font=font_sub, fill=shadow_col, stroke_width=5, stroke_fill=shadow_col)
            d.text((cur_x, y_pos), disp_str, font=font_sub, fill=fill_c, stroke_width=4, stroke_fill=stroke_col)
            cur_x += w_w + spacing


def get_video_info(video_path):
    cmd = [
        "ffprobe", "-v", "error", "-select_streams", "v:0",
        "-show_entries", "stream=r_frame_rate,duration",
        "-of", "json", str(video_path)
    ]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
    info = json.loads(res.stdout)["streams"][0]
    num, den = map(int, info["r_frame_rate"].split("/"))
    fps = num / float(den)
    dur = float(info.get("duration", 0.0))
    return fps, dur


def render_reel_video(cleaned_video, transcript_json, storyboard_json, output_mp4, lang="en", bgm_vol=0.045):
    is_arabic = lang in ["ary", "darija", "moroccan"]
    fps, total_dur = get_video_info(cleaned_video)
    fps_int = int(round(fps))

    with open(transcript_json, "r", encoding="utf-8") as f:
        transcript_data = json.load(f)
    with open(storyboard_json, "r", encoding="utf-8") as f:
        storyboard_data = json.load(f)

    cues = storyboard_data.get("storyboard", [])
    fullscreen_paper_types = {"log_income_curve", "country_comparison"}

    print(f"[render_reel] Pre-baking sprites & academic notebook cutoffs for {Path(cleaned_video).name}...")
    bank = build_sprite_bank()
    paper_base = V.paper_background()
    sub_chunks, font_sub = build_subtitle_chunks(transcript_data, total_dur, is_arabic=is_arabic)

    seg_model = str(SKILL_ROOT / "models" / "selfie_segmenter.tflite")
    segmenter = vision.ImageSegmenter.create_from_options(vision.ImageSegmenterOptions(
        base_options=mpp.BaseOptions(model_asset_path=seg_model),
        output_confidence_masks=True,
        output_category_mask=False
    ))

    temp_silent_mp4 = Path(output_mp4).parent / f"_temp_render_reel_{lang}.mp4"

    in_cmd = [
        "ffmpeg", "-v", "error", "-i", str(cleaned_video),
        "-vf", (
            "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
            "eq=contrast=1.05:brightness=0.02:saturation=1.06,"
            "unsharp=5:5:0.5:5:5:0.2"
        ),
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-"
    ]
    out_cmd = [
        "ffmpeg", "-y", "-v", "error",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "1080x1920", "-r", str(fps_int),
        "-i", "-",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p",
        str(temp_silent_mp4)
    ]

    in_proc = subprocess.Popen(in_cmd, stdout=subprocess.PIPE)
    out_proc = subprocess.Popen(out_cmd, stdin=subprocess.PIPE)

    frame_bytes = 1080 * 1920 * 3
    f_idx = 0
    t0 = time.time()
    smoothed_head_top = None

    print(f"[render_reel] Streaming frames at {fps_int}fps ({total_dur:.1f}s)...")
    while True:
        raw = in_proc.stdout.read(frame_bytes)
        if len(raw) < frame_bytes:
            break
        cur_t = f_idx / float(fps_int)
        frame_np = np.frombuffer(raw, dtype=np.uint8).reshape((1920, 1080, 3))

        # Check active beat cue
        active_cue = None
        for cue in cues:
            st = float(cue.get("start_time", 0.0))
            et = float(cue.get("end_time", st + 8.0))
            if st <= cur_t <= et:
                active_cue = cue
                break

        btype = (active_cue.get("template") or active_cue.get("animation_type", "")) if active_cue else ""
        is_full_paper = (active_cue is not None) and (btype in fullscreen_paper_types)

        if active_cue is None:
            # State 1: REAL SPEAKER BACKGROUND (hook, pauses between beats, outro)
            raw_im = Image.fromarray(frame_np, "RGB")
            punch = 1.04 if (int(cur_t / 4.5) % 2 == 1) else 1.0
            if punch > 1.001:
                im_punched = raw_im.resize((int(1080 * punch), int(1920 * punch)), Image.BILINEAR)
                sx = (1080 - im_punched.width) // 2
                sy = (1920 - im_punched.height) // 2
                canvas = im_punched.crop((-sx, -sy, -sx + 1080, -sy + 1920)).convert("RGBA")
            else:
                canvas = raw_im.convert("RGBA")

            draw_active_subtitle(canvas, sub_chunks, cur_t, is_arabic, font_sub, dark_mode=False)

        elif is_full_paper:
            # State 3: Full-Screen Paper Infographics (Beat 3 & Beat 5)
            canvas = paper_base.copy()
            render_beat_graphics(canvas, active_cue, cur_t, bank)
            draw_active_subtitle(canvas, sub_chunks, cur_t, is_arabic, font_sub, dark_mode=True)

        else:
            # State 2: Lowered Cutout Speaker on Paper + Objects & Notebook Cutoff Above
            canvas = paper_base.copy()

            mp_img = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_np)
            res = segmenter.segment(mp_img)
            m = res.confidence_masks[0].numpy_view()[:, :, 0].astype(np.float32)
            if m[int(1920 * 0.62):int(1920 * 0.75), int(1080 * 0.4):int(1080 * 0.6)].mean() < 0.5:
                m = 1.0 - m

            rows = np.where((m > 0.5).sum(axis=1) > 40)[0]
            cur_ht = int(rows[0]) if len(rows) else 220
            if smoothed_head_top is None:
                smoothed_head_top = float(cur_ht)
            else:
                smoothed_head_top = 0.92 * smoothed_head_top + 0.08 * cur_ht

            cut_rgba = fast_cutout_rgba(frame_np, m)

            st = float(active_cue.get("start_time", 0.0))
            et = float(active_cue.get("end_time", st + 8.0))
            p_in = ease_out_cubic(min(1.0, (cur_t - st) / 0.28))
            p_out = ease_out_cubic(min(1.0, (et - cur_t) / 0.28))
            lower_p = min(p_in, p_out)

            sc = 1.0 - 0.10 * lower_p
            target_y = int((800 - int(smoothed_head_top * 0.90)) * lower_p)
            im_spk = cut_rgba.resize((int(1080 * sc), int(1920 * sc)), Image.BILINEAR)
            sx = (1080 - im_spk.width) // 2

            if lower_p < 0.98:
                raw_im = Image.fromarray(frame_np, "RGB").convert("RGBA")
                canvas = Image.blend(raw_im, canvas, lower_p)

            canvas.alpha_composite(im_spk, (sx, target_y))
            render_beat_graphics(canvas, active_cue, cur_t, bank)
            draw_active_subtitle(canvas, sub_chunks, cur_t, is_arabic, font_sub, dark_mode=False)

        out_proc.stdin.write(canvas.convert("RGB").tobytes())
        f_idx += 1
        if f_idx % 300 == 0:
            elapsed = time.time() - t0
            print(f"  [render_reel] Rendered {f_idx} frames ({cur_t:.1f}s / {total_dur:.1f}s) at {f_idx / elapsed:.1f} fps")

    in_proc.stdout.close()
    in_proc.wait()
    out_proc.stdin.close()
    out_proc.wait()

    print(f"[render_reel] Video complete ({f_idx} frames in {time.time() - t0:.1f}s). Mixing broadcast audio + BGM + SFX...")
    mux_audio(cleaned_video, temp_silent_mp4, cues, output_mp4, total_dur, bgm_vol=bgm_vol)
    if temp_silent_mp4.exists():
        temp_silent_mp4.unlink()

    verify_production_quality(output_mp4)
    return output_mp4


def mux_audio(cleaned_video, silent_video, cues, output_mp4, total_dur, bgm_vol=0.045):
    cmd = ["ffmpeg", "-y", "-v", "error", "-i", str(silent_video), "-i", str(cleaned_video)]
    next_idx = 2

    ambient_idx = None
    ambient_path = find_sfx_path("ambient_bed.wav")
    if ambient_path:
        ambient_idx = next_idx
        next_idx += 1
        cmd.extend(["-i", str(ambient_path)])

    sfx_events = []
    for cue in cues:
        st = float(cue.get("start_time", 0.0))
        for offset_sec, sfx_name, sfx_vol in get_synced_sfx_schedule_for_cue(cue):
            sfx_p = find_sfx_path(sfx_name)
            if sfx_p:
                sfx_events.append({
                    "input_idx": next_idx,
                    "time": max(0.0, st + float(offset_sec)),
                    "vol": float(sfx_vol)
                })
                next_idx += 1
                cmd.extend(["-i", str(sfx_p)])

    filter_chains = [
        "[1:a]highpass=f=85,"
        "lowpass=f=12000,"
        "afftdn=nr=24:nf=-48:tn=1,"
        "equalizer=f=250:t=q:w=1.2:g=-1.5,"
        "equalizer=f=3200:t=q:w=1.4:g=3.2,"
        "agate=threshold=-34dB:ratio=2.5:attack=10:release=120:range=-24dB,"
        "acompressor=threshold=-22dB:ratio=3.5:attack=10:release=90:makeup=3.5dB,"
        "loudnorm=I=-11.5:LRA=3.0:TP=-0.2[a_voice]"
    ]
    mix_inputs = ["[a_voice]"]

    if ambient_idx is not None:
        fade_out_st = max(0.5, total_dur - 1.2)
        filter_chains.append(
            f"[{ambient_idx}:a]atrim=start=0:end={total_dur:.2f},asetpts=PTS-STARTPTS,"
            f"lowpass=f=850,volume={bgm_vol:.3f},"
            f"afade=t=in:st=0:d=0.9,afade=t=out:st={fade_out_st:.2f}:d=1.2,"
            f"aformat=channel_layouts=stereo[a_bed]"
        )
        mix_inputs.append("[a_bed]")

    for k, sfx in enumerate(sfx_events):
        delay_ms = max(0, int(sfx["time"] * 1000))
        vol = sfx["vol"]
        filter_chains.append(
            f"[{sfx['input_idx']}:a]lowpass=f=3600,adelay={delay_ms}|{delay_ms},"
            f"volume={vol:.3f},aformat=channel_layouts=stereo[sfx{k}]"
        )
        mix_inputs.append(f"[sfx{k}]")

    if len(mix_inputs) > 1:
        mix_str = "".join(mix_inputs)
        filter_chains.append(
            f"{mix_str}amix=inputs={len(mix_inputs)}:duration=first:dropout_transition=0:normalize=0,"
            f"alimiter=limit=0.98:level=disabled[a_prod]"
        )
    else:
        filter_chains.append("[a_voice]alimiter=limit=0.98:level=disabled[a_prod]")

    cmd.extend([
        "-filter_complex", ";".join(filter_chains),
        "-map", "0:v:0",
        "-map", "[a_prod]",
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", "192k",
        str(output_mp4)
    ])
    subprocess.run(cmd, check=True)
    print(f"[render_reel] ✓ Final Master Reel saved to: {output_mp4}")


def main():
    parser = argparse.ArgumentParser(description="Render Master Production Reel.")
    parser.add_argument("--cleaned-video", "-v", required=False, help="Cleaned video path")
    parser.add_argument("--transcript", "-t", required=False, help="Transcript JSON path")
    parser.add_argument("--storyboard", "-s", required=False, help="Storyboard JSON path")
    parser.add_argument("--output", "-o", required=False, help="Output MP4 path")
    parser.add_argument("--lang", "-l", default="en", help="Language: en or darija")
    parser.add_argument("--bgm-vol", type=float, default=0.045, help="Background music volume")
    args = parser.parse_args()

    if args.cleaned_video and args.output:
        render_reel_video(args.cleaned_video, args.transcript, args.storyboard, args.output, lang=args.lang, bgm_vol=args.bgm_vol)
    else:
        out_dir = Path.home() / "Desktop" / "projects" / "reels_IG" / "edited_output" / "v10_polished_edits"
        out_dir.mkdir(parents=True, exist_ok=True)
        base_cache = Path.home() / "Desktop" / "projects" / "reels_IG" / "edited_output"

        jobs = [
            {"name": "English_Money_vs_Happiness_V10", "stem": "C7BAE170-9BB5-4BEC-8458-460D29B3C1B7", "lang": "en"},
            {"name": "Darija_Money_vs_Happiness_V10", "stem": "2E1174BB-9D62-4DD0-B768-1A579C686590", "lang": "darija"}
        ]
        for job in jobs:
            cache_dir = base_cache / f".reel_cache_{job['stem']}"
            cleaned_v = cache_dir / f"{job['stem']}_cleaned.mp4"
            trans_j = cache_dir / f"{job['stem']}_transcript.json"
            sb_j = cache_dir / f"{job['stem']}_storyboard.json"
            out_mp4 = out_dir / f"{job['name']}_PROD.mp4"
            out_meta = out_dir / f"{job['name']}_POST_METADATA.json"

            print(f"\n🚀 RENDERING MASTER REEL: {job['name']} ({job['lang']})")
            render_reel_video(cleaned_v, trans_j, sb_j, out_mp4, lang=job["lang"], bgm_vol=args.bgm_vol)

            with open(sb_j, "r", encoding="utf-8") as f:
                sb_data = json.load(f)
            meta = sb_data.get("post_metadata", {})
            if meta:
                with open(out_meta, "w", encoding="utf-8") as mf:
                    json.dump(meta, mf, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()
