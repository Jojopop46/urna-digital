<template>
  <div class="proposals">
    <h1>{{ $t('proposals.title') }}</h1>
    <form @submit.prevent="addProp" class="glass-panel proposal-form">
      <div class="form-group">
        <label for="prop-titulo">{{ $t('proposals.form.title_label') }}</label>
        <input id="prop-titulo" v-model="f.titulo" required class="form-input">
      </div>
      <div class="form-group">
        <label for="prop-desc">{{ $t('proposals.form.desc_label') }}</label>
        <textarea id="prop-desc" v-model="f.descripcion" required class="form-input"></textarea>
      </div>
      <div class="form-row">
        <div class="form-group">
          <label for="prop-costo">{{ $t('proposals.form.cost_label') }}</label>
          <input id="prop-costo" v-model="f.costo" class="form-input">
        </div>
        <div class="form-group">
          <label for="prop-area">{{ $t('proposals.form.area_label') }}</label>
          <input id="prop-area" v-model="f.area" class="form-input">
        </div>
        <div class="form-group">
          <label for="prop-municipio">{{ $t('proposals.form.municipio_label') }}</label>
          <input id="prop-municipio" v-model="f.municipio" class="form-input">
        </div>
      </div>
      <button class="btn btn-primary submit-btn" type="submit">{{ $t('proposals.form.submit') }}</button>
      <p v-if="msg" class="form-msg" role="status">{{ msg }}</p>
    </form>

    <h2>{{ $t('proposals.list_title') }}</h2>
    <div class="filter-bar" role="group" :aria-label="$t('proposals.filter_label')">
      <button
        v-for="opt in filterOptions"
        :key="opt.value"
        class="filter-btn"
        :class="{ active: filter === opt.value }"
        @click="filter = opt.value"
        :aria-pressed="filter === opt.value"
      >
        {{ opt.label }}
        <span class="filter-count" :class="`count-${opt.value}`">{{ counts[opt.value] ?? 0 }}</span>
      </button>
    </div>

    <div class="proposal-grid">
      <div v-for="p in filtered" :key="p.id" class="glass-panel proposal-card">
        <div class="card-header">
          <h3>{{ p.titulo }}</h3>
          <span class="status-badge" :class="`status-${p.status}`">{{ statusLabel(p.status) }}</span>
        </div>
        <p>{{ p.descripcion }}</p>
        <div class="badges">
          <span v-if="p.costo" class="badge"><span aria-hidden="true">💰</span> {{ p.costo }}</span>
          <span class="badge"><span aria-hidden="true">📍</span> {{ p.municipio || '—' }}</span>
          <span class="badge"><span aria-hidden="true">💡</span> {{ p.area || '—' }}</span>
        </div>
      </div>
    </div>
    <p v-if="filtered.length === 0" class="empty-state">{{ $t('proposals.empty') }}</p>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useI18n } from 'vue-i18n';
import { useUrnaStore } from '../stores/useUrnaStore';
import { api } from '../services/api';

const { t } = useI18n();
const s = useUrnaStore();
const f = ref({ titulo: '', descripcion: '', costo: '', area: '', municipio: '' });
const msg = ref('');
const filter = ref<'all' | 'pending' | 'approved' | 'rejected'>('all');

const filterOptions = computed(() => [
  { value: 'all', label: t('proposals.filters.all') },
  { value: 'pending', label: t('proposals.filters.pending') },
  { value: 'approved', label: t('proposals.filters.approved') },
  { value: 'rejected', label: t('proposals.filters.rejected') },
]);

const filtered = computed(() => {
  if (filter.value === 'all') return s.props;
  return s.props.filter((x) => x.status === filter.value);
});

const counts = computed(() => ({
  all: s.props.length,
  pending: s.props.filter((x) => x.status === 'pending').length,
  approved: s.props.filter((x) => x.status === 'approved').length,
  rejected: s.props.filter((x) => x.status === 'rejected').length,
}));

function statusLabel(status: string) {
  const map: Record<string, string> = {
    pending: t('proposals.status.pending'),
    approved: t('proposals.status.approved'),
    rejected: t('proposals.status.rejected'),
  };
  return map[status] ?? status;
}

const loadAll = async () => {
  try {
    const data = await api.get('/api/v1/proposals?status=all');
    s.props = data;
  } catch {
    s.props = [];
  }
};

const addProp = async () => {
  msg.value = '';
  try {
    await api.post('/api/v1/proposals', f.value);
    f.value = { titulo: '', descripcion: '', costo: '', area: '', municipio: '' };
    msg.value = t('proposals.success');
    await loadAll();
  } catch (e: any) {
    msg.value = e.message || 'Error';
  }
};

onMounted(loadAll);
</script>

<style scoped>
.proposals { max-width: 900px; margin: 0 auto; padding: 2rem; }
.proposal-form { padding: 2rem; margin-bottom: 2rem; }
.form-group { margin-bottom: 1rem; }
.form-row { display: flex; flex-wrap: wrap; gap: 1rem; }
.form-row .form-group { flex: 1; min-width: 150px; }
.form-input { width: 100%; padding: 1rem; border: 1px solid var(--panel-border); border-radius: 8px; background: transparent; color: var(--text-main); transition: all 0.2s; }
.form-input:focus { outline: none; border-color: var(--primary); box-shadow: 0 0 0 3px rgba(37,99,235,0.2); }
.submit-btn { width: 100%; margin-top: 1rem; }

.filter-bar { display: flex; flex-wrap: wrap; gap: 0.5rem; margin: 1rem 0 1.5rem; }
.filter-btn { display: inline-flex; align-items: center; gap: 0.4rem; padding: 0.5rem 1rem; border: 1px solid var(--panel-border); border-radius: 999px; background: transparent; color: var(--text-main); cursor: pointer; transition: all 0.2s; font-size: 0.9rem; }
.filter-btn:hover { border-color: var(--primary); }
.filter-btn.active { background: var(--primary); color: #fff; border-color: var(--primary); }
.filter-count { display: inline-flex; align-items: center; justify-content: center; min-width: 1.4rem; padding: 0 0.35rem; height: 1.4rem; border-radius: 999px; background: var(--panel-border); font-size: 0.75rem; font-weight: 700; }
.filter-btn.active .filter-count { background: rgba(255,255,255,0.25); color: #fff; }

.proposal-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 1rem; margin-top: 1rem; }
.proposal-card { padding: 1.5rem; }
.card-header { display: flex; align-items: flex-start; justify-content: space-between; gap: 0.75rem; margin-bottom: 0.5rem; }
.proposal-card h3 { margin: 0; color: var(--primary); font-size: 1.1rem; line-height: 1.3; }
.proposal-card p { color: var(--text-muted); font-size: 0.95rem; margin-bottom: 1rem; line-height: 1.5; }
.badges { display: flex; flex-wrap: wrap; gap: 0.5rem; }
.badge { background: var(--panel-border); padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 0.8rem; color: var(--text-main); }

.status-badge { font-size: 0.75rem; font-weight: 700; text-transform: uppercase; padding: 0.2rem 0.55rem; border-radius: 999px; white-space: nowrap; }
.status-pending { background: #f59e0b; color: #1f2937; }
.status-approved { background: #10b981; color: #fff; }
.status-rejected { background: #ef4444; color: #fff; }

.empty-state { text-align: center; color: var(--text-muted); padding: 2rem; font-size: 0.95rem; }

h1, h2, label { color: var(--text-main); }
h1 { font-size: 1.5rem; font-weight: 800; margin-bottom: 1rem; }

@media (max-width: 768px) {
  .proposals { padding: 1rem; }
  .proposal-form { padding: 1.5rem; }
  .proposal-grid { grid-template-columns: 1fr; }
  .card-header { flex-direction: column; }
}
</style>
