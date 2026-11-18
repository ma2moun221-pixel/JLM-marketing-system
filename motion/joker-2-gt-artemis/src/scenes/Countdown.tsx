import React from "react";
import { AbsoluteFill, Interactive, useCurrentFrame } from "remotion";
import { ANTON, CAIRO, ci, IN, MONO, OUT } from "../theme";

const NUMS = [
  { n: "3", at: 6 },
  { n: "2", at: 21 },
  { n: "1", at: 36 },
];

/** 0–60: hyperspace HUD, Arabic countdown with counter-rotating dials, light streak. */
export const Countdown: React.FC = () => {
  const f = useCurrentFrame();
  const hudOut = ci(f, [44, 52], [1, 0]);
  return (
    <AbsoluteFill>
      <Interactive.Div
        name="HUD top"
        style={{
          position: "absolute",
          top: 140,
          left: 90,
          right: 90,
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          direction: "rtl",
          opacity: hudOut,
        }}
      >
        <span
          style={{
            fontFamily: CAIRO,
            fontWeight: 800,
            fontSize: 50,
            color: "white",
            clipPath: `inset(0 0 0 ${ci(f, [2, 16], [100, 0])}%)`,
          }}
        >
          مهمّة أرتميس
        </span>
        <span style={{ fontFamily: MONO, fontSize: 32, color: "#ff5a5a", opacity: Math.floor(f / 6) % 2 ? 1 : 0.25 }}>
          ● REC
        </span>
      </Interactive.Div>

      {/* Counter-rotating HUD dials */}
      <svg width={1080} height={1920} style={{ position: "absolute", inset: 0, opacity: ci(f, [0, 8, 46, 54], [0, 1, 1, 0]) }}>
        <g transform={`translate(540 960) scale(${ci(f, [0, 12], [0.6, 1], OUT)})`}>
          <g transform={`rotate(${f * 4})`}>
            <circle r={380} fill="none" stroke="white" strokeOpacity={0.5} strokeWidth={2} strokeDasharray="140 40 20 40" />
          </g>
          <g transform={`rotate(${-f * 6})`}>
            <circle r={330} fill="none" stroke="#9cc4ff" strokeOpacity={0.8} strokeWidth={3} strokeDasharray="8 16" />
          </g>
          <g transform={`rotate(${f * 9})`}>
            {new Array(60).fill(0).map((_, i) => (
              <line
                key={i}
                x1={0}
                y1={-430}
                x2={0}
                y2={i % 5 === 0 ? -470 : -446}
                stroke="white"
                strokeOpacity={0.55}
                strokeWidth={2}
                transform={`rotate(${i * 6})`}
              />
            ))}
          </g>
          {/* progress arc */}
          <circle
            r={300}
            fill="none"
            stroke="white"
            strokeWidth={6}
            strokeDasharray={2 * Math.PI * 300}
            strokeDashoffset={2 * Math.PI * 300 * (1 - ci(f, [4, 50], [0, 1]))}
            transform="rotate(-90)"
            strokeLinecap="round"
          />
        </g>
      </svg>

      {NUMS.map(({ n, at }) => {
        const local = f - at;
        if (local < 0 || local > 15) return null;
        return (
          <AbsoluteFill key={n} style={{ justifyContent: "center", alignItems: "center" }}>
            <div
              style={{
                fontFamily: ANTON,
                fontSize: 440,
                lineHeight: 1,
                color: "white",
                scale: ci(local, [0, 7], [1.6, 1], OUT),
                rotate: `${ci(local, [0, 8], [-25, 0], OUT)}deg`,
                opacity: ci(local, [0, 2, 11, 15], [0, 1, 1, 0]),
                filter: `blur(${ci(local, [0, 4, 11, 15], [14, 0, 0, 18])}px)`,
                textShadow: "0 0 70px rgba(150,190,255,0.8)",
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
          bottom: 210,
          left: 0,
          right: 0,
          textAlign: "center",
          fontFamily: CAIRO,
          fontWeight: 700,
          fontSize: 56,
          color: "white",
          opacity: ci(f, [4, 10, 44, 52], [0, 1, 1, 0]),
        }}
      >
        جاهز؟ يلّا ننطلق
      </Interactive.Div>

      {/* Anamorphic streak into the flash */}
      <AbsoluteFill style={{ justifyContent: "center", alignItems: "center" }}>
        <div
          style={{
            width: ci(f, [44, 60], [0, 2600], IN),
            height: ci(f, [44, 60], [2, 80], IN),
            borderRadius: 100,
            background: "white",
            boxShadow: "0 0 90px 36px rgba(150,190,255,0.8)",
            opacity: ci(f, [44, 48], [0, 1]),
          }}
        />
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
