"""JLM GDI Injector Cleaner — Vox-style edit with a light Fast-Paced zoom accent.

    python3 scripts/cut.py src/raw.mp4 build/cut.mov          # jump-cut clean-up first
    python3 scripts/vox.py --src build/cut.mov --out out/jlm_gdi_injector_cleaner.mp4 [--stills 1,5,...]

Vox board (brand/jlm/EDIT_STYLES.md §6) in JLM colours: off-white paper, charcoal ink, yellow
highlighter, red only for the problem. The footage sits in a slightly tilted photo card; a paper
title strip asks the question, then numbers the answer (١ السبب · ٢ الحل · ٣ النتيجة); taped paper
stickers explain it: a direct-injection diagram whose injector tip collects red deposits, a red
marker circle on the real injector's dirty tip, the label line "Cleans the Inside of GDI Injector"
highlighted, and two result cards. Karaoke captions on a paper strip. Punch-ins (1.00 ↔ 1.10) hide
the jump cuts. The clip's own white CTA card is replaced by the usual JLM CTA over the blurred video.
"""
import argparse
import math
import subprocess
import sys
from functools import lru_cache
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(ROOT / "marketing/videos/jlm-care-edit/scripts"))
import edit_v3 as V  # noqa: E402

E, R = V.E, V.R
W, H, FPS = 1080, 1920, 30
YEL, RED, CHA, WHT = (250, 184, 23), (214, 48, 39), (37, 39, 41), (241, 240, 236)
GREY, SIL = (150, 152, 154), (192, 196, 199)
PAPER = np.array([241, 240, 236], np.float32) / 255
ease, back = V.ease_io, V.back

# cut timeline (from scripts/cut.py)
SEGMENTS = [
    (0.00, 3.45, "لماذا يلزم نستخدم مضاف البخاخات من JLM في المحركات الجديدة"),
    (3.45, 6.77, "بسبب مكان وجود البخاخ في المحركات الجديدة فوق غرفة الاحتراق"),
    (6.77, 9.08, "هذا الشي بيؤدي إلى تراكمات وترسّبات"),
    (9.08, 10.70, "تظهر على البخاخ مع الوقت"),
    (10.70, 13.49, "وبالتالي استخدام منظف JLM بشكل دوري"),
    (13.49, 15.31, "بساعد على إزالة هذه التراكمات"),
    (15.31, 16.88, "وبيعطيك كفاءة أعلى للمحرك"),
    (16.88, 18.41, "وبالتالي استهلاك أقل للوقود"),
]
CTA_T = 18.41                 # the spoken CTA runs under the end card
FREEZE_T = 20.0               # last product frame before the clip's own white card
DUR = 24.6
# per segment: zoom target and anchor (fractions of the source frame) — 1.00 ↔ 1.10 alternate over jump cuts
ZOOM = [(1.00, .62, .38), (1.10, .55, .42), (1.00, .5, .5), (1.00, .72, .535), (1.10, .5, .5),
        (1.00, .45, .45), (1.10, .6, .38), (1.00, .6, .4), (1.00, .5, .5)]
# "#" hidden (the title carries it), "!" problem (red), "*" key idea (yellow highlighter)
PHRASES = [
    "#لماذا يلزم نستخدم", "#مضاف البخاخات من JLM", "#في المحركات الجديدة",
    "بسبب مكان وجود *البخاخ", "في المحركات الجديدة", "فوق *غرفة *الاحتراق",
    "هذا الشي بيؤدي إلى", "!تراكمات !وترسّبات",
    "تظهر على *البخاخ مع الوقت",
    "وبالتالي استخدام", "منظف *JLM بشكل دوري",
    "بساعد على *إزالة", "هذه !التراكمات",
    "وبيعطيك *كفاءة *أعلى للمحرك",
    "وبالتالي *استهلاك *أقل للوقود",
]

# card geometry: the footage inside a white-bordered photo, tilted a little
SRC_W, SRC_H = 720, 1280
IN_W, IN_H, BORDER = 832, 1479, 14
CARD_W, CARD_H = IN_W + 2 * BORDER, IN_H + 2 * BORDER
CARD_C, CARD_ROT = (540, 170 + CARD_H / 2), -1.2
TIP = (520, 685)              # the injector's dirty tip in the source frame (shot 4)


def is_ar(w):
    return any("؀" <= ch <= "ۿ" for ch in w)


def word_times(weight):
    out = []
    for t0, t1, text in SEGMENTS:
        words = text.split()
        w = weight[int(t0 * 100):int(t1 * 100)] + 1e-3
        c = np.concatenate([[0], np.cumsum(w)]) / w.sum()
        lens = [len(x) + 1 for x in words]
        acc = np.concatenate([[0], np.cumsum(lens)]) / sum(lens)
        starts = [t0 + np.searchsorted(c, a) / 100 for a in acc[:-1]]
        out += list(zip(starts, starts[1:] + [t1], words))
    return out


# ------------------------------------------------------------------ type ---
@lru_cache(maxsize=None)
def ink_line(items, size, pad=18, bold=True):
    """RTL line on paper: items = ((word, rgb, marker), …). Marker = yellow highlighter on the lower 60 %."""
    fa = E.T.font(size, bold)
    fl = R.albert(int(size * 0.92), 800)
    space = fa.getlength(" ", direction="rtl") * 1.05
    advs = [(fa.getlength(w, direction="rtl") if is_ar(w) else fl.getlength(w)) for w, _, _ in items]
    asc, desc = fa.getmetrics()
    dy_l = asc - fl.getmetrics()[0]
    lw = int(sum(advs) + space * (len(items) - 1)) + 2 * pad
    lh = asc + desc + 2 * pad
    img = Image.new("RGBA", (lw, lh), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    # x positions, RTL with Latin runs kept left-to-right
    xs, x, i = [0.0] * len(items), lw - pad, 0
    while i < len(items):
        j = i + 1
        if not is_ar(items[i][0]):
            while j < len(items) and not is_ar(items[j][0]):
                j += 1
        run_w = sum(advs[i:j]) + space * (j - i - 1)
        xl = x - run_w
        if is_ar(items[i][0]):
            xs[i] = xl
        else:
            for k in range(i, j):
                xs[k] = xl
                xl += advs[k] + space
        x -= run_w + space
        i = j
    top = pad + size * 0.52
    for (w, _, mk), x0, adv in zip(items, xs, advs):
        if mk:
            d.rounded_rectangle((x0 - 6, top, x0 + adv + 6, pad + size * 1.12), radius=6, fill=YEL + (230,))
    for (w, col, _), x0 in zip(items, xs):
        if is_ar(w):
            d.text((x0, pad), w, font=fa, fill=tuple(col) + (255,), direction="rtl")
        else:
            d.text((x0, pad + dy_l), w, font=fl, fill=tuple(col) + (255,))
    return R.to_premul(np.array(img))


def paper_rect(w, h, tone=1.0, radius=10):
    """Paper card (premultiplied RGBA) with a faint grain."""
    rng = np.random.default_rng(w * 7 + h)
    m = np.zeros((h, w), np.float32)
    cv2.rectangle(m, (radius, 0), (w - radius, h), 1, -1)
    cv2.rectangle(m, (0, radius), (w, h - radius), 1, -1)
    for cx, cy in [(radius, radius), (w - radius, radius), (radius, h - radius), (w - radius, h - radius)]:
        cv2.circle(m, (cx, cy), radius, 1, -1, cv2.LINE_AA)
    g = cv2.GaussianBlur(rng.normal(0, 1, (h, w)).astype(np.float32), (0, 0), 1.2) * 0.012
    col = np.clip(np.array([0.985, 0.98, 0.965], np.float32) * tone + g[..., None], 0, 1)
    return np.dstack([col * m[..., None], m]).astype(np.float32)


def tape(w=120, h=34):
    t = np.zeros((h, w, 4), np.float32)
    t[..., :3] = np.array(SIL, np.float32) / 255 * 0.72
    t[..., 3] = 0.72
    t[:, :3, 3] *= 0.4
    t[:, -3:, 3] *= 0.4
    t[..., :3] *= t[..., 3:4] / 0.72
    return t


def place_rotated(f, layer, cx, cy, deg, alpha=1.0, scale=1.0, shadow=0.28):
    """Composite a premultiplied layer rotated about its centre at (cx, cy), with a soft drop shadow."""
    h, w = layer.shape[:2]
    s = int(math.hypot(w, h) * scale) + 40
    M = cv2.getRotationMatrix2D((w / 2, h / 2), deg, scale)
    M[0, 2] += s / 2 - w / 2
    M[1, 2] += s / 2 - h / 2
    lay = cv2.warpAffine(layer, M, (s, s), flags=cv2.INTER_LINEAR)
    if shadow:
        sh = np.zeros_like(lay)
        sh[..., 3] = cv2.GaussianBlur(lay[..., 3], (0, 0), 10) * shadow
        R.over(f, sh, cx - s / 2 + 4, cy - s / 2 + 10, alpha)
    R.over(f, lay, cx - s / 2, cy - s / 2, alpha)


def clean_logo(path, width):
    """A JLM logo file without the faint alpha box some of them carry: keep only the mark's alpha."""
    im = np.array(Image.open(path).convert("RGBA"))
    a = im[..., 3]
    keep = cv2.dilate((a > 128).astype(np.uint8), np.ones((5, 5), np.uint8))
    im[..., 3] = a * keep
    im[:4], im[-4:], im[:, :4], im[:, -4:] = 0, 0, 0, 0
    im = Image.fromarray(im).resize((width, int(im.shape[0] * width / im.shape[1])), Image.LANCZOS)
    return R.to_premul(np.array(im))


def put(dst, src, x, y, alpha=1.0):
    """Premultiplied RGBA over premultiplied RGBA, clipped to dst."""
    h, w = src.shape[:2]
    x, y = int(round(x)), int(round(y))
    x0, y0, x1, y1 = max(x, 0), max(y, 0), min(x + w, dst.shape[1]), min(y + h, dst.shape[0])
    if x0 >= x1 or y0 >= y1 or alpha <= 0:
        return
    s = src[y0 - y:y1 - y, x0 - x:x1 - x] * alpha
    reg = dst[y0:y1, x0:x1]
    reg *= 1 - s[..., 3:4]
    reg += s


# ------------------------------------------------------------- captions ---
class Captions:
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
        assert k == len(words), (k, len(words))
        for i, p in enumerate(self.phrases):
            p["t0"] = p["items"][0][2]
            nxt = self.phrases[i + 1]["items"][0][2] if i + 1 < len(self.phrases) else CTA_T
            p["t1"] = min(nxt, p["items"][-1][3] + 0.45)
        self.all = [(wd, s, e) for p in self.phrases for wd, _, s, e in p["items"]]
        self.strip = paper_rect(980, 118)

    def at(self, word, nth=0):
        return [s for wd, s, _ in self.all if wd == word][nth]

    def draw(self, f, t):
        live = [p for p in self.phrases if not p["hidden"] and p["t0"] <= t < p["t1"]]
        vis = max((p for p in self.phrases if not p["hidden"]), key=lambda p: p["t0"])
        first = min((p["t0"] for p in self.phrases if not p["hidden"]))
        a = ease((t - first + 0.1) / 0.3) * (1 - ease((t - CTA_T + 0.3) / 0.3))
        if a <= 0:
            return
        place_rotated(f, self.strip, 540, 1600, 0.6, a, shadow=0.22)
        for p in live:
            active = max(i for i, it in enumerate(p["items"]) if it[2] <= t)
            items = []
            for i, (wd, tone, _, _) in enumerate(p["items"]):
                col = GREY if i > active else RED if tone == "!" else CHA
                mk = i <= active and (tone == "*" or i == active) and tone != "!"
                items.append((wd, col, mk))
            lay = ink_line(tuple(items), 54)
            R.over(f, lay, (W - lay.shape[1]) / 2, 1600 - lay.shape[0] / 2 + 4, a * min(1.0, (t - p["t0"]) / 0.08))
        del vis


# ---------------------------------------------------------------- title ---
class Title:
    """Paper strip at the top: the question first, then the numbered answer headers."""

    def __init__(self, caps):
        at = caps.at
        q1 = ink_line((("لماذا", CHA, False), ("يلزم", CHA, False), ("مضاف", CHA, True), ("البخاخات", CHA, True)), 66)
        q2 = ink_line((("في", CHA, False), ("المحركات", CHA, False), ("الجديدة؟", CHA, False)), 50, bold=False)
        self.q = (q1, q2)
        self.q_marks = (at("مضاف"), at("البخاخات"))
        self.heads = [
            (at("بسبب"), self.head("١", "السبب:", "مكان", "البخاخ")),
            (at("وبالتالي", 0), self.head("٢", "الحل:", "منظف", "JLM")),
            (at("وبيعطيك"), self.head("٣", "النتيجة", "", "")),
        ]

    @staticmethod
    def head(num, a, b, c):
        words = [(a, CHA, False)] + [(w, CHA, True) for w in (b, c) if w]
        txt = ink_line(tuple(words), 60)
        disc = np.zeros((84, 84, 4), np.uint8)
        cv2.circle(disc, (42, 42), 38, YEL + (255,), -1, cv2.LINE_AA)
        disc = R.to_premul(disc)
        n = ink_line(((num, CHA, False),), 52, pad=0)
        ys, xs = np.nonzero(n[..., 3] > 0.02)
        n = n[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
        R.paste_into(disc, n, (84 - n.shape[1]) // 2, (84 - n.shape[0]) // 2 + 2)
        out = np.zeros((max(txt.shape[0], 84), txt.shape[1] + 100, 4), np.float32)
        R.paste_into(out, txt, 0, (out.shape[0] - txt.shape[0]) // 2)
        R.paste_into(out, disc, txt.shape[1] + 8, (out.shape[0] - 84) // 2)
        return out

    def draw(self, f, t):
        if t >= CTA_T:
            return
        # which content, and a quick flip between them
        events = [(0.0, "q")] + [(t0, k) for k, (t0, _) in enumerate(self.heads)]
        k = max(i for i, (t0, _) in enumerate(events) if t0 <= t)
        t0, which = events[k]
        flip = min(1.0, (t - t0) / 0.28) if k else ease(t / 0.4)
        sy = 0.25 + 0.75 * back(flip, 1.2) if k else 1.0
        h = 236 if which == "q" else 140
        strip = paper_rect(920, h)
        if which == "q":
            q1, q2 = self.q
            put(strip, q1, (920 - q1.shape[1]) // 2, -4)
            put(strip, q2, (920 - q2.shape[1]) // 2, 104)
        else:
            lay = self.heads[which][1]
            put(strip, lay, (920 - lay.shape[1]) // 2, (h - lay.shape[0]) // 2)
        tp = tape()
        if sy < 0.999:
            strip = cv2.resize(strip, (920, max(2, int(h * sy))), interpolation=cv2.INTER_AREA)
        cy = 120 + h / 2 if which == "q" else 210
        place_rotated(f, strip, 540, cy, -0.8, flip if not k else 1.0, shadow=0.25)
        place_rotated(f, tp, 120, cy - h / 2 + 4, -28, flip if not k else 1.0, shadow=0)
        place_rotated(f, tp, 960, cy - h / 2 + 4, 24, flip if not k else 1.0, shadow=0)


# -------------------------------------------------------------- stickers ---
def _poly(img, pts, col, th, p=1.0):
    pts = np.asarray(pts, np.float32)
    cv2.polylines(img, [np.round(pts * 4).astype(np.int32)], False, col, th, cv2.LINE_AA, shift=2)


class Diagram:
    """Direct injection: the injector sits in the combustion chamber; deposits grow on its tip."""
    SW, SH = 430, 520

    def __init__(self, t_in, t_dep, t_out):
        self.t_in, self.t_dep, self.t_out = t_in, t_dep, t_out
        self.strokes = [
            np.array([[110, 470], [110, 190], [330, 190], [330, 470]], np.float32),             # cylinder
            np.array([[80, 190], [360, 190]], np.float32),                                        # head
            np.array([[120, 390], [320, 390], [320, 440], [120, 440], [120, 390]], np.float32),   # piston
            np.array([[220, 440], [220, 505]], np.float32),                                       # rod
            np.array([[180, 190], [200, 140]], np.float32), np.array([[260, 190], [240, 140]], np.float32),  # valves
        ]
        self.inj = [np.array([[48, 70], [92, 44], [178, 186], [146, 206], [48, 70]], np.float32),
                    np.array([[162, 196], [176, 216]], np.float32)]
        rng = np.random.default_rng(3)
        self.dep = [(176 + rng.uniform(-14, 14), 220 + rng.uniform(-8, 14), rng.uniform(5, 10)) for _ in range(9)]
        self.lab_inj = ink_line((("البخاخ", CHA, True),), 34, pad=6)
        self.lab_ch = ink_line((("غرفة", CHA, False), ("الاحتراق", CHA, False)), 30, pad=6, bold=False)
        self.lab_dep = ink_line((("ترسّبات", RED, False),), 34, pad=6)
        self.lab_gdi = ink_line((("حقن", GREY, False), ("مباشر", GREY, False), ("GDI", GREY, False)), 26, pad=4, bold=False)

    def layer(self, t):
        s = 2
        ink = np.zeros((self.SH * s, self.SW * s), np.float32)
        p = ease((t - self.t_in - 0.15) / 0.9)
        for st in V.partial_strokes(self.strokes, p):
            _poly(ink, st * s, 1.0, 5 * s)
        pi = ease((t - self.t_in - 0.7) / 0.6)
        for st in V.partial_strokes(self.inj, pi):
            _poly(ink, st * s, 1.0, 5 * s)
        ink = cv2.resize(ink, (self.SW, self.SH), interpolation=cv2.INTER_AREA)
        out = paper_rect(self.SW, self.SH)
        a = np.clip(ink, 0, 1)[..., None]
        out[..., :3] = out[..., :3] * (1 - a) + a * np.array(CHA, np.float32) / 255 * out[..., 3:4]
        # spray (yellow) into the chamber
        q = ease((t - self.t_in - 1.2) / 0.4)
        if q > 0:
            sp = np.zeros((self.SH, self.SW), np.float32)
            for k in range(7):
                ang = math.radians(40 + k * 9)
                L = 70 * q
                cv2.line(sp, (176, 222), (int(176 + L * math.cos(ang)), int(222 + L * math.sin(ang))), 1.0, 3, cv2.LINE_AA)
            a = (sp * 0.9)[..., None]
            out[..., :3] = out[..., :3] * (1 - a) + a * np.array(YEL, np.float32) / 255
        # labels
        q = ease((t - self.t_in - 1.0) / 0.3)
        if q > 0:
            R.over_local = None
            self._over(out, self.lab_inj, 240, 56, q)
            arr = np.zeros((self.SH, self.SW), np.float32)
            cv2.arrowedLine(arr, (246, 100), (int(246 - 86 * q), int(100 + 22 * q)), 1.0, 3, cv2.LINE_AA, tipLength=0.22)
            a = arr[..., None]
            out[..., :3] = out[..., :3] * (1 - a) + a * np.array(CHA, np.float32) / 255
            self._over(out, self.lab_ch, (self.SW - self.lab_ch.shape[1]) // 2 + 30, 300, q)
            self._over(out, self.lab_gdi, (self.SW - self.lab_gdi.shape[1]) // 2, self.SH - 46, q)
        # deposits grow on the tip
        d = ease((t - self.t_dep) / 0.8)
        if d > 0:
            m = np.zeros((self.SH, self.SW), np.float32)
            for k, (x, y, r) in enumerate(self.dep):
                rr = r * ease((t - self.t_dep - k * 0.06) / 0.4)
                if rr > 0.5:
                    cv2.circle(m, (int(x), int(y)), int(rr), 1.0, -1, cv2.LINE_AA)
            a = m[..., None] * 0.92
            out[..., :3] = out[..., :3] * (1 - a) + a * np.array([0.32, 0.12, 0.08], np.float32)
            self._over(out, self.lab_dep, 250, 236, ease((t - self.t_dep - 0.3) / 0.3))
            arr = np.zeros((self.SH, self.SW), np.float32)
            pa = ease((t - self.t_dep - 0.3) / 0.35)
            if pa > 0:
                x1 = int(252 - 50 * pa)
                cv2.arrowedLine(arr, (252, 262), (x1, int(262 - 28 * pa)), 1.0, 3, cv2.LINE_AA, tipLength=0.3)
                a = arr[..., None]
                out[..., :3] = out[..., :3] * (1 - a) + a * np.array(RED, np.float32) / 255
        tp = tape(110, 32)
        self._over(out, tp, (self.SW - 110) // 2, 0, 1)
        return out

    @staticmethod
    def _over(dst, src, x, y, alpha):
        put(dst, src, x, y, alpha)

    def draw(self, f, t):
        if not (self.t_in <= t < self.t_out + 0.35):
            return
        q = back((t - self.t_in) / 0.45, 1.2)
        o = ease((t - self.t_out) / 0.35)
        cx = 280 - 420 * o
        place_rotated(f, self.layer(t), cx, 1060 + 60 * (1 - min(q, 1)), 3.0 - 3 * (1 - min(q, 1)), min(1.0, q * 2))


class Evidence:
    """The label line, quoted on a taped paper slip and highlighted in yellow; a ✓ stamp on «إزالة»."""
    SW, SH = 840, 236

    def __init__(self, t_in, t_stamp, t_out):
        self.t_in, self.t_stamp, self.t_out = t_in, t_stamp, t_out
        self.cap = ink_line((("من", GREY, False), ("ملصق", GREY, False), ("المنتج", GREY, False)), 26, pad=4, bold=False)
        self.en = R.latin_layer("Cleans the Inside of GDI Injector", 44, CHA, 700, 0.0)
        self.ar = ink_line((("ينظّف", CHA, False), ("البخاخ", CHA, False), ("من", CHA, False), ("الداخل", CHA, False)), 44)

    def layer(self, t):
        out = paper_rect(self.SW, self.SH)
        Diagram._over(out, self.cap, self.SW - self.cap.shape[1] - 30, 10, 1)
        ex, ey = (self.SW - self.en.shape[1]) // 2, 62
        hp = ease((t - self.t_in - 0.4) / 0.6)
        if hp > 0:
            hl = np.zeros((self.SH, self.SW), np.float32)
            cv2.rectangle(hl, (ex - 10, ey + 14), (int(ex - 10 + (self.en.shape[1] + 20) * hp), ey + self.en.shape[0] + 6), 0.85, -1)
            a = hl[..., None]
            out[..., :3] = out[..., :3] * (1 - a) + a * np.array(YEL, np.float32) / 255
        Diagram._over(out, self.en, ex, ey, 1)
        Diagram._over(out, self.ar, (self.SW - self.ar.shape[1]) // 2, 128, ease((t - self.t_in - 0.7) / 0.3))
        sp = (t - self.t_stamp) / 0.3
        if sp > 0:
            st = np.zeros((self.SH, self.SW), np.float32)
            c, r = (70, 150), int(46 * (1.4 - 0.4 * ease(min(sp, 1))))
            cv2.circle(st, c, r, 1.0, 5, cv2.LINE_AA)
            cv2.polylines(st, [np.array([[c[0] - 20, c[1]], [c[0] - 4, c[1] + 16], [c[0] + 22, c[1] - 14]], np.int32)],
                          False, 1.0, 7, cv2.LINE_AA)
            a = st[..., None] * min(1.0, sp)
            out[..., :3] = out[..., :3] * (1 - a) + a * np.array([0.78, 0.55, 0.0], np.float32)
        Diagram._over(out, tape(120, 34), (self.SW - 120) // 2, 0, 1)
        return out

    def draw(self, f, t):
        if not (self.t_in <= t < self.t_out + 0.35):
            return
        q = back((t - self.t_in) / 0.45, 1.2)
        o = ease((t - self.t_out) / 0.35)
        place_rotated(f, self.layer(t), 540, 390 - 30 * (1 - min(q, 1)) - 500 * o, -1.5, min(1.0, q * 2) * (1 - o))


class Results:
    """Two result cards, each on its own word: more efficiency ↑, less fuel ↓."""
    SW, SH = 400, 270

    def __init__(self, t1, t2, t_out):
        self.t = (t1, t2)
        self.t_out = t_out
        self.cards = [
            (ink_line((("كفاءة", CHA, False), ("أعلى", CHA, True)), 50), ink_line((("للمحرك", CHA, False),), 36, bold=False), "gauge"),
            (ink_line((("استهلاك", CHA, False), ("أقل", CHA, True)), 50), ink_line((("للوقود", CHA, False),), 36, bold=False), "fuel"),
        ]

    def icon(self, kind, p):
        s = 2
        ink = np.zeros((96 * s, 120 * s), np.float32)
        if kind == "gauge":
            strokes = [V._arc(48, 60, 40, 40, 180, 360, 40), np.array([[48, 60], [48 + 30 * math.cos(math.radians(-40)), 60 + 30 * math.sin(math.radians(-40))]])]
            arrow = [np.array([[100, 70], [100, 22]]), np.array([[88, 36], [100, 22], [112, 36]])]
        else:
            strokes = [np.array([[20, 86], [20, 18], [62, 18], [62, 86], [20, 86]]), np.array([[28, 30], [54, 30], [54, 50], [28, 50], [28, 30]]),
                       np.array([[62, 40], [74, 46], [74, 74], [80, 80]])]
            arrow = [np.array([[100, 22], [100, 70]]), np.array([[88, 56], [100, 70], [112, 56]])]
        for st in V.partial_strokes([np.asarray(x, np.float32) for x in strokes], p):
            _poly(ink, np.asarray(st) * s, 1.0, 7 * s)
        arr = np.zeros_like(ink)
        for st in V.partial_strokes([np.asarray(x, np.float32) for x in arrow], max(0.0, p * 1.4 - 0.4)):
            _poly(arr, np.asarray(st) * s, 1.0, 8 * s)
        return cv2.resize(ink, (120, 96), interpolation=cv2.INTER_AREA), cv2.resize(arr, (120, 96), interpolation=cv2.INTER_AREA)

    def draw(self, f, t):
        for k, (t0, (l1, l2, kind)) in enumerate(zip(self.t, self.cards)):
            if not (t0 <= t < self.t_out + 0.3):
                continue
            out = paper_rect(self.SW, self.SH)
            ink, arr = self.icon(kind, ease((t - t0 - 0.05) / 0.5))
            for m, col in ((ink, CHA), (arr, (214, 150, 0))):
                a = np.clip(m, 0, 1)[..., None]
                reg = out[18:114, (self.SW - 120) // 2:(self.SW + 120) // 2]
                reg[..., :3] = reg[..., :3] * (1 - a) + a * np.array(col, np.float32) / 255
            Diagram._over(out, l1, (self.SW - l1.shape[1]) // 2, 112, 1)
            Diagram._over(out, l2, (self.SW - l2.shape[1]) // 2, 186, 1)
            Diagram._over(out, tape(100, 30), (self.SW - 100) // 2, 0, 1)
            q = back((t - t0) / 0.4, 1.3)
            o = ease((t - self.t_out) / 0.3)
            cx = 755 if k == 0 else 325
            rot = (-2.5 if k == 0 else 2.0) * min(q, 1)
            place_rotated(f, out, cx, 1300 + 80 * (1 - min(q, 1)), rot, min(1.0, q * 2) * (1 - o))


# --------------------------------------------------------------- footage ---
def marker_circle(img, t0, t, center, r, lab):
    """Red marker circle drawn round the injector tip, then an arrow and «ترسّبات» (source-frame coords)."""
    p = ease((t - t0) / 0.5)
    if p <= 0:
        return
    m = np.zeros(img.shape[:2], np.float32)
    a = np.radians(np.linspace(-120, -120 + 380 * p, 80))
    wob = 1 + 0.06 * np.sin(a * 3)
    pts = np.stack([center[0] + r * 1.15 * wob * np.cos(a), center[1] + r * 0.9 * wob * np.sin(a)], 1)
    _poly(m, pts, 1.0, 7)
    pa = ease((t - t0 - 0.4) / 0.3)
    if pa > 0:
        x0, y0 = center[0] - 40, center[1] + r + 150
        x1, y1 = x0 + (center[0] - 30 - x0) * pa, y0 + (center[1] + r + 10 - y0) * pa
        cv2.arrowedLine(m, (int(x0), int(y0)), (int(x1), int(y1)), 1.0, 6, cv2.LINE_AA, tipLength=0.25)
    a = m[..., None]
    img[:] = img * (1 - a) + a * np.array(RED, np.float32) / 255
    q = ease((t - t0 - 0.6) / 0.3)
    if q > 0:
        bg = paper_rect(lab.shape[1] + 20, lab.shape[0] + 6)
        Diagram._over(bg, lab, 10, 3, 1)
        R.over_src = None
        x, y = int(center[0] - 40 - bg.shape[1] / 2), int(center[1] + r + 150)
        reg = img[y:y + bg.shape[0], x:x + bg.shape[1]]
        s = bg[:reg.shape[0], :reg.shape[1]] * q
        reg *= 1 - s[..., 3:4]
        reg += s[..., :3]


def zoom_frame(fr, t):
    k = max(i for i, s in enumerate(SEGMENTS + [(CTA_T, DUR, "")]) if s[0] <= t)
    s0 = (SEGMENTS + [(CTA_T, DUR, "")])[k][0]
    s1 = (SEGMENTS + [(CTA_T, DUR, "")])[k][1]
    z, ax, ay = ZOOM[k]
    sc = z * (1 + 0.03 * ease((t - s0) / max(s1 - s0, 0.1)))
    cx, cy = ax * SRC_W, ay * SRC_H
    M = np.float32([[sc, 0, cx * (1 - sc)], [0, sc, cy * (1 - sc)]])
    return cv2.warpAffine(fr, M, (SRC_W, SRC_H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)


class Card:
    def __init__(self):
        self.frame = np.ones((CARD_H, CARD_W, 4), np.float32)
        self.frame[..., :3] = 0.985
        M = cv2.getRotationMatrix2D((CARD_W / 2, CARD_H / 2), CARD_ROT, 1.0)
        s = int(math.hypot(CARD_W, CARD_H)) + 40
        M[0, 2] += s / 2 - CARD_W / 2
        M[1, 2] += s / 2 - CARD_H / 2
        self.M, self.s = M, s
        a = cv2.warpAffine(np.ones((CARD_H, CARD_W), np.float32), M, (s, s))
        self.shadow = cv2.GaussianBlur(a, (0, 0), 16) * 0.32
        self.alpha = a
        self.tp = tape(150, 40)

    def draw(self, f, fr):
        card = self.frame.copy()
        card[BORDER:BORDER + IN_H, BORDER:BORDER + IN_W, :3] = cv2.resize(fr, (IN_W, IN_H), interpolation=cv2.INTER_AREA)
        rgb = cv2.warpAffine(card[..., :3], self.M, (self.s, self.s))
        x0, y0 = int(CARD_C[0] - self.s / 2), int(CARD_C[1] - self.s / 2)
        sh = np.zeros((self.s, self.s, 4), np.float32)
        sh[..., 3] = self.shadow
        R.over(f, sh, x0 + 6, y0 + 14)
        lay = np.dstack([rgb * self.alpha[..., None], self.alpha])
        R.over(f, lay, x0, y0)


# ---------------------------------------------------------------- end card ---
class EndCard:
    """The usual JLM CTA over the defocused, darkened product shot."""

    def __init__(self, t0):
        self.t0 = t0
        self.logo = clean_logo(E.KIT / "logos/logo_on_dark.png", 430)
        self.name = R.latin_layer("GDI Injector Cleaner", 58, SIL, 700, 0.0)
        self.cta = E.T.line([("اطلبه الآن", YEL), ("من خلال", WHT)], 76, bold=True, shadow=False, pad=10)
        self.pill = V.url_pill(70)
        self.deliv = E.T.line([("مع توفّر", WHT), ("خدمة التوصيل", YEL)], 54, bold=True, shadow=False, pad=8)
        self.tr = V.EndCard(t0)
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        self.vign = (0.05 * np.exp(-(((xx - W / 2) / 520) ** 2 + ((yy - 0.42 * H) / 700) ** 2)))[..., None]

    def draw(self, f, t, bg_frame):
        b = ease((t - self.t0) / 0.35)
        if b <= 0:
            return
        full = cv2.resize(bg_frame, (W, H), interpolation=cv2.INTER_LINEAR)
        small = cv2.resize(full, (W // 6, H // 6), interpolation=cv2.INTER_AREA)
        bg = cv2.resize(cv2.GaussianBlur(small, (0, 0), 5), (W, H), interpolation=cv2.INTER_CUBIC)
        bg = bg * 0.38 + self.vign * np.array([1.0, 0.75, 0.15], np.float32)
        f[:] = f * (1 - b) + bg * b
        t0 = self.t0 + 0.15
        q = ease((t - t0) / 0.45)
        R.over(f, self.logo, (W - self.logo.shape[1]) / 2, 0.20 * H - self.logo.shape[0] / 2 + 14 * (1 - q), q)
        q = ease((t - t0 - 0.35) / 0.4)
        R.over(f, self.name, (W - self.name.shape[1]) / 2, 0.315 * H - self.name.shape[0] / 2 + 12 * (1 - q), q)
        q = ease((t - t0 - 0.7) / 0.35)
        R.over(f, self.cta, (W - self.cta.shape[1]) / 2, 0.47 * H - self.cta.shape[0] / 2 + 12 * (1 - q), q)
        q = back((t - t0 - 1.0) / 0.4, 1.0)
        if q > 0:
            pill = self.pill.copy()
            sp = (t - t0 - 1.6) / 0.7
            if 0 < sp < 1:
                xs = np.arange(pill.shape[1], dtype=np.float32)
                band = np.exp(-((xs - (-80 + (pill.shape[1] + 160) * ease(sp))) / 40) ** 2)[None, :, None]
                pill[..., :3] += band * pill[..., 3:4] * 0.45
            lay, x, y = R.warp_premul(pill, 0.6 + 0.4 * q, W / 2, 0.55 * H, (pill.shape[1] / 2, pill.shape[0] / 2))
            R.over(f, lay, x, y, min(1.0, q))
        q = ease((t - t0 - 1.35) / 0.3)
        if q > 0:
            tr = self.tr.truck(ease((t - t0 - 1.35) / 0.8), 140)
            row = self.deliv.shape[1] + tr.shape[1]
            x0, y = (W - row) / 2, 0.645 * H
            R.over(f, tr, x0, y - tr.shape[0] / 2, q)
            R.over(f, self.deliv, x0 + tr.shape[1], y - self.deliv.shape[0] / 2 + 4, q)


def paper_bg():
    rng = np.random.default_rng(1)
    g = cv2.GaussianBlur(rng.normal(0, 1, (H, W)).astype(np.float32), (0, 0), 1.0) * 0.010
    fib = cv2.GaussianBlur(rng.normal(0, 1, (H // 4, W // 4)).astype(np.float32), (0, 0), 6)
    fib = cv2.resize(fib, (W, H)) * 0.012
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    vig = 1 - 0.04 * np.clip(np.hypot((xx - W / 2) / W, (yy - H / 2) / H) * 1.6, 0, 1) ** 2
    return np.clip((PAPER[None, None, :] + (g + fib)[..., None]) * vig[..., None], 0, 1).astype(np.float32)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--stills")
    a = ap.parse_args()
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)

    caps = Captions(word_times(V.voiced_weight(a.src)))
    at = caps.at
    for wd, s, e in caps.all:
        print(f"{s:5.2f}-{e:5.2f} {wd}")
    title = Title(caps)
    diagram = Diagram(at("بسبب") + 0.1, at("تراكمات"), SEGMENTS[3][0] - 0.05)
    t_circle = at("البخاخ", 1)
    lab_dep = ink_line((("ترسّبات", RED, False),), 40, pad=6)
    evidence = Evidence(at("منظف"), at("إزالة"), SEGMENTS[6][0] - 0.1)
    results = Results(at("كفاءة"), at("استهلاك"), CTA_T - 0.1)
    card = Card()
    logo = clean_logo(E.KIT / "logos/logo_on_yellow.png", 190)
    end = EndCard(CTA_T)
    bg0 = paper_bg()

    src = subprocess.Popen(["ffmpeg", "-v", "error", "-i", a.src, "-vf", "eq=contrast=1.04:saturation=1.06",
                            "-f", "rawvideo", "-pix_fmt", "rgb24", "-r", str(FPS), "-"], stdout=subprocess.PIPE)
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
    last, frozen = None, None
    for n in range(n_frames):
        t = n / FPS
        raw = src.stdout.read(SRC_W * SRC_H * 3)
        if len(raw) == SRC_W * SRC_H * 3:
            last = np.frombuffer(raw, np.uint8).reshape(SRC_H, SRC_W, 3).astype(np.float32) / 255
        if t <= FREEZE_T:
            frozen = last
        f = bg0.copy()
        if t < CTA_T + 0.4:
            fr = last.copy()
            if SEGMENTS[3][0] <= t < SEGMENTS[4][0]:
                marker_circle(fr, t_circle, t, TIP, 62, lab_dep)
            fr = zoom_frame(fr, t)
            card.draw(f, fr)
            R.over(f, logo, (W - logo.shape[1]) / 2, 34, ease((t - 0.2) / 0.4))
            title.draw(f, t)
            diagram.draw(f, t)
            evidence.draw(f, t)
            results.draw(f, t)
            caps.draw(f, t)
        end.draw(f, t, frozen)
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

    # soft paper swells for each sticker, very quiet ticks for the marker and stamps (≈ −40 dBFS)
    V.DUR = DUR
    ticks = [(diagram.t_in + 0.05, 460.0), (diagram.t_dep + 0.05, 380.0), (t_circle + 0.05, 400.0),
             (evidence.t_in + 0.05, 460.0), (evidence.t_stamp + 0.05, 520.0), (results.t[0] + 0.05, 480.0),
             (results.t[1] + 0.05, 480.0), (CTA_T + 1.2, 440.0), (CTA_T + 1.55, 440.0)]
    ticks += [(t0, 500.0) for t0, _ in title.heads]
    sfx = out.with_name(out.stem + "_sfx.wav")
    V.sfx_track(sfx, ticks, [diagram.t_in, evidence.t_in, results.t[0], CTA_T + 0.1])
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(tmp_v), "-i", a.src, "-i", str(sfx),
                    "-filter_complex",
                    f"[1:a]aresample=48000,apad=whole_dur={DUR}[v];[v][2:a]amix=inputs=2:normalize=0:duration=longest,"
                    "volume=-3dB,alimiter=limit=0.63:attack=2:release=60:level=false,loudnorm=I=-14:TP=-2.5:LRA=11[a]",
                    "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                    "-t", f"{DUR:.2f}", "-movflags", "+faststart", str(out)], check=True)
    tmp_v.unlink(missing_ok=True)
    sfx.unlink(missing_ok=True)
    print("wrote", out)


if __name__ == "__main__":
    main()
