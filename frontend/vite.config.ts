import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { VitePWA } from 'vite-plugin-pwa'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    VitePWA({
      registerType: 'autoUpdate',
      workbox: {
        globPatterns: ['**/*.{js,css,html,ico,png,svg,woff2}'],
        runtimeCaching: [
          {
            urlPattern: /^\/api\/v1\/proceso\//,
            handler: 'CacheFirst',
            options: {
              cacheName: 'proceso-data',
              expiration: { maxAgeSeconds: 60 * 60 * 24 }
            }
          },
          {
            urlPattern: /^\/api\/v1\/vote\//,
            handler: 'NetworkOnly'
          }
        ]
      },
      manifest: {
        name: 'Voz ciudadana',
        short_name: 'VozCiudadana',
        description: 'Plataforma de participación ciudadana',
        theme_color: '#1a237e',
        background_color: '#ffffff',
        display: 'standalone',
        icons: [
          { src: '/favicon.svg', sizes: 'any', type: 'image/svg+xml' }
        ]
      }
    })
  ]
})
