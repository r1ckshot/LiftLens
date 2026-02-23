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
        "score-reveal": {
          "0%": { opacity: "0", transform: "scale(0.6)" },
          "60%": { transform: "scale(1.05)" },
          "100%": { opacity: "1", transform: "scale(1)" },
        },
        "slide-up": {
          "0%": { opacity: "0", transform: "translateY(16px)" },
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
          "0%": { opacity: "0", transform: "translateY(14px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
      },
      animation: {
        "score-reveal": "score-reveal 0.5s cubic-bezier(0.34,1.56,0.64,1) forwards",
        "slide-up": "slide-up 0.4s ease-out forwards",
        "fade-in": "fade-in 0.5s ease-out forwards",
        "glow-pulse": "glow-pulse 2s ease-in-out infinite",
        "border-pulse": "border-pulse 2.5s ease-in-out infinite",
      },
    },
  },
  plugins: [],
};
export default config;
