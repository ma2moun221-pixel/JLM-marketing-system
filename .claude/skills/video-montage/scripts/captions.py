#!/usr/bin/env python3
"""توليد كابشن ASS احترافي يدعم العربية (تشكيل + RTL عبر libass).

مصادر النص الثلاثة:
    python3 captions.py --plan plan.json --out captions.ass
    python3 captions.py --text script.txt --duration 30 --out captions.ass
    python3 captions.py --srt in.srt --out captions.ass

تمييز كلمة: ضع نجمتين حولها  ->  "خفّض تكلفتك *50%* بخطوة واحدة"
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

from mvcommon import ass_escape, ass_time, die, load_plan, pick_arabic_font


def ass_color(hex_rgb: str, alpha: int = 0) -> str:
    """ألوان ASS بصيغة &HAABBGGRR — الترتيب معكوس عن HTML، لا تكتبها يدويًا.

    بلا علامة & ختامية: هذه الصيغة التي يقبلها حقل النمط في [V4+ Styles].
    العلامة الختامية مطلوبة فقط داخل أوامر التنسيق السطرية، وتضيفها `inline()`.
    """
    h = hex_rgb.lstrip("#")
    if len(h) != 6:
        h = "FFFFFF"
    r, g, b = h[0:2], h[2:4], h[4:6]
    return f"&H{alpha:02X}{b}{g}{r}".upper()


def inline(color: str) -> str:
    """&H00FFD400 -> &H00D4FF&  للاستخدام في {\\c...}

    الأمر السطري `\\c` يقبل ستّ خانات (BBGGRR) فقط؛ خانة الشفافية تُضبط بـ `\\1a`
    منفصلة. بعض المشغّلات تتساهل مع ثماني خانات وبعضها يتجاهل السطر كاملًا.
    """
    h = color.strip("&").lstrip("&H").rstrip("&")
    return f"&H{h[-6:].upper()}&"


WHITE = ass_color("FFFFFF")
BLACK = ass_color("000000")
YELLOW = ass_color("FFD400")
GREEN = ass_color("2BD47D")
SHADOW = ass_color("000000", 0x60)

# قوالب الأنماط. الأرقام مضبوطة على لوحة 1080×1920 ويُعاد قياسها تلقائيًا.
# الأحجام معايرة على لوحة 1080×1920 ويُعاد قياسها لأي مقاس آخر في build_header.
# لا تصغّرها: النص الذي يُقرأ مريحًا على شاشة الحاسوب يبدو صغيرًا على الجوال.
STYLE_PRESETS = {
    # الهوك: أعلى الثلث الأول، ضخم — يجب أن يُقرأ في نصف ثانية
    "hook":   {"size": 104, "color": WHITE,  "outline": 8, "align": 8, "margin_v": 260, "bold": -1},
    # الجسم: الثلث السفلي، فوق شريط واجهة تيك توك/ريلز
    "body":   {"size": 88,  "color": WHITE,  "outline": 7, "align": 2, "margin_v": 420, "bold": -1},
    # الوسط: للجمل المفصلية وبطاقات الختام
    "center": {"size": 100, "color": WHITE,  "outline": 8, "align": 5, "margin_v": 0,   "bold": -1},
    # CTA: أسفل، لون مميز
    "cta":    {"size": 90,  "color": YELLOW, "outline": 8, "align": 2, "margin_v": 380, "bold": -1},
    # بطاقة الختام: أكبر نمط — تحمل خلاصة الفيديو (الاسم، التاريخ، المكان)
    "card":   {"size": 120, "color": WHITE,  "outline": 9, "align": 5, "margin_v": 0,   "bold": -1},
    # همسة: صغير وخفيف للتعليقات الجانبية
    "sub":    {"size": 60,  "color": WHITE,  "outline": 5, "align": 2, "margin_v": 330, "bold": 0},
}

# الحركة: pop سريع عند الدخول + تلاشٍ. الظهور المفاجئ يبدو رخيصًا.
ANIMS = {
    "pop":   r"{\fad(100,120)\t(0,170,\fscx112\fscy112)\t(170,260,\fscx100\fscy100)}",
    "fade":  r"{\fad(220,220)}",
    "slide": r"{\fad(120,140)\move(0,40,0,0,0,220)}",
    "none":  "",
}

MAX_WORDS_PER_LINE = 5


def wrap_caption(text: str, max_words: int = MAX_WORDS_PER_LINE) -> str:
    """سطران كحد أقصى، 3–5 كلمات لكل سطر. السطر الطويل لا يُقرأ في ثانيتين.

    فاصل `|` (أو سطر جديد فعلي) في النص يعني كسرًا صريحًا يُحترم كما هو —
    مفيد لبطاقات الختام المكوّنة من ثلاثة أسطر، حيث العدّ الآلي يكسر في مكان خاطئ.
    """
    if "|" in text or "\n" in text:
        lines = [ln.strip() for ln in text.replace("|", "\n").split("\n")]
        return "\n".join(ln for ln in lines if ln)

    words = text.split()
    if len(words) <= max_words:
        return text
    mid = (len(words) + 1) // 2
    return " ".join(words[:mid]) + "\n" + " ".join(words[mid:])


def apply_highlight(text: str, color: str = YELLOW) -> str:
    """تحويل *كلمة* إلى تلوين ASS. النص يُهرَّب أولًا ثم تُحقن أوامر التنسيق."""
    parts = re.split(r"\*([^*]+)\*", text)
    out = []
    for i, part in enumerate(parts):
        esc = ass_escape(part)
        out.append(f"{{\\c{inline(color)}}}{esc}{{\\c{inline(WHITE)}}}" if i % 2 else esc)
    return "".join(out)


def layout_scale(width: int, height: int) -> float:
    """القياس بأصغر النسبتين: الاعتماد على الارتفاع وحده يصغّر النص في الإطارات
    الأطول من 9:16، والاعتماد على العرض وحده يضخّمه في 16:9."""
    return min(width / 1080.0, height / 1920.0)


def build_header(width: int, height: int, font: str) -> str:
    scale = layout_scale(width, height)
    lines = [
        "[Script Info]",
        "ScriptType: v4.00+",
        f"PlayResX: {width}",
        f"PlayResY: {height}",
        "WrapStyle: 0",
        "ScaledBorderAndShadow: yes",
        "YCbCr Matrix: TV.709",
        "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, "
        "BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, "
        "BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
    ]
    for name, s in STYLE_PRESETS.items():
        lines.append(
            f"Style: {name},{font},{max(18, round(s['size'] * scale))},{s['color']},{WHITE},"
            f"{BLACK},{SHADOW},{s['bold']},0,0,0,100,100,0,0,1,"
            f"{max(1, round(s['outline'] * scale))},{max(1, round(3 * scale))},"
            f"{s['align']},60,60,{round(s['margin_v'] * scale)},1"
        )
    lines += ["", "[Events]",
              "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
    return "\n".join(lines)


def build_events(captions: list[dict], scale: float = 1.0) -> list[str]:
    """`margin_v` على كابشن مفرد يزيحه عن عنصر مزدحم في لقطة بعينها (لافتة، وجه).

    القيمة بمقياس اللوحة المرجعية 1080×1920 مثل هوامش الأنماط، ويعاد قياسها هنا.
    """
    events = []
    for c in sorted(captions, key=lambda x: float(x.get("start", 0))):
        start = float(c.get("start", 0))
        end = float(c.get("end", start + 2.0))
        if end <= start:
            end = start + 1.2
        style = c.get("style", "body")
        if style not in STYLE_PRESETS:
            style = "body"
        anim = ANIMS.get(c.get("anim", "pop"), ANIMS["pop"])
        raw = wrap_caption(str(c.get("text", "")).strip())
        if not raw:
            continue
        color = GREEN if c.get("highlight_color") == "green" else YELLOW
        body = apply_highlight(raw, color).replace("\n", "\\N")
        margin_v = round(float(c["margin_v"]) * scale) if c.get("margin_v") else 0
        events.append(f"Dialogue: 0,{ass_time(start)},{ass_time(end)},{style},,"
                      f"0,0,{margin_v},,{anim}{body}")
    return events


def auto_time(text_blocks: list[str], duration: float, start_at: float = 0.0) -> list[dict]:
    """توزيع نص بلا توقيتات على المدة بالتناسب مع طول كل جملة.

    ليس بديلًا عن التفريغ الصوتي، لكنه يعطي بداية معقولة للضبط اليدوي.
    """
    blocks = [b.strip() for b in text_blocks if b.strip()]
    if not blocks:
        return []
    weights = [max(len(b), 8) for b in blocks]
    total = sum(weights)
    span = max(0.5, duration - start_at)
    out, cursor = [], start_at
    for i, (block, w) in enumerate(zip(blocks, weights)):
        seg = min(max(span * w / total, 0.9), 4.0)  # 0.9s ليُقرأ، 4s قبل أن يُمَل
        out.append({
            "start": round(cursor, 2),
            "end": round(cursor + seg, 2),
            "text": block,
            "style": "hook" if i == 0 else "body",
            "anim": "pop",
        })
        cursor += seg
    return out


def parse_srt(path: str) -> list[dict]:
    def to_sec(stamp: str) -> float:
        stamp = stamp.strip().replace(".", ",")
        hh, mm, rest = stamp.split(":")
        ss, ms = (rest.split(",") + ["0"])[:2]
        return int(hh) * 3600 + int(mm) * 60 + int(ss) + int(ms.ljust(3, "0")[:3]) / 1000

    text = Path(path).read_text(encoding="utf-8", errors="replace")
    out = []
    for block in re.split(r"\n\s*\n", text.strip()):
        lines = [ln for ln in block.splitlines() if ln.strip()]
        timing = next((ln for ln in lines if "-->" in ln), None)
        if not timing:
            continue
        try:
            a, b = timing.split("-->")
            start, end = to_sec(a), to_sec(b)
        except (ValueError, IndexError):
            continue
        body = " ".join(lines[lines.index(timing) + 1:])
        if body:
            out.append({"start": start, "end": end, "text": body,
                        "style": "body", "anim": "pop"})
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description="توليد كابشن ASS احترافي")
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--plan", help="plan.json يحتوي مفتاح captions")
    src.add_argument("--text", help="ملف نصّي: كل سطر = كابشن (يُوقَّت تلقائيًا)")
    src.add_argument("--srt", help="ملف SRT موجود")
    ap.add_argument("--out", required=True)
    ap.add_argument("--duration", type=float, default=30.0, help="مع --text فقط")
    ap.add_argument("--width", type=int, default=1080)
    ap.add_argument("--height", type=int, default=1920)
    ap.add_argument("--font", help="اسم الخط (افتراضيًا أول خط عربي متاح)")
    args = ap.parse_args()

    if args.plan:
        captions = load_plan(args.plan).get("captions", [])
        if not captions:
            die("لا يوجد مفتاح captions في الخطة.")
    elif args.text:
        p = Path(args.text)
        if not p.exists():
            die(f"ملف النص غير موجود: {args.text}")
        captions = auto_time(p.read_text(encoding="utf-8").splitlines(), args.duration)
    else:
        captions = parse_srt(args.srt)
        if not captions:
            die("لم يُقرأ أي سطر من ملف SRT.")

    font = args.font or pick_arabic_font()
    content = (build_header(args.width, args.height, font) + "\n"
               + "\n".join(build_events(captions, layout_scale(args.width, args.height)))
               + "\n")

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(content, encoding="utf-8")
    print(f"✅ {len(captions)} كابشن → {out}  (الخط: {font})")


if __name__ == "__main__":
    main()
