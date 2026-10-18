"""Procedural aerial plate: sunny Middle-Eastern stone city seen from ~320 m, plus sky.

Outputs plate.png (BGR, PW x PH) with the horizon at row HZ, and clouds.png (BGRA)
for a fast-moving cloud layer used during the climb.
"""
import sys, time, cv2, numpy as np

out = sys.argv[1]
rng = np.random.default_rng(7)
PW, PH, HZ = 1500, 2800, 1500
F = 640.0          # focal length in px
ALT = 320.0        # camera altitude (m)
RES = 1.5          # heightfield metres per cell
GX0, GX1, GY0, GY1 = -3600.0, 3600.0, -1200.0, 6000.0
ROT = np.deg2rad(28.0)
CR, SR = np.cos(ROT), np.sin(ROT)
NX, NY = int((GX1 - GX0) / RES), int((GY1 - GY0) / RES)


def fbm(h, w, octaves=6, base=4, seed=0):
    r = np.random.default_rng(seed)
    acc = np.zeros((h, w), np.float32)
    amp, tot = 1.0, 0.0
    for o in range(octaves):
        n = base * 2 ** o
        g = r.random((max(2, int(n * h / max(h, w))) + 1, n + 1)).astype(np.float32)
        acc += amp * cv2.resize(g, (w, h), interpolation=cv2.INTER_CUBIC)
        tot += amp
        amp *= 0.5
    return acc / tot


t0 = time.time()
# ---------------- city heightfield + albedo ----------------
xs = GX0 + (np.arange(NX) + 0.5) * RES
ys = GY0 + (np.arange(NY) + 0.5) * RES

def street_lines(coords, mean, jitter, seed):
    r = np.random.default_rng(seed)
    pos, p = [], coords[0]
    while p < coords[-1]:
        p += mean * (1 + jitter * (r.random() - 0.5))
        pos.append(p)
    return np.array(pos)

sx = street_lines(xs, 85, 0.6, 1)
sy = street_lines(ys, 95, 0.6, 2)
ix = np.searchsorted(sx, xs)      # block index per column
iy = np.searchsorted(sy, ys)
dx = np.minimum(np.abs(xs[:, None] - sx[None, :]).min(1), 1e9)  # dist to nearest street (x)
dy = np.abs(ys[:, None] - sy[None, :]).min(1) if len(sy) < 200 else None
if dy is None:
    dy = np.empty_like(ys)
    for k in range(0, len(ys), 4000):
        dy[k:k + 4000] = np.abs(ys[k:k + 4000, None] - sy[None, :]).min(1)
# main roads every ~5 streets are wider
wide_x = np.isin(ix % 5, [0]); wide_y = np.isin(iy % 6, [0])
half_x = np.where(wide_x, 13, 6.5); half_y = np.where(wide_y, 13, 6.5)
street = (dy[:, None] < half_y[:, None]) | (dx[None, :] < half_x[None, :])

# lots: subdivide blocks into ~18 m parcels
lot_x = np.floor(xs / 17.0 + 0.3 * np.sin(ys[:, None] / 37.0)).astype(np.int32)
lot_y = np.floor(ys / 19.0)[:, None].astype(np.int32)
lid = (lot_x * 7349 + lot_y * 1931 + (ix[None, :] * 31 + iy[:, None] * 17)) & 0xFFFF
hrand = (np.sin(lid * 12.9898) * 43758.5453) % 1.0
crand = (np.sin(lid * 78.233) * 12345.678) % 1.0

floors = 4 + np.floor(hrand * 6)                       # 4..9 floors
tower = hrand > 0.985
height = np.where(tower, 45 + crand * 40, floors * 3.2).astype(np.float32)
# setbacks between buildings inside a lot
gap = ((np.abs(((xs[None, :] / 17.0 + 0.3 * np.sin(ys[:, None] / 37.0)) % 1.0) - 0.5) > 0.42) |
       (np.abs(((ys / 19.0) % 1.0) - 0.5)[:, None] > 0.43))
park_noise = cv2.resize(fbm(NY // 16, NX // 16, 5, 3, seed=11), (NX, NY))
park = park_noise > 0.68
tree_noise = cv2.resize(fbm(NY // 4, NX // 4, 4, 40, seed=12), (NX, NY))
trees = ((park & (tree_noise > 0.45)) | (street & (tree_noise > 0.72)) | (gap & (tree_noise > 0.62)))

H = np.where(street | gap | park, 0.0, height)
H = np.where(trees, np.maximum(H, 7 + 4 * tree_noise), H).astype(np.float32)
terrain = (cv2.resize(fbm(NY // 32, NX // 32, 4, 2, seed=13), (NX, NY)) - 0.5) * 70
H += terrain.astype(np.float32)
H[:, :] = H  # keep contiguous

# albedo (BGR, linear-ish 0..1)
stone = np.stack([0.80 + 0.10 * crand, 0.86 + 0.08 * crand, 0.90 + 0.06 * crand], -1)
stone *= (0.82 + 0.18 * hrand)[..., None]
alb = stone.astype(np.float32)
asphalt = np.array([0.42, 0.43, 0.45], np.float32)
dirt = np.array([0.55, 0.66, 0.74], np.float32)
green = np.array([0.22, 0.42, 0.30], np.float32)
alb[street] = asphalt
alb[gap & ~street] = dirt * 0.85
alb[park & ~street] = dirt
alb[trees] = green * (0.7 + 0.5 * tree_noise[trees])[:, None]
# rooftop clutter: water tanks / solar heaters (small dark dots)
clutter = (rng.random((NY, NX)) > 0.993) & (H - terrain > 8) & ~trees
clutter = cv2.dilate(clutter.astype(np.uint8), np.ones((2, 2), np.uint8)).astype(bool)
alb[clutter] *= 0.45
roof_mark = np.zeros((NY, NX), bool)

# ambient occlusion from blurred height
Hb = cv2.GaussianBlur(H, (0, 0), 6)
ao = np.clip(1.0 - np.maximum(Hb - H, 0) / 22.0, 0.45, 1.0)
alb *= ao[..., None]
print("heightfield", round(time.time() - t0, 1), "s", NX, NY)

# ---------------- ray march ----------------
rows = np.arange(HZ + 3, PH)
cols = np.arange(PW)
cc, rr = np.meshgrid(cols, rows)
dx_ = (cc - PW / 2) / F
dz_ = -(rr - HZ) / F            # negative (looking down)
dy_ = np.ones_like(dx_)
nrm = np.sqrt(dx_ ** 2 + dy_ ** 2 + dz_ ** 2)
dx_, dy_, dz_ = dx_ / nrm, dy_ / nrm, dz_ / nrm
hmax = float(H.max()) + 1
tstart = (ALT - hmax) / -dz_
tend = (ALT - float(H.min()) + 1) / -dz_
cam_x, cam_y = 0.0, -900.0

N = dx_.size
fx, fy, fz = dx_.ravel(), dy_.ravel(), dz_.ravel()
t = tstart.ravel().copy(); te = tend.ravel()
hit = np.zeros(N, bool); wall = np.zeros(N, bool); wallside = np.zeros(N, np.int8)
hx = np.zeros(N, np.int32); hy = np.zeros(N, np.int32); hz = np.zeros(N, np.float32)
active = np.arange(N)
prev_cx = np.full(N, -1, np.int32); prev_cy = np.full(N, -1, np.int32)
it = 0
while active.size and it < 3000:
    a = active
    wx = cam_x + fx[a] * t[a]; wy = cam_y + fy[a] * t[a]; pz = ALT + fz[a] * t[a]
    px = wx * CR - wy * SR; py = wx * SR + wy * CR
    cx = np.clip(((px - GX0) / RES).astype(np.int32), 0, NX - 1)
    cy = np.clip(((py - GY0) / RES).astype(np.int32), 0, NY - 1)
    h = H[cy, cx]
    got = (pz <= h) | (t[a] >= te[a])
    if got.any():
        g = a[got]
        hit[g] = True
        hx[g] = cx[got]; hy[g] = cy[got]; hz[g] = pz[got]
        # wall if previous cell differs and its height is lower than our hit z
        pcx, pcy = prev_cx[g], prev_cy[g]
        valid = pcx >= 0
        ph = np.where(valid, H[np.maximum(pcy, 0), np.maximum(pcx, 0)], -1e9)
        w_ = valid & (pz[got] < h[got] - 0.4) & (ph < h[got] - 0.4)
        wall[g] = w_
        wallside[g] = np.where(np.abs(pcx - cx[got]) > np.abs(pcy - cy[got]), np.sign(pcx - cx[got]) * 1, np.sign(pcy - cy[got]) * 3)
    keep = ~got
    prev_cx[a[keep]] = cx[keep]; prev_cy[a[keep]] = cy[keep]
    step = np.maximum(0.6, t[a[keep]] * 0.0011)
    t[a[keep]] += step
    active = a[keep]
    it += 1
print("march", round(time.time() - t0, 1), "s, iters", it)

col = alb[hy, hx].copy()
# wall normal in grid coords -> world; lambert with sun from upper-left
gnx = np.where(np.abs(wallside) == 1, wallside, 0).astype(np.float32)
gny = np.where(np.abs(wallside) == 3, wallside / 3, 0).astype(np.float32)
wnx = gnx * CR + gny * SR; wny = -gnx * SR + gny * CR
el = np.deg2rad(52); az = np.deg2rad(200)
sx_, sy_, sz_ = np.cos(el) * np.cos(az), np.cos(el) * np.sin(az), np.sin(el)
lam_wall = np.clip(wnx * sx_ + wny * sy_, 0, 1)
sun = np.where(wall, 0.42 + 0.75 * lam_wall, 1.0).astype(np.float32)
# floor stripes / windows on walls
stripe = (np.mod(hz - (H[hy, hx] - 0), 3.2) < 0.9)
win = wall & stripe
sun = np.where(win, sun * 0.62, sun)
col *= sun[:, None]
dist = t
haze_col = np.array([0.93, 0.88, 0.82], np.float32)  # BGR pale warm haze
fog = 1 - np.exp(-dist / 2300.0)
fog = np.clip(fog * 1.15, 0, 1)
col = col * (1 - fog[:, None]) + haze_col * fog[:, None]
ground = col.reshape(len(rows), PW, 3)

# ---------------- sky ----------------
sky_rows = np.arange(HZ + 3)
e = np.clip((HZ - sky_rows) / 1500.0, 0, 1)[:, None]
top = np.array([0.86, 0.58, 0.30], np.float32)       # deep blue (BGR)
hor = np.array([0.97, 0.90, 0.80], np.float32)
skyc = hor * (1 - e[..., None] ** 0.55) + top * (e[..., None] ** 0.55)
sky = np.repeat(skyc, PW, 1)
cl = fbm(HZ + 3, PW, 7, 5, seed=21)
cl = np.clip((cl - 0.52) * 3.2, 0, 1) * (0.25 + 0.75 * e)   # fewer clouds near horizon
sky = sky * (1 - cl[..., None] * 0.85) + np.array([1, 1, 1], np.float32) * cl[..., None] * 0.85

plate = np.concatenate([sky, ground], 0)[:PH]
# soften the raymarch aliasing slightly
plate = cv2.GaussianBlur(plate, (0, 0), 0.6)
cv2.imwrite(f"{out}/plate.png", np.clip(plate * 255, 0, 255).astype(np.uint8))

# cloud layer for the climb (white puffs with alpha)
c2 = fbm(2400, 1500, 7, 4, seed=33)
a2 = np.clip((c2 - 0.55) * 4.0, 0, 1)
cloud = np.dstack([np.full_like(a2, 255)] * 3 + [a2 * 255]).astype(np.uint8)
cv2.imwrite(f"{out}/clouds.png", cloud)
print("done", round(time.time() - t0, 1), "s")
