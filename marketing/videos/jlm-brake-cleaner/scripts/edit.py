"""JLM Brake Cleaner — Clean / Minimal edit of the client's 16 s clip, with a Kinetic opening.

    python3 scripts/edit.py --src src/raw.mp4 --out out/jlm_brake_cleaner.mp4 [--stills 1,5,...]

Style (brand/jlm/EDIT_STYLES.md §1 + §5, VIDEO_STYLE.md):
- Kinetic hook: «إذا كنت بتعاني من / أصوات / في البريكات؟» builds word by word with the speech;
  «أصوات» lands in red and vibrates while sound waves ripple out of it.
- One-line karaoke captions at 66 % height (moved above the can on the product shot).
- Two linked icon pairs under the caption, drawn as thin glowing lines: noise → dust (cause),
  Brake Cleaner → clean brake (solution). A small product tag on the product shot.
- Soft 1.00 → 1.05 breathing zoom per shot, JLM logo top-left, black CTA end card
  (اطلبه الآن من خلال jlmstore.com · مع توفّر خدمة التوصيل). Icon ticks ≈ −40 dBFS.
Shared pieces (badges, icons, end-card parts, audio bed) come from jlm-care-edit/scripts/edit_v3.py.
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
SRC_DUR = 16.0
END_T = 15.95                      # black CTA card starts (right after «لكل البلاد»)
DUR = 19.6
CUTS = [0.0, 4.133, 8.7, 11.033, SRC_DUR]
PRODUCT_SHOT = (8.7, 11.033)
ease = V.ease_io
back = V.back

# speech segments between pauses (Whisper turbo, checked window by window)
SEGMENTS = [
    (0.07, 2.15, "إذا كنت بتعاني من أصوات"),
    (2.28, 4.17, "في البريكات عندك فاحتمال يكون المشكلة مش في البريك"),
    (4.47, 6.09, "ولا إنه البريك خالص بدّه تبديل"),
    (6.22, 8.59, "ممكن يكون تراكم أتربة وغبار على البريك"),
    (8.90, 10.77, "بيتم تنظيفه باستخدام"),
    (11.10, 14.28, "JLM Brake Cleaner سعر العبوة 25 شيكل"),
    (14.41, 15.92, "التوصيل متاح لكل البلاد"),
]
# "#" = carried by the kinetic hook; "!" stays red (problem); "*" stays yellow (key idea)
PHRASES = [
    "#إذا كنت بتعاني من", "#أصوات", "#في البريكات عندك", "#فاحتمال",
    "يكون المشكلة", "مش في *البريك",
    "ولا إنه البريك", "خالص بدّه !تبديل",
    "ممكن يكون !تراكم", "!أتربة !وغبار على البريك",
    "بيتم *تنظيفه باستخدام",
    "*JLM *Brake *Cleaner", "سعر العبوة 25 شيكل",
    "*التوصيل متاح لكل البلاد",
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
        y = 0.215 * H if PRODUCT_SHOT[0] <= t < PRODUCT_SHOT[1] else 0.66 * H
        for p in self.phrases:
            if p["hidden"] or not (p["t0"] <= t < p["t1"]):
                continue
            active = max(i for i, it in enumerate(p["items"]) if it[2] <= t)
            lay = self.layer((tuple((wd, tone) for wd, tone, _, _ in p["items"]), active))
            R.over(f, lay, (W - lay.shape[1]) / 2, y - lay.shape[0] / 2, min(1.0, (t - p["t0"]) / 0.08))


# ------------------------------------------------------------ new line icons ---
def _speaker():
    body = np.array([[-0.70, -0.20], [-0.42, -0.20], [-0.06, -0.52], [-0.06, 0.52], [-0.42, 0.20], [-0.70, 0.20], [-0.70, -0.20]])
    return [body, V._arc(0.02, 0, 0.30, 0.30, -45, 45, 20), V._arc(0.02, 0, 0.56, 0.56, -50, 50, 26),
            V._arc(0.02, 0, 0.82, 0.82, -52, 52, 32)]


def _dust():
    cloud = np.concatenate([V._arc(-0.36, 0.10, 0.30, 0.30, 90, 270, 20), V._arc(-0.06, -0.20, 0.36, 0.36, 180, 360, 24),
                            V._arc(0.38, 0.04, 0.30, 0.30, 250, 450, 20), [[0.38, 0.34], [-0.36, 0.40]]])
    dots = [V._arc(x, y, 0.05, 0.05, 0, 360, 10) for x, y in [(-0.50, 0.66), (-0.10, 0.74), (0.30, 0.64), (0.62, 0.78), (0.08, 0.56)]]
    return [cloud] + dots


def _spray():
    can = V._rrect(-0.36, -0.30, 0.20, 0.84, 0.08)
    cap = np.array([[-0.24, -0.30], [-0.24, -0.50], [0.08, -0.50], [0.08, -0.30]])
    nozzle = np.array([[-0.14, -0.50], [-0.14, -0.62], [0.04, -0.62]])
    band = np.array([[-0.36, 0.10], [0.20, 0.10]])
    mist = [np.array([[0.20, -0.62], [0.74, -0.86]]), np.array([[0.22, -0.56], [0.82, -0.56]]),
            np.array([[0.20, -0.50], [0.74, -0.26]])]
    return [can, cap, nozzle, band] + mist


def _disc_ok():
    rim = V._arc(-0.08, 0.06, 0.72, 0.72, 0, 360, 72)
    hub = V._arc(-0.08, 0.06, 0.24, 0.24, 0, 360, 32)
    lugs = [V._arc(-0.08 + 0.42 * math.cos(a), 0.06 + 0.42 * math.sin(a), 0.05, 0.05, 0, 360, 10)
            for a in np.radians(np.arange(5) * 72 - 90)]
    spark = [np.array([[0.72, -0.86], [0.72, -0.46]]), np.array([[0.52, -0.66], [0.92, -0.66]])]
    return [rim, hub] + lugs + spark


V.ICONS.update({"speaker": _speaker, "dust": _dust, "spray": _spray, "disc_ok": _disc_ok})


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
    """«إذا كنت بتعاني من» word by word → «أصوات» lands red and vibrates, waves ripple → «في البريكات؟»."""

    def __init__(self, caps):
        self.small = [(caps.at(w), w) for w in "إذا كنت بتعاني من".split()]
        self.t_big = caps.at("أصوات")
        self.t_low = caps.at("في", 0)
        self.t_out = caps.at("يكون", 0) - 0.08
        self.big = E.T.line([("أصوات", RED)], 150, bold=True, shadow=True, pad=30)
        self.low = mixed_line((("في", WHT), ("البريكات", YEL), ("عندك؟", WHT)), 76)
        self.words = [E.T.line([(w, WHT)], 54, bold=True, shadow=True, pad=16) for _, w in self.small]
        gap = 14
        self.row_w = sum(x.shape[1] for x in self.words) - 32 * len(self.words) + gap * (len(self.words) - 1)
        self.gap = gap
        yy = np.arange(H, dtype=np.float32)[:, None, None]
        self.band = (0.62 * np.exp(-((yy - 0.69 * H) / (0.16 * H)) ** 2)).astype(np.float32)

    def draw(self, f, t):
        if not (0 <= t < self.t_out + 0.3):
            return
        out = 1 - ease((t - self.t_out) / 0.3)
        f *= 1 - self.band * min(1.0, t / 0.25) * out
        # small line, right to left, each word pops on its own time
        x = (W + self.row_w) / 2
        for (ts, _), lay in zip(self.small, self.words):
            w = lay.shape[1] - 32
            q = back((t - ts) / 0.22)
            if t >= ts:
                l2, lx, ly = R.warp_premul(lay, 0.8 + 0.2 * min(q, 1.1), x - w / 2, 0.585 * H, (lay.shape[1] / 2, lay.shape[0] / 2))
                R.over(f, l2, lx, ly, min(1.0, (t - ts) / 0.1) * out)
            x -= w + self.gap
        # «أصوات»: lands, vibrates (decaying), waves ripple from both sides
        lt = t - self.t_big
        if lt >= 0:
            q = back(lt / 0.28, 1.8)
            jit = 6 * math.sin(lt * 70) * math.exp(-lt * 2.2) if lt > 0.2 else 0
            cy = 0.675 * H
            l2, lx, ly = R.warp_premul(self.big, 0.55 + 0.45 * q, W / 2 + jit, cy, (self.big.shape[1] / 2, self.big.shape[0] / 2))
            R.over(f, l2, lx, ly, min(1.0, lt / 0.08) * out)
            half = (self.big.shape[1] - 60) / 2
            ring = np.zeros((360, W), np.float32)
            for k in range(3):
                ph = (lt * 1.25 - k * 0.33) % 1.0
                if lt * 1.25 < k * 0.33:
                    continue
                r = 40 + 120 * ph
                a = (1 - ph) ** 1.5
                for side in (-1, 1):
                    c = (int(W / 2 + side * (half + 10)), 180)
                    ang0 = -38 if side > 0 else 142
                    cv2.ellipse(ring, c, (int(r), int(r)), 0, ang0, ang0 + 76, a, 5, cv2.LINE_AA)
            glow = cv2.GaussianBlur(ring, (0, 0), 6)
            al = np.clip(ring + glow * 0.6, 0, 1)[..., None] * out * min(1.0, lt / 0.2)
            y0 = int(cy - 180)
            reg = f[y0:y0 + 360]
            reg *= 1 - al * 0.9
            reg += al * 0.9 * (np.array(RED, np.float32) / 255)
        lt = t - self.t_low
        if lt >= 0:
            q = ease(lt / 0.3)
            R.over(f, self.low, (W - self.low.shape[1]) / 2, 0.765 * H - self.low.shape[0] / 2 + 24 * (1 - q), q * out)


# ------------------------------------------------------------------- pieces ---
def product_tag():
    txt = mixed_line((("JLM", YEL), ("Brake", WHT), ("Cleaner", WHT)), 46, shadow=False, pad=0)
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
    """Black CTA: logo, «JLM Brake Cleaner», «اطلبه الآن من خلال», jlmstore.com pill with a sheen,
    «مع توفّر خدمة التوصيل» with the truck drawing itself."""

    def __init__(self, t0):
        self.t0 = t0
        self.logo = V.logo_layer(430)
        self.name = mixed_line((("Brake", SIL), ("Cleaner", SIL)), 70, shadow=False, pad=10)
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
        f *= 1 - b
        f += b * (np.array([0.03, 0.032, 0.035], np.float32) + self.vign * np.array([1.0, 0.75, 0.15], np.float32))
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
    """Clean breathing zoom 1.00 → 1.05 over each shot, back to 1.00 on the cut."""
    k = max(i for i, c in enumerate(CUTS[:-1]) if c <= t)
    s0, s1 = CUTS[k], CUTS[k + 1]
    sc = 1 + 0.05 * ease((t - s0) / (s1 - s0))
    ay = 0.32 * H if k in (0, 3) else 0.5 * H          # presenter shots keep the face in place
    M = np.float32([[sc, 0, W / 2 * (1 - sc)], [0, sc, ay * (1 - sc)]])
    return cv2.warpAffine(f, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)


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
        (at("ممكن"), at("أتربة"), at("بيتم") - 0.3,
         ("speaker", RED, "صوت بالبريك"), ("dust", RED, "أتربة وغبار")),
        (at("JLM"), at("Brake") + 0.1, at("العبوة"),        # gone before the clip's own price badge
         ("spray", YEL, "بريك كلينر"), ("disc_ok", YEL, "بريك نظيف")),
    ])
    tag, tag_t = product_tag(), (at("تنظيفه"), PRODUCT_SHOT[1] - 0.1)
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
        if t < SRC_DUR:
            raw = src.stdout.read(W * H * 3)
            if len(raw) == W * H * 3:
                last = np.frombuffer(raw, np.uint8).reshape(H, W, 3).astype(np.float32) / 255
        f = zoom(last, min(t, SRC_DUR - 1e-3)) if t < END_T + 0.4 else last * 0
        if t < END_T + 0.4:
            hook.draw(f, t)
            if tag_t[0] <= t < tag_t[1]:
                p = ease((t - tag_t[0]) / 0.25) * (1 - ease((t - tag_t[1] + 0.2) / 0.2))
                R.over(f, tag, (W - tag.shape[1]) / 2, 0.105 * H + 10 * (1 - p), p)
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
