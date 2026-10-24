"""Cut the JLM product photos into clean transparent PNGs, one per product.

Input:  the two EDSR x4 super-resolved photos (see README "image-enhancer").
        p1_x4.png  - 5W40 + 5W30 cans + Turbo Pre Lube on white (2000x2000)
        p2_x4.png  - Stop Smoke can with alpha (2880x2880)
Output: assets/<product>.png (RGBA, trimmed)

The 5W30 can stands behind the 5W40 can, so its lower-left edge is hidden.
Both cans are the same bottle, so the hidden strip is rebuilt from the
matching part of the 5W40 can (scaled and shifted onto the 5W30).
"""

import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter

src_dir, out_dir = Path(sys.argv[1]), Path(sys.argv[2])
out_dir.mkdir(parents=True, exist_ok=True)

p1 = cv2.cvtColor(cv2.imread(str(src_dir / "p1_x4.png")), cv2.COLOR_BGR2RGB).astype(np.float32)
H, W = p1.shape[:2]
yy, xx = np.mgrid[0:H, 0:W]

# --- foreground mask: remove white that touches the border or fills a handle hole
near_white = (p1.min(axis=2) > 236).astype(np.uint8)
n, labels = cv2.connectedComponents(near_white, connectivity=4)
background_seeds = [(0, 0), (W - 1, H - 1), (600, 640), (1290, 500)]  # border, 5W40 hole, 5W30 hole
bg = np.zeros((H, W), bool)
for x, y in background_seeds:
    if near_white[y, x]:
        bg |= labels == labels[y, x]
fg = ~bg

# --- split line between the 5W40 (front) and the 5W30 (behind), x4 coordinates
pts_y = np.array([0, 510, 800, 850, 1100, 1300, 1400, 2000], np.float32)
pts_x = np.array([828, 828, 915, 924, 922, 917, 915, 910], np.float32)
split_x = np.interp(np.arange(H), pts_y, pts_x)[:, None]
tube_x = 1622

left = fg & (xx < split_x)
middle = fg & (xx >= split_x) & (xx < tube_x)
# the tube's nozzle is off-white, so it needs a stricter white threshold
near_white_strict = (p1.min(axis=2) > 249).astype(np.uint8)
n2, labels2 = cv2.connectedComponents(near_white_strict, connectivity=4)
right = ~(labels2 == labels2[0, W - 1]) & (xx >= tube_x)


def largest_component(mask):
    n, lab, stats, _ = cv2.connectedComponentsWithStats(mask.astype(np.uint8), connectivity=8)
    if n <= 1:
        return mask
    k = 1 + np.argmax(stats[1:, cv2.CC_STAT_AREA])
    return lab == k


left, middle, right = (largest_component(m) for m in (left, middle, right))

# --- rebuild the hidden lower-left strip of the 5W30 from the 5W40
# 5W40 cap top-left (130, 430) maps to 5W30 cap top-left (845, 305), scale 0.965
s, (ax, ay), (bx, by) = 0.965, (130.0, 430.0), (845.0, 305.0)
M = np.float32([[s, 0, bx - s * ax], [0, s, by - s * ay]])
donor_rgb = cv2.warpAffine(p1, M, (W, H), flags=cv2.INTER_CUBIC)
donor_mask = cv2.warpAffine(left.astype(np.float32), M, (W, H), flags=cv2.INTER_LINEAR) > 0.5
# the donor fills only what the 5W40 covers, left of the split line
hidden = donor_mask & (xx < split_x + 6) & ~middle
# match brightness: the rear can is a touch darker
probe = middle & (xx > split_x + 10) & (xx < split_x + 60) & (yy > 900) & (yy < 1300)
probe_d = donor_mask & (xx > split_x + 10) & (xx < split_x + 60) & (yy > 900) & (yy < 1300)
gain = p1[probe].mean(axis=0) / np.maximum(donor_rgb[probe_d].mean(axis=0), 1)
donor_rgb = np.clip(donor_rgb * gain, 0, 255)

# soft seam: blend donor into the visible can over a 34 px band
seam = np.clip((split_x + 24 - xx) / 34.0, 0, 1)[..., None]
p1_30 = p1.copy()
blend_zone = (hidden | (middle & donor_mask & (xx < split_x + 24)))[..., None]
p1_30 = np.where(blend_zone, donor_rgb * seam + p1 * (1 - seam), p1)
p1_30 = np.where(hidden[..., None], donor_rgb, p1_30)
mask_30 = middle | hidden


def soft_alpha(mask, erode=2, blur=1.3):
    m = mask.astype(np.uint8) * 255
    if erode:
        m = cv2.erode(m, np.ones((3, 3), np.uint8), iterations=erode)
    return cv2.GaussianBlur(m, (0, 0), blur)


def finish(rgb, alpha, name, sharpen=True):
    rgba = np.dstack([np.clip(rgb, 0, 255).astype(np.uint8), alpha])
    ys, xs = np.nonzero(alpha > 4)
    pad = 6
    crop = rgba[max(ys.min() - pad, 0): ys.max() + pad, max(xs.min() - pad, 0): xs.max() + pad]
    im = Image.fromarray(crop, "RGBA")
    if sharpen:  # image-enhancer: gentle unsharp mask + a little local contrast
        a = im.getchannel("A")
        rgb_im = im.convert("RGB").filter(ImageFilter.UnsharpMask(radius=2.2, percent=70, threshold=2))
        rgb_im = ImageEnhance.Contrast(rgb_im).enhance(1.06)
        im = rgb_im.convert("RGBA")
        im.putalpha(a)
    im.save(out_dir / f"{name}.png")
    print(name, im.size)


finish(p1, soft_alpha(left), "oil_5w40")
finish(p1_30, soft_alpha(mask_30), "oil_5w30")
finish(p1, soft_alpha(right), "turbo_prelube")

p2 = cv2.imread(str(src_dir / "p2_x4.png"), cv2.IMREAD_UNCHANGED)
p2 = cv2.cvtColor(p2, cv2.COLOR_BGRA2RGBA)
a2 = p2[..., 3]
a2 = cv2.erode(a2, np.ones((3, 3), np.uint8), iterations=2)
finish(p2[..., :3].astype(np.float32), a2, "stop_smoke")

# --- JLM logo, rebuilt as a crisp mask (white = ink) -------------------------
# The roundel is drawn as geometry measured from the 5W40 label; the "JLM"
# letters are traced from the label and smoothed at 8x.
SC = 8
crop = cv2.cvtColor(p1.astype(np.uint8), cv2.COLOR_RGB2GRAY)[1280:1450, 220:640].astype(np.float32)
ink = np.clip((108 - crop) / 40 + 0.5, 0, 1)
ink[:, :162] = 0  # keep the letters only
n, lab, stats, _ = cv2.connectedComponentsWithStats((ink > 0.5).astype(np.uint8), connectivity=8)
keep = np.zeros_like(ink, bool)
for k in range(1, n):
    if stats[k, cv2.CC_STAT_AREA] > 400:  # drops the ® mark and label specks
        keep |= cv2.dilate((lab == k).astype(np.uint8), np.ones((5, 5), np.uint8)) > 0
ink *= keep
big = cv2.resize(ink, None, fx=SC, fy=SC, interpolation=cv2.INTER_CUBIC)
big = cv2.GaussianBlur(big, (0, 0), 3.2)
letters = np.clip((big - 0.5) * 6 + 0.5, 0, 1)

h, w = letters.shape
cx, cy, R = 90.0 * SC, 79.5 * SC, 71.5 * SC
Y, X = np.mgrid[0:h, 0:w].astype(np.float32)
r = np.hypot(X - cx, Y - cy)


def ring(r0, r1, gap_angle_deg, gap_px):
    band = np.clip(np.minimum(r - r0, r1 - r) + 0.5, 0, 1)
    a = np.radians(gap_angle_deg)
    ux, uy = np.cos(a), np.sin(a)
    along = (X - cx) * ux + (Y - cy) * uy        # in the gap direction
    across = np.abs(-(X - cx) * uy + (Y - cy) * ux)
    cut = np.clip(across - gap_px / 2 + 0.5, 0, 1)
    cut = np.where(along > 0, cut, 1)
    return band * cut


roundel = np.maximum(ring(0.72 * R, R, -92, 0.085 * R), ring(0.343 * R, 0.60 * R, 183, 0.085 * R))
logo = np.maximum(roundel, letters)
ys, xs = np.nonzero(logo > 0.02)
logo = logo[ys.min() - 8: ys.max() + 8, xs.min() - 8: xs.max() + 8]
Image.fromarray((logo * 255).astype(np.uint8), "L").save(out_dir / "jlm_logo_mask.png")
print("jlm_logo_mask", logo.shape)
