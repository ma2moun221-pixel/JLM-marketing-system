## Video direction

**One continuous shot.** Every frame boundary is a **match cut**. Only frame 1→2 has an iris, and frames 5→6 and 7→8 have wipes. The incoming frame starts from **exactly** the outgoing frame's final state (`handoff_out` = `handoff_in`, numbers below). The harness transition for every frame is `cut`; all transition motion is built inside the frames. Canvas is 1080×1920 and all coordinates are frame pixels with the origin top-left.

**The circle is the spine.** The JLM roundel is a yellow ring. It becomes an iris, then the lens that frames the bolt, then the orbit around the can, then the timer, then the wrench socket, and finally the CTA ring. Product motion is always **circular**: arcs, orbits, spins and spiral zooms. Never a straight slide.

- **Palette (frame.md):**
  - Ground: ink `#141516`, panels charcoal `#252729`.
  - Accent: JLM yellow `#FAB817`. It is the only accent, and the full field on wipe bands.
  - Silver `#C0C4C7` for line-art and secondary text; off-white `#F1F0EC` for text.
  - Rust is illustrated as warm brown `#8A4B22` / `#B5652A`, and only on the rusted subject.
  - Label blue `#3C6999` appears only as the zoom-through fill in frames 3→4.
  - Never use red or purple gradients.
- **Type:**
  - Arabic: Helvetica Neue LT Arabic. 700 for display and headlines (no 900 exists), 400 for body text.
  - Latin and numbers: Albert Sans 700–900.
  - All Arabic is `dir="rtl" lang="ar"`.
  - Body text on screen is the **user's own copy, verbatim** (quoted per frame).
- **Motion grammar:**
  - Long-tail eases (`power3.out` / `power2.inOut`); smooth, never bouncy.
  - The camera moves on circular paths: spiral zoom, orbit, rotate-while-scaling.
  - Reveals are **paced to the VO cue times given per frame**; nothing appears before its word.
  - During holds, at most a slow orbit-ring rotation or a gentle drift of the product shadow.
- **Held frames:**
  - Frame 3 ends on a held hero read before the zoom-through.
  - Frame 8 holds 1.4 s still on the CTA.
- **Product:**
  - Only `assets/penetrating-oil-can.png` (842×2400 native).
  - Soft floor shadow plus a thin yellow rim-glow allowed.
  - Never redrawn, recolored or distorted.
- **Negative list:**
  - No front-loading (dumping everything at t=0 and freezing), and no screensaver drift (everything floating independently).
  - No straight-line product slides.
  - No emoji, no stock gradients, no bokeh.
  - No text in the bottom 12 % (y > 1690) or top 6 % (y < 115).
  - No made-up claims; only the label and the user's copy.

**Shared geometry (all frames use these exact numbers):**

- `C` = the master circle. Centre (540, 900), radius 470, yellow `#FAB817` stroke 8 px.
- `CROP` = `assets/label-bolt-nut.png` (660×670).
  - Shown at width 940 / height 954.3.
  - Centre (540, 900), so its top-left is (70, 422.85).
  - Masked by circle `C` (radius 470).
- `CAN@CROP`: `assets/penetrating-oil-can.png` placed so that its printed bolt drawing coincides **exactly** with `CROP`.
  - Width 1199.24, height 3418.18, top-left (−129.39, −1357.39).
  - This is the can scaled 1.42424 with native point (470, 1585) at (540, 900).
- `CAN@HERO`: the can upright and centred.
  - Height 1150, width 403.4.
  - Centre (540, 960), so its top-left is (338.3, 385).
- `CAN@DROP`: the can scaled 1.7647, with native point (715, 1285) (the plain blue lower part of the "+MoS2" drop) at screen centre (540, 900).
  - Width 1485.9, height 4235.3, top-left (−721.8, −1367.6).

## Frame 1 — Intro sting
