import React from "react";
import { AbsoluteFill, Interactive, useCurrentFrame } from "remotion";
import { Orbit, Turntable, View } from "../components/Rig";
import { ANTON, CAIRO, ci, INOUT, MONO, OUT, shake } from "../theme";

const CX = 540;
const CY = 1150;
const SPIN: View[] = [
  { name: "lateral", width: 900 },
  { name: "heels", width: 640 },
  { name: "medial", width: 900 },
  { name: "lateral", width: 900 },
];

/** Spiral flight path into the frame (0..24). */
const spiral = (f: number) => {
  const e = ci(f, [0, 24], [0, 1], OUT);
  const th = (1 - e) * Math.PI * 2.4;
  const r = (1 - e) * 950;
  return {
    x: Math.cos(th + 0.6) * r,
    y: Math.sin(th + 0.6) * r * 0.8,
    s: 0.15 + 0.85 * e,
    rot: (1 - e) * 540 - 4,
    e,
  };
};

/** 60–150 (90f): spiral entry, orbit rings, giant title, Arabic subtitle, full 540° turntable. */
export const Reveal: React.FC = () => {
  const f = useCurrentFrame();
  const sp = spiral(f);
  const sk = shake(f, 22, 10, 16);
  const spinAngle = ci(f, [56, 84], [0, 540], INOUT);
  const spinVel = Math.abs(ci(f + 1, [56, 84], [0, 540], INOUT) - spinAngle);
  const bob = Math.sin(f / 13) * 12;
  const ringDraw = ci(f, [18, 38], [0, 1], OUT);

  const lines = [
    { t: "JOKER", stroke: false, d: 14 },
    { t: "2 GT", stroke: true, d: 18 },
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
                scale: ci(f, [0, 90], [1.0, 1.08]),
              }}
            >
              {l.t}
            </div>
          </div>
        ))}
      </AbsoluteFill>

      <Orbit frame={f} layer="back" cx={CX} cy={CY + 40} rx={580} ry={130} tilt={-9} speed={0.07} draw={ringDraw} />
      <Orbit frame={f} layer="back" cx={CX} cy={CY + 20} rx={500} ry={210} tilt={14} speed={-0.05} draw={ringDraw} seed={2} opacity={0.6} />

      {/* Ghost trail along the spiral */}
      {f < 26
        ? [6, 4, 2].map((k) => {
            const g = spiral(f - k);
            return (
              <Turntable
                key={k}
                views={SPIN}
                angle={0}
                cx={CX + g.x}
                cy={CY + g.y}
                glow={0}
                extra={{ scale: g.s, rotate: `${g.rot}deg`, opacity: 0.18 * (1 - sp.e) + 0.05, filter: "blur(6px)" }}
              />
            );
          })
        : null}

      <Turntable
        views={SPIN}
        angle={spinAngle}
        cx={CX + sp.x}
        cy={CY + sp.y + bob}
        blur={Math.min(14, spinVel * 0.5) + (1 - sp.e) * 10}
        sweep={ci(f, [26, 54], [0, 1])}
        extra={{ scale: sp.s * ci(f, [24, 90], [1, 1.06]), rotate: `${sp.rot + Math.sin(f / 17) * 1.5}deg` }}
      />

      <Orbit frame={f} layer="front" cx={CX} cy={CY + 40} rx={580} ry={130} tilt={-9} speed={0.07} draw={ringDraw} />
      <Orbit frame={f} layer="front" cx={CX} cy={CY + 20} rx={500} ry={210} tilt={14} speed={-0.05} draw={ringDraw} seed={2} opacity={0.6} />

      <Interactive.Div
        name="Subtitle"
        style={{ position: "absolute", bottom: 190, left: 0, right: 0, textAlign: "center" }}
      >
        <div
          style={{
            fontFamily: MONO,
            fontWeight: 700,
            fontSize: 40,
            color: "#9cc4ff",
            letterSpacing: ci(f, [26, 60], [40, 16], OUT),
            opacity: ci(f, [26, 34], [0, 1]),
          }}
        >
          “ARTEMIS”
        </div>
        <div style={{ overflow: "hidden" }}>
          <div
            style={{
              fontFamily: CAIRO,
              fontWeight: 900,
              fontSize: 120,
              lineHeight: 1.35,
              color: "white",
              direction: "rtl",
              translate: `0px ${ci(f, [30, 44], [170, 0], OUT)}px`,
            }}
          >
            إصدار أرتميس
          </div>
        </div>
      </Interactive.Div>
    </AbsoluteFill>
  );
};
