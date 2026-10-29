# JLM stand — Instagram Story (19 s, 1080×1920)

Four phone clips from the client (the JLM stand at an outdoor event), cut smoothly with **captions and the
logo only — no animation**, as asked.

| time | clip | caption |
|---|---|---|
| 0 – 2 s | the shelves at sunset (Petrol Extreme Clean) | منتجات JLM |
| 2 – 8 s | a slow move round the full stand | تشكيلة متكاملة للعناية بسيارتك |
| 8 – 12.5 s | the JLM team shirt in the crowd | فريق JLM معكم |
| 12.5 – 19 s | staff advising a visitor | اسأل خبير JLM → اطلبها الآن من خلال jlmstore.com · مع توفر خدمة التوصيل |

Cuts sit on the beat (120 BPM) and dissolve over 0.3 s. Captions are static on the approved soft dark box
(Helvetica Neue LT Arabic Bold, Albert Sans for the URL) and only fade in and out; the JLM logo stays
top-right without the logo file's background box. Music: warm and upbeat (C – G – Am – F) on the
flying-car synth voices, with the clips' own crowd sound faint underneath. −14 LUFS.

```bash
python3 scripts/music.py
python3 scripts/story.py --out out/jlm_stand_story.mp4
```
`src/` holds the client's .mov files (not committed).
