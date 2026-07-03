import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    port: 5173,
    proxy: {
      '/detect': 'http://localhost:8000',
      '/rag': 'http://localhost:8000',
      '/workorders': 'http://localhost:8000',
      '/reports': 'http://localhost:8000',
      '/dashboard': 'http://localhost:8000',
      '/files': 'http://localhost:8000',
    },
  },
})
