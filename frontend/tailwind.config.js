/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ["IBM Plex Sans", "Segoe UI", "sans-serif"],
      },
      colors: {
        ink: "#102027",
        mist: "#f4f7f8",
        signal: "#0f766e",
      },
    },
  },
  plugins: [],
};
