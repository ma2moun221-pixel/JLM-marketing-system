"""Build the JLM Liquid Tools brand assets used by the renderer.

    python3 prepare_brand.py LOGO_YELLOW_ON_DARK GEAR_PATTERN NL_LABEL_PNG OUT_DIR

LOGO_YELLOW_ON_DARK  official lockup, yellow on charcoal (2000x2000)
GEAR_PATTERN         official yellow gear pattern (2000x1125)
NL_LABEL_PNG         "Made in The Netherlands" label rendered from the .ai at 600 dpi

Outputs (RGBA): logo_on_dark.png  (silver roundel · white JLM · yellow LIQUID TOOLS)
                logo_on_yellow.png (all charcoal — the official on-yellow variant)
                gears.png          (gear mask, white = gear, for tinting)
                made_in_nl.png
"""

import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

logo_src, gear_src, nl_src, out = map(Path, sys.argv[1:5])
out.mkdir(parents=True, exist_ok=True)

YELLOW = np.array([250, 184, 23], np.float32)
CHARCOAL = np.array([37, 39, 41], np.float32)
SILVER = np.array([192, 196, 199], np.float32)
WHITE = np.array([241, 240, 236], np.float32)

# --- logo: alpha = how far each pixel moved from charcoal toward yellow
im = np.array(Image.open(logo_src).convert("RGB")).astype(np.float32)
a = np.clip(((im - CHARCOAL) @ (YELLOW - CHARCOAL)) / np.dot(YELLOW - CHARCOAL, YELLOW - CHARCOAL), 0, 1)
ys, xs = np.nonzero(a > 0.05)
y0, y1, x0, x1 = ys.min() - 4, ys.max() + 5, xs.min() - 4, xs.max() + 5
a = a[y0:y1, x0:x1]
h, w = a.shape
# zones: roundel = left of the wordmark; "LIQUID TOOLS" = the line under "JLM"
cols = (a > 0.5).sum(axis=0)
gap = np.where(cols[: w // 2] == 0)[0]
split_x = int(gap[-1]) if len(gap) else int(w * 0.33)
rows = (a[:, split_x:] > 0.5).sum(axis=1)
empty = np.where(rows == 0)[0]
mid = empty[(empty > h * 0.5) & (empty < h * 0.9)]
split_y = int(mid[len(mid) // 2]) if len(mid) else int(h * 0.82)
zone = np.zeros((h, w), np.uint8)       # 0 roundel, 1 JLM, 2 LIQUID TOOLS
zone[:, split_x:] = 1
zone[split_y:, split_x:] = 2
rgb = np.where((zone == 0)[..., None], SILVER, np.where((zone == 1)[..., None], WHITE, YELLOW))
Image.fromarray(np.dstack([rgb, a * 255]).astype(np.uint8), "RGBA").save(out / "logo_on_dark.png")
dark = np.broadcast_to(CHARCOAL, (h, w, 3))
Image.fromarray(np.dstack([dark, a * 255]).astype(np.uint8), "RGBA").save(out / "logo_on_yellow.png")
print("logo", (w, h), "split", split_x, split_y)

# --- gear pattern: the gears are a slightly darker yellow on yellow
g = np.array(Image.open(gear_src).convert("RGB")).astype(np.float32)
lum = g.mean(axis=2)
base = np.percentile(lum, 85)
mask = np.clip((base - lum) / 12.0, 0, 1)
mask = cv2.GaussianBlur(mask, (0, 0), 0.8)
Image.fromarray((mask * 255).astype(np.uint8), "L").save(out / "gears.png")
print("gears", mask.shape, float(mask.mean()))

# --- Made in NL label: crop to its rounded box, white outside → transparent
nl = np.array(Image.open(nl_src).convert("RGB")).astype(np.float32)
ink = (255 - nl.min(axis=2)) > 10
ys, xs = np.nonzero(ink)
crop = nl[ys.min(): ys.max() + 1, xs.min(): xs.max() + 1]
# flood the outside white from the corners so the label keeps its own white fill
outside = np.zeros(crop.shape[:2], np.uint8)
white = (crop.min(axis=2) > 245).astype(np.uint8)
ff = white.copy()
mask_ff = np.zeros((ff.shape[0] + 2, ff.shape[1] + 2), np.uint8)
for cx, cy in [(0, 0), (ff.shape[1] - 1, 0), (0, ff.shape[0] - 1), (ff.shape[1] - 1, ff.shape[0] - 1)]:
    if ff[cy, cx]:
        cv2.floodFill(ff, mask_ff, (cx, cy), 2)
alpha = np.where(ff == 2, 0, 255).astype(np.uint8)
Image.fromarray(np.dstack([crop.astype(np.uint8), alpha]), "RGBA").save(out / "made_in_nl.png")
print("made_in_nl", crop.shape)
