---
name: edit-reel
description: >-
  Fully autonomous, zero-interaction video editing pipeline for Instagram Reels and TikTok.
  Designed for high-signal talking-head educational, scientific, tech, financial, and explanatory content
  across worldwide languages (English, Spanish, Mandarin, Hindi, Arabic, French, Portuguese, German, Japanese).
  Features the signature 'Paper & Objects' editorial aesthetic: real camera studio footage for conversational hooks,
  selective MediaPipe AI person cutout onto warm paper canvas (#E2DDD1) during animated explanations, tangible physical
  objects (hanging cream tags with gold eyelets, 3D coin stacks, dimensional arrows, rounded icon chips), authentic
  academic notebook cutoffs for peer-reviewed citations, side-by-side comparative parallel coordinate plots, dynamic
  rolling odometer counters, kinetic subtitles, broadcast vocal mastering (-11.5 LUFS), ambient background music bed
  (0.045), and keyframe-locked SFX. Delivers the final production reel autonomously with zero mid-process questions.
  Trigger with /edit-reel or /reel.
---

# Reel Auto-Editor: Autonomous Production Pipeline for Instagram Reels

This skill enables Antigravity to monitor your raw video folder (`~/Desktop/projects/reels_IG/`) and autonomously produce high-engagement, production-ready 9:16 vertical Instagram Reels with zero user interaction during execution.

### Content Scope & Language Versatility
The pipeline supports educational, scientific, academic, macroeconomic, business, coding, and explanatory creators worldwide:
1. **Global Languages**: English (`en`), Spanish (`es`), Mandarin Chinese (`zh`), Hindi (`hi`), French (`fr`), Portuguese (`pt`), German (`de`), Japanese (`ja`), Arabic (`ar` - Modern Standard Arabic and regional dialects including Moroccan Darija `ary`).
2. **Universal Ground-Truth Policy**: All academic study names, journal titles, and researcher citations are preserved with typographic integrity.

---

## The Signature "Paper & Objects" Aesthetic

The pipeline employs an authentic, tactile physical-object visual language:

### 1. 3-State Alternating Dynamic Rhythm
- **State 1 — Real Studio Footage (Camera A/B)**:
  - Preserves the speaker's authentic camera background during conversational delivery:
    - Opening hook (first 5–7 seconds).
    - Natural thought transitions and pauses between visual concepts.
    - Final takeaway and outro.
  - Alternates subtle `1.04x` punch-in camera zooms on alternating sentences for viral eye-tracking retention.
  - Subtitles float over the lower chest with a soft dark shadow for maximum legibility.
- **State 2 — Lowered Cutout Speaker on Paper (`y ~ 800..1920`) + Physical Objects Above**:
  - Automatically activated only while an animation or graphic is actively illustrating the point.
  - MediaPipe AI person segmentation (`selfie_segmenter.tflite` + Gaussian smoothstep alpha cleanup) cleanly isolates the speaker and places them standing directly on the warm, grainy paper canvas (`#E2DDD1`).
  - The upper half (`y = 0..900`) displays tangible physical objects and academic notebook cutoffs.
- **State 3 — Full-Screen Paper Infographics (No Speaker)**:
  - Takes over the entire canvas for deep conceptual breakdowns:
    - Side-by-side parallel coordinate charts (e.g. Linear Myth vs. Logarithmic Reality).
    - Global multi-entity comparisons (e.g. Country rankings, metric distributions).

### 2. Tangible Physical Objects (Zero Generic Web-Cards)
- **Hanging Price Tags on Strings**:
  - Cream tags with angled corners, inner stroke border, and gold metal eyelet hanging from a string.
  - Natural pendulum micro-sway upon entry.
  - Dynamic Loading Numbers: Numerical milestones animate as rolling odometer counters.
- **3D Coin Stacks & Dimensional Arrows**:
  - Multi-tier gold coin stacks with rim bevels.
  - Directional green (`#00704A`) up-arrows and red (`#BA1828`) down-arrows.
- **Academic Notebook Cutoffs**:
  - Pinned authentic torn notebook slips with faint ruled blue-gray lines (`#CBD5E1`), red vertical margin line (`#F87171`), torn bottom edge, and semi-transparent top Scotch tape.
  - Positioned lower down (`y = 165` on speaker scenes, `y = 210` on full-screen scenes) to ensure a comfortable buffer below mobile status bars, front cameras, and native interface icons.
  - Typeset in typewriter slab serif (`American Typewriter` / `Courier`) to display peer-reviewed papers.
- **Clean Visual Accents**:
  - Rounded white label chips (`border-radius: 18px`) with high-res vector icons.
  - Clean ink lines drawn directly onto the paper canvas.

---

## Autonomous Execution Rules

- **Zero Mid-Process Questions**: Never pause to ask clarifying questions, solicit confirmation, or request manual inputs during editing. Start immediately and execute all steps end-to-end.
- **Auto Language Determination**:
  - If `/edit-reel <lang>` or `/reel <lang>` is given, use that language code (e.g. `en`, `es`, `zh`, `hi`, `ar`, `fr`, `pt`, `de`, `ja`, `darija`).
  - If triggered without language, default directly to `en`.
- **Reference Script Ground-Truth Workflow**:
  - **Auto-Discovery**: Ingests companion script files (`<video_stem>.txt`, `.md`, `.docx`, `script.txt`) as ground-truth for subtitles, equations, and technical spelling.
  - **Script-Guided Forced Alignment**: Aligns exact script words to acoustic timestamps via time-constrained monotonic anchors.
- **Intelligent Silence, Stumble & Repeated-Word Cutter (`detect_cuts.py`)**:
  - Uses `faster-whisper` (`word_timestamps=True`) to protect every valid spoken syllable.
  - Excises stumbles, false starts, and repeated takes.
  - **Anti-Arm-Reach Cutoff**: Identifies the calm frame after the last spoken word and stops cleanly before the speaker reaches out to turn off the camera.
- **Broadcast Audio Mastering**:
  - **Vocal Chain**: Adaptive FFT spectral denoiser (`afftdn=nr=24:nf=-48:tn=1`) + highpass filter (`85 Hz`) + downward expander gate (`agate`) + studio compressor + `loudnorm` mastered to **-11.5 LUFS**.
  - **Background Music**: Warm ambient music bed (`ambient_bed.wav`) low-passed at `850 Hz` at `volume=0.045`.
  - **Keyframe-Locked SFX**: Micro-accents (`0.036..0.048` volume) synchronized to object reveal milestones (`paper_turn.wav`, `cash_chime.wav`, `tech_tick.wav`, `subtle_whoosh.wav`).

---

## Directory Structure

- **Raw recordings input folder**:
  ```text
  ~/Desktop/projects/reels_IG/
  ```
- **Motion assets & sound effects**:
  ```text
  ~/.gemini/config/skills/edit-reel/motion_library/sfx/
  ~/.gemini/config/skills/edit-reel/models/selfie_segmenter.tflite
  ```
- **Processed production reels output folder**:
  ```text
  ~/Desktop/projects/reels_IG/edited_output/
  ```

---

## Autonomous Execution Commands

### Full Pipeline Run (English):
```bash
~/.gemini/config/skills/edit-reel/.venv/bin/python3 \
  ~/.gemini/config/skills/edit-reel/scripts/pipeline.py \
  --input-folder ~/Desktop/projects/reels_IG \
  --output-dir ~/Desktop/projects/reels_IG/edited_output \
  --lang en
```

### Full Pipeline Run (Spanish / Arabic / French / German):
```bash
~/.gemini/config/skills/edit-reel/.venv/bin/python3 \
  ~/.gemini/config/skills/edit-reel/scripts/pipeline.py \
  --input-folder ~/Desktop/projects/reels_IG \
  --output-dir ~/Desktop/projects/reels_IG/edited_output \
  --lang es
```

### Video with Companion Script:
```bash
~/.gemini/config/skills/edit-reel/.venv/bin/python3 \
  ~/.gemini/config/skills/edit-reel/scripts/pipeline.py \
  -i ~/Desktop/projects/reels_IG/sample_video.MP4 \
  -s ~/Desktop/projects/reels_IG/script.docx \
  --output-dir ~/Desktop/projects/reels_IG/edited_output \
  --lang en
```

### Direct Master Renderer (Instant Execution):
```bash
~/.gemini/config/skills/edit-reel/.venv/bin/python3 \
  ~/.gemini/config/skills/edit-reel/scripts/render_reel.py
```

### Preview All Scene Stills & Contact Sheet:
```bash
~/.gemini/config/skills/edit-reel/.venv/bin/python3 \
  ~/.gemini/config/skills/edit-reel/scripts/preview_reel_stills.py /tmp/reel_previews
```

---

## Packaging & Sharing this Skill

The entire self-contained skill is located at:
```text
~/.gemini/config/skills/edit-reel/
```

To share it with a colleague or transfer to another workstation:
1. **Archive the skill directory** (excluding `.venv` and cache):
   ```bash
   tar -czf edit-reel-skill.tar.gz -C ~/.gemini/config/skills/edit-reel --exclude=".venv" --exclude=".reel_cache*" .
   ```
2. **On the target machine**, extract into the skills directory:
   ```bash
   mkdir -p ~/.gemini/config/skills/edit-reel
   tar -xzf edit-reel-skill.tar.gz -C ~/.gemini/config/skills/edit-reel
   python3 -m venv ~/.gemini/config/skills/edit-reel/.venv
   ~/.gemini/config/skills/edit-reel/.venv/bin/pip install -r ~/.gemini/config/skills/edit-reel/requirements.txt
   ```
