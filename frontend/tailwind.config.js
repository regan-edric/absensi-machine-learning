import { defineConfig } from "@tailwindcss/vite";

export default defineConfig({
  content: ["./index.html", "./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      colors: {
        primary: {
          50: "oklch(0.97 0.01 250)",
          100: "oklch(0.93 0.03 250)",
          200: "oklch(0.87 0.06 250)",
          300: "oklch(0.77 0.12 250)",
          400: "oklch(0.68 0.18 250)",
          500: "oklch(0.58 0.24 250)",
          600: "oklch(0.48 0.24 250)",
          700: "oklch(0.42 0.22 250)",
          800: "oklch(0.36 0.18 250)",
          900: "oklch(0.30 0.14 250)",
        },
      },
      animation: {
        spin: "spin 1s linear infinite",
        pulse: "pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite",
        bounce: "bounce 1s infinite",
      },
    },
  },
});
