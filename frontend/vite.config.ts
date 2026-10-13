import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// В разработке запросы /api уходят на локальный FastAPI.
export default defineConfig({
  plugins: [react()],
  server: { proxy: { "/api": "http://localhost:8000" } },
});
