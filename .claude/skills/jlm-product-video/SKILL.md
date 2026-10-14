---
name: jlm-product-video
description: This skill should be used when the user asks for a JLM promo / product video, Reel, TikTok or Story built from product photos (not from existing footage) — فيديو إعلاني لمنتجات JLM من صور المنتجات. It renders a branded 9:16 motion film (graphite + silver + JLM gold, Helvetica Neue LT Arabic, "Engine Pulse" heartbeat concept) with readable Arabic captions, products shown one after another, a jlmstore.com end card and a synthesized soundtrack.
---

# JLM product video

The reference build is `marketing/videos/jlm-promo-20s/`. Copy that folder
for a new film, then change only `scripts/storyboard.py` and `assets/`.

## Workflow

1. **Assets.** The product photos are usually small web images. Upscale them
   4× with EDSR (OpenCV `dnn_superres`, model `EDSR_x4.pb` cloned from
   `github.com/Saafke/EDSR_Tensorflow`; raw.githubusercontent.com is blocked,
   so use a sparse `git clone`). Then cut each product out to a transparent
   PNG. `scripts/prepare_assets.py` shows how to do this:
   - remove white with seeded connected components, which keeps white labels
     and drops the handle holes;
   - separate products that overlap with a measured split line;
   - rebuild a hidden part from a twin product (same bottle, different label);
   - rebuild the JLM logo as a crisp mask (geometric roundel plus traced letters).
2. **Copy.** Edit `scripts/storyboard.py`. Keep 2–5 words per line and at
   least 2.2 s on screen per line. Mark one gold word per headline. Take
   benefits from the label or the product page; never invent claims.
3. **Stills first.** Run
   `render.py --stills t1,t2,…` and look at every scene. Check the text
   inside the safe areas, the product edges on the dark background, and the
   Arabic shaping.
4. **Render.** Run
   `render.py --assets assets --fonts assets/fonts --out out/x.mp4`.
   It writes 1080×1920 at 30 fps, H.264 CRF 16, AAC 192k,
   loudnorm −14 LUFS with a limiter.
5. **Verify.** Run `ffprobe` (duration and size) and `ebur128` (I ≈ −14,
   true peak < −1 dBFS). Pull frames at each transition and read them.
   Then send the mp4 with `SendUserFile`.

## Brand rules

- Palette: graphite `#0D0E10`, steel `#23262B`, silver `#C9CDD2`, white,
  and JLM gold `#C8A165` (the "Premium Grade" bronze) for one emphasis
  per scene only.
- Type: Helvetica Neue LT Arabic Bold for headlines, Roman for chips and
  body text. Lay out Arabic word by word right-to-left with Pillow + raqm.
  Never use ffmpeg `drawtext` for Arabic.
- The JLM logo stays at the top centre all the way through.
- End card: all products in a row, then
  "زوروا موقعنا / jlmstore.com / لاكتشاف العديد من المنتجات / التي يمكنكم طلبها"
  and a gold badge "مع توفر خدمة التوصيل".
- Leave the bottom 12 % of the frame clear for the platform UI.

## Fonts

Helvetica Neue LT Arabic is licensed. Keep it in `assets/fonts/`
(gitignored) and ask the user for the files if they are missing.
