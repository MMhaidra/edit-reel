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

## The Signature "Paper & Objects" Aesthetic (Primary Default)

Unless `--design glass` is explicitly requested, every pipeline run defaults to (`--design paper`), using an authentic, tactile physical-object visual language:

### 1. 3-State Alternating Dynamic Rhythm
- **State 1 — Real Studio Footage + Typographic Hook Stamp**:
  - Preserves the speaker's authentic camera background during conversational delivery:
    - Opening hook (first 5–12 seconds) with optional minimal editorial header stamp above the head.
    - Natural thought transitions and breathers between visual concepts.
    - Final takeaway and outro.
  - Alternates subtle `1.04x` punch-in camera zooms on alternating sentences for viral eye-tracking retention.
  - Mixed-script captions (`Arial Bold` Arabic + left-to-right `Helvetica Neue` English runs) float cleanly with soft Gaussian drop shadow.
- **State 2 — 3D Pop-Out Speaker Card on Warm Alabaster Paper (`#F3F0E8`) + Editorial Infographics Above**:
  - Frames the speaker's torso and hand gestures cleanly inside an elevated rounded studio card (`190..890, 1155..1730`, zero chopped wrists or floating hand artifacts) while MediaPipe connected-head segmentation pops the speaker's head smoothly out above the card's top border.
  - Keeps subtle left/right (`190px`) and bottom (`190px`) buffers completely clear of native Reels UI buttons.
  - The upper stage (`y = 156..835`) displays micro-provenance academic eyebrow headers, tactile layered stacks, progressive blush-highlighted Georgia Serif archival excerpts, horizontal benchmark bar charts, label-switch sliders, or paper/notebook objects.
- **State 3 — Full-Canvas Editorial Infographics (No Speaker)**:
  - Takes over the entire `#F3F0E8` canvas for deep conceptual breakdowns:
    - Side-by-side 2-column contrast layouts (deep charcoal `#141412` vs stacked sand/blush columns).
    - Side-by-side parallel coordinate charts (e.g. Linear Myth vs. Logarithmic Reality) and global comparisons.

### 2. Editorial & Tactile Visual Components (`motion_library/paper_objects.py`)
- **Micro-Provenance Citations & Academic Notebook Cutoffs**: Single-line editorial citations pinned safely at `y=156` alongside classic torn ruled notebook slips with faint blue-gray rules and Scotch tape.
- **Layered Stack Plates & Callouts**: Staggered tactile plates with strikethrough and terracotta coral (`#CC5A43`) focal transitions.
- **Archival Serif Quote Sheets**: Off-white Georgia Serif document pages with acoustic-synced coral-blush (`#E8C6BC`) highlighter sweeps.
- **Benchmark Charts, Sliders & Physical Objects**: Horizontal bar charts with dashed reference lines, horizontal label-switch sliders, hanging cream tags on strings with gold eyelets, 3D coin stacks, and dimensional arrows.

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
- **Natural Camera Exposure & Skin Tone Grading**:
  - Eliminates over-white highlight blowout from 10-bit Apple HLG / BT.2020 camera footage with gentle gamma compression and selective color balance.
  - Standard SDR tonemapping and reddish-warmth filter chain:
    `scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,eq=gamma=0.85:contrast=0.95:brightness=-0.035:saturation=1.02,colorbalance=rh=0.04:gh=-0.02:bh=-0.03:rm=0.03:gm=-0.01:bm=-0.02:pl=1,unsharp=5:5:0.25:5:5:0.10`
  - Yields rich, healthy, reddish hemoglobin glow (R ~ 124, G ~ 108, B ~ 96) with zero blown-out pixels above 248.
- **Safe Layout Geometry & Zero-Overlap Guarantee**:
  - Safe mobile Reels/TikTok top margin buffer: `y = 0..158` (leaves room for search bar, camera notch, and audio pills).
  - Reference academic notebook cutoffs strictly anchored at `NOTE_Y_SPEAKER = 230` (`y = 158..302`).
  - Secondary tactile objects, chips, and curve plots placed in `y = 315..620` with zero overlap.
  - Speaker cutout active at `y >= 680..720`.
  - All chip and notebook bounding boxes (`label_chip`, `notebook_cutoff`) auto-expand dynamically with at least 32px safe horizontal padding, mathematically guaranteeing zero text clipping.
- **Natural Broadcast Audio Mastering & Room Hiss Suppression**:
  - Strict prohibition against heavy FFT spectral noise cancellation (`afftdn=nr=24`) and aggressive downward gates (`agate`), which cause watery phase artifacts and hollow barrel resonance.
  - Clean, transparent broadcast vocal chain with gentle, smooth hiss reduction (`afftdn=nr=10:nf=-52:tn=1:gs=5`) and `lowpass=f=14000`:
    `highpass=f=75,lowpass=f=14000,afftdn=nr=10:nf=-52:tn=1:gs=5,equalizer=f=220:t=q:w=1.0:g=-1.0,equalizer=f=3800:t=q:w=1.0:g=1.5,acompressor=threshold=-18dB:ratio=2.2:attack=15:release=100:makeup=2.0dB,loudnorm=I=-11.5:LRA=6.0:TP=-0.5`
  - Drops room preamp hiss during pauses from -45 dB to -51 dB while preserving full vocal tone and chest resonance mastered to **-11.5 LUFS**.
  - **Background Music**: Warm ambient music bed (`ambient_bed.wav`) low-passed at `850 Hz` at `volume=0.045`.
  - **Keyframe-Locked SFX**: Micro-accents (`0.036..0.048` volume) synchronized to object reveal milestones (`paper_turn.wav`, `cash_chime.wav`, `tech_tick.wav`, `subtle_whoosh.wav`).
- **Automated Output Naming & Summary Export (`pipeline.py`)**:
  - Automatically exports cleanly titled MP4 filenames (e.g., `Reel_<Title>_<Lang>.mp4`) alongside per-reel `<Video_Stem>_summary_and_titles.txt` and cumulative `reels_summary_and_titles.txt` inside `edited_output/`.
- **100% Subscription-Free Tooling**:
  - Uses local open-source tools only (`faster-whisper`, MediaPipe, FFmpeg, PIL, `yt-dlp`, `hyperframes`), zero paid cloud APIs or subscriptions.

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

### Download Reference Media & B-Roll (yt-dlp):
```bash
# Download reference video / viral clip
~/.gemini/config/skills/edit-reel/.venv/bin/python3 \
  ~/.gemini/config/skills/edit-reel/scripts/download_ref.py "https://youtube.com/watch?v=..." -n ref_broll

# Download and trim specific scene
~/.gemini/config/skills/edit-reel/.venv/bin/python3 \
  ~/.gemini/config/skills/edit-reel/scripts/download_ref.py "https://youtube.com/watch?v=..." -s 00:01:10 -e 00:01:25 -n broll_clip

# Download audio only (WAV)
~/.gemini/config/skills/edit-reel/.venv/bin/python3 \
  ~/.gemini/config/skills/edit-reel/scripts/download_ref.py "https://..." --audio-only -n reference_audio
```

### Secondary Design & Framing Options (`--design`, `--speaker-style`, `--subtitle-style`, `--no-hook-stamp`):
```bash
# Default (Editorial Paper + 3D Pop-Out Speaker Card + All Editorial Tricks):
~/.gemini/config/skills/edit-reel/.venv/bin/python3 \
  ~/.gemini/config/skills/edit-reel/scripts/pipeline.py \
  -i ~/Desktop/projects/reels_IG/raw_video.MP4 \
  --lang darija

# Classic Paper Mode (Original warm #E2DDD1 kraft + full torso cutout + bold-stroke captions):
~/.gemini/config/skills/edit-reel/.venv/bin/python3 \
  ~/.gemini/config/skills/edit-reel/scripts/pipeline.py \
  -i ~/Desktop/projects/reels_IG/raw_video.MP4 \
  --design classic-paper --subtitle-style bold-stroke

# Editorial Paper with Classic Cutout Torso (mix & match framing styles):
~/.gemini/config/skills/edit-reel/.venv/bin/python3 \
  ~/.gemini/config/skills/edit-reel/scripts/pipeline.py \
  -i ~/Desktop/projects/reels_IG/raw_video.MP4 \
  --design paper --speaker-style cutout --no-hook-stamp

# Obsidian Glass & HyperFrames Mode (Secondary dark tech studio aesthetic):
~/.gemini/config/skills/edit-reel/.venv/bin/python3 \
  ~/.gemini/config/skills/edit-reel/scripts/pipeline.py \
  --input-folder ~/Desktop/projects/reels_IG \
  --output-dir ~/Desktop/projects/reels_IG/edited_output \
  --lang darija \
  --design glass

# HyperFrames Standalone Card Scaffolding & Rendering:
~/.gemini/config/skills/edit-reel/.venv/bin/python3 \
  ~/.gemini/config/skills/edit-reel/scripts/hyperframes_engine.py init stat_card -d 6
~/.gemini/config/skills/edit-reel/.venv/bin/python3 \
  ~/.gemini/config/skills/edit-reel/scripts/hyperframes_engine.py render ~/Desktop/projects/reels_IG/motion_hyperframes/stat_card
~/.gemini/config/skills/edit-reel/.venv/bin/python3 \
  ~/.gemini/config/skills/edit-reel/scripts/hyperframes_engine.py render ~/Desktop/projects/reels_IG/motion_hyperframes/stat_card --transparent
```

#### Available Options Summary
- `--design {paper, classic-paper, glass}`:
  - `paper` *(default)*: Warm alabaster `#F3F0E8`, terracotta `#CC5A43` focal accents, `popout` rounded speaker card, micro-provenance eyebrow header, and generic data-driven storytelling templates (`layered_stack`, `quote_excerpt`, `benchmark_bars`, `label_slider`, `two_col_compare`).
  - `classic-paper`: Restores original `#E2DDD1` warm kraft paper, full-body MediaPipe cutout (`cutout`), and torn notebook citations without rounded card frame.
  - `glass`: Dark obsidian studio gradient with frosted HyperFrames glassmorphic cards.
- `--speaker-style {auto, popout, cutout}`: Switch between **3D Pop-Out Floating Card** (`popout`, protects hand gestures) and **Full Body Cutout** (`cutout`).
- `--subtitle-style {editorial, bold-stroke}`: Switch between crisp soft-shadow editorial text and classic thick dark outline captions.
- `--no-hook-stamp`: Disables the State 1 top-of-head opening typographic badge + title stamp.

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
