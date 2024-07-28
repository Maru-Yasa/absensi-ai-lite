/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./templates/**/*.html"],
  theme: {
    extend: {},
  },
  plugins: [require('daisyui')],
  daisyui: {
    themes: [
      {
        mytheme: {
          "primary": "#f100ff",
          "secondary": "#0000ff",
          "accent": "#00d700",
          "neutral": "#1c1c00",
          "base-100": "#ffffd9",
          "info": "#0093f8",
          "success": "#00bf75",
          "warning": "#e18900",
          "error": "#f8204b",
        },
      },
    ]
  }
}


