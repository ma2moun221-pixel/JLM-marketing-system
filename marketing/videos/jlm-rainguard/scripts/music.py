"""Music for the flying-car story: cinematic synthwave, synthesised and deterministic.

    python3 scripts/music.py            # preview: writes assets/bgm/music.wav

120 BPM, D minor (Dm–B♭–F–C). The bar grid is shifted so the lift-off (13 s) lands on
a downbeat:
  0–5      dark drone, heartbeat sub pulse, soft ticks (the weak car)
  5–9      the pad opens, plucked arpeggio with delay, light kick (the product)
  9–13     build: filter sweep, snare roll, riser, a short breath before the drop (the pour)
  13–21    drop: four-on-the-floor, side-chained supersaw chords, sub bass, lead hook (the flight)
  21–25.5  B♭–C–Dm cadence under the CTA, ring-out
Needs numpy + scipy.
"""
import wave
from pathlib import Path

import numpy as np
from scipy.signal import butter, fftconvolve, sosfilt

ROOT = Path(__file__).resolve().parents[1]
SR = 48000
BPM = 120
BEAT = 60 / BPM
GRID0 = -1.0                    # beat grid origin: downbeats at 1, 3, … 13
TOTAL = 25.5
RNG = np.random.default_rng(7)

T_PRODUCT, T_BUILD, T_GAP, T_DROP, T_FILL, T_CTA, T_END = 5.0, 9.0, 12.85, 13.0, 20.5, 21.0, 23.0

DM, BB, F, C = (62, 65, 69), (58, 62, 65), (60, 65, 69), (60, 64, 67)
# (start, end, chord, bass root)
CHORDS = [(0.0, 5.0, DM, 38), (5.0, 7.0, DM, 38), (7.0, 9.0, BB, 34), (9.0, 11.0, F, 41), (11.0, 13.0, C, 36),
          (13.0, 15.0, DM, 38), (15.0, 17.0, BB, 34), (17.0, 19.0, F, 41), (19.0, 21.0, C, 36),
          (21.0, 22.0, BB, 34), (22.0, 23.0, C, 36), (23.0, 25.5, DM, 38)]
# lead hook: (time, midi, beats)
LEAD = [(13.0, 69, 1), (13.5, 74, 1), (14.0, 77, .5), (14.25, 76, .5), (14.5, 74, 1),
        (15.0, 70, 1), (15.5, 74, 1), (16.0, 77, 1), (16.5, 79, 1),
        (17.0, 81, 1.5), (17.75, 79, .5), (18.0, 77, 1), (18.5, 76, 1),
        (19.0, 76, 1), (19.5, 79, 1), (20.0, 81, 1), (20.5, 79, 1),
        (21.0, 77, 2), (22.0, 79, 2), (23.0, 81, 4)]


def hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def tt(n):
    return np.arange(n) / SR


def filt(x, kind, f, order=2):
    return sosfilt(butter(order, f, btype=kind, fs=SR, output="sos"), x)


def sweep_lp(x, f0, f1, curve=2.0):
    """Low-pass whose cutoff glides from f0 to f1 (exponential, eased)."""
    out = np.empty_like(x)
    blk = int(0.02 * SR)
    nb = max(1, -(-len(x) // blk))
    zi = None
    for i in range(nb):
        u = (i / max(1, nb - 1)) ** curve
        sos = butter(2, f0 * (f1 / f0) ** u, btype="low", fs=SR, output="sos")
        if zi is None:
            zi = np.zeros((sos.shape[0], 2))
        y, zi = sosfilt(sos, x[i * blk:(i + 1) * blk], zi=zi)
        out[i * blk:(i + 1) * blk] = y
    return out


def adsr(n, a, d, s, r):
    t = tt(n)
    e = np.where(t < a, t / a, s + (1 - s) * np.exp(-(t - a) / d))
    return e * np.clip((n / SR - t) / r, 0, 1)


def add(buf, sig, at, gain=1.0, pan=0.0):
    i = int(round(at * SR))
    if i >= len(buf) or i < 0:
        return
    m = min(len(sig), len(buf) - i)
    buf[i:i + m, 0] += sig[:m] * gain * (1 - max(0, pan))
    buf[i:i + m, 1] += sig[:m] * gain * (1 + min(0, pan))


def saw(f, n, ph=0.0):
    return 2 * np.mod(f * tt(n) + ph, 1.0) - 1


def supersaw(m, n, voices=7, spread=22):
    x = np.zeros(n)
    for c in np.linspace(-spread, spread, voices):
        x += saw(hz(m) * 2 ** (c / 1200), n, RNG.random())
    return x / voices


def noise(n):
    return RNG.standard_normal(n)


# ---------------------------------------------------------------- voices ---
def kick():
    n = int(0.45 * SR)
    t = tt(n)
    f = 45 + 115 * np.exp(-t / 0.035)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.19)
    click = filt(noise(n), "high", 2500) * np.exp(-t / 0.004) * 0.25
    return body + click


def thump():
    n = int(0.4 * SR)
    t = tt(n)
    f = 42 + 30 * np.exp(-t / 0.05)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.16)
    return filt(np.tanh(3 * x) / np.tanh(3), "low", 400)      # harmonics: audible on phone speakers


def clap():
    n = int(0.3 * SR)
    t = tt(n)
    e = np.zeros(n)
    for o in (0, 0.01, 0.021):
        i = int(o * SR)
        e[i:] += np.exp(-(t[: n - i]) / 0.012)
    e += np.exp(-t / 0.11) * 0.5
    return filt(noise(n), "band", (900, 3800)) * e * 0.6


def snare():
    n = int(0.22 * SR)
    t = tt(n)
    return (filt(noise(n), "band", (1500, 7000)) * np.exp(-t / 0.08) * 0.7
            + np.sin(2 * np.pi * 190 * t) * np.exp(-t / 0.05) * 0.4)


def hat(open_=False):
    n = int((0.25 if open_ else 0.06) * SR)
    return filt(noise(n), "high", 7500) * np.exp(-tt(n) / (0.09 if open_ else 0.018)) * 0.5


def shaker():
    n = int(0.08 * SR)
    t = tt(n)
    return filt(noise(n), "band", (4500, 11000)) * np.minimum(1, t / 0.012) * np.exp(-t / 0.03) * 0.4


def tick():
    n = int(0.05 * SR)
    t = tt(n)
    return np.sin(2 * np.pi * 2400 * t) * np.exp(-t / 0.006) * 0.3


def pad(ch, dur, cut, cut1=None):
    n = int(dur * SR)
    x = sum(supersaw(m, n) for m in ch) + 0.5 * supersaw(ch[0] - 12, n, 5, 10)
    x = sweep_lp(x, cut, cut1) if cut1 else filt(x, "low", cut)
    return x * adsr(n, 0.35, 1.0, 0.85, 0.45) * 0.22


def pluck(m):
    n = int(0.4 * SR)
    x = saw(hz(m), n) + 0.6 * saw(hz(m) * 1.004, n, 0.3)
    return filt(x, "low", 3200) * np.exp(-tt(n) / 0.13) * 0.25


def bass(m, dur):
    n = int(dur * SR)
    t = tt(n)
    x = np.sin(2 * np.pi * hz(m) * t) + 0.45 * filt(saw(hz(m), n), "low", 380)
    return x * adsr(n, 0.004, dur * 0.8, 0.7, 0.03) * 0.5


def lead(m, beats):
    n = int(beats * BEAT * SR)
    t = tt(n)
    vib = 1 + 0.004 * np.sin(2 * np.pi * 5.5 * t) * np.clip((t - 0.25) / 0.2, 0, 1)
    f = hz(m) * vib
    x = np.zeros(n)
    for c in (-9, 0, 9):
        x += 2 * np.mod(np.cumsum(f * 2 ** (c / 1200)) / SR + RNG.random(), 1.0) - 1
    x = filt(x / 3, "low", 6000)
    return x * adsr(n, 0.012, 0.35, 0.7, 0.08) * 0.32


def riser(dur):
    n = int(dur * SR)
    u = (tt(n) / dur) ** 2
    x = sweep_lp(filt(noise(n), "high", 300), 600, 11000, 1.5) * u * 0.35
    f = 220 + 1400 * u
    return x + np.sin(2 * np.pi * np.cumsum(f) / SR) * u * 0.06


def impact():
    n = int(2.0 * SR)
    t = tt(n)
    f = 36 + 70 * np.exp(-t / 0.07)
    boom = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.6)
    crash = filt(noise(n), "high", 3000) * np.exp(-t / 0.5) * 0.18
    return boom * 0.9 + crash


def reverb_ir(seconds=2.2, decay=0.5):
    n = int(seconds * SR)
    t = tt(n)
    irs = [filt(noise(n), "low", 6000) * np.exp(-t / decay) for _ in range(2)]
    for ir in irs:
        ir[: int(0.012 * SR)] = 0                         # pre-delay
        ir /= np.sqrt(np.sum(ir ** 2))
    return irs


# ------------------------------------------------------------ arrangement ---
def beats(t0, t1, step=BEAT):
    k0 = int(np.ceil((t0 - GRID0) / step - 1e-6))
    t = GRID0 + k0 * step
    while t < t1 - 1e-6:
        yield round(t, 4), int(round((t - GRID0) / BEAT)) % 4
        t += step


def build():
    n = int(TOTAL * SR)
    mus = np.zeros((n, 2))      # side-chained
    drm = np.zeros((n, 2))
    fx = np.zeros((n, 2))       # risers / impacts, not muted by the breath
    send = np.zeros((n, 2))
    K = kick()
    kicks = []

    # pads + bass
    for s, e, ch, root in CHORDS:
        dur = e - s + 0.3
        if s < T_PRODUCT:
            p, g = (pad(ch, dur, 900), pad(ch, dur, 900)), 0.8
            add(mus, filt(np.sin(2 * np.pi * hz(root - 12) * tt(int(dur * SR))), "low", 120) * adsr(int(dur * SR), 1.0, 9, 1, 0.5), s, 0.12)
        elif s < T_BUILD:
            p, g = (pad(ch, dur, 1500), pad(ch, dur, 1500)), 1.15
        elif s < T_DROP:
            u0, u1 = (s - T_BUILD) / (T_DROP - T_BUILD), (e - T_BUILD) / (T_DROP - T_BUILD)
            p, g = (pad(ch, dur, 1500 * (5.0 ** u0), 1500 * (5.0 ** u1)), pad(ch, dur, 1500 * (5.0 ** u0), 1500 * (5.0 ** u1))), 1.2
        elif s < T_END:
            p, g = (pad(ch, dur, 6500), pad(ch, dur, 6500)), 1.5
        else:
            p, g = (pad(ch, dur, 4000), pad(ch, dur, 4000)), 1.5
        add(mus, p[0], s, g, -1.0)                        # two detuned stacks, one per side: wide
        add(mus, p[1], s, g, 1.0)
        add(send, p[0] + p[1], s, g * 0.25)
        if T_PRODUCT <= s < T_BUILD:
            add(mus, bass(root, e - s), s, 0.45)
        elif T_BUILD <= s < T_END:
            for t, _ in beats(s, e, BEAT / 2):
                if T_GAP <= t < T_DROP:
                    continue
                m = root + (12 if (s >= T_DROP and int(round((t - GRID0) / (BEAT / 2))) % 4 == 3) else 0)
                add(mus, bass(m, BEAT / 2 - 0.01), t, 0.5 if s >= T_DROP else 0.4)
        elif s >= T_END:
            add(mus, bass(root, e - s + 0.2), s, 0.45)

    # arpeggio: 16ths over the chord, ping-pong delay
    for s, e, ch, _ in CHORDS:
        if s < T_PRODUCT or s >= T_END:
            continue
        notes = list(ch) + [ch[0] + 12, ch[1] + 12]
        order = [0, 1, 2, 3, 4, 3, 2, 1]
        up = 12 if s >= T_DROP else 0
        for i, (t, _) in enumerate(beats(s, e, BEAT / 4)):
            if T_GAP <= t < T_DROP:
                continue
            g = 0.45 if s < T_BUILD else (0.5 if s < T_DROP else 0.38)
            pl = pluck(notes[order[i % 8]] + up)
            add(mus, pl, t, g, 0.2 if i % 2 else -0.2)
            add(mus, pl, t + 0.375, g * 0.33, -0.6)
            add(mus, pl, t + 0.75, g * 0.15, 0.6)
            add(send, pl, t, g * 0.3)

    # lead hook
    for t, m, b in LEAD:
        ld = lead(m, b)
        add(mus, ld, t, 1.3)
        add(mus, lead(m + 12, b), t, 0.4)                 # octave layer: presence
        add(mus, ld, t + 0.375, 0.25, 0.5)
        add(send, ld, t, 0.45)

    # drums
    for t in (0.3, 1.3, 2.3, 3.3, 4.3):                   # heartbeat
        add(drm, thump(), t, 0.3)
        add(drm, thump(), t + 0.24, 0.17)
    for t, _ in beats(1.0, T_PRODUCT, BEAT / 2):
        add(drm, tick(), t, 0.5, 0.3)
    for t, b in beats(T_PRODUCT, T_BUILD):
        if b in (0, 2):
            add(drm, K, t, 0.45)
            kicks.append(t)
        add(drm, hat(), t + BEAT / 2, 0.4, 0.3)
    for t, _ in beats(T_PRODUCT, T_BUILD, BEAT / 4):
        add(drm, shaker(), t, 0.33, -0.3)
    for t, _ in beats(T_BUILD, T_GAP):
        add(drm, K, t, 0.4 + 0.3 * (t - T_BUILD) / (T_DROP - T_BUILD))
    R0 = T_DROP - 2.0
    roll = [(R0, R0 + 1.0, BEAT / 2), (R0 + 1.0, R0 + 1.5, BEAT / 4), (R0 + 1.5, T_GAP, BEAT / 8)]
    for a, b_, st in roll:
        t = a
        while t < b_ - 1e-6:
            add(drm, snare(), t, 0.15 + 0.5 * (t - R0) / 1.85)
            t += st
    for t, b in beats(T_DROP, T_FILL):
        add(drm, K, t, 0.7)
        kicks.append(t)
        if b in (1, 3):
            add(drm, clap(), t, 0.75)
            add(send, clap(), t, 0.3)
        add(drm, hat(True), t + BEAT / 2, 0.45, 0.25)
    for i, (t, _) in enumerate(beats(T_DROP, T_FILL, BEAT / 4)):
        add(drm, hat(), t, 0.35 if i % 2 else 0.2, -0.25)
    t = T_FILL
    while t < T_CTA - 1e-6:
        add(drm, snare(), t, 0.25 + 0.4 * (t - T_FILL) / 0.5)
        t += BEAT / 4
    for t, b in beats(T_CTA, T_END):
        add(drm, K, t, 0.6)
        kicks.append(t)
        if b in (1, 3):
            add(drm, clap(), t, 0.55)
        add(drm, hat(True), t + BEAT / 2, 0.35, 0.25)
    add(drm, K, T_END, 0.55)

    # fx
    add(fx, riser(2.0), T_DROP - 2.0, 0.9)
    add(fx, riser(0.5), T_FILL, 0.6)
    for at, g in ((T_DROP, 0.7), (T_CTA, 0.55), (T_END, 0.3)):
        add(fx, impact(), at, g)
        add(send, impact(), at, g * 0.25)

    # side-chain the music to the kicks
    t = tt(n)
    sc = np.ones(n)
    for k in kicks:
        i0, i1 = int(k * SR), min(n, int((k + 0.32) * SR))
        u = (t[i0:i1] - k) / 0.32
        sc[i0:i1] = np.minimum(sc[i0:i1], 1 - 0.65 * (1 - u) ** 2)
    mus *= sc[:, None]

    # the breath before the drop
    gap = np.ones(n)
    a, b = int(T_GAP * SR), int(T_DROP * SR)
    r = int(0.012 * SR)
    gap[a:b] = 0
    gap[a - r:a] = np.linspace(1, 0, r)
    mus *= gap[:, None]
    drm *= gap[:, None]

    irs = reverb_ir()
    wet = np.stack([fftconvolve(send[:, ch], irs[ch])[:n] for ch in (0, 1)], 1)
    mix = mus + drm * 0.9 + fx * 0.8 + wet * 0.55
    mix = np.stack([filt(mix[:, ch], "high", 32) for ch in (0, 1)], 1)
    mix += np.stack([filt(mix[:, ch], "high", 5000) for ch in (0, 1)], 1) * 0.8   # air shelf

    fade = np.minimum(1, t / 0.3) * np.clip((TOTAL - t) / 1.0, 0, 1) ** 1.5
    mix *= fade[:, None]
    mix = np.tanh(mix * 1.2) / np.tanh(1.2)
    return mix / np.abs(mix).max() * 0.89


def main():
    x = build()
    out = ROOT / "assets/bgm/music.wav"
    with wave.open(str(out), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes())
    print("wrote", out, f"{len(x) / SR:.2f}s")


if __name__ == "__main__":
    main()
