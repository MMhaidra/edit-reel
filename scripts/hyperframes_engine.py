#!/usr/bin/env python3
"""
hyperframes_engine.py - HTML/CSS/WebM Motion Graphics Engine using HyperFrames.

Part of the edit-reel open-source production suite (100% free, local, & Apache-2.0).
Provides a secondary, web-standards motion graphics option:
1. Scaffolds 9:16 vertical HTML/CSS/Canvas animation projects.
2. Renders standalone explainer motion graphics (MP4).
3. Renders transparent alpha motion graphics (WebM) for FFmpeg video overlays.
"""

import sys
import os
import json
import argparse
import subprocess
from pathlib import Path

DEFAULT_HF_DIR = Path.home() / "Desktop" / "projects" / "reels_IG" / "motion_hyperframes"


def init_composition(name="motion_card", output_dir=None, width=1080, height=1920, fps=30, duration=8):
    output_dir = Path(output_dir or (DEFAULT_HF_DIR / name)).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n[hyperframes_engine] Scaffolding HyperFrames composition: '{name}'")
    print(f"  Target:   {output_dir}")
    print(f"  Geometry: {width}x{height} @ {fps}fps, {duration}s")

    # Write hyperframes.json
    hf_config = {
        "width": width,
        "height": height,
        "fps": fps,
        "duration": duration,
        "entry": "index.html"
    }
    with open(output_dir / "hyperframes.json", "w", encoding="utf-8") as f:
        json.dump(hf_config, f, indent=2)

    # Write package.json
    pkg_config = {
        "name": name,
        "version": "1.0.0",
        "private": True,
        "scripts": {
            "dev": "hyperframes preview",
            "render": "hyperframes render -o output.mp4",
            "render-overlay": "hyperframes render --format webm -o overlay.webm"
        }
    }
    with open(output_dir / "package.json", "w", encoding="utf-8") as f:
        json.dump(pkg_config, f, indent=2)

    # Write index.html with HyperFrames 9:16 vertical standard root & GSAP
    html_content = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width={width}, height={height}" />
  <script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
  <style>
    :root {{
      --ground: transparent;
      --card-bg: rgba(255, 255, 255, 0.95);
      --ink: #111827;
      --sub: #4B5563;
      --accent: #00704A;
      --font-display: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }}
    * {{
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }}
    html, body {{
      margin: 0;
      width: {width}px;
      height: {height}px;
      overflow: hidden;
      background: var(--ground);
    }}
    #root {{
      width: 100%;
      height: 100%;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      font-family: var(--font-display);
    }}
    .card {{
      background: var(--card-bg);
      border-radius: 40px;
      padding: 64px 80px;
      box-shadow: 0 30px 80px rgba(0, 0, 0, 0.14);
      border: 2px solid rgba(255, 255, 255, 0.85);
      max-width: 920px;
      text-align: center;
    }}
    .badge {{
      display: inline-block;
      background: var(--accent);
      color: #FFFFFF;
      font-size: 26px;
      font-weight: 700;
      padding: 10px 28px;
      border-radius: 999px;
      letter-spacing: 1.5px;
      margin-bottom: 24px;
      text-transform: uppercase;
    }}
    .title {{
      font-size: 58px;
      font-weight: 800;
      color: var(--ink);
      line-height: 1.15;
      margin-bottom: 20px;
    }}
    .subtitle {{
      font-size: 32px;
      font-weight: 500;
      color: var(--sub);
      line-height: 1.4;
    }}
  </style>
</head>
<body>
  <div
    id="root"
    data-composition-id="main"
    data-start="0"
    data-duration="{duration}"
    data-width="{width}"
    data-height="{height}"
  >
    <div id="card" class="card clip" data-start="0" data-duration="{duration}" data-track-index="0">
      <div class="badge">HyperFrames Motion</div>
      <div class="title">Empirical Evidence & Insights</div>
      <div class="subtitle">HTML, CSS & GSAP Motion Graphics (1080x1920)</div>
    </div>
  </div>
  <script>
    window.__timelines = window.__timelines || {{}};
    const tl = gsap.timeline({{ paused: true }});
    tl.fromTo("#card", 
      {{ opacity: 0, scale: 0.88, y: 80 }},
      {{ opacity: 1, scale: 1.0, y: 0, duration: 0.8, ease: "power3.out" }}, 
      0.2
    );
    tl.to("#card",
      {{ opacity: 0, scale: 0.94, y: -40, duration: 0.6, ease: "power2.in" }},
      {duration} - 0.7
    );
    window.__timelines["main"] = tl;
    tl.seek(0);
  </script>
</body>
</html>
"""
    with open(output_dir / "index.html", "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"[hyperframes_engine] Composition initialized at: {output_dir}")
    return output_dir


def render_composition(project_dir, output_file=None, transparent=False):
    project_dir = Path(project_dir).resolve()
    if not (project_dir / "index.html").exists():
        print(f"[hyperframes_engine] Error: {project_dir} is not a valid HyperFrames directory.", file=sys.stderr)
        return None

    ext = "webm" if transparent else "mp4"
    if not output_file:
        output_file = project_dir / f"rendered_motion.{ext}"
    else:
        output_file = Path(output_file).resolve()

    print(f"\n[hyperframes_engine] Rendering with HyperFrames CLI...")
    print(f"  Project:    {project_dir}")
    print(f"  Output:     {output_file}")
    print(f"  Alpha Mode: {'Transparent WebM' if transparent else 'Standard MP4'}")

    # Detect hyperframes binary (global or npx)
    import shutil
    hf_bin = shutil.which("hyperframes")
    if hf_bin:
        cmd = [hf_bin, "render"]
    else:
        cmd = ["npx", "--yes", "hyperframes@0.9.54", "render"]

    if transparent:
        cmd.extend(["--format", "webm"])
    cmd.extend(["-o", str(output_file)])

    try:
        subprocess.run(cmd, cwd=str(project_dir), check=True)
        print(f"[hyperframes_engine] Render successful: {output_file}\n")
        return output_file
    except subprocess.CalledProcessError as e:
        print(f"[hyperframes_engine] Render error: {e}", file=sys.stderr)
        return None


def main():
    parser = argparse.ArgumentParser(description="HyperFrames HTML/CSS Motion Graphics Engine (Option B).")
    subparsers = parser.add_subparsers(dest="command", help="Sub-commands")

    # init
    p_init = subparsers.add_parser("init", help="Create a new HyperFrames motion composition")
    p_init.add_argument("name", help="Name of composition")
    p_init.add_argument("-o", "--output-dir", default=None, help="Output directory")
    p_init.add_argument("-w", "--width", type=int, default=1080, help="Width (default: 1080)")
    p_init.add_argument("-t", "--height", type=int, default=1920, help="Height (default: 1920)")
    p_init.add_argument("-d", "--duration", type=int, default=8, help="Duration in seconds (default: 8)")

    # render
    p_render = subparsers.add_parser("render", help="Render a HyperFrames motion composition")
    p_render.add_argument("project_dir", help="HyperFrames project folder")
    p_render.add_argument("-o", "--output", default=None, help="Output video file path")
    p_render.add_argument("--transparent", action="store_true", help="Render transparent WebM overlay")

    args = parser.parse_args()
    if args.command == "init":
        init_composition(args.name, args.output_dir, args.width, args.height, duration=args.duration)
    elif args.command == "render":
        render_composition(args.project_dir, args.output, args.transparent)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
