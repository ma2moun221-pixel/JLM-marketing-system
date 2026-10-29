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
    # --- retention layer: clear but never harsh (all low-passed, soft attacks) ---
    n = int(0.55 * SR)
    t = np.arange(n) / SR
    sw = lp(RNG.standard_normal(n), 8)
    sweep = np.sin(2 * np.pi * (300 + 900 * (t / t[-1])) * t) * 0.15
    s["swoosh"] = (sw / np.abs(sw).max() + sweep) * np.sin(np.linspace(0, np.pi, n)) ** 3 * 0.16
    n = int(1.3 * SR)
    t = np.arange(n) / SR
    up = (t / t[-1]) ** 2.2
    r = lp(RNG.standard_normal(n), 10) * up * 0.12 + np.sin(2 * np.pi * (140 + 520 * up) * t) * up * 0.05
    s["riser_long"] = r * np.minimum(1, (t[-1] - t) / 0.03)
    n = int(0.9 * SR)
    t = np.arange(n) / SR
    s["impact"] = (np.sin(2 * np.pi * (45 + 70 * np.exp(-t / 0.05)) * t) * np.exp(-t / 0.28) * 0.30
                   + lp(RNG.standard_normal(n), 25) * np.exp(-t / 0.06) * 0.10)
    n = int(1.1 * SR)
    t = np.arange(n) / SR
    s["ding"] = sum(np.sin(2 * np.pi * f * t) * a for f, a in [(1046.5, 1), (1568, 0.35), (2093, 0.12)]) * env_ad(n, 0.004, 0.28) * 0.07
    n = int(0.22 * SR)
    t = np.arange(n) / SR
    s["pop"] = np.sin(2 * np.pi * (260 + 520 * (1 - np.exp(-t / 0.02))) * t) * env_ad(n, 0.003, 0.05) * 0.10
    n = int(0.45 * SR)
    t = np.arange(n) / SR
    cl = sum(np.sin(2 * np.pi * f * t) * np.exp(-t / d) for f, d in [(620, 0.09), (1430, 0.05), (2710, 0.03)])
    s["clank"] = lp(cl, 3) * np.minimum(1, t / 0.002) * 0.06
    n = int(0.25 * SR)
    t = np.arange(n) / SR
    s["crack"] = lp(RNG.standard_normal(n), 2) * np.exp(-t / 0.03) * 0.10
    n = int(0.09 * SR)
    t = np.arange(n) / SR
    s["clock"] = np.sin(2 * np.pi * 1800 * t) * env_ad(n, 0.0008, 0.012) * 0.05
    n = int(0.6 * SR)
    t = np.arange(n) / SR
    s["thump"] = np.sin(2 * np.pi * 52 * t) * env_ad(n, 0.006, 0.16) * 0.28
    return s


FRAME_START = {1: 0.0, 2: 3.2, 3: 8.36, 4: 20.31, 5: 32.61, 6: 43.77, 7: 53.95, 8: 61.68}

CUES = [  # (frame, sfx, offset_s, volume) — retention design: every cut, reveal and step is marked
    # 1 · intro sting
    (1, "riser", 0.0, 0.55), (1, "impact", 1.0, 0.55), (1, "ding", 1.05, 0.45),
    # 2 · hook — tension, the wrench slips, the promise
    (2, "thump", 0.15, 0.6), (2, "thump", 1.55, 0.6), (2, "clank", 2.55, 0.8), (2, "clank", 2.85, 0.7),
    (2, "crack", 3.0, 0.7), (2, "clank", 3.15, 0.6), (2, "riser_long", 3.3, 0.55), (2, "ding", 4.2, 0.5),
    # 3 · product reveal + orbiting benefits, then dive into the drop
    (3, "impact", 0.05, 0.6), (3, "swoosh", 0.4, 0.6), (3, "ding", 1.6, 0.45),
    (3, "pop", 7.6, 0.6), (3, "pop", 8.3, 0.6), (3, "pop", 9.1, 0.6), (3, "riser_long", 9.75, 0.6),
    # 4 · mechanism — drop, numbered steps
    (4, "swoosh", 0.0, 0.7), (4, "plop", 1.2, 0.7), (4, "ding", 1.7, 0.45), (4, "ding", 5.15, 0.45),
    (4, "ding", 6.2, 0.45), (4, "ding", 7.8, 0.45), (4, "swoosh", 10.8, 0.55),
    # 5 · hub — nodes and chips, then the wipe
    (5, "pop", 1.6, 0.6), (5, "pop", 2.8, 0.6), (5, "pop", 3.9, 0.6), (5, "pop", 7.4, 0.55),
    (5, "pop", 8.0, 0.55), (5, "pop", 9.0, 0.55), (5, "swoosh", 10.4, 0.8),
    # 6 · how to use 1 — shake, spray, timer
    (6, "swoosh", 0.0, 0.5), (6, "ding", 1.8, 0.45), (6, "rattle", 1.95, 0.8), (6, "ding", 3.7, 0.45),
    (6, "spray", 4.15, 0.8), (6, "ding", 7.3, 0.45),
] + [(6, "clock", 7.9 + 0.33 * k, 0.6) for k in range(7)] + [
    # 7 · how to use 2 — wrench turns free, cloth wipe
    (7, "ding", 0.6, 0.45), (7, "ratchet", 2.8, 0.8), (7, "ratchet", 3.7, 0.8), (7, "ding", 4.6, 0.45),
    (7, "cloth", 4.9, 0.8), (7, "riser_long", 6.4, 0.55),
    # 8 · CTA — land, press, sting
    (8, "swoosh", 0.0, 0.6), (8, "impact", 0.45, 0.55), (8, "pop", 3.75, 0.7), (8, "ding", 3.8, 0.4),
    (8, "chime", 7.5, 0.7),
]


def main():
    meta_p = ROOT / "audio_meta.json"
    meta = json.loads(meta_p.read_text())
    total = 3.2 + sum(v["duration_s"] for v in meta["voices"])
    write(ROOT / "assets/bgm/bed.wav", bed(total + 0.5))
    sfx = sfx_all()
    for name, x in sfx.items():
        write(ROOT / f"assets/sfx/{name}.wav", x)
    meta["bgm"] = {"path": "assets/bgm/bed.wav", "volume": 0.18, "source": "host", "duration_s": round(total + 0.5, 2)}
    meta["sfx"] = [{"frame": f, "file": f"assets/sfx/{n}.wav", "offset_s": o, "duration_s": round(len(sfx[n]) / SR, 2),
                    "volume": v, "source": "host"} for f, n, o, v in CUES]
    meta.setdefault("bgm_pending", False)
    meta_p.write_text(json.dumps(meta, ensure_ascii=False, indent=2))
    print(f"bed {total + 0.5:.1f}s · {len(sfx)} sfx · {len(CUES)} cues")


if __name__ == "__main__":
    main()
