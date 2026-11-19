"""40-second cut-down of the JLM Penetrating Oil film (v4: music + SFX, no VO).

    python3 scripts/cutdown.py [--src renders/jlm_penetrating_oil.mp4] [--out renders/jlm_penetrating_oil_40s.mp4]
                               [--stills 1,5,...]

Nothing is cut out: every scene, step, caption and the full CTA stay. The film is
re-timed with speed ramps instead:
- holds (benefit chips, mechanism steps, audience hub, usage steps) play faster;
- transitions and match cuts (logo → bolt, can → drop → blue field, hex spin, wipes)
  stay near 1×, so the "one continuous shot" handoffs are untouched;
- speed changes are smoothed (ramps, no jumps), and fast stretches get frame-blended
  motion blur.

The music is re-arranged for the new length (scripts/music.py with remapped cuts), and
every SFX cue is moved through the same time map.
"""
import argparse
import json
import subprocess
import sys
import wave
from collections import deque
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import music as M  # noqa: E402
import sound as S  # noqa: E402

W, H, FPS = 1080, 1920, 30
TARGET = 40.0
SR = 48000

# (src start, src end, speed) — contiguous; the last segment's end is solved for TARGET
SEGMENTS = [
    (0.00, 3.20, 1.70),     # 1 intro sting
    (3.20, 8.00, 1.45),     # 2 hook: rusty bolt, wrench slips, «هناك حل أذكى»
    (8.00, 8.36, 1.00),     #   silver iris → product (match cut)
    (8.36, 10.00, 1.15),    # 3 product cut-out spiral
    (10.00, 18.00, 2.50),   #   benefits build up
    (18.00, 19.20, 1.20),   #   full benefit state, readable
    (19.20, 20.60, 1.00),   #   dive into the MoS2 drop → blue field (match cut)
    (20.60, 22.00, 1.20),   # 4 mechanism: drop lands on the thread
    (22.00, 30.60, 2.30),   #   the four steps
    (30.60, 32.61, 1.30),   #   hex spin → audience (match cut)
    (32.61, 43.20, 3.20),   # 5 audience hub
    (43.20, 43.90, 1.00),   #   yellow wipe
    (43.90, 53.40, 2.10),   # 6 shake, spray, timer
    (53.40, 53.95, 1.20),   #   timer ring → socket (match cut)
    (53.95, 59.50, 1.75),   # 7 wrench turns free, check
    (59.50, 61.68, 1.25),   #   cloth wipe → CTA
    (61.68, 66.00, 1.15),   # 8 CTA build: logo, name, «اطلبه الآن», jlmstore.com
    (66.00, None, 1.00),    #   delivery line + hold
]
RAMP = 0.30                 # seconds (source time) over which speed changes are eased


def time_map():
    """Return (ts, to): monotone samples mapping source time → output time."""
    fixed = sum((b - a) / s for a, b, s in SEGMENTS if b is not None)
    a_last, _, s_last = SEGMENTS[-1]
    end = a_last + (TARGET - fixed) * s_last
    segs = SEGMENTS[:-1] + [(a_last, end, s_last)]
    dt = 0.001
    ts = np.arange(0, end + dt / 2, dt)
    sp = np.ones_like(ts)
    for a, b, s in segs:
        sp[(ts >= a) & (ts < b)] = s
    k = int(RAMP / dt)
    pad = np.pad(sp, (k, k), mode="edge")
    sp = np.convolve(pad, np.ones(2 * k + 1) / (2 * k + 1), mode="same")[k:-k]
    to = np.concatenate([[0], np.cumsum(dt / sp[:-1])])
    to *= TARGET / to[-1]                       # exact length after smoothing
    return ts, to, sp, end


def render_video(src, out, ts, to, sp, stills=None):
    frames_out = int(round(TARGET * FPS))
    want = None if not stills else {int(round(float(x) * FPS)) for x in stills.split(",")}
    dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", str(src), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                           stdout=subprocess.PIPE)
    enc = None
    if want is None:
        enc = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                                "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "slow", "-crf", "16",
                                "-pix_fmt", "yuv420p", str(out)], stdin=subprocess.PIPE)
    buf, base = deque(), 0                      # buf[i] = source frame (base + i)
    nbytes = W * H * 3

    def frame(i):
        nonlocal base
        while base + len(buf) <= i:
            raw = dec.stdout.read(nbytes)
            if len(raw) < nbytes:
                return buf[-1]
            buf.append(np.frombuffer(raw, np.uint8).reshape(H, W, 3))
        while base < i - 8 and len(buf) > 1:
            buf.popleft()
            base += 1
        return buf[i - base]

    for n in range(frames_out):
        t = n / FPS
        s_t = float(np.interp(t, to, ts))
        s_sp = float(np.interp(s_t, ts, sp))
        fi = s_t * FPS
        if s_sp > 1.4:
            # frame-blended motion blur over one output frame's worth of source
            span = s_sp
            idx = np.arange(int(np.floor(fi - span / 2 + 0.5)), int(np.floor(fi + span / 2 + 0.5)))
            idx = np.clip(idx, 0, None)
            img = np.mean([frame(int(i)).astype(np.float32) for i in idx], axis=0)
            img = (img + 0.5).astype(np.uint8)
        else:
            img = frame(int(round(fi)))
        if want is not None:
            if n in want:
                import cv2
                cv2.imwrite(str(Path(out).parent / f"cut_{t:05.2f}.png"), cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
            if n >= max(want):
                break
            continue
        enc.stdin.write(np.ascontiguousarray(img).tobytes())
    dec.stdout.close()
    dec.terminate()
    if enc:
        enc.stdin.close()
        enc.wait()


def read_wav(p):
    with wave.open(str(p)) as w:
        x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
        return x.reshape(-1, w.getnchannels()).mean(1) if w.getnchannels() > 1 else x


def render_audio(path, ts, to):
    def o(t):
        return float(np.interp(t, ts, to))

    # music re-arranged on the new cut points
    M.TOTAL = TARGET
    M.CUTS = {k: round(o(v), 3) for k, v in M.CUTS.items()}
    music = M.build()                                     # (n, 2), peak 0.89
    n = int(TARGET * SR)
    mix = np.zeros((n, 2))
    m = min(n, len(music))
    mix[:m] += music[:m] * 0.42
    # SFX through the same map; cues past the end land just before it
    for f, name, off, vol in S.CUES:
        at = min(o(S.FRAME_START[f] + off), TARGET - 1.4)
        x = read_wav(ROOT / f"assets/sfx/{name}.wav")
        i = int(at * SR)
        k = min(len(x), n - i)
        if k > 0:
            mix[i:i + k] += x[:k, None] * vol
    pcm = (np.clip(mix, -1, 1) * 32767).astype(np.int16)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    return M.CUTS


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default=str(ROOT / "renders/jlm_penetrating_oil.mp4"))
    ap.add_argument("--out", default=str(ROOT / "renders/jlm_penetrating_oil_40s.mp4"))
    ap.add_argument("--stills")
    a = ap.parse_args()
    ts, to, sp, end = time_map()
    print(f"source used 0–{end:.2f}s → {TARGET:.1f}s")
    for (s0, s1, s), nxt in zip(SEGMENTS, SEGMENTS[1:] + [(end, None, None)]):
        s1 = s1 if s1 is not None else end
        print(f"  {s0:6.2f}–{s1:6.2f} ×{s:.2f} → out {np.interp(s0, ts, to):6.2f}–{np.interp(s1, ts, to):6.2f}")
    out = Path(a.out)
    if a.stills:
        render_video(a.src, out, ts, to, sp, a.stills)
        return
    tmp_v = out.with_name(out.stem + "_v.mp4")
    tmp_a = out.with_name(out.stem + "_a.wav")
    render_video(a.src, tmp_v, ts, to, sp)
    cuts = render_audio(tmp_a, ts, to)
    print("music cuts:", cuts)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(tmp_v), "-i", str(tmp_a), "-filter_complex",
                    "[1:a]volume=-3dB,alimiter=limit=0.63:attack=2:release=60:level=false,"
                    "loudnorm=I=-14:TP=-2.5:LRA=11,alimiter=limit=0.79:attack=1:release=50:level=false[a]", "-map", "0:v", "-map", "[a]", "-c:v", "copy",
                    "-c:a", "aac", "-b:a", "192k", "-ar", str(SR), "-t", f"{TARGET:.2f}",
                    "-movflags", "+faststart", str(out)], check=True)
    tmp_v.unlink(missing_ok=True)
    tmp_a.unlink(missing_ok=True)
    print("wrote", out)


if __name__ == "__main__":
    main()
