/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      // Tokens sémantiques alimentés par des CSS custom properties (cf. src/style.css).
      // Le dark mode et tout ré-accent se règlent en un seul point.
      colors: {
        app: 'rgb(var(--sh-app) / <alpha-value>)',
        surface: {
          DEFAULT: 'rgb(var(--sh-surface) / <alpha-value>)',
          soft: 'rgb(var(--sh-surface-soft) / <alpha-value>)',
        },
        line: {
          DEFAULT: 'rgb(var(--sh-line) / <alpha-value>)',
          soft: 'rgb(var(--sh-line-soft) / <alpha-value>)',
        },
        ink: {
          DEFAULT: 'rgb(var(--sh-ink) / <alpha-value>)',
          muted: 'rgb(var(--sh-ink-muted) / <alpha-value>)',
          subtle: 'rgb(var(--sh-ink-subtle) / <alpha-value>)',
        },
        primary: {
          DEFAULT: 'rgb(var(--sh-primary) / <alpha-value>)',
          strong: 'rgb(var(--sh-primary-strong) / <alpha-value>)',
          soft: 'rgb(var(--sh-primary-soft) / <alpha-value>)',
        },
        accent: {
          DEFAULT: 'rgb(var(--sh-accent) / <alpha-value>)',
          soft: 'rgb(var(--sh-accent-soft) / <alpha-value>)',
        },
        success: {
          DEFAULT: 'rgb(var(--sh-success) / <alpha-value>)',
          soft: 'rgb(var(--sh-success-soft) / <alpha-value>)',
        },
        warning: {
          DEFAULT: 'rgb(var(--sh-warning) / <alpha-value>)',
          soft: 'rgb(var(--sh-warning-soft) / <alpha-value>)',
        },
        danger: {
          DEFAULT: 'rgb(var(--sh-danger) / <alpha-value>)',
          strong: 'rgb(var(--sh-danger-strong) / <alpha-value>)',
          soft: 'rgb(var(--sh-danger-soft) / <alpha-value>)',
        },
        info: {
          DEFAULT: 'rgb(var(--sh-info) / <alpha-value>)',
          soft: 'rgb(var(--sh-info-soft) / <alpha-value>)',
        },
      },
      fontFamily: {
        sans: ['Inter', 'Inter Variable', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      boxShadow: {
        // Élévations douces et basses (Soft & Friendly) — jamais d'ombre dure.
        soft: '0 1px 2px rgb(0 0 0 / 0.04), 0 4px 16px -4px rgb(0 0 0 / 0.06)',
        'soft-lg': '0 2px 8px rgb(0 0 0 / 0.05), 0 12px 32px -8px rgb(0 0 0 / 0.10)',
        'soft-primary': '0 6px 20px -6px rgb(var(--sh-primary) / 0.45)',
      },
      keyframes: {
        'fade-up': {
          '0%': { opacity: '0', transform: 'translateY(6px)' },
          '100%': { opacity: '1', transform: 'none' },
        },
        'pop-in': {
          '0%': { opacity: '0', transform: 'scale(.96)' },
          '100%': { opacity: '1', transform: 'scale(1)' },
        },
      },
      animation: {
        'fade-up': 'fade-up .25s ease-out both',
        'pop-in': 'pop-in .2s ease-out both',
      },
    },
  },
  plugins: [],
}
