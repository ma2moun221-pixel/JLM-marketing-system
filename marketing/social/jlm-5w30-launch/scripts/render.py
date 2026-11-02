"""JLM 5W-30 «launch» post (1080×1350): the bottle takes off like a rocket beside a lit, curved ramp at night.

    python3 scripts/render.py        # writes out/jlm_5w30_launch.png

Built from scratch (no stock or third-party photo): a night runway, one continuous concrete track (a flat run-out on
the ground that rises into a curved ramp) with JLM-yellow LED edges and a steel truss, the client's 5W-30 bottle (assets/oil5w30.png, cut out earlier) tilted for
take-off with a warm rim light, four thrust jets and a billowing smoke plume lit from inside, then the copy
in the JLM fonts: «انطلق بأداء أعلى» / «زيت محرك JLM 5W-30», the logo and jlmstore.com.
"""
import math
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[2]
sys.path.insert(0, str(REPO / "marketing/videos/jlm-care-edit/scripts"))
import edit_v3 as V  # noqa: E402

E, R = V.E, V.R
W, H = 1080, 1350
HOR = 1150
YEL = np.array([250, 184, 23], np.float32) / 255
WARM = np.array([1.0, 0.62, 0.22], np.float32)
RNG = np.random.default_rng(12)
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)


def noise(scale, octaves=5, seed=0):
    rng = np.random.default_rng(seed)
    out = np.zeros((H, W), np.float32)
    amp, tot = 1.0, 0.0
    for o in range(octaves):
        s = max(2, int(scale / 2 ** o))
        n = rng.normal(0, 1, (H // s + 2, W // s + 2)).astype(np.float32)
        out += cv2.resize(cv2.GaussianBlur(n, (0, 0), 1.0), (W, H), interpolation=cv2.INTER_CUBIC) * amp
        tot += amp
        amp *= 0.55
    out /= tot
    return (out - out.min()) / (out.max() - out.min())


def background():
    sky = np.clip(yy / HOR, 0, 1)[..., None]
    f = np.array([0.012, 0.013, 0.016]) * (1 - sky) + np.array([0.05, 0.048, 0.05]) * sky
    g = np.clip((yy - HOR) / (H - HOR), 0, 1)[..., None]
    ground = np.array([0.07, 0.066, 0.064]) * (1 - g) + np.array([0.025, 0.025, 0.027]) * g
    f = np.where((yy >= HOR)[..., None], ground, f).astype(np.float32)
    f += (noise(40, 4, 3)[..., None] - 0.5) * 0.02 * (yy >= HOR)[..., None]
    lights = np.zeros((H, W, 3), np.float32)
    for x in np.linspace(20, W - 20, 26):                  # distant runway / horizon lights
        x += RNG.uniform(-12, 12)
        c = WARM if RNG.random() < 0.6 else np.array([1.0, 0.85, 0.6])
        cv2.circle(lights, (int(x), int(HOR + RNG.uniform(-6, 2))), int(RNG.uniform(2, 4)), (c * RNG.uniform(.5, 1)).tolist(), -1, cv2.LINE_AA)
    f += cv2.GaussianBlur(lights, (0, 0), 1.0) + cv2.GaussianBlur(lights, (0, 0), 12) * 1.5
    return f


def bez(p, t):
    p0, p1, p2, p3 = [np.array(q, np.float32) for q in p]
    return ((1 - t) ** 3)[:, None] * p0 + (3 * (1 - t) ** 2 * t)[:, None] * p1 + (3 * (1 - t) * t ** 2)[:, None] * p2 + (t ** 3)[:, None] * p3


def ramp(f):
    """Curved concrete ramp rising from the ground on the right, LED edges in JLM yellow, steel truss behind."""
    # one continuous track: a flat run-out on the ground coming towards the camera, a smooth quarter-pipe
    # foot, then the curve rising and bending back over the scene (as in a real launch ramp)
    P = [(905, 1172), (1060, 860), (990, 560), (780, 450)]
    t_up = np.linspace(0, 1, 140)
    up = bez(P, t_up)
    s_g = np.linspace(0, 1, 40)[:-1]
    g0, g1 = np.array([760.0, H + 60.0]), np.array([905.0, 1172.0])
    ground = g0 + (g1 - g0) * (s_g ** 0.8)[:, None]
    c = np.concatenate([ground, up])
    t = np.concatenate([np.zeros(len(ground)), t_up])
    d = np.gradient(cv2.GaussianBlur(c.reshape(-1, 1, 2), (1, 9), 0).reshape(-1, 2), axis=0)
    n = np.stack([-d[:, 1], d[:, 0]], 1)
    n /= np.linalg.norm(n, axis=1, keepdims=True)
    w = np.concatenate([360 - 185 * s_g ** 0.8, 175 * (1 - t_up) + 95 * t_up])
    L = c - n * w[:, None] / 2
    Rr = c + n * w[:, None] / 2
    # truss behind (to the right / outside of the curve)
    truss = np.zeros((H, W), np.float32)
    k0 = len(ground)
    for k in range(k0, len(t) - 6, 6):
        a, b = Rr[k], Rr[k + 6]
        a2, b2 = a + n[k] * 70, b + n[k + 6] * 70
        for p, q in ((a2, b2), (a, a2), (a, b2)):
            cv2.line(truss, tuple(np.int32(p)), tuple(np.int32(q)), 1.0, 3, cv2.LINE_AA)
    cv2.line(truss, (1040, 400), (1040, HOR), 1.0, 5, cv2.LINE_AA)
    cv2.line(truss, (1000, 520), (1000, HOR), 1.0, 4, cv2.LINE_AA)
    f[:] = f * (1 - truss[..., None] * 0.9) + truss[..., None] * np.array([0.16, 0.16, 0.17]) * 0.9
    # surface
    poly = np.concatenate([L, Rr[::-1]]).astype(np.int32)
    m = np.zeros((H, W), np.float32)
    cv2.fillPoly(m, [poly], 1.0, cv2.LINE_AA)
    shade = 0.42 + 0.35 * noise(10, 3, 5) * 0.4
    across = np.zeros((H, W), np.float32)
    for k in range(len(t)):            # brighter in the middle of the lane, darker near the top
        cv2.line(across, tuple(np.int32(L[k])), tuple(np.int32(Rr[k])), 0.75 + 0.25 * (1 - t[k]), 10)
    surf = (shade * cv2.GaussianBlur(across, (0, 0), 3))[..., None] * np.array([0.78, 0.77, 0.75])
    f[:] = f * (1 - m[..., None]) + surf * m[..., None]
    # lane line and LED edges
    lane = np.zeros((H, W), np.float32)
    cv2.polylines(lane, [(c + n * (w[:, None] * 0.12)).astype(np.int32)], False, 1.0, 3, cv2.LINE_AA)
    f[:] = f * (1 - lane[..., None] * 0.7) + lane[..., None] * 0.92 * 0.7
    led = np.zeros((H, W), np.float32)
    for edge in (L, Rr):
        for k in range(0, len(t), 3):
            cv2.circle(led, tuple(np.int32(edge[k])), 3, 1.0, -1, cv2.LINE_AA)
        cv2.polylines(led, [edge.astype(np.int32)], False, 0.55, 3, cv2.LINE_AA)
    f += (led[..., None] * 1.1 + cv2.GaussianBlur(led, (0, 0), 7)[..., None] * 1.6) * YEL
    # reflection of the LEDs on the wet ground
    refl = cv2.flip(led, 0)
    shift = np.float32([[1, 0, 0], [0, 1, 2 * HOR - H]])
    refl = cv2.warpAffine(refl, shift, (W, H))
    refl = cv2.GaussianBlur(refl, (0, 0), 5) * (yy > HOR) * np.clip(1 - (yy - HOR) / 160, 0, 1)
    f += refl[..., None] * YEL * 0.6


def bottle():
    im = Image.open(ROOT / "assets/oil5w30.png").convert("RGBA")
    h = 520
    im = im.resize((int(im.width * h / im.height), h), Image.LANCZOS)
    a = np.array(im).astype(np.float32) / 255
    rgb, al = a[..., :3], a[..., 3]
    # warm rim light on the right edge, cool fill on the left, darker base (lit from the jets below)
    hh, ww = al.shape
    edge = np.clip(al - cv2.erode(al, np.ones((9, 9))), 0, 1)
    gx = np.linspace(-1, 1, ww)[None, :]
    rim = cv2.GaussianBlur(edge, (0, 0), 2) * np.clip(gx * 1.4, 0, 1)
    rgb = rgb * (0.82 + 0.18 * np.linspace(1, 0.7, hh)[:, None, None])
    rgb += rim[..., None] * WARM * 0.9
    base = np.clip((np.arange(hh)[:, None] - hh * 0.8) / (hh * 0.2), 0, 1)
    rgb += (base * al)[..., None] * WARM * 0.25
    return np.dstack([np.clip(rgb, 0, 1) * al[..., None], al]).astype(np.float32)


def place_rotated(f, lay, cx, cy, deg):
    hh, ww = lay.shape[:2]
    M = cv2.getRotationMatrix2D((ww / 2, hh / 2), deg, 1.0)
    M[0, 2] += cx - ww / 2
    M[1, 2] += cy - hh / 2
    big = cv2.warpAffine(lay, M, (W, H), flags=cv2.INTER_CUBIC)
    f[:] = f * (1 - big[..., 3:4]) + big[..., :3]
    return M, (ww, hh)


def thrust_and_smoke(f, M, size):
    ww, hh = size
    pts = [M @ np.array([x * ww, hh - 4, 1.0]) for x in (0.18, 0.38, 0.6, 0.8)]
    down = M[:, :2] @ np.array([0.0, 1.0])
    down /= np.linalg.norm(down)
    # smoke: fractal noise inside cones under each jet + a wide bank rolling along the ground
    mask = np.zeros((H, W), np.float32)
    for p in pts:
        for s in np.linspace(0, 1, 50):
            q = p + down * (40 + 470 * s)
            r = 22 + 170 * s ** 1.2
            cv2.circle(mask, (int(q[0]), int(q[1])), int(r), 1.0, -1, cv2.LINE_AA)
    cv2.ellipse(mask, (330, HOR + 30), (520, 150), 0, 0, 360, 1.0, -1, cv2.LINE_AA)
    cv2.ellipse(mask, (60, HOR + 80), (300, 140), 0, 0, 360, 1.0, -1, cv2.LINE_AA)
    cv2.ellipse(mask, (640, HOR + 90), (260, 110), 0, 0, 360, 1.0, -1, cv2.LINE_AA)
    mask = cv2.GaussianBlur(mask, (0, 0), 28)
    n = noise(160, 6, 9)
    n2 = noise(60, 4, 21)
    dens = np.clip(mask * (0.55 + 0.75 * n + 0.25 * n2) - 0.08, 0, 1) ** 0.9
    near = np.zeros((H, W), np.float32)
    for p in pts:
        near += np.exp(-(((xx - p[0]) / 150) ** 2 + ((yy - (p[1] + 230)) / 260) ** 2))
    near = np.clip(near, 0, 1)
    shade = 0.62 + 0.38 * n[..., None] * (0.7 + 0.3 * n2[..., None])
    col = (np.array([0.93, 0.92, 0.92]) * shade
           + near[..., None] * np.array([1.0, 0.85, 0.55]) * 0.35)
    a = np.clip(dens * 0.97, 0, 1)[..., None]
    f[:] = f * (1 - a) + col * a
    # jets: hot white cores fading to warm yellow
    jet = np.zeros((H, W), np.float32)
    core = np.zeros((H, W), np.float32)
    for p in pts:
        for s in np.linspace(0, 1, 70):
            q = p + down * (6 + 300 * s)
            cv2.circle(jet, (int(q[0]), int(q[1])), int(10 + 26 * s), 1 - s, -1, cv2.LINE_AA)
            cv2.circle(core, (int(q[0]), int(q[1])), int(5 + 6 * s), (1 - s) ** 1.5, -1, cv2.LINE_AA)
    jet = cv2.GaussianBlur(jet, (0, 0), 9)
    f += jet[..., None] * np.array([1.0, 0.8, 0.45]) * 1.1 + cv2.GaussianBlur(core, (0, 0), 3)[..., None] * 1.5
    # light spill on the ground and up the smoke
    spill = np.exp(-(((xx - 330) / 380) ** 2 + ((yy - HOR) / 120) ** 2))
    f += spill[..., None] * WARM * 0.22


def text(f):
    logo = Image.open(ROOT / "assets/logo.png")
    logo = R.to_premul(np.array(logo.resize((220, int(logo.height * 220 / logo.width)), Image.LANCZOS)))
    R.over(f, logo, W - 220 - 56, 56)
    YEL8 = (250, 184, 23)
    h1 = E.T.line([("انطلق", (241, 240, 236)), ("بأداء", (241, 240, 236)), ("أعلى", YEL8)], 92, bold=True, shadow=True, pad=20)
    R.over(f, h1, W - h1.shape[1] - 36, 150)
    h2 = E.T.line([("زيت", (192, 196, 199)), ("محرك", (192, 196, 199))], 46, bold=False, shadow=True, pad=14)
    lat = R.latin_layer("JLM 5W-30", 48, YEL8, 800, 0.02)
    x = W - 56
    R.over(f, h2, x - h2.shape[1] + 14, 268)
    R.over(f, lat, x - h2.shape[1] - lat.shape[1] - 4, 268 + (h2.shape[0] - lat.shape[0]) // 2 + 2)
    pill = V.url_pill(40)
    R.over(f, pill, W - pill.shape[1] - 56, H - pill.shape[0] - 52)


def main():
    (ROOT / "out").mkdir(exist_ok=True)
    f = background()
    ramp(f)
    lay = bottle()
    # bottle first (behind the jets' glow), then jets/smoke drawn over its base, then the bottle again on top
    M, size = place_rotated(f.copy(), lay, 330, 640, 8)
    thrust_and_smoke(f, M, size)
    place_rotated(f, lay, 330, 640, 8)
    vig = 1 - 0.45 * np.clip(np.hypot((xx - W / 2) / W, (yy - H * 0.55) / H) * 1.5, 0, 1) ** 2
    f *= vig[..., None]
    f += (RNG.normal(0, 0.012, (H, W, 1))).astype(np.float32)
    text(f)
    img = (np.clip(f, 0, 1) ** (1 / 1.05) * 255 + 0.5).astype(np.uint8)
    Image.fromarray(img).save(ROOT / "out/jlm_5w30_launch.png")
    print("wrote out/jlm_5w30_launch.png")


if __name__ == "__main__":
    main()
