"""Layers for the Air Refresh story, cut from the client's real photo (assets/photo.jpg).

    python3 scripts/prepare_photo.py      # needs opencv, pillow

Writes into assets/gen/:
- can_mask.png   the can only (cap + body, no thumb), at photo resolution: the light sheen is masked to it
- lights.json    the ceiling spot lights (story coordinates, 1080x1920) that get a soft glint
The photo itself is never altered; the film only moves the camera and adds light on top of it.
"""
import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets/gen"
SRC = ROOT / "assets/photo.jpg"
# the can in source pixels (hand-picked)
CAN = (483, 862, 806, 1778)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    im = Image.open(SRC).convert("RGB")
    W, H = im.size
    # the can is a rounded cylinder seen straight on: draw it, then cut away the thumb that overlaps its edge
    x0, y0, x1, y1 = CAN
    m = np.zeros((H, W), np.float32)
    cv2.rectangle(m, (x0 + 22, y0), (x1 - 22, y1), 1, -1)
    cv2.rectangle(m, (x0, y0 + 22), (x1, y1 - 22), 1, -1)
    for cx in (x0 + 22, x1 - 22):
        for cy in (y0 + 22, y1 - 22):
            cv2.circle(m, (cx, cy), 22, 1, -1, cv2.LINE_AA)
    hsv = cv2.cvtColor(np.array(im), cv2.COLOR_RGB2HSV).astype(np.float32)
    skin = ((hsv[..., 0] < 20) & (hsv[..., 1] > 70) & (hsv[..., 2] > 110)).astype(np.float32)
    edge = np.zeros_like(skin)
    edge[:, :x0 + 50] = 1
    edge[:, x1 - 70:] = 1
    skin = cv2.morphologyEx(skin * edge, cv2.MORPH_OPEN, np.ones((5, 5)))
    skin = cv2.GaussianBlur(cv2.dilate(skin, np.ones((11, 11))), (0, 0), 3)
    m = cv2.GaussianBlur(m, (0, 0), 1.5) * (1 - skin)
    # CSS masks read the alpha channel: white, with the can as alpha
    a = (np.clip(m, 0, 1) * 255).astype(np.uint8)
    Image.fromarray(np.dstack([np.full_like(a, 255)] * 3 + [a]), "RGBA").save(OUT / "can_mask.png")

    # ceiling spots: small, very bright blobs in the upper half
    g = cv2.cvtColor(np.array(im), cv2.COLOR_RGB2GRAY)
    b = ((g > 245).astype(np.uint8))
    b[int(H * .45):] = 0
    b[y0 - 20:y1, x0 - 20:x1 + 20] = 0
    n, _, st, cen = cv2.connectedComponentsWithStats(b)
    s = 1080 / W
    lights = []
    for i in range(1, n):
        area = st[i, cv2.CC_STAT_AREA]
        if 30 <= area <= 6000:
            cx, cy = cen[i]
            lights.append({"x": round(cx * s, 1), "y": round(cy * s, 1), "r": round(np.sqrt(area) * s, 1)})
    lights.sort(key=lambda l: -l["r"])
    (OUT / "lights.json").write_text(json.dumps(lights[:24], indent=1))
    print(len(lights), "lights;", lights[:6])


if __name__ == "__main__":
    main()
