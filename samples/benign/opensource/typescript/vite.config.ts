// Source: TypeScript Benign Sample
// Generated: 2026-04-02 11:48:04.520392

/**
 * Vite 配置 - 良性
 */
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/api': 'http://localhost:8080',
    },
  },
});
