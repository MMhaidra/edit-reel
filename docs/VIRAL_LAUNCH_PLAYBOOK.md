# Viral Launch Playbook for edit-reel

This playbook provides copy-paste promotional posts, launch templates, and community directory submission entries to maximize visibility, traffic, and GitHub stars.

---

## 1. Hacker News (Show HN)

**URL**: `https://news.ycombinator.com/submit`  
**Title**:  
`Show HN: edit-reel – Autonomous open-source AI video editor for Reels and TikTok in Python`

**Post Body**:
```text
Hi HN,

We built edit-reel because commercial short-form video clippers (CapCut, Submagic, OpusClip, Veed) either cost monthly SaaS fees, watermark your videos, or output generic neon templates that trigger immediate viewer fatigue.

edit-reel is a free, local-first open-source Python pipeline and agent skill (for Claude Code, Cursor, and Google Antigravity) that transforms raw talking-head footage into 9:16 vertical reels with zero manual timeline interaction:

1. Tactile "Paper and Objects" Editorial Aesthetic: Renders on warm cream paper (#E2DDD1) with physical hanging tags, rolling odometer counters, 3D coin stacks, and authentic academic notebook cutoffs for study citations.
2. Word-Level Speech Cutting: Uses Faster-Whisper to protect spoken syllables while automatically trimming false starts, stumbles, and pauses, with an anti-arm-reach tail cutoff before the speaker touches the lens.
3. Local Vision Segmentation: Uses MediaPipe AI (selfie_segmenter) locally on CPU/GPU without cloud API dependencies.
4. Broadcast Audio Mastering: Normalizes dialogue to -11.5 LUFS with spectral noise suppression, highpass gating, ducked ambient music bed (0.045 volume), and motion-synced sound effects.

Repository: https://github.com/MMhaidra/edit-reel
Interactive Colab: https://colab.research.google.com/github/MMhaidra/edit-reel/blob/main/demo.ipynb

Feedback and contributions welcome!
```

---

## 2. Reddit Communities

### A. r/Python
**Title**: `I built edit-reel: An autonomous open-source AI video editor & auto subtitles generator using Faster-Whisper, MediaPipe & FFmpeg`  
**Flair**: `Project` / `Showcase`  
**Content**:
```text
Hey r/Python,

I wanted to share edit-reel, an open-source Python tool designed to automate short-form video editing (Reels, TikTok, Shorts) without relying on paid cloud services.

Key Architecture:
- Faster-Whisper: Extracts word-level acoustic timestamps to cut silence, stumbles, and retakes without clipping soft speech.
- MediaPipe: Fast local person segmentation (244KB TFLite model) isolating the speaker onto a warm textured paper canvas.
- Procedural Motion Graphics: Pillow & OpenCV rendering hanging price tags, 3D coin stacks, and academic notebook paper slips for citations.
- FFmpeg Multi-Track Audio Chain: Mastered to -11.5 LUFS with highpass filter, downward expander gate, and motion micro-SFX.
- Agent Skill: Works as a standalone CLI or as an autonomous skill inside Claude Code, Cursor, and Antigravity.

GitHub: https://github.com/MMhaidra/edit-reel
Colab Demo: https://colab.research.google.com/github/MMhaidra/edit-reel/blob/main/demo.ipynb

Would love your thoughts and suggestions on new motion primitives!
```

### B. r/LocalLLaMA & r/ClaudeAI & r/Cursor
**Title**: `edit-reel: Open-source autonomous video editor skill for Claude Code, Cursor & local coding agents`  
**Content**:
```text
If you are experimenting with agentic coding IDEs like Claude Code, Cursor, Windsurf, or Antigravity, you can now give your agent the capability to autonomously edit video footage.

Running:
`Install the /edit-reel skill globally from https://github.com/MMhaidra/edit-reel`

allows your agent to take raw smartphone footage, excise false starts, generate tactile paper motion graphics, master the audio track, and output a finished 9:16 vertical reel. Everything runs 100% locally on your machine with zero API cost.

Check out the repo: https://github.com/MMhaidra/edit-reel
```

---

## 3. Twitter / X Launch Thread

**Tweet 1 (The Hook + Looping GIF)**:
```text
Most AI video editors look identical: neon subtitles, floating web-cards, and cheap animations.

Introducing edit-reel: a free, open-source AI video editor that brings the tactile "Paper & Objects" aesthetic to Reels & TikTok.

100% local. Faster-Whisper + MediaPipe + FFmpeg.

[Attach pipeline_flow.gif or video demo]
```

**Tweet 2 (The Aesthetic)**:
```text
Why "Paper & Objects"?

Instead of generic digital boxes, edit-reel renders on warm textured paper (#E2DDD1) with physical objects:
- Hanging cream price tags with gold eyelets
- Rolling odometer money counters
- 3D coin stacks
- Pinned notebook slips with Scotch tape for paper citations
```

**Tweet 3 (Speech-Protected Trimming)**:
```text
Standard silence trimmers use volume thresholds that chop off the start/end of words.

edit-reel uses Faster-Whisper for millisecond word-boundary locks. It cuts stumbles, retakes, and pauses while preserving natural cadence, plus an automatic cutoff before you reach to stop recording.
```

**Tweet 4 (Agentic Skill Integration)**:
```text
Works as a standalone CLI or as a native skill for:
- Claude Code
- Cursor / Windsurf
- Google Antigravity
- OpenAI Codex

Install with one line:
curl -fsSL https://raw.githubusercontent.com/MMhaidra/edit-reel/main/install.sh | bash
```

**Tweet 5 (Links)**:
```text
Try the Google Colab demo or star the repo on GitHub:

GitHub: https://github.com/MMhaidra/edit-reel
Colab: https://colab.research.google.com/github/MMhaidra/edit-reel/blob/main/demo.ipynb

If you find this useful, a star on GitHub is greatly appreciated!
```

---

## 4. Awesome Lists Submission PRs

Submit a Pull Request to these high-traffic repositories:

### A. `hesreallyhim/awesome-claude-code`
- **Section**: `Skills & Extensions`
- **Markdown Entry**:
  ```markdown
  - [edit-reel](https://github.com/MMhaidra/edit-reel) - Autonomous open-source AI video editor and auto subtitles generator for 9:16 Reels and TikTok using Faster-Whisper, MediaPipe, and FFmpeg.
  ```

### B. `zhuyansen/awesome-claude-video-skills`
- **Section**: `Video Editing & Shorts`
- **Markdown Entry**:
  ```markdown
  - [edit-reel](https://github.com/MMhaidra/edit-reel) - Tactile Paper & Objects editorial video editing skill for Claude Code with speech-protected cutting and broadcast audio mastering.
  ```

### C. `krzemienski/awesome-video`
- **Section**: `Editing & Automation`
- **Markdown Entry**:
  ```markdown
  - [edit-reel](https://github.com/MMhaidra/edit-reel) - Python autonomous video editor for Instagram Reels and TikTok with acoustic forced alignment and MediaPipe segmentation.
  ```
