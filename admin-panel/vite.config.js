import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Dev rejimida /api so'rovlari Django backendga yo'naltiriladi (CORS kerak emas).
// Backend boshqa manzilda bo'lsa: VITE_PROXY_TARGET=http://192.168.1.7:8000 npm run dev
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    host: true,
    proxy: {
      "/api": {
        target: process.env.VITE_PROXY_TARGET || "http://localhost:8000",
        changeOrigin: true,
      },
    },
  },
});
