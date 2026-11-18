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

// Cairo (variable 200–1000) for all Arabic copy.
export const CAIRO = "Cairo";
loadFont({
  family: CAIRO,
  url: staticFile("fonts/cairo-arabic.woff2"),
  weight: "200 1000",
  unicodeRange: "U+0600-06FF, U+0750-077F, U+0870-088E, U+0890-0891, U+0897-08E1, U+08E3-08FF, U+200C-200E, U+2010-2011, U+204F, U+2E41, U+FB50-FDFF, U+FE70-FE74, U+FE76-FEFC",
});
loadFont({
  family: CAIRO,
  url: staticFile("fonts/cairo-latin.woff2"),
  weight: "200 1000",
  unicodeRange: "U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+0304, U+0308, U+0329, U+2000-206F, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD",
});

/** Screen point the detail camera locks onto. */
export const FOCUS = { x: 540, y: 860 };

/** Hard cuts that get a whip-spin transition. */
export const CUTS = [270, 525, 735, 780];

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
