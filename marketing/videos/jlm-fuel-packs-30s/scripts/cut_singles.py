"""Cut each product out of the 3-can group photos as its own transparent PNG.

    python3 cut_singles.py ORIGINAL_8 ORIGINAL_9 ASSETS_DIR

The group photos (petrol / diesel) each show Extreme Clean, Injector Cleaner
and Fuel System Cleaner. The middle can (Injector Cleaner) stands in front of
both neighbours, so it is complete; Extreme Clean loses a thin strip on its
right edge and Fuel System Cleaner a sliver on its left edge.

The cans are cylinders seen head-on, so each silhouette is symmetric about the
cap's axis. For every can:
  * axis cx  = centre of its (fully visible) cap
  * half-width hw = distance from cx to its body edge on the unobstructed side
  * mask = min(alpha(x), alpha(2·cx − x)) inside |x − cx| ≤ hw
    (symmetry removes any neighbour pixels and restores the hidden outline)
  * pixels covered by the front can are rebuilt from the mirrored opposite
    edge of the same can (plain silver edge, black band, yellow line).

Measurements run on the original 580 px alpha; work happens on the 4x EDSR
upscale (assets/<line>_pack.png), placed back on its full 2320 px canvas.
"""

import sys
from pathlib import Path

import cv2
import numpy as np
from numpy.lib.stride_tricks import sliding_window_view
from PIL import Image, ImageEnhance, ImageFilter

orig8, orig9, assets = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
S = 4


def runs(row):
    out, start = [], None
    for x, v in enumerate(row):
        if v and start is None:
            start = x
        if not v and start is not None:
            out.append((start, x - 1))
            start = None
    if start is not None:
        out.append((start, len(row) - 1))
    return out


def cap_axis(alpha, rows, xwin):
    """Mean centre of the cap runs that fall inside xwin over the given rows."""
    cs = []
    for y in rows:
        for a, b in runs(alpha[y] > 100):
            if xwin[0] <= a and b <= xwin[1]:
                cs.append((a + b) / 2)
    return float(np.median(cs))


def edge(alpha, rows, side, xwin):
    """Median body edge on the unobstructed side ('left' or 'right')."""
    es = []
    for y in rows:
        cols = np.nonzero(alpha[y, xwin[0]:xwin[1]] > 100)[0]
        if len(cols):
            es.append(xwin[0] + (cols[0] if side == "left" else cols[-1]))
    return float(np.median(es))


def full_canvas(orig_path, asset_path):
    """Re-place the cropped 4x asset on its full canvas (same crop as the upscale)."""
    a = np.array(Image.open(orig_path).convert("RGBA"))[..., 3]
    a4 = cv2.resize(a, (a.shape[1] * S, a.shape[0] * S), interpolation=cv2.INTER_CUBIC)
    a4 = cv2.erode(a4, np.ones((3, 3), np.uint8))
    ys, xs = np.nonzero(a4 > 8)
    ox, oy = xs.min(), ys.min()
    asset = np.array(Image.open(asset_path).convert("RGBA"))
    canvas = np.zeros((a4.shape[0], a4.shape[1], 4), np.uint8)
    canvas[oy: oy + asset.shape[0], ox: ox + asset.shape[1]] = asset
    return a, canvas


def cut(canvas, cx, hw, front_l=None, front_r=None, margin=10, extend=False):
    """Extract one can. front_l / front_r: x (4x px) where a can in front starts
    covering this can from the left / right; pixels beyond are mirrored."""
    H, W = canvas.shape[:2]
    rgb = canvas[..., :3].astype(np.float32)
    al = canvas[..., 3].astype(np.float32)
    xx = np.arange(W, dtype=np.float32)
    mx = np.clip(np.round(2 * cx - xx).astype(int), 0, W - 1)
    al_m = al[:, mx]
    rgb_m = rgb[:, mx]
    inside = (np.abs(xx - cx) <= hw)[None, :]
    mask = np.minimum(al, al_m) * inside
    # rebuild covered strips from the mirror, with a soft cross-fade
    w = np.zeros(W, np.float32)
    if front_r is not None:
        w = np.maximum(w, np.clip((xx - (front_r - margin)) / margin, 0, 1))
    if front_l is not None:
        w = np.maximum(w, np.clip(((front_l + margin) - xx) / margin, 0, 1))
    # the mirrored strip must not carry (reversed) label text: wherever it
    # departs from the vertical median of the can surface, use that median
    cols = np.nonzero(w > 0)[0]
    if len(cols):
        c0, c1 = cols.min(), cols.max() + 1
        strip = rgb_m[:, c0:c1].astype(np.float32)
        lum = strip.mean(-1)
        # tall vertical median (301 px): removes letters and the round dosage icon,
        # keeps the black band (taller than half the window) with sharp edges.
        # Transparent pixels (above the shoulder, below the base) are ignored.
        win = 301
        opaque = al_m[:, c0:c1] > 128
        lum_n = np.where(opaque, lum, np.nan)
        rgb_n = np.where(opaque[..., None], strip, np.nan)
        lum_pad = np.pad(lum_n, ((win // 2, win // 2), (0, 0)), constant_values=np.nan)
        rgb_pad = np.pad(rgb_n, ((win // 2, win // 2), (0, 0), (0, 0)), constant_values=np.nan)
        with np.errstate(all="ignore"):
            import warnings
            warnings.simplefilter("ignore", RuntimeWarning)
            vmed = np.nanmedian(sliding_window_view(lum_pad, win, axis=0)[:, :, ::6], axis=-1)
            vmed_rgb = np.stack([np.nanmedian(sliding_window_view(rgb_pad[..., k], win, axis=0)[:, :, ::6], axis=-1)
                                 for k in range(3)], -1)
        vmed = np.where(np.isnan(vmed), lum, vmed)
        vmed_rgb = np.where(np.isnan(vmed_rgb), strip, vmed_rgb)
        sat = strip.max(-1) - strip.min(-1)
        text = (np.abs(lum - vmed) > 18) | (sat > 45)
        text = cv2.dilate(text.astype(np.uint8), np.ones((7, 7), np.uint8)) > 0
        clean = np.where(text[..., None], vmed_rgb, strip)
        if extend and front_r is not None:
            # The mirror source is full of label text (its text margin), so extend the
            # can's own surface instead: colour of the last genuine columns, vertically
            # median-filtered (drops letter strokes), times the cylinder's fall-off.
            x_ref = int(front_r - margin) - 2
            ref = rgb[:, x_ref - 6: x_ref + 1].mean(1)
            win2 = 151  # taller than a letter, shorter than half the black band
            ref_pad = np.pad(ref, ((win2 // 2, win2 // 2), (0, 0)), mode="edge")
            A_med = np.median(sliding_window_view(ref_pad, win2, axis=0)[:, :, ::3], axis=-1)
            # keep each row's own colour (thin yellow line, band edges) unless it is a
            # letter stroke: much darker than its vertical neighbourhood
            stroke = np.abs(ref.mean(-1) - A_med.mean(-1)) > 45
            stroke = cv2.dilate(stroke.astype(np.uint8)[:, None], np.ones((9, 1), np.uint8))[:, 0] > 0
            A = np.where(stroke[:, None], A_med, ref)
            lum_all = rgb.mean(-1)
            l0, l1 = lum_all[:, x_ref - 40], lum_all[:, x_ref]
            ok = (al[:, x_ref - 40] > 200) & (al[:, x_ref] > 200) & (l1 > 90)
            s_rel = float(np.median((l1[ok] - l0[ok]) / 40 / l1[ok])) if ok.any() else -0.005
            xs_strip = np.arange(c0, c1, dtype=np.float32)
            fall = np.clip(1 + s_rel * (xs_strip - x_ref), 0.55, 1.2)
            d_edge = (cx + hw) - xs_strip
            rim = np.clip(0.78 + 0.022 * d_edge, 0.78, 1.0)
            clean = A[:, None, :] * (fall * rim)[None, :, None]
        rgb_m = rgb_m.copy()
        rgb_m[:, c0:c1] = clean
    out_rgb = rgb * (1 - w[None, :, None]) + rgb_m * w[None, :, None]
    mask = np.where(w[None, :] > 0, al_m * inside, mask)
    # light edge clean-up: 1 px erode + soft blur on alpha
    m8 = cv2.erode(mask.astype(np.uint8), np.ones((3, 3), np.uint8))
    m8 = cv2.GaussianBlur(m8, (0, 0), 0.9)
    rgba = np.dstack([np.clip(out_rgb, 0, 255).astype(np.uint8), m8])
    ys, xs = np.nonzero(m8 > 6)
    rgba = rgba[ys.min() - 4: ys.max() + 5, xs.min() - 4: xs.max() + 5]
    im = Image.fromarray(rgba, "RGBA")
    a = im.getchannel("A")
    im = ImageEnhance.Contrast(im.convert("RGB").filter(ImageFilter.UnsharpMask(2.0, 60, 2))).enhance(1.04).convert("RGBA")
    im.putalpha(a)
    return im


LINES = {
    # caps: (rows, x-window) in original px; clean body side for the half-width
    "petrol": dict(orig=orig8, asset=assets / "petrol_pack.png",
                   extreme=dict(cap=(range(138, 182, 2), (100, 230)), side="left", body=(range(220, 500, 4), (60, 200))),
                   injector=dict(cap=(range(56, 100, 2), (250, 362)), side="left", body=(range(140, 180, 2), (225, 300))),
                   fuel=dict(cap=(range(18, 84, 2), (390, 500)), side="right", body=(range(200, 500, 4), (440, 540)))),
    "diesel": dict(orig=orig9, asset=assets / "diesel_pack.png",
                   extreme=dict(cap=(range(100, 124, 2), (100, 210)), side="left", body=(range(160, 500, 4), (30, 150))),
                   injector=dict(cap=(range(18, 84, 2), (255, 365)), side="left", body=(range(98, 104, 1), (230, 300))),
                   fuel=dict(cap=(range(40, 92, 2), (395, 500)), side="right", body=(range(200, 500, 4), (440, 540)))),
}

for line, cfg in LINES.items():
    alpha, canvas = full_canvas(cfg["orig"], cfg["asset"])
    geo = {}
    for can in ("extreme", "injector", "fuel"):
        c = cfg[can]
        cx = cap_axis(alpha, *c["cap"])
        e = edge(alpha, *c["body"][:1], c["side"], c["body"][1])
        hw = abs(cx - e) + 0.5
        geo[can] = (cx, hw)
        print(f"{line:6s} {can:8s} axis {cx:6.1f}  half-width {hw:5.1f}  edges {cx - hw:6.1f}..{cx + hw:6.1f}")
    (cxe, hwe), (cxi, hwi), (cxf, hwf) = geo["extreme"], geo["injector"], geo["fuel"]
    inj_l, inj_r = (cxi - hwi) * S + 1.5, (cxi + hwi) * S + 1.5
    jobs = {
        # start the rebuild 6 px inside the seam: drops the front can's edge shadow
        # petrol Extreme Clean has label text running to its left edge, so its
        # hidden right strip is extended from its own surface instead of mirrored
        "extreme_clean": cut(canvas, cxe * S + 1.5, hwe * S, front_r=inj_l - 6, margin=6,
                             extend=(line == "petrol")),
        "injector_cleaner": cut(canvas, cxi * S + 1.5, hwi * S),
        "fuel_system_cleaner": cut(canvas, cxf * S + 1.5, hwf * S, front_l=inj_r + 6, margin=6),
    }
    for name, im in jobs.items():
        path = assets / f"{line}_{name}.png"
        im.save(path)
        print("  wrote", path.name, im.size)
