import type { Config } from 'tailwindcss';

const config: Config = {
  content: [
    './app/**/*.{ts,tsx}',
    './components/**/*.{ts,tsx}',
    './lib/**/*.{ts,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        bg: '#0a0d0a',
        felt: {
          deep: '#0e4a2e',
          mid: '#1a6b46',
          highlight: '#2d8a5e',
        },
        brass: '#b08d57',
        gold: '#d4af37',
        cream: '#f5e6c8',
        walnut: '#3d2817',
      },
      fontFamily: {
        display: ['var(--font-fraunces)', 'Georgia', 'serif'],
        body: ['var(--font-geist-sans)', 'system-ui', 'sans-serif'],
        mono: ['var(--font-geist-mono)', 'JetBrains Mono', 'monospace'],
      },
      backgroundImage: {
        'felt-gradient': 'radial-gradient(ellipse at center, #1a6b46 0%, #0e4a2e 50%, #0a0d0a 100%)',
        'gold-shimmer': 'linear-gradient(90deg, #b08d57 0%, #d4af37 50%, #b08d57 100%)',
      },
      boxShadow: {
        'gold-glow': '0 0 40px rgba(212, 175, 55, 0.3), 0 0 80px rgba(212, 175, 55, 0.1)',
        'brass-glow': '0 0 20px rgba(176, 141, 87, 0.4)',
        'felt-inset': 'inset 0 2px 20px rgba(0,0,0,0.8), inset 0 0 60px rgba(14,74,46,0.3)',
        'card-dark': '0 24px 48px rgba(0,0,0,0.6), 0 8px 16px rgba(0,0,0,0.4)',
      },
      animation: {
        'marquee': 'marquee 30s linear infinite',
        'marquee-reverse': 'marquee-reverse 30s linear infinite',
        'float': 'float 6s ease-in-out infinite',
        'gold-pulse': 'gold-pulse 2s ease-in-out infinite',
      },
      keyframes: {
        marquee: {
          '0%': { transform: 'translateX(0%)' },
          '100%': { transform: 'translateX(-50%)' },
        },
        'marquee-reverse': {
          '0%': { transform: 'translateX(-50%)' },
          '100%': { transform: 'translateX(0%)' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-10px)' },
        },
        'gold-pulse': {
          '0%, 100%': { boxShadow: '0 0 20px rgba(212,175,55,0.2)' },
          '50%': { boxShadow: '0 0 40px rgba(212,175,55,0.6), 0 0 80px rgba(212,175,55,0.2)' },
        },
      },
      transitionTimingFunction: {
        'expo-out': 'cubic-bezier(0.16, 1, 0.3, 1)',
        'power3-in-out': 'cubic-bezier(0.645, 0.045, 0.355, 1.000)',
        'spring': 'cubic-bezier(0.175, 0.885, 0.32, 1.275)',
      },
    },
  },
  plugins: [],
};

export default config;
