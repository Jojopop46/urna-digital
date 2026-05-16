<template>
  <div class="home-container">
    <div class="glass-panel hero">
      <h1 style="color:var(--primary);font-weight:800;letter-spacing:-0.5px;">{{ $t('home.title') }}</h1>
      <p style="font-size:1.1rem;color:var(--text-muted);font-weight:400;">{{ $t('home.subtitle') }}</p>
      <div class="actions">
        <router-link to="/urna" class="btn btn-primary">{{ $t('home.vote') }}</router-link>
        <router-link to="/transparencia" class="btn btn-outline">{{ $t('home.results') }}</router-link>
        <router-link to="/proposals" class="btn btn-outline">{{ $t('home.propose') }}</router-link>
        <router-link to="/admin" class="btn btn-outline">{{ $t('nav.admin') }}</router-link>
      </div>
    </div>
  </div>
</template>

<style scoped>
.home-container { display: flex; justify-content: center; align-items: center; min-height: 70vh; padding: 1rem; }
.hero { padding: 4rem 2rem; text-align: center; max-width: 800px; width: 100%; transition: all 0.3s; }
h1 { font-size: clamp(2rem, 5vw, 3rem); margin-bottom: 1.5rem; }
p { font-size: clamp(1rem, 3vw, 1.25rem); color: var(--text-muted); margin-bottom: 2.5rem; line-height: 1.6; }
.actions { display: flex; gap: 1rem; justify-content: center; flex-wrap: wrap; }
.btn { flex: 1; min-width: 150px; }
</style>
