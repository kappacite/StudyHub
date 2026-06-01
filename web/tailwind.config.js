/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#4F46E5',
          dark: '#3730A3',
        },
        surface: {
          DEFAULT: '#FFFFFF',
          dark: '#1E1E2E',
        },
        muted: '#6B7280',
        success: '#22C55E',
        warning: '#F59E0B',
        danger: '#EF4444',
      },
      fontFamily: {
        sans: ['Inter', 'Inter Variable', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
    },
  },
  plugins: [],
}
