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
    "card": "بطاقة الختام — وسط الشاشة، أكبر خط",
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


def clean_text(text: str) -> str:
    """إزالة نجوم التمييز؛ CapCut لا يفهمها. `|` فاصل سطر صريح يصير سطرًا فعليًا."""
    return "\n".join(
        ln.strip() for ln in str(text).replace("*", "").replace("|", "\n").split("\n")
        if ln.strip()
    )


def write_srt(captions: list[dict], path: Path) -> int:
    """SRT بنص نظيف بلا علامات التمييز — CapCut لا يفهم نجوم التلوين."""
    blocks = []
    for i, c in enumerate(sorted(captions, key=lambda x: float(x.get("start", 0))), 1):
        start = float(c.get("start", 0))
        end = float(c.get("end", start + 2))
        text = clean_text(c.get("text", ""))
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
    total = plan.get("estimated_duration") or (round(
        sum((s["end"] - s["start"]) / float(s.get("speed", 1) or 1) for s in segments), 2)
        if segments else plan.get("source_duration"))

    L: list[str] = []
    add = L.append
    step = [0]

    def section(title: str) -> None:
        step[0] += 1
        add(f"## {step[0]}) {title}")
        add("")

    add("# ورقة تنفيذ المونتاج في CapCut (النسخة المجانية)")
    add("")
    add(f"**المصدر:** `{plan.get('input')}`  ")
    add(f"**المقاس:** {ASPECT_AR.get(aspect, aspect)}  ")
    add(f"**المدة:** {total} ثانية  " if total else "**المدة:** كما في المصدر  ")
    add(f"**القصّ:** {len(segments)} مقطع" if segments
        else "**القصّ:** بلا قصّ — الفيديو كامل والانتقالات الأصلية كما هي")
    add("")
    if segments:
        add("> توقيتات جدول القصّ من **الفيديو الأصلي**.  ")
        add("> توقيتات الكابشن والأيقونات من **الخط الزمني بعد القصّ**.")
    else:
        add("> كل التوقيتات من الفيديو الأصلي — لا قصّ يزيحها.")
    add("")

    section("الإعداد")
    add("1. `New project` ← استورد الفيديو الأصلي.")
    add("2. `Ratio` ← اترك النسبة كما هي (لا تغيّر المقاس)."
        if aspect == "keep" else f"2. `Ratio` ← اختر **{aspect}**.")
    add("3. `Format` ← أعلى دقّة متاحة ومعدّل إطارات **30**.")
    add("")

    if segments:
        section("القصّ")
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

    section("اللون")
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

    section("الكابشن")
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
            text = (str(c.get("text", "")).replace("*", "**")
                    .replace("|", " ⏎ ").replace("\n", " ⏎ "))
            add(f"| {start:.2f}s | {end:.2f}s | {text} "
                f"| {STYLE_AR.get(c.get('style', 'body'), c.get('style', 'body'))} |")
        add("")
        add("الكلمات **بين نجمتين** لوّنها بالأصفر يدويًا "
            "(حدّد الكلمة ← `Color`). كلمة واحدة في كل جملة، لا أكثر.")
        add("")
        add("الرمز `⏎` يعني كسر سطر داخل مربّع النص نفسه (وهو مطبَّق في ملف SRT).")
    else:
        add("لا كابشن في هذه الخطة.")
    add("")

    section("الأيقونات")
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

    outro = plan.get("outro") or {}
    if outro:
        section("الختام — تمويه تدريجي")
        o_start = float(outro.get("start", 0))
        o_ramp = float(outro.get("ramp", 0.8))
        add(f"من **{o_start:.2f}s** حتى **{o_start + o_ramp:.2f}s** تتحوّل الصورة من حادّة "
            "إلى مموّهة تدريجيًا، وتبقى مموّهة حتى النهاية. بطاقة الختام تُقرأ فوقها.")
        add("")
        add("في CapCut:")
        add("")
        add(f"1. `Split` عند **{o_start:.2f}s** لعزل المقطع الأخير.")
        add("2. حدّد المقطع الأخير ← `Effects` ← `Basic` ← **Blur**.")
        add(f"3. `Keyframes` على شدّة التمويه: 0 عند **{o_start:.2f}s** ← "
            f"الأقصى عند **{o_start + o_ramp:.2f}s**. بدون الكيفريم يظهر التمويه فجأة.")
        if outro.get("darken"):
            add(f"4. `Adjust` ← `Brightness` **-{round(float(outro['darken']) * 100)}** "
                "على المقطع الأخير ليزيد تباين النص.")
        add("")

    section("الصوت")
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
    fade = plan.get("audio_fade_out")
    if fade:
        add(f"- `Fade out` على مسار الصوت الأصلي: يبدأ عند **{float(fade['start']):.2f}s** "
            f"بمدّة **{float(fade.get('duration', 1.0)):.1f}s**.")
    add("- ارفع صوت الكلام إلى **100%** وتحقّق ألا يتشوّه في القمم.")
    add("- مؤثّر صوتي (whoosh) على **أول انتقال فقط** — تكراره يجعل الفيديو صاخبًا.")
    add("")

    section("التصدير")
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

    section("فحص أخير قبل النشر")
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
