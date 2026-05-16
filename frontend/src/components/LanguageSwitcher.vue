<template>
  <div class="lang-switcher" role="group" :aria-label="$t('language.select')">
    <button
      v-for="lang in langs"
      :key="lang.code"
      :aria-pressed="locale === lang.code"
      :aria-label="lang.name"
      @click="setLang(lang.code)"
      :class="['lang-btn', { active: locale === lang.code }]"
      :title="lang.name"
    >
      <span aria-hidden="true">{{ lang.flag }}</span>
      <span class="sr-only">{{ lang.name }}</span>
      <span aria-hidden="true">{{ lang.label }}</span>
    </button>
  </div>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n'
const { locale } = useI18n()

const langs = [
  { code: 'es', label: 'Español', name: 'Español estándar', flag: '🇲🇽' },
  { code: 'es-easy', label: 'Fácil', name: 'Español fácil de leer', flag: '🇲🇽' },
  { code: 'rar', label: 'Rarámuri', name: 'Idioma Rarámuri', flag: '🏔️' },
  { code: 'men', label: 'Plautdietsch', name: 'Idioma Plautdietsch (Menonita)', flag: '🌾' }
]

const setLang = (code: string) => {
  locale.value = code
  localStorage.setItem('lang', code)
}
</script>

<style scoped>
.lang-switcher {
  display: flex;
  gap: 0.25rem;
  align-items: center;
}
.lang-btn {
  background: transparent;
  border: 1px solid transparent;
  color: var(--text-muted);
  padding: 0.375rem 0.625rem;
  border-radius: var(--radius-sm);
  font-size: 0.8rem;
  font-weight: 600;
  cursor: pointer;
  transition: var(--transition);
  white-space: nowrap;
}
.lang-btn.active {
  background: var(--primary-light);
  color: var(--primary);
  border-color: var(--primary);
}
.lang-btn:hover:not(.active) {
  background: var(--bg-color);
  color: var(--text-main);
}
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border-width: 0;
}
@media (max-width: 768px) {
  .lang-switcher { justify-content: center; }
  .lang-btn { font-size: 0.875rem; padding: 0.5rem 0.75rem; }
}
</style>
