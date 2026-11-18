import React from "react";
import { AbsoluteFill, Sequence, useCurrentFrame } from "remotion";
import { Callout, Reticle } from "../components/Callout";
import { camPath, place } from "../components/Cam3D";
import { pt, View } from "../components/Rig";
import { ShoeItem, ShoeStage, turn } from "../components/Shoe3D";
import { ci, FOCUS, INOUT } from "../theme";

const LAT: View = { name: "lateral", width: 900 };
const HEELS: View = { name: "heels", width: 660 };
const SOLE: View = { name: "sole", width: 900 };

const CENTER = { x: 540, y: 960 };
const CAGE = pt(LAT, 600, 200);
const LOGO = pt(LAT, 483, 250);
const PODS = pt(LAT, 492, 398);
const EMBLEM = pt(HEELS, 182, 185);
const HERRING = pt(SOLE, 150, 195);

const LABEL_TOP = 1330;

/** Darkens everything outside the focus ring while zoomed in. */
const FocusVignette: React.FC<{ s: number }> = ({ s }) => (
  <AbsoluteFill
    style={{
      background: `radial-gradient(circle 420px at ${FOCUS.x}px ${FOCUS.y}px, rgba(3,4,11,0) 55%, rgba(3,4,11,0.62) 100%)`,
      opacity: ci(s, [1.15, 2], [0, 1]),
    }}
  />
);

/** 270–525 (255f): 3D macro camera glides between three details of the upper. */
export const UpperDetails: React.FC = () => {
  const f = useCurrentFrame();
  const frames = [0, 18, 78, 96, 156, 174, 247, 255];
  const cam = camPath(
    f,
    frames,
    [CENTER, CAGE, CAGE, LOGO, LOGO, PODS, PODS, CENTER],
    [1, 2.3, 2.4, 2.7, 2.8, 2.2, 2.35, 1.6],
    [0, -18, -8, 16, 6, -14, -4, 0],
    [0, 8, 5, -5, -2, 12, 6, 0],
  );
  const prev = camPath(
    f - 1,
    frames,
    [CENTER, CAGE, CAGE, LOGO, LOGO, PODS, PODS, CENTER],
    [1, 2.3, 2.4, 2.7, 2.8, 2.2, 2.35, 1.6],
    [0, -18, -8, 16, 6, -14, -4, 0],
    [0, 8, 5, -5, -2, 12, 6, 0],
  );
  const speed = Math.hypot(cam.P.x - prev.P.x, cam.P.y - prev.P.y) * cam.s;
  return (
    <AbsoluteFill>
      <ShoeStage
        items={[place(LAT, cam, { sweep: ci(f, [0, 255], [-0.2, 1.3]) })]}
        light={[-0.6 + 0.3 * Math.sin(f / 50), 0.55, 0.6]}
        style={{ filter: speed > 3 ? `blur(${Math.min(7, speed / 8)}px)` : undefined }}
      />
      <FocusVignette s={cam.s} />

      <Sequence from={18} durationInFrames={60} layout="none">
        <Reticle dur={60} lineTo={LABEL_TOP - 20} />
        <Callout index="01" label="وجه البوط" tagline="تفاصيل بتجنّن" top={LABEL_TOP} dur={60} />
      </Sequence>
      <Sequence from={96} durationInFrames={60} layout="none">
        <Reticle dur={60} lineTo={LABEL_TOP - 20} />
        <Callout index="02" label="اللوغو" tagline="لوغو الجوكر" top={LABEL_TOP} dur={60} />
      </Sequence>
      <Sequence from={174} durationInFrames={75} layout="none">
        <Reticle dur={75} lineTo={LABEL_TOP - 20} />
        <Callout index="03" label="النعل من النص" tagline="خطوطه ناعمة" top={LABEL_TOP} dur={75} />
      </Sequence>
    </AbsoluteFill>
  );
};

/** 525–735 (210f): 3D turn to the heel and focus; 3D flip to the outsole and focus. */
export const TurnDetails: React.FC = () => {
  const f = useCurrentFrame();
  const cam = camPath(
    f,
    [0, 16, 32, 100, 112, 122, 138, 210],
    [CENTER, CENTER, EMBLEM, EMBLEM, CENTER, CENTER, HERRING, HERRING],
    [1, 1, 2.2, 2.3, 1, 1, 2.3, 2.45],
    [0, 0, -16, 10, 0, 0, 14, -6],
    [0, 6, 8, 4, 6, 0, -10, -4],
  );

  let items: ShoeItem[];
  let blur = 0;
  if (f <= 16) {
    const r = turn(ci(f, [0, 16], [0, 1], INOUT), place(LAT, cam), place(HEELS, cam));
    items = r.items.map((it) => ({ ...it, flare: r.flare }));
    blur = r.blur;
  } else if (f < 104) {
    items = [place(HEELS, cam, { sweep: ci(f, [30, 100], [-0.2, 1.3]) })];
  } else if (f <= 122) {
    const r = turn(ci(f, [104, 122], [0, 1], INOUT), place(HEELS, cam), place(SOLE, cam), "x", 70);
    items = r.items.map((it) => ({ ...it, flare: r.flare }));
    blur = r.blur;
  } else {
    items = [place(SOLE, cam, { sweep: ci(f, [130, 210], [-0.2, 1.3]) })];
  }

  return (
    <AbsoluteFill>
      <ShoeStage
        items={items}
        light={[-0.5, 0.6 + 0.2 * Math.sin(f / 40), 0.65]}
        style={{ filter: blur > 0.3 ? `blur(${blur}px)` : undefined }}
      />
      <FocusVignette s={cam.s} />

      <Sequence from={32} durationInFrames={68} layout="none">
        <Reticle dur={68} lineTo={LABEL_TOP - 20} />
        <Callout index="04" label="الكعب" tagline="حتى من ورا مرتّب" size={106} top={LABEL_TOP} dur={68} />
      </Sequence>
      <Sequence from={138} durationInFrames={72} layout="none">
        <Reticle dur={72} lineTo={LABEL_TOP - 20} />
        <Callout index="05" label="النعل من تحت" tagline="شوف هالنقشة" size={112} top={LABEL_TOP} dur={72} />
      </Sequence>
    </AbsoluteFill>
  );
};
