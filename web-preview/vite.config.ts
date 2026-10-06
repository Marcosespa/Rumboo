import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
export default defineConfig({plugins: [react(), tailwindcss()], build: {cssTarget: ['chrome111', 'edge111', 'firefox113', 'safari16.4']}, server: {proxy: {'/api': {target: process.env.API_URL || 'http://localhost:8000', changeOrigin: true}}}, test: {environment: 'jsdom', setupFiles: './src/test-setup.ts', include: ['src/**/*.test.{ts,tsx}']}})
