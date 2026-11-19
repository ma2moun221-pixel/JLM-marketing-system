# JLM ATF Stop Leak & Conditioner — Instagram Story (20 s, 1080×1920)

A new look for JLM: a **technical blueprint**. A dark drawing board with a grid that slowly drifts,
corner brackets and figure numbers (FIG. 01–06), everything drawn in thin silver lines; yellow is the
fix, red only for the problem.

| time | scene |
|---|---|
| 0 – 3.2 s | the P R N D selector slips between D and N, an oil drop falls: «ناقل الحركة الأوتوماتيكي يسرّب زيت؟» |
| 3.2 – 6.8 s | gearbox schematic draws itself (torque converter + planetary set turning); red seals, drops, callouts: تسرّب الزيت · انزلاق الغيارات · استهلاك الزيت |
| 6.8 – 10.4 s | the product as a line sketch; a yellow scan line turns it into the real can: «مانع تسرّب زيت الجير» / ATF Stop Leak & Conditioner |
| 10.4 – 14.6 s | how to use: ١ رجّ العلبة جيداً · ٢ أضفه إلى سائل ناقل الحركة الأوتوماتيكي · ٣ قُد السيارة 15 دقيقة (timer counts to 15) |
| 14.6 – 17.2 s | the schematic again: seals turn yellow, drops stop — تبديل سلس وهادئ بين الغيارات · ويطيل عمر ناقل الحركة · *غير مناسب لنواقل الحركة CVT و DSG |
| 17.2 – 20 s | CTA: logo, can, «اطلبه الآن من خلال» jlmstore.com, «مع توفّر خدمة التوصيل» |

Copy comes only from the client's product text and the label. Music: a calm 100 BPM technical pulse
(A minor, lifting to major on the result) + the soft JLM SFX.

```bash
python3 scripts/prepare.py      # can cut-out, its line sketch, the logo without its background box
python3 scripts/audio.py        # assets/bgm/story_mix.wav
npx --yes hyperframes@0.8.161 check
npx --yes hyperframes@0.8.161 render -o renders/atf_video.mp4 -q delivery --quiet
ffmpeg -i renders/atf_video.mp4 -i assets/bgm/story_mix.wav -filter_complex "[1:a]volume=-3dB,alimiter=limit=0.63:attack=2:release=60:level=false,loudnorm=I=-14:TP=-2.5:LRA=11,aresample=48000,alimiter=limit=0.79:attack=1:release=50:level=false,volume=-1.5dB[a]" \
  -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -t 20 -movflags +faststart renders/jlm_atf_stop_leak_story.mp4
```

## v2 — cinematic film on real footage (`renders/jlm_atf_stop_leak_film.mp4`)

The client asked for a strong film on real footage, no schematic over it, where the viewer lives the
product stage by stage. `scripts/film.py` cuts five Pexels clips the client picked (kept in
`assets/footage/`, not committed) with the product photo:

| time | stage |
|---|---|
| 0 – 2.5 s | gear shift that jolts twice (camera shake, red flashes): «ناقل الحركة ينزلق؟ أو يسرّب الزيت؟» |
| 2.5 – 5.5 s | inside the gearbox (CGI gears), cold grade: تسرّب · انزلاق · استهلاك للزيت |
| 5.5 – 8.5 s | the can, hero-lit with a light sweep: مانع تسرّب زيت الجير / ATF Stop Leak & Conditioner |
| 8.5 – 12.5 s | ١ رجّ العلبة جيداً (the can is shaken by hand: up-and-down arc, tilt, motion blur) → ٢ أضفه إلى سائل ناقل الحركة (pour under the bonnet, funnel in slow motion) |
| 12.5 – 15 s | ٣ قُد السيارة 15 دقيقة — time-lapse drive with a 0 → 15 timer |
| 15 – 17.5 s | the same shift, now smooth and warm: تبديل سلس وهادئ بين الغيارات · ويطيل عمر ناقل الحركة · *CVT / DSG note |
| 17.5 – 20 s | CTA: logo, can, اطلبه الآن من خلال jlmstore.com, مع توفّر خدمة التوصيل |

Car-brand badges in the stock clips (FIAT on the steering wheel, STI on the console) are cropped out of
frame. Cuts sit on a 120 BPM grid with zoom-blur whips and a warm light flash; cold grade for the problem,
warm JLM gold after the product. Music (`scripts/music_film.py`) uses the flying-car synth voices:
tension → dark pulse → impact on the product → full beat through the steps → major lift → CTA.

```bash
python3 scripts/music_film.py
python3 scripts/film.py --out renders/jlm_atf_stop_leak_film.mp4
```
