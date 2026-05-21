'use client';

import { useEffect, useRef, useState } from 'react';
import { gsap } from 'gsap';

// Characters are split and animated individually — GSAP SplitText pattern
// implemented manually so we don't need the Club-tier GSAP plugin.
const TITLE = 'THE CORNER POCKET';

export function Loader() {
  const containerRef = useRef<HTMLDivElement>(null);
  const ballRef = useRef<HTMLDivElement>(null);
  const lettersRef = useRef<(HTMLSpanElement | null)[]>([]);
  const curtainRef = useRef<HTMLDivElement>(null);
  const [mounted, setMounted] = useState(false);
  const [done, setDone] = useState(false);

  useEffect(() => {
    setMounted(true);
    document.body.classList.add('is-loading');
  }, []);

  useEffect(() => {
    if (!mounted) return;

    const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    if (reduced) {
      // Skip loader entirely for reduced-motion users
      document.body.classList.remove('is-loading');
      setDone(true);
      return;
    }

    const ctx = gsap.context(() => {
      const tl = gsap.timeline({
        onComplete: () => {
          document.body.classList.remove('is-loading');
          setDone(true);
        },
      });

      // Phase 1: Cue ball rolls in from off-screen left
      tl.fromTo(
        ballRef.current,
        { x: '-120vw', scale: 1, opacity: 1 },
        {
          x: '0vw',
          duration: 0.9,
          ease: 'power3.inOut',
        }
      );

      // Phase 2: Ball "cracks" — scale burst then fragments out
      tl.to(ballRef.current, {
        scale: 3,
        opacity: 0,
        duration: 0.25,
        ease: 'expo.out',
      });

      // Phase 3: Letters assemble one by one from below
      tl.fromTo(
        lettersRef.current.filter(Boolean),
        { y: 60, opacity: 0, rotateX: -80 },
        {
          y: 0,
          opacity: 1,
          rotateX: 0,
          duration: 0.6,
          ease: 'expo.out',
          stagger: 0.04,
        },
        '-=0.1'
      );

      // Hold on title for a beat
      tl.to({}, { duration: 0.5 });

      // Phase 4: Curtain wipes up to reveal hero
      tl.to(curtainRef.current, {
        yPercent: -100,
        duration: 0.9,
        ease: 'power3.inOut',
      });

    }, containerRef);

    return () => ctx.revert();
  }, [mounted]);

  if (done) return null;

  return (
    <div
      ref={containerRef}
      className="fixed inset-0 z-[9999] flex flex-col items-center justify-center overflow-hidden"
      aria-hidden="true"
      role="presentation"
    >
      {/* Main dark background */}
      <div className="absolute inset-0 bg-bg" />

      {/* Curtain panel that wipes upward */}
      <div
        ref={curtainRef}
        className="absolute inset-0 bg-bg z-10"
      />

      {/* Subtle radial felt glow at center — sets the mood */}
      <div
        className="absolute inset-0 pointer-events-none"
        style={{
          background: 'radial-gradient(ellipse 60% 40% at 50% 50%, rgba(14,74,46,0.15) 0%, transparent 70%)',
        }}
      />

      {/* Cue ball — procedural white circle with subtle shading */}
      <div
        ref={ballRef}
        className="absolute"
        style={{
          width: 56,
          height: 56,
          borderRadius: '50%',
          background: 'radial-gradient(circle at 35% 35%, #ffffff 0%, #e8e8e0 60%, #c0c0b8 100%)',
          boxShadow: '0 4px 20px rgba(0,0,0,0.6), inset -4px -4px 8px rgba(0,0,0,0.2)',
          zIndex: 5,
        }}
        aria-hidden="true"
      />

      {/* Title assembly */}
      <div
        className="relative z-5 flex flex-col items-center gap-3"
        style={{ perspective: '600px' }}
      >
        {/* The overline */}
        <div
          className="flex items-center gap-3 mb-2"
          style={{ opacity: 0.5 }}
        >
          <span className="block h-px w-12 bg-gold" />
          <span
            className="font-mono text-xs tracking-[0.4em] text-brass uppercase"
            style={{ fontSize: '0.6rem' }}
          >
            Est. 2018 · Mumbai
          </span>
          <span className="block h-px w-12 bg-gold" />
        </div>

        {/* Character-split title */}
        <div
          className="font-display font-light tracking-[0.15em] text-cream flex"
          style={{ fontSize: 'clamp(1.8rem, 5vw, 4rem)', letterSpacing: '0.12em' }}
          aria-label={TITLE}
        >
          {TITLE.split('').map((char, i) => (
            <span
              key={`${char}-${i}`}
              ref={(el) => { lettersRef.current[i] = el; }}
              style={{
                display: 'inline-block',
                whiteSpace: char === ' ' ? 'pre' : 'normal',
                minWidth: char === ' ' ? '0.4em' : undefined,
              }}
            >
              {char}
            </span>
          ))}
        </div>

        {/* Tagline under title */}
        <div
          className="font-mono text-brass text-xs tracking-[0.3em] uppercase"
          style={{ fontSize: '0.65rem', opacity: 0.7 }}
        >
          Premium Snooker Club
        </div>
      </div>
    </div>
  );
}
