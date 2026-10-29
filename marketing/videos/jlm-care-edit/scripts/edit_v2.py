"""JLM «العناية الدورية» — v2 edit in the talking-head reference style
(brand/jlm/VIDEO_STYLE.md §1–5): word-synced chest captions (white + yellow
keyword), numbered points, dashed-yellow icon tiles placed above / beside the
head (never on the face), one short minimal B-roll, soft SFX, JLM end card.

    python3 edit_v2.py --src CLIENT_VIDEO --out ../out/jlm_care_edit_v2.mp4 [--stills 1,5,...]
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
sys.path.insert(0, str(HERE))
import edit as E  # noqa: E402  (shared: R, T, IC, KIT, icon_obj, DepositClean, colours)

R, T, IC = E.R, E.T, E.IC
W, H, FPS = 1080, 1920, 30
YEL, WHT, CHA = E.YEL, E.WHT, E.CHA
SRC_DUR = 23.9
HOLD = 1.5                       # frozen last frame for the end card
DUR = SRC_DUR + HOLD

# ------------------------------------------------------------ face track ---
# (t, cx, cy, w) normalised (w = face width / frame width); None = no person.
# Built from Haar detections where reliable (0–2.8 s, 4.2–7.2 s) and checked by eye.
FACE_KEYS = [
    (0.0, 0.66, 0.26, 0.14), (0.6, 0.53, 0.27, 0.15), (1.0, 0.45, 0.25, 0.14), (1.3, 0.44, 0.26, 0.14),
    (2.3, 0.35, 0.23, 0.18), (2.8, 0.52, 0.30, 0.13), (3.2, 0.62, 0.28, 0.12), (3.8, 0.60, 0.22, 0.20),
    (4.4, 0.42, 0.22, 0.22), (5.4, 0.55, 0.18, 0.25), (5.8, 0.62, 0.16, 0.27), (6.4, 0.49, 0.14, 0.28),
    (7.8, 0.50, 0.18, 0.20), (8.2, 0.50, 0.18, 0.20),
]
FACE_LATE = (20.9, 0.60, 0.31, 0.10)     # presenter behind the product table


def face_at(t):
    if t <= FACE_KEYS[-1][0]:
        ks = FACE_KEYS
        for a, b in zip(ks, ks[1:]):
            if a[0] <= t <= b[0]:
                u = (t - a[0]) / (b[0] - a[0])
                return tuple(a[i] + (b[i] - a[i]) * u for i in (1, 2, 3))
        return ks[0][1:]
    if t >= FACE_LATE[0]:
        return FACE_LATE[1:]
    return None


def face_rect(f):
    """Face box in px, expanded 15 % each side (the keep-out zone)."""
    cx, cy, w = f
    fw = w * W
    fh = fw * 1.25
    return (cx * W - fw * 0.65, cy * H - fh * 0.65, cx * W + fw * 0.65, cy * H + fh * 0.65)


def caption_y(t):
    f = face_at(t)
    if f is None:
        return 0.50 * H
    cx, cy, w = f
    return float(np.clip(cy + 0.20 + w * 0.25, 0.40, 0.62)) * H


# --------------------------------------------------------------- captions ---
# Segments between pauses (s): chunks with kind 'w' white, 'k' yellow keyword,
# or ('n', number) numbered point. Chunk start = proportional to characters.
SEGMENTS = [
    (0.64, 2.87, [("انت ما بتستنى", "w"), ("المرض", "k"), ("عشان تهتم", "w")]),
    (3.27, 3.56, [("بحالك", "k")]),
    (3.82, 6.09, [("وسيارتك كمان", "w"), ("مش لازم", "w")]),
    (6.34, 7.65, [("تستنى العطل", "k"), ("عشان تهتم فيها", "w")]),
    (8.27, 9.63, [("العناية الدورية", "k"), ("بمنتجات", "w")]),
    (9.76, 12.36, [("JLM", "k"), ("بتساعد في الحفاظ", "w"), ("نظافة المحرّك", ("n", 1))]),
    (12.54, 13.30, [("نظام الوقود", ("n", 2))]),
    (13.81, 16.26, [("وبتحافظ على", "w"), ("أداء السيارة", ("n", 3)), ("مع الاستخدام اليومي", "w")]),
    (17.24, 19.83, [("اهتم بسيارتك", "w"), ("اليوم", "k"), ("ووفّر على نفسك", "w"), ("أعطال بكرا", "k")]),
    (20.74, 21.14, [("JLM", "k")]),
    (21.38, 23.23, [("عناية احترافية", "w"), ("تبدأ من الداخل", "k")]),
]


def chunk_times():
    out = []
    for t0, t1, chunks in SEGMENTS:
        lens = [max(len(c[0].replace(" ", "")), 2) + 1 for c in chunks]
        tot = sum(lens)
        acc = 0
        for (txt, kind), L in zip(chunks, lens):
            out.append((t0 + (t1 - t0) * acc / tot, txt, kind))
            acc += L
    return out


@lru_cache(maxsize=None)
def text_layer(txt, size, color):
    if all(ord(ch) < 128 for ch in txt):
        return soft_shadow(pad_layer(R.latin_layer(txt, int(size * 1.05), color, 900, 0.01), 26))
    return T.line([(txt, color)], size, bold=True, shadow=True, pad=26)


def pad_layer(layer, p):
    out = np.zeros((layer.shape[0] + 2 * p, layer.shape[1] + 2 * p, 4), np.float32)
    out[p:-p, p:-p] = layer
    return out


def soft_shadow(layer):
    a = cv2.GaussianBlur(layer[..., 3], (0, 0), 8) * 0.55
    sh = np.zeros_like(layer)
    sh[..., 3] = np.roll(a, 5, axis=0)
    out = sh
    out = out * (1 - layer[..., 3:4]) + layer
    return out


@lru_cache(maxsize=None)
def number_layer(n, txt):
    num = soft_shadow(pad_layer(R.latin_layer(str(n), 112, YEL, 900, 0), 20))
    word = text_layer(txt, 72, WHT)
    gap = 22
    h = max(num.shape[0], word.shape[0])
    out = np.zeros((h, word.shape[1] + gap + num.shape[1], 4), np.float32)
    R.paste_into(out, word, 0, (h - word.shape[0]) // 2)
    R.paste_into(out, num, word.shape[1] + gap, (h - num.shape[0]) // 2 - 6)
    return out


class Captions:
    """Groups: a white line, optionally joined by a yellow keyword under it."""

    def __init__(self):
        ch = chunk_times()
        self.groups = []
        for i, (t, txt, kind) in enumerate(ch):
            nxt = ch[i + 1][0] if i + 1 < len(ch) else t + 1.6
            seg_end = next(t1 for t0, t1, _ in SEGMENTS if t0 - 1e-6 <= t <= t1 + 1e-6)
            end = min(nxt, seg_end + 0.45) if nxt > seg_end else nxt
            if kind == "k" and self.groups and self.groups[-1]["kind"] == "w" \
                    and len(self.groups[-1]["lines"]) == 1 and t - self.groups[-1]["t0"] < 1.4 \
                    and self.groups[-1]["seg"] == seg_end:
                g = self.groups[-1]
                g["lines"].append((t, text_layer(txt, 84, YEL)))
                g["t1"] = end
                continue
            if isinstance(kind, tuple):
                lines = [(t, number_layer(kind[1], txt))]
            else:
                lines = [(t, text_layer(txt, 84 if kind == "k" else 62, YEL if kind == "k" else WHT))]
            self.groups.append({"t0": t, "t1": end, "lines": lines, "seg": seg_end,
                                "kind": kind if isinstance(kind, str) else "n"})

    def draw(self, f, t):
        for g in self.groups:
            if not (g["t0"] <= t < g["t1"]):
                continue
            y = caption_y(t) - sum(l.shape[0] for _, l in g["lines"]) * 0.42
            for ts, layer in g["lines"]:
                p = E.ease((t - ts) / 0.15)
                if p > 0:
                    sc = 0.92 + 0.08 * p
                    lay, x, yy = R.warp_premul(layer, sc, W / 2, y + layer.shape[0] / 2, (layer.shape[1] / 2, layer.shape[0] / 2))
                    R.over(f, lay, x, yy, p)
                y += layer.shape[0] * 0.80


# ------------------------------------------------------------------ tiles ---
TILE = 216


@lru_cache(maxsize=None)
def tile_layer(icon):
    s = 3
    img = Image.new("RGBA", (TILE * s, TILE * s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    r = 30 * s
    d.rounded_rectangle([3 * s, 3 * s, (TILE - 3) * s, (TILE - 3) * s], radius=r, fill=(14, 15, 16, 150))
    # dashed yellow border
    dash, gapd = 16 * s, 10 * s
    x0, y0, x1, y1 = 4 * s, 4 * s, (TILE - 4) * s, (TILE - 4) * s
    for (ax, ay, bx, by) in [(x0 + r, y0, x1 - r, y0), (x0 + r, y1, x1 - r, y1), (x0, y0 + r, x0, y1 - r), (x1, y0 + r, x1, y1 - r)]:
        L = math.hypot(bx - ax, by - ay)
        k = 0
        while k < L:
            e = min(k + dash, L)
            d.line([(ax + (bx - ax) * k / L, ay + (by - ay) * k / L), (ax + (bx - ax) * e / L, ay + (by - ay) * e / L)],
                   fill=YEL + (255,), width=3 * s)
            k += dash + gapd
    for (cx, cy, a0) in [(x0 + r, y0 + r, 180), (x1 - r, y0 + r, 270), (x1 - r, y1 - r, 0), (x0 + r, y1 - r, 90)]:
        d.arc([cx - r, cy - r, cx + r, cy + r], a0, a0 + 90, fill=YEL + (255,), width=3 * s)
    tile = R.to_premul(np.array(img.resize((TILE, TILE), Image.LANCZOS)))
    glow_a = cv2.GaussianBlur(tile[..., 3] * (tile[..., 0] > 0.4), (0, 0), 7) * 0.55
    glow = np.dstack([glow_a[..., None] * E.rgb01(YEL), glow_a])
    out = glow * (1 - tile[..., 3:4]) + tile
    # static 3D icon, settled pose
    ic = E.icon_obj(icon)
    fr = np.clip(ic.frame(min(ic.duration * 0.62, 1.6)), 0, 1).astype(np.float32)
    px = int(TILE * 0.86)
    fr = cv2.resize(fr, (px, px), interpolation=cv2.INTER_AREA)
    R.paste_into(out, fr, (TILE - px) // 2, (TILE - px) // 2)
    pad = 14
    big = np.zeros((TILE + 2 * pad, TILE + 2 * pad, 4), np.float32)
    big[pad:pad + TILE, pad:pad + TILE] = out
    return big


# (t0, t1, [(icon, appear_t), ...]) — rows build left-to-right in reading order
TILE_SETS = []


def build_tiles(ch):
    def at(word):
        return next(t for t, txt, _ in ch if txt == word)
    return [
        (at("المرض"), 3.62, [("Heart", at("المرض"))]),
        (at("تستنى العطل"), 7.70, [("CarWarning", at("تستنى العطل"))]),
        (at("العناية الدورية"), 9.70, [("Calendar", at("العناية الدورية"))]),
        (at("نظافة المحرّك"), 16.30, [("Engine", at("نظافة المحرّك")), ("FuelPump", at("نظام الوقود")), ("Gauge", at("أداء السيارة"))]),
        (at("أعطال بكرا"), 19.90, [("Shield", at("أعطال بكرا"))]),
        (20.74, 23.30, [("JLMDrop", 20.74)]),
    ]


def tiles_xy(t, n):
    """Centre of a row of n tiles that keeps clear of the face."""
    size = TILE + 28
    row_w = n * size + (n - 1) * 8
    f = face_at(t)
    top_band = 0.05 * H
    if f is None:
        return W / 2, top_band + size / 2 + 40, "row"
    x0, y0, x1, y1 = face_rect(f)
    if y0 - top_band >= size + 10:                       # room above the head
        cx = float(np.clip((x0 + x1) / 2, row_w / 2 + 30, W - row_w / 2 - 30))
        return cx, y0 - 10 - size / 2, "row"
    # beside the face, on the emptier side, top-aligned with the face
    side = 1 if (x0 + x1) / 2 < W / 2 else -1
    cx = W / 2 + side * (W / 2 - size / 2 - 40)
    cy = max(top_band + size / 2, (y0 + y1) / 2)
    return cx, cy, "side"


def draw_tiles(f, t, sets):
    for t0, t1, items in sets:
        if not (t0 <= t <= t1 + 0.2):
            continue
        out = 1 - E.ease((t - t1) / 0.2)
        shown = [(ic, ta) for ic, ta in items if t >= ta]
        if not shown:
            continue
        cx, cy, mode = tiles_xy(t, len(items))
        size = TILE + 28 + 8
        total = len(items) * size - 8
        for k, (ic, ta) in enumerate(shown):
            p = E.ease((t - ta) / 0.2)
            layer = tile_layer(ic)
            # RTL reading: first tile on the right
            x = cx + total / 2 - (k + 0.5) * size if mode == "row" else cx
            y = cy + (k * size if mode == "side" else 0)
            lay, lx, ly = R.warp_premul(layer, 0.9 + 0.1 * p, x, y, (layer.shape[1] / 2, layer.shape[0] / 2))
            R.over(f, lay, lx, ly, p * out)


# ----------------------------------------------------------------- audio ---
def soft_click(sr):
    n = int(0.11 * sr)
    t = np.arange(n) / sr
    env = np.minimum(1, t / 0.004) * np.exp(-t / 0.045)
    x = np.sin(2 * np.pi * 520 * t) * 0.7 + np.sin(2 * np.pi * 780 * t) * 0.25
    return (x * env * 0.03).astype(np.float32)         # ≈ −30 dBFS


def bed(sr, dur):
    """Very quiet warm pad under the voice."""
    t = np.arange(int(dur * sr)) / sr
    x = np.zeros_like(t)
    for f0 in (110.0, 164.8, 220.0, 277.2):
        x += np.sin(2 * np.pi * f0 * t) + 0.3 * np.sin(2 * np.pi * f0 * 2.002 * t)
    lfo = 0.75 + 0.25 * np.sin(2 * np.pi * 0.12 * t)
    env = np.minimum(1, t / 1.5) * np.minimum(1, (dur - t) / 1.2)
    return (x / 5.2 * lfo * env * 0.022).astype(np.float32)


def sfx_track(path, sets, broll):
    sr = 48000
    n = int(DUR * sr)
    buf = bed(sr, DUR)
    click = soft_click(sr)
    times = sorted({ta for _, _, items in sets for _, ta in items})
    for ta in times:
        i = int(ta * sr)
        m = min(len(click), n - i)
        buf[i:i + m] += click[:m]
    # soft low swish into the B-roll
    rng = np.random.default_rng(3)
    L = int(0.5 * sr)
    w = np.convolve(rng.standard_normal(L), np.ones(160) / 160, mode="same")
    w = (w * np.sin(np.linspace(0, np.pi, L)) * 0.05).astype(np.float32)
    i = int((broll[0] - 0.3) * sr)
    buf[i:i + L] += w[: n - i]
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

    caps = Captions()
    sets = build_tiles(chunk_times())
    broll = (12.45, 13.95)                          # minimal "inside" cut-away
    clean = E.DepositClean()
    ov = E.Overlay()
    logo = soft_shadow(pad_layer(ov.logo_small * 0.92, 12))
    url = R.latin_layer("jlmstore.com", 46, WHT, 600, 0.02)
    cta = E.cta_pill("اطلبه الآن", 50)
    logo_end = cv2.resize(ov.logo_big, (420, int(ov.logo_big.shape[0] * 420 / ov.logo_big.shape[1])), interpolation=cv2.INTER_AREA)

    src = subprocess.Popen(["ffmpeg", "-v", "error", "-i", a.src, "-vf",
                            f"scale={W}:{H},eq=contrast=1.05:saturation=1.06",
                            "-f", "rawvideo", "-pix_fmt", "rgb24", "-r", str(FPS), "-"], stdout=subprocess.PIPE)
    want = None
    n_frames = int(DUR * FPS)
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
        if broll[0] <= t < broll[1]:
            g = clean.frame(t - broll[0], broll[1] - broll[0])
            mix = min(1.0, (t - broll[0]) / 0.12, (broll[1] - t) / 0.12)
            f = f * (1 - mix) + g * mix
        if t >= SRC_DUR - 0.6:                       # end card over the held last frame
            p = E.ease((t - (SRC_DUR - 0.6)) / 0.5)
            f = f * (1 - 0.65 * p)
        caps.draw(f, t)
        draw_tiles(f, t, sets)
        R.over(f, logo, 32, 80, min(1.0, t / 0.4) * (1 - E.ease((t - SRC_DUR + 0.6) / 0.4)))
        if t >= SRC_DUR - 0.4:
            q = E.ease((t - (SRC_DUR - 0.4)) / 0.4)
            R.over(f, logo_end, (W - logo_end.shape[1]) / 2, 0.40 * H - logo_end.shape[0] / 2, q)
            R.over(f, url, (W - url.shape[1]) / 2, 0.40 * H + logo_end.shape[0] / 2 + 30, q)
            q2 = E.ease((t - SRC_DUR) / 0.35)
            if q2 > 0:
                lay, x, y = R.warp_premul(cta, 0.92 + 0.08 * q2, W / 2, 0.40 * H + logo_end.shape[0] / 2 + 150,
                                          (cta.shape[1] / 2, cta.shape[0] / 2))
                R.over(f, lay, x, y, q2)
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
    sfx = out.with_name(out.stem + "_sfx.wav")
    sfx_track(sfx, sets, broll)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(tmp_v), "-i", a.src, "-i", str(sfx),
                    "-filter_complex",
                    f"[1:a]aresample=48000,apad=whole_dur={DUR}[v];[v][2:a]amix=inputs=2:normalize=0:duration=longest,"
                    "loudnorm=I=-14:TP=-2.5:LRA=11,alimiter=limit=0.66:level=false[a]",
                    "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                    "-t", f"{DUR:.2f}", "-movflags", "+faststart", str(out)], check=True)
    tmp_v.unlink(missing_ok=True)
    sfx.unlink(missing_ok=True)
    print("wrote", out)


if __name__ == "__main__":
    main()
