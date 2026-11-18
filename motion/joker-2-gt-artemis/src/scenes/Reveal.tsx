import React from "react";
import { AbsoluteFill, Interactive, useCurrentFrame } from "remotion";
import { Shoe } from "../components/Shoe";
import { ANTON, ci, INTER, OUT, shake } from "../theme";

/** 60–150 (90f): shoe slams in, giant title behind, ARTEMIS tracks in. */
export const Reveal: React.FC = () => {
  const f = useCurrentFrame();
  const enter = ci(f, [0, 13], [0, 1], OUT);
  const vel = ci(f, [0, 3, 13], [1, 1, 0]);
  const sk = shake(f, 11, 10, 18);
  const lines = [
    { t: "JOKER", stroke: false, d: 2 },
    { t: "2 GT", stroke: true, d: 6 },
  ];
  return (
    <AbsoluteFill style={{ translate: `${sk.x}px ${sk.y}px` }}>
      {/* Giant type behind the shoe */}
      <AbsoluteFill style={{ justifyContent: "flex-start", alignItems: "center", top: 330 }}>
        {lines.map((l) => (
          <div key={l.t} style={{ overflow: "hidden", height: 350 }}>
            <div
              style={{
                fontFamily: ANTON,
                fontSize: 340,
                lineHeight: 0.98,
                letterSpacing: 6,
                color: l.stroke ? "transparent" : "rgba(255,255,255,0.16)",
                WebkitTextStroke: l.stroke ? "3px rgba(255,255,255,0.9)" : "3px rgba(255,255,255,0.35)",
                translate: `0px ${ci(f, [l.d, l.d + 14], [340, 0], OUT)}px`,
                scale: ci(f, [0, 90], [1.0, 1.08]),
              }}
            >
              {l.t}
            </div>
          </div>
        ))}
      </AbsoluteFill>

      {/* Ghost trails */}
      {[3, 2, 1].map((k) => (
        <AbsoluteFill key={k} style={{ justifyContent: "center", alignItems: "center", top: 330 }}>
          <Shoe
            name="lateral"
            width={940}
            glow={0}
            style={{
              translate: `${(1 - enter) * 1500 + k * 90 * vel}px 0px`,
              rotate: `${-6 - (1 - enter) * 18}deg`,
              opacity: 0.22 * vel,
              filter: "blur(6px)",
            }}
          />
        </AbsoluteFill>
      ))}

      <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", top: 330 }}>
        <Shoe
          name="lateral"
          width={940}
          sweep={ci(f, [18, 50], [0, 1])}
          style={{
            translate: `${(1 - enter) * 1500}px ${Math.sin(f / 13) * 14}px`,
            rotate: `${-6 - (1 - enter) * 18 + Math.sin(f / 17) * 1.5}deg`,
            scale: ci(f, [13, 90], [1, 1.07]),
            filter: `blur(${vel * 10}px)`,
          }}
        />
      </AbsoluteFill>

      <Interactive.Div
        name="Artemis"
        style={{
          position: "absolute",
          bottom: 230,
          left: 0,
          right: 0,
          textAlign: "center",
          fontFamily: INTER,
          fontWeight: 800,
          fontSize: 104,
          color: "white",
          letterSpacing: ci(f, [16, 50], [70, 18], OUT),
          opacity: ci(f, [16, 26], [0, 1]),
          filter: `blur(${ci(f, [16, 28], [12, 0])}px)`,
        }}
      >
        “ARTEMIS”
      </Interactive.Div>
    </AbsoluteFill>
  );
};
