# JLM Air Refresh — Instagram Story (10 s, 1080×1920)

A light, realistic animation built on the client's real photo (`assets/photo.jpg`, a hand holding
JLM AIR REFRESH Apple Scent in the showroom). The photo is never altered: the film only moves the camera
and adds light on top.

| time | what happens |
|---|---|
| 0 – 1.1 s | focus pull (blur → sharp), slow push-in towards the can starts, light hand-held breathing |
| 0.7 – 3.9 s | «هواء منعش في سيارتك / برائحة التفاح» · light sheen over the can |
| 4.0 – 7.2 s | «يزيل الروائح المزعجة / من المكيّف ونظام التدفئة» + chips ينظّف · يعادل الروائح · سهل الاستعمال |
| 7.3 – 10 s | JLM Air Refresh + CTA: اطلبه الآن من خلال jlmstore.com · مع توفّر خدمة التوصيل · second sheen |

The showroom spot lights breathe and three of them glint, and soft apple-green motes drift up beside the can.
All copy comes from the can label (Eliminates unpleasant smell from air condition and heater unit ·
Cleans, neutralises and provides fresh air · Easy to use · Apple scent).

## Build
```bash
python3 scripts/prepare_photo.py   # assets/gen/can_mask.png (sheen mask) + lights.json
python3 scripts/audio.py           # assets/bgm/story_mix.wav (calm 90 BPM bed + soft SFX)
npx --yes hyperframes@0.8.161 check
npx --yes hyperframes@0.8.161 render -o renders/ar_video.mp4 -q delivery --quiet
ffmpeg -i renders/ar_video.mp4 -i assets/bgm/story_mix.wav -filter_complex "[1:a]volume=-3dB,alimiter=limit=0.63:attack=2:release=60:level=false,loudnorm=I=-14:TP=-2.5:LRA=11,aresample=48000,alimiter=limit=0.79:attack=1:release=50:level=false,volume=-1.5dB[a]" \
  -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -t 10 -movflags +faststart renders/jlm_air_refresh_story.mp4
```
