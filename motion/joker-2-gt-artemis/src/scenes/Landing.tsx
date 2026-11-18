import React from "react";
import { AbsoluteFill, Img, Interactive, random, staticFile, useCurrentFrame } from "remotion";
import { Shoe } from "../components/Shoe";
import { ANTON, ci, IN, INTER, MONO, OUT, shake } from "../theme";

const LAND = 18; // local frame of touchdown (abs 393 = 13.1s, synced to the boom)
const GROUND_Y = 1460;

const DUST = new Array(70).fill(0).map((_, i) => {
  const side = random(`ds${i}`) < 0.5 ? -1 : 1;
  return {
    vx: side * (6 + random(`dv${i}`) * 30),
    vy: -(2 + random(`dy${i}`) * 13),
    size: 8 + random(`dz${i}`) * 40,
    x0: side * random(`dx${i}`) * 380,
    life: 25 + random(`dl${i}`) * 35,
  };
});

/** 375–450 (75f): touchdown on the lunar surface + end card. */
export const Landing: React.FC = () => {
  const f = useCurrentFrame();
  const t = f - LAND;
  const sk = shake(f, LAND, 14, 34);
  const shoeY = ci(f, [4, LAND], [-1500, 0], IN);
  const title = "JOKER 2 GT".split("");

  return (
    <AbsoluteFill style={{ translate: `${sk.x}px ${sk.y}px`, scale: ci(f, [LAND, 75], [1, 1.04]) }}>
      {/* Lunar ground rises in (camera tilt) */}
      <Img
        src={staticFile("ground.png")}
        style={{
          position: "absolute",
          width: 1500,
          left: -210,
          top: ci(f, [0, 14], [1920, GROUND_Y - 110], OUT),
        }}
      />

      {/* Shockwave on the ground */}
      {t >= 0 ? (
        <div
          style={{
            position: "absolute",
            left: 540,
            top: GROUND_Y + 10,
            width: ci(t, [0, 22], [200, 2000], OUT),
            height: ci(t, [0, 22], [30, 300], OUT),
            translate: "-50% -50%",
            borderRadius: "50%",
            border: "4px solid white",
            opacity: ci(t, [0, 22], [0.9, 0]),
          }}
        />
      ) : null}

      {/* Dust burst */}
      {t >= 0
        ? DUST.map((d, i) => {
            const k = Math.min(t, d.life);
            const x = 540 + d.x0 + d.vx * k * (1 - k / (d.life * 2.2));
            const y = GROUND_Y + d.vy * k + 0.18 * k * k;
            return (
              <div
                key={i}
                style={{
                  position: "absolute",
                  left: x,
                  top: Math.min(y, GROUND_Y + 30),
                  width: d.size * (1 + k / 20),
                  height: d.size * (1 + k / 20),
                  borderRadius: "50%",
                  background: "rgba(200,200,200,0.9)",
                  filter: `blur(${4 + k / 3}px)`,
                  opacity: ci(t, [0, 3, d.life], [0, 0.55, 0]),
                }}
              />
            );
          })
        : null}

      {/* The shoe drops */}
      <AbsoluteFill style={{ alignItems: "center" }}>
        <Shoe
          name="lateral"
          width={980}
          glow={ci(t, [0, 6, 30], [0.2, 0.5, 0.2])}
          sweep={ci(f, [30, 70], [0, 1])}
          style={{
            position: "absolute",
            top: GROUND_Y - 445,
            translate: `0px ${shoeY}px`,
            rotate: `${ci(f, [4, LAND], [-28, -2], IN)}deg`,
            filter: `blur(${ci(f, [4, LAND - 3, LAND], [0, 12, 0])}px)`,
          }}
        />
      </AbsoluteFill>

      {/* Logo lockup (cropped from official artwork, unaltered) */}
      <Img
        src={staticFile("logo.png")}
        style={{
          position: "absolute",
          width: 400,
          left: 340,
          top: 150,
          opacity: ci(t, [10, 22], [0, 1]),
          scale: ci(t, [10, 26], [1.2, 1], OUT),
          filter: `blur(${ci(t, [10, 20], [10, 0])}px)`,
        }}
      />

      {/* Title */}
      <AbsoluteFill style={{ top: 520, alignItems: "center" }}>
        <div style={{ display: "flex", overflow: "hidden", paddingTop: 8 }}>
          {title.map((c, i) => (
            <span
              key={i}
              style={{
                fontFamily: ANTON,
                fontSize: 190,
                lineHeight: 1.05,
                color: "white",
                whiteSpace: "pre",
                display: "inline-block",
                translate: `0px ${ci(t, [4 + i * 1.5, 16 + i * 1.5], [220, 0], OUT)}px`,
              }}
            >
              {c}
            </span>
          ))}
        </div>
        <Interactive.Div
          name="Artemis"
          style={{
            fontFamily: INTER,
            fontWeight: 800,
            fontSize: 96,
            color: "white",
            marginTop: 4,
            letterSpacing: ci(t, [14, 45], [60, 14], OUT),
            opacity: ci(t, [14, 24], [0, 1]),
            filter: `blur(${ci(t, [14, 24], [12, 0])}px)`,
          }}
        >
          “ARTEMIS”
        </Interactive.Div>
      </AbsoluteFill>

      {/* CTA */}
      <AbsoluteFill style={{ top: 1690, alignItems: "center" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 26, opacity: ci(t, [26, 34], [0, 1]) }}>
          <div style={{ height: 2, background: "white", width: ci(t, [26, 40], [0, 120], OUT) }} />
          <div style={{ fontFamily: MONO, fontWeight: 700, fontSize: 46, letterSpacing: 12, color: "white" }}>
            AVAILABLE NOW
          </div>
          <div style={{ height: 2, background: "white", width: ci(t, [26, 40], [0, 120], OUT) }} />
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
