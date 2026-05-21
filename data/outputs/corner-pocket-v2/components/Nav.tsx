'use client';

import { useEffect, useRef, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { gsap } from 'gsap';

const NAV_LINKS = [
  { href: '#about', label: 'About' },
  { href: '#tables', label: 'Tables' },
  { href: '#membership', label: 'Membership' },
  { href: '#coaching', label: 'Coaching' },
  { href: '#events', label: 'Events' },
  { href: '#booking', label: 'Book' },
] as const;

export function Nav() {
  const [scrolled, setScrolled] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);
  const navRef = useRef<HTMLElement>(null);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 60);
    window.addEventListener('scroll', onScroll, { passive: true });
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  // Smooth scroll to section via Lenis-compatible native behavior
  const handleLinkClick = (e: React.MouseEvent<HTMLAnchorElement>, href: string) => {
    e.preventDefault();
    setMenuOpen(false);
    const target = document.querySelector(href);
    if (target) {
      // Lenis intercepts native scroll calls when active
      target.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <nav
      ref={navRef}
      role="navigation"
      aria-label="Main navigation"
      className={`fixed top-0 left-0 right-0 z-[1000] transition-all duration-700 ${
        scrolled
          ? 'bg-bg/90 backdrop-blur-md border-b border-white/5'
          : 'bg-transparent'
      }`}
    >
      <div className="max-w-screen-xl mx-auto px-6 md:px-10 h-16 flex items-center justify-between">
        {/* Wordmark */}
        <a
          href="/"
          className="font-display text-cream tracking-widest text-sm uppercase focus-visible:outline focus-visible:outline-gold"
          aria-label="The Corner Pocket — Home"
        >
          <span className="text-gold-gradient font-semibold">TCP</span>
        </a>

        {/* Desktop links */}
        <ul className="hidden md:flex items-center gap-8" role="list">
          {NAV_LINKS.map(({ href, label }) => (
            <li key={href}>
              <a
                href={href}
                onClick={(e) => handleLinkClick(e, href)}
                className="font-mono text-xs tracking-[0.15em] uppercase text-cream/70 hover:text-gold transition-colors duration-300 relative group"
              >
                {label}
                <span className="absolute -bottom-px left-0 w-0 h-px bg-gold group-hover:w-full transition-all duration-400 ease-expo-out" />
              </a>
            </li>
          ))}
        </ul>

        {/* CTA */}
        <a
          href="#booking"
          onClick={(e) => handleLinkClick(e, '#booking')}
          className="hidden md:inline-flex items-center gap-2 px-5 py-2 border border-gold/60 text-gold font-mono text-xs tracking-[0.15em] uppercase hover:bg-gold hover:text-bg transition-all duration-300 rounded-sm"
        >
          Book a Table
        </a>

        {/* Mobile hamburger */}
        <button
          className="md:hidden flex flex-col gap-1.5 p-2"
          onClick={() => setMenuOpen((o) => !o)}
          aria-expanded={menuOpen}
          aria-label={menuOpen ? 'Close menu' : 'Open menu'}
        >
          <motion.span
            animate={menuOpen ? { rotate: 45, y: 7 } : { rotate: 0, y: 0 }}
            className="block w-6 h-px bg-cream"
          />
          <motion.span
            animate={menuOpen ? { opacity: 0, scaleX: 0 } : { opacity: 1, scaleX: 1 }}
            className="block w-6 h-px bg-cream"
          />
          <motion.span
            animate={menuOpen ? { rotate: -45, y: -7 } : { rotate: 0, y: 0 }}
            className="block w-6 h-px bg-cream"
          />
        </button>
      </div>

      {/* Mobile menu panel */}
      <AnimatePresence>
        {menuOpen && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.3, ease: [0.16, 1, 0.3, 1] }}
            className="md:hidden bg-bg/98 backdrop-blur-xl border-b border-white/10 px-6 py-8"
          >
            <ul className="flex flex-col gap-6" role="list">
              {NAV_LINKS.map(({ href, label }, i) => (
                <motion.li
                  key={href}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.06 }}
                >
                  <a
                    href={href}
                    onClick={(e) => handleLinkClick(e, href)}
                    className="font-display text-2xl text-cream/90 hover:text-gold transition-colors"
                  >
                    {label}
                  </a>
                </motion.li>
              ))}
              <motion.li
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.4 }}
              >
                <a
                  href="#booking"
                  onClick={(e) => handleLinkClick(e, '#booking')}
                  className="inline-flex items-center gap-2 px-6 py-3 bg-gold text-bg font-mono text-xs tracking-[0.15em] uppercase rounded-sm w-full justify-center"
                >
                  Book a Table
                </a>
              </motion.li>
            </ul>
          </motion.div>
        )}
      </AnimatePresence>
    </nav>
  );
}
