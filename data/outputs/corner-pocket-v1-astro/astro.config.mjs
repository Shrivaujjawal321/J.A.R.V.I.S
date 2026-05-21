// @ts-check
import { defineConfig } from 'astro/config';
import tailwind from '@astrojs/tailwind';
import sitemap from '@astrojs/sitemap';

// https://astro.build/config
export default defineConfig({
  // design-note: update site URL before deploy — used by sitemap + canonical/OG tags
  site: 'https://thecornerpocket.club',
  integrations: [
    tailwind({
      // we own the base CSS reset in src/styles/global.css
      applyBaseStyles: false,
    }),
    sitemap(),
  ],
  compressHTML: true,
  build: {
    inlineStylesheets: 'auto',
  },
  prefetch: {
    prefetchAll: false,
    defaultStrategy: 'hover',
  },
});
