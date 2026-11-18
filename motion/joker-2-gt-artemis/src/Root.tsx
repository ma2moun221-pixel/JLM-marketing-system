import React from "react";
import { Composition } from "remotion";
import { JokerArtemis } from "./JokerArtemis";

export const RemotionRoot: React.FC = () => {
  return (
    <Composition
      id="JokerArtemis"
      component={JokerArtemis}
      durationInFrames={900}
      fps={30}
      width={1080}
      height={1920}
    />
  );
};
