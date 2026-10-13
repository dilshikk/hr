import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  // Локально запросы /api идут на uvicorn; в продакшене это делает nginx.
  server: { proxy: { "/api": "http://127.0.0.1:8000" } },
});
