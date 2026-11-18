import React from "react";
import { AbsoluteFill, Img, Interactive, random, staticFile, useCurrentFrame } from "remotion";
import { Orbit } from "../components/Rig";
import { ShoeStage } from "../components/Shoe3D";
import { ANTON, CAIRO, ci, IN, INTER, OUT, shake } from "../theme";

const HIT = 15; // local frame of the impact (abs 795 = 26.5s, synced to the boom)
const CX = 540;
const CY = 1110;

const STREAKS = new Array(90).fill(0).map((_, i) => ({
  a: random(`fa${i}`) * Math.PI * 2,
  r0: 900 + random(`fr${i}`) * 900,
  delay: random(`fd${i}`) * 6,
  len: 60 + random(`fl${i}`) * 200,
}));

const SPARKS = new Array(80).fill(0).map((_, i) => ({
  a: random(`sa${i}`) * Math.PI * 2,
  v: 14 + random(`sv${i}`) * 46,
  size: 3 + random(`sz${i}`) * 9,
  life: 18 + random(`sl${i}`) * 30,
}));

/** 780–900 (120f): energy implodes, explodes, shoe orbits above the planet; Arabic end card. */
export const Finale: React.FC = () => {
  const f = useCurrentFrame();
  const t = f - HIT;
  const sk = shake(f, HIT, 14, 30);
  const title = "JOKER 2 GT".split("");
  const ringDraw = ci(t, [4, 26], [0, 1], OUT);

  return (
    <AbsoluteFill style={{ translate: `${sk.x}px ${sk.y}px`, scale: ci(f, [HIT, 120], [1, 1.05]) }}>
      {/* readability gradient over the planet */}
      <AbsoluteFill
        style={{ background: "linear-gradient(180deg, rgba(0,0,0,0) 72%, rgba(0,0,0,0.75) 100%)" }}
      />

      {/* Implosion: streaks pulled into the centre */}
      {t < 0 ? (
        <svg width={1080} height={1920} style={{ position: "absolute", inset: 0 }}>
          {STREAKS.map((s, i) => {
            const p = ci(f, [s.delay, HIT], [0, 1], IN);
            const r = s.r0 * (1 - p);
            const r2 = r + s.len * (1 - p * 0.6);
            const a = s.a + p * 1.2; // swirl inwards
            return (
              <line
                key={i}
                x1={CX + Math.cos(a) * r}
                y1={CY + Math.sin(a) * r}
                x2={CX + Math.cos(a - 0.15) * r2}
                y2={CY + Math.sin(a - 0.15) * r2}
                stroke={i % 3 ? "white" : "#9cc4ff"}
                strokeWidth={3}
                strokeLinecap="round"
                opacity={ci(f, [s.delay, s.delay + 3], [0, 0.9])}
              />
            );
          })}
          <circle
            cx={CX}
            cy={CY}
            r={ci(f, [0, HIT], [900, 10], IN)}
            fill="none"
            stroke="white"
            strokeWidth={ci(f, [0, HIT], [2, 10])}
            opacity={0.7}
          />
          <circle cx={CX} cy={CY} r={ci(f, [6, HIT], [0, 60], IN)} fill="white" opacity={0.9} />
        </svg>
      ) : null}

      {/* Shockwaves + sparks */}
      {t >= 0 ? (
        <svg width={1080} height={1920} style={{ position: "absolute", inset: 0, overflow: "visible" }}>
          {[0, 4, 9].map((d) => (
            <circle
              key={d}
              cx={CX}
              cy={CY}
              r={ci(t - d, [0, 24], [40, 1500], OUT)}
              fill="none"
              stroke={d === 4 ? "#9cc4ff" : "white"}
              strokeWidth={ci(t - d, [0, 24], [16, 1])}
              opacity={t >= d ? ci(t - d, [0, 24], [0.9, 0]) : 0}
            />
          ))}
          {SPARKS.map((s, i) => {
            const k = Math.min(t, s.life);
            const dist = s.v * k * (1 - k / (s.life * 2));
            return (
              <circle
                key={i}
                cx={CX + Math.cos(s.a) * dist}
                cy={CY + Math.sin(s.a) * dist * 0.75}
                r={s.size * (1 - k / s.life) + 0.5}
                fill={i % 4 ? "white" : "#9cc4ff"}
                opacity={ci(t, [0, s.life], [1, 0])}
              />
            );
          })}
        </svg>
      ) : null}

      {t >= 0 ? (
        <>
          <Orbit frame={f} layer="back" cx={CX} cy={CY + 30} rx={560} ry={120} tilt={-8} speed={0.06} draw={ringDraw} />
          <ShoeStage
            items={[
              {
                name: "lateral",
                width: 860 * ci(t, [0, 14], [1.35, 1], OUT),
                x: CX,
                y: CY + Math.sin(t / 14) * 12,
                rx: 10 + Math.sin(t / 30) * 5,
                ry: ci(t, [0, 18], [-70, 0], OUT) + Math.sin(t / 22) * 22 * ci(t, [8, 30], [0, 1]),
                rz: ci(t, [0, 16], [-15, -3], OUT),
                sweep: ci(t, [12, 70], [-0.2, 1.3]),
                flare: ci(t, [0, 10], [0.35, 0]),
              },
            ]}
            light={[-0.5 + 0.5 * Math.sin(t / 35), 0.6, 0.65]}
            style={{ filter: t < 10 ? `blur(${ci(t, [0, 10], [14, 0])}px)` : undefined }}
          />
          <Orbit frame={f} layer="front" cx={CX} cy={CY + 30} rx={560} ry={120} tilt={-8} speed={0.06} draw={ringDraw} />
        </>
      ) : null}

      {/* Logo lockup (cropped from official artwork, unaltered) */}
      <Img
        src={staticFile("logo.png")}
        style={{
          position: "absolute",
          width: 380,
          left: 350,
          top: 140,
          opacity: ci(t, [12, 22], [0, 1]),
          scale: ci(t, [12, 26], [1.25, 1], OUT),
          filter: `blur(${ci(t, [12, 20], [10, 0])}px)`,
        }}
      />

      {/* Title */}
      <AbsoluteFill style={{ top: 380, alignItems: "center" }}>
        <div style={{ display: "flex", overflow: "hidden", paddingTop: 8 }}>
          {title.map((c, i) => (
            <span
              key={i}
              style={{
                fontFamily: ANTON,
                fontSize: 180,
                lineHeight: 1.05,
                color: "white",
                whiteSpace: "pre",
                display: "inline-block",
                translate: `0px ${ci(t, [4 + i * 1.5, 16 + i * 1.5], [220, 0], OUT)}px`,
                rotate: `${ci(t, [4 + i * 1.5, 16 + i * 1.5], [20, 0], OUT)}deg`,
              }}
            >
              {c}
            </span>
          ))}
        </div>
        <Interactive.Div
          name="Artemis"
          style={{
            fontFamily: INTER,
            fontWeight: 800,
            fontSize: 88,
            color: "white",
            marginTop: 0,
            letterSpacing: ci(t, [14, 45], [60, 14], OUT),
            opacity: ci(t, [14, 24], [0, 1]),
            filter: `blur(${ci(t, [14, 24], [12, 0])}px)`,
          }}
        >
          “ARTEMIS”
        </Interactive.Div>
      </AbsoluteFill>

      {/* Arabic CTA */}
      <AbsoluteFill style={{ top: 1640, alignItems: "center" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 30, opacity: ci(t, [24, 32], [0, 1]) }}>
          <div style={{ height: 3, background: "white", width: ci(t, [24, 40], [0, 140], OUT) }} />
          <div
            style={{
              fontFamily: CAIRO,
              fontWeight: 900,
              fontSize: 92,
              lineHeight: 1.4,
              color: "white",
              direction: "rtl",
              scale: ci(t, [24, 34], [1.3, 1], OUT),
            }}
          >
            صار متوفّر
          </div>
          <div style={{ height: 3, background: "white", width: ci(t, [24, 40], [0, 140], OUT) }} />
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
