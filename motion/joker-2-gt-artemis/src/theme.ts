import { Easing, interpolate, random, staticFile } from "remotion";
import { loadFont } from "@remotion/fonts";

// Google Fonts (OFL), bundled locally in public/fonts so renders work offline.
export const ANTON = "Anton";
export const INTER = "Inter";
export const MONO = "Space Mono";

loadFont({ family: ANTON, url: staticFile("fonts/anton.woff2"), weight: "400" });
loadFont({ family: INTER, url: staticFile("fonts/inter800.woff2"), weight: "800" });
loadFont({ family: MONO, url: staticFile("fonts/mono400.woff2"), weight: "400" });
loadFont({ family: MONO, url: staticFile("fonts/mono700.woff2"), weight: "700" });

export const W = 1080;
export const H = 1920;
export const FPS = 30;

export const OUT = Easing.bezier(0.16, 1, 0.3, 1);
export const IN = Easing.bezier(0.7, 0, 0.84, 0);
export const INOUT = Easing.bezier(0.65, 0, 0.35, 1);

/** Clamped interpolate. */
export const ci = (
  f: number,
  input: number[],
  output: number[],
  easing?: (t: number) => number,
) =>
  interpolate(f, input, output, {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing,
  });

/** Decaying camera shake starting at `start`. */
export const shake = (f: number, start: number, dur: number, amp: number) => {
  const t = f - start;
  if (t < 0 || t > dur) return { x: 0, y: 0 };
  const k = amp * Math.pow(1 - t / dur, 2);
  return {
    x: (random(`sx${Math.floor(f)}`) - 0.5) * 2 * k,
    y: (random(`sy${Math.floor(f)}`) - 0.5) * 2 * k,
  };
};
