import React from "react";
import { AbsoluteFill } from "remotion";
import { FOCUS, H, W } from "../theme";
import { Shoe } from "./Shoe";

export type ShoeName = "lateral" | "medial" | "sole" | "heels";
export type View = { name: ShoeName; width: number };

/** Natural pixel size of each cut-out. */
export const NATURAL: Record<ShoeName, { w: number; h: number }> = {
  lateral: { w: 944, h: 444 },
  medial: { w: 975, h: 443 },
  heels: { w: 844, h: 503 },
  sole: { w: 1005, h: 408 },
};

/** Screen position of an image-space point for a view centred at (cx, cy). */
export const pt = (v: View, x: number, y: number, cx = 540, cy = 960) => {
  const k = v.width / NATURAL[v.name].w;
  return {
    x: cx - v.width / 2 + x * k,
    y: cy - (NATURAL[v.name].h * k) / 2 + y * k,
  };
};

/**
 * Fake-3D turntable from the real product photos: the visible view swaps every
 * 180° of `angle`, each view turning from edge-on (−90°) to face-on (0°) to edge-on (+90°).
 */
export const Turntable: React.FC<{
  views: View[];
  angle: number;
  axis?: "X" | "Y";
  cx?: number;
  cy?: number;
  blur?: number;
  sweep?: number;
  glow?: number;
  extra?: React.CSSProperties;
}> = ({ views, angle, axis = "Y", cx = 540, cy = 960, blur = 0, sweep, glow, extra }) => {
  const idx = Math.max(0, Math.min(views.length - 1, Math.round(angle / 180)));
  const local = angle - idx * 180;
  const v = views[idx];
  const edge = Math.abs(local) / 90;
  return (
    <AbsoluteFill style={{ perspective: 1700 }}>
      <div
        style={{
          position: "absolute",
          left: cx,
          top: cy,
          translate: "-50% -50%",
          transform: `rotate${axis}(${local}deg)`,
          ...extra,
        }}
      >
        <Shoe
          name={v.name}
          width={v.width}
          sweep={sweep}
          glow={glow}
          style={{
            filter: `brightness(${1 + edge * 0.5})${blur > 0.3 ? ` blur(${blur}px)` : ""}`,
          }}
        />
      </div>
    </AbsoluteFill>
  );
};

/**
 * Tilted elliptical orbit around the product. Render once with layer="back"
 * (before the shoe) and once with layer="front" (after) for real depth.
 */
export const Orbit: React.FC<{
  frame: number;
  layer: "back" | "front";
  cx: number;
  cy: number;
  rx: number;
  ry: number;
  tilt: number;
  speed: number;
  draw: number;
  opacity?: number;
  seed?: number;
}> = ({ frame, layer, cx, cy, rx, ry, tilt, speed, draw, opacity = 1, seed = 0 }) => {
  const sweep = layer === "back" ? 1 : 0;
  const d = `M ${cx - rx} ${cy} A ${rx} ${ry} 0 0 ${sweep} ${cx + rx} ${cy}`;
  const len = Math.PI * rx * 1.1;
  const parts = new Array(7).fill(0).map((_, i) => {
    const a = frame * speed + (i / 7) * Math.PI * 2 + seed;
    return { x: cx + rx * Math.cos(a), y: cy + ry * Math.sin(a), front: Math.sin(a) > 0, big: i % 3 === 0 };
  });
  return (
    <svg
      width={W}
      height={H}
      style={{ position: "absolute", inset: 0, opacity, overflow: "visible" }}
    >
      <defs>
        <filter id={`glow-${layer}-${seed}`} x="-50%" y="-50%" width="200%" height="200%">
          <feGaussianBlur stdDeviation="5" />
        </filter>
      </defs>
      <g transform={`rotate(${tilt} ${cx} ${cy})`}>
        <path
          d={d}
          fill="none"
          stroke="rgba(170,205,255,0.5)"
          strokeWidth={layer === "front" ? 2.5 : 1.5}
          strokeDasharray={len}
          strokeDashoffset={len * (1 - draw)}
        />
        <path
          d={d}
          fill="none"
          stroke="white"
          strokeWidth={layer === "front" ? 3 : 2}
          strokeDasharray="3 22"
          strokeDashoffset={-frame * speed * 400}
          opacity={draw}
        />
        {parts
          .filter((p) => p.front === (layer === "front"))
          .map((p, i) => (
            <g key={i} opacity={draw}>
              <circle cx={p.x} cy={p.y} r={p.big ? 14 : 8} fill="rgba(160,200,255,0.9)" filter={`url(#glow-${layer}-${seed})`} />
              <circle cx={p.x} cy={p.y} r={p.big ? 5 : 3} fill="white" />
            </g>
          ))}
      </g>
    </svg>
  );
};

/**
 * Macro camera: scales by `s` around the image point P (screen coords at s=1)
 * and moves it to the FOCUS point. Renders a blurred pass plus a sharp pass
 * masked around P for a shallow depth-of-field look.
 */
export const Camera: React.FC<{ P: { x: number; y: number }; s: number; rot?: number; children: React.ReactNode }> = ({
  P,
  s,
  rot = 0,
  children,
}) => {
  const blur = Math.max(0, s - 1.25) * 1.3;
  const r = 330 / s;
  const mask = `radial-gradient(circle ${r}px at ${P.x}px ${P.y}px, black 45%, transparent 100%)`;
  return (
    <AbsoluteFill
      style={{
        transform: `translate(${FOCUS.x - P.x}px, ${FOCUS.y - P.y}px) rotate(${rot}deg) scale(${s})`,
        transformOrigin: `${P.x}px ${P.y}px`,
      }}
    >
      <AbsoluteFill style={{ filter: blur > 0.2 ? `blur(${blur}px) brightness(0.85)` : undefined }}>{children}</AbsoluteFill>
      {blur > 0.2 ? <AbsoluteFill style={{ maskImage: mask, WebkitMaskImage: mask }}>{children}</AbsoluteFill> : null}
    </AbsoluteFill>
  );
};
