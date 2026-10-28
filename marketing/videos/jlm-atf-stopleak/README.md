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
