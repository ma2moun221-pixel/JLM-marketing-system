"""Soundtrack for the 15 s Automatic Transmission Flush story: music + soft SFX, mixed.

    python3 scripts/audio.py            # writes assets/bgm/story_mix.wav

The music is the JLM house track (jlm-penetrating-oil/scripts/music.py, 112 BPM, A minor)
re-arranged on this story's cuts: hook pulse → drop on the product reveal → groove under
the cleaning / results → lift into the CTA, ring-out at the end. SFX are the shared soft
JLM set, placed on the on-screen beats.
"""
import sys
import wave
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT.parent / "jlm-penetrating-oil/scripts"))
import music as M  # noqa: E402

SR = 48000
TOTAL = 15.0
# scene starts in compositions/story.html
CUTS = {"hook": 0.2, "drop": 2.55, "mech": 5.75, "aud": 9.0, "use": 99.0, "use2": 99.0, "cta": 11.95}

# (time, sfx, volume)
CUES = [
    (0.05, "whoosh", 0.45), (0.45, "pop", 0.30), (0.75, "pop", 0.30), (1.05, "pop", 0.30),
    (2.10, "swoosh", 0.45), (2.62, "impact", 0.40), (3.45, "swoosh", 0.30), (3.75, "ding", 0.30),
    (5.35, "swoosh", 0.55), (6.55, "plop", 0.40), (6.85, "plop", 0.30), (7.15, "plop", 0.25),
    (8.35, "ding", 0.30), (9.30, "pop", 0.45), (9.90, "pop", 0.45), (10.50, "pop", 0.45),
    (11.60, "swoosh", 0.45), (12.05, "impact", 0.35), (12.95, "pop", 0.50), (13.00, "ding", 0.30),
    (13.50, "whoosh", 0.25), (14.20, "chime", 0.45),
]


def read(p):
    with wave.open(str(p)) as w:
        x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
        return x.reshape(-1, w.getnchannels()).mean(1)


def main():
    M.TOTAL, M.CUTS = TOTAL, CUTS
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
