import path from "path"
import { defineConfig } from "vite"
import react from "@vitejs/plugin-react"
import tsconfigPaths from 'vite-tsconfig-paths'

export default defineConfig({
  plugins: [react(), tsconfigPaths()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
      "@/lib": path.resolve(__dirname, "./src/lib"),
      "@/lib/utils": path.resolve(__dirname, "./src/lib/utils"),
    },
  },
  build: {
    outDir: "dist",
    assetsDir: "assets",
    sourcemap: false
  },
  server: {
    host: "0.0.0.0",
    allowedHosts: true
  }
})