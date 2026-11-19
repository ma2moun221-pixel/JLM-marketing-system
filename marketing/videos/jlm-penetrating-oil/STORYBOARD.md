---
format: 1080x1920
duration: 71s
message: "JLM Penetrating Oil frees any rusted, seized bolt in minutes — without breaking it."
arc: Intro sting → Hook (pain) → Product intro → Mechanism → Who/where → How to use ×2 → CTA
audience: Mechanics, workshop technicians and DIY car owners in Palestine
mode: autonomous
music: industrial-tech pulse (host-synthesised, very low under VO)
captions: skipped (every frame carries the user's own product copy on screen; Arabic VO captions would duplicate it)
---

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

- scene: A yellow ring draws itself on black, the official JLM logo resolves inside it, then the logo leaves and the ring waits like a lens.
- duration: 3.2s
- poster: 1.8s
- transition_in: cut
- status: animated
- type: branding
- blueprint: logo-assemble-lockup (Adapt)
- focal: assets/logo_on_dark.png
- roles: logo_on_dark = supporting
- asset_candidates: assets/logo_on_dark.png
- voiceover: (none — music + sfx only)
- sfx: soft riser, soft tick on logo
- src: compositions/frames/01-intro.html
- handoff_out: ring `C` — centre (540, 900), r 470, stroke 8 px `#FAB817`, opacity 1, no rotation, static; background solid `#141516`; nothing else on screen (logo opacity 0).

Adapt: keep the signature (an abstract system assembles around a fixed mark), with the JLM roundel ring as the system.

- Scene 1 (0.0–1.1s): A pure ink ground. Yellow ring `C` **self-draws** clockwise from 12 o'clock (→ `svg-path-draw`). Two fainter concentric silver hairline arcs (r 520, r 560, opacity 0.25) draw in counter-clockwise just behind it (orbit feel).
- Scene 2 (1.0–2.2s): `logo_on_dark.png` at width 560, centred (540, 900), resolves with scale 0.92→1 and opacity 0→1, plus a soft yellow glow bloom (→ `ambient-glow-bloom`). The silver arcs rotate slowly.
- Scene 3 (2.2–3.2s): The logo scales 1→0.9 and fades out; the silver arcs fade out. Ring `C` remains alone, exactly at the handoff pose by 3.1 s, and holds.

## Frame 2 — Hook: the seized bolt

- scene: Through the ring-lens we see the bolt and nut — rusted. A wrench line-icon tries to turn the nut and only shakes. The rust then clears into the clean label drawing.
- duration: 5.16s
- poster: 2.6s
- transition_in: cut
- status: animated
- type: hook
- blueprint: kinetic-type-beats (Adapt)
- focal: assets/label-bolt-nut.png
- roles: label-bolt-nut = cutout (inside the circle mask)
- asset_candidates: assets/label-bolt-nut.png
- voiceover: "برغي عالق بسبب الصدأ؟ قبل أن تكسره... هناك حلّ أذكى."
- VO cues (s): برغي 0.2 · الصدأ 1.6 · قبل 2.4 · تكسره 3.0 · هناك 3.5 · حل 3.9 · أذكى 4.2
- sfx: metal strain creak (soft), tick
- src: compositions/frames/02-hook.html
- handoff_in: ring `C` exactly as frame 1's handoff_out; background `#141516`.
- handoff_out:
  - `CROP` fully visible inside circle mask `C` (r 470), **clean**: no rust tint, no overlay, opacity 1.
  - Ring `C` stroke 8 px yellow, opacity 1.
  - Outside the circle: solid `#141516`.
  - No text, no wrench.

Adapt: keep the signature (the key word lands alone, then the line escalates), here over a macro of the problem.

- Scene 1 (0.0–0.7s): **Iris in.** Inside ring `C`, a circular mask grows from r 0 to r 470 (centre (540, 900)), revealing `CROP` at its shared pose. While the mask grows, the crop counter-rotates from −12° to 0° around (540, 900), which reads as a spiral lens opening.
  - The crop is **rusted**: a warm-brown multiply tint plus a sparse rust-speck SVG layer (seeded, deterministic) on the nut and the bolt head.
- Scene 2 (0.2–2.3s): "برغي عالق بسبب الصدأ؟" enters above the ring.
  - Off-white, Arabic 700, ~78 px, centred at y≈300; per-word staggered (→ `dynamic-content-sequencing`).
  - "الصدأ" is in rust-brown.
  - At 1.6 s ("الصدأ") the rust specks pulse brighter once.
- Scene 3 (2.4–3.4s): A silver line-art **wrench** icon (~420 px) enters on an arc onto the nut (nut centre on screen ≈ (683, 735)). It tries to rotate +10°, snaps back, and **shakes** with a tight 3-cycle jitter: stuck.
  - At "تكسره" (3.0 s), a thin crack-flash line appears briefly on the bolt shank.
  - The line below the ring reads "قبل أن تكسره…" (silver, ~56 px, y≈1460).
- Scene 4 (3.5–4.5s): The wrench arcs away and fades. "هناك حلّ أذكى" replaces the lower line, in JLM yellow, ~72 px; "أذكى" lands last.
  - The rust tint and specks **dissolve** radially from the nut outward (0.5 s), leaving the clean label drawing.
- Scene 5 (4.5–5.16s): The texts fade out. The clean `CROP` is in the circle and ring `C` holds, exactly the handoff_out state.

## Frame 3 — Product intro: the can is revealed

- scene: Match cut. The clean bolt drawing is revealed to be printed on the JLM can as the camera spirals back. The product is named, its role is stated, and three benefits orbit it. Finally the camera dives into the +MoS2 drop.
- duration: 11.95s
- poster: 6.0s
- transition_in: cut
- status: animated
- type: product_intro
- blueprint: zoom-out-workspace-reveal (Adapt)
- focal: assets/penetrating-oil-can.png
- roles: penetrating-oil-can = cutout (hero)
- asset_candidates: assets/penetrating-oil-can.png
- voiceover: "زيت الاختراق من JLM. بخاخ اختراق عالي الأداء ومتعدد الاستخدامات، لمعالجة الصدأ والتآكل والأجزاء الملتصقة بسهولة."
- VO cues (s): زيت 0.2 · JLM 1.6–2.3 · بخاخ 2.6 · عالي الأداء 3.9 · ومتعدد الاستخدامات 4.9 · لمعالجة 7.0 · الصدأ 7.6 · والتآكل 8.3 · والأجزاء الملتصقة 9.1 · بسهولة 10.9
- sfx: deep whoosh on the pull-back, soft ticks on each benefit, rising whoosh into the zoom-through
- src: compositions/frames/03-product.html
- handoff_in: `CAN@CROP` (the full can image at width 1199.24, top-left (−129.39, −1357.39), rotation 0) masked by circle `C` r 470; ring `C` stroke 8 px yellow opacity 1; outside solid `#141516`. This is pixel-identical to frame 2's last frame.
- handoff_out: full frame solid `#3C6999` (label blue), opacity 1, nothing else visible.

Adapt: keep the signature (the close-up mystery re-scopes into the whole object exactly when the VO names it).

- Scene 1 (0.0–2.4s): **Cut-out reveal + spiral pull-back.** The circle mask grows past the frame (r 470 → 1400) while ring `C` expands and fades.
  - At the same time the can moves from `CAN@CROP` to `CAN@HERO`: scale 1.42424 → 0.4792 (height 1150), with a **circular** camera path. The can rotates −8° and back to 0° while its anchor travels on an arc, one smooth `power3.inOut`.
  - The silver of the can is now on the ink ground, with a soft floor shadow under it.
  - At "JLM" (1.6 s) the title assembles above the can: "زيت الاختراق" (off-white Arabic 700, ~84 px, y≈205), with "Penetrating Oil" in Albert Sans 800 yellow ~40 px under it.
- Scene 2 (2.6–6.6s): A thin yellow **orbit ring** (ellipse rx 330, ry 90, centred (540, 1500), tilted like a turntable) draws around the can's base and keeps rotating slowly.
  - On "بخاخ" the line «بخاخ اختراق عالي الأداء» appears below the can, per word (silver/off-white Arabic 400, ~44 px, y≈1600).
  - On "ومتعدد الاستخدامات" the line «ومتعدد الاستخدامات» appears (y≈1655).
  - A small yellow "+ MoS2" Albert Sans tag points to the drop on the label.
- Scene 3 (7.0–11.0s): The three benefits **orbit in** on circular paths and settle around the can, as icon + word chips. Each is a silver line icon in a charcoal pill with a yellow hairline.
  - "الصدأ" (7.6 s): right side, y≈700.
  - "التآكل" (8.3 s): left side, y≈980.
  - "الأجزاء الملتصقة" (9.1 s): right side, y≈1260.
  - The bottom lines fade at 7.0 s. «لمعالجة الصدأ والتآكل والأجزاء الملتصقة بسهولة» assembles at y≈1600, with "بسهولة" in yellow at 10.9 s.
- Scene 4 (11.0–11.95s): **Zoom-through.** Everything except the can fades in 0.25 s.
  - The camera spiral-zooms into the can: from `CAN@HERO` to `CAN@DROP` and beyond, rotating +6°, with motion-blur streaks (→ `coordinate-target-zoom`, `motion-blur-streak`).
  - By 11.75 s the blue of the drop fills the frame; the last 0.2 s is solid `#3C6999`.

## Frame 4 — How it works: inside the thread

- scene: Out of the blue drop, a yellow oil drop falls into a cutaway of a rusted bolt inside its nut. Oil penetrates the threads, rust dissolves, moisture is pushed out, and a protective film coats everything. The bolt then spins free.
- duration: 12.3s
- poster: 9.0s
- transition_in: cut
- status: animated
- type: feature_showcase
- blueprint: compose
- focal: (vector schematic — no image asset)
- roles: none
- asset_candidates: none
- voiceover: "تركيبته القوية تخترق البراغي والصواميل الصدئة بعمق. تذيب الصدأ، وتطرد الرطوبة، وتمنح تزييتًا فائقًا، وحماية طويلة الأمد."
- VO cues (s): تخترق 1.7 · البراغي 2.4 · والصواميل 3.0 · بعمق 4.5 · تذيب الصدأ 5.3 · وتطرد الرطوبة 6.2 · وتمنح تزييتًا فائقًا 7.9 · وحماية 10.0 · طويلة الأمد 10.7
- sfx: drop plop (soft), liquid seep, soft ticks per step
- src: compositions/frames/04-mechanism.html
- handoff_in: full frame solid `#3C6999`, opacity 1.
- handoff_out:
  - Ink `#141516` ground.
  - A yellow `#FAB817` regular **hexagon outline** (bolt head, top view), stroke 10 px, circumradius 150, centre (540, 760), flat-top orientation.
  - The hexagon is **rotating clockwise at 90°/s**; at the cut its rotation is exactly 0° (flat-top).
  - Nothing else visible.

Compose: a technical cutaway in a blueprint style, built from silver hairline SVG on ink, with numbered steps.

- Scene 1 (0.0–1.4s): The blue field irises down into a single **yellow oil drop** (teardrop, ~140 px tall) at (540, 520), while the ink ground and a faint silver grid appear.
  - The drop falls on a gentle arc to (540, 760), onto the top of the cutaway.
  - The cutaway draws itself (→ `svg-path-draw`): a vertical bolt shank, with sawtooth threads on both flanks, inside nut walls. It spans x 300–780, y 760–1500, in silver hairlines.
  - The gaps between bolt and nut threads hold **rust** (brown granules, seeded) and **moisture** (small silver-blue droplets).
- Scene 2 (1.7–4.9s): Step **1 «يخترق بعمق»** appears as a label: a yellow number disc "1" (Albert Sans 800) with off-white Arabic 700 ~52 px, top-left at (100, 300), RTL.
  - Yellow oil **creeps down the thread gaps** as a glowing path that follows the zigzag, reaching the bottom by 4.5 s ("بعمق").
- Scene 3 (5.3–6.2s): Step **2 «يذيب الصدأ»**. The rust granules touched by oil shrink and dissolve with tiny yellow sparkles (→ `particle-burst`, small).
- Scene 4 (6.2–7.8s): Step **3 «يطرد الرطوبة»**. The moisture droplets are pushed outward and up, out of the thread gaps, and leave the frame.
- Scene 5 (7.9–10.6s): Step **4 «يزيّت ويحمي»**. A thin glowing yellow film coats every thread flank. A shield line-icon (silver, ~110 px) draws itself beside the label. The label list now shows 1–4 stacked; the earlier steps are dimmed to 45 %.
- Scene 6 (10.7–12.3s): "طويلة الأمد": the cutaway fades to 20 % and the camera tilts to top-down.
  - The bolt head is seen from above as the yellow hexagon (circumradius 150, centre (540, 760)), and it **spins freely**: the bolt is loosened.
  - The rotation reaches a steady clockwise 90°/s and is exactly 0° at the cut (12.3 s).
  - Everything else is gone by 12.1 s.

## Frame 5 — Who it's for, where it works

- scene: The spinning hex becomes the hub. Three audiences and three applications orbit in around it, then a yellow wipe sweeps the screen.
- duration: 11.16s
- poster: 9.5s
- transition_in: cut
- status: animated
- type: benefit_highlight
- blueprint: constellation-hub (Adapt)
- focal: (vector hub — no image asset)
- roles: none
- asset_candidates: none
- voiceover: "أداة أساسية للميكانيكيين والمهندسين وهواة الأعمال اليدوية، لصيانة وإصلاح الآلات والمركبات والمعدات الصناعية."
- VO cues (s): أداة أساسية 0.2–1.5 · للميكانيكيين 1.6 · والمهندسين 2.8 · وهواة الأعمال اليدوية 3.9 · لصيانة وإصلاح 6.1 · الآلات 7.4 · والمركبات 8.0 · والمعدات الصناعية 9.0
- sfx: soft ticks per node, airy whoosh on the wipe
- src: compositions/frames/05-audience.html
- handoff_in: yellow hexagon outline, stroke 10 px, circumradius 150, centre (540, 760), flat-top, rotation 0° and spinning clockwise at 90°/s; ink ground.
- handoff_out:
  - A **yellow wipe band** `#FAB817` covers the **entire** frame, opacity 1.
  - Its leading edge has a 14° slant and moves right-to-left; at the cut the band covers x 0–1080 fully.
  - Nothing else is visible.

Adapt: keep the signature (nodes ring a centre and lines connect them in).

- Scene 1 (0.0–1.5s): The hexagon decelerates to a stop over 1.0 s, with its inertia carried in. A small yellow wrench glyph draws inside it.
  - The headline «أداة أساسية» lands above it (off-white Arabic 700 ~80 px, y≈330).
- Scene 2 (1.6–5.6s): Three **audience nodes** orbit in on an inner ring (radius 330 around (540, 760)) and connect to the hub with yellow hairlines (→ `avatar-cloud-network`, `orbit-3d-entry`). Each node is a charcoal circle 150 px with a silver line icon and an Arabic label of ~38 px under it.
  - «الميكانيكيين» (1.6 s), with a wrench + gear icon, at the 2 o'clock position.
  - «المهندسين» (2.8 s), with a caliper/compass icon, at 6 o'clock.
  - «هواة الأعمال اليدوية» (3.9 s), with a hand + screwdriver icon, at 10 o'clock.
- Scene 3 (6.1–10.2s): The ring rotates 60° to make room. «لصيانة وإصلاح» appears under the constellation (silver ~46 px, y≈1300).
  - The applications appear as a row of three yellow-outlined chips at y≈1450:
    - «الآلات» (7.4 s, gear icon),
    - «المركبات» (8.0 s, car icon),
    - «المعدات الصناعية» (9.0 s, factory icon).
  - They enter on circular arcs from the hub.
- Scene 4 (10.3–11.16s): **Wipe.** A yellow band with a 14° slanted leading edge sweeps from the right edge to the left edge (RTL reading direction), covering everything by 11.1 s.

## Frame 6 — How to use, part 1

- scene: The wipe reveals the can again. It shakes, sprays the bolt, then a circular timer counts the soak.
- duration: 10.18s
- poster: 8.8s
- transition_in: cut
- status: animated
- type: feature_showcase
- blueprint: device-surface-showcase (Adapt)
- focal: assets/penetrating-oil-can.png
- roles: penetrating-oil-can = cutout · label-bolt-nut = supporting (inside a circle)
- asset_candidates: assets/penetrating-oil-can.png, assets/label-bolt-nut.png
- voiceover: "طريقة الاستخدام: قم برجّ العبوة جيدًا. رشّ الزيت مباشرة على المنطقة المستهدفة. واتركه يتغلغل بضع دقائق."
- VO cues (s): طريقة الاستخدام 0.2–1.6 · قم برج العبوة جيدا 1.8–3.5 · رش الزيت 3.7 · المنطقة المستهدفة 5.5–7.0 · واتركه يتغلغل 7.4 · بضع دقائق 8.7–9.6
- sfx: rattle (very soft), spray hiss, clock ticks (soft)
- src: compositions/frames/06-usage-1.html
- handoff_in: the yellow wipe band `#FAB817` covering the whole frame (leading edge slant 14°), continuing to travel right-to-left.
- handoff_out:
  - Ink ground.
  - A yellow **timer ring**: a circle stroke 8 px `#FAB817`, centre (540, 900), radius 300, **fully closed** (360° drawn), opacity 1.
  - Inside it, `CROP` (`assets/label-bolt-nut.png`) masked to a circle of radius 292, centred (540, 900), shown at width 600 (scale 0.9091 → height 609.1, top-left (240, 595.45)), opacity 1, rotation 0, with a light yellow sheen (oil) over it.
  - The can and all text are gone.

Adapt: keep the signature (the product does its loop step by step, with no cursor).

- Scene 1 (0.0–1.6s): **Wipe out.** The yellow band keeps travelling right-to-left and exits at the left edge (0.0–0.55 s), revealing the ink ground.
  - The title «طريقة الاستخدام» sits top-right (off-white Arabic 700 ~74 px, y≈250), with a short yellow rule under it.
  - The can sits at `CAN@HERO` but shifted left: centre (330, 980), height 1000.
- Scene 2 (1.8–3.5s): Step «١ رجّ العبوة جيدًا قبل الاستخدام» (user's copy, Arabic 400 ~44 px) appears at right, y≈620, with a yellow number disc. The can **shakes**: a rotation oscillation ±7°, 6 cycles, decaying.
- Scene 3 (3.7–7.0s): Step «٢ رشّ الزيت مباشرة على المنطقة المستهدفة».
  - The can tilts −25° on an arc, nozzle toward the right.
  - A circle-masked `CROP` (radius 200) appears at (790, 1180). A cone of fine yellow **spray mist** particles (seeded) travels from the nozzle onto the bolt.
  - The bolt drawing gets an oil sheen.
- Scene 4 (7.4–10.18s): Step «٣ اترك المنتج يتغلغل لمدة بضع دقائق، اعتمادًا على مستوى التآكل».
  - The can arcs out of frame to the left and fades. The bolt circle moves on an arc to centre (540, 900) and grows to radius 292.
  - A yellow **timer ring** (radius 300) sweeps clockwise from 12 o'clock to closed by 9.9 s (→ `stat-bars-and-fills` ring), with small tick marks. A tiny clock-hand line rotates inside.
  - The step texts fade by 9.9 s.

## Frame 7 — How to use, part 2

- scene: The timer ring becomes the socket of a wrench. The bolt turns freely, then a cloth-wipe cleans the surplus oil and wipes the screen.
- duration: 7.73s
- poster: 4.0s
- transition_in: cut
- status: animated
- type: feature_showcase
- blueprint: compose
- focal: assets/label-bolt-nut.png
- roles: label-bolt-nut = supporting (inside a circle)
- asset_candidates: assets/label-bolt-nut.png
- voiceover: "ثم استخدم الأدوات المناسبة لفكّ الأجزاء بعناية، وقم بمسح أي زوائد من المنتج."
- VO cues (s): استخدم الأدوات المناسبة 0.6–2.7 · لفك الأجزاء 2.8–3.9 · بعناية 4.0 · وقم بمسح 4.7–5.5 · أي زوائد من المنتج 5.6–7.2
- sfx: ratchet clicks (soft), cloth swipe
- src: compositions/frames/07-usage-2.html
- handoff_in: ink ground; timer ring stroke 8 px yellow, centre (540, 900), r 300, closed; `CROP` circle-masked r 292 at width 600, top-left (240, 595.45), with a light yellow sheen.
- handoff_out:
  - A **charcoal wipe band** `#252729` covers the whole frame. It has a soft 40 px yellow leading highlight, slant −14°, and moves left-to-right; at the cut it covers x 0–1080 fully.
  - Nothing else is visible.

Compose: a match cut from ring to socket, then a circular turn, then a literal wipe.

- Scene 1 (0.0–2.7s): The timer ring thickens into the **socket ring** of a silver line-art socket wrench. Its handle draws out to the lower-left at −35°.
  - Step «٤ استخدم الأدوات المناسبة لفك الأجزاء بعناية، وتجنب إتلاف المكونات المحيطة» (user's copy) appears at the top (Arabic 400 ~42 px, y≈260–330, two lines max), with a yellow disc "٤".
- Scene 2 (2.8–4.6s): **The turn.** The wrench and socket rotate 120° counter-clockwise around (540, 900) in two smooth ratchet strokes, and the bolt drawing inside rotates with them: the part comes loose.
  - A yellow arc arrow draws around the ring. On "بعناية" a small yellow check appears.
- Scene 3 (4.7–7.2s): Step «٥ قم بمسح أي زوائد من المنتج بعد فك الأجزاء» (user's copy) replaces the top text.
  - A charcoal **cloth band** enters from the left with a soft yellow highlight on its leading edge and wipes across the bolt: the sheen disappears behind it.
- Scene 4 (7.2–7.73s): The cloth band completes the **wipe**, covering the full frame by 7.7 s.

## Frame 8 — CTA

- scene: The wipe reveals the can at the centre of a slowly turning JLM ring, with the logo, the store and delivery.
- duration: 9.51s
- poster: 8.0s
- transition_in: cut
- status: animated
- type: cta
- blueprint: cta-morph-press (Adapt)
- focal: assets/penetrating-oil-can.png
- roles: penetrating-oil-can = cutout (hero) · logo_on_dark = supporting
- asset_candidates: assets/penetrating-oil-can.png, assets/logo_on_dark.png
- voiceover: "زيت الاختراق من JLM. اطلبه الآن من متجرنا الإلكتروني، مع توفّر خدمة التوصيل."
- VO cues (s): زيت الاختراق 0.2–1.3 · JLM 1.6–2.4 · اطلبه الآن 2.7–3.5 · متجرنا الإلكتروني 3.8–5.4 · مع توفر خدمة التوصيل 5.6–7.5 · (hold to 9.51)
- sfx: soft tick on the pill, soft chime at the end
- src: compositions/frames/08-cta.html
- handoff_in: charcoal wipe band `#252729` covering the whole frame (soft yellow leading highlight, slant −14°), continuing left-to-right.

Adapt: keep the signature (one small widget — the yellow store pill — performs a press while the VO names the action).

Layout (fixed): logo centre (540, 215) width 420 · ring centre (540, 800) r 430 (yellow 6 px) + silver hairline ring r 480 · can centre (540, 810) height 800 · title y 1320 · CTA line y 1415 · pill centre y 1515 · delivery row y 1625. Nothing below y 1690.

- Scene 1 (0.0–0.6s): The charcoal band continues left-to-right and exits at the right edge, revealing the ink ground. The yellow ring self-draws; the silver hairline ring rotates slowly for the whole frame. The can arrives on a circular arc (from lower-left, rotation −10°→0°) to its fixed pose, with floor shadow + thin yellow rim glow.
- Scene 2 (0.2–2.4s): `logo_on_dark.png` settles at the top; «زيت الاختراق من JLM» lands at y 1320 (off-white Arabic 700 ~64 px; "JLM" Albert Sans 800 yellow) on "JLM".
- Scene 3 (2.7–5.4s): «اطلبه الآن من خلال» (Arabic 700 ~54 px, "اطلبه الآن" yellow) at y 1415; then the yellow pill «jlmstore.com» (Albert Sans 800 ~52 px, charcoal text) pops in with a press-and-release on "متجرنا" (→ `press-release-spring`).
- Scene 4 (5.6–7.6s): delivery row «مع توفّر خدمة التوصيل» (off-white Arabic 700 ~44 px, "خدمة التوصيل" yellow) with a small yellow truck line-icon that self-draws, at y 1625.
- Scene 5 (7.6–9.51s): held read — everything still except the slow ring rotation.
