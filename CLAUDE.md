# Claude Code Guide for edit-reel

`edit-reel` is an autonomous AI video editor producing 9:16 vertical Instagram Reels and TikToks using the signature tactile **"Paper & Objects"** editorial aesthetic.

## Architecture
- **Language**: Python 3.9+ (`requirements.txt`).
- **Core Dependencies**: `pillow`, `numpy`, `opencv-python-headless`, `mediapipe`, `faster-whisper`, `ffmpeg`.
- **Pipeline Runner**: `scripts/pipeline.py`
- **Master Renderer**: `scripts/render_reel.py`
- **Physical Objects Library**: `motion_library/paper_objects.py`
- **Segmentation Model**: `models/selfie_segmenter.tflite`
- **Sound Effects**: `motion_library/sfx/`

## Execution Commands
- **Full Video Pipeline**:
  ```bash
  .venv/bin/python3 scripts/pipeline.py -i <input.mp4> -s <script.txt> -o <output_dir> --lang en
  ```
- **Preview All 8 Scene Stills & Contact Sheet**:
  ```bash
  .venv/bin/python3 scripts/preview_reel_stills.py /tmp/reel_previews
  ```
- **Lint / Syntax Check**:
  ```bash
  python3 -m py_compile scripts/*.py motion_library/*.py
  ```

## Key Editorial Conventions
1. **3-State Alternating Rhythm**:
   - *State 1 (Real Studio)*: Speaker with original camera background for hook and narrative pauses.
   - *State 2 (Lowered Cutout)*: Isolated speaker on warm paper (`#E2DDD1`, `y=800..1920`) with physical objects above (`y=0..900`).
   - *State 3 (Full-Screen Infographics)*: Parallel coordinate plots, country rankings, or concept diagrams without speaker.
2. **Notebook Cutoffs**:
   - Pinned authentic torn notebook slips for academic citations (`y=165` on speaker scenes, `y=210` on full-screen scenes).
3. **Sound Engineering**:
   - Vocals mastered to -11.5 LUFS with highpass filter (`85 Hz`) + downward expander gate + studio compressor.
   - Ambient music bed (`ambient_bed.wav`) low-passed at 850 Hz at volume 0.045.
   - Barely-audible micro-SFX (0.036..0.048 volume) locked to key visual beats.
