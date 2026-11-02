---
name: jlm-product-video
description: This skill should be used for ANY JLM design or video — promo / product video, Reel, TikTok, Story, post, banner — تصميم أو فيديو لـ JLM. It applies the approved JLM Liquid Tools brand kit in brand/jlm/ (charcoal + JLM yellow, official logos, Helvetica Neue LT Arabic + Albert Sans, drop icon, gear pattern, ATL template layout) and renders 9:16 motion films with readable Arabic captions, products one after another, a jlmstore.com end card and a synthesized soundtrack.
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

## Footage edits (real video with a presenter)

When the user sends a video to edit, **start with the `jlm-edit-styles` skill**. It
analyses the footage, asks which of the six editing styles to use and recommends one
(see `brand/jlm/EDIT_STYLES.md`). When the user picks the approved look (Clean with a
Fast-Paced accent), follow `brand/jlm/VIDEO_STYLE.md` (the client's approved style, third
reference). The style has:
- one-line karaoke captions at 66 % height on a soft dark box: the spoken word in
  yellow, upcoming words grey, problem words red;
- under the caption, one pair of round dark badges per sentence, linked by a
  yellow dashed arrow (problem → solution, cause → result); each badge's ring and
  line icon draw themselves, red for problems and yellow for solutions;
- a dark-board explainer with numbered steps and a gold flow;
- a black CTA end screen: the logo, the spoken line,
  «اطلبها الآن من خلال jlmstore.com» and «مع توفر خدمة التوصيل».

Icon sounds stay very soft (about −40 dBFS); the client asked for this explicitly.
Never change the JLM fonts. The reference implementation is
`marketing/videos/jlm-care-edit/scripts/edit_v3.py`. The client rejected v2
(`edit_v2.py`, with 3D tiles); do not reuse its look.
Transcribe the voice first. Whisper turbo via sherpa-onnx works offline; the
model comes from the k2-fsa GitHub releases. Then time every caption to the
spoken words.

## Brand rules

**Read `brand/jlm/BRAND.md` first. It is the approved kit (logos, fonts, icons,
templates) and it overrides anything below.** Pick the logo variant by
background: `logo_on_dark.png` on charcoal, `logo_on_yellow.png` on yellow.

- Palette: charcoal `#252729`, JLM yellow `#FAB817`, silver `#C0C4C7`,
  off-white `#F1F0EC`.
- Type: Helvetica Neue LT Arabic Bold for Arabic headlines and Roman for
  Arabic body text; Albert Sans for Latin product names and URLs. Lay out Arabic word by word right-to-left with Pillow + raqm.
  Never use ffmpeg `drawtext` for Arabic.
- Layout follows the ATL vertical template: headline in a yellow 5 px frame
  with a solid yellow tag, the product in the middle on the gear pattern,
  and a yellow footer with the drop, the logo and jlmstore.com.
- The transition is a yellow drop that falls into the footer.
- End card: all products in a row, then
  "زوروا موقعنا / jlmstore.com / لاكتشاف العديد من المنتجات / التي يمكنكم طلبها"
  and a charcoal badge with yellow text "مع توفر خدمة التوصيل", then the Made in The Netherlands label.
- Leave the bottom 12 % of the frame clear for the platform UI.

## Fonts

All fonts live in `brand/jlm/fonts/`. Pass that folder as `--fonts`.
