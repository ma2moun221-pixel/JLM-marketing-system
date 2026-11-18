import React from "react";
import { Audio } from "@remotion/media";
import { AbsoluteFill, Sequence, staticFile } from "remotion";
import { Finish, Flash, Space } from "./components/Space";
import { Athlete } from "./scenes/Athlete";
import { Countdown } from "./scenes/Countdown";
import { HeelDetail, SoleDetail, UpperDetail } from "./scenes/Details";
import { Landing } from "./scenes/Landing";
import { Reveal } from "./scenes/Reveal";

/**
 * 361° JOKER 2 GT "ARTEMIS" — 15s vertical motion spot (1080x1920, 30fps).
 * Every cut lands on the 120 BPM grid of the soundtrack (15 frames per beat).
 */
export const JokerArtemis: React.FC = () => {
  return (
    <AbsoluteFill style={{ backgroundColor: "#050505" }}>
      <Space />
      <Sequence name="Countdown" from={0} durationInFrames={60}>
        <Countdown />
      </Sequence>
      <Sequence name="Reveal" from={60} durationInFrames={90}>
        <Reveal />
      </Sequence>
      <Sequence name="Upper" from={150} durationInFrames={75}>
        <UpperDetail />
      </Sequence>
      <Sequence name="Outsole" from={225} durationInFrames={60}>
        <SoleDetail />
      </Sequence>
      <Sequence name="Heel" from={285} durationInFrames={45}>
        <HeelDetail />
      </Sequence>
      <Sequence name="Athlete" from={330} durationInFrames={45}>
        <Athlete />
      </Sequence>
      <Sequence name="Landing" from={375} durationInFrames={75}>
        <Landing />
      </Sequence>

      <Flash at={60} peak={1} len={14} />
      <Flash at={150} peak={0.45} len={6} />
      <Flash at={225} peak={0.45} len={6} />
      <Flash at={285} peak={0.45} len={6} />
      <Flash at={330} peak={0.6} len={6} />
      <Flash at={375} peak={0.5} len={6} />
      <Flash at={393} peak={0.75} len={10} />

      <Finish />
      <Audio src={staticFile("soundtrack.wav")} />
    </AbsoluteFill>
  );
};
