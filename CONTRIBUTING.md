# Contributing to edit-reel

Thank you for your interest in contributing to edit-reel. We welcome bug reports, feature suggestions, new physical motion primitives, and improvements to agentic IDE workflows.

## Development Setup

1. Fork the repository on GitHub: `https://github.com/MMhaidra/edit-reel/fork`
2. Clone your fork locally:
   ```bash
   git clone https://github.com/<your-username>/edit-reel.git
   cd edit-reel
   ```
3. Create a dedicated Python virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
4. Ensure FFmpeg is installed:
   ```bash
   # macOS
   brew install ffmpeg
   # Ubuntu / Debian
   sudo apt-get install -y ffmpeg
   ```

## Adding New Motion Primitives

All physical objects and editorial graphic elements live inside `motion_library/`:
- `motion_library/paper_objects.py`: Canvas primitives (hanging tags, coin stacks, notebook paper cutoffs, odometers).
- `motion_library/palette.py`: Editorial color system (`#E2DDD1` paper, `#00704A` green, `#BA1828` red).
- `motion_library/icons/`: High-resolution vector icon SVGs and PNGs.

When adding a new primitive:
1. Adhere to the tactile aesthetic: realistic drop shadows, warm cream paper tones, and authentic materials (paper, brass, Scotch tape).
2. Avoid generic digital web-cards, neon colors, and caution stripes.
3. Test rendering via `python scripts/preview_reel_stills.py /tmp/test_previews`.

## Pull Request Guidelines

1. Create a feature branch: `git checkout -b feature/your-feature-name`.
2. Keep code clean and self-documenting.
3. Verify syntax across all modules:
   ```bash
   python3 -m py_compile scripts/*.py motion_library/*.py
   ```
4. Do not commit temporary video outputs, cache folders (`.reel_cache*`), or personal API tokens.
5. Push to your fork and submit a Pull Request against the `main` branch.
