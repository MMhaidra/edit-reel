#!/usr/bin/env python3
"""
generate_sfx_library.py - Generates studio-quality subtle ('shallow') sound effects for Instagram Reels:
1. subtle_whoosh.wav - Sleek, low-profile UI whoosh for 2D animations
2. tech_tick.wav - Crisp digital tick for numbers, metrics, and calculations
3. cash_chime.wav - High-resonance metallic coin / cash chime for money & finance
4. paper_turn.wav - Organic paper flip / turning page for academic papers & articles
5. clean_pop.wav - Gentle dampened pop for badges and alerts
"""

import math
import struct
import random
import wave
from pathlib import Path

SKILL_SFX_DIR = Path(__file__).resolve().parent.parent / "motion_library" / "sfx"
PROJECT_SFX_DIR = Path.home() / "Desktop" / "projects" / "reels_IG" / "motion_assets" / "sfx"

SKILL_SFX_DIR.mkdir(parents=True, exist_ok=True)
PROJECT_SFX_DIR.mkdir(parents=True, exist_ok=True)

SAMPLE_RATE = 44100


def write_wav(file_path, samples):
    """Writes a 16-bit mono WAV file from normalized float samples (-1.0 to 1.0)."""
    with wave.open(str(file_path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        raw_bytes = bytearray()
        for s in samples:
            val = max(-1.0, min(1.0, s))
            int_val = int(val * 32767.0)
            raw_bytes.extend(struct.pack("<h", int_val))
        wf.writeframes(raw_bytes)


def create_subtle_whoosh():
    """Generates a smooth, silky UI whoosh with low-to-high frequency sweep and smooth envelope."""
    dur = 0.28
    num_samples = int(dur * SAMPLE_RATE)
    samples = []
    
    # Pseudo-random noise seed
    rng = random.Random(42)
    noise_buffer = [rng.uniform(-1.0, 1.0) for _ in range(num_samples)]
    
    for i in range(num_samples):
        t = i / SAMPLE_RATE
        t_norm = t / dur
        
        # Smooth Bell Curve Envelope (Hanning-like)
        env = math.sin(t_norm * math.pi) ** 2.2
        
        # Center frequency sweep: starts at 180Hz, peaks at 1400Hz, drops to 220Hz
        freq = 180 + 1220 * math.sin(t_norm * math.pi)
        
        # Tone + filtered noise
        tone = math.sin(2 * math.pi * freq * t) * 0.4
        noise = noise_buffer[i] * 0.6
        
        val = (tone + noise) * env * 0.45
        samples.append(val)
        
    return samples


def create_tech_tick():
    """Generates a crisp digital / mechanical click for numbers, metrics, and calculations."""
    dur = 0.08
    num_samples = int(dur * SAMPLE_RATE)
    samples = []
    
    for i in range(num_samples):
        t = i / SAMPLE_RATE
        t_norm = t / dur
        
        # Sharp exponential decay
        env = math.exp(-t_norm * 14.0)
        
        # Dual high-frequency harmonics (3200Hz + 4800Hz)
        sig = math.sin(2 * math.pi * 3200 * t) * 0.6 + math.sin(2 * math.pi * 4800 * t) * 0.4
        
        val = sig * env * 0.40
        samples.append(val)
        
    return samples


def create_cash_chime():
    """Generates a sparkling metallic coin / cash chime (C7 + G7 + C8 resonant harmonics)."""
    dur = 0.38
    num_samples = int(dur * SAMPLE_RATE)
    samples = []
    
    # Frequencies: 2093Hz (C7), 3136Hz (G7), 4186Hz (C8)
    f1, f2, f3 = 2093.0, 3136.0, 4186.0
    
    for i in range(num_samples):
        t = i / SAMPLE_RATE
        t_norm = t / dur
        
        # Fast attack, natural metallic exponential decay
        attack = min(1.0, t / 0.005)
        decay = math.exp(-t_norm * 7.5)
        env = attack * decay
        
        sig = (
            math.sin(2 * math.pi * f1 * t) * 0.50 +
            math.sin(2 * math.pi * f2 * t) * 0.35 +
            math.sin(2 * math.pi * f3 * t) * 0.25
        )
        
        val = sig * env * 0.35
        samples.append(val)
        
    return samples


def create_paper_turn():
    """Generates an organic page flip / paper turning rustle for academic articles and citations."""
    dur = 0.26
    num_samples = int(dur * SAMPLE_RATE)
    samples = []
    
    rng = random.Random(1337)
    
    # Simulate paper flutter transients
    flutters = [
        (0.02, 0.07, 1200),
        (0.08, 0.16, 2100),
        (0.14, 0.24, 1600)
    ]
    
    for i in range(num_samples):
        t = i / SAMPLE_RATE
        val = 0.0
        
        for st, et, freq in flutters:
            if st <= t <= et:
                f_dur = et - st
                f_norm = (t - st) / f_dur
                env = math.sin(f_norm * math.pi) ** 1.8
                noise = rng.uniform(-1.0, 1.0)
                tone = math.sin(2 * math.pi * freq * t) * 0.25
                val += (noise * 0.75 + tone) * env * 0.32
                
        samples.append(val)
        
    return samples


def create_clean_pop():
    """Generates a gentle dampened UI bubble pop for badges and alerts."""
    dur = 0.06
    num_samples = int(dur * SAMPLE_RATE)
    samples = []
    
    for i in range(num_samples):
        t = i / SAMPLE_RATE
        t_norm = t / dur
        
        env = math.exp(-t_norm * 9.0)
        # Pitch drop: 620Hz down to 200Hz
        freq = 620 - 420 * (t_norm ** 0.5)
        sig = math.sin(2 * math.pi * freq * t)
        
        val = sig * env * 0.38
        samples.append(val)
        
    return samples


def generate_all():
    sfx_generators = {
        "subtle_whoosh.wav": create_subtle_whoosh,
        "tech_tick.wav": create_tech_tick,
        "cash_chime.wav": create_cash_chime,
        "paper_turn.wav": create_paper_turn,
        "clean_pop.wav": create_clean_pop
    }
    
    print(f"Generating {len(sfx_generators)} shallow sound effects...")
    for filename, gen_fn in sfx_generators.items():
        samples = gen_fn()
        skill_path = SKILL_SFX_DIR / filename
        proj_path = PROJECT_SFX_DIR / filename
        
        write_wav(skill_path, samples)
        # Mirror to project motion_assets/sfx/
        write_wav(proj_path, samples)
        print(f"  ✓ Created {filename}")
        
    print("All sound effects generated and mirrored successfully!")


if __name__ == "__main__":
    generate_all()
