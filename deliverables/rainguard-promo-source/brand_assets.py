"""Turn the official JLM brand files into video-ready assets."""
import sys, numpy as np
from PIL import Image
Image.MAX_IMAGE_PIXELS = None
UP, OUT = sys.argv[1], sys.argv[2]
f = lambda k: f"{UP}/{k}-image.png"

def key_out(path, bg, palette, out, width):
    a = np.asarray(Image.open(path).convert('RGB')).astype(float)
    bg = np.array(bg, float)
    best_a = np.zeros(a.shape[:2]); best_fg = np.zeros(a.shape); best_d = np.full(a.shape[:2], 1e9)
    for fg in palette:
        fg = np.array(fg, float); v = fg - bg
        al = np.clip(((a - bg) @ v) / (v @ v), 0, 1)
        d = np.linalg.norm(a - (bg + al[..., None] * v), axis=2)
        m = d < best_d
        best_d[m] = d[m]; best_a[m] = al[m]; best_fg[m] = fg
    rgba = np.dstack([best_fg, best_a * 255]).astype(np.uint8)
    im = Image.fromarray(rgba, 'RGBA'); im = im.crop(im.getchannel('A').point(lambda x: 255 if x > 10 else 0).getbbox())
    im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS); im.save(out); print(out, im.size)
    return im

src = np.asarray(Image.open(f('3a7f9b88')).convert('RGB'))
gray = tuple(int(x) for x in src[2236, 605]); print('icon gray', gray)
# dark-background version: gray icon, white JLM, yellow LIQUID TOOLS
dark = key_out(f('3a7f9b88'), (37, 39, 41), [gray, (255, 255, 255), (250, 184, 23)], f"{OUT}/logo_on_dark.png", 1400)
# yellow-background version: gray icon, dark JLM + LIQUID TOOLS
key_out(f('57aae914'), (250, 184, 23), [gray, (37, 39, 41)], f"{OUT}/logo_on_yellow.png", 1400)
# icon only (left part of the dark version) for the big background mark
w, h = dark.size; icon = dark.crop((0, 0, int(h * 1.0), h)); icon = icon.crop(icon.getchannel('A').getbbox()); icon.save(f"{OUT}/icon.png"); print('icon', icon.size)
# all-yellow logo (already transparent)
y = Image.open(f('a8249b64')).convert('RGBA'); y = y.crop(y.getchannel('A').getbbox()); y.save(f"{OUT}/logo_yellow.png"); print('yellow', y.size)
# oil-drop divider: drop shape as an alpha mask
d = Image.open(f('e16de8d5')).convert('RGBA'); A = np.asarray(d.getchannel('A'))
cols = np.where(A.max(0) > 0)[0]; rows = (A > 128).sum(1)
cx = d.width // 2; drop = d.crop((cx - 200, 0, cx + 200, d.height)); drop = drop.crop(drop.getchannel('A').getbbox())
# remove the line from the drop crop: keep columns where the drop is (alpha wide area)
Ad = np.asarray(drop.getchannel('A')); colsum = (Ad > 128).sum(0); keep = np.where(colsum > colsum.max() * 0.25)[0]
drop = drop.crop((keep[0], 0, keep[-1] + 1, drop.height)); drop.save(f"{OUT}/drop.png"); print('drop', drop.size)
line_rows = np.where((A[:, 200:1500] > 128).mean(1) > .5)[0]; print('line rows', line_rows.min(), line_rows.max(), 'of', d.height)
dd = d.resize((2000, round(d.height * 2000 / d.width)), Image.LANCZOS); dd.save(f"{OUT}/divider.png")
# blueprint: full-colour portrait crop + line-only mask for dark scenes
bp = Image.open(f('d7a2bc9b')).convert('RGB'); H = 2400; W = round(bp.width * H / bp.height)
bp = bp.resize((W, H), Image.LANCZOS); x0 = (W - 1500) // 2; bp = bp.crop((x0, 0, x0 + 1500, H)); bp.save(f"{OUT}/blueprint.jpg", quality=92)
Y = np.asarray(bp.convert('L')).astype(float); base = np.median(Y); lo = np.percentile(Y, 1)
al = np.clip((base - Y) / max(1, base - lo), 0, 1)
Image.fromarray(np.dstack([np.full(Y.shape + (3,), 255, np.uint8), (al * 255).astype(np.uint8)]), 'RGBA').save(f"{OUT}/blueprint_lines.png")
print('blueprint', bp.size, base, lo)
