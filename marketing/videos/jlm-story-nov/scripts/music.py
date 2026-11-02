"""Warm, upbeat bed for the 19 s JLM stand story (scripts/story.py), on the flying-car synth voices.

    python3 scripts/music.py        # writes assets/music.wav

120 BPM in C major (C – G – Am – F), cuts of the story fall on beats (2.0, 8.0, 12.5 s): soft kick and clap,
16th shaker, plucked arpeggio, warm pad, bass; a gentle riser into the CTA at 15.5 s and a ring-out ending.
The clips' own crowd sound sits underneath at a low level.
"""
import importlib.util
import subprocess
import wave
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("fc_music", ROOT.parent / "jlm-flying-car/scripts/music.py")
M = importlib.util.module_from_spec(spec)
spec.loader.exec_module(M)

SR, BEAT, TOTAL = M.SR, 0.5, 19.0
C, G, AM, F = (60, 64, 67), (55, 59, 62), (57, 60, 64), (53, 57, 60)
PROG = [(C, 36), (G, 31), (AM, 33), (F, 29)]          # one chord per bar (2 s)
ARP = [0, 1, 2, 1, 2, 1]


def grid(t0, t1, step):
    t = t0
    while t < t1 - 1e-6:
        yield round(t, 4)
        t += step


def crowd(n):
    """The clips' own ambience (crowd), very low, so the stand feels alive."""
    parts = [("m1", 0.0, 2.0), ("m2", 2.0, 6.0), ("m3", 0.3, 4.5), ("m4", 2.0, 6.5)]
    out = []
    for name, t0, d in parts:
        raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(t0), "-t", str(d), "-i", str(ROOT / f"src/{name}.mov"),
                              "-map", "0:a:0", "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True).stdout
        x = np.frombuffer(raw, np.float32)
        x = np.pad(x, (0, max(0, int(d * SR) - len(x))))[: int(d * SR)]
        out.append(x)
    x = np.concatenate(out)[:n]
    return np.pad(x, (0, n - len(x)))


def main():
    n = int(TOTAL * SR)
    buf = np.zeros((n, 2))
    add = M.add
    for b, t in enumerate(grid(0.0, TOTAL - 1.0, 2.0)):
        ch, root = PROG[b % 4]
        add(buf, M.pad(ch, 2.3, 1400, 2200), t, 0.8)
        for tt in grid(t, t + 2.0, BEAT / 2):
            if t >= 2.0:
                add(buf, M.bass(root, BEAT / 2 * 0.8), tt, 0.45)
        for i, tt in enumerate(grid(t, t + 2.0, BEAT / 2)):
            add(buf, M.pluck(ch[ARP[i % 6]] + 12), tt, 0.42, pan=0.35 if i % 2 else -0.35)
    for t in grid(2.0, 17.5, BEAT):
        k = int(round((t - 2.0) / BEAT))
        add(buf, M.kick(), t, 0.55)
        if k % 2 == 1:
            add(buf, M.clap(), t, 0.35)
    for t in grid(2.0, 17.5, BEAT / 4):
        add(buf, M.shaker(), t, 0.5, pan=0.25)
    add(buf, M.riser(1.5), 14.0, 0.35)
    add(buf, M.pad(C, 3.0, 2200, 800), 17.0, 0.9)
    add(buf, M.pluck(72), 17.0, 0.5)
    irL, irR = M.reverb_ir(1.8, 0.5)
    from scipy.signal import fftconvolve
    wet = np.stack([fftconvolve(buf[:, 0], irL)[:n], fftconvolve(buf[:, 1], irR)[:n]], 1)
    buf = buf * 0.85 + wet * 0.3
    t = np.arange(n) / SR
    buf *= (np.minimum(1, t / 0.2) * np.clip((TOTAL - t) / 1.5, 0, 1))[:, None]
    buf *= 0.5 / np.max(np.abs(buf))
    amb = crowd(n)
    if np.max(np.abs(amb)) > 0:
        buf += (amb / np.max(np.abs(amb)) * 0.06)[:, None]
    pcm = (np.clip(buf, -1, 1) * 32767).astype(np.int16)
    with wave.open(str(ROOT / "assets/music.wav"), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    print("wrote assets/music.wav")


if __name__ == "__main__":
    main()
