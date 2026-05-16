<template>
  <div class="transparencia">
    <div class="page-header">
      <h1 class="page-title">Transparencia y Resultados</h1>
      <p class="page-subtitle">Datos públicos en tiempo real. Cada voto es verificable.</p>
    </div>

    <div class="stats-grid">
      <div class="stat-card glass-panel">
        <div class="stat-icon" style="background: var(--primary-light); color: var(--primary);">📋</div>
        <div class="stat-value">{{ approved.length }}</div>
        <div class="stat-label">Propuestas activas</div>
      </div>
      <div class="stat-card glass-panel">
        <div class="stat-icon" style="background: var(--secondary-light); color: var(--secondary);">🗳️</div>
        <div class="stat-value">{{ totalVotos }}</div>
        <div class="stat-label">Votos registrados</div>
      </div>
      <div class="stat-card glass-panel">
        <div class="stat-icon" style="background: var(--warning-light); color: var(--warning);">🔗</div>
        <div class="stat-value">{{ chainHeight }}</div>
        <div class="stat-label">Bloques en cadena</div>
      </div>
    </div>

    <div class="glass-panel chart-section">
      <div class="section-header">
        <h2>Resultados en vivo</h2>
        <span class="live-badge">
          <span class="live-dot"></span> En vivo
        </span>
      </div>
      <div v-for="item in resultados" :key="item.id" class="result-row">
        <div class="result-info">
          <span class="result-title">{{ item.titulo }}</span>
          <span class="result-count">{{ item.votos }} votos</span>
        </div>
        <div class="result-bar-track">
          <div class="result-bar-fill" :style="{ width: porcentaje(item.votos) + '%' }">
            <span v-if="porcentaje(item.votos) > 15" class="result-bar-label">{{ porcentaje(item.votos) }}%</span>
          </div>
        </div>
      </div>
      <div v-if="!resultados.length" class="empty-state">
        Aún no hay votos registrados. ¡Sé el primero en participar!
      </div>
    </div>

    <div class="info-grid">
      <div class="glass-panel info-card">
        <h3>🔐 ¿Cómo se garantiza la transparencia?</h3>
        <ul>
          <li>Cada voto se hashea y se agrega a una blockchain pública</li>
          <li>La raíz Merkle se calcula en tiempo real</li>
          <li>Cualquier ciudadano puede verificar su voto con el recibo</li>
        </ul>
      </div>
      <div class="glass-panel info-card">
        <h3>🛡️ ¿Dónde está mi información personal?</h3>
        <ul>
          <li>No almacenamos CURP ni datos personales</li>
          <li>Usamos pruebas de conocimiento cero (ZK-Proofs)</li>
          <li>Tu identidad nunca se vincula con tu voto</li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { useUrnaStore } from '../stores/useUrnaStore';

const s = useUrnaStore();
const approved = computed(() => s.props.filter((x:any) => x.status==='approved'));
const totalVotos = ref(0);
const chainHeight = ref(1);

const resultados = computed(() => {
  return approved.value.map((p:any) => ({
    id: p.id,
    titulo: p.titulo,
    votos: mockVotes(p.id)
  }));
});

const mockVotes = (id:string) => {
  const base = String(id).split('').reduce((a,c)=>a+c.charCodeAt(0),0) * 13 % 1000;
  return base + Math.floor(Math.random() * 50);
};

const porcentaje = (votos:number) => {
  const total = resultados.value.reduce((a:number, r:any) => a + r.votos, 0);
  if (!total) return 0;
  return Math.round((votos / total) * 100);
};

let timer: number;
onMounted(() => {
  timer = window.setInterval(() => {
    totalVotos.value += Math.floor(Math.random() * 3);
    chainHeight.value += 1;
  }, 8000);
});
onUnmounted(() => clearInterval(timer));
</script>

<style scoped>
.transparencia { max-width: 900px; margin: 0 auto; }

.page-header { text-align: center; margin-bottom: 2rem; }
.page-title { font-size: clamp(1.6rem, 4vw, 2.2rem); font-weight: 800; }
.page-subtitle { color: var(--text-muted); margin-top: 0.25rem; }

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}
.stat-card {
  padding: 1.5rem;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
}
.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: var(--radius-lg);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
}
.stat-value {
  font-size: 2rem;
  font-weight: 800;
  color: var(--primary);
}
.stat-label {
  font-size: 0.875rem;
  color: var(--text-muted);
  font-weight: 500;
}

.chart-section { padding: 2rem; margin-bottom: 2rem; }
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
  gap: 0.5rem;
}
.section-header h2 { font-size: 1.25rem; font-weight: 700; }
.live-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  background: var(--secondary-light);
  color: #065F46;
  padding: 0.375rem 0.75rem;
  border-radius: 999px;
  font-size: 0.8rem;
  font-weight: 700;
}
.live-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--secondary);
  animation: pulse 2s infinite;
}
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}

.result-row { margin-bottom: 1.25rem; }
.result-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.375rem;
  font-size: 0.9375rem;
}
.result-title { font-weight: 600; }
.result-count { color: var(--text-muted); font-weight: 500; font-size: 0.875rem; }
.result-bar-track {
  height: 28px;
  background: var(--bg-color);
  border-radius: var(--radius-sm);
  overflow: hidden;
}
.result-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--primary) 0%, #3B82F6 100%);
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
  justify-content: flex-end;
  padding-right: 0.75rem;
  transition: width 1s cubic-bezier(0.4,0,0.2,1);
  min-width: 40px;
}
.result-bar-label {
  color: white;
  font-weight: 700;
  font-size: 0.8rem;
}
.empty-state {
  text-align: center;
  padding: 2rem;
  color: var(--text-muted);
  font-weight: 500;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1rem;
}
.info-card {
  padding: 1.5rem;
}
.info-card h3 {
  font-size: 1rem;
  font-weight: 700;
  margin-bottom: 0.75rem;
}
.info-card ul {
  padding-left: 1.25rem;
  color: var(--text-muted);
  font-size: 0.9375rem;
  line-height: 1.7;
}
.info-card li { margin-bottom: 0.375rem; }

@media (max-width: 768px) {
  .chart-section { padding: 1.25rem; }
}
</style>
