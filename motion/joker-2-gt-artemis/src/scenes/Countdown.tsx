import React from "react";
import { AbsoluteFill, Interactive, useCurrentFrame } from "remotion";
import { ANTON, ci, IN, MONO, OUT } from "../theme";

const NUMS = [
  { n: "3", at: 6 },
  { n: "2", at: 21 },
  { n: "1", at: 36 },
];

const typed = (text: string, f: number, start: number, cps = 1.2) =>
  text.slice(0, Math.max(0, Math.floor((f - start) * cps)));

/** 0–60: HUD countdown, warp, light streak. */
export const Countdown: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill>
      <Interactive.Div
        name="HUD top"
        style={{
          position: "absolute",
          top: 150,
          left: 90,
          right: 90,
          display: "flex",
          justifyContent: "space-between",
          fontFamily: MONO,
          fontSize: 34,
          letterSpacing: 6,
          color: "rgba(255,255,255,0.85)",
          opacity: ci(f, [44, 54], [1, 0]),
        }}
      >
        <span>{typed("MISSION // ARTEMIS", f, 1)}</span>
        <span style={{ opacity: Math.floor(f / 6) % 2 ? 1 : 0.2 }}>● REC</span>
      </Interactive.Div>

      {NUMS.map(({ n, at }) => {
        const local = f - at;
        if (local < 0 || local > 15) return null;
        return (
          <AbsoluteFill key={n} style={{ justifyContent: "center", alignItems: "center" }}>
            <div
              style={{
                position: "absolute",
                width: ci(local, [0, 14], [200, 900], OUT),
                height: ci(local, [0, 14], [200, 900], OUT),
                borderRadius: "50%",
                border: "3px solid white",
                opacity: ci(local, [0, 14], [0.8, 0]),
              }}
            />
            <div
              style={{
                fontFamily: ANTON,
                fontSize: 620,
                lineHeight: 1,
                color: "white",
                scale: ci(local, [0, 7], [1.45, 1], OUT),
                opacity: ci(local, [0, 2, 11, 15], [0, 1, 1, 0]),
                filter: `blur(${ci(local, [0, 4, 11, 15], [14, 0, 0, 18])}px)`,
                textShadow: "0 0 60px rgba(255,255,255,0.45)",
              }}
            >
              {n}
            </div>
          </AbsoluteFill>
        );
      })}

      <Interactive.Div
        name="HUD bottom"
        style={{
          position: "absolute",
          bottom: 190,
          left: 0,
          right: 0,
          textAlign: "center",
          fontFamily: MONO,
          fontSize: 38,
          letterSpacing: 14,
          color: "white",
          opacity: ci(f, [4, 10, 44, 52], [0, 1, 1, 0]),
        }}
      >
        T-MINUS
      </Interactive.Div>

      {/* Horizontal anamorphic streak into the flash */}
      <AbsoluteFill style={{ justifyContent: "center", alignItems: "center" }}>
        <div
          style={{
            width: ci(f, [44, 60], [0, 2600], IN),
            height: ci(f, [44, 60], [2, 70], IN),
            borderRadius: 100,
            background: "white",
            boxShadow: "0 0 80px 30px rgba(255,255,255,0.7)",
            opacity: ci(f, [44, 48], [0, 1]),
          }}
        />
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
