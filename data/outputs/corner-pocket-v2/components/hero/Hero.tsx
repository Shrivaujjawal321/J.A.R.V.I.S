'use client';

import dynamic from 'next/dynamic';
import { useRef, useCallback, useEffect } from 'react';
import { motion, useReducedMotion } from 'framer-motion';
import Image from 'next/image';

// Lazy-load the entire R3F scene — Three.js is ~600KB gzipped.
// SSR:false because R3F uses browser APIs.
const Hero3D = dynamic(
  () => import('./Hero3D').then((mod) => mod.Hero3D),
  {
    ssr: false,
    loading: () => (
      <div
        className="absolute inset-0 bg-felt-gradient"
        aria-hidden="true"
      />
    ),
  }
);

// Tagline options (uncomment preferred, comment rest):
// Option A — evocative / nocturnal
const TAGLINE = 'Where the city racks up after dark.';
// Option B — prestige positioning
// const TAGLINE = 'The game demands precision. So do we.';
// Option C — invite / community
// const TAGLINE = 'Six tables. No amateurs. Welcome home.';

function MagneticButton({
  children,
  className,
  href,
  variant = 'primary',
}: {
  children: React.ReactNode;
  className?: string;
  href: string;
  variant?: 'primary' | 'ghost';
}) {
  const btnRef = useRef<HTMLAnchorElement>(null);

  const onMouseMove = useCallback((e: React.MouseEvent<HTMLAnchorElement>) => {
    const el = btnRef.current;
    if (!el) return;
    const rect = el.getBoundingClientRect();
    const cx = rect.left + rect.width / 2;
    const cy = rect.top + rect.height / 2;
    const dx = (e.clientX - cx) * 0.35;
    const dy = (e.clientY - cy) * 0.35;
    el.style.transform = `translate(${dx}px, ${dy}px)`;
  }, []);

  const onMouseLeave = useCallback(() => {
    const el = btnRef.current;
    if (!el) return;
    el.style.transform = 'translate(0,0)';
    el.style.transition = 'transform 0.6s cubic-bezier(0.16, 1, 0.3, 1)';
  }, []);

  const base =
    'inline-flex items-center gap-2 px-8 py-4 font-mono text-sm tracking-[0.12em] uppercase transition-all duration-300 rounded-sm select-none';

  const styles = {
    primary:
      'bg-gold text-bg hover:bg-cream hover:text-bg shadow-gold-glow',
    ghost:
      'border border-brass/70 text-brass hover:border-gold hover:text-gold',
  };

  return (
    <a
      ref={btnRef}
      href={href}
      onMouseMove={onMouseMove}
      onMouseLeave={onMouseLeave}
      className={`magnetic-btn ${base} ${styles[variant]} ${className ?? ''}`}
      style={{ transition: 'background-color 0.3s, color 0.3s, border-color 0.3s' }}
    >
      {children}
    </a>
  );
}

// Scroll indicator — gold vertical line + bouncing cue ball icon
function ScrollIndicator() {
  return (
    <div
      className="absolute bottom-8 left-1/2 -translate-x-1/2 flex flex-col items-center gap-2"
      aria-hidden="true"
    >
      <span className="font-mono text-[0.6rem] tracking-[0.3em] text-brass/60 uppercase">
        Scroll
      </span>
      <div className="relative w-px h-16 bg-gold/30 overflow-hidden">
        <motion.div
          className="absolute top-0 left-0 w-full bg-gold"
          animate={{ y: ['0%', '100%'] }}
          transition={{ duration: 1.4, repeat: Infinity, ease: 'linear' }}
          style={{ height: '40%' }}
        />
      </div>
      <motion.div
        animate={{ y: [0, 6, 0] }}
        transition={{ duration: 1.2, repeat: Infinity, ease: 'easeInOut' }}
        style={{
          width: 8,
          height: 8,
          borderRadius: '50%',
          background: 'radial-gradient(circle at 35% 35%, #ffffff 0%, #e8e8e0 100%)',
          boxShadow: '0 2px 6px rgba(0,0,0,0.5)',
        }}
      />
    </div>
  );
}

export function Hero() {
  const mouseX = useRef(0);
  const mouseY = useRef(0);
  const prefersReducedMotion = useReducedMotion();

  const onMouseMove = useCallback((e: React.MouseEvent<HTMLDivElement>) => {
    if (prefersReducedMotion) return;
    // Normalize to -1..1
    mouseX.current = (e.clientX / window.innerWidth - 0.5) * 2;
    mouseY.current = (e.clientY / window.innerHeight - 0.5) * 2;
  }, [prefersReducedMotion]);

  return (
    <section
      id="hero"
      className="relative w-full h-screen min-h-[600px] overflow-hidden"
      onMouseMove={onMouseMove}
      aria-label="Hero section — The Corner Pocket 3D snooker table"
    >
      {/* 3D scene layer — full bleed */}
      <div className="absolute inset-0" aria-hidden={prefersReducedMotion ?? false}>
        {prefersReducedMotion ? (
          /* Static fallback for reduced-motion — a photograph of the club */
          <Image
            src="/fallback/hero.jpg"
            alt="The Corner Pocket — premium snooker club interior with felt-green tables"
            fill
            priority
            sizes="100vw"
            className="object-cover"
            placeholder="blur"
            blurDataURL="data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAAUADIDASIAAhEBAxEB/8QAGQABAQEBAQEAAAAAAAAAAAAAAAUEAwYC/8QAIxAAAQQCAgMBAQAAAAAAAAAAAQACAxESIQQxQVH/xAAUAQEAAAAAAAAAAAAAAAAAAAAA/8QAFBEBAAAAAAAAAAAAAAAAAAAAAP/aAAwDAQACEQMRAD8A9ywGm0hzWuILi1oJHMnkDlqPNEEPQdXIPbRVOF7ZJZJHxkuBce0HOTz5UWIpNMr5YN8GQM6g8EHQP2rSbmtqG0ANgB0AFAA6AftERB//2Q=="
          />
        ) : (
          <Hero3D mouseX={mouseX} mouseY={mouseY} />
        )}
      </div>

      {/* Gradient overlays to make text legible over the 3D scene */}
      <div
        className="absolute inset-0 pointer-events-none"
        aria-hidden="true"
        style={{
          background:
            'linear-gradient(to right, rgba(10,13,10,0.85) 0%, rgba(10,13,10,0.3) 55%, transparent 100%)',
        }}
      />
      <div
        className="absolute bottom-0 left-0 right-0 h-48 pointer-events-none"
        aria-hidden="true"
        style={{
          background: 'linear-gradient(to top, #0a0d0a 0%, transparent 100%)',
        }}
      />

      {/* Content overlay */}
      <div className="relative z-10 h-full flex flex-col justify-center px-6 md:px-16 lg:px-24 max-w-screen-xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 1, delay: 2.2, ease: [0.16, 1, 0.3, 1] }}
          className="max-w-xl"
        >
          {/* Overline */}
          <div className="flex items-center gap-3 mb-6">
            <span className="block w-8 h-px bg-gold" />
            <span className="font-mono text-xs tracking-[0.4em] text-brass uppercase">
              Mumbai · Est. 2018
            </span>
          </div>

          {/* Main headline */}
          <h1
            className="font-display font-light leading-none tracking-[-0.02em] text-cream mb-6"
            style={{ fontSize: 'clamp(3rem, 7vw, 6.5rem)' }}
          >
            The<br />
            <em
              className="not-italic text-gold-gradient"
              style={{ fontStyle: 'italic' }}
            >
              Corner
            </em>
            <br />
            Pocket
          </h1>

          {/* Tagline */}
          <p
            className="font-body text-cream/75 mb-10 leading-relaxed"
            style={{ fontSize: 'clamp(1rem, 2vw, 1.25rem)' }}
          >
            {TAGLINE}
          </p>

          {/* CTAs */}
          <div className="flex flex-wrap gap-4">
            <MagneticButton href="#booking" variant="primary">
              Book a Table
            </MagneticButton>
            <MagneticButton href="#membership" variant="ghost">
              Become a Member
            </MagneticButton>
          </div>
        </motion.div>
      </div>

      {/* Scroll indicator */}
      <ScrollIndicator />

      {/* Decorative gold corner lines — subtle luxury signal */}
      <div
        className="absolute top-24 right-8 pointer-events-none hidden lg:block"
        aria-hidden="true"
      >
        <div className="w-px h-24 bg-gold/20" />
        <div className="w-24 h-px bg-gold/20 -mt-px ml-auto" />
      </div>
    </section>
  );
}
