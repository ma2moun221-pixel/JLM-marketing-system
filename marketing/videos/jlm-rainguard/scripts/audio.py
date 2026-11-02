"""Soundtrack for the 25.5 s Screen Rainguard film: music + rain ambience + soft SFX, mixed.

    python3 scripts/audio.py            # writes assets/bgm/story_mix.wav

The music is the cinematic synthwave track from the flying-car film (scripts/music.py, 120 BPM,
D minor, 25.5 s); its cuts fit this film too: drone under the rainy hook → arpeggio under the
product → build under the pour → drop on "how it works" → cadence under the CTA. A rain bed
(filtered noise + drop ticks) sits under the windshield scenes. SFX are the shared soft JLM set.
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
    (1.90, "swoosh", 0.35), (2.45, "swoosh", 0.30), (4.30, "whoosh", 0.40), (4.70, "impact", 0.30),
    (5.55, "swoosh", 0.20), (5.60, "ding", 0.30), (5.90, "pop", 0.30), (6.05, "pop", 0.30), (6.20, "pop", 0.30),
    (8.45, "whoosh", 0.30), (9.00, "pop", 0.25), (9.10, "swoosh", 0.30), (10.00, "plop", 0.45),
    (10.25, "plop", 0.30), (11.20, "chime", 0.30), (12.00, "pop", 0.20), (13.60, "spray", 0.30),
    (14.05, "ding", 0.25), (15.35, "plop", 0.45), (15.90, "swoosh", 0.25), (16.40, "swoosh", 0.30),
    (17.75, "spray", 0.40), (18.10, "swoosh", 0.35), (18.60, "swoosh", 0.30), (19.05, "chime", 0.35),
    (20.90, "whoosh", 0.30), (21.35, "impact", 0.20), (22.40, "pop", 0.50), (22.45, "ding", 0.30),
    (22.95, "whoosh", 0.25), (23.30, "swoosh", 0.20), (23.70, "chime", 0.45),
]


def rain(n):
    """Rain on glass: soft filtered noise + small random drop ticks, louder on the windshield."""
    from scipy.signal import butter, sosfilt
    rng = np.random.default_rng(3)
    x = sosfilt(butter(2, (400, 6000), btype="band", fs=SR, output="sos"), rng.standard_normal(n))
    ticks = np.zeros(n)
    for i in rng.integers(0, n - 400, 900):
        ticks[i:i + 300] += rng.uniform(.2, 1) * np.exp(-np.arange(300) / 40) * np.sin(np.arange(300) * rng.uniform(.3, .8))
    t = np.arange(n) / SR
    env = np.interp(t, [0, .4, 4.3, 4.8, 17.4, 17.8, 19.5, 21.3, 25.5],
                    [0, .30, .30, .05, .05, .26, .12, .04, .03])
    return (x * .35 + ticks * .25) * env


def read(p):
    with wave.open(str(p)) as w:
        x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
        return x.reshape(-1, w.getnchannels()).mean(1)


def main():
    mix = M.build() * 0.55                          # music bed, peak ≈ 0.49
    n = len(mix)
    mix += rain(n)[:, None]
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
