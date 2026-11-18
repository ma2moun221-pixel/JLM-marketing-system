# 361° JOKER 2 GT "ARTEMIS" — 30s motion spot (Palestinian Arabic, 3D)

Vertical 1080×1920, 30 fps, 30 s. Palestinian Arabic copy (product names kept in English), deep-space backdrop,
2.5D shoe rendered in WebGL, original synthesized soundtrack (120 BPM; cuts hidden by whip-spins).

Final render: `output/Joker2GT_Artemis_AR_30s.mp4`

## Timeline
| Time | Scene | Content |
|---|---|---|
| 0–3s | Countdown | Hyperspace star tunnel, "مهمّة أرتميس", 3·2·1 in counter-rotating HUD dials, "جاهز؟ يلّا ننطلق" |
| 3–9s | Reveal | Shoe spirals in and sways in 3D, orbit rings (front/back depth), "JOKER 2 GT", "نسخة أرتميس", 3D turns side → heel → other side |
| 9–17.5s | Details 01–03 | 3D macro camera + reticle: وجه البوط «تفاصيل بتجنّن» · اللوغو «لوغو الجوكر» · النعل من النص «خطوطه ناعمة» |
| 17.5–24.5s | Details 04–05 | 3D turn to the heel «حتى من ورا مرتّب», 3D flip to the outsole «شوف هالنقشة» |
| 24.5–26s | Athlete | Campaign photo with "الجوكر" layered behind the player |
| 26–30s | Finale | Light implodes → explosion + shockwaves, 3D shoe above the planet, logo, title, "صار متوفّر" |

## How the 3D works
Each genuine product photo (side, other side, heels, outsole) becomes a relief mesh in Three.js:
- `depth_maps.py` runs Depth Anything V2 (ONNX) on the original photos, blends it with a silhouette
  inflation and tapers it at the edges → `public/depth_*.png` (displacement) and `public/normal_*.png` (lighting).
- `src/components/Shoe3D.tsx` displaces a dense plane by the depth map and re-lights it per frame
  (diffuse + specular + blue rim), so turning shows real volume. Switching between photo angles is a 3D
  turn with a hand-off at peak speed under motion blur.
- No product geometry, texture or logo is generated; only the photos are used.

## Assets
- Product images: background-removed cut-outs of the official 361° campaign photos.
- Logo: cropped from the official artwork, unaltered.
- Space backdrop: `space_assets.py` → `public/nebula.jpg`, `public/planet.png` (procedural).
- Fonts: Cairo (Arabic), Anton, Inter, Space Mono (Google Fonts, OFL), bundled in `public/fonts`.
- Soundtrack: `soundtrack_synth.py` (numpy/scipy) → `public/soundtrack.wav`.

## Run
```bash
npm i
npx remotion studio            # preview / edit
npx remotion render JokerArtemis output/Joker2GT_Artemis_AR_30s.mp4 --codec=h264 --crf=17
# WebGL uses the ANGLE renderer (remotion.config.ts)
# offline/locked-down machines: add --browser-executable=/path/to/chrome-headless-shell
```
