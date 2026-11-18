import * as THREE from "three";
import { ci, FOCUS, INOUT } from "../theme";
import { View } from "./Rig";
import { ShoeItem } from "./Shoe3D";

export type Cam = { P: { x: number; y: number }; s: number; rx: number; ry: number; rz?: number };

const D2R = Math.PI / 180;

/**
 * Macro camera for a 3D shoe view centred at (540, 960) at zoom 1:
 * scales by `s`, rotates, and moves so the surface point under screen point P lands on FOCUS.
 */
export const place = (v: View, cam: Cam, extra?: Partial<ShoeItem>): ShoeItem => {
  const depthScale = v.width * 0.3;
  const vec = new THREE.Vector3(cam.P.x - 540, -(cam.P.y - 960), 0.4 * depthScale);
  vec.applyEuler(new THREE.Euler(cam.rx * D2R, cam.ry * D2R, (cam.rz ?? 0) * D2R));
  const fx = FOCUS.x - 540;
  const fy = 960 - FOCUS.y;
  return {
    name: v.name,
    width: v.width * cam.s,
    x: 540 + (fx - cam.s * vec.x),
    y: 960 - (fy - cam.s * vec.y),
    z: -cam.s * vec.z,
    rx: cam.rx,
    ry: cam.ry,
    rz: cam.rz ?? 0,
    ...extra,
  };
};

/** Keyframed camera path with smooth in-out segments. */
export const camPath = (
  f: number,
  frames: number[],
  pts: { x: number; y: number }[],
  scales: number[],
  rys: number[],
  rxs: number[],
): Cam => ({
  P: { x: ci(f, frames, pts.map((p) => p.x), INOUT), y: ci(f, frames, pts.map((p) => p.y), INOUT) },
  s: ci(f, frames, scales, INOUT),
  ry: ci(f, frames, rys, INOUT),
  rx: ci(f, frames, rxs, INOUT),
});
