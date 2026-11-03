/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#f0fdf4',
          100: '#dcfce7',
          500: '#22c55e',
          600: '#16a34a',
          700: '#15803d',
          800: '#166534',
        },
        transit: {
          train: '#10b981',
          bus: '#f59e0b',
          metro: '#6366f1',
          walk: '#94a3b8'
        }
      }
    },
  },
  plugins: [],
}

