"""Animated, realistic 3D icons in JLM yellow for the "العناية الدورية" video.

    python3 icons.py --out ../out            # renders every icon (mov + webm + green screen)
    python3 icons.py --out ../out --sheet    # still contact sheet only

Every icon is drawn as vector masks at 2x, then turned into a 3D object:
distance-transform bevel -> height map -> normals -> Blinn-Phong lighting with a
warm environment gradient, engraved details as grooves, and a soft contact
shadow. Animated parts (needle, check mark, ECG line, drops, sparkles, shine)
are re-shaded per frame.
"""

import argparse
import math
import subprocess
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw

SIZE = 720          # output canvas (square, transparent)
SS = 2              # supersampling for the vector masks
N = SIZE * SS
FPS = 30
YELLOW = np.array([250, 184, 23], np.float32) / 255
YELLOW_DEEP = np.array([226, 138, 6], np.float32) / 255
CHARCOAL = np.array([37, 39, 41], np.float32) / 255
WHITE = np.array([1.0, 0.98, 0.94], np.float32)
LIGHT = np.array([-0.45, -0.65, 0.62], np.float32)
LIGHT /= np.linalg.norm(LIGHT)
HALF = LIGHT + np.array([0, 0, 1], np.float32)
HALF /= np.linalg.norm(HALF)


# ------------------------------------------------------------- masks --------
def canvas():
    return Image.new("L", (N, N), 0)


def to_mask(img):
    """2x PIL mask -> float mask at output size (anti-aliased)."""
    a = np.asarray(img, np.float32) / 255
    return cv2.resize(a, (SIZE, SIZE), interpolation=cv2.INTER_AREA)


def P(x, y):
    """Design coordinates are 0..1000 on the output square."""
    return (x * N / 1000, y * N / 1000)


def heart_poly(cx, cy, s):
    pts = []
    for t in np.linspace(0, 2 * math.pi, 400):
        x = 16 * math.sin(t) ** 3
        y = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
        pts.append(P(cx + x * s, cy - y * s))
    return pts


def drop_poly(cx, cy, R, n=120):
    """JLM drop: pointed tip, round base; (cx, cy) = base-circle centre."""
    tip = np.array([0.0, -1.9 * R])
    side = np.array([R, 0.0])
    c1, c2 = np.array([0.30 * R, -1.50 * R]), np.array([R, -0.80 * R])
    pts = []
    for t in np.linspace(0, 1, n):
        pts.append((1 - t) ** 3 * tip + 3 * (1 - t) ** 2 * t * c1 + 3 * (1 - t) * t ** 2 * c2 + t ** 3 * side)
    for a in np.linspace(0, math.pi, n):
        pts.append(np.array([R * math.cos(a), R * math.sin(a)]))
    for t in np.linspace(1, 0, n):
        pts.append((1 - t) ** 3 * tip + 3 * (1 - t) ** 2 * t * c1 * [-1, 1] + 3 * (1 - t) * t ** 2 * c2 * [-1, 1] + t ** 3 * side * [-1, 1])
    return [P(cx + x, cy + y) for x, y in pts]


def stroke(draw, pts, w, fill=255):
    pts = [P(*p) for p in pts]
    draw.line(pts, fill=fill, width=int(w * N / 1000), joint="curve")
    r = w * N / 2000
    for x, y in (pts[0], pts[-1]):
        draw.ellipse([x - r, y - r, x + r, y + r], fill=fill)


def partial(pts, p):
    """First p (0..1) of a polyline, by length."""
    pts = np.array(pts, np.float32)
    seg = np.linalg.norm(np.diff(pts, axis=0), axis=1)
    L = seg.sum() * p
    out = [tuple(pts[0])]
    for i, s in enumerate(seg):
        if L <= 0:
            break
        if s <= L:
            out.append(tuple(pts[i + 1]))
            L -= s
        else:
            out.append(tuple(pts[i] + (pts[i + 1] - pts[i]) * (L / s)))
            L = 0
    return out


# ----------------------------------------------------------- shading --------
def emboss(mask, base=YELLOW, deep=YELLOW_DEEP, bevel=34, height=1.0, shine=60.0, grooves=None,
           metal=0.55, gloss=0.9):
    """Shade a mask as a glossy 3D object. grooves: mask of engraved channels."""
    m8 = (mask > 0.5).astype(np.uint8)
    dt = cv2.distanceTransform(m8, cv2.DIST_L2, 5)
    x = np.clip(dt / bevel, 0, 1)
    h = np.sqrt(1 - (1 - x) ** 2) * bevel * height          # rounded bevel profile
    if grooves is not None:
        g = cv2.GaussianBlur(grooves, (0, 0), 2.2)
        h = h - g * bevel * 0.45
    h = cv2.GaussianBlur(h, (0, 0), 1.2)
    gx = cv2.Sobel(h, cv2.CV_32F, 1, 0, ksize=3) / 8
    gy = cv2.Sobel(h, cv2.CV_32F, 0, 1, ksize=3) / 8
    n = np.dstack([-gx, -gy, np.ones_like(h)])
    n /= np.linalg.norm(n, axis=2, keepdims=True)
    diff = np.clip(n @ LIGHT, 0, 1)
    spec = np.clip(n @ HALF, 0, 1) ** shine
    # vertical colour gradient (lighter top, deeper bottom) + environment rim
    yy = np.linspace(0, 1, SIZE, dtype=np.float32)[:, None, None]
    col = base * (1 - yy * 0.45) + deep * (yy * 0.45)
    rim = (1 - n[..., 2:3]) ** 2
    rgb = col * (0.38 + 0.78 * diff[..., None]) + rim * col * 0.25
    rgb = rgb + spec[..., None] * WHITE * gloss
    # soft reflection band across the top (studio softbox)
    band = np.exp(-((np.linspace(0, 1, SIZE)[:, None] - 0.22) / 0.07) ** 2)[..., None] * 0.12 * metal
    rgb = rgb + band * (n[..., 2:3] > 0.97)
    if grooves is not None:
        rgb = rgb * (1 - 0.35 * np.clip(grooves, 0, 1)[..., None])
    rgb = np.clip(rgb, 0, 1)
    return np.dstack([rgb * mask[..., None], mask])       # premultiplied RGBA


def flat_inlay(mask, color, gloss=0.5):
    """Thin raised inlay (charcoal / white details) with its own small bevel."""
    return emboss(mask, base=color, deep=color * 0.75, bevel=6, height=1.0, shine=40, gloss=gloss, metal=0.2)


def glow(mask, color, radius=18, strength=1.0):
    g = cv2.GaussianBlur(mask, (0, 0), radius) * strength
    return np.dstack([np.clip(g[..., None] * color, 0, 1), np.clip(g, 0, 1)])


def over(dst, src):
    a = src[..., 3:4]
    return src + dst * (1 - a)


def add(dst, src):
    out = dst.copy()
    out[..., :3] = np.clip(dst[..., :3] + src[..., :3], 0, 1)
    out[..., 3] = np.clip(dst[..., 3] + src[..., 3] * 0.6, 0, 1)
    return out


def shadow(mask, dx=10, dy=22, blur=16, alpha=0.45):
    m = np.roll(np.roll(mask, dy, 0), dx, 1)
    m = cv2.GaussianBlur(m, (0, 0), blur) * alpha
    return np.dstack([np.zeros((SIZE, SIZE, 3), np.float32), m])


def shine_sweep(layer, p, mask):
    """Diagonal specular sweep across an object (p: 0..1)."""
    if not 0 < p < 1:
        return layer
    yy, xx = np.mgrid[0:SIZE, 0:SIZE].astype(np.float32)
    pos = -300 + p * (SIZE * 2 + 300)
    band = np.exp(-(((xx + yy * 0.6) - pos) / 40) ** 2) * 0.55 * mask
    out = layer.copy()
    out[..., :3] = np.clip(out[..., :3] + band[..., None], 0, 1) * (out[..., 3:4] > 0)
    return out


def transform(layer, scale=1.0, angle=0.0, dx=0.0, dy=0.0, cx=SIZE / 2, cy=SIZE / 2):
    M = cv2.getRotationMatrix2D((cx, cy), angle, scale)
    M[0, 2] += dx
    M[1, 2] += dy
    return cv2.warpAffine(layer, M, (SIZE, SIZE), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)


def ease_out_back(x, k=1.7):
    x = min(max(x, 0), 1)
    return 1 + (k + 1) * (x - 1) ** 3 + k * (x - 1) ** 2


def ease_out(x):
    x = min(max(x, 0), 1)
    return 1 - (1 - x) ** 3


def envelope(t, dur, t_in=0.42, t_out=0.3):
    """Pop-in with overshoot, hold, quick shrink-out."""
    s_in = ease_out_back(t / t_in)
    s_out = 1 - ease_out((t - (dur - t_out)) / t_out)
    return max(0.0, s_in * s_out), min(1.0, t / 0.18) * s_out


def sparkle(cx, cy, r):
    im = canvas()
    d = ImageDraw.Draw(im)
    pts = []
    for k in range(8):
        a = k * math.pi / 4
        rr = r if k % 2 == 0 else r * 0.22
        pts.append(P(cx + rr * math.sin(a), cy - rr * math.cos(a)))
    d.polygon(pts, fill=255)
    return to_mask(im)


# ------------------------------------------------------------- icons --------
class Icon:
    name = ""
    label = ""
    duration = 2.6

    def frame(self, t):
        raise NotImplementedError


class Heart(Icon):
    """انت ما بتستنى المرض عشان تهتم بحالك — heart with a live ECG trace."""
    name, label, duration = "01_heart_pulse", "الصحة / تهتم بحالك", 2.7

    def __init__(self):
        im = canvas()
        ImageDraw.Draw(im).polygon(heart_poly(500, 470, 21), fill=255)
        self.mask = to_mask(im)
        self.body = emboss(self.mask, bevel=46)
        self.ecg = [(150, 500), (330, 500), (370, 440), (420, 600), (480, 330), (540, 640), (590, 480), (640, 500), (850, 500)]

    def frame(self, t):
        s, a = envelope(t, self.duration)
        beat = 1 + 0.06 * (math.exp(-((t % 0.9) / 0.07) ** 2) + 0.6 * math.exp(-(((t % 0.9) - 0.2) / 0.07) ** 2))
        out = over(np.zeros((SIZE, SIZE, 4), np.float32), shadow(self.mask))
        out = over(out, self.body)
        im = canvas()
        stroke(ImageDraw.Draw(im), partial(self.ecg, ease_out((t - 0.3) / 1.1)), 30)
        line = to_mask(im) * self.mask_dilated()
        out = add(out, glow(line, WHITE * np.array([1, 0.95, 0.75]), 10, 1.2))
        out = over(out, flat_inlay(line, WHITE, gloss=0.8))
        out = shine_sweep(out, (t - 0.9) / 0.8, self.mask)
        return transform(out, s * beat) * a

    def mask_dilated(self):
        return np.ones_like(self.mask)


class CarWarning(Icon):
    """سيارتك مش لازم تستنى العطل — car with a dashboard warning light."""
    name, label, duration = "02_car_warning", "العطل / تهتم فيها", 4.2

    def __init__(self):
        im = canvas()
        d = ImageDraw.Draw(im)
        body = [(120, 600), (150, 520), (250, 500), (340, 390), (620, 385), (730, 500), (860, 520),
                (895, 560), (890, 640), (120, 640)]
        d.polygon([P(*p) for p in body], fill=255)
        d.rounded_rectangle([*P(110, 560), *P(900, 660)], radius=int(40 * N / 1000), fill=255)
        for wx in (290, 710):  # wheel arches cut out
            d.ellipse([*P(wx - 95, 545), *P(wx + 95, 735)], fill=0)
        self.mask = to_mask(im)
        g = canvas()
        gd = ImageDraw.Draw(g)
        gd.polygon([P(*p) for p in [(370, 410), (500, 410), (500, 500), (300, 500)]], fill=255)   # windows
        gd.polygon([P(*p) for p in [(525, 410), (610, 410), (690, 500), (525, 500)]], fill=255)
        gd.line([P(150, 575), P(860, 575)], fill=255, width=int(8 * N / 1000))                   # body line
        win = to_mask(g)
        self.body = emboss(self.mask, bevel=30, grooves=win * 0.0)
        self.glass = flat_inlay(win, CHARCOAL * 1.2, gloss=1.0)
        wm = canvas()
        for wx in (290, 710):
            ImageDraw.Draw(wm).ellipse([*P(wx - 78, 562), *P(wx + 78, 718)], fill=255)
        self.wheels_mask = to_mask(wm)
        hub = canvas()
        for wx in (290, 710):
            ImageDraw.Draw(hub).ellipse([*P(wx - 34, 606), *P(wx + 34, 674)], fill=255)
        self.wheels = over(flat_inlay(self.wheels_mask, CHARCOAL * 1.1, 0.6), emboss(to_mask(hub), base=np.array([0.78, 0.8, 0.82]), deep=np.array([0.5, 0.52, 0.55]), bevel=10))
        # warning triangle badge
        tri = canvas()
        td = ImageDraw.Draw(tri)
        td.polygon([P(*p) for p in [(735, 120), (900, 395), (570, 395)]], fill=255)
        tri = cv2.dilate(np.asarray(tri), np.ones((25, 25), np.uint8))
        self.tri_mask = to_mask(Image.fromarray(tri))
        ex = canvas()
        ed = ImageDraw.Draw(ex)
        ed.rounded_rectangle([*P(718, 205), *P(752, 315)], radius=int(16 * N / 1000), fill=255)
        ed.ellipse([*P(717, 330), *P(753, 366)], fill=255)
        self.ex = to_mask(ex)

    def frame(self, t):
        s, a = envelope(t, self.duration)
        out = over(np.zeros((SIZE, SIZE, 4), np.float32), shadow(np.maximum(self.mask, self.wheels_mask), dy=26))
        out = over(out, self.body)
        out = over(out, self.glass)
        out = over(out, self.wheels)
        # badge pops after the car, then blinks like a dashboard light
        bs, ba = envelope(t - 0.45, self.duration - 0.45)
        blink = 0.55 + 0.45 * (0.5 + 0.5 * math.cos(t * 2 * math.pi * 1.6))
        warn_col = np.array([1.0, 0.33, 0.12], np.float32)
        badge = over(np.zeros((SIZE, SIZE, 4), np.float32), glow(self.tri_mask, warn_col, 28, 0.9 * blink))
        badge = over(badge, shadow(self.tri_mask, 6, 12, 10, 0.4))
        badge = over(badge, emboss(self.tri_mask, base=YELLOW, bevel=22))
        badge = over(badge, flat_inlay(self.ex, CHARCOAL, 0.7))
        badge = transform(badge, bs, angle=8 * math.sin(t * 9) * math.exp(-max(t - 0.45, 0) * 2.2), cx=735 * SIZE / 1000, cy=300 * SIZE / 1000) * ba
        out = over(out, badge)
        out = shine_sweep(out, (t - 1.2) / 0.9, self.mask)
        return transform(out, s, dy=4 * math.sin(t * 3)) * a


class Calendar(Icon):
    """العناية الدورية — calendar page with a check and a repeat arrow."""
    name, label, duration = "03_periodic_care", "العناية الدورية", 2.4

    def __init__(self):
        im = canvas()
        ImageDraw.Draw(im).rounded_rectangle([*P(190, 220), *P(810, 820)], radius=int(70 * N / 1000), fill=255)
        self.mask = to_mask(im)
        g = canvas()
        gd = ImageDraw.Draw(g)
        gd.rounded_rectangle([*P(190, 220), *P(810, 360)], radius=int(70 * N / 1000), fill=0)
        for i in range(4):
            for j in range(3):
                x0, y0 = 245 + i * 135, 410 + j * 128
                gd.rounded_rectangle([*P(x0, y0), *P(x0 + 105, y0 + 98)], radius=int(16 * N / 1000), outline=255, width=int(7 * N / 1000))
        hdr = canvas()
        ImageDraw.Draw(hdr).line([P(200, 365), P(800, 365)], fill=255, width=int(10 * N / 1000))
        self.grooves = np.maximum(to_mask(g), to_mask(hdr))
        self.body = emboss(self.mask, bevel=40, grooves=self.grooves)
        rings = canvas()
        for x in (340, 660):
            ImageDraw.Draw(rings).rounded_rectangle([*P(x - 28, 160), *P(x + 28, 290)], radius=int(28 * N / 1000), fill=255)
        self.rings = emboss(to_mask(rings), base=CHARCOAL * 1.6, deep=CHARCOAL, bevel=14, shine=80)
        self.rings_mask = to_mask(rings)
        self.check_pts = [(560, 590), (605, 640), (700, 520)]

    def frame(self, t):
        s, a = envelope(t, self.duration)
        out = over(np.zeros((SIZE, SIZE, 4), np.float32), shadow(self.mask))
        out = over(out, self.body)
        out = over(out, self.rings)
        im = canvas()
        stroke(ImageDraw.Draw(im), partial(self.check_pts, ease_out((t - 0.5) / 0.45)), 34)
        chk = to_mask(im)
        out = over(out, flat_inlay(chk, CHARCOAL, 0.8))
        # repeat badge: circular arrow turning, bottom-right
        arr = canvas()
        ad = ImageDraw.Draw(arr)
        c, r = (790, 790), 120
        ad.ellipse([*P(c[0] - r, c[1] - r), *P(c[0] + r, c[1] + r)], fill=255)
        badge_mask = to_mask(arr)
        ring = canvas()
        rd = ImageDraw.Draw(ring)
        rd.arc([*P(c[0] - 70, c[1] - 70), *P(c[0] + 70, c[1] + 70)], 30, 320, fill=255, width=int(22 * N / 1000))
        ang = math.radians(320)
        tipx, tipy = c[0] + 70 * math.cos(ang), c[1] + 70 * math.sin(ang)
        rd.polygon([P(tipx + 32, tipy - 4), P(tipx - 22, tipy - 30), P(tipx - 8, tipy + 34)], fill=255)
        ring_m = to_mask(ring)
        bs, ba = envelope(t - 0.25, self.duration - 0.25)
        badge = over(np.zeros((SIZE, SIZE, 4), np.float32), shadow(badge_mask, 5, 10, 8, 0.4))
        badge = over(badge, emboss(badge_mask, base=CHARCOAL * 1.5, deep=CHARCOAL, bevel=20, shine=70))
        spin = transform(flat_inlay(ring_m, YELLOW, 0.9), 1.0, angle=-t * 160, cx=c[0] * SIZE / 1000, cy=c[1] * SIZE / 1000)
        badge = over(badge, spin)
        badge = transform(badge, bs, cx=c[0] * SIZE / 1000, cy=c[1] * SIZE / 1000) * ba
        out = over(out, badge)
        out = shine_sweep(out, (t - 1.1) / 0.8, self.mask)
        return transform(out, s, angle=2 * math.sin(t * 2.4)) * a


class Engine(Icon):
    """نظافة المحرك — clean engine block with sparkles."""
    name, label, duration = "04_clean_engine", "نظافة المحرك", 2.3

    def __init__(self):
        im = canvas()
        d = ImageDraw.Draw(im)
        d.rounded_rectangle([*P(250, 330), *P(760, 720)], radius=int(40 * N / 1000), fill=255)      # block
        d.rounded_rectangle([*P(300, 250), *P(710, 340)], radius=int(30 * N / 1000), fill=255)      # valve cover
        d.rounded_rectangle([*P(430, 190), *P(580, 260)], radius=int(18 * N / 1000), fill=255)      # oil cap
        d.rounded_rectangle([*P(150, 430), *P(260, 600)], radius=int(26 * N / 1000), fill=255)      # left mount
        d.rounded_rectangle([*P(750, 400), *P(860, 520)], radius=int(26 * N / 1000), fill=255)      # right pipe
        d.rounded_rectangle([*P(330, 710), *P(680, 790)], radius=int(26 * N / 1000), fill=255)      # oil pan
        self.mask = to_mask(im)
        g = canvas()
        gd = ImageDraw.Draw(g)
        for k in range(4):
            x = 330 + k * 105
            gd.rounded_rectangle([*P(x, 420), *P(x + 70, 640)], radius=int(20 * N / 1000), outline=255, width=int(9 * N / 1000))
        gd.line([P(310, 300), P(700, 300)], fill=255, width=int(8 * N / 1000))
        self.body = emboss(self.mask, bevel=36, grooves=to_mask(g))
        self.sparks = [(220, 230, 70, 0.0), (820, 290, 90, 0.35), (850, 700, 60, 0.7), (180, 760, 55, 0.5)]

    def frame(self, t):
        s, a = envelope(t, self.duration)
        out = over(np.zeros((SIZE, SIZE, 4), np.float32), shadow(self.mask))
        out = over(out, self.body)
        out = shine_sweep(out, (t - 0.4) / 0.8, self.mask)
        for (x, y, r, ph) in self.sparks:
            k = (t - 0.35 - ph) / 0.8
            if 0 < k < 2.2:
                tw = math.sin(min(k, 1) * math.pi) if k < 1 else 0.5 + 0.5 * math.sin((k - 1) * 9)
                m = sparkle(x, y, r * (0.5 + 0.5 * tw))
                out = add(out, glow(m, WHITE, 12, 0.9 * tw))
                out = over(out, np.dstack([m[..., None] * WHITE * tw, m * tw]))
        return transform(out, s, dy=5 * math.sin(t * 3)) * a


class FuelPump(Icon):
    """نظام الوقود — fuel pump with a drop falling from the nozzle."""
    name, label, duration = "05_fuel_system", "نظام الوقود", 2.2

    def __init__(self):
        im = canvas()
        d = ImageDraw.Draw(im)
        d.rounded_rectangle([*P(250, 180), *P(600, 840)], radius=int(50 * N / 1000), fill=255)      # body
        d.rounded_rectangle([*P(210, 800), *P(640, 870)], radius=int(20 * N / 1000), fill=255)      # base
        self.mask = to_mask(im)
        hose = canvas()
        hd = ImageDraw.Draw(hose)
        hd.line([P(600, 330), P(690, 330), P(730, 380), P(730, 640), P(780, 690), P(820, 650), P(820, 430), P(760, 380)],
                fill=255, width=int(34 * N / 1000), joint="curve")
        hd.rounded_rectangle([*P(730, 330), *P(800, 450)], radius=int(16 * N / 1000), fill=255)     # nozzle
        self.hose_mask = to_mask(hose)
        g = canvas()
        ImageDraw.Draw(g).rounded_rectangle([*P(320, 260), *P(530, 430)], radius=int(26 * N / 1000), fill=255)
        self.screen = to_mask(g)
        self.body = emboss(self.mask, bevel=40)
        self.hose = emboss(self.hose_mask, base=CHARCOAL * 1.7, deep=CHARCOAL, bevel=14, shine=70)
        self.screen_l = flat_inlay(self.screen, CHARCOAL * 1.2, 1.0)

    def frame(self, t):
        s, a = envelope(t, self.duration)
        both = np.maximum(self.mask, self.hose_mask)
        out = over(np.zeros((SIZE, SIZE, 4), np.float32), shadow(both))
        out = over(out, self.hose)
        out = over(out, self.body)
        out = over(out, self.screen_l)
        # digits on the screen counting (glowing yellow bars)
        k = int(max(0, t - 0.3) * 10) % 4
        bars = canvas()
        for i in range(k + 1):
            ImageDraw.Draw(bars).rounded_rectangle([*P(345 + i * 45, 380 - i * 25), *P(375 + i * 45, 405)], radius=4, fill=255)
        bm = to_mask(bars)
        out = add(out, glow(bm, YELLOW, 6, 1.0))
        out = over(out, np.dstack([bm[..., None] * YELLOW, bm]))
        # drop falls from the nozzle and stretches, then a new one forms
        ph = ((t - 0.4) % 1.0) / 1.0 if t > 0.4 else 0
        im = canvas()
        y = 480 + ph ** 2 * 380
        R = 34 * (0.6 + 0.4 * min(ph * 3, 1))
        ImageDraw.Draw(im).polygon(drop_poly(765, y, R), fill=255)
        dm = to_mask(im) * (1 - max(0, ph - 0.85) / 0.15)
        out = over(out, emboss(dm, bevel=12, shine=90))
        out = shine_sweep(out, (t - 1.0) / 0.8, self.mask)
        return transform(out, s) * a


class Gauge(Icon):
    """أداء السيارة — speedometer whose needle sweeps up into the yellow zone."""
    name, label, duration = "06_performance", "أداء السيارة", 2.5

    def __init__(self):
        self.c = (500, 560)
        im = canvas()
        ImageDraw.Draw(im).ellipse([*P(140, 200), *P(860, 920)], fill=255)
        cut = canvas()
        ImageDraw.Draw(cut).rectangle([*P(0, 770), *P(1000, 1000)], fill=255)
        self.mask = to_mask(im) * (1 - to_mask(cut))
        rim = canvas()
        ImageDraw.Draw(rim).ellipse([*P(205, 265), *P(795, 855)], fill=255)
        self.face = to_mask(rim) * (1 - to_mask(cut))
        self.body = emboss(self.mask, bevel=34)
        ticks = canvas()
        td = ImageDraw.Draw(ticks)
        for k in range(11):
            ang = math.radians(200 - k * 22)
            r0, r1 = (240, 285) if k % 2 == 0 else (255, 285)
            td.line([P(self.c[0] + r0 * math.cos(ang), self.c[1] - r0 * math.sin(ang)),
                     P(self.c[0] + r1 * math.cos(ang), self.c[1] - r1 * math.sin(ang))],
                    fill=255, width=int((12 if k % 2 == 0 else 7) * N / 1000))
        self.ticks = to_mask(ticks)
        self.face_l = emboss(self.face, base=CHARCOAL * 1.25, deep=CHARCOAL * 0.9, bevel=10, shine=50, gloss=0.6)
        hub = canvas()
        ImageDraw.Draw(hub).ellipse([*P(self.c[0] - 45, self.c[1] - 45), *P(self.c[0] + 45, self.c[1] + 45)], fill=255)
        self.hub = emboss(to_mask(hub), bevel=18)

    def frame(self, t):
        s, a = envelope(t, self.duration)
        out = over(np.zeros((SIZE, SIZE, 4), np.float32), shadow(self.mask))
        out = over(out, self.body)
        out = over(out, self.face_l)
        out = over(out, np.dstack([self.ticks[..., None] * WHITE * 0.92, self.ticks]))
        # performance arc filling in yellow
        p = ease_out((t - 0.35) / 1.0)
        arc = canvas()
        ImageDraw.Draw(arc).arc([*P(self.c[0] - 230, self.c[1] - 230), *P(self.c[0] + 230, self.c[1] + 230)],
                                160, 160 + 220 * p * 0.85, fill=255, width=int(24 * N / 1000))
        am = to_mask(arc) * (p > 0.01)
        out = add(out, glow(am, YELLOW, 12, 0.9))
        out = over(out, np.dstack([am[..., None] * YELLOW, am]))
        # needle: from 200° (left) to ~25° with a little overshoot and settle
        k = ease_out_back((t - 0.35) / 1.0, 1.2)
        ang = math.radians(200 - 175 * k + 2.5 * math.sin(t * 22) * math.exp(-max(t - 1.4, 0) * 3) * (t > 1.4))
        nd = canvas()
        tip = (self.c[0] + 245 * math.cos(ang), self.c[1] - 245 * math.sin(ang))
        perp = (math.cos(ang + math.pi / 2) * 16, -math.sin(ang + math.pi / 2) * 16)
        ImageDraw.Draw(nd).polygon([P(*tip), P(self.c[0] + perp[0], self.c[1] + perp[1]), P(self.c[0] - perp[0], self.c[1] - perp[1])], fill=255)
        nm = to_mask(nd)
        out = add(out, glow(nm, np.array([1, 0.4, 0.1]), 8, 0.6))
        out = over(out, emboss(nm, base=np.array([1.0, 0.42, 0.12]), deep=np.array([0.75, 0.18, 0.05]), bevel=6, shine=60))
        out = over(out, self.hub)
        out = shine_sweep(out, (t - 1.3) / 0.8, self.mask)
        return transform(out, s) * a


class Shield(Icon):
    """وفر على نفسك أعطال بكرا — protection shield with a check mark."""
    name, label, duration = "07_protection", "وفّر أعطال بكرا", 2.6

    def __init__(self):
        im = canvas()

        def bez(p0, p1, p2, n=40):
            return [((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t ** 2 * p2[0],
                     (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t ** 2 * p2[1]) for t in np.linspace(0, 1, n)]
        right = [(500, 130), (800, 235)] + bez((800, 235), (810, 470), (790, 560)) + bez((790, 560), (720, 780), (500, 885))
        left = [(1000 - x, y) for x, y in reversed(right)]
        ImageDraw.Draw(im).polygon([P(*p) for p in right + left[1:]], fill=255)
        self.mask = to_mask(im)
        inner = cv2.erode((self.mask > 0.5).astype(np.uint8), np.ones((43, 43), np.uint8)).astype(np.float32)
        ring = np.clip(self.mask - cv2.GaussianBlur(inner, (0, 0), 1), 0, 1)
        self.body = emboss(self.mask, bevel=44, grooves=cv2.dilate(ring, np.ones((3, 3))) * 0 + (cv2.Canny((inner * 255).astype(np.uint8), 50, 150) > 0).astype(np.float32))
        self.check_pts = [(360, 500), (460, 610), (660, 400)]

    def frame(self, t):
        s, a = envelope(t, self.duration)
        out = over(np.zeros((SIZE, SIZE, 4), np.float32), shadow(self.mask))
        out = over(out, self.body)
        im = canvas()
        stroke(ImageDraw.Draw(im), partial(self.check_pts, ease_out((t - 0.45) / 0.5)), 58)
        chk = to_mask(im)
        out = add(out, glow(chk, WHITE, 12, 0.7))
        out = over(out, flat_inlay(chk, WHITE, 0.9))
        out = shine_sweep(out, (t - 1.0) / 0.8, self.mask)
        return transform(out, s, angle=-3 * math.sin(t * 2.2)) * a


class JLMDrop(Icon):
    """JLM عناية احترافية تبدأ من الداخل — the JLM drop with the roundel, glowing from inside."""
    name, label, duration = "08_jlm_inside", "عناية تبدأ من الداخل", 2.6

    def __init__(self, roundel_png):
        im = canvas()
        ImageDraw.Draw(im).polygon(drop_poly(500, 610, 260), fill=255)
        self.mask = to_mask(im)
        self.body = emboss(self.mask, bevel=50)
        r = Image.open(roundel_png).convert("RGBA")
        a = np.asarray(r)[..., 3].astype(np.float32) / 255
        ys, xs = np.nonzero(a > 0.1)
        a = a[ys.min(): ys.max() + 1, xs.min(): xs.max() + 1]
        side = int(SIZE * 0.36)
        a = cv2.resize(a, (side, int(a.shape[0] * side / a.shape[1])), interpolation=cv2.INTER_AREA)
        m = np.zeros((SIZE, SIZE), np.float32)
        y0, x0 = int(SIZE * 0.61 - a.shape[0] / 2), int(SIZE / 2 - side / 2)
        m[y0:y0 + a.shape[0], x0:x0 + side] = a
        self.roundel = m

    def frame(self, t):
        s, a = envelope(t, self.duration)
        out = over(np.zeros((SIZE, SIZE, 4), np.float32), glow(self.mask, YELLOW, 40, 0.35 + 0.15 * math.sin(t * 4)))
        out = over(out, shadow(self.mask))
        out = over(out, self.body)
        # roundel engraved in charcoal, slowly turning; inner light pulses "from the inside"
        rr = transform(np.dstack([self.roundel] * 4), 1.0, angle=-(1 - ease_out((t - 0.2) / 1.2)) * 90,
                       cx=SIZE / 2, cy=SIZE * 0.61)[..., 0]
        core = cv2.GaussianBlur(self.roundel, (0, 0), 20) * (0.5 + 0.5 * math.sin(t * 5)) * 0.8
        out = add(out, np.dstack([core[..., None] * WHITE, core * 0]))
        out = over(out, flat_inlay(rr, CHARCOAL, 0.7))
        out = shine_sweep(out, (t - 0.8) / 0.9, self.mask)
        return transform(out, s, dy=6 * math.sin(t * 2.6)) * a


# ------------------------------------------------------------- export -------
def render(icon, out_dir):
    out_dir.mkdir(parents=True, exist_ok=True)
    n = int(round(icon.duration * FPS))
    frames = []
    for i in range(n):
        f = np.clip(icon.frame(i / FPS), 0, 1)
        frames.append((f * 255 + 0.5).astype(np.uint8))
    rgba = [np.dstack([fr[..., :3].astype(np.float32) / np.maximum(fr[..., 3:4].astype(np.float32) / 255, 1e-3) / 255, fr[..., 3:4] / 255]) for fr in frames]
    straight = [(np.clip(x, 0, 1) * 255 + 0.5).astype(np.uint8) for x in rgba]   # un-premultiplied for video alpha

    def pipe(args, data):
        p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", data[0], "-s", f"{SIZE}x{SIZE}",
                              "-r", str(FPS), "-i", "-"] + args, stdin=subprocess.PIPE)
        for fr in data[1]:
            p.stdin.write(fr.tobytes())
        p.stdin.close()
        p.wait()

    (out_dir / "mov").mkdir(exist_ok=True)
    (out_dir / "webm").mkdir(exist_ok=True)
    (out_dir / "greenscreen").mkdir(exist_ok=True)
    pipe(["-c:v", "prores_ks", "-profile:v", "4", "-pix_fmt", "yuva444p10le", "-vendor", "apl0",
          str(out_dir / "mov" / f"{icon.name}.mov")], ("rgba", straight))
    pipe(["-c:v", "libvpx-vp9", "-pix_fmt", "yuva420p", "-b:v", "0", "-crf", "24", "-auto-alt-ref", "0",
          str(out_dir / "webm" / f"{icon.name}.webm")], ("rgba", straight))
    green = np.array([0, 255, 0], np.float32)
    gs = [((fr[..., :3].astype(np.float32) + green * (1 - fr[..., 3:4] / 255))).clip(0, 255).astype(np.uint8) for fr in frames]
    pipe(["-c:v", "libx264", "-crf", "16", "-pix_fmt", "yuv420p", str(out_dir / "greenscreen" / f"{icon.name}_green.mp4")], ("rgb24", gs))
    return frames


def build(roundel):
    return [Heart(), CarWarning(), Calendar(), Engine(), FuelPump(), Gauge(), Shield(), JLMDrop(roundel)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--sheet", action="store_true")
    ap.add_argument("--only")
    a = ap.parse_args()
    root = Path(__file__).resolve().parents[4]
    roundel = root / "brand/jlm/icons/roundel_charcoal.png"
    icons = build(roundel)
    if a.only:
        icons = [i for i in icons if a.only in i.name]
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    tiles = []
    for ic in icons:
        if a.sheet:
            fr = ic.frame(min(ic.duration * 0.6, 1.6))
            tiles.append((np.clip(fr, 0, 1) * 255).astype(np.uint8))
        else:
            frames = render(ic, out)
            tiles.append(frames[int(len(frames) * 0.6)])
            print("rendered", ic.name, len(frames), "frames")
    # contact sheet on a mid-grey and on a dark background
    cols = 4
    rows = math.ceil(len(tiles) / cols)
    sheet = np.zeros((rows * 2 * SIZE // 2, cols * SIZE // 2, 3), np.uint8)
    for k, tile in enumerate(tiles):
        small = cv2.resize(tile, (SIZE // 2, SIZE // 2), interpolation=cv2.INTER_AREA).astype(np.float32) / 255
        for b, bg in enumerate(((0.62, 0.64, 0.66), (0.13, 0.14, 0.15))):
            comp = small[..., :3] + np.array(bg) * (1 - small[..., 3:4])
            r, c = (k // cols) * 2 + b, k % cols
            sheet[r * SIZE // 2:(r + 1) * SIZE // 2, c * SIZE // 2:(c + 1) * SIZE // 2] = (comp * 255).astype(np.uint8)
    Image.fromarray(sheet).save(out / "icons_sheet.png")
    print("wrote", out / "icons_sheet.png")


if __name__ == "__main__":
    main()
