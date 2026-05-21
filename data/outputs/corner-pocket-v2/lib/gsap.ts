'use client';

import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import { ScrollToPlugin } from 'gsap/ScrollToPlugin';

let registered = false;

export function registerGSAP(): void {
  if (registered || typeof window === 'undefined') return;
  gsap.registerPlugin(ScrollTrigger, ScrollToPlugin);
  registered = true;
}

// Wrap any GSAP animation with reduced-motion respect.
// If prefers-reduced-motion is set, run the to-values immediately with duration 0.
export function motionSafe(
  fn: () => gsap.core.Tween | gsap.core.Timeline | null | undefined
): gsap.core.Tween | gsap.core.Timeline | null {
  if (typeof window === 'undefined') return null;
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (reduced) {
    // Execute fn but override all durations to 0 so end-state is still applied
    gsap.globalTimeline.timeScale(1000);
    const anim = fn() ?? null;
    gsap.globalTimeline.timeScale(1);
    return anim;
  }
  return fn() ?? null;
}

// Eases used across the site — named for consistency
export const ease = {
  expoOut: 'expo.out',
  power3InOut: 'power3.inOut',
  power2Out: 'power2.out',
  back: 'back.out(1.7)',
} as const;

export { gsap, ScrollTrigger };
