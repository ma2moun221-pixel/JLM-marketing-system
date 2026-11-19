"""JLM stand story — four phone clips from the client, cut smoothly, captions + logo only (no animation).

    python3 scripts/music.py                         # assets/music.wav (warm, 120 BPM, C major)
    python3 scripts/story.py --out out/jlm_stand_story.mp4 [--stills 1,5,...]

Cuts sit on the beat (0.5 s grid) and dissolve over 0.3 s; captions are static on the approved soft dark
box (Helvetica Neue LT Arabic), fading in and out; the JLM logo (without its file's background box) stays
top-right. The clips' own sound is replaced by the music with a faint bed of the crowd.
"""
import argparse
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[2]
sys.path.insert(0, str(REPO / "marketing/videos/jlm-care-edit/scripts"))
import edit_v3 as V  # noqa: E402

E, R = V.E, V.R
W, H, FPS = 1080, 1920, 30
YEL, WHT = (250, 184, 23), (241, 240, 236)
XF = 0.3                     # dissolve length

# (clip, src start, length) — iPhone .mov files are auto-rotated by ffmpeg
CLIPS = [("m1", 0.0, 2.0),   # shelves at sunset (Petrol Extreme Clean)
         ("m2", 2.0, 6.0),   # slow move round the full stand
         ("m3", 0.3, 4.5),   # the JLM team shirt in the crowd
         ("m4", 2.0, 6.5)]   # staff advising a visitor
DUR = sum(c[2] for c in CLIPS)
STARTS = np.cumsum([0] + [c[2] for c in CLIPS[:-1]])
# captions: (start, end, [(text, colour), …] lines)
CAPS = [
    (0.3, 1.9, [[("منتجات", WHT), ("JLM", YEL)]]),
    (2.2, 7.8, [[("تشكيلة", WHT), ("متكاملة", YEL)], [("للعناية", WHT), ("بسيارتك", WHT)]]),
    (8.2, 12.3, [[("فريق", WHT), ("JLM", YEL), ("معكم", WHT)]]),
    (12.7, 15.4, [[("اسأل", WHT), ("خبير", YEL), ("JLM", YEL)]]),
    (15.7, DUR, [[("اطلبها", YEL), ("الآن", YEL), ("من", WHT), ("خلال", WHT)], [("jlmstore.com", YEL)],
                 [("مع", WHT), ("توفر", WHT), ("خدمة", WHT), ("التوصيل", WHT)]]),
]


def extract():
    b = ROOT / "build"
    b.mkdir(exist_ok=True)
    for name, t0, dur in CLIPS:
        out = b / f"{name}.mp4"
        if out.exists():
            continue
        vf = (f"scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos,crop={W}:{H},fps={FPS},"
              "eq=contrast=1.04:saturation=1.06")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", str(t0), "-i", str(ROOT / f"src/{name}.mov"),
                        "-t", str(dur + XF + 0.2), "-vf", vf, "-an", "-c:v", "libx264", "-crf", "14", "-preset", "fast",
                        str(out)], check=True)


def frames(name):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(ROOT / f"build/{name}.mp4"), "-f", "rawvideo",
                          "-pix_fmt", "rgb24", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, H, W, 3)


def is_ar(w):
    return any("؀" <= c <= "ۿ" for c in w)


def caption(lines):
    """Static caption block on the soft dark box (one or more centred lines)."""
    rows = []
    for runs in lines:
        if len(runs) == 1 and not is_ar(runs[0][0]):
            rows.append(R.latin_layer(runs[0][0], 60, runs[0][1], 800, 0.01))
        else:
            rows.append(E.T.line(runs, 64, bold=True, shadow=True, pad=14))
    w = max(r.shape[1] for r in rows)
    h = sum(r.shape[0] for r in rows) + 12 * (len(rows) - 1)
    box = V.soft_box(w + 40, h + 16, alpha=0.66)
    out = np.zeros((max(box.shape[0], h), max(box.shape[1], w), 4), np.float32)
    R.paste_into(out, box, (out.shape[1] - box.shape[1]) // 2, (out.shape[0] - box.shape[0]) // 2)
    y = (out.shape[0] - h) // 2
    for r in rows:
        R.paste_into(out, r, (out.shape[1] - r.shape[1]) // 2, y)
        y += r.shape[0] + 12
    return out


def logo_layer(width):
    im = np.array(Image.open(E.KIT / "logos/logo_on_dark.png").convert("RGBA"))
    keep = cv2.dilate((im[..., 3] > 128).astype(np.uint8), np.ones((5, 5), np.uint8))
    im[..., 3] = im[..., 3] * keep
    im[:4], im[-4:], im[:, :4], im[:, -4:] = 0, 0, 0, 0
    im = Image.fromarray(im).resize((width, int(im.shape[0] * width / im.shape[1])), Image.LANCZOS)
    return R.to_premul(np.array(im))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--stills")
    a = ap.parse_args()
    out = ROOT / a.out
    out.parent.mkdir(parents=True, exist_ok=True)
    extract()
    clips = {c[0]: frames(c[0]) for c in CLIPS}
    logo = logo_layer(200)
    caps = [(t0, t1, caption(lines)) for t0, t1, lines in CAPS]
    want = None
    if a.stills:
        want = {int(round(float(s) * FPS)) for s in a.stills.split(",")}
    tmp = out.with_name(out.stem + "_video.mp4")
    enc = None
    if want is None:
        enc = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                                "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "slow",
                                "-crf", "18", "-pix_fmt", "yuv420p", str(tmp)], stdin=subprocess.PIPE)
    n_frames = int(round(DUR * FPS))
    for n in range(n_frames):
        if want is not None and n not in want:
            continue
        t = n / FPS
        k = int(np.searchsorted(STARTS, t, side="right") - 1)
        name, _, _ = CLIPS[k]
        fr = clips[name]
        f = fr[min(int(round((t - STARTS[k]) * FPS)), len(fr) - 1)].astype(np.float32) / 255
        # dissolve into the next clip over the last XF seconds of this one
        if k + 1 < len(CLIPS):
            d = t - (STARTS[k + 1] - XF / 2)
            if d > 0:
                nx = clips[CLIPS[k + 1][0]]
                g = nx[min(int(round(d * FPS)), len(nx) - 1)].astype(np.float32) / 255
                m = min(1.0, d / XF)
                f = f * (1 - m) + g * m
        if k > 0 and t - STARTS[k] < XF / 2:   # second half of the dissolve from the previous clip
            pv = clips[CLIPS[k - 1][0]]
            g = pv[min(int(round((t - STARTS[k - 1]) * FPS)), len(pv) - 1)].astype(np.float32) / 255
            m = 0.5 + (t - STARTS[k]) / XF
            f = g * (1 - m) + f * m
        for t0, t1, lay in caps:
            if t0 <= t < t1 + 0.25:
                al = min(1.0, (t - t0) / 0.25, (t1 + 0.25 - t) / 0.25) if t1 < DUR else min(1.0, (t - t0) / 0.25)
                R.over(f, lay, (W - lay.shape[1]) / 2, 0.70 * H - lay.shape[0] / 2, max(0.0, al))
        R.over(f, logo, W - logo.shape[1] - 50, 110)
        if t > DUR - 0.5:
            f *= 0.35 + 0.65 * (DUR - t) / 0.5
        img = (np.clip(f, 0, 1) * 255 + 0.5).astype(np.uint8)
        if want is not None:
            cv2.imwrite(str(out.parent / f"still_{t:05.2f}.png"), cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
        else:
            enc.stdin.write(img.tobytes())
    if enc is None:
        return
    enc.stdin.close()
    enc.wait()
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(tmp), "-i", str(ROOT / "assets/music.wav"),
                    "-filter_complex", "[1:a]loudnorm=I=-14:TP=-1.5:LRA=9,aresample=48000,"
                    "alimiter=limit=0.76:attack=1:release=60:level=false[a]",
                    "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-t", f"{DUR:.2f}",
                    "-movflags", "+faststart", str(out)], check=True)
    tmp.unlink(missing_ok=True)
    print("wrote", out, f"{DUR:.1f}s")


if __name__ == "__main__":
    main()
