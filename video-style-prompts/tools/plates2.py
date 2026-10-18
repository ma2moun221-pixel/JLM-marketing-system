"""Build the Ramallah flight plate and the showroom landing plate.

usage: plates2.py sky_plate.png ramallah.jpg showroom.jpg outdir
"""
import sys, cv2, numpy as np

skyp, ramp, shp, out = sys.argv[1:5]
PW, PH, HZ = 1500, 2800, 1500


def unsharp(img, sigma, amt):
    b = cv2.GaussianBlur(img, (0, 0), sigma)
    return np.clip(img * (1 + amt) - b * amt, 0, 1)


# ---------- Ramallah: procedural sky above, real aerial photo below ----------
sky = cv2.imread(skyp).astype(np.float32) / 255
ram = cv2.imread(ramp).astype(np.float32) / 255
rh = int(ram.shape[0] * PW / ram.shape[1])
ram = cv2.resize(ram, (PW, rh), interpolation=cv2.INTER_LANCZOS4)
ram = unsharp(ram, 1.6, 0.55)
# sunny grade: a bit brighter, warmer, slightly more saturated
ram = np.clip((ram - 0.5) * 1.08 + 0.5 + 0.04, 0, 1) * np.array([0.96, 1.0, 1.04], np.float32)
g = ram.mean(-1, keepdims=True)
ram = np.clip(g + (ram - g) * 1.12, 0, 1)
# aerial perspective: distant (top) rows hazier
haze = np.array([0.93, 0.89, 0.85], np.float32)
d = np.clip(1 - np.arange(rh) / (rh * 0.55), 0, 1)[:, None, None] ** 1.6 * 0.55
ram = ram * (1 - d) + haze * d

plate = np.zeros((PH, PW, 3), np.float32)
plate[:HZ] = sky[:HZ]
plate[HZ:HZ + rh] = ram[:PH - HZ]
if HZ + rh < PH:
    plate[HZ + rh:] = ram[::-1][: PH - HZ - rh]
# soft horizon: sky thickens into haze, far hills emerge from it
up = 220; dn = 160
wu = (np.arange(up) / up)[:, None, None] ** 1.5 * 0.9
plate[HZ - up:HZ] = plate[HZ - up:HZ] * (1 - wu) + haze * wu
wd = (1 - np.arange(dn) / dn)[:, None, None] ** 1.3 * 0.9
plate[HZ:HZ + dn] = plate[HZ:HZ + dn] * (1 - wd) + haze * wd
cv2.imwrite(f"{out}/plate_ramallah.png", np.clip(plate * 255, 0, 255).astype(np.uint8))

# ---------- Showroom: graded to the midday footage ----------
sh = cv2.imread(shp).astype(np.float32) / 255
sh = np.clip(sh * 1.10 + 0.02, 0, 1)
g = sh.mean(-1, keepdims=True)
sh = np.clip(g + (sh - g) * 0.95, 0, 1)
sh = unsharp(sh, 1.2, 0.25)
cv2.imwrite(f"{out}/plate_showroom.png", np.clip(sh * 255, 0, 255).astype(np.uint8))
print("ok", plate.shape, sh.shape)
