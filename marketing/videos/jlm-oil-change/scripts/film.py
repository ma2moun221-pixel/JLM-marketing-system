"""JLM oil-change film — Engine Oil Flush, then 5W-30: 30 s cinematic story on real workshop footage.

    python3 scripts/music.py                                      # assets/bgm/film_mix.wav
    python3 scripts/film.py --out renders/jlm_oil_change_film.mp4 [--stills 1,5,...]

One service, lived step by step (cuts on a 120 BPM grid, zoom-blur whips with a warm light flash):
  0.0  an old engine, black & white — «محرّك قديم؟ أوساخ وترسّبات زيت المحرك»
  3.0  Engine Oil Flush, hero-lit — ينظّف المحرك من الأوساخ وترسّبات الزيت · ديزل · بنزين · هايبرد
  6.0  ١ اسكبه في زيت المحرك قبل تغيير الزيت
  8.5  ٢ اترك المحرك دائراً 15 دقيقة (0 → 15 timer)
 11.0  ٣ أفرغ زيت المحرك واستبدل فلتر الزيت (under the car)
 14.5  أداء أفضل · استهلاك أقل للوقود
 16.5  5W-30, hero-lit — زيت محرك مناسب · A5/B5 · احتكاك منخفض
 19.5  ٤ ضع الزيت الجديد حسب تعليمات المركبة (golden pour, slow motion)
 22.0  ٥ افحص مستوى الزيت — وتجنّب الملء الزائد
 24.5  كفاءة أعلى في استهلاك الوقود · مع حماية عالية للمحرك
 27.0  CTA — both products, اطلبهما الآن من خلال jlmstore.com, مع توفّر خدمة التوصيل
Shared look (grade, grain, whips, kinetic type, step chips, timer) comes from jlm-atf-stopleak/scripts/film.py.
"""
import argparse
import importlib.util
import math
import subprocess
from functools import lru_cache
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("atf_film", ROOT.parent / "jlm-atf-stopleak/scripts/film.py")
A = importlib.util.module_from_spec(spec)
spec.loader.exec_module(A)

V, E, R = A.V, A.E, A.R
W, H, FPS, DUR = 1080, 1920, 30, 30.0
YEL, WHT, RED, SIL = A.YEL, A.WHT, A.RED, A.SIL
FOOT = ROOT / "assets/footage"
ATF_FOOT = ROOT.parent / "jlm-atf-stopleak/assets/footage"
BUILD = ROOT / "build/shots"
ease, back = A.ease, A.back
line, latin, punch, shade, glow = A.line, A.latin, A.punch, A.shade, A.glow

# name: (file, src start, output length, speed, crop w:h:x:y)
SHOTS = {
    "old":     (FOOT / "v5.mp4", 1.0, 3.0, 0.9, "2160:3840:0:0"),
    "lift":    (FOOT / "v2.mp4", 2.0, 3.0, 0.6, "1215:2160:1300:0"),        # blurred behind the Flush can
    "pour1":   (ATF_FOOT / "c1.mp4", 1.0, 2.5, 1.0, "2160:3840:0:0"),
    "idle":    (FOOT / "v6.mp4", 1.0, 2.5, 1.0, "1215:2160:1450:0"),
    "drain":   (FOOT / "v3.mp4", 2.0, 1.75, 1.0, "1215:2160:1450:0"),
    "plug":    (FOOT / "v1.mp4", 2.0, 1.75, 1.0, "1440:2560:0:0"),
    "under":   (FOOT / "v2.mp4", 5.0, 2.0, 0.8, "1215:2160:900:0"),
    "bay":     (FOOT / "v6.mp4", 6.0, 3.0, 0.6, "1215:2160:1450:0"),       # blurred behind the 5W-30
    "pour2":   (ATF_FOOT / "c2.mp4", 1.0, 2.5, 0.6, "608:1080:560:0"),     # 60 fps → smooth slow motion
    "dip":     (FOOT / "v4.mp4", 1.5, 2.5, 1.0, "1215:2160:1420:0"),
    "happy":   (FOOT / "v6.mp4", 8.0, 2.5, 1.0, "1215:2160:1450:0"),
    "cta":     (FOOT / "v2.mp4", 8.0, 3.0, 0.5, "1215:2160:1300:0"),
}
EDL = [(0.0, 3.0, "old"), (3.0, 6.0, "lift"), (6.0, 8.5, "pour1"), (8.5, 11.0, "idle"), (11.0, 12.75, "drain"),
       (12.75, 14.5, "plug"), (14.5, 16.5, "under"), (16.5, 19.5, "bay"), (19.5, 22.0, "pour2"), (22.0, 24.5, "dip"),
       (24.5, 27.0, "happy"), (27.0, 30.0, "cta")]
CUTS = [s for s, *_ in EDL[1:]]
BLURRED = {"lift", "bay", "cta"}


def extract():
    BUILD.mkdir(parents=True, exist_ok=True)
    for name, (src, t0, dur, speed, crop) in SHOTS.items():
        out = BUILD / f"{name}.mp4"
        if out.exists():
            continue
        vf = (f"trim=start={t0}:duration={dur * speed + 0.2},setpts=(PTS-STARTPTS)/{speed},crop={crop},"
              f"scale={W}:{H}:flags=lanczos,fps={FPS}")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(src), "-vf", vf, "-an", "-t", str(dur + 0.1),
                        "-c:v", "libx264", "-crf", "12", "-preset", "fast", str(out)], check=True)


A.BUILD = BUILD   # the shared frame reader reads our shots


@lru_cache(maxsize=None)
def product(name, h):
    """Product photo (transparent background), cropped to the pack and scaled to height h."""
    src = {"flush": ROOT / "assets/gen/flush.png", "oil": ROOT / "assets/gen/oil5w30.png"}[name]   # cut out by scripts/prepare.py
    im = Image.open(src).convert("RGBA")
    a = np.array(im)[..., 3]
    ys, xs = np.nonzero(a > 10)
    im = im.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))
    im = im.resize((int(im.width * h / im.height), h), Image.LANCZOS)
    if name == "oil":          # the client's 5W-30 photo is 400 px: a light unsharp mask after the upscale
        im = im.filter(ImageFilter.UnsharpMask(radius=2, percent=60, threshold=2))
    return R.to_premul(np.array(im))


def with_sheen(lay, p):
    if not 0 < p < 1:
        return lay
    lay = lay.copy()
    hh, ww = lay.shape[:2]
    yy, xx = np.mgrid[0:hh, 0:ww].astype(np.float32)
    band = np.exp(-(((xx * 0.6 + yy) - (-0.4 * hh + 1.8 * hh * ease(p))) / 60) ** 2)[..., None]
    lay[..., :3] += band * lay[..., 3:4] * 0.45
    return lay


def hero(f, name, h, lt, cy=880):
    q = ease(lt / 0.6)
    glow(f, W / 2, cy, q)
    lay = with_sheen(product(name, h), (lt - 0.9) / 1.0)
    l2, x, y = R.warp_premul(lay, 1.18 - 0.18 * q + 0.02 * lt, W / 2, cy - 10 * lt, (lay.shape[1] / 2, lay.shape[0] / 2))
    if q < 1:
        l2 = cv2.GaussianBlur(l2, (0, 0), 1 + 10 * (1 - q))
    R.over(f, l2, x, y, q)


@lru_cache(maxsize=None)
def small(text, color=WHT, size=44):
    return E.T.line([(text, color)], size, bold=False, shadow=True, pad=16)


def frame(shots, t, n, logo, tr, bits):
    k = max(i for i, e in enumerate(EDL) if e[0] <= t)
    s0, s1, name = EDL[k]
    lt = t - s0
    fr = shots.get(name, int(round(lt * FPS)))
    sc = 1.04 + 0.06 * (lt / (s1 - s0)) + 0.08 * (1 - ease(lt / 0.25))
    f = A.zoom(fr, sc, W / 2, H * 0.45)
    if name in BLURRED:
        f = A.blur(f, 22) * 0.42
    f = A.grade(f, -1.0 if t < 3.0 else 1.0)
    for c in CUTS:
        d = t - c
        if -0.13 < d < 0.13:
            f = A.zoom_blur(f, 0.12 * (1 - abs(d) / 0.13))
            f = A.light_leak(f, 0.5 + d / 0.26)

    if t < 3.0:
        shade(f, 1150, 1780, 0.6)
        punch(f, line((("محرّك", WHT), ("قديم؟", WHT)), 130), t, 0.3, 2.75, 1300, big=1.5)
        punch(f, line((("أوساخ", RED), ("وترسّبات", RED), ("زيت", WHT), ("المحرك", WHT)), 64), t, 1.1, 2.75, 1460)
    elif t < 6.0:
        hero(f, "flush", 900, t - 3.0)
        punch(f, latin("Engine Oil Flush", 76, YEL), t, 3.6, 5.75, 1440)
        punch(f, line((("ينظّف", WHT), ("المحرك", WHT), ("من", WHT), ("الأوساخ", WHT), ("وترسّبات", WHT), ("الزيت", WHT)), 50), t, 3.9, 5.75, 1545)
        punch(f, bits["fuels"], t, 4.3, 5.75, 1650)
    elif t < 14.5:
        shade(f, 1250, 1800, 0.6)
        if t < 8.5:
            punch(f, A.step_chip("١", "اسكبه في زيت المحرك"), t, 6.05, 8.3, 1430)
            punch(f, small("قبل تغيير الزيت"), t, 6.3, 8.3, 1560)
        elif t < 11.0:
            punch(f, A.step_chip("٢", "اترك المحرك دائراً 15 دقيقة"), t, 8.55, 10.8, 1430)
            A.timer(f, t, 8.6, W / 2, 520)
        else:
            punch(f, A.step_chip("٣", "أفرغ زيت المحرك"), t, 11.05, 14.3, 1430)
            punch(f, small("واستبدل فلتر الزيت"), t, 11.4, 14.3, 1560)
    elif t < 16.5:
        shade(f, 1000, 1800, 0.6)
        punch(f, line((("أداء", WHT), ("أفضل", YEL), ("للمحرك", WHT)), 92), t, 14.6, 16.3, 1250, big=1.4)
        punch(f, line((("واستهلاك", WHT), ("أقل", YEL), ("للوقود", WHT)), 80), t, 15.0, 16.3, 1385, big=1.4)
    elif t < 19.5:
        hero(f, "oil", 640, t - 16.5, cy=860)
        punch(f, latin("5W-30", 120, YEL), t, 17.0, 19.25, 1340)
        punch(f, line((("زيت", WHT), ("محرك", WHT), ("مناسب", YEL)), 66), t, 17.3, 19.25, 1475)
        punch(f, bits["spec"], t, 17.7, 19.25, 1600)
    elif t < 24.5:
        shade(f, 1250, 1800, 0.6)
        if t < 22.0:
            punch(f, A.step_chip("٤", "ضع الزيت الجديد"), t, 19.55, 21.8, 1430)
            punch(f, small("حسب تعليمات المركبة"), t, 19.85, 21.8, 1560)
        else:
            punch(f, A.step_chip("٥", "افحص مستوى الزيت"), t, 22.05, 24.3, 1430)
            punch(f, small("وتجنّب الملء الزائد"), t, 22.4, 24.3, 1560)
    elif t < 27.0:
        shade(f, 1050, 1800, 0.6)
        punch(f, line((("كفاءة", WHT), ("أعلى", YEL), ("في", WHT), ("استهلاك", WHT), ("الوقود", WHT)), 70), t, 24.6, 26.8, 1300, big=1.4)
        punch(f, line((("مع", WHT), ("حماية", YEL), ("عالية", YEL), ("للمحرك", WHT)), 70), t, 25.1, 26.8, 1420, big=1.4)
    else:
        lt = t - 27.0
        q = ease(lt / 0.6)
        glow(f, W / 2, 840, q)
        fl = with_sheen(product("flush", 600), (lt - 1.2) / 0.9)
        oil = with_sheen(product("oil", 430), (lt - 1.4) / 0.9)
        for lay, cx, cy, d in ((fl, 355, 840, 0.0), (oil, 720, 900, 0.12)):
            qq = ease((lt - d) / 0.6)
            l2, x, y = R.warp_premul(lay, 1.1 - 0.1 * qq, cx, cy - 8 * lt, (lay.shape[1] / 2, lay.shape[0] / 2))
            R.over(f, l2, x, y, qq)
        punch(f, bits["logo"], t, 27.1, 31, 330)
        punch(f, line((("اطلبهما", YEL), ("الآن", YEL), ("من", WHT), ("خلال", WHT)), 70), t, 27.5, 31, 1290)
        q = back((t - 27.8) / 0.4, 1.4)
        if q > 0:
            pill = bits["pill"].copy()
            sp = (t - 28.4) / 0.7
            if 0 < sp < 1:
                xs = np.arange(pill.shape[1], dtype=np.float32)
                band = np.exp(-((xs - (-80 + (pill.shape[1] + 160) * ease(sp))) / 40) ** 2)[None, :, None]
                pill[..., :3] += band * pill[..., 3:4] * 0.45
            lay, x, y = R.warp_premul(pill, 0.6 + 0.4 * q, W / 2, 1420, (pill.shape[1] / 2, pill.shape[0] / 2))
            R.over(f, lay, x, y, min(1.0, q))
        q = ease((t - 28.15) / 0.3)
        if q > 0:
            trk = tr.truck(ease((t - 28.15) / 0.8), 130)
            dl = bits["deliv"]
            row = dl.shape[1] + trk.shape[1]
            x0, yy = (W - row) / 2, 1555
            R.over(f, trk, x0, yy - trk.shape[0] / 2, q)
            R.over(f, dl, x0 + trk.shape[1], yy - dl.shape[0] / 2 + 4, q)
    if t < 27.0:
        R.over(f, logo, W - logo.shape[1] - 40, 70, ease((t - 0.2) / 0.4))
    f = np.clip(f, 0, 1)
    if t > DUR - 0.4:
        f *= max(0.0, (DUR - t) / 0.4) * 0.6 + 0.4
    return A.finish(f, n)


def chip_row(words, size=40):
    """Small dark pill with silver words separated by yellow dots (mixed Arabic / Latin)."""
    parts = []
    for i, w in enumerate(words):
        if i:
            parts.append(latin("•", size, YEL))
        parts.append(E.T.line([(w, SIL)], size, bold=True, shadow=False, pad=0) if any("؀" <= c <= "ۿ" for c in w)
                     else latin(w, size - 4, SIL))
    gap = 22
    h = max(p.shape[0] for p in parts) + 30
    w = sum(p.shape[1] for p in parts) + gap * (len(parts) - 1) + 60
    s = 3
    img = np.zeros((h * s, w * s, 4), np.uint8)
    r = h * s // 2
    cv2.rectangle(img, (r, 0), (w * s - r, h * s), (16, 17, 18, 210), -1)
    cv2.circle(img, (r, r), r, (16, 17, 18, 210), -1, cv2.LINE_AA)
    cv2.circle(img, (w * s - r, r), r, (16, 17, 18, 210), -1, cv2.LINE_AA)
    lay = R.to_premul(cv2.resize(img, (w, h), interpolation=cv2.INTER_AREA))
    x = w - 30                                  # right to left
    for p in parts:
        x -= p.shape[1]
        R.paste_into(lay, p, x, (h - p.shape[0]) // 2)
        x -= gap
    return lay


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--stills")
    a = ap.parse_args()
    out = ROOT / a.out
    out.parent.mkdir(parents=True, exist_ok=True)
    extract()
    shots = A.Shots()
    lg = Image.open(ROOT.parent / "jlm-atf-stopleak/assets/gen/logo.png")
    logo = R.to_premul(np.array(lg.resize((190, int(lg.height * 190 / lg.width)), Image.LANCZOS)))
    big_logo = R.to_premul(np.array(lg.resize((440, int(lg.height * 440 / lg.width)), Image.LANCZOS)))
    bits = {"logo": big_logo, "pill": V.url_pill(70),
            "deliv": E.T.line([("مع توفّر", WHT), ("خدمة التوصيل", YEL)], 52, bold=True, shadow=True, pad=8),
            "fuels": chip_row(["ديزل", "بنزين", "هايبرد"]),
            "spec": chip_row(["A5/B5", "احتكاك منخفض"])}
    tr = V.EndCard(27.0)

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
        img = (frame(shots, t, n, logo, tr, bits) * 255 + 0.5).astype(np.uint8)
        if want is not None:
            cv2.imwrite(str(out.parent / f"still_{t:05.2f}.png"), cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
        else:
            enc.stdin.write(img.tobytes())
    if enc is None:
        return
    enc.stdin.close()
    enc.wait()
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(tmp), "-i", str(ROOT / "assets/bgm/film_mix.wav"),
                    "-filter_complex", "[1:a]loudnorm=I=-13:TP=-1.5:LRA=9,aresample=48000,alimiter=limit=0.76:attack=1:release=60:level=false[a]",
                    "-map", "0:v", "-map", "[a]", "-c:v", "libx264", "-preset", "slow", "-crf", "20", "-maxrate", "14M",
                    "-bufsize", "28M", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-t", str(DUR),
                    "-movflags", "+faststart", str(out)], check=True)
    tmp.unlink(missing_ok=True)
    print("wrote", out)


if __name__ == "__main__":
    main()
