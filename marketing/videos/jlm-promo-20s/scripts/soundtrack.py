"""Synthesised soundtrack: royalty-free by construction, timed to the edit.

0–3.2 s   heartbeat (lub-dub) under the pulse line, synced to the trace
3.2 s →   120 BPM drive: kick, sub bass, off-beat hats, dark pad
each cut  rising whoosh into a low impact (every cut lands on a downbeat)
end card  a wider final hit, then the groove thins out and fades
"""

import wave

import numpy as np

SR = 48000


def _t(n):
    return np.arange(n, dtype=np.float32) / SR


def _place(buf, x, at):
    i = int(at * SR)
    if i >= len(buf):
        return
    n = min(len(x), len(buf) - i)
    buf[i:i + n] += x[:n]


def kick(dur=0.45, f0=110, f1=42, amp=0.9):
    t = _t(int(dur * SR))
    f = f1 + (f0 - f1) * np.exp(-t * 28)
    ph = 2 * np.pi * np.cumsum(f) / SR
    env = np.exp(-t * 7.5)
    click = np.exp(-t * 400) * 0.25
    return (np.sin(ph) * env + click * np.sin(2 * np.pi * 2000 * t)) * amp


def heartbeat(amp=1.0):
    lub = kick(0.35, 80, 38, 1.0 * amp)
    dub = kick(0.30, 90, 42, 0.7 * amp)
    out = np.zeros(int(0.6 * SR), np.float32)
    _place(out, lub, 0)
    _place(out, dub, 0.18)
    return out


def hat(rng, dur=0.05, amp=0.12):
    n = int(dur * SR)
    x = rng.standard_normal(n).astype(np.float32)
    x = np.diff(x, prepend=0)  # crude high-pass
    return x * np.exp(-_t(n) * 80) * amp


def whoosh(rng, dur=0.55, amp=0.35):
    n = int(dur * SR)
    t = _t(n)
    x = rng.standard_normal(n).astype(np.float32)
    # moving one-pole low-pass: cutoff rises through the swell
    cutoff = 300 + 5000 * (t / dur) ** 2
    a = np.exp(-2 * np.pi * cutoff / SR)
    y = np.zeros(n, np.float32)
    acc = 0.0
    for i in range(n):
        acc = a[i] * acc + (1 - a[i]) * x[i]
        y[i] = acc
    env = (t / dur) ** 2.2
    env[int(n * 0.9):] *= np.linspace(1, 0, n - int(n * 0.9))
    return y * env * amp * 2.5


def impact(amp=0.8, dur=1.2):
    t = _t(int(dur * SR))
    boom = np.sin(2 * np.pi * (38 + 30 * np.exp(-t * 10)) * t) * np.exp(-t * 3.2)
    return boom * amp


def pad(dur, freqs, amp=0.05):
    t = _t(int(dur * SR))
    x = np.zeros_like(t)
    for k, f in enumerate(freqs):
        for det in (-0.6, 0.6):  # detuned pair for width
            ph = 2 * np.pi * (f + det) * t + k
            x += np.sin(ph) + 0.3 * np.sin(2 * ph)
    env = np.minimum(1, t / 0.8) * np.minimum(1, (dur - t) / 0.8)
    return x / (len(freqs) * 2) * env * amp


def write(path, duration, cuts, end_start):
    rng = np.random.default_rng(3)
    n = int(duration * SR)
    L = np.zeros(n, np.float32)
    R = np.zeros(n, np.float32)

    def both(x, at, pan=0.0):
        _place(L, x * (1 - max(pan, 0)), at)
        _place(R, x * (1 + min(pan, 0)), at)

    # heartbeat under the trace (its R peaks pass at 0.49 s and 1.11 s; the
    # third beat at 2.09 s brightens the finished line)
    both(heartbeat(0.9), 0.47)
    both(heartbeat(1.0), 1.09)
    both(heartbeat(0.75), 2.07)
    both(pad(3.4, [55.0, 82.4], 0.07), 0.0)

    # 120 BPM drive from the first cut
    start, beat = cuts[0], 0.5
    t = start
    while t < duration - 0.4:
        k = round((t - start) / beat)
        late = t >= end_start + 2.0  # thin out at the very end
        both(kick(amp=0.55 if not late else 0.3), t)
        if not late:
            both(hat(rng), t + beat / 2, pan=0.25 if k % 2 else -0.25)
        # sub bass on the root, moving A–A–F–G across each 6-beat scene
        root = [55.0, 55.0, 43.65, 43.65, 49.0, 49.0][k % 6]
        tb = _t(int(beat * 0.9 * SR))
        both(np.sin(2 * np.pi * root * tb) * np.exp(-tb * 2.2) * (0.32 if not late else 0.18), t)
        t += beat

    chords = [[110.0, 164.8, 261.6], [87.3, 130.8, 220.0], [98.0, 146.8, 246.9], [110.0, 164.8, 261.6]]
    for i, c in enumerate(cuts[:-1]):
        both(pad(3.1, chords[i % len(chords)], 0.045), c)

    for c in cuts:
        both(whoosh(rng), c - 0.5, pan=-0.15)
        both(impact(0.55 if c < end_start else 0.85), c)
    both(pad(duration - end_start, [110.0, 164.8, 220.0, 329.6], 0.06), end_start)

    mix = np.stack([L, R], axis=1)
    fade = int(0.9 * SR)
    mix[-fade:] *= np.linspace(1, 0, fade)[:, None] ** 1.5
    mix = np.tanh(mix * 1.1) * 0.85  # soft-clip glue
    pcm = (np.clip(mix, -1, 1) * 32767).astype(np.int16)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
