import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "var(--background)",
        foreground: "var(--foreground)",
      },
      keyframes: {
        // No overshoot — avoids layout overflow that caused the scrollbar flash
        "score-reveal": {
          "0%": { opacity: "0", transform: "scale(0.72)" },
          "100%": { opacity: "1", transform: "scale(1)" },
        },
        "slide-up": {
          "0%": { opacity: "0", transform: "translateY(14px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        // For navbar — slides in from above
        "slide-down": {
          "0%": { opacity: "0", transform: "translateY(-10px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        "glow-pulse": {
          "0%, 100%": { boxShadow: "0 0 20px rgba(34,197,94,0.25)" },
          "50%": { boxShadow: "0 0 45px rgba(34,197,94,0.55)" },
        },
        "border-pulse": {
          "0%, 100%": { borderColor: "rgba(255,255,255,0.15)" },
          "50%": { borderColor: "rgba(34,197,94,0.35)" },
        },
        "fade-in": {
          "0%": { opacity: "0", transform: "translateY(10px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        "fade-out": {
          "0%": { opacity: "1" },
          "100%": { opacity: "0" },
        },
        "slide-down-out": {
          "0%": { opacity: "1", transform: "translateY(0)" },
          "100%": { opacity: "0", transform: "translateY(12px)" },
        },
      },
      animation: {
        "score-reveal": "score-reveal 0.7s cubic-bezier(0.22,1,0.36,1) both",
        "slide-up": "slide-up 0.6s ease-out both",
        "slide-down": "slide-down 0.55s ease-out both",
        "fade-in": "fade-in 0.65s ease-out both",
        "fade-out": "fade-out 0.25s ease-in both",
        "slide-down-out": "slide-down-out 0.28s ease-in both",
        "glow-pulse": "glow-pulse 2s ease-in-out infinite",
        "border-pulse": "border-pulse 2.5s ease-in-out infinite",
      },
    },
  },
  plugins: [],
};
export default config;
