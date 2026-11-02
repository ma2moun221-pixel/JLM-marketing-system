"""Soundtrack for the 30 s oil-change film (scripts/film.py): music + soft SFX, mixed.

    python3 scripts/music.py        # writes assets/bgm/film_mix.wav

120 BPM, A minor → C major, on the flying-car synth voices:
  0.0  an old engine: low drone, heartbeat thumps, riser into the product
  3.0  impact — Engine Oil Flush; soft arpeggio
  6.0  the steps: full beat (kick, clap on 2 and 4, 16th hats, 8th bass)
 14.5  the Flush result — a lift
 16.5  impact — 5W-30; beat back in at 19.5 for the pour and the dipstick
 24.5  major lift (open hats), 27.0 impact into the CTA, tail
"""
import importlib.util
import wave
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("fc_music", ROOT.parent / "jlm-flying-car/scripts/music.py")
M = importlib.util.module_from_spec(spec)
spec.loader.exec_module(M)

SR, BEAT, TOTAL = M.SR, 0.5, 30.0
AM, F, C, G, E = (57, 60, 64), (53, 57, 60), (60, 64, 67), (55, 59, 62), (52, 56, 59)
# (start, end, chord, bass root, pad cutoff from → to)
CHORDS = [(0.0, 3.0, AM, 33, 300, 700), (3.0, 6.0, F, 29, 900, 2400), (6.0, 8.5, AM, 33, 1500, 2200),
          (8.5, 11.0, F, 29, 1600, 2400), (11.0, 14.5, G, 31, 1700, 2600), (14.5, 16.5, C, 36, 2200, 3200),
          (16.5, 19.5, F, 29, 1200, 2800), (19.5, 22.0, AM, 33, 1800, 2600), (22.0, 24.5, G, 31, 1900, 2800),
          (24.5, 27.0, C, 36, 2600, 4200), (27.0, 30.0, C, 36, 3000, 1200)]
ARP = [0, 1, 2, 1]
CUES = [(0.05, "swoosh", .18), (0.6, "thump", .35), (2.95, "whoosh", .3), (5.95, "swoosh", .22), (6.3, "plop", .25),
        (8.45, "swoosh", .2), (8.6, "clock", .16), (10.95, "swoosh", .2), (11.3, "ratchet", .18), (12.8, "clank", .14),
        (14.45, "whoosh", .2), (14.6, "chime", .25), (16.45, "whoosh", .3), (19.45, "swoosh", .22), (19.7, "plop", .25),
        (21.95, "swoosh", .2), (22.3, "tick", .2), (24.45, "swoosh", .22), (24.6, "chime", .28), (26.95, "whoosh", .25),
        (27.8, "pop", .3), (27.85, "ding", .25)]


def read(p):
    with wave.open(str(p)) as w:
        x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
        return x.reshape(-1, w.getnchannels()).mean(1)


def grid(t0, t1, step):
    t = t0
    while t < t1 - 1e-6:
        yield round(t, 4)
        t += step


def build():
    n = int(TOTAL * SR)
    buf = np.zeros((n, 2))
    add = M.add
    for t0, t1, ch, root, c0, c1 in CHORDS:
        d = t1 - t0
        add(buf, M.pad(ch, d + 0.4, c0, c1), t0, 0.9)
    # an old engine: drone + heartbeat, riser into the product
    add(buf, M.pad((33, 45, 52), 3.1, 120, 380), 0.0, 1.3)
    for t in (0.0, 0.45, 1.5, 1.95):
        add(buf, M.thump(), t, 0.7)
    add(buf, M.riser(2.2), 0.8, 0.7)
    # the two product reveals
    for tr, ch in ((3.0, F), (16.5, F)):
        add(buf, M.impact(), tr, 0.9)
        for i, t in enumerate(grid(tr + 0.5, tr + 3.0, BEAT / 2)):
            add(buf, M.pluck(ch[ARP[i % 4]] + 12), t, 0.5, pan=0.4 if i % 2 else -0.4)
        add(buf, M.riser(1.0), tr + 2.0, 0.6)
    # the steps: full beat
    for a0, a1 in ((6.0, 16.5), (19.5, 27.0)):
        for t in grid(a0, a1, BEAT):
            k = int(round((t - a0) / BEAT))
            add(buf, M.kick(), t, 0.85)
            if k % 2 == 1:
                add(buf, M.clap(), t, 0.55)
        for t in grid(a0, a1, BEAT / 4):
            add(buf, M.hat(), t, 0.22, pan=0.3)
        for t in grid(a0, a1, BEAT / 2):
            root = [c for c in CHORDS if c[0] <= t][-1][3]
            add(buf, M.bass(root, BEAT / 2 * 0.85), t, 0.6)
        for i, t in enumerate(grid(a0 + 2.5, a1, BEAT / 2)):
            ch = [c for c in CHORDS if c[0] <= t][-1][2]
            add(buf, M.pluck(ch[ARP[i % 4]] + 12), t, 0.35, pan=0.3 if i % 2 else -0.3)
    for t in grid(14.5, 16.5, BEAT):
        add(buf, M.hat(True), t + BEAT / 2, 0.2, pan=-0.3)
    for t in grid(24.5, 27.0, BEAT):
        add(buf, M.hat(True), t + BEAT / 2, 0.2, pan=-0.3)
    add(buf, M.riser(1.0), 26.0, 0.6)
    # CTA
    add(buf, M.impact(), 27.0, 0.8)
    for i, t in enumerate(grid(27.0, 29.5, BEAT / 2)):
        add(buf, M.pluck(C[ARP[i % 4]] + 12), t, 0.35 * (1 - i / 10), pan=0.3 if i % 2 else -0.3)
    # space
    irL, irR = M.reverb_ir(1.8, 0.45)
    from scipy.signal import fftconvolve
    wet = np.stack([fftconvolve(buf[:, 0], irL)[:n], fftconvolve(buf[:, 1], irR)[:n]], 1)
    buf = buf * 0.85 + wet * 0.25
    t = np.arange(n) / SR
    buf *= np.clip((TOTAL - t) / 1.2, 0, 1)[:, None]
    buf *= 0.5 / np.max(np.abs(buf))
    for at, name, vol in CUES:
        x = read(ROOT / f"assets/sfx/{name}.wav")
        add(buf, x, at, vol)
    return buf


def main():
    mix = build()
    out = ROOT / "assets/bgm/film_mix.wav"
    pcm = (np.clip(mix, -1, 1) * 32767).astype(np.int16)
    with wave.open(str(out), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    print("wrote", out)


if __name__ == "__main__":
    main()
