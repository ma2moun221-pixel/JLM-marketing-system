import React from "react";
import { Interactive, useCurrentFrame } from "remotion";
import { CAIRO, ci, FOCUS, MONO, OUT } from "../theme";

/**
 * Arabic detail label (RTL): number, line, small label, big tagline.
 * Use inside a <Sequence> so the frame is local; `dur` drives the exit.
 */
export const Callout: React.FC<{
  index: string;
  label: string;
  tagline: string;
  top: number;
  dur: number;
  size?: number;
}> = ({
  index,
  label,
  tagline,
  top,
  dur,
  size = 132,
}) => {
  const f = useCurrentFrame();
  const out = ci(f, [dur - 6, dur], [1, 0]);
  return (
    <Interactive.Div
      name="Callout"
      style={{ position: "absolute", left: 90, right: 90, top, direction: "rtl", opacity: out }}
    >
      <div style={{ display: "flex", alignItems: "center", gap: 22 }}>
        <div style={{ fontFamily: MONO, fontWeight: 700, fontSize: 42, color: "#9cc4ff", opacity: ci(f, [0, 5], [0, 1]) }}>
          {index}
        </div>
        <div style={{ height: 2, background: "white", width: ci(f, [1, 12], [0, 200], OUT) }} />
        <div
          style={{
            fontFamily: CAIRO,
            fontWeight: 600,
            fontSize: 46,
            color: "rgba(255,255,255,0.9)",
            opacity: ci(f, [5, 11], [0, 1]),
            translate: `${ci(f, [5, 14], [-30, 0], OUT)}px 0px`,
          }}
        >
          {label}
        </div>
      </div>
      <div style={{ overflow: "hidden", marginTop: 4 }}>
        <div
          style={{
            fontFamily: CAIRO,
            fontWeight: 900,
            fontSize: size,
            whiteSpace: "nowrap",
            lineHeight: 1.35,
            color: "white",
            translate: `0px ${ci(f, [3, 15], [190, 0], OUT)}px`,
            textShadow: "0 6px 40px rgba(0,0,0,0.6)",
          }}
        >
          {tagline}
        </div>
      </div>
    </Interactive.Div>
  );
};

/** Rotating HUD reticle on the camera focus point, with a leader line down to the label. */
export const Reticle: React.FC<{ lineTo?: number; dur: number }> = ({ lineTo, dur }) => {
  const f = useCurrentFrame();
  const R = 175;
  const pop = ci(f, [0, 9], [1.6, 1], OUT);
  const o = ci(f, [0, 4, dur - 5, dur], [0, 1, 1, 0]);
  const ticks = new Array(36).fill(0);
  return (
    <svg width={1080} height={1920} style={{ position: "absolute", inset: 0, opacity: o, overflow: "visible" }}>
      <g transform={`translate(${FOCUS.x} ${FOCUS.y}) scale(${pop})`}>
        <g transform={`rotate(${f * 3})`}>
          <circle r={R} fill="none" stroke="white" strokeWidth={2} strokeDasharray="60 20" opacity={0.9} />
          {ticks.map((_, i) => (
            <line
              key={i}
              x1={0}
              y1={-R - 10}
              x2={0}
              y2={-R - (i % 3 === 0 ? 30 : 18)}
              stroke="white"
              strokeWidth={2}
              opacity={0.6}
              transform={`rotate(${i * 10})`}
            />
          ))}
        </g>
        <g transform={`rotate(${-f * 5})`}>
          <circle r={R * 0.72} fill="none" stroke="#9cc4ff" strokeWidth={2} strokeDasharray="4 12" />
        </g>
        {[0, 90, 180, 270].map((a) => (
          <line key={a} x1={0} y1={-26} x2={0} y2={-56} stroke="white" strokeWidth={3} transform={`rotate(${a})`} />
        ))}
      </g>
      {lineTo ? (
        <line
          x1={FOCUS.x}
          y1={FOCUS.y + R * pop + 34}
          x2={FOCUS.x}
          y2={ci(f, [3, 14], [FOCUS.y + R + 34, lineTo], OUT)}
          stroke="white"
          strokeWidth={2}
          opacity={0.8}
        />
      ) : null}
    </svg>
  );
};
