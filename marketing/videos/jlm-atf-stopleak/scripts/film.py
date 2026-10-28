"""JLM ATF Stop Leak & Conditioner — 20 s cinematic story on real footage (no schematic over it).

    python3 scripts/film.py --out renders/jlm_atf_stop_leak_film.mp4 [--stills 1,5,...]
    (needs scripts/music_film.py's track: python3 scripts/music_film.py)

The viewer lives the product, stage by stage:
  0.0  the gear shifts and jolts — «ناقل الحركة ينزلق؟ أو يسرّب الزيت؟» (cold, red flashes)
  2.5  inside the gearbox — تسرّب · انزلاق · استهلاك للزيت (cold)
  5.5  the product, hero-lit — مانع تسرّب زيت الجير / ATF Stop Leak & Conditioner (warm from here on)
  8.5  ١ رجّ العلبة جيداً → ٢ أضفه إلى سائل ناقل الحركة (pour under the bonnet, then into the funnel)
 12.5  ٣ قُد السيارة 15 دقيقة (time-lapse drive, a 0 → 15 timer)
 15.0  the same gear shift, now smooth and warm — تبديل سلس وهادئ · ويطيل عمر ناقل الحركة · *CVT/DSG note
 17.5  CTA — logo, can, اطلبه الآن من خلال jlmstore.com, مع توفّر خدمة التوصيل
Stock clips (Pexels, from the client) are cropped so the car-brand badges (FIAT on the wheel, STI on the
console) stay out of frame. Cuts sit on the 120 BPM grid; zoom-blur whips with a warm light flash join them.
"""
import argparse
import math
import subprocess
import sys
from functools import lru_cache
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
REPO = ROOT.parents[2]
sys.path.insert(0, str(REPO / "marketing/videos/jlm-care-edit/scripts"))
import edit_v3 as V  # noqa: E402

E, R = V.E, V.R
W, H, FPS, DUR = 1080, 1920, 30, 20.0
YEL, WHT, RED, SIL = (250, 184, 23), (241, 240, 236), (232, 69, 46), (192, 196, 199)
FOOT = ROOT / "assets/footage"
BUILD = ROOT / "build/shots"
ease, back = V.ease_io, V.back

# name: (clip, src start, output length, speed, crop w:h:x:y in source pixels)
SHOTS = {
    "shift":  ("c3", 0.0, 2.5, 1.0, "1215:2160:1200:0"),       # console badge (x ≥ 0.66) left out
    "gears":  ("c4", 8.0, 3.0, 0.9, "608:1080:656:0"),
    "hero":   ("c4", 0.5, 3.0, 0.6, "608:1080:656:0"),         # blurred behind the can
    "bonnet": ("c1", 0.0, 2.5, 1.0, "2160:3840:0:0"),          # 0–1 s blurred behind the shake, then the pour
    "funnel": ("c2", 1.0, 1.5, 0.6, "608:1080:560:0"),         # 60 fps source → smooth slow motion
    "drive":  ("c5", 0.5, 2.5, 1.6, "1543:2743:617:150"),      # FIAT hub badge (x < 0.26) left out
    "smooth": ("c3", 4.0, 1.3, 0.8, "1215:2160:1200:0"),
    "golden": ("c4", 13.5, 1.2, 0.6, "608:1080:656:0"),
    "cta":    ("c4", 25.0, 2.5, 0.5, "608:1080:656:0"),
}
# timeline: (start, end, shot, offset into the shot)
EDL = [(0.0, 2.5, "shift", 0.0), (2.5, 5.5, "gears", 0.0), (5.5, 8.5, "hero", 0.0), (8.5, 9.5, "bonnet", 0.0),
       (9.5, 11.0, "bonnet", 1.0), (11.0, 12.5, "funnel", 0.0), (12.5, 15.0, "drive", 0.0),
       (15.0, 16.3, "smooth", 0.0), (16.3, 17.5, "golden", 0.0), (17.5, 20.0, "cta", 0.0)]
CUTS = [s for s, *_ in EDL[1:]]


def extract():
    BUILD.mkdir(parents=True, exist_ok=True)
    for name, (clip, t0, dur, speed, crop) in SHOTS.items():
        out = BUILD / f"{name}.mp4"
        if out.exists():
            continue
        vf = (f"trim=start={t0}:duration={dur * speed + 0.2},setpts=(PTS-STARTPTS)/{speed},crop={crop},"
              f"scale={W}:{H}:flags=lanczos,fps={FPS}")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(FOOT / f"{clip}.mp4"), "-vf", vf, "-an",
                        "-t", str(dur + 0.1), "-c:v", "libx264", "-crf", "12", "-preset", "fast", str(out)], check=True)


class Shots:
    def __init__(self):
        self.frames = {}

    def get(self, name, k):
        if name not in self.frames:
            raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(BUILD / f"{name}.mp4"), "-f", "rawvideo",
                                  "-pix_fmt", "rgb24", "-"], capture_output=True, check=True).stdout
            self.frames[name] = np.frombuffer(raw, np.uint8).reshape(-1, H, W, 3)
        fr = self.frames[name]
        return fr[min(k, len(fr) - 1)].astype(np.float32) / 255


# ------------------------------------------------------------------ look ---
def grade(f, warm):
    """Cold = desaturated steel blue (the problem); warm = JLM gold highlights (the fix)."""
    lum = f.mean(2, keepdims=True)
    if warm > 0:
        sat = 1.0 + 0.1 * warm
        tint = np.array([1.06, 1.0, 0.86], np.float32) ** warm
    else:
        sat = 1.0 + 0.45 * warm
        tint = np.array([0.92, 0.98, 1.06], np.float32) ** (-warm)
    f = lum + (f - lum) * sat
    f = f * tint
    f = np.clip((f - 0.03) / 0.97, 0, 1) ** 1.08          # deeper blacks
    return f


VIGN = None
GRAIN = None


def finish(f, n):
    global VIGN, GRAIN
    if VIGN is None:
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        VIGN = (1 - 0.42 * np.clip(np.hypot((xx - W / 2) / W, (yy - H / 2) / H) * 1.5, 0, 1) ** 2)[..., None]
        rng = np.random.default_rng(2)
        GRAIN = [cv2.resize(rng.normal(0, 0.022, (H // 2, W // 2)).astype(np.float32), (W, H))[..., None] for _ in range(6)]
    return np.clip(f * VIGN + GRAIN[n % 6], 0, 1)


def zoom(f, sc, cx=W / 2, cy=H / 2, rot=0.0, dx=0.0, dy=0.0):
    M = cv2.getRotationMatrix2D((cx, cy), rot, sc)
    M[0, 2] += dx
    M[1, 2] += dy
    return cv2.warpAffine(f, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)


def zoom_blur(f, amount):
    """Radial (zoom) blur: average of slightly scaled copies."""
    if amount <= 0.002:
        return f
    acc = np.zeros_like(f)
    k = 6
    for i in range(k):
        acc += zoom(f, 1 + amount * i / (k - 1))
    return acc / k


def blur(f, s):
    small = cv2.resize(f, (W // 4, H // 4), interpolation=cv2.INTER_AREA)
    return cv2.resize(cv2.GaussianBlur(small, (0, 0), s / 4), (W, H), interpolation=cv2.INTER_LINEAR)


LEAK = None


def light_leak(f, p):
    """Warm flash sweeping across at a cut (p: 0 → 1 → 0)."""
    global LEAK
    if LEAK is None:
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        LEAK = (xx, yy)
    if p <= 0:
        return f
    xx, yy = LEAK
    g = np.exp(-(((xx - W * (0.2 + 0.6 * p)) / 520) ** 2 + ((yy - H * 0.45) / 900) ** 2))[..., None]
    return f + g * np.array([1.0, 0.72, 0.2], np.float32) * 0.55 * math.sin(math.pi * p)


# ------------------------------------------------------------------ type ---
@lru_cache(maxsize=None)
def line(runs, size, bold=True):
    return E.T.line(list(runs), size, bold=bold, shadow=True, pad=30)


@lru_cache(maxsize=None)
def latin(text, size, color):
    return R.latin_layer(text, size, color, 800, 0.02)


def punch(f, layer, t, t0, t1, cy, cx=W / 2, big=1.25):
    """Kinetic text: slams in from a bigger, blurred state; leaves upward."""
    if not (t0 <= t < t1 + 0.25):
        return
    p = ease((t - t0) / 0.22)
    o = ease((t - t1) / 0.25)
    sc = big - (big - 1) * p - 0.04 * o
    lay = layer
    if p < 1:
        lay = cv2.GaussianBlur(layer, (0, 0), 1 + 8 * (1 - p))
    l2, x, y = R.warp_premul(lay, sc, cx, cy - 30 * o, (layer.shape[1] / 2, layer.shape[0] / 2))
    R.over(f, l2, x, y, min(1.0, p * 1.6) * (1 - o))


def shade(f, y0, y1, a):
    """Dark gradient band for legible text over footage."""
    yy = np.arange(H, dtype=np.float32)
    g = np.clip(np.minimum((yy - y0) / 200, (y1 - yy) / 200), 0, 1) * a
    f *= (1 - g)[:, None, None]


# --------------------------------------------------------------- product ---
CAN = None


def can_layer(h):
    global CAN
    if CAN is None:
        CAN = np.array(Image.open(ROOT / "assets/gen/can.png").convert("RGBA"))
    im = Image.fromarray(CAN).resize((int(CAN.shape[1] * h / CAN.shape[0]), h), Image.LANCZOS)
    return R.to_premul(np.array(im))


@lru_cache(maxsize=None)
def can_cached(h):
    return can_layer(h)


def can_with_sheen(h, p):
    lay = can_cached(h).copy()
    if 0 < p < 1:
        hh, ww = lay.shape[:2]
        yy, xx = np.mgrid[0:hh, 0:ww].astype(np.float32)
        pos = -0.4 * hh + (1.8 * hh) * ease(p)
        band = np.exp(-(((xx * 0.6 + yy) - pos) / 60) ** 2)[..., None]
        lay[..., :3] += band * lay[..., 3:4] * 0.5
    return lay


GLOW = None


def glow(f, cx, cy, a):
    global GLOW
    if GLOW is None:
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        GLOW = (xx, yy)
    xx, yy = GLOW
    g = np.exp(-(((xx - cx) / 330) ** 2 + ((yy - cy) / 620) ** 2))[..., None]
    f += g * np.array([1.0, 0.7, 0.12], np.float32) * 0.42 * a


def timer(f, t, t0, cx, cy):
    """Ring 0 → 15 with «دقيقة» under the number."""
    p = ease((t - t0 - 0.2) / 1.9)
    if t < t0:
        return
    a = min(1.0, (t - t0) / 0.3)
    s = 2
    m = np.zeros((300 * s, 300 * s), np.float32)
    c = (150 * s, 150 * s)
    cv2.circle(m, c, 120 * s, 0.25, 12 * s, cv2.LINE_AA)
    lay = np.zeros((300 * s, 300 * s, 4), np.float32)
    ring = np.zeros_like(m)
    if p > 0:
        cv2.ellipse(ring, c, (120 * s, 120 * s), -90, 0, 360 * p, 1.0, 14 * s, cv2.LINE_AA)
    m = cv2.resize(m, (300, 300), interpolation=cv2.INTER_AREA)
    ring = cv2.resize(ring, (300, 300), interpolation=cv2.INTER_AREA)
    lay = np.zeros((300, 300, 4), np.float32)
    lay[..., :3] = m[..., None] * np.array(WHT, np.float32) / 255 + ring[..., None] * np.array(YEL, np.float32) / 255
    lay[..., 3] = np.clip(m + ring, 0, 1)
    lay[..., :3] = np.minimum(lay[..., :3], lay[..., 3:4])
    bg = np.zeros((300, 300), np.float32)
    cv2.circle(bg, (150, 150), 140, 0.55, -1, cv2.LINE_AA)
    base = np.dstack([np.zeros((300, 300, 3), np.float32), bg])
    R.over(f, base, cx - 150, cy - 150, a)
    R.over(f, lay, cx - 150, cy - 150, a)
    num = latin(str(int(round(15 * p))), 110, WHT)
    R.over(f, num, cx - num.shape[1] / 2, cy - num.shape[0] / 2 - 22, a)
    lab = line((("دقيقة", YEL),), 40)
    R.over(f, lab, cx - lab.shape[1] / 2, cy + 18, a)


# ---------------------------------------------------------------- render ---
def frame(shots, t, n, logo, tr, end_bits):
    k = max(i for i, e in enumerate(EDL) if e[0] <= t)
    s0, s1, name, off = EDL[k]
    lt = t - s0
    fr = shots.get(name, int(round((lt + off) * FPS)))

    # per-shot camera: slow push, punch on the cut, the jolt in the first shot
    sc, rot, dx, dy = 1.04 + 0.06 * (lt / (s1 - s0)), 0.0, 0.0, 0.0
    sc += 0.08 * (1 - ease(lt / 0.25))
    if name == "shift":
        sc += 0.06
        for tj in (0.9, 1.6):
            if tj <= t < tj + 0.35:
                d = math.exp(-(t - tj) * 14)
                dx, dy, rot = 26 * d * math.sin(t * 90), 18 * d * math.cos(t * 75), 1.2 * d * math.sin(t * 60)
    f = zoom(fr, sc, W / 2, H * 0.42, rot, dx, dy)
    warm = -1.0 if t < 5.5 else 1.0
    if name in ("hero", "cta"):
        f = blur(f, 22) * 0.42
    if name == "bonnet" and lt + off < 1.0:
        f = blur(f, 18) * 0.45
    f = grade(f, warm)

    # whip into each cut (last 4 frames before, first 4 after)
    for c in CUTS:
        d = t - c
        if -0.13 < d < 0.13:
            f = zoom_blur(f, 0.12 * (1 - abs(d) / 0.13))
            f = light_leak(f, 0.5 + d / 0.26) if c >= 5.5 else f
    # red flashes on the jolts
    for tj in (0.9, 1.6):
        if tj <= t < tj + 0.3:
            f = f * (1 - 0.25 * math.exp(-(t - tj) * 10)) + np.array([0.35, 0.02, 0.0], np.float32) * math.exp(-(t - tj) * 10) * 0.6

    # ---- overlays per stage
    if t < 2.5:
        shade(f, 1150, 1750, 0.6)
        punch(f, line((("ناقل", WHT), ("الحركة", WHT)), 64), t, 0.25, 2.25, 1270)
        punch(f, line((("ينزلق؟", RED),), 150), t, 0.85, 2.25, 1420, big=1.6)
        punch(f, line((("أو", WHT), ("يسرّب", RED), ("الزيت؟", WHT)), 70), t, 1.55, 2.25, 1590)
    elif t < 5.5:
        shade(f, 1000, 1760, 0.55)
        for i, (w, at) in enumerate([("تسرّب", 2.65), ("انزلاق", 3.25), ("استهلاك للزيت", 3.85)]):
            punch(f, line(((w, RED),), 104), t, at, 5.25, 1150 + i * 175, big=1.5)
        punch(f, line((("في", WHT), ("نواقل", WHT), ("الحركة", WHT), ("الأوتوماتيكية", WHT)), 48, False), t, 4.45, 5.25, 1680)
    elif t < 8.5:
        lt = t - 5.5
        q = ease(lt / 0.6)
        glow(f, W / 2, 900, q)
        can = can_with_sheen(980, (lt - 0.9) / 1.0)
        l2, x, y = R.warp_premul(can, 1.18 - 0.18 * q + 0.02 * lt, W / 2, 900 - 10 * lt, (can.shape[1] / 2, can.shape[0] / 2))
        if q < 1:
            l2 = cv2.GaussianBlur(l2, (0, 0), 1 + 10 * (1 - q))
        R.over(f, l2, x, y, q)
        punch(f, line((("مانع", WHT), ("تسرّب", WHT), ("زيت", WHT), ("الجير", YEL)), 74), t, 6.2, 8.25, 1500)
        punch(f, latin("ATF Stop Leak & Conditioner", 46, YEL), t, 6.5, 8.25, 1605)
    elif t < 12.5:
        shade(f, 1250, 1800, 0.6)
        if t < 9.5:
            lt = t - 8.5
            glow(f, W / 2, 860, 0.8)
            ang = 13 * math.sin(lt * 2 * math.pi * 3.2) * ease(lt / 0.15)
            can = can_cached(820)
            acc = None
            for j, da in enumerate((-4, 0, 4)):          # motion blur of the shake
                l2, x, y = R.warp_premul(can, 1.0, W / 2, 860, (can.shape[1] / 2, can.shape[0] / 2))
                M = cv2.getRotationMatrix2D((W / 2 - x, 860 - y), ang + da * math.cos(lt * 20), 1.0)
                l3 = cv2.warpAffine(l2, M, (l2.shape[1], l2.shape[0]))
                acc = l3 if acc is None else acc + l3
            R.over(f, acc / 3, x, y)
        punch(f, step_chip("١", "رجّ العلبة جيداً"), t, 8.55, 9.4, 1430)
        punch(f, step_chip("٢", "أضفه إلى سائل ناقل الحركة"), t, 9.55, 12.3, 1430)
    elif t < 15.0:
        shade(f, 1250, 1800, 0.55)
        punch(f, step_chip("٣", "قُد السيارة 15 دقيقة"), t, 12.55, 14.8, 1430)
        timer(f, t, 12.6, W / 2, 520)
    elif t < 17.5:
        shade(f, 1100, 1800, 0.6)
        punch(f, line((("تبديل", WHT), ("سلس", YEL), ("وهادئ", YEL)), 96), t, 15.1, 17.3, 1230, big=1.4)
        punch(f, line((("بين", WHT), ("الغيارات", WHT)), 64), t, 15.3, 17.3, 1360)
        punch(f, line((("ويطيل", WHT), ("عمر", YEL), ("ناقل", YEL), ("الحركة", YEL)), 64), t, 16.3, 17.3, 1490)
        punch(f, end_bits["note"], t, 15.6, 17.3, 1640)
    else:
        lt = t - 17.5
        glow(f, W / 2, 820, ease(lt / 0.5))
        can = can_with_sheen(560, (lt - 1.2) / 0.9)
        q = ease(lt / 0.5)
        l2, x, y = R.warp_premul(can, 1.1 - 0.1 * q, W / 2, 830 - 8 * lt, (can.shape[1] / 2, can.shape[0] / 2))
        R.over(f, l2, x, y, q)
        punch(f, end_bits["logo"], t, 17.6, 21, 330)
        punch(f, line((("اطلبه", YEL), ("الآن", YEL), ("من", WHT), ("خلال", WHT)), 70), t, 17.9, 21, 1210)
        q = back((t - 18.2) / 0.4, 1.4)
        if q > 0:
            pill = end_bits["pill"].copy()
            sp = (t - 18.8) / 0.7
            if 0 < sp < 1:
                xs = np.arange(pill.shape[1], dtype=np.float32)
                band = np.exp(-((xs - (-80 + (pill.shape[1] + 160) * ease(sp))) / 40) ** 2)[None, :, None]
                pill[..., :3] += band * pill[..., 3:4] * 0.45
            lay, x, y = R.warp_premul(pill, 0.6 + 0.4 * q, W / 2, 1345, (pill.shape[1] / 2, pill.shape[0] / 2))
            R.over(f, lay, x, y, min(1.0, q))
        q = ease((t - 18.55) / 0.3)
        if q > 0:
            trk = tr.truck(ease((t - 18.55) / 0.8), 130)
            dl = end_bits["deliv"]
            row = dl.shape[1] + trk.shape[1]
            x0, yy = (W - row) / 2, 1480
            R.over(f, trk, x0, yy - trk.shape[0] / 2, q)
            R.over(f, dl, x0 + trk.shape[1], yy - dl.shape[0] / 2 + 4, q)
    if t < 17.5:
        R.over(f, logo, W - logo.shape[1] - 40, 70, ease((t - 0.2) / 0.4))
    f = np.clip(f, 0, 1)
    if t > DUR - 0.4:
        f *= max(0.0, (DUR - t) / 0.4) * 0.6 + 0.4
    return finish(f, n)


@lru_cache(maxsize=None)
def step_chip(num, text):
    txt = E.T.line([(text, WHT)], 62, bold=True, shadow=False, pad=8)
    d = 104
    h = max(txt.shape[0], d) + 34
    w = txt.shape[1] + d + 80
    s = 3
    img = np.zeros((h * s, w * s, 4), np.uint8)
    cv2.rectangle(img, (0, 0), (w * s, h * s), (16, 17, 18, 215), -1)
    cv2.rectangle(img, (w * s - 8 * s, 0), (w * s, h * s), YEL + (255,), -1)
    lay = R.to_premul(cv2.resize(img, (w, h), interpolation=cv2.INTER_AREA))
    disc = np.zeros((d, d, 4), np.uint8)
    cv2.circle(disc, (d // 2, d // 2), d // 2 - 2, YEL + (255,), -1, cv2.LINE_AA)
    disc = R.to_premul(disc)
    n = E.T.line([(num, (37, 39, 41))], 60, bold=True, shadow=False, pad=0)
    ys, xs = np.nonzero(n[..., 3] > 0.02)
    n = n[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    R.paste_into(disc, n, (d - n.shape[1]) // 2, (d - n.shape[0]) // 2)
    R.paste_into(lay, disc, w - d - 30, (h - d) // 2)
    R.paste_into(lay, txt, w - d - 50 - txt.shape[1], (h - txt.shape[0]) // 2)
    return lay


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--stills")
    a = ap.parse_args()
    out = ROOT / a.out
    out.parent.mkdir(parents=True, exist_ok=True)
    extract()
    shots = Shots()
    lg = Image.open(ROOT / "assets/gen/logo.png")
    logo = R.to_premul(np.array(lg.resize((190, int(lg.height * 190 / lg.width)), Image.LANCZOS)))
    big_logo = R.to_premul(np.array(lg.resize((440, int(lg.height * 440 / lg.width)), Image.LANCZOS)))
    note = E.T.line([("*غير مناسب لنواقل الحركة", SIL)], 34, bold=False, shadow=True, pad=10)
    cvt = R.latin_layer("CVT / DSG", 32, SIL, 700, 0.02)
    nb = np.zeros((max(note.shape[0], cvt.shape[0] + 20), note.shape[1] + cvt.shape[1] + 10, 4), np.float32)
    R.paste_into(nb, cvt, 0, (nb.shape[0] - cvt.shape[0]) // 2 + 2)
    R.paste_into(nb, note, cvt.shape[1] + 10, (nb.shape[0] - note.shape[0]) // 2)
    end_bits = {"logo": big_logo, "pill": V.url_pill(70), "note": nb,
                "deliv": E.T.line([("مع توفّر", WHT), ("خدمة التوصيل", YEL)], 52, bold=True, shadow=True, pad=8)}
    tr = V.EndCard(17.5)

    want, n_frames = None, int(DUR * FPS)
    if a.stills:
        want = {int(round(float(s) * FPS)) for s in a.stills.split(",")}
    tmp = out.with_name(out.stem + "_video.mp4")
    enc = None
    if want is None:
        enc = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                                "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "slow", "-crf", "16",
                                "-pix_fmt", "yuv420p", str(tmp)], stdin=subprocess.PIPE)
    for n in range(n_frames):
        if want is not None and n not in want:
            continue
        t = n / FPS
        img = (frame(shots, t, n, logo, tr, end_bits) * 255 + 0.5).astype(np.uint8)
        if want is not None:
            cv2.imwrite(str(out.parent / f"still_{t:05.2f}.png"), cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
        else:
            enc.stdin.write(img.tobytes())
    if enc is None:
        return
    enc.stdin.close()
    enc.wait()
    mix = ROOT / "assets/bgm/film_mix.wav"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(tmp), "-i", str(mix), "-filter_complex",
                    "[1:a]loudnorm=I=-13:TP=-1.5:LRA=9,aresample=48000,alimiter=limit=0.8:attack=1:release=60:level=false[a]",
                    "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-t", str(DUR),
                    "-movflags", "+faststart", str(out)], check=True)
    tmp.unlink(missing_ok=True)
    print("wrote", out)


if __name__ == "__main__":
    main()
