'use client';

import { useMemo } from 'react';
import * as THREE from 'three';
import { BallRack } from './BallRack';

// Snooker table proportions: 12ft × 6ft playfield.
// We use a 1-unit = 0.3m scale: table body ~3.6 × 1.8 units.
const TABLE_W = 1.83; // metres (6ft) → scaled
const TABLE_L = 3.66; // metres (12ft) → scaled
const TABLE_H = 0.08; // play surface height
const CUSHION_H = 0.08;
const CUSHION_W = 0.1;
const RAIL_W = 0.15;
const RAIL_H = 0.14;
const LEG_R = 0.06;
const LEG_H = 0.72;
const POCKET_R = 0.082;

// Materials
function feltMaterial() {
  return new THREE.MeshPhysicalMaterial({
    color: new THREE.Color('#1a6b46'),
    roughness: 0.92,
    metalness: 0,
    clearcoat: 0,
    // Directional felt nap — approximate with anisotropy if available
    envMapIntensity: 0.3,
  });
}

function walnutMaterial() {
  return new THREE.MeshPhysicalMaterial({
    color: new THREE.Color('#3d2817'),
    roughness: 0.6,
    metalness: 0,
    clearcoat: 0.3,
    clearcoatRoughness: 0.2,
  });
}

function brassMaterial() {
  return new THREE.MeshStandardMaterial({
    color: new THREE.Color('#b08d57'),
    metalness: 1.0,
    roughness: 0.2,
    envMapIntensity: 1.2,
  });
}

function cushionMaterial() {
  return new THREE.MeshPhysicalMaterial({
    color: new THREE.Color('#155237'),
    roughness: 0.85,
    metalness: 0,
  });
}

// Pocket ring geometry — a torus sitting at each pocket opening
function PocketRing({ position }: { position: [number, number, number] }) {
  const mat = useMemo(brassMaterial, []);
  const darkMat = useMemo(
    () =>
      new THREE.MeshStandardMaterial({
        color: new THREE.Color('#080a08'),
        roughness: 0.8,
      }),
    []
  );

  return (
    <group position={position}>
      {/* Dark hole */}
      <mesh material={darkMat} rotation={[-Math.PI / 2, 0, 0]}>
        <circleGeometry args={[POCKET_R * 0.9, 24]} />
      </mesh>
      {/* Brass ring */}
      <mesh material={mat} rotation={[-Math.PI / 2, 0, 0]}>
        <torusGeometry args={[POCKET_R, 0.012, 8, 24]} />
      </mesh>
    </group>
  );
}

export function SnookerTable() {
  const felt = useMemo(feltMaterial, []);
  const walnut = useMemo(walnutMaterial, []);
  const cushion = useMemo(cushionMaterial, []);
  const brass = useMemo(brassMaterial, []);

  const halfW = TABLE_W / 2;
  const halfL = TABLE_L / 2;
  const surfaceY = LEG_H + TABLE_H;

  // Pocket positions: 4 corners + 2 mid-rail
  const pocketPositions: [number, number, number][] = [
    [-halfW, surfaceY + 0.001, -halfL],
    [halfW, surfaceY + 0.001, -halfL],
    [-halfW, surfaceY + 0.001, halfL],
    [halfW, surfaceY + 0.001, halfL],
    [-halfW, surfaceY + 0.001, 0],
    [halfW, surfaceY + 0.001, 0],
  ];

  return (
    <group position={[0, 0, 0]}>
      {/* ── Legs ── */}
      {(
        [
          [-halfW + 0.12, 0, -halfL + 0.12],
          [halfW - 0.12, 0, -halfL + 0.12],
          [-halfW + 0.12, 0, halfL - 0.12],
          [halfW - 0.12, 0, halfL - 0.12],
        ] as [number, number, number][]
      ).map((pos, i) => (
        <mesh key={i} position={[pos[0], LEG_H / 2, pos[2]]} material={walnut} castShadow>
          <cylinderGeometry args={[LEG_R, LEG_R * 1.2, LEG_H, 16]} />
        </mesh>
      ))}

      {/* ── Apron / body frame ── */}
      <mesh
        position={[0, LEG_H + TABLE_H / 2, 0]}
        material={walnut}
        castShadow
        receiveShadow
      >
        <boxGeometry args={[TABLE_W + RAIL_W * 2, TABLE_H, TABLE_L + RAIL_W * 2]} />
      </mesh>

      {/* ── Play surface (felt) ── */}
      <mesh
        position={[0, surfaceY, 0]}
        material={felt}
        receiveShadow
      >
        <boxGeometry args={[TABLE_W, 0.008, TABLE_L]} />
      </mesh>

      {/* ── Side rails (walnut) ── */}
      {/* Long sides */}
      <mesh position={[-halfW - RAIL_W / 2, surfaceY + RAIL_H / 2, 0]} material={walnut} castShadow>
        <boxGeometry args={[RAIL_W, RAIL_H, TABLE_L + RAIL_W * 2]} />
      </mesh>
      <mesh position={[halfW + RAIL_W / 2, surfaceY + RAIL_H / 2, 0]} material={walnut} castShadow>
        <boxGeometry args={[RAIL_W, RAIL_H, TABLE_L + RAIL_W * 2]} />
      </mesh>
      {/* Short ends */}
      <mesh position={[0, surfaceY + RAIL_H / 2, -halfL - RAIL_W / 2]} material={walnut} castShadow>
        <boxGeometry args={[TABLE_W, RAIL_H, RAIL_W]} />
      </mesh>
      <mesh position={[0, surfaceY + RAIL_H / 2, halfL + RAIL_W / 2]} material={walnut} castShadow>
        <boxGeometry args={[TABLE_W, RAIL_H, RAIL_W]} />
      </mesh>

      {/* ── Cushions (rubber covered in green) ── */}
      {/* Long cushions — split at mid-pocket (z=0), 2 segments per side */}
      {/* Left side, top half */}
      <mesh position={[-halfW + CUSHION_W / 2, surfaceY + CUSHION_H / 2, -(TABLE_L / 4 + POCKET_R)]} material={cushion}>
        <boxGeometry args={[CUSHION_W, CUSHION_H, TABLE_L / 2 - POCKET_R * 3]} />
      </mesh>
      {/* Left side, bottom half */}
      <mesh position={[-halfW + CUSHION_W / 2, surfaceY + CUSHION_H / 2, TABLE_L / 4 + POCKET_R]} material={cushion}>
        <boxGeometry args={[CUSHION_W, CUSHION_H, TABLE_L / 2 - POCKET_R * 3]} />
      </mesh>
      {/* Right side, top half */}
      <mesh position={[halfW - CUSHION_W / 2, surfaceY + CUSHION_H / 2, -(TABLE_L / 4 + POCKET_R)]} material={cushion}>
        <boxGeometry args={[CUSHION_W, CUSHION_H, TABLE_L / 2 - POCKET_R * 3]} />
      </mesh>
      {/* Right side, bottom half */}
      <mesh position={[halfW - CUSHION_W / 2, surfaceY + CUSHION_H / 2, TABLE_L / 4 + POCKET_R]} material={cushion}>
        <boxGeometry args={[CUSHION_W, CUSHION_H, TABLE_L / 2 - POCKET_R * 3]} />
      </mesh>
      {/* Short cushions (baulk + top ends) */}
      <mesh position={[0, surfaceY + CUSHION_H / 2, -halfL + CUSHION_W / 2]} material={cushion}>
        <boxGeometry args={[TABLE_W - POCKET_R * 4, CUSHION_H, CUSHION_W]} />
      </mesh>
      <mesh position={[0, surfaceY + CUSHION_H / 2, halfL - CUSHION_W / 2]} material={cushion}>
        <boxGeometry args={[TABLE_W - POCKET_R * 4, CUSHION_H, CUSHION_W]} />
      </mesh>

      {/* ── Brass pocket rings ── */}
      {pocketPositions.map((pos, i) => (
        <PocketRing key={i} position={pos} />
      ))}

      {/* ── Brass corner ornaments ── */}
      {(
        [
          [-halfW - RAIL_W * 0.5, surfaceY + RAIL_H, -halfL - RAIL_W * 0.5],
          [halfW + RAIL_W * 0.5, surfaceY + RAIL_H, -halfL - RAIL_W * 0.5],
          [-halfW - RAIL_W * 0.5, surfaceY + RAIL_H, halfL + RAIL_W * 0.5],
          [halfW + RAIL_W * 0.5, surfaceY + RAIL_H, halfL + RAIL_W * 0.5],
        ] as [number, number, number][]
      ).map((pos, i) => (
        <mesh key={i} position={pos} material={brass}>
          <sphereGeometry args={[0.04, 8, 8]} />
        </mesh>
      ))}

      {/* ── Balls ── */}
      <BallRack tableLength={TABLE_L} />
    </group>
  );
}
