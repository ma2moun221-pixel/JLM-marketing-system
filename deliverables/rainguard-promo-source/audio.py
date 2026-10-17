"""Synthesized soundtrack for the JLM Screen Rainguard winter promo (20s, 48 kHz stereo)."""
import numpy as np
from scipy.signal import butter, sosfilt, fftconvolve
import wave, sys

SR = 48000
DUR = 20.0
N = int(SR * DUR)
t = np.arange(N) / SR
rng = np.random.default_rng(4)
L = np.zeros(N); Rr = np.zeros(N)


def filt(x, kind, f, order=4):
    return sosfilt(butter(order, f, kind, fs=SR, output='sos'), x)


def env(t0, a, d, length=None):
    """attack a, exponential decay d, starting at t0"""
    x = t - t0
    e = np.where(x < 0, 0, np.where(x < a, x / max(a, 1e-4), np.exp(-(x - a) / d)))
    return e


def add(sig, gain=1.0, pan=0.0):
    global L, Rr
    L += sig * gain * np.sqrt(0.5 * (1 - pan))
    Rr += sig * gain * np.sqrt(0.5 * (1 + pan))


def seg(t0, t1, fade=0.05):
    return np.clip((t - t0) / fade, 0, 1) * np.clip((t1 - t) / fade, 0, 1)


def ramp(points):
    xs, ys = zip(*points)
    return np.interp(t, xs, ys)


# ---------- rain ambience ----------
for ch, pan in ((0, -.6), (1, .6)):
    n = rng.standard_normal(N)
    rain = filt(n, 'bandpass', [900, 9000], 2) * 0.6 + filt(rng.standard_normal(N), 'lowpass', 400, 2) * 0.5
    # random droplet ticks
    ticks = np.zeros(N)
    idx = rng.integers(0, N, 2600)
    ticks[idx] = rng.uniform(.3, 1, idx.size)
    ticks = filt(ticks, 'highpass', 2500, 2)
    rain += ticks * 2.2
    lvl = ramp([(0, .0), (.25, .34), (2.3, .36), (3.0, .11), (16.4, .10), (17.0, .14), (19.2, .12), (20, 0)])
    add(rain * lvl, 0.55, pan)

# ---------- thunder ----------
n = rng.standard_normal(N)
crack = filt(n, 'bandpass', [300, 4000], 2) * env(1.03, .005, .12)
rumble = filt(rng.standard_normal(N), 'lowpass', 160, 4) * env(1.08, .25, 1.3) * (1 + .5 * np.sin(2 * np.pi * 3 * t))
add(crack * .55 + rumble * 2.4, 1.0)
rumble2 = filt(rng.standard_normal(N), 'lowpass', 140, 4) * env(16.62, .15, 1.0)
add(rumble2 * 1.2, 1.0)


# ---------- synth helpers ----------
def boom(t0, f0=90, f1=38, dec=.6, g=1.0):
    x = np.clip(t - t0, 0, None)
    ph = 2 * np.pi * np.cumsum(f1 + (f0 - f1) * np.exp(-x / .08)) / SR
    s = np.sin(ph) * env(t0, .004, dec)
    add(np.tanh(s * 1.6) * g)


def whoosh(t0, d=.5, g=.5, up=True):
    n = rng.standard_normal(N)
    x = np.clip((t - t0) / d, 0, 1)
    shape = np.sin(np.pi * x) ** 2 * ((t >= t0) & (t <= t0 + d))
    lo = filt(n, 'bandpass', [400, 2000], 2)
    hi = filt(n, 'bandpass', [2000, 7000], 2)
    mix = (x if up else 1 - x)
    s = (lo * (1 - mix) + hi * mix) * shape
    add(s * g, 1.0, -.4)
    add(np.roll(s, 400) * g, 1.0, .4)


def pluck(t0, f, g=.25, dec=.35, bright=1.0):
    x = t - t0
    m = x >= 0
    s = np.zeros(N)
    xs = x[m]
    s[m] = (np.sin(2 * np.pi * f * xs) + .4 * bright * np.sin(4 * np.pi * f * xs) + .15 * bright * np.sin(6 * np.pi * f * xs)) * np.exp(-xs / dec) * np.clip(xs / .003, 0, 1)
    return s * g


def note(f):
    return 440 * 2 ** ((f - 69) / 12)


fx = np.zeros(N)  # gets reverb

# ---------- hook hits (each question) ----------
for tq in (0.15, 1.05, 1.85):
    boom(tq, 110, 42, .5, .55)
    whoosh(tq - .25, .3, .28)

# riser into the reveal
x = np.clip((t - 1.9) / .95, 0, 1)
riser_n = filt(rng.standard_normal(N), 'highpass', 1500, 2) * (x ** 2) * seg(1.9, 2.85, .02)
ph = 2 * np.pi * np.cumsum(200 + 600 * x ** 2) / SR
add(riser_n * .35 + np.sin(ph) * .06 * x * seg(1.9, 2.85, .02))

# reveal impact
boom(2.85, 140, 34, 1.1, 1.0)
cym = filt(rng.standard_normal(N), 'highpass', 4000, 2) * env(2.85, .002, .9)
add(cym * .22)
whoosh(3.0, .7, .35, True)

# ---------- music bed (120 bpm, A minor: Am F C G) ----------
BPM = 120; beat = 60 / BPM; start = 2.85
chords = [[57, 60, 64], [53, 57, 60], [48, 55, 60, 64], [55, 59, 62]]
roots = [45, 41, 48, 43]
bar = 4 * beat
music_lvl = ramp([(0, 0), (2.85, 0), (3.0, 1), (16.3, 1), (16.55, .3), (16.65, 1.1), (19.0, 1), (20, 0)])
pad = np.zeros(N); bass = np.zeros(N); drums = np.zeros(N)
k = 0
tb = start
while tb < DUR:
    ci = k % 4
    t0, t1 = tb, tb + bar
    m = seg(t0, t1 + .05, .08)
    for nn in chords[ci]:
        f = note(nn + 12)
        for det in (-.12, .12):
            ph = 2 * np.pi * f * (1 + det / 100) * t
            pad += (2 * ((ph / (2 * np.pi)) % 1) - 1) * m * .05
    # bass eighths
    for e in range(8):
        te = t0 + e * beat / 2
        if te >= DUR: break
        fr = note(roots[ci] - 12 + (12 if e % 4 == 3 else 0))
        x = t - te
        mm = (x >= 0) & (x < beat / 2)
        bass[mm] += np.sin(2 * np.pi * fr * x[mm]) * np.exp(-x[mm] / .18) * .5
    k += 1
    tb += bar
pad = filt(pad, 'lowpass', 1800, 2)
add(pad * music_lvl, .9)
add(np.tanh(bass * 1.5) * music_lvl, .55)

# drums
nb = int((DUR - start) / beat) + 1
for i in range(nb):
    tb = start + i * beat
    if tb >= 19.6: break
    quiet = 1.0
    # kick every beat
    x = np.clip(t - tb, 0, None)
    ph = 2 * np.pi * np.cumsum(45 + 110 * np.exp(-x / .03)) / SR
    drums += np.sin(ph) * env(tb, .002, .16) * .8 * quiet
    # clap on 2 and 4
    if i % 2 == 1:
        drums += filt(rng.standard_normal(N), 'bandpass', [900, 3500], 2) * env(tb, .002, .09) * .45
    # hats on off-beats
    th = tb + beat / 2
    drums += filt(rng.standard_normal(N), 'highpass', 7000, 2) * env(th, .001, .03) * .25
# soften drums during the "how it works" diagram so the bloops read
drum_lvl = music_lvl * ramp([(0, 1), (6.2, 1), (6.4, .7), (10.1, .7), (10.3, 1), (20, 1)])
add(drums * drum_lvl, .7)

# ---------- transition whooshes ----------
for tw in (6.0, 10.1, 13.65, 16.35):
    whoosh(tw, .45, .45)

# ---------- UI / story sounds ----------
for i, tt in enumerate((3.5, 3.65, 4.0, 4.35)):
    fx += pluck(tt, note(76 + [0, 3, 7, 12][i]), .12, .25)
# coating shimmer 7.7-8.3
x = np.clip((t - 7.7) / .6, 0, 1)
ph = 2 * np.pi * np.cumsum(1200 + 2200 * x) / SR
fx += np.sin(ph) * .06 * seg(7.7, 8.35, .05) + filt(rng.standard_normal(N), 'highpass', 6000, 2) * .05 * seg(7.7, 8.35, .05)
# droplet landings (spread phase) and bead bloops
for tl in (6.45, 6.55, 6.6, 6.7, 6.85, 6.95):
    fx += pluck(tl, 900 + rng.uniform(-150, 150), .06, .05)
for i in range(6):
    tb = 8.2 + i * .1
    x = np.clip(t - tb, 0, None)
    ph = 2 * np.pi * np.cumsum(500 + 900 * (1 - np.exp(-x / .04))) / SR
    fx += np.sin(ph) * env(tb, .003, .07) * .14
whoosh(9.0, .55, .3, False)
# pour gurgle
n = filt(rng.standard_normal(N), 'bandpass', [250, 1400], 2)
gurg = n * (0.6 + 0.4 * np.sin(2 * np.pi * 14 * t)) * seg(11.1, 12.3, .1)
add(gurg * .22)
# step and feature plucks
for tt, nn in ((10.8, 69), (11.75, 72), (12.6, 76), (14.0, 69), (14.55, 72), (15.1, 76), (15.65, 81)):
    fx += pluck(tt, note(nn + 12), .16, .3)
# end card: logo hit, CTA chime
boom(16.6, 130, 36, 1.2, .9)
fx += filt(rng.standard_normal(N), 'highpass', 5000, 2) * env(16.6, .002, 1.2) * .12
for i, nn in enumerate((81, 84, 88, 93)):
    fx += pluck(17.7 + i * .06, note(nn), .12, .6)

# reverb on fx
ir_t = np.arange(int(SR * 1.2)) / SR
ir = rng.standard_normal(ir_t.size) * np.exp(-ir_t / .35)
ir = filt(ir, 'lowpass', 6000, 2); ir /= np.abs(ir).sum() / 6
wet = fftconvolve(fx, ir)[:N]
add(fx, .9); add(wet, .35, -.2); add(np.roll(wet, 700), .35, .2)

# master
mix = np.stack([L, Rr], 1)
mix = filt(mix.T, 'highpass', 28, 2).T
fade = np.clip((DUR - t) / .6, 0, 1)[:, None] * np.clip(t / .05, 0, 1)[:, None]
mix *= fade
mix = np.tanh(mix / np.max(np.abs(mix)) * 1.6) * .89
out = (mix * 32767).astype(np.int16)
with wave.open(sys.argv[1], 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(out.tobytes())
print('ok', out.shape)
