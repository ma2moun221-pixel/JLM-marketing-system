"""Music bed + soft SFX for the JLM Penetrating Oil film (all synthesised, deterministic).

    python3 scripts/sound.py

Writes assets/bgm/bed.wav, assets/sfx/*.wav and the `bgm` / `sfx` entries of
audio_meta.json (marked "source": "host"). SFX stay soft (client preference).
"""
import json
import wave
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SR = 48000
RNG = np.random.default_rng(7)


def write(path, x, stereo=True):
    path.parent.mkdir(parents=True, exist_ok=True)
    x = np.clip(x, -1, 1)
    if stereo and x.ndim == 1:
        x = np.stack([x, x], 1)
    pcm = (x * 32767).astype(np.int16)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2 if stereo else 1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


def lp(x, k):
    return np.convolve(x, np.ones(k) / k, mode="same")


def env_ad(n, a, d):
    t = np.arange(n) / SR
    return np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / d)


# ------------------------------------------------------------------ bed ---
def bed(dur, bpm=96):
    n = int(dur * SR)
    t = np.arange(n) / SR
    beat = 60 / bpm
    out = np.zeros((n, 2))
    # sub pad: A minor → F → C → G, 2 bars each
    prog = [(55.0, 65.41, 82.41), (43.65, 55.0, 65.41), (65.41, 82.41, 98.0), (49.0, 61.74, 73.42)]
    bar = 4 * beat
    for i in range(int(dur / (2 * bar)) + 1):
        f = prog[i % 4]
        s0 = int(i * 2 * bar * SR)
        m = min(n - s0, int(2 * bar * SR))
        if m <= 0:
            break
        tt = np.arange(m) / SR
        ch = sum(np.sin(2 * np.pi * fr * 2 * tt) + 0.4 * np.sin(2 * np.pi * fr * 4.004 * tt) for fr in f)
        e = np.minimum(1, tt / 0.6) * np.minimum(1, (2 * bar - tt) / 0.6)
        out[s0:s0 + m, 0] += ch * e * 0.045
        out[s0:s0 + m, 1] += ch * e * 0.045
    # soft kick on every beat, hat on off-beats, muted pluck arp on 16ths
    kick_n = int(0.35 * SR)
    kt = np.arange(kick_n) / SR
    kick = np.sin(2 * np.pi * (48 + 60 * np.exp(-kt / 0.03)) * kt) * np.exp(-kt / 0.12) * 0.32
    hat = lp(RNG.standard_normal(int(0.05 * SR)), 2) * env_ad(int(0.05 * SR), 0.001, 0.012) * 0.035
    notes = [220.0, 261.63, 329.63, 392.0, 329.63, 261.63]
    k = 0
    tb = 0.0
    while tb < dur:
        i = int(tb * SR)
        if tb > 3.0:  # the intro sting runs on pad only
            m = min(kick_n, n - i)
            out[i:i + m] += kick[:m, None]
            j = int((tb + beat / 2) * SR)
            m = min(len(hat), n - j)
            if m > 0:
                out[j:j + m, 0] += hat[:m] * 0.8
                out[j:j + m, 1] += hat[:m]
        for q in range(4):
            j = int((tb + q * beat / 4) * SR)
            pn = int(0.18 * SR)
            m = min(pn, n - j)
            if m <= 0 or tb < 1.5:
                continue
            pt = np.arange(m) / SR
            f0 = notes[k % len(notes)]
            k += 1
            pl = (np.sin(2 * np.pi * f0 * pt) + 0.3 * np.sin(2 * np.pi * 2 * f0 * pt)) * env_ad(m, 0.003, 0.05) * 0.05
            pan = 0.5 + 0.35 * np.sin(k * 0.7)
            out[j:j + m, 0] += pl * (1 - pan)
            out[j:j + m, 1] += pl * pan
        tb += beat
    fade = np.minimum(1, t / 1.0) * np.minimum(1, (dur - t) / 2.5)
    out *= fade[:, None]
    return out / np.abs(out).max() * 0.7


# ------------------------------------------------------------------ sfx ---
def sfx_all():
    s = {}
    n = int(0.6 * SR)
    w = lp(lp(RNG.standard_normal(n), 30), 30)
    s["whoosh"] = w / np.abs(w).max() * np.sin(np.linspace(0, np.pi, n)) ** 2 * 0.12
    n = int(1.2 * SR)
    t = np.arange(n) / SR
    r = lp(RNG.standard_normal(n), 12) * (t / t[-1]) ** 2 * 0.10 + np.sin(2 * np.pi * (180 + 300 * t) * t) * (t / t[-1]) ** 2 * 0.03
    s["riser"] = r * np.minimum(1, (t[-1] - t) / 0.05)
    n = int(0.16 * SR)
    t = np.arange(n) / SR
    s["tick"] = (np.sin(2 * np.pi * 480 * t) + 0.25 * np.sin(2 * np.pi * 720 * t)) * env_ad(n, 0.008, 0.05) * 0.06
    n = int(0.3 * SR)
    t = np.arange(n) / SR
    s["plop"] = np.sin(2 * np.pi * (300 + 500 * np.exp(-t / 0.04)) * t) * env_ad(n, 0.004, 0.07) * 0.10
    n = int(2.4 * SR)
    t = np.arange(n) / SR
    hiss = RNG.standard_normal(n) - lp(RNG.standard_normal(n), 3)
    s["spray"] = hiss * np.minimum(1, t / 0.08) * np.minimum(1, (t[-1] - t) / 0.4) * 0.035
    n = int(0.9 * SR)
    t = np.arange(n) / SR
    rat = np.zeros(n)
    for c in range(6):
        i = int((0.05 + c * 0.13) * SR)
        m = int(0.03 * SR)
        rat[i:i + m] += RNG.standard_normal(m) * env_ad(m, 0.0005, 0.006)
    s["rattle"] = lp(rat, 3) * 0.10
    n = int(0.5 * SR)
    rat = np.zeros(n)
    for c in range(4):
        i = int((0.02 + c * 0.1) * SR)
        m = int(0.02 * SR)
        rat[i:i + m] += np.sin(2 * np.pi * 2400 * np.arange(m) / SR) * env_ad(m, 0.0003, 0.004)
    s["ratchet"] = lp(rat, 4) * 0.12
    n = int(1.0 * SR)
    t = np.arange(n) / SR
    cl = lp(RNG.standard_normal(n), 6) * np.sin(np.linspace(0, np.pi, n)) ** 1.5
    s["cloth"] = cl / np.abs(cl).max() * 0.07
    n = int(1.6 * SR)
    t = np.arange(n) / SR
    s["chime"] = sum(np.sin(2 * np.pi * f * t) * a for f, a in [(880, 1), (1318.5, 0.5), (1760, 0.25)]) * env_ad(n, 0.01, 0.45) * 0.035
    n = int(1.4 * SR)
    t = np.arange(n) / SR
    s["strain"] = (np.sin(2 * np.pi * (70 + 8 * np.sin(2 * np.pi * 5 * t)) * t) * 0.5 + lp(RNG.standard_normal(n), 40) * 2) * np.sin(np.linspace(0, np.pi, n)) * 0.05
    return s


CUES = [  # (frame, sfx, offset_s, volume)
    (1, "riser", 0.0, 0.6), (1, "tick", 1.1, 0.6),
    (2, "tick", 1.6, 0.5), (2, "strain", 2.4, 0.7), (2, "tick", 4.2, 0.5),
    (3, "whoosh", 0.05, 0.7), (3, "tick", 7.6, 0.5), (3, "tick", 8.3, 0.5), (3, "tick", 9.1, 0.5), (3, "riser", 10.6, 0.5),
    (4, "plop", 1.2, 0.7), (4, "tick", 1.7, 0.5), (4, "tick", 5.3, 0.5), (4, "tick", 6.2, 0.5), (4, "tick", 7.9, 0.5),
    (5, "tick", 1.6, 0.5), (5, "tick", 2.8, 0.5), (5, "tick", 3.9, 0.5), (5, "tick", 7.4, 0.45), (5, "tick", 8.0, 0.45),
    (5, "tick", 9.0, 0.45), (5, "whoosh", 10.3, 0.7),
    (6, "rattle", 1.9, 0.7), (6, "spray", 3.9, 0.7), (6, "tick", 7.6, 0.35), (6, "tick", 8.3, 0.35), (6, "tick", 9.0, 0.35),
    (7, "ratchet", 2.8, 0.7), (7, "ratchet", 3.7, 0.7), (7, "cloth", 4.9, 0.8), (7, "whoosh", 7.2, 0.6),
    (8, "whoosh", 0.0, 0.5), (8, "tick", 3.8, 0.5), (8, "chime", 7.6, 0.6),
]


def main():
    meta_p = ROOT / "audio_meta.json"
    meta = json.loads(meta_p.read_text())
    total = 3.2 + sum(v["duration_s"] for v in meta["voices"])
    write(ROOT / "assets/bgm/bed.wav", bed(total + 0.5))
    sfx = sfx_all()
    for name, x in sfx.items():
        write(ROOT / f"assets/sfx/{name}.wav", x)
    meta["bgm"] = {"path": "assets/bgm/bed.wav", "volume": 0.16, "source": "host", "duration_s": round(total + 0.5, 2)}
    meta["sfx"] = [{"frame": f, "file": f"assets/sfx/{n}.wav", "offset_s": o, "duration_s": round(len(sfx[n]) / SR, 2),
                    "volume": v, "source": "host"} for f, n, o, v in CUES]
    meta.setdefault("bgm_pending", False)
    meta_p.write_text(json.dumps(meta, ensure_ascii=False, indent=2))
    print(f"bed {total + 0.5:.1f}s · {len(sfx)} sfx · {len(CUES)} cues")


if __name__ == "__main__":
    main()
