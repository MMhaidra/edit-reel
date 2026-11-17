"""
v9_objects.py - "Paper & Objects" style learned by LOOKING at example.MP4:
  * warm grainy paper background, speaker CUT OUT and standing on it
  * very little text; big tangible objects instead: hanging price tags on a string
    (gold eyelet), brand/flag badges, coin stacks, arrows, caution tape + paper slip,
    icon + short label chips
  * typewriter slab font for object text (American Typewriter / Courier), ink black
  * green = gain / buyer, red = risk / drop, caution-yellow for warnings
All drawing is supersampled (S=2) so edges are crisp. Pure PIL + numpy.
"""
import math
import re
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1080, 1920
PAPER = (243, 240, 232)
PAPER_WARM = (226, 221, 209)
INK = (20, 20, 18)
CHARCOAL = (20, 20, 18)
INK_SOFT = (104, 99, 90)
SAND = (234, 229, 218)
SAND_DARK = (218, 210, 196)
CORAL = (204, 90, 67)
BLUSH = (232, 198, 188)
GREEN = (0, 112, 74)
SAGE = (31, 110, 80)
RED = (186, 24, 40)
GOLD = (201, 162, 39)
YELLOW = (250, 204, 21)
TAG_FILL = (246, 244, 238)
S = 2

_TW_PATH = "/System/Library/Fonts/Supplemental/AmericanTypewriter.ttc"
_CB_PATH = "/System/Library/Fonts/Supplemental/Courier New Bold.ttf"
_SANS = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
_SANS_BLACK = "/System/Library/Fonts/Supplemental/Arial Black.ttf"


def tw_font(size, bold=True):
    for idx in ([3, 2, 1, 0] if bold else [0]):
        try:
            f = ImageFont.truetype(_TW_PATH, size, index=idx)
            return f
        except Exception:
            continue
    return ImageFont.truetype(_CB_PATH, size)


def sans_font(size, black=False):
    return ImageFont.truetype(_SANS_BLACK if black else _SANS, size)


# ---------------------------------------------------------------- paper
_paper_cache = {}


def paper_background(w=W, h=H, seed=7, tone="editorial"):
    """Generate warm grainy paper background; supports 'editorial' (#F3F0E8) and 'warm' (#E2DDD1)."""
    key = (w, h, seed, tone)
    if key in _paper_cache:
        return _paper_cache[key].copy()
    rng = np.random.default_rng(seed)
    base = np.zeros((h, w, 3), np.float32)
    base[:] = PAPER_WARM if tone == "warm" else PAPER
    # soft mottling
    blotch = rng.normal(0, 1, (h // 64 + 2, w // 64 + 2)).astype(np.float32)
    blotch = np.array(Image.fromarray(blotch).resize((w, h), Image.BICUBIC))
    base += blotch[..., None] * 3.2
    # fine grain
    base += rng.normal(0, 4.0, (h, w, 1)).astype(np.float32)
    # gentle vignette
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    d = np.sqrt(((xx - w / 2) / (w * 0.75)) ** 2 + ((yy - h / 2) / (h * 0.75)) ** 2)
    base *= (1.0 - 0.07 * np.clip(d, 0, 1.2) ** 2)[..., None]
    im = Image.fromarray(np.clip(base, 0, 255).astype(np.uint8), "RGB").convert("RGBA")
    _paper_cache[key] = im
    return im.copy()


# ---------------------------------------------------------------- helpers
def _shadow(layer, offset=(0, 16), blur=18, alpha=95):
    a = layer.split()[-1]
    sh = Image.new("RGBA", layer.size, (60, 45, 30, 0))
    sh.putalpha(a.point(lambda v: int(v * alpha / 255)))
    sh = sh.filter(ImageFilter.GaussianBlur(blur))
    out = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    out.alpha_composite(sh, (offset[0], offset[1]))
    out.alpha_composite(layer)
    return out


def _place(canvas, obj, cx, cy, rot=0.0, scale=1.0, shadow=True, opacity=1.0):
    """obj is an RGBA image drawn at S x; downscale, rotate, shadow, paste centered."""
    im = obj.resize((max(1, int(obj.width / S * scale)), max(1, int(obj.height / S * scale))), Image.LANCZOS)
    if abs(rot) > 0.01:
        im = im.rotate(rot, resample=Image.BICUBIC, expand=True)
    if shadow:
        pad = 60
        padded = Image.new("RGBA", (im.width + pad * 2, im.height + pad * 2), (0, 0, 0, 0))
        padded.alpha_composite(im, (pad, pad))
        im = _shadow(padded)
    if opacity < 1.0:
        a = im.split()[-1].point(lambda v: int(v * opacity))
        im.putalpha(a)
    canvas.alpha_composite(im, (int(cx - im.width / 2), int(cy - im.height / 2)))


def _grain(layer, strength=5.0, seed=3):
    arr = np.array(layer).astype(np.float32)
    rng = np.random.default_rng(seed)
    n = rng.normal(0, strength, arr.shape[:2])[..., None]
    arr[..., :3] = np.clip(arr[..., :3] + n, 0, 255)
    return Image.fromarray(arr.astype(np.uint8), "RGBA")


def _center_text(d, cx, cy, text, font, fill, spacing=0):
    bb = d.textbbox((0, 0), text, font=font)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    d.text((cx - tw / 2 - bb[0], cy - th / 2 - bb[1]), text, font=font, fill=fill)
    return tw, th


# ---------------------------------------------------------------- objects
def draw_tag(w, h, lines, fonts, colors=None, icon=None):
    """Hanging price tag (RGBA at S x). lines: list of strings; colors per line.
    Returns (img, eyelet_xy_in_final_px)."""
    sw, sh = w * S, h * S
    pad = 10
    im = Image.new("RGBA", (sw + pad * 2, sh + pad * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    ch = int(sw * 0.2)
    ox, oy = pad, pad
    poly = [(ox + ch, oy), (ox + sw - ch, oy), (ox + sw, oy + ch), (ox + sw, oy + sh), (ox, oy + sh), (ox, oy + ch)]
    d.polygon(poly, fill=TAG_FILL + (255,))
    ins = 16 * S // 2
    inner = [(ox + ch + 6, oy + ins), (ox + sw - ch - 6, oy + ins), (ox + sw - ins, oy + ch + 6),
             (ox + sw - ins, oy + sh - ins), (ox + ins, oy + sh - ins), (ox + ins, oy + ch + 6)]
    d.line(inner + [inner[0]], fill=(168, 163, 154, 255), width=4)
    # eyelet
    ex, ey = ox + sw // 2, oy + int(ch * 0.95)
    r = int(sw * 0.06)
    d.ellipse([ex - r, ey - r, ex + r, ey + r], fill=PAPER + (255,), outline=GOLD + (255,), width=int(r * 0.35))
    im = _grain(im, 4.0)
    # keep alpha shape (grain only touched rgb)
    d = ImageDraw.Draw(im)
    colors = colors or [INK] * len(lines)
    y = oy + int(ch * 1.9)
    for i, (txt, f) in enumerate(zip(lines, fonts)):
        f2 = f.font_variant(size=f.size * S)
        _center_text(d, ox + sw // 2, y + f2.size // 2, txt, f2, colors[i])
        y += int(f2.size * 1.25)
    return im, ((ox + sw // 2) / S, (oy + int(ch * 0.95)) / S)


def hang_tag(canvas, cx, top_y, w, h, lines, fonts, colors=None, rot=0.0, string_to=0):
    """Draw string + tag so the tag hangs from y=string_to (top) down; tag top at top_y."""
    tag, (ex, ey) = draw_tag(w, h, lines, fonts, colors)
    # string
    d = ImageDraw.Draw(canvas)
    eyelet_y = top_y + (ey - 10 / S * 1) * 1.0
    d.line([(cx, string_to), (cx, eyelet_y)], fill=(70, 62, 54, 255), width=3)
    _place(canvas, tag, cx, top_y + (tag.height / S) / 2 - 10 / S, rot=rot)


def draw_arrow(size, up=True, color=GREEN):
    sw = size * S
    im = Image.new("RGBA", (sw, sw), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    sh = sw * 0.34  # shaft half width
    head = sw * 0.5
    if up:
        pts = [(sw / 2, 0), (sw, head), (sw / 2 + sh * 0.6, head), (sw / 2 + sh * 0.6, sw),
               (sw / 2 - sh * 0.6, sw), (sw / 2 - sh * 0.6, head), (0, head)]
    else:
        pts = [(sw / 2, sw), (sw, sw - head), (sw / 2 + sh * 0.6, sw - head), (sw / 2 + sh * 0.6, 0),
               (sw / 2 - sh * 0.6, 0), (sw / 2 - sh * 0.6, sw - head), (0, sw - head)]
    d.polygon(pts, fill=color + (255,))
    # soft highlight
    hl = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(hl).polygon(pts, fill=(255, 255, 255, 40))
    hl = hl.crop((0, 0, sw // 2, sw))
    im.alpha_composite(hl, (0, 0))
    return im


def draw_coin_stack(n, r=90):
    sw = r * 2 * S
    th = int(r * 0.34 * S)
    hh = int(r * 0.9 * S)
    total_h = hh + th * n + 20
    im = Image.new("RGBA", (sw + 20, total_h + 20), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for i in range(n):
        y = total_h - hh - th * (i + 1) + 10
        d.ellipse([10, y + th, 10 + sw, y + th + hh], fill=(150, 112, 18, 255))
        d.rectangle([10, y + hh // 2 + th // 2, 10 + sw, y + th + hh // 2], fill=(170, 130, 24, 255))
        d.ellipse([10, y, 10 + sw, y + hh], fill=(222, 182, 52, 255), outline=(150, 112, 18, 255), width=4)
        d.ellipse([10 + sw * 0.16, y + hh * 0.16, 10 + sw * 0.84, y + hh * 0.84], outline=(176, 136, 28, 255), width=4)
    return im


def draw_clock(r=110):
    s = r * 2 * S
    im = Image.new("RGBA", (s + 20, s + 20), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse([10, 10, 10 + s, 10 + s], fill=(250, 248, 243, 255), outline=INK + (255,), width=10)
    c = 10 + s / 2
    for i in range(12):
        a = i * math.pi / 6
        d.line([(c + math.sin(a) * s * 0.40, c - math.cos(a) * s * 0.40), (c + math.sin(a) * s * 0.46, c - math.cos(a) * s * 0.46)], fill=INK + (255,), width=6)
    d.line([(c, c), (c + s * 0.2, c - s * 0.12)], fill=INK + (255,), width=12)
    d.line([(c, c), (c - s * 0.02, c - s * 0.34)], fill=INK + (255,), width=9)
    d.ellipse([c - 12, c - 12, c + 12, c + 12], fill=RED + (255,))
    return im


def draw_heart(sz=200, color=RED):
    s = sz * S
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    r = s * 0.27
    d.ellipse([s * 0.06, s * 0.12, s * 0.06 + 2 * r, s * 0.12 + 2 * r], fill=color + (255,))
    d.ellipse([s * 0.94 - 2 * r, s * 0.12, s * 0.94, s * 0.12 + 2 * r], fill=color + (255,))
    d.polygon([(s * 0.07, s * 0.42), (s * 0.93, s * 0.42), (s * 0.5, s * 0.92)], fill=color + (255,))
    hl = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(hl).ellipse([s * 0.16, s * 0.2, s * 0.32, s * 0.34], fill=(255, 255, 255, 90))
    im.alpha_composite(hl)
    return im


def draw_plane(sz=220):
    s = sz * S
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    # paper plane
    d.polygon([(s * 0.05, s * 0.45), (s * 0.95, s * 0.12), (s * 0.55, s * 0.88)], fill=(250, 248, 243, 255), outline=INK + (255,))
    d.polygon([(s * 0.05, s * 0.45), (s * 0.95, s * 0.12), (s * 0.42, s * 0.56)], fill=(214, 210, 200, 255))
    d.polygon([(s * 0.42, s * 0.56), (s * 0.95, s * 0.12), (s * 0.55, s * 0.88)], fill=(236, 233, 225, 255))
    d.line([(s * 0.05, s * 0.45), (s * 0.95, s * 0.12), (s * 0.55, s * 0.88), (s * 0.05, s * 0.45)], fill=INK + (255,), width=6)
    d.line([(s * 0.42, s * 0.56), (s * 0.95, s * 0.12)], fill=INK + (255,), width=4)
    return im


def draw_flag_badge(kind, r=120):
    s = r * 2 * S
    flag = Image.new("RGBA", (s, s), (255, 255, 255, 255))
    d = ImageDraw.Draw(flag)
    if kind == "CR":
        parts = [(0, 1, (0, 43, 127)), (1, 2, (255, 255, 255)), (2, 4, (206, 17, 38)), (4, 5, (255, 255, 255)), (5, 6, (0, 43, 127))]
        for a, b, col in [(0, 1, (0, 43, 127)), (1, 2, (255, 255, 255)), (2, 4, (206, 17, 38)), (4, 5, (255, 255, 255)), (5, 6, (0, 43, 127))]:
            d.rectangle([0, s * a / 6, s, s * b / 6], fill=col)
    elif kind == "US":
        for i in range(13):
            d.rectangle([0, s * i / 13, s, s * (i + 1) / 13], fill=(178, 34, 52) if i % 2 == 0 else (255, 255, 255))
        d.rectangle([0, 0, s * 0.5, s * 7 / 13], fill=(60, 59, 110))
        for i in range(4):
            for j in range(4):
                x, y = s * (0.08 + j * 0.115), s * (0.08 + i * 0.115)
                d.ellipse([x - 5, y - 5, x + 5, y + 5], fill=(255, 255, 255))
    elif kind == "SG":
        d.rectangle([0, 0, s, s / 2], fill=(237, 41, 57))
        d.rectangle([0, s / 2, s, s], fill=(255, 255, 255))
        d.ellipse([s * 0.18, s * 0.1, s * 0.5, s * 0.42], fill=(255, 255, 255))
        d.ellipse([s * 0.26, s * 0.1, s * 0.58, s * 0.42], fill=(237, 41, 57))
        for (px, py) in [(0.64, 0.14), (0.78, 0.24), (0.72, 0.36), (0.56, 0.36), (0.5, 0.24)]:
            d.ellipse([s * px - 7, s * py - 7, s * px + 7, s * py + 7], fill=(255, 255, 255))
    out = Image.new("RGBA", (s + 36, s + 36), (0, 0, 0, 0))
    od = ImageDraw.Draw(out)
    od.ellipse([0, 0, s + 35, s + 35], fill=(252, 251, 248, 255))
    mask = Image.new("L", (s, s), 0)
    ImageDraw.Draw(mask).ellipse([0, 0, s - 1, s - 1], fill=255)
    out.paste(flag, (18, 18), mask)
    return out


def caution_tape(width=1500, height=84, angle=-5):
    sw, sh = width * S, height * S
    im = Image.new("RGBA", (sw, sh), YELLOW + (255,))
    d = ImageDraw.Draw(im)
    step = 70 * S
    for x in range(-sh, sw + sh, step * 2):
        d.polygon([(x, sh), (x + step, sh), (x + step + sh, 0), (x + sh, 0)], fill=(28, 28, 28, 255))
    return im


def paper_slip(text, font, pad=(34, 18), rot=0.0, color=INK):
    font = font.font_variant(size=font.size * S)
    d0 = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    bb = d0.textbbox((0, 0), text, font=font)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    sw, sh = (tw + pad[0] * 2 * S), (th + pad[1] * 2 * S)
    im = Image.new("RGBA", (sw, sh), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, sw - 1, sh - 1], fill=(250, 248, 243, 255))
    d.text((pad[0] * S - bb[0], pad[1] * S - bb[1]), text, font=font, fill=color)
    return _grain(im, 3.0)


def label_chip(icon_img, text, font, w=470, h=150, icon_h=84):
    font_s = font.font_variant(size=font.size * S)
    d_dummy = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    bb = d_dummy.textbbox((0, 0), text, font=font_s)
    tw = bb[2] - bb[0]
    th = bb[3] - bb[1]

    icon_space = 0
    if icon_img is not None:
        ic_scaled_h = icon_h * S
        ic_scaled_w = int(icon_img.width * (ic_scaled_h / icon_img.height))
        icon_space = ic_scaled_w + 22 * S

    # Auto-expand w to guarantee no text is ever clipped, with generous safe padding
    min_needed_w = int((24 * S + icon_space + tw + 32 * S) / S)
    w = max(w, min_needed_w)

    sw, sh = w * S, h * S
    im = Image.new("RGBA", (sw, sh), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, sw - 1, sh - 1], radius=18 * S, fill=(252, 251, 248, 255))
    if icon_img is not None:
        ic = icon_img.copy()
        sc = (icon_h * S) / ic.height
        ic = ic.resize((int(ic.width * sc), int(ic.height * sc)), Image.LANCZOS)
        im.alpha_composite(ic, (24 * S, (sh - ic.height) // 2))
        tx0 = 24 * S + ic.width + 22 * S
    else:
        tx0 = 24 * S
    d.text((tx0 - bb[0], (sh - th) // 2 - bb[1]), text, font=font_s, fill=INK)
    return im


def notebook_cutoff(title, subtitle=None, note=None, w=480, h=140, rot=0.0):
    """
    Renders an authentic torn notebook / paper cutoff with faint ruled lines,
    red margin line, torn bottom edge, and optional top Scotch tape.
    """
    f_title = tw_font(21, bold=True).font_variant(size=21 * S)
    f_sub = tw_font(17, bold=False).font_variant(size=17 * S)
    f_note = tw_font(15, bold=False).font_variant(size=15 * S)

    d_dummy = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    margin_x = 36 * S
    tx_start = margin_x + 16 * S

    w_title = (d_dummy.textbbox((0, 0), title, font=f_title)[2] - d_dummy.textbbox((0, 0), title, font=f_title)[0]) if title else 0
    w_sub = (d_dummy.textbbox((0, 0), subtitle, font=f_sub)[2] - d_dummy.textbbox((0, 0), subtitle, font=f_sub)[0]) if subtitle else 0
    w_note = (d_dummy.textbbox((0, 0), note, font=f_note)[2] - d_dummy.textbbox((0, 0), note, font=f_note)[0]) if note else 0

    max_text_w = max(w_title, w_sub, w_note)
    min_needed_w = int((tx_start + max_text_w + 32 * S) / S)
    w = max(w, min_needed_w)

    sw, sh = w * S, h * S
    im = Image.new("RGBA", (sw, sh), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)

    # Torn bottom edge points
    teeth = 18
    bottom_pts = []
    dx = sw / float(teeth)
    for i in range(teeth + 1):
        x = i * dx
        y_tear = sh - (12 * S if i % 2 == 1 else 0)
        bottom_pts.append((x, y_tear))

    poly = [(0, 0), (sw, 0)] + bottom_pts[::-1]
    d.polygon(poly, fill=(251, 249, 241, 255))

    # Faint ruled horizontal lines (blue-gray)
    line_spacing = 28 * S
    for ly in range(line_spacing, sh - 16 * S, line_spacing):
        d.line([(8 * S, ly), (sw - 8 * S, ly)], fill=(218, 224, 233, 200), width=2)

    # Faint red left margin line
    d.line([(margin_x, 4 * S), (margin_x, sh - 16 * S)], fill=(248, 113, 113, 140), width=3)

    # Semi-transparent Scotch tape at the top
    tape_w, tape_h = 70 * S, 18 * S
    tx0 = (sw - tape_w) // 2
    d.rectangle([tx0, 0, tx0 + tape_w, tape_h], fill=(245, 240, 220, 160), outline=(220, 215, 195, 200), width=2)

    cur_ty = 22 * S
    if title:
        d.text((tx_start, cur_ty), title, font=f_title, fill=INK)
        cur_ty += int(24 * S)
    if subtitle:
        d.text((tx_start, cur_ty), subtitle, font=f_sub, fill=INK_SOFT)
        cur_ty += int(20 * S)
    if note:
        d.text((tx_start, cur_ty), note, font=f_note, fill=(120, 110, 100))

    return _grain(im, 2.5)


def draw_two_parallel_graphs(canvas, anim_p=1.0):
    """
    Draws two parallel graphs side-by-side on the paper canvas:
      Left Graph: LINEAR (MYTH) - each +$50K gives less and less boost, curve flattens out!
      Right Graph: LOGARITHMIC (REALITY) - each 2x doubling gives the exact same boost!
    """
    F = tw_font
    d = ImageDraw.Draw(canvas)

    # 1. Left Graph Box (LINEAR)
    lx0, lx1, ly0, ly1 = 55, 525, 490, 1280
    d.rounded_rectangle([lx0, ly0, lx1, ly1], radius=16, fill=(248, 245, 238, 230), outline=(190, 184, 172, 255), width=3)
    # Header slip
    slip_l = paper_slip("LINEAR (MYTH)", F(36), pad=(16, 8), color=RED)
    _place(canvas, slip_l, (lx0 + lx1) // 2, ly0 + 26, rot=-1.5)

    # Linear badge in upper right corner of box
    chip_flat = label_chip(draw_arrow(50, False, RED), "FLATTENS", F(26), w=260, h=72, icon_h=42)
    _place(canvas, chip_flat, lx1 - 150, ly0 + 95, rot=2.0)

    # Axes with generous inset
    ax_x0, ax_x1 = lx0 + 68, lx1 - 32
    ax_y0, ax_y1 = ly0 + 140, ly1 - 65
    d.line([(ax_x0, ax_y0), (ax_x0, ax_y1), (ax_x1, ax_y1)], fill=INK + (255,), width=4)
    text_c(canvas, ax_x0, ax_y0 - 24, "JOY", F(24), INK_SOFT)

    # Linear X ticks (+$50K)
    linear_ticks = ["$50K", "$100K", "$150K", "$200K"]
    l_pts = []
    cw_l = ax_x1 - ax_x0 - 20
    ch_l = ax_y1 - ax_y0 - 30
    for i, lab in enumerate(linear_ticks):
        px = ax_x0 + 10 + i * (cw_l / 3.0)
        # Rises fast then flattens completely
        u = i / 3.0
        py = ax_y1 - (1.0 - math.exp(-u * 3.5)) * ch_l
        l_pts.append((px, py))
        text_c(canvas, px, ax_y1 + 30, lab, F(22), INK)
        d.line([(px, ax_y1), (px, ax_y1 + 8)], fill=INK + (255,), width=3)

    # Animate linear curve
    n_l = max(2, int(len(l_pts) * 15 * anim_p))
    curve_l = []
    for k in range(min(45, n_l)):
        u = k / 44.0 * 3.0
        i = int(min(2, math.floor(u)))
        f = u - i
        px = l_pts[i][0] + (l_pts[i + 1][0] - l_pts[i][0]) * f
        py = l_pts[i][1] + (l_pts[i + 1][1] - l_pts[i][1]) * f
        curve_l.append((px, py))
    if len(curve_l) > 1:
        ink_line(canvas, curve_l, RED, 8)
    for px, py in l_pts:
        if anim_p >= 0.5:
            d.ellipse([px - 10, py - 10, px + 10, py + 10], fill=PAPER + (255,), outline=RED + (255,), width=4)

    # 2. Right Graph Box (LOGARITHMIC)
    rx0, rx1, ry0, ry1 = 555, 1025, 490, 1280
    d.rounded_rectangle([rx0, ry0, rx1, ry1], radius=16, fill=(248, 245, 238, 230), outline=(190, 184, 172, 255), width=3)
    # Header slip
    slip_r = paper_slip("LOGARITHMIC (REALITY)", F(34), pad=(16, 8), color=GREEN)
    _place(canvas, slip_r, (rx0 + rx1) // 2, ry0 + 26, rot=1.5)

    # Log badge in upper right corner of box
    chip_boost = label_chip(draw_arrow(50, True, GREEN), "EQUAL BOOST", F(24), w=290, h=72, icon_h=42)
    _place(canvas, chip_boost, rx1 - 150, ry0 + 95, rot=-1.5)

    # Axes with generous inset
    rax_x0, rax_x1 = rx0 + 68, rx1 - 32
    rax_y0, rax_y1 = ry0 + 140, ry1 - 65
    d.line([(rax_x0, rax_y0), (rax_x0, rax_y1), (rax_x1, rax_y1)], fill=INK + (255,), width=4)
    text_c(canvas, rax_x0, rax_y0 - 24, "JOY", F(24), INK_SOFT)

    # Log X ticks (Doublings 2x)
    log_ticks = ["$50K", "$100K", "$200K", "$400K"]
    r_pts = []
    cw_r = rax_x1 - rax_x0 - 20
    ch_r = rax_y1 - rax_y0 - 30
    for i, lab in enumerate(log_ticks):
        px = rax_x0 + 10 + i * (cw_r / 3.0)
        # Steady diagonal steps
        py = rax_y1 - (i / 3.0) * ch_r
        r_pts.append((px, py))
        text_c(canvas, px, rax_y1 + 30, lab, F(22), INK)
        d.line([(px, rax_y1), (px, rax_y1 + 8)], fill=INK + (255,), width=3)
        if i < 3:
            mx = (rax_x0 + 10 + i * (cw_r / 3.0) + rax_x0 + 10 + (i + 1) * (cw_r / 3.0)) / 2
            text_c(canvas, mx, rax_y1 + 54, "x2", F(24), RED)

    # Animate log curve
    n_r = max(2, int(len(r_pts) * 15 * anim_p))
    curve_r = []
    for k in range(min(45, n_r)):
        u = k / 44.0 * 3.0
        i = int(min(2, math.floor(u)))
        f = u - i
        px = r_pts[i][0] + (r_pts[i + 1][0] - r_pts[i][0]) * f
        py = r_pts[i][1] + (r_pts[i + 1][1] - r_pts[i][1]) * f
        curve_r.append((px, py))
    if len(curve_r) > 1:
        ink_line(canvas, curve_r, GREEN, 8)
    for px, py in r_pts:
        if anim_p >= 0.5:
            d.ellipse([px - 10, py - 10, px + 10, py + 10], fill=PAPER + (255,), outline=GREEN + (255,), width=4)

    # Bottom takeaway banner
    slip_bot = paper_slip("DOUBLE THE INCOME = SAME BOOST", F(46), pad=(28, 14))
    _place(canvas, slip_bot, 540, 1420, rot=-1.0)


# ---------------------------------------------------------------- charts (ink on paper)
def ink_line(canvas, pts, color, width, glow=False):
    d = ImageDraw.Draw(canvas)
    for a, b in zip(pts[:-1], pts[1:]):
        d.line([a, b], fill=color + (255,), width=width)
    for p in pts:
        d.ellipse([p[0] - width / 2, p[1] - width / 2, p[0] + width / 2, p[1] + width / 2], fill=color + (255,))


def text_c(canvas, cx, cy, text, font, fill=INK, shadow=False):
    d = ImageDraw.Draw(canvas)
    if shadow:
        _center_text(d, cx + 2, cy + 3, text, font, (40, 30, 20, 60))
    _center_text(d, cx, cy, text, font, fill)


# ---------------------------------------------------------------- speaker + subtitles
def person_mask(frame_rgb, segmenter, mp):
    res = segmenter.segment(mp.Image(image_format=mp.ImageFormat.SRGB, data=np.array(frame_rgb)))
    m = res.confidence_masks[0].numpy_view()[:, :, 0].astype(np.float32)
    h, w = m.shape
    # polarity: the speaker is always around lower-centre of the frame
    if m[int(h * 0.62):int(h * 0.75), int(w * 0.4):int(w * 0.6)].mean() < 0.5:
        m = 1.0 - m
    return m


def cutout_layer(frame_rgb, mask, feather=2.0):
    m = np.clip(mask, 0, 1)
    a = Image.fromarray((m * 255).astype(np.uint8), "L").filter(ImageFilter.GaussianBlur(3))
    m = np.asarray(a).astype(np.float32) / 255.0
    m = np.clip((m - 0.42) / 0.26, 0, 1)            # smoothstep-ish: kills halo / sparkles
    m = m * m * (3 - 2 * m)
    a = Image.fromarray((m * 255).astype(np.uint8), "L").filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(1.2))
    im = frame_rgb.convert("RGBA")
    im.putalpha(a)
    return im


def draw_subtitle(canvas, text, cy=1540, dark=False, size=64, max_w=880):
    f = sans_font(size, black=False)
    d = ImageDraw.Draw(canvas)
    while d.textbbox((0, 0), text, font=f)[2] > max_w and size > 36:
        size -= 2
        f = sans_font(size, black=False)
    bb = d.textbbox((0, 0), text, font=f)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    x, y = (W - tw) / 2 - bb[0], cy - th / 2 - bb[1]
    if not dark:
        sh = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
        ImageDraw.Draw(sh).text((x + 2, y + 5), text, font=f, fill=(0, 0, 0, 200))
        canvas.alpha_composite(sh.filter(ImageFilter.GaussianBlur(5)))
        d.text((x, y), text, font=f, fill=(255, 255, 255, 255))
    else:
        d.text((x, y), text, font=f, fill=INK + (255,))


# ---------------------------------------------------------------- editorial & 3D pop-out components
_HN_PATH = "/System/Library/Fonts/HelveticaNeue.ttc"
_AV_PATH = "/System/Library/Fonts/Avenir Next.ttc"
_GEORGIA_PATH = "/System/Library/Fonts/Supplemental/Georgia.ttf"
_GEORGIA_BOLD = "/System/Library/Fonts/Supplemental/Georgia Bold.ttf"
_GEEZA_PATH = "/System/Library/Fonts/GeezaPro.ttc"
_ED_FONT_CACHE = {}


def ed_sans(size, weight="bold"):
    """Load crisp Apple Helvetica Neue / Avenir Next sans font with caching."""
    key = ("sans", int(size), weight)
    if key in _ED_FONT_CACHE:
        return _ED_FONT_CACHE[key]
    idx_map = {"regular": 0, "bold": 1, "medium": 10, "black": 9, "condensed": 4}
    idx = idx_map.get(weight, 1)
    try:
        f = ImageFont.truetype(_HN_PATH, int(size), index=idx)
    except Exception:
        try:
            f = ImageFont.truetype(_SANS_BLACK if weight == "black" else _SANS, int(size))
        except Exception:
            f = tw_font(int(size), bold=(weight != "regular"))
    _ED_FONT_CACHE[key] = f
    return f


def ed_serif(size, bold=False):
    """Load crisp Georgia editorial serif font for archival book excerpts."""
    key = ("serif", int(size), bold)
    if key in _ED_FONT_CACHE:
        return _ED_FONT_CACHE[key]
    path = _GEORGIA_BOLD if bold else _GEORGIA_PATH
    try:
        f = ImageFont.truetype(path, int(size))
    except Exception:
        f = tw_font(int(size), bold=bold)
    _ED_FONT_CACHE[key] = f
    return f


def ar_sans(size, bold=True):
    """Load complete Arabic + digit + Latin font (Arial Bold) with 100% Presentation Form coverage."""
    key = ("ar", int(size), bold)
    if key in _ED_FONT_CACHE:
        return _ED_FONT_CACHE[key]
    path = _SANS if bold else "/System/Library/Fonts/Supplemental/Arial.ttf"
    f = ImageFont.truetype(path, int(size))
    _ED_FONT_CACHE[key] = f
    return f


def is_latin_token(text):
    """Return True when token contains only Latin/numeric/punctuation characters."""
    if not text:
        return False
    return not re.search(r"[\u0600-\u06FF]", str(text))


def _ease_out_cubic(x):
    x = max(0.0, min(1.0, float(x)))
    return 1.0 - (1.0 - x) ** 3


def _ease_out_back(x, s=1.2):
    x = max(0.0, min(1.0, float(x)))
    t = x - 1.0
    return 1.0 + t * t * ((s + 1.0) * t + s)


def _rounded_mask(w, h, r):
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, w - 1, h - 1], radius=r, fill=255)
    return m


def draw_provenance_eyebrow(canvas, text, y=156, opacity=1.0):
    """Draw a minimal, crisp academic source citation eyebrow safely below mobile UI."""
    if opacity <= 0.02 or not text:
        return
    f = ed_sans(23, weight="medium")
    d = ImageDraw.Draw(canvas)
    bb = d.textbbox((0, 0), text, font=f)
    tw = bb[2] - bb[0]
    if tw > 940:
        f = ed_sans(20, weight="medium")
        bb = d.textbbox((0, 0), text, font=f)
        tw = bb[2] - bb[0]
    alpha = int(235 * max(0.0, min(1.0, opacity)))
    tx = (W - tw) // 2 - bb[0]
    d.text((tx, y), text, font=f, fill=INK_SOFT + (alpha,))


def draw_hook_stamp(canvas, badge_text, main_title, el, fade_out=1.0):
    """Minimal editorial header stamp popping cleanly above speaker head during State 1 hook."""
    p_in = _ease_out_back(min(1.0, max(0.0, (el - 0.15) / 0.40)))
    alpha = min(1.0, p_in * fade_out)
    if alpha <= 0.02:
        return
    overlay = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    f_badge = ed_sans(24, weight="bold")
    f_main = ed_sans(56, weight="black")

    off_y = int((1.0 - p_in) * -28)
    cy_badge = 195 + off_y
    if badge_text:
        bb = d.textbbox((0, 0), badge_text, font=f_badge)
        bw = (bb[2] - bb[0]) + 40
        bh = (bb[3] - bb[1]) + 20
        bx0 = (W - bw) // 2
        d.rounded_rectangle(
            [bx0, cy_badge, bx0 + bw, cy_badge + bh],
            radius=bh // 2,
            fill=(243, 240, 232, int(235 * alpha)),
            outline=(20, 20, 18, int(45 * alpha)),
            width=2
        )
        _center_text(d, W // 2, cy_badge + bh // 2, badge_text, f_badge, CORAL + (int(255 * alpha),))

    if main_title:
        cy_main = 285 + off_y
        sh = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
        _center_text(ImageDraw.Draw(sh), W // 2 + 2, cy_main + 4, main_title, f_main, (0, 0, 0, int(145 * alpha)))
        sh = sh.filter(ImageFilter.GaussianBlur(5))
        overlay.alpha_composite(sh)
        _center_text(ImageDraw.Draw(overlay), W // 2, cy_main, main_title, f_main, (250, 248, 243, int(255 * alpha)))

    canvas.alpha_composite(overlay)


def draw_layered_stack_plates(canvas, plates, el, active_idx=None, strike_idx=None, strike_at=4.8, highlight_at=8.8, right_badge=None, fade_out=1.0):
    """
    Stacked full-width editorial bars inspired by high-retention explainer reels.
    Each plate slides in with stagger, gently highlights focal concepts in coral (#CC5A43),
    and optionally reveals a crisp right-side callout badge.
    """
    n = len(plates)
    if n == 0:
        return
    overlay = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    f_label = ed_sans(40, weight="medium")
    f_badge_big = ed_sans(62, weight="bold")
    f_badge_sub = ed_sans(24, weight="medium")

    x0, x1 = 76, W - 76
    bar_h = 104
    gap = 16
    top_y = 225

    for idx, label in enumerate(plates):
        delay = idx * 0.16
        p = _ease_out_back(min(1.0, max(0.0, (el - delay) / 0.42)))
        op = min(1.0, p * 1.4) * fade_out
        if op <= 0.02:
            continue

        by0 = int(top_y + idx * (bar_h + gap) + (1.0 - p) * 32)
        by1 = by0 + bar_h

        is_active = (active_idx == idx) and (el >= highlight_at)
        is_struck = (strike_idx == idx) and (el >= strike_at)

        if is_active:
            active_t = min(1.0, (el - highlight_at) / 0.35)
            bg = tuple(int(SAND[c] + (CORAL[c] - SAND[c]) * active_t) for c in range(3))
            fg = (255, 255, 255, int(255 * op))
        elif is_struck:
            bg = SAND_DARK
            fg = (120, 114, 106, int(220 * op))
        else:
            bg = (247, 244, 237) if idx == 0 else SAND
            fg = INK + (int(255 * op),)

        # Soft ambient card shadow
        d.rounded_rectangle([x0, by0 + 4, x1, by1 + 6], radius=16, fill=(30, 24, 18, int(22 * op)))
        d.rounded_rectangle(
            [x0, by0, x1, by1],
            radius=16,
            fill=bg + (int(248 * op),),
            outline=(195, 188, 174, int(190 * op)),
            width=2
        )

        # Left label
        bb = d.textbbox((0, 0), label, font=f_label)
        ty = by0 + (bar_h - (bb[3] - bb[1])) // 2 - bb[1]
        d.text((x0 + 36, ty), label, font=f_label, fill=fg)

        if is_struck:
            strike_p = min(1.0, max(0.0, (el - strike_at) / 0.35))
            lw = (bb[2] - bb[0]) + 18
            mid_y = by0 + bar_h // 2
            d.line([(x0 + 28, mid_y), (x0 + 28 + int(lw * strike_p), mid_y)], fill=CORAL + (int(230 * op),), width=5)

    # Optional right-side large callout overlaid across lower bars
    if right_badge and el >= right_badge.get("at", 11.0):
        bp = _ease_out_back(min(1.0, (el - right_badge["at"]) / 0.45)) * fade_out
        if bp > 0.02:
            rx = x1 - 40
            ry = top_y + 2 * (bar_h + gap) + bar_h // 2 + 12
            val_txt = right_badge.get("value", "")
            sub_txt = right_badge.get("sub", "")
            bbv = d.textbbox((0, 0), val_txt, font=f_badge_big)
            vw = bbv[2] - bbv[0]
            vx = rx - vw
            # Clean cream-sand pill backing so underlying row text stays masked
            pad_x, pad_y = 26, 14
            d.rounded_rectangle(
                [vx - pad_x, ry - 48 - pad_y, rx + pad_x, ry + 62 + pad_y],
                radius=16,
                fill=(234, 229, 218, int(252 * bp)),
            )
            d.text((vx, ry - 44), val_txt, font=f_badge_big, fill=INK + (int(255 * bp),))
            bbs = d.textbbox((0, 0), sub_txt, font=f_badge_sub)
            d.text((rx - (bbs[2] - bbs[0]), ry + 24), sub_txt, font=f_badge_sub, fill=CORAL + (int(255 * bp),))

    canvas.alpha_composite(overlay)


def draw_highlighted_excerpt_sheet(canvas, doc_title, text_lines, highlights, cur_t, el, fade_out=1.0, footer="— Ch. 1: The New Forms of Control, p. 9"):
    """
    Renders a realistic off-white archival document / book excerpt sheet with
    Georgia Serif typography and smooth coral-blush highlighter ink washes
    synchronized word-by-word to exact acoustic trigger timestamps.
    """
    p_in = _ease_out_cubic(min(1.0, el / 0.42))
    op = min(1.0, p_in * 1.5) * fade_out
    if op <= 0.02:
        return

    sheet = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(sheet)

    x0, y0 = 64, int(218 + (1.0 - p_in) * 32)
    x1, y1 = W - 64, y0 + 448

    # Paper sheet shadow & surface
    d.rounded_rectangle([x0 + 4, y0 + 14, x1 + 4, y1 + 14], radius=16, fill=(40, 32, 24, int(42 * op)))
    d.rounded_rectangle(
        [x0, y0, x1, y1],
        radius=16,
        fill=(251, 250, 246, int(252 * op)),
        outline=(212, 206, 194, int(230 * op)),
        width=2
    )

    f_hdr = ed_sans(22, weight="bold")
    d.text((x0 + 38, y0 + 28), doc_title, font=f_hdr, fill=CORAL + (int(240 * op),))
    d.line([(x0 + 38, y0 + 64), (x1 - 38, y0 + 64)], fill=(224, 218, 206, int(220 * op)), width=2)

    f_body = ed_serif(39, bold=False)
    cur_y = y0 + 92
    line_step = 66

    for line in text_lines:
        tx = x0 + 42
        # Check if any highlight substring is inside this line
        segments = [(line, None)]
        for phrase, trig_t in highlights:
            new_segs = []
            for seg_txt, seg_trig in segments:
                if seg_trig is None and phrase in seg_txt:
                    idx_p = seg_txt.index(phrase)
                    if idx_p > 0:
                        new_segs.append((seg_txt[:idx_p], None))
                    new_segs.append((phrase, trig_t))
                    if idx_p + len(phrase) < len(seg_txt):
                        new_segs.append((seg_txt[idx_p + len(phrase):], None))
                else:
                    new_segs.append((seg_txt, seg_trig))
            segments = new_segs

        cur_x = tx
        for seg_txt, seg_trig in segments:
            bb = d.textbbox((0, 0), seg_txt, font=f_body)
            sw = bb[2] - bb[0]
            sh = bb[3] - bb[1]
            if seg_trig is not None and cur_t >= seg_trig:
                hp = _ease_out_cubic(min(1.0, (cur_t - seg_trig) / 0.32))
                hx0 = cur_x - 6
                hx1 = cur_x + int((sw + 10) * hp)
                hy0 = cur_y - 4
                hy1 = cur_y + sh + 16
                d.rounded_rectangle([hx0, hy0, hx1, hy1], radius=6, fill=BLUSH + (int(220 * op),))
            d.text((cur_x, cur_y), seg_txt, font=f_body, fill=INK + (int(255 * op),))
            # Advance accurately using textlength
            cur_x += int(round(d.textlength(seg_txt, font=f_body)))
        cur_y += line_step

    if footer:
        d.text((x0 + 42, y1 - 54), footer, font=ed_serif(24, bold=False), fill=INK_SOFT + (int(225 * op),))
    canvas.alpha_composite(sheet)


def draw_horizontal_benchmark_bars(canvas, bars, bench_label, bench_ratio, el, title_text=None, fade_out=1.0):
    """
    Horizontal bar comparison chart with dashed benchmark vertical rule
    (learned from Price/Sales & CapEx comparison layouts).
    bars: list of dict {"label": str, "val": float, "val_str": str, "accent": bool}
    """
    overlay = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)

    f_lbl = ed_sans(32, weight="medium")
    f_val = ed_sans(32, weight="bold")
    f_bench = ed_sans(26, weight="bold")

    y_start = 248
    if title_text:
        d.text((76, 206), title_text, font=ed_sans(28, weight="bold"), fill=INK + (int(240 * fade_out),))
        y_start = 294

    label_x = 76
    bar_x0 = 400
    bar_max_w = 500
    row_h = 72
    row_gap = 26

    # Dashed benchmark vertical line
    bx = bar_x0 + int(bar_max_w * bench_ratio)
    line_y0 = y_start - 10
    line_y1 = y_start + len(bars) * (row_h + row_gap) - row_gap + 12
    bench_p = min(1.0, max(0.0, el / 0.45)) * fade_out
    if bench_label and bench_p > 0.05:
        d.text((bx - 52, line_y0 - 34), bench_label, font=f_bench, fill=INK_SOFT + (int(245 * bench_p),))
        for dy in range(line_y0, line_y1, 16):
            d.line([(bx, dy), (bx, min(dy + 9, line_y1))], fill=(90, 85, 78, int(200 * bench_p)), width=3)

    for idx, b in enumerate(bars):
        delay = 0.25 + idx * 0.22
        p = _ease_out_cubic(min(1.0, max(0.0, (el - delay) / 0.55)))
        op = min(1.0, p * 2.0) * fade_out
        if op <= 0.02:
            continue

        ry = y_start + idx * (row_h + row_gap)
        # Left card pill
        d.rounded_rectangle(
            [label_x, ry, bar_x0 - 18, ry + row_h],
            radius=12,
            fill=(248, 246, 240, int(245 * op)),
            outline=(205, 198, 184, int(220 * op)),
            width=2
        )
        _center_text(d, (label_x + bar_x0 - 18) // 2, ry + row_h // 2, b["label"], f_lbl, INK + (int(255 * op),))

        # Horizontal bar
        bw = max(8, int(bar_max_w * b["ratio"] * p))
        bar_col = CORAL if b.get("accent") else CHARCOAL
        if b.get("muted"):
            bar_col = SAND_DARK
        d.rounded_rectangle([bar_x0, ry + 10, bar_x0 + bw, ry + row_h - 10], radius=10, fill=bar_col + (int(245 * op),))

        if p > 0.35:
            val_op = min(1.0, (p - 0.35) / 0.35) * op
            val_col = CORAL if b.get("accent") else INK
            d.text((bar_x0 + bw + 14, ry + 18), b["val_str"], font=f_val, fill=val_col + (int(255 * val_op),))

    canvas.alpha_composite(overlay)


def draw_slider_switch_track(canvas, left_label, right_label, slide_p, y=385, opacity=1.0):
    """
    Minimal horizontal slider track inspired by Fair Value estimate UI (@ 110s):
    glides a rounded rectangle thumb smoothly from left_label to right_label.
    """
    if opacity <= 0.02:
        return
    overlay = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    f_tag = ed_sans(30, weight="bold")
    f_sub = ed_sans(25, weight="medium")

    x0, x1 = 150, W - 150
    d.line([(x0, y), (x1, y)], fill=INK + (int(220 * opacity),), width=4)

    tx0, tx1 = x0 + 130, x1 - 130
    cur_x = int(tx0 + (tx1 - tx0) * max(0.0, min(1.0, slide_p)))
    is_right = slide_p >= 0.72
    fill_c = CORAL if is_right else SAND_DARK
    text_c_in = (255, 255, 255) if is_right else INK
    active_txt = right_label if is_right else left_label
    bb_act = d.textbbox((0, 0), active_txt, font=f_tag)
    thumb_w = max(210, (bb_act[2] - bb_act[0]) + 56)
    thumb_h = 66

    d.rounded_rectangle(
        [cur_x - thumb_w // 2, y - thumb_h // 2, cur_x + thumb_w // 2, y + thumb_h // 2],
        radius=12,
        fill=fill_c + (int(250 * opacity),),
        outline=INK + (int(230 * opacity),),
        width=2
    )
    _center_text(d, cur_x, y, active_txt, f_tag, text_c_in + (int(255 * opacity),))

    # Endpoint labels below line (omit when active thumb covers that side to prevent duplicate text)
    if slide_p > 0.28:
        d.text((x0 + 20, y + 48), left_label, font=f_sub, fill=INK_SOFT + (int(230 * opacity),))
    if not is_right:
        bbr = d.textbbox((0, 0), right_label, font=f_sub)
        d.text((x1 - 20 - (bbr[2] - bbr[0]), y + 48), right_label, font=f_sub, fill=INK_SOFT + (int(235 * opacity),))

    canvas.alpha_composite(overlay)


def draw_full_compare_columns(canvas, left_cfg, right_cfg, el, fade_out=1.0):
    """
    Full-canvas State 3 2-Column Analytical Contrast (inspired by $900B Fixed vs Revenue @ 95s).
    Left: Solid dark charcoal rounded card with bold headline + sequential symptom pills.
    Right: Tall warm sand/blush stacked proportional card with horizontal dividers.
    """
    p_cols = _ease_out_back(min(1.0, el / 0.50))
    op = min(1.0, p_cols * 1.4) * fade_out
    if op <= 0.02:
        return

    overlay = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)

    col_w = 452
    col_h = 920
    lx0 = 72
    rx0 = W - 72 - col_w
    y0 = int(320 + (1.0 - p_cols) * 40)

    f_hdr = ed_serif(34, bold=True)
    f_big = ed_sans(56, weight="black")
    f_pill = ed_sans(32, weight="bold")
    f_small = ed_sans(28, weight="medium")

    # Headers above columns
    _center_text(d, lx0 + col_w // 2, y0 - 44, left_cfg["header"], f_hdr, INK + (int(255 * op),))
    _center_text(d, rx0 + col_w // 2, y0 - 44, right_cfg["header"], f_hdr, INK + (int(255 * op),))

    # Left dark charcoal card
    d.rounded_rectangle([lx0, y0, lx0 + col_w, y0 + col_h], radius=26, fill=CHARCOAL + (int(252 * op),))
    _center_text(d, lx0 + col_w // 2, y0 + 185, left_cfg["big_title"], f_big, (250, 248, 243, int(255 * op)))
    _center_text(d, lx0 + col_w // 2, y0 + 255, left_cfg["subtitle"], f_small, SAND_DARK + (int(220 * op),))

    # Sequential terracotta pills popping inside left dark column
    for i, item in enumerate(left_cfg.get("items", [])):
        trig = item.get("at", 0.6 + i * 1.5)
        if el >= trig:
            ip = _ease_out_back(min(1.0, (el - trig) / 0.42))
            iop = min(1.0, ip * 1.8) * op
            py = int(y0 + 380 + i * 138 + (1.0 - ip) * 24)
            px0, px1 = lx0 + 42, lx0 + col_w - 42
            d.rounded_rectangle([px0, py, px1, py + 98], radius=16, fill=CORAL + (int(245 * iop),))
            _center_text(d, (px0 + px1) // 2, py + 49, item["text"], f_pill, (255, 255, 255, int(255 * iop)))

    # Right warm proportional stacked card
    d.rounded_rectangle([rx0, y0, rx0 + col_w, y0 + col_h], radius=26, fill=(247, 244, 238, int(250 * op)), outline=INK + (int(235 * op),), width=3)

    # Top segment (blush/terracotta tint)
    split_y1 = y0 + int(col_h * 0.34)
    d.rounded_rectangle([rx0 + 4, y0 + 4, rx0 + col_w - 4, split_y1 + 20], radius=22, fill=BLUSH + (int(240 * op),))
    d.rectangle([rx0 + 4, split_y1 - 24, rx0 + col_w - 4, split_y1], fill=BLUSH + (int(240 * op),))
    d.line([(rx0, split_y1), (rx0 + col_w, split_y1)], fill=INK + (int(230 * op),), width=3)
    _center_text(d, rx0 + col_w // 2, y0 + int(col_h * 0.17), right_cfg["top_label"], f_pill, INK + (int(255 * op),))

    # Middle badge bar
    split_y2 = y0 + int(col_h * 0.48)
    d.rectangle([rx0 + 4, split_y1, rx0 + col_w - 4, split_y2], fill=SAND_DARK + (int(235 * op),))
    d.line([(rx0, split_y2), (rx0 + col_w, split_y2)], fill=INK + (int(230 * op),), width=3)
    _center_text(d, rx0 + col_w // 2, (split_y1 + split_y2) // 2, right_cfg["mid_label"], f_small, INK + (int(255 * op),))

    # Bottom large block
    _center_text(d, rx0 + col_w // 2, split_y2 + 150, right_cfg["bot_big"], f_big, INK + (int(255 * op),))
    _center_text(d, rx0 + col_w // 2, split_y2 + 235, right_cfg["bot_sub"], f_small, INK_SOFT + (int(240 * op),))

    canvas.alpha_composite(overlay)


def _clean_head_popout_mask(mask_crop, anchor_x_local):
    """
    Keeps ONLY the primary connected head component touching the bottom edge
    near anchor_x_local so detached floating hand fragments or wall artifacts
    never bleed above the rounded portrait card border.
    """
    h, w = mask_crop.shape
    if h < 8 or w < 8:
        return mask_crop
    # Clamp pop-out horizontally to strict head zone so raised outer hands stay inside card
    masked_band = mask_crop.copy()
    hx_min = max(0, int(anchor_x_local - 220))
    hx_max = min(w, int(anchor_x_local + 220))
    masked_band[:, :hx_min] = 0.0
    masked_band[:, hx_max:] = 0.0

    bw = (masked_band > 0.44).astype(np.uint8)
    num_lbl, labels, stats, centroids = cv2.connectedComponentsWithStats(bw, connectivity=8)
    if num_lbl <= 1:
        return masked_band
    keep = np.zeros_like(bw)
    for lbl in range(1, num_lbl):
        area = int(stats[lbl, cv2.CC_STAT_AREA])
        top = int(stats[lbl, cv2.CC_STAT_TOP])
        comp_h = int(stats[lbl, cv2.CC_STAT_HEIGHT])
        cx = float(centroids[lbl][0])
        touches_card = (top + comp_h) >= (h - 24)
        near_face = abs(cx - anchor_x_local) < 135.0
        if area >= 900 and touches_card and near_face:
            keep[labels == lbl] = 1
    if keep.sum() == 0:
        return np.zeros_like(mask_crop)
    keep = cv2.dilate(keep, np.ones((5, 5), np.uint8), iterations=1)
    m = cv2.GaussianBlur(masked_band * keep.astype(np.float32), (5, 5), 1.4)
    m = np.clip((m - 0.36) / 0.28, 0.0, 1.0)
    return m * m * (3.0 - 2.0 * m)


def composite_popout_speaker_card(
    canvas,
    frame_np,
    mask_f32,
    smoothed_head_top=320.0,
    smoothed_head_cx=540.0,
    lower_p=1.0,
    card_rect=(190, 1155, 700, 575),
    target_head_top_y=855,
    card_scale=0.72,
    radius=30,
):
    """
    Composites the speaker inside an elevated rounded studio card (`card_rect`) on paper,
    keeping torso/hands 100% solid inside the card while allowing the segmented head
    to pop cleanly above the top edge (`target_head_top_y .. card_y0`) in 3D.
    """
    cx0, cy0, cw, ch = card_rect
    lp = max(0.0, min(1.0, float(lower_p)))

    if lp <= 0.02:
        canvas.alpha_composite(Image.fromarray(frame_np, "RGB").convert("RGBA"))
        return

    # Smooth transition between full-bleed (0,0,1080,1920) and target rounded card
    sc = 1.0 + (card_scale - 1.0) * lp
    sw = max(cw, int(round(1080 * sc)))
    sh = max(ch, int(round(1920 * sc)))

    cur_x0 = int(round(0 + cx0 * lp))
    cur_y0 = int(round(0 + cy0 * lp))
    cur_x1 = int(round(1080 + (cx0 + cw - 1080) * lp))
    cur_y1 = int(round(1920 + (cy0 + ch - 1920) * lp))
    cur_w = max(16, cur_x1 - cur_x0)
    cur_h = max(16, cur_y1 - cur_y0)
    cur_r = int(round(radius * lp))

    # Position scaled speaker so head_top settles cleanly at target_head_top_y (855)
    dest_ht = int(round(0 * (1.0 - lp) + (target_head_top_y - smoothed_head_top * sc) * lp))
    # Clamp vertically so card stays 100% filled from top to bottom
    sy = min(cur_y0, max(cur_y1 - sh, dest_ht))
    # Center horizontally around face centroid while guaranteeing zero empty side gaps inside card
    sx_ideal = int(round((W / 2.0) - smoothed_head_cx * sc))
    sx = max(cur_x1 - sw, min(cur_x0, sx_ideal))

    # Fast OpenCV resize of speaker RGB
    frame_scaled = cv2.resize(frame_np, (sw, sh), interpolation=cv2.INTER_LINEAR)

    # 1. Extract card interior crop directly from scaled camera frame (100% solid shoulders & hands)
    rx0 = max(0, cur_x0 - sx)
    ry0 = max(0, cur_y0 - sy)
    card_rgb = frame_scaled[ry0:ry0 + cur_h, rx0:rx0 + cur_w]
    if card_rgb.shape[0] != cur_h or card_rgb.shape[1] != cur_w:
        card_rgb = cv2.resize(card_rgb, (cur_w, cur_h), interpolation=cv2.INTER_LINEAR)

    # Drop shadow behind elevated studio card
    if lp > 0.15:
        sh_im = Image.new("RGBA", (cur_w + 48, cur_h + 48), (0, 0, 0, 0))
        ImageDraw.Draw(sh_im).rounded_rectangle(
            [24, 24, 24 + cur_w - 1, 24 + cur_h - 1],
            radius=max(1, cur_r),
            fill=(24, 20, 16, int(52 * lp))
        )
        sh_im = sh_im.filter(ImageFilter.GaussianBlur(14))
        canvas.alpha_composite(sh_im, (cur_x0 - 24, cur_y0 - 16))

    card_im = Image.fromarray(card_rgb, "RGB").convert("RGBA")
    if cur_r > 2:
        card_im.putalpha(_rounded_mask(cur_w, cur_h, cur_r))
    canvas.alpha_composite(card_im, (cur_x0, cur_y0))

    # Subtle crisp 1.5px editorial border around studio card
    if lp > 0.25:
        b_im = Image.new("RGBA", (cur_w, cur_h), (0, 0, 0, 0))
        ImageDraw.Draw(b_im).rounded_rectangle(
            [0, 0, cur_w - 1, cur_h - 1],
            radius=max(1, cur_r),
            outline=(255, 253, 248, int(145 * lp)),
            width=2
        )
        canvas.alpha_composite(b_im, (cur_x0, cur_y0))

    # 2. Pop-out head segmentation ONLY above card top edge (cur_y0) up to stage safety zone
    pop_top_canvas = max(0, cur_y0 - 340)
    pop_bot_canvas = min(1920, cur_y0 + 16)
    if pop_bot_canvas > pop_top_canvas + 8 and lp > 0.10:
        ry_pop0 = pop_top_canvas - sy
        ry_pop1 = pop_bot_canvas - sy
        # Compute intersection in scaled frame space
        s_y0 = max(0, ry_pop0)
        s_y1 = min(sh, ry_pop1)
        s_x0 = max(0, cur_x0 - sx)
        s_x1 = min(sw, cur_x1 - sx)
        if s_y1 > s_y0 + 4 and s_x1 > s_x0 + 4:
            mask_scaled = cv2.resize(mask_f32, (sw, sh), interpolation=cv2.INTER_LINEAR)
            head_mask_crop = mask_scaled[s_y0:s_y1, s_x0:s_x1]
            face_local_x = int(round(smoothed_head_cx * sc)) - s_x0
            clean_m = _clean_head_popout_mask(head_mask_crop, face_local_x)
            # Smooth bottom overlap blend into card interior so hairline edge has zero seam
            if clean_m.shape[0] > 14:
                clean_m[-14:, :] *= np.linspace(1.0, 0.0, 14)[:, None]
            head_rgb = frame_scaled[s_y0:s_y1, s_x0:s_x1]
            head_alpha = (clean_m * 255.0 * min(1.0, lp * 1.15)).astype(np.uint8)
            head_im = Image.fromarray(np.dstack([head_rgb, head_alpha]), "RGBA")
            canvas.alpha_composite(head_im, (sx + s_x0, sy + s_y0))


def draw_editorial_trend_curve(
    canvas,
    title_text,
    bench_label,
    start_label,
    end_label,
    norm_points,
    metric_big,
    metric_sub,
    el,
    curve_color=CORAL,
    bench_norm_y=0.15,
    fade_out=1.0,
):
    """
    Draws an animated macro-index trend chart on the warm alabaster stage (y=214..755)
    with a dashed reference line, progressive ink curve (0.0=bottom .. 1.0=top norm y),
    endpoint dot, and floating corner metric badge.
    """
    p_in = _ease_out_cubic(min(1.0, el / 0.40))
    op = min(1.0, p_in * 1.5) * fade_out
    if op <= 0.02:
        return

    overlay = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)

    f_title = ed_sans(31, weight="bold")
    f_sub = ed_sans(23, weight="medium")
    f_big = ed_sans(56, weight="black")
    f_bsub = ed_sans(22, weight="bold")

    d.text((76, 212), title_text, font=f_title, fill=INK + (int(255 * op),))

    # Plot bounds inside upper stage leaving >=115px clearance above pop-out head (y=855)
    x0, x1 = 92, W - 92
    y_top, y_bot = 315, 655
    plot_h = y_bot - y_top

    # Clean light card backing
    d.rounded_rectangle(
        [72, 265, W - 72, 725],
        radius=18,
        fill=(250, 248, 243, int(235 * op)),
        outline=(214, 208, 196, int(210 * op)),
        width=2,
    )

    # Horizontal dashed benchmark line
    by = int(y_bot - bench_norm_y * plot_h)
    for dx in range(x0, x1, 20):
        d.line([(dx, by), (min(dx + 10, x1), by)], fill=INK_SOFT + (int(195 * op),), width=3)
    b_lbl_y = by - 28 if bench_norm_y >= 0.72 else by + 10
    d.text((x0 + 8, b_lbl_y), bench_label, font=f_sub, fill=INK_SOFT + (int(230 * op),))

    # Interpolate smooth polyline from norm_points
    curve_p = _ease_out_cubic(min(1.0, max(0.0, (el - 0.30) / 1.8)))
    if curve_p > 0.02 and len(norm_points) >= 2:
        n_steps = 80
        max_k = max(2, int(n_steps * curve_p))
        pts = []
        seg_n = len(norm_points) - 1
        for k in range(max_k):
            u = k / float(n_steps - 1)
            pos = u * seg_n
            idx = min(seg_n - 1, int(math.floor(pos)))
            frac = pos - idx
            yn = norm_points[idx] + (norm_points[idx + 1] - norm_points[idx]) * frac
            px = x0 + 24 + u * (x1 - x0 - 48)
            py = y_bot - yn * plot_h
            pts.append((px, py))
        ink_line(overlay, pts, curve_color, 9)
        ex, ey = pts[-1]
        d.ellipse([ex - 11, ey - 11, ex + 11, ey + 11], fill=(255, 255, 255, int(255 * op)), outline=curve_color + (int(255 * op),), width=5)

    # X-axis start/end labels inside bottom of card
    d.text((x0 + 16, y_bot + 18), start_label, font=f_sub, fill=INK_SOFT + (int(230 * op),))
    bbe = d.textbbox((0, 0), end_label, font=f_sub)
    d.text((x1 - 16 - (bbe[2] - bbe[0]), y_bot + 18), end_label, font=f_sub, fill=INK + (int(240 * op),))

    # Metric callout card in opposite quadrant to endpoint
    if el >= 0.9:
        mp_t = _ease_out_back(min(1.0, (el - 0.9) / 0.42)) * op
        bbm = d.textbbox((0, 0), metric_big, font=f_big)
        bbs = d.textbbox((0, 0), metric_sub, font=f_bsub)
        mw = max(bbm[2] - bbm[0], bbs[2] - bbs[0]) + 64
        bx0 = (x1 - mw - 18) if norm_points[-1] < 0.5 else (x0 + 18)
        is_low_end = norm_points[-1] < 0.5
        by0 = 300 if is_low_end else 325
        # Keep badge opposite endpoint Y when endpoint finishes low vs high
        if norm_points[-1] >= 0.5:
            bx0 = x0 + 24
            by0 = 305
        else:
            bx0 = x1 - mw - 24
            by0 = 335
        d.rounded_rectangle(
            [bx0, by0, bx0 + mw, by0 + 112],
            radius=16,
            fill=CHARCOAL + (int(244 * mp_t),),
        )
        _center_text(d, bx0 + mw // 2, by0 + 42, metric_big, f_big, (255, 255, 255, int(255 * mp_t)))
        _center_text(d, bx0 + mw // 2, by0 + 88, metric_sub, f_bsub, BLUSH + (int(255 * mp_t),))

    canvas.alpha_composite(overlay)

