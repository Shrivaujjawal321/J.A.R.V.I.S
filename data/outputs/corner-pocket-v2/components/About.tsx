'use client';

import { useEffect, useRef } from 'react';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import { registerGSAP } from '@/lib/gsap';

const PANELS = [
  {
    number: '01',
    title: 'The Room Where\nGreat Games Live',
    body:
      'Twelve years ago, a small group of Mumbaikars wanted one thing: a place to play seriously. No distractions, no noise, no compromise on equipment. A room that respected the game as much as they did.',
  },
  {
    number: '02',
    title: 'Tournament Grade,\nEvery Night',
    body:
      'Six Strachan 6811 cloth tables. Humidity-controlled. Re-ironed every morning. The same cloth you\'ll find at the National Championship — because your practice should feel like the real thing.',
  },
  {
    number: '03',
    title: 'More Than\na Snooker Club',
    body:
      'A craft bar. A coaching studio. A members\' library stocked with match footage going back to the 1985 World Championship. The Corner Pocket is where Mumbai\'s players — serious and social alike — call home.',
  },
] as const;

export function About() {
  const sectionRef = useRef<HTMLDivElement>(null);
  const panelsRef = useRef<(HTMLDivElement | null)[]>([]);
  const bgRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    registerGSAP();
    const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (reduced) return;

    const ctx = gsap.context(() => {
      // Each panel pins for ~600px of scroll, then releases to next
      panelsRef.current.forEach((panel, i) => {
        if (!panel) return;

        // Pin + fade in on entry
        ScrollTrigger.create({
          trigger: panel,
          start: 'top 70%',
          onEnter: () => {
            gsap.to(panel, {
              opacity: 1,
              y: 0,
              duration: 0.9,
              ease: 'expo.out',
            });
          },
        });

        // Background hue shift as panels progress
        ScrollTrigger.create({
          trigger: panel,
          start: 'top center',
          end: 'bottom center',
          onUpdate: (self) => {
            if (!bgRef.current) return;
            // Transition from near-black → felt-green across panels
            const progress = (i + self.progress) / PANELS.length;
            const r = Math.round(10 + progress * 4);
            const g = Math.round(13 + progress * 61);
            const b = Math.round(10 + progress * 4);
            bgRef.current.style.backgroundColor = `rgb(${r},${g},${b})`;
          },
        });
      });
    }, sectionRef);

    return () => ctx.revert();
  }, []);

  return (
    <section
      id="about"
      ref={sectionRef}
      className="relative py-32 md:py-48 overflow-hidden"
      aria-label="About The Corner Pocket"
    >
      {/* Morphing background */}
      <div
        ref={bgRef}
        className="absolute inset-0 transition-colors duration-700"
        style={{ backgroundColor: '#0a0d0a' }}
        aria-hidden="true"
      />

      {/* Subtle felt texture overlay */}
      <div
        className="absolute inset-0 pointer-events-none"
        aria-hidden="true"
        style={{
          backgroundImage:
            'repeating-linear-gradient(0deg, transparent, transparent 3px, rgba(255,255,255,0.008) 3px, rgba(255,255,255,0.008) 4px)',
        }}
      />

      <div className="relative z-10 max-w-screen-xl mx-auto px-6 md:px-16">
        {/* Section label */}
        <div className="flex items-center gap-4 mb-20">
          <span className="gold-rule max-w-[80px]" aria-hidden="true" />
          <span className="font-mono text-xs tracking-[0.35em] text-brass/70 uppercase">
            Our Story
          </span>
        </div>

        {/* Panels */}
        <div className="flex flex-col gap-32 md:gap-48">
          {PANELS.map(({ number, title, body }, i) => (
            <div
              key={number}
              ref={(el) => { panelsRef.current[i] = el; }}
              className="max-w-3xl"
              style={{
                opacity: 0,
                transform: 'translateY(60px)',
              }}
            >
              {/* Panel number */}
              <span
                className="font-mono text-[8rem] font-bold leading-none text-felt-mid/20 select-none block mb-0 -ml-4"
                aria-hidden="true"
              >
                {number}
              </span>

              {/* Title */}
              <h2
                className="font-display font-light leading-tight text-cream -mt-10 mb-6"
                style={{ fontSize: 'clamp(2.2rem, 5vw, 4rem)', whiteSpace: 'pre-line' }}
              >
                {title}
              </h2>

              {/* Gold rule under title */}
              <div className="gold-rule max-w-[160px] mb-6" aria-hidden="true" />

              {/* Body */}
              <p
                className="font-body text-cream/65 leading-relaxed max-w-lg"
                style={{ fontSize: 'clamp(1rem, 1.5vw, 1.125rem)' }}
              >
                {body}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
