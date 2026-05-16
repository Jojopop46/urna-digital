<template>
  <div class="lang-switcher" role="group" :aria-label="$t('language.select')">
    <button
      v-for="lang in langs"
      :key="lang.code"
      :aria-pressed="locale === lang.code"
      @click="setLang(lang.code)"
      :class="['lang-btn', { active: locale === lang.code }]"
      :title="lang.name"
    >
      {{ lang.flag }} {{ lang.label }}
    </button>
  </div>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n'
const { locale } = useI18n()

const langs = [
  { code: 'es', label: 'Español', name: 'Español estándar', flag: '🇲🇽' },
  { code: 'es-easy', label: 'Fácil', name: 'Español fácil de leer', flag: '🇲🇽' },
  { code: 'rar', label: 'Rarámuri', name: 'Idioma Rarámuri', flag: '🏔️' }
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
@media (max-width: 768px) {
  .lang-switcher { justify-content: center; }
  .lang-btn { font-size: 0.875rem; padding: 0.5rem 0.75rem; }
}
</style>
