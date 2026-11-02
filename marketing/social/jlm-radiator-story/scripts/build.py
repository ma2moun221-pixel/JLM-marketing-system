"""JLM Radiator Stop Leak — a series of three Instagram stories (1080×1920) from the client's photos.

    python3 scripts/build.py        # writes out/story_1_good_morning.png, story_2_product.png, story_3_use_order.png

1 «صباح الخير من JLM» — start-of-week greeting with a morning glow and the can · 2 the product: title, the two
engine-bay photos, three short points, the honest note · 3 «سهل الاستعمال»: the pour, «أضفه إلى سائل التبريد»
(from the label), and the usual CTA. Progress dots top-left tie the three together.
Earlier single-image version (all in one):
Layout (HTML in the JLM fonts, rendered by headless Chromium, cropped to 1080×1920):
logo top-right · title «مانع تسرّب الرادياتور» / Radiator Stop Leak · the two engine-bay photos as cards
(the can on the radiator, the pour) · the cut-out can beside three short points taken from the client's
copy · the honest note «لا يصلح القطع التالفة» · the usual CTA (jlmstore.com, delivery).
"""
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FONTS = (ROOT.parents[2] / "brand/jlm/fonts").as_uri()
CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"

HEAD = f"""<!doctype html><html lang="ar"><head><meta charset="utf-8"><style>
@font-face{{font-family:HNA;font-weight:700;src:url('{FONTS}/helveticaneueltarabic-bold.ttf')}}
@font-face{{font-family:HNA;font-weight:400;src:url('{FONTS}/helveticaneueltarabic-roman.ttf')}}
@font-face{{font-family:Albert;font-weight:100 900;src:url('{FONTS}/AlbertSans.ttf')}}
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:1080px;height:1920px;background:#252729;overflow:hidden}}
#s{{position:relative;width:1080px;height:1920px;overflow:hidden;
   background:radial-gradient(1000px 900px at 50% 38%,#33363a 0%,#252729 60%,#1b1c1e 100%)}}
.ar{{font-family:HNA;direction:rtl;color:#F1F0EC}}
.lat{{font-family:Albert;font-weight:800;direction:ltr;unicode-bidi:isolate}}
.y{{color:#FAB817}}
#logo{{position:absolute;right:64px;top:96px;width:210px}}
#t1{{position:absolute;right:64px;top:210px;font-weight:700;font-size:82px;line-height:1.15}}
#t2{{position:absolute;right:66px;top:318px;font-size:46px;color:#FAB817}}
.card{{position:absolute;top:410px;width:462px;height:520px;border-radius:26px;overflow:hidden;
      box-shadow:0 24px 50px rgba(0,0,0,.45);border:2px solid rgba(192,196,199,.25)}}
.card img{{width:100%;height:100%;object-fit:cover}}
.tag{{position:absolute;bottom:18px;right:18px;padding:8px 20px 12px;border-radius:30px;background:rgba(20,21,22,.82);
     border:2px solid #FAB817;font-family:HNA;font-weight:700;font-size:30px;color:#F1F0EC;direction:rtl}}
#can{{position:absolute;left:66px;top:965px;height:520px;filter:drop-shadow(0 26px 30px rgba(0,0,0,.55))}}
#glow{{position:absolute;left:-50px;top:990px;width:420px;height:520px;border-radius:50%;
      background:radial-gradient(closest-side,rgba(250,184,23,.22),rgba(250,184,23,0))}}
#pts{{position:absolute;right:64px;top:1000px;width:730px}}
.pt{{display:flex;flex-direction:row-reverse;align-items:flex-start;gap:18px;margin-bottom:28px}}
.pt b{{flex:0 0 46px;height:46px;border-radius:23px;background:#FAB817;color:#252729;font-family:Albert;font-weight:900;
      font-size:28px;display:flex;align-items:center;justify-content:center;margin-top:4px}}
.pt span{{font-family:HNA;font-weight:700;font-size:40px;line-height:1.35;color:#F1F0EC;direction:rtl;text-align:right}}
#note{{position:absolute;right:64px;top:1405px;font-size:28px;color:#C0C4C7}}
#line{{position:absolute;left:64px;right:64px;top:1478px;height:2px;background:linear-gradient(90deg,rgba(250,184,23,0),#FAB817,rgba(250,184,23,0))}}
#cta{{position:absolute;left:0;width:1080px;top:1500px;text-align:center;font-weight:700;font-size:52px;line-height:1.3}}
#pill{{position:absolute;left:310px;top:1592px;width:460px;height:84px;border-radius:42px;background:#FAB817;color:#252729;
      font-family:Albert;font-weight:800;font-size:48px;display:flex;align-items:center;justify-content:center}}
#del{{position:absolute;left:0;width:1080px;top:1690px;text-align:center;font-size:36px;font-weight:400}}

.dots{{position:absolute;left:64px;top:122px;display:flex;gap:10px}}
.dots i{{width:34px;height:8px;border-radius:4px;background:rgba(192,196,199,.35)}}
.dots i.on{{background:#FAB817}}
#sun{{position:absolute;left:50%;top:330px;width:900px;height:900px;margin-left:-450px;border-radius:50%;
     background:radial-gradient(closest-side,rgba(250,184,23,.55),rgba(250,184,23,.18) 45%,rgba(250,184,23,0))}}
#ring{{position:absolute;left:50%;top:520px;width:520px;height:520px;margin-left:-260px;border-radius:50%;border:3px solid rgba(250,184,23,.55)}}
#gm1{{position:absolute;left:0;width:1080px;top:230px;text-align:center;font-weight:700;font-size:118px}}
#gm2{{position:absolute;left:0;width:1080px;top:415px;text-align:center;font-weight:700;font-size:70px}}
#hero1{{position:absolute;left:50%;top:600px;height:760px;transform:translateX(-50%);filter:drop-shadow(0 40px 40px rgba(0,0,0,.6))}}
#gm3{{position:absolute;left:0;width:1080px;top:1420px;text-align:center;font-weight:400;font-size:52px;line-height:1.45}}
#big{{position:absolute;left:64px;right:64px;top:410px;height:820px;border-radius:28px;overflow:hidden;
     box-shadow:0 24px 50px rgba(0,0,0,.45);border:2px solid rgba(192,196,199,.25)}}
#big img{{width:100%;height:100%;object-fit:cover;object-position:55% 50%}}
#use1{{position:absolute;right:64px;top:1265px;font-weight:700;font-size:62px}}
#use2{{position:absolute;right:64px;top:1385px;font-weight:400;font-size:44px;color:#C0C4C7}}
</style></head><body><div id="s">
<img id="logo" src="../assets/logo.png">"""

DOTS = lambda k: '<div class="dots">' + "".join(f'<i class="{"on" if i == k else ""}"></i>' for i in range(3)) + "</div>"
CTA = """<div id="line"></div>
<div id="cta" class="ar"><span class="y">اطلبه الآن</span> من خلال</div>
<div id="pill">jlmstore.com</div>
<div id="del" class="ar">مع توفّر <span class="y">خدمة التوصيل</span></div>"""

PAGES = {
 "1_good_morning": DOTS(0) + """
<div id="sun"></div><div id="ring"></div>
<div id="gm1" class="ar">صباح الخير</div>
<div id="gm2" class="ar">من <span class="lat y">JLM</span></div>
<img id="hero1" src="../assets/product_cut.png">
<div id="gm3" class="ar">بداية <span class="y">أسبوع موفّقة</span> للجميع<br>وانطلاقة جديدة مع سيارتك</div>""",
 "2_product": DOTS(1) + """
<div id="t1" class="ar">مانع تسرّب <span class="y">الرادياتور</span></div>
<div id="t2" class="lat">Radiator Stop Leak</div>
<div class="card" style="right:64px"><img src="../assets/in_engine.png" style="object-position:50% 50%"></div>
<div class="card" style="left:64px"><img src="../assets/pour.png" style="object-position:58% 50%"></div>
<div id="glow"></div>
<img id="can" src="../assets/product_cut.png">
<div id="pts">
 <div class="pt"><b>1</b><span>يغلق الثقوب الصغيرة في الرادياتور ومضخات التبريد</span></div>
 <div class="pt"><b>2</b><span>ينظّفها من الأكسدة</span></div>
 <div class="pt"><b>3</b><span>ينعش اللبادات ويقلّل التسريب</span></div>
</div>
<div id="note" class="ar">*لا يعمل على إصلاح القطع التالفة</div>""",
 "3_use_order": DOTS(2) + """
<div id="t1" class="ar">سهل <span class="y">الاستعمال</span></div>
<div id="big"><img src="../assets/pour.png"></div>
<div id="use1" class="ar">أضفه إلى <span class="y">سائل التبريد</span></div>
<div id="use2" class="ar">مانع تسرّب الرادياتور من <span class="lat y">JLM</span></div>""" + CTA,
}


def main():
    from PIL import Image
    (ROOT / "out").mkdir(exist_ok=True)
    for name, body in PAGES.items():
        page = ROOT / "out/_story.html"
        page.write_text(HEAD + body + "</div></body></html>", encoding="utf-8")
        raw = ROOT / "out/_shot.png"
        subprocess.run([CHROME, "--headless", "--no-sandbox", "--hide-scrollbars", "--allow-file-access-from-files",
                        f"--screenshot={raw}", "--window-size=1080,2220", "--virtual-time-budget=3000", page.as_uri()],
                       check=True, capture_output=True)
        Image.open(raw).crop((0, 0, 1080, 1920)).convert("RGB").save(ROOT / f"out/story_{name}.png")
        raw.unlink()
        page.unlink()
        print("wrote", f"out/story_{name}.png")


if __name__ == "__main__":
    main()
