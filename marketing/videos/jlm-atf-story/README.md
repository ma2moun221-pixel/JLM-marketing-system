# JLM Automatic Transmission Flush — 15 s Story

A 1080×1920 HyperFrames motion story with a GSAP timeline in `compositions/story.html`. All text stays inside the Story safe area (about y 250–1580).

| Time | Scene |
|---|---|
| 0–2.6 s | **Hook.** A line gear gathers dark deposits: «بقايا ومخلفات / سائل ناقل الحركة القديم؟». The gear's rim irises into a yellow ring. |
| 2.55–5.75 s | **Product.** The can rises into the ring, a sheen crosses the label, and the name appears (Albert Sans) with «منظّف ناقل الحركة الأوتوماتيكي من JLM». A yellow gear-pattern wipe follows. |
| 5.75–9.0 s | **Cleaning.** «يضمن إزالة جميع بقايا ومخلفات سائل ناقل الحركة القديم». A gold wave dissolves the deposits and the gear turns gold. Then «قبل استبداله بسائل جديد»: the old fluid drains from a gauge and gold fills it. |
| 9.0–12.0 s | **Results.** «نتيجة لذلك» and three cards with self-drawing JLM line icons: cooler running, clutches and gears protected, maximum wear protection. |
| 11.95–15 s | **CTA.** Logo, can in the ring, «اطلبه الآن من خلال», the jlmstore.com pill and «مع توفّر خدمة التوصيل». |

The on-screen copy comes from the client's caption. The product image is the client's photo, upscaled 4× with EDSR and cut out (`assets/atf-can.png`).

## Build

```
npx hyperframes@0.8.161 check
npx hyperframes@0.8.161 render . -o renders/atf_video.mp4 -q delivery
python3 scripts/audio.py          # music (house track on these cuts) + soft SFX → assets/bgm/story_mix.wav
ffmpeg -i renders/atf_video.mp4 -i assets/bgm/story_mix.wav -filter_complex \
  "[1:a]volume=-3dB,alimiter=limit=0.63:attack=2:release=60:level=false,loudnorm=I=-14:TP=-2.5:LRA=11,aresample=48000,alimiter=limit=0.79:level=false[a]" \
  -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -shortest renders/jlm_atf_story.mp4
```
