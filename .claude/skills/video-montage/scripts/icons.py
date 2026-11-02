#!/usr/bin/env python3
"""استخراج أيقونات إيموجي ملوّنة كصور PNG شفّافة — مجانًا وبلا إنترنت.

المصدر: خط Noto Color Emoji (رخصة SIL OFL) الذي يخزّن كل إيموجي كصورة PNG
داخل جدول CBDT. نستخرجها كما هي بلا إعادة رسم، فتبقى بجودتها الأصلية.

    python3 icons.py 🔥 🚀 💰 --out-dir out/icons
    python3 icons.py --plan plan.json --out-dir out/icons   # كل أيقونات الخطة
    python3 icons.py --list-cached --out-dir out/icons
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

from mvcommon import die, load_plan

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"

EMOJI_FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf",
    "/usr/share/fonts/truetype/noto-color-emoji/NotoColorEmoji.ttf",
    "/usr/share/fonts/NotoColorEmoji.ttf",
    "/System/Library/Fonts/Apple Color Emoji.ttc",
    str(Path.home() / ".local/share/fonts/NotoColorEmoji.ttf"),
]


def find_emoji_font() -> str | None:
    for path in EMOJI_FONT_CANDIDATES:
        if Path(path).exists():
            return path
    fc = shutil.which("fc-match")
    if fc:
        proc = subprocess.run([fc, "-f", "%{file}", "emoji"],
                              capture_output=True, text=True)
        candidate = (proc.stdout or "").strip()
        if candidate and Path(candidate).exists() and "emoji" in candidate.lower():
            return candidate
    return None


def ensure_fonttools() -> None:
    try:
        import fontTools  # noqa: F401
    except ImportError:
        print("… تثبيت fontTools (مجاني، مكتبة بايثون)")
        subprocess.run([sys.executable, "-m", "pip", "install", "--quiet",
                        "--user", "fonttools"], check=False)
        try:
            import fontTools  # noqa: F401
        except ImportError:
            die("تعذّر تثبيت fontTools. ثبّته يدويًا: pip install fonttools")


def slug(emoji: str) -> str:
    """اسم ملف آمن مبني على نقاط الترميز: 🔥 -> u1f525"""
    return "_".join(f"u{ord(ch):x}" for ch in emoji if ord(ch) > 0x20)


def extract(emoji: str, font_path: str, out_dir: Path) -> Path | None:
    """يستخرج صورة الإيموجي. يعيد None إن لم يكن له رسم في الخط."""
    from fontTools.ttLib import TTFont

    out = out_dir / f"{slug(emoji)}.png"
    if out.exists() and out.stat().st_size > 0:
        return out

    try:
        font = TTFont(font_path, fontNumber=0, lazy=True)
    except Exception as exc:  # noqa: BLE001 — الخط قد يكون تالفًا أو بصيغة غير مدعومة
        print(f"  ⚠ تعذّرت قراءة خط الإيموجي: {exc}")
        return None

    # نتجاهل المُعدِّلات (variation selector / ZWJ) ونأخذ نقطة الترميز الأساسية.
    codepoints = [ord(c) for c in emoji
                  if ord(c) not in (0xFE0F, 0xFE0E, 0x200D) and ord(c) > 0x20]
    if not codepoints:
        return None

    cmap = font.getBestCmap()
    glyph = next((cmap[cp] for cp in codepoints if cp in cmap), None)
    if glyph is None:
        print(f"  ⚠ {emoji} غير موجود في الخط — استخدم أيقونة PNG بدل ذلك.")
        return None

    if "CBDT" not in font:
        print("  ⚠ الخط بلا جدول CBDT (ليس خط إيموجي ملوّن).")
        return None

    for strike in font["CBDT"].strikeData:
        entry = strike.get(glyph)
        if entry is None:
            continue
        raw = getattr(entry, "data", None) or getattr(entry, "imageData", b"")
        idx = raw.find(PNG_MAGIC)
        if idx < 0:
            continue
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(raw[idx:])
        return out

    print(f"  ⚠ {emoji} بلا صورة نقطية في الخط.")
    return None


def collect_from_plan(plan_path: str) -> list[str]:
    plan = load_plan(plan_path)
    return [i["emoji"] for i in plan.get("icons", []) if i.get("emoji")]


def main() -> None:
    ap = argparse.ArgumentParser(description="استخراج إيموجي كصور PNG شفّافة")
    ap.add_argument("emojis", nargs="*", help="إيموجي مفصولة بمسافات")
    ap.add_argument("--plan", help="استخرج كل الإيموجي المذكورة في plan.json")
    ap.add_argument("--out-dir", default="out/icons")
    ap.add_argument("--font", help="مسار خط إيموجي ملوّن مخصّص")
    ap.add_argument("--list-cached", action="store_true", help="اعرض ما هو مستخرج مسبقًا")
    args = ap.parse_args()

    out_dir = Path(args.out_dir)

    if args.list_cached:
        files = sorted(out_dir.glob("*.png")) if out_dir.exists() else []
        print(f"{len(files)} أيقونة في {out_dir}")
        for f in files:
            print(f"  {f.name}")
        return

    wanted = list(args.emojis)
    if args.plan:
        wanted += collect_from_plan(args.plan)
    # إزالة التكرار مع الحفاظ على الترتيب
    wanted = list(dict.fromkeys(wanted))
    if not wanted:
        die("لم تُحدَّد أي إيموجي. مثال: python3 icons.py 🔥 🚀")

    font_path = args.font or find_emoji_font()
    if not font_path:
        die("لم يُعثر على خط إيموجي ملوّن.\n"
            "ثبّته: apt-get install fonts-noto-color-emoji\n"
            "أو مرّر أيقوناتك عبر \"image\": \"path.png\" في الخطة.")

    ensure_fonttools()
    print(f"الخط: {font_path}")

    made = 0
    for emoji in wanted:
        path = extract(emoji, font_path, out_dir)
        if path:
            made += 1
            print(f"  ✅ {emoji} → {path}")

    print(f"\n{made}/{len(wanted)} أيقونة جاهزة في {out_dir}")
    if made < len(wanted):
        print("الأيقونات الناقصة: استخدم PNG خاصة بك عبر \"image\" في الخطة "
              "(مصادر مجانية في references/free-assets.md).")


if __name__ == "__main__":
    main()
