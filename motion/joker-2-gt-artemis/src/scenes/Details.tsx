import React from "react";
import { AbsoluteFill, Sequence, useCurrentFrame } from "remotion";
import { Callout, Reticle } from "../components/Callout";
import { Camera, pt, Turntable, View } from "../components/Rig";
import { Shoe } from "../components/Shoe";
import { ci, INOUT } from "../theme";

const LAT: View = { name: "lateral", width: 900 };
const HEELS: View = { name: "heels", width: 700 };
const SOLE: View = { name: "sole", width: 920 };

const CENTER = { x: 540, y: 960 };
const CAGE = pt(LAT, 600, 200);
const LOGO = pt(LAT, 483, 250);
const PODS = pt(LAT, 492, 398);
const EMBLEM = pt(HEELS, 182, 185);
const HERRING = pt(SOLE, 150, 195);

const LABEL_TOP = 1330;

/** Smoothly interpolated camera path through keyframes. */
const path = (f: number, frames: number[], pts: { x: number; y: number }[], scales: number[], rots: number[]) => ({
  P: {
    x: ci(f, frames, pts.map((p) => p.x), INOUT),
    y: ci(f, frames, pts.map((p) => p.y), INOUT),
  },
  s: ci(f, frames, scales, INOUT),
  rot: ci(f, frames, rots, INOUT),
});

/** 150–240 (90f): macro camera glides between three details of the upper. */
export const UpperDetails: React.FC = () => {
  const f = useCurrentFrame();
  const cam = path(
    f,
    [0, 12, 30, 40, 60, 70, 90],
    [CENTER, CAGE, CAGE, LOGO, LOGO, PODS, PODS],
    [1, 2.6, 2.8, 3.4, 3.6, 2.7, 2.9],
    [0, -4, -2, 5, 6, -3, -1],
  );
  return (
    <AbsoluteFill>
      <Camera P={cam.P} s={cam.s} rot={cam.rot}>
        <AbsoluteFill style={{ justifyContent: "center", alignItems: "center" }}>
          <Shoe name="lateral" width={LAT.width} glow={0.12} sweep={ci(f, [0, 90], [0, 1])} />
        </AbsoluteFill>
      </Camera>

      <Sequence from={12} durationInFrames={24} layout="none">
        <Reticle dur={24} lineTo={LABEL_TOP - 20} />
        <Callout index="01" label="الجزء العلوي" tagline="قفص منحوت" top={LABEL_TOP} dur={24} />
      </Sequence>
      <Sequence from={40} durationInFrames={26} layout="none">
        <Reticle dur={26} lineTo={LABEL_TOP - 20} />
        <Callout index="02" label="شعار الجوكر" tagline="توقيع النجم" top={LABEL_TOP} dur={26} />
      </Sequence>
      <Sequence from={70} durationInFrames={20} layout="none">
        <Reticle dur={22} lineTo={LABEL_TOP - 20} />
        <Callout index="03" label="النعل الأوسط" tagline="خطوط انسيابية" top={LABEL_TOP} dur={22} />
      </Sequence>
    </AbsoluteFill>
  );
};

/** 240–330 (90f): turntable to the heel, focus; flip to the outsole, focus. */
export const TurnDetails: React.FC = () => {
  const f = useCurrentFrame();
  const cam = path(
    f,
    [0, 12, 20, 42, 48, 56, 64, 90],
    [CENTER, CENTER, EMBLEM, EMBLEM, CENTER, CENTER, HERRING, HERRING],
    [1, 1, 2.3, 2.5, 1, 1, 2.6, 2.85],
    [0, 0, -3, 2, 0, 0, 4, 1],
  );
  const yAngle = ci(f, [0, 12], [0, 180], INOUT);
  const yVel = Math.abs(ci(f + 1, [0, 12], [0, 180], INOUT) - yAngle);
  const xAngle = ci(f, [44, 56], [0, 180], INOUT);
  const xVel = Math.abs(ci(f + 1, [44, 56], [0, 180], INOUT) - xAngle);

  return (
    <AbsoluteFill>
      <Camera P={cam.P} s={cam.s} rot={cam.rot}>
        {f < 44 ? (
          <Turntable
            views={[LAT, HEELS]}
            angle={yAngle}
            cx={CENTER.x}
            cy={CENTER.y}
            blur={Math.min(14, yVel * 0.6)}
            sweep={ci(f, [14, 42], [0, 1])}
            glow={0.15}
          />
        ) : (
          <Turntable
            views={[HEELS, SOLE]}
            axis="X"
            angle={xAngle}
            cx={CENTER.x}
            cy={CENTER.y}
            blur={Math.min(14, xVel * 0.6)}
            sweep={ci(f, [58, 90], [0, 1])}
            glow={0.15}
            extra={{ rotate: `${ci(f, [44, 90], [0, -6])}deg` }}
          />
        )}
      </Camera>

      <Sequence from={20} durationInFrames={24} layout="none">
        <Reticle dur={24} lineTo={LABEL_TOP - 20} />
        <Callout index="04" label="الكعب" tagline="بصمة الجوكر" top={LABEL_TOP} dur={24} />
      </Sequence>
      <Sequence from={64} durationInFrames={26} layout="none">
        <Reticle dur={28} lineTo={LABEL_TOP - 20} />
        <Callout index="05" label="النعل الخارجي" tagline="نقشة متعرّجة" top={LABEL_TOP} dur={28} />
      </Sequence>
    </AbsoluteFill>
  );
};
