import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// Keep API traffic same-origin and credentials exclusively in the Python backend.
export default defineConfig({
  plugins: [react()],
  server: { proxy: { '/api': 'http://127.0.0.1:8000' } },
});
