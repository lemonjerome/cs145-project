import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import tailwindcss from '@tailwindcss/vite'
import path from 'path' // Import path for resolving aliases

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue(), tailwindcss()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'), // Map @ to the src folder
    },
  },
  // for production set to '/static/'
  // for development set to '/'
  base: process.env.VITE_BASE_URL,
})
