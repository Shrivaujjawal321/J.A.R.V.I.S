'use client';

import { useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';

// Tungsten key light from above + brass-tinted rim light + dim felt-green fill.
// The subtle breathing on the key light makes the scene feel alive without being distracting.
export function Lights() {
  const keyLightRef = useRef<THREE.DirectionalLight>(null);
  const t = useRef(0);

  useFrame((_, delta) => {
    t.current += delta * 0.4;
    if (keyLightRef.current) {
      // Gentle intensity breath — 0.05 amplitude so it's subliminal
      keyLightRef.current.intensity = 2.2 + Math.sin(t.current) * 0.05;
    }
  });

  return (
    <>
      {/* Ambient — very low, keeps shadows from going pitch black */}
      <ambientLight intensity={0.12} color="#1a2a1a" />

      {/* Key light — warm tungsten from above and slightly front */}
      <directionalLight
        ref={keyLightRef}
        position={[3, 8, 4]}
        intensity={2.2}
        color="#ffe4b0"
        castShadow
        shadow-mapSize-width={1024}
        shadow-mapSize-height={1024}
        shadow-camera-near={0.5}
        shadow-camera-far={30}
        shadow-camera-left={-6}
        shadow-camera-right={6}
        shadow-camera-top={6}
        shadow-camera-bottom={-6}
        shadow-bias={-0.001}
      />

      {/* Rim light — brass-gold from camera-right, catches the pocket rings */}
      <directionalLight
        position={[-5, 2, -2]}
        intensity={0.9}
        color="#c8973a"
      />

      {/* Fill — subtle blue-green from below, like light bouncing off the felt */}
      <directionalLight
        position={[0, -3, 5]}
        intensity={0.3}
        color="#1a4a32"
      />

      {/* Overhead point for the pockets — small pools of highlight */}
      <pointLight position={[-3.2, 3, -1.8]} intensity={0.6} color="#ffe4b0" distance={5} />
      <pointLight position={[3.2, 3, -1.8]} intensity={0.6} color="#ffe4b0" distance={5} />
      <pointLight position={[0, 3, 1.8]} intensity={0.4} color="#ffe4b0" distance={5} />
    </>
  );
}
