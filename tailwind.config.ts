import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        'dos': {
          'blue': '#011E3B',
          'blue-dark': '#0A0E1A',
          'orange': '#FF7D28',
          'orange-dark': '#FF3E04',
          'magenta': '#B1005A',
          'gray': '#E6E8EE',
          'gray-dark': '#CCC8D8',
          'border': '#4A4A6A',
          'white': '#FFFFFF',
        },
      },
      fontFamily: {
        'heading': ['Space Grotesk', 'sans-serif'],
        'body': ['Inter', 'sans-serif'],
      },
      spacing: {
        'xs': '16px',
        'sm': '24px',
        'md': '32px',
        'lg': '48px',
      },
      animation: {
        'fade-in': 'fadeIn 0.6s ease-out',
        'slide-up': 'slideUp 0.8s ease-out',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(20px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
      },
      backgroundImage: {
        'gradient-dos': 'linear-gradient(135deg, #011E3B 0%, #FF7D28 100%)',
      },
    },
  },
  plugins: [],
}
export default config
