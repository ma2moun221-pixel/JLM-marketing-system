# Frame packet: 05-audience

## Project inputs

- Project: /home/user/JLM-marketing-system/marketing/videos/jlm-penetrating-oil
- Design tokens: /home/user/JLM-marketing-system/marketing/videos/jlm-penetrating-oil/frame.md
- RULES_DIR: /home/user/JLM-marketing-system/.claude/skills/hyperframes-animation/rules

## Assigned storyboard block

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

## Selected blueprint: constellation-hub

# constellation-hub — Constellation / Hub + Satellites

**intent**: Labeled/iconned nodes spring into a ring/cluster around a center, then the shot resolves on the core — either by pushing the camera INTO the center (depth-of-field collapsing onto it) or by holding a hub mark while the satellites ORBIT it; the "everything connects to / sits around one center" beat.

**roles served**

- Hook (from `hook-cluster-push-in`): a constellation of tool/app nodes springs into a wide ring, then a sustained camera push-in with depth-of-field resolves on the inner core — "it connects everything / one hub for all your tools."
- Social_Proof (from `social-proof-orbit-ecosystem`): the product brand mark lands as the center hub and partner logos spring onto a ring and revolve around it — "plugs into / sits at the center of your stack."
- CTA (from `cta-orbit-collapse`): the ring resolves by COLLAPSE rather than a push-in — category icons drift around an empty central CTA, a cursor click implodes the orbit toward the click point, and the product demo springs OUT of that collapse as the answer (scope → choice → consequence → product).
- Social_Proof (from `proof-logo-chain`): a persistent center logo accrues proofs — its wordmark decodes, a claim ticker swaps, the logo glides to center, then avatars cascade into orbit with drawn connectors while partner logos scroll the bottom strip; four claims read as one statement.
- Social_Proof (from `scatter-drift-finisher`): the ecosystem beat as a
  static END CARD — a two-line serif `[headline]` is the center (no hub mark, no ring), `[~20 app
icons]` pop in scattered frame-wide in a quick stagger, then keep drifting very slowly OUTWARD
  to the end. "Connects to thousands of apps" said with count and spread, not geometry.

**duration**: 5–8s (Hook 5–6s · Social_Proof 5–8s · CTA orbit-collapse ~6s · Social_Proof
scatter-drift end card ~2.5s as a closing beat)

**shot structure**

Consolidated template — nodes ring a center, then one of two finishers resolves on the core.

- Scene 1 (0.0–~1.5s): `[bg]` (dark/space field, optionally slow-drifting diffused gradient blobs). `[primary nodes]` (circles carrying `[icon]` + label) SPRING-POP in (scale 0→1, ~1.15 elastic overshoot, staggered) arranged in a wide ring/cluster around an empty or marked center `[hub]`.
- Scene 2 (~0.7–2.5s, overlapping): smaller `[secondary nodes]` (platform / partner-logo chips) pop in staggered with the same elastic spring, filling the gaps; optional thin `[accent]` connector lines / orbit ring draw from hub→nodes. Camera holds.
- Scene 3 (~2.5–Xs, the resolve): see finisher variant below; lands and HOLDS on the magnified / orbited center to the end.

- Variant — Hook (push-in finisher): from Scene 3, a continuous smooth CAMERA PUSH-IN toward the center inner cluster — inner nodes scale up and stay sharp while outer nodes are pushed toward the edges and progressively BLUR (depth-of-field), background scales up smoothly; holds magnified on the core.
- Variant — Social_Proof (orbit finisher): the center `[brand mark]` snaps in via a quick 3D rotate that decelerates and settles; a thin `[accent]` orbit ring draws around it; `[N partner badges]` spring onto the ring (staggered overshoot) and revolve CLOCKWISE while staying upright, under a continuous slow camera ZOOM-OUT (ecosystem reveal).
- Variant — Social_Proof (optional type-push-through opener, prepended before Scene 1): centered `[headline]` types/slides in with a huge transparent-fill OUTLINE copy of the same words behind it; the outline text scales up exponentially toward camera (high-speed dolly / push-through), breaches the frame, then HARD-CUTS to the hub bg of Scene 1.
- Variant — Social_Proof (scatter-drift finisher, no ring): the center is a two-line serif
  `[headline]` building in place (not a mark); `[~20 app icons]` pop in SCATTERED across the whole
  frame in a quick stagger — no ring geometry, no connectors — then sustain a very slow outward
  drift to the end. Camera fully static: no push-in, no zoom-out; the "everything around one
  center" reads from the drift vectors pointing away from the headline. Often chained as the end
  card of a preceding UI beat (the prior card dissolves into it).

**motion vocabulary**: staggered elastic spring-pop node entrances (~1.15 overshoot); slow gradient-blob drift; connector-line / orbit-ring draw-on; 3D snap-rotate-settle on the hub mark; continuous camera push-in (inner sharp, outer depth-of-field blur, bg scale-up); clockwise orbital revolve of upright badges; continuous slow camera zoom-out (ecosystem reveal); optional outline-text push-through dolly entry. Scatter-drift finisher: frame-wide scattered icon pop-in (staggered, no ring); sustained slow
outward icon drift; in-place two-line serif headline build; static-frame hold to the end.

**rule mapping** (motion verb → `rules/<id>.md`)

- staggered spring-pop node entrances → `spring-pop-entrance` (elastic overshoot) + `gsap-effects` (stagger recipe); 3D-flip-in flavor → `orbit-3d-entry`
- ring / cluster layout of nodes around a center → `avatar-cloud-network` (nodes on an elliptical ring + SVG lines to a center)
- icons on the nodes → `svg-icon-enrichment`
- connector lines hub→node → `svg-path-draw`
- orbit-ring draw-on → `svg-path-draw`
- slow gradient-blob drift → `sine-wave-loop` (idle looped drift)
- 3D snap-rotate-settle on hub mark → `orbit-3d-entry` (3D-flip entry); technique CSS-3D
- clockwise orbital revolve of upright badges → `orbit-3d-entry` (continuous elliptical orbit); technique MotionPath
- camera push-in toward center → `multi-phase-camera` (PUSH-in) + `coordinate-target-zoom` (target the core)
- background scale-up during push-in → `multi-phase-camera`
- continuous slow zoom-out (ecosystem reveal) → `multi-phase-camera` (pull-back) / `coordinate-target-zoom`
- outline-text push-through dolly opener (Social_Proof) → `3d-text-depth-layers` (outline copy behind) + `multi-phase-camera` (push-through)
- depth-of-field blur on outer nodes during push-in → `depth-of-field-blur` (progressive DOF/focus-falloff blur on the off-center outer nodes while the inner core stays sharp)
- frame-wide scattered icon pop-in (no ring) → `spring-pop-entrance` (staggered group) +
  `gsap-effects` (stagger recipe); positions pre-baked scattered — NOT `avatar-cloud-network`'s
  elliptical ring
- sustained slow outward icon drift → `center-outward-expansion` (outward vectors, slow sustained
  register — drift targets sit slightly past the pop-in positions)
- in-place serif headline build → `gsap-effects` (staggered line/word reveal)

**camera modifier**: push-in-with-DOF (Hook) — `multi-phase-camera` PUSH-in targeted via `coordinate-target-zoom` onto the core; the focus-falloff blur half of it is backed by `depth-of-field-blur`. Orbit finisher (Social_Proof) — slow continuous zoom-out via `multi-phase-camera` (pull-back) while satellites revolve. Scatter-drift finisher (Social_Proof end card) — none: the frame never moves; the outward drift
is element-level.

## Selected motion rule: avatar-cloud-network

---
name: avatar-cloud-network
description: Avatars distributed on an elliptical ring connected by SVG dashed lines to a center hub — social proof "community" reveal with staggered entry.
metadata:
  tags: avatar, cloud, network, social-proof, ellipse, connection, stagger
---

# Avatar Cloud Network

Avatars on an elliptical ring around a central hub (logo / counter), with SVG dashed lines drawing outward from the hub to each avatar — "community" / social proof. Distinct from [orbit-3d-entry.md](orbit-3d-entry.md) (continuous orbit): this settles into a static composed formation.

## How It Works

Three layers: SVG lines (z-index 1, behind), avatars (z-index 2), hub (z-index 5 — lines terminate AT its edge, never pass through). Avatar positions and lines are built once at setup from ONE shared center; the timeline then runs hub fade → avatar cascade → outward line draw → breathing dwell. Drawing FROM the center is the narrative: "the hub connects to its community."

## Recipe

```html
<!-- inside a standard scene clip (hyperframes-core) -->
<svg class="lines" viewBox="0 0 1920 1080"><!-- lines injected --></svg>
<div class="hub-wrap">
  <div class="hub">{counterValue} {counterLabel}</div>
  <!-- avatars injected -->
</div>
```

```css
.lines {
  position: absolute;
  inset: 0;
  z-index: 1;
  pointer-events: none;
}
.hub-wrap {
  position: absolute;
  inset: 0;
  display: grid;
  place-items: center;
}
.hub {
  position: relative;
  z-index: 5;
}
.avatar {
  position: absolute;
  z-index: 2;
  transform: translate(-50%, -50%); /* centers on the (left, top) the script sets */
  will-change: transform, opacity;
}
```

```js
// CENTER_X/Y must equal the hub's RENDERED center exactly — every avatar
// position and line endpoint derives from it. For a place-items:center hub on
// a 1920×1080 canvas: (W/2, H × CENTER_Y_FACTOR).
const C = { x: CENTER_X, y: CENTER_Y };
const wrap = document.querySelector(".hub-wrap");
const svg = document.querySelector(".lines");

for (let i = 0; i < AVATAR_COUNT; i++) {
  const a = (i / AVATAR_COUNT) * Math.PI * 2 - Math.PI / 2; // start at top
  const x = C.x + Math.cos(a) * RADIUS_X;
  const y = C.y + Math.sin(a) * RADIUS_Y;

  const av = document.createElement("div");
  av.className = "avatar"; // assign image / glyph from authoring data
  av.style.left = `${x}px`;
  av.style.top = `${y}px`;
  wrap.appendChild(av);

  const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
  const attrs = {
    x1: C.x,
    y1: C.y,
    x2: x,
    y2: y,
    stroke: "{lineColor}",
    "stroke-dasharray": "6 8",
  };
  Object.entries(attrs).forEach(([k, v]) => line.setAttribute(k, String(v)));
  const len = Math.hypot(x - C.x, y - C.y); // straight line — Math.hypot, not getTotalLength()
  line.style.strokeDashoffset = String(len);
  svg.appendChild(line);
}

tl.from(".hub", { opacity: 0, scale: 0.8, duration: HUB_DUR, ease: `back.out(${HUB_BOUNCE})` }, 0);

const avatars = document.querySelectorAll(".avatar");
avatars.forEach((av, i) => {
  tl.from(
    av,
    { opacity: 0, scale: 0, duration: AVATAR_DUR, ease: `back.out(${AVATAR_BOUNCE})` },
    AVATAR_AT + i * AVATAR_STAGGER,
  );
});
svg.querySelectorAll("line").forEach((line, i) => {
  tl.to(
    line,
    { strokeDashoffset: 0, duration: LINE_DUR, ease: "power2.out" },
    LINES_AT + i * LINE_STAGGER,
  );
});

// Climax dwell — out-of-phase breathing holds the eye on the formed network:
// one phase proxy (0 → 2π·BREATH_CYCLES, ease "none"); onUpdate scales avatar i by
// 1 + sin(p + (i/n)·2π) · BREATH_AMP — sine-wave-loop's multiplicative onUpdate form.
// Keep the -50% centering in the same transform write.
```

## Variations

- **Size variety**: vary avatar sizes by a small index-keyed array so the ring doesn't read rigidly repetitive.
- **Solid lines**: drop the dash + draw; lines fade in via opacity — more corporate, less networky.
- **Multi-orbit**: inner ring (fewer, larger) connected to the hub; outer ring is an unconnected "halo."
- **Glyph avatars**: flags / emoji / icons instead of faces — reads "global community" or role spread.

## Values

| token          | range                        | notes                                                            |
| -------------- | ---------------------------- | ---------------------------------------------------------------- |
| AVATAR_COUNT   | 8–12                         | fewer feels sparse; more clutters the ellipse                    |
| RADIUS_X / \_Y | ~20–30% W / ~18–25% H        | ratio X/Y 1.5–3.0 reads as perspective; 1 (circle) reads flat    |
| avatar size    | 80–120px @1920               | ring must fit 10+ without overlap                                |
| HUB_DUR        | 0.4–0.6s                     | HUB_BOUNCE 1.4–1.8                                               |
| AVATAR_AT      | ≥ 0.6 × HUB_DUR              | hub established before satellites arrive                         |
| AVATAR_DUR     | 0.4–0.7s                     | AVATAR_BOUNCE 1.4–1.8, slightly firmer than hub                  |
| AVATAR_STAGGER | 0.06–0.10s                   | cascade reads "joining"; simultaneous reads "already there"      |
| LINES_AT       | overlaps last avatar settle  | start ~0.1–0.2s before it — draw reads as consequence of landing |
| LINE_DUR       | 0.4–0.7s                     | LINE_STAGGER 0.02–0.05s = a wave outward                         |
| BREATH_CYCLES  | 1.0–2.0 over the remaining s | under 1 = single sigh; over 2 = anxious. BREATH_AMP 0.02–0.06    |

Tokens: dark `{bgColor}` so the cloud reads as a constellation; translucent accent `{lineColor}`; soft border + glow keeps avatars legible on dark.

## Critical Constraints

- **CENTER_X/Y must match the hub's actual rendered center** — when composed with another scene (e.g. a recentered logo), bake them from the same source as the hub's final position, or lines visibly miss the hub.
- **Hub z-index above lines** — lines terminate at the hub edge, never cross it.
- **Lines draw outward** (dashoffset len → 0), starting after avatars are mostly settled.
- **`RADIUS_X > RADIUS_Y`** — a horizontal ellipse reads as perspective; a circle reads flat.
- **Climax dwell ≥ 1s** after lines complete so the formed network is readable.
- Straight lines: `Math.hypot` for length — `getTotalLength()` not needed.

## See also

`counting-dynamic-scale` (the hub IS a growing counter) · `sine-wave-loop` (the breathing form) · `orbit-3d-entry` (the continuously-orbiting cousin).

## Selected motion rule: orbit-3d-entry

---
name: orbit-3d-entry
description: Elements flip in from 3D space then settle into continuous elliptical orbit around a focal point.
metadata:
  tags: orbit, 3d, flip, ellipse, circular, icon, entry, continuous
---

# Orbit with 3D Entry

Elements flip in from 3D space (`rotateX` + `rotateY` + negative `z`) then settle into a continuous elliptical orbit around a center label. Distinct from one-shot reveals — the orbit keeps running, driven by a 0→1 progress tween INSIDE the timeline (never rAF).

## How It Works

Per element, two phases: (1) a `back.out` flip from a hidden 3D orientation to flat — **in place at its orbital starting position** (see Critical Constraints); (2) a continuous orbit where `onUpdate` computes `x/y` from `cos/sin(initialAngle + p·2π)` on the ellipse. The stage needs `perspective` on the scene root and `preserve-3d` on stage + items, or the flip flattens to a 2D scale.

## Recipe

```html
<!-- inside a standard scene clip (hyperframes-core) -->
<div class="orbit-stage">
  <div class="orbit-item" data-angle="0">{glyph1}</div>
  <div class="orbit-item" data-angle="60">{glyph2}</div>
  <!-- … evenly-spaced angles … -->
  <div class="orbit-center">{centerLabel}</div>
</div>
```

```css
.scene-root {
  display: grid;
  place-items: center;
  perspective: 1800px; /* REQUIRED */
}
.orbit-stage {
  position: relative;
  display: grid;
  place-items: center;
  transform-style: preserve-3d;
}
.orbit-item {
  position: absolute;
  top: 50%;
  left: 50%;
  transform-style: preserve-3d;
  will-change: transform;
}
.orbit-center {
  position: relative;
  transform: translateZ(220px); /* wins paint order inside preserve-3d */
  z-index: 9999;
}
```

```js
const items = document.querySelectorAll(".orbit-item");
const RADIUS_Y = RADIUS_X * Y_TO_X_RATIO; // perspective-flattened ellipse

items.forEach((el, i) => {
  const a0 = (Number(el.dataset.angle) / 360) * Math.PI * 2;
  const startX = Math.cos(a0) * RADIUS_X;
  const startY = Math.sin(a0) * RADIUS_Y;

  // 1) Park at the orbital position, hidden — BEFORE any tween fires
  gsap.set(el, {
    xPercent: -50,
    yPercent: -50,
    x: startX,
    y: startY,
    rotateX: ROTATE_X_FROM,
    rotateY: ROTATE_Y_FROM,
    z: Z_FROM,
    opacity: 0,
    scale: SCALE_FROM,
  });

  // 2) Flip in IN PLACE — rotation/opacity/scale only, never translate
  tl.to(
    el,
    {
      rotateX: 0,
      rotateY: 0,
      z: 0,
      opacity: 1,
      scale: 1,
      duration: ENTRY_DUR,
      ease: `back.out(${FLIP_BACK})`,
    },
    i * STAGGER,
  );

  // 3) Continuous orbit — each item gets its OWN progress tween (own initialAngle)
  const orbit = { p: 0 };
  tl.to(
    orbit,
    {
      p: 1,
      duration: ORBIT_DURATION,
      ease: "none",
      onUpdate: () => {
        const a = a0 + orbit.p * Math.PI * 2;
        const x = Math.cos(a) * RADIUS_X;
        const y = Math.sin(a) * RADIUS_Y;
        // capped z-index band [1, 50] — see center-label clearance below
        el.style.zIndex = String(1 + Math.round(((y + RADIUS_Y) / (2 * RADIUS_Y)) * 49));
        el.style.transform = `translate(-50%, -50%) translate(${x}px, ${y}px)`;
      },
    },
    i * STAGGER + ENTRY_DUR,
  );
});

tl.from(
  ".orbit-center",
  { opacity: 0, scale: 0.6, duration: ENTRY_DUR, ease: `back.out(${CENTER_BACK})` },
  CENTER_FADE_AT,
);
```

## Variations

- **Collapse to center**: a final 1→0 driver multiplies both radii (and item scale) in `onUpdate` — the ring condenses into the center element; pairs with a CTA "click" igniting the collapse.
- **Tilted orbit plane**: `rotateX(25deg)` on `.orbit-stage` — items visibly arc through the plane.

## Values

| token                   | range                         | notes                                                               |
| ----------------------- | ----------------------------- | ------------------------------------------------------------------- |
| RADIUS_X                | 300–900px                     | must also clear the center label horizontally (see below)           |
| Y_TO_X_RATIO            | 0.4–0.7                       | keep < 1 — a tilted ring, not a frontal halo                        |
| ORBIT_DURATION          | 4–25s per revolution          | ≥ time on screen, or the tween ends and items freeze                |
| ENTRY_DUR               | 0.4–0.8s                      |                                                                     |
| STAGGER                 | 0.06–0.12s                    | below reads "popcorn", above reads plodding                         |
| FLIP_BACK / CENTER_BACK | 1.2–2.0 / 1.2–1.8             | calm the center pop if both fire close together                     |
| CENTER_FADE_AT          | after 2–4 items land          | too early competes; too late leaves a hole                          |
| ROTATE_X/Y_FROM, Z_FROM | ±60–120°, ±45–120°, −200…−400 | one consistent rotation direction across items; mixed signs = noise |
| SCALE_FROM              | 0.2–0.6                       |                                                                     |
| item count              | 4–12                          | fewer feels empty, more crowds the center                           |

## Critical Constraints

- **❗ Entry must flip IN PLACE at the orbital position, NOT at center** — `gsap.set` each item at `(cos(a0)·RADIUS_X, sin(a0)·RADIUS_Y)` with `opacity: 0` BEFORE adding tweens, then phase 1 animates only rotation/opacity/scale. A fromTo that keeps `x/y: 0` flips at the stage center, collides with the center label, then teleports to the orbit when phase 2 starts.
- **❗ Center-label clearance** — `z-index` alone is unreliable inside `preserve-3d` (paint order follows actual Z): push the label forward with `translateZ(220px)` + `z-index: 9999`, cap item z-index to `[1, 50]`, AND size the ring so items clear the label horizontally at every angle: `RADIUS_X × min|cos(θ)| ≥ L_w + I_w + breathing_room` (label/item half-widths; for 6 items the worst case is `cos(30°) ≈ 0.866`). A heavier wordmark needs a wider ring.
- **Each item gets its OWN orbit tween** — a shared `targets: ".orbit-item"` tween can't carry per-item `initialAngle`.
- **The center element is the headline** — the orbit is ornament; if it dominates, grow the center or fade the items down.

## See also

`center-outward-expansion` (burst entry; reversed driver = the collapse finish) · `cursor-click-ripple` (the click that triggers a collapse) · `depth-scatter-assemble` (3D entrance that resolves flat instead of orbiting).
