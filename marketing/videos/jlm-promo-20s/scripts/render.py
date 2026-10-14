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


def chip(typer, text, size=40):
    """Outlined gold pill with silver text."""
    txt = typer.line([(text, sb.SILVER)], size, bold=False, shadow=False, pad=0)
    th, tw = txt.shape[:2]
    padx, pady = 34, 16
    w, h = tw + 2 * padx, th + 2 * pady - 10
    S = 3  # supersample the pill outline
    img = Image.new("RGBA", (w * S, h * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([S, S, w * S - S, h * S - S], radius=h * S // 2,
                        fill=sb.GRAPHITE + (150,), outline=sb.GOLD + (235,), width=2 * S)
    img = img.resize((w, h), Image.LANCZOS)
    pill = to_premul(np.array(img))
    y = (h - th) // 2 - 3
    region = pill[y: y + th, padx: padx + tw]
    region *= 1 - txt[..., 3:4]
    region += txt
    return pill


def badge(typer, text, size=46):
    """Solid gold pill with a drawn delivery-truck icon (dark ink)."""
    ink = sb.GRAPHITE
    txt = typer.line([(text, ink)], size, bold=True, shadow=False, pad=0)
    th, tw = txt.shape[:2]
    S = 4
    icon_w, gap, padx, pady = 74, 22, 40, 18
    w, h = tw + icon_w + gap + 2 * padx, th + 2 * pady - 8
    img = Image.new("RGBA", (w * S, h * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, w * S - 1, h * S - 1], radius=h * S // 2, fill=sb.GOLD + (255,))
    # truck, facing left (RTL reading direction), at the right end of the pill
    ix, iy = (w - padx - icon_w) * S, (h // 2 - 22) * S
    u = S
    d.rounded_rectangle([ix + 26 * u, iy + 2 * u, ix + 72 * u, iy + 32 * u], radius=4 * u, fill=ink + (255,))
    d.polygon([(ix + 26 * u, iy + 10 * u), (ix + 10 * u, iy + 10 * u), (ix + 2 * u, iy + 21 * u),
               (ix + 2 * u, iy + 32 * u), (ix + 26 * u, iy + 32 * u)], fill=ink + (255,))
    d.polygon([(ix + 22 * u, iy + 14 * u), (ix + 12 * u, iy + 14 * u), (ix + 7 * u, iy + 21 * u),
               (ix + 22 * u, iy + 21 * u)], fill=sb.GOLD + (255,))
    for wx in (14, 56):
        d.ellipse([ix + (wx - 8) * u, iy + 26 * u, ix + (wx + 8) * u, iy + 42 * u], fill=ink + (255,))
        d.ellipse([ix + (wx - 3) * u, iy + 31 * u, ix + (wx + 3) * u, iy + 37 * u], fill=sb.GOLD + (255,))
    img = img.resize((w, h), Image.LANCZOS)
    pill = to_premul(np.array(img))
    y = (h - th) // 2 - 4
    region = pill[y: y + th, padx: padx + tw]
    region *= 1 - txt[..., 3:4]
    region += txt
    return pill


def logo_layer(mask_path, width, color):
    m = Image.open(mask_path)
    m = m.resize((width, int(m.height * width / m.width)), Image.LANCZOS)
    a = np.array(m).astype(np.float32)[..., None] / 255.0
    return np.concatenate([rgb01(color)[None, None, :] * a, a], axis=2)


# ------------------------------------------------------------- background ---
def build_background():
    rng = np.random.default_rng(7)
    y = np.linspace(0, 1, H, dtype=np.float32)[:, None]
    x = np.linspace(0, 1, W, dtype=np.float32)[None, :]
    base = rgb01(sb.GRAPHITE)[None, None, :] * np.ones((H, W, 1), np.float32)
    # soft overhead light behind the product zone
    d = np.sqrt(((x - 0.5) / 0.62) ** 2 + ((y - 0.42) / 0.36) ** 2)
    spot = np.exp(-d ** 2 * 1.6)[..., None]
    base += (rgb01(sb.STEEL) - rgb01(sb.GRAPHITE)) * spot * 1.25
    # brushed-metal grain: noise smeared horizontally
    n = rng.standard_normal((H, W)).astype(np.float32)
    n = cv2.GaussianBlur(n, (0, 0), sigmaX=40, sigmaY=0.6)
    base += (n / (n.std() + 1e-6) * 0.006)[..., None]
    # vignette
    v = np.sqrt((x - 0.5) ** 2 * 1.4 + (y - 0.5) ** 2)
    base *= (1 - 0.55 * np.clip(v - 0.25, 0, 1) ** 1.5)[..., None]
    return np.clip(base, 0, 1)


def build_glow(radius, color, strength):
    s = int(radius * 2)
    yy, xx = np.mgrid[0:s, 0:s].astype(np.float32)
    d = np.hypot(xx - s / 2, yy - s / 2) / radius
    g = np.exp(-(d ** 2) * 3.2) * strength
    return g[..., None] * rgb01(color)[None, None, :]


def build_floor():
    """A thin silver horizon line the products stand on."""
    x = np.linspace(-1, 1, W, dtype=np.float32)
    fade = np.exp(-(x ** 2) * 2.2)
    line = np.zeros((9, W, 3), np.float32)
    prof = np.exp(-((np.arange(9) - 4) ** 2) / 2.5)[:, None]
    line += (prof * fade[None, :])[..., None] * rgb01(sb.SILVER)[None, None, :] * 0.16
    return line


# ---------------------------------------------- algorithmic-art flow field ---
class OilFlow:
    """Seeded flow field of fine gold particles leaving fading trails.
    Runs at half resolution; a surge parameter pushes the flow right-to-left
    during scene transitions so the oil 'carries' the cut."""

    def __init__(self, n=1500, seed=11):
        self.rng = np.random.default_rng(seed)
        self.w, self.h = W // 2, H // 2
        self.p = self.rng.random((n, 2)).astype(np.float32) * [self.w, self.h]
        self.buf = np.zeros((self.h, self.w), np.float32)

    def field(self, p, t):
        x, y = p[:, 0], p[:, 1]
        a = (np.sin(x * 0.011 + t * 0.35) + np.cos(y * 0.009 - t * 0.27)
             + 0.6 * np.sin((x + y) * 0.006 + 1.7)) * math.pi * 0.55 + math.pi
        return np.stack([np.cos(a), np.sin(a)], axis=1)

    def step(self, t, surge):
        v = self.field(self.p, t) * (0.9 + 0.4 * surge)
        v[:, 0] -= surge * 9.0  # right-to-left rush
        p0 = self.p.copy()
        self.p += v
        self.buf *= 0.88 if surge < 0.05 else 0.8
        steps = 3
        for k in range(1, steps + 1):  # splat along the segment for streaks
            q = p0 + (self.p - p0) * (k / steps)
            xi = np.clip(q[:, 0].astype(int), 0, self.w - 1)
            yi = np.clip(q[:, 1].astype(int), 0, self.h - 1)
            np.add.at(self.buf, (yi, xi), 0.32 / steps * (1 + surge * 2))
        out = (self.p[:, 0] < -4) | (self.p[:, 0] > self.w + 4) | (self.p[:, 1] < -4) | (self.p[:, 1] > self.h + 4)
        respawn = out | (self.rng.random(len(self.p)) < 0.004)
        k = int(respawn.sum())
        if k:
            self.p[respawn] = self.rng.random((k, 2)).astype(np.float32) * [self.w, self.h]
            if surge > 0.05:  # during a rush new particles enter from the right
                self.p[respawn, 0] = self.w + self.rng.random(k) * 20

    def light(self):
        b = cv2.GaussianBlur(self.buf, (0, 0), 0.9)
        b = cv2.resize(b, (W, H), interpolation=cv2.INTER_LINEAR)
        return np.clip(b, 0, 1.2)[..., None] * rgb01(sb.GOLD)[None, None, :]


# ------------------------------------------------------------ pulse line ----
def ecg_y(x, base_y, spikes, amp=1.0):
    """Heartbeat trace: flat line with a P-QRS-T complex at each spike x.
    Drawn right-to-left, so each complex is mirrored in x."""
    y = np.full_like(x, base_y, dtype=np.float32)
    for sx in spikes:
        u = (sx - x) / 46.0  # positive to the left of the spike
        y -= 16 * amp * np.exp(-((u + 1.9) ** 2) / 0.12)   # P
        y += 22 * amp * np.exp(-((u - 0.0) ** 2) / 0.012)  # Q
        y -= 150 * amp * np.exp(-((u - 0.32) ** 2) / 0.018)  # R
        y += 60 * amp * np.exp(-((u - 0.68) ** 2) / 0.02)   # S
        y -= 30 * amp * np.exp(-((u - 2.0) ** 2) / 0.22)   # T
    return y


def draw_trace(frame, xs, ys, alpha_along, width=3.0, glow=1.0):
    """Draw a glowing gold polyline whose opacity varies along its length."""
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
    core = canvas[..., None] * rgb01(sb.GOLD_HI)[None, None, :]
    halo = cv2.GaussianBlur(canvas, (0, 0), 10)[..., None] * rgb01(sb.GOLD)[None, None, :] * 1.6 * glow
    frame[y0:y1, x0:x1] += core + halo


# ------------------------------------------------------------------ film ----
class Film:
    def __init__(self, assets, fonts):
        self.assets = Path(assets)
        self.T = Type(fonts)
        self.bg = build_background()
        self.floor = build_floor()
        self.glow = build_glow(430, sb.SILVER, 0.10)
        self.glow_gold = build_glow(380, sb.GOLD, 0.07)
        self.flow = OilFlow()
        self.logo = logo_layer(self.assets / "jlm_logo_mask.png", 230, sb.WHITE)
        self.trans = sb.transitions()
        self._build_text()
        self._build_products()

    # ---- assets
    def _build_text(self):
        T = self.T
        self.hook_head = T.line(sb.HOOK["headline"], 108)
        self.hook_sub = T.line([(sb.HOOK["sub"], sb.SILVER)], 58, bold=False)
        self.scenes = []
        for p in sb.PRODUCTS:
            self.scenes.append({
                "tag": T.latin(p["tag"], 32, sb.SILVER, tracking=0.16),
                "watermark": T.outline(p["watermark"], 330, sb.SILVER, stroke=3),
                "headline": [T.line(runs, 96) for runs in p["headline"]],
                "chips": [chip(T, c) for c in p["chips"]],
            })
        e = sb.END
        self.end = {
            "line1": T.line([(e["line1"], sb.WHITE)], 70),
            "url": T.latin(e["url"], 104, sb.GOLD_HI, tracking=0.01),
            "line2": T.line([(e["line2"], sb.SILVER)], 52, bold=False),
            "line3": T.line([(e["line3"], sb.SILVER)], 52, bold=False),
            "badge": badge(T, e["badge"]),
        }

    def _build_products(self):
        self.products = []
        for p in sb.PRODUCTS:
            im = Image.open(self.assets / p["asset"]).convert("RGBA")
            hi = int(p["height"] * 1.12)  # headroom for the slow push-in
            im = im.resize((int(im.width * hi / im.height), hi), Image.LANCZOS)
            arr = to_premul(np.array(im))
            # reflection: flipped, blurred, fading out over 170 px
            ref = arr[::-1].copy()
            fade = np.clip(1 - np.arange(ref.shape[0]) / (170 * 1.12), 0, 1) ** 1.6 * 0.20
            ref *= fade[:, None, None]
            ref = cv2.GaussianBlur(ref, (0, 0), 2.2)
            self.products.append({"img": arr, "ref": ref, "base_scale": p["height"] / hi})
        # end-card lineup (smaller copies)
        self.lineup = []
        for p, h in zip(sb.PRODUCTS, (450, 450, 490, 510)):
            im = Image.open(self.assets / p["asset"]).convert("RGBA")
            im = im.resize((int(im.width * h / im.height), h), Image.LANCZOS)
            arr = to_premul(np.array(im))
            ref = arr[::-1].copy() * (np.clip(1 - np.arange(h) / 90, 0, 1) ** 1.6 * 0.18)[:, None, None]
            self.lineup.append((arr, cv2.GaussianBlur(ref, (0, 0), 1.6)))

    # ---- helpers
    def surge(self, t):
        return max(math.exp(-((t - tt + 0.05) / 0.16) ** 2) for tt in self.trans)

    def centered(self, frame, layer, cy, alpha=1.0, dx=0.0, dy=0.0):
        h, w = layer.shape[:2]
        over(frame, layer, (W - w) / 2 + dx, cy - h / 2 + dy, alpha)

    def sweep_streak(self, frame, t):
        """Gold pulse racing right-to-left across the frame at each cut."""
        for tt in self.trans:
            p = (t - (tt - 0.32)) / 0.5
            if not 0 <= p <= 1:
                continue
            head = 1180 - ease_in_out(p) * 1380
            xs = np.arange(int(max(head, -100)), W + 140, 6, dtype=np.float32)
            ys = ecg_y(xs, 860, [head + 70], amp=0.55)
            dist = xs - head
            alpha = np.exp(-dist / 380) * (1 - p ** 3)
            draw_trace(frame, xs, ys, alpha, width=3.2, glow=1.2)
            # flash at the head
            fl = build_glow(90, sb.GOLD_HI, 0.55 * (1 - p))
            add_light(frame, fl, int(head - 90), 860 - 90)

    def light_sweep(self, layer, p):
        """Diagonal specular band crossing a product (masked by its alpha)."""
        if not 0 < p < 1:
            return layer
        h, w = layer.shape[:2]
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        pos = (1 - p) * (w + h) * 1.0 - h * 0.3  # right-to-left
        band = np.exp(-(((xx + yy * 0.45) - pos) / (w * 0.10)) ** 2) * 0.45
        out = layer.copy()
        out[..., :3] += band[..., None] * layer[..., 3:4]
        return out

    # ---- scenes
    def draw_hook(self, f, t):
        if t > sb.HOOK_END + 0.1:
            return
        out = ease_in_out((t - (sb.HOOK_END - 0.3)) / 0.3)
        vis = 1 - out
        # heartbeat trace drawn right-to-left, beats at 0.49 s and 1.11 s
        # constant-speed monitor sweep: the R peaks pass at 0.49 s and 1.11 s,
        # exactly on the heartbeat sounds (soundtrack.write)
        head = 1100 - (t / 1.6) * 1120 if t < 1.6 else -20
        breath = 0.8 + 0.5 * sum(math.exp(-((t - tb) / 0.12) ** 2) for tb in (0.49, 1.11, 2.09))
        xs = np.arange(max(int(head), -20), W + 20, 4, dtype=np.float32)
        ys = ecg_y(xs, 860, [760, 320], amp=1.0)
        alpha = np.clip((xs - head) / 40, 0, 1) * vis * breath
        draw_trace(f, xs, ys, alpha, width=3.4, glow=1.0)
        if t < 1.7:
            add_light(f, build_glow(70, sb.GOLD_HI, 0.6), int(head - 70), int(ecg_y(np.array([head], np.float32), 860, [760, 320])[0]) - 70)
        pin, _ = window(t, 0.25, sb.HOOK_END, d_in=0.55)
        self.centered(f, rtl_reveal(self.hook_head, pin), 650, vis, dy=(1 - pin) * 24)
        pin2, _ = window(t, 1.15, sb.HOOK_END, d_in=0.5)
        self.centered(f, rtl_reveal(self.hook_sub, pin2), 1090, vis, dy=(1 - pin2) * 18)

    def draw_product_scene(self, f, t, i):
        s0 = sb.HOOK_END + i * sb.SCENE_LEN
        s1 = s0 + sb.SCENE_LEN
        if not (s0 - 0.05 <= t <= s1 + 0.15):
            return
        sc, pr = self.scenes[i], self.products[i]
        lt = t - s0
        pin, pout = window(t, s0, s1 + 0.1, d_in=0.6, d_out=0.35)
        vis = pin * (1 - pout)

        # watermark drifting slowly behind the product
        wm = sc["watermark"]
        self.centered(f, wm, 760, 0.075 * vis, dx=60 - lt * 40 - pout * 120)

        # glow + floor
        g = self.glow
        add_light(f, g, W // 2 - g.shape[1] // 2, 820 - g.shape[0] // 2, vis)
        gg = self.glow_gold
        add_light(f, gg, W // 2 - gg.shape[1] // 2, sb.PRODUCT_BOTTOM - gg.shape[0] // 2 + 40, vis * 0.8)
        add_light(f, self.floor, 0, sb.PRODUCT_BOTTOM - 4, vis)

        # product: rise in, slow push-in, slide out left with the pulse
        scale = pr["base_scale"] * (0.94 + 0.06 * pin + 0.035 * clamp01(lt / sb.SCENE_LEN))
        img = pr["img"]
        img = self.light_sweep(img, (lt - 0.55) / 0.8)
        h, w = img.shape[:2]
        cx = W / 2 - pout * 160
        cy = sb.PRODUCT_BOTTOM + (1 - pin) * 70
        layer, x, y = warp_premul(img, scale, cx, cy, (w / 2, h))
        over(f, layer, x, y, vis)
        rlayer, rx, ry = warp_premul(pr["ref"], scale, cx, cy, (w / 2, 0))
        over(f, rlayer, rx, ry + 2, vis)

        # tag (Latin, above the product)
        tin, tout = window(t, s0 + 0.15, s1, d_in=0.5)
        self.centered(f, ltr_reveal(sc["tag"], tin), sb.TAG_Y, (1 - tout), dy=(1 - tin) * 12)

        # headline lines + chips (Arabic, lower third)
        y = sb.HEADLINE_Y
        for k, line in enumerate(sc["headline"]):
            hin, hout = window(t, s0 + 0.3 + 0.18 * k, s1, d_in=0.5)
            self.centered(f, rtl_reveal(line, hin), y, 1 - hout, dy=(1 - hin) * 26 - hout * 14)
            y += 112
        chips = sc["chips"]
        gap = 22
        total = sum(c.shape[1] for c in chips) + gap * (len(chips) - 1)
        x = (W + total) / 2  # RTL: first chip on the right
        cy = sb.CHIPS_Y + (len(sc["headline"]) - 1) * 70
        for k, c in enumerate(chips):
            cin, cout = window(t, s0 + 0.7 + 0.18 * k, s1, d_in=0.45)
            x -= c.shape[1]
            over(f, c, x, cy - c.shape[0] / 2 + (1 - cin) * 20, cin * (1 - cout))
            x -= gap

    def draw_end(self, f, t):
        s0 = sb.END_START
        if t < s0 - 0.05:
            return
        lt = t - s0
        # lineup of all four products, rising in one after another
        arrs = self.lineup
        gap = 26
        total = sum(a.shape[1] for a, _ in arrs) + gap * (len(arrs) - 1)
        x = (W - total) / 2
        base = 1030
        add_light(f, self.floor, 0, base - 4, ease_out(lt / 0.6))
        add_light(f, self.glow, W // 2 - self.glow.shape[1] // 2, 780 - self.glow.shape[0] // 2,
                  ease_out(lt / 0.6))
        for k, (a, ref) in enumerate(arrs):
            p = ease_out((lt - 0.08 * k) / 0.6)
            over(f, a, x, base - a.shape[0] + (1 - p) * 60, p)
            over(f, ref, x, base + 2 + (1 - p) * 60, p)
            x += a.shape[1] + gap

        e = self.end
        p1 = ease_out((lt - 0.30) / 0.5)
        self.centered(f, rtl_reveal(e["line1"], p1), 1140, 1, dy=(1 - p1) * 20)
        p2 = ease_out((lt - 0.55) / 0.6)
        pulse = 1 + 0.012 * math.sin(max(lt - 1.2, 0) * 4.2)
        url = e["url"]
        if p2 > 0:
            layer, ux, uy = warp_premul(url, pulse * (0.96 + 0.04 * p2), W / 2, 1258,
                                        (url.shape[1] / 2, url.shape[0] / 2))
            over(f, layer, ux, uy, p2)
            # gold underline drawing out from the centre
            uw = int(560 * ease_in_out((lt - 0.8) / 0.5))
            if uw > 2:
                f[1326:1329, W // 2 - uw // 2: W // 2 + uw // 2] = rgb01(sb.GOLD)
        p3 = ease_out((lt - 1.0) / 0.5)
        self.centered(f, rtl_reveal(e["line2"], p3), 1410, 1, dy=(1 - p3) * 18)
        p4 = ease_out((lt - 1.25) / 0.5)
        self.centered(f, rtl_reveal(e["line3"], p4), 1480, 1, dy=(1 - p4) * 18)
        p5 = ease_out((lt - 1.6) / 0.45)
        b = e["badge"]
        if p5 > 0:
            layer, bx, by = warp_premul(b, 0.85 + 0.15 * p5, W / 2, 1605, (b.shape[1] / 2, b.shape[0] / 2))
            over(f, layer, bx, by, p5)

    def frame(self, t):
        f = self.bg.copy()
        surge = self.surge(t)
        self.flow.step(t, surge)
        fl = self.flow.light()
        f += fl * 0.33
        self.draw_hook(f, t)
        for i in range(len(sb.PRODUCTS)):
            self.draw_product_scene(f, t, i)
        self.draw_end(f, t)
        self.sweep_streak(f, t)
        # persistent logo (moves into the end card at the same place)
        lp = ease_out((t - 0.1) / 0.6)
        self.centered(f, self.logo, sb.LOGO_Y + 40, lp * 0.95)
        # flash on each cut
        for tt in self.trans:
            fl_a = math.exp(-((t - tt) / 0.06) ** 2) * 0.10
            if fl_a > 0.003:
                f += fl_a * rgb01(sb.GOLD_HI)
        # opening fade from black
        f *= ease_out(t / 0.35)
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
