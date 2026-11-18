"""Procedural deep-space assets: nebula backdrop (with baked far stars) and a lit planet.

Run from this folder:  python3 space_assets.py
Outputs: public/nebula.jpg, public/planet.png
"""
import numpy as np
from PIL import Image
from scipy import ndimage

rng = np.random.default_rng(361)


def fbm(n, octaves=7, base=4, persistence=0.55, seed=0):
    r = np.random.default_rng(seed)
    out = np.zeros((n, n))
    amp, total = 1.0, 0.0
    for o in range(octaves):
        g = base * 2**o
        grid = r.random((g + 3, g + 3))
        up = ndimage.zoom(grid, n / g, order=3)[:n, :n]
        out += up * amp
        total += amp
        amp *= persistence
    out /= total
    return (out - out.min()) / (out.max() - out.min())


def warp(field, wx, wy, strength):
    n = field.shape[0]
    yy, xx = np.mgrid[0:n, 0:n].astype(np.float32)
    return ndimage.map_coordinates(field, [yy + (wy - 0.5) * strength, xx + (wx - 0.5) * strength], order=1, mode="reflect")


# ---------- Nebula ----------
N = 2400
n1 = fbm(N, seed=1)
wx, wy = fbm(N, octaves=5, seed=2), fbm(N, octaves=5, seed=3)
neb = warp(n1, wx, wy, 520)
neb2 = warp(fbm(N, seed=4), wy, wx, 380)
dust = warp(fbm(N, octaves=8, base=6, seed=5), wx, wy, 240)

yy, xx = np.mgrid[0:N, 0:N] / N
# a diagonal band of gas, like a galactic arm
band = np.exp(-(((xx - yy) * 1.0 + 0.05) ** 2) / 0.09)

dens = np.clip((neb - 0.42) * 2.6, 0, 1) ** 1.6 * (0.35 + 0.9 * band)
dens2 = np.clip((neb2 - 0.5) * 3.0, 0, 1) ** 1.8 * (0.25 + 0.8 * band)
lanes = np.clip((dust - 0.55) * 3.2, 0, 1)

base = np.array([4, 6, 16], np.float32)
violet = np.array([96, 36, 150], np.float32)
blue = np.array([24, 70, 170], np.float32)
cyan = np.array([60, 170, 210], np.float32)
pink = np.array([190, 70, 150], np.float32)

img = base + dens[..., None] * blue * 0.9 + dens2[..., None] * violet * 0.85
img += (dens * dens2)[..., None] * pink * 0.9
img += np.clip(dens - 0.55, 0, 1)[..., None] * cyan * 0.8
img *= (1 - lanes * 0.75)[..., None]

# far stars
def add_stars(img, count, smin, smax, bmin, bmax, seed):
    r = np.random.default_rng(seed)
    for _ in range(count):
        x, y = r.integers(0, N, 2)
        s = r.uniform(smin, smax)
        b = r.uniform(bmin, bmax)
        rad = int(s * 3) + 1
        x0, x1, y0, y1 = max(0, x - rad), min(N, x + rad + 1), max(0, y - rad), min(N, y + rad + 1)
        gy, gx = np.mgrid[y0:y1, x0:x1]
        g = np.exp(-((gx - x) ** 2 + (gy - y) ** 2) / (2 * (s * 0.6) ** 2)) * b
        tint = np.array([1.0, 1.0, 1.0]) if r.random() < 0.7 else np.array([0.75, 0.85, 1.0])
        img[y0:y1, x0:x1] += g[..., None] * 255 * tint


add_stars(img, 9000, 0.5, 1.1, 0.15, 0.7, 10)
add_stars(img, 900, 1.0, 1.8, 0.4, 1.0, 11)
# bright stars with spikes
r = np.random.default_rng(12)
for _ in range(36):
    x, y = r.integers(60, N - 60, 2)
    L = int(r.uniform(18, 60))
    b = r.uniform(0.5, 1.0)
    for d in range(-L, L + 1):
        f = (1 - abs(d) / L) ** 3 * b * 220
        img[y, x + d] += f
        img[y + d, x] += f
    add_stars(img[y - 40:y + 41, x - 40:x + 41], 0, 0, 0, 0, 0, 0)
    gy, gx = np.mgrid[y - 30:y + 31, x - 30:x + 31]
    img[y - 30:y + 31, x - 30:x + 31] += (np.exp(-((gx - x) ** 2 + (gy - y) ** 2) / 60) * 255 * b)[..., None]
    img[y - 30:y + 31, x - 30:x + 31] += (np.exp(-((gx - x) ** 2 + (gy - y) ** 2) / 500) * 60 * b)[..., None] * np.array([0.7, 0.8, 1.0])

img = 255 * (1 - np.exp(-img / 210))  # soft tonemap
Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).save("public/nebula.jpg", quality=92)
print("nebula ok")

# ---------- Planet ----------
TW, TH = 2048, 1024
tex = fbm(1024, octaves=8, base=3, seed=20)
tex = ndimage.zoom(tex, (1, 2), order=1)[:TH, :TW]
maria = np.clip((fbm(1024, octaves=4, base=2, seed=21) - 0.5) * 3, 0, 1)
maria = ndimage.zoom(maria, (1, 2), order=1)[:TH, :TW]
alb = 0.58 + 0.5 * (tex - 0.5) - 0.22 * maria
vy, vx = np.mgrid[0:TH, 0:TW]
for _ in range(900):
    cx, cy = r.integers(0, TW), r.integers(60, TH - 60)
    cr = r.uniform(2, 12) if r.random() < 0.93 else r.uniform(12, 34)
    d = np.sqrt(((vx - cx + TW / 2) % TW - TW / 2) ** 2 + (vy - cy) ** 2) / cr
    m = d < 1.4
    alb[m] += np.where(d[m] < 0.8, -0.05, np.where(d[m] < 1.0, 0.05 * (d[m] - 0.8) / 0.2, 0.05 * np.clip(1.4 - d[m], 0, 1) / 0.4))
alb = ndimage.gaussian_filter(alb, 1.6)

P = 1800
R = 820
c = P / 2
yy, xx = np.mgrid[0:P, 0:P].astype(np.float32)
nx, ny = (xx - c) / R, (yy - c) / R
rr = nx**2 + ny**2
inside = rr <= 1
nz = np.sqrt(np.clip(1 - rr, 0, 1))
u = (np.arctan2(nx, nz) / np.pi * 0.5 + 0.5) * (TW - 1) * 0.5 + TW * 0.25
v = (np.arcsin(np.clip(ny, -1, 1)) / np.pi + 0.5) * (TH - 1)
surf = ndimage.map_coordinates(alb, [v, u], order=1)
light = np.array([0.35, -0.75, 0.56])
light /= np.linalg.norm(light)
lam = np.clip(nx * light[0] + ny * light[1] + nz * light[2], 0, 1)
shade = lam**0.8
col = surf[..., None] * shade[..., None] * np.array([215, 222, 238])
# atmosphere: inner fresnel rim + outer halo, brightest on the lit side
lit_side = np.clip((nx * light[0] + ny * light[1]) / np.sqrt(np.maximum(rr, 1e-6)) * 0.5 + 0.5, 0, 1)
fres = (1 - nz) ** 3
atm = np.array([90, 160, 255])
col += (fres * (0.25 + 0.75 * lit_side))[..., None] * atm * 0.9
dist = np.sqrt(rr)
halo = np.exp(-np.clip(dist - 1, 0, None) * 18) * (0.2 + 0.8 * lit_side)
alpha = np.where(inside, 1.0, halo * 0.85)
col = np.where(inside[..., None], col, halo[..., None] * atm)
rgba = np.dstack([np.clip(col, 0, 255), alpha * 255]).astype(np.uint8)
Image.fromarray(rgba, "RGBA").save("public/planet.png")
print("planet ok")
