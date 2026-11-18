import React from "react";
import { AbsoluteFill, useCurrentFrame } from "remotion";
import { Brackets, Callout } from "../components/Callout";
import { Shoe } from "../components/Shoe";
import { ci, INOUT, OUT } from "../theme";

/** 150–225 (75f): macro pan across the sculpted upper. */
export const UpperDetail: React.FC = () => {
  const f = useCurrentFrame();
  // speed ramp: fast whip then slow drift
  const x = ci(f, [0, 10, 75], [900, 380, -260], OUT);
  return (
    <AbsoluteFill>
      <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", top: -260 }}>
        <Shoe
          name="medial"
          width={2500}
          glow={0.1}
          sweep={ci(f, [10, 60], [0.05, 0.95])}
          style={{
            translate: `${x}px 0px`,
            rotate: `${ci(f, [0, 75], [-4, 2])}deg`,
            filter: `blur(${ci(f, [0, 8], [12, 0])}px)`,
          }}
        />
      </AbsoluteFill>
      <Brackets x={90} y={380} w={900} h={640} />
      <Callout index="01" label="UPPER" tagline="PURE WHITE." top={1420} />
    </AbsoluteFill>
  );
};

/** 225–285 (60f): outsole flips up out of the dark. */
export const SoleDetail: React.FC = () => {
  const f = useCurrentFrame();
  const e = ci(f, [0, 16], [0, 1], OUT);
  return (
    <AbsoluteFill style={{ perspective: 1600 }}>
      <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", top: -140 }}>
        <Shoe
          name="sole"
          width={1040}
          glow={0.22}
          sweep={ci(f, [12, 55], [0, 1])}
          style={{
            rotate: `${-14 + (1 - e) * -30 + ci(f, [16, 60], [0, 5])}deg`,
            transform: `rotateX(${(1 - e) * 75}deg)`,
            scale: ci(f, [0, 16, 60], [0.55, 1, 1.07], INOUT),
            opacity: ci(f, [0, 4], [0, 1]),
          }}
        />
      </AbsoluteFill>
      <Callout index="02" label="OUTSOLE" tagline="ZERO GRAVITY." top={1300} />
    </AbsoluteFill>
  );
};

/** 285–330 (45f): heel pair rises into frame. */
export const HeelDetail: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill>
      <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", top: -120 }}>
        <Shoe
          name="heels"
          width={860}
          glow={0.25}
          sweep={ci(f, [8, 40], [0, 1])}
          style={{
            translate: `0px ${ci(f, [0, 12], [520, 0], OUT)}px`,
            scale: ci(f, [0, 12, 45], [0.7, 1, 1.12], OUT),
            filter: `blur(${ci(f, [0, 8], [10, 0])}px)`,
          }}
        />
      </AbsoluteFill>
      <Callout index="03" label="HEEL" tagline="MOON READY." top={1300} />
    </AbsoluteFill>
  );
};
