import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// En desarrollo, redirige /api al backend local (puerto 8000).
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': 'http://127.0.0.1:8000',
    },
  },
  build: {
    outDir: 'dist',
  },
})
