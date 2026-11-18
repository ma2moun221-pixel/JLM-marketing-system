import React from "react";
import { Interactive, useCurrentFrame } from "remotion";
import { ANTON, ci, MONO, OUT } from "../theme";

/** Numbered HUD label + big tagline that wipes up from a mask. */
export const Callout: React.FC<{ index: string; label: string; tagline: string; top: number }> = ({
  index,
  label,
  tagline,
  top,
}) => {
  const f = useCurrentFrame();
  return (
    <Interactive.Div name="Callout" style={{ position: "absolute", left: 90, right: 90, top }}>
      <div style={{ display: "flex", alignItems: "center", gap: 22 }}>
        <div
          style={{
            fontFamily: MONO,
            fontWeight: 700,
            fontSize: 40,
            color: "white",
            opacity: ci(f, [2, 8], [0, 1]),
          }}
        >
          {index}
        </div>
        <div
          style={{
            height: 2,
            background: "white",
            width: ci(f, [3, 16], [0, 220], OUT),
          }}
        />
        <div
          style={{
            fontFamily: MONO,
            fontSize: 38,
            letterSpacing: 8,
            color: "rgba(255,255,255,0.85)",
            opacity: ci(f, [8, 14], [0, 1]),
          }}
        >
          {label}
        </div>
      </div>
      <div style={{ overflow: "hidden", marginTop: 12, paddingTop: 6 }}>
        <div
          style={{
            fontFamily: ANTON,
            fontSize: 150,
            lineHeight: 1.02,
            color: "white",
            letterSpacing: 2,
            translate: `0px ${ci(f, [4, 16], [170, 0], OUT)}px`,
          }}
        >
          {tagline}
        </div>
      </div>
    </Interactive.Div>
  );
};

/** Four corner brackets framing the focus area. */
export const Brackets: React.FC<{ x: number; y: number; w: number; h: number }> = ({ x, y, w, h }) => {
  const f = useCurrentFrame();
  const grow = ci(f, [0, 10], [1.25, 1], OUT);
  const o = ci(f, [0, 6], [0, 0.9]);
  const L = 60;
  const st = (r: number): React.CSSProperties => ({
    position: "absolute",
    width: L,
    height: L,
    borderColor: "white",
    borderStyle: "solid",
    borderWidth: 0,
    rotate: `${r}deg`,
    borderTopWidth: 3,
    borderLeftWidth: 3,
  });
  return (
    <div style={{ position: "absolute", left: x, top: y, width: w, height: h, scale: grow, opacity: o }}>
      <div style={{ ...st(0), left: 0, top: 0 }} />
      <div style={{ ...st(90), right: 0, top: 0 }} />
      <div style={{ ...st(180), right: 0, bottom: 0 }} />
      <div style={{ ...st(270), left: 0, bottom: 0 }} />
    </div>
  );
};
