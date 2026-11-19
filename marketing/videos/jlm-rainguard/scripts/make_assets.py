"""Photo-like layers for the Screen Rainguard film (procedural, deterministic).

    python3 scripts/make_assets.py

Writes into assets/gen/:
- road.png        night road seen through the windshield (sharp; the composition blurs it)
- glass_rain.png  the 'before' glass: blurred road + water film + flat, smeared drops (poor visibility)
- beads.png       the 'after' glass: round beads that refract the road (transparent layer)
- bead_0..3.png   single beads for the sliding animation
Every drop is a small lens: it shows the road upside down and magnified, with a dark rim,
a specular highlight and a soft contact shadow.
"""
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets/gen"
W, H = 1080, 1920
HOR = 860
RNG = np.random.default_rng(5)


def road():
    img = np.zeros((H, W, 3), np.float32)
    y = np.arange(H)[:, None]
    sky = np.clip(y / HOR, 0, 1)
    img[:] = (np.array([10, 12, 16]) * (1 - sky)[..., None] + np.array([34, 30, 34]) * sky[..., None])
    # wet asphalt
    g = np.clip((y - HOR) / (H - HOR), 0, 1)
    asphalt = np.array([26, 25, 27]) * (1 - g)[..., None] + np.array([12, 12, 13]) * g[..., None]
    img = np.where((y >= HOR)[..., None], np.broadcast_to(asphalt, img.shape), img).astype(np.float32)
    lights = np.zeros_like(img)
    # building windows on the horizon
    for _ in range(140):
        x = RNG.uniform(0, W)
        yy = RNG.uniform(HOR - 260, HOR - 20)
        c = RNG.choice([[255, 190, 120], [200, 215, 235], [255, 220, 170]])
        cv2.rectangle(lights, (int(x), int(yy)), (int(x + RNG.uniform(4, 10)), int(yy + RNG.uniform(5, 12))),
                      (np.array(c) * RNG.uniform(.3, .8)).tolist(), -1)
    # street lamps along both sides, receding to the vanishing point
    vx = W / 2
    for k in range(9):
        t = (k / 9) ** 1.6
        for side in (-1, 1):
            x = vx + side * (60 + 900 * (1 - t))
            yy = HOR - 40 - 520 * (1 - t)
            r = 6 + 40 * (1 - t)
            cv2.circle(lights, (int(x), int(yy)), int(r), (255 * .95, 175 * .95, 90 * .95), -1, cv2.LINE_AA)
            # reflection streak on the wet road
            cv2.ellipse(lights, (int(x * .92 + vx * .08), int(HOR + (HOR - yy) * .55 + 20)), (int(r * .35), int(r * 3)),
                        0, 0, 360, (70, 48, 26), -1, cv2.LINE_AA)
    # traffic ahead: tail lights; oncoming head lights
    for k, (dx, d) in enumerate([(-60, .25), (40, .45), (-130, .6), (150, .8)]):
        x, yy, s = vx + dx * (1 - d) * 3, HOR + 40 + 300 * (1 - d), 40 * (1 - d) + 6
        for sx in (-1, 1):
            cv2.circle(lights, (int(x + sx * s * 1.4), int(yy)), int(s * .35), (230, 40, 30), -1, cv2.LINE_AA)
            cv2.ellipse(lights, (int(x + sx * s * 1.4), int(yy + s * 1.8)),
                        (int(s * .18), int(s * 1.4)), 0, 0, 360, (70, 12, 9), -1, cv2.LINE_AA)
    for k, d in enumerate((.3, .55)):
        x, yy, s = vx + 260 * (1 - d) + 30, HOR + 30 + 260 * (1 - d), 34 * (1 - d) + 5
        for sx in (-1, 1):
            cv2.circle(lights, (int(x + sx * s), int(yy)), int(s * .5), (255, 250, 235), -1, cv2.LINE_AA)
    glow = cv2.GaussianBlur(lights, (0, 0), 10) * 1.4 + cv2.GaussianBlur(lights, (0, 0), 40) * 1.2
    img += cv2.GaussianBlur(lights, (0, 0), 1.2) * .9 + glow
    # haze near the horizon
    img += np.exp(-((y - HOR + 60) / 220.0) ** 2)[..., None] * np.array([26, 22, 22])
    # lane markings in perspective
    for k in range(12):
        t0, t1 = (k / 12) ** 1.8, ((k + .45) / 12) ** 1.8
        y0, y1 = HOR + (H - HOR) * t0, HOR + (H - HOR) * t1
        w0, w1 = 2 + 26 * t0, 2 + 26 * t1
        pts = np.array([[vx - w0, y0], [vx + w0, y0], [vx + w1, y1], [vx - w1, y1]], np.int32)
        cv2.fillPoly(img, [pts], (150, 150, 145), cv2.LINE_AA)
    for side in (-1, 1):
        cv2.line(img, (int(vx + side * 8), HOR), (int(vx + side * 760), H), (90, 90, 88), 6, cv2.LINE_AA)
    img = cv2.GaussianBlur(img, (0, 0), 1.0)
    img += RNG.normal(0, 2.2, img.shape)
    return np.clip(img, 0, 255)


def lens_drop(canvas, src, cx, cy, rx, ry, flat=False):
    """Paint one drop into canvas (float RGB) refracting src (float RGB)."""
    x0, x1 = int(max(0, cx - rx - 4)), int(min(W, cx + rx + 5))
    y0, y1 = int(max(0, cy - ry - 4)), int(min(H, cy + ry + 6))
    yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
    nx, ny = (xx - cx) / rx, (yy - cy) / ry
    d = np.sqrt(nx ** 2 + ny ** 2)
    inside = d < 1
    if not inside.any():
        return
    # what you see through a drop: the scene behind, slightly magnified, plus the lights
    # it gathers from a wider area, upside down (a small lens)
    local = cv2.remap(src, np.clip(cx + nx * rx * .8, 0, W - 1), np.clip(cy + ny * ry * .8, 0, H - 1), cv2.INTER_LINEAR)
    k = 1.2 if flat else 3.0
    inv = cv2.remap(src, np.clip(cx - nx * rx * k, 0, W - 1), np.clip(cy - ny * ry * k, 0, H - 1), cv2.INTER_LINEAR)
    col = local * (.75 if not flat else .95) + inv * (.55 if not flat else .15)
    edge = np.clip(d, 0, 1)
    col *= (1 - (.55 if not flat else .25) * np.clip((edge - .7) / .3, 0, 1) ** 2 * np.clip(.5 + nx * .5 + ny * .5, 0, 1))[..., None]
    rimlight = np.exp(-((d - .9) / .07) ** 2) * np.clip(-(nx + ny) * .7, 0, 1) * (70 if not flat else 30)
    hl = np.exp(-(((nx + .3) / .16) ** 2 + ((ny + .38) / .12) ** 2)) * (230 if not flat else 70)
    hl2 = np.exp(-(((nx - .35) / .12) ** 2 + ((ny - .5) / .08) ** 2)) * (70 if not flat else 20)
    col += (rimlight + hl + hl2)[..., None] + (18 if flat else 0)
    a = np.clip((1 - d) * max(rx, ry) / 1.5, 0, 1)
    region = canvas[y0:y1, x0:x1]
    region[:] = region * (1 - a[..., None]) + col * a[..., None]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    rd = road()
    Image.fromarray(rd.astype(np.uint8)).save(OUT / "road.png")
    blur = cv2.GaussianBlur(rd.astype(np.float32), (0, 0), 16)

    # BEFORE: water film (wavy distortion + smears) and flat, irregular drops
    n = cv2.GaussianBlur(RNG.normal(0, 1, (H // 4, W // 4)).astype(np.float32), (0, 0), 6)
    n = cv2.resize(n, (W, H)) * 60
    gy, gx = np.gradient(n)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    film = cv2.remap(blur, xx + gx * 18, yy + gy * 18, cv2.INTER_LINEAR)
    film = film * .8 + 20
    # vertical run-off streaks
    streak = np.zeros((H, W), np.float32)
    for _ in range(70):
        x = RNG.uniform(0, W)
        cv2.line(streak, (int(x), int(RNG.uniform(0, H))), (int(x + RNG.uniform(-15, 15)), int(RNG.uniform(0, H))),
                 float(RNG.uniform(.2, .6)), int(RNG.uniform(2, 7)), cv2.LINE_AA)
    streak = cv2.GaussianBlur(streak, (0, 0), 3)
    film += streak[..., None] * 40
    for _ in range(330):
        r = RNG.uniform(6, 34)
        lens_drop(film, blur, RNG.uniform(0, W), RNG.uniform(0, H), r * RNG.uniform(1, 1.8), r * RNG.uniform(.6, 1.1), flat=True)
    Image.fromarray(np.clip(film, 0, 255).astype(np.uint8)).save(OUT / "glass_rain.png")

    # AFTER: round beads refracting the sharp road, on a transparent layer
    rgb = np.zeros((H, W, 3), np.float32)
    alpha = np.zeros((H, W), np.float32)
    for _ in range(170):
        r = RNG.uniform(5, 22)
        cx, cy = RNG.uniform(0, W), RNG.uniform(0, H)
        layer = rgb.copy()
        lens_drop(layer, rd.astype(np.float32), cx, cy, r, r * 1.04)
        d = np.sqrt(((xx - cx) / r) ** 2 + ((yy - cy) / (r * 1.04)) ** 2)
        m = np.clip((1 - d) * r / 1.5, 0, 1)
        rgb = rgb * (1 - m[..., None]) + layer * m[..., None]
        sh = np.clip(1 - np.sqrt(((xx - cx - r * .25) / (r * 1.1)) ** 2 + ((yy - cy - r * .35) / (r * 1.1)) ** 2), 0, 1) * .35
        alpha = np.maximum(alpha, np.maximum(m, sh))
    out = np.dstack([np.clip(rgb, 0, 255), alpha * 255]).astype(np.uint8)
    Image.fromarray(out, "RGBA").save(OUT / "beads.png")

    # single beads (sprites) for the slide-off animation
    for i, r in enumerate((14, 20, 28, 36)):
        s = int(r * 3)
        sub = np.zeros((s, s, 3), np.float32)
        src = cv2.resize(rd.astype(np.float32)[HOR - 300:HOR + 300, 240:840], (s, s))
        global_w, global_h = W, H
        # local lens on the small crop
        yy2, xx2 = np.mgrid[0:s, 0:s].astype(np.float32)
        c = s / 2
        nx, ny = (xx2 - c) / r, (yy2 - c) / (r * 1.05)
        d = np.sqrt(nx ** 2 + ny ** 2)
        inv = cv2.remap(src, np.clip(c - nx * r * 1.4, 0, s - 1), np.clip(c - ny * r * 1.4, 0, s - 1), cv2.INTER_LINEAR)
        col = inv * .9 + 28
        col *= (1 - .55 * np.clip((np.clip(d, 0, 1) - .7) / .3, 0, 1) ** 2 * np.clip(.5 + nx * .5 + ny * .5, 0, 1))[..., None]
        col += (np.exp(-((d - .9) / .07) ** 2) * np.clip(-(nx + ny) * .7, 0, 1) * 70
                + np.exp(-(((nx + .3) / .16) ** 2 + ((ny + .38) / .12) ** 2)) * 230)[..., None]
        a = np.clip((1 - d) * r / 1.5, 0, 1)
        shadow = np.clip(1 - np.sqrt(((xx2 - c - r * .25) / (r * 1.1)) ** 2 + ((yy2 - c - r * .35) / (r * 1.1)) ** 2), 0, 1) * .35
        al = np.maximum(a, shadow)
        Image.fromarray(np.dstack([np.clip(col * a[..., None], 0, 255), al * 255]).astype(np.uint8), "RGBA").save(OUT / f"bead_{i}.png")
    print("wrote", sorted(p.name for p in OUT.iterdir()))


if __name__ == "__main__":
    main()
