"""Layers for the ATF Stop Leak & Conditioner story (blueprint style).

    python3 scripts/prepare.py      # needs rembg (birefnet-general-lite), opencv, pillow

From the client's product photo (assets/src/product.png, white background) it writes into assets/gen/:
- can.png         the can cut out, cropped to its outline
- can_sketch.png  the same can as a silver line drawing (what the scan line turns into the real photo)
- logo.png        logo_on_dark.png with only the mark's alpha (the file carries a faint background box)
"""
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
KIT = ROOT.parents[2] / "brand/jlm"
OUT = ROOT / "assets/gen"


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    from rembg import new_session, remove
    im = Image.open(ROOT / "assets/src/product.png").convert("RGB")
    rgba = np.array(remove(im, session=new_session("birefnet-general-lite")))
    a = rgba[..., 3]
    n, lab, st, _ = cv2.connectedComponentsWithStats((a > 60).astype(np.uint8))
    keep = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))
    rgba[..., 3] = np.where(lab == keep, a, 0)
    ys, xs = np.nonzero(rgba[..., 3] > 10)
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    can = rgba[y0:y1, x0:x1]
    Image.fromarray(can).save(OUT / "can.png")

    # line drawing: edges of the photo inside the can + its outline, silver on transparent
    g = cv2.cvtColor(can[..., :3], cv2.COLOR_RGB2GRAY)
    e = cv2.Canny(cv2.GaussianBlur(g, (0, 0), 1.4), 40, 110)
    outline = cv2.morphologyEx((can[..., 3] > 128).astype(np.uint8), cv2.MORPH_GRADIENT, np.ones((3, 3), np.uint8))
    lines = np.maximum(cv2.dilate(e, np.ones((2, 2), np.uint8)) * (can[..., 3:4][..., 0] > 128), outline * 255)
    sk = np.zeros_like(can)
    sk[..., :3] = (192, 196, 199)
    sk[..., 3] = cv2.GaussianBlur(lines, (0, 0), 0.6)
    Image.fromarray(sk).save(OUT / "can_sketch.png")

    lg = np.array(Image.open(KIT / "logos/logo_on_dark.png").convert("RGBA"))
    keep = cv2.dilate((lg[..., 3] > 128).astype(np.uint8), np.ones((5, 5), np.uint8))
    lg[..., 3] = lg[..., 3] * keep
    lg[:4], lg[-4:], lg[:, :4], lg[:, -4:] = 0, 0, 0, 0
    Image.fromarray(lg).save(OUT / "logo.png")
    print("can", can.shape)


if __name__ == "__main__":
    main()
