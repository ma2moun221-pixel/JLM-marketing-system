# JLM Petrol Extreme Clean — "Your car flies" 25.5 s Story

A 1080×1920 HyperFrames motion story with a GSAP timeline in `compositions/story.html`. A real sedan (the client's side render, cut into body + wheel layers by `scripts/prepare_car.py`; the hub-cap logos are covered with JLM-yellow caps) gets Petrol Extreme Clean, lights up in JLM yellow, folds its wheels into hover pads and takes off. Realism layers: wet-road reflection and contact shadows, suspension pitch (squat when pulling away, nose-dip and spring settle when braking), idle shiver, exhaust coughs, rotational motion blur on the wheels at speed, camera push-ins and a lift-off shake, dust and thruster light on the road. Every caption holds about 2–4 s after it lands. All text stays inside the Story safe area.

| Time | Scene |
|---|---|
| 0–4.8 s | **Hook.** A light sweep reveals the car; weak, flickering lights, two coughs of smoke. «سيارتك فقدت قوتها؟» and a red engine-power meter. The car pulls away. |
| 4.8–8.4 s | **Product.** The can rises into a yellow ring smaller than the can, a sheen crosses the label: «PETROL EXTREME CLEAN / منظّف شامل لنظام الوقود / من JLM». |
| 8.4–12.4 s | **The pour.** The car brakes back into frame, the can tips over the real fuel flap and a yellow drop falls in. Energy runs around the body, the lights come on, the meter fills gold: «يعيد أعلى أداء للمحرّك». |
| 12.4–17.2 s | **Take-off.** «مع JLM / سيارتك تطير». The wheels fold flat, thrusters light the road, the car lifts off with a camera shake; the city drops away, trails and speed lines stream past. |
| 17.2–21.3 s | **Benefits.** The car cruises above three cards with self-drawing JLM line icons: full fuel-system cleaning, removes stubborn deposits, restores engine power and efficiency. |
| 21.3–25.5 s | **CTA.** The car blasts out of frame. Logo, can in the ring, «اطلبه الآن من خلال», the jlmstore.com pill and «مع توفّر خدمة التوصيل». |

The copy comes from the can's own label (Extreme fuel system cleaning · Restores peak performance · Removes stubborn deposits · Recovers engine power and efficiency). The product cut-out is `assets/extreme-can.png` (from `jlm-fuel-packs-30s`).

## Build

```
python3 scripts/prepare_car.py     # once: assets/src/car-side.jpg → assets/car/ (rembg isnet-general-use, opencv)
npx hyperframes@0.8.161 check
npx hyperframes@0.8.161 render . -o renders/car_video.mp4 -q delivery
python3 scripts/audio.py          # own synthwave track (scripts/music.py, needs scipy) + soft SFX → assets/bgm/story_mix.wav
ffmpeg -i renders/car_video.mp4 -i assets/bgm/story_mix.wav -filter_complex \
  "[1:a]volume=-3dB,alimiter=limit=0.63:attack=2:release=60:level=false,loudnorm=I=-14:TP=-2.5:LRA=11,aresample=48000,alimiter=limit=0.79:level=false,volume=-1.5dB[a]" \
  -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -t 25.5 renders/jlm_flying_car.mp4
```
