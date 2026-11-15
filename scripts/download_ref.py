#!/usr/bin/env python3
"""
download_ref.py - High-Efficiency Reference & B-Roll Downloader using yt-dlp.

Part of the edit-reel open-source production suite (100% free & local).
Downloads reference footage, B-roll, research talks, or audio from
YouTube, TikTok, Instagram Reels, X/Twitter, etc. into ~/Desktop/projects/reels_IG/references/
"""

import sys
import os
import argparse
import subprocess
from pathlib import Path

DEFAULT_REF_DIR = Path.home() / "Desktop" / "projects" / "reels_IG" / "references"


def download_media(url, output_dir=None, filename=None, start_time=None, end_time=None, audio_only=False):
    output_dir = Path(output_dir or DEFAULT_REF_DIR).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n[download_ref] Initiating yt-dlp media fetch...")
    print(f"  URL:        {url}")
    print(f"  Destination:{output_dir}")

    # Build yt-dlp command
    venv_ytdlp = Path(__file__).resolve().parent.parent / ".venv" / "bin" / "yt-dlp"
    ytdlp_bin = str(venv_ytdlp) if venv_ytdlp.exists() else "yt-dlp"

    out_template = str(output_dir / (f"{filename}.%(ext)s" if filename else "%(title).60s_%(id)s.%(ext)s"))

    cmd = [
        ytdlp_bin,
        "--no-playlist",
        "--embed-metadata",
        "-o", out_template
    ]

    if audio_only:
        cmd.extend([
            "-x",
            "--audio-format", "wav",
            "--audio-quality", "0"
        ])
    else:
        # Best SDR 1080p video with audio merged to mp4 (or fallback to any best format)
        cmd.extend([
            "-f", "bestvideo[height<=1080]+bestaudio/best[height<=1080]/best",
            "--merge-output-format", "mp4"
        ])

    cmd.append(url)

    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"[download_ref] Error downloading media: {e}", file=sys.stderr)
        return None

    # Find the downloaded file
    downloaded_files = sorted(output_dir.glob(f"{filename or '*'}*"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not downloaded_files:
        print("[download_ref] Download completed, but target file could not be located.")
        return None

    final_file = downloaded_files[0]

    # Optional trimming via FFmpeg
    if start_time or end_time:
        trimmed_file = output_dir / f"{final_file.stem}_trimmed{final_file.suffix}"
        trim_cmd = ["ffmpeg", "-y"]
        if start_time:
            trim_cmd.extend(["-ss", str(start_time)])
        trim_cmd.extend(["-i", str(final_file)])
        if end_time:
            trim_cmd.extend(["-to", str(end_time)])
        trim_cmd.extend(["-c", "copy", str(trimmed_file)])

        try:
            subprocess.run(trim_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            final_file.unlink()  # remove untrimmed
            final_file = trimmed_file
            print(f"[download_ref] Trimmed clip to window: {start_time or '00:00:00'} -> {end_time or 'end'}")
        except Exception as ex:
            print(f"[download_ref] Trimming notice: {ex}")

    print(f"[download_ref] Finished. Saved file to: {final_file}\n")
    return final_file


def main():
    parser = argparse.ArgumentParser(description="Download reference clips or audio using yt-dlp.")
    parser.add_argument("url", help="Media URL (YouTube, TikTok, Reels, etc.)")
    parser.add_argument("-o", "--output-dir", default=str(DEFAULT_REF_DIR), help="Output folder")
    parser.add_argument("-n", "--name", default=None, help="Custom output filename (without extension)")
    parser.add_argument("-s", "--start", default=None, help="Start trim time (e.g. 00:01:10)")
    parser.add_argument("-e", "--end", default=None, help="End trim time (e.g. 00:01:25)")
    parser.add_argument("--audio-only", action="store_true", help="Extract audio as WAV")
    args = parser.parse_args()

    download_media(args.url, args.output_dir, args.name, args.start, args.end, args.audio_only)


if __name__ == "__main__":
    main()
