/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{vue,js,ts,jsx,tsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: 'var(--primary)',
          hover: 'var(--primary-hover)',
          soft: 'var(--primary-soft)',
          contrast: 'var(--primary-contrast)',
        },
        surface: {
          DEFAULT: 'var(--bg)',
          secondary: 'var(--bg-secondary)',
          elevated: 'var(--bg-elevated)',
          hover: 'var(--surface-hover)',
        },
        content: {
          DEFAULT: 'var(--text)',
          secondary: 'var(--text-secondary)',
        },
        line: 'var(--border)',
      },
      borderColor: {
        DEFAULT: 'var(--border)',
      },
      borderRadius: {
        gsm: 'var(--radius-sm)',
        gmd: 'var(--radius-md)',
        glg: 'var(--radius-lg)',
        pill: 'var(--radius-pill)',
      },
      boxShadow: {
        gsm: 'var(--shadow-sm)',
        gmd: 'var(--shadow-md)',
        glg: 'var(--shadow-lg)',
      },
      backgroundImage: {
        'gemini-accent': 'var(--accent-gradient)',
      },
    },
  },
  plugins: [],
}
