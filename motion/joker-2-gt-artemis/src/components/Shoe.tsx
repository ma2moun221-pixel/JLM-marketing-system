import React from "react";
import { Img, staticFile } from "remotion";

/**
 * Genuine product cut-out (no generated product imagery).
 * `sweep` (0..1) moves a soft light band across the shoe, masked to its silhouette.
 */
export const Shoe: React.FC<{
  name: "lateral" | "medial" | "sole" | "heels";
  width: number;
  sweep?: number;
  glow?: number;
  style?: React.CSSProperties;
}> = ({ name, width, sweep, glow = 0.18, style }) => {
  const src = staticFile(`shoe_${name}.png`);
  const pos = sweep === undefined ? -100 : -60 + sweep * 220;
  return (
    <div style={{ position: "relative", width, ...style }}>
      <div
        style={{
          position: "absolute",
          inset: "-30%",
          background: `radial-gradient(ellipse 50% 45% at 50% 55%, rgba(150,190,255,${glow}) 0%, rgba(150,190,255,0) 70%)`,
        }}
      />
      <Img
        src={src}
        style={{
          width: "100%",
          display: "block",
          position: "relative",
          filter: "drop-shadow(0 30px 40px rgba(0,0,0,0.65))",
        }}
      />
      {sweep !== undefined ? (
        <div
          style={{
            position: "absolute",
            inset: 0,
            WebkitMaskImage: `url(${src})`,
            WebkitMaskSize: "100% 100%",
            maskImage: `url(${src})`,
            maskSize: "100% 100%",
            background: `linear-gradient(105deg, rgba(255,255,255,0) ${pos - 14}%, rgba(255,255,255,0.85) ${pos}%, rgba(255,255,255,0) ${pos + 14}%)`,
            mixBlendMode: "screen",
          }}
        />
      ) : null}
    </div>
  );
};
