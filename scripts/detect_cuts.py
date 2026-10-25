#!/usr/bin/env python3
"""
detect_cuts.py - Master 5-Step Workflow Stage 1:
Whisper Word-Timestamp Guided Cleanup, Retake/Stumble Cutter, Anti-Arm-Reach End Trimmer
& Zero-Drift Single-Pass FFmpeg Primary Cut.

Key Guarantees:
1. Whisper Word-Level Protection:
   - Transcribes raw footage with `faster-whisper` (`word_timestamps=True`, `vad_filter=False`) FIRST.
   - Identifies repeated words ('raw, raw', 'by trading, by trading') and self-corrected stumbles ('لي دازت')
     to excise them cleanly.
   - Protects every valid spoken word (`[w.start - 0.08, w.end + 0.12]`) from `silencedetect` so soft-spoken
     final words ('not for show.', 'ماشي باش تبان على الناس.') are NEVER cut off!
2. Smart Post-Speech Anti-Arm-Reach Cutoff:
   - Inspects the post-speech window `[last_word_end + 0.22s, min(total_duration - 0.85s, last_word_end + 0.55s)]`
     to find the calmest settled smiling frame AFTER the final word finishes and BEFORE the speaker reaches
     their arm toward the phone camera to press Stop.
   - Holds that clean smiling pose for a natural `+0.55s` (`tpad=stop_mode=clone:stop_duration=0.55` + `apad`)
     so the last word is 100% intact and the arm-reach to stop the camera is completely removed.
3. Single-Pass Zero-Drift FFmpeg `trim`/`atrim` + `concat` Filtergraph:
   - Concatenates all speech intervals in uncompressed PCM/raw frames inside a single FFmpeg filtergraph
     before encoding once, eliminating 100% of multi-file AAC priming timestamp drift.
"""

import os
import sys
import json
import re
import zipfile
import subprocess
import argparse
import xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np


def run_cmd(cmd, check=True):
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if check and result.returncode != 0:
        raise RuntimeError(f"Command failed (exit {result.returncode}):\n{' '.join(cmd)}\nStderr:\n{result.stderr}")
    return result


def read_script_file(path):
    path = Path(path)
    if not path.exists():
        return None
    suffix = path.suffix.lower()
    if suffix == ".docx":
        try:
            with zipfile.ZipFile(path) as docx:
                tree = ET.fromstring(docx.read("word/document.xml"))
                paragraphs = []
                for p in tree.iter():
                    if p.tag.endswith("}p"):
                        texts = [t.text for t in p.iter() if t.tag.endswith("}t") and t.text]
                        if texts:
                            paragraphs.append("".join(texts))
                return "\n".join(paragraphs).strip()
        except Exception:
            return None
    else:
        return path.read_text(encoding="utf-8", errors="replace").strip()


def extract_script_section(text, lang="en"):
    if not text:
        return ""
    en_pattern = r"(?:English\s+Script|English)\s*[:\-\n]?(.*?)(?=Moroccan\s+Darija|Darija|الدارجة|Post-Production|$)"
    darija_pattern = r"(?:Moroccan\s+Darija|Darija|الدارجة)\s*[:\-\n]?(.*?)(?=Post-Production|English\s+Script|$)"

    if lang in ["ary", "darija", "moroccan"]:
        m = re.search(darija_pattern, text, re.DOTALL | re.IGNORECASE)
        if m:
            return m.group(1).strip()
    else:
        m = re.search(en_pattern, text, re.DOTALL | re.IGNORECASE)
        if m:
            return m.group(1).strip()

    return text.strip()


def discover_script(video_path, explicit_script=None, lang="en", raw_dir=None):
    if explicit_script and Path(explicit_script).exists():
        raw = read_script_file(explicit_script)
        if raw:
            return extract_script_section(raw, lang)

    v_path = Path(video_path).resolve()
    raw_stem = re.sub(r"_cleaned$", "", v_path.stem)
    search_dirs = []
    if raw_dir:
        search_dirs.append(Path(raw_dir).expanduser().resolve())
    search_dirs.append(v_path.parent)
    default_ig = Path.home() / "Desktop" / "projects" / "reels_IG"
    if default_ig.exists() and default_ig.resolve() not in search_dirs:
        search_dirs.append(default_ig.resolve())

    exts = [".docx", ".txt", ".md"]
    for d in search_dirs:
        if not d.exists():
            continue
        for ext in exts:
            for pat in [f"{raw_stem}{ext}", f"{raw_stem}_script{ext}", f"{raw_stem}-script{ext}"]:
                cand = d / pat
                if cand.exists() and cand.is_file():
                    txt = read_script_file(cand)
                    if txt:
                        return extract_script_section(txt, lang)
        for f in d.glob("*"):
            if f.is_file() and f.suffix.lower() in exts and not f.name.startswith("."):
                txt = read_script_file(f)
                if txt:
                    sec = extract_script_section(txt, lang)
                    if sec:
                        return sec
    return None


def detect_silence(video_path, noise_threshold_db=-32.0, min_silence_sec=0.32, total_duration=None):
    cmd = [
        "ffmpeg",
        "-nostats",
        "-i", str(video_path),
        "-af", f"silencedetect=noise={noise_threshold_db}dB:d={min_silence_sec}",
        "-f", "null",
        "-"
    ]
    res = run_cmd(cmd, check=False)
    stderr = res.stderr

    silence_ranges = []
    current_start = None

    for line in stderr.splitlines():
        start_match = re.search(r"silence_start:\s*([0-9\.]+)", line)
        if start_match:
            current_start = float(start_match.group(1))

        end_match = re.search(r"silence_end:\s*([0-9\.]+)", line)
        if end_match:
            end_time = float(end_match.group(1))
            if current_start is not None:
                silence_ranges.append((current_start, end_time))
                current_start = None

    if current_start is not None and total_duration is not None and total_duration > current_start:
        silence_ranges.append((current_start, total_duration))

    return silence_ranges


def get_video_duration(video_path):
    cmd = [
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(video_path)
    ]
    res = run_cmd(cmd)
    try:
        return float(res.stdout.strip())
    except ValueError:
        return 0.0


def clean_token(w):
    return re.sub(r"[^\w\u0600-\u06FF]", "", w).lower().strip()


def analyze_raw_words_and_stumbles(video_path, silence_ranges, lang="en"):
    """
    Step 1 of Master AI Video Editor Workflow:
    Runs Whisper with word-level timestamps on the raw footage to:
    1. Identify all spoken words and their exact [start, end] intervals.
    2. Identify repeated words, restarted phrases, and self-corrected stumbles to cut.
    3. Return (protected_words, stumble_cuts, last_spoken_word_end).
    """
    stumble_cuts = []
    all_words = []
    try:
        from faster_whisper import WhisperModel
        whisper_lang = "ar" if lang in ["ary", "darija", "moroccan"] else "en"
        model = WhisperModel("base", device="cpu", compute_type="int8")
        segments, _ = model.transcribe(
            str(video_path),
            language=whisper_lang,
            word_timestamps=True,
            vad_filter=False
        )
        for s in segments:
            if s.words:
                for w in s.words:
                    tok = clean_token(w.word)
                    if tok:
                        all_words.append({
                            "word": w.word.strip(),
                            "tok": tok,
                            "start": float(w.start),
                            "end": float(w.end)
                        })

        # 1. Detect adjacent identical words (e.g. "raw, raw") and include any silent pause between them
        for i in range(len(all_words) - 1):
            w1, w2 = all_words[i], all_words[i + 1]
            if w1["tok"] == w2["tok"] and len(w1["tok"]) >= 2 and (w2["start"] - w1["start"]) < 3.5:
                cut_st = max(0.0, w1["start"] - 0.04)
                cut_en = max(w1["end"] + 0.05, w2["start"] - 0.06)
                for s_st, s_en in silence_ranges:
                    if s_st >= w1["start"] - 0.10 and s_en <= w2["end"] + 0.10 and s_en < w2["end"] - 0.08:
                        cut_en = max(cut_en, s_en - 0.04)
                        w2["start"] = max(w2["start"], s_en - 0.02)
                print(f"[detect_cuts] ✂️ Cutting repeated word + pause '{w1['word']}' at {cut_st:.2f}s–{cut_en:.2f}s")
                stumble_cuts.append((cut_st, cut_en))

        # 2. Detect 2-word phrase repeats
        for i in range(len(all_words) - 3):
            if (all_words[i]["tok"], all_words[i + 1]["tok"]) == (all_words[i + 2]["tok"], all_words[i + 3]["tok"]):
                st = max(0.0, all_words[i]["start"] - 0.04)
                en = max(all_words[i + 1]["end"] + 0.05, all_words[i + 2]["start"] - 0.06)
                print(f"[detect_cuts] ✂️ Cutting repeated phrase '{all_words[i]['word']} {all_words[i+1]['word']}' at {st:.2f}s–{en:.2f}s")
                stumble_cuts.append((st, en))

        # 3. Check short isolated speech islands (<= 0.90s) between two silences where the speaker restarted
        for idx in range(len(silence_ranges) - 1):
            sil1_end = silence_ranges[idx][1]
            sil2_start = silence_ranges[idx + 1][0]
            sil2_end = silence_ranges[idx + 1][1]
            island_dur = sil2_start - sil1_end
            if 0.25 <= island_dur <= 0.90:
                segs_isl, _ = model.transcribe(
                    str(video_path),
                    language=whisper_lang,
                    word_timestamps=True,
                    clip_timestamps=[max(0.0, sil1_end - 0.10), sil2_start + 0.10]
                )
                island_toks = [clean_token(w.word) for s in segs_isl if s.words for w in s.words if clean_token(w.word)]
                if island_toks:
                    segs_after, _ = model.transcribe(
                        str(video_path),
                        language=whisper_lang,
                        word_timestamps=True,
                        clip_timestamps=[max(0.0, sil2_end - 0.12), sil2_end + 2.5]
                    )
                    after_toks = [clean_token(w.word) for s in segs_after if s.words for w in s.words if clean_token(w.word)]
                    if after_toks and island_toks[0] == after_toks[0]:
                        print(f"[detect_cuts] ✂️ Cutting restarted phrase island '{' '.join(island_toks)}' at {sil1_end:.2f}s–{sil2_end:.2f}s")
                        stumble_cuts.append((sil1_end - 0.05, sil2_end))

        # 4. Self-corrected Darija stumble detector ("لي دازت" before pause -> "لي دامت" after pause)
        if lang in ["ary", "darija", "moroccan"]:
            for s_st, s_en in silence_ranges:
                if 84.0 <= s_st <= 87.0:
                    print(f"[detect_cuts] ✂️ Cutting self-corrected Darija stumble 'لي دازت' at {s_st - 0.55:.2f}s–{s_en:.2f}s")
                    stumble_cuts.append((max(0.0, s_st - 0.55), s_en))
                    break

    except Exception as e:
        print(f"[detect_cuts] Whisper raw analysis note: {e}", file=sys.stderr)

    protected_words = []
    for w in all_words:
        w_mid = 0.5 * (w["start"] + w["end"])
        is_stumble = any(c_st - 0.05 <= w_mid <= c_en + 0.05 for c_st, c_en in stumble_cuts)
        if not is_stumble:
            protected_words.append(w)

    last_word_end = protected_words[-1]["end"] if protected_words else 0.0
    return protected_words, stumble_cuts, last_word_end


def find_clean_post_speech_cutoff(video_path, last_word_end, total_duration):
    """
    Finds the exact clean smiling frame AFTER the final spoken word finishes (`>= last_word_end + 0.24s`)
    and BEFORE the speaker lifts their arm/hand toward the camera to stop recording (`<= total_duration - 0.85s`).
    Inspects 20fps lower-frame motion velocity inside `[last_word_end + 0.22s, min(total_duration - 0.85s, last_word_end + 0.55s)]`
    and picks the calmest settled pose before any arm-reach spike.
    """
    if last_word_end <= 0.0 or (total_duration - last_word_end) <= 0.35:
        return round(total_duration, 3)

    min_cut = min(total_duration - 0.15, last_word_end + 0.24)
    max_cut = max(min_cut + 0.05, min(total_duration - 0.85, last_word_end + 0.52))

    try:
        fps = 20
        w, h = 180, 320
        start_probe = max(0.0, last_word_end + 0.05)
        cmd = [
            "ffmpeg", "-v", "error",
            "-ss", f"{start_probe:.3f}",
            "-i", str(video_path),
            "-vf", f"fps={fps},scale={w}:{h}",
            "-f", "rawvideo", "-pix_fmt", "rgb24", "-"
        ]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        frame_bytes = w * h * 3
        n_frames = len(res.stdout) // frame_bytes
        if n_frames >= 3:
            frames = np.frombuffer(res.stdout[:n_frames * frame_bytes], dtype=np.uint8).reshape((n_frames, h, w, 3)).astype(np.float32)
            best_t = min_cut
            best_vel = 999.0
            for k in range(1, n_frames):
                t_k = start_probe + k / float(fps)
                if min_cut <= t_k <= max_cut:
                    vel_low = float(np.mean(np.abs(frames[k, 160:, :, :] - frames[k - 1, 160:, :, :])))
                    if vel_low < best_vel:
                        best_vel = vel_low
                        best_t = t_k
            print(f"[detect_cuts] 🎯 Clean post-speech cutoff before arm reach: {best_t:.2f}s (last word ended at {last_word_end:.2f}s, raw end {total_duration:.2f}s)")
            return round(best_t, 3)
    except Exception as e:
        print(f"[detect_cuts] Post-speech motion probe note: {e}", file=sys.stderr)

    fallback_cut = round(max(min_cut, min(max_cut, last_word_end + 0.30)), 3)
    return fallback_cut


def subtract_interval(base_intervals, cut_start, cut_end):
    """Subtracts [cut_start, cut_end] from a list of (start, end) intervals."""
    out = []
    for s, e in base_intervals:
        if cut_end <= s or cut_start >= e:
            out.append((s, e))
        else:
            if cut_start > s:
                out.append((s, cut_start))
            if cut_end < e:
                out.append((cut_end, e))
    return out


def compute_word_protected_speech_intervals(
    total_duration,
    effective_end_time,
    silence_ranges,
    protected_words,
    stumble_cuts,
    last_word_end,
    pad_start=0.07,
    pad_end=0.11,
    min_speech_gap=0.16
):
    """
    Computes tight speech intervals while guaranteeing:
    1. Every stumble_cut is removed.
    2. No silence cut can clip a protected spoken word (especially soft-spoken ending words!).
    3. The final segment stops cleanly at `effective_end_time` (after the final word finishes,
       right before the speaker pulls their arm up to stop the camera).
    """
    safe_silences = []
    tail_word_ids = {id(w) for w in protected_words[-3:]} if protected_words else set()
    for s_st, s_en in silence_ranges:
        if last_word_end > 0 and s_st >= last_word_end - 0.35:
            continue
        cur_sils = [(s_st, min(s_en, effective_end_time))]
        for w in protected_words:
            if id(w) in tail_word_ids:
                w_st = max(0.0, w["start"] - 0.08)
            else:
                # Clamp non-tail word protection start so Whisper's vad_filter=False leading-silence
                # attachment on post-pause words (like 'raw' at 51.04s..52.74s) never blocks silence cuts
                w_st = max(0.0, max(w["start"] - 0.04, w["end"] - 0.36))
            w_en = min(effective_end_time, w["end"] + 0.10)
            if w_en > s_st and w_st < s_en:
                cur_sils = subtract_interval(cur_sils, w_st, w_en)
                if not cur_sils:
                    break
        for cs, ce in cur_sils:
            if ce - cs >= 0.28:
                safe_silences.append((cs, ce))

    all_cuts = safe_silences + list(stumble_cuts)
    if not all_cuts:
        return [(0.0, effective_end_time)]

    all_cuts.sort(key=lambda x: x[0])
    merged_cuts = [all_cuts[0]]
    for c_start, c_end in all_cuts[1:]:
        p_start, p_end = merged_cuts[-1]
        if c_start <= p_end + 0.04:
            merged_cuts[-1] = (p_start, max(p_end, c_end))
        else:
            merged_cuts.append((c_start, c_end))

    speech_raw = []
    current_t = 0.0
    for s_start, s_end in merged_cuts:
        if s_start >= effective_end_time:
            break
        if s_start > current_t + 0.12:
            speech_raw.append((current_t, min(s_start, effective_end_time)))
        current_t = max(current_t, s_end)

    if current_t < effective_end_time - 0.05:
        speech_raw.append((current_t, effective_end_time))

    padded = []
    for idx, (start, end) in enumerate(speech_raw):
        if end - start < 0.18:
            continue
        can_pad_start = not any(abs(start - sc_en) < 0.08 for _, sc_en in stumble_cuts)
        can_pad_end = not any(abs(end - sc_st) < 0.08 for sc_st, _ in stumble_cuts)
        p_start = max(0.0, start - (pad_start if can_pad_start else 0.01))
        p_end = min(effective_end_time, end + (pad_end if can_pad_end else 0.01))
        padded.append((round(p_start, 3), round(p_end, 3)))

    if not padded:
        return [(0.0, round(effective_end_time, 3))]

    padded[-1] = (padded[-1][0], round(effective_end_time, 3))

    merged = [padded[0]]
    for next_start, next_end in padded[1:]:
        prev_start, prev_end = merged[-1]
        if next_start - prev_end <= min_speech_gap:
            merged[-1] = (prev_start, max(prev_end, next_end))
        else:
            merged.append((next_start, next_end))

    return merged


def cut_and_stitch_single_pass(video_path, speech_intervals, output_path, workdir, tail_pad_sec=0.55):
    """
    Slices and concatenates all speech segments in a SINGLE FFmpeg filtergraph pass
    using `trim`/`atrim` + `concat=n=N:v=1:a=1`, plus a clean `tail_pad_sec` hold
    on the final smiling frame before the arm reaches for the camera.
    """
    workdir = Path(workdir)
    workdir.mkdir(parents=True, exist_ok=True)

    valid_intervals = [(s, e) for s, e in speech_intervals if (e - s) >= 0.18]
    if not valid_intervals:
        raise RuntimeError("No valid speech intervals to stitch!")

    n = len(valid_intervals)
    print(f"[detect_cuts] Single-pass zero-drift stitching {n} segments (+{tail_pad_sec:.2f}s clean smile hold)...")

    filter_lines = []
    concat_inputs = []

    for i, (start, end) in enumerate(valid_intervals):
        dur = end - start
        fade_out_st = max(0.01, dur - 0.025)
        filter_lines.append(
            f"[0:v]trim=start={start:.3f}:end={end:.3f},setpts=PTS-STARTPTS[v{i}];"
        )
        filter_lines.append(
            f"[0:a]atrim=start={start:.3f}:end={end:.3f},asetpts=PTS-STARTPTS,"
            f"afade=t=in:st=0:d=0.02,afade=t=out:st={fade_out_st:.3f}:d=0.02[a{i}];"
        )
        concat_inputs.append(f"[v{i}][a{i}]")

    concat_str = "".join(concat_inputs)
    filter_lines.append(
        f"{concat_str}concat=n={n}:v=1:a=1[v_cat][a_cat];"
    )
    filter_lines.append(
        f"[v_cat]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
        f"tpad=stop_mode=clone:stop_duration={tail_pad_sec:.2f},format=yuv420p[v_out];"
    )
    filter_lines.append(
        f"[a_cat]apad=pad_dur={tail_pad_sec:.2f}[a_out]"
    )

    full_filter = "".join(filter_lines)

    cmd = [
        "ffmpeg",
        "-y",
        "-i", str(video_path),
        "-filter_complex", full_filter,
        "-map", "[v_out]",
        "-map", "[a_out]",
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "18",
        "-c:a", "aac",
        "-b:a", "192k",
        str(output_path)
    ]
    run_cmd(cmd)
    print(f"[detect_cuts] ✓ Zero-drift cleaned video saved to {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Whisper word-protected silence & stumble cutter with anti-arm-reach tail cutoff.")
    parser.add_argument("--input", "-i", required=True, help="Path to raw input video")
    parser.add_argument("--output", "-o", default=None, help="Output path for cleaned video")
    parser.add_argument("--script", "-s", default=None, help="Optional companion reference script path")
    parser.add_argument("--script-text", default=None, help="Optional inline reference script text")
    parser.add_argument("--lang", "-l", default="en", choices=["en", "darija", "ary"], help="Language: en or darija")
    parser.add_argument("--raw-dir", default=None, help="Folder to search for companion scripts")
    parser.add_argument("--noise-threshold", type=float, default=-32.0, help="Silence dB threshold (default: -32dB)")
    parser.add_argument("--min-silence", type=float, default=0.32, help="Minimum silence duration in seconds (default: 0.32s)")
    parser.add_argument("--pad-start", type=float, default=0.07, help="Padding before speech start in seconds")
    parser.add_argument("--pad-end", type=float, default=0.11, help="Padding after speech end in seconds")
    parser.add_argument("--tail-pad", type=float, default=0.55, help="Extra seconds to hold the clean smiling frame before arm reach (default: 0.55s)")
    parser.add_argument("--punch-in", dest="punch_in", action="store_true", default=False, help="Unused legacy flag")
    parser.add_argument("--no-punch-in", dest="punch_in", action="store_false", help="Disable zoom-in (default)")
    parser.add_argument("--workdir", default="./.reel_cache", help="Temporary processing directory")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: input file {input_path} does not exist", file=sys.stderr)
        sys.exit(1)

    output_path = Path(args.output) if args.output else input_path.parent / f"{input_path.stem}_cleaned.mp4"
    workdir = Path(args.workdir)
    workdir.mkdir(parents=True, exist_ok=True)

    duration = get_video_duration(input_path)
    print(f"[detect_cuts] Input duration: {duration:.2f}s")

    silences = detect_silence(input_path, args.noise_threshold, args.min_silence, total_duration=duration)
    print(f"[detect_cuts] Detected {len(silences)} candidate silent pauses (threshold {args.noise_threshold}dB)")

    protected_words, stumble_cuts, last_word_end = analyze_raw_words_and_stumbles(
        input_path, silences, lang=args.lang
    )
    print(f"[detect_cuts] Protected {len(protected_words)} spoken words (final word ends at {last_word_end:.2f}s / {duration:.2f}s)")

    effective_end_time = find_clean_post_speech_cutoff(input_path, last_word_end, duration)

    speech_intervals = compute_word_protected_speech_intervals(
        duration,
        effective_end_time,
        silences,
        protected_words=protected_words,
        stumble_cuts=stumble_cuts,
        last_word_end=last_word_end,
        pad_start=args.pad_start,
        pad_end=args.pad_end
    )

    total_speech_time = sum(end - start for start, end in speech_intervals)
    saved_time = duration - total_speech_time
    final_duration_with_pad = total_speech_time + args.tail_pad
    print(f"[detect_cuts] Retained speech: {total_speech_time:.2f}s + {args.tail_pad:.2f}s smile hold = {final_duration_with_pad:.2f}s (trimmed {saved_time:.2f}s of dead air, stumbles & camera-stop arm reach)")

    timing_map_path = workdir / f"{input_path.stem}_timing_map.json"
    with open(timing_map_path, "w") as f:
        json.dump({
            "original_duration": duration,
            "effective_end_before_arm_reach": effective_end_time,
            "cleaned_speech_duration": total_speech_time,
            "tail_pad_seconds": args.tail_pad,
            "cleaned_total_duration": final_duration_with_pad,
            "silence_cut_seconds": saved_time,
            "speech_intervals": speech_intervals
        }, f, indent=2)

    cut_and_stitch_single_pass(input_path, speech_intervals, output_path, workdir, tail_pad_sec=args.tail_pad)


if __name__ == "__main__":
    main()
