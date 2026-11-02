"""JLM GDI Injector Cleaner — the usual JLM edit (same look as the Brake Cleaner reel):
Clean / Minimal with a Kinetic opening, on the jump-cut clean-up from scripts/cut.py.

    python3 scripts/cut.py src/raw.mp4 build/cut.mov
    python3 scripts/edit.py --src build/cut.mov --out out/jlm_gdi_injector_cleaner.mp4 [--stills 1,5,...]

- Kinetic hook: «لماذا يلزم نستخدم» word by word → «مضاف البخاخات» lands in yellow with a soft spray
  mist → «من JLM في المحركات الجديدة؟».
- One-line karaoke captions at 66 % height on a soft dark box (above the can on the product shot).
- Two linked icon pairs: تراكمات وترسّبات → على البخاخ (problem), كفاءة أعلى → استهلاك أقل (result).
  A small «JLM GDI Injector Cleaner» tag on the product shot.
- Soft breathing zoom per shot, 1.00 ↔ 1.08 over the jump cuts; JLM logo top-left without the logo
  file's background box; the usual CTA over the blurred product shot (the clip's white card is gone).
Shared pieces come from jlm-care-edit/scripts/edit_v3.py.
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
YEL, WHT, RED, GREY, CHA = V.YEL, V.WHT, V.RED, V.GREY, V.CHA
SIL = (192, 196, 199)
END_T = 18.41                      # CTA card starts with the spoken CTA (cut timeline)
FREEZE_T = 20.0                    # last product frame before the clip's own white card
DUR = 24.6
# shot changes and jump cuts in the cut timeline (scripts/cut.py)
CUTS = [0.0, 3.45, 5.25, 6.77, 9.08, 10.70, 11.90, 13.49, 14.51, 15.31, 16.88, 18.41, DUR]
PRESENTER = {0, 1, 8, 9, 10}       # pieces where the presenter is on screen
JUMP = {3, 5, 7, 9}                # same shot as the piece before: punch in to hide the cut
PRODUCT_SHOT = (11.90, 14.51)
ease = V.ease_io
back = V.back

# speech segments between pauses (Whisper turbo, checked window by window)
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
# "#" = carried by the kinetic hook; "!" stays red (problem); "*" stays yellow (key idea)
PHRASES = [
    "#لماذا يلزم نستخدم", "#مضاف البخاخات", "#من JLM في المحركات الجديدة",
    "بسبب مكان وجود *البخاخ", "في المحركات الجديدة", "فوق *غرفة *الاحتراق",
    "هذا الشي بيؤدي إلى", "!تراكمات !وترسّبات",
    "تظهر على *البخاخ مع الوقت",
    "وبالتالي استخدام", "منظف *JLM بشكل دوري",
    "بساعد على *إزالة", "هذه !التراكمات",
    "وبيعطيك *كفاءة *أعلى للمحرك",
    "وبالتالي *استهلاك *أقل للوقود",
]


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


def is_ar(w):
    return any("؀" <= ch <= "ۿ" for ch in w)


@lru_cache(maxsize=None)
def mixed_line(runs, size, shadow=True, pad=26):
    """Arabic words in Helvetica Neue LT Arabic Bold, Latin words/numbers in Albert Sans (RTL order)."""
    fa = E.T.font(size, True)
    fl = R.albert(int(size * 0.92), 800)
    words = [(w, c) for w, c in runs]
    space = fa.getlength(" ", direction="rtl") * 1.05
    advs = [(fa.getlength(w, direction="rtl") if is_ar(w) else fl.getlength(w)) for w, _ in words]
    asc, desc = fa.getmetrics()
    dy_l = asc - fl.getmetrics()[0]          # share the baseline with the Arabic words
    lw = int(sum(advs) + space * (len(words) - 1)) + 2 * pad
    img = Image.new("RGBA", (lw, asc + desc + 2 * pad), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    x = lw - pad
    # Latin runs keep their own left-to-right order inside the RTL line
    i = 0
    while i < len(words):
        if is_ar(words[i][0]):
            x -= advs[i]
            d.text((x, pad), words[i][0], font=fa, fill=tuple(words[i][1]) + (255,), direction="rtl")
            x -= space
            i += 1
            continue
        j = i
        while j < len(words) and not is_ar(words[j][0]):
            j += 1
        run_w = sum(advs[i:j]) + space * (j - i - 1)
        xl = x - run_w
        for k in range(i, j):
            d.text((xl, pad + dy_l), words[k][0], font=fl, fill=tuple(words[k][1]) + (255,))
            xl += advs[k] + space
        x -= run_w + space
        i = j
    return E.T._finish(img, shadow)


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
            nxt = self.phrases[i + 1]["items"][0][2] if i + 1 < len(self.phrases) else END_T
            p["t1"] = min(nxt, p["items"][-1][3] + 0.45)
        self.all = [(wd, s, e) for p in self.phrases for wd, _, s, e in p["items"]]

    def at(self, word, nth=0):
        return [s for wd, s, _ in self.all if wd == word][nth]

    @staticmethod
    @lru_cache(maxsize=None)
    def layer(key):
        items, active = key
        runs = []
        for i, (wd, tone) in enumerate(items):
            col = GREY if i > active else RED if tone == "!" else YEL if (tone == "*" or i == active) else WHT
            runs.append((wd, col))
        txt = mixed_line(tuple(runs), 64)
        box = V.soft_box(txt.shape[1] - 18, txt.shape[0] - 30)
        out = np.zeros((max(box.shape[0], txt.shape[0]), max(box.shape[1], txt.shape[1]), 4), np.float32)
        R.paste_into(out, box, (out.shape[1] - box.shape[1]) // 2, (out.shape[0] - box.shape[0]) // 2)
        R.paste_into(out, txt, (out.shape[1] - txt.shape[1]) // 2, (out.shape[0] - txt.shape[0]) // 2)
        return out

    def draw(self, f, t):
        y = 0.19 * H if PRODUCT_SHOT[0] <= t < PRODUCT_SHOT[1] else 0.66 * H
        for p in self.phrases:
            if p["hidden"] or not (p["t0"] <= t < p["t1"]):
                continue
            active = max(i for i, it in enumerate(p["items"]) if it[2] <= t)
            lay = self.layer((tuple((wd, tone) for wd, tone, _, _ in p["items"]), active))
            R.over(f, lay, (W - lay.shape[1]) / 2, y - lay.shape[0] / 2, min(1.0, (t - p["t0"]) / 0.08))


# ------------------------------------------------------------ new line icons ---
def _dust():
    cloud = np.concatenate([V._arc(-0.36, 0.10, 0.30, 0.30, 90, 270, 20), V._arc(-0.06, -0.20, 0.36, 0.36, 180, 360, 24),
                            V._arc(0.38, 0.04, 0.30, 0.30, 250, 450, 20), [[0.38, 0.34], [-0.36, 0.40]]])
    dots = [V._arc(x, y, 0.05, 0.05, 0, 360, 10) for x, y in [(-0.50, 0.66), (-0.10, 0.74), (0.30, 0.64), (0.62, 0.78), (0.08, 0.56)]]
    return [cloud] + dots


def _injector():
    plug = np.array([[-0.18, -0.62], [-0.18, -0.86], [0.18, -0.86], [0.18, -0.62]])
    body = V._rrect(-0.30, -0.62, 0.30, 0.22, 0.08)
    neck = np.array([[-0.12, 0.22], [-0.12, 0.52], [0.12, 0.52], [0.12, 0.22]])
    tip = np.array([[-0.07, 0.52], [-0.07, 0.64], [0.07, 0.64], [0.07, 0.52]])
    spray = [np.array([[0, 0.70], [-0.30, 0.94]]), np.array([[0, 0.72], [0, 0.98]]), np.array([[0, 0.70], [0.30, 0.94]])]
    return [plug, body, neck, tip] + spray


def _gauge():
    dial = V._arc(0, 0.20, 0.74, 0.74, 180, 360, 48)
    ticks = [np.array([[0.74 * math.cos(a), 0.20 + 0.74 * math.sin(a)], [0.58 * math.cos(a), 0.20 + 0.58 * math.sin(a)]])
             for a in np.radians([200, 240, 270, 300, 340])]
    needle = np.array([[0, 0.20], [0.46 * math.cos(math.radians(-38)), 0.20 + 0.46 * math.sin(math.radians(-38))]])
    hub = V._arc(0, 0.20, 0.07, 0.07, 0, 360, 12)
    base = np.array([[-0.74, 0.20], [-0.74, 0.44], [0.74, 0.44], [0.74, 0.20]])
    return [dial] + ticks + [needle, hub, base]


def _fuel():
    pump = V._rrect(-0.62, -0.70, 0.18, 0.80, 0.08)
    window = V._rrect(-0.48, -0.54, 0.04, -0.12, 0.05)
    hose = np.array([[0.18, -0.40], [0.44, -0.40], [0.56, -0.26], [0.56, 0.44], [0.70, 0.56]])
    nozzle = np.array([[0.44, -0.40], [0.44, -0.62], [0.62, -0.62]])
    base = np.array([[-0.76, 0.80], [0.32, 0.80]])
    return [pump, window, hose, nozzle, base]


V.ICONS.update({"dust": _dust, "injector": _injector, "gauge": _gauge, "fuel": _fuel})


def logo_layer(width, shadow=0.0):
    """logo_on_dark.png without the faint grey box the file carries (alpha 1–40 over the whole
    canvas, plus a hairline frame): keep only the alpha that belongs to the mark and the letters,
    so the logo sits straight on the video. No drop shadow by default: a soft shadow fills the gaps
    between the letters and reads as a dark box behind the logo."""
    im = np.array(Image.open(E.KIT / "logos/logo_on_dark.png").convert("RGBA"))
    a = im[..., 3]
    keep = cv2.dilate((a > 128).astype(np.uint8), np.ones((5, 5), np.uint8))
    im[..., 3] = a * keep
    im[:4], im[-4:], im[:, :4], im[:, -4:] = 0, 0, 0, 0
    im = Image.fromarray(im).resize((width, int(im.shape[0] * width / im.shape[1])), Image.LANCZOS)
    lay = R.to_premul(np.array(im))
    pad = 20
    out = np.zeros((lay.shape[0] + 2 * pad, lay.shape[1] + 2 * pad, 4), np.float32)
    if shadow:
        out[pad + 3:pad + 3 + lay.shape[0], pad:pad + lay.shape[1], 3] = cv2.GaussianBlur(lay[..., 3], (0, 0), 6) * shadow
    R.paste_into(out, lay, pad, pad)
    return out


V.logo_layer = logo_layer


class Pairs(V.Pairs):
    """The approved linked pair, a little smaller (lighter on screen)."""
    Y = 0.765 * H
    XA, XB = 0.72 * W, 0.28 * W
    SC = 0.82

    def _badge(self, f, cx, lt, out, icon, color, label):
        layer = V.badge_layer(icon, color, lt)
        sc = (0.35 + 0.65 * back(lt / 0.32)) * (0.92 + 0.08 * out) * self.SC
        lay, x, y = R.warp_premul(layer, sc, cx, self.Y, (layer.shape[1] / 2, layer.shape[0] / 2))
        R.over(f, lay, x, y, min(1.0, lt / 0.08) * out)
        q = ease((lt - 0.45) / 0.25)
        if q > 0:
            lab = V.label_layer(label, color)
            R.over(f, lab, cx - lab.shape[1] / 2, self.Y + V.BADGE * self.SC / 2 + 4 + 10 * (1 - q), q * out)

    def _arrow(self, f, p, out, ca, cb):
        xa, xb = self.XA, self.XB
        self.XA, self.XB = xa - V.BADGE * (1 - self.SC) / 2, xb + V.BADGE * (1 - self.SC) / 2
        super()._arrow(f, p, out, ca, cb)
        self.XA, self.XB = xa, xb


# ---------------------------------------------------------------- kinetic hook ---
class Hook:
    """«لماذا يلزم نستخدم» word by word → «مضاف البخاخات» lands in yellow with a soft spray mist from
    both ends → «من JLM في المحركات الجديدة؟»."""

    def __init__(self, caps):
        self.small = [(caps.at(w), w) for w in "لماذا يلزم نستخدم".split()]
        self.t_big = caps.at("مضاف")
        self.t_low = caps.at("من", 0)
        self.t_out = caps.at("بسبب") - 0.08
        self.big = E.T.line([("مضاف", WHT), ("البخاخات", YEL)], 118, bold=True, shadow=True, pad=30)
        self.low = mixed_line((("من", WHT), ("JLM", YEL), ("في", WHT), ("المحركات", WHT), ("الجديدة؟", WHT)), 66)
        self.words = [E.T.line([(w, WHT)], 56, bold=True, shadow=True, pad=16) for _, w in self.small]
        gap = 14
        self.row_w = sum(x.shape[1] for x in self.words) - 32 * len(self.words) + gap * (len(self.words) - 1)
        self.gap = gap
        yy = np.arange(H, dtype=np.float32)[:, None, None]
        self.band = (0.62 * np.exp(-((yy - 0.69 * H) / (0.16 * H)) ** 2)).astype(np.float32)
        rng = np.random.default_rng(9)
        self.mist = [(rng.uniform(-0.45, 0.45), rng.uniform(160, 330), rng.uniform(0, 0.5), rng.uniform(2.5, 6))
                     for _ in range(46)]

    def draw(self, f, t):
        if not (0 <= t < self.t_out + 0.3):
            return
        out = 1 - ease((t - self.t_out) / 0.3)
        f *= 1 - self.band * min(1.0, t / 0.25) * out
        x = (W + self.row_w) / 2
        for (ts, _), lay in zip(self.small, self.words):
            w = lay.shape[1] - 32
            q = back((t - ts) / 0.22)
            if t >= ts:
                l2, lx, ly = R.warp_premul(lay, 0.8 + 0.2 * min(q, 1.1), x - w / 2, 0.585 * H, (lay.shape[1] / 2, lay.shape[0] / 2))
                R.over(f, l2, lx, ly, min(1.0, (t - ts) / 0.1) * out)
            x -= w + self.gap
        lt = t - self.t_big
        if lt >= 0:
            q = back(lt / 0.3, 1.6)
            cy = 0.675 * H
            l2, lx, ly = R.warp_premul(self.big, 0.6 + 0.4 * q, W / 2, cy, (self.big.shape[1] / 2, self.big.shape[0] / 2))
            R.over(f, l2, lx, ly, min(1.0, lt / 0.08) * out)
            # a soft spray mist fans out from both ends of the word (an injector spraying)
            half = (self.big.shape[1] - 60) / 2
            m = np.zeros((420, W), np.float32)
            for k, (ang, spd, dl, r) in enumerate(self.mist):
                u = lt - 0.15 - dl
                if u <= 0:
                    continue
                side = 1 if k % 2 else -1
                d = spd * (1 - math.exp(-u * 2.2))
                px = W / 2 + side * (half + 6 + d * math.cos(ang))
                py = 210 + d * math.sin(ang)
                al = max(0.0, 1 - u / 1.6)
                cv2.circle(m, (int(px), int(py)), int(r), al, -1, cv2.LINE_AA)
            m = cv2.GaussianBlur(m, (0, 0), 1.6)
            al = np.clip(m, 0, 1)[..., None] * out * 0.85
            y0 = int(cy - 210)
            reg = f[y0:y0 + 420]
            reg *= 1 - al
            reg += al * (np.array(YEL, np.float32) / 255)
        lt = t - self.t_low
        if lt >= 0:
            q = ease(lt / 0.3)
            R.over(f, self.low, (W - self.low.shape[1]) / 2, 0.765 * H - self.low.shape[0] / 2 + 24 * (1 - q), q * out)


# ------------------------------------------------------------------- pieces ---
def product_tag():
    txt = mixed_line((("JLM", YEL), ("GDI", WHT), ("Injector", WHT), ("Cleaner", WHT)), 44, shadow=False, pad=0)
    h, w = txt.shape[0] + 26, txt.shape[1] + 56
    s = 3
    img = np.zeros((h * s, w * s, 4), np.uint8)
    rr = h * s // 2
    for fill, inset in [(YEL + (255,), 0), ((14, 15, 16, 230), 3 * s)]:
        cv2.rectangle(img, (rr, inset), (w * s - rr, h * s - inset), fill, -1)
        cv2.circle(img, (rr, rr), rr - inset, fill, -1, cv2.LINE_AA)
        cv2.circle(img, (w * s - rr, rr), rr - inset, fill, -1, cv2.LINE_AA)
    pill = R.to_premul(cv2.resize(img, (w, h), interpolation=cv2.INTER_AREA))
    R.paste_into(pill, txt, (w - txt.shape[1]) // 2, (h - txt.shape[0]) // 2 + 2)
    return pill


class EndCard:
    """CTA over the defocused, darkened video: logo, «GDI Injector Cleaner», «اطلبه الآن من خلال», jlmstore.com pill with a sheen,
    «مع توفّر خدمة التوصيل» with the truck drawing itself."""

    def __init__(self, t0):
        self.t0 = t0
        self.logo = V.logo_layer(430)
        self.name = mixed_line((("GDI", SIL), ("Injector", SIL), ("Cleaner", SIL)), 62, shadow=False, pad=10)
        self.cta = E.T.line([("اطلبه الآن", YEL), ("من خلال", WHT)], 76, bold=True, shadow=False, pad=10)
        self.pill = V.url_pill(70)
        self.deliv = E.T.line([("مع توفّر", WHT), ("خدمة التوصيل", YEL)], 54, bold=True, shadow=False, pad=8)
        self.tr = V.EndCard(t0)
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        self.vign = (0.05 * np.exp(-(((xx - W / 2) / 520) ** 2 + ((yy - 0.42 * H) / 700) ** 2)))[..., None]

    def draw(self, f, t):
        b = ease((t - self.t0) / 0.35)
        if b <= 0:
            return False
        # the video stays behind the CTA, defocused and darkened, so the logo sits in the scene
        small = cv2.resize(f, (W // 6, H // 6), interpolation=cv2.INTER_AREA)
        bg = cv2.resize(cv2.GaussianBlur(small, (0, 0), 1 + 4 * b), (W, H), interpolation=cv2.INTER_CUBIC)
        bg = bg * (1 - 0.62 * b) + self.vign * np.array([1.0, 0.75, 0.15], np.float32) * b
        f[:] = f * (1 - b) + bg * b
        t0 = self.t0 + 0.15
        q = ease((t - t0) / 0.45)
        R.over(f, self.logo, (W - self.logo.shape[1]) / 2, 0.20 * H - self.logo.shape[0] / 2 + 14 * (1 - q), q)
        q = ease((t - t0 - 0.35) / 0.4)
        R.over(f, self.name, (W - self.name.shape[1]) / 2, 0.325 * H - self.name.shape[0] / 2 + 12 * (1 - q), q)
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
        return True


def zoom(f, t):
    """Clean breathing zoom (+5 %) over each piece; jump cuts inside one shot punch in to 1.08."""
    k = max(i for i, c in enumerate(CUTS[:-1]) if c <= t)
    s0, s1 = CUTS[k], CUTS[k + 1]
    sc = (1.08 if k in JUMP else 1.0) * (1 + 0.05 * ease((t - s0) / (s1 - s0)))
    ax, ay = (0.6 * W, 0.34 * H) if k in PRESENTER else (0.5 * W, 0.5 * H)
    M = np.float32([[sc, 0, ax * (1 - sc)], [0, sc, ay * (1 - sc)]])
    return cv2.warpAffine(f, M, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)


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
    hook = Hook(caps)
    pairs = Pairs([
        (at("تراكمات"), at("البخاخ", 1), at("وبالتالي", 0) - 0.25,
         ("dust", RED, "تراكمات وترسّبات"), ("injector", RED, "على البخاخ")),
        (at("كفاءة"), at("استهلاك"), END_T - 0.1,
         ("gauge", YEL, "كفاءة أعلى"), ("fuel", YEL, "استهلاك أقل")),
    ])
    tag, tag_t = product_tag(), (max(at("منظف"), PRODUCT_SHOT[0]), PRODUCT_SHOT[1] - 0.1)
    logo = V.logo_layer(210)
    end = EndCard(END_T)
    for wd, s, e in caps.all:
        print(f"{s:5.2f}-{e:5.2f} {wd}")

    src = subprocess.Popen(["ffmpeg", "-v", "error", "-i", a.src, "-vf",
                            f"scale={W}:{H}:flags=lanczos,eq=contrast=1.04:saturation=1.05",
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
    last = None
    for n in range(n_frames):
        t = n / FPS
        if t <= FREEZE_T:
            raw = src.stdout.read(W * H * 3)
            if len(raw) == W * H * 3:
                last = np.frombuffer(raw, np.uint8).reshape(H, W, 3).astype(np.float32) / 255
        f = zoom(last, min(t, DUR - 1e-3))              # the product shot holds under the end card
        if t < END_T + 0.4:
            hook.draw(f, t)
            if tag_t[0] <= t < tag_t[1]:
                p = ease((t - tag_t[0]) / 0.25) * (1 - ease((t - tag_t[1] + 0.2) / 0.2))
                R.over(f, tag, (W - tag.shape[1]) / 2, 0.098 * H + 10 * (1 - p), p)
            pairs.draw(f, t)
            caps.draw(f, t)
            q = ease((t - 0.3) / 0.4)
            R.over(f, logo, 34, 96, q)
        end.draw(f, t)
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

    # soft icon ticks (≈ −40 dBFS), quiet bed, the voice untouched
    V.DUR = DUR
    ticks = [(x + 0.05, 480.0) for it in pairs.items for x in it[:2]]
    ticks += [(hook.t_big + 0.02, 420.0), (tag_t[0] + 0.05, 520.0), (END_T + 1.2, 440.0), (END_T + 1.55, 440.0)]
    sfx = out.with_name(out.stem + "_sfx.wav")
    V.sfx_track(sfx, ticks, [END_T + 0.1])
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
