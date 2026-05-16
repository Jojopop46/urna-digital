<template>
  <div class="transparencia">
    <h1 class="page-title">Transparencia y Resultados en Tiempo Real</h1>
    
    <div class="stats-grid">
      <div class="stat-card glass-panel"><h3>Propuestas Aprobadas</h3><p class="value">{{ approved.length }}</p></div>
      <div class="stat-card glass-panel"><h3>Participación</h3><p class="value">{{ participation.toFixed(1) }}%</p></div>
      <div class="stat-card glass-panel"><h3>Cierre de Votación</h3><p class="value date-value">{{ s.dl ? new Date(s.dl).toLocaleDateString() : 'No definido' }}</p></div>
    </div>
    
    <div class="glass-panel trends-panel">
      <h2>Tendencias de Votación</h2>
      <div v-for="p in approved" :key="p.id" class="trend-row">
        <div class="trend-header">
          <span>{{p.titulo}}</span><span class="vote-count">{{ mockVotes(p.id) }} votos</span>
        </div>
        <div class="bar-track">
          <div class="bar-fill" :style="{width: (mockVotes(p.id)%100)+'%'}"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted, onUnmounted } from 'vue';
import { useUrnaStore } from '../stores/useUrnaStore';
const s = useUrnaStore();
const approved = computed(() => s.props.filter((x:any) => x.status==='approved'));
const mockVotes = (id:string) => String(id).split('').reduce((a,c)=>a+c.charCodeAt(0),0) * 13 % 1000;
const participation = ref(45.2);
let timer: number;
onMounted(() => { timer = window.setInterval(() => participation.value += 0.1, 5000); });
onUnmounted(() => clearInterval(timer));
</script>

<style scoped>
.transparencia { max-width: 900px; margin: 0 auto; padding: 2rem; }
.page-title { margin-bottom: 2rem; font-size: clamp(1.8rem, 4vw, 2.5rem); text-align: center; font-weight:800; }
.stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1.5rem; margin-bottom:2rem; }
.stat-card { text-align:center; padding: 1.5rem; background: var(--panel-bg); border-radius:12px; border: 1px solid var(--panel-border); }
.stat-card h3 { color: var(--text-muted); font-size: .9rem; text-transform: uppercase; margin-bottom:.5rem; letter-spacing: 1px; }
.value { font-size: clamp(2rem, 4vw, 2.5rem); font-weight: 800; color: var(--primary); }
.date-value { font-size: 1.5rem; }
.trends-panel { padding: 2rem; }
.trends-panel h2 { margin-bottom: 1.5rem; }
.trend-row { margin-bottom: 1.5rem; }
.trend-header { display: flex; justify-content: space-between; margin-bottom: .5rem; font-weight: 600; }
.vote-count { color: var(--text-muted); }
.bar-track { height:12px; background:var(--panel-border); border-radius:6px; overflow:hidden; box-shadow: inset 0 2px 4px rgba(0,0,0,0.1); }
.bar-fill { height:100%; background:var(--primary); transition: width 1s cubic-bezier(0.4,0,0.2,1); }

@media (max-width: 768px) {
  .transparencia { padding: 1rem; }
  .trends-panel { padding: 1.5rem; }
  .trend-header { flex-direction: column; gap: 0.25rem; }
}
</style>
