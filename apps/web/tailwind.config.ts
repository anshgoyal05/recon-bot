import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: ["class"],
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        apple: {
          bg: {
            light: "#FBFBFD",
            dark: "#000000",
          },
          surface: {
            light: "#FFFFFF",
            dark: "#161617",
          },
          surfaceElevated: {
            light: "#FFFFFF",
            dark: "#1D1D1F",
          },
          text: {
            primary: {
              light: "#1D1D1F",
              dark: "#F5F5F7",
            },
            secondary: {
              light: "#6E6E73",
              dark: "#86868B",
            },
            tertiary: {
              light: "#A1A1A6",
              dark: "#6E6E73",
            },
          },
          accent: {
            DEFAULT: "#0071E3",
            hover: "#0077ED",
            light: "#E8F2FE",
            dark: "#0A3D73",
          },
          border: {
            light: "rgba(0, 0, 0, 0.08)",
            dark: "rgba(255, 255, 255, 0.12)",
          },
          status: {
            success: "#30D158",
            warning: "#FF9F0A",
            danger: "#FF453A",
            successLight: "rgba(48, 209, 88, 0.12)",
            warningLight: "rgba(255, 159, 10, 0.12)",
            dangerLight: "rgba(255, 69, 58, 0.12)",
          },
        },
      },
      fontFamily: {
        sans: [
          "-apple-system",
          "BlinkMacSystemFont",
          "SF Pro Display",
          "SF Pro Text",
          "Inter",
          "system-ui",
          "sans-serif",
        ],
        mono: [
          "SF Mono",
          "ui-monospace",
          "Menlo",
          "Monaco",
          "Cascadia Mono",
          "monospace",
        ],
      },
      borderRadius: {
        "apple-sm": "12px",
        "apple-md": "16px",
        "apple-lg": "20px",
        "apple-xl": "24px",
        "apple-2xl": "28px",
      },
      boxShadow: {
        "apple-subtle": "0 2px 8px rgba(0, 0, 0, 0.04)",
        "apple-card": "0 4px 20px rgba(0, 0, 0, 0.05), 0 1px 3px rgba(0, 0, 0, 0.02)",
        "apple-card-hover": "0 12px 36px rgba(0, 0, 0, 0.10), 0 2px 6px rgba(0, 0, 0, 0.04)",
        "apple-elevated": "0 20px 48px rgba(0, 0, 0, 0.12), 0 4px 12px rgba(0, 0, 0, 0.06)",
        "apple-glow-blue": "0 0 30px rgba(0, 113, 227, 0.35)",
        "apple-glow-red": "0 0 30px rgba(255, 69, 58, 0.35)",
        "apple-glow-green": "0 0 30px rgba(48, 209, 88, 0.35)",
      },
      animation: {
        "fade-in": "fadeIn 0.5s cubic-bezier(0.16, 1, 0.3, 1) forwards",
        "fade-up": "fadeUp 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards",
        "scale-in": "scaleIn 0.4s cubic-bezier(0.16, 1, 0.3, 1) forwards",
        "pulse-subtle": "pulseSubtle 3s ease-in-out infinite",
        "float": "float 6s ease-in-out infinite",
      },
      keyframes: {
        fadeIn: {
          "0%": { opacity: "0" },
          "100%": { opacity: "1" },
        },
        fadeUp: {
          "0%": { opacity: "0", transform: "translateY(20px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        scaleIn: {
          "0%": { opacity: "0", transform: "scale(0.96)" },
          "100%": { opacity: "1", transform: "scale(1)" },
        },
        pulseSubtle: {
          "0%, 100%": { opacity: "1", transform: "scale(1)" },
          "50%": { opacity: "0.85", transform: "scale(1.02)" },
        },
        float: {
          "0%, 100%": { transform: "translateY(0px)" },
          "50%": { transform: "translateY(-10px)" },
        },
      },
    },
  },
  plugins: [],
};

export default config;
