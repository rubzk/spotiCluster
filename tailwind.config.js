/** @type {import('tailwindcss').Config} */

const { fontFamily, fontWeight } = require('tailwindcss/defaultTheme')

module.exports = {
  mode: "jit",
  content: [
    "./templates/**/*.{html,js}"
  ],
  theme: {
    extend: {
      fontFamily: {
        ...fontFamily,
        'sans': ['Helvetica', 'Arial', 'sans-serif'],
      },
      animation: {
        fadedown: "fadedown 0.5s"
      },
      keyframes: {
        fadedown: {
          "0%": {
            opacity: 0,
            transform: "translateY(-30px) scale(0.9)",
          },
          "100%": {
            opacity: 100,
            transform: "translateY(0px) scale(1)",
          }
        }
      }
    },

  },
  plugins: [],
}
