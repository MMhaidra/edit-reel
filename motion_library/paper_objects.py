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
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1080, 1920
PAPER = (226, 221, 209)
INK = (28, 26, 24)
INK_SOFT = (96, 90, 82)
GREEN = (0, 112, 74)
RED = (186, 24, 40)
GOLD = (201, 162, 39)
YELLOW = (250, 204, 21)
TAG_FILL = (232, 230, 224)
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


def paper_background(w=W, h=H, seed=7):
    key = (w, h, seed)
    if key in _paper_cache:
        return _paper_cache[key].copy()
    rng = np.random.default_rng(seed)
    base = np.zeros((h, w, 3), np.float32)
    base[:] = PAPER
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
    sw, sh = w * S, h * S
    font = font.font_variant(size=font.size * S)
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
    bb = d.textbbox((0, 0), text, font=font)
    d.text((tx0 - bb[0], (sh - (bb[3] - bb[1])) / 2 - bb[1]), text, font=font, fill=INK)
    return im


def notebook_cutoff(title, subtitle=None, note=None, w=480, h=140, rot=0.0):
    """
    Renders an authentic torn notebook / paper cutoff with faint ruled lines,
    red margin line, torn bottom edge, and optional top Scotch tape.
    """
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
    margin_x = 36 * S
    d.line([(margin_x, 4 * S), (margin_x, sh - 16 * S)], fill=(248, 113, 113, 140), width=3)

    # Semi-transparent Scotch tape at the top
    tape_w, tape_h = 70 * S, 18 * S
    tx0 = (sw - tape_w) // 2
    d.rectangle([tx0, 0, tx0 + tape_w, tape_h], fill=(245, 240, 220, 160), outline=(220, 215, 195, 200), width=2)

    # Text content (typewriter font)
    f_title = tw_font(21, bold=True).font_variant(size=21 * S)
    f_sub = tw_font(17, bold=False).font_variant(size=17 * S)
    f_note = tw_font(15, bold=False).font_variant(size=15 * S)

    cur_ty = 22 * S
    tx_start = margin_x + 16 * S
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
