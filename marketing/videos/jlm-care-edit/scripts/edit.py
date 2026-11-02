"""JLM "العناية الدورية" — edit of the client's footage in the reference Reels style
(brand/jlm/VIDEO_STYLE.md) + an inside-the-engine animation + the 3D icons.

    python3 edit.py --src CLIENT_VIDEO --out ../out/jlm_care_edit.mp4 [--stills 1.5,5,...]
    python3 edit.py --anim-only --out ../out/jlm_engine_inside_anim.mp4

Layers per frame: graded footage (or animation) -> caption boxes -> badge icon ->
logo top-left -> end CTA + footer. Audio: the original voice, plus light SFX.
"""

import argparse
import math
import subprocess
import sys
import wave
from functools import lru_cache
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(ROOT / "marketing/videos/jlm-promo-20s/scripts"))
sys.path.insert(0, str(ROOT / "marketing/videos/jlm-care-icons/scripts"))
import render as R  # noqa: E402  Arabic type + compositing helpers
import icons as IC  # noqa: E402  3D icon library

W, H, FPS = 1080, 1920, 30
YEL = (250, 184, 23)
CHA = (37, 39, 41)
WHT = (244, 244, 242)
RED = (232, 52, 40)
KIT = ROOT / "brand/jlm"
R.ALBERT_PATH = KIT / "fonts/AlbertSans.ttf"
T = R.Type(KIT / "fonts")


def rgb01(c):
    return np.array(c, np.float32) / 255


def ease(x):
    return R.ease_out(x)


# ============================================================ captions ======
def _symbol(kind, h):
    """✗ (red) or ✓-in-circle drawn as vectors, h px tall."""
    s = 4
    img = Image.new("RGBA", (h * s, h * s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    w = int(h * s * 0.16)
    if kind == "x":
        m = h * s * 0.2
        d.line([(m, m), (h * s - m, h * s - m)], fill=RED + (255,), width=w)
        d.line([(m, h * s - m), (h * s - m, m)], fill=RED + (255,), width=w)
    else:
        d.ellipse([0, 0, h * s - 1, h * s - 1], fill=CHA + (255,))
        d.line([(h * s * .27, h * s * .52), (h * s * .44, h * s * .68), (h * s * .74, h * s * .34)],
               fill=YEL + (255,), width=w, joint="curve")
    return R.to_premul(np.array(img.resize((h, h), Image.LANCZOS)))


def cap_box(text, style="outline_w", size=62, symbol=None):
    """Reference caption box. styles: outline_y, outline_w, solid, small."""
    if style == "small":
        size = int(size * 0.74)
    color = {"outline_y": YEL, "outline_w": WHT, "solid": CHA, "small": WHT}[style]
    txt = T.line([(text, color)], size, bold=True, shadow=False, pad=0)
    th, tw = txt.shape[:2]
    padx, pady = int(size * 0.42), int(size * 0.22)
    sym = _symbol(symbol, int(size * 0.62)) if symbol else None
    sw = sym.shape[1] + int(size * 0.25) if sym is not None else 0
    bw, bh = tw + sw + 2 * padx, th + 2 * pady
    out = np.zeros((bh, bw, 4), np.float32)
    if style == "solid":
        out[...] = np.concatenate([rgb01(YEL), [1]])
    elif style == "small":
        out[...] = np.concatenate([rgb01(CHA) * 0.82, [0.82]])
    else:
        out[...] = np.concatenate([rgb01((18, 19, 20)) * 0.8, [0.8]])
        b = 4
        frame = np.zeros((bh, bw), bool)
        frame[:b], frame[-b:], frame[:, :b], frame[:, -b:] = True, True, True, True
        out[frame] = np.concatenate([rgb01(YEL), [1]])
    R.paste_into(out, txt, bw - padx - tw, (bh - th) // 2)
    if sym is not None:
        R.paste_into(out, sym, padx, (bh - sym.shape[0]) // 2)
    return out


def step_box(num, text, size=58):
    """Numbered step: yellow number disc glued to the right of an outlined box."""
    box = cap_box(text, "outline_w", size)
    bh = box.shape[0]
    d = int(bh * 0.82)
    s = 4
    img = Image.new("RGBA", (d * s, d * s), (0, 0, 0, 0))
    ImageDraw.Draw(img).ellipse([0, 0, d * s - 1, d * s - 1], fill=YEL + (255,))
    disc = R.to_premul(np.array(img.resize((d, d), Image.LANCZOS)))
    n = R.latin_layer(str(num), int(d * 0.62), CHA, 900, 0)
    R.paste_into(disc, n, (d - n.shape[1]) // 2, (d - n.shape[0]) // 2)
    gap = 16
    out = np.zeros((bh, box.shape[1] + gap + d, 4), np.float32)
    R.paste_into(out, box, 0, 0)
    R.paste_into(out, disc, box.shape[1] + gap, (bh - d) // 2)
    return out


def product_tag(text, size=40):
    t = R.latin_layer(text, size, CHA, 800, 0.02)
    out = np.zeros((t.shape[0] + 22, t.shape[1] + 44, 4), np.float32)
    out[...] = np.concatenate([rgb01(YEL), [1]])
    R.paste_into(out, t, 22, 11)
    return out


def cta_pill(text="اطلبه الآن", size=56):
    txt = T.line([(text, CHA)], size, bold=True, shadow=False, pad=0)
    ah = int(size * 0.62)
    aimg = Image.new("RGBA", (ah * 4, ah * 4), (0, 0, 0, 0))
    ad = ImageDraw.Draw(aimg)
    u = ah * 4
    ad.line([(u * .12, u * .5), (u * .92, u * .5)], fill=CHA + (255,), width=int(u * .13))
    ad.polygon([(0, u * .5), (u * .45, u * .12), (u * .45, u * .88)], fill=CHA + (255,))
    arrow = R.to_premul(np.array(aimg.resize((ah, ah), Image.LANCZOS)))
    th, tw = txt.shape[:2]
    padx, pady = 46, 20
    w, h = tw + arrow.shape[1] + 24 + 2 * padx, th + 2 * pady
    s = 3
    img = Image.new("RGBA", (w * s, h * s), (0, 0, 0, 0))
    ImageDraw.Draw(img).rounded_rectangle([0, 0, w * s - 1, h * s - 1], radius=h * s // 2, fill=YEL + (255,))
    pill = R.to_premul(np.array(img.resize((w, h), Image.LANCZOS)))
    R.paste_into(pill, txt, w - padx - tw, (h - th) // 2)
    R.paste_into(pill, arrow, padx, (h - arrow.shape[0]) // 2)
    return pill


class Caption:
    """A group of boxes stacked vertically, centred, with staggered entry."""

    def __init__(self, t0, t1, boxes, y, gap=6, stagger=0.38):
        self.t0, self.t1, self.boxes, self.y, self.gap, self.stagger = t0, t1, boxes, y, gap, stagger

    def draw(self, f, t):
        if not (self.t0 - 0.01 <= t <= self.t1 + 0.25):
            return
        out = 1 - ease((t - self.t1) / 0.22)
        y = self.y
        for k, b in enumerate(self.boxes):
            p = ease((t - self.t0 - k * self.stagger) / 0.26)
            if p > 0:
                R.over(f, b, (W - b.shape[1]) / 2, y + (1 - p) * 12, p * out)
            y += b.shape[0] + self.gap


# ============================================================== badge =======
ICONS = {cls.__name__: cls for cls in (IC.Heart, IC.CarWarning, IC.Calendar, IC.Engine, IC.FuelPump,
                                       IC.Gauge, IC.Shield)}


@lru_cache(maxsize=None)
def icon_obj(name):
    if name == "JLMDrop":
        return IC.JLMDrop(KIT / "icons/roundel_charcoal.png")
    return ICONS[name]()


@lru_cache(maxsize=2000)
def icon_frame(name, idx, px):
    ic = icon_obj(name)
    t = min(idx / FPS, ic.duration - 0.32)       # hold before the icon's own exit
    fr = np.clip(ic.frame(t), 0, 1).astype(np.float32)
    return cv2.resize(fr, (px, px), interpolation=cv2.INTER_AREA)


class Badge:
    """Reference badge: dark disc, red (problem) or yellow (solution) ring, 3D icon."""

    def __init__(self, t0, t1, icon, ring="y", y=1610, d=260):
        self.t0, self.t1, self.icon, self.ring, self.y, self.d = t0, t1, icon, ring, y, d
        s = 4
        img = Image.new("RGBA", (d * s, d * s), (0, 0, 0, 0))
        col = YEL if ring == "y" else RED
        ImageDraw.Draw(img).ellipse([6 * s, 6 * s, (d - 6) * s, (d - 6) * s], fill=(20, 21, 22, 225),
                                    outline=col + (255,), width=6 * s)
        self.disc = R.to_premul(np.array(img.resize((d, d), Image.LANCZOS)))
        self.glow = R.build_glow(d * 0.75, col, 0.22)

    def draw(self, f, t):
        if not (self.t0 <= t <= self.t1 + 0.25):
            return
        lt = t - self.t0
        sc = IC.ease_out_back(lt / 0.38) * (1 - ease((t - self.t1) / 0.22))
        if sc <= 0.01:
            return
        g = self.glow
        R.add_light(f, g, int(W / 2 - g.shape[1] / 2), int(self.y - g.shape[0] / 2), sc)
        layer, x, y = R.warp_premul(self.disc, sc, W / 2, self.y, (self.d / 2, self.d / 2))
        R.over(f, layer, x, y)
        px = int(self.d * 0.92)
        ic = icon_frame(self.icon, int(lt * FPS), px)
        ic = ic.copy()
        ic[..., :3] *= 1.0
        layer, x, y = R.warp_premul(ic, sc, W / 2, self.y, (px / 2, px / 2))
        R.over(f, layer, x, y)


# ========================================================= animation ========
RNG = np.random.default_rng(5)


def bloom(img, amount=0.9, sigma=14):
    b = cv2.GaussianBlur(img, (0, 0), sigma)
    return img + b * amount


def dark_bg(t, tint=(1.0, 0.75, 0.25)):
    y = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]
    x = np.linspace(0, 1, W, dtype=np.float32)[None, :, None]
    d = np.sqrt((x - 0.5) ** 2 * 1.4 + (y - 0.42) ** 2)
    return (0.03 + 0.10 * np.exp(-d ** 2 * 6)) * np.array(tint, np.float32)


GOLD = np.array([1.0, 0.72, 0.18], np.float32)
GOLD_HI = np.array([1.0, 0.9, 0.55], np.float32)


class GoldenPour:
    """Scene A: golden additive pours from the top and swirls into the oil."""

    def __init__(self, n=9000):
        self.p = np.zeros((n, 2), np.float32)
        self.v = np.zeros((n, 2), np.float32)
        self.age = np.full(n, 1e9, np.float32)
        self.n = n
        self.t_last = None
        self.metal = self._metal()

    def _metal(self):
        # suggestion of the engine interior: two dark steel walls with highlights
        f = np.zeros((H, W, 3), np.float32)
        x = np.linspace(0, 1, W, dtype=np.float32)
        wall = np.exp(-((x - 0.08) / 0.05) ** 2) + np.exp(-((x - 0.92) / 0.05) ** 2)
        streak = cv2.GaussianBlur(RNG.standard_normal((H, W)).astype(np.float32), (0, 0), sigmaX=1, sigmaY=40)
        f += (wall[None, :, None] * 0.22 + 0.02) * (1 + 0.25 * streak[..., None]) * np.array([0.8, 0.82, 0.85], np.float32)
        return f

    def frame(self, t):
        f = dark_bg(t) + self.metal
        # stream
        x = np.arange(W, dtype=np.float32)
        top_h = int(H * 0.55)
        wob = 6 * np.sin(np.arange(top_h) / 40 + t * 12)
        cx = W / 2 + wob
        w = 18 + 6 * np.sin(np.arange(top_h) / 23 - t * 9)
        stream = np.exp(-((x[None, :] - cx[:, None]) / w[:, None]) ** 2)
        f[:top_h] += stream[..., None] * GOLD * 1.1 + (stream ** 6)[..., None] * GOLD_HI * 0.9
        # pool surface glow
        y = np.linspace(0, 1, H, dtype=np.float32)
        pool = np.clip((y - 0.55) / 0.45, 0, 1)
        f += (pool ** 0.8)[:, None, None] * GOLD * 0.22
        # particles: spawned at the impact, swirl down through a flow field
        spawn = 260
        dead = np.nonzero(self.age > 2.2)[0][:spawn]
        self.p[dead] = np.stack([W / 2 + RNG.normal(0, 40, len(dead)), np.full(len(dead), H * 0.55)], 1)
        ang = RNG.uniform(0, 2 * np.pi, len(dead))
        sp = RNG.uniform(4, 22, len(dead))
        self.v[dead] = np.stack([np.cos(ang) * sp, np.abs(np.sin(ang)) * sp * 0.8 + 2], 1)
        self.age[dead] = 0
        alive = self.age < 2.2
        q = self.p[alive]
        fx = np.sin(q[:, 1] / 90 + t * 2) * 3 + np.cos(q[:, 0] / 120 - t) * 2
        fy = np.cos(q[:, 0] / 80 + t * 1.5) * 2 + 1.2
        self.v[alive] = self.v[alive] * 0.95 + np.stack([fx, fy], 1) * 0.6
        self.p[alive] += self.v[alive]
        self.age[alive] += 1 / FPS
        buf = np.zeros((H, W), np.float32)
        xi = np.clip(self.p[alive, 0].astype(int), 0, W - 1)
        yi = np.clip(self.p[alive, 1].astype(int), 0, H - 1)
        br = np.exp(-self.age[alive] * 1.4)
        np.add.at(buf, (yi, xi), br)
        buf = cv2.GaussianBlur(buf, (0, 0), 1.2) * 3
        f += buf[..., None] * GOLD_HI
        return np.clip(bloom(f, 0.8, 18), 0, 1)


class DepositClean:
    """Scene B: macro of an engine surface; a golden wave lifts the carbon off."""

    def __init__(self):
        def noise(scale, sigma):
            n = RNG.standard_normal((H // scale, W // scale)).astype(np.float32)
            n = cv2.GaussianBlur(n, (0, 0), sigma)
            return cv2.resize(n / (n.std() + 1e-6), (W, H), interpolation=cv2.INTER_CUBIC)
        field = noise(8, 4) * 0.7 + noise(3, 3) * 0.3
        self.dep = np.clip((field + 0.45) * 1.8, 0, 1)            # ~65 % covered, crusty edges
        crust = noise(2, 1.5) * 0.5 + noise(1, 1) * 0.5
        gy, gx = np.gradient(cv2.GaussianBlur(crust, (0, 0), 1.2))
        self.crust_light = np.clip(-(gx * 0.6 + gy * 0.8) * 3, 0, 1)
        self.crust = crust
        grain = cv2.GaussianBlur(RNG.standard_normal((H, W)).astype(np.float32), (0, 0), sigmaX=40, sigmaY=0.7)
        x = np.linspace(0, 1, W, dtype=np.float32)[None, :]
        y = np.linspace(0, 1, H, dtype=np.float32)[:, None]
        spec = np.exp(-(((x * 0.8 + y * 0.6) - 0.62) / 0.10) ** 2)      # diagonal studio highlight
        self.steel = (0.30 + 0.10 * grain / (grain.std() + 1e-6) * 0.5 + 0.38 * spec)[..., None] * np.array([0.82, 0.84, 0.88], np.float32)
        self.parts = np.zeros((0, 4), np.float32)

    def frame(self, t, dur):
        p = min(max(t / dur, 0), 1)
        front = -120 + p * (H + 240)
        yy = np.arange(H, dtype=np.float32)[:, None]
        cleaned = np.clip((front - yy) / 140, 0, 1)
        cover = self.dep * (1 - cleaned)
        carbon = (0.035 + 0.03 * self.crust[..., None]) * np.array([1.0, 0.9, 0.8], np.float32) \
            + self.crust_light[..., None] * 0.12
        f = self.steel * (1 - cover[..., None]) + carbon * cover[..., None]
        gold = cleaned[..., None] * GOLD * 0.06 * (0.6 + 0.4 * self.steel / 0.5)
        band = np.exp(-((yy - front) / 38) ** 2)
        gold = gold + band[..., None] * GOLD * 0.7
        if 0 < front < H:
            k = 160
            xs = RNG.uniform(0, W, k)
            ok = self.dep[int(np.clip(front, 0, H - 1)), xs.astype(int)] > 0.3
            m = int(ok.sum())
            new = np.stack([xs[ok], np.full(m, front), RNG.normal(0, 4, m), RNG.uniform(-18, -5, m)], 1)
            self.parts = np.concatenate([self.parts, new.astype(np.float32)])[-3000:]
        self.parts[:, 0] += self.parts[:, 2]
        self.parts[:, 1] += self.parts[:, 3]
        self.parts[:, 3] += 0.7
        flakes = np.zeros((H, W), np.float32)
        xi = np.clip(self.parts[:, 0].astype(int), 0, W - 1)
        yi = np.clip(self.parts[:, 1].astype(int), 0, H - 1)
        np.add.at(flakes, (yi, xi), 1.0)
        flakes = cv2.GaussianBlur(flakes, (0, 0), 1.4) * 2.2
        gold = gold + flakes[..., None] * GOLD_HI
        f = f + bloom(gold, 1.0, 14)
        x = np.linspace(-1, 1, W)[None, :]
        y = np.linspace(-1, 1, H)[:, None]
        f *= (1 - 0.5 * np.clip(x ** 2 + y ** 2 * 0.6, 0, 1))[..., None]
        return np.clip(f, 0, 1)


def _shape(draw_fn):
    im = Image.new("L", (IC.N, IC.N), 0)
    draw_fn(ImageDraw.Draw(im))
    return IC.to_mask(im)


class Piston:
    """Scene C: cutaway cylinder; the piston runs on a glowing protective film."""

    STEEL = np.array([0.58, 0.60, 0.64], np.float32)
    STEEL_D = np.array([0.20, 0.21, 0.24], np.float32)

    def __init__(self):
        P = IC.P
        walls = _shape(lambda d: (d.rectangle([*P(150, 120), *P(250, 760)], fill=255),
                                  d.rectangle([*P(750, 120), *P(850, 760)], fill=255)))
        self.walls = IC.emboss(walls, base=self.STEEL, deep=self.STEEL_D, bevel=14, shine=90, gloss=0.8)
        self.walls_m = walls
        head = _shape(lambda d: d.rounded_rectangle([*P(262, 0), *P(738, 260)], radius=int(26 * IC.N / 1000), fill=255))
        rings = _shape(lambda d: [d.line([P(262, y), P(738, y)], fill=255, width=int(9 * IC.N / 1000)) for y in (55, 90, 125)])
        self.head = IC.emboss(head, base=self.STEEL, deep=self.STEEL_D, bevel=20, shine=80, grooves=rings)
        self.head_m = head
        film = _shape(lambda d: (d.rectangle([*P(246, 120), *P(258, 760)], fill=255),
                                 d.rectangle([*P(742, 120), *P(754, 760)], fill=255)))
        self.film = film
        self.parts = RNG.uniform([0, 0], [1, 1], (900, 2)).astype(np.float32)

    def frame(self, t):
        S = IC.SIZE
        f = np.zeros((S, S, 4), np.float32)
        ang = t * 2 * math.pi * 2.2
        dy = (math.cos(ang) * 0.5 + 0.5) * 0.36 * S          # piston travel
        f = IC.over(f, IC.glow(self.film, GOLD, 10, 1.0 + 0.3 * math.sin(t * 8)))
        f = IC.over(f, self.walls)
        # connecting rod (simple dark bar) and crank disc below the piston
        cx, cy = S / 2, S * 0.92
        crank = (cx + math.sin(ang) * S * 0.09, cy - math.cos(ang) * S * 0.09)
        pin = (cx, S * 0.12 + dy + S * 0.2)
        rod = np.zeros((S, S), np.float32)
        cv2.line(rod, (int(pin[0]), int(pin[1])), (int(crank[0]), int(crank[1])), 1.0, int(S * 0.07), cv2.LINE_AA)
        f = IC.over(f, IC.emboss(rod, base=self.STEEL_D * 1.3, deep=self.STEEL_D * 0.7, bevel=8, shine=60, gloss=0.5))
        head = IC.transform(self.head, dy=S * 0.12 + dy)
        f = IC.over(f, head)
        # golden micro-particles riding on the film along the walls
        pts = self.parts.copy()
        pts[:, 1] = (pts[:, 1] + t * 0.6) % 1
        buf = np.zeros((S, S), np.float32)
        xs = np.where(pts[:, 0] < 0.5, 0.25 + pts[:, 0] * 0.02, 0.73 + pts[:, 0] * 0.02) * S
        ys = (0.12 + pts[:, 1] * 0.64) * S
        np.add.at(buf, (ys.astype(int).clip(0, S - 1), xs.astype(int).clip(0, S - 1)), 1)
        buf = cv2.GaussianBlur(buf, (0, 0), 1.3) * 3
        f[..., :3] += buf[..., None] * GOLD_HI
        f[..., 3] = np.maximum(f[..., 3], np.clip(buf, 0, 1))
        return f

    def full(self, t):
        bg = dark_bg(t, (1.0, 0.8, 0.35))
        # dark cylinder bore behind the piston
        bx0, bx1 = int(W * 0.24), int(W * 0.76)
        bore = np.linspace(0.05, 0.11, bx1 - bx0, dtype=np.float32)
        bore = np.minimum(bore, bore[::-1]) + 0.02
        bg[int(H * 0.2):int(H * 0.74), bx0:bx1] = bore[None, :, None] * np.array([0.9, 0.85, 0.75], np.float32)
        fr = self.frame(t)
        sc = 1.32 + 0.05 * t
        fr = cv2.resize(fr, (int(IC.SIZE * sc * 1.1), int(IC.SIZE * sc * 1.1)))
        out = bg.copy()
        layer = fr
        x, y = (W - layer.shape[1]) // 2, int(H * 0.47 - layer.shape[0] / 2)
        R.over(out, layer, x, y)
        warm = np.clip(out - 0.55, 0, 1) * GOLD
        return np.clip(out + cv2.GaussianBlur(warm, (0, 0), 16) * 0.8, 0, 1)


# =========================================================== timeline =======
def build_timeline(anim_only=False):
    caps, badges = [], []
    if anim_only:
        A = (0.0, 2.6)
        B = (2.6, 5.0)
        C = (5.0, 8.0)
        caps += [Caption(0.2, 2.5, [step_box(1, "يُضاف إلى زيت المحرّك")], 230),
                 Caption(2.7, 4.9, [step_box(2, "يحافظ على نظافة المحرّك")], 230),
                 Caption(5.1, 7.8, [step_box(3, "ويحافظ على أداء السيارة"), cap_box("مع الاستخدام اليومي", "small")], 230)]
        badges += [Badge(2.8, 4.9, "Engine"), Badge(5.2, 7.8, "Gauge")]
        return dict(A=A, B=B, C=C, caps=caps, badges=badges, end=None)
    A, B, C = (12.4, 13.1), (13.1, 14.3), (14.3, 16.3)
    TOP, LOW = 210, 1150
    caps += [
        Caption(0.62, 3.25, [cap_box("انت ما بتستنى المرض", "outline_y"), cap_box("عشان تهتم بحالك؟", "outline_w")], TOP),
        Caption(3.35, 5.85, [cap_box("وسيارتك كمان", "small"), cap_box("مش لازم تستنى العطل", "solid", symbol="x")], LOW),
        Caption(5.9, 7.62, [cap_box("عشان تهتم فيها", "outline_w")], LOW + 60),
        Caption(8.27, 10.95, [cap_box("العناية الدورية", "outline_y"), cap_box("بمنتجات JLM", "outline_w")], TOP),
        Caption(11.0, 12.35, [step_box(1, "يُضاف إلى زيت المحرّك")], TOP),
        Caption(12.45, 14.25, [step_box(2, "نظافة المحرّك ونظام الوقود")], TOP),
        Caption(14.35, 16.25, [step_box(3, "ويحافظ على أداء السيارة"), cap_box("مع الاستخدام اليومي", "small")], TOP),
        Caption(17.24, 19.8, [cap_box("اهتم بسيارتك اليوم", "outline_y"), cap_box("ووفّر على نفسك أعطال بكرا", "solid", symbol="v")], TOP),
        Caption(20.74, 23.92, [cap_box("JLM عناية احترافية", "outline_w"), cap_box("تبدأ من الداخل", "solid")], TOP),
    ]
    badges += [
        Badge(0.7, 3.25, "Heart", ring="r"),
        Badge(3.4, 7.62, "CarWarning", ring="r"),
        Badge(8.3, 10.95, "Calendar"),
        Badge(12.45, 13.3, "Engine"),
        Badge(13.35, 14.25, "FuelPump"),
        Badge(14.35, 16.25, "Gauge"),
        Badge(17.24, 19.8, "Shield"),
        Badge(20.74, 21.75, "JLMDrop"),
    ]
    tag = (11.05, 12.35, product_tag("JLM Ceramic Engine Protector"), 1350)
    return dict(A=A, B=B, C=C, caps=caps, badges=badges, end=21.8, tag=tag)


class Overlay:
    def __init__(self):
        logo = Image.open(KIT / "logos/logo_on_dark.png").convert("RGBA")
        a = np.asarray(logo)[..., 3]
        white = np.dstack([np.full(a.shape + (3,), 244, np.uint8), a])
        im = Image.fromarray(white, "RGBA")
        self.logo_small = R.to_premul(np.array(im.resize((170, int(im.height * 170 / im.width)), Image.LANCZOS)))
        self.logo_big = R.to_premul(np.array(im.resize((330, int(im.height * 330 / im.width)), Image.LANCZOS)))
        self.dealer = T.line([("وكيل JLM في فلسطين: الشركة المتحدة لتجارة السيارات", WHT)], 30, bold=False, shadow=False, pad=0)
        self.cta = cta_pill()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src")
    ap.add_argument("--out", required=True)
    ap.add_argument("--stills")
    ap.add_argument("--anim-only", action="store_true")
    a = ap.parse_args()
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    tl = build_timeline(a.anim_only)
    ov = Overlay()
    pour, clean, piston = GoldenPour(), DepositClean(), Piston()
    duration = 8.0 if a.anim_only else 23.9
    n_frames = int(duration * FPS)

    src = None
    if not a.anim_only:
        src = subprocess.Popen(["ffmpeg", "-v", "error", "-i", a.src, "-vf",
                                f"scale={W}:{H},eq=contrast=1.06:saturation=1.1:brightness=0.005",
                                "-f", "rawvideo", "-pix_fmt", "rgb24", "-r", str(FPS), "-"], stdout=subprocess.PIPE)

    want = None
    if a.stills:
        want = {int(round(float(s) * FPS)) for s in a.stills.split(",")}
        n_frames = max(want) + 1

    enc = None
    if not a.stills:
        tmp_v = out.with_name(out.stem + "_video_tmp.mp4")
        enc = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                                "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "slow",
                                "-crf", "17", "-pix_fmt", "yuv420p", str(tmp_v)], stdin=subprocess.PIPE)

    for n in range(n_frames):
        t = n / FPS
        if src is not None:
            raw = src.stdout.read(W * H * 3)
            if len(raw) < W * H * 3:
                break
            f = np.frombuffer(raw, np.uint8).reshape(H, W, 3).astype(np.float32) / 255
        else:
            f = np.zeros((H, W, 3), np.float32)
        (a0, a1), (b0, b1), (c0, c1) = tl["A"], tl["B"], tl["C"]
        if a0 <= t < c1:
            if t < a1:
                g = pour.frame(t - a0)
            elif t < b1:
                g = clean.frame(t - b0, b1 - b0)
            else:
                g = piston.full(t - c0)
            # 4-frame cross-fades at the scene joins, with a short flash on entry
            mix = min(1.0, (t - a0) / 0.13) if src is not None else 1.0
            f = f * (1 - mix) + g * mix
            flash = math.exp(-((t - a0) / 0.05) ** 2) * 0.5 if src is not None else 0
            f = f + flash
        for c in tl["caps"]:
            c.draw(f, t)
        if "tag" in tl:
            t0, t1, tag, y = tl["tag"]
            if t0 <= t <= t1 + 0.2:
                p = ease((t - t0) / 0.25) * (1 - ease((t - t1) / 0.2))
                R.over(f, tag, (W - tag.shape[1]) / 2, y + (1 - p) * 10, p)
        for b in tl["badges"]:
            b.draw(f, t)
        R.over(f, ov.logo_small, 46, 96, min(1.0, t / 0.4))
        if tl.get("end") and t >= tl["end"]:
            p = ease((t - tl["end"]) / 0.4)
            band_h = 250
            y0 = int(H - band_h * p)
            f[y0:] = f[y0:] * 0.08 + rgb01(CHA) * 0.92
            R.over(f, ov.logo_big, (W - ov.logo_big.shape[1]) / 2, y0 + 40)
            R.over(f, ov.dealer, (W - ov.dealer.shape[1]) / 2, y0 + 40 + ov.logo_big.shape[0] + 22)
            q = IC.ease_out_back((t - tl["end"] - 0.25) / 0.4)
            if q > 0:
                layer, x, y = R.warp_premul(ov.cta, q, W / 2, H - band_h - 80, (ov.cta.shape[1] / 2, ov.cta.shape[0] / 2))
                R.over(f, layer, x, y)
        img = (np.clip(f, 0, 1) * 255 + 0.5).astype(np.uint8)
        if want is not None:
            if n in want:
                cv2.imwrite(str(out.parent / f"still_{t:05.2f}.png"), cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
            continue
        enc.stdin.write(img.tobytes())
        if n % 90 == 0:
            print(f"frame {n}/{n_frames}", file=sys.stderr, flush=True)
    if src is not None:
        src.stdout.close()
        src.wait()
    if enc is None:
        return
    enc.stdin.close()
    enc.wait()
    mux(out, a, tl, duration)


def sfx_track(path, duration, tl):
    """Light SFX: a soft pop on every badge, a whoosh into the animation."""
    sr = 48000
    n = int(duration * sr)
    buf = np.zeros(n, np.float32)

    def place(x, at):
        i = int(at * sr)
        if i < 0:
            x, i = x[-i:], 0
        m = min(len(x), n - i)
        if m > 0:
            buf[i:i + m] += x[:m]
    tt = np.arange(int(0.09 * sr)) / sr
    pop = np.sin(2 * np.pi * (950 - 5200 * tt) * tt) * np.exp(-tt * 45) * 0.35
    for b in tl["badges"]:
        place(pop, b.t0)
    rng = np.random.default_rng(1)
    wl = int(0.6 * sr)
    w = rng.standard_normal(wl).astype(np.float32)
    w = np.convolve(w, np.ones(30) / 30, mode="same") * np.linspace(0, 1, wl) ** 2 * 0.5
    place(w, tl["A"][0] - 0.55)
    pcm = (np.clip(np.stack([buf, buf], 1), -1, 1) * 32767).astype(np.int16)
    with wave.open(str(path), "wb") as wv:
        wv.setnchannels(2)
        wv.setsampwidth(2)
        wv.setframerate(sr)
        wv.writeframes(pcm.tobytes())


def mux(out, a, tl, duration):
    tmp_v = out.with_name(out.stem + "_video_tmp.mp4")
    sfx = out.with_name(out.stem + "_sfx.wav")
    sfx_track(sfx, duration, tl)
    if a.anim_only:
        cmd = ["ffmpeg", "-y", "-loglevel", "error", "-i", str(tmp_v), "-i", str(sfx), "-c:v", "copy",
               "-af", "volume=2.0,alimiter=limit=0.8", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", str(out)]
    else:
        cmd = ["ffmpeg", "-y", "-loglevel", "error", "-i", str(tmp_v), "-i", a.src, "-i", str(sfx),
               "-filter_complex", "[1:a]aresample=48000,volume=1.0[v];[2:a]volume=0.55[s];[v][s]amix=inputs=2:normalize=0,"
               "loudnorm=I=-13.5:TP=-3:LRA=11,alimiter=limit=0.6:level=false[a]",
               "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest",
               "-movflags", "+faststart", str(out)]
    subprocess.run(cmd, check=True)
    tmp_v.unlink(missing_ok=True)
    sfx.unlink(missing_ok=True)
    print("wrote", out)


if __name__ == "__main__":
    main()
