"""Composite the flying effect: real cabin + tracked window replacement.

usage: comp.py base.mp4 tf.npy plate.png clouds.png out.mp4 END_SECONDS [preview_times...]
"""
import sys, subprocess, cv2, numpy as np

src, tfp, platep, cloudp, outp, END = sys.argv[1:7]
END = float(END)
previews = [float(x) for x in sys.argv[7:]]
FPS, W, H = 30, 1080, 1920
T_LIFT = 10.0
S = 1080 / 720
SUNROOF = np.array([(-60, -80), (780, -80), (780, 283), (400, 304), (160, 327), (-60, 190)], np.float32) * S
WINDSHIELD = np.array([(147, 479), (340, 467), (560, 457), (780, 452), (780, 658), (540, 651),
                       (360, 646), (200, 649), (116, 655), (127, 560)], np.float32) * S
# zones where dark / skin pixels inside the windshield are real foreground (head, mirror, wheel+hand)
PROTECT = [np.array([(-60, 380), (195, 380), (195, 700), (-60, 700)], np.float32) * S,
           np.array([(365, 430), (515, 430), (515, 565), (365, 565)], np.float32) * S,
           np.array([(150, 600), (370, 600), (370, 700), (150, 700)], np.float32) * S]

MIRROR = np.array([(386, 512), (496, 510), (500, 520), (498, 543), (488, 548), (392, 549), (382, 540), (381, 520)], np.float32) * S

plate = cv2.imread(platep).astype(np.float32) / 255
PW, PHh = plate.shape[1], plate.shape[0]
HZ = 1500
# city slightly warmer (stone), glass haze
plate[HZ:] *= np.array([0.94, 1.0, 1.05], np.float32)
plate = cv2.GaussianBlur(plate, (0, 0), 0.7)
clouds = cv2.imread(cloudp, cv2.IMREAD_UNCHANGED).astype(np.float32) / 255
clouds = np.vstack([clouds, clouds])
clouds = cv2.blur(clouds, (1, 31))  # vertical motion blur (rushing upward through clouds)

# ---- camera transforms (ref -> frame), temporally smoothed ----
tf = np.load(tfp, allow_pickle=True).item()
keys = sorted(tf)
par = []
for k in keys:
    A = tf[k]
    par.append([A[0, 0], A[1, 0], A[0, 2], A[1, 2]] if A is not None else par[-1])
par = np.array(par, np.float64)
ker = cv2.getGaussianKernel(9, 1.6).ravel()
pad = np.pad(par, ((4, 4), (0, 0)), mode="edge")
par = np.stack([np.convolve(pad[:, j], ker, mode="valid") for j in range(4)], 1)
TF = {k: np.array([[p[0], -p[1], p[2]], [p[1], p[0], p[3]]]) for k, p in zip(keys, par)}


def ss(a, b, x):
    x = np.clip((x - a) / (b - a), 0, 1)
    return x * x * (3 - 2 * x)


def horizon_y(t):
    if t < 10.9:
        return 1500 + 600 * ss(10.3, 10.9, t)
    if t < 12.0:
        return 2100 + 100 * (t - 10.9) / 1.1
    if t < 12.9:
        return 2200 - (2200 - 715) * ss(12.0, 12.9, t)
    return 715 - 30 * (t - 12.9) / 3.1


def plate_affine(t):
    zoom = 0.93 + 0.10 * ss(12.6, 16.5, t)                 # forward flight
    bank = np.deg2rad(1.8 * np.sin((t - 12.0) * 0.9))      # gentle banking
    c, s = np.cos(bank) * zoom, np.sin(bank) * zoom
    hy = horizon_y(t)
    # ref = R*(p - [PW/2, HZ]) + [540, hy]
    return np.array([[c, -s, 540 - c * PW / 2 + s * HZ], [s, c, hy - s * PW / 2 - c * HZ]])


def compose(A2, B2):
    """A2 ∘ B2 for 2x3 affines."""
    A3 = np.vstack([A2, [0, 0, 1]]); B3 = np.vstack([B2, [0, 0, 1]])
    return (A3 @ B3)[:2]


def window_mask(frame, A):
    m = np.zeros((H, W), np.uint8)
    for poly in (SUNROOF, WINDSHIELD):
        cv2.fillPoly(m, [cv2.transform(poly[None], A)[0].astype(np.int32)], 255)
    f = frame.astype(np.float32)
    y = 0.114 * f[..., 0] + 0.587 * f[..., 1] + 0.299 * f[..., 2]
    warm = (f[..., 2] - f[..., 0]) > 28
    skin = ((f[..., 2] - f[..., 0]) > 42) & (y < 190)
    fg = ((y < 120) | skin).astype(np.uint8) * 255
    zone = np.zeros((H, W), np.uint8)
    for poly in PROTECT:
        cv2.fillPoly(zone, [cv2.transform(poly[None], A)[0].astype(np.int32)], 255)
    fg = cv2.bitwise_and(fg, zone)
    fg = cv2.morphologyEx(fg, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
    fg = cv2.morphologyEx(fg, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(fg, 8)
    big = np.zeros(n, np.uint8); big[1:] = (st[1:, cv2.CC_STAT_AREA] > 4000) * 255
    fg = big[lab]
    cv2.fillPoly(fg, [cv2.transform(MIRROR[None], A)[0].astype(np.int32)], 255)
    m = cv2.bitwise_and(m, cv2.bitwise_not(fg))
    m = cv2.GaussianBlur(m.astype(np.float32) / 255, (0, 0), 2.2)
    return m


def shake(t):
    a = 16 * np.exp(-(t - T_LIFT) * 3.2) * (t >= T_LIFT)
    return (a * np.sin(t * 97.0) * 0.8 + a * np.sin(t * 61.3) * 0.5,
            a * np.sin(t * 83.0 + 1.3) * 0.9)


def process(frame, i):
    t = i / FPS
    if t < 9.5:
        return frame
    A = TF[min(max(i, keys[0]), keys[-1])]
    f = frame.astype(np.float32) / 255
    m = window_mask(frame, A)[..., None]

    white = ss(9.75, 10.0, t) * (1 - ss(10.3, 10.75, t))
    show_plate = t >= 10.3
    win = f
    if show_plate:
        P = cv2.warpAffine(plate, compose(A, plate_affine(t)), (W, H), flags=cv2.INTER_LINEAR,
                           borderMode=cv2.BORDER_REFLECT_101)
        ca = 0.92 * ss(10.35, 10.6, t) * (1 - ss(11.9, 12.45, t))
        if ca > 0:
            off = int(((t - 10.35) * 1800) % clouds.shape[0] // 2)
            Cl = clouds[off:off + PHh] if off + PHh <= clouds.shape[0] else clouds[-PHh:]
            Mc = compose(A, plate_affine(t))
            Cw = cv2.warpAffine(Cl, Mc, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT_101)
            al = Cw[..., 3:4] * ca
            P = P * (1 - al) + Cw[..., :3] * al
        P = P * 0.93 + 0.07  # glass haze
        win = P
    win = win * (1 - white) + 1.0 * white
    out = f * (1 - m) + win * m

    # bloom from the windows
    glow_amt = 0.55 * ss(9.75, 10.05, t) * (1 - ss(10.25, 11.2, t)) + 0.10 * ss(10.6, 11.5, t)
    if glow_amt > 0:
        g = cv2.GaussianBlur(cv2.resize((m * np.clip(win, 0, 1)), (W // 4, H // 4)), (0, 0), 18)
        g = cv2.resize(g, (W, H))
        out = 1 - (1 - out) * (1 - g * glow_amt)
    # cabin gets a touch brighter / cooler in the open sky
    sky_light = ss(10.4, 11.5, t)
    out = out * (1 + 0.05 * sky_light) * np.array([1 + 0.03 * sky_light, 1, 1 - 0.02 * sky_light], np.float32)

    # lift-off shake (with slight constant zoom to hide edges)
    z = 1.0 + 0.035 * ss(9.8, 10.0, t)
    sx, sy = shake(t)
    M = np.array([[z, 0, (1 - z) * W / 2 + sx], [0, z, (1 - z) * H / 2 + sy]])
    out = cv2.warpAffine(np.clip(out, 0, 1), M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT_101)
    return (out * 255 + 0.5).astype(np.uint8)


cap = cv2.VideoCapture(src)
if previews:
    tiles = []
    if previews[0] < 0:
        t = -previews[0]; i = int(round(t * FPS))
        cap.set(cv2.CAP_PROP_POS_FRAMES, i); ok, fr = cap.read()
        cv2.imwrite(outp, process(fr, i)[500:1300]); sys.exit()
    for t in previews:
        i = int(round(t * FPS))
        cap.set(cv2.CAP_PROP_POS_FRAMES, i)
        ok, fr = cap.read()
        tiles.append(cv2.resize(process(fr, i), (360, 640)))
    cv2.imwrite(outp, np.hstack(tiles))
    sys.exit()

enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}",
                        "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "12", "-preset", "medium",
                        "-pix_fmt", "yuv420p", outp], stdin=subprocess.PIPE)
n = int(END * FPS)
for i in range(n):
    ok, fr = cap.read()
    if not ok:
        break
    enc.stdin.write(process(fr, i).tobytes())
    if i % 60 == 0:
        print("frame", i, flush=True)
enc.stdin.close(); enc.wait()
