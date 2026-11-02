"""Product cut-outs for the oil-change film.

    python3 scripts/prepare.py      # needs rembg (birefnet-general-lite), opencv, pillow

The client's product files (assets/src/flush.png, oil5w30.png) carry a background behind the pack
(black / white), so each is flattened on white and cut out again; the 400 px 5W-30 photo is upscaled 3×
first. Writes assets/gen/flush.png and assets/gen/oil5w30.png, cropped to the pack.
"""
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from rembg import new_session, remove

ROOT = Path(__file__).resolve().parents[1]


def main():
    sess = new_session("birefnet-general-lite")
    for name, up in (("flush", 1), ("oil5w30", 3)):
        im = Image.open(ROOT / f"assets/src/{name}.png").convert("RGBA")
        rgb = Image.alpha_composite(Image.new("RGBA", im.size, (255, 255, 255, 255)), im).convert("RGB")
        if up > 1:
            rgb = rgb.resize((rgb.width * up, rgb.height * up), Image.LANCZOS)
        out = np.array(remove(rgb, session=sess))
        al = out[..., 3]
        n, lab, st, _ = cv2.connectedComponentsWithStats((al > 60).astype(np.uint8))
        keep = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))
        out[..., 3] = np.where(lab == keep, al, 0)
        ys, xs = np.nonzero(out[..., 3] > 10)
        out = out[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
        Image.fromarray(out).save(ROOT / f"assets/gen/{name}.png")
        print(name, out.shape)


if __name__ == "__main__":
    main()
