"""JLM winter story «البرد ما بوقّفك» — 1080×1920, a frosted windshield with the wiper's cleared arc.

    python3 scripts/build.py          # → out/jlm_winter_wiper_story.png

The idea: the whole story is a car windshield covered in frost. The wiper has cleared an arc from the
bottom, and through it the viewer sees a warm night with three JLM winter products standing on a wet
floor. The slogan sits on the frost above, in charcoal with a yellow tag. Light theme, so the logo is
the official charcoal one.

Product lines come from the labels only, as used in the winter campaign (../jlm-winter-stories):
- 5W-30 Premium Grade Performance Oil: «زيت محرك بلزوجة 5W-30»;
- Penetrating Oil: «يذيب الصدأ ويطرد الرطوبة»;
- Fuel System Cleaner · Petrol: «ينظّف البخاخات بعمق» (label: deep cleans injectors).

Background painted in numpy: frost, wiper arc, residue streaks and the warm bokeh behind the glass.
Text and products in HTML (JLM fonts), rendered by the pre-installed Chromium.
"""
import subprocess
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[2]
BUILD, OUT = ROOT / "build", ROOT / "out"
FONTS = (REPO / "brand/jlm/fonts").as_uri()
PRODS = REPO / "marketing/social/jlm-winter-stories/assets"
CHROME = "/opt/pw-browsers/chromium-1243/chrome-linux64/chrome"
W, H = 1080, 1920
PIVOT, R_OUT, R_IN = (540, 2010), 1210, 250        # wiper pivot below the frame; cleared annulus sector
FLOOR = 1395
rng = np.random.default_rng(31)


def fractal(scale, octaves, seed):
    r = np.random.default_rng(seed)
    o, a, tot = np.zeros((H, W), np.float32), 1.0, 0.0
    for k in range(octaves):
        s = max(2, int(scale / 2 ** k))
        z = r.normal(0, 1, (H // s + 2, W // s + 2)).astype(np.float32)
        o += cv2.resize(z, (W, H), interpolation=cv2.INTER_CUBIC) * a
        tot += a
        a *= .55
    o /= tot
    return (o - o.min()) / (o.max() - o.min())


def background():
    y = np.arange(H, dtype=np.float32)[:, None]
    x = np.arange(W, dtype=np.float32)[None, :]
    # ---- behind the glass: warm night, bokeh, wet floor
    t = np.clip((y - 700) / (FLOOR - 700), 0, 1)
    scene = np.array([.075, .078, .085]) * (1 - t)[..., None] + np.array([.15, .14, .13]) * t[..., None]
    scene = np.broadcast_to(scene, (H, W, 3)).copy()
    bok, refl = np.zeros((H, W, 3), np.float32), np.zeros((H, W, 3), np.float32)
    cols = [(1.0, .72, .09)] * 4 + [(1.0, .85, .55)] * 3 + [(.85, .88, .92)] * 2 + [(.9, .25, .18)]
    for _ in range(60):
        cx, cy, r = rng.uniform(-40, W + 40), rng.uniform(780, 1300), rng.uniform(8, 38)
        c = np.array(cols[rng.integers(len(cols))]) * rng.uniform(.25, .6)
        cv2.circle(bok, (int(cx), int(cy)), int(r), c.tolist(), -1, cv2.LINE_AA)
        cv2.ellipse(refl, (int(cx), int(2 * FLOOR - cy + 40)), (int(r * .6), int(r * 2.6)), 0, 0, 360, (c * .45).tolist(), -1, cv2.LINE_AA)
    scene += cv2.GaussianBlur(bok, (0, 0), 9) * (y < FLOOR)[..., None]
    scene += cv2.blur(cv2.GaussianBlur(refl, (0, 0), 9), (3, 50)) * (y >= FLOOR)[..., None]
    f = np.clip((y - FLOOR) / (H - FLOOR), 0, 1)
    scene = np.where((y >= FLOOR)[..., None], scene * (1 - .5 * f)[..., None], scene)
    scene += np.exp(-((y - FLOOR - 4) / 18) ** 2)[..., None] * np.array([.12, .11, .09])       # wet sheen
    scene += (np.exp(-(((x - 540) / 520) ** 2 + ((y - 1180) / 330) ** 2)))[..., None] * np.array([.20, .14, .03])  # warm glow

    # ---- frost on the glass
    n1, n2, n3 = fractal(260, 6, 3), fractal(60, 4, 5), fractal(14, 2, 8)
    frost = np.array([.80, .85, .90]) + ((n1 - .5) * .10 + (n2 - .5) * .08 + (n3 - .5) * .06)[..., None]
    # ice crystals: fern-like streaks
    cr = np.zeros((H, W), np.float32)
    for _ in range(900):
        x0, y0 = rng.uniform(0, W), rng.uniform(0, H)
        ang, ln = rng.uniform(0, np.pi), rng.uniform(10, 60)
        for b in range(3):
            a2 = ang + rng.normal(0, .5)
            x1, y1 = x0 + ln * np.cos(a2), y0 + ln * np.sin(a2)
            cv2.line(cr, (int(x0), int(y0)), (int(x1), int(y1)), float(rng.uniform(.25, .7)), 1, cv2.LINE_AA)
    cr = cv2.GaussianBlur(cr, (0, 0), .7)
    frost = frost + cr[..., None] * np.array([.12, .12, .12])

    # ---- the wiper's cleared arc (annulus sector above the pivot)
    px, py = PIVOT
    dist = np.hypot(x - px, y - py)
    ang = np.degrees(np.arctan2(y - py, x - px))                       # −180..180, up = −90
    sector = (ang > -160) & (ang < -20)
    clear = ((dist < R_OUT) & (dist > R_IN) & sector).astype(np.float32)
    clear = cv2.GaussianBlur(clear, (0, 0), 3)
    # residue: faint concentric streaks the blade leaves, and a few drops
    streak = (np.sin(dist / 2.2 + 3 * n2) * .5 + .5) ** 30 * .045 + np.clip((n1 - .74) * 3, 0, 1) * .05
    drops = np.zeros((H, W), np.float32)
    for _ in range(140):
        cx, cy = rng.uniform(0, W), rng.uniform(800, H)
        cv2.circle(drops, (int(cx), int(cy)), int(rng.uniform(2, 6)), 1.0, -1, cv2.LINE_AA)
    drops = cv2.GaussianBlur(drops, (0, 0), 1.0)
    # pushed-up frost ridge along the arc's edge (brighter, thicker)
    ridge = np.exp(-((dist - R_OUT - 10) / 16) ** 2) * sector
    edge_l = np.exp(-((ang + 160) / 1.2) ** 2) * (dist > R_IN) * (dist < R_OUT)
    edge_r = np.exp(-((ang + 20) / 1.2) ** 2) * (dist > R_IN) * (dist < R_OUT)
    ridge = np.clip(ridge + edge_l + edge_r, 0, 1)

    glass_alpha = 1 - clear * (1 - streak - drops * .25)
    img = scene * (1 - glass_alpha[..., None]) + frost * glass_alpha[..., None]
    img += ridge[..., None] * .10
    img += (drops * clear)[..., None] * np.array([.10, .09, .07])
    # inner shadow of the frost along the clear edge (frost has thickness)
    sh = cv2.GaussianBlur(1 - clear, (0, 0), 10) * clear
    img *= (1 - .35 * sh)[..., None]
    Image.fromarray((np.clip(img, 0, 1) * 255 + .5).astype(np.uint8)).save(BUILD / "bg.png")


def logo():
    im = np.array(Image.open(REPO / "brand/jlm/logos/logo_charcoal_on_white_src.png").convert("RGBA"))
    keep = cv2.dilate((im[..., 3] > 128).astype(np.uint8), np.ones((5, 5), np.uint8))
    im[..., 3] = im[..., 3] * keep
    ys, xs = np.nonzero(im[..., 3] > 10)
    Image.fromarray(im[ys.min():ys.max() + 1, xs.min():xs.max() + 1]).save(BUILD / "logo.png")


def page():
    p = PRODS.as_uri()
    prods = [  # (file, height, centre x, name, line)
        ("oil_5w30.png", 360, 250, "5W-30 Oil", "زيت محرك بلزوجة 5W-30"),
        ("penetrating_oil.png", 440, 540, "Penetrating Oil", "يذيب الصدأ ويطرد الرطوبة"),
        ("petrol_fuel_system_cleaner.png", 440, 830, "Fuel System Cleaner", "ينظّف البخاخات بعمق"),
    ]
    items = "".join(
        f"<img class='prod' src='{p}/{f}' style='height:{h}px;left:{cx}px;top:{FLOOR + 8 - h}px'>"
        f"<img class='prod refl' src='{p}/{f}' style='height:{h}px;left:{cx}px;top:{FLOOR + 6}px'>"
        f"<div class='chip' style='left:{cx}px'><b class='lat'>{n}</b><span class='ar'>{ln}</span></div>"
        for f, h, cx, n, ln in prods)
    return f"""<!doctype html><html lang="ar"><head><meta charset="utf-8"><style>
@font-face{{font-family:HNA;font-weight:700;src:url('{FONTS}/helveticaneueltarabic-bold.ttf')}}
@font-face{{font-family:HNA;font-weight:400;src:url('{FONTS}/helveticaneueltarabic-roman.ttf')}}
@font-face{{font-family:Albert;font-weight:100 900;src:url('{FONTS}/AlbertSans.ttf')}}
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:{W}px;height:{H}px;overflow:hidden;background:#252729}}
#s{{position:relative;width:{W}px;height:{H}px;background:url('bg.png');overflow:hidden}}
.ar{{font-family:HNA;direction:rtl}}
.lat{{font-family:Albert;font-weight:800;direction:ltr;unicode-bidi:isolate}}
#logo{{position:absolute;right:66px;top:170px;width:220px}}
#h1{{position:absolute;right:66px;top:285px;font-family:HNA;font-weight:700;font-size:150px;line-height:1;color:#252729;direction:rtl}}
#h2{{position:absolute;right:66px;top:500px;background:#FAB817;padding:8px 34px 24px;font-family:HNA;font-weight:700;font-size:118px;
     line-height:1.05;color:#252729;direction:rtl;box-shadow:0 14px 34px rgba(37,39,41,.22)}}
#sub{{position:absolute;right:68px;top:690px;font-size:40px;color:#252729;font-weight:400}}
#sub b{{font-family:Albert;font-weight:800}}
.prod{{position:absolute;transform:translateX(-50%);filter:drop-shadow(0 18px 22px rgba(0,0,0,.55))}}
.refl{{transform:translateX(-50%) scaleY(-1);opacity:.16;filter:blur(2px);
       -webkit-mask-image:linear-gradient(to top,rgba(0,0,0,.9),rgba(0,0,0,0) 45%)}}
.chip{{position:absolute;top:{FLOOR + 22}px;transform:translateX(-50%);width:290px;text-align:center;color:#F1F0EC}}
.chip b{{display:block;font-size:26px;color:#FAB817;margin-bottom:2px}}
.chip span{{display:block;font-size:26px;line-height:1.3;color:#F1F0EC}}
#cta{{position:absolute;left:0;width:{W}px;top:1545px;display:flex;justify-content:center;align-items:center;gap:20px;direction:rtl}}
#cta .t{{font-family:HNA;font-weight:700;font-size:46px;color:#F1F0EC}}
#cta .y{{color:#FAB817}}
#pill{{height:78px;padding:0 36px;border-radius:39px;background:#FAB817;color:#252729;font-family:Albert;font-weight:800;font-size:44px;
      display:flex;align-items:center;box-shadow:0 10px 26px rgba(0,0,0,.45)}}
#del{{position:absolute;left:0;width:{W}px;top:1642px;display:flex;justify-content:center;align-items:center;gap:14px;direction:rtl;
     font-family:HNA;font-size:36px;color:#F1F0EC}}
#del .y{{color:#FAB817}}
</style></head><body><div id="s">
<img id="logo" src="logo.png">
<div id="h1">البرد</div>
<div id="h2">ما بوقّفك!</div>
<div id="sub" class="ar">منتجات <b>JLM</b> لسيارتك هذا الشتاء</div>
{items}
<div id="cta"><span class="t"><span class="y">اطلبها الآن</span> من خلال</span><div id="pill">jlmstore.com</div></div>
<div id="del">مع توفر <span class="y">خدمة التوصيل</span>
<svg viewBox="0 0 66 40" width="62" height="38"><g fill="none" stroke="#FAB817" stroke-width="3.5" stroke-linejoin="round" stroke-linecap="round">
<path d="M3 6 H40 V30 H3 Z"/><path d="M40 14 H52 L62 23 V30 H40"/><circle cx="14" cy="32" r="5" fill="#252729"/><circle cx="50" cy="32" r="5" fill="#252729"/></g></svg></div>
</div></body></html>"""


def main():
    BUILD.mkdir(exist_ok=True)
    OUT.mkdir(exist_ok=True)
    background()
    logo()
    p = BUILD / "story.html"
    p.write_text(page(), encoding="utf-8")
    shot = BUILD / "shot.png"
    subprocess.run([CHROME, "--headless", "--no-sandbox", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=1",
                    "--allow-file-access-from-files", f"--window-size={W},{H + 300}", "--virtual-time-budget=4000",
                    f"--screenshot={shot}", p.as_uri()], check=True, capture_output=True)
    Image.open(shot).convert("RGB").crop((0, 0, W, H)).save(OUT / "jlm_winter_wiper_story.png")
    print("wrote", OUT / "jlm_winter_wiper_story.png")


if __name__ == "__main__":
    main()
