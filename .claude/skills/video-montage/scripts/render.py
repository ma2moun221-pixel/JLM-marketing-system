#!/usr/bin/env python3
"""تنفيذ خطة المونتاج في تمريرة ترميز واحدة (single-pass) بأعلى جودة.

    python3 render.py out/plan.json --out out/final.mp4
    python3 render.py out/plan.json --out out/final.mp4 --preview   # نصف الأبعاد، سريع للمراجعة
    python3 render.py out/plan.json --print-cmd                     # اطبع أمر ffmpeg فقط

مبدأ ثابت: كل الفلاتر في سلسلة واحدة. كل تمريرة ترميز إضافية تفقد جودة.
صيغة الخطة الكاملة في references/edit-plan.md
"""
from __future__ import annotations

import argparse
import shlex
import subprocess
from pathlib import Path

import captions as capmod
from mvcommon import (FFMPEG, die, duration_of, ffprobe_json, filter_escape,
                      load_plan, parse_fps, pick_arabic_font, require_tools,
                      stream)

ASPECT_SIZES = {
    "9:16": (1080, 1920),
    "16:9": (1920, 1080),
    "1:1":  (1080, 1080),
    "4:5":  (1080, 1350),
}

POSITIONS = {
    "top-left":     ("W*0.16", "H*0.16"),
    "top-center":   ("W*0.50", "H*0.14"),
    "top-right":    ("W*0.84", "H*0.16"),
    "center":       ("W*0.50", "H*0.50"),
    "left":         ("W*0.18", "H*0.50"),
    "right":        ("W*0.82", "H*0.50"),
    "bottom-left":  ("W*0.16", "H*0.80"),
    "bottom-center":("W*0.50", "H*0.82"),
    "bottom-right": ("W*0.84", "H*0.80"),
}

POP_SEC = 0.16      # زمن التكبير
SETTLE_SEC = 0.10   # زمن الاستقرار بعد التجاوز


def even(n: float) -> int:
    """أبعاد فردية ترفضها ترميزات yuv420p."""
    return max(2, int(round(n / 2)) * 2)


def atempo_chain(speed: float) -> str:
    """atempo يقبل 0.5–2.0 فقط لكل نسخة — تُسَلسَل للسرعات خارج المدى."""
    if abs(speed - 1.0) < 1e-3:
        return ""
    parts, remaining = [], speed
    while remaining > 2.0:
        parts.append("atempo=2.0")
        remaining /= 2.0
    while remaining < 0.5:
        parts.append("atempo=0.5")
        remaining /= 0.5
    parts.append(f"atempo={remaining:.6f}")
    return ",".join(parts)


def target_size(plan: dict, src_w: int, src_h: int) -> tuple[int, int]:
    aspect = plan.get("aspect", "9:16")
    if aspect == "keep" or aspect not in ASPECT_SIZES:
        return even(src_w), even(src_h)
    w, h = ASPECT_SIZES[aspect]
    # لا نكبّر أكثر من 1.35× فوق دقّة المصدر: التكبير يضيف حجمًا بلا تفاصيل.
    if src_w and src_h and min(w / src_w, h / src_h) > 1.35:
        shrink = 1.35 / min(w / src_w, h / src_h)
        return even(w * shrink), even(h * shrink)
    return w, h


def build_segments(plan: dict, has_audio: bool, src_dur: float) -> tuple[list[str], str, str, int]:
    """قصّ المقاطع وتسريعها ثم دمجها. يعيد (فلاتر، منفذ الفيديو، منفذ الصوت، العدد)."""
    segments = plan.get("segments") or [{"start": 0, "end": src_dur}]
    parts, v_labels, a_labels = [], [], []

    for i, seg in enumerate(segments):
        start = max(0.0, float(seg.get("start", 0)))
        end = float(seg.get("end", src_dur))
        if end <= start:
            continue
        speed = float(seg.get("speed", 1.0)) or 1.0
        zoom = float(seg.get("zoom", 1.0))

        vf = [f"trim=start={start:.3f}:end={end:.3f}", "setpts=PTS-STARTPTS"]
        if abs(speed - 1.0) > 1e-3:
            vf.append(f"setpts=PTS/{speed:.6f}")
        if zoom > 1.001:
            # punch-in ثابت: يخفي القطع المفاجئ ويعطي تنوّعًا بين اللقطات
            vf.append(f"scale=iw*{zoom:.4f}:ih*{zoom:.4f}")
            vf.append("crop=w=iw/%.4f:h=ih/%.4f" % (zoom, zoom))
        parts.append(f"[0:v]{','.join(vf)}[v{i}]")
        v_labels.append(f"[v{i}]")

        if has_audio:
            af = [f"atrim=start={start:.3f}:end={end:.3f}", "asetpts=PTS-STARTPTS"]
            tempo = atempo_chain(speed)
            if tempo:
                af.append(tempo)
            parts.append(f"[0:a]{','.join(af)}[a{i}]")
            a_labels.append(f"[a{i}]")

    if not v_labels:
        die("لا يوجد أي مقطع صالح في الخطة (تحقّق من start/end).")

    n = len(v_labels)
    if n == 1:
        return parts, v_labels[0], (a_labels[0] if a_labels else ""), n

    if has_audio:
        parts.append("".join(v + a for v, a in zip(v_labels, a_labels))
                     + f"concat=n={n}:v=1:a=1[vcat][acat]")
        return parts, "[vcat]", "[acat]", n

    parts.append("".join(v_labels) + f"concat=n={n}:v=1:a=0[vcat]")
    return parts, "[vcat]", "", n


def build_geometry(plan: dict, vin: str, w: int, h: int,
                   src_w: int = 0, src_h: int = 0) -> tuple[list[str], str]:
    """تحويل الأبعاد إلى المقاس الهدف: خلفية ضبابية / قصّ / أشرطة سوداء."""
    # المصدر بالمقاس المطلوب أصلًا: أي تحجيم هنا خسارة جودة بلا مقابل.
    if (src_w, src_h) == (w, h):
        return [], vin

    mode = plan.get("crop_mode", "blur")
    if mode == "crop":
        chain = (f"scale={w}:{h}:force_original_aspect_ratio=increase:flags=lanczos,"
                 f"crop={w}:{h}")
        return [f"{vin}{chain}[vgeo]"], "[vgeo]"
    if mode == "pad":
        chain = (f"scale={w}:{h}:force_original_aspect_ratio=decrease:flags=lanczos,"
                 f"pad={w}:{h}:(ow-iw)/2:(oh-ih)/2:black")
        return [f"{vin}{chain}[vgeo]"], "[vgeo]"

    # blur (الافتراضي): يملأ الإطار دون قصّ الوجوه ولا أشرطة سوداء ميتة.
    # التمويه على نسخة مصغّرة ثم التكبير — نفس المظهر بكلفة أقل بعشرات المرات
    # من gblur بسيغما كبيرة على الإطار الكامل.
    small_w = even(w / 8)
    return ([
        f"{vin}split=2[bgsrc][fgsrc]",
        f"[bgsrc]scale={small_w}:-2,gblur=sigma=6,"
        f"scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},"
        f"eq=brightness=-0.10:saturation=0.85[bg]",
        f"[fgsrc]scale={w}:{h}:force_original_aspect_ratio=decrease:flags=lanczos[fg]",
        "[bg][fg]overlay=(W-w)/2:(H-h)/2[vgeo]",
    ], "[vgeo]")


def build_color(plan: dict, vin: str) -> tuple[list[str], str]:
    color = plan.get("color") or {}
    if not color:
        return [], vin
    eq = (f"eq=contrast={color.get('contrast', 1.0)}"
          f":saturation={color.get('saturation', 1.0)}"
          f":brightness={color.get('brightness', 0.0)}"
          f":gamma={color.get('gamma', 1.0)}")
    chain = [eq]
    if color.get("sharpen"):
        chain.append("unsharp=5:5:0.6:5:5:0.0")
    return [f"{vin}{','.join(chain)}[vcol]"], "[vcol]"


def build_outro(plan: dict, vin: str, timeline: float) -> tuple[list[str], str]:
    """تمويه تدريجي في نهاية الفيديو — خلفية هادئة لبطاقة الختام.

    `gblur` لا تقبل سيغما متغيّرة بالزمن، فنمزج النسخة الحادّة بالمموّهة عبر `blend`
    بتعبير يعتمد على الطابع الزمني `T` — فيبدأ التمويه من الصفر ويكتمل تدريجيًا.
    و`enable` على `gblur` يجعلها تمرّ دون عمل قبل بداية الختام، فلا تُموَّه كل إطارات
    الفيديو بلا داعٍ.
    """
    outro = plan.get("outro") or {}
    if not outro:
        return [], vin

    start = float(outro.get("start", max(0.0, timeline - 2.0)))
    ramp = max(0.1, float(outro.get("ramp", 0.8)))
    sigma = float(outro.get("blur", 24))
    darken = float(outro.get("darken", 0.0))

    progress = f"clip((T-{start:.3f})/{ramp:.3f},0,1)"
    blur_chain = f"gblur=sigma={sigma:g}:enable='gte(t,{max(0.0, start - 0.1):.3f})'"
    if darken > 0:
        blur_chain += f",eq=brightness=-{darken:g}"

    return ([
        f"{vin}split=2[osharp][oblurbase]",
        f"[oblurbase]{blur_chain}[oblur]",
        f"[osharp][oblur]blend=all_expr='A*(1-{progress})+B*{progress}'[voutro]",
    ], "[voutro]")


def build_icon_filters(icons: list[dict], vin: str, icon_dir: Path,
                       w: int, h: int, fps: float,
                       timeline: float) -> tuple[list[str], list[str], str]:
    """يعيد (مدخلات ffmpeg، فلاتر، منفذ الفيديو الأخير).

    كل أيقونة صورة ثابتة، لكن حركة الظهور تحتاج زمنًا يتقدّم. نكرّرها عند **المدخل**
    بـ `-loop 1 -framerate F -t D` فتصير مقطعًا محدود الطول بتوقيتات مطابقة للفيديو.
    التكرار داخل سلسلة الفلاتر (`loop=-1`) يولّد إطارات بلا نهاية ويُبطئ الرندر بشدّة.
    """
    inputs: list[str] = []
    filters: list[str] = []
    current = vin
    idx = 0

    for icon in icons:
        path = icon.get("image")
        if not path and icon.get("emoji"):
            candidate = icon_dir / f"{'_'.join(f'u{ord(c):x}' for c in icon['emoji'] if ord(c) > 0x20)}.png"
            if candidate.exists():
                path = str(candidate)
        if not path or not Path(path).exists():
            print(f"  ⚠ تخطّي أيقونة بلا صورة: {icon.get('emoji') or icon.get('image')}"
                  f" — شغّل icons.py أولًا")
            continue

        start = float(icon.get("start", 0))
        end = float(icon.get("end", start + 1.5))
        if end <= start:
            end = start + 1.2
        size = float(icon.get("size", 0.16)) * w  # نسبة من عرض الإطار
        px, py = POSITIONS.get(icon.get("pos", "top-right"), POSITIONS["top-right"])

        stream_idx = 1 + sum(1 for x in inputs if x == "-i")
        inputs += ["-loop", "1", "-framerate", f"{fps:.4f}",
                   "-t", f"{timeline:.3f}", "-i", path]
        label_in = f"[{stream_idx}:v]"
        label_out = f"[ic{idx}]"

        if icon.get("anim", "pop") == "pop":
            # صغير ← أكبر من الهدف ← يستقرّ. الظهور المفاجئ يبدو رخيصًا.
            grow = f"{size:.1f}*(0.55+0.65*(t-{start:.3f})/{POP_SEC})"
            settle = f"{size:.1f}*(1.20-0.20*(t-{start + POP_SEC:.3f})/{SETTLE_SEC})"
            expr = (f"if(lt(t,{start:.3f}),2,"
                    f"if(lt(t,{start + POP_SEC:.3f}),{grow},"
                    f"if(lt(t,{start + POP_SEC + SETTLE_SEC:.3f}),{settle},{size:.1f})))")
        else:
            expr = f"{size:.1f}"

        filters.append(
            f"{label_in}format=rgba,"
            f"scale=w='max(2,{expr})':h='max(2,{expr})':eval=frame{label_out}"
        )
        nxt = f"[vic{idx}]"
        filters.append(
            f"{current}{label_out}overlay=x='{px}-overlay_w/2':y='{py}-overlay_h/2'"
            f":enable='between(t,{start:.3f},{end:.3f})':shortest=0{nxt}"
        )
        current = nxt
        idx += 1

    return inputs, filters, current


def build_audio(plan: dict, ain: str, music_index: int | None) -> tuple[list[str], str]:
    """تطبيع الكلام + خلط الموسيقى مع ducking تلقائي."""
    filters: list[str] = []
    audio_cfg = plan.get("audio") or {}
    music = plan.get("music") or {}
    target = audio_cfg.get("target_lufs", -14)

    speech = ain
    if speech:
        chain = ["highpass=f=80"]  # إزالة هدير الغرفة والميكروفون
        if audio_cfg.get("normalize", True):
            chain.append(f"loudnorm=I={target}:TP=-1.5:LRA=11")
        filters.append(f"{speech}{','.join(chain)}[sp]")
        speech = "[sp]"

    fade = plan.get("audio_fade_out")
    if fade:
        filters.append(f"{speech}afade=t=out:st={float(fade['start']):.3f}"
                       f":d={float(fade.get('duration', 1.0)):.3f}[spf]")
        speech = "[spf]"

    if music_index is None:
        return filters, speech

    gain = float(music.get("gain_db", -18))
    mlabel = f"[{music_index}:a]"
    filters.append(f"{mlabel}volume={gain}dB,aloop=loop=-1:size=2e9[mus]")

    if not speech:
        filters.append(f"[mus]loudnorm=I={target}:TP=-1.5:LRA=11[aout]")
        return filters, "[aout]"

    if music.get("ducking", True):
        # نسخة من الكلام تعمل كمفتاح جانبي يخفض الموسيقى وقت النطق
        filters.append(f"{speech}asplit=2[sp1][spkey]")
        filters.append("[mus][spkey]sidechaincompress=threshold=0.02:ratio=12:"
                       "attack=15:release=350:makeup=1[duck]")
        filters.append("[sp1][duck]amix=inputs=2:duration=first:dropout_transition=0"
                       ":normalize=0,alimiter=limit=0.95[aout]")
    else:
        filters.append(f"{speech}[mus]amix=inputs=2:duration=first:dropout_transition=0"
                       ":normalize=0,alimiter=limit=0.95[aout]")
    return filters, "[aout]"


def encode_args(plan: dict, preview: bool, fps: float, has_audio: bool) -> list[str]:
    quality = plan.get("quality") or {}
    if preview:
        args = ["-c:v", "libx264", "-preset", "veryfast", "-crf", "28"]
    else:
        args = ["-c:v", "libx264",
                "-preset", quality.get("preset", "medium"),
                "-crf", str(quality.get("crf", 18)),
                "-profile:v", "high", "-level", "4.2",
                "-x264-params", "keyint=%d:min-keyint=%d:scenecut=40" % (round(fps) * 2, round(fps))]
    args += ["-pix_fmt", "yuv420p", "-r", f"{fps:.4f}",
             "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
             "-movflags", "+faststart"]
    if has_audio:
        args += ["-c:a", "aac", "-b:a", quality.get("audio_bitrate", "192k"), "-ar", "48000"]
    else:
        args += ["-an"]
    return args


def main() -> None:
    ap = argparse.ArgumentParser(description="تنفيذ خطة المونتاج")
    ap.add_argument("plan")
    ap.add_argument("--out", default="out/final.mp4")
    ap.add_argument("--preview", action="store_true", help="تصدير سريع منخفض الجودة للمراجعة")
    ap.add_argument("--print-cmd", action="store_true", help="اطبع أمر ffmpeg دون تنفيذه")
    ap.add_argument("--icon-dir", default=None, help="مجلد أيقونات PNG (افتراضيًا بجانب المخرج)")
    args = ap.parse_args()

    require_tools()
    plan = load_plan(args.plan)
    src = plan.get("input")
    if not src or not Path(src).exists():
        die(f"ملف الإدخال غير موجود: {src}")

    info = ffprobe_json(src)
    v = stream(info, "video") or {}
    has_audio = stream(info, "audio") is not None
    src_w, src_h = int(v.get("width") or 1080), int(v.get("height") or 1920)
    src_fps = parse_fps(v.get("avg_frame_rate") or v.get("r_frame_rate"))
    src_dur = duration_of(info)

    fps = float(plan.get("fps") or 0) or min(src_fps, 30.0)
    w, h = target_size(plan, src_w, src_h)
    if args.preview:
        w, h = even(w * 0.5), even(h * 0.5)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    work = out_path.parent
    icon_dir = Path(args.icon_dir) if args.icon_dir else work / "icons"

    # ---- بناء سلسلة الفلاتر ----
    filters, vcur, acur, n_seg = build_segments(plan, has_audio, src_dur)

    # طول المونتاج بعد القصّ والتسريع — يحدّد طول مقاطع الأيقونات.
    # نبقيه أقصر قليلًا من الفيديو: مدخل أطول من الفيديو يمدّ المخرج بإطارات فارغة،
    # وآخر إطار للأيقونة يتكرّر تلقائيًا (eof_action=repeat) فلا يظهر نقص.
    timeline = max(1.0, sum(
        (float(s.get("end", src_dur)) - float(s.get("start", 0)))
        / (float(s.get("speed", 1.0)) or 1.0)
        for s in (plan.get("segments") or [{"start": 0, "end": src_dur}])
    ) - 0.05)

    geo, vcur = build_geometry(plan, vcur, w, h, even(src_w), even(src_h))
    filters += geo
    col, vcur = build_color(plan, vcur)
    filters += col

    # الختام قبل الكابشن والأيقونات: تُموَّه الصورة وحدها ويبقى النص حادًّا فوقها
    outro_filters, vcur = build_outro(plan, vcur, timeline)
    filters += outro_filters

    # الكابشن بعد كل عمليات الهندسة، وإلا شُوّه النص مع التحجيم.
    caption_list = plan.get("captions") or []
    ass_path = None
    if caption_list:
        ass_path = work / "captions.ass"
        font = plan.get("font") or pick_arabic_font()
        ass_path.write_text(
            capmod.build_header(w, h, font) + "\n"
            + "\n".join(capmod.build_events(caption_list, capmod.layout_scale(w, h)))
            + "\n",
            encoding="utf-8")
        filters.append(f"{vcur}ass='{filter_escape(str(ass_path))}'[vsub]")
        vcur = "[vsub]"

    extra_inputs: list[str] = []
    icon_inputs, icon_filters, vcur = build_icon_filters(
        plan.get("icons") or [], vcur, icon_dir, w, h, fps, timeline)
    extra_inputs += icon_inputs
    filters += icon_filters

    music_index = None
    music_cfg = plan.get("music") or {}
    music_path = music_cfg.get("path")
    if music_path:
        if Path(music_path).exists():
            music_index = 1 + sum(1 for x in extra_inputs if x == "-i")
            extra_inputs += ["-i", music_path]
        else:
            print(f"  ⚠ ملف الموسيقى غير موجود، سيُتجاهل: {music_path}")

    audio_filters, aout = build_audio(plan, acur, music_index)
    filters += audio_filters

    filters.append(f"{vcur}format=yuv420p[vout]")

    cmd = [FFMPEG, "-y", "-hide_banner", "-i", src] + extra_inputs + [
        "-filter_complex", ";".join(filters),
        "-map", "[vout]",
    ]
    out_has_audio = bool(aout)
    if out_has_audio:
        cmd += ["-map", aout]
    cmd += encode_args(plan, args.preview, fps, out_has_audio)
    if plan.get("target_duration") and not plan.get("segments"):
        cmd += ["-t", str(plan["target_duration"])]
    cmd += [str(out_path)]

    if args.print_cmd:
        print(" ".join(shlex.quote(c) for c in cmd))
        return

    print(f"… رندر {n_seg} مقطع → {w}×{h} @ {fps:.2f}fps"
          f"{' [معاينة]' if args.preview else ''}")
    proc = subprocess.run(cmd, stderr=subprocess.PIPE, text=True)
    if proc.returncode != 0:
        tail = "\n".join((proc.stderr or "").strip().splitlines()[-25:])
        die(f"فشل الرندر:\n{tail}\n\nلتشخيص المشكلة: أعد التشغيل بـ --print-cmd")

    result = ffprobe_json(str(out_path))
    dur = duration_of(result)
    size_mb = out_path.stat().st_size / 1_048_576
    print(f"\n✅ {out_path}")
    print(f"   المدة: {dur:.2f}s | الحجم: {size_mb:.1f} MB | {w}×{h}")
    if ass_path:
        print(f"   الكابشن: {ass_path}")
    print("\nتحقّق من الناتج قبل التسليم:")
    print(f"   python3 probe.py {out_path}")


if __name__ == "__main__":
    main()
