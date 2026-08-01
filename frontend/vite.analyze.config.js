import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { visualizer } from 'rollup-plugin-visualizer'

// Bundle analysis for the prerender PoC (docs/adr/0006-prerender-poc.md).
// `npm run analyze` builds with this config and writes dist/stats.html —
// a treemap of what's actually in each chunk, sized by gzip.
export default defineConfig({
  plugins: [
    react(),
    visualizer({
      filename: 'dist/stats.html',
      gzipSize: true,
      brotliSize: true,
      template: 'treemap',
    }),
  ],
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
  },
})
