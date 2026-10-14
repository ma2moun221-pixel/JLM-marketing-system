"""JLM «العناية الدورية» — v3 edit in the client's third reference style
(brand/jlm/VIDEO_STYLE.md): one-line karaoke captions on a soft dark box at
2/3 height, round line-icon badges that draw themselves in the top corners
(red = problem, yellow = solution) with a small label pill, an "inside the
engine" explainer with numbered steps, the JLM logo and a jlmstore.com pill at
the end. Icon sounds are very soft (≈ −40 dBFS).

    python3 edit_v3.py --src CLIENT_VIDEO --out ../out/jlm_care_edit_v3.mp4 [--stills 1,5,...]
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
from PIL import Image

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import edit as E  # noqa: E402  (shared: R, T, IC, KIT, colours)

R, T, IC = E.R, E.T, E.IC
W, H, FPS = 1080, 1920, 30
YEL, WHT, CHA = E.YEL, E.WHT, E.CHA
RED = (240, 62, 50)
GREY = (168, 170, 172)
SRC_DUR = 23.9
HOLD = 1.0
DUR = SRC_DUR + HOLD
CAP_Y = 0.66 * H


def ease_io(x):
    return R.ease_in_out(x)


def back(x, s=1.4):
    x = R.clamp01(x)
    return 1 + (s + 1) * (x - 1) ** 3 + s * (x - 1) ** 2


# ------------------------------------------------------------ word timing ---
# Speech segments between pauses (from the Whisper transcript, refined by ear).
SEGMENTS = [
    (0.64, 2.87, "انت ما بتستنى المرض عشان تهتم"),
    (3.27, 3.56, "بحالك"),
    (3.82, 6.09, "وسيارتك كمان مش لازم"),
    (6.34, 7.65, "تستنى العطل عشان تهتم فيها"),
    (8.27, 9.63, "العناية الدورية بمنتجات"),
    (9.76, 12.36, "JLM بتساعد في الحفاظ على نظافة المحرّك"),
    (12.54, 13.30, "ونظام الوقود"),
    (13.81, 16.26, "وبتحافظ على أداء السيارة مع الاستخدام اليومي"),
    (17.24, 19.83, "اهتم بسيارتك اليوم ووفّر على نفسك أعطال بكرا"),
    (20.74, 21.14, "JLM"),
    (21.38, 23.23, "عناية احترافية تبدأ من الداخل"),
]

# Caption phrases in speech order. "!word" stays red (problem), "*word" stays
# yellow (key idea); other words are yellow only while spoken. "#" hides a
# phrase (the explainer's step titles carry it).
PHRASES = [
    "انت ما بتستنى !المرض", "عشان تهتم *بحالك", "وسيارتك كمان مش لازم", "تستنى !العطل عشان تهتم فيها",
    "*العناية *الدورية", "بمنتجات *JLM", "بتساعد في الحفاظ",
    "#على نظافة المحرّك", "#ونظام الوقود", "#وبتحافظ على أداء السيارة", "#مع الاستخدام اليومي",
    "اهتم بسيارتك *اليوم", "ووفّر على نفسك", "!أعطال بكرا", "*JLM عناية احترافية", "تبدأ من *الداخل",
]


def voiced_weight(src):
    """Per-10 ms speech weight from the source audio (0 in pauses)."""
    sr = 16000
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", src, "-ac", "1", "-ar", str(sr), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    x = np.frombuffer(raw, np.float32)
    hop = sr // 100
    n = len(x) // hop
    rms = np.sqrt((x[: n * hop].reshape(n, hop) ** 2).mean(1) + 1e-12)
    rms = np.convolve(rms, np.ones(3) / 3, mode="same")
    lo, hi = np.percentile(rms, 15), np.percentile(rms, 97)
    return np.clip((rms - lo) / (hi - lo), 0, 1) ** 0.6


def word_times(weight):
    """[(start, end, word)] — each word starts where its share of characters
    falls on the cumulative speech weight inside its segment."""
    out = []
    for t0, t1, text in SEGMENTS:
        words = text.split()
        i0, i1 = int(t0 * 100), int(t1 * 100)
        w = weight[i0:i1] + 1e-3
        c = np.concatenate([[0], np.cumsum(w)]) / w.sum()
        lens = [len(x) + 1 for x in words]
        acc = np.concatenate([[0], np.cumsum(lens)]) / sum(lens)
        starts = [t0 + np.searchsorted(c, a) / 100 for a in acc[:-1]]
        ends = starts[1:] + [t1]
        out += [(s, e, wd) for s, e, wd in zip(starts, ends, words)]
    return out


class Captions:
    def __init__(self, words):
        self.phrases = []
        k = 0
        for ph in PHRASES:
            hidden = ph.startswith("#")
            toks = ph.lstrip("#").split()
            items = []
            for tok in toks:
                tone = tok[0] if tok[0] in "!*" else ""
                s, e, wd = words[k]
                assert wd == tok.lstrip("!*"), (wd, tok)
                items.append((wd, tone, s, e))
                k += 1
            self.phrases.append({"items": items, "hidden": hidden})
        assert k == len(words)
        for i, p in enumerate(self.phrases):
            nxt = self.phrases[i + 1]["items"][0][2] if i + 1 < len(self.phrases) else DUR
            p["t0"] = p["items"][0][2]
            p["t1"] = min(nxt, p["items"][-1][3] + 0.45) if i + 1 < len(self.phrases) else DUR
        self.words = {wd: s for p in self.phrases for wd, _, s, _ in p["items"]}

    def at(self, word, nth=0):
        hits = [s for p in self.phrases for wd, _, s, _ in p["items"] if wd == word]
        return hits[nth]

    @staticmethod
    @lru_cache(maxsize=None)
    def line(key):
        items, active = key
        runs = []
        for i, (wd, tone) in enumerate(items):
            if i > active:
                col = GREY
            elif tone == "!":
                col = RED
            elif tone == "*" or i == active:
                col = YEL
            else:
                col = WHT
            runs.append((wd, col))
        txt = E.T.line(runs, 64, bold=True, shadow=True, pad=26)
        box = soft_box(txt.shape[1] - 18, txt.shape[0] - 30)
        out = np.zeros((max(box.shape[0], txt.shape[0]), max(box.shape[1], txt.shape[1]), 4), np.float32)
        R.paste_into(out, box, (out.shape[1] - box.shape[1]) // 2, (out.shape[0] - box.shape[0]) // 2)
        R.paste_into(out, txt, (out.shape[1] - txt.shape[1]) // 2, (out.shape[0] - txt.shape[0]) // 2)
        return out

    def draw(self, f, t, y=CAP_Y):
        for p in self.phrases:
            if p["hidden"] or not (p["t0"] <= t < p["t1"]):
                continue
            active = max(i for i, it in enumerate(p["items"]) if it[2] <= t)
            layer = self.line((tuple((wd, tone) for wd, tone, _, _ in p["items"]), active))
            a = min(1.0, (t - p["t0"]) / 0.08)
            R.over(f, layer, (W - layer.shape[1]) / 2, y - layer.shape[0] / 2, a)


@lru_cache(maxsize=None)
def soft_box(w, h, alpha=0.48, r=18):
    pad = 14
    m = np.zeros((h + 2 * pad, w + 2 * pad), np.float32)
    cv2.rectangle(m, (pad + r, pad), (pad + w - r, pad + h), 1, -1)
    cv2.rectangle(m, (pad, pad + r), (pad + w, pad + h - r), 1, -1)
    for cx, cy in [(pad + r, pad + r), (pad + w - r, pad + r), (pad + r, pad + h - r), (pad + w - r, pad + h - r)]:
        cv2.circle(m, (cx, cy), r, 1, -1, cv2.LINE_AA)
    m = cv2.GaussianBlur(m, (0, 0), 5) * alpha
    out = np.zeros(m.shape + (4,), np.float32)
    out[..., :3] = np.array([0.03, 0.03, 0.035], np.float32) * m[..., None]
    out[..., 3] = m
    return out


# ------------------------------------------------------------ line icons ---
# Unit coordinates (−1..1, y down). Each icon is a list of strokes drawn in order.
def _arc(cx, cy, rx, ry, a0, a1, n=48):
    a = np.radians(np.linspace(a0, a1, n))
    return np.stack([cx + rx * np.cos(a), cy + ry * np.sin(a)], 1)


def _rrect(x0, y0, x1, y1, r):
    pts = []
    for cx, cy, a0 in [(x1 - r, y0 + r, -90), (x1 - r, y1 - r, 0), (x0 + r, y1 - r, 90), (x0 + r, y0 + r, 180)]:
        pts.append(_arc(cx, cy, r, r, a0, a0 + 90, 10))
    p = np.concatenate(pts)
    return np.concatenate([p, p[:1]])


def _car(sign):
    roof = np.array([[-0.62, 0.02], [-0.44, -0.36], [0.44, -0.36], [0.62, 0.02]])
    body = _rrect(-0.78, 0.02, 0.78, 0.40, 0.10)
    wl = np.array([[-0.56, 0.40], [-0.56, 0.56], [-0.34, 0.56], [-0.34, 0.40]])
    wr = wl * [-1, 1]
    lamp_l, lamp_r = _arc(-0.50, 0.21, 0.08, 0.08, 0, 360, 20), _arc(0.50, 0.21, 0.08, 0.08, 0, 360, 20)
    strokes = [roof, body, wl, wr, lamp_l, lamp_r]
    if sign == "!":
        strokes += [np.array([[0, -0.80], [0, -0.58]]), _arc(0, -0.48, 0.025, 0.025, 0, 360, 10)]
    else:
        strokes += [np.array([[-0.20, -0.66], [-0.04, -0.52], [0.24, -0.80]])]
    return strokes


def _heart():
    a = np.linspace(0, 2 * np.pi, 120)
    x = 16 * np.sin(a) ** 3
    y = -(13 * np.cos(a) - 5 * np.cos(2 * a) - 2 * np.cos(3 * a) - np.cos(4 * a))
    heart = np.stack([x, y + 1.5], 1) / 17 * 0.80
    ecg = np.array([[-0.95, 0.04], [-0.42, 0.04], [-0.28, -0.30], [-0.10, 0.38], [0.06, -0.12], [0.16, 0.04], [0.95, 0.04]])
    return [heart, ecg]


def _calendar():
    return [_rrect(-0.62, -0.50, 0.62, 0.66, 0.12), np.array([[-0.62, -0.18], [0.62, -0.18]]),
            np.array([[-0.32, -0.68], [-0.32, -0.36]]), np.array([[0.32, -0.68], [0.32, -0.36]]),
            np.array([[-0.26, 0.22], [-0.06, 0.42], [0.30, 0.02]])]


def _coins():
    s = []
    for k, y in enumerate([0.46, 0.18, -0.10]):
        s.append(_arc(-0.10, y, 0.46, 0.14, 0, 360, 40))
        if k:
            s.append(np.array([[-0.56, y], [-0.56, y + 0.28]]))
            s.append(np.array([[0.36, y], [0.36, y + 0.28]]))
    s.append(np.array([[0.66, -0.70], [0.66, 0.10]]))
    s.append(np.array([[0.50, -0.06], [0.66, 0.12], [0.82, -0.06]]))
    return s


def _shield():
    t = np.linspace(0, 1, 30)
    right = np.stack([0.62 - 0.0 * t, -0.52 + 0.52 * t], 1)
    curve = np.stack([0.62 * np.cos(t * np.pi / 2), 0.0 + 0.78 * np.sin(t * np.pi / 2)], 1)
    side = np.concatenate([[[0, -0.82]], [[0.62, -0.58]], right, curve[1:]])
    shield = np.concatenate([side[::-1] * [-1, 1], side[1:]])
    drop = np.concatenate([[[0, -0.40]], _arc(0, 0.12, 0.24, 0.24, -30, 210, 30), [[0, -0.40]]])
    return [shield, drop]


ICONS = {"heart": _heart, "car_warn": lambda: _car("!"), "car_ok": lambda: _car("v"),
         "calendar": _calendar, "coins": _coins, "shield": _shield}


def partial_strokes(strokes, p):
    lens = [np.linalg.norm(np.diff(s, axis=0), axis=1) for s in strokes]
    total = sum(l.sum() for l in lens)
    left = p * total
    out = []
    for s, l in zip(strokes, lens):
        if left <= 0:
            break
        if l.sum() <= left:
            out.append(s)
            left -= l.sum()
            continue
        c = np.concatenate([[0], np.cumsum(l)])
        j = np.searchsorted(c, left) - 1
        u = (left - c[j]) / max(l[j], 1e-6)
        out.append(np.concatenate([s[: j + 1], [s[j] + (s[j + 1] - s[j]) * u]]))
        left = 0
    return out


# ---------------------------------------------------------------- badges ---
BADGE = 232            # disc diameter, px


@lru_cache(maxsize=None)
def disc_layer():
    s = BADGE + 60
    yy, xx = np.mgrid[0:s, 0:s].astype(np.float32)
    c = s / 2
    r = np.hypot(xx - c, yy - c) / (BADGE / 2)
    inside = np.clip((1 - r) * BADGE / 2 + 0.5, 0, 1)
    shade = np.clip(1 - np.hypot(xx - c + 0.25 * BADGE, yy - c + 0.30 * BADGE) / BADGE, 0, 1)
    col = np.array([0.05, 0.055, 0.065]) + shade[..., None] * np.array([0.13, 0.14, 0.16])
    shadow = cv2.GaussianBlur(np.clip((1.06 - r) * 20, 0, 1), (0, 0), 10) * 0.45
    shadow = np.roll(shadow, 6, axis=0)
    a = inside + shadow * (1 - inside)
    rgb = col * inside[..., None]
    return np.dstack([rgb, a]).astype(np.float32)


@lru_cache(maxsize=None)
def label_layer(text, color):
    txt = E.T.line([(text, WHT)], 34, bold=True, shadow=False, pad=0)
    h = txt.shape[0] + 18
    w = txt.shape[1] + 40
    s = 3
    img = np.zeros((h * s, w * s, 4), np.uint8)
    r = h * s // 2
    col = tuple(int(c) for c in color)
    for fill, inset in [(col + (255,), 0), ((8, 8, 9, 235), 3 * s)]:
        cv2.rectangle(img, (r, inset), (w * s - r, h * s - inset), fill, -1)
        cv2.circle(img, (r, r), r - inset, fill, -1, cv2.LINE_AA)
        cv2.circle(img, (w * s - r, r), r - inset, fill, -1, cv2.LINE_AA)
    pill = R.to_premul(cv2.resize(img, (w, h), interpolation=cv2.INTER_AREA))
    R.paste_into(pill, txt, (w - txt.shape[1]) // 2, (h - txt.shape[0]) // 2 + 1)
    return pill


def badge_layer(icon, color, lt):
    """Badge at local time lt (s since it appears): disc pops in, the ring
    draws clockwise, the icon draws itself stroke by stroke with a glow."""
    s = BADGE + 60
    ss = 2
    disc = disc_layer()
    col = np.array(color, np.float32) / 255
    line = np.zeros((s * ss, s * ss), np.float32)
    c = s * ss / 2
    pr = ease_io((lt - 0.08) / 0.40)
    if pr > 0:
        pts = _arc(c, c, (BADGE / 2 - 3) * ss, (BADGE / 2 - 3) * ss, -90, -90 + 360 * pr, 90)
        cv2.polylines(line, [np.round(pts * 4).astype(np.int32)], False, 0.85, 3 * ss, cv2.LINE_AA, shift=2)
    pi = ease_io((lt - 0.22) / 0.65)
    if pi > 0:
        sc = BADGE * 0.27 * ss
        for st in partial_strokes(ICONS[icon](), pi):
            pts = np.round((st * sc + c) * 4).astype(np.int32)
            cv2.polylines(line, [pts], False, 1.0, int(5.5 * ss), cv2.LINE_AA, shift=2)
    line = cv2.resize(line, (s, s), interpolation=cv2.INTER_AREA)
    glow = cv2.GaussianBlur(line, (0, 0), 7) * 0.9
    a_line = np.clip(line, 0, 1)
    out = disc.copy()
    out[..., :3] += glow[..., None] * col * 0.8
    out[..., :3] = out[..., :3] * (1 - a_line[..., None]) + a_line[..., None] * np.minimum(col * 1.08, 1)
    out[..., 3] = np.maximum(out[..., 3], np.clip(glow * 0.6 + a_line, 0, 1))
    return out


class Badges:
    """(t_in, t_out, icon, colour, label, side) — side: 'L' / 'R' top corner."""

    def __init__(self, items):
        self.items = items

    def draw(self, f, t):
        for t0, t1, icon, color, label, side in self.items:
            if not (t0 <= t < t1 + 0.25):
                continue
            lt = t - t0
            out = 1 - ease_io((t - t1) / 0.25)
            cx = 0.17 * W if side == "L" else 0.83 * W
            cy = 0.165 * H
            layer = badge_layer(icon, color, lt)
            sc = (0.35 + 0.65 * back(lt / 0.32)) * (0.92 + 0.08 * out)
            lay, x, y = R.warp_premul(layer, sc, cx, cy, (layer.shape[1] / 2, layer.shape[0] / 2))
            R.over(f, lay, x, y, min(1.0, lt / 0.08) * out)
            q = ease_io((lt - 0.45) / 0.25)
            if q > 0:
                lab = label_layer(label, color)
                R.over(f, lab, cx - lab.shape[1] / 2, cy + BADGE / 2 + 4 + 10 * (1 - q), q * out)


# ------------------------------------------------------------- explainer ---
GOLD = np.array([1.0, 0.74, 0.16], np.float32)
LINE = (0.36, 0.38, 0.41)
WORLD_H = 3600


def _sprite(r):
    k = int(r * 3)
    yy, xx = np.mgrid[-k:k + 1, -k:k + 1].astype(np.float32)
    g = np.exp(-(xx ** 2 + yy ** 2) / (2 * r * r))
    return g


SPR = _sprite(5.0)
SPR_BIG = _sprite(11.0)


def add_spr(f, x, y, gain, spr=SPR, col=GOLD):
    k = spr.shape[0] // 2
    x, y = int(round(x)), int(round(y))
    x0, y0, x1, y1 = max(x - k, 0), max(y - k, 0), min(x + k + 1, W), min(y + k + 1, H)
    if x0 >= x1 or y0 >= y1:
        return
    f[y0:y1, x0:x1] += spr[y0 - y + k:y1 - y + k, x0 - x + k:x1 - x + k, None] * col * gain


def _resample(pts, step=4.0):
    pts = np.asarray(pts, np.float32)
    seg = np.linalg.norm(np.diff(pts, axis=0), axis=1)
    c = np.concatenate([[0], np.cumsum(seg)])
    s = np.arange(0, c[-1], step)
    x = np.interp(s, c, pts[:, 0])
    y = np.interp(s, c, pts[:, 1])
    return np.stack([x, y], 1)


class Explainer:
    """Dark JLM board, camera pans down a gold flow: 1 engine deposits wash
    away, 2 fuel rail + injectors clear and spray, 3 the performance gauge rises."""

    CYL = [300, 460, 620, 780]

    def __init__(self, a, t1, t2, t3, b):
        self.a, self.t1, self.t2, self.t3, self.b = a, t1, t2, t3, b
        self.paths = [_resample([(540, -200), (540, 200), (420, 320), (420, 470), (540, 560)]),
                      _resample([(540, 1200), (540, 1290), (700, 1400), (700, 1590)]),
                      _resample([(880, 1620), (960, 1620), (960, 1880), (540, 2020), (540, 2210)])]
        self.fronts = [(a - 0.3, t1 + 0.05), (t2 - 0.40, t2 + 0.02), (t3 - 0.40, t3 + 0.02)]
        rng = np.random.default_rng(11)
        self.deposits = []
        for cx in self.CYL:
            for _ in range(15):
                side = rng.choice([-1, 1])
                x = cx + side * rng.uniform(34, 52)
                y = rng.uniform(650, 1060)
                self.deposits.append((x, y, rng.uniform(6, 13)))
            for _ in range(5):
                self.deposits.append((cx + rng.uniform(-50, 50), rng.uniform(630, 660), rng.uniform(6, 11)))
        self.spray = rng.uniform(-1, 1, (36, 2))
        self.world = self._world()
        self.titles = [self._title(1, "نظافة المحرّك"), self._title(2, "نظام الوقود"), self._title(3, "أداء السيارة")]
        self.bar_lab = E.T.line([("نسبة الرواسب", GREY)], 26, bold=False, shadow=False, pad=4)

    # -- static board -------------------------------------------------------
    def _world(self):
        w = np.zeros((WORLD_H, W, 3), np.float32)
        w[:] = np.array([0.055, 0.058, 0.066], np.float32)
        for x in range(0, W, 60):
            w[:, x] += 0.012
        for y in range(0, WORLD_H, 60):
            w[y, :] += 0.012
        L = LINE

        def poly(pts, th=3):
            cv2.polylines(w, [np.round(np.asarray(pts) * 4).astype(np.int32)], False, L, th, cv2.LINE_AA, shift=2)

        for p in self.paths:
            poly(p, 3)
        poly(_rrect(190, 560, 890, 1200, 30), 3)
        for cx in self.CYL:
            poly(_rrect(cx - 60, 620, cx + 60, 1080, 10), 3)
        poly(np.array([[200, 1140], [880, 1140]]), 2)
        poly(_rrect(200, 1598, 880, 1642, 22), 3)
        for cx in self.CYL:
            poly(_rrect(cx - 24, 1642, cx + 24, 1770, 8), 3)
            poly(np.array([[cx - 14, 1770], [cx, 1800], [cx + 14, 1770]]), 3)
        g = (540, 2500)
        cv2.ellipse(w, g, (300, 300), 0, 135, 405, (0.16, 0.17, 0.19), 26, cv2.LINE_AA)
        for k in range(11):
            ang = math.radians(135 + 27 * k)
            p0 = (g[0] + 250 * math.cos(ang), g[1] + 250 * math.sin(ang))
            p1 = (g[0] + 222 * math.cos(ang), g[1] + 222 * math.sin(ang))
            poly(np.array([p0, p1]), 3)
        for txt, x, y in [("ENGINE", 212, 1180), ("FUEL SYSTEM", 212, 1580), ("PERFORMANCE", 452, 2860)]:
            lab = R.latin_layer(txt, 24, (120, 124, 128), 600, 0.12)
            h, ww = lab.shape[:2]
            reg = w[y - h // 2:y - h // 2 + h, x:x + ww]
            reg *= 1 - lab[..., 3:4]
            reg += lab[..., :3]
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        self.top_fade = (1 - 0.72 * np.clip((500 - np.arange(500, dtype=np.float32)) / 200, 0, 1))[:, None, None]
        self.vign = (1 - 0.55 * np.clip(np.hypot((xx - W / 2) / W, (yy - H / 2) / H) * 1.25, 0, 1) ** 2)[..., None]
        return w

    @staticmethod
    def _title(n, text):
        num = np.zeros((70, 70, 4), np.uint8)
        cv2.circle(num, (35, 35), 30, YEL + (255,), -1, cv2.LINE_AA)
        num = R.to_premul(num)
        d = R.latin_layer(str(n), 40, CHA, 900, 0)
        R.paste_into(num, d, (70 - d.shape[1]) // 2, (70 - d.shape[0]) // 2)
        txt = E.T.line([(text, WHT)], 66, bold=True, shadow=True, pad=20)
        return num, txt

    def cam(self, t):
        cy = 880 + 60 * (1 - R.ease_out((t - self.a) / 0.8))
        cy += (1720 - 880) * ease_io((t - (self.t2 - 0.42)) / 0.45)
        cy += (2500 - 1720) * ease_io((t - (self.t3 - 0.42)) / 0.45)
        return cy

    # -- per frame ----------------------------------------------------------
    def frame(self, t):
        cy = self.cam(t)
        top = int(round(cy - H / 2))
        f = self.world[max(top, 0):top + H].copy()
        if f.shape[0] < H:
            pad = np.zeros((H - f.shape[0], W, 3), np.float32) + self.world[0, 0]
            f = np.concatenate([pad, f]) if top < 0 else np.concatenate([f, pad])
        oy = -top
        light = np.zeros((H, W), np.float32)

        # gold flow in the pipes
        for path, (f0, f1) in zip(self.paths, self.fronts):
            u = ease_io((t - f0) / (f1 - f0))
            if u <= 0:
                continue
            n = max(2, int(len(path) * u))
            seg = path[:n] + [0, oy]
            cv2.polylines(light, [np.round(seg * 4).astype(np.int32)], False, 1.0, 5, cv2.LINE_AA, shift=2)
            L = len(path)
            for k in range(26):
                ph = (t * 0.55 + k / 26) % 1.0
                i = int(ph * L)
                if i < n:
                    x, y = path[i] + [0, oy]
                    add_spr(f, x + 4 * math.sin(k * 7.1 + t * 3), y, 0.9)

        # 1 · engine: pistons, deposits washed away by a gold band
        band = 630 + 460 * ease_io((t - self.t1 - 0.05) / 1.05)
        active = t >= self.t1 - 0.02
        for i, cx in enumerate(self.CYL):
            ph = t * 5.0 + i * math.pi / 2
            py = 900 + 70 * math.sin(ph) + oy
            cv2.rectangle(f, (cx - 50, int(py - 40)), (cx + 50, int(py + 40)), (0.22, 0.23, 0.25), -1, cv2.LINE_AA)
            cv2.rectangle(f, (cx - 50, int(py - 40)), (cx + 50, int(py + 40)), LINE, 2, cv2.LINE_AA)
            cv2.line(f, (cx, int(py + 40)), (cx + int(30 * math.cos(ph)), int(1140 + oy)), LINE, 3, cv2.LINE_AA)
            if active:
                y0, y1 = 622 + oy, int(min(band, 1078)) + oy
                if y1 > y0:
                    yy = np.arange(y0, y1, dtype=np.float32)
                    g = 0.10 + 0.55 * np.exp(-((yy - (band + oy)) / 40.0) ** 2)
                    ya, yb = max(int(y0), 0), min(int(y1), H)
                    if yb > ya:
                        f[ya:yb, cx - 58:cx + 58] += g[ya - int(y0):yb - int(y0), None, None] * GOLD * 0.55
        for x, y, r in self.deposits:
            q = ease_io((band - y + 20) / 90) if active else 0
            if q >= 1:
                continue
            rr = r * (1 - 0.6 * q)
            col = np.array([0.03, 0.025, 0.02]) * (1 - q) + np.array([0.06, 0.05, 0.03]) * q
            cv2.circle(f, (int(x), int(y + oy)), max(1, int(rr)), col.tolist(), -1, cv2.LINE_AA)
            if 0 < q < 1:
                add_spr(f, x, y + oy, 0.7 * (1 - q))

        # 2 · fuel rail fills, injectors clear and spray
        xf = 200 + 680 * ease_io((t - self.t2) / 0.55)
        if t >= self.t2:
            cv2.rectangle(light, (204, int(1603 + oy)), (int(xf), int(1637 + oy)), 0.55, -1, cv2.LINE_AA)
        for i, cx in enumerate(self.CYL):
            ta = self.t2 + (cx - 200) / 680 * 0.55
            q = ease_io((t - ta) / 0.3)
            tip = (cx, 1800 + oy)
            if q < 1:
                cv2.circle(f, (cx, int(1796 + oy)), int(14 * (1 - q)) + 1, (0.03, 0.025, 0.02), -1, cv2.LINE_AA)
            if q > 0:
                cv2.rectangle(light, (cx - 20, int(1646 + oy)), (cx + 20, int(1766 + oy)), 0.30 * q, -1)
                for k, (u, v) in enumerate(self.spray):
                    ph = (t * 1.6 + (k / len(self.spray))) % 1.0
                    d = 14 + 170 * ph
                    ang = math.radians(90 + 20 * u)
                    add_spr(f, tip[0] + d * math.cos(ang), tip[1] + d * math.sin(ang), 0.75 * q * (1 - ph))

        # 3 · performance gauge
        v = 0.18 + 0.70 * ease_io((t - self.t3 - 0.1) / 1.3)
        g = (540, int(2500 + oy))
        cv2.ellipse(light, g, (300, 300), 0, 135, 135 + 270 * v, 1.0, 22, cv2.LINE_AA)
        ang = math.radians(135 + 270 * v)
        tip = (int(g[0] + 236 * math.cos(ang)), int(g[1] + 236 * math.sin(ang)))
        cv2.line(light, g, tip, 0.9, 6, cv2.LINE_AA)
        cv2.circle(f, g, 34, (0.10, 0.10, 0.11), -1, cv2.LINE_AA)
        cv2.circle(light, g, 34, 0.9, 4, cv2.LINE_AA)

        glow = cv2.GaussianBlur(light, (0, 0), 9)
        f += (np.minimum(light, 1)[..., None] * 0.95 + glow[..., None] * 0.9) * GOLD
        f *= self.vign
        f[:500] *= self.top_fade

        # step titles (number circle + title), fixed on screen
        steps = [self.t1, self.t2, self.t3, self.b + 1]
        for k, (num, txt) in enumerate(self.titles):
            s0, s1 = steps[k], steps[k + 1]
            p_in = ease_io((t - s0) / 0.22)
            p_out = ease_io((t - s1 + 0.05) / 0.15)
            al = p_in * (1 - p_out)
            if al <= 0:
                continue
            dy = 14 * (1 - p_in)
            R.over(f, num, (W - num.shape[1]) / 2, 190 + dy, al)
            R.over(f, txt, (W - txt.shape[1]) / 2, 262 + dy, al)
            if k == 0:
                fill = 1 - 0.85 * ease_io((t - self.t1 - 0.05) / 1.05)
                bx0, bx1, by = 360, 720, 410
                cv2.line(f, (bx0, by), (bx1, by), (0.18, 0.18, 0.2), 8, cv2.LINE_AA)
                c = np.array(RED, np.float32) / 255 * fill + np.array(YEL, np.float32) / 255 * (1 - fill)
                cv2.line(f, (bx0, by), (int(bx0 + (bx1 - bx0) * fill), by), (c * al).tolist(), 8, cv2.LINE_AA)
                R.over(f, self.bar_lab, (W - self.bar_lab.shape[1]) / 2, by + 10, al)
        return np.clip(f, 0, 1)


# ------------------------------------------------------------ end assets ---
def url_pill():
    txt = R.latin_layer("jlmstore.com", 40, CHA, 800, 0.01)
    h, w = 66, txt.shape[1] + 30
    s = 3
    img = np.zeros((h * s, w * s, 4), np.uint8)
    r = h * s // 2
    cv2.rectangle(img, (r, 0), (w * s - r, h * s), YEL + (255,), -1)
    cv2.circle(img, (r, r), r, YEL + (255,), -1, cv2.LINE_AA)
    cv2.circle(img, (w * s - r, r), r, YEL + (255,), -1, cv2.LINE_AA)
    pill = R.to_premul(cv2.resize(img, (w, h), interpolation=cv2.INTER_AREA))
    R.paste_into(pill, txt, (w - txt.shape[1]) // 2, (h - txt.shape[0]) // 2)
    return pill


def chip(runs):
    txt = E.T.line(runs, 44, bold=True, shadow=False, pad=0)
    h, w = txt.shape[0] + 28, txt.shape[1] + 48
    s = 3
    img = np.zeros((h * s, w * s, 4), np.uint8)
    cv2.rectangle(img, (0, 0), (w * s - 1, h * s - 1), YEL + (255,), -1)
    cv2.rectangle(img, (3 * s, 3 * s), (w * s - 1 - 3 * s, h * s - 1 - 3 * s), (14, 15, 16, 235), -1)
    im = R.to_premul(cv2.resize(img, (w, h), interpolation=cv2.INTER_AREA))
    mask = np.zeros((h, w), np.float32)
    rr = 16
    cv2.rectangle(mask, (rr, 0), (w - rr, h), 1, -1)
    cv2.rectangle(mask, (0, rr), (w, h - rr), 1, -1)
    for cx, cy in [(rr, rr), (w - rr, rr), (rr, h - rr), (w - rr, h - rr)]:
        cv2.circle(mask, (cx, cy), rr, 1, -1, cv2.LINE_AA)
    im *= mask[..., None]
    R.paste_into(im, txt, (w - txt.shape[1]) // 2, (h - txt.shape[0]) // 2 + 2)
    return im


def logo_layer(width):
    im = Image.open(E.KIT / "logos/logo_on_dark.png").convert("RGBA")
    im = im.resize((width, int(im.height * width / im.width)), Image.LANCZOS)
    lay = R.to_premul(np.array(im))
    a = cv2.GaussianBlur(lay[..., 3], (0, 0), 8) * 0.5
    pad = 20
    out = np.zeros((lay.shape[0] + 2 * pad, lay.shape[1] + 2 * pad, 4), np.float32)
    out[pad + 4:pad + 4 + lay.shape[0], pad:pad + lay.shape[1], 3] = a
    R.paste_into(out, lay, pad, pad)
    return out


# ----------------------------------------------------------------- audio ---
def soft_tick(sr, f0=480.0, amp=0.010):
    """Rounded, very quiet tick (≈ −40 dBFS): no transient edge, no highs."""
    n = int(0.16 * sr)
    t = np.arange(n) / sr
    env = np.minimum(1, t / 0.008) * np.exp(-t / 0.05)
    x = np.sin(2 * np.pi * f0 * t) + 0.25 * np.sin(2 * np.pi * f0 * 1.5 * t)
    return (x * env * amp).astype(np.float32)


def soft_swell(sr, dur=0.7, amp=0.012):
    rng = np.random.default_rng(4)
    n = int(dur * sr)
    w = np.convolve(rng.standard_normal(n), np.ones(220) / 220, mode="same")
    w = np.convolve(w, np.ones(220) / 220, mode="same")
    env = np.sin(np.linspace(0, np.pi, n)) ** 2
    return (w / (np.abs(w).max() + 1e-9) * env * amp).astype(np.float32)


def bed(sr, dur):
    t = np.arange(int(dur * sr)) / sr
    x = np.zeros_like(t)
    for f0 in (110.0, 164.8, 220.0, 277.2):
        x += np.sin(2 * np.pi * f0 * t) + 0.3 * np.sin(2 * np.pi * f0 * 2.002 * t)
    lfo = 0.75 + 0.25 * np.sin(2 * np.pi * 0.12 * t)
    env = np.minimum(1, t / 1.5) * np.minimum(1, (dur - t) / 1.0)
    return (x / 5.2 * lfo * env * 0.018).astype(np.float32)


def sfx_track(path, ticks, swells):
    sr = 48000
    n = int(DUR * sr)
    buf = bed(sr, DUR)

    def place(sig, at):
        i = int(at * sr)
        if i < 0:
            sig, i = sig[-i:], 0
        m = min(len(sig), n - i)
        buf[i:i + m] += sig[:m]

    for at, f0 in ticks:
        place(soft_tick(sr, f0), at)
    for at in swells:
        place(soft_swell(sr), at - 0.35)
    pcm = (np.clip(np.stack([buf, buf], 1), -1, 1) * 32767).astype(np.int16)
    with wave.open(str(path), "wb") as wv:
        wv.setnchannels(2)
        wv.setsampwidth(2)
        wv.setframerate(sr)
        wv.writeframes(pcm.tobytes())


# ------------------------------------------------------------------- main ---
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--stills")
    a = ap.parse_args()
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)

    caps = Captions(word_times(voiced_weight(a.src)))
    at = caps.at
    t_engine, t_fuel, t_perf = at("نظافة"), at("ونظام"), at("أداء")
    anim = (at("على", 0) - 0.12, SEGMENTS[7][1] + 0.12)
    expl = Explainer(anim[0], t_engine, t_fuel, t_perf, anim[1])
    end_t = at("JLM", 1)
    badges = Badges([
        (at("المرض"), at("وسيارتك") + 0.2, "heart", RED, "صحّتك أولًا", "L"),
        (at("العطل"), at("العناية") - 0.1, "car_warn", RED, "لا تنتظر العطل", "R"),
        (at("العناية"), anim[0] - 0.05, "calendar", YEL, "عناية دورية", "L"),
        (at("اهتم"), end_t - 0.2, "car_ok", YEL, "اهتم اليوم", "R"),
        (at("ووفّر"), end_t - 0.2, "coins", YEL, "وفّر بكرا", "L"),
        (at("عناية"), DUR + 1, "shield", YEL, "حماية من الداخل", "L"),
    ])
    prod = chip([("منتجات", WHT), ("JLM", YEL), ("للعناية الدورية", WHT)])
    prod_t = (at("JLM", 0), anim[0] - 0.05)
    logo = logo_layer(330)
    pill = url_pill()
    print(f"anim {anim[0]:.2f}–{anim[1]:.2f}  steps {t_engine:.2f} {t_fuel:.2f} {t_perf:.2f}  end {end_t:.2f}")
    for p in caps.phrases:
        print(f"  {p['t0']:5.2f}–{p['t1']:5.2f} {'#' if p['hidden'] else ' '} " + " ".join(w for w, *_ in p["items"]))

    src = subprocess.Popen(["ffmpeg", "-v", "error", "-i", a.src, "-vf",
                            f"scale={W}:{H}:flags=lanczos,eq=contrast=1.04:saturation=1.05",
                            "-f", "rawvideo", "-pix_fmt", "rgb24", "-r", str(FPS), "-"], stdout=subprocess.PIPE)
    want = None
    n_frames = int(round(DUR * FPS))
    if a.stills:
        want = {int(round(float(s) * FPS)) for s in a.stills.split(",")}
        n_frames = max(want) + 1
    enc = None
    tmp_v = out.with_name(out.stem + "_video_tmp.mp4")
    if want is None:
        enc = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                                "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "slow",
                                "-crf", "17", "-pix_fmt", "yuv420p", str(tmp_v)], stdin=subprocess.PIPE)
    last = None
    for n in range(n_frames):
        t = n / FPS
        if t < SRC_DUR:
            raw = src.stdout.read(W * H * 3)
            if len(raw) == W * H * 3:
                last = np.frombuffer(raw, np.uint8).reshape(H, W, 3).astype(np.float32) / 255
        f = last.copy()
        if anim[0] - 0.2 <= t < anim[1] + 0.2:
            mix = min(1.0, (t - anim[0] + 0.2) / 0.2, (anim[1] + 0.2 - t) / 0.2)
            f = f * (1 - mix) + expl.frame(t) * mix
        if prod_t[0] <= t < prod_t[1]:
            p = ease_io((t - prod_t[0]) / 0.25) * (1 - ease_io((t - prod_t[1] + 0.2) / 0.2))
            R.over(f, prod, (W - prod.shape[1]) / 2, 0.075 * H + 10 * (1 - p), p)
        badges.draw(f, t)
        caps.draw(f, t)
        if t >= end_t:
            q = ease_io((t - end_t) / 0.35)
            R.over(f, logo, (W - logo.shape[1]) / 2, 0.045 * H + 10 * (1 - q), q)
            q2 = back((t - end_t - 0.25) / 0.35, 1.0)
            if q2 > 0:
                lay, x, y = R.warp_premul(pill, 0.6 + 0.4 * q2, W / 2, CAP_Y + 105, (pill.shape[1] / 2, pill.shape[0] / 2))
                R.over(f, lay, x, y, min(1.0, q2))
        img = (np.clip(f, 0, 1) * 255 + 0.5).astype(np.uint8)
        if want is not None:
            if n in want:
                cv2.imwrite(str(out.parent / f"still_{t:05.2f}.png"), cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
            continue
        enc.stdin.write(img.tobytes())
    src.stdout.close()
    src.wait()
    if enc is None:
        return
    enc.stdin.close()
    enc.wait()
    ticks = [(b[0] + 0.05, 480.0) for b in badges.items]
    ticks += [(s, 400.0) for s in (t_engine, t_fuel, t_perf)]
    ticks += [(end_t + 0.25, 440.0)]
    sfx = out.with_name(out.stem + "_sfx.wav")
    sfx_track(sfx, ticks, [anim[0], anim[1]])
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(tmp_v), "-i", a.src, "-i", str(sfx),
                    "-filter_complex",
                    f"[1:a]aresample=48000,apad=whole_dur={DUR}[v];[v][2:a]amix=inputs=2:normalize=0:duration=longest,"
                    "loudnorm=I=-14:TP=-2.5:LRA=11,alimiter=limit=0.66:level=false,volume=1.3dB,alimiter=limit=0.70:level=false[a]",
                    "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                    "-t", f"{DUR:.2f}", "-movflags", "+faststart", str(out)], check=True)
    tmp_v.unlink(missing_ok=True)
    sfx.unlink(missing_ok=True)
    print("wrote", out)


if __name__ == "__main__":
    main()
