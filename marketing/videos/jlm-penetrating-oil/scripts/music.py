"""Music track for the JLM Penetrating Oil film (no-VO cut) — synthesised, deterministic.

    python3 scripts/music.py

112 BPM, A minor (Am–F–C–G). The arrangement follows the film:
intro swell → hook tension (pulse + dark bass) → DROP at the product reveal →
full groove through mechanism / audience → lighter groove under the how-to →
lift + final hit on the CTA, ring-out to the end.
Writes assets/bgm/music.wav and points audio_meta.json `bgm` at it; removes voices.
"""
import json
import wave
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SR = 48000
BPM = 112
BEAT = 60 / BPM
RNG = np.random.default_rng(21)
TOTAL = 71.3
CUTS = {"hook": 3.2, "drop": 8.36, "mech": 20.31, "aud": 32.61, "use": 43.77, "use2": 53.95, "cta": 61.68}
PROG = [(57, 60, 64), (53, 57, 60), (48, 52, 55), (55, 59, 62)]   # Am F C G (MIDI)
BASS = [45, 41, 36, 43]


def hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def lp(x, k):
    return np.convolve(x, np.ones(k) / k, mode="same") if k > 1 else x


def env(n, a, d):
    t = np.arange(n) / SR
    return np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / d)


def add(buf, sig, at, gain=1.0, pan=0.0):
    i = int(at * SR)
    if i >= len(buf):
        return
    m = min(len(sig), len(buf) - i)
    buf[i:i + m, 0] += sig[:m] * gain * (1 - max(0, pan))
    buf[i:i + m, 1] += sig[:m] * gain * (1 + min(0, pan))


def saw(f, n, harm=8):
    t = np.arange(n) / SR
    return sum(np.sin(2 * np.pi * f * k * t) / k for k in range(1, harm + 1))


# ---------------------------------------------------------------- voices ---
def kick():
    n = int(0.42 * SR)
    t = np.arange(n) / SR
    return np.sin(2 * np.pi * (46 * t + 95 * 0.035 * (1 - np.exp(-t / 0.035)))) * np.exp(-t / 0.16)


def clap():
    n = int(0.25 * SR)
    x = RNG.standard_normal(n)
    x = x - lp(x, 6)                       # remove lows
    e = np.zeros(n)
    for o in (0, 0.011, 0.022):
        i = int(o * SR)
        e[i:] += env(n - i, 0.001, 0.05)
    return lp(x, 2) * e * 0.5


def hat(open_=False):
    n = int((0.18 if open_ else 0.05) * SR)
    x = RNG.standard_normal(n)
    x = x - lp(x, 3)
    return x * env(n, 0.001, 0.06 if open_ else 0.012) * 0.35


def bass_note(m, dur):
    n = int(dur * SR)
    x = saw(hz(m), n, 6) + 0.6 * np.sin(2 * np.pi * hz(m) / 2 * np.arange(n) / SR)
    return lp(x, 18) * env(n, 0.005, dur * 0.7) * 0.45


def pluck(m, dur=0.22):
    n = int(dur * SR)
    return lp(saw(hz(m), n, 5), 3) * env(n, 0.002, 0.07) * 0.22


def pad_chord(ch, dur, bright=0.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = np.zeros(n)
    for m in ch:
        for det in (-0.12, 0.12):
            x += saw(hz(m + 12) * (1 + det / 100), n, 4)
    x = lp(x, int(14 - 8 * bright))
    e = np.minimum(1, t / 0.4) * np.minimum(1, (dur - t) / 0.4)
    return x * e * 0.06


def riser(dur):
    n = int(dur * SR)
    t = np.arange(n) / SR
    u = (t / t[-1]) ** 2
    x = RNG.standard_normal(n)
    return (x - lp(x, 4)) * u * 0.18 + np.sin(2 * np.pi * (180 + 900 * u) * t) * u * 0.05


def hit():
    n = int(1.6 * SR)
    t = np.arange(n) / SR
    return (np.sin(2 * np.pi * (40 + 60 * np.exp(-t / 0.08)) * t) * np.exp(-t / 0.5) * 0.8
            + lp(RNG.standard_normal(n), 3) * np.exp(-t / 0.12) * 0.25)


# ---------------------------------------------------------- arrangement ---
def section(t):
    keys = sorted(CUTS.items(), key=lambda kv: kv[1])
    name = "intro"
    for k, v in keys:
        if t >= v:
            name = k
    return name


def build():
    n = int(TOTAL * SR)
    buf = np.zeros((n, 2))
    K, C, H, HO = kick(), clap(), hat(), hat(True)
    bar = 4 * BEAT
    # chords + bass per bar
    nbars = int(TOTAL / bar) + 1
    for b in range(nbars):
        t0 = b * bar
        ch, bs = PROG[b % 4], BASS[b % 4]
        sec = section(t0)
        bright = {"intro": 0.0, "hook": 0.1, "drop": 0.6, "mech": 0.6, "aud": 0.9, "use": 0.5, "use2": 0.5, "cta": 1.0}[sec]
        add(buf, pad_chord(ch, bar + 0.3, bright), t0, 1.0 if sec != "intro" else 1.4)
        if sec == "intro":
            continue
        # bass: hook = whole notes pulsing, groove = 8th-note drive
        if sec == "hook":
            for q in range(4):
                add(buf, bass_note(bs, BEAT * 0.9), t0 + q * BEAT, 0.8)
        else:
            for e in range(8):
                m = bs + (12 if e in (3, 7) else 0)
                add(buf, bass_note(m, BEAT * 0.45), t0 + e * BEAT / 2, 0.9)
    # drums + arp on a beat grid
    tb = 0.0
    k = 0
    arp_notes = [69, 72, 76, 72, 74, 72, 69, 67]
    while tb < TOTAL - 0.5:
        sec = section(tb)
        beat_in_bar = k % 4
        if sec == "hook":
            if beat_in_bar in (0, 2):
                add(buf, K, tb, 0.7)
            add(buf, H, tb + BEAT / 2, 0.25, 0.3)
        elif sec in ("drop", "mech", "aud", "use", "use2", "cta"):
            add(buf, K, tb, 0.95)
            if beat_in_bar in (1, 3) and sec not in ("use",):
                add(buf, C, tb, 0.55)
            add(buf, H, tb, 0.3, -0.3)
            add(buf, HO if beat_in_bar == 3 else H, tb + BEAT / 2, 0.35, 0.3)
            if sec in ("mech", "aud", "cta", "use2"):
                for q in range(4):
                    m = arp_notes[(k * 4 + q) % len(arp_notes)] + (12 if sec == "cta" else 0)
                    add(buf, pluck(m), tb + q * BEAT / 4, 0.8, 0.5 * np.sin(k + q))
        tb += BEAT
        k += 1
    # transitions: risers into the drop / mech / CTA, hits on them
    add(buf, riser(2.2), 0.6, 0.5)
    for at in (CUTS["drop"], CUTS["cta"]):
        add(buf, riser(1.6), at - 1.6, 0.8)
        add(buf, hit(), at, 0.6)
    add(buf, riser(1.0), CUTS["mech"] - 1.0, 0.5)
    # end: ring-out chord, everything else fades
    t = np.arange(n) / SR
    tail = np.clip((TOTAL - 1.8 - t) / 1.5, 0, 1)
    buf *= np.maximum(tail, 0)[:, None]
    add(buf, pad_chord(PROG[0], 3.0, 1.0), TOTAL - 3.0, 2.0)
    fade_in = np.minimum(1, t / 0.6)
    buf *= fade_in[:, None]
    # gentle glue + master
    buf = np.tanh(buf * 1.4) / np.tanh(1.4)
    return buf / np.abs(buf).max() * 0.89


def main():
    x = build()
    p = ROOT / "assets/bgm/music.wav"
    pcm = (np.clip(x, -1, 1) * 32767).astype(np.int16)
    with wave.open(str(p), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    mp = ROOT / "audio_meta.json"
    meta = json.loads(mp.read_text())
    meta["voices"] = []
    meta["bgm"] = {"path": "assets/bgm/music.wav", "volume": 0.42, "source": "host", "duration_s": TOTAL}
    mp.write_text(json.dumps(meta, ensure_ascii=False, indent=2))
    print(f"music {TOTAL}s written; voices removed")


if __name__ == "__main__":
    main()
