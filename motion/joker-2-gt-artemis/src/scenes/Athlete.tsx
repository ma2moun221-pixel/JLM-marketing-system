import React from "react";
import { AbsoluteFill, Img, staticFile, useCurrentFrame } from "remotion";
import { CAIRO, ci, OUT } from "../theme";

/**
 * 330–375 (45f): official campaign photo with depth-sandwiched Arabic type.
 * The same image is layered twice (full photo + its cut-out) so the word sits
 * behind the athlete without altering the photo.
 */
export const Athlete: React.FC = () => {
  const f = useCurrentFrame();
  const cam: React.CSSProperties = {
    position: "absolute",
    width: 1080,
    left: 0,
    top: 0,
    scale: ci(f, [0, 45], [1.18, 1.03], OUT),
    rotate: `${ci(f, [0, 45], [-3, 0], OUT)}deg`,
    transformOrigin: "50% 30%",
  };
  return (
    <AbsoluteFill style={{ background: "#03040b" }}>
      <Img src={staticFile("athlete.jpg")} style={cam} />
      <AbsoluteFill style={{ alignItems: "center", top: -70 }}>
        <div style={{ overflow: "hidden", padding: "0 20px" }}>
          <div
            style={{
              fontFamily: CAIRO,
              fontWeight: 900,
              fontSize: 300,
              lineHeight: 1.45,
              color: "white",
              direction: "rtl",
              translate: `0px ${ci(f, [2, 14], [480, 0], OUT)}px`,
              scale: ci(f, [0, 45], [1.12, 1]),
              textShadow: "0 0 60px rgba(150,190,255,0.5)",
            }}
          >
            الجوكر
          </div>
        </div>
      </AbsoluteFill>
      <Img src={staticFile("athlete_cut.png")} style={cam} />
    </AbsoluteFill>
  );
};
