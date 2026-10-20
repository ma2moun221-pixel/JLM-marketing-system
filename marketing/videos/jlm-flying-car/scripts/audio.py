"""Soundtrack for the 25.5 s flying-car story (Petrol Extreme Clean): music + soft SFX, mixed.

    python3 scripts/audio.py            # writes assets/bgm/story_mix.wav

The music is this story's own track (scripts/music.py: cinematic synthwave, 120 BPM,
D minor, 25.5 s) built on the cuts: heartbeat drone → arpeggio under the product → build and a
breath before the drop on the lift-off → side-chained supersaws under the flight → cadence
under the CTA. SFX are the shared soft JLM set, placed on the on-screen beats.
"""
import sys
import wave
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import music as M  # noqa: E402

SR = 48000
TOTAL = 25.5

# (time, sfx, volume)
CUES = [
    (0.15, "whoosh", 0.35), (1.60, "pop", 0.25), (2.30, "thump", 0.30), (3.30, "thump", 0.30),
    (4.35, "whoosh", 0.45), (4.85, "impact", 0.30), (5.70, "swoosh", 0.25), (5.75, "ding", 0.30),
    (8.30, "swoosh", 0.35), (8.40, "whoosh", 0.40), (9.15, "thump", 0.20), (9.69, "plop", 0.50),
    (10.35, "chime", 0.35), (12.55, "pop", 0.30), (12.75, "pop", 0.30), (13.00, "whoosh", 0.45),
    (16.90, "swoosh", 0.35), (17.40, "pop", 0.45), (18.10, "pop", 0.45), (18.80, "pop", 0.45),
    (20.85, "whoosh", 0.45), (21.35, "impact", 0.20), (22.40, "pop", 0.50), (22.45, "ding", 0.30),
    (22.95, "whoosh", 0.25), (23.30, "swoosh", 0.20), (23.70, "chime", 0.45),
]


def read(p):
    with wave.open(str(p)) as w:
        x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
        return x.reshape(-1, w.getnchannels()).mean(1)


def main():
    mix = M.build() * 0.55                          # music bed, peak ≈ 0.49
    n = len(mix)
    for at, name, vol in CUES:
        x = read(ROOT / f"assets/sfx/{name}.wav")
        i = int(at * SR)
        m = min(len(x), n - i)
        mix[i:i + m] += x[:m, None] * vol
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
