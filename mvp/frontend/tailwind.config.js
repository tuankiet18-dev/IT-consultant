/** Design tokens from the ui-ux-pro-max design system: Minimalism / Swiss, Inter, tracking blue + sparing orange accent. */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      fontFamily: { sans: ['"Inter Variable"', "Inter", "system-ui", "Segoe UI", "Roboto", "sans-serif"] },
      colors: {
        brand: { 50: "#EFF6FF", 100: "#DBEAFE", 200: "#BFDBFE", 300: "#93C5FD", 500: "#3B82F6", 600: "#2563EB", 700: "#1D4ED8", 800: "#1E40AF" },
        accent: { 50: "#FFF7ED", 600: "#EA580C", 700: "#C2410C" },
      },
      boxShadow: { card: "0 1px 2px rgb(15 23 42 / 0.05)" },
    },
  },
  plugins: [],
};
