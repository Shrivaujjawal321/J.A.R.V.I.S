'use client';

import { motion } from 'framer-motion';

const HOURS = [
  { days: 'Monday – Thursday', time: '12:00 PM – 2:00 AM' },
  { days: 'Friday', time: '12:00 PM – 3:00 AM' },
  { days: 'Saturday', time: '11:00 AM – 3:00 AM' },
  { days: 'Sunday', time: '11:00 AM – 2:00 AM' },
] as const;

export function Contact() {
  return (
    <section
      id="contact"
      className="relative py-32 bg-bg"
      aria-label="Contact and Location"
    >
      <div className="gold-rule mb-0" aria-hidden="true" />

      <div className="max-w-screen-xl mx-auto px-6 md:px-16 pt-20">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-16 items-start">
          {/* Left: address + hours */}
          <div>
            <div className="flex items-center gap-4 mb-10">
              <span className="gold-rule max-w-[60px]" aria-hidden="true" />
              <span className="font-mono text-xs tracking-[0.35em] text-brass/70 uppercase">
                Find Us
              </span>
            </div>

            <address className="not-italic mb-10">
              <p
                className="font-display font-light text-cream mb-2"
                style={{ fontSize: 'clamp(1.4rem, 2.5vw, 2rem)' }}
              >
                The Corner Pocket
              </p>
              {/* REPLACE with real address */}
              <p className="font-body text-cream/65 text-sm leading-relaxed">
                42, Linking Road<br />
                Bandra West<br />
                Mumbai, Maharashtra 400050
              </p>
              <div className="flex flex-col gap-2 mt-4">
                <a
                  href="tel:+912245678900"
                  className="font-mono text-sm text-brass hover:text-gold transition-colors"
                >
                  +91-22-4567-8900
                </a>
                <a
                  href="mailto:hello@cornerpocket.in"
                  className="font-mono text-sm text-brass hover:text-gold transition-colors"
                >
                  hello@cornerpocket.in
                </a>
              </div>
            </address>

            {/* Hours */}
            <div>
              <h3 className="font-mono text-xs tracking-[0.3em] text-brass/70 uppercase mb-4">
                Opening Hours
              </h3>
              <dl className="flex flex-col gap-2">
                {HOURS.map(({ days, time }) => (
                  <div key={days} className="flex justify-between gap-4">
                    <dt className="font-body text-cream/60 text-sm">{days}</dt>
                    <dd className="font-mono text-xs text-brass">{time}</dd>
                  </div>
                ))}
              </dl>
            </div>
          </div>

          {/* Right: map placeholder */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
            className="relative overflow-hidden rounded-sm"
            style={{
              aspectRatio: '4/3',
              background: 'rgba(14,74,46,0.15)',
              border: '1px solid rgba(176,141,87,0.15)',
            }}
            aria-label="Map placeholder — embed Google Maps iframe here"
          >
            {/* REPLACE: embed Google Maps iframe
                <iframe
                  src="https://www.google.com/maps/embed?pb=!1m18...YOUR_EMBED_KEY"
                  width="100%" height="100%"
                  style={{ border: 0 }}
                  allowFullScreen
                  loading="lazy"
                  referrerPolicy="no-referrer-when-downgrade"
                  title="The Corner Pocket location map"
                />
            */}
            <div className="absolute inset-0 flex flex-col items-center justify-center gap-3">
              <div
                className="w-12 h-12 rounded-full flex items-center justify-center"
                style={{ border: '1px solid rgba(212,175,55,0.3)' }}
                aria-hidden="true"
              >
                <span className="text-gold text-xl">◎</span>
              </div>
              <span className="font-mono text-xs text-brass/50 tracking-widest text-center">
                Google Maps embed<br />goes here
              </span>
            </div>

            {/* Grid overlay */}
            <div
              className="absolute inset-0 pointer-events-none"
              style={{
                backgroundImage:
                  'linear-gradient(rgba(26,107,70,0.08) 1px, transparent 1px), linear-gradient(to right, rgba(26,107,70,0.08) 1px, transparent 1px)',
                backgroundSize: '30px 30px',
              }}
              aria-hidden="true"
            />
          </motion.div>
        </div>
      </div>
    </section>
  );
}
