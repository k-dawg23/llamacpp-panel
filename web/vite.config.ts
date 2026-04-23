import path from "node:path";
import { fileURLToPath } from "node:url";
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

const __dirname = path.dirname(fileURLToPath(import.meta.url));

export default defineConfig({
  plugins: [react()],
  server: {
    fs: {
      allow: [path.resolve(__dirname, "..")],
    },
    port: 5173,
    proxy: {
      "/api": {
        target: "http://127.0.0.1:8742",
        changeOrigin: true,
      },
      "/assets": {
        target: "http://127.0.0.1:8742",
        changeOrigin: true,
      },
    },
  },
});
