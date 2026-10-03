/** Tailwind theme: parish tokens (navy/gold) + offline-safe font stacks. */
export default {
  content: ['./src/**/*.{astro,html,js,jsx,md,mdx,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        navy: '#1e2e4f',
        navyDark: '#141f36',
        gold: '#c9a227',
        goldDeep: '#a8861c',
        goldSoft: '#faf4e2',
        parishBlue: '#236fa1',
        ink: '#24272e',
        soft: '#5b6270',
        line: '#e3e6ec',
        muted: '#f5f6f8',
      },
      fontFamily: {
        serif: ['Georgia', "'Palatino Linotype'", "'Book Antiqua'", 'Palatino', "'Times New Roman'", 'serif'],
        sans: ['system-ui', '-apple-system', "'Segoe UI'", 'Roboto', "'Helvetica Neue'", 'Arial', 'sans-serif'],
      },
    },
  },
  plugins: [],
};
