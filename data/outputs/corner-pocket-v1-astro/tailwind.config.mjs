/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{astro,html,js,jsx,md,mdx,svelte,ts,tsx,vue}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // Corner Pocket palette — premium snooker hall
        ink: {
          DEFAULT: '#0b0f0c', // near-black green-tinted (page bg)
          deep: '#070a08',    // deeper for shadow wells
          soft: '#111713',    // section bg variant
        },
        felt: {
          DEFAULT: '#0e4a2e', // primary felt green
          light: '#1a6b46',   // lifted felt (cards, hovers)
          glow: '#22855b',    // accent / focus
        },
        brass: {
          DEFAULT: '#b08d57', // brass hardware
          dark: '#8a6f44',
          light: '#c9a872',
        },
        gold: {
          DEFAULT: '#d4af37', // accent gold (rare, never body text)
          light: '#e6c75c',
        },
        cream: {
          DEFAULT: '#f5e6c8', // body text on dark — WCAG AA on ink
          muted: '#cbb898',   // secondary text
          dim: '#9a8b6e',     // tertiary / metadata
        },
        walnut: {
          DEFAULT: '#3d2817', // cards, dividers
          light: '#5a3d24',
          dark: '#2a1a0f',
        },
      },
      fontFamily: {
        // loaded via Google Fonts <link> in Layout.astro
        serif: ['"Cormorant Garamond"', 'Georgia', 'serif'],
        display: ['"Playfair Display"', 'Georgia', 'serif'],
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
      },
      letterSpacing: {
        tightest: '-0.04em',
        tight: '-0.02em',
        wider: '0.08em',
        widest: '0.18em',
      },
      maxWidth: {
        prose: '65ch',
        container: '1280px',
      },
      boxShadow: {
        'brass-glow': '0 0 0 1px rgba(176, 141, 87, 0.3), 0 8px 32px -8px rgba(176, 141, 87, 0.25)',
        'gold-glow': '0 0 0 1px rgba(212, 175, 55, 0.4), 0 12px 40px -12px rgba(212, 175, 55, 0.35)',
        'felt-inner': 'inset 0 1px 0 0 rgba(255,255,255,0.04), inset 0 -1px 0 0 rgba(0,0,0,0.4)',
      },
      backgroundImage: {
        'felt-grain': 'radial-gradient(ellipse at center, rgba(34, 133, 91, 0.12) 0%, rgba(11, 15, 12, 0) 70%)',
        'gold-line': 'linear-gradient(90deg, transparent 0%, rgba(212, 175, 55, 0.5) 50%, transparent 100%)',
        'brass-line': 'linear-gradient(90deg, transparent 0%, rgba(176, 141, 87, 0.4) 50%, transparent 100%)',
      },
      animation: {
        'shimmer': 'shimmer 8s ease-in-out infinite',
        'fade-up': 'fade-up 0.8s cubic-bezier(0.22, 1, 0.36, 1) forwards',
      },
      keyframes: {
        shimmer: {
          '0%, 100%': { opacity: '0.6', transform: 'translateY(0)' },
          '50%': { opacity: '1', transform: 'translateY(-4px)' },
        },
        'fade-up': {
          from: { opacity: '0', transform: 'translateY(24px)' },
          to: { opacity: '1', transform: 'translateY(0)' },
        },
      },
    },
  },
  plugins: [],
};
