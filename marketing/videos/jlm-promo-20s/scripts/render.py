"""Render the JLM 20s promo frame by frame and pipe it into ffmpeg.

    python3 render.py --assets ../assets --fonts FONT_DIR --out out/jlm_promo_20s.mp4
    python3 render.py ... --stills 1.0,4.6,19.5      # PNG checks only, no video

FONT_DIR must hold the two Helvetica Neue LT Arabic files (Bold + Roman).
"""

import argparse
import math
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

import soundtrack
import storyboard as sb

W, H = sb.SIZE
FPS = sb.FPS
N_FRAMES = int(sb.DURATION * FPS)
ALBERT_PATH = None  # set in main() from --fonts


# ---------------------------------------------------------------- easing ----
def clamp01(x):
    return max(0.0, min(1.0, x))


def ease_out(x):
    x = clamp01(x)
    return 1 - (1 - x) ** 3


def ease_in_out(x):
    x = clamp01(x)
    return 4 * x ** 3 if x < 0.5 else 1 - (-2 * x + 2) ** 3 / 2


def window(t, t_in, t_out, d_in=0.4, d_out=0.25):
    """(in-progress, out-progress) for an element living in [t_in, t_out]."""
    return ease_out((t - t_in) / d_in), ease_in_out((t - (t_out - d_out)) / d_out)


def rgb01(c):
    return np.array(c, np.float32) / 255.0


# ----------------------------------------------------------- compositing ----
def to_premul(rgba_u8):
    a = rgba_u8[..., 3:4].astype(np.float32) / 255.0
    rgb = rgba_u8[..., :3].astype(np.float32) / 255.0
    return np.concatenate([rgb * a, a], axis=2)


def over(dst, src, x, y, alpha=1.0):
    """Composite premultiplied RGBA `src` onto `dst` (RGB float) at integer x, y."""
    if alpha <= 0.002:
        return
    h, w = src.shape[:2]
    x, y = int(round(x)), int(round(y))
    x0, y0, x1, y1 = max(x, 0), max(y, 0), min(x + w, W), min(y + h, H)
    if x0 >= x1 or y0 >= y1:
        return
    s = src[y0 - y: y1 - y, x0 - x: x1 - x]
    if alpha < 1:
        s = s * alpha
    d = dst[y0:y1, x0:x1]
    d *= 1 - s[..., 3:4]
    d += s[..., :3]


def add_light(dst, rgb_img, x, y, gain=1.0):
    """Additive light (glows, particles)."""
    h, w = rgb_img.shape[:2]
    x0, y0, x1, y1 = max(x, 0), max(y, 0), min(x + w, W), min(y + h, H)
    if x0 >= x1 or y0 >= y1:
        return
    dst[y0:y1, x0:x1] += rgb_img[y0 - y: y1 - y, x0 - x: x1 - x] * gain


def warp_premul(src, scale, cx, cy, anchor):
    """Scale premultiplied `src` about its `anchor` (ax, ay) and place that
    anchor at frame position (cx, cy) with sub-pixel accuracy. Returns
    (layer, x, y) ready for `over`."""
    ax, ay = anchor
    h, w = src.shape[:2]
    ow, oh = int(w * scale) + 4, int(h * scale) + 4
    ox, oy = math.floor(cx - ax * scale) - 2, math.floor(cy - ay * scale) - 2
    M = np.float32([[scale, 0, cx - ax * scale - ox], [0, scale, cy - ay * scale - oy]])
    layer = cv2.warpAffine(src, M, (ow, oh), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
    return layer, ox, oy


def rtl_reveal(layer, p, soft=90):
    """Right-to-left wipe for Arabic lines: columns appear from the right edge."""
    if p >= 1:
        return layer
    w = layer.shape[1]
    r = (1 - p) * (w + soft) - soft
    ramp = np.clip((np.arange(w, dtype=np.float32) - r) / soft, 0, 1)
    return layer * ramp[None, :, None]


def ltr_reveal(layer, p, soft=90):
    if p >= 1:
        return layer
    w = layer.shape[1]
    r = p * (w + soft)
    ramp = np.clip((r - np.arange(w, dtype=np.float32)) / soft, 0, 1)
    return layer * ramp[None, :, None]


# ------------------------------------------------------------------ type ----
class Type:
    def __init__(self, font_dir):
        fd = Path(font_dir)
        self.bold_path = next(fd.glob("*bold*.ttf"))
        self.roman_path = next(fd.glob("*roman*.ttf"))
        self._cache = {}

    def font(self, size, bold=True):
        key = (size, bold)
        if key not in self._cache:
            path = self.bold_path if bold else self.roman_path
            self._cache[key] = ImageFont.truetype(str(path), size, layout_engine=ImageFont.Layout.RAQM)
        return self._cache[key]

    @staticmethod
    def _is_arabic(word):
        return any("؀" <= ch <= "ۿ" for ch in word)

    def line(self, runs, size, bold=True, shadow=True, pad=40):
        """Arabic line from [(text, color), ...] in logical order, laid out
        right-to-left word by word so each word can carry its own colour.
        Returns a premultiplied float RGBA array."""
        f = self.font(size, bold)
        words = [(w, c) for text, c in runs for w in text.split(" ") if w]
        space = f.getlength(" ", direction="rtl") * 1.05
        advs = [f.getlength(w, direction="rtl" if self._is_arabic(w) else "ltr") for w, _ in words]
        ascent, descent = f.getmetrics()
        lw = int(sum(advs) + space * (len(words) - 1)) + 2 * pad
        lh = ascent + descent + 2 * pad
        img = Image.new("RGBA", (lw, lh), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        x = lw - pad
        for (wd, col), adv in zip(words, advs):
            x -= adv
            d.text((x, pad), wd, font=f, fill=tuple(col) + (255,),
                   direction="rtl" if self._is_arabic(wd) else "ltr")
            x -= space
        return self._finish(img, shadow)

    def latin(self, text, size, color, bold=True, tracking=0.0, shadow=True, pad=40):
        f = self.font(size, bold)
        advs = [f.getlength(ch) for ch in text]
        ascent, descent = f.getmetrics()
        lw = int(sum(advs) + tracking * size * (len(text) - 1)) + 2 * pad
        img = Image.new("RGBA", (lw, ascent + descent + 2 * pad), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        x = pad
        for ch, adv in zip(text, advs):
            d.text((x, pad), ch, font=f, fill=tuple(color) + (255,))
            x += adv + tracking * size
        return self._finish(img, shadow)

    def outline(self, text, size, color, stroke=3):
        f = self.font(size, True)
        l, t, r, b = f.getbbox(text)
        img = Image.new("RGBA", (r - l + 40, b - t + 40), (0, 0, 0, 0))
        ImageDraw.Draw(img).text((20 - l, 20 - t), text, font=f, fill=(0, 0, 0, 0),
                                 stroke_width=stroke, stroke_fill=tuple(color) + (255,))
        return to_premul(np.array(img))

    @staticmethod
    def _finish(img, shadow):
        arr = to_premul(np.array(img))
        if not shadow:
            return arr
        a = cv2.GaussianBlur(arr[..., 3], (0, 0), 9) * 0.55
        sh = np.zeros_like(arr)
        sh[..., 3] = a
        sh = np.roll(sh, 5, axis=0)
        out = sh.copy()
        out *= 1 - arr[..., 3:4]
        out += arr
        return out


def albert(size, weight=900):
    """Albert Sans (the JLM template typeface) at a given weight."""
    f = ImageFont.truetype(str(ALBERT_PATH), size)
    try:
        f.set_variation_by_axes([weight])
    except Exception:
        pass
    return f


def latin_layer(text, size, color, weight=900, tracking=0.04):
    f = albert(size, weight)
    advs = [f.getlength(ch) for ch in text]
    ascent, descent = f.getmetrics()
    pad = 6
    w = int(sum(advs) + tracking * size * (len(text) - 1)) + 2 * pad
    img = Image.new("RGBA", (w, ascent + descent + 2 * pad), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    x = pad
    for ch, adv in zip(text, advs):
        d.text((x, pad), ch, font=f, fill=tuple(color) + (255,))
        x += adv + tracking * size
    arr = np.array(img)
    ys = np.nonzero(arr[..., 3].max(axis=1) > 0)[0]
    return to_premul(arr[max(ys.min() - 2, 0): ys.max() + 3])


def drop_points(cx, cy, R, n=90):
    """JLM drop: pointed tip on top, round base. (cx, cy) = centre of the base
    circle, R its radius; the tip sits 1.9 R above the centre."""
    pts = []
    tip = np.array([0.0, -1.9 * R])
    side = np.array([R, 0.0])
    c1, c2 = np.array([0.30 * R, -1.50 * R]), np.array([R, -0.80 * R])
    for t in np.linspace(0, 1, n):  # right flank, tip → side
        p = (1 - t) ** 3 * tip + 3 * (1 - t) ** 2 * t * c1 + 3 * (1 - t) * t ** 2 * c2 + t ** 3 * side
        pts.append(p)
    for a in np.linspace(0, math.pi, n):  # base circle, right → left
        pts.append(np.array([R * math.cos(a), R * math.sin(a)]))
    for t in np.linspace(1, 0, n):  # left flank, side → tip
        p = (1 - t) ** 3 * tip + 3 * (1 - t) ** 2 * t * (c1 * [-1, 1]) + 3 * (1 - t) * t ** 2 * (c2 * [-1, 1]) + t ** 3 * (side * [-1, 1])
        pts.append(p)
    return [(cx + x, cy + y) for x, y in pts]


def drop_layer(R, color, stretch=1.0):
    """Anti-aliased drop sprite. Returns (premul, anchor) where anchor is the
    base-circle centre inside the sprite."""
    S = 4
    w, h = int(2 * R + 8), int(2.9 * R * stretch + 8)
    img = Image.new("L", (w * S, h * S), 0)
    cx, cy = w / 2 * S, (h - R - 4) * S
    pts = [(x, cy + (y - cy) * stretch) for x, y in drop_points(cx, cy, R * S)]
    ImageDraw.Draw(img).polygon(pts, fill=255)
    a = np.array(img.resize((w, h), Image.LANCZOS)).astype(np.float32)[..., None] / 255.0
    return np.concatenate([rgb01(color)[None, None, :] * a, a], axis=2), (w / 2, h - R - 4)


def box_frame(w, h, color, stroke=5):
    a = np.zeros((h, w), np.float32)
    a[:stroke], a[-stroke:], a[:, :stroke], a[:, -stroke:] = 1, 1, 1, 1
    return np.concatenate([rgb01(color)[None, None, :] * a[..., None], a[..., None]], axis=2)


def solid(w, h, color, alpha=1.0):
    out = np.zeros((h, w, 4), np.float32)
    out[..., :3] = rgb01(color) * alpha
    out[..., 3] = alpha
    return out


def paste_into(dst, src, x, y):
    """Premultiplied over, inside a premultiplied layer."""
    h, w = src.shape[:2]
    region = dst[y: y + h, x: x + w]
    region *= 1 - src[..., 3:4]
    region += src


def headline_box(typer, lines, tag):
    """ATL headline: yellow 5 px frame, Arabic headline inside, and a solid
    yellow tag with the product name hanging off its bottom-left corner
    (the template's bottom-right, mirrored for right-to-left reading)."""
    rendered = [typer.line(runs, 84, shadow=False, pad=0) for runs in lines]
    tw = max(r.shape[1] for r in rendered)
    line_h = 104
    padx, pady = 46, 26
    bw = min(tw + 2 * padx, W - 80)
    bh = line_h * len(rendered) + 2 * pady
    tag_layer = None
    th = 0
    if tag:
        txt = latin_layer(tag, 34, sb.CHARCOAL, 800, 0.06)
        th = txt.shape[0] + 24
        tag_layer = solid(txt.shape[1] + 40, th, sb.YELLOW)
        paste_into(tag_layer, txt, 20, 12)
    total_h = bh + (th - 6 if tag else 0)
    out = np.zeros((total_h, bw, 4), np.float32)
    paste_into(out, box_frame(bw, bh, sb.YELLOW), 0, 0)
    y = pady
    for r in rendered:
        paste_into(out, r, (bw - r.shape[1]) // 2, y + (line_h - r.shape[0]) // 2)
        y += line_h
    if tag_layer is not None:
        tw2 = min(tag_layer.shape[1], bw)
        paste_into(out, tag_layer[:, :tw2], 0, bh - 6)
    return out, bh


def chip(typer, text, size=40):
    """Dark pill, thin yellow outline, light Arabic text."""
    txt = typer.line([(text, sb.WHITE)], size, bold=False, shadow=False, pad=0)
    th, tw = txt.shape[:2]
    padx, pady = 34, 16
    w, h = tw + 2 * padx, th + 2 * pady - 10
    S = 3
    img = Image.new("RGBA", (w * S, h * S), (0, 0, 0, 0))
    ImageDraw.Draw(img).rounded_rectangle([S, S, w * S - S, h * S - S], radius=h * S // 2,
                                          fill=sb.CHARCOAL_2 + (235,), outline=sb.YELLOW + (255,), width=2 * S)
    pill = to_premul(np.array(img.resize((w, h), Image.LANCZOS)))
    paste_into(pill, txt, padx, (h - th) // 2 - 3)
    return pill


def badge(typer, text, size=44):
    """Solid charcoal pill with yellow text and a delivery truck (facing left)."""
    ink = sb.YELLOW
    txt = typer.line([(text, ink)], size, bold=True, shadow=False, pad=0)
    th, tw = txt.shape[:2]
    S = 4
    icon_w, gap, padx, pady = 74, 22, 40, 18
    w, h = tw + icon_w + gap + 2 * padx, th + 2 * pady - 8
    img = Image.new("RGBA", (w * S, h * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, w * S - 1, h * S - 1], radius=h * S // 2, fill=sb.CHARCOAL + (255,),
                        outline=sb.YELLOW + (255,), width=2 * S)
    ix, iy, u = (w - padx - icon_w) * S, (h // 2 - 22) * S, S
    bg = sb.CHARCOAL
    d.rounded_rectangle([ix + 26 * u, iy + 2 * u, ix + 72 * u, iy + 32 * u], radius=4 * u, fill=ink + (255,))
    d.polygon([(ix + 26 * u, iy + 10 * u), (ix + 10 * u, iy + 10 * u), (ix + 2 * u, iy + 21 * u),
               (ix + 2 * u, iy + 32 * u), (ix + 26 * u, iy + 32 * u)], fill=ink + (255,))
    d.polygon([(ix + 22 * u, iy + 14 * u), (ix + 12 * u, iy + 14 * u), (ix + 7 * u, iy + 21 * u),
               (ix + 22 * u, iy + 21 * u)], fill=bg + (255,))
    for wx in (14, 56):
        d.ellipse([ix + (wx - 8) * u, iy + 26 * u, ix + (wx + 8) * u, iy + 42 * u], fill=ink + (255,))
        d.ellipse([ix + (wx - 3) * u, iy + 31 * u, ix + (wx + 3) * u, iy + 37 * u], fill=bg + (255,))
    pill = to_premul(np.array(img.resize((w, h), Image.LANCZOS)))
    paste_into(pill, txt, padx, (h - th) // 2 - 4)
    return pill


def image_layer(path, width):
    im = Image.open(path).convert("RGBA")
    im = im.resize((width, int(im.height * width / im.width)), Image.LANCZOS)
    return to_premul(np.array(im))


# ---------------------------------------------------------- background ------
class Backdrop:
    """Charcoal with the JLM gear pattern, drifting slowly (parallax pan)."""

    def __init__(self, gears_path):
        g = np.array(Image.open(gears_path)).astype(np.float32) / 255.0
        scale = H * 1.08 / g.shape[0]
        g = cv2.resize(g, (int(g.shape[1] * scale), int(g.shape[0] * scale)), interpolation=cv2.INTER_AREA)
        self.g = g
        base = rgb01(sb.CHARCOAL)
        lift = rgb01((58, 60, 63)) - base
        self.base = base[None, None, :]
        self.lift = lift[None, None, :]
        y = np.linspace(0, 1, H, dtype=np.float32)[:, None]
        x = np.linspace(0, 1, W, dtype=np.float32)[None, :]
        v = np.sqrt((x - 0.5) ** 2 * 1.2 + (y - 0.42) ** 2)
        self.vig = (1 - 0.35 * np.clip(v - 0.2, 0, 1))[..., None]
        d = np.sqrt(((x - 0.5) / 0.55) ** 2 + ((y - 0.45) / 0.32) ** 2)
        self.spot = (np.exp(-d ** 2 * 1.8) * 0.05)[..., None]

    def frame(self, t):
        span = self.g.shape[1] - W
        x0 = int(span * 0.25 + t * 9)
        y0 = int((self.g.shape[0] - H) / 2 + math.sin(t * 0.3) * 8)
        gm = self.g[y0: y0 + H, x0: x0 + W][..., None]
        f = self.base + self.lift * gm * 0.9
        f = f + self.spot
        return f * self.vig


def ecg_y(x, base_y, spikes, amp=1.0):
    """Heartbeat trace (P-QRS-T per spike), drawn right-to-left."""
    y = np.full_like(x, base_y, dtype=np.float32)
    for sx in spikes:
        u = (sx - x) / 46.0
        y -= 16 * amp * np.exp(-((u + 1.9) ** 2) / 0.12)
        y += 22 * amp * np.exp(-((u - 0.0) ** 2) / 0.012)
        y -= 150 * amp * np.exp(-((u - 0.32) ** 2) / 0.018)
        y += 60 * amp * np.exp(-((u - 0.68) ** 2) / 0.02)
        y -= 30 * amp * np.exp(-((u - 2.0) ** 2) / 0.22)
    return y


def draw_trace(frame, xs, ys, alpha_along, width=4.0, glow=1.0):
    if len(xs) < 2:
        return
    x0, x1 = int(max(xs.min() - 60, 0)), int(min(xs.max() + 60, W))
    y0, y1 = int(max(ys.min() - 60, 0)), int(min(ys.max() + 60, H))
    if x1 <= x0 or y1 <= y0:
        return
    canvas = np.zeros((y1 - y0, x1 - x0), np.float32)
    pts = np.stack([(xs - x0) * 4, (ys - y0) * 4], axis=1).astype(np.int32)
    for i in range(len(pts) - 1):
        a = float(alpha_along[i])
        if a > 0.01:
            cv2.line(canvas, tuple(pts[i]), tuple(pts[i + 1]), a, int(width), cv2.LINE_AA, shift=2)
    yellow = rgb01(sb.YELLOW)[None, None, :]
    core = canvas[..., None]
    halo = cv2.GaussianBlur(canvas, (0, 0), 9)[..., None] * 0.9 * glow
    region = frame[y0:y1, x0:x1]
    region *= 1 - np.clip(core, 0, 1)
    region += core * yellow + halo * yellow * 0.6


def build_glow(radius, color, strength):
    s = int(radius * 2)
    yy, xx = np.mgrid[0:s, 0:s].astype(np.float32)
    d = np.hypot(xx - s / 2, yy - s / 2) / radius
    return (np.exp(-(d ** 2) * 3.2) * strength)[..., None] * rgb01(color)[None, None, :]


# ------------------------------------------------------------------ film ----
class Film:
    def __init__(self, assets, fonts):
        self.assets = Path(assets)
        brand = self.assets / "brand"
        self.T = Type(fonts)
        self.bg = Backdrop(brand / "gears.png")
        self.trans = sb.transitions()
        self.logo_footer = image_layer(brand / "logo_on_yellow.png", 360)
        self.logo_dark = image_layer(brand / "logo_on_dark.png", 520)
        self.nl = image_layer(brand / "made_in_nl.png", 360)
        self.url_footer = latin_layer("jlmstore.com", 30, sb.CHARCOAL, 700, 0.03)
        self.drop_big, self.drop_big_anchor = drop_layer(52, sb.YELLOW)
        self.drop_fall, self.drop_fall_anchor = drop_layer(30, sb.YELLOW, stretch=1.25)
        self.glow = build_glow(420, sb.WHITE, 0.07)
        self._build_text()
        self._build_products()

    def _build_text(self):
        T = self.T
        self.hook_box, self.hook_bh = headline_box(T, [sb.HOOK["headline"]], None)
        self.hook_sub = T.line([(sb.HOOK["sub"], sb.WHITE)], 58, bold=False)
        self.scenes = []
        for p in sb.PRODUCTS:
            box, bh = headline_box(T, p["headline"], p["tag"])
            self.scenes.append({"box": box, "chips": [chip(T, c) for c in p["chips"]]})
        e = sb.END
        self.end_box, _ = headline_box(T, [[(e["line1"], sb.WHITE)]], None)
        self.end = {
            "url": latin_layer(e["url"], 112, sb.YELLOW, 900, 0.0),
            "line2": T.line([(e["line2"], sb.WHITE)], 52, bold=False),
            "line3": T.line([(e["line3"], sb.WHITE)], 52, bold=False),
            "badge": badge(T, e["badge"]),
        }

    def _build_products(self):
        self.products = []
        for p in sb.PRODUCTS:
            im = Image.open(self.assets / p["asset"]).convert("RGBA")
            hi = int(p["height"] * 1.1)
            im = im.resize((int(im.width * hi / im.height), hi), Image.LANCZOS)
            arr = to_premul(np.array(im))
            ref = arr[::-1].copy()
            fade = np.clip(1 - np.arange(ref.shape[0]) / (130 * 1.1), 0, 1) ** 1.6 * 0.16
            ref = cv2.GaussianBlur(ref * fade[:, None, None], (0, 0), 2.0)
            self.products.append({"img": arr, "ref": ref, "base_scale": p["height"] / hi})
        self.lineup = []
        for p, h in zip(sb.PRODUCTS, (380, 380, 410, 430)):
            im = Image.open(self.assets / p["asset"]).convert("RGBA")
            im = im.resize((int(im.width * h / im.height), h), Image.LANCZOS)
            arr = to_premul(np.array(im))
            ref = arr[::-1].copy() * (np.clip(1 - np.arange(h) / 70, 0, 1) ** 1.6 * 0.14)[:, None, None]
            self.lineup.append((arr, cv2.GaussianBlur(ref, (0, 0), 1.4)))

    # ---- helpers
    def centered(self, f, layer, cy, alpha=1.0, dx=0.0, dy=0.0):
        h, w = layer.shape[:2]
        over(f, layer, (W - w) / 2 + dx, cy - h / 2 + dy, alpha)

    def box_in(self, f, box, top, p_in, p_out):
        """Headline box: frame grows from the centre line, text wipes RTL."""
        if p_in <= 0 or p_out >= 1:
            return
        h, w = box.shape[:2]
        layer = rtl_reveal(box, ease_out(p_in), soft=140)
        over(f, layer, (W - w) / 2, top - (1 - p_in) * 24 - p_out * 30, 1 - p_out)

    def light_sweep(self, layer, p):
        if not 0 < p < 1:
            return layer
        h, w = layer.shape[:2]
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        pos = (1 - p) * (w + h) - h * 0.3
        band = np.exp(-(((xx + yy * 0.45) - pos) / (w * 0.10)) ** 2) * 0.40
        out = layer.copy()
        out[..., :3] += band[..., None] * layer[..., 3:4]
        return out

    # ---- footer + drop
    def draw_footer(self, f, t):
        rise = ease_out((t - 0.05) / 0.55)
        top = int(sb.FOOTER_Y + (1 - rise) * (H - sb.FOOTER_Y + 120))
        # landing pulse: the footer's drop swells for a moment at every cut
        pulse = max([math.exp(-((t - tt) / 0.09) ** 2) for tt in self.trans] + [0.0])
        if top < H:
            f[top:H] = rgb01(sb.YELLOW)
            # drop sitting on the band's top edge
            R = 52 * (1 + 0.18 * pulse)
            d, (ax, ay) = (self.drop_big, self.drop_big_anchor) if pulse < 0.02 else drop_layer(R, sb.YELLOW)
            over(f, d, W / 2 - ax, top + 18 - ay)
            ly = top + 58
            over(f, self.logo_footer, (W - self.logo_footer.shape[1]) / 2, ly)
            over(f, self.url_footer, (W - self.url_footer.shape[1]) / 2, ly + self.logo_footer.shape[0] + 18)
            # ripple rings on the band edge after a landing
            for tt in self.trans:
                lt = t - tt
                if 0 <= lt < 0.6:
                    r = 60 + lt * 520
                    a = (1 - lt / 0.6) ** 2 * 0.8
                    canvas = np.zeros((90, W), np.float32)
                    cv2.ellipse(canvas, (W // 2, 45), (int(r), int(r * 0.12)), 0, 180, 360, a, 3, cv2.LINE_AA)
                    y0 = top - 45
                    if 0 <= y0 < H - 90:
                        f[y0:y0 + 90] += canvas[..., None] * rgb01(sb.YELLOW)[None, None, :] * 0.9

    def draw_falling_drop(self, f, t):
        for tt in self.trans:
            p = (t - (tt - 0.42)) / 0.42
            if 0 <= p < 1:
                y = -120 + (sb.FOOTER_Y + 10 + 120) * p * p   # gravity
                d, (ax, ay) = self.drop_fall, self.drop_fall_anchor
                # short motion trail
                for k, a in ((3, 0.18), (2, 0.3), (1, 0.5)):
                    yk = -120 + (sb.FOOTER_Y + 130) * max(p - k * 0.035, 0) ** 2
                    over(f, d, W / 2 - ax, yk - ay, a)
                over(f, d, W / 2 - ax, y - ay)

    # ---- scenes
    def draw_hook(self, f, t):
        if t > sb.HOOK_END + 0.1:
            return
        out = ease_in_out((t - (sb.HOOK_END - 0.35)) / 0.3)
        vis = 1 - out
        head = 1100 - (t / 1.6) * 1120 if t < 1.6 else -20
        breath = 0.8 + 0.5 * sum(math.exp(-((t - tb) / 0.12) ** 2) for tb in (0.49, 1.11, 2.09))
        xs = np.arange(max(int(head), -20), W + 20, 4, dtype=np.float32)
        ys = ecg_y(xs, 860, [760, 320], amp=1.0)
        alpha = np.clip((xs - head) / 40, 0, 1) * vis * min(breath, 1.0)
        draw_trace(f, xs, ys, alpha, width=4.5, glow=breath)
        if t < 1.7:
            hy = int(ecg_y(np.array([head], np.float32), 860, [760, 320])[0])
            gl = build_glow(60, sb.YELLOW, 0.8)
            f[max(hy - 60, 0):hy + 60, max(int(head) - 60, 0):int(head) + 60] += gl[:min(120, H), :][
                max(60 - hy, 0):, max(60 - int(head), 0):][:f[max(hy - 60, 0):hy + 60, max(int(head) - 60, 0):int(head) + 60].shape[0],
                :f[max(hy - 60, 0):hy + 60, max(int(head) - 60, 0):int(head) + 60].shape[1]]
        pin = clamp01((t - 0.2) / 0.6)
        self.box_in(f, self.hook_box, sb.HEADLINE_Y - self.hook_box.shape[0] / 2, pin, out)
        p2 = ease_out((t - 1.15) / 0.5)
        self.centered(f, rtl_reveal(self.hook_sub, p2), 1150, vis, dy=(1 - p2) * 18)

    def draw_product_scene(self, f, t, i):
        s0 = sb.HOOK_END + i * sb.SCENE_LEN
        s1 = s0 + sb.SCENE_LEN
        if not (s0 - 0.05 <= t <= s1 + 0.05):
            return
        sc, pr = self.scenes[i], self.products[i]
        lt = t - s0
        pin = ease_out(lt / 0.55)
        pout = ease_in_out((t - (s1 - 0.3)) / 0.3)
        vis = pin * (1 - pout)

        add = self.glow
        f[820 - add.shape[0] // 2: 820 + add.shape[0] // 2, W // 2 - add.shape[1] // 2: W // 2 + add.shape[1] // 2] += add * vis

        scale = pr["base_scale"] * (0.92 + 0.08 * pin + 0.03 * clamp01(lt / sb.SCENE_LEN))
        img = self.light_sweep(pr["img"], (lt - 0.6) / 0.8)
        h, w = img.shape[:2]
        cx = W / 2
        cy = sb.PRODUCT_BOTTOM + (1 - pin) * 90 + pout * 60
        layer, x, y = warp_premul(img, scale, cx, cy, (w / 2, h))
        over(f, layer, x, y, vis)
        rl, rx, ry = warp_premul(pr["ref"], scale, cx, cy, (w / 2, 0))
        over(f, rl, rx, ry + 2, vis)

        bin_ = clamp01((lt - 0.15) / 0.6)
        self.box_in(f, sc["box"], sb.HEADLINE_Y - 90, bin_, pout)

        chips = sc["chips"]
        gap = 22
        total = sum(c.shape[1] for c in chips) + gap * (len(chips) - 1)
        x = (W + total) / 2
        for k, c in enumerate(chips):
            cin = ease_out((lt - 0.75 - 0.18 * k) / 0.45)
            x -= c.shape[1]
            over(f, c, x, sb.CHIPS_Y - c.shape[0] / 2 + (1 - cin) * 20, cin * (1 - pout))
            x -= gap

    def draw_end(self, f, t):
        s0 = sb.END_START
        if t < s0 - 0.05:
            return
        lt = t - s0
        self.box_in(f, self.end_box, 130, clamp01((lt - 0.05) / 0.5), 0)
        p = ease_out((lt - 0.35) / 0.5)
        url = self.end["url"]
        if p > 0:
            layer, ux, uy = warp_premul(url, 0.94 + 0.06 * p + 0.01 * math.sin(max(lt - 1, 0) * 4),
                                        W / 2, 370, (url.shape[1] / 2, url.shape[0] / 2))
            over(f, layer, ux, uy, p)

        arrs = self.lineup
        gap = 30
        total = sum(a.shape[1] for a, _ in arrs) + gap * (len(arrs) - 1)
        x = (W - total) / 2
        base = 900
        for k, (a, ref) in enumerate(arrs):
            pk = ease_out((lt - 0.1 - 0.08 * k) / 0.55)
            over(f, a, x, base - a.shape[0] + (1 - pk) * 60, pk)
            over(f, ref, x, base + 2 + (1 - pk) * 60, pk)
            x += a.shape[1] + gap

        p3 = ease_out((lt - 0.9) / 0.5)
        self.centered(f, rtl_reveal(self.end["line2"], p3), 1010, 1, dy=(1 - p3) * 18)
        p4 = ease_out((lt - 1.15) / 0.5)
        self.centered(f, rtl_reveal(self.end["line3"], p4), 1080, 1, dy=(1 - p4) * 18)
        p5 = ease_out((lt - 1.5) / 0.45)
        b = self.end["badge"]
        if p5 > 0:
            layer, bx, by = warp_premul(b, 0.85 + 0.15 * p5, W / 2, 1210, (b.shape[1] / 2, b.shape[0] / 2))
            over(f, layer, bx, by, p5)
        p6 = ease_out((lt - 1.9) / 0.45)
        self.centered(f, self.nl, 1350, p6, dy=(1 - p6) * 16)

    def frame(self, t):
        f = self.bg.frame(t).astype(np.float32)
        self.draw_hook(f, t)
        for i in range(len(sb.PRODUCTS)):
            self.draw_product_scene(f, t, i)
        self.draw_end(f, t)
        self.draw_falling_drop(f, t)
        self.draw_footer(f, t)
        f *= ease_out(t / 0.3)
        return np.clip(f, 0, 1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--assets", required=True)
    ap.add_argument("--fonts", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--stills", help="comma-separated seconds; writes PNGs instead of a video")
    args = ap.parse_args()

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    global ALBERT_PATH
    ALBERT_PATH = Path(args.fonts) / "AlbertSans.ttf"
    film = Film(args.assets, args.fonts)

    if args.stills:
        want = sorted(float(s) for s in args.stills.split(","))
        last = int(max(want) * FPS)
        targets = {int(round(s * FPS)): s for s in want}
        for n in range(last + 1):
            img = film.frame(n / FPS)  # particles need the full history
            if n in targets:
                path = out.parent / f"still_{targets[n]:05.2f}.png"
                cv2.imwrite(str(path), cv2.cvtColor((img * 255).astype(np.uint8), cv2.COLOR_RGB2BGR))
                print("wrote", path)
        return

    wav = out.with_suffix(".wav")
    soundtrack.write(wav, sb.DURATION, sb.transitions(), sb.END_START)
    cmd = ["ffmpeg", "-y", "-loglevel", "error",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-i", str(wav),
           "-c:v", "libx264", "-preset", "slow", "-crf", "16", "-pix_fmt", "yuv420p",
           "-profile:v", "high", "-tune", "film",
           "-af", "loudnorm=I=-14:TP=-1.5:LRA=9,alimiter=limit=0.7:level=false",
           "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
           "-movflags", "+faststart", "-shortest", str(out)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for n in range(N_FRAMES):
        img = film.frame(n / FPS)
        # light dither before quantising so the dark gradients don't band
        img = img + (np.random.default_rng(n).random(img.shape, dtype=np.float32) - 0.5) / 255.0
        proc.stdin.write((np.clip(img, 0, 1) * 255 + 0.5).astype(np.uint8).tobytes())
        if n % 60 == 0:
            print(f"frame {n}/{N_FRAMES}", file=sys.stderr, flush=True)
    proc.stdin.close()
    proc.wait()
    wav.unlink(missing_ok=True)
    print("wrote", out)


if __name__ == "__main__":
    main()
