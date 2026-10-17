---
name: jlm-edit-styles
description: Use FIRST whenever the user sends a video (mp4/mov/link) to edit, montage, cut, caption or turn into a Reel — عندما يرسل المستخدم فيديو للتعديل أو المونتاج. Analyses the footage, ASKS the user which of the six editing styles to use (Clean/Minimal, Jump Cut/Vlog, Fast-Paced/Retention, Meme/Comedy, Kinetic Typography, Vox-style) with a reasoned recommendation, then edits in that style with the JLM brand kit.
---

# JLM edit styles — ask, recommend, then edit

The six styles were studied from the Khater Academy episode the client sent on 2026-10-17.
**Read `brand/jlm/EDIT_STYLES.md` before every edit.** It holds each style's definition,
on-screen traits, mistakes, JLM adaptation and parameters. A picture per style is in
`brand/jlm/edit-styles/six_styles_reference.jpg`.

## Workflow

1. **Look at the footage before asking anything.**
   - Probe the file: `ffprobe` duration, size and fps, and whether it has audio.
   - Pull a frame every 2 s into a 5×5 contact sheet and read it.
   - Transcribe with Whisper turbo (sherpa-onnx, offline). Run
     `python3 .claude/skills/jlm-edit-styles/scripts/asr_chunks.py MODEL_DIR video.mp4 ar`.
     It writes about 22 s chunks with timestamps; the script header says where to get the
     model.
   - Classify the footage:
     - talking head, b-roll only, product shots, or screen recording;
     - length;
     - how much filler and silence it has;
     - the purpose: sell / trust / explain / entertain / launch.
2. **Ask which style, and recommend one.** This step is required and is never skipped, even
   when the answer seems obvious. Use `AskUserQuestion`:
   - **Question 1, «أي ستايل مونتاج تريد لهذا الفيديو؟», single choice.**
     - The recommended style goes first, labelled «(موصى به)», with a one-line reason drawn
       from this footage (its length, its content, its purpose).
     - Three more styles follow, best-fit first.
     - The remaining styles stay reachable through "Other". Name all six in the question
       text so the user can type any of them.
   - **Question 2, «هل تريد لمسة من ستايل آخر؟», multiSelect.** Offer the 2–3 most useful
     accents from the table in EDIT_STYLES.md, for example:
     - Kinetic for the hook and tagline;
     - a Vox board for the "how it works" part;
     - Jump-cut clean-up;
     - «بدون إضافات».
   - In the same message, give a short Arabic note: what the footage is, why the
     recommended style fits, and what the second-best style would look like.
3. **Clean the footage when needed.** Raw speech with fillers or long pauses always gets a
   jump-cut pass first, whatever style was chosen:
   - cut the fillers;
   - trim gaps longer than 0.25 s down to 0.08–0.12 s;
   - keep the last good take of each repeated line;
   - add a 15 ms audio crossfade at every cut.
4. **Edit in the chosen style** with the parameters in EDIT_STYLES.md.
   - **Footage overlays** (Clean, Fast-Paced, Jump Cut, Meme): use the Python/numpy/OpenCV/PIL
     pipeline. `marketing/videos/jlm-care-edit/scripts/edit_v3.py` has these pieces:
     - `Captions`;
     - `badge_layer` / `Pairs`;
     - `Explainer`;
     - `EndCard`;
     - `soft_tick`.

     Copy the script into a new folder under `marketing/videos/`.
   - **Full-screen motion graphics** (Kinetic, Vox boards): use HyperFrames compositions,
     with `jlm-penetrating-oil/` as the reference. GSAP is vendored at
     `assets/vendor/gsap.min.js` because the CDN is blocked. Alternatively, render the boards
     in Python and cut them in.
   - Arabic is always set with Pillow + raqm (RTL), never with ffmpeg `drawtext`.
5. **Verify and deliver.**
   - Pull stills at every style beat (each pop, freeze, card and cut) and read them.
   - Check loudness: about −14 LUFS with true peak below −1.5 dBFS, using
     `volume=-3dB,alimiter=limit=0.63:attack=2:release=60:level=false,loudnorm=I=-14:TP=-2.5:LRA=11`.
   - Send the mp4 with `SendUserFile`.
   - Commit it under `marketing/videos/<name>/out/` so the user can fetch it on the phone.

## Non-negotiable JLM rules (every style)

- **Fonts:** Helvetica Neue LT Arabic (Bold / Roman) and Albert Sans, from `brand/jlm/fonts/`.
  Never change them.
- **Palette:** charcoal `#252729`, yellow `#FAB817`, silver `#C0C4C7`, off-white `#F1F0EC`.
  Red is for problem words only. The reference video's orange and teal map to yellow and silver.
- **Logo and end card:** the logo follows the background (see `brand/jlm/BRAND.md`). End on the
  black CTA screen: «اطلبها الآن من خلال jlmstore.com» and «مع توفر خدمة التوصيل».
- **Sound:** icon and SFX sounds stay soft and harmless (ticks at about −40 dBFS). Meme stingers
  stay short and soft unless the user explicitly asks for louder ones.
- **Wording:** never call fuel products «باكج».
- **Claims and numbers:** only from the product label or the client. No copyrighted film or TV
  clips in commercial edits; Meme beats use the client's own reaction shots, cartoons or
  stickers instead.
- **Safe area:** keep the bottom 12 % clear of key text (Reels UI).
- **Approved and rejected looks:** the client's approved talking-head look
  (`brand/jlm/VIDEO_STYLE.md`, the DPF reference) is Clean + a Fast-Paced accent; when in doubt,
  recommend it. The v2 3D-tile look is rejected.

## Recommendation logic (short form)

| Signal in the footage | Recommend |
|---|---|
| Presenter explains a product or its usage, 30–90 s | Clean / Minimal |
| Short ad or Reel under 45 s, the goal is sales | Fast-Paced / Retention |
| Long raw talk, a testimonial or a story, lots of filler | Jump Cut / Vlog |
| Comparison, causes, "how it works", the goal is understanding | Vox-style |
| No presenter: slogan, offer, launch, intro | Kinetic Typography |
| Funny workshop moment, a trend, a reaction | Meme / Comedy (brand-safe) |

Mixing is encouraged: one main style plus one accent. The episode's own closing rule is that
the best editors combine styles.
