'use client';

import { useState, useRef } from 'react';
import {
  motion,
  useMotionValue,
  useTransform,
  AnimatePresence,
  useReducedMotion,
} from 'framer-motion';

interface Tier {
  id: string;
  name: string;
  price: string;
  period: string;
  tagline: string;
  perks: string[];
  highlight: boolean;
  borderColor: string;
  glowColor: string;
}

const TIERS: Tier[] = [
  {
    id: 'casual',
    name: 'Casual',
    price: '₹2,000',
    period: '/month',
    tagline: 'For the social player.',
    perks: [
      '10% off table bookings',
      'Priority booking 24h ahead',
      'Bar member discount',
      'Monthly newsletter',
      'Access to Pro Shop at member rates',
    ],
    highlight: false,
    borderColor: 'rgba(176,141,87,0.3)',
    glowColor: 'rgba(176,141,87,0.1)',
  },
  {
    id: 'regular',
    name: 'Regular',
    price: '₹8,000',
    period: '/month',
    tagline: 'For the serious amateur.',
    perks: [
      '20% off table bookings',
      'Priority booking 48h ahead',
      'Complimentary 2hr session weekly',
      '1 guest pass per month',
      'Coaching consultation (30 min/month)',
      'VIP room access (with booking)',
      'Library access',
    ],
    highlight: true,
    borderColor: 'rgba(212,175,55,0.5)',
    glowColor: 'rgba(212,175,55,0.15)',
  },
  {
    id: 'elite',
    name: 'Elite',
    price: '₹25,000',
    period: '/month',
    tagline: 'For the committed competitor.',
    perks: [
      'Unlimited table time (off-peak)',
      'Priority booking 7 days ahead',
      'Dedicated locker + cue storage',
      '4 guest passes per month',
      'Monthly coaching session (1hr)',
      'Permanent VIP room slot (weekends)',
      'Library & archive access',
      'Invitation to closed tournaments',
      'Personal match stats tracking',
    ],
    highlight: false,
    borderColor: 'rgba(176,141,87,0.4)',
    glowColor: 'rgba(176,141,87,0.12)',
  },
];

interface CardProps {
  tier: Tier;
  index: number;
}

function MembershipCard({ tier, index }: CardProps) {
  const [flipped, setFlipped] = useState(false);
  const prefersReducedMotion = useReducedMotion();

  const rotateX = useMotionValue(0);
  const rotateY = useMotionValue(0);

  const cardRotateX = useTransform(rotateX, [-1, 1], [8, -8]);
  const cardRotateY = useTransform(rotateY, [-1, 1], [-10, 10]);

  const onMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    if (prefersReducedMotion || flipped) return;
    const rect = e.currentTarget.getBoundingClientRect();
    const x = (e.clientX - rect.left) / rect.width - 0.5;
    const y = (e.clientY - rect.top) / rect.height - 0.5;
    rotateX.set(y);
    rotateY.set(x);
  };

  const onMouseLeave = () => {
    rotateX.set(0);
    rotateY.set(0);
  };

  const handleFlip = () => setFlipped((f) => !f);
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      handleFlip();
    }
  };

  const isElite = tier.id === 'elite';

  return (
    <motion.div
      initial={{ opacity: 0, y: 60 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: '-80px' }}
      transition={{ duration: 0.8, delay: index * 0.15, ease: [0.16, 1, 0.3, 1] }}
      className="perspective-container"
      style={{ perspective: 1200 }}
    >
      <motion.div
        className="relative cursor-pointer select-none"
        style={{
          width: 320,
          height: 460,
          rotateX: prefersReducedMotion ? 0 : cardRotateX,
          rotateY: prefersReducedMotion ? 0 : cardRotateY,
          transformStyle: 'preserve-3d',
        }}
        animate={{ rotateY: flipped ? 180 : 0 }}
        transition={{ duration: 0.7, ease: [0.16, 1, 0.3, 1] }}
        onMouseMove={onMouseMove}
        onMouseLeave={onMouseLeave}
        onClick={handleFlip}
        onKeyDown={handleKeyDown}
        tabIndex={0}
        role="button"
        aria-pressed={flipped}
        aria-label={`${tier.name} membership — ${tier.price}${tier.period}. ${flipped ? 'Click to show front' : 'Click to see benefits'}`}
      >
        {/* FRONT FACE */}
        <div
          className="absolute inset-0 rounded-sm flex flex-col justify-between p-8"
          style={{
            backfaceVisibility: 'hidden',
            WebkitBackfaceVisibility: 'hidden',
            background: `linear-gradient(135deg, rgba(14,74,46,0.4) 0%, rgba(10,13,10,0.97) 100%)`,
            border: `1px solid ${tier.borderColor}`,
            boxShadow: tier.highlight
              ? `0 32px 64px rgba(0,0,0,0.5), 0 0 60px ${tier.glowColor}`
              : `0 24px 48px rgba(0,0,0,0.4)`,
          }}
        >
          {/* Elite badge */}
          {isElite && (
            <div className="absolute top-4 right-4">
              <span
                className="font-mono text-[0.55rem] tracking-[0.3em] uppercase px-2 py-1"
                style={{
                  background: 'linear-gradient(90deg, #b08d57, #d4af37)',
                  color: '#0a0d0a',
                  borderRadius: 2,
                }}
              >
                Elite
              </span>
            </div>
          )}

          {tier.highlight && (
            <div className="absolute top-4 right-4">
              <span
                className="font-mono text-[0.55rem] tracking-[0.3em] uppercase px-2 py-1"
                style={{
                  background: 'rgba(212,175,55,0.15)',
                  color: '#d4af37',
                  border: '1px solid rgba(212,175,55,0.4)',
                  borderRadius: 2,
                }}
              >
                Most Popular
              </span>
            </div>
          )}

          <div>
            <span className="font-mono text-xs tracking-[0.3em] text-brass/70 uppercase block mb-3">
              Membership
            </span>
            <h3
              className="font-display font-light text-cream"
              style={{ fontSize: '2.2rem' }}
            >
              {tier.name}
            </h3>
          </div>

          <div>
            <div className="w-8 h-px bg-gold/50 mb-4" aria-hidden="true" />
            <p className="font-body text-cream/60 text-sm mb-6">{tier.tagline}</p>
            <div className="flex items-end gap-1">
              <span
                className="font-display font-light text-cream"
                style={{ fontSize: '2.5rem', lineHeight: 1 }}
              >
                {tier.price}
              </span>
              <span className="font-mono text-xs text-brass/70 mb-1">{tier.period}</span>
            </div>
          </div>

          <div className="flex items-center gap-2 text-brass/60">
            <span className="font-mono text-[0.65rem] tracking-widest uppercase">
              See benefits
            </span>
            <span aria-hidden="true">→</span>
          </div>
        </div>

        {/* BACK FACE — full perks list */}
        <div
          className="absolute inset-0 rounded-sm flex flex-col p-8"
          style={{
            backfaceVisibility: 'hidden',
            WebkitBackfaceVisibility: 'hidden',
            transform: 'rotateY(180deg)',
            background: `linear-gradient(135deg, rgba(10,13,10,0.98) 0%, rgba(14,74,46,0.35) 100%)`,
            border: `1px solid ${tier.borderColor}`,
            boxShadow: `0 24px 48px rgba(0,0,0,0.5)`,
          }}
        >
          <div className="flex items-center justify-between mb-6">
            <h3
              className="font-display font-light text-cream"
              style={{ fontSize: '1.6rem' }}
            >
              {tier.name}
            </h3>
            <button
              onClick={(e) => { e.stopPropagation(); handleFlip(); }}
              className="text-brass/60 hover:text-gold text-xs font-mono tracking-widest"
              aria-label="Close benefits, return to front"
            >
              ✕
            </button>
          </div>

          <ul className="flex flex-col gap-3 flex-1 overflow-hidden">
            {tier.perks.map((perk, pi) => (
              <li key={pi} className="flex items-start gap-3">
                <span className="text-gold mt-0.5 flex-shrink-0" aria-hidden="true">◆</span>
                <span className="font-body text-cream/70 text-sm leading-tight">{perk}</span>
              </li>
            ))}
          </ul>

          <a
            href="#booking"
            className="mt-6 flex items-center justify-center py-3 font-mono text-xs tracking-[0.15em] uppercase rounded-sm"
            style={{
              background: tier.highlight
                ? 'linear-gradient(90deg, #b08d57, #d4af37)'
                : 'transparent',
              color: tier.highlight ? '#0a0d0a' : '#d4af37',
              border: tier.highlight ? 'none' : '1px solid rgba(212,175,55,0.4)',
            }}
            onClick={(e) => e.stopPropagation()}
          >
            Choose {tier.name}
          </a>
        </div>
      </motion.div>
    </motion.div>
  );
}

export function Membership() {
  return (
    <section
      id="membership"
      className="relative py-32 md:py-48 bg-bg"
      aria-label="Membership Tiers"
    >
      <div className="max-w-screen-xl mx-auto px-6 md:px-16">
        {/* Header */}
        <div className="flex items-center gap-4 mb-6">
          <span className="gold-rule max-w-[60px]" aria-hidden="true" />
          <span className="font-mono text-xs tracking-[0.35em] text-brass/70 uppercase">
            Membership
          </span>
        </div>
        <h2
          className="font-display font-light text-cream mb-16"
          style={{ fontSize: 'clamp(2.5rem, 5vw, 4rem)' }}
        >
          Choose Your Game.
        </h2>

        {/* Cards row */}
        <div className="flex flex-wrap justify-center gap-8 lg:gap-12">
          {TIERS.map((tier, i) => (
            <MembershipCard key={tier.id} tier={tier} index={i} />
          ))}
        </div>

        {/* Fine print */}
        <p className="text-center font-mono text-xs text-cream/30 mt-12 tracking-wider">
          All memberships are month-to-month. Cancel anytime. Joining fee: ₹5,000 (waived for first 50 members).
        </p>
      </div>
    </section>
  );
}
