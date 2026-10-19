"""Cut the client's side photo of the car into layers for the story.

    python3 scripts/prepare_car.py      # needs rembg (isnet-general-use), opencv, pillow

From assets/src/car-side.webp it writes
- assets/car/body.png   the car without its wheels (wheel discs filled with a dark wheel well)
- assets/car/wheel-r.png, wheel-f.png   round wheel crops (they spin, then fold into hover pads)
- assets/car/geometry.json   wheel centres / radius, lights, fuel door and the outline path,
  all in the car <svg> coordinates of compositions/story.html (viewBox 0 0 1000 400)
"""
import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from rembg import new_session, remove

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets/car"
SRC = ROOT / "assets/src/car-side.webp"

# the car sits in the svg like the old drawing: x 30–975, wheels on the ground at y 296
X0, X1, GROUND = 30.0, 975.0, 296.0
# hand-picked from the photo (source pixels), refined below
WHEELS_GUESS = [(437, 496), (1077, 493)]
LIGHTS = {"head": [(1167, 397), (1247, 409)], "tail": [(224, 362), (307, 372)]}
FUEL = (420, 363)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    im = Image.open(SRC).convert("RGB")
    rgba = np.array(remove(im, session=new_session("isnet-general-use")))
    a = rgba[:, :, 3]
    # keep only the car (largest blob)
    n, lab, st, _ = cv2.connectedComponentsWithStats((a > 40).astype(np.uint8))
    keep = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))
    a = np.where(lab == keep, a, 0).astype(np.uint8)
    rgba[:, :, 3] = a

    # refine the wheels: strongest circle near each guess
    gray = cv2.medianBlur(cv2.cvtColor(rgba[:, :, :3], cv2.COLOR_RGB2GRAY), 5)
    wheels = []
    for gx, gy in WHEELS_GUESS:
        x0, y0 = gx - 110, gy - 110
        roi = gray[y0:gy + 110, x0:gx + 110]
        c = cv2.HoughCircles(roi, cv2.HOUGH_GRADIENT, dp=1, minDist=200, param1=120, param2=30,
                             minRadius=62, maxRadius=82)
        if c is not None:
            cx, cy, r = c[0][0]
            wheels.append((x0 + float(cx), y0 + float(cy), float(r)))
        else:
            wheels.append((gx, gy, 72.0))
    r = max(w[2] for w in wheels) + 2

    ys, xs = np.nonzero(a > 40)
    bx0, bx1 = xs.min(), xs.max()
    s = (X1 - X0) / (bx1 - bx0)
    bottom = max(w[1] + w[2] for w in wheels)
    tx, ty = X0 - bx0 * s, GROUND - bottom * s

    def P(x, y):
        return round(x * s + tx, 1), round(y * s + ty, 1)

    # wheel layers + body with dark wheel wells
    body = rgba.copy()
    h, w = a.shape
    yy, xx = np.mgrid[0:h, 0:w]
    geo_w = []
    for i, (cx, cy, _) in enumerate(wheels):
        R = int(np.ceil(r)) + 2
        crop = rgba[int(cy) - R:int(cy) + R, int(cx) - R:int(cx) + R].copy()
        cyy, cxx = np.mgrid[0:2 * R, 0:2 * R]
        d = np.hypot(cxx - (cx - int(cx) + R), cyy - (cy - int(cy) + R))
        crop[:, :, 3] = (np.clip(r + 0.5 - d, 0, 1) * crop[:, :, 3]).astype(np.uint8)
        Image.fromarray(crop).save(OUT / f"wheel-{'rf'[i]}.png")
        # the arch shows a dark wheel well down to the sill; below it the car is see-through
        disc = np.hypot(xx - cx, yy - cy) <= r + 1
        sill = cy + 0.25 * r
        well = np.clip(1 - np.hypot(xx - cx, yy - cy) / (r + 1), 0, 1)
        for ch in range(3):
            body[:, :, ch] = np.where(disc, (10 + 16 * well).astype(np.uint8), body[:, :, ch])
        fade = np.clip((sill + 6 - yy) / 12, 0, 1)
        body[:, :, 3] = np.where(disc, (255 * fade).astype(np.uint8), body[:, :, 3])
        px, py = P(cx, cy)
        geo_w.append({"cx": px, "cy": py, "r": round(r * s, 1),
                      "x": round((int(cx) - R) * s + tx, 1), "y": round((int(cy) - R) * s + ty, 1),
                      "size": round(2 * R * s, 1)})
    Image.fromarray(body).save(OUT / "body.png")

    # outline of the body without its wheels (for the gold energy line): follows the arches
    cnts, _ = cv2.findContours((body[:, :, 3] > 128).astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    c = max(cnts, key=cv2.contourArea)
    c = cv2.approxPolyDP(c, 1.2, True)[:, 0, :]
    d = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in (P(*p) for p in c)) + " Z"

    geo = {
        "image": {"x": round(tx, 2), "y": round(ty, 2), "w": round(w * s, 2), "h": round(h * s, 2), "scale": round(s, 5)},
        "wheels": geo_w,
        "head": [P(*p) for p in LIGHTS["head"]],
        "tail": [P(*p) for p in LIGHTS["tail"]],
        "fuel": P(*FUEL),
        "outline": d,
    }
    (OUT / "geometry.json").write_text(json.dumps(geo, indent=1))
    print(json.dumps({k: v for k, v in geo.items() if k != "outline"}, indent=1), len(d))


if __name__ == "__main__":
    main()
