"""JLM Petrol Hybrid Treatment — Clean / Minimal version (brand/jlm/EDIT_STYLES.md §1)
of the same edit as edit_fast.py: same footage, words, board, close and CTA, calmer.

    python3 edit_clean.py --src CLIENT_VIDEO --out ../out/jlm_hybrid_clean.mp4 [--stills 1,5,...]

Clean rules applied:
- one lower-third bar (charcoal, 5 px JLM-yellow frame) carries the words; whole phrases,
  white, one yellow keyword, red only for the problem word; phrases crossfade inside the bar;
- one small line icon at a time, always in the same spot, crossfading from one to the next;
- camera: one slow push per shot, no reframes or punch-ins; the jump cut is matched + dissolved;
- the board and the close crossfade in and out; the close's words fade up one by one;
- music about 20 dB under the voice, only soft ticks and two soft whooshes.
"""
import argparse
import subprocess
import sys
import wave
from functools import lru_cache
from pathlib import Path

import cv2
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import edit_fast as F  # noqa: E402  (footage timing, board, icons, end card, music)

V, R, T = F.V, F.R, F.T
W, H, FPS, SR = F.W, F.H, F.FPS, F.SR
YEL, WHT, CHA, RED = F.YEL, F.WHT, F.CHA, F.RED
ease = F.ease
KIN0, END0, DUR, SPEECH_END, KEEP = F.KIN0, F.END0, F.DUR, F.SPEECH_END, F.KEEP

# whole phrases; "*" = the one yellow keyword, "!" = the problem word (red), "#" = hidden
PHRASES = [
    "نظام *الوقود",
    "بسيارات *Hybrid و Plug-in Hybrid",
    "بمحركات *البنزين",
    "بحاجة دائماً *لتنظيف مستمر",
    "#بسبب تراكم مخلفات الاحتراق فيها",                      # the board carries these
    "#وبالذات إنّ المحرّك ما بيشتغل بصورة دائمة ومستمرة",
    "#مع منتج Petrol Hybrid Treatment من JLM",               # the product lower-third carries this
    "اللي بيعمل على *منع",
    "تراكم !الرواسب الكربونية",
    "*وتشحيم نظام الاحتراق",
]
LT_Y = 0.79 * H                 # lower-third centre
ICON_XY = (0.84 * W, 0.665 * H)  # the one icon spot
ICON_SCALE = 0.78


def phrases(words):
    out, k = [], 0
    for ph in PHRASES:
        hidden = ph.startswith("#")
        items = []
        for tok in ph.lstrip("#").split():
            tone = tok[0] if tok[0] in "!*" else ""
            s, e, wd = words[k]
            assert wd == tok.lstrip("!*"), (wd, tok)
            items.append((wd, tone, s, e))
            k += 1
        out.append({"items": items, "hidden": hidden, "t0": items[0][2], "end": items[-1][3]})
    assert k == len(words)
    return out


@lru_cache(maxsize=None)
def bar(w, h):
    """Charcoal lower-third bar with a 5 px JLM-yellow frame and a soft shadow."""
    s, r, pad = 3, 14, 26
    img = np.zeros((h * s, w * s, 4), np.uint8)

    def rr(im, inset, col):
        x0, y0, x1, y1, q = inset, inset, w * s - 1 - inset, h * s - 1 - inset, r * s - inset
        cv2.rectangle(im, (x0 + q, y0), (x1 - q, y1), col, -1)
        cv2.rectangle(im, (x0, y0 + q), (x1, y1 - q), col, -1)
        for cx, cy in [(x0 + q, y0 + q), (x1 - q, y0 + q), (x0 + q, y1 - q), (x1 - q, y1 - q)]:
            cv2.circle(im, (cx, cy), q, col, -1, cv2.LINE_AA)
    rr(img, 0, YEL + (255,))
    rr(img, 5 * s, CHA + (232,))
    b = R.to_premul(cv2.resize(img, (w, h), interpolation=cv2.INTER_AREA))
    out = np.zeros((h + 2 * pad, w + 2 * pad, 4), np.float32)
    sh = np.zeros(out.shape[:2], np.float32)
    sh[pad + 6:pad + 6 + h, pad:pad + w] = b[..., 3]
    out[..., 3] = cv2.GaussianBlur(sh, (0, 0), 12) * 0.35
    R.paste_into(out, b, pad, pad)
    return out


@lru_cache(maxsize=None)
def phrase_layer(key):
    """A whole phrase in the bar: white, one yellow keyword, red problem word."""
    toks = []
    for wd, tone in key:
        col = RED if tone == "!" else YEL if tone == "*" else WHT
        latin = not T._is_arabic(wd)
        if toks and latin and toks[-1][2] and toks[-1][1] == col:
            toks[-1] = (toks[-1][0] + " " + wd, col, True)
        else:
            toks.append((wd, col, latin))
    pad, gap = 20, 20
    lays = [F.latin_token(tx, col, pad) if lat else T.line([(tx, col)], 66, bold=True, shadow=False, pad=pad)
            for tx, col, lat in toks]
    th = max(l.shape[0] for l in lays)
    lays = [np.pad(l, (((th - l.shape[0]) // 2, th - l.shape[0] - (th - l.shape[0]) // 2), (0, 0), (0, 0))) for l in lays]
    tw = sum(l.shape[1] - 2 * pad for l in lays) + gap * (len(lays) - 1)
    txt = np.zeros((th, tw + 2 * pad, 4), np.float32)
    x = tw + pad
    for l in lays:
        x -= l.shape[1] - 2 * pad
        R.paste_into(txt, l, x - pad, 0)
        x -= gap
    return framed(txt)


def framed(txt):
    maxw = W - 120
    if txt.shape[1] > maxw:                      # long phrases shrink to fit the bar
        k = maxw / txt.shape[1]
        txt = cv2.resize(txt, (maxw, int(txt.shape[0] * k)), interpolation=cv2.INTER_AREA)
    b = bar(min(txt.shape[1] + 40, W - 60), max(txt.shape[0] - 10, 96))
    out = b.copy()
    R.paste_into(out, txt, (out.shape[1] - txt.shape[1]) // 2, (out.shape[0] - txt.shape[0]) // 2)
    return out


def product_layer():
    """Two-line product lower-third: the name (Albert Sans, yellow) and «من JLM»."""
    name = R.latin_layer("Petrol Hybrid Treatment", 58, YEL, 800, 0.01)
    by = T.line([("من", WHT), ("JLM", WHT)], 42, bold=True, shadow=False, pad=6)
    w = max(name.shape[1], by.shape[1])
    h = name.shape[0] + by.shape[0] + 22
    txt = np.zeros((h + 24, w + 40, 4), np.float32)
    R.paste_into(txt, name, (txt.shape[1] - name.shape[1]) // 2, 12)
    R.paste_into(txt, by, (txt.shape[1] - by.shape[1]) // 2, 12 + name.shape[0] + 14)
    return framed(txt)


class LowerThird:
    """One bar at a time. Back-to-back contents crossfade (0.22 s); after a pause the bar
    rises in (0.32 s); before a pause it fades out (0.25 s)."""

    def __init__(self, segs):
        self.segs = segs            # [(t0, t1, layer)] in time order

    def draw(self, f, t):
        for i, (t0, t1, lay) in enumerate(self.segs):
            if not (t0 <= t < t1 + 0.25):
                continue
            joined_in = i > 0 and t0 - self.segs[i - 1][1] < 0.05
            joined_out = i + 1 < len(self.segs) and self.segs[i + 1][0] - t1 < 0.05
            if joined_in:
                a_in, dy = ease((t - t0) / 0.22), 0.0
            else:
                a_in = ease((t - t0) / 0.32)
                dy = 18 * (1 - a_in)
            a_out = 1.0 if t < t1 else (1 - ease((t - t1) / (0.22 if joined_out else 0.25)))
            R.over(f, lay, W / 2 - lay.shape[1] / 2, LT_Y - lay.shape[0] / 2 + dy, a_in * a_out)


class OneIcon:
    """One small line icon, always in the same spot; each new icon crossfades over the last."""

    def __init__(self, items):
        self.items = items          # [(t0, t1, icon)]

    def draw(self, f, t):
        for t0, t1, icon in self.items:
            if not (t0 <= t < t1 + 0.25):
                continue
            lt = t - t0
            a = ease(lt / 0.25) * (1 - ease((t - t1) / 0.25))
            layer = V.badge_layer(icon, YEL, lt * 1.6)
            sc = ICON_SCALE * (0.92 + 0.08 * ease(lt / 0.35))
            lay, x, y = R.warp_premul(layer, sc, ICON_XY[0], ICON_XY[1], (layer.shape[1] / 2, layer.shape[0] / 2))
            R.over(f, lay, x, y, a)


class CalmClose:
    """«يمنع / الرواسب / ويشحّم / نظام الاحتراق» fade up one by one on charcoal and stay."""

    def __init__(self, t0):
        self.t0 = t0
        k = F.Kinetic(t0)
        self.bg = k.bg
        self.lines = [(0.30, k.w1, 0.335), (0.75, k.w2, 0.435), (1.35, k.w3, 0.545), (1.95, k.w4, 0.655)]

    def frame(self, t, under):
        p = ease((t - self.t0) / 0.5)
        f = under * (1 - p) + self.bg * p
        for d, lay, yy in self.lines:
            q = ease((t - self.t0 - d) / 0.45)
            if q > 0:
                R.over(f, lay, W / 2 - lay.shape[1] / 2, yy * H - lay.shape[0] / 2 + 22 * (1 - q), q)
        return f


def write_fx(path, events):
    n = int(DUR * SR)
    t = np.arange(n) / SR
    g = np.where(t < KIN0 - 0.1, 0.15 / 0.22, 0.85)          # music ≈ 20 dB under the voice
    g = np.convolve(g, np.ones(4800) / 4800, mode="same")
    buf = F.music(DUR) * g
    for at, sig in events:
        i = int(at * SR)
        m = min(len(sig), n - i)
        if m > 0:
            buf[i:i + m] += sig[:m]
    pcm = (np.clip(np.stack([buf, buf], 1), -1, 1) * 32767).astype(np.int16)
    with wave.open(str(path), "wb") as wv:
        wv.setnchannels(2)
        wv.setsampwidth(2)
        wv.setframerate(SR)
        wv.writeframes(pcm.tobytes())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--stills")
    a = ap.parse_args()
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)

    words = F.word_times(V.voiced_weight(a.src))
    ph = phrases(words)
    at = {}
    for p in ph:
        for wd, _, s, _ in p["items"]:
            at.setdefault(wd, s)
    b0, b1 = F.s2o(5.82), F.s2o(11.13)
    board = F.VoxBoard(b0, b1, [s for p in ph for wd, _, s, _ in p["items"] if wd == "تراكم"][0], at["وبالذات"])
    close = CalmClose(KIN0)
    endcard = V.EndCard(END0)
    endcard.cta = T.line([("اطلبه الآن", YEL), ("من خلال", WHT)], 74, bold=True, shadow=False, pad=10)
    name = F.NameLine(END0)

    # lower-third contents: visible phrases + the product title in place of «مع منتج … من JLM»
    vis = [p for p in ph if not p["hidden"]]
    segs = []
    for i, p in enumerate(vis):
        nxt = vis[i + 1]["t0"] - 0.05 if i + 1 < len(vis) else SPEECH_END
        t1 = nxt if nxt - p["end"] < 0.7 else p["end"] + 0.4
        segs.append((p["t0"] - 0.05, min(t1, b0 - 0.25) if p["t0"] < b0 else t1,
                     phrase_layer(tuple((wd, tone) for wd, tone, _, _ in p["items"]))))
    t_prod0, t_prod1 = at["مع"] - 0.05, at["اللي"] - 0.05
    segs.append((t_prod0, t_prod1, product_layer()))
    segs.sort(key=lambda s: s[0])
    lt = LowerThird(segs)
    icons = OneIcon([
        (at["بسيارات"] - 0.05, at["و"] - 0.05, "hybrid"),
        (at["و"] - 0.05, at["بمحركات"] - 0.05, "plugin"),
        (at["بمحركات"] - 0.05, at["لتنظيف"] - 0.05, "pump"),
        (at["لتنظيف"] - 0.05, b0 - 0.3, "sparkle"),
        (at["منع"] - 0.05, at["وتشحيم"] - 0.05, "shield"),
        (at["وتشحيم"] - 0.05, SPEECH_END - 0.25, "drop"),
    ])
    cuts = [F.s2o(4.33), F.s2o(8.2), b1, F.s2o(KEEP[1][0])]
    # one slow push per shot; across the jump cut the framing is matched, so it only dissolves
    kfs = [
        (0.00, 1.03, 580, 820, 0), (0.01, 1.08, 580, 790, cuts[0] - 0.06),
        (cuts[0], 1.02, 560, 880, 0), (cuts[0] + 0.01, 1.05, 560, 850, b0 - cuts[0] - 0.05),
        (b1, 1.04, 520, 900, 0), (b1 + 0.01, 1.14, 500, 880, cuts[3] - b1 - 0.06),
        (cuts[3], 1.14, 500, 880, 0), (cuts[3] + 0.01, 1.19, 505, 850, SPEECH_END - cuts[3] - 0.05),
    ]
    for s0, s1, _ in segs:
        print(f"  lower-third {s0:5.2f}–{s1:5.2f}")
    print(f"board {b0:.2f}–{b1:.2f}  product {t_prod0:.2f}–{t_prod1:.2f}")

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
    fade = 0.35
    for n in range(n_frames):
        t = n / FPS
        if t < SPEECH_END:
            raw = src.stdout.read(W * H * 3)
            if len(raw) == W * H * 3:
                live = np.frombuffer(raw, np.uint8).reshape(H, W, 3).astype(np.float32) / 255
        if t < KIN0:
            ff = F.apply_cam(live, *F.camera(kfs, t))
            if t < cuts[3]:
                held = ff
            elif t < cuts[3] + 0.2:
                u = ease((t - cuts[3]) / 0.2)
                ff = held * (1 - u) + ff * u
            f = ff
            if b0 - fade <= t < b1 + fade:
                # the board dissolves in and out over the footage
                if t < b1:
                    board_live = live
                bf = board.frame(min(max(t, b0), b1 - 1 / FPS), board_live)
                u = ease((t - b0 + fade) / fade) * (1 - ease((t - b1) / fade))
                f = ff * (1 - u) + bf * u
            if not (b0 - 0.1 <= t < b1 + 0.1):
                icons.draw(f, t)
                lt.draw(f, t)
            last = f
        elif t < END0 + 0.1:
            f = close.frame(t, last)
            endcard.draw(f, t, name)
        else:
            f = np.zeros((H, W, 3), np.float32)
            endcard.draw(f, t, name)
        img = (np.clip(f, 0, 1) * 255 + 0.5).astype(np.uint8)
        if want is not None:
            if n in want:
                cv2.imwrite(str(out.parent / f"clean_{t:05.2f}.png"), cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
            continue
        enc.stdin.write(img.tobytes())
    src.stdout.close()
    src.wait()
    if enc is None:
        return
    enc.stdin.close()
    enc.wait()

    # sound: a soft tick per icon and board card, a soft whoosh into and out of the board
    ev = [(t0 + 0.05, V.soft_tick(SR, 470.0, 0.008)) for t0, _, _ in icons.items]
    ev += [(board.tc1, V.soft_tick(SR, 440.0, 0.008)), (board.tc2, V.soft_tick(SR, 440.0, 0.008))]
    ev += [(b0 - 0.3, F.soft_whoosh(0.5, 0.012)), (b1 - 0.1, F.soft_whoosh(0.5, 0.012))]
    ev += [(END0 + 0.95, V.soft_tick(SR, 440.0)), (END0 + 1.35, V.soft_tick(SR, 440.0))]
    fx = out.with_name(out.stem + "_fx.wav")
    write_fx(fx, ev)
    af = (f"[0:a]atrim={k0}:{k1},asetpts=PTS-STARTPTS,afade=t=out:st={k1 - k0 - 0.015}:d=0.015[a1];"
          f"[0:a]atrim={k2}:{k3},asetpts=PTS-STARTPTS,afade=t=in:d=0.015,afade=t=out:st={k3 - k2 - 0.06}:d=0.06[a2];"
          f"[a1][a2]concat=n=2:v=0:a=1,aresample={SR},apad=whole_dur={DUR}[vo];"
          f"[vo][2:a]amix=inputs=2:normalize=0:duration=longest,"
          "volume=-3dB,alimiter=limit=0.63:attack=2:release=60:level=false,loudnorm=I=-14:TP=-2.5:LRA=11,"
          "alimiter=limit=0.79:attack=1:release=50:level=false[aout]")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", a.src, "-i", str(tmp_v), "-i", str(fx),
                    "-filter_complex", af, "-map", "1:v", "-map", "[aout]", "-c:v", "copy", "-c:a", "aac",
                    "-b:a", "192k", "-ar", str(SR), "-t", f"{DUR:.2f}", "-movflags", "+faststart", str(out)], check=True)
    tmp_v.unlink(missing_ok=True)
    fx.unlink(missing_ok=True)
    print("wrote", out)


if __name__ == "__main__":
    main()
