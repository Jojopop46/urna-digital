<template>
  <div class="lang-switcher" role="navigation" :aria-label="$t('language.select')">
    <button
      v-for="lang in langs"
      :key="lang.code"
      :aria-pressed="locale === lang.code"
      :aria-label="`Cambiar idioma a ${lang.name}`"
      @click="setLang(lang.code)"
      :class="{ active: locale === lang.code }"
    >{{ lang.label }}</button>
  </div>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n'
const { locale } = useI18n()

const langs = [
  { code: 'es', label: 'Español', name: 'Español estándar' },
  { code: 'es-easy', label: 'Fácil', name: 'Español fácil de leer' },
  { code: 'rar', label: 'Rarámuri', name: 'Idioma Rarámuri' }
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
.lang-switcher button {
  background: transparent;
  border: 1px solid var(--panel-border);
  color: var(--text-muted);
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
  cursor: pointer;
  transition: all 0.2s;
}
.lang-switcher button.active {
  background: var(--primary);
  color: white;
  border-color: var(--primary);
}
.lang-switcher button:hover:not(.active) {
  border-color: var(--primary);
  color: var(--primary);
}
</style>
