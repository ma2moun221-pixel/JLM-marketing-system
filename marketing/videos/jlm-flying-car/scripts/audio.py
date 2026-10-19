"""Soundtrack for the 20 s flying-car story (Petrol Extreme Clean): music + soft SFX, mixed.

    python3 scripts/audio.py            # writes assets/bgm/story_mix.wav

The music is the JLM house track (jlm-penetrating-oil/scripts/music.py, 112 BPM, A minor)
re-arranged on this story's cuts: hook pulse → light groove under the product and the pour →
riser into the drop on the lift-off → bright groove under the flight → lift into the CTA.
SFX are the shared soft JLM set, placed on the on-screen beats.
"""
import sys
import wave
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT.parent / "jlm-penetrating-oil/scripts"))
import music as M  # noqa: E402

SR = 48000
TOTAL = 20.0
# scene starts in compositions/story.html; "drop" lands on the lift-off
CUTS = {"hook": 0.2, "use": 3.6, "drop": 9.8, "mech": 13.2, "aud": 99.0, "use2": 99.0, "cta": 16.8}

# (time, sfx, volume)
CUES = [
    (0.15, "whoosh", 0.35), (1.50, "pop", 0.25), (3.20, "swoosh", 0.45), (3.65, "impact", 0.35),
    (4.50, "swoosh", 0.25), (4.55, "ding", 0.30), (6.35, "swoosh", 0.40), (6.40, "whoosh", 0.35),
    (7.45, "plop", 0.50), (7.95, "chime", 0.35), (9.30, "pop", 0.30), (9.50, "pop", 0.30),
    (9.80, "whoosh", 0.50), (9.82, "impact", 0.30), (13.00, "swoosh", 0.35), (13.45, "pop", 0.45),
    (14.15, "pop", 0.45), (14.85, "pop", 0.45), (16.25, "whoosh", 0.45), (16.85, "impact", 0.35),
    (17.80, "pop", 0.50), (17.85, "ding", 0.30), (18.35, "whoosh", 0.25), (19.10, "chime", 0.45),
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
