"""Soundtrack for the 10 s Air Refresh story: a calm, airy bed + the soft JLM SFX, mixed.

    python3 scripts/audio.py            # writes assets/bgm/story_mix.wav

Music: 90 BPM, F major, warm pad (Fmaj7 → Am7 → Dm9 → Bbmaj7) under a soft plucked arpeggio with
a long reverb and a quiet shaker; it opens with the focus pull and settles on the CTA.
"""
import wave
from pathlib import Path

import numpy as np
from scipy.signal import butter, fftconvolve, sosfilt

ROOT = Path(__file__).resolve().parents[1]
SR = 48000
TOTAL = 10.0
BEAT = 60 / 90
RNG = np.random.default_rng(4)

CHORDS = [(0.0, [53, 57, 60, 64]), (2.667, [57, 60, 64, 67]), (5.333, [50, 57, 60, 64]), (8.0, [46, 53, 57, 62])]
ARP = [0, 2, 3, 1, 2, 3]

# (time, sfx, volume): text in, sheen, chips, CTA
CUES = [
    (0.65, "swoosh", 0.18), (1.25, "chime", 0.22), (3.95, "swoosh", 0.16), (4.50, "pop", 0.18),
    (4.68, "pop", 0.18), (4.86, "pop", 0.18), (7.25, "swoosh", 0.18), (7.65, "chime", 0.20),
    (7.80, "ding", 0.20),
]


def hz(m):
    return 440 * 2 ** ((m - 69) / 12)


def filt(x, kind, f, order=2):
    return sosfilt(butter(order, f, btype=kind, fs=SR, output="sos"), x)


def env(n, a, r):
    t = np.arange(n) / SR
    return np.minimum(1, t / a) * np.clip((n / SR - t) / r, 0, 1)


def pad(notes, dur):
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = np.zeros(n)
    for m in notes:
        for c in (-7, 0, 7):
            f = hz(m) * 2 ** (c / 1200)
            x += 2 * np.mod(f * t + RNG.random(), 1) - 1      # saw
    return filt(x / 12, "low", 1400) * env(n, 0.8, 0.9) * 0.22


def pluck(m):
    n = int(0.9 * SR)
    t = np.arange(n) / SR
    x = np.sin(2 * np.pi * hz(m) * t) + 0.35 * np.sin(2 * np.pi * hz(m) * 2 * t) + 0.12 * np.sin(2 * np.pi * hz(m) * 3 * t)
    return x * np.exp(-t / 0.22) * np.minimum(1, t / 0.004) * 0.16


def shaker():
    n = int(0.07 * SR)
    t = np.arange(n) / SR
    return filt(RNG.standard_normal(n), "band", (5000, 11000)) * np.exp(-t / 0.025) * 0.05


def read(p):
    with wave.open(str(p)) as w:
        x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
        return x.reshape(-1, w.getnchannels()).mean(1)


def add(buf, sig, at, gain=1.0, pan=0.0):
    i = int(at * SR)
    m = min(len(sig), len(buf) - i)
    if m > 0:
        buf[i:i + m, 0] += sig[:m] * gain * (1 - pan) / 1.0
        buf[i:i + m, 1] += sig[:m] * gain * (1 + pan) / 1.0


def main():
    n = int(TOTAL * SR)
    dry = np.zeros((n, 2))
    for k, (at, notes) in enumerate(CHORDS):
        end = CHORDS[k + 1][0] if k + 1 < len(CHORDS) else TOTAL
        add(dry, pad(notes, end - at + 0.6), at, 1.0)
    # arpeggio in eighths, entering after the focus pull, one octave up
    t, i = 0.9, 0
    while t < TOTAL - 0.8:
        notes = [c for at, c in CHORDS if at <= t + 1e-6][-1]
        add(dry, pluck(notes[ARP[i % len(ARP)]] + 12), t, 1.0, pan=0.3 * np.sin(i * 0.9))
        if t > 2.6:
            add(dry, shaker(), t + BEAT / 4, 1.0, pan=-0.2)
        t += BEAT / 2
        i += 1
    # long airy reverb
    ir_n = int(2.6 * SR)
    ir_t = np.arange(ir_n) / SR
    wet = np.zeros_like(dry)
    for ch in range(2):
        ir = filt(RNG.standard_normal(ir_n), "low", 5000) * np.exp(-ir_t / 0.7)
        ir[: int(0.02 * SR)] = 0
        ir /= np.sqrt(np.sum(ir ** 2))
        wet[:, ch] = fftconvolve(dry[:, ch], ir)[:n]
    mix = dry * 0.75 + wet * 0.55
    fade = np.clip((TOTAL - np.arange(n) / SR) / 1.2, 0, 1) * np.minimum(1, np.arange(n) / SR / 0.4)
    mix *= fade[:, None]
    mix *= 0.5 / np.max(np.abs(mix))
    for at, name, vol in CUES:
        add(mix, read(ROOT / f"assets/sfx/{name}.wav"), at, vol / 2)
    out = ROOT / "assets/bgm/story_mix.wav"
    out.parent.mkdir(parents=True, exist_ok=True)
    pcm = (np.clip(mix, -1, 1) * 32767).astype(np.int16)
    with wave.open(str(out), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    print("wrote", out, f"{n / SR:.2f}s")


if __name__ == "__main__":
    main()
