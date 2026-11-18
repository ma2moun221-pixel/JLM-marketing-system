import React from "react";
import { Audio } from "@remotion/media";
import { AbsoluteFill, Sequence, staticFile } from "remotion";
import { Finish, Flash, Space, WhipCamera } from "./components/Space";
import { Athlete } from "./scenes/Athlete";
import { Countdown } from "./scenes/Countdown";
import { TurnDetails, UpperDetails } from "./scenes/Details";
import { Finale } from "./scenes/Finale";
import { Reveal } from "./scenes/Reveal";

/**
 * 361° JOKER 2 GT "ARTEMIS" — 30s vertical motion spot, Palestinian Arabic (1080x1920, 30fps).
 * Every cut lands on the 120 BPM grid of the soundtrack (15 frames per beat)
 * and is hidden by a whip-spin camera move.
 */
export const JokerArtemis: React.FC = () => {
  return (
    <AbsoluteFill style={{ backgroundColor: "#03040b" }}>
      <Space />
      <WhipCamera>
        <Sequence name="Countdown" from={0} durationInFrames={90}>
          <Countdown />
        </Sequence>
        <Sequence name="Reveal + 3D turns" from={90} durationInFrames={180}>
          <Reveal />
        </Sequence>
        <Sequence name="Details 01–03" from={270} durationInFrames={255}>
          <UpperDetails />
        </Sequence>
        <Sequence name="Details 04–05" from={525} durationInFrames={210}>
          <TurnDetails />
        </Sequence>
        <Sequence name="Athlete" from={735} durationInFrames={45}>
          <Athlete />
        </Sequence>
        <Sequence name="Finale" from={780} durationInFrames={120}>
          <Finale />
        </Sequence>
      </WhipCamera>

      <Flash at={90} peak={1} len={14} />
      <Flash at={270} peak={0.3} len={6} />
      <Flash at={525} peak={0.3} len={6} />
      <Flash at={735} peak={0.4} len={6} />
      <Flash at={795} peak={0.85} len={12} />

      <Finish />
      <Audio src={staticFile("soundtrack.wav")} />
    </AbsoluteFill>
  );
};
