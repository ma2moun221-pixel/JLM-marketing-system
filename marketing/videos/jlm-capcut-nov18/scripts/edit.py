"""JLM «مين ورا JLM في فلسطين؟» — CapCut-style edit of the client's 22 s team clip.

    python3 scripts/edit.py --out out/jlm_team_palestine.mp4 [--stills 0.9,2.5,...]

Style (brand/jlm/EDIT_STYLES.md): Clean + Kinetic, the client's usual look (as in Brake Cleaner), with
the accents the client picked: a Kinetic hook, Fast-Paced zooms and an animated jlmstore.com card.
- Pauses tightened: the voice-over runs 15.3 s instead of 21.7 s. The b-roll is re-cut on the
  music's beat grid, and the presenter shots stay lip-synced.
- Hook: «مين ورا» pops word by word, «JLM» slams in (impact, flash, light shake), «في فلسطين؟» with a
  map pin. The hook music drops on «JLM».
- CapCut-style transitions between shots: whip-slide with motion blur, zoom-in punch, light flash.
  A slow 1.00 → 1.05 zoom runs within each shot, with punch-ins on the key words.
- One-line karaoke captions (Helvetica Neue LT Arabic + Albert Sans) at 76.5 % height, below the can
  and the faces. A round line icon draws itself at the start of the caption for each idea
  (wrench, can, car, shop, cart, snowflake, bulb, tag, question).
- The jlmstore.com card pops with a cursor click on «jlmstore.com».
- End card over the blurred video: logo, «اطلبها الآن من خلال» jlmstore.com, «مع توفر خدمة التوصيل».
- Audio: cleaned voice; synthesised music (hook riser + drop, 120 BPM groove in A minor), side-chain
  ducked under the voice; soft whooshes and ticks. Final −14 LUFS.
"""
import argparse
import importlib.util
import math
import subprocess
import sys
import wave
from functools import lru_cache
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[2]
sys.path.insert(0, str(REPO / "marketing/videos/jlm-care-edit/scripts"))
import edit_v3 as V  # noqa: E402

spec = importlib.util.spec_from_file_location("fc_music", REPO / "marketing/videos/jlm-flying-car/scripts/music.py")
M = importlib.util.module_from_spec(spec)
spec.loader.exec_module(M)

E, R = V.E, V.R
W, H, FPS = 1080, 1920, 30
YEL, WHT, RED, GREY, CHA = V.YEL, V.WHT, V.RED, V.GREY, V.CHA
SIL = (192, 196, 199)
SRC = ROOT / "src/raw.mp4"
SRC_END = 21.70
ease = V.ease_io
back = V.back

# ---------------------------------------------------------------- the cut ---
# --mode full22 (default): the client's clip untouched, 1:1 (every shot, real speed), CTA as a bottom bar, 22.0 s
# --mode fullcard: the clip untouched + the usual CTA end card after it
# --mode tight: pauses removed, b-roll re-cut on the beat (first version, 18.5 s)
MODE = sys.argv[sys.argv.index("--mode") + 1] if "--mode" in sys.argv else "full22"
FULL = MODE != "tight"
# voice: source ranges kept (pauses removed) — played back to back
AUD = [(1.55, 3.70), (4.90, 10.12), (12.32, 15.56), (16.95, 21.60)]
AUD_OUT = list(np.cumsum([0] + [b - a for a, b in AUD]))           # 0, 2.15, 7.37, 10.61, 15.26
# picture: (out start, src start) — b-roll re-cut on the beat; last range lip-synced with the voice
VID = [(0.00, 1.55),   # presenter walks in (synced)
       (1.95, 3.52),   # diagnostics on the laptop
       (2.90, 4.70),   # checking the car
       (3.45, 5.58),   # car on the lift, oil drain
       (4.45, 6.80),   # mechanic under the bonnet
       (5.45, 8.30),   # mechanic at the engine
       (6.45, 9.85),   # pouring JLM into the engine
       (7.45, 11.50),  # JLM into the fuel tank
       (8.45, 13.40),  # the JLM stand
       (AUD_OUT[3], AUD[3][0])]   # shelves → presenter (synced)
SHOT_CUTS = [v[0] for v in VID] + [AUD_OUT[3] + (17.667 - AUD[3][0])]   # + the clip's own cut to the presenter
SHOT_CUTS = sorted(SHOT_CUTS)
PRESENTER = {0, len(SHOT_CUTS) - 1}                                     # shot indices with a face to keep
URL_END = VID[-1][0] - 0.02
if FULL:                                    # the clip as filmed: same picture and sound timeline
    AUD, AUD_OUT, VID = [(0.0, SRC_END)], [0.0], [(0.0, 0.0)]
    SHOT_CUTS = [0.0, 3.5, 4.5, 5.5, 6.633, 8.0, 9.733, 11.1, 13.267, 15.733, 17.667]   # the clip's own cuts
    PRESENTER = {0, 10}
    URL_END = 15.733 - 0.02
TRANS = {1: "zoom", 2: "whip", 3: "whip", 4: "flash", 5: "whip", 6: "zoom", 7: "whip", 8: "zoom", 9: "whip",
         10: "zoom"}
TW = 0.13                                                               # half-length of a transition

# speech (source time), Whisper turbo checked segment by segment
SEGMENTS = [
    (1.95, 3.62, "مين ورا JLM في فلسطين؟"),
    (4.98, 10.06, "ورا كل منتج JLM في فلسطين في ناس خبراء بالصيانة بيشتغلوا بالمنتجات والسيارات كل يوم"),
    (12.38, 15.50, "منتجات بتلاقيها بمراكزنا وعلى jlmstore.com"),
    (17.12, 21.28, "بهذا الشتاء سنكون معكم بالنصائح والعروض والأجوبة على كل استفساراتكم"),
]
# "#" = carried by the kinetic hook; "*" stays yellow (key idea)
PHRASES = [
    "#مين #ورا #JLM #في #فلسطين؟",
    "ورا كل منتج *JLM", "في فلسطين", "في ناس *خبراء *بالصيانة", "بيشتغلوا *بالمنتجات", "والسيارات *كل *يوم",
    "منتجات بتلاقيها *بمراكزنا", "وعلى *jlmstore.com",
    "*بهذا *الشتاء سنكون معكم", "*بالنصائح *والعروض", "*والأجوبة على كل استفساراتكم",
]
ICON_AT = {"خبراء": "wrench", "بالمنتجات": "can", "والسيارات": "car_ok", "بمراكزنا": "shop", "jlmstore.com": "cart",
           "الشتاء": "snow", "بالنصائح": "bulb", "والعروض": "tag", "والأجوبة": "chat"}
PUNCH_AT = ["خبراء", "بمراكزنا", "بالنصائح"]
CAP_Y = 0.765 * H


def src_to_out(t):
    for (a, b), o in zip(AUD, AUD_OUT):
        if a - 0.01 <= t <= b + 0.01:
            return o + t - a
    raise ValueError(t)


def word_times(weight):
    out = []
    for t0, t1, text in SEGMENTS:
        words = text.split()
        w = weight[int(t0 * 100):int(t1 * 100)] + 1e-3
        c = np.concatenate([[0], np.cumsum(w)]) / w.sum()
        lens = [len(x) + 1 for x in words]
        acc = np.concatenate([[0], np.cumsum(lens)]) / sum(lens)
        starts = [t0 + np.searchsorted(c, a) / 100 for a in acc[:-1]]
        out += [(src_to_out(s), src_to_out(e), wd) for s, e, wd in zip(starts, starts[1:] + [t1], words)]
    return out


SPEECH_END = src_to_out(SEGMENTS[-1][1])
CTA_T = None                                          # full22: CTA bar from the last sentence on
if MODE == "tight":
    END_T = SPEECH_END + 0.12                         # CTA card starts after «استفساراتكم»
    DUR = END_T + 3.4
elif MODE == "fullcard":
    END_T = SPEECH_END + 0.12
    DUR = END_T + 3.2
else:
    END_T, DUR, CTA_T = 99.0, 22.0, 19.45             # no end card: the CTA rides on the last shot


def cap_y(t0):
    """Caption height for a phrase starting at t0 (lifted above the CTA bar in full22)."""
    return 0.700 * H if CTA_T is not None and t0 >= CTA_T else CAP_Y


def is_ar(w):
    return any("؀" <= ch <= "ۿ" for ch in w)


@lru_cache(maxsize=None)
def mixed_line(runs, size, shadow=True, pad=26):
    """Arabic words in Helvetica Neue LT Arabic Bold, Latin words in Albert Sans (RTL order)."""
    fa = E.T.font(size, True)
    fl = R.albert(int(size * 0.92), 800)
    words = list(runs)
    space = fa.getlength(" ", direction="rtl") * 1.05
    advs = [(fa.getlength(w, direction="rtl") if is_ar(w) else fl.getlength(w)) for w, _ in words]
    asc, desc = fa.getmetrics()
    dy_l = asc - fl.getmetrics()[0]
    lw = int(sum(advs) + space * (len(words) - 1)) + 2 * pad
    img = Image.new("RGBA", (lw, asc + desc + 2 * pad), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    x = lw - pad
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


# ------------------------------------------------------------- new icons ---
def _can():
    body = V._rrect(-0.40, -0.36, 0.40, 0.82, 0.08)
    neck = np.array([[-0.40, -0.30], [-0.18, -0.56], [0.18, -0.56], [0.40, -0.30]])
    cap = V._rrect(-0.15, -0.82, 0.15, -0.56, 0.04)
    band = np.array([[-0.40, 0.10], [0.40, 0.10]])
    drop = np.concatenate([[[0, 0.22]], V._arc(0, 0.50, 0.14, 0.14, -40, 220, 20), [[0, 0.22]]])
    return [body, neck, cap, band, drop]


def _shop():
    awning = np.array([[-0.82, -0.22], [-0.62, -0.62], [0.62, -0.62], [0.82, -0.22], [-0.82, -0.22]])
    scallops = [V._arc(x, -0.22, 0.164, 0.14, 0, 180, 12) for x in (-0.656, -0.328, 0.0, 0.328, 0.656)]
    body = np.array([[-0.68, -0.08], [-0.68, 0.74], [0.68, 0.74], [0.68, -0.08]])
    door = np.array([[-0.18, 0.74], [-0.18, 0.26], [0.18, 0.26], [0.18, 0.74]])
    return [awning] + scallops + [body, door]


def _cart():
    basket = np.array([[-0.92, -0.62], [-0.64, -0.62], [-0.44, 0.30], [0.56, 0.30], [0.78, -0.36], [-0.54, -0.36]])
    return [basket, V._arc(-0.30, 0.58, 0.12, 0.12, 0, 360, 20), V._arc(0.44, 0.58, 0.12, 0.12, 0, 360, 20)]


def _snow():
    s = []
    for a in (90, 30, 150):
        r = math.radians(a)
        d = np.array([math.cos(r), math.sin(r)])
        s.append(np.array([-0.82 * d, 0.82 * d]))
        for sign in (1, -1):
            p = 0.52 * d * sign
            for b in (35, -35):
                rb = math.radians(a + (180 if sign < 0 else 0) + 180 + b)
                s.append(np.array([p, p + 0.26 * np.array([math.cos(rb), math.sin(rb)])]))
    return s


def _bulb():
    glass = np.concatenate([[[-0.22, 0.38]], V._arc(0, -0.18, 0.46, 0.46, 125, 415, 50), [[0.22, 0.38]]])
    base = [np.array([[-0.22, 0.38], [0.22, 0.38]]), np.array([[-0.20, 0.54], [0.20, 0.54]]),
            np.array([[-0.12, 0.70], [0.12, 0.70]])]
    rays = [np.array([[0.70, -0.62], [0.86, -0.76]]), np.array([[-0.70, -0.62], [-0.86, -0.76]]),
            np.array([[0, -0.84], [0, -0.98]])]
    return [glass] + base + rays


def _tag():
    tag = np.array([[-0.84, 0.0], [-0.10, -0.74], [0.74, -0.74], [0.74, 0.10], [0.0, 0.84], [-0.84, 0.0]])
    hole = V._arc(0.42, -0.42, 0.11, 0.11, 0, 360, 20)
    pct = [np.array([[-0.30, 0.34], [0.22, -0.18]]), V._arc(-0.22, -0.06, 0.08, 0.08, 0, 360, 16),
           V._arc(0.14, 0.26, 0.08, 0.08, 0, 360, 16)]
    return [tag, hole] + pct


def _chat():
    bubble = V._rrect(-0.84, -0.66, 0.84, 0.38, 0.22)
    tail = np.array([[-0.44, 0.38], [-0.60, 0.76], [-0.08, 0.38]])
    q = np.concatenate([V._arc(0, -0.28, 0.17, 0.17, 180, 400, 24), [[0.0, -0.02], [0.0, 0.06]]])
    dot = V._arc(0, 0.20, 0.035, 0.035, 0, 360, 10)
    return [bubble, tail, q, dot]


def _pin():
    arc = V._arc(0, -0.22, 0.50, 0.50, 140, 400, 50)
    return [np.concatenate([[[0, 0.84]], arc, [[0, 0.84]]]), V._arc(0, -0.22, 0.17, 0.17, 0, 360, 24)]


V.ICONS.update({"can": _can, "shop": _shop, "cart": _cart, "snow": _snow, "bulb": _bulb, "tag": _tag, "chat": _chat,
                "pin": _pin})


def glyph(icon, size, p, color=YEL, stroke=5.5):
    """A line icon drawing itself (no disc), with a soft glow — premultiplied RGBA."""
    ss = 3
    s = int(size * 1.25)
    c = np.zeros((s * ss, s * ss), np.float32)
    sc = size * 0.46 * ss
    for st in V.partial_strokes(V.ICONS[icon](), p):
        pts = np.round((st * sc + s * ss / 2) * 4).astype(np.int32)
        cv2.polylines(c, [pts], False, 1.0, int(stroke * ss), cv2.LINE_AA, shift=2)
    c = cv2.resize(c, (s, s), interpolation=cv2.INTER_AREA)
    g = cv2.GaussianBlur(c, (0, 0), 6) * 0.7
    a = np.clip(c + g, 0, 1)
    col = np.array(color, np.float32) / 255
    return np.dstack([a[..., None] * col, a]).astype(np.float32)


def with_shadow(lay, blur=10, strength=0.55, dy=6):
    pad = blur * 3
    out = np.zeros((lay.shape[0] + 2 * pad, lay.shape[1] + 2 * pad, 4), np.float32)
    sh = cv2.GaussianBlur(np.pad(lay[..., 3], pad), (0, 0), blur) * strength
    out[..., 3] = np.roll(sh, dy, axis=0)
    R.paste_into(out, lay, pad, pad)
    return out


def logo_layer(width):
    """logo_on_dark.png without the file's faint background box; no drop shadow (it reads as a box)."""
    im = np.array(Image.open(E.KIT / "logos/logo_on_dark.png").convert("RGBA"))
    a = im[..., 3]
    keep = cv2.dilate((a > 128).astype(np.uint8), np.ones((5, 5), np.uint8))
    im[..., 3] = a * keep
    im[:4], im[-4:], im[:, :4], im[:, -4:] = 0, 0, 0, 0
    im = Image.fromarray(im).resize((width, int(im.shape[0] * width / im.shape[1])), Image.LANCZOS)
    return R.to_premul(np.array(im))


# --------------------------------------------------------------- captions ---
class Captions:
    BADGE_SC = 0.60

    def __init__(self, words):
        self.phrases, k = [], 0
        for ph in PHRASES:
            hidden = ph.startswith("#")
            items = []
            for tok in ph.split():
                tok = tok.lstrip("#")
                tone = "*" if tok.startswith("*") else ""
                s, e, wd = words[k]
                assert wd == tok.lstrip("*"), (wd, tok)
                items.append((wd, tone, s, e))
                k += 1
            icons = [(s, ICON_AT[wd]) for wd, _, s, _ in items if wd in ICON_AT]
            self.phrases.append({"items": items, "hidden": hidden, "icons": icons})
        assert k == len(words), (k, len(words))
        for i, p in enumerate(self.phrases):
            p["t0"] = p["items"][0][2]
            nxt = self.phrases[i + 1]["items"][0][2] if i + 1 < len(self.phrases) else min(END_T, DUR)
            p["t1"] = min(nxt, p["items"][-1][3] + (0.7 if i + 1 == len(PHRASES) and CTA_T else 0.45))
        self.all = [(wd, s, e) for p in self.phrases for wd, _, s, e in p["items"]]

    def at(self, word, nth=0):
        return [s for wd, s, _ in self.all if wd == word][nth]

    @staticmethod
    @lru_cache(maxsize=None)
    def layer(key):
        items, active = key
        runs = []
        for i, (wd, tone) in enumerate(items):
            col = GREY if i > active else YEL if (tone == "*" or i == active) else WHT
            runs.append((wd, col))
        txt = mixed_line(tuple(runs), 64)
        box = V.soft_box(txt.shape[1] - 18, txt.shape[0] - 30, alpha=0.66)
        out = np.zeros((max(box.shape[0], txt.shape[0]), max(box.shape[1], txt.shape[1]), 4), np.float32)
        R.paste_into(out, box, (out.shape[1] - box.shape[1]) // 2, (out.shape[0] - box.shape[0]) // 2)
        R.paste_into(out, txt, (out.shape[1] - txt.shape[1]) // 2, (out.shape[0] - txt.shape[0]) // 2)
        return out

    def draw(self, f, t):
        for p in self.phrases:
            if p["hidden"] or not (p["t0"] <= t < p["t1"]):
                continue
            active = max(i for i, it in enumerate(p["items"]) if it[2] <= t)
            lay = self.layer((tuple((wd, tone) for wd, tone, _, _ in p["items"]), active))
            fade = min(1.0, (t - p["t0"]) / 0.08) * min(1.0, (p["t1"] - t) / 0.08)
            pop = 0.9 + 0.1 * back(min(1.0, (t - p["t0"]) / 0.18))
            cy = cap_y(p["t0"])
            l2, lx, ly = R.warp_premul(lay, pop, W / 2, cy, (lay.shape[1] / 2, lay.shape[0] / 2))
            R.over(f, l2, lx, ly, fade)


# ------------------------------------------------------------ icon rows ---
# Icons for one idea gather in a row (right-aligned, RTL order) above the caption: each pops in on its word,
# draws itself in ≈ 0.55 s and stays until the idea is over (≥ 2 s on screen), then the row leaves together.
ICON_GROUPS = [["خبراء", "بالمنتجات", "والسيارات"],
               ["بمراكزنا", "jlmstore.com"],
               ["الشتاء", "بالنصائح", "والعروض", "والأجوبة"]]


class IconRows:
    SC = 0.66                                   # badge ≈ 130 px
    GAP = 14
    SPEED = 1.6                                 # draw-on 1.6× faster than the stock badge

    def __init__(self, caps):
        self.rows = []
        for gi, words in enumerate(ICON_GROUPS):
            items = [(caps.at(w), ICON_AT[w]) for w in words]
            last_end = [e for wd, s, e in caps.all if wd == words[-1]][0]
            if gi + 1 < len(ICON_GROUPS):
                nxt = caps.at(ICON_GROUPS[gi + 1][0])
                t_end = min(nxt - 0.3, max(last_end + 1.3, items[-1][0] + 2.0))
            else:
                t_end = min(END_T, DUR) + 0.3
            self.rows.append((items, t_end))

    def row_y(self, t):
        y = CAP_Y - 0.095 * H
        if CTA_T is not None:
            y -= (CAP_Y - cap_y(CTA_T)) * ease((t - CTA_T + 0.05) / 0.3)
        return y

    def draw(self, f, t):
        d = V.BADGE * self.SC
        for items, t_end in self.rows:
            if not (items[0][0] <= t < t_end + 0.3):
                continue
            out = 1 - ease((t - t_end) / 0.25)
            y = self.row_y(t)
            for k, (ts, ic) in enumerate(items):
                lt = t - ts
                if lt < 0:
                    continue
                cx = W - 64 - d / 2 - k * (d + self.GAP)
                bl = V.badge_layer(ic, YEL, lt * self.SPEED)
                sc = (0.35 + 0.65 * back(lt / 0.3)) * self.SC * (0.85 + 0.15 * out)
                l3, x3, y3 = R.warp_premul(bl, sc, cx, y, (bl.shape[1] / 2, bl.shape[0] / 2))
                R.over(f, l3, x3, y3, min(1.0, lt / 0.08) * out)


# ------------------------------------------------------------ kinetic hook ---
class Hook:
    """«مين» «ورا» pop → «JLM» slams in (flash, shake) → «في فلسطين؟» with a map pin drawing itself."""

    def __init__(self, caps):
        self.t_w = [caps.at("مين"), caps.at("ورا")]
        self.t_jlm = caps.at("JLM")
        self.t_low = caps.at("في")
        self.t_out = SHOT_CUTS[1] + 0.3 if FULL else caps.at("ورا", 1) - 0.18
        self.words = [E.T.line([(w, WHT)], 86, bold=True, shadow=True, pad=18) for w in ("مين", "ورا")]
        self.jlm = with_shadow(R.latin_layer("JLM", 250, YEL, 900, 0.02), 14, 0.6, 8)
        self.low = E.T.line([("في", WHT), ("فلسطين؟", WHT)], 80, bold=True, shadow=True, pad=16)
        yy = np.arange(H, dtype=np.float32)[:, None, None]
        self.band = (0.62 * np.exp(-((yy - 0.75 * H) / (0.15 * H)) ** 2)).astype(np.float32)

    def land(self):
        return self.t_jlm + 0.10

    def draw(self, f, t):
        if not (0 <= t < self.t_out + 0.25):
            return
        out = 1 - ease((t - self.t_out) / 0.25)
        f *= 1 - self.band * min(1.0, t / 0.2) * out
        gap = 18
        ws = [x.shape[1] - 36 for x in self.words]
        x = (W + sum(ws) + gap) / 2
        for ts, lay, w in zip(self.t_w, self.words, ws):
            if t >= ts:
                q = back((t - ts) / 0.22)
                l2, lx, ly = R.warp_premul(lay, 0.7 + 0.3 * min(q, 1.1), x - w / 2, 0.655 * H,
                                           (lay.shape[1] / 2, lay.shape[0] / 2))
                R.over(f, l2, lx, ly, min(1.0, (t - ts) / 0.08) * out)
            x -= w + gap
        lt = t - self.t_jlm
        if lt >= 0:
            q = min(1.0, lt / 0.10)
            sc = 1.9 - 0.9 * ease(q) if lt < 0.10 else 1.0 + 0.06 * math.exp(-(lt - 0.10) * 9) * math.cos((lt - 0.10) * 30)
            l2, lx, ly = R.warp_premul(self.jlm, sc, W / 2, 0.748 * H, (self.jlm.shape[1] / 2, self.jlm.shape[0] / 2))
            R.over(f, l2, lx, ly, min(1.0, lt / 0.05) * out)
        lt = t - self.t_low
        if lt >= 0:
            q = ease(lt / 0.25)
            pin = glyph("pin", 74, ease((lt - 0.1) / 0.5))
            row = self.low.shape[1] - 32 + pin.shape[1]
            x0 = (W - row) / 2
            y = 0.838 * H + 20 * (1 - q)
            R.over(f, pin, x0, y - pin.shape[0] / 2, q * out)
            R.over(f, self.low, x0 + pin.shape[1] - 16, y - self.low.shape[0] / 2, q * out)


# ----------------------------------------------------------- jlmstore card ---
class UrlCard:
    """jlmstore.com pill pops in, a cursor glides in and clicks (ripple + sheen)."""

    def __init__(self, t0, t1):
        self.t0, self.t1 = t0, t1
        self.pill = with_shadow(self.url_pill(66), 12, 0.5, 8)
        cur = np.zeros((90, 70, 4), np.uint8)
        poly = np.array([[6, 4], [6, 70], [22, 55], [34, 82], [46, 77], [34, 51], [56, 51]], np.int32)
        cv2.fillPoly(cur, [poly], (241, 240, 236, 255), cv2.LINE_AA)
        cv2.polylines(cur, [poly], True, (20, 20, 22, 255), 3, cv2.LINE_AA)
        self.cursor = R.to_premul(cur)

    @staticmethod
    def url_pill(size):
        """Yellow pill: cart icon + jlmstore.com (charcoal)."""
        txt = R.latin_layer("jlmstore.com", size, CHA, 800, 0.01)
        cart = glyph("cart", int(size * 0.9), 1.0, CHA, 6.5)
        h = int(size * 1.65)
        w = txt.shape[1] + cart.shape[1] + int(size * 0.55)
        s = 3
        img = np.zeros((h * s, w * s, 4), np.uint8)
        r = h * s // 2
        cv2.rectangle(img, (r, 0), (w * s - r, h * s), YEL + (255,), -1)
        cv2.circle(img, (r, r), r, YEL + (255,), -1, cv2.LINE_AA)
        cv2.circle(img, (w * s - r, r), r, YEL + (255,), -1, cv2.LINE_AA)
        pill = R.to_premul(cv2.resize(img, (w, h), interpolation=cv2.INTER_AREA))
        x0 = int(size * 0.28)
        R.paste_into(pill, cart, x0, (h - cart.shape[0]) // 2 + 2)
        R.paste_into(pill, txt, x0 + cart.shape[1] - int(size * 0.12), (h - txt.shape[0]) // 2)
        return pill

    def draw(self, f, t):
        if not (self.t0 <= t < self.t1):
            return
        lt = t - self.t0
        out = 1 - ease((t - self.t1 + 0.2) / 0.2)
        q = back(lt / 0.32, 1.6)
        click = lt - 0.62
        press = 1 - 0.06 * math.exp(-((click - 0.06) / 0.06) ** 2) if click > 0 else 1.0
        pill = self.pill.copy()
        sp = (lt - 0.75) / 0.6
        if 0 < sp < 1:
            xs = np.arange(pill.shape[1], dtype=np.float32)
            band = np.exp(-((xs - (-80 + (pill.shape[1] + 160) * ease(sp))) / 40) ** 2)[None, :, None]
            pill[..., :3] += band * pill[..., 3:4] * 0.4
        cy = 0.60 * H
        lay, x, y = R.warp_premul(pill, (0.5 + 0.5 * q) * press, W / 2, cy, (pill.shape[1] / 2, pill.shape[0] / 2))
        R.over(f, lay, x, y, min(1.0, lt / 0.08) * out)
        if click > -0.35:                                               # cursor glides in, clicks
            u = ease((click + 0.35) / 0.35)
            px, py = W / 2 + 150 + 260 * (1 - u), cy + 30 + 220 * (1 - u)
            R.over(f, self.cursor, px, py, min(1.0, (click + 0.35) / 0.1) * out)
        if click > 0:                                                   # ripple
            ph = click / 0.45
            if ph < 1:
                ring = np.zeros((300, 300), np.float32)
                cv2.circle(ring, (150, 150), int(20 + 110 * ease(ph)), 1.0, 5, cv2.LINE_AA)
                ring = cv2.GaussianBlur(ring, (0, 0), 1.2) * (1 - ph) * out
                lay = np.dstack([ring[..., None] * (np.array(YEL, np.float32) / 255), ring])
                R.over(f, lay, W / 2 + 150 - 150, cy + 30 - 150)


# ---------------------------------------------------------------- end card ---
class EndCard:
    """CTA over the defocused, darkened video: logo, «Driving your journey», «اطلبها الآن من خلال»,
    jlmstore.com pill with a sheen, «مع توفر خدمة التوصيل» with the truck drawing itself."""

    def __init__(self, t0):
        self.t0 = t0
        self.logo = logo_layer(430)
        self.tag = R.latin_layer("Driving your journey", 52, SIL, 600, 0.02)
        self.cta = E.T.line([("اطلبها الآن", YEL), ("من خلال", WHT)], 76, bold=True, shadow=False, pad=10)
        self.pill = V.url_pill(70)
        self.deliv = E.T.line([("مع توفر", WHT), ("خدمة التوصيل", YEL)], 54, bold=True, shadow=False, pad=8)
        self.tr = V.EndCard(t0)
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        self.vign = (0.05 * np.exp(-(((xx - W / 2) / 520) ** 2 + ((yy - 0.42 * H) / 700) ** 2)))[..., None]

    def draw(self, f, t):
        b = ease((t - self.t0) / 0.35)
        if b <= 0:
            return
        small = cv2.resize(f, (W // 6, H // 6), interpolation=cv2.INTER_AREA)
        bg = cv2.resize(cv2.GaussianBlur(small, (0, 0), 1 + 4 * b), (W, H), interpolation=cv2.INTER_CUBIC)
        bg = bg * (1 - 0.62 * b) + self.vign * np.array([1.0, 0.75, 0.15], np.float32) * b
        f[:] = f * (1 - b) + bg * b
        t0 = self.t0 + 0.15
        q = ease((t - t0) / 0.45)
        R.over(f, self.logo, (W - self.logo.shape[1]) / 2, 0.20 * H - self.logo.shape[0] / 2 + 14 * (1 - q), q)
        q = ease((t - t0 - 0.35) / 0.4)
        R.over(f, self.tag, (W - self.tag.shape[1]) / 2, 0.315 * H - self.tag.shape[0] / 2 + 12 * (1 - q), q)
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


class CtaBar:
    """full22: the usual CTA as a bottom bar on the last shot — «اطلبها الآن من خلال» + jlmstore.com pill,
    then «مع توفر خدمة التوصيل» with the truck drawing itself, on a soft dark box (kept above the Reels UI)."""

    def __init__(self, t0):
        self.t0 = t0
        self.cta = E.T.line([("اطلبها الآن", YEL), ("من خلال", WHT)], 52, bold=True, shadow=False, pad=8)
        self.pill = V.url_pill(50)
        self.deliv = E.T.line([("مع توفر", WHT), ("خدمة التوصيل", YEL)], 42, bold=True, shadow=False, pad=6)
        self.tr = V.EndCard(t0)
        self.row1 = self.cta.shape[1] + 14 + self.pill.shape[1]
        self.box = V.soft_box(self.row1 + 40, 190, alpha=0.70)

    def draw(self, f, t):
        lt = t - self.t0
        if lt < 0:
            return
        q = ease(lt / 0.3)
        y1, y2 = 0.808 * H, 0.858 * H
        R.over(f, self.box, (W - self.box.shape[1]) / 2, (y1 + y2) / 2 - self.box.shape[0] / 2 + 6, q)
        x0 = (W - self.row1) / 2
        q1 = ease((lt - 0.1) / 0.3)
        R.over(f, self.cta, x0 + self.pill.shape[1] + 14, y1 - self.cta.shape[0] / 2 + 14 * (1 - q1), q1)
        q2 = back((lt - 0.3) / 0.35, 1.2)
        if q2 > 0:
            pill = self.pill.copy()
            sp = (lt - 0.8) / 0.6
            if 0 < sp < 1:
                xs = np.arange(pill.shape[1], dtype=np.float32)
                band = np.exp(-((xs - (-80 + (pill.shape[1] + 160) * ease(sp))) / 40) ** 2)[None, :, None]
                pill[..., :3] += band * pill[..., 3:4] * 0.45
            lay, x, y = R.warp_premul(pill, 0.6 + 0.4 * q2, x0 + self.pill.shape[1] / 2, y1,
                                      (pill.shape[1] / 2, pill.shape[0] / 2))
            R.over(f, lay, x, y, min(1.0, q2))
        q3 = ease((lt - 0.55) / 0.3)
        if q3 > 0:
            tr = self.tr.truck(ease((lt - 0.55) / 0.8), 100)
            row = self.deliv.shape[1] + tr.shape[1]
            xr = (W - row) / 2
            R.over(f, tr, xr, y2 - tr.shape[0] / 2, q3)
            R.over(f, self.deliv, xr + tr.shape[1], y2 - self.deliv.shape[0] / 2 + 3, q3)


# ---------------------------------------------------------------- picture ---
class Source:
    """Sequential reader per picture range (ffmpeg seeks to the range start)."""

    def __init__(self):
        self.k, self.proc, self.n, self.last = None, None, 0, None

    def frame(self, t):
        k = max(i for i, (o, _) in enumerate(VID) if o <= t + 1e-6)
        o, s = VID[k]
        if k != self.k:
            if self.proc:
                self.proc.kill()
            end = VID[k + 1][0] if k + 1 < len(VID) else DUR
            self.proc = subprocess.Popen(
                ["ffmpeg", "-v", "error", "-ss", f"{s:.3f}", "-i", str(SRC), "-t", f"{end - o + 0.2:.3f}", "-vf",
                 f"fps={FPS},scale={W}:{H}:flags=lanczos,eq=contrast=1.05:saturation=1.08", "-f", "rawvideo",
                 "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
            self.k, self.n = k, 0
        want = int(round((t - o) * FPS))
        while self.n <= want:
            raw = self.proc.stdout.read(W * H * 3)
            if len(raw) < W * H * 3:
                break                                   # past the end of the clip: hold the last frame
            self.last = np.frombuffer(raw, np.uint8).reshape(H, W, 3).astype(np.float32) / 255
            self.n += 1
        return self.last.copy()


def bumps(t, times, amp=0.07):
    s = 0.0
    for tp in times:
        d = t - tp
        if d > 0:
            s += amp * min(1.0, d / 0.10) * math.exp(-max(0.0, d - 0.10) / 0.5)
    return s


def camera(f, t, punch_times, shake_t):
    k = max(i for i, c in enumerate(SHOT_CUTS) if c <= t + 1e-6)
    s0 = SHOT_CUTS[k]
    s1 = SHOT_CUTS[k + 1] if k + 1 < len(SHOT_CUTS) else DUR
    sc = 1 + 0.05 * ease((t - s0) / (s1 - s0)) + bumps(t, punch_times)
    ay = 0.32 * H if k in PRESENTER else 0.5 * H
    dx = dy = 0.0
    blur, zblur, flash = 0, 0.0, 0.0
    # transition around the nearest cut
    for i, c in enumerate(SHOT_CUTS):
        d = (t - c) / TW
        if i == 0 or not (-1 <= d < 1) or i not in TRANS:
            continue
        kind, p = TRANS[i], 1 - abs(d)
        if kind == "whip":
            dx = -0.42 * W * ease(1 + d) ** 2 if d < 0 else 0.42 * W * (1 - ease(d)) ** 2
            blur = int(150 * p)
        elif kind == "zoom":
            sc *= 1 + 0.30 * (ease(1 + d) ** 2 if d < 0 else (1 - ease(d)) ** 2)
            zblur = p
        elif kind == "flash":
            flash = p ** 2 * 0.85
    lt = t - shake_t
    if 0 < lt < 0.45:
        a = 14 * math.exp(-lt * 9)
        dx += a * math.sin(lt * 95)
        dy += a * math.cos(lt * 77)
    Mx = np.float32([[sc, 0, W / 2 * (1 - sc) + dx], [0, sc, ay * (1 - sc) + dy]])
    g = cv2.warpAffine(f, Mx, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    if zblur > 0.05:
        acc = g.copy()
        for j in (1, 2, 3):
            s2 = sc * (1 + 0.025 * j * zblur)
            M2 = np.float32([[s2, 0, W / 2 * (1 - s2) + dx], [0, s2, ay * (1 - s2) + dy]])
            acc += cv2.warpAffine(f, M2, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        g = acc / 4
    if blur > 2:
        g = cv2.blur(g, (blur, 1))
    if flash > 0:
        g = g + (1 - g) * flash
    return g


# ------------------------------------------------------------------ audio ---
def voice_track(path):
    parts, labels = [], []
    for i, (a, b) in enumerate(AUD):
        d = b - a
        parts.append(f"[0:a]atrim={a}:{b},asetpts=PTS-STARTPTS,afade=t=in:d=0.015,afade=t=out:st={d - 0.015:.3f}:d=0.015[a{i}];")
        labels.append(f"[a{i}]")
    graph = ("".join(parts) + "".join(labels) + f"concat=n={len(AUD)}:v=0:a=1,highpass=f=90,afftdn=nr=10:nf=-32,"
             f"equalizer=f=3000:t=q:w=1:g=2,aresample=48000,apad=whole_dur={DUR:.3f}[a]")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(SRC), "-filter_complex", graph, "-map", "[a]",
                    "-ac", "1", "-c:a", "pcm_f32le", str(path)], check=True)
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-f", "f32le", "-ac", "1", "-ar", "48000", "-"],
                         capture_output=True, check=True).stdout
    x = np.frombuffer(raw, np.float32).copy()
    n = int(DUR * 48000)
    return np.pad(x, (0, max(0, n - len(x))))[:n]


def whoosh(sr, dur=0.34):
    n = int(dur * sr)
    t = np.arange(n) / sr
    x = M.noise(n)
    env = np.sin(np.pi * np.clip(t / dur, 0, 1)) ** 2.5
    # band-pass whose centre sweeps up then down
    out = np.zeros(n)
    blk = int(0.01 * sr)
    for i in range(0, n, blk):
        u = i / n
        fc = 500 + 2600 * math.sin(math.pi * u)
        out[i:i + blk] = M.filt(x[i:i + blk + 400], "band", (fc * 0.6, fc * 1.6))[:len(out[i:i + blk])]
    return out * env * 0.05


def music(t_drop, end_t, dur):
    sr = M.SR
    n = int(dur * sr)
    buf = np.zeros((n, 2))
    add = M.add
    beat = 0.5
    AM, F, C, G = (57, 60, 64), (53, 57, 60), (60, 64, 67), (55, 59, 62)
    prog = [(AM, 45), (F, 41), (C, 48), (G, 43)]

    def grid(t0, t1, step):
        k0 = math.ceil((t0 - t_drop) / step - 1e-6)
        t = t_drop + k0 * step
        while t < t1 - 1e-6:
            yield t
            t += step

    # hook: low boom at 0, riser into the drop on «JLM»
    add(buf, M.thump(), 0.0, 0.6)
    add(buf, M.pad(AM, t_drop + 0.2, 500, 1800), 0.0, 0.5)
    add(buf, M.riser(t_drop), 0.0, 0.7)
    # pre-drop build (the walk-in before the first words): plucked arpeggio + hats, rising
    for i, tt in enumerate(grid(0.0, t_drop - 0.01, beat / 2)):
        g = 0.18 + 0.22 * tt / t_drop
        add(buf, M.pluck(AM[[0, 1, 2, 1][i % 4]] + 12), tt, g, pan=0.3 if i % 2 else -0.3)
        add(buf, M.hat(), tt, 0.10 + 0.08 * tt / t_drop, pan=0.2)
    for tt in grid(0.0, t_drop - 0.01, beat):
        add(buf, M.kick(), tt, 0.25 + 0.2 * tt / t_drop)
    add(buf, M.impact(), t_drop, 0.75)
    riff = [(0, 76, 1), (1, 74, 0.5), (1.5, 72, 0.5), (2, 69, 1), (3, 72, 1), (4, 76, 1), (5, 79, 0.5), (5.5, 77, 0.5),
            (6, 76, 2)]
    for bt, m, ln in riff:
        add(buf, M.lead(m, ln), t_drop + bt * beat, 0.42, pan=0.1)
    # groove (bar = 2 s, chord per bar)
    groove_end = dur - 0.9                    # the groove carries on under the end card
    for b, t in enumerate(grid(t_drop, groove_end, 2.0)):
        ch, root = prog[b % 4]
        add(buf, M.pad(ch, 2.2, 1300), t, 0.55)
        for i, tt in enumerate(grid(t, min(t + 2.0, groove_end), beat / 2)):
            add(buf, M.bass(root, beat / 2 * 0.8), tt, 0.5)
            add(buf, M.pluck(ch[[0, 1, 2, 1, 2, 1][i % 6]] + 12), tt, 0.3, pan=0.35 if i % 2 else -0.35)
    for t in grid(t_drop, groove_end, beat):
        k = int(round((t - t_drop) / beat))
        add(buf, M.kick(), t, 0.6)
        if k % 2 == 1:
            add(buf, M.clap(), t, 0.32)
    for t in grid(t_drop, groove_end, beat / 2):
        add(buf, M.hat(), t + 0.0, 0.18, pan=0.2)
    # end card: riser → impact, the hook riff returns and rings out
    add(buf, M.riser(1.0), end_t - 1.0, 0.35)
    add(buf, M.impact(), end_t + 0.05, 0.55)
    add(buf, M.pad(AM, dur - end_t, 2200, 900), end_t + 0.05, 0.7)
    for bt, m, ln in riff:
        if end_t + 0.3 + bt * beat < dur - 0.6:
            add(buf, M.lead(m, ln), end_t + 0.3 + bt * beat, 0.42, pan=0.1)
    irL, irR = M.reverb_ir(1.6, 0.45)
    from scipy.signal import fftconvolve
    wet = np.stack([fftconvolve(buf[:, 0], irL)[:n], fftconvolve(buf[:, 1], irR)[:n]], 1)
    buf = buf * 0.85 + wet * 0.28
    t = np.arange(n) / sr
    buf *= np.clip((dur - t) / 1.2, 0, 1)[:, None]
    return buf / np.max(np.abs(buf))


def mix(path, voice, t_drop, end_t, ticks, whooshes):
    sr = 48000
    n = len(voice)
    mus = music(t_drop, end_t, n / sr)
    # side-chain: the music dips ≈ 11 dB under the voice, recovers in 0.3 s
    hop = 480
    m = len(voice) // hop
    env = np.sqrt((voice[: m * hop].reshape(m, hop) ** 2).mean(1))
    env = np.clip(env / (np.percentile(env, 90) + 1e-9), 0, 1)
    sm = np.zeros_like(env)
    for i in range(1, m):
        a = 0.5 if env[i] > sm[i - 1] else 0.035
        sm[i] = sm[i - 1] + a * (env[i] - sm[i - 1])
    duck = np.repeat(1 - 0.72 * np.clip(sm * 1.4, 0, 1), hop)
    duck = np.pad(duck, (0, n - len(duck)), mode="edge")
    out = np.zeros((n, 2))
    vpk = np.max(np.abs(voice)) + 1e-9
    out += (voice / vpk * 0.8)[:, None]
    tt = np.arange(n) / sr
    lift = 1 + 0.9 * np.clip((tt - end_t) / 0.3, 0, 1) + 1.2 * (tt < t_drop)   # music forward on the hook and the CTA
    out += mus * 0.55 * (duck * lift)[:, None]

    def place(sig, at, gain=1.0):
        i = int(at * sr)
        if i < 0:
            sig, i = sig[-i:], 0
        k = min(len(sig), n - i)
        if k <= 0:
            return
        out[i:i + k] += (sig[:k] * gain)[:, None]

    for at, f0 in ticks:
        place(V.soft_tick(sr, f0, 0.02), at)
    for at in whooshes:
        place(whoosh(sr), at - 0.17)
    pcm = (np.clip(out * 0.9, -1, 1) * 32767).astype(np.int16)
    with wave.open(str(path), "wb") as wv:
        wv.setnchannels(2)
        wv.setsampwidth(2)
        wv.setframerate(sr)
        wv.writeframes(pcm.tobytes())


# -------------------------------------------------------------------- main ---
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--stills")
    ap.add_argument("--mode", choices=["full22", "fullcard", "tight"], default="full22")
    a = ap.parse_args()
    out = ROOT / a.out
    out.parent.mkdir(parents=True, exist_ok=True)

    caps = Captions(word_times(V.voiced_weight(str(SRC))))
    for wd, s, e in caps.all:
        print(f"{s:5.2f}-{e:5.2f} {wd}")
    print("END_T", round(END_T, 2), "DUR", round(DUR, 2), "cuts", [round(c, 2) for c in SHOT_CUTS])
    hook = Hook(caps)
    url = UrlCard(caps.at("jlmstore.com"), URL_END)
    icons = IconRows(caps)
    for items, te in icons.rows:
        print("icons", [(round(s, 2), ic) for s, ic in items], "until", round(te, 2))
    bar = CtaBar(CTA_T) if CTA_T is not None else None
    logo = logo_layer(200)
    end = EndCard(END_T)
    punch = [hook.land()] + [caps.at(w) for w in PUNCH_AT]

    want, n_frames = None, int(round(DUR * FPS))
    if a.stills:
        want = {int(round(float(s) * FPS)) for s in a.stills.split(",")}
    tmp_v = out.with_name(out.stem + "_video_tmp.mp4")
    enc = None
    if want is None:
        enc = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                                "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "slow",
                                "-crf", "19", "-maxrate", "12M", "-bufsize", "24M", "-pix_fmt", "yuv420p", str(tmp_v)],
                               stdin=subprocess.PIPE)
    srcr = Source()
    for nf in range(n_frames):
        t = nf / FPS
        if want is not None and nf not in want:
            continue
        f = camera(srcr.frame(t), t, punch, hook.land())
        lt = t - hook.land()                                    # flash on the «JLM» slam
        if 0 <= lt < 0.2:
            f += (1 - f) * 0.45 * (1 - lt / 0.2) ** 2
        if t < END_T + 0.4:
            hook.draw(f, t)
            caps.draw(f, t)
            icons.draw(f, t)
            url.draw(f, t)
            if bar:
                bar.draw(f, t)
            R.over(f, logo, 40, 100, ease((t - 0.2) / 0.4))
        end.draw(f, t)
        img = (np.clip(f, 0, 1) * 255 + 0.5).astype(np.uint8)
        if want is not None:
            cv2.imwrite(str(out.parent / f"still_{t:05.2f}.png"), cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
            continue
        enc.stdin.write(img.tobytes())
    if enc is None:
        return
    enc.stdin.close()
    enc.wait()

    vtmp = out.with_name(out.stem + "_voice.wav")
    voice = voice_track(vtmp)
    ticks = [(s + 0.04, 520.0) for p in caps.phrases for s, _ in p["icons"]]
    cta0 = CTA_T + 0.3 if CTA_T is not None else END_T + 1.0
    ticks += [(url.t0 + 0.62, 900.0), (cta0 + 0.2, 440.0), (cta0 + 0.55, 440.0)]
    wh = [SHOT_CUTS[i] for i, k in TRANS.items() if k in ("whip", "zoom")] + [min(END_T, CTA_T or 99)]
    mtmp = out.with_name(out.stem + "_mix.wav")
    mix(mtmp, voice, hook.land(), min(END_T, SPEECH_END + 0.12), ticks, wh)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(tmp_v), "-i", str(mtmp), "-filter_complex",
                    "[1:a]volume=-3dB,alimiter=limit=0.63:attack=2:release=60:level=false,"
                    "loudnorm=I=-14:TP=-2.5:LRA=11,aresample=48000[a]",
                    "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                    "-t", f"{DUR:.2f}", "-movflags", "+faststart", str(out)], check=True)
    for p in (tmp_v, vtmp, mtmp):
        p.unlink(missing_ok=True)
    print("wrote", out, f"{DUR:.2f}s")


if __name__ == "__main__":
    main()
