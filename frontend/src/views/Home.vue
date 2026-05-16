<template>
  <div class="home">
    <!-- Hero -->
    <section class="hero-section" aria-labelledby="home-title">
      <div class="glass-panel hero-card">
        <div class="hero-badge"><span aria-hidden="true">🔒</span> {{ $t('home.badge') }}</div>
        <h1 id="home-title">{{ $t('home.title') }}</h1>
        <p class="hero-subtitle">{{ $t('home.subtitle') }}</p>
        <div class="hero-actions">
          <router-link to="/urna" class="btn btn-primary hero-btn">
            <svg aria-hidden="true" focusable="false" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
            {{ $t('home.vote') }}
          </router-link>
          <router-link to="/transparencia" class="btn btn-outline hero-btn">
            {{ $t('home.results') }}
          </router-link>
        </div>
      </div>
    </section>

    <!-- Features -->
    <section class="features-section" aria-labelledby="features-title">
      <h2 id="features-title" class="sr-only">{{ $t('home.features.anonymous.title') }}, {{ $t('home.features.transparent.title') }}, {{ $t('home.features.offline.title') }}</h2>
      <div class="features-grid">
        <div class="glass-panel feature-card">
          <div class="feature-icon" style="background: var(--primary-light); color: var(--primary);"><span aria-hidden="true">🔐</span></div>
          <h3>{{ $t('home.features.anonymous.title') }}</h3>
          <p>{{ $t('home.features.anonymous.desc') }}</p>
        </div>
        <div class="glass-panel feature-card">
          <div class="feature-icon" style="background: var(--secondary-light); color: var(--secondary);"><span aria-hidden="true">🌐</span></div>
          <h3>{{ $t('home.features.transparent.title') }}</h3>
          <p>{{ $t('home.features.transparent.desc') }}</p>
        </div>
        <div class="glass-panel feature-card">
          <div class="feature-icon" style="background: var(--warning-light); color: var(--warning);"><span aria-hidden="true">📱</span></div>
          <h3>{{ $t('home.features.offline.title') }}</h3>
          <p>{{ $t('home.features.offline.desc') }}</p>
        </div>
      </div>
    </section>

    <!-- How it works -->
    <section class="how-section" aria-labelledby="how-title">
      <h2 id="how-title" class="section-title">{{ $t('home.how_it_works.title') }}</h2>
      <div class="steps-row">
        <div class="step-item">
          <div class="step-num">1</div>
          <h4>{{ $t('home.how_it_works.steps.1.title') }}</h4>
          <p>{{ $t('home.how_it_works.steps.1.desc') }}</p>
        </div>
        <div class="step-arrow" aria-hidden="true">→</div>
        <div class="step-item">
          <div class="step-num">2</div>
          <h4>{{ $t('home.how_it_works.steps.2.title') }}</h4>
          <p>{{ $t('home.how_it_works.steps.2.desc') }}</p>
        </div>
        <div class="step-arrow" aria-hidden="true">→</div>
        <div class="step-item">
          <div class="step-num">3</div>
          <h4>{{ $t('home.how_it_works.steps.3.title') }}</h4>
          <p>{{ $t('home.how_it_works.steps.3.desc') }}</p>
        </div>
        <div class="step-arrow" aria-hidden="true">→</div>
        <div class="step-item">
          <div class="step-num">4</div>
          <h4>{{ $t('home.how_it_works.steps.4.title') }}</h4>
          <p>{{ $t('home.how_it_works.steps.4.desc') }}</p>
        </div>
      </div>
    </section>

    <!-- Propuestas destacadas -->
    <section class="featured-proposals-section" aria-labelledby="featured-title" v-if="featuredProposals.length">
      <div class="section-header">
        <h2 id="featured-title">{{ $t('home.featured.title') }}</h2>
        <router-link to="/proposals" class="view-all-link">{{ $t('home.featured.view_all') }} →</router-link>
      </div>
      <div class="featured-grid">
        <div v-for="p in featuredProposals" :key="p.id" class="glass-panel featured-card">
          <div class="featured-status" :class="`status-${p.status}`">{{ statusLabel(p.status) }}</div>
          <h3>{{ p.titulo }}</h3>
          <p>{{ p.descripcion }}</p>
          <div class="featured-meta">
            <span v-if="p.municipio" class="meta-tag"><span aria-hidden="true">📍</span> {{ p.municipio }}</span>
            <span v-if="p.area" class="meta-tag"><span aria-hidden="true">💡</span> {{ p.area }}</span>
          </div>
        </div>
      </div>
    </section>

    <!-- CTA -->
    <section class="cta-section" aria-labelledby="cta-title">
      <div class="glass-panel cta-card">
        <h2 id="cta-title">{{ $t('home.cta.title') }}</h2>
        <p>{{ $t('home.cta.desc') }}</p>
        <router-link to="/urna" class="btn btn-primary">{{ $t('home.cta.button') }}</router-link>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue';
import { useI18n } from 'vue-i18n';
import { useUrnaStore } from '../stores/useUrnaStore';
import { api } from '../services/api';

const { t } = useI18n();
const store = useUrnaStore();

const featuredProposals = computed(() => store.props.filter((p) => p.status === 'approved').slice(0, 3));

function statusLabel(status: string) {
  const map: Record<string, string> = {
    pending: t('proposals.status.pending'),
    approved: t('proposals.status.approved'),
    rejected: t('proposals.status.rejected'),
  };
  return map[status] ?? status;
}

onMounted(async () => {
  if (store.props.length === 0) {
    try {
      const data = await api.get('/api/v1/proposals?status=approved');
      store.props = data;
    } catch {
      // silently fail
    }
  }
});
</script>

<style scoped>
.home { display: flex; flex-direction: column; gap: 2.5rem; }

/* Hero */
.hero-section { text-align: center; }
.hero-card {
  padding: 3.5rem 2rem;
  max-width: 800px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1.25rem;
}
.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  background: var(--primary-light);
  color: var(--primary);
  padding: 0.375rem 1rem;
  border-radius: 9999px;
  font-size: 0.875rem;
  font-weight: 600;
}
.hero-card h1 {
  font-size: clamp(2rem, 5vw, 3rem);
  font-weight: 800;
  color: var(--primary);
  line-height: 1.15;
  letter-spacing: -0.02em;
}
.hero-subtitle {
  font-size: clamp(1.05rem, 2.5vw, 1.25rem);
  color: var(--text-muted);
  max-width: 600px;
  line-height: 1.6;
}
.hero-actions {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
  justify-content: center;
  margin-top: 0.5rem;
}
.hero-btn {
  min-width: 180px;
  padding: 1rem 2rem;
  font-size: 1.05rem;
}

/* Features */
.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 1.25rem;
}
.feature-card {
  padding: 2rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  text-align: center;
}
.feature-icon {
  width: 56px;
  height: 56px;
  border-radius: var(--radius-lg);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  margin: 0 auto;
}
.feature-card h3 {
  font-size: 1.15rem;
  font-weight: 700;
}
.feature-card p {
  color: var(--text-muted);
  font-size: 0.95rem;
  line-height: 1.6;
}

/* How it works */
.how-section { text-align: center; }
.section-title {
  font-size: clamp(1.5rem, 3vw, 2rem);
  font-weight: 800;
  margin-bottom: 2rem;
  color: var(--text-main);
}
.steps-row {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  flex-wrap: wrap;
}
.step-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  max-width: 160px;
  text-align: center;
}
.step-num {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: var(--primary);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 1.1rem;
}
.step-item h4 {
  font-weight: 700;
  font-size: 1rem;
}
.step-item p {
  font-size: 0.85rem;
  color: var(--text-muted);
}
.step-arrow {
  font-size: 1.5rem;
  color: var(--primary);
  font-weight: 700;
}
@media (max-width: 768px) {
  .step-arrow { display: none; }
  .steps-row { gap: 1.5rem; }
}

/* CTA */
.cta-card {
  padding: 3rem 2rem;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  background: linear-gradient(135deg, var(--primary-light) 0%, var(--panel-bg) 100%);
  border-color: var(--primary);
}
.cta-card h2 {
  font-size: 1.75rem;
  font-weight: 800;
  color: var(--primary);
}
.cta-card p {
  color: var(--text-muted);
  max-width: 500px;
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

/* Featured proposals */
.featured-proposals-section { display: flex; flex-direction: column; gap: 1rem; }
.section-header { display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 0.5rem; }
.section-header h2 { font-size: clamp(1.25rem, 3vw, 1.5rem); font-weight: 800; color: var(--text-main); }
.view-all-link { color: var(--primary); font-weight: 600; text-decoration: none; font-size: 0.95rem; }
.view-all-link:hover { text-decoration: underline; }
.featured-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 1rem; }
.featured-card { padding: 1.5rem; display: flex; flex-direction: column; gap: 0.5rem; }
.featured-card h3 { font-size: 1.05rem; font-weight: 700; color: var(--primary); }
.featured-card p { color: var(--text-muted); font-size: 0.9rem; line-height: 1.5; display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden; }
.featured-status { align-self: flex-start; font-size: 0.7rem; font-weight: 700; text-transform: uppercase; padding: 0.2rem 0.55rem; border-radius: 999px; }
.status-approved { background: #10b981; color: #fff; }
.featured-meta { display: flex; flex-wrap: wrap; gap: 0.5rem; margin-top: auto; padding-top: 0.5rem; }
.meta-tag { display: inline-flex; align-items: center; gap: 0.25rem; background: var(--panel-border); padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 0.8rem; color: var(--text-main); }
</style>
