<template>
  <a href="#main-content" class="skip-link">Saltar al contenido principal</a>
  <NetworkStatus />
  <nav class="nav-bar" :class="{ 'nav-open': menuOpen }">
    <router-link to="/" class="logo">
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-building-2"><path d="M6 22V4a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v18Z"/><path d="M6 12H4a2 2 0 0 0-2 2v6a2 2 0 0 0 2 2h2"/><path d="M18 9h2a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2h-2"/><path d="M10 6h4"/><path d="M10 10h4"/><path d="M10 14h4"/><path d="M10 18h4"/></svg>
      <span class="logo-text">IEE | Participación Digital</span>
    </router-link>
    <button class="menu-toggle" @click="menuOpen = !menuOpen" :aria-expanded="menuOpen" aria-label="Abrir menú de navegación">
      <svg v-if="!menuOpen" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="4" y1="6" x2="20" y2="6"/><line x1="4" y1="12" x2="20" y2="12"/><line x1="4" y1="18" x2="20" y2="18"/></svg>
      <svg v-else width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
    </button>
    <div class="nav-links" :class="{ open: menuOpen }">
      <LanguageSwitcher />
      <button @click="toggleTheme" class="theme-toggle" :aria-label="theme==='light' ? 'Activar modo oscuro' : 'Activar modo claro'" title="Cambiar tema">
        <svg v-if="theme === 'light'" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/></svg>
        <svg v-else width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2"/><path d="M12 20v2"/><path d="m4.93 4.93 1.41 1.41"/><path d="m17.66 17.66 1.41 1.41"/><path d="M2 12h2"/><path d="M20 12h2"/><path d="m6.34 17.66-1.41 1.41"/><path d="m19.07 4.93-1.41 1.41"/></svg>
      </button>
      <router-link to="/" @click="menuOpen = false">{{ $t('nav.home') }}</router-link>
      <router-link to="/transparencia" @click="menuOpen = false">{{ $t('nav.transparency') }}</router-link>
      <router-link to="/verificar" @click="menuOpen = false">{{ $t('nav.verify') }}</router-link>
      <router-link to="/urna" class="btn btn-primary nav-vote" @click="menuOpen = false">{{ $t('nav.vote') }}</router-link>
    </div>
  </nav>

  <main id="main-content" class="container">
    <router-view v-slot="{ Component }">
      <transition name="fade" mode="out-in">
        <component :is="Component" />
      </transition>
    </router-view>
  </main>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import NetworkStatus from './components/NetworkStatus.vue'
import LanguageSwitcher from './components/LanguageSwitcher.vue'

const theme = ref(localStorage.getItem('theme') || (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'));
const menuOpen = ref(false);

const toggleTheme = () => {
  theme.value = theme.value === 'light' ? 'dark' : 'light';
  localStorage.setItem('theme', theme.value);
  document.documentElement.setAttribute('data-theme', theme.value);
};

onMounted(() => {
  document.documentElement.setAttribute('data-theme', theme.value);
});
</script>

<style>
.theme-toggle { background:transparent; border:none; color:var(--text-muted); cursor:pointer; padding:0.5rem; display:flex; align-items:center; justify-content:center; border-radius:50%; transition:all 0.2s; }
.theme-toggle:hover { background:var(--panel-border); color:var(--primary); }

.menu-toggle {
  display: none;
  background: transparent;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  padding: 0.5rem;
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
    gap: 0.75rem;
    box-shadow: var(--panel-shadow);
    z-index: 99;
  }
  .nav-links.open {
    display: flex;
  }
  .nav-links a,
  .nav-links .btn {
    width: 100%;
    text-align: center;
    margin: 0 !important;
  }
  .nav-vote {
    margin-top: 0.5rem;
  }
}
</style>
