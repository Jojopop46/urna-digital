<template>
  <div class="proposals">
    <h2>Propuestas Ciudadanas</h2>
    <form @submit.prevent="addProp" class="glass-panel proposal-form">
      <div class="form-group">
        <label>Título</label><input v-model="f.titulo" required class="form-input">
      </div>
      <div class="form-group">
        <label>Descripción</label><textarea v-model="f.descripcion" required class="form-input"></textarea>
      </div>
      <div class="form-row">
        <div class="form-group"><label>Costo Estimado</label><input v-model="f.costo" class="form-input"></div>
        <div class="form-group"><label>Área</label><input v-model="f.area" class="form-input"></div>
        <div class="form-group"><label>Municipio</label><input v-model="f.municipio" class="form-input"></div>
      </div>
      <button class="btn btn-primary submit-btn" type="submit">Enviar Propuesta</button>
    </form>
    <h3>Propuestas Aprobadas</h3>
    <div class="approved-grid">
      <div v-for="p in approved" :key="p.id" class="glass-panel proposal-card">
        <h4>{{p.titulo}}</h4>
        <p>{{p.descripcion}}</p>
        <div class="badges">
          <span class="badge">📍 {{p.municipio}}</span>
          <span class="badge">💡 {{p.area}}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { useUrnaStore } from '../stores/useUrnaStore';
const s = useUrnaStore();
const f = ref({titulo:'',descripcion:'',costo:'',area:'',municipio:''});
const approved = computed(() => s.props.filter((x:any) => x.status==='approved'));
const addProp = () => { s.props.push({id:Date.now(), ...f.value, status:'pending'}); f.value={titulo:'',descripcion:'',costo:'',area:'',municipio:''}; alert('Enviada!'); };
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
.proposal-card h4 { margin-bottom: 0.5rem; color: var(--primary); }
.proposal-card p { color: var(--text-muted); font-size: 0.95rem; margin-bottom: 1rem; }
.badges { display: flex; flex-wrap: wrap; gap: 0.5rem; }
.badge { background: var(--panel-border); padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 0.8rem; color: var(--text-main); }
h2, h3, label { color: var(--text-main); }

@media (max-width: 768px) {
  .proposals { padding: 1rem; }
  .proposal-form { padding: 1.5rem; }
  .approved-grid { grid-template-columns: 1fr; }
}
</style>
