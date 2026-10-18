"""Flying car v3: like v2, cabin pixels untouched, flight lengthened by a boomerang of source frames.

usage: comp2.py base.mp4 tf.npy plate_ramallah.png clouds.png plate_showroom.png out END [previews...]
A negative preview time writes a single full-res frame instead of a strip.
"""
import sys, subprocess, cv2, numpy as np
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from geom import SUNROOF, WINDSHIELD, WHEEL_C, WHEEL_R, SCREEN, MIRROR, PROTECT

src, tfp, ramp, cloudp, shp, outp, END = sys.argv[1:8]
END = float(END)
previews = [float(x) for x in sys.argv[8:]]
FPS, W, H = 30, 1080, 1920
T_LIFT, T_SWITCH, T_TOUCH = 10.0, 19.45, 21.45
T_DIVE = 18.75
# source frames C..B are replayed backwards then forwards (adds 2*D-1 frames of flight)
C, B = 372, 432
D = B - C


def src_index(i):
    if i < B:
        return i
    if i < B + D:
        return 2 * B - 1 - i
    return i - 2 * D + 1

ram = cv2.imread(ramp).astype(np.float32) / 255
RPW, RHZ = ram.shape[1], 1500
ram = cv2.GaussianBlur(ram, (0, 0), 0.5)
clouds = cv2.imread(cloudp, cv2.IMREAD_UNCHANGED).astype(np.float32) / 255
clouds = cv2.blur(np.vstack([clouds, clouds]), (1, 31))
show = cv2.imread(shp).astype(np.float32) / 255
show = np.hstack([show, show[:, -320:][:, ::-1]])      # continue the facade to the right
SH_ANCHOR = (515.0, 1395.0)      # bottom of the showroom door in the photo
SH_TARGET = (420.0, 982.0)       # where it sits in the reference frame when parked

# ---- camera transforms (ref -> frame), smoothed ----
tf = np.load(tfp, allow_pickle=True).item()
keys = sorted(tf)
par = []
for k in keys:
    A = tf[k]
    par.append([A[0, 0], A[1, 0], A[0, 2], A[1, 2]] if A is not None else par[-1])
par = np.array(par, np.float64)
ker = cv2.getGaussianKernel(7, 1.2).ravel()
pad = np.pad(par, ((3, 3), (0, 0)), mode="edge")
par = np.stack([np.convolve(pad[:, j], ker, mode="valid") for j in range(4)], 1)
TF = {k: np.array([[p[0], -p[1], p[2]], [p[1], p[0], p[3]]]) for k, p in zip(keys, par)}


def ss(a, b, x):
    x = np.clip((x - a) / (b - a), 0, 1)
    return x * x * (3 - 2 * x)


def ease_in(a, b, x):
    x = np.clip((x - a) / (b - a), 0, 1)
    return x ** 2.2


def ease_out(a, b, x):
    x = np.clip((x - a) / (b - a), 0, 1)
    return 1 - (1 - x) ** 2.6


def compose(A2, B2):
    return (np.vstack([A2, [0, 0, 1]]) @ np.vstack([B2, [0, 0, 1]]))[:2]


def about(pt, z):
    return np.array([[z, 0, pt[0] * (1 - z)], [0, z, pt[1] * (1 - z)]])


# ---------------- flight plate (sky / Ramallah) ----------------
def horizon_y(t):
    if t < 10.9:
        return 1500 + 600 * ss(10.3, 10.9, t)
    if t < 12.0:
        return 2100 + 100 * (t - 10.9) / 1.1
    if t < 12.9:
        return 2200 - (2200 - 700) * ss(12.0, 12.9, t)
    if t < T_DIVE:
        return 700 - 45 * (t - 12.9) / (T_DIVE - 12.9)
    return 655 - 500 * ease_in(T_DIVE, T_SWITCH, t)          # nose down into the descent


def flight_affine(t):
    zoom = 0.93 + 0.12 * ss(12.9, T_DIVE, t)
    bank = np.deg2rad(1.6 * np.sin((t - 12.0) * 0.7))
    c, s = np.cos(bank) * zoom, np.sin(bank) * zoom
    hy = horizon_y(t)
    M = np.array([[c, -s, 540 - c * RPW / 2 + s * RHZ], [s, c, hy - s * RPW / 2 - c * RHZ]])
    dive = 1.0 + 1.1 * ease_in(T_DIVE, T_SWITCH, t)
    return compose(about((620, 840), dive), M)


# ---------------- landing plate (showroom) ----------------
def show_affine(t):
    k = ease_out(T_SWITCH, T_TOUCH + 0.45, t)
    s = 0.74 + 0.08 * k
    dy = 300 * (1 - ease_out(T_SWITCH, T_TOUCH + 0.15, t))
    if t >= T_TOUCH:   # suspension settles: the world bounces, the cabin footage stays untouched
        dy += 16 * np.exp(-(t - T_TOUCH) * 5.5) * np.sin((t - T_TOUCH) * 15)
    dx = -40 * (1 - k)
    return np.array([[s, 0, SH_TARGET[0] + dx - s * SH_ANCHOR[0]],
                     [0, s, SH_TARGET[1] + dy - s * SH_ANCHOR[1]]])


def window_mask(frame, A):
    sc = float(np.hypot(A[0, 0], A[1, 0]))
    m = np.zeros((H, W), np.uint8)
    for poly in (SUNROOF, WINDSHIELD):
        cv2.fillPoly(m, [cv2.transform(poly[None], A)[0].astype(np.int32)], 255)
    f = frame.astype(np.float32)
    y = 0.114 * f[..., 0] + 0.587 * f[..., 1] + 0.299 * f[..., 2]
    keep = np.zeros((H, W), np.uint8)                              # always-interior geometry
    for poly in (SCREEN, MIRROR):
        cv2.fillPoly(keep, [cv2.transform(poly[None], A)[0].astype(np.int32)], 255)
    rim = cv2.bitwise_and(keep, ((y > 205).astype(np.uint8) * 255))   # bright exterior caught at the edges
    rim = cv2.bitwise_and(rim, cv2.bitwise_not(cv2.erode(keep, np.ones((15, 15), np.uint8))))
    keep = cv2.bitwise_and(keep, cv2.bitwise_not(rim))
    wc = cv2.transform(np.array([[WHEEL_C]], np.float32), A)[0][0]
    cv2.circle(keep, (int(wc[0]), int(wc[1])), int(WHEEL_R * sc), 255, -1)
    # dark / skin foreground (head, hands) inside the protect zones
    skin = ((f[..., 2] - f[..., 0]) > 38) & (y < 200)
    fg = ((y < 118) | skin).astype(np.uint8) * 255
    zone = np.zeros((H, W), np.uint8)
    for poly in PROTECT:
        cv2.fillPoly(zone, [cv2.transform(poly[None], A)[0].astype(np.int32)], 255)
    fg = cv2.bitwise_and(cv2.bitwise_and(fg, zone), cv2.dilate(m, np.ones((5, 5), np.uint8)))
    fg = cv2.morphologyEx(fg, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8))
    fg = cv2.morphologyEx(fg, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(fg, 8)
    big = np.zeros(n, np.uint8); big[1:] = (st[1:, cv2.CC_STAT_AREA] > 1500) * 255
    fg = cv2.dilate(big[lab], np.ones((3, 3), np.uint8))
    keep = cv2.bitwise_or(keep, fg)
    m = cv2.bitwise_and(m, cv2.bitwise_not(keep))
    return cv2.GaussianBlur(m.astype(np.float32) / 255, (0, 0), 1.6)


def bump(t, t0, amp, decay, f1, f2):
    if t < t0:
        return 0.0, 0.0, 0.0
    e = amp * np.exp(-(t - t0) * decay)
    return e * np.sin((t - t0) * f1), e * np.sin((t - t0) * f2 + 1.1), e


def process(frame, i, si):
    t = i / FPS
    if t < 9.5:
        return frame
    A = TF[min(max(si, keys[0]), keys[-1])]
    f = frame.astype(np.float32) / 255
    m = window_mask(frame, A)[..., None]

    if t < 10.3:
        win = f
    elif t < T_SWITCH:
        M = compose(A, flight_affine(t))
        P = cv2.warpAffine(ram, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT_101)
        ca = 0.92 * ss(10.35, 10.6, t) * (1 - ss(11.9, 12.45, t))
        if ca > 0:
            off = int(((t - 10.35) * 1800) % (clouds.shape[0] // 2))
            Cw = cv2.warpAffine(clouds[off:off + ram.shape[0]], M, (W, H), flags=cv2.INTER_LINEAR,
                                borderMode=cv2.BORDER_REFLECT_101)
            al = Cw[..., 3:4] * ca
            P = P * (1 - al) + Cw[..., :3] * al
        kb = int(2 + 46 * ease_in(T_DIVE, T_SWITCH, t))
        if kb > 3:
            P = cv2.blur(P, (max(1, kb // 4), kb))
        win = P * 0.94 + 0.06
    else:
        M = compose(A, show_affine(t))
        P = cv2.warpAffine(show, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
        kb = int(40 * (1 - ss(T_SWITCH, T_SWITCH + 0.55, t)))
        if kb > 3:
            P = cv2.blur(P, (max(1, kb // 4), kb))
        win = P * 0.95 + 0.05

    white = (ss(9.75, 10.0, t) * (1 - ss(10.3, 10.75, t))
             + 0.85 * ss(T_SWITCH - 0.25, T_SWITCH, t) * (1 - ss(T_SWITCH, T_SWITCH + 0.4, t)))
    win = win * (1 - white) + white
    out = f * (1 - m) + win * m
    out = np.where(m > 0.002, out, f)   # pixels outside the glass stay bit-identical

    return (np.clip(out, 0, 1) * 255 + 0.5).astype(np.uint8)


cap = cv2.VideoCapture(src)
_cache, _pos = {}, [0]


def get(si):
    if si in _cache:
        return _cache[si]
    if si < _pos[0]:
        cap.set(cv2.CAP_PROP_POS_FRAMES, si); _pos[0] = si
    while True:
        ok, fr = cap.read()
        idx = _pos[0]; _pos[0] += 1
        if C <= idx <= B:
            _cache[idx] = fr
        if idx == si:
            return fr


if previews:
    if previews[0] < 0:
        i = int(round(-previews[0] * FPS)); si = src_index(i)
        cap.set(cv2.CAP_PROP_POS_FRAMES, si); _pos[0] = si
        cv2.imwrite(outp, process(get(si), i, si)); sys.exit()
    tiles = []
    for t in previews:
        i = int(round(t * FPS)); si = src_index(i)
        _cache.clear(); cap.set(cv2.CAP_PROP_POS_FRAMES, si); _pos[0] = si
        tiles.append(cv2.resize(process(get(si), i, si), (360, 640)))
    rows = [np.hstack(tiles[k:k + 6]) for k in range(0, len(tiles), 6)]
    w = max(r.shape[1] for r in rows)
    cv2.imwrite(outp, np.vstack([np.pad(r, ((0, 0), (0, w - r.shape[1]), (0, 0))) for r in rows]))
    sys.exit()

enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}",
                        "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "10", "-preset", "medium",
                        "-pix_fmt", "yuv420p", outp], stdin=subprocess.PIPE)
for i in range(int(END * FPS)):
    si = src_index(i)
    enc.stdin.write(process(get(si), i, si).tobytes())
    if i % 90 == 0:
        print("frame", i, "src", si, flush=True)
enc.stdin.close(); enc.wait()
