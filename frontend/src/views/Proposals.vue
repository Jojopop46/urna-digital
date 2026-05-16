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
    </form>
    <h2>{{ $t('proposals.list_title') }}</h2>
    <div class="approved-grid">
      <div v-for="p in approved" :key="p.id" class="glass-panel proposal-card">
        <h3>{{p.titulo}}</h3>
        <p>{{p.descripcion}}</p>
        <div class="badges">
          <span class="badge"><span aria-hidden="true">📍</span> {{p.municipio}}</span>
          <span class="badge"><span aria-hidden="true">💡</span> {{p.area}}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { useI18n } from 'vue-i18n';
import { useUrnaStore } from '../stores/useUrnaStore';
const { t } = useI18n();
const s = useUrnaStore();
const f = ref({titulo:'',descripcion:'',costo:'',area:'',municipio:''});
const approved = computed(() => s.props.filter((x:any) => x.status==='approved'));
const addProp = () => { s.props.push({id:Date.now(), ...f.value, status:'pending'}); f.value={titulo:'',descripcion:'',costo:'',area:'',municipio:''}; alert(t('proposals.success')); };
</script>

<style scoped>
.proposals { max-width: 800px; margin: 0 auto; padding: 2rem; }
.proposal-form { padding: 2rem; margin-bottom: 2rem; }
.form-group { margin-bottom: 1rem; }
.form-row { display: flex; flex-wrap: wrap; gap: 1rem; }
.form-row .form-group { flex: 1; min-width: 150px; }
.form-input { width: 100%; padding: 1rem; border: 1px solid var(--panel-border); border-radius: 8px; background: transparent; color: var(--text-main); transition: all 0.2s; }
.form-input:focus { outline: none; border-color: var(--primary); box-shadow: 0 0 0 3px rgba(37,99,235,0.2); }
.submit-btn { width: 100%; margin-top: 1rem; }
.approved-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 1rem; margin-top: 1rem; }
.proposal-card { padding: 1.5rem; }
.proposal-card h3 { margin-bottom: 0.5rem; color: var(--primary); }
.proposal-card p { color: var(--text-muted); font-size: 0.95rem; margin-bottom: 1rem; }
.badges { display: flex; flex-wrap: wrap; gap: 0.5rem; }
.badge { background: var(--panel-border); padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 0.8rem; color: var(--text-main); }
h1, h2, label { color: var(--text-main); }
h1 { font-size: 1.5rem; font-weight: 800; margin-bottom: 1rem; }

@media (max-width: 768px) {
  .proposals { padding: 1rem; }
  .proposal-form { padding: 1.5rem; }
  .approved-grid { grid-template-columns: 1fr; }
}
</style>
