"""Soundtrack for the 20 s ATF Stop Leak & Conditioner story (blueprint style), mixed with soft SFX.

    python3 scripts/audio.py            # writes assets/bgm/story_mix.wav

Music: 100 BPM in A minor, a clean "technical" pulse — soft sub thump on the beat, quiet 16th ticks,
a dark pad (Am → F → C → G) under the problem, lifting to F → G → C (major) on the result, resolving on
the CTA. SFX come from the shared soft JLM set.
"""
import wave
from pathlib import Path

import numpy as np
from scipy.signal import butter, fftconvolve, sosfilt

ROOT = Path(__file__).resolve().parents[1]
SR = 48000
TOTAL = 20.0
BEAT = 60 / 100
RNG = np.random.default_rng(6)

# (start, notes) — midi
CHORDS = [(0.0, [45, 57, 60, 64]), (3.2, [41, 57, 60, 65]), (6.8, [48, 55, 60, 64]), (10.4, [43, 55, 59, 62]),
          (14.6, [41, 57, 60, 65]), (15.9, [43, 55, 59, 62]), (17.2, [48, 55, 60, 64])]
CUES = [(0.1, "swoosh", .16), (1.05, "plop", .22), (2.0, "plop", .18), (3.2, "whoosh", .18), (4.25, "tick", .14),
        (4.65, "tick", .14), (5.05, "tick", .14), (6.8, "whoosh", .18), (7.5, "riser", .12), (8.9, "ding", .2),
        (10.4, "swoosh", .16), (10.9, "rattle", .1), (12.2, "plop", .2), (13.2, "clock", .1), (14.6, "whoosh", .16),
        (15.0, "chime", .18), (17.2, "swoosh", .18), (18.1, "pop", .2), (18.15, "ding", .16)]


def hz(m):
    return 440 * 2 ** ((m - 69) / 12)


def filt(x, kind, f, order=2):
    return sosfilt(butter(order, f, btype=kind, fs=SR, output="sos"), x)


def env(n, a, r):
    t = np.arange(n) / SR
    return np.minimum(1, t / a) * np.clip((n / SR - t) / r, 0, 1)


def pad(notes, dur, bright):
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = np.zeros(n)
    for m in notes[1:]:
        for c in (-6, 0, 6):
            x += 2 * np.mod(hz(m) * 2 ** (c / 1200) * t + RNG.random(), 1) - 1
    x = filt(x / 9, "low", 900 + 1400 * bright)
    bass = np.sin(2 * np.pi * hz(notes[0]) * t) * 0.5
    return (x * 0.2 + bass * 0.18) * env(n, 0.5, 0.6)


def thump():
    n = int(0.3 * SR)
    t = np.arange(n) / SR
    f = 48 + 60 * np.exp(-t / 0.04)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.12) * 0.35


def tick():
    n = int(0.04 * SR)
    t = np.arange(n) / SR
    return filt(RNG.standard_normal(n), "band", (5000, 10000)) * np.exp(-t / 0.01) * 0.05


def read(p):
    with wave.open(str(p)) as w:
        x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
        return x.reshape(-1, w.getnchannels()).mean(1)


def add(buf, sig, at, gain=1.0, pan=0.0):
    i = int(at * SR)
    m = min(len(sig), len(buf) - i)
    if m > 0:
        buf[i:i + m, 0] += sig[:m] * gain * (1 - pan)
        buf[i:i + m, 1] += sig[:m] * gain * (1 + pan)


def main():
    n = int(TOTAL * SR)
    mix = np.zeros((n, 2))
    for k, (at, notes) in enumerate(CHORDS):
        end = CHORDS[k + 1][0] if k + 1 < len(CHORDS) else TOTAL
        add(mix, pad(notes, end - at + 0.5, 1.0 if at >= 14.6 else 0.0), at)
    t, k = 0.3, 0
    while t < TOTAL - 1.2:
        if k % 4 == 0 and 3.2 <= t < 17.0:
            add(mix, thump(), t, 1.0)
        if 3.2 <= t < 17.0:
            add(mix, tick(), t, 1.0 if k % 2 == 0 else 0.6, pan=0.3 if k % 2 else -0.3)
        t += BEAT / 4
        k += 1
    ir_n = int(1.8 * SR)
    ir = filt(RNG.standard_normal(ir_n), "low", 5000) * np.exp(-np.arange(ir_n) / SR / 0.5)
    ir /= np.sqrt(np.sum(ir ** 2))
    for ch in range(2):
        mix[:, ch] = mix[:, ch] * 0.8 + fftconvolve(mix[:, ch], ir)[:n] * 0.35
    tt = np.arange(n) / SR
    mix *= (np.minimum(1, tt / 0.3) * np.clip((TOTAL - tt) / 1.0, 0, 1))[:, None]
    mix *= 0.5 / np.max(np.abs(mix))
    for at, name, vol in CUES:
        add(mix, read(ROOT / f"assets/sfx/{name}.wav"), at, vol)
    out = ROOT / "assets/bgm/story_mix.wav"
    pcm = (np.clip(mix, -1, 1) * 32767).astype(np.int16)
    with wave.open(str(out), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    print("wrote", out, f"{n / SR:.2f}s")


if __name__ == "__main__":
    main()
