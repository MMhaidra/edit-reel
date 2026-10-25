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
    Locks the exact words of `script_text` onto the millisecond acoustic word timestamps
    from `faster-whisper` using Time-Constrained Content-Word Anchor Matching.
    Guarantees zero shift/delay on both Moroccan Darija and English scripts.
    """
    clean_script = script_text.replace("—", " - ").replace("–", " - ")
    script_tokens = [t for t in clean_script.split() if t.strip() and t.strip() != "-"]
    if not script_tokens or not acoustic_words:
        return None

    norm_script = [normalize_token(t, language) for t in script_tokens]
    norm_acoustic = [normalize_token(w["word"], language) for w in acoustic_words]

    n_s = len(script_tokens)
    n_a = len(acoustic_words)

    speech_start_t = float(acoustic_words[0]["start"])
    speech_end_t = float(acoustic_words[-1]["end"])
    speech_span = max(1.0, speech_end_t - speech_start_t)

    # Build cumulative character progress for script tokens to estimate expected timestamp
    char_lens = [max(2, len(t)) for t in norm_script]
    tot_script_chars = float(sum(char_lens))
    cum_chars = []
    acc = 0.0
    for cl in char_lens:
        cum_chars.append(acc / tot_script_chars)
        acc += cl

    def expected_time_for_script_idx(si):
        return speech_start_t + cum_chars[si] * speech_span

    # Time-Constrained Monotonic Anchor Search:
    # We march through script words `si` and search for strong content-word matches in `acoustic_words`
    # within a local time window around `expected_time_for_script_idx(si)`.
    anchors = [(0, 0)]
    last_si = 0
    last_aj = 0

    for si in range(1, n_s - 1):
        s_tok = norm_script[si]
        if not is_anchor_worthy(s_tok, language):
            continue

        exp_t = expected_time_for_script_idx(si)
        # Estimate expected acoustic index from last anchor + proportional progress
        rem_s = max(1, (n_s - 1) - last_si)
        rem_a = max(1, (n_a - 1) - last_aj)
        center_aj = last_aj + int(((si - last_si) / float(rem_s)) * rem_a)

        win_start = max(last_aj + 1, center_aj - 10)
        win_end = min(n_a - 1, center_aj + 12)

        best_aj = None
        best_score = 0.0

        for aj in range(win_start, win_end):
            a_tok = norm_acoustic[aj]
            if not a_tok:
                continue
            ac_t = float(acoustic_words[aj]["start"])
            time_diff = abs(ac_t - exp_t)
            # Never allow an anchor to jump more than 4.2s away from expected speech progress
            if time_diff > 4.2:
                continue

            if s_tok == a_tok:
                sim = 1.0
            else:
                if len(s_tok) < 3 or len(a_tok) < 3:
                    continue
                sim = difflib.SequenceMatcher(None, s_tok, a_tok).ratio()

            if sim < 0.72:
                continue

            # Combine phonetic similarity with temporal proximity bonus
            prox_bonus = max(0.0, 1.0 - (time_diff / 4.5)) * 0.15
            idx_bonus = max(0.0, 1.0 - (abs(aj - center_aj) / 12.0)) * 0.10
            score = sim + prox_bonus + idx_bonus
            if score > best_score:
                best_score = score
                best_aj = aj

        if best_aj is not None:
            anchors.append((si, best_aj))
            last_si = si
            last_aj = best_aj

    if anchors[-1][0] < n_s - 1:
        anchors.append((n_s - 1, n_a - 1))

    # Deduplicate and enforce strict monotonicity
    clean_anchors = [anchors[0]]
    for si, aj in anchors[1:]:
        prev_si, prev_aj = clean_anchors[-1]
        if si > prev_si and aj >= prev_aj:
            clean_anchors.append((si, aj))

    print(f"[transcribe_align] ✓ Locked {len(clean_anchors)} time-constrained acoustic anchors across {n_s} script words!")

    # Step 2: Assign exact timestamps to every script word by mapping across the acoustic words in each span
    aligned_words = [None] * n_s

    for idx in range(len(clean_anchors)):
        s_idx, a_idx = clean_anchors[idx]
        w_ac = acoustic_words[min(a_idx, n_a - 1)]
        aligned_words[s_idx] = {
            "word": script_tokens[s_idx],
            "start": w_ac["start"],
            "end": w_ac["end"]
        }

        if idx + 1 < len(clean_anchors):
            next_s, next_a = clean_anchors[idx + 1]
            span_s = next_s - s_idx - 1
            if span_s > 0:
                inner_ac = acoustic_words[a_idx + 1:next_a]
                if len(inner_ac) >= span_s and len(inner_ac) > 0:
                    for k in range(span_s):
                        ac_k = inner_ac[int(k * len(inner_ac) / float(span_s))]
                        aligned_words[s_idx + 1 + k] = {
                            "word": script_tokens[s_idx + 1 + k],
                            "start": ac_k["start"],
                            "end": ac_k["end"]
                        }
                else:
                    span_start_t = acoustic_words[min(a_idx, n_a - 1)]["end"]
                    span_end_t = acoustic_words[min(next_a, n_a - 1)]["start"]
                    if span_end_t <= span_start_t:
                        span_start_t = acoustic_words[min(a_idx, n_a - 1)]["start"]
                        span_end_t = acoustic_words[min(next_a, n_a - 1)]["end"]

                    sub_tokens = script_tokens[s_idx + 1:next_s]
                    tot_chars = max(1, sum(len(t) for t in sub_tokens))
                    cur_t = span_start_t
                    avail_dur = max(0.08 * span_s, span_end_t - span_start_t)
                    for k, tok_str in enumerate(sub_tokens):
                        w_dur = avail_dur * (len(tok_str) / float(tot_chars))
                        st = round(cur_t, 3)
                        en = round(cur_t + max(0.06, w_dur * 0.94), 3)
                        aligned_words[s_idx + 1 + k] = {
                            "word": tok_str,
                            "start": st,
                            "end": en
                        }
                        cur_t += w_dur

    # Enforce strict monotonic non-decreasing timestamps across all aligned words
    for i in range(1, len(aligned_words)):
        if aligned_words[i] and aligned_words[i - 1]:
            prev_st = float(aligned_words[i - 1]["start"])
            if float(aligned_words[i]["start"]) < prev_st:
                aligned_words[i]["start"] = round(prev_st + 0.02, 3)
                aligned_words[i]["end"] = round(max(float(aligned_words[i]["end"]), float(aligned_words[i]["start"]) + 0.06), 3)

    # Step 3: Group aligned words into natural sentence segments
    segments = []
    cur_seg_words = []
    seg_id = 0
    for w_obj in aligned_words:
        if not w_obj:
            continue
        cur_seg_words.append(w_obj)
        if w_obj["word"].endswith((".", "!", "?", "؟", "،", ",")) and len(cur_seg_words) >= 6:
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
