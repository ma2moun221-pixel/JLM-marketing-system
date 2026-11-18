import React from "react";
import { AbsoluteFill, Interactive, useCurrentFrame } from "remotion";
import { Orbit } from "../components/Rig";
import { ShoeItem, ShoeStage, turn } from "../components/Shoe3D";
import { ANTON, CAIRO, ci, INOUT, MONO, OUT, shake } from "../theme";

const CX = 540;
const CY = 1150;

/** Spiral flight path into the frame (0..30). */
const spiral = (f: number) => {
  const e = ci(f, [0, 30], [0, 1], OUT);
  const th = (1 - e) * Math.PI * 2.4;
  const r = (1 - e) * 950;
  return { x: Math.cos(th + 0.6) * r, y: Math.sin(th + 0.6) * r * 0.8, s: 0.15 + 0.85 * e, rz: (1 - e) * 360, e };
};

/** 90–270 (180f): spiral entry, 3D sway, orbit rings, title, then 3D turns to the heel and the other side. */
export const Reveal: React.FC = () => {
  const f = useCurrentFrame();
  const sp = spiral(f);
  const sk = shake(f, 28, 10, 16);
  const bob = Math.sin(f / 15) * 12;
  const ringDraw = ci(f, [26, 50], [0, 1], OUT);
  const sway = Math.sin((f - 30) / 20) * 30 * ci(f, [26, 46], [0, 1]);

  const lateral: ShoeItem = {
    name: "lateral",
    width: 860 * sp.s,
    x: CX + sp.x,
    y: CY + sp.y + bob,
    rx: 10 + Math.sin(f / 27) * 6,
    ry: (1 - sp.e) * -90 + sway,
    rz: sp.rz - 3,
    sweep: ci(f, [40, 100], [-0.2, 1.3]),
  };
  const heels: ShoeItem = { name: "heels", width: 600, x: CX, y: CY + bob, rx: 8, ry: Math.sin(f / 14) * 14 };
  const medial: ShoeItem = {
    name: "medial",
    width: 860,
    x: CX,
    y: CY + bob,
    rx: 10,
    ry: ci(f, [164, 180], [0, -14]),
    rz: 3,
    sweep: ci(f, [164, 180], [-0.2, 0.6]),
  };

  let items: ShoeItem[] = [lateral];
  let blur = (1 - sp.e) * 8;
  let flare = 0;
  const t1 = ci(f, [120, 136], [0, 1], INOUT);
  const t2 = ci(f, [148, 164], [0, 1], INOUT);
  if (f >= 120 && f <= 136) {
    const r = turn(t1, lateral, heels);
    items = r.items;
    blur = r.blur;
    flare = r.flare;
  } else if (f > 136 && f < 148) {
    items = [heels];
  } else if (f >= 148 && f <= 164) {
    const r = turn(t2, heels, medial);
    items = r.items;
    blur = r.blur;
    flare = r.flare;
  } else if (f > 164) {
    items = [medial];
  }
  items = items.map((it) => ({ ...it, flare }));

  const lines = [
    { t: "JOKER", stroke: false, d: 20 },
    { t: "2 GT", stroke: true, d: 26 },
  ];

  return (
    <AbsoluteFill style={{ translate: `${sk.x}px ${sk.y}px` }}>
      {/* Giant type behind */}
      <AbsoluteFill style={{ alignItems: "center", top: 250 }}>
        {lines.map((l) => (
          <div key={l.t} style={{ overflow: "hidden", height: 350 }}>
            <div
              style={{
                fontFamily: ANTON,
                fontSize: 340,
                lineHeight: 0.98,
                letterSpacing: 6,
                color: l.stroke ? "transparent" : "rgba(255,255,255,0.14)",
                WebkitTextStroke: l.stroke ? "3px rgba(200,220,255,0.95)" : "3px rgba(255,255,255,0.4)",
                translate: `0px ${ci(f, [l.d, l.d + 14], [340, 0], OUT)}px`,
                scale: ci(f, [0, 180], [1.0, 1.1]),
              }}
            >
              {l.t}
            </div>
          </div>
        ))}
      </AbsoluteFill>

      <Orbit frame={f} layer="back" cx={CX} cy={CY + 40} rx={580} ry={130} tilt={-9} speed={0.06} draw={ringDraw} />
      <Orbit frame={f} layer="back" cx={CX} cy={CY + 20} rx={500} ry={210} tilt={14} speed={-0.045} draw={ringDraw} seed={2} opacity={0.6} />

      <ShoeStage
        items={items}
        light={[-0.5 + 0.4 * Math.sin(f / 40), 0.6, 0.65]}
        style={{ filter: blur > 0.3 ? `blur(${blur}px)` : undefined }}
      />

      <Orbit frame={f} layer="front" cx={CX} cy={CY + 40} rx={580} ry={130} tilt={-9} speed={0.06} draw={ringDraw} />
      <Orbit frame={f} layer="front" cx={CX} cy={CY + 20} rx={500} ry={210} tilt={14} speed={-0.045} draw={ringDraw} seed={2} opacity={0.6} />

      <Interactive.Div name="Subtitle" style={{ position: "absolute", bottom: 170, left: 0, right: 0, textAlign: "center" }}>
        <div
          style={{
            fontFamily: MONO,
            fontWeight: 700,
            fontSize: 40,
            color: "#9cc4ff",
            letterSpacing: ci(f, [34, 80], [40, 16], OUT),
            opacity: ci(f, [34, 42], [0, 1]),
          }}
        >
          “ARTEMIS”
        </div>
        <div style={{ overflow: "hidden" }}>
          <div
            style={{
              fontFamily: CAIRO,
              fontWeight: 900,
              fontSize: 124,
              lineHeight: 1.35,
              color: "white",
              direction: "rtl",
              translate: `0px ${ci(f, [38, 52], [170, 0], OUT)}px`,
            }}
          >
            نسخة أرتميس
          </div>
        </div>
      </Interactive.Div>
    </AbsoluteFill>
  );
};
