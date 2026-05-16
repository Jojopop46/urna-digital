import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import { router } from './router'
import { createPinia } from 'pinia'
import { createI18n } from 'vue-i18n'
import es from './locales/es.json'
import esEasy from './locales/es-easy.json'
import rar from './locales/rar.json'

const i18n = createI18n({
  legacy: false,
  locale: localStorage.getItem('lang') || 'es',
  fallbackLocale: 'es',
  messages: { es, 'es-easy': esEasy, rar }
})

const pinia = createPinia()
const app = createApp(App)

app.use(router)
app.use(pinia)
app.use(i18n)
app.mount('#app')
