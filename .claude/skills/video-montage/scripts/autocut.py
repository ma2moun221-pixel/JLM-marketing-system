#!/usr/bin/env python3
"""قصّ آلي: حذف الصمت وبناء خطة مونتاج ابتدائية جاهزة للتعديل.

    python3 autocut.py raw.mp4 --out out/plan.json --aspect 9:16 --max-duration 45

المخرج ملف plan.json فيه المقاطع المحتفَظ بها. أضف إليه الكابشن والأيقونات
والموسيقى، ثم مرّره إلى render.py.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from mvcommon import die, require_tools
from probe import analyse

# هامش أمان حول الكلام: القصّ على حدّ الصمت تمامًا يبتر أول/آخر حرف.
PAD_BEFORE = 0.12
PAD_AFTER = 0.18


def keep_segments(silence: list[dict], duration: float,
                  min_silence: float = 0.35,
                  min_segment: float = 0.4) -> list[dict]:
    """يحوّل فترات الصمت إلى مقاطع كلام يُحتفظ بها، مع هوامش ودمج القصير."""
    gaps = [s for s in silence if s["dur"] >= min_silence]
    segments: list[dict] = []
    cursor = 0.0

    for gap in gaps:
        end = max(cursor, gap["start"] + PAD_AFTER)
        if end - cursor >= min_segment:
            segments.append({"start": round(cursor, 2), "end": round(end, 2)})
        cursor = max(cursor, gap["end"] - PAD_BEFORE)

    if duration - cursor >= min_segment:
        segments.append({"start": round(cursor, 2), "end": round(duration, 2)})

    # دمج المقاطع المتلاصقة (فجوة < 0.1s) — القطع هناك يُسمع كطقطقة.
    merged: list[dict] = []
    for seg in segments:
        if merged and seg["start"] - merged[-1]["end"] < 0.1:
            merged[-1]["end"] = seg["end"]
        else:
            merged.append(seg)
    return merged


def trim_to_budget(segments: list[dict], budget: float) -> list[dict]:
    """قصّ الخطة إلى المدة المستهدفة بالاحتفاظ بالبداية — الهوك أهم ما في الفيديو."""
    if budget <= 0:
        return segments
    out, spent = [], 0.0
    for seg in segments:
        length = seg["end"] - seg["start"]
        if spent + length <= budget:
            out.append(seg)
            spent += length
        else:
            remaining = budget - spent
            if remaining >= 0.6:  # مقطع أقصر من ذلك يبدو كخطأ لا كقطع
                out.append({"start": seg["start"], "end": round(seg["start"] + remaining, 2)})
            break
    return out


def build_plan(video: str, report: dict, segments: list[dict],
               aspect: str, speed: float) -> dict:
    kept = round(sum(s["end"] - s["start"] for s in segments), 2)
    for seg in segments:
        seg["speed"] = speed

    return {
        "input": video,
        "aspect": aspect,
        "crop_mode": "blur",
        "fps": 30,
        "source_duration": report["duration"],
        "estimated_duration": round(kept / speed, 2) if speed else kept,
        "segments": segments,
        "color": {"contrast": 1.08, "saturation": 1.10, "brightness": 0.02},
        "captions": [],
        "icons": [],
        "music": None,
        "audio": {"normalize": True, "target_lufs": -14},
        "_notes": report.get("recommendations", []),
    }


def main() -> None:
    ap = argparse.ArgumentParser(description="قصّ الصمت وبناء خطة مونتاج ابتدائية")
    ap.add_argument("input")
    ap.add_argument("--out", default="out/plan.json")
    ap.add_argument("--aspect", default="9:16", choices=["9:16", "16:9", "1:1", "4:5", "keep"])
    ap.add_argument("--min-silence", type=float, default=0.35,
                    help="أقصر صمت يُحذف (ثانية)")
    ap.add_argument("--min-segment", type=float, default=0.4,
                    help="أقصر مقطع يُحتفظ به (ثانية)")
    ap.add_argument("--max-duration", type=float, default=0,
                    help="سقف المدة النهائية بالثواني (0 = بلا سقف)")
    ap.add_argument("--speed", type=float, default=1.0,
                    help="سرعة التشغيل، 1.05–1.15 ترفع الإيقاع بلا أن يُلاحظ")
    ap.add_argument("--keep-silence", action="store_true",
                    help="لا تحذف الصمت — مقطع واحد كامل")
    args = ap.parse_args()

    require_tools()
    if not Path(args.input).exists():
        die(f"الملف غير موجود: {args.input}")

    print("… فحص الفيديو")
    report = analyse(args.input)
    duration = report["duration"]

    if args.keep_silence or not report.get("has_audio"):
        segments = [{"start": 0.0, "end": duration}]
    else:
        segments = keep_segments(report.get("silence", []), duration,
                                 args.min_silence, args.min_segment)
    if not segments:
        segments = [{"start": 0.0, "end": duration}]

    before = round(sum(s["end"] - s["start"] for s in segments), 2)
    if args.max_duration:
        segments = trim_to_budget(segments, args.max_duration * args.speed)

    plan = build_plan(args.input, report, segments,
                      "keep" if args.aspect == "keep" else args.aspect, args.speed)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\n✅ خطة المونتاج: {out}")
    print(f"   المصدر  : {duration}s")
    print(f"   بعد حذف الصمت: {before}s  ({len(segments)} مقطع)")
    print(f"   المدة المتوقّعة: {plan['estimated_duration']}s  @ سرعة {args.speed}×")
    print("\nالخطوة التالية: أضف captions و icons و music إلى الخطة، ثم:")
    print(f"   python3 render.py {out} --out out/final.mp4")


if __name__ == "__main__":
    main()
