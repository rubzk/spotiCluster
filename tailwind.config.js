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
    },

  },
  plugins: [],
}
