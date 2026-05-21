import { type ComponentProps } from 'react';

// Static server component — no interactivity needed here.
// Social icon hover is pure CSS.

function SocialLink({
  href,
  label,
  children,
}: {
  href: string;
  label: string;
  children: React.ReactNode;
}) {
  return (
    <a
      href={href}
      target="_blank"
      rel="noopener noreferrer"
      aria-label={`The Corner Pocket on ${label}`}
      className="w-9 h-9 flex items-center justify-center border border-brass/25 text-brass/70 hover:text-gold hover:border-gold transition-all duration-300 rounded-sm hover:scale-110 hover:-translate-y-0.5"
      style={{ transitionTimingFunction: 'cubic-bezier(0.175, 0.885, 0.32, 1.275)' }}
    >
      {children}
    </a>
  );
}

const FOOTER_LINKS = {
  Club: [
    { label: 'About Us', href: '#about' },
    { label: 'Tables', href: '#tables' },
    { label: 'Gallery', href: '#gallery' },
  ],
  Play: [
    { label: 'Book a Table', href: '#booking' },
    { label: 'Events', href: '#events' },
    { label: 'Coaching', href: '#coaching' },
  ],
  Membership: [
    { label: 'Casual', href: '#membership' },
    { label: 'Regular', href: '#membership' },
    { label: 'Elite', href: '#membership' },
  ],
} as const;

export function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer
      className="relative bg-bg pt-20 pb-10 overflow-hidden"
      role="contentinfo"
      aria-label="Site footer"
    >
      {/* Top gold rule */}
      <div className="gold-rule mb-16" aria-hidden="true" />

      <div className="max-w-screen-xl mx-auto px-6 md:px-16">
        {/* Main footer grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-12 mb-16">
          {/* Brand column */}
          <div className="col-span-2 md:col-span-1">
            <p
              className="font-display font-light text-cream tracking-widest mb-2"
              style={{ fontSize: '1.2rem' }}
            >
              The Corner<br />Pocket
            </p>
            <p className="font-mono text-[0.6rem] text-brass/50 tracking-[0.3em] uppercase mb-6">
              Est. 2018 · Bandra, Mumbai
            </p>

            {/* Social icons */}
            <div className="flex gap-2" role="list" aria-label="Social media links">
              <div role="listitem">
                <SocialLink href="https://instagram.com/cornerpocketbandra" label="Instagram">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" aria-hidden="true">
                    <rect x="2" y="2" width="20" height="20" rx="5" ry="5" />
                    <circle cx="12" cy="12" r="4" />
                    <circle cx="17.5" cy="6.5" r="0.5" fill="currentColor" />
                  </svg>
                </SocialLink>
              </div>
              <div role="listitem">
                <SocialLink href="https://twitter.com/cornerpocket_in" label="X / Twitter">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
                    <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" />
                  </svg>
                </SocialLink>
              </div>
              <div role="listitem">
                <SocialLink href="https://wa.me/912245678900" label="WhatsApp">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" aria-hidden="true">
                    <path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z" />
                  </svg>
                </SocialLink>
              </div>
            </div>
          </div>

          {/* Link columns */}
          {Object.entries(FOOTER_LINKS).map(([category, links]) => (
            <div key={category}>
              <h3 className="font-mono text-[0.65rem] tracking-[0.35em] text-brass/60 uppercase mb-5">
                {category}
              </h3>
              <ul className="flex flex-col gap-3" role="list">
                {links.map(({ label, href }) => (
                  <li key={label}>
                    <a
                      href={href}
                      className="font-body text-sm text-cream/55 hover:text-cream transition-colors duration-200"
                    >
                      {label}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        {/* Bottom bar */}
        <div className="gold-rule mb-6" aria-hidden="true" />
        <div className="flex flex-col md:flex-row justify-between items-center gap-4">
          <p className="font-mono text-[0.6rem] text-cream/25 tracking-wider">
            © {currentYear} The Corner Pocket. All rights reserved.
          </p>
          <div className="flex gap-6">
            {['Privacy Policy', 'House Rules', 'Responsible Gaming'].map((link) => (
              <a
                key={link}
                href="#"
                className="font-mono text-[0.6rem] text-cream/25 hover:text-cream/60 transition-colors tracking-wider"
              >
                {link}
              </a>
            ))}
          </div>
        </div>
      </div>

      {/* Large background watermark */}
      <p
        className="absolute bottom-0 left-1/2 -translate-x-1/2 font-display font-black text-white/[0.018] select-none pointer-events-none whitespace-nowrap"
        style={{ fontSize: 'clamp(6rem, 18vw, 18rem)', lineHeight: 0.8 }}
        aria-hidden="true"
      >
        TCP
      </p>
    </footer>
  );
}
