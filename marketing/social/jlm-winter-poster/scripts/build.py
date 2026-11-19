"""JLM winter poster «سيارتك جاهزة للشتا؟» — 1080×1350 (4:5, Facebook + Instagram feed).

    python3 scripts/build.py            # → out/jlm_winter_poster.png
    python3 scripts/build.py story      # → out/jlm_winter_poster_story.png (1080×1920)

Scene, painted in numpy: a winter night on a snowy road with falling snow in three depths. The car from the
winter campaign (assets/car-side.jpg, hub badges blacked out) is night-graded. Its headlights cut a warm
beam that lights up the snowflakes.
Overlay (HTML in the JLM fonts, rendered by the pre-installed Chromium): the official logo top-right
(no box, no shadow), the slogan «سيارتك جاهزة / للشتا؟» with a snowflake, one supporting line, and the
usual CTA «اطلبها الآن من خلال» jlmstore.com · «مع توفر خدمة التوصيل».
No product claims.
Needs numpy, opencv, pillow and rembg (car cut-out, once).
"""
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[2]
BUILD, OUT = ROOT / "build", ROOT / "out"
FONTS = (REPO / "brand/jlm/fonts").as_uri()
CHROME = "/opt/pw-browsers/chromium-1243/chrome-linux64/chrome"
STORY = len(sys.argv) > 1 and sys.argv[1] == "story"
W, H = (1080, 1920) if STORY else (1080, 1350)
DY = 210 if STORY else 0                      # story: the slogan sits below the top UI (≈ 200 px)
FLOOR = 1000 + DY + (140 if STORY else 0)     # snowy ground line (story: a taller sky)
CAR_W = 800
rng = np.random.default_rng(23)


def car_layer():
    """Cut-out car → night grade, hub badges blacked out, cropped; returns RGBA float (0-1) and headlight xy."""
    p = BUILD / "car_cut.png"
    if not p.exists():
        from rembg import new_session, remove
        remove(Image.open(REPO / "marketing/social/jlm-winter-stories/assets/car-side.jpg").convert("RGB"),
               session=new_session("isnet-general-use")).save(p)
    car = Image.open(p).convert("RGBA")
    d = ImageDraw.Draw(car)
    for cx, cy in ((436, 610), (1228, 610)):                       # car-brand hub badges out
        d.ellipse((cx - 24, cy - 24, cx + 24, cy + 24), fill=(16, 17, 18, 255))
    box = car.getbbox()
    a = np.array(car.crop(box)).astype(np.float32) / 255
    a[..., 3] = np.where(a[..., 3] < 0.35, 0, a[..., 3])            # drop rembg's faint floor shadow
    rgb = a[..., :3] * np.array([.40, .44, .52])                    # cool night grade
    lum = rgb.mean(2, keepdims=True)
    rgb = np.clip((rgb - lum * .3) * 1.12 + lum * .3, 0, 1)
    # cold rim light along the roof line (moonlight from above)
    al = a[..., 3]
    top = np.clip(al - np.roll(al, 6, axis=0), 0, 1)
    rgb += cv2.GaussianBlur(top, (0, 0), 2)[..., None] * np.array([.30, .36, .45])
    s = CAR_W / a.shape[1]
    img = cv2.resize(np.dstack([rgb, al]), (CAR_W, int(a.shape[0] * s)), interpolation=cv2.INTER_AREA)
    head = ((1440 - box[0]) * s, (505 - box[1]) * s)               # headlight, car faces right
    tail = ((175 - box[0]) * s, (462 - box[1]) * s)
    return img, head, tail


def snow_layer(n, rad, alpha, blur, avoid=None):
    lay = np.zeros((H, W), np.float32)
    for _ in range(n):
        x, y = rng.uniform(-20, W + 20), rng.uniform(-20, H + 20)
        if avoid and any(x0 < x < x1 and y0 < y < y1 for x0, y0, x1, y1 in avoid):
            continue
        r = rng.uniform(*rad)
        cv2.circle(lay, (int(x), int(y)), max(1, int(round(r))), float(rng.uniform(*alpha)), -1, cv2.LINE_AA)
    return cv2.GaussianBlur(lay, (0, 0), blur) if blur else lay


def background():
    y = np.arange(H, dtype=np.float32)[:, None]
    x = np.arange(W, dtype=np.float32)[None, :]
    img = np.zeros((H, W, 3), np.float32)
    # night sky: deep cold charcoal → blue-grey haze at the horizon
    t = np.clip(y / FLOOR, 0, 1) ** 1.8
    img[:] = (np.array([.065, .072, .088]) * (1 - t)[..., None] + np.array([.17, .20, .25]) * t[..., None])
    # distant tree line / hills, dark silhouettes in the haze
    hill = FLOOR - 70 - 40 * np.sin(x / 140 + 1.3) - 25 * np.sin(x / 57) - 18 * np.sin(x / 23 + 2)
    img = np.where((y > hill)[..., None] & (y < FLOOR)[..., None], img * .72, img)
    # snowy ground: soft blue-white, darker toward the viewer, fine texture, tyre tracks
    f = np.clip((y - FLOOR) / (H - FLOOR), 0, 1)
    ground = np.array([.40, .45, .53]) * (1 - f)[..., None] ** 0.6 + np.array([.15, .17, .21]) * f[..., None]
    tex = cv2.GaussianBlur(rng.normal(0, 1, (H, W)).astype(np.float32), (0, 0), 1.2) * .035
    ground = ground + tex[..., None]
    # soft drifts: low snow mounds whose crests catch the light
    drift = np.zeros((H, W), np.float32)
    for _ in range(int(14 * H / 1350)):
        dx, dy = rng.uniform(-100, W + 100), rng.uniform(FLOOR + 60, H + 40)
        cv2.ellipse(drift, (int(dx), int(dy)), (int(rng.uniform(140, 320)), int(rng.uniform(26, 60))), 0, 180, 360,
                    float(rng.uniform(.5, 1)), -1, cv2.LINE_AA)
    drift = cv2.GaussianBlur(drift, (0, 0), 18)
    ground = ground + (drift - np.roll(drift, 10, axis=0)).clip(0, 1)[..., None] * np.array([.30, .33, .38])
    # sparkle: tiny ice glints on the snow
    gl = (rng.random((H, W)) > .9985).astype(np.float32) * (y >= FLOOR + 8)
    ground = ground + cv2.GaussianBlur(gl, (0, 0), .7)[..., None] * 1.6
    img = np.where((y >= FLOOR)[..., None], ground, img)
    # fog band at the horizon
    img += np.exp(-((y - FLOOR + 30) / 90) ** 2)[..., None] * np.array([.10, .12, .15])

    # car on the snow, with its shadow
    car, head, tail = car_layer()
    ch, cw = car.shape[:2]
    cx0, cy0 = 40, FLOOR + 22 - ch
    sh = np.zeros((H, W), np.float32)
    cv2.ellipse(sh, (cx0 + cw // 2, FLOOR + 14), (int(cw * .50), 26), 0, 0, 360, 1.0, -1, cv2.LINE_AA)
    sh = cv2.GaussianBlur(sh, (0, 0), 14)
    img *= 1 - .6 * sh[..., None]
    # headlight beam (warm) across the snow and the air, from the front of the car to the right edge
    hx, hy = cx0 + head[0], cy0 + head[1]
    ang = np.arctan2(y - hy, x - hx)
    dist = np.hypot(x - hx, y - hy)
    cone = np.exp(-((ang - 0.13) / 0.17) ** 2) * (x > hx) * np.exp(-dist / 700)
    beam = cv2.GaussianBlur(cone.astype(np.float32), (0, 0), 6)
    warm = np.array([1.0, .90, .66])
    img += beam[..., None] * warm * .42
    pool = np.exp(-(((x - hx - 170) / 170) ** 2 + ((y - FLOOR - 38) / 44) ** 2)) * (y >= FLOOR)
    img += pool[..., None] * warm * .38
    # car composite
    reg = img[cy0:cy0 + ch, cx0:cx0 + cw]
    a = car[..., 3:4]
    reg[:] = reg * (1 - a) + car[..., :3] * a
    # headlight + tail-light glows
    for (px, py), col, r, g in [((hx, hy), np.array([1.0, .96, .84]), 26, 1.6), ((cx0 + tail[0], cy0 + tail[1]), np.array([1.0, .20, .14]), 16, .7)]:
        gl = np.exp(-((x - px) ** 2 + ((y - py) * 1.6) ** 2) / (2 * r * r))
        img += gl[..., None] * col * g
        gl2 = np.exp(-((x - px) ** 2 + ((y - py) * 1.3) ** 2) / (2 * (r * 4) ** 2))
        img += gl2[..., None] * col * g * .18
    # snow on the roof line and the bonnet (thin white cap where the car's top edge faces up)
    al = np.zeros((H, W), np.float32)
    al[cy0:cy0 + ch, cx0:cx0 + cw] = car[..., 3]
    cap = np.clip(al - np.roll(al, 5, axis=0), 0, 1) * (y < cy0 + ch * .55)
    cap = cv2.GaussianBlur(cap, (0, 0), 1.2)
    img = img * (1 - cap[..., None] * .8) + cap[..., None] * np.array([.86, .90, .96]) * .8

    # falling snow: far, mid, near (bokeh); near flakes avoid the slogan and the CTA
    text_zones = [(60, 120 + DY, 1020, 520 + DY), (90, FLOOR + 50, 990, H - 30)]
    far = snow_layer(int(900 * H / 1350), (0.6, 1.4), (.35, .8), 0)
    mid = snow_layer(int(260 * H / 1350), (1.5, 3.0), (.5, .9), 0.8)
    near = snow_layer(int(26 * H / 1350), (7, 15), (.25, .45), 5, avoid=text_zones)
    flakes = far * .55 + mid * .8 + near
    lit = 1 + 2.2 * beam                                            # flakes in the beam light up warm
    img += flakes[..., None] * (np.array([.80, .86, .95]) + (lit - 1)[..., None] * warm * .5)
    # vignette
    v = 1 - .5 * (((x - W / 2) / (W * .8)) ** 2 + ((y - H * .5) / (H * .7)) ** 2)
    img *= np.clip(v, .45, 1)[..., None]
    # darken the top for the slogan
    img *= (1 - .35 * np.exp(-((y - (300 + DY)) / 260) ** 2))[..., None]
    Image.fromarray((np.clip(img, 0, 1) * 255 + .5).astype(np.uint8)).save(BUILD / "bg.png")


def clean_logo():
    im = np.array(Image.open(REPO / "brand/jlm/logos/logo_on_dark.png").convert("RGBA"))
    keep = cv2.dilate((im[..., 3] > 128).astype(np.uint8), np.ones((5, 5), np.uint8))
    im[..., 3] = im[..., 3] * keep
    im[:4], im[-4:], im[:, :4], im[:, -4:] = 0, 0, 0, 0
    Image.fromarray(im).save(BUILD / "logo.png")


SNOWFLAKE = """<svg viewBox="-50 -50 100 100" width="96" height="96"><g stroke="#FAB817" stroke-width="7" stroke-linecap="round" fill="none">
<g id="arm"><path d="M0 -44 V44"/><path d="M-14 -30 L0 -18 L14 -30"/><path d="M-14 30 L0 18 L14 30"/></g>
<use href="#arm" transform="rotate(60)"/><use href="#arm" transform="rotate(120)"/></g></svg>"""


def page():
    cta_top = FLOOR + (95 if not STORY else 120)          # story: delivery line ends above the bottom ≈ 300 px
    return f"""<!doctype html><html lang="ar"><head><meta charset="utf-8"><style>
@font-face{{font-family:HNA;font-weight:700;src:url('{FONTS}/helveticaneueltarabic-bold.ttf')}}
@font-face{{font-family:HNA;font-weight:400;src:url('{FONTS}/helveticaneueltarabic-roman.ttf')}}
@font-face{{font-family:Albert;font-weight:100 900;src:url('{FONTS}/AlbertSans.ttf')}}
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:{W}px;height:{H}px;overflow:hidden;background:#252729}}
#s{{position:relative;width:{W}px;height:{H}px;background:url('bg.png')}}
.ar{{font-family:HNA;direction:rtl;color:#F1F0EC}}
.lat{{font-family:Albert;font-weight:800;direction:ltr;unicode-bidi:isolate}}
.y{{color:#FAB817}}
#logo{{position:absolute;right:60px;top:{56 + DY}px;width:220px}}
#h1{{position:absolute;left:0;width:{W}px;top:{170 + DY}px;text-align:center;font-weight:700;font-size:112px;line-height:1.08;
     text-shadow:0 6px 30px rgba(0,0,0,.55)}}
#h2{{position:absolute;left:0;width:{W}px;top:{300 + DY}px;display:flex;justify-content:center;align-items:center;gap:26px;
     direction:rtl}}
#h2 span{{font-family:HNA;font-weight:700;font-size:170px;line-height:1.05;color:#FAB817;text-shadow:0 8px 40px rgba(0,0,0,.6)}}
#h2 svg{{filter:drop-shadow(0 0 14px rgba(250,184,23,.55));margin-top:10px}}
#sub{{position:absolute;left:0;width:{W}px;top:{518 + DY}px;text-align:center;font-weight:400;font-size:38px;color:#C0C4C7}}
#sub b{{font-weight:700;color:#F1F0EC}}
#line{{position:absolute;left:140px;right:140px;top:{cta_top - 22}px;height:2px;
      background:linear-gradient(90deg,rgba(250,184,23,0),#FAB817,rgba(250,184,23,0))}}
#cta{{position:absolute;left:0;width:{W}px;top:{cta_top}px;display:flex;justify-content:center;align-items:center;gap:22px;direction:rtl}}
#cta .t{{font-family:HNA;font-weight:700;font-size:50px;color:#F1F0EC}}
#pill{{height:84px;padding:0 40px;border-radius:42px;background:#FAB817;color:#252729;font-family:Albert;font-weight:800;
      font-size:48px;display:flex;align-items:center;box-shadow:0 10px 30px rgba(0,0,0,.45)}}
#del{{position:absolute;left:0;width:{W}px;top:{cta_top + 112}px;display:flex;justify-content:center;align-items:center;gap:16px;
     direction:rtl;font-family:HNA;font-size:38px;color:#F1F0EC}}
#del svg{{width:66px;height:40px}}
</style></head><body><div id="s">
<img id="logo" src="logo.png">
<div id="h1" class="ar">سيارتك جاهزة</div>
<div id="h2"><span>للشتا؟</span>{SNOWFLAKE}</div>
<div id="sub" class="ar">منتجات <b class="lat">JLM</b> معك هذا الشتاء</div>
<div id="line"></div>
<div id="cta"><span class="t"><span class="y">اطلبها الآن</span> من خلال</span><div id="pill">jlmstore.com</div></div>
<div id="del">مع توفر <span class="y">خدمة التوصيل</span>
<svg viewBox="0 0 66 40"><g fill="none" stroke="#FAB817" stroke-width="3.5" stroke-linejoin="round" stroke-linecap="round">
<path d="M3 6 H40 V30 H3 Z"/><path d="M40 14 H52 L62 23 V30 H40"/><circle cx="14" cy="32" r="5" fill="#252729"/><circle cx="50" cy="32" r="5" fill="#252729"/></g></svg></div>
</div></body></html>"""


def main():
    BUILD.mkdir(exist_ok=True)
    OUT.mkdir(exist_ok=True)
    background()
    clean_logo()
    p = BUILD / "poster.html"
    p.write_text(page(), encoding="utf-8")
    shot = BUILD / "shot.png"
    subprocess.run([CHROME, "--headless", "--no-sandbox", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=1",
                    "--allow-file-access-from-files", f"--window-size={W},{H + 300}", "--virtual-time-budget=4000",
                    f"--screenshot={shot}", p.as_uri()], check=True, capture_output=True)
    name = "jlm_winter_poster_story.png" if STORY else "jlm_winter_poster.png"
    Image.open(shot).convert("RGB").crop((0, 0, W, H)).save(OUT / name)
    print("wrote", OUT / name)


if __name__ == "__main__":
    main()
