# 361° JOKER 2 GT "ARTEMIS" — 15s motion spot (Arabic)

Vertical 1080×1920, 30 fps, 15 s, Arabic copy (product names kept in English), deep-space backdrop,
original synthesized soundtrack (120 BPM; every cut lands on a beat and is hidden by a whip-spin).

Final render: `output/Joker2GT_Artemis_AR_15s.mp4`

## Timeline
| Time | Scene | Content |
|---|---|---|
| 0.0–2.0s | Countdown | Hyperspace star tunnel, "المهمة: أرتميس", 3·2·1 inside counter-rotating HUD dials, light streak |
| 2.0–5.0s | Reveal | Shoe spirals in, orbit rings around it (front/back depth), "JOKER 2 GT", "إصدار أرتميس", 540° turntable (side → heel → other side → side) |
| 5.0–8.0s | Details 01–03 | Macro camera with depth of field + reticle: قفص منحوت · توقيع النجم · خطوط انسيابية |
| 8.0–11.0s | Details 04–05 | Turn to the heel (بصمة الجوكر), flip to the outsole (نقشة متعرّجة) |
| 11.0–12.5s | Athlete | Campaign photo with "الجوكر" layered behind the player |
| 12.5–15.0s | Finale | Light implodes → explosion + shockwaves, shoe orbits above the planet, logo, title, "متوفر الآن" |

## Assets
- Product images: background-removed cut-outs of the official 361° campaign photos (no AI-generated product imagery). The turntable is a 2D flip between the real photo angles.
- Logo: cropped from the official artwork, unaltered.
- Space backdrop: `space_assets.py` → `public/nebula.jpg`, `public/planet.png` (procedural).
- Fonts: Cairo (Arabic), Anton, Inter, Space Mono (Google Fonts, OFL), bundled in `public/fonts`.
- Soundtrack: `soundtrack_synth.py` (numpy/scipy) → `public/soundtrack.wav`.

## Run
```bash
npm i
npx remotion studio            # preview / edit
npx remotion render JokerArtemis output/Joker2GT_Artemis_AR_15s.mp4 --codec=h264 --crf=17
# offline/locked-down machines: add --browser-executable=/path/to/chrome-headless-shell
```
