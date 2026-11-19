"""أدوات مشتركة لسكربتات مهارة المونتاج. مكتبة قياسية فقط — لا تبعيات خارجية."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import NoReturn

FFMPEG = shutil.which("ffmpeg") or str(Path.home() / ".local/bin/ffmpeg")
FFPROBE = shutil.which("ffprobe") or str(Path.home() / ".local/bin/ffprobe")


def die(msg: str, code: int = 1) -> NoReturn:
    print(f"\033[1;31mخطأ:\033[0m {msg}", file=sys.stderr)
    sys.exit(code)


def require_tools() -> None:
    for name, path in (("ffmpeg", FFMPEG), ("ffprobe", FFPROBE)):
        if not Path(path).exists() and not shutil.which(name):
            die(f"{name} غير مثبّت. شغّل: bash .claude/skills/video-montage/scripts/setup_tools.sh")


def run(cmd: list[str], *, capture: bool = True, check: bool = True) -> subprocess.CompletedProcess:
    """تشغيل أمر خارجي مع رسالة خطأ مفيدة بدل tracebackمبهم."""
    proc = subprocess.run(
        cmd,
        stdout=subprocess.PIPE if capture else None,
        stderr=subprocess.PIPE,
        text=True,
    )
    if check and proc.returncode != 0:
        tail = (proc.stderr or "").strip().splitlines()[-15:]
        die("فشل الأمر: " + " ".join(cmd[:6]) + " ...\n" + "\n".join(tail))
    return proc


def ffprobe_json(path: str) -> dict:
    proc = run([FFPROBE, "-v", "error", "-print_format", "json",
                "-show_format", "-show_streams", path])
    return json.loads(proc.stdout or "{}")


def stream(info: dict, kind: str) -> dict | None:
    for s in info.get("streams", []):
        if s.get("codec_type") == kind:
            return s
    return None


def parse_fps(rate: str | None) -> float:
    """'30000/1001' -> 29.97 . يعيد 30.0 عند التعذّر بدل الانهيار."""
    if not rate:
        return 30.0
    try:
        if "/" in rate:
            num, den = rate.split("/", 1)
            den_f = float(den)
            return float(num) / den_f if den_f else 30.0
        return float(rate)
    except (ValueError, ZeroDivisionError):
        return 30.0


def duration_of(info: dict) -> float:
    try:
        return float(info.get("format", {}).get("duration", 0.0))
    except (TypeError, ValueError):
        return 0.0


def ass_escape(text: str) -> str:
    """تهريب النص لملف ASS: الأقواس المعقوفة تفتح أوامر تنسيق."""
    return (text.replace("\\", "\\\\").replace("{", "\\{").replace("}", "\\}")
                .replace("\n", "\\N"))


def ass_time(seconds: float) -> str:
    """0.0 -> '0:00:00.00' بدقّة السنتي-ثانية التي يتطلّبها ASS."""
    seconds = max(0.0, seconds)
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = seconds % 60
    return f"{h}:{m:02d}:{s:05.2f}"


def srt_time(seconds: float) -> str:
    seconds = max(0.0, seconds)
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int(round((seconds - int(seconds)) * 1000))
    if ms == 1000:  # تفادي 00:00:01,1000
        s, ms = s + 1, 0
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def filter_escape(path: str) -> str:
    """تهريب مسار داخل سلسلة فلاتر ffmpeg (النقطتان تفصلان الوسائط)."""
    return path.replace("\\", "/").replace(":", "\\:").replace("'", "\\'")


def pick_arabic_font(preferred: list[str] | None = None) -> str:
    """اختيار خط عربي متاح فعليًا على النظام — يمنع ظهور مربّعات مكان الحروف."""
    preferred = preferred or ["Cairo", "Tajawal", "Almarai", "Noto Kufi Arabic",
                              "Noto Naskh Arabic", "Noto Sans Arabic"]
    fc = shutil.which("fc-list")
    if not fc:
        return preferred[-1]
    proc = run([fc, ":lang=ar", "family"], check=False)
    available = (proc.stdout or "").replace("\n", ",")
    for name in preferred:
        if name.lower() in available.lower():
            return name
    return "DejaVu Sans"


def load_plan(path: str) -> dict:
    p = Path(path)
    if not p.exists():
        die(f"ملف الخطة غير موجود: {path}")
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        die(f"خطة غير صالحة (JSON): {exc}")
