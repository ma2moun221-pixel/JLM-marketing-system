#!/usr/bin/env python3
"""تحويل خطة المونتاج إلى ورقة تنفيذ داخل CapCut المجاني + ملف SRT.

    python3 capcut_sheet.py out/plan.json --out out/capcut.md --srt out/captions.srt

CapCut لا يُتحكَّم به من سطر الأوامر، ولا يوجد تنسيق مشروع مفتوح يُكتب من الخارج.
لذلك المخرج هنا وصفة دقيقة بالثواني ينفّذها المستخدم على الجوال في دقائق —
مع SRT يستورده CapCut مباشرة فلا يعيد كتابة الكابشن يدويًا.
"""
from __future__ import annotations

import argparse
from pathlib import Path

from mvcommon import load_plan, srt_time

POS_AR = {
    "top-left": "أعلى يسار", "top-center": "أعلى الوسط", "top-right": "أعلى يمين",
    "left": "يسار الوسط", "center": "وسط الشاشة", "right": "يمين الوسط",
    "bottom-left": "أسفل يسار", "bottom-center": "أسفل الوسط",
    "bottom-right": "أسفل يمين",
}
STYLE_AR = {
    "hook": "الهوك — أعلى الثلث الأول، أكبر خط",
    "body": "الجسم — الثلث السفلي",
    "center": "وسط الشاشة",
    "cta": "دعوة للفعل — أسفل، لون مميز",
    "sub": "تعليق جانبي — صغير",
}
ASPECT_AR = {
    "9:16": "9:16 عمودي (Reels / TikTok / Shorts)",
    "16:9": "16:9 أفقي (YouTube)",
    "1:1": "1:1 مربّع",
    "4:5": "4:5 (Instagram Feed)",
    "keep": "كما هو في المصدر",
}


def write_srt(captions: list[dict], path: Path) -> int:
    """SRT بنص نظيف بلا علامات التمييز — CapCut لا يفهم نجوم التلوين."""
    blocks = []
    for i, c in enumerate(sorted(captions, key=lambda x: float(x.get("start", 0))), 1):
        start = float(c.get("start", 0))
        end = float(c.get("end", start + 2))
        text = str(c.get("text", "")).replace("*", "").strip()
        if not text:
            continue
        blocks.append(f"{i}\n{srt_time(start)} --> {srt_time(end)}\n{text}\n")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(blocks), encoding="utf-8")
    return len(blocks)


def build_sheet(plan: dict, srt_name: str | None) -> str:
    aspect = plan.get("aspect", "9:16")
    segments = plan.get("segments") or []
    captions = sorted(plan.get("captions") or [], key=lambda c: float(c.get("start", 0)))
    icons = sorted(plan.get("icons") or [], key=lambda c: float(c.get("start", 0)))
    music = plan.get("music") or {}
    color = plan.get("color") or {}
    total = plan.get("estimated_duration") or round(
        sum((s["end"] - s["start"]) / float(s.get("speed", 1) or 1) for s in segments), 2)

    L: list[str] = []
    add = L.append

    add("# ورقة تنفيذ المونتاج في CapCut (النسخة المجانية)")
    add("")
    add(f"**المصدر:** `{plan.get('input')}`  ")
    add(f"**المقاس:** {ASPECT_AR.get(aspect, aspect)}  ")
    add(f"**المدة المستهدفة:** {total} ثانية  ")
    add(f"**عدد المقاطع:** {len(segments)}")
    add("")
    add("> كل التوقيتات في جدول القصّ من **الفيديو الأصلي**.  ")
    add("> توقيتات الكابشن والأيقونات من **الخط الزمني بعد القصّ**.")
    add("")

    add("## 1) الإعداد")
    add("")
    add("1. `New project` ← استورد الفيديو الأصلي.")
    add(f"2. `Ratio` ← اختر **{aspect}**.")
    add("3. `Format` ← تأكّد أن الدقّة **1080p** ومعدّل الإطارات **30**.")
    add("")

    if segments:
        add("## 2) القصّ")
        add("")
        add("ضع رأس التشغيل عند كل توقيت ثم `Split`، واحذف ما بين المقاطع المحتفَظ بها.")
        add("")
        add("| # | من | إلى | المدة | السرعة | تكبير |")
        add("|---|---|---|---|---|---|")
        for i, s in enumerate(segments, 1):
            start, end = float(s["start"]), float(s["end"])
            speed = float(s.get("speed", 1.0) or 1.0)
            zoom = float(s.get("zoom", 1.0))
            zoom_txt = f"{zoom:.2f}× (Scale {round(zoom * 100)}%)" if zoom > 1.001 else "—"
            add(f"| {i} | {start:.2f}s | {end:.2f}s | {end - start:.2f}s "
                f"| {speed:.2f}× | {zoom_txt} |")
        add("")
        speeds = {round(float(s.get("speed", 1.0) or 1.0), 2) for s in segments}
        if speeds != {1.0}:
            add(f"**السرعة:** حدّد كل المقاطع ← `Speed` ← `Normal` ← "
                f"**{max(speeds):.2f}×**. فعّل `Pitch` لتبقى نبرة الصوت طبيعية.")
            add("")

    add("## 3) اللون")
    add("")
    if color:
        add("`Adjust` ← اضبط القيم التالية على **كل** المقاطع (وإلا اختلف لون اللقطات):")
        add("")
        add("| الإعداد | القيمة في CapCut |")
        add("|---|---|")
        contrast = round((float(color.get("contrast", 1.0)) - 1) * 100)
        sat = round((float(color.get("saturation", 1.0)) - 1) * 100)
        bright = round(float(color.get("brightness", 0.0)) * 100)
        add(f"| Contrast | {contrast:+d} |")
        add(f"| Saturation | {sat:+d} |")
        add(f"| Brightness | {bright:+d} |")
        if color.get("sharpen"):
            add("| Sharpen | +30 |")
        add("")
        add("نصيحة: اضبط المقطع الأول ثم `Copy` ← `Paste` على البقية "
            "(`Adjust` ينسخ مع خصائص المقطع).")
    else:
        add("لا تعديل لون في هذه الخطة.")
    add("")

    add("## 4) الكابشن")
    add("")
    if srt_name and captions:
        add(f"**الطريقة السريعة:** `Text` ← `Local subtitle` ← استورد **`{srt_name}`** "
            "(كل التوقيتات تدخل جاهزة).")
        add("")
        add("ثم نسّق النص:")
        add("")
        add("- **الخط:** أي خط عربي عريض متاح (Cairo أو ما يشبهه في قائمة CapCut).")
        add("- **الحدّ:** `Outline` أسود بسماكة 6–8 — بدونه يختفي النص على الخلفيات الفاتحة.")
        add("- **الظل:** `Shadow` خفيف.")
        add("- **الحركة:** `Animation` ← `In` ← **Bounce** أو **Pop** بمدة 0.3s.")
        add("- **الموضع:** ارفع النص فوق شريط الواجهة — اترك 18% من أسفل الشاشة فارغة.")
        add("")
    if captions:
        add("توقيتات الكابشن (بعد القصّ):")
        add("")
        add("| من | إلى | النص | النمط |")
        add("|---|---|---|---|")
        for c in captions:
            start = float(c.get("start", 0))
            end = float(c.get("end", start + 2))
            text = str(c.get("text", "")).replace("*", "**").replace("|", "\\|")
            add(f"| {start:.2f}s | {end:.2f}s | {text} "
                f"| {STYLE_AR.get(c.get('style', 'body'), c.get('style', 'body'))} |")
        add("")
        add("الكلمات **بين نجمتين** لوّنها بالأصفر يدويًا "
            "(حدّد الكلمة ← `Color`). كلمة واحدة في كل جملة، لا أكثر.")
    else:
        add("لا كابشن في هذه الخطة.")
    add("")

    add("## 5) الأيقونات")
    add("")
    if icons:
        add("`Stickers` ← ابحث عن الإيموجي ← ضعه على الخط الزمني بالتوقيت التالي.")
        add("")
        add("| من | إلى | الأيقونة | الموضع | الحجم | الحركة |")
        add("|---|---|---|---|---|---|")
        for ic in icons:
            start = float(ic.get("start", 0))
            end = float(ic.get("end", start + 1.5))
            label = ic.get("emoji") or Path(str(ic.get("image", "?"))).name
            size = round(float(ic.get("size", 0.16)) * 100)
            anim = "Pop / Bounce In" if ic.get("anim", "pop") == "pop" else "بلا حركة"
            add(f"| {start:.2f}s | {end:.2f}s | {label} "
                f"| {POS_AR.get(ic.get('pos', 'top-right'), ic.get('pos'))} "
                f"| ~{size}% من العرض | {anim} |")
        add("")
        add("قاعدة: أيقونتان على الشاشة كحد أقصى، وكل واحدة 1–2 ثانية فقط.")
    else:
        add("لا أيقونات في هذه الخطة.")
    add("")

    add("## 6) الصوت")
    add("")
    if music.get("path"):
        gain = float(music.get("gain_db", -18))
        add(f"1. `Audio` ← `Add music` ← استورد `{Path(str(music['path'])).name}` "
            "(أو اختر من مكتبة CapCut المجانية).")
        add(f"2. اضبط `Volume` للموسيقى على **{round(20 + gain)}%** تقريبًا (يقابل {gain:.0f} dB).")
        if music.get("ducking", True):
            add("3. فعّل **`Auto ducking`** على مسار الموسيقى — يخفضها تلقائيًا وقت الكلام. "
                "إن لم تجدها في نسختك، اخفض يدويًا بـ `Volume keyframes` عند كل جملة.")
        add("4. `Fade out` آخر ثانية من الموسيقى.")
    else:
        add("لا موسيقى في هذه الخطة. أضف من مكتبة CapCut المجانية "
            "(`Audio` ← `Sounds`) — مرخّصة للاستخدام داخل التطبيق.")
    add("")
    add("- ارفع صوت الكلام إلى **100%** وتحقّق ألا يتشوّه في القمم.")
    add("- مؤثّر صوتي (whoosh) على **أول انتقال فقط** — تكراره يجعل الفيديو صاخبًا.")
    add("")

    add("## 7) التصدير")
    add("")
    add("`Export` ← اضبط:")
    add("")
    add("| الإعداد | القيمة |")
    add("|---|---|")
    add("| Resolution | **1080p** |")
    add("| Frame rate | **30** |")
    add("| Bitrate | **Higher** (أو Recommended) |")
    add("| Format | MP4 |")
    add("")
    add("أطفئ `Add CapCut watermark to the end` إن ظهر الخيار.")
    add("")

    add("## 8) فحص أخير قبل النشر")
    add("")
    for item in [
        "الثانية الأولى فيها حركة وكابشن — لا مشهد ساكن.",
        "لا لقطة تتجاوز 4 ثوانٍ بلا تغيير بصري.",
        "كل كابشن ≤ 5 كلمات في السطر وداخل المنطقة الآمنة (18% سفلية فارغة).",
        "الموسيقى لا تغطّي الكلام في أي لحظة.",
        "دعوة واحدة للفعل في النهاية، لا ثلاث.",
        "شاهد الفيديو **بلا صوت** — هل الرسالة واضحة من الكابشن وحده؟",
    ]:
        add(f"- [ ] {item}")
    add("")
    return "\n".join(L) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser(description="ورقة تنفيذ CapCut من خطة المونتاج")
    ap.add_argument("plan")
    ap.add_argument("--out", default="out/capcut.md")
    ap.add_argument("--srt", default=None, help="مسار ملف SRT (يُستورد في CapCut)")
    args = ap.parse_args()

    plan = load_plan(args.plan)
    captions = plan.get("captions") or []

    srt_name = None
    if args.srt and captions:
        count = write_srt(captions, Path(args.srt))
        srt_name = Path(args.srt).name
        print(f"✅ {count} سطر → {args.srt}")

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(build_sheet(plan, srt_name), encoding="utf-8")
    print(f"✅ ورقة CapCut → {out}")


if __name__ == "__main__":
    main()
