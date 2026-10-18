"""Sound design v2: pulse, riser, lift-off impact at 10 s, wind, dive whoosh, touchdown at 17.45 s."""
import sys, wave, numpy as np

out, DUR, T = sys.argv[1], float(sys.argv[2]), 10.0
T_SW, T_TD = 15.45, 17.45
SR = 44100
n = int(DUR * SR)
t = np.arange(n) / SR
rng = np.random.default_rng(3)
L = np.zeros(n); R = np.zeros(n)


def ss(a, b, x):
    x = np.clip((x - a) / (b - a), 0, 1)
    return x * x * (3 - 2 * x)


def onepole(x, a):
    y = np.empty_like(x); acc = 0.0
    for i in range(len(x)):  # small arrays only
        acc += a * (x[i] - acc); y[i] = acc
    return y


def lp(x, cutoff):
    """cheap FFT low-pass (cutoff may be an array -> use mean)"""
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR)
    X *= 1 / (1 + (f / cutoff) ** 4)
    return np.fft.irfft(X, len(x))


def kick(at, gain=1.0):
    i0 = int(at * SR); m = int(0.5 * SR)
    if i0 >= n: return
    tt = np.arange(min(m, n - i0)) / SR
    f = 42 + 90 * np.exp(-tt * 30)
    ph = 2 * np.pi * np.cumsum(f) / SR
    s = np.sin(ph) * np.exp(-tt * 7) * gain
    L[i0:i0 + len(s)] += s; R[i0:i0 + len(s)] += s

# pulse (90 BPM) building toward lift-off
beat = 60 / 90
k = 0.0
while k < T - 0.05:
    kick(k, 0.30 + 0.35 * (k / T))
    k += beat
# hats on off-beats from 5 s
k = 5 + beat / 2
while k < T:
    i0 = int(k * SR); m = int(0.06 * SR)
    hn = rng.standard_normal(m) * np.exp(-np.arange(m) / SR * 60)
    hn = np.diff(np.r_[0, hn])  # crude high-pass
    L[i0:i0 + m] += hn * 0.05; R[i0:i0 + m] += hn * 0.05
    k += beat

# riser 7.4 -> 10.0 : noise swell + rising tone
rise = ss(7.4, 10.0, t) * (t < T)
noise = rng.standard_normal(n)
hp_noise = np.diff(np.r_[0, noise])
tone_f = 180 + 900 * ss(7.4, 10.0, t) ** 2
tone = np.sin(2 * np.pi * np.cumsum(tone_f) / SR)
L += (hp_noise * 0.10 + tone * 0.06) * rise ** 2
R += (hp_noise * 0.10 + tone * 0.06 * 0.9) * rise ** 2

# impact at lift-off: sub drop + noise burst
i0 = int(T * SR); m = int(3.0 * SR)
tt = np.arange(m) / SR
sub = np.sin(2 * np.pi * np.cumsum(70 * np.exp(-tt * 1.2) + 28) / SR) * np.exp(-tt * 1.4) * 0.9
burst = lp(rng.standard_normal(m), 900) * np.exp(-tt * 3.5) * 0.9
L[i0:i0 + m] += sub + burst; R[i0:i0 + m] += sub + burst * 0.9

# wind / air rush during flight, stronger through the clouds
wind_env = ss(10.0, 10.6, t) * (0.55 + 0.45 * ss(10.3, 10.8, t) * (1 - ss(11.9, 12.6, t)) + 0.6 * ss(14.75, T_SW, t) * (1 - ss(T_SW, 16.2, t))) * (1 - ss(16.6, T_TD + 0.3, t))
wl = lp(rng.standard_normal(n), 500); wr = lp(rng.standard_normal(n), 500)
gust = 0.75 + 0.25 * np.sin(2 * np.pi * 0.35 * t) * np.sin(2 * np.pi * 0.13 * t + 1)
L += wl * 1.3 * wind_env * gust; R += wr * 1.3 * wind_env * gust

# soft pad (A minor add9) after lift-off, swelling at the city reveal
pad_env = ss(10.2, 12.0, t) * (0.6 + 0.4 * ss(12.2, 13.0, t)) * (1 - 0.5 * ss(T_TD, T_TD + 1.0, t)) * (1 - ss(DUR - 1.0, DUR, t))
pad = np.zeros(n)
for fr, g in [(110, 1), (164.8, .8), (220, .7), (261.6, .6), (246.9, .35), (329.6, .4)]:
    for det in (-0.6, 0.6):
        pad += g * np.sin(2 * np.pi * (fr + det) * t + rng.random() * 6)
pad = lp(pad, 1200) * 0.045
L += pad * pad_env; R += pad * pad_env * 0.95
# second, softer boom on the city reveal
kick(12.55, 0.45)
# dive whoosh: falling tone + noise swell into the landing flash
dv = ss(14.75, T_SW, t) * (1 - ss(T_SW, 15.9, t))
dtone = np.sin(2 * np.pi * np.cumsum(900 - 650 * ss(14.75, 15.9, t)) / SR)
L += (hp_noise * 0.08 + dtone * 0.04) * dv ** 1.5; R += (hp_noise * 0.08 + dtone * 0.035) * dv ** 1.5
# touchdown: suspension thump + short tyre scuff
kick(T_TD, 0.95)
i0 = int(T_TD * SR); m = int(0.35 * SR); tt = np.arange(m) / SR
sc = lp(rng.standard_normal(m), 1800) * np.exp(-tt * 12) * 0.35
L[i0:i0 + m] += sc; R[i0:i0 + m] += sc

mix = np.stack([L, R], 1)
mix /= np.abs(mix).max() / 0.89
with wave.open(out, "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((mix * 32767).astype("<i2").tobytes())
