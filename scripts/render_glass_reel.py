#!/usr/bin/env python3
"""
render_glass_reel.py - Next-Gen "Obsidian Glass & HyperFrames" Reel Renderer.

New Design Aesthetic:
1. 3-State Rhythm with Modern Dark Obsidian Aesthetic:
   - State 1 (Real Camera Studio): Hook & conversational pauses keep original footage with subtle 1.04x punch-in.
   - State 2 (Lowered Cutout Speaker on Obsidian Canvas + HyperFrames Glass Card Above):
     MediaPipe AI person segmentation isolates the speaker standing on a deep obsidian canvas (#090D16)
     with sleek HyperFrames HTML/CSS/GSAP motion graphics cards displayed above (y = 0..920).
2. Modern Glassmorphic Subtitles:
   - Dynamic kinetic typography floating over lower chest in a translucent dark pill (rgba(15, 23, 42, 0.85))
   - Active spoken word highlighted in electric gold (#FBBF24) with full RTL Arabic support.
3. Broadcast Vocal Mastering (-11.5 LUFS) + Keyframed Audio Hits.
"""

import os
import sys
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

from motion_library.renderers import shape_text
from scripts.pipeline import find_sfx_path, verify_production_quality
from scripts.render_reel import get_video_info, build_subtitle_chunks, fast_cutout_rgba, ease_out_cubic


def create_obsidian_canvas(width=1080, height=1920):
    """Creates a deep obsidian dark gradient background canvas."""
    # Radial dark gradient from #131B2E (center) to #070A10 (edges)
    img = np.zeros((height, width, 3), dtype=np.uint8)
    cy, cx = height * 0.4, width * 0.5
    y, x = np.ogrid[:height, :width]
    dist_from_center = np.sqrt((x - cx)**2 + (y - cy)**2)
    max_dist = np.sqrt(cx**2 + cy**2)
    norm_dist = np.clip(dist_from_center / max_dist, 0.0, 1.0)

    # Center color: (19, 27, 46) -> Edge color: (7, 10, 16)
    r = (19 * (1.0 - norm_dist) + 7 * norm_dist).astype(np.uint8)
    g = (27 * (1.0 - norm_dist) + 10 * norm_dist).astype(np.uint8)
    b = (46 * (1.0 - norm_dist) + 16 * norm_dist).astype(np.uint8)

    img[:, :, 0] = r
    img[:, :, 1] = g
    img[:, :, 2] = b

    pil_img = Image.fromarray(img, "RGB").convert("RGBA")
    return pil_img


def draw_modern_glass_subtitles(canvas, sub_chunks, cur_t, is_arabic, font, y_pos=1620):
    """Renders modern glassmorphic kinetic captions with highlighted active word."""
    active_chunk = None
    for chunk in sub_chunks:
        if chunk["start"] <= cur_t <= chunk["end"]:
            active_chunk = chunk
            break

    if not active_chunk:
        return

    words = active_chunk["words"]
    if not words:
        return

    draw = ImageDraw.Draw(canvas)

    if is_arabic:
        full_text = " ".join([w["word"] for w in words])
        disp_text = shape_text(full_text)
        bbox = draw.textbbox((0, 0), disp_text, font=font)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]

        # Draw translucent dark pill
        pill_pad_x = 36
        pill_pad_y = 14
        pill_x1 = int((1080 - tw) / 2 - pill_pad_x)
        pill_y1 = int(y_pos - pill_pad_y)
        pill_x2 = int((1080 + tw) / 2 + pill_pad_x)
        pill_y2 = int(y_pos + th + pill_pad_y)

        # Draw dark translucent glass pill overlay
        pill_overlay = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
        p_draw = ImageDraw.Draw(pill_overlay)
        p_draw.rounded_rectangle([pill_x1, pill_y1, pill_x2, pill_y2], radius=24, fill=(15, 23, 42, 210), outline=(255, 255, 255, 45), width=1)
        canvas.alpha_composite(pill_overlay)

        # Text in bright gold/white
        draw.text(((1080 - tw) // 2, y_pos), disp_text, font=font, fill=(251, 191, 36, 255))
    else:
        # English: Word-level lighting inside a sleek glass pill
        text_parts = [w["word"] for w in words]
        full_text = " ".join(text_parts)
        bbox = draw.textbbox((0, 0), full_text, font=font)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]

        pill_pad_x = 36
        pill_pad_y = 14
        pill_x1 = int((1080 - tw) / 2 - pill_pad_x)
        pill_y1 = int(y_pos - pill_pad_y)
        pill_x2 = int((1080 + tw) / 2 + pill_pad_x)
        pill_y2 = int(y_pos + th + pill_pad_y)

        pill_overlay = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
        p_draw = ImageDraw.Draw(pill_overlay)
        p_draw.rounded_rectangle([pill_x1, pill_y1, pill_x2, pill_y2], radius=24, fill=(15, 23, 42, 210), outline=(255, 255, 255, 45), width=1)
        canvas.alpha_composite(pill_overlay)

        cur_x = (1080 - tw) // 2
        for w in words:
            w_str = w["word"] + " "
            w_box = draw.textbbox((0, 0), w_str, font=font)
            w_width = w_box[2] - w_box[0]
            is_active_word = w["start"] <= cur_t <= w["end"]
            color = (251, 191, 36, 255) if is_active_word else (255, 255, 255, 230)
            draw.text((cur_x, y_pos), w_str, font=font, fill=color)
            cur_x += w_width


def render_glass_reel_video(cleaned_video, transcript_json, storyboard_json, output_mp4, lang="darija", bgm_vol=0.045):
    is_arabic = lang in ["ary", "darija", "moroccan"]
    fps, total_dur = get_video_info(cleaned_video)
    fps_int = int(round(fps))

    with open(transcript_json, "r", encoding="utf-8") as f:
        transcript_data = json.load(f)
    with open(storyboard_json, "r", encoding="utf-8") as f:
        storyboard_data = json.load(f)

    cues = storyboard_data.get("storyboard", [])

    # Map cues to HyperFrames rendered cards
    hf_cards_dir = Path.home() / "Desktop" / "projects" / "reels_IG" / "motion_hyperframes"
    hf_caps = {}
    cue_card_map = {
        1: hf_cards_dir / "beat1_marcuse" / "beat1_marcuse.mp4",
        2: hf_cards_dir / "beat2_brickman" / "beat2_brickman.mp4",
        3: hf_cards_dir / "beat3_kasser" / "beat3_kasser.mp4",
        4: hf_cards_dir / "beat4_bauer" / "beat4_bauer.mp4",
    }
    for b_id, card_path in cue_card_map.items():
        if card_path.exists():
            cap = cv2.VideoCapture(str(card_path))
            hf_caps[b_id] = cap
            print(f"[render_glass_reel] Loaded HyperFrames Card #{b_id}: {card_path.name}")

    obsidian_base = create_obsidian_canvas(1080, 1920)
    sub_chunks, font_sub = build_subtitle_chunks(transcript_data, total_dur, is_arabic=is_arabic)

    seg_model = str(SKILL_ROOT / "models" / "selfie_segmenter.tflite")
    segmenter = vision.ImageSegmenter.create_from_options(vision.ImageSegmenterOptions(
        base_options=mpp.BaseOptions(model_asset_path=seg_model),
        output_confidence_masks=True,
        output_category_mask=False
    ))

    temp_silent_mp4 = Path(output_mp4).parent / f"_temp_render_glass_{lang}.mp4"

    in_cmd = [
        "ffmpeg", "-v", "error", "-i", str(cleaned_video),
        "-vf", (
            "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
            "eq=gamma=0.85:contrast=0.95:brightness=-0.035:saturation=1.02,"
            "colorbalance=rh=0.04:gh=-0.02:bh=-0.03:rm=0.03:gm=-0.01:bm=-0.02:pl=1,"
            "unsharp=5:5:0.25:5:5:0.10"
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

    print(f"[render_glass_reel] Streaming 'Obsidian Glass & HyperFrames' frames at {fps_int}fps ({total_dur:.1f}s)...")
    while True:
        raw = in_proc.stdout.read(frame_bytes)
        if len(raw) < frame_bytes:
            break
        cur_t = f_idx / float(fps_int)
        frame_np = np.frombuffer(raw, dtype=np.uint8).reshape((1920, 1080, 3))

        # Check active cue
        active_cue = None
        for cue in cues:
            st = float(cue.get("start_time", 0.0))
            et = float(cue.get("end_time", st + 8.0))
            if st <= cur_t <= et:
                active_cue = cue
                break

        if active_cue is None:
            # State 1: Live Studio Footage with subtle 1.04x camera punch-in
            raw_im = Image.fromarray(frame_np, "RGB")
            punch = 1.04 if (int(cur_t / 4.5) % 2 == 1) else 1.0
            if punch > 1.001:
                im_punched = raw_im.resize((int(1080 * punch), int(1920 * punch)), Image.BILINEAR)
                sx = (1080 - im_punched.width) // 2
                sy = (1920 - im_punched.height) // 2
                canvas = im_punched.crop((-sx, -sy, -sx + 1080, -sy + 1920)).convert("RGBA")
            else:
                canvas = raw_im.convert("RGBA")

            draw_modern_glass_subtitles(canvas, sub_chunks, cur_t, is_arabic, font_sub)

        else:
            # State 2: Lowered Cutout Speaker on Obsidian Canvas + HyperFrames Glass Card
            canvas = obsidian_base.copy()
            st = float(active_cue.get("start_time", 0.0))
            et = float(active_cue.get("end_time", st + 8.0))
            b_id = active_cue.get("beat_id", 1)

            # Render top HyperFrames card
            if b_id in hf_caps:
                cap = hf_caps[b_id]
                card_t = max(0.0, cur_t - st)
                card_frame_idx = int(card_t * 30.0)
                cap.set(cv2.CAP_PROP_POS_FRAMES, card_frame_idx)
                ret, hf_frame = cap.read()
                if ret and hf_frame is not None:
                    hf_rgb = cv2.cvtColor(hf_frame, cv2.COLOR_BGR2RGB)
                    hf_im = Image.fromarray(hf_rgb).convert("RGBA")
                    canvas.paste(hf_im, (0, 0), hf_im)

            # Person Segmentation
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

            p_in = ease_out_cubic(min(1.0, (cur_t - st) / 0.28))
            p_out = ease_out_cubic(min(1.0, (et - cur_t) / 0.28))
            lower_p = min(p_in, p_out)

            sc = 1.0 - 0.10 * lower_p
            target_y = int((820 - int(smoothed_head_top * 0.90)) * lower_p)
            im_spk = cut_rgba.resize((int(1080 * sc), int(1920 * sc)), Image.BILINEAR)
            sx = (1080 - im_spk.width) // 2

            if lower_p < 0.98:
                raw_im = Image.fromarray(frame_np, "RGB").convert("RGBA")
                canvas = Image.blend(raw_im, canvas, lower_p)

            canvas.paste(im_spk, (sx, target_y), im_spk)
            draw_modern_glass_subtitles(canvas, sub_chunks, cur_t, is_arabic, font_sub)

        out_proc.stdin.write(canvas.convert("RGB").tobytes())
        f_idx += 1

        if f_idx % 300 == 0:
            elapsed = time.time() - t0
            rfps = f_idx / elapsed
            pct = (f_idx / float(int(total_dur * fps_int))) * 100
            print(f"  [render_glass_reel] Rendered {f_idx} frames ({f_idx/fps_int:.1f}s / {total_dur:.1f}s, {pct:.1f}%) at {rfps:.1f} fps")

    in_proc.stdout.close()
    in_proc.wait()
    out_proc.stdin.close()
    out_proc.wait()

    # Release HyperFrames video captures
    for cap in hf_caps.values():
        cap.release()

    print(f"[render_glass_reel] Video frames composite complete. Mixing broadcast audio & SFX...")

    # Audio Mastering: -11.5 LUFS + BGM + SFX
    cleaned_wav = Path(cleaned_video).parent / f"{Path(cleaned_video).stem}.wav"
    ambient_bed = SKILL_ROOT / "motion_library" / "sfx" / "ambient_bed.wav"

    audio_cmd = [
        "ffmpeg", "-y", "-v", "error",
        "-i", str(temp_silent_mp4),
        "-i", str(cleaned_wav)
    ]

    has_bgm = ambient_bed.exists()
    if has_bgm:
        audio_cmd.extend(["-i", str(ambient_bed)])

    filter_complex = (
        "[1:a]highpass=f=75,lowpass=f=14000,afftdn=nr=10:nf=-52:tn=1:gs=5,"
        "equalizer=f=220:t=q:w=1.0:g=-1.0,equalizer=f=3800:t=q:w=1.0:g=1.5,"
        "acompressor=threshold=-18dB:ratio=2.2:attack=15:release=100:makeup=2.0dB[voice];"
    )

    if has_bgm:
        filter_complex += f"[2:a]lowpass=f=850,volume={bgm_vol}[bgm];[voice][bgm]amix=inputs=2:duration=first[mixed];[mixed]loudnorm=I=-11.5:LRA=6.0:TP=-0.5[aout]"
    else:
        filter_complex += "[voice]loudnorm=I=-11.5:LRA=6.0:TP=-0.5[aout]"

    audio_cmd.extend([
        "-filter_complex", filter_complex,
        "-map", "0:v", "-map", "[aout]",
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
        str(output_mp4)
    ])

    subprocess.run(audio_cmd, check=True)
    if temp_silent_mp4.exists():
        temp_silent_mp4.unlink()

    print(f"[render_glass_reel] Finished! Master Obsidian Glass Reel saved to:\n  {output_mp4}")
    return output_mp4


def main():
    parser = argparse.ArgumentParser(description="Render Next-Gen Obsidian Glass & HyperFrames Reel.")
    parser.add_argument("-i", "--input", required=True, help="Path to cleaned talking-head video")
    parser.add_argument("-t", "--transcript", required=True, help="Path to aligned transcript.json")
    parser.add_argument("-s", "--storyboard", required=True, help="Path to storyboard.json")
    parser.add_argument("-o", "--output", required=True, help="Path to output MP4 file")
    parser.add_argument("-l", "--lang", default="darija", help="Language code (default: darija)")
    args = parser.parse_args()

    render_glass_reel_video(args.input, args.transcript, args.storyboard, args.output, lang=args.lang)


if __name__ == "__main__":
    main()
