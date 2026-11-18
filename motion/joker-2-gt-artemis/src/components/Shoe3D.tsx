import React, { useEffect, useMemo, useState } from "react";
import { ThreeCanvas } from "@remotion/three";
import * as THREE from "three";
import { cancelRender, continueRender, delayRender, staticFile } from "remotion";
import { H, W } from "../theme";
import { NATURAL, ShoeName } from "./Rig";

/**
 * 2.5D product rendering: each genuine product photo becomes a relief mesh,
 * displaced by a monocular depth map (Depth Anything V2) blended with a
 * silhouette inflation, and re-lit per frame so turning reveals real volume.
 * No product geometry or texture is invented.
 */

const NAMES: ShoeName[] = ["lateral", "medial", "heels", "sole"];
const FOV = 30;
export const CAM_Z = H / 2 / Math.tan(((FOV / 2) * Math.PI) / 180);

type Tex = Record<ShoeName, { map: THREE.Texture; depth: THREE.Texture; normal: THREE.Texture }>;

const useShoeTextures = () => {
  const [tex, setTex] = useState<Tex | null>(null);
  const [handle] = useState(() => delayRender("Loading shoe textures"));
  useEffect(() => {
    const loader = new THREE.TextureLoader();
    const load = (url: string) =>
      new Promise<THREE.Texture>((res, rej) => loader.load(url, res, undefined, rej));
    Promise.all(
      NAMES.flatMap((n) => [
        load(staticFile(`shoe_${n}.png`)),
        load(staticFile(`depth_${n}.png`)),
        load(staticFile(`normal_${n}.png`)),
      ]),
    )
      .then((arr) => {
        const out = {} as Tex;
        NAMES.forEach((n, i) => {
          const map = arr[3 * i];
          map.anisotropy = 8;
          map.generateMipmaps = true;
          map.minFilter = THREE.LinearMipmapLinearFilter;
          map.magFilter = THREE.LinearFilter;
          out[n] = { map, depth: arr[3 * i + 1], normal: arr[3 * i + 2] };
        });
        setTex(out);
      })
      .catch((e) => cancelRender(e));
  }, [handle]);
  // release the render only after the meshes had a chance to draw with the textures
  useEffect(() => {
    if (!tex) return;
    let r2 = 0;
    const r1 = requestAnimationFrame(() => {
      r2 = requestAnimationFrame(() => continueRender(handle));
    });
    return () => {
      cancelAnimationFrame(r1);
      cancelAnimationFrame(r2);
    };
  }, [tex, handle]);
  return tex;
};

const vertex = /* glsl */ `
  uniform sampler2D depthMap;
  uniform float depthScale;
  varying vec2 vUv;
  varying vec3 vViewPos;
  void main() {
    vUv = uv;
    float d = texture2D(depthMap, uv).r;
    vec3 p = position + vec3(0.0, 0.0, (d - 0.45) * depthScale);
    vec4 mv = modelViewMatrix * vec4(p, 1.0);
    vViewPos = mv.xyz;
    gl_Position = projectionMatrix * mv;
  }
`;

const fragment = /* glsl */ `
  uniform sampler2D map;
  uniform sampler2D normalMap;
  uniform mat3 rot;
  uniform vec3 lightDir;
  uniform float opacity;
  uniform float sweep;
  uniform float flare;
  varying vec2 vUv;
  varying vec3 vViewPos;
  void main() {
    vec4 c = texture2D(map, vUv);
    if (c.a < 0.5) discard;
    vec3 n = normalize(rot * (texture2D(normalMap, vUv).rgb * 2.0 - 1.0));
    vec3 L = normalize(lightDir);
    vec3 V = normalize(-vViewPos);
    float diff = max(dot(n, L), 0.0);
    float spec = pow(max(dot(n, normalize(L + V)), 0.0), 36.0);
    float rim = pow(1.0 - max(dot(n, V), 0.0), 2.5);
    vec3 col = c.rgb * (0.52 + 0.46 * diff) + spec * 0.1 + rim * vec3(0.45, 0.65, 1.0) * 0.32;
    float band = vUv.x * 0.85 + vUv.y * 0.3;
    col += smoothstep(0.1, 0.0, abs(band - sweep)) * 0.32;
    col += flare;
    gl_FragColor = vec4(col, opacity);
  }
`;

export type ShoeItem = {
  name: ShoeName;
  /** on-screen width in px at zoom 1 */
  width: number;
  /** screen centre in px */
  x: number;
  y: number;
  /** depth offset in px (towards camera is positive) */
  z?: number;
  /** degrees */
  rx?: number;
  ry?: number;
  rz?: number;
  opacity?: number;
  sweep?: number;
  flare?: number;
  key?: string;
};

const ShoeMesh: React.FC<{ item: ShoeItem; tex: Tex; light: [number, number, number] }> = ({ item, tex, light }) => {
  const nat = NATURAL[item.name];
  const h = (nat.h / nat.w) * item.width;
  const depthScale = item.width * 0.3;
  const geo = useMemo(() => new THREE.PlaneGeometry(1, 1, 360, 180), []);
  const mat = useMemo(
    () =>
      new THREE.ShaderMaterial({
        vertexShader: vertex,
        fragmentShader: fragment,
        transparent: true,
        toneMapped: false,
        uniforms: {
          map: { value: null },
          depthMap: { value: null },
          normalMap: { value: null },
          depthScale: { value: 1 },
          rot: { value: new THREE.Matrix3() },
          lightDir: { value: new THREE.Vector3() },
          opacity: { value: 1 },
          sweep: { value: -1 },
          flare: { value: 0 },
        },
      }),
    [],
  );
  const euler = new THREE.Euler(
    ((item.rx ?? 0) * Math.PI) / 180,
    ((item.ry ?? 0) * Math.PI) / 180,
    ((item.rz ?? 0) * Math.PI) / 180,
  );
  const t = tex[item.name];
  mat.uniforms.map.value = t.map;
  mat.uniforms.depthMap.value = t.depth;
  mat.uniforms.normalMap.value = t.normal;
  mat.uniforms.depthScale.value = depthScale;
  mat.uniforms.rot.value.setFromMatrix4(new THREE.Matrix4().makeRotationFromEuler(euler));
  mat.uniforms.lightDir.value.set(...light);
  mat.uniforms.opacity.value = item.opacity ?? 1;
  mat.uniforms.sweep.value = item.sweep ?? -1;
  mat.uniforms.flare.value = item.flare ?? 0;
  mat.depthWrite = (item.opacity ?? 1) > 0.98;

  return (
    <group position={[item.x - W / 2, H / 2 - item.y, item.z ?? 0]} rotation={euler}>
      {/* scale x/y only; z displacement is already in px via depthScale */}
      <mesh geometry={geo} material={mat} scale={[item.width, h, 1]} />
    </group>
  );
};

/** Full-frame transparent WebGL layer rendering one or more shoe meshes. */
export const ShoeStage: React.FC<{
  items: ShoeItem[];
  light?: [number, number, number];
  style?: React.CSSProperties;
}> = ({ items, light = [-0.5, 0.6, 0.65], style }) => {
  const tex = useShoeTextures();
  return (
    <div style={{ position: "absolute", inset: 0, ...style }}>
      <ThreeCanvas
        width={W}
        height={H}
        camera={{ fov: FOV, position: [0, 0, CAM_Z], near: 10, far: CAM_Z * 4 }}
        gl={{ antialias: true, alpha: true, premultipliedAlpha: false }}
      >
        {tex
          ? items
              .filter((it) => (it.opacity ?? 1) > 0.01)
              .map((it, i) => <ShoeMesh key={it.key ?? `${it.name}-${i}`} item={it} tex={tex} light={light} />)
          : null}
      </ThreeCanvas>
    </div>
  );
};

/** Smoothstep helper. */
const ss = (a: number, b: number, x: number) => {
  const t = Math.max(0, Math.min(1, (x - a) / (b - a)));
  return t * t * (3 - 2 * t);
};

/**
 * A 3D turn from view A to view B: A keeps rotating away while B rotates in
 * from the other side; the hand-off happens at peak speed (hidden by blur).
 * Returns the mesh items plus a blur amount for the stage.
 */
export const turn = (
  p: number,
  a: Omit<ShoeItem, "opacity">,
  b: Omit<ShoeItem, "opacity">,
  axis: "x" | "y" = "y",
  amount = 60,
) => {
  const key = axis === "y" ? "ry" : "rx";
  const ia: ShoeItem = { ...a, key: "A", [key]: ((a as ShoeItem)[key] ?? 0) + amount * p, opacity: 1 - ss(0.4, 0.6, p) };
  const ib: ShoeItem = {
    ...b,
    key: "B",
    [key]: ((b as ShoeItem)[key] ?? 0) - amount * (1 - p),
    opacity: ss(0.4, 0.6, p),
  };
  const peak = 1 - Math.abs(p - 0.5) * 2;
  return { items: [ia, ib], blur: peak * peak * 12, flare: peak * 0.25 };
};
