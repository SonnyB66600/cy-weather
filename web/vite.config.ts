import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  // REMPLACEZ 'cy-weather' par le nom exact de votre dépôt GitHub
  base: '/cy-weather/', 
  plugins: [vue()],
})
