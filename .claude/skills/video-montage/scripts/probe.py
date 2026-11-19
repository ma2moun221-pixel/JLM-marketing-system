#!/usr/bin/env python3
"""فحص فيديو قبل/بعد المونتاج: الأبعاد، الإيقاع، الصوت، الصمت، تغيّرات المشهد.

الاستخدام:
    python3 probe.py INPUT.mp4                 # تقرير مقروء
    python3 probe.py INPUT.mp4 --json out.json # + حفظ JSON لبناء الخطة
    python3 probe.py INPUT.mp4 --quick         # بدون تحليل الصوت والمشاهد (أسرع)
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from mvcommon import (FFMPEG, die, duration_of, ffprobe_json, parse_fps,
                      require_tools, run, stream)

SILENCE_THRESHOLD_DB = -32.0
SILENCE_MIN_SEC = 0.35
SCENE_THRESHOLD = 0.30


def detect_silence(path: str) -> list[dict]:
    """يعيد فترات الصمت — مرشّحة للحذف في `autocut`."""
    proc = run([FFMPEG, "-hide_banner", "-nostats", "-i", path,
                "-af", f"silencedetect=noise={SILENCE_THRESHOLD_DB}dB:d={SILENCE_MIN_SEC}",
                "-f", "null", "-"], check=False)
    log = proc.stderr or ""
    starts = [float(m) for m in re.findall(r"silence_start:\s*(-?[\d.]+)", log)]
    ends = [float(m) for m in re.findall(r"silence_end:\s*(-?[\d.]+)", log)]
    return [{"start": round(s, 2), "end": round(e, 2), "dur": round(e - s, 2)}
            for s, e in zip(starts, ends)]


def measure_loudness(path: str) -> dict:
    """قياس EBU R128. الهدف للنشر: ‎-14 LUFS."""
    proc = run([FFMPEG, "-hide_banner", "-nostats", "-i", path,
                "-af", "loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json",
                "-f", "null", "-"], check=False)
    log = proc.stderr or ""
    match = re.search(r"\{[^{}]*input_i[^{}]*\}", log, re.S)
    if not match:
        return {}
    try:
        raw = json.loads(match.group(0))
    except json.JSONDecodeError:
        return {}
    out = {}
    for key, label in (("input_i", "lufs"), ("input_tp", "true_peak_db"),
                       ("input_lra", "range_lu")):
        try:
            out[label] = float(raw[key])
        except (KeyError, TypeError, ValueError):
            pass
    return out


def detect_scenes(path: str, duration: float) -> list[float]:
    """لحظات تغيّر المشهد — نقاط القطع الطبيعية للمونتاج."""
    proc = run([FFMPEG, "-hide_banner", "-nostats", "-i", path,
                "-filter:v", f"select='gt(scene,{SCENE_THRESHOLD})',showinfo",
                "-f", "null", "-"], check=False)
    times = [round(float(m), 2)
             for m in re.findall(r"pts_time:([\d.]+)", proc.stderr or "")]
    return [t for t in times if 0.0 < t < duration]


def analyse(path: str, quick: bool = False) -> dict:
    info = ffprobe_json(path)
    if not info.get("streams"):
        die(f"تعذّرت قراءة الفيديو (ملف تالف أو صيغة غير مدعومة): {path}")

    v = stream(info, "video") or {}
    a = stream(info, "audio")
    dur = duration_of(info)
    w, h = int(v.get("width") or 0), int(v.get("height") or 0)
    fps = parse_fps(v.get("avg_frame_rate") or v.get("r_frame_rate"))

    if h and w:
        ratio = w / h
        aspect = ("9:16" if abs(ratio - 9 / 16) < 0.04 else
                  "16:9" if abs(ratio - 16 / 9) < 0.06 else
                  "1:1" if abs(ratio - 1) < 0.04 else
                  "4:5" if abs(ratio - 0.8) < 0.04 else f"{ratio:.2f}:1")
    else:
        aspect = "unknown"

    report = {
        "path": path,
        "duration": round(dur, 2),
        "width": w, "height": h, "aspect": aspect,
        "fps": round(fps, 3),
        "video_codec": v.get("codec_name"),
        "rotation": next((int(sd.get("rotation", 0))
                          for sd in v.get("side_data_list", []) if "rotation" in sd), 0),
        "has_audio": a is not None,
        "audio_codec": (a or {}).get("codec_name"),
        "audio_channels": (a or {}).get("channels"),
        "size_mb": round(Path(path).stat().st_size / 1_048_576, 2),
        "bitrate_kbps": round(int(info.get("format", {}).get("bit_rate", 0) or 0) / 1000),
    }

    if not quick and a is not None:
        report["loudness"] = measure_loudness(path)
        silence = detect_silence(path)
        report["silence"] = silence
        report["silence_total"] = round(sum(s["dur"] for s in silence), 2)
    if not quick:
        report["scene_cuts"] = detect_scenes(path, dur)

    report["recommendations"] = recommend(report)
    return report


def recommend(r: dict) -> list[str]:
    """ترجمة الأرقام إلى قرارات مونتاج. هذه هي القيمة الحقيقية للتقرير."""
    tips: list[str] = []
    dur = r["duration"]

    if r["aspect"] == "16:9":
        tips.append("أفقي — للـ Reels/TikTok حوّله 9:16 بخلفية ضبابية أو قصّ ذكي (crop_mode).")
    if r["rotation"]:
        tips.append(f"دوران {r['rotation']}° في الميتاداتا — طبّق transpose قبل أي فلتر آخر.")
    if r["height"] and r["height"] < 1080:
        tips.append(f"ارتفاع {r['height']}px أقل من 1080 — لن ترتفع الجودة بالتكبير؛ صدّر بالأبعاد الأصلية.")
    if r["fps"] > 50:
        tips.append(f"{r['fps']:.0f} fps — انزل إلى 30 لتقليل الحجم، أو استفد منها في سلو موشن 0.5×.")

    if dur > 90:
        tips.append(f"المدة {dur:.0f}s طويلة لريلز — اختر أقوى 30–45 ثانية.")
    elif dur > 60:
        tips.append(f"المدة {dur:.0f}s — انزل تحت 60s ليُنشر كـ Short/Reel.")

    sil = r.get("silence_total", 0)
    if sil > 1.5:
        pct = sil / dur * 100 if dur else 0
        tips.append(f"صمت {sil:.1f}s ({pct:.0f}% من المدة) — احذفه بـ autocut.py لرفع الإيقاع.")

    loud = r.get("loudness", {})
    if "lufs" in loud:
        lufs = loud["lufs"]
        if lufs < -20:
            tips.append(f"الصوت منخفض ({lufs:.1f} LUFS) — طبّع إلى ‎-14 LUFS.")
        elif lufs > -10:
            tips.append(f"الصوت مرتفع ({lufs:.1f} LUFS) وقد يتشوّه — طبّع إلى ‎-14 LUFS.")
        else:
            tips.append(f"مستوى الصوت جيد ({lufs:.1f} LUFS).")
    if not r["has_audio"]:
        tips.append("لا يوجد مسار صوتي — أضف موسيقى مجانية (راجع references/free-assets.md).")

    cuts = r.get("scene_cuts", [])
    if dur > 0:
        rate = len(cuts) / dur * 60
        if rate < 8:
            tips.append(f"إيقاع بطيء ({rate:.0f} قطع/دقيقة) — أضف قطعًا أو زووم كل 2–3 ثوانٍ.")
        elif rate > 45:
            tips.append(f"إيقاع سريع جدًا ({rate:.0f} قطع/دقيقة) — قد يُرهق المشاهد.")
    return tips


def print_report(r: dict) -> None:
    print("\n\033[1m━━━ تقرير فحص الفيديو ━━━\033[0m")
    print(f"  الملف        : {r['path']}")
    print(f"  المدة        : {r['duration']}s")
    print(f"  الأبعاد      : {r['width']}×{r['height']}  ({r['aspect']})  @ {r['fps']}fps")
    print(f"  الترميز      : {r['video_codec']} / {r.get('audio_codec') or 'بلا صوت'}")
    print(f"  الحجم        : {r['size_mb']} MB  ({r['bitrate_kbps']} kbps)")
    if r.get("loudness"):
        L = r["loudness"]
        print(f"  الصوت        : {L.get('lufs', '?')} LUFS, ذروة {L.get('true_peak_db', '?')} dBTP")
    if "silence_total" in r:
        print(f"  الصمت        : {r['silence_total']}s عبر {len(r.get('silence', []))} فترة")
    if "scene_cuts" in r:
        cuts = r["scene_cuts"]
        preview = ", ".join(f"{c}s" for c in cuts[:8]) + (" ..." if len(cuts) > 8 else "")
        print(f"  تغيّر المشهد : {len(cuts)} نقطة  [{preview}]")
    if r["recommendations"]:
        print("\n\033[1;33m  توصيات المونتاج:\033[0m")
        for tip in r["recommendations"]:
            print(f"    • {tip}")
    print()


def main() -> None:
    ap = argparse.ArgumentParser(description="فحص فيديو وإخراج توصيات مونتاج")
    ap.add_argument("input")
    ap.add_argument("--json", help="حفظ التقرير الكامل في ملف JSON")
    ap.add_argument("--quick", action="store_true", help="تخطّي تحليل الصوت والمشاهد")
    args = ap.parse_args()

    require_tools()
    if not Path(args.input).exists():
        die(f"الملف غير موجود: {args.input}")

    report = analyse(args.input, quick=args.quick)
    print_report(report)

    if args.json:
        out = Path(args.json)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"  تقرير JSON: {out}\n")


if __name__ == "__main__":
    main()
