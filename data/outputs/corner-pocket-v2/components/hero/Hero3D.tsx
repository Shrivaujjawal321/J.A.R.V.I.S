'use client';

import { useRef } from 'react';
import { Canvas, useFrame, useThree } from '@react-three/fiber';
import { Environment, AdaptiveDpr, AdaptiveEvents } from '@react-three/drei';
import { EffectComposer, Bloom, Noise } from '@react-three/postprocessing';
import * as THREE from 'three';
import { SnookerTable } from './SnookerTable';
import { Lights } from './Lights';

// Orbit + mouse parallax controller.
// The camera slowly auto-orbits AND tilts subtly with mouse position.
// Max tilt: ±5deg. This is the "alive but not distracting" range.
function CameraRig({ mouseX, mouseY }: { mouseX: React.MutableRefObject<number>; mouseY: React.MutableRefObject<number> }) {
  const { camera } = useThree();

  // Base orbit angle
  const orbitAngle = useRef(0);
  const targetX = useRef(0);
  const targetY = useRef(0);

  // Camera sits above and slightly in front — viewing the table at ~35deg angle
  const BASE_RADIUS = 6.5;
  const BASE_Y = 4.2;

  useFrame((_, delta) => {
    // Slow auto-orbit: 360° in ~90 seconds
    orbitAngle.current += delta * 0.07;

    const orbitX = Math.sin(orbitAngle.current) * BASE_RADIUS;
    const orbitZ = Math.cos(orbitAngle.current) * BASE_RADIUS;

    // Mouse parallax targets (max ±0.4 units of world displacement)
    targetX.current += (mouseX.current * 0.4 - targetX.current) * 0.05;
    targetY.current += (mouseY.current * 0.3 - targetY.current) * 0.05;

    camera.position.set(
      orbitX + targetX.current,
      BASE_Y + targetY.current,
      orbitZ
    );

    // Always look at the center of the table surface
    camera.lookAt(0, 0.85, 0);
  });

  return null;
}

// Floor plane to catch shadows and add subtle depth
function Floor() {
  return (
    <mesh
      rotation={[-Math.PI / 2, 0, 0]}
      position={[0, 0, 0]}
      receiveShadow
    >
      <planeGeometry args={[30, 30]} />
      <meshStandardMaterial
        color="#080a08"
        roughness={0.9}
        metalness={0}
        envMapIntensity={0.1}
      />
    </mesh>
  );
}

interface Hero3DProps {
  mouseX: React.MutableRefObject<number>;
  mouseY: React.MutableRefObject<number>;
}

export function Hero3D({ mouseX, mouseY }: Hero3DProps) {
  return (
    <Canvas
      shadows
      camera={{ fov: 40, near: 0.1, far: 100, position: [0, 4, 6.5] }}
      gl={{
        antialias: true,
        toneMapping: THREE.ACESFilmicToneMapping,
        toneMappingExposure: 1.1,
        outputColorSpace: THREE.SRGBColorSpace,
      }}
      dpr={[1, 1.5]} // Cap at 1.5x DPR — mobile perf guard
      aria-label="3D snooker table — The Corner Pocket premium club"
      role="img"
    >
      {/* Adaptive DPR drops resolution when frame rate tanks */}
      <AdaptiveDpr pixelated />
      <AdaptiveEvents />

      <CameraRig mouseX={mouseX} mouseY={mouseY} />

      <Lights />

      {/* Nightclub-style environment lighting — just fills, no distracting reflections */}
      <Environment preset="night" />

      <Floor />
      <SnookerTable />

      {/* Subtle postprocessing: bloom on bright brass/gold + film grain */}
      <EffectComposer multisampling={2}>
        <Bloom
          intensity={0.4}
          luminanceThreshold={0.7}
          luminanceSmoothing={0.3}
          radius={0.6}
        />
        <Noise opacity={0.025} />
      </EffectComposer>
    </Canvas>
  );
}
