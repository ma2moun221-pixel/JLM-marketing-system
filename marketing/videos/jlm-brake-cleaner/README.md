# JLM Brake Cleaner — Reel edit (19.6 s, 1080×1920)

The client's 16 s clip (presenter + brake b-roll + product shot), edited in **Clean / Minimal** with a
**Kinetic** opening (brand/jlm/EDIT_STYLES.md §1 + §5, the approved DPF look in VIDEO_STYLE.md).

- **Kinetic hook (0–3 s):** «إذا كنت بتعاني من» builds word by word → «أصوات» lands in red, vibrates and
  sends out sound waves → «في البريكات عندك؟».
- **Karaoke captions** at 66 % height in the JLM fonts (Helvetica Neue LT Arabic + Albert Sans for
  `JLM Brake Cleaner` and the price); on the product shot the caption moves above the can.
- **Light icons:** two linked pairs drawn as thin glowing lines — صوت بالبريك → أتربة وغبار (cause),
  بريك كلينر → بريك نظيف (solution) — plus a small `JLM Brake Cleaner` tag on the product shot.
  Each icon gives one soft tick (≈ −40 dBFS).
- Gentle 1.00 → 1.05 zoom per shot, the JLM logo top-left, and the black CTA end card:
  logo · Brake Cleaner · «اطلبه الآن من خلال» · jlmstore.com (with a sheen) · «مع توفّر خدمة التوصيل».
- Voice kept as recorded; loudness −14 LUFS.

Captions follow the speech as transcribed (Whisper turbo); the price line is «سعر العبوة 25 شيكل».

```bash
python3 scripts/edit.py --src src/raw.mp4 --out out/jlm_brake_cleaner.mp4          # full render
python3 scripts/edit.py --src src/raw.mp4 --out out/stills/x.mp4 --stills 1,5,9.6   # check frames
```
`src/raw.mp4` is the client's footage (not committed). Shared badge / icon / end-card code lives in
`../jlm-care-edit/scripts/edit_v3.py`.
