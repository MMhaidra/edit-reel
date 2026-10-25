---
name: edit-reel
description: >-
  Fully autonomous, zero-interaction video editing pipeline for Instagram Reels.
  Strictly focused on Quant/Finance/Science/Tech talking-head content for 'Quant and the Physicist' (English)
  and Moroccan Darija Account (الدارجة المغربية بالحروف العربية). Features the signature 'Paper & Objects'
  editorial aesthetic (learned from viral creator reels): real studio background for talking head shots,
  selective AI person cutout onto warm paper canvas (#E2DDD1) during animations, tangible physical objects
  (hanging tags on strings with gold eyelets, 3D coin stacks, arrows, chips), academic notebook cutoffs for peer-reviewed
  citations, side-by-side comparative parallel plots, animated rolling money counters, kinetic subtitles over video,
  -11.5 LUFS broadcast voice mastering, 0.045 ambient music bed, and keyframe-locked SFX.
  Delivers strictly the final production reel with zero clutter from ~/Desktop/projects/reels_IG/ with zero
  mid-process questions. Trigger with /edit-reel or /reel.
---

# Reel Auto-Editor: Autonomous Production Pipeline for Instagram Reels

This skill enables Antigravity to monitor your raw video folder (`~/Desktop/projects/reels_IG/`) and **autonomously produce high-engagement, production-ready 9:16 vertical Instagram Reels** with **zero user interaction during execution**.

### Dedicated Content Focus (Strict Scope)
1. **Quant and the Physicist** (English: Quantitative Finance, Macroeconomics, Capital Markets, Physics, Math, Academia, Scientific Papers, Complex Algorithms).
2. **Moroccan Darija Account** (الدارجة المغربية بالحروف العربية: AI, Finance, Tech Concepts).

---

## The Signature "Paper & Objects" Aesthetic (V10 Architecture)

The pipeline employs an authentic, tactile physical-object visual language inspired by elite editorial creators:

### 1. 3-State Alternating Dynamic Rhythm
- **State 1 — Real Studio Footage (Camera A/B)**:
  - Preserves the speaker's **real camera background** (office, blinds, desk) during conversational delivery:
    - Opening hook (first 5–7 seconds).
    - Natural thought transitions and pauses between visual concepts.
    - Final takeaway and outro.
  - Alternates subtle `1.04x` punch-in camera zooms on alternating sentences for viral eye-tracking retention.
  - Subtitles float over the lower chest with a soft dark shadow for maximum legibility.
- **State 2 — Lowered Cutout Speaker on Paper (`y ~ 800..1920`) + Physical Objects Above**:
  - Automatically activated **only while an animation/graphic is actively showing**.
  - MediaPipe AI person segmentation (`selfie_segmenter.tflite` + Gaussian smoothstep alpha cleanup) cleanly isolates the speaker and places them standing directly on the warm, grainy paper canvas (`#E2DDD1`).
  - The upper half (`y = 0..900`) displays tangible physical objects and academic notebook cutoffs.
- **State 3 — Full-Screen Paper Infographics (No Speaker)**:
  - Takes over the entire canvas for deep conceptual breakdowns:
    - **Side-by-side parallel coordinate charts** (e.g. `LINEAR MYTH` vs `LOGARITHMIC REALITY`).
    - **Global comparisons** (e.g. World Happiness Report circular flag badges).

### 2. Tangible Physical Objects (Zero Generic Web-Cards)
- **Hanging Price Tags on Strings**:
  - Cream tags with angled corners, inner stroke border, and gold metal eyelet hanging from a string.
  - Natural pendulum micro-sway upon entry.
  - **Dynamic Loading Money**: Monetary milestones animate as rolling odometer counters (e.g. `$0` $\rightarrow$ `$75,000` before stamping crimson `STOPS?`).
- **3D Coin Stacks & Dimensional Arrows**:
  - Multi-tier gold coin stacks with rim bevels.
  - Forest-green (`#00704A`) up-arrows and crimson (`#BA1828`) down-arrows.
- **Academic Notebook Cutoffs**:
  - Pinned authentic torn notebook slips with faint ruled blue-gray lines (`#CBD5E1`), red vertical margin line (`#F87171`), torn bottom edge, and semi-transparent top Scotch tape.
  - Positioned lower down (`y = 165` on speaker scenes, `y = 210` on full-screen scenes) to ensure a comfortable buffer below mobile status bars, front cameras, and native Instagram interface icons.
  - Typeset in typewriter slab serif (`American Typewriter` / `Courier`) to display peer-reviewed papers (e.g. `PNAS (2023)`, `Harvard 85-Year Study`, `Gallup / Oxford`).
- **Clean Visual Accents**:
  - Rounded white label chips (`border-radius: 18px`) with high-res vector icons.
  - Clean ink lines drawn directly onto the paper canvas.
  - **Zero generic PowerPoint cards, zero tiny corner pills, and zero hazard caution tape**.

---

## Autonomous Execution Rules (Crucial)

- **Zero Mid-Process Questions**: Never pause to ask clarifying questions, solicit confirmation, or request manual inputs during editing. Start immediately and execute all steps end-to-end.
- **Auto Language Determination**:
  - If `/edit-reel darija` or `/reel darija` is given $\rightarrow$ use Moroccan Darija (`darija`).
  - If `/edit-reel english` or `/reel english` is given $\rightarrow$ use English (`en`).
  - If triggered without language $\rightarrow$ default directly to `en` ("Quant and the Physicist").
- **Reference Script Ground-Truth Workflow**:
  - **Auto-Discovery**: Ingests companion script files (`<video_stem>.txt`, `.md`, `.docx`, `script.txt`) as 100% ground-truth for subtitles, equations, and technical spelling.
  - **Script-Guided Forced Alignment**: Aligns exact script words to acoustic timestamps via time-constrained monotonic anchors (zero subtitle drift).
  - **Strict English Study Names Rule**: All academic study names, journal titles, and researcher names remain in English across both English and Moroccan Darija videos.
- **Intelligent Silence, Stumble & Repeated-Word Cutter (`detect_cuts.py`)**:
  - Uses `faster-whisper` (`word_timestamps=True`) to protect every valid spoken syllable.
  - Excises stumbles, false starts, and repeated words.
  - **Anti-Arm-Reach Cutoff**: Identifies the calm smiling frame after the last word and stops cleanly before the speaker reaches out to turn off the camera.
- **Broadcast Audio Mastering**:
  - **Vocal Chain**: Adaptive FFT spectral denoiser (`afftdn=nr=24:nf=-48:tn=1`) + highpass filter (`85 Hz`) + downward expander gate (`agate`) + studio compressor + `loudnorm` mastered to **-11.5 LUFS** (zero room hiss, zero HVAC hum).
  - **Background Music**: Warm ambient music bed (`ambient_bed.wav`) low-passed at `850 Hz` at `volume=0.045`.
  - **Keyframe-Locked SFX**: Barely-audible micro-accents (`0.036..0.048` volume) synchronized to object reveal milestones (`paper_turn.wav`, `cash_chime.wav`, `tech_tick.wav`, `subtle_whoosh.wav`).

---

## Directory Structure

- **Raw recordings input folder**:
  ```text
  /Users/mhaidra/Desktop/projects/reels_IG/
  ```
- **Motion assets & sound effects**:
  ```text
  /Users/mhaidra/.gemini/config/skills/edit-reel/motion_library/sfx/
  /Users/mhaidra/.gemini/config/skills/edit-reel/models/selfie_segmenter.tflite
  ```
- **Processed production reels output folder**:
  ```text
  /Users/mhaidra/Desktop/projects/reels_IG/edited_output/
  ```

---

## Autonomous Execution Commands

### Full Pipeline Run (English):
```bash
/Users/mhaidra/.gemini/config/skills/edit-reel/.venv/bin/python3 \
  /Users/mhaidra/.gemini/config/skills/edit-reel/scripts/pipeline.py \
  --input-folder ~/Desktop/projects/reels_IG \
  --output-dir ~/Desktop/projects/reels_IG/edited_output \
  --lang en
```

### Full Pipeline Run (Moroccan Darija):
```bash
/Users/mhaidra/.gemini/config/skills/edit-reel/.venv/bin/python3 \
  /Users/mhaidra/.gemini/config/skills/edit-reel/scripts/pipeline.py \
  --input-folder ~/Desktop/projects/reels_IG \
  --output-dir ~/Desktop/projects/reels_IG/edited_output \
  --lang darija
```

### Video with Companion Script:
```bash
/Users/mhaidra/.gemini/config/skills/edit-reel/.venv/bin/python3 \
  /Users/mhaidra/.gemini/config/skills/edit-reel/scripts/pipeline.py \
  -i ~/Desktop/projects/reels_IG/C7BAE170-9BB5-4BEC-8458-460D29B3C1B7.MP4 \
  -s ~/Desktop/projects/reels_IG/Money\ vs\ happiness.docx \
  --output-dir ~/Desktop/projects/reels_IG/edited_output \
  --lang en
```

### Direct Master Renderer (Instant Execution):
```bash
/Users/mhaidra/.gemini/config/skills/edit-reel/.venv/bin/python3 \
  /Users/mhaidra/.gemini/config/skills/edit-reel/scripts/render_reel.py
```

### Preview All Scene Stills & Contact Sheet:
```bash
/Users/mhaidra/.gemini/config/skills/edit-reel/.venv/bin/python3 \
  /Users/mhaidra/.gemini/config/skills/edit-reel/scripts/preview_reel_stills.py /tmp/reel_previews
```

---

## Packaging & Sharing this Skill

The entire self-contained skill is located at:
```text
/Users/mhaidra/.gemini/config/skills/edit-reel/
```

To share it with a colleague or transfer to another workstation:
1. **Archive the skill directory** (excluding the local `.venv` and cache to keep the zip light):
   ```bash
   tar -czf edit-reel-skill.tar.gz -C ~/.gemini/config/skills/edit-reel --exclude=".venv" --exclude=".reel_cache" .
   ```
2. **On the target machine**, extract into their skills folder (e.g. `~/.gemini/config/skills/edit-reel/`) and recreate the virtual environment:
   ```bash
   python3 -m venv ~/.gemini/config/skills/edit-reel/.venv
   ~/.gemini/config/skills/edit-reel/.venv/bin/pip install pillow numpy opencv-python-headless mediapipe faster-whisper
   ```
The AI models (`models/selfie_segmenter.tflite`), audio suite (`motion_library/sfx/`), and graphics library (`motion_library/paper_objects.py`) are all stored directly inside the skill directory, making it 100% portable.

