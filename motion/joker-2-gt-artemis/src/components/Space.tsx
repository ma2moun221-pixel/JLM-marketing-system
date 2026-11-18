import React from "react";
import { AbsoluteFill, Img, random, staticFile, useCurrentFrame } from "remotion";
import { ci, H, IN, W } from "../theme";

const STARS = new Array(150).fill(0).map((_, i) => ({
  x: random(`x${i}`) * W,
  y: random(`y${i}`) * H,
  s: 1 + random(`s${i}`) * 2.6,
  tw: random(`t${i}`) * Math.PI * 2,
  depth: 0.3 + random(`d${i}`) * 0.7,
}));

/** Global space backdrop: moon plate, orbit lines, stars with warp streaks. */
export const Space: React.FC = () => {
  const frame = useCurrentFrame();
  // warp from frame 40 to 60 (into first impact)
  const warp = frame < 60 ? ci(frame, [38, 60], [0, 1], IN) : 0;
  const moonOpacity = frame < 55 ? 0 : ci(frame, [55, 70], [0, 1]) * (frame >= 150 && frame < 285 ? 0.45 : 1);
  const orbitDraw = ci(frame, [0, 50], [1, 0]);

  return (
    <AbsoluteFill style={{ backgroundColor: "#050505", overflow: "hidden" }}>
      {/* Moon */}
      <Img
        src={staticFile("moon.png")}
        style={{
          position: "absolute",
          width: 1700,
          left: -310,
          top: ci(frame, [55, 450], [-40, 30]),
          opacity: moonOpacity,
          scale: ci(frame, [55, 450], [1.08, 1]),
        }}
      />
      {/* Orbit rings */}
      <svg width={W} height={H} style={{ position: "absolute", inset: 0 }}>
        {new Array(11).fill(0).map((_, i) => {
          const r = 180 + i * 150;
          const c = 2 * Math.PI * r;
          const ang = frame * (0.18 - i * 0.012);
          return (
            <g key={i} style={{ rotate: `${ang}deg`, transformOrigin: "120px 1250px" }}>
              <circle
                cx={120}
                cy={1250}
                r={r}
                fill="none"
                stroke="white"
                strokeOpacity={0.13}
                strokeWidth={1.4}
                strokeDasharray={c}
                strokeDashoffset={c * orbitDraw}
              />
              <circle
                cx={120 + r * Math.cos(i * 1.7)}
                cy={1250 + r * Math.sin(i * 1.7)}
                r={i % 3 === 0 ? 5 : 3}
                fill="white"
                opacity={0.7 * (1 - orbitDraw)}
              />
            </g>
          );
        })}
      </svg>
      {/* Stars / warp streaks */}
      {STARS.map((s, i) => {
        const cx = W / 2;
        const cy = H / 2;
        const ang = Math.atan2(s.y - cy, s.x - cx);
        const push = warp * warp * 900 * s.depth;
        const x = s.x + Math.cos(ang) * push;
        const y = s.y + Math.sin(ang) * push - frame * 0.4 * s.depth;
        const len = s.s + warp * 260 * s.depth;
        const tw = 0.45 + 0.55 * Math.abs(Math.sin(frame / 9 + s.tw));
        return (
          <div
            key={i}
            style={{
              position: "absolute",
              left: x,
              top: ((y % H) + H) % H,
              width: len,
              height: s.s,
              borderRadius: s.s,
              background: "white",
              opacity: tw * (0.4 + 0.6 * s.depth),
              rotate: `${(ang * 180) / Math.PI}deg`,
              transformOrigin: "0 50%",
            }}
          />
        );
      })}
    </AbsoluteFill>
  );
};

/** Film grain + vignette, rendered on top of everything. */
export const Finish: React.FC = () => {
  const frame = useCurrentFrame();
  return (
    <AbsoluteFill style={{ pointerEvents: "none" }}>
      <AbsoluteFill
        style={{
          background:
            "radial-gradient(ellipse 75% 60% at 50% 50%, rgba(0,0,0,0) 55%, rgba(0,0,0,0.65) 100%)",
        }}
      />
      <svg width={W} height={H} style={{ position: "absolute", inset: 0, opacity: 0.11, mixBlendMode: "screen" }}>
        <filter id="grain">
          <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves={2} seed={frame % 12} />
          <feColorMatrix type="saturate" values="0" />
        </filter>
        <rect width={W} height={H} filter="url(#grain)" />
      </svg>
    </AbsoluteFill>
  );
};

/** White flash that peaks at `at`. */
export const Flash: React.FC<{ at: number; peak: number; len?: number }> = ({ at, peak, len = 10 }) => {
  const frame = useCurrentFrame();
  const o = ci(frame, [at - 2, at, at + len], [0, peak, 0]);
  if (o <= 0) return null;
  return <AbsoluteFill style={{ background: "white", opacity: o, pointerEvents: "none" }} />;
};
