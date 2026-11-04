import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Build output goes to ../web so the FastAPI app serves it without Node installed.
export default defineConfig({
  plugins: [react()],
  base: "./",
  build: { outDir: "../web", emptyOutDir: true },
  server: { port: 5173, proxy: { "/api": "http://localhost:8000" } },
});
