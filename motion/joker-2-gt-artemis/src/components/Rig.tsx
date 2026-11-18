import React from "react";
import { H, W } from "../theme";

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
