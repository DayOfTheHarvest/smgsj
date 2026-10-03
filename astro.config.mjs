import { defineConfig } from 'astro/config';
import tailwind from '@astrojs/tailwind';

// Static parish site. No adapter (static output by default).
// Slugs stay English; per-locale pages at /en/<slug>, /es/<slug>, /vi/<slug>.
// Sitemap is generated post-build by scripts/sitemap.py.
// Tailwind (build-time only) purges to a few KB — portable to Cloudflare Pages untouched.
export default defineConfig({
  site: 'https://www.smgsj.org',
  output: 'static',
  integrations: [tailwind({ applyBaseStyles: true })],
  i18n: {
    defaultLocale: 'en',
    locales: ['en', 'es', 'vi'],
  },
});
