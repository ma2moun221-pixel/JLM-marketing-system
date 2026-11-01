"""JLM Radiator Stop Leak — one Instagram story image (1080×1920) from the client's three photos.

    python3 scripts/build.py        # writes out/radiator_stop_leak_story.png

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

HTML = f"""<!doctype html><html lang="ar"><head><meta charset="utf-8"><style>
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
</style></head><body><div id="s">
<img id="logo" src="../assets/logo.png">
<div id="t1" class="ar">مانع تسرّب <span class="y">الرادياتور</span></div>
<div id="t2" class="lat">Radiator Stop Leak</div>
<div class="card" style="right:64px"><img src="../assets/in_engine.png" style="object-position:50% 50%"></div>
<div class="card" style="left:64px"><img src="../assets/pour.png" style="object-position:58% 50%"><div class="tag">سهل الاستعمال</div></div>
<div id="glow"></div>
<img id="can" src="../assets/product_cut.png">
<div id="pts">
 <div class="pt"><b>1</b><span>يغلق الثقوب الصغيرة في الرادياتور والبرابيج ومضخات التبريد</span></div>
 <div class="pt"><b>2</b><span>ينظّفها من الأكسدة</span></div>
 <div class="pt"><b>3</b><span>ينعش اللبادات ويقلّل التسريب</span></div>
</div>
<div id="note" class="ar">*لا يعمل على إصلاح القطع التالفة</div>
<div id="line"></div>
<div id="cta" class="ar"><span class="y">اطلبه الآن</span> من خلال</div>
<div id="pill">jlmstore.com</div>
<div id="del" class="ar">مع توفّر <span class="y">خدمة التوصيل</span></div>
</div></body></html>"""


def main():
    (ROOT / "out").mkdir(exist_ok=True)
    page = ROOT / "out/_story.html"
    page.write_text(HTML, encoding="utf-8")
    raw = ROOT / "out/_shot.png"
    subprocess.run([CHROME, "--headless", "--no-sandbox", "--hide-scrollbars", "--allow-file-access-from-files",
                    f"--screenshot={raw}", "--window-size=1080,2220", "--virtual-time-budget=3000", page.as_uri()],
                   check=True, capture_output=True)
    from PIL import Image
    Image.open(raw).crop((0, 0, 1080, 1920)).convert("RGB").save(ROOT / "out/radiator_stop_leak_story.png")
    raw.unlink()
    page.unlink()
    print("wrote out/radiator_stop_leak_story.png")


if __name__ == "__main__":
    main()
