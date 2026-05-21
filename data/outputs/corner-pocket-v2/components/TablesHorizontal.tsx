'use client';

import { useEffect, useRef } from 'react';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import { registerGSAP } from '@/lib/gsap';

interface FacilityCard {
  number: string;
  title: string;
  subtitle: string;
  description: string;
  accentColor: string;
}

const FACILITIES: FacilityCard[] = [
  {
    number: '01',
    title: '6 Tournament Snooker Tables',
    subtitle: 'Match-Grade Play',
    description:
      'Strachan 6811 cloth. Humidity-controlled at 55–60% RH. Levelled within 0.5mm. Re-ironed every morning before open.',
    accentColor: '#1a6b46',
  },
  {
    number: '02',
    title: '4 American Pool Tables',
    subtitle: 'Drop & Play',
    description:
      'Brunswick Gold Crown VI. 9-foot slates. Perfect for 8-ball, 9-ball, and straight pool. Walk-in, no reservation needed.',
    accentColor: '#0e4a2e',
  },
  {
    number: '03',
    title: 'Private VIP Room',
    subtitle: 'Members Only',
    description:
      'Two tables in a sound-isolated room. Your own server, your own playlist, your own pace. Book minimum 2 hours.',
    accentColor: '#3d2817',
  },
  {
    number: '04',
    title: 'Lounge Bar',
    subtitle: 'Craft Drinks',
    description:
      'Hand-picked whisky selection, single malts, and a cocktail menu built around snooker heritage. The 147 is our signature.',
    accentColor: '#2d1a0e',
  },
  {
    number: '05',
    title: 'Coaching Studio',
    subtitle: 'Get Sharper',
    description:
      'One table reserved exclusively for lessons. Overhead camera, positional boards, slow-motion playback. Certified WPBSA coaches.',
    accentColor: '#1a4a32',
  },
  {
    number: '06',
    title: 'Pro Shop',
    subtitle: 'The Real Gear',
    description:
      'Curated cues from Peradon, John Parris, and Dennis Wilkins. Chalk, tips, cases, gloves. Staff who know the difference.',
    accentColor: '#4a3010',
  },
  {
    number: '07',
    title: "Members' Library",
    subtitle: 'The Archive',
    description:
      'Match footage from 1985 to present. Instructional libraries. A quiet room for study. Ronnie, Hendry, and O\'Sullivan on screen.',
    accentColor: '#0a1a12',
  },
];

export function TablesHorizontal() {
  const sectionRef = useRef<HTMLDivElement>(null);
  const trackRef = useRef<HTMLDivElement>(null);
  const cardsRef = useRef<(HTMLDivElement | null)[]>([]);

  useEffect(() => {
    registerGSAP();
    const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (reduced) return;

    const ctx = gsap.context(() => {
      const track = trackRef.current;
      const section = sectionRef.current;
      if (!track || !section) return;

      // Total scroll distance = full track width minus viewport width
      const scrollWidth = () => track.scrollWidth - window.innerWidth;

      // Pin the section and translate the track horizontally
      const tl = gsap.timeline({
        scrollTrigger: {
          trigger: section,
          start: 'top top',
          end: () => `+=${scrollWidth()}`,
          pin: true,
          scrub: 1, // 1 second smoothing — not instant, feels physical
          invalidateOnRefresh: true,
          anticipatePin: 1,
        },
      });

      tl.to(track, {
        x: () => -scrollWidth(),
        ease: 'none', // Linear — ScrollTrigger's scrub handles the easing
      });

      // Parallax per card — each card moves at slightly different speed
      cardsRef.current.forEach((card, i) => {
        if (!card) return;
        const depth = 0.04 * (i % 3); // 0, 0.04, or 0.08 depth offset
        gsap.to(card, {
          xPercent: -depth * 20,
          ease: 'none',
          scrollTrigger: {
            trigger: section,
            start: 'top top',
            end: () => `+=${scrollWidth()}`,
            scrub: 1.5,
          },
        });
      });
    }, sectionRef);

    return () => ctx.revert();
  }, []);

  return (
    <section
      id="tables"
      ref={sectionRef}
      className="relative overflow-hidden"
      aria-label="Tables and Facilities"
      style={{ height: '100vh' }}
    >
      {/* Section header — visible above the scroll track */}
      <div className="absolute top-12 left-6 md:left-16 z-10 flex items-center gap-4">
        <span className="gold-rule max-w-[60px]" aria-hidden="true" />
        <span className="font-mono text-xs tracking-[0.35em] text-brass/70 uppercase">
          The Facilities
        </span>
      </div>

      {/* Drag hint */}
      <div
        className="absolute bottom-12 right-8 z-10 hidden md:flex items-center gap-2"
        aria-hidden="true"
      >
        <span className="font-mono text-[0.65rem] tracking-[0.25em] text-brass/50 uppercase">
          Scroll to explore
        </span>
        <div className="flex gap-1">
          {[0, 1, 2].map((i) => (
            <div key={i} className="w-1 h-1 rounded-full bg-brass/40" />
          ))}
        </div>
        <span className="text-brass/50">→</span>
      </div>

      {/* Horizontal track */}
      <div
        ref={trackRef}
        className="horizontal-track absolute top-0 left-0 h-full flex items-center"
        style={{
          width: `${FACILITIES.length * 440 + 200}px`,
          paddingLeft: '8vw',
          paddingRight: '8vw',
          gap: '32px',
        }}
        role="list"
        aria-label="Facility cards — scroll horizontally"
      >
        {/* Big section title — part of the scrolling track for dramatic reveal */}
        <div className="flex-shrink-0 w-64 md:w-80 pr-8">
          <h2
            className="font-display font-light leading-tight text-cream"
            style={{ fontSize: 'clamp(2.8rem, 5vw, 4.5rem)' }}
          >
            Every<br />
            <em className="text-gold-gradient not-italic" style={{ fontStyle: 'italic' }}>
              Detail
            </em>
            <br />
            Earned.
          </h2>
        </div>

        {FACILITIES.map(({ number, title, subtitle, description, accentColor }, i) => (
          <div
            key={number}
            ref={(el) => { cardsRef.current[i] = el; }}
            className="flex-shrink-0 relative overflow-hidden rounded-sm"
            style={{
              width: 380,
              height: 480,
              background: `linear-gradient(135deg, ${accentColor} 0%, rgba(10,13,10,0.95) 100%)`,
              boxShadow: '0 32px 64px rgba(0,0,0,0.5), inset 0 1px 0 rgba(255,255,255,0.04)',
              border: '1px solid rgba(176,141,87,0.12)',
            }}
            role="listitem"
          >
            {/* Top brass accent bar */}
            <div
              className="absolute top-0 left-0 right-0 h-px"
              style={{
                background: 'linear-gradient(90deg, transparent 0%, rgba(212,175,55,0.5) 40%, rgba(212,175,55,0.5) 60%, transparent 100%)',
              }}
              aria-hidden="true"
            />

            <div className="relative z-10 h-full flex flex-col justify-between p-8">
              {/* Number */}
              <div className="flex items-start justify-between">
                <span
                  className="font-mono text-[5rem] font-bold leading-none text-white/[0.06] select-none"
                  aria-hidden="true"
                >
                  {number}
                </span>
                {/* Subtle dot indicator */}
                <div className="w-2 h-2 rounded-full bg-gold/60 mt-2" aria-hidden="true" />
              </div>

              {/* Content */}
              <div>
                <span className="font-mono text-xs tracking-[0.25em] text-brass uppercase block mb-3">
                  {subtitle}
                </span>
                <h3
                  className="font-display font-light text-cream leading-tight mb-4"
                  style={{ fontSize: 'clamp(1.4rem, 2.5vw, 1.8rem)' }}
                >
                  {title}
                </h3>
                <div className="w-8 h-px bg-gold/40 mb-4" aria-hidden="true" />
                <p className="font-body text-cream/60 text-sm leading-relaxed">
                  {description}
                </p>
              </div>
            </div>

            {/* Hover overlay — subtle gold sheen on interactive hover */}
            <div
              className="absolute inset-0 opacity-0 hover:opacity-100 transition-opacity duration-500 pointer-events-none"
              style={{
                background: 'radial-gradient(ellipse at 50% 50%, rgba(212,175,55,0.04) 0%, transparent 70%)',
              }}
              aria-hidden="true"
            />
          </div>
        ))}
      </div>
    </section>
  );
}
