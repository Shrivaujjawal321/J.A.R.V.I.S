'use client';

import { motion } from 'framer-motion';

const TOURNAMENT_NAMES = [
  'The 147 Invitational',
  'Mumbai Open 2026',
  'Monsoon Classic',
  'Corner Cup',
  'Night of Champions',
  'The Season Opener',
  'Ladies Invitational',
  'Bandra Masters',
  'The Grudge Match',
  'All-India Amateur Series',
];

// Doubled for seamless infinite loop
const MARQUEE_ITEMS = [...TOURNAMENT_NAMES, ...TOURNAMENT_NAMES];

interface EventCardData {
  date: string;
  month: string;
  title: string;
  description: string;
  spots: string;
  type: string;
}

const EVENTS: EventCardData[] = [
  {
    date: '14',
    month: 'Jun',
    title: 'Mumbai Open 2026',
    description:
      '64-player open draw. ₹2L prize pool. Full round-robin group stage followed by knockout. Open to all skill levels.',
    spots: '18 spots left',
    type: 'Tournament',
  },
  {
    date: '28',
    month: 'Jun',
    title: 'The 147 Invitational',
    description:
      'Invitation-only. Top 16 members by ranking points. One session per day across 3 days. Trophy + lifetime plaque.',
    spots: 'By invitation',
    type: 'Members Only',
  },
  {
    date: '12',
    month: 'Jul',
    title: 'Monsoon Classic',
    description:
      "Annual doubles event. Pair up with a partner, blind draw for opponents. Rain, snooker, whisky. It's tradition.",
    spots: '24 spots left',
    type: 'Doubles',
  },
];

export function Events() {
  return (
    <section
      id="events"
      className="relative py-32 md:py-48 overflow-hidden bg-bg"
      aria-label="Upcoming Events and Tournaments"
    >
      {/* Top gold accent */}
      <div className="gold-rule mb-0" aria-hidden="true" />

      {/* Marquee strip */}
      <div
        className="relative bg-felt-deep/80 py-4 overflow-hidden mb-20"
        aria-hidden="true"
      >
        <div className="flex">
          <div
            className="flex gap-12 animate-marquee whitespace-nowrap"
            style={{ animationDuration: '35s' }}
          >
            {MARQUEE_ITEMS.map((name, i) => (
              <span
                key={`${name}-${i}`}
                className="font-mono text-xs tracking-[0.25em] uppercase text-brass/70 flex-shrink-0"
              >
                {name}
                <span className="text-gold/40 mx-6" aria-hidden="true">◆</span>
              </span>
            ))}
          </div>
        </div>
      </div>

      <div className="max-w-screen-xl mx-auto px-6 md:px-16">
        {/* Header */}
        <div className="flex items-end justify-between mb-12 flex-wrap gap-6">
          <div>
            <div className="flex items-center gap-4 mb-4">
              <span className="gold-rule max-w-[60px]" aria-hidden="true" />
              <span className="font-mono text-xs tracking-[0.35em] text-brass/70 uppercase">
                Events
              </span>
            </div>
            <h2
              className="font-display font-light text-cream"
              style={{ fontSize: 'clamp(2.5rem, 5vw, 4rem)' }}
            >
              Next Up.
            </h2>
          </div>
          <a
            href="#booking"
            className="font-mono text-xs tracking-[0.2em] text-brass hover:text-gold transition-colors uppercase border-b border-brass/40 hover:border-gold pb-1"
          >
            View Full Calendar →
          </a>
        </div>

        {/* Event cards */}
        <div
          className="grid grid-cols-1 md:grid-cols-3 gap-6"
          role="list"
          aria-label="Upcoming events"
        >
          {EVENTS.map((event, i) => (
            <motion.article
              key={event.title}
              role="listitem"
              initial={{ opacity: 0, y: 50 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: '-60px' }}
              transition={{ duration: 0.8, delay: i * 0.12, ease: [0.16, 1, 0.3, 1] }}
              className="group relative overflow-hidden rounded-sm"
              style={{
                background: 'linear-gradient(135deg, rgba(14,74,46,0.2) 0%, rgba(10,13,10,0.97) 100%)',
                border: '1px solid rgba(176,141,87,0.12)',
                boxShadow: '0 16px 40px rgba(0,0,0,0.4)',
              }}
            >
              {/* Top bar — event type */}
              <div
                className="flex items-center justify-between px-6 pt-6 pb-4"
                style={{ borderBottom: '1px solid rgba(176,141,87,0.1)' }}
              >
                <span className="font-mono text-[0.6rem] tracking-[0.3em] text-brass uppercase">
                  {event.type}
                </span>
                <span className="font-mono text-[0.6rem] tracking-[0.2em] text-felt-highlight uppercase">
                  {event.spots}
                </span>
              </div>

              <div className="p-6">
                {/* Date */}
                <div className="flex items-end gap-3 mb-4">
                  <span
                    className="font-display font-light text-gold leading-none"
                    style={{ fontSize: '3.5rem' }}
                    aria-label={`${event.date} ${event.month}`}
                  >
                    {event.date}
                  </span>
                  <span className="font-mono text-lg text-brass/70 uppercase mb-1">
                    {event.month}
                  </span>
                </div>

                <div className="w-8 h-px bg-gold/30 mb-4" aria-hidden="true" />

                <h3
                  className="font-display font-light text-cream mb-3"
                  style={{ fontSize: '1.5rem' }}
                >
                  {event.title}
                </h3>

                <p className="font-body text-cream/55 text-sm leading-relaxed mb-6">
                  {event.description}
                </p>

                <a
                  href="#booking"
                  className="inline-flex items-center gap-2 font-mono text-xs tracking-[0.15em] text-gold hover:text-cream uppercase transition-colors group-hover:gap-3 duration-300"
                >
                  Register
                  <span aria-hidden="true" className="transition-transform group-hover:translate-x-1 duration-300">→</span>
                </a>
              </div>

              {/* Hover: gold top line slides in */}
              <div
                className="absolute top-0 left-0 w-0 h-px bg-gold group-hover:w-full transition-all duration-700 ease-expo-out"
                aria-hidden="true"
              />
            </motion.article>
          ))}
        </div>
      </div>

      {/* Bottom gold accent */}
      <div className="gold-rule mt-20" aria-hidden="true" />
    </section>
  );
}
