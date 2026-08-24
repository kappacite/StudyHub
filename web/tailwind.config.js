/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{vue,js,ts,jsx,tsx}'],
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
          ink: 'rgb(var(--sh-primary-ink) / <alpha-value>)',
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
        'cat-note': {
          DEFAULT: 'rgb(var(--sh-cat-note) / <alpha-value>)',
          soft: 'rgb(var(--sh-cat-note-soft) / <alpha-value>)',
        },
        'cat-pdf': {
          DEFAULT: 'rgb(var(--sh-cat-pdf) / <alpha-value>)',
          soft: 'rgb(var(--sh-cat-pdf-soft) / <alpha-value>)',
        },
        'cat-diagram': {
          DEFAULT: 'rgb(var(--sh-cat-diagram) / <alpha-value>)',
          soft: 'rgb(var(--sh-cat-diagram-soft) / <alpha-value>)',
        },
        'cat-deck': {
          DEFAULT: 'rgb(var(--sh-cat-deck) / <alpha-value>)',
          soft: 'rgb(var(--sh-cat-deck-soft) / <alpha-value>)',
        },
        'cat-set': {
          DEFAULT: 'rgb(var(--sh-cat-set) / <alpha-value>)',
          soft: 'rgb(var(--sh-cat-set-soft) / <alpha-value>)',
        },
      },
      fontFamily: {
        display: ['Bitter', 'Georgia', 'serif'],
        sans: ['Karla', 'system-ui', 'sans-serif'],
        mono: ['Space Mono', 'Courier New', 'monospace'],
      },
      fontSize: {
        tiny: ['10px', { lineHeight: '1.3' }],
        meta: ['13px', { lineHeight: '1.4' }],
        'display-md': ['19px', { lineHeight: '1.25', fontWeight: '700' }],
        'display-lg': ['30px', { lineHeight: '1.15', fontWeight: '700' }],
      },
      borderRadius: {
        'btn-primary': '10px',
        checkbox: '3px',
      },
      boxShadow: {
        'elev-1': 'var(--sh-shadow)',
        'elev-2': 'var(--sh-shadow-lg)',
        'elev-3': 'var(--sh-shadow-lg)',
        'elev-primary': '0 6px 20px -8px rgb(var(--sh-primary) / 0.35)',
        // Alias rétro-compat : composants existants (shadow-soft*) non touchés par ce plan.
        soft: 'var(--sh-shadow)',
        'soft-lg': 'var(--sh-shadow-lg)',
        'soft-primary': '0 6px 20px -8px rgb(var(--sh-primary) / 0.35)',
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
