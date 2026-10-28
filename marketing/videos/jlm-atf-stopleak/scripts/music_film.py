"""Soundtrack for the 20 s ATF cinematic story (scripts/film.py): music + soft SFX, mixed.

    python3 scripts/music_film.py        # writes assets/bgm/film_mix.wav

120 BPM, A minor → C major. The voices (kick, snare, hats, bass, pads, risers, impacts) are the
synths of jlm-flying-car/scripts/music.py; the arrangement follows the film:
  0.0  tension: low drone, heartbeat thumps, a hit on each gear jolt (0.9, 1.6), riser into 2.5
  2.5  the problem: dark half-time pulse, a sting on each red word
  5.5  impact + reveal: the product, wide pad and a soft arpeggio
  8.5  the steps: full beat (kick, clap on 2 and 4, 16th hats, bass) — the viewer is doing it
 15.0  the result: lift to C major, open hats; 17.5 impact into the CTA, then the tail
"""
import importlib.util
import wave
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("fc_music", ROOT.parent / "jlm-flying-car/scripts/music.py")
M = importlib.util.module_from_spec(spec)
spec.loader.exec_module(M)

SR, BEAT, TOTAL = M.SR, 0.5, 20.0
AM, F, C, G, E = (57, 60, 64), (53, 57, 60), (60, 64, 67), (55, 59, 62), (52, 56, 59)
# (start, end, chord, bass root, pad cutoff from → to)
CHORDS = [(0.0, 2.5, AM, 33, 300, 700), (2.5, 4.0, AM, 33, 500, 900), (4.0, 5.5, E, 28, 600, 1400),
          (5.5, 8.5, F, 29, 900, 2600), (8.5, 10.5, AM, 33, 1600, 2200), (10.5, 12.5, F, 29, 1600, 2400),
          (12.5, 15.0, G, 31, 1800, 3000), (15.0, 17.5, C, 36, 2400, 4200), (17.5, 20.0, C, 36, 3000, 1200)]
ARP = [0, 1, 2, 1]
CUES = [(0.05, "swoosh", .18), (0.9, "thump", .5), (1.6, "thump", .5), (2.65, "tick", .2), (3.25, "tick", .2),
        (3.85, "tick", .2), (5.4, "whoosh", .3), (8.45, "swoosh", .22), (8.6, "rattle", .22), (9.45, "swoosh", .2),
        (9.7, "plop", .25), (11.0, "plop", .22), (12.45, "whoosh", .22), (12.6, "clock", .16), (14.95, "swoosh", .22),
        (15.15, "chime", .3), (17.45, "whoosh", .25), (18.2, "pop", .3), (18.25, "ding", .25)]


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
    # tension: drone + heartbeat
    add(buf, M.pad((33, 45, 52), 2.6, 120, 380), 0.0, 1.3)
    for t in (0.0, 0.45, 1.5, 1.95):
        add(buf, M.thump(), t, 0.7)
    for tj in (0.9, 1.6):
        add(buf, M.impact(), tj, 0.35)
    add(buf, M.riser(2.0), 0.5, 0.7)
    # the problem: half-time kick + 8th bass
    for t in grid(2.5, 5.5, BEAT * 2):
        add(buf, M.kick(), t, 0.8)
    for t in grid(2.5, 5.5, BEAT / 2):
        root = 33 if t < 4.0 else 28
        add(buf, M.bass(root, BEAT / 2 * 0.9), t, 0.55)
    add(buf, M.riser(1.2), 4.3, 0.8)
    # reveal
    add(buf, M.impact(), 5.5, 0.9)
    for i, t in enumerate(grid(6.0, 8.5, BEAT / 2)):
        add(buf, M.pluck(F[ARP[i % 4]] + 12), t, 0.5, pan=0.4 if i % 2 else -0.4)
    add(buf, M.riser(1.0), 7.5, 0.6)
    # the steps: full beat
    for t in grid(8.5, 17.5, BEAT):
        k = int(round((t - 8.5) / BEAT))
        add(buf, M.kick(), t, 0.85)
        if k % 2 == 1:
            add(buf, M.clap(), t, 0.55)
    for t in grid(8.5, 17.5, BEAT / 4):
        add(buf, M.hat(), t, 0.22, pan=0.3)
    for t in grid(8.5, 17.5, BEAT / 2):
        root = [c for c in CHORDS if c[0] <= t][-1][3]
        add(buf, M.bass(root, BEAT / 2 * 0.85), t, 0.6)
    for t in grid(15.0, 17.5, BEAT):
        add(buf, M.hat(True), t + BEAT / 2, 0.2, pan=-0.3)
    for i, t in enumerate(grid(12.5, 17.5, BEAT / 2)):
        ch = [c for c in CHORDS if c[0] <= t][-1][2]
        add(buf, M.pluck(ch[ARP[i % 4]] + 12), t, 0.4, pan=0.3 if i % 2 else -0.3)
    add(buf, M.riser(1.0), 16.5, 0.6)
    # CTA
    add(buf, M.impact(), 17.5, 0.8)
    for i, t in enumerate(grid(17.5, 19.5, BEAT / 2)):
        add(buf, M.pluck(C[ARP[i % 4]] + 12), t, 0.35 * (1 - i / 8), pan=0.3 if i % 2 else -0.3)
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
