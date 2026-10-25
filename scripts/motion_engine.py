#!/usr/bin/env python3
"""
motion_engine.py - Step 3: Light Modern Editorial Motion Graphics & Parallel Multi-Worker Renderer
Inspired by 'Example to learn from.MP4' (50/50 Split-Screen: 100% Opaque Visuals Above + Speaker Below)
& the 5-Step Master AI Video Editor Workflow.

Features:
1. 100% Opaque Top-Half Split-Screen Light Editorial Canvas (1080x920, alpha=255):
   - Warm Alabaster / Studio White (#F6F8FC) background with Royal Cobalt Blue (#2563EB) & Emerald (#059669) accents.
   - Zero alpha fade on the background — guarantees the top half of the background video NEVER bleeds through.
   - Leaves the bottom half (y=920..1920, 1080x1000) for the live speaker talking down below.
2. Parallel Multi-Worker Rendering (Capped at 4 Workers):
   - Renders beat graphics concurrently using `ProcessPoolExecutor(max_workers=4)` to maximize speed without system overload.
3. Millisecond-Locked Kinetic Subtitles:
   - Crisp white & modern Sky-Cyan / Emerald / Gold word-pop typography with deep slate-navy (#0F172A) stroke at y=1555,
     positioned cleanly across the lower third of the speaker in both full-screen and 50/50 split-screen modes.
"""

import os
import re
import sys
import math
import json
import subprocess
import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

SKILL_ROOT = Path(__file__).resolve().parent.parent
if str(SKILL_ROOT) not in sys.path:
    sys.path.insert(0, str(SKILL_ROOT))

from motion_library.renderers import (
    TEMPLATE_MAP,
    get_editorial_background,
    draw_hud_progress_filament,
    shape_text,
    COBALT_ACCENT,
    EMERALD_ACCENT,
    DEEP_NAVY,
    PURE_WHITE,
    MUTED_SLATE
)


def get_fonts(is_arabic=False):
    fonts = {}
    if is_arabic:
        try:
            ar_bold = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
            fonts["kicker"] = ImageFont.truetype(ar_bold, 19)
            fonts["headline"] = ImageFont.truetype(ar_bold, 38)
            fonts["title"] = ImageFont.truetype(ar_bold, 36)
            fonts["hero_title"] = ImageFont.truetype(ar_bold, 44)
            fonts["hero_stat"] = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Black.ttf", 58)
            fonts["pill"] = ImageFont.truetype(ar_bold, 20)
            fonts["giant_num"] = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Black.ttf", 76)
            fonts["card_num"] = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Black.ttf", 42)
            fonts["card_title"] = ImageFont.truetype(ar_bold, 26)
            fonts["citation_title"] = ImageFont.truetype(ar_bold, 21)
            fonts["citation_sub"] = ImageFont.truetype(ar_bold, 18)
            fonts["badge"] = ImageFont.truetype(ar_bold, 19)
            fonts["label"] = ImageFont.truetype(ar_bold, 22)
            fonts["sub"] = ImageFont.truetype(ar_bold, 46)
            fonts["sub_pop1"] = ImageFont.truetype(ar_bold, 49)
            fonts["sub_pop2"] = ImageFont.truetype(ar_bold, 52)
        except Exception:
            f_def = ImageFont.load_default()
            for k in ["kicker", "headline", "title", "hero_title", "hero_stat", "pill", "giant_num", "card_num", "card_title", "citation_title", "citation_sub", "badge", "label", "sub", "sub_pop1", "sub_pop2"]:
                fonts[k] = f_def
    else:
        try:
            fonts["kicker"] = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 19)
            fonts["headline"] = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Black.ttf", 38)
            fonts["title"] = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Black.ttf", 36)
            fonts["hero_title"] = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Black.ttf", 44)
            fonts["hero_stat"] = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Black.ttf", 58)
            fonts["pill"] = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 20)
            fonts["giant_num"] = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Black.ttf", 76)
            fonts["card_num"] = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Black.ttf", 42)
            fonts["card_title"] = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 26)
            fonts["citation_title"] = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 21)
            fonts["citation_sub"] = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 18)
            fonts["badge"] = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 19)
            fonts["label"] = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 21)
            fonts["sub"] = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Black.ttf", 44)
            fonts["sub_pop1"] = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Black.ttf", 47)
            fonts["sub_pop2"] = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Black.ttf", 50)
        except Exception:
            f_def = ImageFont.load_default()
            for k in ["kicker", "headline", "title", "hero_title", "hero_stat", "pill", "giant_num", "card_num", "card_title", "citation_title", "citation_sub", "badge", "label", "sub", "sub_pop1", "sub_pop2"]:
                fonts[k] = f_def

    return fonts


SKY_CYAN_POP = (56, 189, 248, 255)      # #38BDF8 Modern Sky Cyan
EMERALD_MINT_POP = (52, 211, 153, 255)  # #34D399 Modern Emerald Mint
WARM_GOLD_POP = (251, 191, 36, 255)     # #FBBF24 Warm Amber Gold

SEMANTIC_ALPHA_TERMS = {
    "happiness", "wealth", "income", "autonomy", "freedom", "generosity", "experiences", "memories",
    "peace", "love", "costa", "rica", "flourishing", "75,000", "200,000", "500,000", "800,000",
    "السعادة", "الفلوس", "حريتك", "الأمان", "والحرية", "التجارب", "العطاء", "ربح", "كوستاريكا"
}

SEMANTIC_RISK_TERMS = {
    "stops", "catch", "tiny", "unhappiest", "stress", "zero", "treadmill", "hedonic", "debt",
    "uncertainty", "terrible", "meaningless", "0.09",
    "مكتبقاش", "ضعيفة", "الضغط", "التعود", "الستريس", "الكريدي"
}

SEMANTIC_TECH_TERMS = {
    "kahneman", "killingsworth", "logarithmic", "linear", "statistical", "correlation", "harvard",
    "dunn", "psychologists", "study", "report", "gdp",
    "كانيمان", "كيلينغسوورث", "لوغاريتمية", "هارفارد", "إليزابيث", "دراسة", "تقرير"
}


def resolve_semantic_word_color(word_str, is_arabic=False, custom_highlights=None):
    clean_w = re.sub(r"[^\w\-\u0600-\u06FF\d\.]", "", word_str).lower()

    if custom_highlights:
        alpha_list = [w.lower() for w in custom_highlights.get("alpha", [])]
        risk_list = [w.lower() for w in custom_highlights.get("risk", [])]
        tech_list = [w.lower() for w in custom_highlights.get("tech", [])]
        if any(term in clean_w for term in risk_list):
            return SKY_CYAN_POP
        if any(term in clean_w for term in alpha_list):
            return EMERALD_MINT_POP
        if any(term in clean_w for term in tech_list):
            return WARM_GOLD_POP

    if any(k in clean_w for k in SEMANTIC_RISK_TERMS):
        return SKY_CYAN_POP
    if any(k in clean_w for k in SEMANTIC_TECH_TERMS):
        return WARM_GOLD_POP
    if any(k in clean_w for k in SEMANTIC_ALPHA_TERMS):
        return EMERALD_MINT_POP

    return SKY_CYAN_POP if not is_arabic else WARM_GOLD_POP


def render_cue_to_video(cue, output_mov_path, fps=24, is_arabic=False):
    """
    Renders a single visual beat cue onto a 100% opaque 1080x920 Top-Half Split-Screen
    Light Modern Editorial canvas (alpha=255 on every frame).
    """
    duration = float(cue.get("duration", 9.0))
    total_frames = max(12, int(duration * fps))
    anim_type = cue.get("template") or cue.get("animation_type", "study_citation")
    layout_mode = cue.get("layout_mode", "split")

    template_key = anim_type if anim_type in TEMPLATE_MAP else "study_citation"
    renderer_fn = TEMPLATE_MAP[template_key]

    canvas_w = 1080
    split_h = int(cue.get("split_height", 920))
    canvas_h = split_h if layout_mode == "split" else 1920
    render_h = canvas_h

    fonts = get_fonts(is_arabic=is_arabic)
    print(f"[motion_engine] Rendering '{template_key}' [{layout_mode.upper()} OPAQUE {canvas_w}x{canvas_h}] ({duration:.1f}s, {total_frames} frames)...")

    cmd = [
        "ffmpeg", "-y",
        "-f", "rawvideo",
        "-pix_fmt", "rgba",
        "-s", f"{canvas_w}x{canvas_h}",
        "-r", str(fps),
        "-i", "-",
        "-c:v", "qtrle",
        str(output_mov_path)
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    for f_idx in range(total_frames):
        t_norm = f_idx / float(max(1, total_frames - 1))

        img = get_editorial_background(canvas_w, canvas_h)
        draw = ImageDraw.Draw(img)

        try:
            renderer_fn(draw, t_norm, f_idx, cue, fonts, width=canvas_w, height=render_h, is_arabic=is_arabic, img=img)
        except TypeError:
            renderer_fn(draw, t_norm, f_idx, cue, fonts, width=canvas_w, height=render_h, is_arabic=is_arabic)
        if layout_mode == "split":
            draw_hud_progress_filament(draw, t_norm, cue, width=canvas_w, y_pos=canvas_h - 4)
        else:
            draw_hud_progress_filament(draw, t_norm, cue, width=canvas_w, y_pos=canvas_h - 6)

        proc.stdin.write(img.tobytes())

    proc.stdin.close()
    proc.wait()
    print(f"[motion_engine] ✓ Saved liquid glass floating visual to {output_mov_path}")
    return str(output_mov_path)


def _worker_render_task(task_tuple):
    idx, cue, mov_path_str, fps, is_arabic = task_tuple
    render_cue_to_video(cue, Path(mov_path_str), fps=fps, is_arabic=is_arabic)
    return idx, {"cue": cue, "video_path": mov_path_str}


def render_burnt_in_subtitles(transcript_data, output_mov_path, total_duration, fps=24, lang="en"):
    """
    Renders millisecond-accurate kinetic word-level subtitles at base_y = 1555,
    sitting cleanly over the speaker's lower chest in both full-screen and 50/50 split-screen modes.
    """
    print(f"\n[motion_engine] Rendering acoustic-locked kinetic subtitles ({total_duration:.2f}s)...")
    is_arabic = lang in ["ary", "darija", "moroccan"]
    fonts = get_fonts(is_arabic=is_arabic)
    font_sub = fonts["sub"]
    font_sub_pop1 = fonts["sub_pop1"]
    font_sub_pop2 = fonts["sub_pop2"]

    custom_highlights = transcript_data.get("semantic_highlights", {})

    width, height = 1080, 1920
    max_line_width = 820
    total_frames = max(1, int(total_duration * fps))

    segments = transcript_data.get("segments", [])
    timed_words = []
    for seg in segments:
        words = seg.get("words", [])
        for w in words:
            timed_words.append(w)

    chunks = []
    spacing = 18
    curr_words = []
    curr_w = 0

    for w in timed_words:
        w_text = w["word"].upper() if not is_arabic else w["word"]
        bbox = font_sub.getbbox(w_text)
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

    cmd = [
        "ffmpeg", "-y",
        "-f", "rawvideo",
        "-pix_fmt", "rgba",
        "-s", f"{width}x{height}",
        "-r", str(fps),
        "-i", "-",
        "-c:v", "qtrle",
        str(output_mov_path)
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    blank_img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    blank_bytes = blank_img.tobytes()

    last_rendered_key = None
    last_rendered_bytes = blank_bytes

    base_y = 1540
    stroke_col = (9, 13, 22, 255)
    shadow_col = (9, 13, 22, 230)

    for f_idx in range(total_frames):
        cur_t = f_idx / float(fps)

        active_chunk = None
        for c in chunks:
            if c["start"] <= cur_t <= c["end"] + 0.06:
                active_chunk = c
                break

        if not active_chunk:
            proc.stdin.write(blank_bytes)
            last_rendered_key = None
            continue

        active_word_idx = 0
        pop_stage = 0
        lift_y = 0
        active_font = font_sub

        active_word_obj = active_chunk["words"][0]
        for w_i, w in enumerate(active_chunk["words"]):
            if w["start"] <= cur_t:
                active_word_idx = w_i
                active_word_obj = w

        word_elapsed = cur_t - active_word_obj.get("start", cur_t)
        if 0.0 <= word_elapsed < 0.05:
            pop_stage = 2
            lift_y = 6
            active_font = font_sub_pop2
        elif 0.05 <= word_elapsed < 0.11:
            pop_stage = 1
            lift_y = 3
            active_font = font_sub_pop1

        key = (id(active_chunk), active_word_idx, pop_stage)
        if key == last_rendered_key:
            proc.stdin.write(last_rendered_bytes)
            continue

        img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)

        words_list = [w["word"].upper() if not is_arabic else w["word"] for w in active_chunk["words"]]
        word_boxes = []
        total_w = 0

        for idx, w_str in enumerate(words_list):
            f_use = active_font if idx == active_word_idx else font_sub
            disp_str = shape_text(w_str) if is_arabic else w_str
            bbox = f_use.getbbox(disp_str)
            w_w = bbox[2] - bbox[0]
            w_h = bbox[3] - bbox[1]
            word_boxes.append((w_str, disp_str, w_w, w_h, f_use))
            total_w += w_w
        total_w += spacing * (len(words_list) - 1)

        start_x = (width - total_w) // 2

        if is_arabic:
            cur_x = start_x + total_w
            for i, (w_str, disp_str, w_w, w_h, f_use) in enumerate(word_boxes):
                cur_x -= w_w
                if i == active_word_idx:
                    fill_color = resolve_semantic_word_color(w_str, is_arabic=True, custom_highlights=custom_highlights)
                    y_pos = base_y - lift_y
                    d.text((cur_x + 3, y_pos + 4), disp_str, font=f_use, fill=shadow_col, stroke_width=5, stroke_fill=shadow_col)
                    d.text((cur_x, y_pos), disp_str, font=f_use, fill=fill_color, stroke_width=5, stroke_fill=stroke_col)
                else:
                    y_pos = base_y
                    d.text((cur_x + 3, y_pos + 4), disp_str, font=f_use, fill=shadow_col, stroke_width=4, stroke_fill=shadow_col)
                    d.text((cur_x, y_pos), disp_str, font=f_use, fill=PURE_WHITE, stroke_width=5, stroke_fill=stroke_col)
                cur_x -= spacing
        else:
            cur_x = start_x
            for i, (w_str, disp_str, w_w, w_h, f_use) in enumerate(word_boxes):
                if i == active_word_idx:
                    fill_color = resolve_semantic_word_color(w_str, is_arabic=False, custom_highlights=custom_highlights)
                    y_pos = base_y - lift_y
                    d.text((cur_x + 3, y_pos + 4), disp_str, font=f_use, fill=shadow_col, stroke_width=5, stroke_fill=shadow_col)
                    d.text((cur_x, y_pos), disp_str, font=f_use, fill=fill_color, stroke_width=5, stroke_fill=stroke_col)
                else:
                    y_pos = base_y
                    d.text((cur_x + 3, y_pos + 4), disp_str, font=f_use, fill=shadow_col, stroke_width=4, stroke_fill=shadow_col)
                    d.text((cur_x, y_pos), disp_str, font=f_use, fill=PURE_WHITE, stroke_width=5, stroke_fill=stroke_col)
                cur_x += w_w + spacing

        last_rendered_bytes = img.tobytes()
        last_rendered_key = key
        proc.stdin.write(last_rendered_bytes)

    proc.stdin.close()
    proc.wait()
    print(f"[motion_engine] Saved kinetic burnt-in subtitles to {output_mov_path}")
    return output_mov_path


def main():
    parser = argparse.ArgumentParser(description="Render 50/50 Split-Screen Light Modern Editorial 2D motion graphics in parallel (max 4 workers) and burnt-in subtitles.")
    parser.add_argument("--storyboard", "-s", default=None, help="Storyboard JSON file")
    parser.add_argument("--subtitles-transcript", "-t", default=None, help="Transcript JSON file for subtitles")
    parser.add_argument("--subtitles-out", default=None, help="Output MOV path for burnt-in subtitles")
    parser.add_argument("--duration", type=float, default=25.0, help="Total video duration for subtitles")
    parser.add_argument("--output-dir", "-o", default="./.reel_cache/overlays", help="Output directory")
    parser.add_argument("--fps", type=int, default=24, help="FPS")
    parser.add_argument("--workers", type=int, default=4, help="Max parallel rendering sub-agents/workers (capped at 4)")
    parser.add_argument("--lang", "-l", default="en", help="Language")
    args = parser.parse_args()

    if args.subtitles_transcript and args.subtitles_out:
        with open(args.subtitles_transcript, "r", encoding="utf-8") as f:
            t_data = json.load(f)
        render_burnt_in_subtitles(t_data, args.subtitles_out, args.duration, args.fps, args.lang)
        return

    if args.storyboard:
        with open(args.storyboard, "r", encoding="utf-8") as f:
            data = json.load(f)

        cues = data.get("storyboard", [])
        out_dir = Path(args.output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)

        is_arabic = args.lang in ["ary", "darija", "moroccan"]
        max_workers = max(1, min(4, int(args.workers)))
        print(f"[motion_engine] Launching Step 3 Multi-Worker Motion Rendering (capped at {max_workers} parallel workers)...")

        tasks = []
        for idx, cue in enumerate(cues):
            template_name = cue.get("template") or cue.get("animation_type", "study_citation")
            mov_path = out_dir / f"overlay_{idx}_{template_name}.mov"
            tasks.append((idx, cue, str(mov_path), args.fps, is_arabic))

        results_by_idx = {}
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(_worker_render_task, t) for t in tasks]
            for fut in as_completed(futures):
                idx, item = fut.result()
                results_by_idx[idx] = item

        rendered_manifest = [results_by_idx[i] for i in sorted(results_by_idx.keys())]

        manifest_file = out_dir / "rendered_overlays.json"
        with open(manifest_file, "w", encoding="utf-8") as f:
            json.dump(rendered_manifest, f, indent=2, ensure_ascii=False)

        print(f"[motion_engine] Successfully rendered {len(rendered_manifest)} 50/50 Split-Screen Light Editorial Overlays.")


if __name__ == "__main__":
    main()
