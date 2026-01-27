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
        // Design System Colors
        primary: {
          50: '#E8EDFF',
          100: '#D1DBFF',
          200: '#A3B5FF',
          300: '#758FFF',
          400: '#4869FF',
          500: '#1E40AF', // Primary Brand Color
          600: '#163599',
          700: '#0F2A83',
          800: '#08206D',
          900: '#011657',
        },
        secondary: {
          50: '#EDF5FF',
          100: '#D6EBFF',
          200: '#ADD7FF',
          300: '#84C4FF',
          400: '#5BB0FF',
          500: '#3B82F6', // Secondary Brand Color
          600: '#2D6FD9',
          700: '#1F5BBC',
          800: '#11479F',
          900: '#033382',
        },
        cta: {
          50: '#FEF3E2',
          100: '#FDE8C5',
          200: '#FBD18B',
          300: '#F9BA51',
          400: '#F7A317',
          500: '#F59E0B', // CTA/Accent Color
          600: '#D48508',
          700: '#B36C05',
          800: '#925303',
          900: '#713A01',
        },
        background: {
          50: '#FFFFFF',
          100: '#F8FAFC',
          200: '#F1F5F9',
        },
        text: {
          50: '#3B82F6',
          100: '#2563EB',
          200: '#1D4ED8',
          300: '#1E40AF', // Primary Text Color
          400: '#1E3A8A', // Main Text Color
          500: '#172554',
          600: '#0F172A',
          700: '#0C1220',
          800: '#070D18',
          900: '#030711',
        },
        dark: {
          100: '#1E293B',
          200: '#1A2234',
          300: '#151C2C',
          400: '#111827',
          500: '#0D1321',
        }
      },
      fontFamily: {
        'code': ['Fira Code', 'monospace'],
        'sans': ['Fira Sans', 'Inter', 'system-ui', 'sans-serif'],
      },
      boxShadow: {
        'sm': '0 1px 2px rgba(30, 64, 175, 0.05)',
        'md': '0 4px 6px rgba(30, 64, 175, 0.1)',
        'lg': '0 10px 15px rgba(30, 64, 175, 0.1)',
        'xl': '0 20px 25px rgba(30, 64, 175, 0.15)',
      },
      spacing: {
        'xs': '0.25rem',  // 4px
        'sm': '0.5rem',   // 8px
        'md': '1rem',     // 16px
        'lg': '1.5rem',   // 24px
        'xl': '2rem',     // 32px
        '2xl': '3rem',    // 48px
        '3xl': '4rem',    // 64px
      },
    },
  },
  plugins: [],
}
