"""JLM AIRCO Foam Cleaner clip — simple clean-up (no icons, no animation), as the client asked.

    python3 scripts/clean.py --out out/jlm_airco_clean.mp4 [--stills 1,44,57,...]

- Quality: 720×1280 → 1080×1920 (Lanczos), light temporal/spatial denoise (hqdn3d), gentle unsharp,
  a touch more contrast and colour.
- The landscape inserts that sat in black bars (starting the car, the dashboard, the AC panel, the part
  shot, the recap) fill the frame: the shot full-width over a blurred, darkened copy of itself; the one
  near-full insert (AC panel with the red circle) is simply zoomed to fill.
- The two longest pauses are tightened (11.6 s, 40.8 s); 15 ms audio fades at each cut; voice cleaned
  (high-pass, light denoise) and levelled to −14 LUFS; short fade at the very end.
The clip's own titles (شكوى الزبون · تحديد سبب المشكلة · الحل) and narration are kept as they are.
"""
import argparse
import subprocess
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src/raw.mp4"
SW, SH, W, H, FPS = 720, 1280, 1080, 1920, 30
DUR = 84.43
CUTS_OUT = [(11.59, 11.94), (40.79, 41.07)]           # removed (source seconds)
# letterboxed inserts: (t0, t1, mode, (y0, y1, x0, x1) of the picture inside the bars)
BOXES = [(43.30, 47.00, "pad", (314, 702, 0, 720)),
         (47.00, 48.95, "pad", (485, 897, 0, 720)),
         (48.95, 51.37, "fill", (131, 1218, 0, 720)),
         (56.55, 59.54, "pad", (437, 843, 0, 720)),
         (67.22, 68.98, "pad", (377, 648, 57, 662)),
         (68.98, 70.34, "pad", (496, 784, 58, 661))]


def keep_ranges():
    out, t = [], 0.0
    for a, b in CUTS_OUT:
        out.append((t, a))
        t = b
    out.append((t, DUR))
    return out


def cover(img, w, h):
    ih, iw = img.shape[:2]
    s = max(w / iw, h / ih)
    r = cv2.resize(img, (int(iw * s + 0.5), int(ih * s + 0.5)), interpolation=cv2.INTER_LANCZOS4)
    y, x = (r.shape[0] - h) // 2, (r.shape[1] - w) // 2
    return r[y:y + h, x:x + w]


def treat(fr, t):
    for t0, t1, mode, (y0, y1, x0, x1) in BOXES:
        if t0 <= t < t1:
            pic = fr[y0:y1, x0:x1]
            if mode == "fill":
                return cover(pic, W, H)
            bg = cover(pic, W // 4, H // 4).astype(np.float32)
            bg = cv2.resize(cv2.GaussianBlur(bg, (0, 0), 9), (W, H), interpolation=cv2.INTER_CUBIC) * 0.45
            fw = W
            fh = int(pic.shape[0] * fw / pic.shape[1])
            fg = cv2.resize(pic, (fw, fh), interpolation=cv2.INTER_LANCZOS4).astype(np.float32)
            y = (H - fh) // 2
            bg[y:y + fh] = fg
            # soft shadow edge above and below the picture
            for k in range(18):
                a = 0.5 * (1 - k / 18)
                if y - 1 - k >= 0:
                    bg[y - 1 - k] *= 1 - a
                if y + fh + k < H:
                    bg[y + fh + k] *= 1 - a
            return np.clip(bg, 0, 255).astype(np.uint8)
    return cv2.resize(fr, (W, H), interpolation=cv2.INTER_LANCZOS4)


def finish(img):
    f = img.astype(np.float32)
    f = f + 0.55 * (f - cv2.GaussianBlur(f, (0, 0), 1.3))        # gentle unsharp
    lum = f.mean(2, keepdims=True)
    f = lum + (f - lum) * 1.07                                   # a little more colour
    f = (f - 128) * 1.05 + 128 + 2                               # a little more contrast
    return np.clip(f, 0, 255).astype(np.uint8)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--stills")
    a = ap.parse_args()
    out = ROOT / a.out
    out.parent.mkdir(parents=True, exist_ok=True)
    keep = keep_ranges()
    total = sum(b - a for a, b in keep)
    dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", str(SRC), "-vf", "hqdn3d=1.5:1.5:5:5", "-f", "rawvideo",
                            "-pix_fmt", "bgr24", "-r", str(FPS), "-"], stdout=subprocess.PIPE)
    want = {round(float(s), 2) for s in a.stills.split(",")} if a.stills else None
    tmp = out.with_name(out.stem + "_video.mp4")
    enc = None if want else subprocess.Popen(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r", str(FPS),
         "-i", "-", "-c:v", "libx264", "-preset", "slow", "-crf", "21", "-maxrate", "8M", "-bufsize", "16M",
         "-pix_fmt", "yuv420p", str(tmp)],
        stdin=subprocess.PIPE)
    n, written = 0, 0
    while True:
        raw = dec.stdout.read(SW * SH * 3)
        if len(raw) < SW * SH * 3:
            break
        t = n / FPS
        n += 1
        if not any(a0 <= t < b0 for a0, b0 in keep):
            continue
        img = finish(treat(np.frombuffer(raw, np.uint8).reshape(SH, SW, 3), t))
        tout = written / FPS
        written += 1
        if tout > total - 0.4:                                    # fade at the very end
            img = (img.astype(np.float32) * max(0.0, (total - tout) / 0.4)).astype(np.uint8)
        if want is not None:
            if round(t, 2) in want or any(abs(t - w) < 0.5 / FPS for w in want):
                cv2.imwrite(str(out.parent / f"still_{t:05.2f}.png"), img)
            continue
        enc.stdin.write(img.tobytes())
    dec.stdout.close()
    dec.wait()
    if enc is None:
        return
    enc.stdin.close()
    enc.wait()
    parts, labels = [], []
    for i, (a0, b0) in enumerate(keep):
        d = b0 - a0
        parts.append(f"[0:a]atrim={a0}:{b0},asetpts=PTS-STARTPTS,afade=t=in:d=0.015,afade=t=out:st={d - 0.015}:d=0.015[a{i}];")
        labels.append(f"[a{i}]")
    graph = ("".join(parts) + "".join(labels) + f"concat=n={len(keep)}:v=0:a=1,highpass=f=80,afftdn=nr=8:nf=-30,"
             f"loudnorm=I=-14:TP=-1.5:LRA=9,afade=t=out:st={total - 0.4}:d=0.4[a]")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(SRC), "-i", str(tmp), "-filter_complex", graph,
                    "-map", "1:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
                    "-movflags", "+faststart", str(out)], check=True)
    tmp.unlink(missing_ok=True)
    print("wrote", out, f"{total:.2f}s")


if __name__ == "__main__":
    main()
