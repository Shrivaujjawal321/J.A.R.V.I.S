'use client';

import { useRef, useMemo } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';

// Snooker ball colors: 15 reds + 6 colours + cue ball = 22 total.
// We render the full triangle rack of 15 reds in a 5-row triangle,
// plus the 6 colour balls at their proper spots, plus the cue ball.

// Standard snooker ball colors
const BALL_COLORS = {
  red: '#c8102e',
  yellow: '#f0c010',
  green: '#00843d',
  brown: '#7b3f00',
  blue: '#005db9',
  pink: '#ee82b4',
  black: '#111111',
  cue: '#fffdf8',
} as const;

// Material for each ball type
function useBallMaterial(color: string, roughness = 0.25) {
  return useMemo(() => {
    const mat = new THREE.MeshPhysicalMaterial({
      color: new THREE.Color(color),
      roughness,
      metalness: 0,
      reflectivity: 0.6,
      clearcoat: 0.8,
      clearcoatRoughness: 0.1,
    });
    return mat;
  }, [color, roughness]);
}

interface BallProps {
  position: [number, number, number];
  color: string;
  radius?: number;
}

function Ball({ position, color, radius = 0.0525 }: BallProps) {
  const meshRef = useRef<THREE.Mesh>(null);
  const mat = useBallMaterial(color);

  return (
    <mesh ref={meshRef} position={position} castShadow receiveShadow material={mat}>
      <sphereGeometry args={[radius, 32, 32]} />
    </mesh>
  );
}

// Rack triangle: 5 rows (1+2+3+4+5 = 15 reds)
// Positioned at the spot (2/3 down the table from the baulk end)
function RedRack({ tableLength }: { tableLength: number }) {
  const positions = useMemo<[number, number, number][]>(() => {
    const R = 0.0525; // ball radius
    const D = R * 2 * 1.02; // slight gap
    const rootX = 0;
    const rootZ = tableLength * 0.25; // "top" of table
    const y = 0.0525;
    const pts: [number, number, number][] = [];

    for (let row = 0; row < 5; row++) {
      const count = row + 1;
      const startX = -(D * row) / 2;
      for (let col = 0; col < count; col++) {
        pts.push([
          rootX + startX + col * D,
          y,
          rootZ + row * D * 0.866, // equilateral triangle packing
        ]);
      }
    }
    return pts;
  }, [tableLength]);

  return (
    <>
      {positions.map((pos, i) => (
        <Ball key={i} position={pos} color={BALL_COLORS.red} />
      ))}
    </>
  );
}

interface BallRackProps {
  tableLength: number;
}

export function BallRack({ tableLength }: BallRackProps) {
  const baulkZ = -tableLength * 0.35;

  return (
    <group>
      {/* 15 reds in triangle */}
      <RedRack tableLength={tableLength} />

      {/* Colour balls at their spots */}
      <Ball position={[0, 0.0525, tableLength * 0.25 + 0.32]} color={BALL_COLORS.pink} />
      <Ball position={[0, 0.0525, 0]} color={BALL_COLORS.blue} />
      <Ball position={[0, 0.0525, -tableLength * 0.27]} color={BALL_COLORS.black} />

      {/* Baulk line colours */}
      <Ball position={[-0.32, 0.0525, baulkZ]} color={BALL_COLORS.yellow} />
      <Ball position={[0, 0.0525, baulkZ]} color={BALL_COLORS.green} />
      <Ball position={[0.32, 0.0525, baulkZ]} color={BALL_COLORS.brown} />

      {/* Cue ball — in the D */}
      <Ball position={[0, 0.0525, baulkZ - 0.3]} color={BALL_COLORS.cue} />
    </group>
  );
}
