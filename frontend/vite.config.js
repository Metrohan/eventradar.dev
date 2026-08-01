import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    host: '0.0.0.0',
    // Allow external domain access via Nginx reverse proxy
    allowedHosts: ['eventradar.dev', 'www.eventradar.dev'],
    proxy: {
      '/api': {
        target: 'http://backend:8000',
        changeOrigin: true,
        secure: false,
      },
      '/sitemap.xml': {
        target: 'http://backend:8000',
        changeOrigin: true,
        secure: false,
      },
      '/media': {
        target: 'http://backend:8000',
        changeOrigin: true,
        secure: false,
      },
      '/health': {
        target: 'http://backend:8000',
        changeOrigin: true,
        secure: false,
      }
    }
  },
  preview: {
    // Lets `vite preview` (and the prerender PoC script that runs on top
    // of it — see docs/adr/0006-prerender-poc.md) reach a real backend the
    // same way the dev server does. Override for local runs outside
    // Docker, e.g. VITE_PREVIEW_API_TARGET=http://localhost:8000
    proxy: {
      '/api': {
        target: process.env.VITE_PREVIEW_API_TARGET || 'http://backend:8000',
        changeOrigin: true,
        secure: false,
      },
      '/sitemap.xml': {
        target: process.env.VITE_PREVIEW_API_TARGET || 'http://backend:8000',
        changeOrigin: true,
        secure: false,
      },
      '/media': {
        target: process.env.VITE_PREVIEW_API_TARGET || 'http://backend:8000',
        changeOrigin: true,
        secure: false,
      },
      '/health': {
        target: process.env.VITE_PREVIEW_API_TARGET || 'http://backend:8000',
        changeOrigin: true,
        secure: false,
      }
    }
  },
  build: {
    outDir: 'dist',
    sourcemap: false,
    chunkSizeWarningLimit: 500,
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom', 'react-router-dom'],
          query: ['react-query'],
          ui: ['date-fns', 'react-hot-toast'],
        },
      },
    },
  }
})


