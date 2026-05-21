'use client';

import { useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import Image from 'next/image';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import { registerGSAP } from '@/lib/gsap';

const COACHING_POINTS = [
  { title: 'WPBSA Certified Coaches', desc: 'Our coaches hold World Professional Billiards and Snooker Association certification.' },
  { title: 'Video Analysis', desc: 'Overhead camera captures your technique. Frame-by-frame review shows exactly what needs work.' },
  { title: 'Custom Programmes', desc: 'From beginner fundamentals to tournament prep. Programmes built around your schedule and goals.' },
  { title: 'Group Sessions', desc: 'Saturday morning group sessions: 4 players, 2 hours, ₹800 per player. Great for mixed-level friends.' },
] as const;

export function Coaching() {
  const sectionRef = useRef<HTMLDivElement>(null);
  const imageRef = useRef<HTMLDivElement>(null);
  const textRef = useRef<HTMLDivElement>(null);
  const cuePathRef = useRef<SVGPathElement>(null);
  const listItemsRef = useRef<(HTMLLIElement | null)[]>([]);

  useEffect(() => {
    registerGSAP();
    const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (reduced) return;

    const ctx = gsap.context(() => {
      // Image reveal — slides up into view
      ScrollTrigger.create({
        trigger: imageRef.current,
        start: 'top 75%',
        onEnter: () => {
          gsap.to(imageRef.current, {
            clipPath: 'inset(0% 0% 0% 0%)',
            y: 0,
            duration: 1.1,
            ease: 'expo.out',
          });
        },
      });

      // Text block reveal
      ScrollTrigger.create({
        trigger: textRef.current,
        start: 'top 70%',
        onEnter: () => {
          gsap.to(textRef.current, {
            opacity: 1,
            x: 0,
            duration: 1,
            ease: 'expo.out',
          });
        },
      });

      // Cue stick SVG draw — strokeDashoffset from 1 to 0
      if (cuePathRef.current) {
        const length = cuePathRef.current.getTotalLength();
        gsap.set(cuePathRef.current, {
          strokeDasharray: length,
          strokeDashoffset: length,
        });
        ScrollTrigger.create({
          trigger: sectionRef.current,
          start: 'top 60%',
          onEnter: () => {
            gsap.to(cuePathRef.current, {
              strokeDashoffset: 0,
              duration: 1.4,
              ease: 'power3.inOut',
            });
          },
        });
      }

      // Stagger list items
      ScrollTrigger.create({
        trigger: textRef.current,
        start: 'top 65%',
        onEnter: () => {
          gsap.to(listItemsRef.current.filter(Boolean), {
            opacity: 1,
            y: 0,
            duration: 0.7,
            ease: 'expo.out',
            stagger: 0.1,
          });
        },
      });
    }, sectionRef);

    return () => ctx.revert();
  }, []);

  return (
    <section
      id="coaching"
      ref={sectionRef}
      className="relative py-32 md:py-48 overflow-hidden"
      aria-label="Coaching and Training"
    >
      {/* Section bg with subtle felt tint */}
      <div
        className="absolute inset-0"
        style={{ background: 'linear-gradient(180deg, #0a0d0a 0%, #0c1a10 50%, #0a0d0a 100%)' }}
        aria-hidden="true"
      />

      <div className="relative z-10 max-w-screen-xl mx-auto px-6 md:px-16">
        {/* Section label */}
        <div className="flex items-center gap-4 mb-20">
          <span className="gold-rule max-w-[60px]" aria-hidden="true" />
          <span className="font-mono text-xs tracking-[0.35em] text-brass/70 uppercase">
            Coaching
          </span>
        </div>

        {/* Two-column split */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 lg:gap-24 items-center">
          {/* LEFT — image */}
          <div className="relative">
            {/* Decorative corner lines */}
            <div
              className="absolute -top-4 -left-4 w-12 h-12 pointer-events-none"
              aria-hidden="true"
            >
              <div className="w-full h-px bg-gold/40" />
              <div className="w-px h-full bg-gold/40" />
            </div>

            <div
              ref={imageRef}
              className="relative overflow-hidden rounded-sm"
              style={{
                clipPath: 'inset(100% 0% 0% 0%)',
                transform: 'translateY(20px)',
                aspectRatio: '3/4',
              }}
            >
              {/* REPLACE: /coaching-photo.jpg — Unsplash snooker coaching shot */}
              <Image
                src="https://images.unsplash.com/photo-1636486491869-a9abef84e6b2?w=600&q=80&auto=format"
                alt="WPBSA certified coach demonstrating cue technique at The Corner Pocket coaching studio"
                fill
                sizes="(max-width: 1024px) 100vw, 50vw"
                className="object-cover"
                placeholder="blur"
                blurDataURL="data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/wAAGQABAAMBAAIAAREBAxEB/9oADAMBAAIRAxEAPwDXwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAP/Z"
              />
              {/* Felt-green tint overlay */}
              <div
                className="absolute inset-0"
                style={{
                  background: 'linear-gradient(to top, rgba(10,74,46,0.5) 0%, transparent 50%)',
                }}
                aria-hidden="true"
              />
            </div>

            {/* Coaching stat callout */}
            <div
              className="absolute bottom-6 right-6 p-4 rounded-sm"
              style={{
                background: 'rgba(10,13,10,0.9)',
                border: '1px solid rgba(212,175,55,0.25)',
                backdropFilter: 'blur(8px)',
              }}
            >
              <span className="font-display text-3xl text-gold block leading-none">12+</span>
              <span className="font-mono text-[0.65rem] text-brass/70 tracking-[0.2em] uppercase">
                Years coaching
              </span>
            </div>
          </div>

          {/* RIGHT — text + list */}
          <div
            ref={textRef}
            style={{ opacity: 0, transform: 'translateX(40px)' }}
          >
            <h2
              className="font-display font-light text-cream leading-tight mb-6"
              style={{ fontSize: 'clamp(2.2rem, 4vw, 3.5rem)' }}
            >
              Raise Your Game.<br />
              <em
                className="text-gold-gradient not-italic"
                style={{ fontStyle: 'italic' }}
              >
                Seriously.
              </em>
            </h2>

            <p className="font-body text-cream/65 leading-relaxed mb-10 max-w-md">
              Most players plateau at the same break for years. Our coaches diagnose exactly why — and build a personalised programme to break through it.
            </p>

            <ul className="flex flex-col gap-6" role="list">
              {COACHING_POINTS.map(({ title, desc }, i) => (
                <li
                  key={title}
                  ref={(el) => { listItemsRef.current[i] = el; }}
                  className="flex items-start gap-4"
                  style={{ opacity: 0, transform: 'translateY(20px)' }}
                >
                  <span
                    className="flex-shrink-0 w-6 h-6 flex items-center justify-center rounded-full border border-gold/40 text-gold text-xs"
                    aria-hidden="true"
                  >
                    ◆
                  </span>
                  <div>
                    <span className="font-mono text-xs tracking-[0.15em] text-brass uppercase block mb-1">
                      {title}
                    </span>
                    <p className="font-body text-cream/60 text-sm leading-relaxed">{desc}</p>
                  </div>
                </li>
              ))}
            </ul>

            <div className="mt-10 flex items-center gap-4">
              <a
                href="#booking"
                className="inline-flex items-center gap-2 px-6 py-3 bg-felt-deep border border-felt-highlight/40 text-cream/80 font-mono text-xs tracking-[0.15em] uppercase rounded-sm hover:bg-felt-mid hover:text-cream transition-all duration-300"
              >
                Book a Lesson
              </a>
              <span className="font-mono text-xs text-brass/50">Starting ₹1,500/hr</span>
            </div>
          </div>
        </div>
      </div>

      {/* Cue stick SVG divider — draws itself on scroll */}
      <div
        className="absolute inset-y-0 left-1/2 -translate-x-1/2 w-px hidden lg:block pointer-events-none"
        aria-hidden="true"
      >
        <svg
          width="2"
          height="100%"
          viewBox="0 0 2 800"
          preserveAspectRatio="none"
          className="w-full h-full"
          aria-hidden="true"
        >
          <path
            ref={cuePathRef}
            d="M1,0 L1,800"
            stroke="rgba(212,175,55,0.15)"
            strokeWidth="1"
            fill="none"
          />
        </svg>
      </div>
    </section>
  );
}
