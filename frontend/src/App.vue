<template>
  <a href="#main-content" class="skip-link">{{ $t('a11y.skip_to_content') || 'Saltar al contenido principal' }}</a>
  <NetworkStatus />
  <nav class="nav-bar" :class="{ 'nav-open': menuOpen }" :aria-label="$t('a11y.menu')">
    <router-link to="/" class="logo">
      <svg aria-hidden="true" focusable="false" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 22V4a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v18Z"/><path d="M6 12H4a2 2 0 0 0-2 2v6a2 2 0 0 0 2 2h2"/><path d="M18 9h2a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2h-2"/><path d="M10 6h4"/><path d="M10 10h4"/><path d="M10 14h4"/><path d="M10 18h4"/></svg>
      <span class="logo-text">Urna Digital</span>
    </router-link>
    <button ref="menuToggleRef" class="menu-toggle" @click="toggleMenu" :aria-expanded="menuOpen" :aria-label="menuOpen ? $t('a11y.close_menu') : $t('a11y.open_menu')">
      <svg v-if="!menuOpen" aria-hidden="true" focusable="false" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="4" y1="6" x2="20" y2="6"/><line x1="4" y1="12" x2="20" y2="12"/><line x1="4" y1="18" x2="20" y2="18"/></svg>
      <svg v-else aria-hidden="true" focusable="false" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
    </button>
    <div ref="navLinksRef" class="nav-links" :class="{ open: menuOpen }">
      <router-link ref="firstLinkRef" to="/" @click="closeMenu">{{ $t('nav.home') }}</router-link>
      <router-link to="/transparencia" @click="closeMenu">{{ $t('nav.transparency') }}</router-link>
      <router-link to="/verificar" @click="closeMenu">{{ $t('nav.verify') }}</router-link>
      <LanguageSwitcher />
      <button @click="toggleTTS" class="nav-icon-btn tts-toggle" :class="{ active: ttsEnabled }" :aria-label="ttsEnabled ? $t('a11y.tts_off') : $t('a11y.tts_on')" :title="ttsEnabled ? $t('a11y.tts_off') : $t('a11y.tts_on')">
        <svg aria-hidden="true" focusable="false" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/><path d="M15.54 8.46a5 5 0 0 1 0 7.07"/><path d="M19.07 4.93a10 10 0 0 1 0 14.14"/></svg>
      </button>
      <button @click="openA11yPanel" class="nav-icon-btn a11y-nav-btn" :aria-label="$t('a11y_panel.open')" :title="$t('a11y_panel.open')">
        <svg aria-hidden="true" focusable="false" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/></svg>
      </button>
      <button @click="toggleTheme" class="nav-icon-btn theme-toggle" :aria-label="theme==='light' ? $t('a11y.dark_mode') : $t('a11y.light_mode')" :title="$t('a11y.dark_mode') + ' / ' + $t('a11y.light_mode')">
        <svg v-if="theme === 'light'" aria-hidden="true" focusable="false" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/></svg>
        <svg v-else aria-hidden="true" focusable="false" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="4"/><path d="M12 2v2"/><path d="M12 20v2"/><path d="m4.93 4.93 1.41 1.41"/><path d="m17.66 17.66 1.41 1.41"/><path d="M2 12h2"/><path d="M20 12h2"/></svg>
      </button>
      <router-link to="/urna" class="btn btn-primary nav-vote" @click="closeMenu">{{ $t('nav.vote') }}</router-link>
    </div>
  </nav>

  <main id="main-content" class="container">
    <router-view v-slot="{ Component }">
      <transition name="fade" mode="out-in">
        <component :is="Component" />
      </transition>
    </router-view>
  </main>

  <AccessibilityPanel v-model="a11yOpen" />
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick, watch } from 'vue';
import { useI18n } from 'vue-i18n';
import NetworkStatus from './components/NetworkStatus.vue'
import LanguageSwitcher from './components/LanguageSwitcher.vue'
import AccessibilityPanel from './components/AccessibilityPanel.vue'
import { useTTS } from './composables/useTTS'

const theme = ref(localStorage.getItem('theme') || (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'));
const menuOpen = ref(false);
const firstLinkRef = ref<HTMLAnchorElement | null>(null);
const a11yOpen = ref(false);

const { locale } = useI18n();
const { enabled: ttsEnabled, toggle: toggleTTS } = useTTS();

watch(locale, (newLocale) => {
  document.documentElement.lang = newLocale === 'men' ? 'de' : (newLocale === 'rar' ? 'es' : newLocale);
}, { immediate: true });

const toggleTheme = () => {
  theme.value = theme.value === 'light' ? 'dark' : 'light';
  localStorage.setItem('theme', theme.value);
  document.documentElement.setAttribute('data-theme', theme.value);
};

const toggleMenu = () => {
  menuOpen.value = !menuOpen.value;
  if (menuOpen.value) {
    nextTick(() => {
      firstLinkRef.value?.focus();
    });
  }
};

const closeMenu = () => {
  menuOpen.value = false;
};

const openA11yPanel = () => {
  a11yOpen.value = true;
};

onMounted(() => {
  document.documentElement.setAttribute('data-theme', theme.value);
});
</script>

<style scoped>
.nav-icon-btn {
  background: transparent;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  padding: 0.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: var(--transition);
}

.nav-icon-btn:hover {
  background: var(--primary-light);
  color: var(--primary);
}

.theme-toggle {
  /* keep existing behavior */
}

.tts-toggle.active {
  background: var(--primary);
  color: white;
}

.a11y-nav-btn:hover {
  background: var(--secondary-light);
  color: var(--secondary);
}

.menu-toggle {
  display: none;
  background: transparent;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  padding: 0.5rem;
  border-radius: var(--radius-sm);
}

.logo-text {
  white-space: nowrap;
}

@media (max-width: 768px) {
  .nav-bar {
    flex-wrap: nowrap;
    padding: 0.75rem 1rem;
  }
  .menu-toggle {
    display: flex;
    align-items: center;
    justify-content: center;
  }
  .nav-links {
    display: none;
    position: absolute;
    top: 100%;
    left: 0;
    right: 0;
    background: var(--panel-bg);
    border-bottom: 1px solid var(--panel-border);
    flex-direction: column;
    padding: 1rem;
    gap: 0.5rem;
    box-shadow: var(--panel-shadow-lg);
    z-index: 99;
    align-items: stretch;
  }
  .nav-links.open {
    display: flex;
  }
  .nav-links a,
  .nav-links .btn {
    width: 100%;
    text-align: center;
    margin: 0 !important;
    justify-content: center;
  }
  .nav-vote {
    margin-top: 0.5rem;
  }
}
</style>
