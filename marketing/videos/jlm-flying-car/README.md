# JLM Petrol Extreme Clean — "Your car flies" 20 s Story

A 1080×1920 HyperFrames motion story with a GSAP timeline in `compositions/story.html`. A real sedan (the client's side photo, cut into body + wheel layers by `scripts/prepare_car.py`; the hub-cap logos are covered with JLM-yellow caps) gets Petrol Extreme Clean, lights up in JLM yellow, folds its wheels into hover pads and takes off. All text stays inside the Story safe area.

| Time | Scene |
|---|---|
| 0–3.6 s | **Hook.** A light sweep reveals the car in a dark city; weak, flickering lights. «سيارتك فقدت قوتها؟» and a red engine-power meter at about a third. The car drives off. |
| 3.6–6.4 s | **Product.** The can rises into a yellow ring that is smaller than the can, a sheen crosses the label: «PETROL EXTREME CLEAN / منظّف شامل لنظام الوقود / من JLM». |
| 6.4–9.2 s | **The pour.** The car rolls back in, the can tips over the fuel door and a yellow drop falls in. Energy runs around the body, the lights come on and the meter fills gold: «يعيد أعلى أداء للمحرّك». |
| 9.2–13.2 s | **Take-off.** «مع JLM / سيارتك تطير». The wheels fold flat, thrusters ignite, the car lifts off and the city drops away; speed lines and clouds stream past. |
| 13.2–16.8 s | **Benefits.** The car flies above three cards with self-drawing JLM line icons: full fuel-system cleaning, removes stubborn deposits, restores engine power and efficiency. |
| 16.8–20 s | **CTA.** The car blasts out of frame. Logo, can in the ring, «اطلبه الآن من خلال», the jlmstore.com pill and «مع توفّر خدمة التوصيل». |

The copy comes from the can's own label (Extreme fuel system cleaning · Restores peak performance · Removes stubborn deposits · Recovers engine power and efficiency). The product cut-out is `assets/extreme-can.png` (from `jlm-fuel-packs-30s`).

## Build

```
python3 scripts/prepare_car.py     # once: assets/src/car-side.webp → assets/car/ (rembg isnet-general-use, opencv)
npx hyperframes@0.8.161 check
npx hyperframes@0.8.161 render . -o renders/car_video.mp4 -q delivery
python3 scripts/audio.py          # own synthwave track (scripts/music.py, needs scipy) + soft SFX → assets/bgm/story_mix.wav
ffmpeg -i renders/car_video.mp4 -i assets/bgm/story_mix.wav -filter_complex \
  "[1:a]volume=-3dB,alimiter=limit=0.63:attack=2:release=60:level=false,loudnorm=I=-14:TP=-2.5:LRA=11,aresample=48000,alimiter=limit=0.79:level=false,volume=-1.5dB[a]" \
  -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -t 20 renders/jlm_flying_car.mp4
```
