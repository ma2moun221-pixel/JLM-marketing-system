# JLM oil change — Engine Oil Flush + 5W-30 (30 s cinematic film, 1080×1920)

One full service, lived step by step on real workshop footage (Pexels clips from the client, kept in
`assets/footage/`, not committed; the two pour shots come from `../jlm-atf-stopleak/assets/footage/`).

| time | stage |
|---|---|
| 0 – 3 s | an old engine, black & white: «محرّك قديم؟ أوساخ وترسّبات زيت المحرك» |
| 3 – 6 s | Engine Oil Flush, hero-lit: ينظّف المحرك من الأوساخ وترسّبات الزيت · ديزل • بنزين • هايبرد |
| 6 – 8.5 s | ١ اسكبه في زيت المحرك — قبل تغيير الزيت |
| 8.5 – 11 s | ٢ اترك المحرك دائراً 15 دقيقة (0 → 15 timer) |
| 11 – 14.5 s | ٣ أفرغ زيت المحرك — واستبدل فلتر الزيت (under the car) |
| 14.5 – 16.5 s | أداء أفضل للمحرك · واستهلاك أقل للوقود |
| 16.5 – 19.5 s | 5W-30, hero-lit: زيت محرك تخليقي بالكامل · A5/B5 • احتكاك منخفض |
| 19.5 – 22 s | ٤ ضع الزيت الجديد — حسب تعليمات المركبة (golden pour, slow motion) |
| 22 – 24.5 s | ٥ افحص المستوى بالديبستيك — وتجنّب الملء الزائد |
| 24.5 – 27 s | كفاءة أعلى في استهلاك الوقود · مع حماية عالية للمحرك |
| 27 – 30 s | CTA: both products, اطلبهما الآن من خلال jlmstore.com, مع توفّر خدمة التوصيل |

Copy comes only from the client's product text. Look and helpers are shared with the ATF film
(`../jlm-atf-stopleak/scripts/film.py`): cold → warm grade, grain, zoom-blur whips with a warm light flash
on a 120 BPM grid, kinetic type in the JLM fonts, step chips, the timer.

```bash
python3 scripts/prepare.py      # product cut-outs (the client's files carry a background)
python3 scripts/music.py        # assets/bgm/film_mix.wav
python3 scripts/film.py --out renders/jlm_oil_change_film.mp4
```
