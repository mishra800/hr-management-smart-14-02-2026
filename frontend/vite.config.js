import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  // Load env file from root directory (one level up from frontend)
  const env = loadEnv(mode, path.resolve(__dirname, '..'), '')
  
  return {
    plugins: [react()],
    envDir: path.resolve(__dirname, '..'), // Load .env from root directory
    envDir: path.resolve(__dirname, '..'), // Load .env from root directory
    server: {
      // Configure proper MIME types for resume files
      middlewareMode: false,
      fs: {
        allow: ['..']
      }
    },
    // Configure static asset handling
    assetsInclude: ['**/*.docx', '**/*.doc', '**/*.pdf'],
    build: {
      outDir: 'dist',
      sourcemap: false,
      rollupOptions: {
        output: {
          manualChunks: {
            vendor: ['react', 'react-dom'],
            router: ['react-router-dom'],
            ui: ['lucide-react']
          }
        }
      }
    }
  }
})
