"""Jump-cut clean-up of the client's GDI Injector Cleaner clip (EDIT_STYLES.md §2, always first).

    python3 scripts/cut.py src/raw.mp4 build/cut.mov

Keeps only the spoken parts (pauses > 0.25 s trimmed to ≈ 0.1 s, the silent shot ends dropped)
and ends on the spoken CTA; the clip's own white CTA card (24.77 s →) is replaced in vox.py.
Every cut gets a 15 ms audio fade so nothing clicks. Prints the output time of each segment.
"""
import subprocess
import sys

# (in, out) in source seconds — speech from silencedetect (−30 dB) with 0.06 s before / 0.08 s after
SEGMENTS = [
    (0.78, 4.23),    # لماذا يلزم نستخدم مضاف البخاخات من JLM في المحركات الجديدة
    (5.20, 8.52),    # بسبب مكان وجود البخاخ في المحركات الجديدة فوق غرفة الاحتراق
    (9.00, 11.31),   # هذا الشي بيؤدي إلى تراكمات وترسّبات
    (11.97, 13.59),  # تظهر على البخاخ مع الوقت
    (13.97, 16.76),  # وبالتالي استخدام منظف JLM بشكل دوري
    (17.01, 18.83),  # بساعد على إزالة هذه التراكمات
    (19.11, 20.68),  # وبيعطيك كفاءة أعلى للمحرك
    (20.91, 22.44),  # وبالتالي استهلاك أقل للوقود
    (23.04, 28.00),  # (spoken CTA, under the new end card)
]
FADE = 0.015


def main():
    src, out = sys.argv[1], sys.argv[2]
    parts, labels = [], []
    for i, (a, b) in enumerate(SEGMENTS):
        d = b - a
        parts.append(f"[0:v]trim={a}:{b},setpts=PTS-STARTPTS[v{i}];"
                     f"[0:a]atrim={a}:{b},asetpts=PTS-STARTPTS,afade=t=in:d={FADE},afade=t=out:st={d - FADE}:d={FADE}[a{i}];")
        labels.append(f"[v{i}][a{i}]")
    graph = "".join(parts) + "".join(labels) + f"concat=n={len(SEGMENTS)}:v=1:a=1[v][a]"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", src, "-filter_complex", graph, "-map", "[v]", "-map", "[a]",
                    "-r", "30", "-c:v", "libx264", "-crf", "14", "-preset", "fast", "-c:a", "pcm_s16le", out], check=True)
    t = 0.0
    for a, b in SEGMENTS:
        print(f"{t:6.2f} – {t + b - a:6.2f}   (src {a:.2f}–{b:.2f})")
        t += b - a


if __name__ == "__main__":
    main()
