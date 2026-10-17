"""JLM Petrol Hybrid Treatment — Fast-Paced / Retention edit of the client's footage
(brand/jlm/EDIT_STYLES.md §3), with the accents the client picked: a jump-cut clean-up (§2),
a Vox paper board for the "why" (§6) and a Kinetic close (§5) before the black CTA screen.

    python3 edit_fast.py --src CLIENT_VIDEO --out ../out/jlm_hybrid_fast.mp4 [--stills 1,5,...]

Something new every 1–2.5 s on a calm camera (one slow push per shot), word-pop captions,
linked icon pairs at the bottom, the board, one smooth move into the can. All SFX are
soft (ticks ≈ −40 dBFS); a synthesized 112 BPM bed sits under the voice.
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

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(ROOT / "marketing/videos/jlm-care-edit/scripts"))
import edit_v3 as V  # noqa: E402  (badges, pairs, end card, icons, soft ticks)

E, R = V.E, V.R
T = E.T
W, H, FPS = 1080, 1920, 30
YEL, WHT, CHA, RED, GREY = V.YEL, V.WHT, V.CHA, V.RED, V.GREY
PAPER = np.array([241, 240, 236], np.float32) / 255
INK = (37, 39, 41)
ease = V.ease_io
back = V.back

# ------------------------------------------------------------ timeline ---
KEEP = [(0.10, 15.30), (15.60, 18.40)]   # jump cut: lead-in and the 0.4 s pause go
SPEECH_END = 18.0                        # out time where the voice ends
KIN0 = 18.0                              # kinetic close
END0 = 20.9                              # black CTA screen
DUR = END0 + 3.4


def s2o(ts):
    return ts - 0.10 if ts < KEEP[0][1] else ts - KEEP[1][0] + KEEP[0][1] - KEEP[0][0]


# speech segments between pauses (source time), from the Whisper transcript
SEGMENTS = [
    (0.19, 0.98, "نظام الوقود"),
    (1.11, 1.95, "بسيارات Hybrid"),
    (2.15, 3.13, "و Plug-in Hybrid"),
    (3.29, 4.28, "بمحركات البنزين"),
    (4.49, 5.76, "بحاجة دائماً لتنظيف مستمر"),
    (5.88, 7.55, "بسبب تراكم مخلفات"),
    (7.67, 8.05, "الاحتراق فيها"),
    (8.32, 9.61, "وبالذات إنّ المحرّك"),
    (9.74, 11.06, "ما بيشتغل بصورة دائمة ومستمرة"),
    (11.20, 12.92, "مع منتج Petrol Hybrid"),
    (13.06, 15.24, "Treatment من JLM اللي بيعمل على منع تراكم"),
    (15.65, 18.38, "الرواسب الكربونية وتشحيم نظام الاحتراق"),
]

# word-pop phrases (1–3 words). "!" red, "*" yellow, "#" hidden (the board carries it)
PHRASES = [
    "*نظام *الوقود", "بسيارات *Hybrid و *Plug-in *Hybrid", "بمحركات *البنزين",
    "بحاجة دائماً", "*لتنظيف مستمر",
    "#بسبب تراكم مخلفات", "#الاحتراق فيها", "#وبالذات إنّ المحرّك", "#ما بيشتغل", "#بصورة دائمة ومستمرة",
    "مع منتج", "*Petrol *Hybrid", "*Treatment", "من *JLM", "اللي بيعمل", "على *منع !تراكم",
    "!الرواسب !الكربونية", "*وتشحيم", "نظام الاحتراق",
]


def word_times(weight):
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
        out += [(s2o(s), s2o(e), wd) for s, e, wd in zip(starts, ends, words)]
    return out


# ------------------------------------------------------------- captions ---
CAP_Y = 0.43 * H          # on the shirt, clear of the can
CAP_LOW = 0.80 * H        # during the can close-up


class PopCaptions:
    """Words appear as they are spoken (1–3 per phrase); the phrase pops in,
    every new word gives it a small bump. Spoken = white, current = yellow."""

    def __init__(self, words):
        self.phrases, k = [], 0
        for ph in PHRASES:
            hidden = ph.startswith("#")
            items = []
            for tok in ph.lstrip("#").split():
                tone = tok[0] if tok[0] in "!*" else ""
                s, e, wd = words[k]
                assert wd == tok.lstrip("!*"), (wd, tok)
                items.append((wd, tone, s, e))
                k += 1
            self.phrases.append({"items": items, "hidden": hidden})
        assert k == len(words)
        for i, p in enumerate(self.phrases):
            p["t0"] = p["items"][0][2]
            nxt = self.phrases[i + 1]["items"][0][2] if i + 1 < len(self.phrases) else SPEECH_END
            p["t1"] = min(nxt, p["items"][-1][3] + 0.35)

    def at(self, word, nth=0):
        return [s for p in self.phrases for wd, _, s, _ in p["items"] if wd == word][nth]

    def keywords(self):
        return [(s, tone) for p in self.phrases if not p["hidden"] for _, tone, s, _ in p["items"] if tone]

    @staticmethod
    @lru_cache(maxsize=None)
    def layer(key):
        """Words placed right to left one by one (explicit gap); consecutive Latin
        words stay one left-to-right token so «Petrol Hybrid» keeps its order."""
        items, active = key
        toks = []
        for i, (wd, tone) in enumerate(items[: active + 1]):
            col = RED if tone == "!" else YEL if (tone == "*" or i == active) else WHT
            latin = not T._is_arabic(wd)
            if toks and latin and toks[-1][2] and toks[-1][1] == col:
                toks[-1] = (toks[-1][0] + " " + wd, col, True)
            else:
                toks.append((wd, col, latin))
        pad, gap = 26, 22
        lays = [latin_token(tx, col, pad) if lat else T.line([(tx, col)], 78, bold=True, shadow=True, pad=pad)
                for tx, col, lat in toks]
        th = max(l.shape[0] for l in lays)
        lays = [np.pad(l, (((th - l.shape[0]) // 2, th - l.shape[0] - (th - l.shape[0]) // 2), (0, 0), (0, 0)))
                for l in lays]
        tw = sum(l.shape[1] - 2 * pad for l in lays) + gap * (len(lays) - 1)
        txt = np.zeros((th, tw + 2 * pad, 4), np.float32)
        x = tw + pad
        for l in lays:
            x -= l.shape[1] - 2 * pad
            R.paste_into(txt, l, x - pad, 0)
            x -= gap
        box = V.soft_box(txt.shape[1] - 14, txt.shape[0] - 34, alpha=0.55)
        out = np.zeros((max(box.shape[0], txt.shape[0]), max(box.shape[1], txt.shape[1]), 4), np.float32)
        R.paste_into(out, box, (out.shape[1] - box.shape[1]) // 2, (out.shape[0] - box.shape[0]) // 2)
        R.paste_into(out, txt, (out.shape[1] - txt.shape[1]) // 2, (out.shape[0] - txt.shape[0]) // 2)
        return out

    def draw(self, f, t, y=CAP_Y):
        for p in self.phrases:
            if p["hidden"] or not (p["t0"] <= t < p["t1"]):
                continue
            active = max(i for i, it in enumerate(p["items"]) if it[2] <= t)
            lay = self.layer((tuple((wd, tone) for wd, tone, _, _ in p["items"]), active))
            sc = 0.72 + 0.28 * back((t - p["t0"]) / 0.18, 2.0)
            ta = p["items"][active][2]
            if active:
                sc *= 1 + 0.05 * math.sin(math.pi * R.clamp01((t - ta) / 0.14))
            sc *= min(1.0, 0.94 * W / lay.shape[1])
            l2, x, yy = R.warp_premul(lay, sc, W / 2, y, (lay.shape[1] / 2, lay.shape[0] / 2))
            a = min(1.0, (t - p["t0"]) / 0.06, (p["t1"] - t) / 0.06)
            R.over(f, l2, x, yy, a)


def latin_token(text, col, pad):
    """Latin words of a caption in Albert Sans (the JLM Latin face), with the caption shadow."""
    lay = R.latin_layer(text, 70, col, 800, 0.01)
    h = T.line([("ا", WHT)], 78, bold=True, shadow=False, pad=pad).shape[0]
    out = np.zeros((h, lay.shape[1] + 2 * pad, 4), np.float32)
    R.paste_into(out, lay, pad, (h - lay.shape[0]) // 2 + 11)
    sh = np.roll(cv2.GaussianBlur(out[..., 3], (0, 0), 9) * 0.55, 5, axis=0)
    res = np.zeros_like(out)
    res[..., 3] = sh
    res *= 1 - out[..., 3:4]
    res += out
    return res


# ---------------------------------------------------------------- icons ---
def _star(cx, cy, r):
    k = 0.28 * r
    return np.array([[cx, cy - r], [cx + k, cy - k], [cx + r, cy], [cx + k, cy + k], [cx, cy + r],
                     [cx - k, cy + k], [cx - r, cy], [cx - k, cy - k], [cx, cy - r]])


def _hybrid():
    car = V._car("v")[:6]
    bolt = np.array([[0.10, -0.98], [-0.14, -0.62], [0.06, -0.62], [-0.10, -0.40]])
    return car + [bolt]


def _pump():
    body = V._rrect(-0.58, -0.72, 0.18, 0.74, 0.08)
    win = V._rrect(-0.42, -0.54, 0.02, -0.16, 0.04)
    base = np.array([[-0.74, 0.74], [0.34, 0.74]])
    hose = np.array([[0.18, -0.34], [0.46, -0.34], [0.60, -0.14], [0.60, 0.42], [0.46, 0.54], [0.36, 0.42]])
    nozzle = np.array([[0.46, -0.34], [0.46, -0.60], [0.70, -0.72]])
    return [body, win, base, hose, nozzle]


def _sparkle():
    return [_star(-0.12, 0.10, 0.62), _star(0.56, -0.52, 0.26), _star(-0.62, -0.58, 0.18), _star(0.52, 0.62, 0.16)]


def _plugin():
    car = V._car("v")[:6]
    plug = V._rrect(-0.16, -0.86, 0.16, -0.62, 0.05)
    prongs = [np.array([[-0.08, -0.86], [-0.08, -1.0]]), np.array([[0.08, -0.86], [0.08, -1.0]])]
    cable = np.array([[0.0, -0.62], [0.0, -0.50], [0.10, -0.42], [0.10, -0.36]])
    return car + [plug] + prongs + [cable]


def _drop():
    pts = np.array(R.drop_points(0.0, 0.30, 0.46, 40))
    pts = np.concatenate([pts, pts[:1]])
    shine = V._arc(0.0, 0.30, 0.26, 0.26, 110, 170, 12)
    return [pts, shine]


V.ICONS.update({"hybrid": _hybrid, "pump": _pump, "sparkle": _sparkle, "plugin": _plugin, "drop": _drop})


_arabic_label = V.label_layer


@lru_cache(maxsize=None)
def _label(text, color):
    """Badge label pill; Latin labels (Hybrid, Plug-in Hybrid) set in Albert Sans."""
    if T._is_arabic(text):
        return _arabic_label(text, color)
    txt = R.latin_layer(text, 30, WHT, 800, 0.01)
    h = _arabic_label("ا", color).shape[0]
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
    R.paste_into(pill, txt, (w - txt.shape[1]) // 2, (h - txt.shape[0]) // 2)
    return pill


V.label_layer = _label


class LinkedPairs(V.Pairs):
    """The approved bottom pairs (VIDEO_STYLE §2): first badge on the right, second on the
    left, same size and pop. kind "then" draws the arrow (cause → result); kind "and" draws a
    plain dashed yellow line with a «+» in the middle (two things of the same kind)."""

    def __init__(self, items):
        super().__init__([it[:5] for it in items])
        self.kinds = [it[5] for it in items]

    def _plus_link(self, f, p, out):
        x0, x1 = self.XA - V.BADGE / 2 - 16, self.XB + V.BADGE / 2 + 16
        y = int(self.Y)
        xe = x0 + (x1 - x0) * p
        col = np.array(YEL, np.float32) / 255
        lay = np.zeros((70, W), np.float32)
        x = x0
        while x > xe:
            cv2.line(lay, (int(x), 35), (int(max(x - 22, xe)), 35), 1.0, 5, cv2.LINE_AA)
            x -= 34
        q = ease((p - 0.55) / 0.3)
        if q > 0:
            xm = int((x0 + x1) / 2)
            cv2.circle(lay, (xm, 35), int(26 * q), 1.0, -1, cv2.LINE_AA)
            cv2.line(lay, (xm - int(13 * q), 35), (xm + int(13 * q), 35), 0.0, 5, cv2.LINE_AA)
            cv2.line(lay, (xm, 35 - int(13 * q)), (xm, 35 + int(13 * q)), 0.0, 5, cv2.LINE_AA)
            disc = np.zeros_like(lay)
            cv2.circle(disc, (xm, 35), int(26 * q), 1.0, -1, cv2.LINE_AA)
        a = np.clip(lay + cv2.GaussianBlur(lay, (0, 0), 6) * 0.4, 0, 1)[..., None] * out
        reg = f[y - 35:y + 35]
        reg *= 1 - a
        reg += a * col
        if q > 0:
            # the «+» strokes cut out of the disc, in charcoal
            cut = (disc - lay).clip(0, 1)[..., None] * out
            reg *= 1 - cut
            reg += cut * np.array(CHA, np.float32) / 255

    def draw(self, f, t):
        for (ta, tb, t1, A, B), kind in zip(self.items, self.kinds):
            if not (ta <= t < t1 + 0.25):
                continue
            out = 1 - ease((t - t1) / 0.25)
            p = ease((t - tb + 0.25) / 0.40)
            if p > 0:
                if kind == "and":
                    self._plus_link(f, p, out)
                else:
                    self._arrow(f, p, out, A[1], B[1])
            self._badge(f, self.XA, t - ta, out, *A)
            if t >= tb:
                self._badge(f, self.XB, t - tb, out, *B)


# ---------------------------------------------------------------- camera ---
def ease5(x):
    """Quintic in-out: slow start, fast middle, soft landing (camera moves)."""
    x = R.clamp01(x)
    return 16 * x ** 5 if x < 0.5 else 1 - (-2 * x + 2) ** 5 / 2


def camera(kfs, t):
    """Keyframed camera: (t, scale, cx, cy, dur) in source pixels. Moves shorter than
    1 s use a quintic ease (designed moves); longer ones are slow drifts."""
    cur = prev = (1.0, W / 2, H / 2)
    for t0, s, cx, cy, d in kfs:
        if t < t0:
            break
        u = 1.0 if d <= 0 else (ease5((t - t0) / d) if d < 1.0 else ease((t - t0) / d))
        cur = tuple(a + (b - a) * u for a, b in zip(prev, (s, cx, cy)))
        prev = (s, cx, cy)
    return cur


def cam_frame(img, kfs, t):
    """Camera with motion blur: while the camera moves fast, average sub-frame positions."""
    c0 = camera(kfs, t)
    c1, c2 = camera(kfs, t - 0.4 / FPS), camera(kfs, t + 0.4 / FPS)
    speed = abs(c2[0] - c1[0]) * 900 + abs(c2[1] - c1[1]) + abs(c2[2] - c1[2])
    if speed < 6:
        return apply_cam(img, *c0)
    n = 7
    acc = np.zeros_like(img)
    for k in range(n):
        acc += apply_cam(img, *camera(kfs, t + (k / (n - 1) - 0.5) * 0.35 / FPS))
    return acc / n


def apply_cam(img, s, cx, cy):
    if abs(s - 1) < 1e-3 and abs(cx - W / 2) < 0.5 and abs(cy - H / 2) < 0.5:
        return img
    cx = min(max(cx, W / 2 / s), W - W / 2 / s)
    cy = min(max(cy, H / 2 / s), H - H / 2 / s)
    M = np.float32([[s, 0, W / 2 - s * cx], [0, s, H / 2 - s * cy]])
    return cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)


# ------------------------------------------------------------- vox board ---
def rot_layer(layer, ang, sc, cx, cy):
    """Rotate + scale a premultiplied layer about its centre; place the centre at (cx, cy)."""
    h, w = layer.shape[:2]
    d = int(math.hypot(w, h) * sc) + 8
    M = cv2.getRotationMatrix2D((w / 2, h / 2), ang, sc)
    M[0, 2] += d / 2 - w / 2
    M[1, 2] += d / 2 - h / 2
    out = cv2.warpAffine(layer, M, (d, d), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
    return out, cx - d / 2, cy - d / 2


def card_base(w, h, r=12):
    s = 3
    m = np.zeros((h * s, w * s), np.uint8)
    rr = r * s
    cv2.rectangle(m, (rr, 0), (w * s - rr, h * s), 255, -1)
    cv2.rectangle(m, (0, rr), (w * s, h * s - rr), 255, -1)
    for cx, cy in [(rr, rr), (w * s - rr, rr), (rr, h * s - rr), (w * s - rr, h * s - rr)]:
        cv2.circle(m, (cx, cy), rr, 255, -1, cv2.LINE_AA)
    a = cv2.resize(m, (w, h), interpolation=cv2.INTER_AREA).astype(np.float32) / 255
    pad = 30
    out = np.zeros((h + 2 * pad, w + 2 * pad, 4), np.float32)
    sh = np.zeros((h + 2 * pad, w + 2 * pad), np.float32)
    sh[pad + 8:pad + 8 + h, pad + 2:pad + 2 + w] = a
    sh = cv2.GaussianBlur(sh, (0, 0), 10) * 0.28
    out[..., 3] = sh
    card = np.zeros((h, w, 4), np.float32)
    card[..., :3] = np.array([0.995, 0.993, 0.985]) * a[..., None]
    card[..., 3] = a
    R.paste_into(out, card, pad, pad)
    # tape strip
    tape = np.zeros((34, 150, 4), np.float32)
    tape[..., :3] = np.array(V.GREY, np.float32) / 255 * 0.55
    tape[..., 3] = 0.55
    R.paste_into(out, tape, pad + w // 2 - 75, pad - 16)
    return out, pad


def poly(img, pts, col, th, closed=False):
    cv2.polylines(img, [np.round(np.asarray(pts) * 4).astype(np.int32)], closed, col, th, cv2.LINE_AA, shift=2)


class VoxBoard:
    """Paper board for «بسبب تراكم مخلفات الاحتراق … وبالذات إنّ المحرّك ما بيشتغل بصورة دايمة».
    Card 1 (right): an injector whose tip clogs with carbon while the spray weakens.
    Card 2 (left): the hybrid hand-over — petrol ⇄ electric — the engine keeps switching off.
    An arrow links card 2 → card 1 (cause → result); the presenter stays live in a photo card."""

    CW, CH = 470, 430

    def __init__(self, t0, t1, tc1, tc2):
        self.t0, self.t1, self.tc1, self.tc2 = t0, t1, tc1, tc2
        rng = np.random.default_rng(3)
        n = cv2.GaussianBlur(rng.standard_normal((H, W)).astype(np.float32), (0, 0), 1.2) * 0.012
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        vig = 1 - 0.10 * np.clip(np.hypot((xx - W / 2) / W, (yy - H / 2) / H) * 1.6, 0, 1) ** 2
        self.paper = (PAPER[None, None] + n[..., None]) * vig[..., None]
        self.card, self.pad = card_base(self.CW, self.CH)
        self.title = T.line([("السبب؟", INK)], 104, bold=True, shadow=False, pad=10)
        self.lab1 = T.line([("تراكم", RED), ("مخلفات الاحتراق", INK)], 46, bold=True, shadow=False, pad=8)
        self.lab2 = T.line([("المحرّك", INK), ("لا يعمل", RED), ("بشكل دائم", INK)], 46, bold=True, shadow=False, pad=8)
        self.petrol = T.line([("بنزين", INK)], 34, bold=True, shadow=False, pad=4)
        self.elec = T.line([("كهرباء", INK)], 34, bold=True, shadow=False, pad=4)
        self.blobs = [(rng.uniform(-30, 30), rng.uniform(-6, 26), rng.uniform(7, 15), rng.uniform(0, 0.8)) for _ in range(16)]
        self.spray = rng.uniform(-1, 1, (40, 2))
        self.photo, self.ppad = card_base(400, 452, r=6)

    # card 1: injector
    def injector(self, t):
        c = self.card.copy()
        p = self.pad
        cx = p + self.CW // 2
        g = np.zeros(c.shape[:2], np.float32)
        body = [(cx - 52, p + 50), (cx + 52, p + 50), (cx + 52, p + 190), (cx + 18, p + 250), (cx + 14, p + 285),
                (cx - 14, p + 285), (cx - 18, p + 250), (cx - 52, p + 190), (cx - 52, p + 50)]
        ink = np.array(INK, np.float32) / 255
        lt = t - self.tc1
        clog = R.clamp01(lt / 1.6)
        # spray cone of fuel droplets (weakens as the tip clogs)
        tip = (cx, p + 290)
        for k, (u, v) in enumerate(self.spray):
            ph = (t * 1.5 + k / len(self.spray)) % 1.0
            dd = 10 + 110 * ph * (1 - 0.65 * clog)
            ang = math.radians(90 + 22 * u * (1 - 0.6 * clog))
            x, y = tip[0] + dd * math.cos(ang), tip[1] + dd * math.sin(ang)
            cv2.circle(g, (int(x), int(y)), 4, 1.0 * (1 - ph) * (1 - 0.7 * clog), -1, cv2.LINE_AA)
        col = np.array(YEL, np.float32) / 255
        c[..., :3] = c[..., :3] * (1 - g[..., None]) + g[..., None] * col
        img = c[..., :3].copy()
        poly(img, body, ink.tolist(), 5, True)
        poly(img, [(cx - 52, p + 95), (cx + 52, p + 95)], ink.tolist(), 3)
        poly(img, [(cx - 20, p + 50), (cx - 20, p + 18), (cx + 20, p + 18), (cx + 20, p + 50)], ink.tolist(), 5)
        # carbon deposits growing at the tip
        for bx, by, r, d in self.blobs:
            q = ease((lt - d) / 0.7)
            if q > 0:
                cv2.circle(img, (int(cx + bx), int(tip[0] * 0 + p + 272 + by)), max(1, int(r * q)),
                           (0.10, 0.09, 0.085), -1, cv2.LINE_AA)
        c[..., :3] = img * c[..., 3:4]
        return c

    # card 2: petrol ⇄ electric, engine on/off
    def switcher(self, t):
        c = self.card.copy()
        p = self.pad
        img = c[..., :3].copy()
        lt = t - self.tc2
        on = (int(max(lt, 0) / 0.55) % 2 == 0)
        ink = (np.array(INK, np.float32) / 255).tolist()
        yel = (np.array(YEL, np.float32) / 255).tolist()
        grey = (np.array(GREY, np.float32) / 255).tolist()
        # engine
        sc = 120
        ex, ey = p + self.CW / 2, p + 285
        for st in V._engine()[:4]:
            poly(img, st * sc + [ex, ey], ink if on else grey, 6)
        # ON / OFF tag
        tag = "ON" if on else "OFF"
        lay = R.latin_layer(tag, 40, YEL if on else RED, 900, 0.04)
        # pump (right) ⇄ bolt (left)
        px, bx, iy = p + self.CW - 110, p + 110, p + 105
        for st in _pump():
            poly(img, st * 46 + [px, iy], yel if on else grey, 5)
        bolt = np.array([[0.14, -0.9], [-0.26, 0.05], [0.10, 0.05], [-0.14, 0.9]])
        poly(img, bolt * 52 + [bx, iy], grey if on else yel, 6)
        for k in (-1, 1):
            y = iy + 14 * k
            a0, a1 = (px - 70, bx + 70) if k < 0 else (bx + 70, px - 70)
            poly(img, [(a0, y), (a1, y)], ink, 3)
            poly(img, [(a1 + 14 * (1 if a1 < a0 else -1), y - 9), (a1, y), (a1 + 14 * (1 if a1 < a0 else -1), y + 9)], ink, 3)
        c[..., :3] = img * c[..., 3:4]
        R.paste_into(c, self.petrol, int(px - self.petrol.shape[1] / 2), int(iy + 52))
        R.paste_into(c, self.elec, int(bx - self.elec.shape[1] / 2), int(iy + 52))
        R.paste_into(c, lay, int(ex - lay.shape[1] / 2), int(ey + 92))
        return c

    def arrow(self, f, q):
        """Dashed curved arrow card 2 → card 1 (cause → result)."""
        pts = []
        a, b, ctrl = np.array([430, 975]), np.array([492, 640]), np.array([420, 650])
        for u in np.linspace(0, q, 40):
            pts.append((1 - u) ** 2 * a + 2 * (1 - u) * u * ctrl + u ** 2 * b)
        pts = np.array(pts)
        col = (np.array(YEL, np.float32) / 255 * 0.92).tolist()
        for i in range(0, len(pts) - 1, 3):
            poly(f, pts[i:i + 2], col, 7)
        if q > 0.95:
            d = pts[-1] - pts[-4]
            d /= np.linalg.norm(d) + 1e-6
            nrm = np.array([-d[1], d[0]])
            tip = pts[-1]
            poly(f, [tip - 22 * d + 14 * nrm, tip, tip - 22 * d - 14 * nrm], col, 7)

    def frame(self, t, live):
        f = self.paper.copy()
        # title + underline
        q = ease((t - self.t0 - 0.05) / 0.25)
        R.over(f, self.title, W / 2 - self.title.shape[1] / 2, 170 + 20 * (1 - q), q)
        u = ease((t - self.t0 - 0.25) / 0.35)
        if u > 0:
            # under the letters' dots, never through them
            x1, x0 = W / 2 + 170, W / 2 - 170
            yl = 170 + self.title.shape[0] + 10
            poly(f, [(x1, yl), (x1 + (x0 - x1) * u, yl)], (np.array(YEL, np.float32) / 255).tolist(), 12)
        # card 1 (right, upper)
        q = back((t - self.tc1 + 0.15) / 0.30)
        if q > 0:
            lay, x, y = rot_layer(self.injector(t), 2.5, 0.8 + 0.2 * q, 745, 630)
            R.over(f, lay, x, y, min(1.0, q * 3))
            R.over(f, self.lab1, 745 - self.lab1.shape[1] / 2, 862, ease((t - self.tc1 - 0.15) / 0.25))
        # card 2 (left, lower)
        q = back((t - self.tc2 + 0.1) / 0.30)
        if q > 0:
            lay, x, y = rot_layer(self.switcher(t), -2.5, 0.8 + 0.2 * q, 320, 1200)
            R.over(f, lay, x, y, min(1.0, q * 3))
            R.over(f, self.lab2, 320 - self.lab2.shape[1] / 2, 1432, ease((t - self.tc2 - 0.15) / 0.25))
            self.arrow(f, ease((t - self.tc2 - 0.35) / 0.45))
        # presenter, live, in a photo card (bottom right)
        ph = self.photo.copy()
        crop = live[640 - 362:640 + 362, 590 - 320:590 + 320]
        crop = cv2.resize(crop, (400 - 28, 452 - 28), interpolation=cv2.INTER_AREA)
        pp = self.ppad
        ph[pp + 14:pp + 14 + crop.shape[0], pp + 14:pp + 14 + crop.shape[1], :3] = crop
        q = ease((t - self.t0 - 0.2) / 0.3)
        lay, x, y = rot_layer(ph, 3.0, 0.78 + 0.08 * q, 840, 1480 + 40 * (1 - q))
        R.over(f, lay, x, y, q)
        # gentle camera: push in, refocus from card 1 to card 2
        k = R.clamp01((t - self.t0) / (self.t1 - self.t0))
        s = 1.0 + 0.05 * k
        cy = 880 + 140 * ease((t - self.tc2 + 0.2) / 0.5)
        return apply_cam(f, s, W / 2, cy)


# ------------------------------------------------------------ kinetic close ---
class Kinetic:
    """«يمنع» lands with a hit, «الرواسب» dissolves away, «ويشحّم» slides in, a sheen
    crosses it and a JLM drop falls — the motion carries the meaning (EDIT_STYLES §5)."""

    def __init__(self, t0):
        self.t0 = t0
        self.w1 = T.line([("يمنع", WHT)], 150, bold=True, shadow=True, pad=30)
        self.w2 = T.line([("الرواسب", RED)], 150, bold=True, shadow=True, pad=30)
        self.w3 = T.line([("ويشحّم", YEL)], 170, bold=True, shadow=True, pad=30)
        self.w4 = T.line([("نظام الاحتراق", WHT)], 78, bold=True, shadow=True, pad=20)
        rng = np.random.default_rng(9)
        self.noise = cv2.GaussianBlur(rng.random(self.w2.shape[:2]).astype(np.float32), (0, 0), 3)
        self.noise = (self.noise - self.noise.min()) / (np.ptp(self.noise) + 1e-6)
        self.drop, self.drop_anchor = R.drop_layer(34, YEL)
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        self.bg = (np.array([0.145, 0.153, 0.161]) * (1 - 0.30 * (np.hypot((xx - W / 2) / W, (yy - H / 2) / H) * 1.4) ** 2)[..., None]).astype(np.float32)

    def frame(self, t, under):
        t0 = self.t0
        # yellow wipe from the right: footage → charcoal
        p = ease((t - t0) / 0.45)
        edge = W * (1 - p)
        f = under.copy()
        xs = int(max(edge, 0))
        f[:, xs:] = self.bg[:, xs:]
        band0, band1 = int(max(edge - 70, 0)), int(min(edge + 50, W))
        if p < 1 and band1 > band0:
            f[:, band0:band1] = np.array(YEL, np.float32) / 255
        # يمنع — impact
        lt = t - t0 - 0.18
        if lt > 0:
            sc = 1 + 0.6 * (1 - ease(lt / 0.18))
            sh = 6 * math.exp(-lt / 0.09) * math.sin(lt * 70)
            lay, x, y = R.warp_premul(self.w1, sc, W / 2 + sh, 0.34 * H, (self.w1.shape[1] / 2, self.w1.shape[0] / 2))
            R.over(f, lay, x, y, min(1.0, lt / 0.06))
        # الرواسب — appears, then dissolves and drifts down
        lt = t - t0 - 0.45
        if lt > 0:
            d = R.clamp01((lt - 0.55) / 0.65)
            m = np.clip((self.noise - d * 1.15) / 0.12 + 1, 0, 1) if d > 0 else 1.0
            lay = self.w2 * (m[..., None] if d > 0 else 1.0)
            R.over(f, lay, W / 2 - lay.shape[1] / 2, 0.45 * H - lay.shape[0] / 2 + 60 * d * d, min(1.0, lt / 0.1))
        # ويشحّم — slides in from the right, sheen, falling drop
        lt = t - t0 - 1.45
        if lt > 0:
            u = ease(lt / 0.22)
            lay = self.w3.copy()
            sp = (lt - 0.35) / 0.45
            if 0 < sp < 1:
                hh, ww = lay.shape[:2]
                yy, xx = np.mgrid[0:hh, 0:ww].astype(np.float32)
                c = (1.2 - 1.6 * sp) * (ww + hh)
                band = np.exp(-(((xx + yy) - c) / 38.0) ** 2) * 0.85
                lay[..., :3] += band[..., None] * lay[..., 3:4] * (1 - lay[..., :3])
            R.over(f, lay, W / 2 - lay.shape[1] / 2 + 260 * (1 - u), 0.58 * H - lay.shape[0] / 2, u)
            dq = (lt - 0.5) / 0.6
            if 0 < dq < 1.2:
                y = 0.58 * H + 60 + 120 * min(dq, 1) ** 2
                R.over(f, self.drop, W / 2 - self.drop_anchor[0], y - self.drop_anchor[1], min(1.0, dq * 4) * (1 - R.clamp01((dq - 0.9) / 0.3)))
        lt = t - t0 - 2.0
        if lt > 0:
            q = ease(lt / 0.25)
            R.over(f, self.w4, W / 2 - self.w4.shape[1] / 2, 0.74 * H - self.w4.shape[0] / 2 + 16 * (1 - q), q)
        return f


class NameLine:
    """The spoken line slot of the end card: the product name in Albert Sans."""

    def __init__(self, t0):
        self.t0 = t0
        self.name = R.latin_layer("Petrol Hybrid Treatment", 66, YEL, 800, 0.01)

    def draw(self, f, t, y):
        q = ease((t - self.t0 - 0.2) / 0.35)
        R.over(f, self.name, W / 2 - self.name.shape[1] / 2, y - self.name.shape[0] / 2 + 12 * (1 - q), q)


def product_chip():
    txt = R.latin_layer("Petrol Hybrid Treatment", 46, YEL, 800, 0.01)
    by = T.line([("من", WHT), ("JLM", WHT)], 40, bold=True, shadow=False, pad=0)
    h = max(txt.shape[0], by.shape[0]) + 34
    w = txt.shape[1] + by.shape[1] + 80
    s = 3
    img = np.zeros((h * s, w * s, 4), np.uint8)
    cv2.rectangle(img, (0, 0), (w * s - 1, h * s - 1), YEL + (255,), -1)
    cv2.rectangle(img, (3 * s, 3 * s), (w * s - 1 - 3 * s, h * s - 1 - 3 * s), (14, 15, 16, 235), -1)
    chip = R.to_premul(cv2.resize(img, (w, h), interpolation=cv2.INTER_AREA))
    R.paste_into(chip, txt, 28, (h - txt.shape[0]) // 2)
    R.paste_into(chip, by, w - 28 - by.shape[1], (h - by.shape[0]) // 2 + 2)
    return chip


# ----------------------------------------------------------------- audio ---
SR = 48000
BPM = 112.0


def music(dur):
    """Light 112 BPM bed in A minor (Am–F–C–G): soft kick, hats, plucked bass, pad.
    Under the voice it stays low; it lifts for the kinetic close and resolves on the end card."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    beat = 60 / BPM
    out = np.zeros(n, np.float32)
    roots = [110.0, 87.31, 130.81, 98.0]                       # A2 F2 C3 G2
    chords = [(220.0, 261.63, 329.63), (174.61, 220.0, 261.63), (261.63, 329.63, 392.0), (196.0, 246.94, 293.66)]

    def add(sig, at, gain):
        i = int(at * SR)
        if i >= n:
            return
        m = min(len(sig), n - i)
        out[i:i + m] += sig[:m] * gain

    kick_t = np.arange(int(0.22 * SR)) / SR
    kick = np.sin(2 * np.pi * (48 * kick_t + 50 * (1 - np.exp(-kick_t * 30)) / 30)) * np.exp(-kick_t / 0.09)
    hat_t = np.arange(int(0.04 * SR)) / SR
    rng = np.random.default_rng(1)
    hat = np.diff(rng.standard_normal(len(hat_t) + 1)).astype(np.float32) * np.exp(-hat_t / 0.012)
    nb = int(dur / beat) + 1
    for b in range(nb):
        at = b * beat
        lift = at >= KIN0 - 0.05
        end = at >= END0 + 2.2
        if end:
            continue
        if b % 2 == 0 or lift:
            add(kick, at, 0.32 if lift else 0.20)
        add(hat, at + beat / 2, 0.05 if lift else 0.03)
        bar = int(b // 4) % 4
        for k in range(2):                                     # eighth-note bass pluck
            tt = np.arange(int(beat / 2 * SR)) / SR
            f0 = roots[bar] * (2 if (k == 1 and b % 2) else 1)
            pl = sum(np.sin(2 * np.pi * f0 * h * tt) / h for h in (1, 2, 3)) * np.exp(-tt / 0.12)
            add(pl, at + k * beat / 2, 0.06 if lift else 0.045)
    # pad
    bar_len = 4 * beat
    for i in range(int(dur / bar_len) + 1):
        at = i * bar_len
        tt = np.arange(int(bar_len * SR)) / SR
        env = np.minimum(1, tt / 0.4) * np.minimum(1, (bar_len - tt) / 0.4)
        ch = chords[i % 4] if at < END0 else chords[0]
        sig = sum(np.sin(2 * np.pi * f * tt) + 0.2 * np.sin(2 * np.pi * f * 2.003 * tt) for f in ch) / 3
        add(sig * env, at, 0.05)
    # level: low under the voice, up for the close, fade out at the end
    lvl = np.where(t < KIN0 - 0.1, 0.22, 1.0) * np.minimum(1, t / 0.4) * np.clip((dur - t) / 1.2, 0, 1)
    lvl = np.convolve(lvl, np.ones(2400) / 2400, mode="same")
    return out * lvl


def soft_whoosh(dur=0.32, amp=0.022):
    rng = np.random.default_rng(7)
    n = int(dur * SR)
    w = rng.standard_normal(n)
    for k in (60, 30):
        w = np.convolve(w, np.ones(k) / k, mode="same")
    env = np.sin(np.linspace(0, np.pi, n)) ** 2
    return (w / (np.abs(w).max() + 1e-9) * env * amp).astype(np.float32)


def soft_thump(amp=0.05):
    tt = np.arange(int(0.3 * SR)) / SR
    return (np.sin(2 * np.pi * (60 * tt + 40 * (1 - np.exp(-tt * 25)) / 25)) * np.exp(-tt / 0.08) * amp).astype(np.float32)


def shimmer(amp=0.004):
    tt = np.arange(int(0.5 * SR)) / SR
    f = 2200 + 1600 * tt / 0.5
    return (np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * tt / 0.5) ** 2 * amp).astype(np.float32)


def write_fx(path, events):
    n = int(DUR * SR)
    buf = music(DUR)
    for at, sig in events:
        i = int(at * SR)
        if i < 0:
            sig, i = sig[-i:], 0
        m = min(len(sig), n - i)
        if m > 0:
            buf[i:i + m] += sig[:m]
    pcm = (np.clip(np.stack([buf, buf], 1), -1, 1) * 32767).astype(np.int16)
    with wave.open(str(path), "wb") as wv:
        wv.setnchannels(2)
        wv.setsampwidth(2)
        wv.setframerate(SR)
        wv.writeframes(pcm.tobytes())


# ------------------------------------------------------------------ main ---
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--stills")
    a = ap.parse_args()
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)

    caps = PopCaptions(word_times(V.voiced_weight(a.src)))
    at = caps.at
    b0, b1 = s2o(5.82), s2o(11.13)                      # board over the "why"
    board = VoxBoard(b0, b1, at("تراكم", 0), at("وبالذات"))
    kin = Kinetic(KIN0)
    endcard = V.EndCard(END0)
    endcard.cta = T.line([("اطلبه الآن", YEL), ("من خلال", WHT)], 74, bold=True, shadow=False, pad=10)  # المنتج: masculine
    name = NameLine(END0)
    chip = product_chip()
    chip_t = (b1, at("اللي") - 0.05)
    # icons: always a pair at the bottom — first on the right, second on the left
    pairs = LinkedPairs([
        (at("بسيارات"), at("و"), at("بمحركات") - 0.12,
         ("hybrid", YEL, "Hybrid"), ("plugin", YEL, "Plug-in Hybrid"), "and"),
        (at("بمحركات"), at("لتنظيف"), b0 - 0.12,
         ("pump", YEL, "محرّك بنزين"), ("sparkle", YEL, "تنظيف مستمر"), "then"),
        (at("منع"), at("وتشحيم"), SPEECH_END - 0.12,
         ("shield", YEL, "يمنع الرواسب"), ("drop", YEL, "يشحّم"), "and"),
    ])
    cuts = [s2o(4.33), s2o(8.2), b1, s2o(KEEP[1][0])]
    t_tr = at("Treatment")
    t_hy, t_pl, t_back = at("بسيارات") - 0.12, at("و") - 0.18, at("بمحركات") - 0.12
    # camera: one slow push per shot, plus one motivated move into the can when the
    # product is named (and a smooth pull back out) — no punch-ins
    kfs = [
        (0.00, 1.04, 580, 820, 0), (0.01, 1.07, 580, 800, t_hy - 0.06),
        # «بسيارات الهايبريد»: push in on the presenter
        (t_hy, 1.20, 585, 740, 0.7),
        # «والبلَغ إن هايبريد»: glide to the charger and its plug, drift, glide back
        (t_pl, 1.45, 372, 975, 0.8), (t_pl + 0.81, 1.50, 372, 975, t_back - t_pl - 0.86),
        (t_back, 1.08, 580, 800, 0.75), (t_back + 0.76, 1.11, 580, 785, cuts[0] - t_back - 0.81),
        (cuts[0], 1.03, 560, 860, 0), (cuts[0] + 0.01, 1.08, 560, 820, b0 - cuts[0] - 0.05),
        (b1, 1.85, 450, 1000, 0), (b1 + 0.01, 1.98, 450, 1000, t_tr - 0.4 - b1 - 0.05),
        (t_tr - 0.4, 1.06, 520, 840, 0.7),
        (t_tr + 0.31, 1.12, 520, 790, cuts[3] - t_tr - 0.4),
        (cuts[3], 1.06, 520, 840, 0), (cuts[3] + 0.01, 1.12, 520, 790, SPEECH_END - cuts[3] - 0.05),
    ]
    board_out = 0.4
    for p in caps.phrases:
        print(f"  {p['t0']:5.2f}–{p['t1']:5.2f} {'#' if p['hidden'] else ' '} " + " ".join(w for w, *_ in p["items"]))
    print(f"board {b0:.2f}–{b1:.2f}  card1 {board.tc1:.2f} card2 {board.tc2:.2f}")

    (k0, k1), (k2, k3) = KEEP
    vf = (f"[0:v]trim=start={k0}:end={k1},setpts=PTS-STARTPTS[a];[0:v]trim=start={k2}:end={k3},setpts=PTS-STARTPTS[b];"
          f"[a][b]concat=n=2:v=1:a=0,fps={FPS},scale={W}:{H}:flags=lanczos,eq=contrast=1.04:saturation=1.06[v]")
    src = subprocess.Popen(["ffmpeg", "-v", "error", "-i", a.src, "-filter_complex", vf, "-map", "[v]",
                            "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    want, n_frames = None, int(round(DUR * FPS))
    if a.stills:
        want = {int(round(float(s) * FPS)) for s in a.stills.split(",")}
        n_frames = max(want) + 1
    tmp_v = out.with_name(out.stem + "_video_tmp.mp4")
    enc = None
    if want is None:
        enc = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                                "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "slow",
                                "-crf", "17", "-pix_fmt", "yuv420p", str(tmp_v)], stdin=subprocess.PIPE)
    live = last = held = board_live = None
    for n in range(n_frames):
        t = n / FPS
        if t < SPEECH_END:
            raw = src.stdout.read(W * H * 3)
            if len(raw) == W * H * 3:
                live = np.frombuffer(raw, np.uint8).reshape(H, W, 3).astype(np.float32) / 255
        if t < KIN0:
            ff = cam_frame(live, kfs, t)
            if t < cuts[3]:
                held = ff
            elif t < cuts[3] + 0.14:
                # the jump cut is a short dissolve, not a jump
                u = ease((t - cuts[3]) / 0.14)
                ff = held * (1 - u) + ff * u
            if b0 <= t < b1 + board_out:
                # board slides up over the footage, then up and away onto the can close-up
                bf = board.frame(min(t, b1 - 1 / FPS), live if t < b1 else board_live)
                if t < b1:
                    board_live = live
                pin = ease((t - b0) / 0.4)
                pout = ease((t - b1) / board_out)
                f = ff.copy()
                y_in = int(round(H * (1 - pin)))
                if pout <= 0:
                    f[y_in:] = bf[:H - y_in]
                else:
                    k = int(round(H * pout))
                    f[:H - k] = bf[k:]
            else:
                f = ff
                pairs.draw(f, t)
                if chip_t[0] <= t < chip_t[1]:
                    q = back((t - chip_t[0]) / 0.3) * (1 - ease((t - chip_t[1] + 0.2) / 0.2))
                    lay, x, y = R.warp_premul(chip, 0.7 + 0.3 * q, W / 2, 0.095 * H, (chip.shape[1] / 2, chip.shape[0] / 2))
                    R.over(f, lay, x, y, min(1.0, q * 2))
                caps.draw(f, t, CAP_LOW if b1 <= t < t_tr - 0.1 else CAP_Y)
            last = f
        elif t < END0 + 0.1:
            f = kin.frame(t, last)
            endcard.draw(f, t, name)
        else:
            f = np.zeros((H, W, 3), np.float32)
            endcard.draw(f, t, name)
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

    # sound: soft ticks on badges and key words, whooshes on reframes / board / wipe
    ev = []
    for ta, tb, *_ in pairs.items:
        ev += [(ta + 0.05, V.soft_tick(SR, 420.0)), (tb + 0.05, V.soft_tick(SR, 520.0))]
    lastk = -1
    for s, tone in caps.keywords():
        if s - lastk > 0.6:
            ev.append((s, V.soft_tick(SR, 620.0 if tone == "*" else 380.0, 0.007)))
            lastk = s
    for tk in [t_hy + 0.15, t_pl + 0.2, t_back + 0.2, b0 + 0.05, b1 + 0.1, t_tr - 0.25, KIN0 + 0.1]:
        ev.append((tk - 0.16, soft_whoosh(0.42, 0.02)))
    ev += [(board.tc1, V.soft_tick(SR, 440.0)), (board.tc2, V.soft_tick(SR, 440.0))]
    ev += [(KIN0 + 0.18, soft_thump()), (KIN0 + 1.45, soft_whoosh(0.25, 0.018)), (KIN0 + 1.8, shimmer())]
    ev += [(END0 + 0.95, V.soft_tick(SR, 440.0)), (END0 + 1.35, V.soft_tick(SR, 440.0))]
    fx = out.with_name(out.stem + "_fx.wav")
    write_fx(fx, ev)
    af = (f"[0:a]atrim={k0}:{k1},asetpts=PTS-STARTPTS,afade=t=out:st={k1 - k0 - 0.015}:d=0.015[a1];"
          f"[0:a]atrim={k2}:{k3},asetpts=PTS-STARTPTS,afade=t=in:d=0.015,afade=t=out:st={k3 - k2 - 0.06}:d=0.06[a2];"
          f"[a1][a2]concat=n=2:v=0:a=1,aresample={SR},apad=whole_dur={DUR}[vo];"
          f"[vo][2:a]amix=inputs=2:normalize=0:duration=longest,"
          "volume=-3dB,alimiter=limit=0.63:attack=2:release=60:level=false,loudnorm=I=-14:TP=-2.5:LRA=11[aout]")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", a.src, "-i", str(tmp_v), "-i", str(fx),
                    "-filter_complex", af, "-map", "1:v", "-map", "[aout]", "-c:v", "copy", "-c:a", "aac",
                    "-b:a", "192k", "-ar", str(SR), "-t", f"{DUR:.2f}", "-movflags", "+faststart", str(out)], check=True)
    tmp_v.unlink(missing_ok=True)
    fx.unlink(missing_ok=True)
    print("wrote", out)


if __name__ == "__main__":
    main()
