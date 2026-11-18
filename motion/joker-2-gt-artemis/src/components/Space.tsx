import React from "react";
import { AbsoluteFill, Img, random, staticFile, useCurrentFrame } from "remotion";
import { ci, CUTS, H, IN, W } from "../theme";

/** Rotation contribution of the whip transitions (deg); also used by the scene camera. */
export const whip = (f: number) => {
  let rot = 0;
  let zoom = 1;
  let blur = 0;
  CUTS.forEach((c, i) => {
    const dir = i % 2 === 0 ? 1 : -1;
    if (f >= c - 7 && f < c) {
      const p = ci(f, [c - 7, c], [0, 1], IN);
      rot += 22 * dir * p;
      zoom *= 1 + 0.3 * p;
      blur += 16 * p;
    } else if (f >= c && f < c + 9) {
      const p = ci(f, [c, c + 9], [1, 0], (t) => 1 - Math.pow(1 - t, 3));
      rot -= 22 * dir * p;
      zoom *= 1 + 0.3 * p;
      blur += 16 * p;
    }
  });
  return { rot, zoom, blur };
};

const TUNNEL = new Array(260).fill(0).map((_, i) => {
  const a = random(`ta${i}`) * Math.PI * 2;
  const r = 0.08 + random(`tr${i}`) * 1.4;
  return { x: Math.cos(a) * r, y: Math.sin(a) * r * 1.6, z0: random(`tz${i}`) };
});

const DRIFT = new Array(110).fill(0).map((_, i) => ({
  x: random(`x${i}`) * W,
  y: random(`y${i}`) * H,
  s: 1.2 + random(`s${i}`) * 2.4,
  tw: random(`t${i}`) * Math.PI * 2,
  depth: 0.3 + random(`d${i}`) * 0.7,
}));

const BOKEH = new Array(12).fill(0).map((_, i) => ({
  x: random(`bx${i}`) * W,
  y: random(`by${i}`) * H,
  s: 40 + random(`bs${i}`) * 110,
  v: 0.6 + random(`bv${i}`) * 1.6,
}));

/** Distance travelled through the star tunnel by frame f. */
const travel = (f: number) => f * 0.007 + Math.pow(ci(f, [26, 62], [0, 1], IN), 2) * 1.9;

/** Global deep-space backdrop: rotating nebula, planet, star tunnel, drifting stars, bokeh dust. */
export const Space: React.FC = () => {
  const f = useCurrentFrame();
  const w = whip(f);
  const intro = f < 62;

  // Planet placement per act
  let planet: React.CSSProperties = { display: "none" };
  if (f >= 56 && f < 375) {
    planet = {
      width: 1500,
      left: 960 - 750 + ci(f, [56, 375], [40, -40]),
      top: -150 - 750 + ci(f, [56, 375], [-60, 20]),
      rotate: `${200 + f * 0.03}deg`,
      opacity: ci(f, [56, 72], [0, 1]),
    };
  } else if (f >= 375) {
    planet = {
      width: 2800,
      left: 540 - 1400,
      top: 2440 - 1400 + ci(f, [375, 400], [500, 0], (t) => 1 - Math.pow(1 - t, 3)),
      rotate: `${-12 + (f - 375) * 0.04}deg`,
    };
  }

  return (
    <AbsoluteFill style={{ backgroundColor: "#03040b", overflow: "hidden" }}>
      {/* Nebula */}
      <Img
        src={staticFile("nebula.jpg")}
        style={{
          position: "absolute",
          width: 2400,
          height: 2400,
          left: (W - 2400) / 2,
          top: (H - 2400) / 2,
          rotate: `${f * 0.05 + w.rot * 0.6}deg`,
          scale: (intro ? ci(f, [0, 62], [1.0, 1.5], IN) : ci(f, [62, 450], [1.08, 1.22])) * (1 + (w.zoom - 1) * 0.5),
          opacity: intro ? ci(f, [0, 30, 62], [0.35, 0.45, 0.9]) : f >= 375 ? 0.75 : 0.9,
          filter: w.blur > 0.5 ? `blur(${w.blur * 0.4}px)` : undefined,
        }}
      />

      {/* Planet */}
      <Img src={staticFile("planet.png")} style={{ position: "absolute", ...planet }} />

      {/* Hyperspace tunnel (intro) */}
      {intro ? (
        <svg width={W} height={H} style={{ position: "absolute", inset: 0 }}>
          {TUNNEL.map((s, i) => {
            const z = 1 - ((((s.z0 + travel(f)) % 1) + 1) % 1);
            const zp = 1 - ((((s.z0 + travel(f - 1.6)) % 1) + 1) % 1);
            if (zp < z || z < 0.02) return null;
            const fov = 260;
            const x = W / 2 + (s.x / z) * fov;
            const y = H / 2 + (s.y / z) * fov;
            const xp = W / 2 + (s.x / zp) * fov;
            const yp = H / 2 + (s.y / zp) * fov;
            return (
              <line
                key={i}
                x1={xp}
                y1={yp}
                x2={x}
                y2={y}
                stroke="white"
                strokeWidth={Math.min(5, 0.6 / z)}
                strokeLinecap="round"
                opacity={Math.min(1, 0.15 / z)}
              />
            );
          })}
        </svg>
      ) : null}

      {/* Drifting stars */}
      {!intro
        ? DRIFT.map((s, i) => {
            const tw = 0.4 + 0.6 * Math.abs(Math.sin(f / 8 + s.tw));
            return (
              <div
                key={i}
                style={{
                  position: "absolute",
                  left: (((s.x - f * 0.6 * s.depth) % W) + W) % W,
                  top: (((s.y + f * 0.25 * s.depth) % H) + H) % H,
                  width: s.s,
                  height: s.s,
                  borderRadius: "50%",
                  background: "white",
                  boxShadow: `0 0 ${s.s * 3}px rgba(170,200,255,0.8)`,
                  opacity: tw * s.depth,
                }}
              />
            );
          })
        : null}

      {/* Foreground space dust (bokeh) */}
      {!intro
        ? BOKEH.map((b, i) => (
            <div
              key={i}
              style={{
                position: "absolute",
                left: (((b.x - f * 3 * b.v) % (W + 300)) + W + 300) % (W + 300) - 150,
                top: b.y + Math.sin(f / 30 + i) * 30,
                width: b.s,
                height: b.s,
                borderRadius: "50%",
                background: "radial-gradient(circle, rgba(160,190,255,0.22) 0%, rgba(160,190,255,0) 70%)",
                filter: "blur(4px)",
              }}
            />
          ))
        : null}
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
          background: "radial-gradient(ellipse 80% 62% at 50% 50%, rgba(0,0,0,0) 55%, rgba(0,0,0,0.6) 100%)",
        }}
      />
      <svg width={W} height={H} style={{ position: "absolute", inset: 0, opacity: 0.08, mixBlendMode: "screen" }}>
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

/** Whip-spin camera applied to the scene layer at each cut. */
export const WhipCamera: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const f = useCurrentFrame();
  const w = whip(f);
  return (
    <AbsoluteFill
      style={{
        rotate: `${w.rot}deg`,
        scale: w.zoom,
        filter: w.blur > 0.5 ? `blur(${w.blur}px)` : undefined,
      }}
    >
      {children}
    </AbsoluteFill>
  );
};

