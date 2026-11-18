import React from "react";
import { AbsoluteFill, Img, staticFile, useCurrentFrame } from "remotion";
import { ANTON, ci, OUT } from "../theme";

/**
 * 330–375 (45f): official campaign photo with depth-sandwiched type.
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
    scale: ci(f, [0, 45], [1.16, 1.02], OUT),
    transformOrigin: "50% 30%",
  };
  return (
    <AbsoluteFill style={{ background: "#050505" }}>
      <Img src={staticFile("athlete.jpg")} style={cam} />
      <AbsoluteFill style={{ alignItems: "center", top: 120 }}>
        <div style={{ overflow: "hidden" }}>
          <div
            style={{
              fontFamily: ANTON,
              fontSize: 400,
              lineHeight: 1,
              color: "white",
              letterSpacing: ci(f, [0, 45], [40, 12]),
              translate: `0px ${ci(f, [2, 14], [420, 0], OUT)}px`,
              opacity: 0.95,
            }}
          >
            JOKER
          </div>
        </div>
      </AbsoluteFill>
      <Img src={staticFile("athlete_cut.png")} style={cam} />
    </AbsoluteFill>
  );
};
