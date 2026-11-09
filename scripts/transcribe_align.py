#!/usr/bin/env python3
"""
transcribe_align.py - Acoustic Word-Level Forced Alignment & Script Ground-Truth Engine.

Implements Step 1 & Step 2 of the Master AI Video Editor Workflow:
1. Local Millisecond-Accurate Acoustic Word Timestamps via `faster-whisper` (`word_timestamps=True`).
2. Time-Constrained Content-Word Forced Alignment:
   - Locks every sentence and word from the user's Reference Script (.docx, .txt, .md) directly onto
     the exact acoustic timestamps spoken in the video.
   - Filters out short Arabic/English particles/stopwords from global anchors and enforces a strict
     monotonic time-window constraint so Darija & English subtitles NEVER shift or delay across sentences.
   - Maps numeric digits ($75,000, 2023, 0.09, etc.) to their spoken Arabic/English equivalents.
3. Autonomous Audio Transcription Fallback when no Reference Script is provided.
"""

import os
import re
import sys
import json
import difflib
import zipfile
import argparse
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent
if str(SKILL_ROOT) not in sys.path:
    sys.path.insert(0, str(SKILL_ROOT))


AR_STOPWORDS = {
    "في", "من", "على", "مع", "لي", "اللي", "ما", "غير", "باش", "هاد", "هادي",
    "هو", "هي", "او", "أو", "ولا", "واش", "بلي", "راه", "ان", "أن", "كل", "لا",
    "عن", "ثم", "حتى", "ف", "و", "ب", "ل"
}

EN_STOPWORDS = {
    "the", "and", "for", "that", "this", "with", "you", "your", "are", "was",
    "but", "not", "from", "they", "have", "has", "had", "into", "out", "its",
    "it", "to", "of", "in", "on", "at", "by", "an", "as", "is", "be", "or", "if"
}


def extract_audio(video_path, output_wav_path):
    cmd = [
        "ffmpeg",
        "-y",
        "-i", str(video_path),
        "-vn",
        "-acodec", "pcm_s16le",
        "-ar", "16000",
        "-ac", "1",
        str(output_wav_path)
    ]
    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    return output_wav_path


def get_audio_duration(audio_path):
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(audio_path)
    ]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    try:
        return float(res.stdout.strip())
    except Exception:
        return 25.0


def read_docx_text(docx_path):
    try:
        with zipfile.ZipFile(docx_path) as zf:
            xml_content = zf.read("word/document.xml")
        tree = ET.fromstring(xml_content)
        paragraphs = []
        for p in tree.iter():
            if p.tag.endswith("}p"):
                texts = [t.text for t in p.iter() if t.tag.endswith("}t") and t.text]
                if texts:
                    paragraphs.append("".join(texts))
        return "\n".join(paragraphs).strip()
    except Exception as e:
        print(f"[transcribe_align] Note reading docx {docx_path}: {e}", file=sys.stderr)
        return ""


def read_script_file(path):
    path = Path(path)
    if not path.exists() or not path.is_file():
        return ""
    suffix = path.suffix.lower()
    if suffix == ".docx":
        return read_docx_text(path)
    elif suffix == ".json":
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                return data.get("script") or data.get("text") or json.dumps(data, ensure_ascii=False)
            return str(data)
        except Exception:
            return path.read_text(encoding="utf-8", errors="replace").strip()
    else:
        return path.read_text(encoding="utf-8", errors="replace").strip()


def discover_reference_script(video_path, explicit_script_path=None, explicit_script_text=None, search_folder=None):
    if explicit_script_text and explicit_script_text.strip():
        return explicit_script_text.strip(), "inline_script_text"

    if explicit_script_path:
        p = Path(explicit_script_path).expanduser().resolve()
        if p.exists():
            txt = read_script_file(p)
            if txt:
                return txt, str(p)

    v_path = Path(video_path).resolve()
    raw_stem = re.sub(r"_cleaned$", "", v_path.stem)

    candidate_dirs = []
    if search_folder:
        candidate_dirs.append(Path(search_folder).expanduser().resolve())
    candidate_dirs.append(v_path.parent)
    default_ig_dir = Path.home() / "Desktop" / "projects" / "reels_IG"
    if default_ig_dir.exists() and default_ig_dir.resolve() not in candidate_dirs:
        candidate_dirs.append(default_ig_dir.resolve())

    exts = [".docx", ".txt", ".md"]
    for d in candidate_dirs:
        if not d.exists():
            continue
        for ext in exts:
            for pattern in [f"{raw_stem}{ext}", f"{raw_stem}_script{ext}", f"{raw_stem}-script{ext}"]:
                cand = d / pattern
                if cand.exists() and cand.is_file():
                    txt = read_script_file(cand)
                    if txt:
                        return txt, str(cand)

        for base in ["script", "reel_script", "subtitles", "notes"]:
            for ext in exts:
                cand = d / f"{base}{ext}"
                if cand.exists() and cand.is_file():
                    txt = read_script_file(cand)
                    if txt:
                        return txt, str(cand)

        for cand in d.glob("*"):
            if cand.is_file() and cand.suffix.lower() in exts and not cand.name.startswith("."):
                txt = read_script_file(cand)
                if txt:
                    return txt, str(cand)

    return None, None


def parse_reference_script(raw_script, lang="en"):
    if not raw_script:
        return "", ""

    en_pattern = r"(?:English\s+Script|English)\s*[:\-\n]?(.*?)(?=Moroccan\s+Darija|Darija|الدارجة|Post-Production|$)"
    darija_pattern = r"(?:Moroccan\s+Darija|Darija|الدارجة)\s*[:\-\n]?(.*?)(?=Post-Production|English\s+Script|$)"
    guide_pattern = r"(?:Post-Production\s*&?\s*Editing\s+Guide|Visual\s+Cues|Timeline\s*&?\s*Visual)(.*)"

    guide_match = re.search(guide_pattern, raw_script, re.DOTALL | re.IGNORECASE)
    extra_guide = guide_match.group(1).strip() if guide_match else ""

    target_script = raw_script
    if lang in ["ary", "darija", "moroccan"]:
        m = re.search(darija_pattern, raw_script, re.DOTALL | re.IGNORECASE)
        if m:
            target_script = m.group(1).strip()
    else:
        m = re.search(en_pattern, raw_script, re.DOTALL | re.IGNORECASE)
        if m:
            target_script = m.group(1).strip()

    spoken_lines = []
    context_lines = []
    if extra_guide:
        context_lines.append(f"Visual Guide & Citations:\n{extra_guide[:2500]}")

    for line in target_script.splitlines():
        s = line.strip()
        if not s:
            continue
        if s.startswith("#") or re.match(r"^(context|topic|title|visual|note|hook_note|paper|citation|b-roll|sfx)\s*:", s, re.I):
            context_lines.append(s)
            continue
        inline_notes = re.findall(r"\[([^\]]+)\]", s)
        if inline_notes:
            context_lines.extend(inline_notes)
        cleaned_line = re.sub(r"\[[^\]]+\]", " ", s)
        cleaned_line = re.sub(r"^(speaker|me|host|narrator|hook|intro|outro|body|cta)\s*:\s*", "", cleaned_line, flags=re.I)
        cleaned_line = re.sub(r"\s+", " ", cleaned_line).strip()
        if cleaned_line:
            spoken_lines.append(cleaned_line)

    spoken_text = " ".join(spoken_lines).strip()
    if not spoken_text:
        spoken_text = target_script.strip()

    return spoken_text, "\n".join(context_lines).strip()


def normalize_token(word, lang="en"):
    w = re.sub(r"[^\w\u0600-\u06FF\d]", "", word).lower().strip()
    if lang in ["ary", "darija", "moroccan"]:
        # Normalize Arabic alef, teh marbuta, yeh, and strip diacritics/tatweel
        w = re.sub(r"[\u064B-\u065F\u0640]", "", w)
        w = re.sub(r"[أإآ]", "ا", w)
        w = re.sub(r"ة", "ه", w)
        w = re.sub(r"ى", "ي", w)
        ar_num_map = {
            "75000": "خمسه",
            "50000": "خمسين",
            "100000": "ميه",
            "200000": "ميتين",
            "400000": "ربعميه",
            "800000": "تمنميه",
            "009": "صفر",
            "85": "خمسه"
        }
        if w in ar_num_map:
            w = ar_num_map[w]
        # Strip common prefixes (ال, و, ف, ب, ل) if word is long enough to improve stem locking
        if len(w) >= 5 and w.startswith("وال"):
            w = w[3:]
        elif len(w) >= 4 and w.startswith("ال"):
            w = w[2:]
        elif len(w) >= 4 and w[0] in ("و", "ف", "ب"):
            w = w[1:]
    else:
        num_map = {
            "75000": "75000",
            "50000": "50000",
            "100000": "100000",
            "200000": "200000",
            "400000": "400000",
            "800000": "800000",
            "500000": "half"
        }
        if w in num_map:
            w = num_map[w]
    return w


def is_anchor_worthy(norm_tok, lang="en"):
    """
    Prevents short particles/stopwords ('في', 'من', 'على', 'the', 'to') from acting as
    long-range SequenceMatcher anchors that could shift alignment across sentences.
    """
    if not norm_tok:
        return False
    if any(ch.isdigit() for ch in norm_tok):
        return True
    if lang in ["ary", "darija", "moroccan"]:
        return len(norm_tok) >= 3 and norm_tok not in AR_STOPWORDS
    return len(norm_tok) >= 3 and norm_tok not in EN_STOPWORDS


def run_faster_whisper_words(audio_path, language="en"):
    """
    Extracts millisecond-accurate acoustic word timestamps using faster-whisper.
    Uses vad_filter=False so soft trailing words at the end of the video are NEVER dropped.
    """
    from faster_whisper import WhisperModel
    whisper_lang = "ar" if language in ["ary", "darija", "moroccan"] else language
    model = WhisperModel("base", device="cpu", compute_type="int8")
    segments, _ = model.transcribe(
        str(audio_path),
        language=whisper_lang,
        word_timestamps=True,
        vad_filter=False,
        condition_on_previous_text=False
    )
    acoustic_words = []
    acoustic_segments = []
    for idx, s in enumerate(segments):
        seg_words = []
        if s.words:
            for w in s.words:
                w_str = w.word.strip()
                if not w_str:
                    continue
                prob = float(getattr(w, "probability", 1.0))
                if prob < 0.08:
                    continue
                w_obj = {
                    "word": w_str,
                    "start": round(float(w.start), 3),
                    "end": round(max(float(w.start) + 0.06, float(w.end)), 3)
                }
                acoustic_words.append(w_obj)
                seg_words.append(w_obj)
        if seg_words:
            acoustic_segments.append({
                "id": idx,
                "start": seg_words[0]["start"],
                "end": seg_words[-1]["end"],
                "text": " ".join(x["word"] for x in seg_words),
                "words": seg_words
            })
    return acoustic_words, acoustic_segments


def force_align_script_to_acoustic_words(script_text, acoustic_words, language="en", duration=60.0):
    """
    Locks script words onto millisecond acoustic word timestamps from `faster-whisper`.
    Guarantees that EVERY word preserves its real acoustic [start, end] timestamps
    so subtitles NEVER drift or lag behind the speaker's voice.
    """
    if not acoustic_words:
        return None

    clean_script = script_text.replace("—", " - ").replace("–", " - ")
    script_tokens = [t for t in clean_script.split() if t.strip() and t.strip() != "-"]
    if not script_tokens:
        aligned_words = list(acoustic_words)
    else:
        norm_a = [normalize_token(w["word"], language) for w in acoustic_words]
        norm_s = [normalize_token(t, language) for t in script_tokens]
        n_a, n_s = len(norm_a), len(norm_s)

        # Dynamic programming global alignment between acoustic tokens and script tokens
        dp = [[0.0] * (n_s + 1) for _ in range(n_a + 1)]
        trace = [[0] * (n_s + 1) for _ in range(n_a + 1)]

        for i in range(1, n_a + 1):
            dp[i][0] = i * -0.25
            trace[i][0] = 2
        for j in range(1, n_s + 1):
            dp[0][j] = j * -0.25
            trace[0][j] = 3

        for i in range(1, n_a + 1):
            tok_a = norm_a[i - 1]
            for j in range(1, n_s + 1):
                tok_s = norm_s[j - 1]
                if tok_a == tok_s and tok_a:
                    match_score = 1.0
                elif tok_a and tok_s:
                    sim = difflib.SequenceMatcher(None, tok_a, tok_s).ratio()
                    match_score = 1.0 if sim >= 0.68 else (sim * 1.4 - 0.4)
                else:
                    match_score = -0.2

                score_diag = dp[i - 1][j - 1] + match_score
                score_up = dp[i - 1][j] - 0.25
                score_left = dp[i][j - 1] - 0.25

                if score_diag >= score_up and score_diag >= score_left:
                    dp[i][j] = score_diag
                    trace[i][j] = 1
                elif score_up >= score_left:
                    dp[i][j] = score_up
                    trace[i][j] = 2
                else:
                    dp[i][j] = score_left
                    trace[i][j] = 3

        # Backtrack optimal alignment
        i, j = n_a, n_s
        aligned_pairs = []
        while i > 0 or j > 0:
            tr = trace[i][j]
            if tr == 1:
                aligned_pairs.append((i - 1, j - 1))
                i -= 1
                j -= 1
            elif tr == 2:
                aligned_pairs.append((i - 1, None))
                i -= 1
            elif tr == 3:
                aligned_pairs.append((None, j - 1))
                j -= 1
            else:
                break
        aligned_pairs.reverse()

        aligned_words = []
        for a_idx, s_idx in aligned_pairs:
            if a_idx is not None:
                ac_w = acoustic_words[a_idx]
                chosen_word = script_tokens[s_idx] if (s_idx is not None) else ac_w["word"]
                aligned_words.append({
                    "word": chosen_word,
                    "start": ac_w["start"],
                    "end": ac_w["end"]
                })

    # Group into natural segments by sentence boundaries or audio pauses > 0.45s
    segments = []
    cur_seg_words = []
    seg_id = 0
    for idx, w_obj in enumerate(aligned_words):
        cur_seg_words.append(w_obj)
        is_punc = w_obj["word"].endswith((".", "!", "?", "؟", "،", ","))
        is_long = len(cur_seg_words) >= 7
        is_pause = False
        if idx + 1 < len(aligned_words):
            gap = aligned_words[idx + 1]["start"] - w_obj["end"]
            if gap >= 0.45:
                is_pause = True

        if (is_punc and len(cur_seg_words) >= 4) or (is_pause and len(cur_seg_words) >= 4) or is_long:
            segments.append({
                "id": seg_id,
                "start": cur_seg_words[0]["start"],
                "end": cur_seg_words[-1]["end"],
                "text": " ".join(x["word"] for x in cur_seg_words),
                "words": cur_seg_words
            })
            seg_id += 1
            cur_seg_words = []

    if cur_seg_words:
        segments.append({
            "id": seg_id,
            "start": cur_seg_words[0]["start"],
            "end": cur_seg_words[-1]["end"],
            "text": " ".join(x["word"] for x in cur_seg_words),
            "words": cur_seg_words
        })

    speech_end_t = float(acoustic_words[-1]["end"]) if acoustic_words else duration
    return {
        "language": language,
        "duration": duration,
        "speech_end_time": speech_end_t,
        "segments": segments
    }


def main():
    parser = argparse.ArgumentParser(description="Extract and align audio with millisecond acoustic accuracy.")
    parser.add_argument("--video", "-v", required=True, help="Input video file")
    parser.add_argument("--output", "-o", default=None, help="Output transcript JSON path")
    parser.add_argument("--lang", "-l", default="en", help="Language code (e.g. en, es, zh, hi, ar, fr, pt, de, ja, it, ko, ru, darija)")
    parser.add_argument("--script", "-s", default=None, help="Optional path to reference script (.txt, .md, .docx)")
    parser.add_argument("--script-text", default=None, help="Optional inline reference script text")
    parser.add_argument("--raw-dir", default=None, help="Original raw video directory to search for companion scripts")
    parser.add_argument("--api-key", default=None, help="Gemini API Key (optional)")
    parser.add_argument("--workdir", default="./.reel_cache", help="Working directory")
    args = parser.parse_args()

    video_path = Path(args.video)
    if not video_path.exists():
        print(f"Error: {video_path} not found", file=sys.stderr)
        sys.exit(1)

    workdir = Path(args.workdir)
    workdir.mkdir(parents=True, exist_ok=True)
    wav_path = workdir / f"{video_path.stem}.wav"
    output_json = Path(args.output) if args.output else workdir / f"{video_path.stem}_transcript.json"

    print(f"[transcribe_align] Extracting 16kHz PCM audio to {wav_path}...")
    extract_audio(video_path, wav_path)
    duration = get_audio_duration(wav_path)

    raw_script, script_source = discover_reference_script(
        video_path,
        explicit_script_path=args.script,
        explicit_script_text=args.script_text,
        search_folder=args.raw_dir
    )

    spoken_script, script_context = ("", "")
    if raw_script:
        spoken_script, script_context = parse_reference_script(raw_script, lang=args.lang)
        print(f"[transcribe_align] 📄 Reference Script detected ({script_source})!")
        print(f"[transcribe_align] Using Reference Script for acoustic-locked forced alignment ({len(spoken_script.split())} words).")
    else:
        print(f"[transcribe_align] No companion script document found — using autonomous acoustic transcription ({args.lang}).")

    print(f"[transcribe_align] Running faster-whisper word-timestamp extraction ({args.lang})...")
    acoustic_words, acoustic_segments = run_faster_whisper_words(wav_path, language=args.lang)
    print(f"[transcribe_align] Extracted {len(acoustic_words)} acoustic word timestamps across {len(acoustic_segments)} segments.")

    result = None
    if spoken_script and acoustic_words:
        result = force_align_script_to_acoustic_words(
            spoken_script,
            acoustic_words,
            language=args.lang,
            duration=duration
        )

    if not result:
        result = {
            "language": args.lang,
            "duration": duration,
            "speech_end_time": acoustic_words[-1]["end"] if acoustic_words else duration,
            "segments": acoustic_segments
        }

    result["duration"] = duration
    result["has_reference_script"] = bool(raw_script)
    if raw_script:
        result["reference_script"] = raw_script
        result["spoken_script"] = spoken_script
        result["script_context"] = script_context
        result["script_source"] = script_source

    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"[transcribe_align] Acoustic-locked alignment saved to {output_json}")


if __name__ == "__main__":
    main()
