# JLM Screen Rainguard — 25.5 s product film (9:16)

HyperFrames motion film with photo-like procedural layers (`scripts/make_assets.py`): a night road seen through a rainy windshield, a water-film glass with flat smeared drops (before), round refracting beads (after), and single bead sprites that slide off. The product image is the client's original cut-out (`assets/rainguard.png`). Copy is the client's product text.

| Time | Scene |
|---|---|
| 0–4.6 s | **Hook.** Night rain on the windshield, drops land, one wiper pass leaves the water smeared: «رؤية ضعيفة تحت المطر؟» |
| 4.6–8.4 s | **Product.** Bottle rises in a yellow ring (smaller than the bottle), pink label accent: «SCREEN RAINGUARD · معالج احترافي لزجاج السيارة الأمامي» + label chips (deep cleaning, enhanced protection, easy to mix). |
| 8.4–13.0 s | **How to use.** The washer-reservoir cap comes off, the whole 100 ml bottle pours into the full tank, the yellow plume swirls and mixes: «اسكب العبوة كاملة (100 مل) في خزان سائل غسيل الزجاج وهو ممتلئ» → «يمتزج فوراً مع سائل الغسيل ويعزّز قوة التنظيف». |
| 13.0–17.6 s | **How it works.** Two glass panels: plain vs treated (yellow coating forms). A drop spreads flat on plain glass and beads on the coating; tilt: the bead slides off. «ينظّف الزجاج ويمنحه طبقة طاردة للماء» / «قطرات المطر تنزلق بسهولة». |
| 17.6–21.3 s | **Result.** Washer spray, one wipe: the view sharpens, rain beads and slides away: «رؤية أوضح وأمان أكبر أثناء القيادة في مختلف الظروف الجوية» + «آمن على الزجاج والبلاستيك والمساحات». |
| 21.3–25.5 s | **CTA.** Logo, bottle in the ring, «اطلبه الآن من خلال jlmstore.com», «مع توفّر خدمة التوصيل». |

## Build

```
python3 scripts/make_assets.py    # assets/gen/*.png (road, rainy glass, beads)
npx hyperframes@0.8.161 check
npx hyperframes@0.8.161 render . -o renders/rg_video.mp4 -q delivery
python3 scripts/audio.py          # synthwave track (scripts/music.py, needs scipy) + rain bed + soft SFX
ffmpeg -i renders/rg_video.mp4 -i assets/bgm/story_mix.wav -filter_complex \
  "[1:a]volume=-3dB,alimiter=limit=0.63:attack=2:release=60:level=false,loudnorm=I=-14:TP=-2.5:LRA=11,aresample=48000,alimiter=limit=0.79:level=false,volume=-1.5dB[a]" \
  -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -t 25.5 renders/jlm_screen_rainguard.mp4
```
