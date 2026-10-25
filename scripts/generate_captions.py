#!/usr/bin/env python3
"""
generate_captions.py - Viral Kinetic Subtitle Generator for Instagram Reels.

Supports:
- English: Bold uppercase typography with active-word color highlights.
- Moroccan Darija: Arabic script (الحروف العربية) with right-to-left layout and high-contrast styling.
- Instagram Safe Zones: Y placement at ~42% from bottom to avoid UI obstruction.
"""

import os
import sys
import json
import argparse
from pathlib import Path


ASS_HEADER_TEMPLATE = """[Script Info]
Title: Quant and the Physicist & Darija Reels Captions
ScriptType: v4.00+
WrapStyle: 0
ScaledBorderAndShadow: yes
YCbCr Matrix: None
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: EnglishBold,Montserrat Black,72,&H00FFFFFF,&H0000E6FF,&H00000000,&H80000000,-1,0,0,0,100,100,2,0,1,6,3,2,60,60,520,1
Style: DarijaArabic,Geeza Pro,78,&H0000FFA3,&H0000FFFF,&H00000000,&H80000000,-1,0,0,0,100,100,1,0,1,7,3,2,60,60,520,178

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""


def format_ass_time(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    cs = int(round((seconds - int(seconds)) * 100))
    if cs == 100:
        s += 1
        cs = 0
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"


def create_kinetic_ass(transcript_data, output_ass_path, lang="en", words_per_screen=3):
    segments = transcript_data.get("segments", [])
    events = []
    is_arabic = lang in ["ary", "darija", "moroccan"] or transcript_data.get("language") in ["ary", "darija", "moroccan"]
    style_name = "DarijaArabic" if is_arabic else "EnglishBold"

    for seg in segments:
        words = seg.get("words", [])
        if not words:
            start_t = format_ass_time(seg.get("start", 0.0))
            end_t = format_ass_time(seg.get("end", 3.0))
            text = seg.get("text", "")
            if not is_arabic:
                text = text.upper()
            events.append(f"Dialogue: 0,{start_t},{end_t},{style_name},,0,0,0,,{text}")
            continue

        for i in range(0, len(words), words_per_screen):
            chunk = words[i : i + words_per_screen]
            chunk_start = chunk[0]["start"]
            chunk_end = chunk[-1]["end"]

            for active_idx, target_word in enumerate(chunk):
                w_start = format_ass_time(target_word["start"])
                w_end = format_ass_time(target_word["end"])

                formatted_words = []
                for w_i, w in enumerate(chunk):
                    word_str = w["word"]
                    if not is_arabic:
                        word_str = word_str.upper()

                    if w_i == active_idx:
                        # Highlight active word
                        color_code = "\\c&H0000E6FF&" if not is_arabic else "\\c&H0000FFA3&"
                        formatted_words.append(f"{{{color_code}\\fscx106\\fscy106}}{word_str}{{\\r}}")
                    else:
                        formatted_words.append(f"{{\\c&H00FFFFFF&}}{word_str}")

                line_text = " ".join(formatted_words)
                events.append(f"Dialogue: 0,{w_start},{w_end},{style_name},,0,0,0,,{line_text}")

    with open(output_ass_path, "w", encoding="utf-8") as f:
        f.write(ASS_HEADER_TEMPLATE)
        for ev in events:
            f.write(ev + "\n")

    print(f"[generate_captions] Saved captions ({style_name}) to {output_ass_path}")
    return output_ass_path


def format_srt_time(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int(round((seconds - int(seconds)) * 1000))
    if ms >= 1000:
        s += 1
        ms = 0
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def create_srt(transcript_data, output_srt_path, lang="en"):
    segments = transcript_data.get("segments", [])
    is_arabic = lang in ["ary", "darija", "moroccan"] or transcript_data.get("language") in ["ary", "darija", "moroccan"]
    lines = []
    idx = 1
    for seg in segments:
        words = seg.get("words", [])
        if not words:
            start_str = format_srt_time(seg.get("start", 0.0))
            end_str = format_srt_time(seg.get("end", 3.0))
            text = seg.get("text", "")
            if not is_arabic:
                text = text.upper()
            lines.append(f"{idx}\n{start_str} --> {end_str}\n{text}\n")
            idx += 1
            continue

        for i in range(0, len(words), 4):
            chunk = words[i : i + 4]
            start_str = format_srt_time(chunk[0]["start"])
            end_str = format_srt_time(chunk[-1]["end"])
            chunk_text = " ".join(w["word"] for w in chunk)
            if not is_arabic:
                chunk_text = chunk_text.upper()
            lines.append(f"{idx}\n{start_str} --> {end_str}\n{chunk_text}\n")
            idx += 1

    with open(output_srt_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"[generate_captions] Saved SRT captions to {output_srt_path}")
    return output_srt_path


def main():
    parser = argparse.ArgumentParser(description="Generate kinetic subtitles for Quant & The Physicist / Darija.")
    parser.add_argument("--transcript", "-t", required=True, help="Transcript JSON file")
    parser.add_argument("--output", "-o", default=None, help="Output ASS subtitle path")
    parser.add_argument("--lang", "-l", default="en", help="Language: en or darija")
    args = parser.parse_args()

    t_path = Path(args.transcript)
    if not t_path.exists():
        print(f"Error: {t_path} not found", file=sys.stderr)
        sys.exit(1)

    out_path = Path(args.output) if args.output else t_path.parent / f"{t_path.stem}.ass"
    srt_path = out_path.with_suffix(".srt")

    with open(t_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    create_kinetic_ass(data, out_path, args.lang)
    create_srt(data, srt_path, args.lang)



if __name__ == "__main__":
    main()
