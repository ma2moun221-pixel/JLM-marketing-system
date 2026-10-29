"""JLM winter campaign: 5 Instagram slides from one master template.

    python3 scripts/build.py                  # carousel 1080x1350 (4:5) → out/carousel/slide_01..05.png + overview.jpg
    python3 scripts/build.py story            # Stories 1080x1920 (9:16) → out/story/story_01..05.png + overview.jpg

One background (night rain, wet asphalt), one header (progress + logo top-right),
one headline frame (yellow 5 px frame + solid tag, from the JLM ATL template), one
product stage on the wet floor, one info panel with the yellow drop. Only the copy,
the product and its packaging category colour change between stories.
Product copy comes from the packaging text only (see COPY notes below).
Needs numpy, opencv, pillow, rembg (car cut-out, once) and the pre-installed Chromium.
"""
import html
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "build"
OUT = ROOT / "out"
FONTS = ROOT.parents[2] / "brand/jlm/fonts"
CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"
# every size and position that differs between the two formats
LAYOUTS = {
    "carousel": dict(W=1080, H=1350, FLOOR=950, bokeh=(690, 925), prog=70, logo_top=46, logo_w=214,
                     frame_top=158, h1=64, frame_pad="28px 36px 32px", tag=30, glow=600, glow_up=430,
                     panel_top=1004, panel_h=286, panel_pad="40px 40px 30px", name=32, benefit=44, support=30,
                     body=40, cta_top=930, cta_body=32, cta=40, cta2=27, car_w=860,
                     prods={"oil_5w30.png": 430, "penetrating_oil.png": 480, "petrol_fuel_system_cleaner.png": 480},
                     cta_prods=(270, 320), file="slide", thumb=(432, 540)),
    "story": dict(W=1080, H=1920, FLOOR=1270, bokeh=(930, 1245), prog=250, logo_top=224, logo_w=236,
                  frame_top=360, h1=74, frame_pad="34px 40px 40px", tag=34, glow=760, glow_up=520,
                  panel_top=1352, panel_h=330, panel_pad="46px 44px 36px", name=36, benefit=50, support=34,
                  body=44, cta_top=1300, cta_body=40, cta=48, cta2=32, car_w=930,
                  prods={"oil_5w30.png": 600, "penetrating_oil.png": 640, "petrol_fuel_system_cleaner.png": 640},
                  cta_prods=(360, 430), file="story", thumb=(432, 768)),
}
FORMAT = sys.argv[1] if len(sys.argv) > 1 else "carousel"
L = LAYOUTS[FORMAT]
W, H, FLOOR = L["W"], L["H"], L["FLOOR"]   # FLOOR: horizon / wet floor line; products stand on it
OUT = OUT / FORMAT

# palette from the campaign brief (JLM Brand Bible)
YELLOW, BLACK, GREEN, WHITE, SILVER = "#FAB717", "#252729", "#376941", "#F2F0EB", "#C1C4C7"
# packaging category colours (sampled from the official labels; petrol = brand green)
CAT = {"oil": "#B8935C", "service": "#3F72AA", "petrol": GREEN}

STORIES = [
    {   # 1 · opening
        "kind": "intro",
        "tag": "منتجات JLM",
        "headline": "منتجات رح تساعد<br>سيارتك في <span class='y'>الشتاء</span>",
        "body": "منتجات JLM المناسبة لسيارتك في البرد والمطر.",
    },
    {   # 2 · 5W-30 — label: "5W30 · Premium Grade Performance Oil · Synthetic";
        # SAE J300: the "W" grade is the winter (low-temperature) viscosity rating
        "kind": "product", "img": "oil_5w30.png", "cat": "oil", "cat_ar": "زيت المحرّك",
        "tag": "المحرّك",
        "headline": "الصباح البارد<br>بدّه <span class='y'>زيت مناسب</span>",
        "name": "5W-30 Premium Grade Performance Oil",
        "benefit": "زيت اصطناعي بدرجة لزوجة 5W-30",
        "support": "حرف W يعني Winter: تصنيف SAE لأداء الزيت في درجات الحرارة المنخفضة.",
    },
    {   # 3 · Penetrating Oil — label: "Penetrates easily corroded, rusted and frozen parts ·
        # Dissolves rust and displaces moisture · Loosens rusted bolts, nuts, screws"
        "kind": "product", "img": "penetrating_oil.png", "cat": "service", "cat_ar": "خدمة وصيانة",
        "tag": "الصدأ والرطوبة",
        "headline": "المطر والرطوبة<br>بيزيدوا <span class='y'>الصدأ</span>",
        "name": "Penetrating Oil",
        "benefit": "يذيب الصدأ ويطرد الرطوبة",
        "support": "يخترق القطع الصدئة والمتجمّدة ويسهّل فكّ البراغي والصواميل.",
    },
    {   # 4 · Petrol Fuel System Cleaner — label: "Deep cleans injectors and combustion
        # chambers · Prevents new deposits across the fuel system · Perfect for routine fuel system care"
        "kind": "product", "img": "petrol_fuel_system_cleaner.png", "cat": "petrol", "cat_ar": "بنزين",
        "tag": "نظام الوقود",
        "headline": "حافظ على نظافة<br><span class='y'>نظام الوقود</span>",
        "name": "Fuel System Cleaner · Petrol",
        "benefit": "ينظّف البخاخات وغرف الاحتراق بعمق",
        "support": "مناسب للعناية الدورية بنظام الوقود، ويمنع تكوّن رواسب جديدة.",
    },
    {   # 5 · CTA
        "kind": "cta",
        "tag": "تواصل معنا",
        "headline": "سيارتك إلها احتياجاتها…<br>وإحنا <span class='y'>بنساعدك تختار!</span>",
        "body": "احكيلنا نوع سيارتك، موديلها، ونوع المحرك، وبنساعدك تتعرّف على المنتج المناسب.",
        "cta": "اسأل خبير JLM",
        "cta2": "تسوّق منتجاتنا من المتجر الإلكتروني",
        "url": "jlmstore.com",
    },
]


# ------------------------------------------------------------------ background ---
def background():
    rng = np.random.default_rng(11)
    y = np.arange(H)[:, None].astype(np.float32)
    img = np.zeros((H, W, 3), np.float32)
    # sky: cold charcoal gradient
    top, hor = np.array([18, 20, 23]), np.array([38, 43, 50])
    t = np.clip(y / FLOOR, 0, 1) ** 1.6
    sky = top * (1 - t)[..., None] + hor * t[..., None]
    img[:] = sky
    # wet asphalt below the horizon
    f = np.clip((y - FLOOR) / (H - FLOOR), 0, 1)
    floor = np.array([24, 26, 29]) * (1 - f)[..., None] + np.array([10, 11, 12]) * f[..., None]
    img = np.where((y >= FLOOR)[..., None], np.broadcast_to(floor, img.shape), img).astype(np.float32)
    grain = cv2.GaussianBlur(rng.normal(0, 1, (H, W)).astype(np.float32), (0, 0), 0.8) * 5
    img[FLOOR:] += grain[FLOOR:, :, None]
    # city bokeh along the horizon + their streaked reflections on the wet floor
    bok = np.zeros((H, W, 3), np.float32)
    refl = np.zeros((H, W, 3), np.float32)
    cols = [(205, 216, 228)] * 7 + [(250, 183, 23)] * 2 + [(200, 60, 50)]
    for _ in range(70):
        cx, cy = rng.uniform(-40, W + 40), rng.uniform(*L["bokeh"])
        r = rng.uniform(5, 30)
        c = np.array(cols[rng.integers(len(cols))], np.float32) * rng.uniform(.25, .7)
        cv2.circle(bok, (int(cx), int(cy)), int(r), c.tolist(), -1, cv2.LINE_AA)
        ry = int(2 * FLOOR - cy + 30)
        cv2.ellipse(refl, (int(cx), ry), (int(r * .6), int(r * 3.2)), 0, 0, 360, (c * .55).tolist(), -1, cv2.LINE_AA)
    bok = cv2.GaussianBlur(bok, (0, 0), 7)
    refl = cv2.GaussianBlur(refl, (0, 0), 9)
    refl = cv2.blur(refl, (3, 60))
    img += bok * (y < FLOOR)[..., None] + refl * (y >= FLOOR)[..., None]
    # fog band + wet sheen at the horizon
    fog = np.exp(-((y - FLOOR + 40) / (150 * H / 1920)) ** 2)
    img += fog[..., None] * np.array([24, 28, 34])
    sheen = np.exp(-((y - FLOOR - 6) / 26) ** 2) * (y >= FLOOR)
    img += sheen[..., None] * np.array([30, 34, 40])
    # rain: two layers of slanted streaks
    rain = np.zeros((H, W), np.float32)
    for layer, (n, ln, a, bl) in enumerate([(int(260 * H / 1920), (40, 90), (.05, .12), 1.2), (int(90 * H / 1920), (80, 150), (.10, .20), .6)]):
        lay = np.zeros((H, W), np.float32)
        for _ in range(n):
            x0, y0 = rng.uniform(-100, W + 100), rng.uniform(-100, H)
            length = rng.uniform(*ln)
            dx, dy = length * np.sin(np.radians(9)), length * np.cos(np.radians(9))
            cv2.line(lay, (int(x0), int(y0)), (int(x0 - dx), int(y0 + dy)), float(rng.uniform(*a)) * 255, 1, cv2.LINE_AA)
        rain += cv2.GaussianBlur(lay, (0, 0), bl)
    img += rain[..., None] * np.array([.75, .82, .9])
    # vignette
    yy, xx = np.mgrid[0:H, 0:W]
    v = 1 - .55 * (((xx - W / 2) / (W * .75)) ** 2 + ((yy - H * .48) / (H * .62)) ** 2)
    img *= np.clip(v, .35, 1)[..., None]
    Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).save(BUILD / "bg.png")


def night_car():
    """The cut-out car as a night silhouette: dark, cool, hub caps blacked out."""
    car = Image.open(BUILD / "car_cut.png").convert("RGBA")
    a = np.array(car).astype(np.float32)
    a[:, :, :3] = a[:, :, :3] * np.array([.36, .39, .45])            # night grade, cool
    lum = a[:, :, :3].mean(2)
    a[:, :, :3] = np.clip((a[:, :, :3] - lum[..., None] * .35) * 1.15 + lum[..., None] * .35, 0, 255)
    img = Image.fromarray(a.astype(np.uint8))
    d = ImageDraw.Draw(img)
    for cx, cy in ((436, 610), (1228, 610)):                        # cover hub badges
        d.ellipse((cx - 22, cy - 22, cx + 22, cy + 22), fill=(16, 17, 18, 255))
    img = img.crop(img.getbbox())
    # drop the faint floor shadow rembg kept under the tyres
    arr = np.array(img)
    arr[:, :, 3] = np.where(arr[:, :, 3] < 90, 0, arr[:, :, 3])
    Image.fromarray(arr).save(BUILD / "car_night.png")


# -------------------------------------------------------------------- template ---
CSS = f"""
@font-face{{font-family:HNA;font-weight:700;src:url("{FONTS}/helveticaneueltarabic-bold.ttf")}}
@font-face{{font-family:HNA;font-weight:400;src:url("{FONTS}/helveticaneueltarabic-roman.ttf")}}
@font-face{{font-family:Albert;font-weight:100 900;src:url("{FONTS}/AlbertSans.ttf")}}
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:{W}px;height:{H}px;overflow:hidden;background:{BLACK}}}
.s{{position:relative;width:{W}px;height:{H}px;overflow:hidden;background:url(bg.png)}}
.ar{{font-family:HNA;direction:rtl;text-align:right;color:{WHITE}}}
.lat{{font-family:Albert;direction:ltr;unicode-bidi:isolate}}
.y{{color:{YELLOW}}}
/* header: progress (left) + official logo (top-right, fixed) */
.prog{{position:absolute;left:72px;top:{L["prog"]}px;display:flex;align-items:center;gap:10px}}
.prog i{{display:block;width:38px;height:6px;border-radius:3px;background:rgba(193,196,199,.32)}}
.prog i.on{{background:{YELLOW}}}
.prog b{{font-family:Albert;font-weight:700;font-size:26px;color:{SILVER};margin-left:10px;letter-spacing:1px}}
.logo{{position:absolute;right:72px;top:{L["logo_top"]}px;width:{L["logo_w"]}px}}
/* headline frame + tag (JLM ATL template) */
.frame{{position:absolute;left:72px;right:72px;top:{L["frame_top"]}px;border:5px solid {YELLOW};padding:{L["frame_pad"]}}}
.frame h1{{font-weight:700;font-size:{L["h1"]}px;line-height:1.28}}
.tag{{position:absolute;left:72px;top:0;transform:translateY(0);background:{YELLOW};color:{BLACK};
      font-family:HNA;font-weight:700;font-size:{L["tag"]}px;padding:10px 26px 12px;direction:rtl}}
/* product stage */
.stage{{position:absolute;left:0;right:0;top:0;height:{H}px}}
.glow{{position:absolute;left:50%;width:{L["glow"]}px;height:{L["glow"]}px;margin-left:-{L["glow"] // 2}px;border-radius:50%;filter:blur(30px)}}
.prod{{position:absolute;left:50%;transform:translateX(-50%);
       -webkit-box-reflect:below 2px linear-gradient(transparent 62%, rgba(255,255,255,.22));
       filter:drop-shadow(0 26px 30px rgba(0,0,0,.55))}}
.shadow{{position:absolute;left:50%;height:34px;border-radius:50%;background:rgba(0,0,0,.75);filter:blur(14px)}}
/* info panel with the brand drop */
.panel{{position:absolute;left:72px;right:72px;top:{L["panel_top"]}px;height:{L["panel_h"]}px;background:rgba(17,18,20,.82);
        border:1.5px solid rgba(193,196,199,.22);border-radius:26px;padding:{L["panel_pad"]}}}
.drop{{position:absolute;left:50%;top:-30px;margin-left:-19px;width:38px;height:52px}}
.name{{font-family:Albert;font-weight:800;font-size:{L["name"]}px;color:{WHITE};direction:ltr;display:flex;align-items:center;justify-content:flex-end;gap:16px;white-space:nowrap}}
.name i{{display:block;width:8px;height:40px;border-radius:4px}}
.cat{{position:absolute;left:40px;top:-22px;font-family:HNA;font-weight:700;font-size:28px;color:#fff;padding:5px 20px 8px;border-radius:8px;direction:rtl;white-space:nowrap}}
.benefit{{font-weight:700;font-size:{L["benefit"]}px;margin-top:20px;line-height:1.3;white-space:nowrap}}
.support{{font-weight:400;font-size:{L["support"]}px;color:{SILVER};margin-top:14px;line-height:1.5}}
.body{{font-weight:400;font-size:{L["body"]}px;line-height:1.5}}
.next{{font-family:HNA;font-weight:700;font-size:32px;color:{YELLOW};margin-top:26px;display:flex;align-items:center;gap:14px;direction:rtl}}
.cta{{display:block;margin-top:30px;background:{YELLOW};color:{BLACK};text-align:center;border-radius:60px;
      font-family:HNA;font-weight:700;font-size:{L["cta"]}px;padding:{L["cta"] * .4:.0f}px 0 {L["cta"] * .55:.0f}px;box-shadow:0 14px 40px rgba(250,183,23,.28)}}
.cta2{{margin-top:22px;text-align:center;font-family:HNA;font-size:{L["cta2"]}px;color:{SILVER};direction:rtl}}
.cta2 .lat{{color:{WHITE};font-weight:700}}
"""

DROP = (f"<svg class='drop' viewBox='0 0 38 52'><path d='M19 0 C19 0 0 24 0 33 A19 19 0 0 0 38 33 "
        f"C38 24 19 0 19 0 Z' fill='{YELLOW}'/></svg>")


def header(i):
    bars = "".join(f"<i class='{'on' if k <= i else ''}'></i>" for k in range(5))
    return (f"<div class='prog'>{bars}<b>0{i + 1} / 05</b></div>"
            f"<img class='logo' src='{ROOT}/assets/logo_on_dark.png'>")


def headline(s):
    return (f"<div class='frame ar' id='frame'><h1>{s['headline']}</h1></div>"
            f"<div class='tag' id='tag'>{html.escape(s['tag'])}</div>")


def product_stage(img, h, color, x_center=540, glow=True, floor=None):
    floor = floor or FLOOR
    im = Image.open(ROOT / "assets" / img)
    w = im.width * h / im.height
    top = floor + 18 - h
    g = (f"<div class='glow' style='left:{x_center}px;top:{FLOOR - L['glow_up']}px;"
         f"background:radial-gradient(closest-side, {color}88, {color}00)'></div>") if glow else ""
    return (g + f"<div class='shadow' style='left:{x_center - w * .55}px;width:{w * 1.1}px;top:{floor}px'></div>"
            f"<img class='prod' src='{ROOT}/assets/{img}' style='left:{x_center}px;top:{top}px;height:{h}px'>")


def story_html(i, s):
    body = ""
    if s["kind"] == "intro":
        car = Image.open(BUILD / "car_night.png")
        cw = L['car_w']
        ch = car.height * cw / car.width
        body = (f"<div class='glow' style='left:540px;top:{FLOOR - L['glow_up'] - 40}px;background:radial-gradient(closest-side,{YELLOW}30,{YELLOW}00)'></div>"
                f"<div class='shadow' style='left:{540 - cw * .48}px;width:{cw * .96}px;top:{FLOOR - 6}px'></div>"
                f"<img class='prod' src='car_night.png' style='left:540px;top:{FLOOR + 14 - ch}px;width:{cw}px'>"
                # head-light glow on the front (car faces right)
                f"<div style='position:absolute;left:{540 + cw * .40}px;top:{FLOOR - ch * .52}px;width:150px;height:46px;"
                f"border-radius:50%;background:radial-gradient(closest-side,#FFF6D8dd,#FFF6D800);filter:blur(6px)'></div>"
                f"<div style='position:absolute;left:{540 + cw * .45}px;top:{FLOOR - ch * .6}px;width:{cw * .6}px;height:{ch * .62}px;"
                f"background:linear-gradient(90deg,#FFF2C433,#FFF2C400);clip-path:polygon(0 42%,100% 0,100% 100%,0 58%);filter:blur(10px)'></div>")
        panel = (f"<div class='panel ar'>{DROP}<p class='body'>{html.escape(s['body'])}</p>"
                 f"<div class='next'>اسحب للتالي <svg width='54' height='24' viewBox='0 0 54 24'><path d='M50 12 H6 M16 2 L4 12 L16 22' "
                 f"fill='none' stroke='{YELLOW}' stroke-width='4' stroke-linecap='round' stroke-linejoin='round'/></svg></div></div>")
    elif s["kind"] == "product":
        c = CAT[s["cat"]]
        body = product_stage(s["img"], L["prods"][s["img"]], c)
        panel = (f"<div class='panel ar'>{DROP}<span class='cat' style='background:{c}'>{s['cat_ar']}</span>"
                 f"<div class='name'>{html.escape(s['name'])}<i style='background:{c}'></i></div>"
                 f"<p class='benefit'>{html.escape(s['benefit'])}</p><p class='support'>{html.escape(s['support'])}</p></div>")
    else:
        a, b = L["cta_prods"]
        prods = [("oil_5w30.png", a, 300, CAT["oil"]), ("penetrating_oil.png", b, 540, CAT["service"]),
                 ("petrol_fuel_system_cleaner.png", b, 780, CAT["petrol"])]
        body = (f"<div class='glow' style='left:540px;top:{FLOOR - L['glow_up'] - 40}px;background:radial-gradient(closest-side,{YELLOW}2a,{YELLOW}00)'></div>"
                + "".join(product_stage(img, h, c, x, glow=False, floor=L['cta_top'] - 30) for img, h, x, c in prods))
        panel = (f"<div class='panel ar' style='top:{L['cta_top']}px;height:auto'>{DROP}<p class='body' style='font-size:{L['cta_body']}px'>{html.escape(s['body'])}</p>"
                 f"<span class='cta'>{html.escape(s['cta'])}</span>"
                 f"<p class='cta2'>{html.escape(s['cta2'])} · <span class='lat'>{s['url']}</span></p></div>")
    # tag sits just under the frame: measured in the page
    js = ("<script>document.fonts.ready.then(()=>{const f=document.getElementById('frame'),t=document.getElementById('tag');"
          "t.style.top=(f.offsetTop+f.offsetHeight-5)+'px';document.body.dataset.ready=1;});</script>")
    return (f"<!doctype html><html><head><meta charset='utf-8'><style>{CSS}</style></head><body>"
            f"<div class='s'>{body}{header(i)}{headline(s)}{panel}</div>{js}</body></html>")


def shoot(src, dst):
    subprocess.run([CHROME, "--headless", "--no-sandbox", "--disable-gpu", "--hide-scrollbars",
                    "--force-device-scale-factor=1", f"--window-size={W},{H + 300}", "--virtual-time-budget=4000",
                    "--allow-file-access-from-files", f"--screenshot={dst}", str(src)],
                   check=True, capture_output=True)
    # headless keeps part of the window for browser chrome: shoot taller, keep the W x H page
    Image.open(dst).convert("RGB").crop((0, 0, W, H)).save(dst)


def main():
    BUILD.mkdir(exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    if not (BUILD / "car_cut.png").exists():
        from rembg import new_session, remove
        remove(Image.open(ROOT / "assets/car-side.jpg").convert("RGB"),
               session=new_session("isnet-general-use")).save(BUILD / "car_cut.png")
    background()
    night_car()
    files = []
    for i, s in enumerate(STORIES):
        p = BUILD / f"{L['file']}_{i + 1:02d}.html"
        p.write_text(story_html(i, s), encoding="utf-8")
        dst = OUT / f"{L['file']}_{i + 1:02d}.png"
        shoot(p, dst)
        files.append(dst)
        print("wrote", dst)
    # overview: the five slides side by side
    tw, tht = L["thumb"]
    th = [Image.open(f).convert("RGB").resize((tw, tht), Image.LANCZOS) for f in files]
    ov = Image.new("RGB", (tw * 5 + 24 * 6, tht + 48), (14, 15, 16))
    for k, t in enumerate(th):
        ov.paste(t, (24 + k * (tw + 24), 24))
    ov.save(OUT / "overview.jpg", quality=92)
    print("wrote", OUT / "overview.jpg")


if __name__ == "__main__":
    main()
