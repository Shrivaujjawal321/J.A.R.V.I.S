'use client';

import { useState, useRef } from 'react';
import Image from 'next/image';
import {
  motion,
  AnimatePresence,
  useScroll,
  useTransform,
  useReducedMotion,
} from 'framer-motion';

// REPLACE: swap these Unsplash URLs for actual club photography
// Each entry: src, alt, and parallax speed factor (1 = normal, <1 = slower, >1 = faster)
const GALLERY_IMAGES = [
  {
    src: 'https://images.unsplash.com/photo-1560066984-138dadb4c035?w=800&q=80&auto=format',
    alt: 'Tournament snooker table under warm tungsten lighting at The Corner Pocket',
    span: 'col-span-2 row-span-2',
    speed: 0.85,
    width: 800,
    height: 600,
  },
  {
    src: 'https://images.unsplash.com/photo-1616712134411-6b6ae89bc3ba?w=500&q=80&auto=format',
    alt: 'Close-up of snooker balls racked in triangle on green felt',
    span: 'col-span-1 row-span-1',
    speed: 1.1,
    width: 500,
    height: 400,
  },
  {
    src: 'https://images.unsplash.com/photo-1580128637134-31d93e3a3ca8?w=500&q=80&auto=format',
    alt: 'The Corner Pocket members lounge and craft bar',
    span: 'col-span-1 row-span-2',
    speed: 0.95,
    width: 500,
    height: 700,
  },
  {
    src: 'https://images.unsplash.com/photo-1580128637134-31d93e3a3ca8?w=500&q=80&auto=format',
    alt: 'Professional snooker cue rack in the pro shop',
    span: 'col-span-1 row-span-1',
    speed: 1.05,
    width: 500,
    height: 400,
  },
  {
    src: 'https://images.unsplash.com/photo-1579952363873-27f3bade9f55?w=700&q=80&auto=format',
    alt: 'Evening at The Corner Pocket — club interior under atmospheric lighting',
    span: 'col-span-2 row-span-1',
    speed: 0.9,
    width: 700,
    height: 400,
  },
  {
    src: 'https://images.unsplash.com/photo-1553521041-408d2a20d465?w=500&q=80&auto=format',
    alt: 'Player making a precise long pot during a tournament game',
    span: 'col-span-1 row-span-1',
    speed: 1.15,
    width: 500,
    height: 400,
  },
  {
    src: 'https://images.unsplash.com/photo-1569517282132-25d22f4573e6?w=500&q=80&auto=format',
    alt: "Detail of the club's collection of John Parris and Peradon cues in the pro shop",
    span: 'col-span-1 row-span-1',
    speed: 0.88,
    width: 500,
    height: 400,
  },
  {
    src: 'https://images.unsplash.com/photo-1551698618-1dfe5d97d256?w=600&q=80&auto=format',
    alt: 'The Corner Pocket — exterior sign and entrance, Bandra West Mumbai',
    span: 'col-span-1 row-span-1',
    speed: 1.0,
    width: 600,
    height: 400,
  },
] as const;

interface LightboxProps {
  src: string;
  alt: string;
  onClose: () => void;
}

function Lightbox({ src, alt, onClose }: LightboxProps) {
  return (
    <motion.div
      className="fixed inset-0 z-[9000] flex items-center justify-center p-6"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.3 }}
      onClick={onClose}
      role="dialog"
      aria-label={`Photo lightbox: ${alt}`}
      aria-modal="true"
    >
      {/* Backdrop */}
      <div className="absolute inset-0 bg-bg/96 backdrop-blur-sm" aria-hidden="true" />

      {/* Close button */}
      <button
        className="absolute top-6 right-6 z-10 w-10 h-10 flex items-center justify-center border border-brass/40 text-brass hover:text-gold hover:border-gold transition-colors rounded-sm"
        onClick={onClose}
        aria-label="Close lightbox"
      >
        ✕
      </button>

      {/* Image */}
      <motion.div
        className="relative z-10 max-w-5xl max-h-[85vh] overflow-hidden rounded-sm"
        initial={{ scale: 0.92, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.92, opacity: 0 }}
        transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
        onClick={(e) => e.stopPropagation()}
        style={{ border: '1px solid rgba(176,141,87,0.2)' }}
      >
        <Image
          src={src}
          alt={alt}
          width={1200}
          height={800}
          className="object-cover max-h-[80vh] w-auto"
          quality={90}
        />
      </motion.div>
    </motion.div>
  );
}

interface GalleryItemProps {
  src: string;
  alt: string;
  span: string;
  speed: number;
  width: number;
  height: number;
  onClick: () => void;
}

function GalleryItem({ src, alt, span, speed, width, height, onClick }: GalleryItemProps) {
  const itemRef = useRef<HTMLDivElement>(null);
  const prefersReducedMotion = useReducedMotion();
  const { scrollYProgress } = useScroll({
    target: itemRef,
    offset: ['start end', 'end start'],
  });

  // Parallax: image moves at `speed` rate — slower = more depth illusion
  const y = useTransform(
    scrollYProgress,
    [0, 1],
    prefersReducedMotion ? ['0%', '0%'] : [`${(speed - 1) * 50}%`, `${(1 - speed) * 50}%`]
  );

  return (
    <div
      ref={itemRef}
      className={`${span} relative overflow-hidden rounded-sm cursor-pointer group img-reveal`}
      style={{
        border: '1px solid rgba(176,141,87,0.08)',
        minHeight: 200,
      }}
    >
      <motion.div
        className="absolute inset-0"
        style={{ y }}
        onClick={onClick}
        role="button"
        tabIndex={0}
        aria-label={`View larger: ${alt}`}
        onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); onClick(); } }}
      >
        <Image
          src={src}
          alt={alt}
          fill
          sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
          className="object-cover transition-transform duration-700 ease-expo-out group-hover:scale-105"
          quality={80}
        />

        {/* Hover overlay — brass vignette */}
        <div
          className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500"
          style={{
            background: 'radial-gradient(ellipse at center, rgba(176,141,87,0.08) 0%, rgba(10,13,10,0.5) 100%)',
          }}
          aria-hidden="true"
        />
      </motion.div>
    </div>
  );
}

export function Gallery() {
  const [lightbox, setLightbox] = useState<{ src: string; alt: string } | null>(null);

  const closeLightbox = () => setLightbox(null);

  return (
    <section
      id="gallery"
      className="relative py-32 md:py-48 bg-bg"
      aria-label="Gallery — The Corner Pocket club photos"
    >
      <div className="max-w-screen-xl mx-auto px-6 md:px-16">
        {/* Header */}
        <div className="flex items-center gap-4 mb-16">
          <span className="gold-rule max-w-[60px]" aria-hidden="true" />
          <span className="font-mono text-xs tracking-[0.35em] text-brass/70 uppercase">
            Gallery
          </span>
        </div>
        <h2
          className="font-display font-light text-cream mb-12"
          style={{ fontSize: 'clamp(2.5rem, 5vw, 4rem)' }}
        >
          The Room.
        </h2>

        {/* Asymmetric grid */}
        <div
          className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3 md:gap-4"
          style={{ gridAutoRows: '200px' }}
        >
          {GALLERY_IMAGES.map((img, i) => (
            <GalleryItem
              key={i}
              {...img}
              onClick={() => setLightbox({ src: img.src, alt: img.alt })}
            />
          ))}
        </div>

        <p className="font-mono text-xs text-cream/25 text-center mt-6 tracking-wider">
          Photography placeholder — replace with actual club imagery before launch
        </p>
      </div>

      <AnimatePresence>
        {lightbox && (
          <Lightbox
            src={lightbox.src}
            alt={lightbox.alt}
            onClose={closeLightbox}
          />
        )}
      </AnimatePresence>
    </section>
  );
}
