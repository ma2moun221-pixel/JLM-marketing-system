# 361° JOKER 2 GT "ARTEMIS" — 15s motion spot

Vertical 1080×1920, 30 fps, 15 s, with an original synthesized soundtrack (120 BPM; every cut lands on a beat).

Final render: `output/Joker2GT_Artemis_15s.mp4`

## Timeline
| Time | Scene | Content |
|---|---|---|
| 0.0–2.0s | Countdown | HUD "MISSION // ARTEMIS", 3·2·1, star warp, light streak |
| 2.0–5.0s | Reveal | White flash, shoe slams in, "JOKER / 2 GT" giant type, "ARTEMIS" |
| 5.0–7.5s | 01 Upper | Macro pan across the upper — "PURE WHITE." |
| 7.5–9.5s | 02 Outsole | Outsole flips up — "ZERO GRAVITY." |
| 9.5–11.0s | 03 Heel | Heel pair rises — "MOON READY." |
| 11.0–12.5s | Athlete | Campaign photo with "JOKER" layered behind the player |
| 12.5–15.0s | Landing | Lunar ground, shoe touchdown (dust + shockwave), logo, title, "AVAILABLE NOW" |

## Assets
- Product images: background-removed cut-outs of the official 361° campaign photos (no AI-generated product imagery).
- Logo: cropped from the official artwork, unaltered.
- Fonts: Anton, Inter, Space Mono (Google Fonts, OFL), bundled in `public/fonts`.
- Soundtrack: `soundtrack_synth.py` (numpy/scipy) → `public/soundtrack.wav`.

## Run
```bash
npm i
npx remotion studio            # preview / edit
npx remotion render JokerArtemis output/Joker2GT_Artemis_15s.mp4 --codec=h264 --crf=17
# offline/locked-down machines: add --browser-executable=/path/to/chrome-headless-shell
```
