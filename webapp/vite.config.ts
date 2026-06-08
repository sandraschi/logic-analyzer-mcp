import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";
import path from "path";

export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: { "@": path.resolve(__dirname, "./src") },
  },
  server: {
    port: 10987,
    strictPort: true,
    host: "127.0.0.1",
    proxy: {
      "/api": { target: "http://127.0.0.1:10985", changeOrigin: true },
      "/mcp": { target: "http://127.0.0.1:10985", changeOrigin: true },
      "/health": { target: "http://127.0.0.1:10985", changeOrigin: true },
    },
  },
});
