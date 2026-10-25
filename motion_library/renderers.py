"""
motion_library/renderers.py - V8 Editorial Paper & Newsprint UI Engine
Learned from the Master IG Financial Reference (example.MP4):
1. Warm Textured Editorial Newsprint Canvas (#E2DDD1 / #E0D9C7, alpha=255):
   - Fine organic paper grain texture giving authentic Wall Street Journal / Financial Times credibility
   - Zero digital harshness, zero murky obsidian, 100% opaque solid background
2. Editorial Print Cards & Badges:
   - Crisp off-white card surface (#FDFBF7) with fine dark ink borders (#2D2A26)
   - Deep Ink Black typography (#1A1A1A) for 100% razor-sharp contrast and readability
   - Muted Warm Slate descriptions (#5A544E)
3. High-Credibility Financial & Brand Accents:
   - Forest Green (#00704A): Happiness, Wealth, Growth, Costa Rica
   - Crimson / Brick Red (#C53030): Risks, Hedonic Treadmill, Bottom 20% Flatline
   - Ochre Gold (#D4AF37): Autonomy, Utility Multipliers, Key Highlights
   - Royal Cobalt (#2563EB): PNAS 2023 Study Citations, Math Laws
4. Snappy Physics & Clean Alignment:
   - Cubic-bezier curves, zero text collisions, generous margins
"""

import math
import os
import re
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
import numpy as np

try:
    import arabic_reshaper
    from bidi.algorithm import get_display
    HAS_ARABIC_SHAPER = True
except ImportError:
    HAS_ARABIC_SHAPER = False


def find_broll_asset(filename):
    candidates = [
        Path.home() / "Desktop" / "projects" / "reels_IG" / "motion_assets" / "broll" / filename,
        Path(__file__).resolve().parent / "broll" / filename,
    ]
    for c in candidates:
        if c.exists():
            return c
    return None


def shape_text(text):
    if not text:
        return ""
    s = str(text)
    if HAS_ARABIC_SHAPER and re.search(r"[\u0600-\u06FF]", s):
        try:
            return get_display(arabic_reshaper.reshape(s))
        except Exception:
            return s
    return s


# ---------------------------------------------------------------------------
# V8 Editorial Newsprint Palette (Inspired by example.MP4)
# ---------------------------------------------------------------------------
PAPER_BASE = (226, 221, 209, 255)     # #E2DDD1 Warm Newsprint Paper
CARD_OFFWHITE = (253, 251, 247, 255)  # #FDFBF7 Crisp Print Card
BORDER_INK = (45, 42, 38, 255)        # #2D2A26 Fine Ink Border (1.5px)
BORDER_FAINT = (205, 199, 187, 255)   # #CDC7BB Hairline Grid Border

INK_BLACK = (26, 26, 26, 255)         # #1A1A1A Primary Deep Ink Headlines
WARM_SLATE = (90, 84, 78, 255)        # #5A544E Secondary Body Text & Authors
FAINT_INK = (145, 138, 130, 255)      # #918A82 Sub-captions & Micro-headers

# High-Credibility Financial & Brand Accents
FOREST_GREEN = (0, 112, 74, 255)      # #00704A Starbucks / Wealth / Costa Rica
CRIMSON_RED = (197, 48, 48, 255)      # #C53030 Chipotle / Hedonic / Risk / Warning
OCHRE_GOLD = (212, 175, 55, 255)      # #D4AF37 Premium / Multipliers / Autonomy
ROYAL_COBALT = (37, 99, 235, 255)     # #2563EB PNAS Study / Technical Math
PILL_BG_LIGHT = (244, 240, 232, 255)  # #F4F0E8 Soft Paper Pill Background

# Aliases for backward compatibility
LIGHT_CANVAS = PAPER_BASE
CARD_WHITE = CARD_OFFWHITE
BORDER_SUBTLE = BORDER_INK
MIDNIGHT_NAVY = INK_BLACK
DEEP_SLATE = INK_BLACK
MUTED_SLATE = WARM_SLATE
FAINT_SLATE = FAINT_INK
COBALT_ACCENT = ROYAL_COBALT
EMERALD_ACCENT = FOREST_GREEN
RADIANT_EMERALD = FOREST_GREEN
AMBER_ACCENT = OCHRE_GOLD
WARM_AMBER = OCHRE_GOLD
WARM_GOLD_POP = OCHRE_GOLD
CORAL_ACCENT = CRIMSON_RED
CORAL_CRIMSON = CRIMSON_RED
ELECTRIC_ROSE = CRIMSON_RED
SKY_CYAN = ROYAL_COBALT
SKY_CYAN_POP = ROYAL_COBALT
NEON_CYAN = ROYAL_COBALT
DEEP_NAVY = INK_BLACK
PURE_WHITE = CARD_OFFWHITE


# ---------------------------------------------------------------------------
# Pre-Baked Organic Paper Grain Texture Cache
# ---------------------------------------------------------------------------
_PAPER_TEXTURE_CACHE = {}

def _create_paper_texture(width=1080, height=920):
    base_col = np.array([226, 221, 209], dtype=np.float32)
    np.random.seed(42)
    noise = np.random.normal(0, 4.2, (height, width, 3)).astype(np.float32)
    img_arr = np.clip(base_col + noise, 0, 255).astype(np.uint8)
    alpha = np.full((height, width, 1), 255, dtype=np.uint8)
    rgba = np.concatenate([img_arr, alpha], axis=2)
    im = Image.fromarray(rgba)
    draw = ImageDraw.Draw(im)
    # Refined top ink filament
    draw.line([(0, 0), (width, 0)], fill=BORDER_INK, width=3)
    return im


def get_editorial_background(width=1080, height=920):
    """
    100% Solid Warm Textured Newsprint Paper Canvas (#E2DDD1, alpha=255).
    Guarantees zero bleed-through from the speaker video underneath.
    """
    key = (width, height)
    if key not in _PAPER_TEXTURE_CACHE:
        _PAPER_TEXTURE_CACHE[key] = _create_paper_texture(width, height)
    return _PAPER_TEXTURE_CACHE[key].copy()


def get_cinematic_dark_background(width=1080, height=920):
    return get_editorial_background(width, height)


# ---------------------------------------------------------------------------
# Physics Easing Engine: Apple Cubic Bezier & Spring Dynamics
# ---------------------------------------------------------------------------

def make_cubic_bezier(x1=0.16, y1=1.0, x2=0.3, y2=1.0):
    def bezier_at(t):
        if t <= 0.0: return 0.0
        if t >= 1.0: return 1.0
        u = t
        for _ in range(8):
            one_minus_u = 1.0 - u
            bx = 3 * one_minus_u**2 * u * x1 + 3 * one_minus_u * u**2 * x2 + u**3
            diff = bx - t
            if abs(diff) < 1e-5: break
            dbx = 3 * one_minus_u**2 * x1 + 6 * one_minus_u * u * (x2 - x1) + 3 * u**2 * (1.0 - x2)
            if abs(dbx) < 1e-6: break
            u = max(0.0, min(1.0, u - diff / dbx))
        one_minus_u = 1.0 - u
        return 3 * one_minus_u**2 * u * y1 + 3 * one_minus_u * u**2 * y2 + u**3
    return bezier_at

ease_apple = make_cubic_bezier(0.16, 1.0, 0.3, 1.0)


def get_item_physics(t_norm, cue_duration=10.0, stagger_sec=0.0, entry_dur=0.36, exit_dur=0.18):
    elapsed = max(0.0, t_norm * cue_duration)
    t_sec = elapsed - stagger_sec
    if t_sec < 0.0:
        return 0.0, 24, 0.0  # not visible yet

    # Snappy Entrance
    if t_sec < entry_dur:
        u = t_sec / entry_dur
        p = ease_apple(u)
        scale = 0.94 + 0.06 * p
        dy = int(20 * (1.0 - p))
        opacity = min(1.0, p * 1.3)
    else:
        scale = 1.0
        dy = 0
        opacity = 1.0

    # Smooth Glide-out in final exit window
    time_left = cue_duration - elapsed
    if 0 < time_left < exit_dur:
        exit_p = time_left / exit_dur
        dy -= int(14 * (1.0 - exit_p))
        opacity *= (exit_p ** 1.3)
    elif time_left <= 0:
        opacity = 0.0

    return scale, dy, opacity


def _text_w(font, text):
    if not font or not text: return 0
    bbox = font.getbbox(shape_text(text))
    return bbox[2] - bbox[0]


def _text_h(font, text="Ag"):
    if not font: return 24
    bbox = font.getbbox(shape_text(text))
    return bbox[3] - bbox[1]


def _draw_modern_pill(draw, x1, y1, text, font, fill=CARD_OFFWHITE, text_col=INK_BLACK, border_col=BORDER_INK, pad_x=16, pad_y=6, dot_col=None):
    clean_txt = str(text).strip()
    disp = shape_text(clean_txt)
    bbox = font.getbbox(disp)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    dot_space = 18 if dot_col else 0
    w = tw + pad_x * 2 + dot_space
    h = th + pad_y * 2

    # Soft ambient pill shadow
    draw.rounded_rectangle([x1 + 1, y1 + 2, x1 + w + 1, y1 + h + 2], radius=h // 2, fill=(45, 38, 30, 20))
    # Pill body
    draw.rounded_rectangle([x1, y1, x1 + w, y1 + h], radius=h // 2, fill=fill, outline=border_col, width=1)

    if dot_col:
        r = 4
        cx = x1 + pad_x + r
        cy = y1 + h // 2
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=dot_col)
        draw.text((x1 + pad_x + dot_space, y1 + pad_y), disp, font=font, fill=text_col)
    else:
        draw.text((x1 + pad_x, y1 + pad_y), disp, font=font, fill=text_col)

    return x1 + w, y1 + h


def _draw_modern_light_card(img, box, radius=20, fill=CARD_OFFWHITE, border_col=BORDER_INK, rot_deg=0.0, shadow_blur=14):
    """
    Renders an editorial print paper card:
    - Crisp off-white card surface (#FDFBF7)
    - Fine dark ink border (#2D2A26)
    - Soft, diffuse warm ambient drop shadow
    - Optional organic micro-rotation
    """
    x1, y1, x2, y2 = box
    cw = max(10, x2 - x1)
    ch = max(10, y2 - y1)
    pad = 32
    im_w = cw + pad * 2
    im_h = ch + pad * 2

    card_surf = Image.new("RGBA", (im_w, im_h), (0, 0, 0, 0))

    # 1. Warm ambient diffusion shadow
    shadow = Image.new("RGBA", (im_w, im_h), (0, 0, 0, 0))
    sdraw = ImageDraw.Draw(shadow)
    sdraw.rounded_rectangle([pad + 1, pad + 6, pad + cw + 1, pad + ch + 6], radius=radius, fill=(45, 38, 30, 24))
    shadow_blurred = shadow.filter(ImageFilter.GaussianBlur(shadow_blur))
    card_surf.paste(shadow_blurred, (0, 0), shadow_blurred)

    # 2. Crisp Print Card Body
    body = Image.new("RGBA", (im_w, im_h), (0, 0, 0, 0))
    bdraw = ImageDraw.Draw(body)
    bdraw.rounded_rectangle([pad, pad, pad + cw, pad + ch], radius=radius, fill=fill, outline=border_col, width=1)
    card_surf = Image.alpha_composite(card_surf, body)

    # 3. Organic micro-rotation if requested
    if abs(rot_deg) > 0.05:
        card_surf = card_surf.rotate(rot_deg, resample=Image.Resampling.BICUBIC, expand=True)
        nw, nh = card_surf.size
        px = x1 - (nw - cw) // 2
        py = y1 - (nh - ch) // 2
        img.paste(card_surf, (px, py), card_surf)
    else:
        img.paste(card_surf, (x1 - pad, y1 - pad), card_surf)


def _draw_liquid_glass_card(img, box, radius=20, fill=CARD_OFFWHITE, border_col=BORDER_INK, rot_deg=0.0, shadow_blur=14, specular=False):
    _draw_modern_light_card(img, box, radius=radius, fill=fill, border_col=border_col, rot_deg=rot_deg, shadow_blur=shadow_blur)


def draw_wrapped_text(draw, text, font, fill, x, y, max_w, line_spacing=6, is_arabic=False, shadow=False):
    if not text:
        return y
    words = str(text).split(" ")
    lines = []
    cur_line = []
    cur_w = 0
    space_w = _text_w(font, " ")

    for w in words:
        ww = _text_w(font, w)
        if cur_line and (cur_w + space_w + ww > max_w):
            lines.append(" ".join(cur_line))
            cur_line = [w]
            cur_w = ww
        else:
            cur_line.append(w)
            cur_w += (space_w if len(cur_line) > 1 else 0) + ww
    if cur_line:
        lines.append(" ".join(cur_line))

    th = _text_h(font, "Ag")
    cur_y = y
    for line in lines:
        disp = shape_text(line)
        lw = _text_w(font, line)
        lx = (x + max_w - lw) if is_arabic else x

        if shadow:
            draw.text((lx + 1, cur_y + 1), disp, font=font, fill=(0, 0, 0, 20))
        draw.text((lx, cur_y), disp, font=font, fill=fill)
        cur_y += th + line_spacing

    return cur_y


def draw_editorial_header(draw, t_norm, f_idx, cue, fonts, width=1080, y_start=28, is_arabic=False):
    kicker = str(cue.get("kicker") or cue.get("badge") or "EMPIRICAL RESEARCH STUDY")
    headline = str(cue.get("headline") or cue.get("title") or "Key Research Finding")

    f_kicker = fonts.get("pill", fonts.get("badge"))
    f_head = fonts.get("hero_title", fonts.get("headline"))

    margin_x = 54
    cur_y = y_start

    _draw_modern_pill(
        draw, margin_x, cur_y, kicker, f_kicker,
        fill=CARD_OFFWHITE, text_col=ROYAL_COBALT, dot_col=ROYAL_COBALT
    )
    cur_y += 46

    clean_head = headline.strip()
    if clean_head.endswith("."): clean_head = clean_head[:-1]

    cur_y = draw_wrapped_text(draw, clean_head, f_head, INK_BLACK, margin_x, cur_y, width - 2 * margin_x, is_arabic=is_arabic)
    return cur_y + 14


# ---------------------------------------------------------------------------
# Template 1: Threshold Counter ($75K Myth Disproven -> $500,000+ Rising)
# ---------------------------------------------------------------------------

def render_threshold_counter(draw, t_norm, f_idx, cue, fonts, width=1080, height=920, is_arabic=False, img=None):
    dur = float(cue.get("duration", 10.0))
    scale, dy, opacity = get_item_physics(t_norm, cue_duration=dur, stagger_sec=0.0)
    if opacity <= 0.001: return

    margin_x = 54
    max_w = width - 2 * margin_x
    cur_y = 28 + dy

    # Header Capsule
    _draw_modern_pill(draw, margin_x, cur_y, "EMPIRICAL RE-EVALUATION // 2010 VS. 2023 PNAS", fonts.get("pill"), fill=CARD_OFFWHITE, text_col=ROYAL_COBALT, dot_col=ROYAL_COBALT)
    cur_y += 46
    cur_y = draw_wrapped_text(draw, "BEYOND THE $75,000 MYTH", fonts.get("hero_title", fonts.get("title")), INK_BLACK, margin_x, cur_y, max_w, is_arabic=is_arabic)
    cur_y += 18

    # Card 1: 2010 Strikethrough Benchmark (Old Myth)
    c1_h = 130
    if img is not None:
        _draw_modern_light_card(img, [margin_x, cur_y, width - margin_x, cur_y + c1_h], radius=18, fill=CARD_OFFWHITE, rot_deg=-0.6)
    draw = ImageDraw.Draw(img)

    _draw_modern_pill(draw, margin_x + 20, cur_y + 14, "OLD 2010 BELIEF // KAHNEMAN & DEATON", fonts.get("citation_sub"), fill=PILL_BG_LIGHT, text_col=WARM_SLATE, dot_col=CRIMSON_RED)
    st_text = "$75,000 HAPPINESS PLATEAU (DISPROVEN)"
    draw.text((margin_x + 20, cur_y + 52), shape_text(st_text), font=fonts.get("card_title"), fill=WARM_SLATE)
    st_w = _text_w(fonts.get("card_title"), st_text)
    draw.line([(margin_x + 20, cur_y + 66), (margin_x + 20 + min(st_w, max_w - 40), cur_y + 66)], fill=CRIMSON_RED, width=3)
    draw_wrapped_text(draw, "Believed emotional well-being stopped rising past $75,000.", fonts.get("citation_sub"), FAINT_INK, margin_x + 20, cur_y + 86, max_w - 40, is_arabic=is_arabic)
    cur_y += c1_h + 18

    # Card 2: 2023 Discovery Animated Spring Counter
    sc2, dy2, op2 = get_item_physics(t_norm, cue_duration=dur, stagger_sec=0.10)
    c2_h = 280
    if img is not None and op2 > 0:
        _draw_modern_light_card(img, [margin_x, cur_y, width - margin_x, cur_y + c2_h], radius=20, fill=CARD_OFFWHITE, border_col=BORDER_INK, rot_deg=0.6)
    draw = ImageDraw.Draw(img)

    _draw_modern_pill(draw, margin_x + 20, cur_y + 16, "2023 PNAS DISCOVERY // RESOLUTION", fonts.get("pill"), fill=(236, 253, 245, 255), text_col=FOREST_GREEN, dot_col=FOREST_GREEN)

    anim_p = ease_apple(min(1.0, max(0.0, (t_norm * dur - 0.12) / 2.6)))
    val = int(75000 + (500000 - 75000) * anim_p)
    counter_str = f"${val:,}"
    f_stat = fonts.get("giant_num", fonts.get("hero_stat"))

    draw.text((margin_x + 20, cur_y + 60), counter_str, font=f_stat, fill=FOREST_GREEN)

    bar_w = max_w - 40
    draw.rounded_rectangle([margin_x + 20, cur_y + 148, margin_x + 20 + bar_w, cur_y + 158], radius=5, fill=(230, 224, 214, 255))
    fill_w = int(bar_w * max(0.08, anim_p))
    draw.rounded_rectangle([margin_x + 20, cur_y + 148, margin_x + 20 + fill_w, cur_y + 158], radius=5, fill=FOREST_GREEN)

    draw_wrapped_text(draw, "- For the happiest 80%, well-being continues climbing past $500,000.", fonts.get("card_title"), INK_BLACK, margin_x + 20, cur_y + 175, max_w - 40, is_arabic=is_arabic)
    draw_wrapped_text(draw, "- Real-time smartphone sampling of 33,391 US working adults in daily life.", fonts.get("citation_sub"), WARM_SLATE, margin_x + 20, cur_y + 225, max_w - 40, is_arabic=is_arabic)
    cur_y += c2_h + 18

    # Card 3: The Critical Caveat (Unhappiest 20%)
    sc3, dy3, op3 = get_item_physics(t_norm, cue_duration=dur, stagger_sec=0.20)
    c3_h = 160
    if img is not None and op3 > 0:
        _draw_modern_light_card(img, [margin_x, cur_y, width - margin_x, cur_y + c3_h], radius=18, fill=CARD_OFFWHITE, border_col=BORDER_INK, rot_deg=-0.4)
    draw = ImageDraw.Draw(img)

    _draw_modern_pill(draw, margin_x + 20, cur_y + 14, "THE CRITICAL CAVEAT", fonts.get("citation_sub"), fill=(255, 251, 235, 255), text_col=OCHRE_GOLD, dot_col=OCHRE_GOLD)
    draw_wrapped_text(draw, "Money buys happiness only if you aren't already unhappy.", fonts.get("card_title"), INK_BLACK, margin_x + 20, cur_y + 52, max_w - 40, is_arabic=is_arabic)
    draw_wrapped_text(draw, "- For the unhappiest 20%, more income flatlines at $100,000.", fonts.get("citation_sub"), CRIMSON_RED, margin_x + 20, cur_y + 96, max_w - 40, is_arabic=is_arabic)


# ---------------------------------------------------------------------------
# Template 2: Study Citation (Kahneman & Killingsworth 2023 PNAS Paper)
# ---------------------------------------------------------------------------

def render_study_citation(draw, t_norm, f_idx, cue, fonts, width=1080, height=920, is_arabic=False, img=None):
    dur = float(cue.get("duration", 10.0))
    scale, dy, opacity = get_item_physics(t_norm, cue_duration=dur, stagger_sec=0.0)
    if opacity <= 0.001: return

    margin_x = 54
    max_w = width - 2 * margin_x
    cur_y = 28 + dy

    # Header
    _draw_modern_pill(draw, margin_x, cur_y, "PNAS RESEARCH // MARCH 2023", fonts.get("pill"), fill=CARD_OFFWHITE, text_col=ROYAL_COBALT, dot_col=ROYAL_COBALT)
    cur_y += 46
    cur_y = draw_wrapped_text(draw, "KAHNEMAN & KILLINGSWORTH (2023)", fonts.get("hero_title", fonts.get("title")), INK_BLACK, margin_x, cur_y, max_w, is_arabic=is_arabic)
    cur_y += 8
    cur_y = draw_wrapped_text(draw, "Adversarial Collaboration to Resolve the $75,000 Plateau", fonts.get("card_title"), WARM_SLATE, margin_x, cur_y, max_w, is_arabic=is_arabic)
    cur_y += 18

    # Main Paper Plaque
    p_h = 160
    if img is not None:
        _draw_modern_light_card(img, [margin_x, cur_y, width - margin_x, cur_y + p_h], radius=20, fill=CARD_OFFWHITE, border_col=BORDER_INK, rot_deg=0.6)
    draw = ImageDraw.Draw(img)

    paper_title = "\"Income and emotional well-being: A conflict resolved\""
    draw_wrapped_text(draw, paper_title, fonts.get("title", fonts.get("headline")), INK_BLACK, margin_x + 20, cur_y + 18, max_w - 40, is_arabic=is_arabic)
    _draw_modern_pill(draw, margin_x + 20, cur_y + 88, "AUTHORS: Daniel Kahneman (Nobel Laureate) & Matthew Killingsworth (Penn)", fonts.get("citation_sub"), fill=PILL_BG_LIGHT, text_col=ROYAL_COBALT, dot_col=ROYAL_COBALT)
    cur_y += p_h + 18

    # Dual Floating Metric Chips (Side-by-Side)
    sc2, dy2, op2 = get_item_physics(t_norm, cue_duration=dur, stagger_sec=0.10)
    col_w = (max_w - 20) // 2
    c_h = 160

    if img is not None and op2 > 0:
        _draw_modern_light_card(img, [margin_x, cur_y, margin_x + col_w, cur_y + c_h], radius=18, fill=CARD_OFFWHITE, border_col=BORDER_INK, rot_deg=-0.6)
        rx = margin_x + col_w + 20
        _draw_modern_light_card(img, [rx, cur_y, width - margin_x, cur_y + c_h], radius=18, fill=CARD_OFFWHITE, border_col=BORDER_INK, rot_deg=0.6)
    draw = ImageDraw.Draw(img)

    # Left Stat
    draw.text((margin_x + 20, cur_y + 18), "1,725,994", font=fonts.get("hero_stat"), fill=ROYAL_COBALT)
    draw.text((margin_x + 20, cur_y + 86), "REAL-TIME CHECK-INS", font=fonts.get("label"), fill=INK_BLACK)
    draw.text((margin_x + 20, cur_y + 118), "Track Your Happiness App", font=fonts.get("citation_sub"), fill=WARM_SLATE)

    # Right Stat
    rx = margin_x + col_w + 20
    draw.text((rx + 20, cur_y + 18), "33,391", font=fonts.get("hero_stat"), fill=FOREST_GREEN)
    draw.text((rx + 20, cur_y + 86), "US WORKING ADULTS", font=fonts.get("label"), fill=INK_BLACK)
    draw.text((rx + 20, cur_y + 118), "Diverse Socioeconomic Cohort", font=fonts.get("citation_sub"), fill=WARM_SLATE)
    cur_y += c_h + 18

    # Key Finding Capsule
    sc3, dy3, op3 = get_item_physics(t_norm, cue_duration=dur, stagger_sec=0.18)
    f_h = 165
    if img is not None and op3 > 0:
        _draw_modern_light_card(img, [margin_x, cur_y, width - margin_x, cur_y + f_h], radius=20, fill=CARD_OFFWHITE, border_col=BORDER_INK, rot_deg=-0.4)
    draw = ImageDraw.Draw(img)

    _draw_modern_pill(draw, margin_x + 20, cur_y + 14, "CORE EMPIRICAL FINDING", fonts.get("citation_sub"), fill=(239, 246, 255, 255), text_col=ROYAL_COBALT, dot_col=ROYAL_COBALT)
    draw_wrapped_text(draw, "Happiness keeps rising past $500,000 for 80% of people.", fonts.get("card_title"), INK_BLACK, margin_x + 20, cur_y + 54, max_w - 40, is_arabic=is_arabic)
    draw_wrapped_text(draw, "- Real-time sampling eliminated retrospective memory bias.", fonts.get("citation_sub"), WARM_SLATE, margin_x + 20, cur_y + 98, max_w - 40, is_arabic=is_arabic)


# ---------------------------------------------------------------------------
# Template 3: Logarithmic Income Curve (Equal Doublings for Equal Happiness)
# ---------------------------------------------------------------------------

def render_log_income_curve(draw, t_norm, f_idx, cue, fonts, width=1080, height=920, is_arabic=False, img=None):
    dur = float(cue.get("duration", 10.0))
    scale, dy, opacity = get_item_physics(t_norm, cue_duration=dur, stagger_sec=0.0)
    if opacity <= 0.001: return

    margin_x = 54
    max_w = width - 2 * margin_x
    cur_y = 28 + dy

    # Header
    _draw_modern_pill(draw, margin_x, cur_y, "MATHEMATICAL UTILITY LAW // PNAS 2023", fonts.get("pill"), fill=CARD_OFFWHITE, text_col=ROYAL_COBALT, dot_col=ROYAL_COBALT)
    cur_y += 46
    cur_y = draw_wrapped_text(draw, "THE LAW OF LOGARITHMIC WEALTH", fonts.get("hero_title", fonts.get("title")), INK_BLACK, margin_x, cur_y, max_w, is_arabic=is_arabic)
    cur_y += 8
    cur_y = draw_wrapped_text(draw, "Happiness = Log(Income) // Equal Doublings for Equal Joy", fonts.get("card_title"), ROYAL_COBALT, margin_x, cur_y, max_w, is_arabic=is_arabic)
    cur_y += 18

    # Modern Coordinate Chart Card
    chart_h = 440
    if img is not None:
        _draw_modern_light_card(img, [margin_x, cur_y, width - margin_x, cur_y + chart_h], radius=20, fill=CARD_OFFWHITE, border_col=BORDER_INK, rot_deg=-0.5)
    draw = ImageDraw.Draw(img)

    cx1 = margin_x + 40
    cx2 = width - margin_x - 40
    cw = cx2 - cx1
    cy_top = cur_y + 40
    cy_bot = cur_y + chart_h - 60
    ch = cy_bot - cy_top

    # Subtle horizontal grid lines
    for step in range(5):
        gy = cy_bot - int(step * ch / 4.0)
        draw.line([(cx1, gy), (cx2, gy)], fill=BORDER_FAINT, width=1)
        if step > 0:
            draw.text((cx1 + 8, gy - 20), f"Level {step}: Equal Happiness Gain (+1.0)", font=fonts.get("citation_sub"), fill=FAINT_INK)

    # Linear myth line (gray dotted)
    draw.line([(cx1, cy_bot), (cx1 + int(cw * 0.60), cy_top + 20)], fill=(185, 178, 166, 255), width=2)
    draw.text((cx1 + int(cw * 0.60) - 110, cy_top + 4), "LINEAR MYTH", font=fonts.get("citation_sub"), fill=FAINT_INK)

    # Spring animated glowing log curve
    anim_p = ease_apple(min(1.0, max(0.0, (t_norm * dur - 0.10) / 2.6)))
    pts = []
    num_samples = 70
    max_idx = max(2, int(num_samples * anim_p))
    for i in range(max_idx):
        u = i / float(num_samples - 1)
        px = cx1 + int(u * cw)
        log_val = math.log1p(u * 15.0) / math.log1p(15.0)
        py = cy_bot - int(log_val * (ch - 24))
        pts.append((px, py))

    if len(pts) > 1:
        draw.line(pts, fill=(219, 234, 254, 255), width=10)
        draw.line(pts, fill=ROYAL_COBALT, width=4)

    milestones = [
        (0.04, "$50K", "1x"),
        (0.18, "$100K", "2x"),
        (0.38, "$200K", "4x"),
        (0.64, "$400K", "8x"),
        (0.94, "$800K", "16x")
    ]
    for frac, label, mult in milestones:
        if anim_p >= frac * 0.85:
            mx = cx1 + int(frac * cw)
            log_val = math.log1p(frac * 15.0) / math.log1p(15.0)
            my = cy_bot - int(log_val * (ch - 24))
            draw.line([(mx, my), (mx, cy_bot)], fill=BORDER_FAINT, width=1)
            draw.ellipse([mx - 6, my - 6, mx + 6, my + 6], fill=ROYAL_COBALT, outline=CARD_OFFWHITE, width=2)
            lw = _text_w(fonts.get("card_title"), label)
            draw.text((mx - lw // 2, cy_bot + 10), label, font=fonts.get("card_title"), fill=INK_BLACK)
            if frac > 0.1:
                _draw_modern_pill(draw, mx - 24, my - 34, mult, fonts.get("citation_sub"), fill=CARD_OFFWHITE, text_col=ROYAL_COBALT, pad_x=8, pad_y=3)

    cur_y += chart_h + 18

    # Bottom Reality Check Card
    sc2, dy2, op2 = get_item_physics(t_norm, cue_duration=dur, stagger_sec=0.14)
    r_h = 160
    if img is not None and op2 > 0:
        _draw_modern_light_card(img, [margin_x, cur_y, width - margin_x, cur_y + r_h], radius=18, fill=CARD_OFFWHITE, border_col=BORDER_INK, rot_deg=0.5)
    draw = ImageDraw.Draw(img)

    _draw_modern_pill(draw, margin_x + 20, cur_y + 14, "THE EXPONENTIAL EFFORT TAX", fonts.get("citation_sub"), fill=(255, 251, 235, 255), text_col=OCHRE_GOLD, dot_col=OCHRE_GOLD)
    draw_wrapped_text(draw, "Going from $50K to $100K gives the EXACT same happiness boost as $400K to $800K.", fonts.get("card_title"), INK_BLACK, margin_x + 20, cur_y + 52, max_w - 40, is_arabic=is_arabic)
    draw_wrapped_text(draw, "- Each incremental unit of happiness costs 2x more income than before.", fonts.get("citation_sub"), WARM_SLATE, margin_x + 20, cur_y + 98, max_w - 40, is_arabic=is_arabic)


# ---------------------------------------------------------------------------
# Template 4: Correlation r = 0.09 & Unhappiest 20% Flatline
# ---------------------------------------------------------------------------

def render_correlation_split(draw, t_norm, f_idx, cue, fonts, width=1080, height=920, is_arabic=False, img=None):
    dur = float(cue.get("duration", 10.0))
    scale, dy, opacity = get_item_physics(t_norm, cue_duration=dur, stagger_sec=0.0)
    if opacity <= 0.001: return

    margin_x = 54
    max_w = width - 2 * margin_x
    cur_y = 28 + dy

    # Header
    _draw_modern_pill(draw, margin_x, cur_y, "STATISTICAL EFFECT SIZE // PNAS 2023", fonts.get("pill"), fill=CARD_OFFWHITE, text_col=OCHRE_GOLD, dot_col=OCHRE_GOLD)
    cur_y += 46
    cur_y = draw_wrapped_text(draw, "A SURPRISINGLY WEAK CORRELATION", fonts.get("hero_title", fonts.get("title")), INK_BLACK, margin_x, cur_y, max_w, is_arabic=is_arabic)
    cur_y += 18

    # Giant Stat Card
    s_h = 160
    if img is not None:
        _draw_modern_light_card(img, [margin_x, cur_y, width - margin_x, cur_y + s_h], radius=20, fill=CARD_OFFWHITE, border_col=BORDER_INK, rot_deg=0.6)
    draw = ImageDraw.Draw(img)

    anim_p = ease_apple(min(1.0, max(0.0, (t_norm * dur - 0.08) / 2.2)))
    r_val = 0.09 * min(1.0, anim_p * 1.3)
    stat_str = f"r = {r_val:.2f}"
    f_stat = fonts.get("giant_num", fonts.get("hero_stat"))

    draw.text((margin_x + 20, cur_y + 14), stat_str, font=f_stat, fill=ROYAL_COBALT)
    draw.text((margin_x + 20, cur_y + 90), "CORRELATION COEFFICIENT // EXPLAINS < 1% OF DAILY HAPPINESS", font=fonts.get("label"), fill=INK_BLACK)
    draw.text((margin_x + 20, cur_y + 120), "Killingsworth & Kahneman (2023) • N = 33,391 US Adults", font=fonts.get("citation_sub"), fill=WARM_SLATE)
    cur_y += s_h + 18

    # Dual Path Divergence Chart Card (80% vs 20%)
    sc2, dy2, op2 = get_item_physics(t_norm, cue_duration=dur, stagger_sec=0.10)
    ch_h = 300
    if img is not None and op2 > 0:
        _draw_modern_light_card(img, [margin_x, cur_y, width - margin_x, cur_y + ch_h], radius=20, fill=CARD_OFFWHITE, border_col=BORDER_INK, rot_deg=-0.5)
    draw = ImageDraw.Draw(img)

    cx1 = margin_x + 40
    cx2 = width - margin_x - 40
    cw = cx2 - cx1
    cy_base = cur_y + ch_h - 50
    ch = 180

    pts_80 = []
    pts_20 = []
    num_pts = 60
    max_idx = max(2, int(num_pts * anim_p))
    for i in range(max_idx):
        u = i / float(num_pts - 1)
        px = cx1 + int(u * cw)
        py80 = cy_base - int((0.20 + 0.70 * u) * ch)
        pts_80.append((px, py80))

        u_clamp = min(0.32, u)
        py20 = cy_base - int((0.15 + 0.35 * (u_clamp / 0.32)) * ch)
        pts_20.append((px, py20))

    if len(pts_80) > 1:
        draw.line(pts_80, fill=(209, 250, 229, 255), width=10)
        draw.line(pts_80, fill=FOREST_GREEN, width=4)
        draw.text((margin_x + 40, cur_y + 20), "HAPPIEST 80%: RISES TO $500,000+", font=fonts.get("label"), fill=FOREST_GREEN)

    if len(pts_20) > 1:
        draw.line(pts_20, fill=(255, 228, 230, 255), width=10)
        draw.line(pts_20, fill=CRIMSON_RED, width=4)
        draw.text((margin_x + 40, cur_y + ch_h - 90), "UNHAPPIEST 20%: FLATLINES AT $100,000", font=fonts.get("label"), fill=CRIMSON_RED)

    cur_y += ch_h + 18

    # Bottom Synthesis Card
    sc3, dy3, op3 = get_item_physics(t_norm, cue_duration=dur, stagger_sec=0.18)
    b_h = 160
    if img is not None and op3 > 0:
        _draw_modern_light_card(img, [margin_x, cur_y, width - margin_x, cur_y + b_h], radius=18, fill=CARD_OFFWHITE, border_col=BORDER_INK, rot_deg=0.4)
    draw = ImageDraw.Draw(img)

    _draw_modern_pill(draw, margin_x + 20, cur_y + 14, "THE PSYCHOLOGICAL WEALTH RULE", fonts.get("citation_sub"), fill=(255, 251, 235, 255), text_col=OCHRE_GOLD, dot_col=OCHRE_GOLD)
    draw_wrapped_text(draw, "Money is a weak tool for creating joy, but a powerful tool for eliminating misery.", fonts.get("card_title"), INK_BLACK, margin_x + 20, cur_y + 52, max_w - 40, is_arabic=is_arabic)
    draw_wrapped_text(draw, "- If you are fundamentally miserable, more money stops helping above $100K.", fonts.get("citation_sub"), WARM_SLATE, margin_x + 20, cur_y + 98, max_w - 40, is_arabic=is_arabic)


# ---------------------------------------------------------------------------
# Template 5: World Happiness Report (Costa Rica vs. Live Singapore Moving Video)
# ---------------------------------------------------------------------------

def render_country_comparison(draw, t_norm, f_idx, cue, fonts, width=1080, height=920, is_arabic=False, img=None):
    dur = float(cue.get("duration", 10.0))
    scale, dy, opacity = get_item_physics(t_norm, cue_duration=dur, stagger_sec=0.0)
    if opacity <= 0.001: return

    margin_x = 54
    card_w = width - 2 * margin_x
    v_h = 360
    f_stat = fonts.get("hero_stat", fonts.get("giant_num"))

    # Top Viewport: Costa Rica
    top_y = 28 + dy
    if img is not None:
        _draw_modern_light_card(img, [margin_x, top_y, margin_x + card_w, top_y + v_h], radius=20, fill=CARD_OFFWHITE, border_col=BORDER_INK, rot_deg=-0.6)
    draw = ImageDraw.Draw(img)

    _draw_modern_pill(draw, margin_x + 20, top_y + 16, "RANK #4 WORLD HAPPINESS // OXFORD & GALLUP", fonts.get("pill"), fill=(236, 253, 245, 255), text_col=FOREST_GREEN, dot_col=FOREST_GREEN)
    draw.text((margin_x + 20, top_y + 60), "COSTA RICA", font=fonts.get("hero_title", fonts.get("title")), fill=INK_BLACK)

    draw.text((margin_x + 20, top_y + 116), "~$16,000", font=f_stat, fill=FOREST_GREEN)
    draw.text((margin_x + 20, top_y + 190), "ANNUAL GDP PER CAPITA", font=fonts.get("kicker"), fill=WARM_SLATE)

    tx1, ty1 = _draw_modern_pill(draw, margin_x + 20, top_y + 232, "TIME AFFLUENCE", fonts.get("pill"), fill=PILL_BG_LIGHT, text_col=INK_BLACK, dot_col=FOREST_GREEN)
    _draw_modern_pill(draw, tx1 + 12, top_y + 232, "SOCIAL TRUST", fonts.get("pill"), fill=PILL_BG_LIGHT, text_col=INK_BLACK, dot_col=FOREST_GREEN)
    draw_wrapped_text(draw, "- Outranks Richest Nations in Life Satisfaction and Longevity", fonts.get("citation_sub"), WARM_SLATE, margin_x + 20, top_y + 296, card_w - 40, is_arabic=is_arabic)

    # Center Floating Divider
    div_w, div_h = 320, 44
    div_x1 = (width - div_w) // 2
    div_y1 = top_y + v_h + 16
    draw.rounded_rectangle([div_x1, div_y1, div_x1 + div_w, div_y1 + div_h], radius=div_h // 2, fill=CARD_OFFWHITE, outline=BORDER_INK, width=1)
    div_txt = "VS // THE HAPPINESS PARADOX"
    f_pill = fonts.get("pill")
    bbox = f_pill.getbbox(div_txt)
    draw.text((div_x1 + (div_w - (bbox[2] - bbox[0])) // 2, div_y1 + 12), div_txt, font=f_pill, fill=ROYAL_COBALT)

    # Bottom Viewport: US & Singapore (High GDP Contrast)
    bot_y = div_y1 + div_h + 16
    if img is not None:
        _draw_modern_light_card(img, [margin_x, bot_y, margin_x + card_w, bot_y + v_h], radius=20, fill=CARD_OFFWHITE, border_col=BORDER_INK, rot_deg=0.6)
    draw = ImageDraw.Draw(img)

    _draw_modern_pill(draw, margin_x + 20, bot_y + 16, "RANK #23 WORLD HAPPINESS // WORLD BANK", fonts.get("pill"), fill=(239, 246, 255, 255), text_col=ROYAL_COBALT, dot_col=ROYAL_COBALT)
    draw.text((margin_x + 20, bot_y + 60), "US & SINGAPORE", font=fonts.get("hero_title", fonts.get("title")), fill=INK_BLACK)

    draw.text((margin_x + 20, bot_y + 116), "$80,000+", font=f_stat, fill=ROYAL_COBALT)
    draw.text((margin_x + 20, bot_y + 190), "ANNUAL GDP PER CAPITA (5X HIGHER)", font=fonts.get("kicker"), fill=WARM_SLATE)

    tx2, ty2 = _draw_modern_pill(draw, margin_x + 20, bot_y + 232, "CHRONIC TIME FAMINE", fonts.get("pill"), fill=(255, 241, 242, 255), text_col=CRIMSON_RED, dot_col=CRIMSON_RED)
    _draw_modern_pill(draw, tx2 + 12, bot_y + 232, "MATERIAL SATURATION", fonts.get("pill"), fill=(255, 241, 242, 255), text_col=CRIMSON_RED, dot_col=CRIMSON_RED)
    draw_wrapped_text(draw, "- High Financial Output // Rapid Hedonic Adaptation", fonts.get("citation_sub"), WARM_SLATE, margin_x + 20, bot_y + 296, card_w - 40, is_arabic=is_arabic)


# ---------------------------------------------------------------------------
# Template 6: The Hedonic Treadmill (Material Upgrade Spike -> Baseline Reset)
# ---------------------------------------------------------------------------

def render_hedonic_treadmill(draw, t_norm, f_idx, cue, fonts, width=1080, height=920, is_arabic=False, img=None):
    dur = float(cue.get("duration", 10.0))
    scale, dy, opacity = get_item_physics(t_norm, cue_duration=dur, stagger_sec=0.0)
    if opacity <= 0.001: return

    margin_x = 54
    max_w = width - 2 * margin_x
    cur_y = 28 + dy

    # Header
    _draw_modern_pill(draw, margin_x, cur_y, "COGNITIVE PSYCHOLOGY // CONSUMER TRAP", fonts.get("pill"), fill=CARD_OFFWHITE, text_col=CRIMSON_RED, dot_col=CRIMSON_RED)
    cur_y += 46
    cur_y = draw_wrapped_text(draw, "THE HEDONIC TREADMILL", fonts.get("hero_title", fonts.get("title")), CRIMSON_RED, margin_x, cur_y, max_w, is_arabic=is_arabic)
    cur_y += 8
    cur_y = draw_wrapped_text(draw, "Material Upgrades Reset Back to Baseline in 30 Days", fonts.get("card_title"), WARM_SLATE, margin_x, cur_y, max_w, is_arabic=is_arabic)
    cur_y += 18

    # Main Chart Card
    chart_h = 440
    if img is not None:
        _draw_modern_light_card(img, [margin_x, cur_y, width - margin_x, cur_y + chart_h], radius=20, fill=CARD_OFFWHITE, border_col=BORDER_INK, rot_deg=-0.5)
    draw = ImageDraw.Draw(img)

    cx1 = margin_x + 40
    cx2 = width - margin_x - 40
    cw = cx2 - cx1
    base_y = cur_y + 310

    # Baseline
    draw.line([(cx1, base_y), (cx2, base_y)], fill=OCHRE_GOLD, width=2)
    draw.text((cx1 + 10, base_y + 12), "HAPPINESS SET-POINT BASELINE (LUCAS ET AL., 2004)", font=fonts.get("citation_sub"), fill=OCHRE_GOLD)

    anim_p = ease_apple(min(1.0, max(0.0, (t_norm * dur - 0.10) / 2.6)))
    pts = []
    num_pts = 80
    max_idx = max(2, int(num_pts * anim_p))
    for i in range(max_idx):
        u = i / float(num_pts - 1)
        px = cx1 + int(u * cw)
        if u < 0.22:
            frac = u / 0.22
            spike = math.sin(frac * math.pi / 2.0)
            py = base_y - int(spike * 220)
        else:
            decay = math.exp(-(u - 0.22) * 5.8)
            py = base_y - int(decay * 220)
        pts.append((px, py))

    if len(pts) > 1:
        draw.line(pts, fill=(254, 243, 199, 255), width=10)
        draw.line(pts, fill=OCHRE_GOLD, width=4)

    sx1 = cx1 + int(0.22 * cw)
    _draw_modern_pill(draw, sx1 - 120, base_y - 260, "DOPAMINE PEAK // NEW PURCHASES", fonts.get("citation_sub"), fill=(254, 243, 199, 255), text_col=OCHRE_GOLD, dot_col=OCHRE_GOLD)
    draw.line([(sx1, base_y - 225), (sx1, base_y - 210)], fill=OCHRE_GOLD, width=2)

    if anim_p >= 0.70:
        rx = cx1 + int(0.72 * cw)
        _draw_modern_pill(draw, rx - 110, base_y - 65, "BASELINE RESET // 2-4 WEEKS", fonts.get("citation_sub"), fill=(255, 241, 242, 255), text_col=CRIMSON_RED, dot_col=CRIMSON_RED)
        draw.line([(rx, base_y - 30), (rx, base_y - 6)], fill=CRIMSON_RED, width=2)

    cur_y += chart_h + 18

    # Bottom Empirical Card
    sc2, dy2, op2 = get_item_physics(t_norm, cue_duration=dur, stagger_sec=0.14)
    b_h = 160
    if img is not None and op2 > 0:
        _draw_modern_light_card(img, [margin_x, cur_y, width - margin_x, cur_y + b_h], radius=18, fill=CARD_OFFWHITE, border_col=BORDER_INK, rot_deg=0.5)
    draw = ImageDraw.Draw(img)

    _draw_modern_pill(draw, margin_x + 20, cur_y + 14, "EMPIRICAL PSYCHOLOGY // BRICKMAN & CAMPBELL (1971)", fonts.get("citation_sub"), fill=PILL_BG_LIGHT, text_col=WARM_SLATE)
    draw_wrapped_text(draw, "Material luxury never permanently scales well-being.", fonts.get("card_title"), INK_BLACK, margin_x + 20, cur_y + 52, max_w - 40, is_arabic=is_arabic)

    draw.text((margin_x + 20, cur_y + 90), "ADAPTATION TO LUXURY: COMPLETE", font=fonts.get("kicker"), fill=CRIMSON_RED)
    bar_w = max_w - 40
    draw.rounded_rectangle([margin_x + 20, cur_y + 118, margin_x + 20 + bar_w, cur_y + 128], radius=5, fill=(230, 224, 214, 255))
    fill_w = int(bar_w * min(1.0, anim_p * 1.3))
    draw.rounded_rectangle([margin_x + 20, cur_y + 118, margin_x + 20 + fill_w, cur_y + 128], radius=5, fill=CRIMSON_RED)


# ---------------------------------------------------------------------------
# Template 7: 3 Pillars of Happiness (Autonomy, Experiences, Generosity)
# ---------------------------------------------------------------------------

def render_three_pillars(draw, t_norm, f_idx, cue, fonts, width=1080, height=920, is_arabic=False, img=None):
    dur = float(cue.get("duration", 16.5))
    scale, dy, opacity = get_item_physics(t_norm, cue_duration=dur, stagger_sec=0.0)
    if opacity <= 0.001: return

    margin_x = 44
    card_w = width - 2 * margin_x
    card_h = 220
    gap_y = 16
    start_y = 150 + dy

    pillars = [
        ("01", "BUYING TIME & AUTONOMY", "Eliminate commute stress and consumer debt. Buy control over daily hours.", "TIME AFFLUENCE", "Whillans & Dunn (2017) PNAS: Buying Time Promotes Life Satisfaction", OCHRE_GOLD, -0.6, 0.0),
        ("02", "SHARED EXPERIENCES", "Adventures and travels appreciate over time while physical things fade.", "LASTING MEMORIES", "Gilovich & Kumar (2014) Journal of Personality & Social Psychology", ROYAL_COBALT, 0.6, 0.08),
        ("03", "GENEROSITY & RELATIONSHIPS", "Investing in loved ones and community is the #1 empirical predictor of joy.", "DEEP CONNECTION", "Harvard 85-Year Study of Adult Development & Dunn et al. (Science)", FOREST_GREEN, -0.4, 0.16),
    ]

    # Header
    _draw_modern_pill(draw, margin_x, 26 + dy, "HARVARD 85-YEAR STUDY // ELIZABETH DUNN (SCIENCE / PNAS)", fonts.get("pill"), fill=CARD_OFFWHITE, text_col=FOREST_GREEN, dot_col=FOREST_GREEN)
    draw_wrapped_text(draw, "3 PILLARS OF TRUE WEALTH", fonts.get("hero_title", fonts.get("title")), INK_BLACK, margin_x, 74 + dy, card_w, is_arabic=is_arabic)

    cur_y = start_y
    for idx, (num_str, title, sub, pill_text, cit, accent_col, rot_deg, stag_sec) in enumerate(pillars):
        sc_i, dy_i, op_i = get_item_physics(t_norm, cue_duration=dur, stagger_sec=stag_sec)
        if op_i <= 0.001:
            cur_y += card_h + gap_y
            continue

        item_y = cur_y + dy_i
        if img is not None:
            _draw_modern_light_card(img, [margin_x, item_y, margin_x + card_w, item_y + card_h], radius=18, fill=CARD_OFFWHITE, border_col=BORDER_INK, rot_deg=rot_deg)
        draw = ImageDraw.Draw(img)

        # Number Tag (Fixed width, clean spacing)
        draw.text((margin_x + 22, item_y + 16), num_str, font=fonts.get("hero_stat"), fill=accent_col)
        # Status Pill
        _draw_modern_pill(draw, margin_x + 115, item_y + 20, pill_text, fonts.get("pill"), fill=PILL_BG_LIGHT, text_col=accent_col, dot_col=accent_col)

        text_y = item_y + 80
        text_y = draw_wrapped_text(draw, title, fonts.get("card_title"), INK_BLACK, margin_x + 22, text_y, card_w - 44, is_arabic=is_arabic)
        text_y = draw_wrapped_text(draw, sub, fonts.get("citation_sub"), WARM_SLATE, margin_x + 22, text_y + 4, card_w - 44, is_arabic=is_arabic)
        draw_wrapped_text(draw, f"- {cit}", fonts.get("citation_sub"), accent_col, margin_x + 22, item_y + card_h - 32, card_w - 44, is_arabic=is_arabic)

        cur_y += card_h + gap_y


TEMPLATE_MAP = {
    "threshold_counter": render_threshold_counter,
    "study_citation": render_study_citation,
    "log_income_curve": render_log_income_curve,
    "correlation_split": render_correlation_split,
    "country_comparison": render_country_comparison,
    "hedonic_treadmill": render_hedonic_treadmill,
    "three_pillars": render_three_pillars,
    "market_trend": render_log_income_curve,
    "crypto_flow": render_three_pillars,
    "risk_meter": render_threshold_counter,
    "network_mesh": render_three_pillars,
    "banking_vault": render_country_comparison,
    "instruments_spread": render_log_income_curve,
    "ai_neural": render_three_pillars,
    "algorithm_metric": render_correlation_split,
    "policy_framework": render_study_citation,
    "academic_thesis": render_study_citation,
    "quantum_physics": render_hedonic_treadmill,
    "calculus_integral": render_log_income_curve,
    "data_distribution": render_correlation_split,
    "citation_network": render_study_citation,
    "order_book": render_country_comparison,
    "sentiment_meter": render_threshold_counter,
    "smart_audit": render_study_citation
}


def draw_hud_progress_filament(draw, t_norm, config, width=1080, y_pos=916):
    """
    Sleek modern bottom divider filament separating top newsprint card from live speaker.
    Includes a fine ink border (#2D2A26) and Forest Green progress fill.
    """
    x_start, x_end = 0, width
    prog = max(0.02, min(1.0, float(t_norm)))
    cur_x = x_start + int((x_end - x_start) * prog)
    # 1. Subtle dividing baseline
    draw.line([(x_start, y_pos), (x_end, y_pos)], fill=BORDER_INK, width=2)
    # 2. Forest Green progress indicator
    draw.line([(x_start, y_pos), (cur_x, y_pos)], fill=FOREST_GREEN, width=3)


def find_external_asset(keyword):
    return None
