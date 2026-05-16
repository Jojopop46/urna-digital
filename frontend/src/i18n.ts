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

export default i18n
