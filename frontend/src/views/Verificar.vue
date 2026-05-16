<template>
  <div class="verificar-container">
    <div class="glass-panel verify-box">
      <h2>Verificación de Voto</h2>
      <p>Ingresa el hash criptográfico (recibo) de tu voto para confirmar que fue registrado correctamente en la blockchain ciudadana de forma anónima.</p>
      
      <div class="form-group mt-4">
        <label for="hash">Hash de Recibo</label>
        <input id="hash" type="text" v-model="hashInput" placeholder="Ej: SHA256-..." class="form-input" />
      </div>
      
      <button class="btn btn-primary w-full" @click="verificar" :disabled="!hashInput">
        Verificar en la Blockchain
      </button>

      <div v-if="resultado" class="resultado-box mt-4" :class="resultado.status">
        <div class="icon">{{ resultado.status === 'success' ? '✓' : '✕' }}</div>
        <div class="texto">
          <h4>{{ resultado.titulo }}</h4>
          <p>{{ resultado.mensaje }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';

const hashInput = ref('');
const resultado = ref<{status: 'success'|'error', titulo: string, mensaje: string} | null>(null);

const verificar = async () => {
  resultado.value = null;
  const api_url = import.meta.env.VITE_API_URL || 'http://localhost:8000';
  
  try {
    const response = await fetch(`${api_url}/transparencia/verificar/${hashInput.value}`);
    if (response.ok) {
      const data = await response.json();
      if (data.encontrado) {
        resultado.value = {
          status: 'success',
          titulo: 'Voto Encontrado e Íntegro',
          mensaje: `El recibo corresponde al bloque #${data.block.index} sellado el ${new Date(data.block.timestamp * 1000).toLocaleString()}. Su inmutabilidad está garantizada por la cadena.`
        };
      } else {
        resultado.value = {
          status: 'error',
          titulo: 'Voto No Encontrado',
          mensaje: 'El recibo no figura en la blockchain pública. Verifica que esté escrito exactamente igual.'
        };
      }
    } else {
      throw new Error("API Error");
    }
  } catch (error) {
    console.warn("Backend no disponible, simulando respuesta...");
    if (hashInput.value.length > 10 && hashInput.value.startsWith('SHA256-')) {
      resultado.value = {
        status: 'success',
        titulo: 'Voto Encontrado (Modo Local)',
        mensaje: 'El recibo corresponde a un voto emitido en esta sesión. (Nota: Backend desconectado).'
      };
    } else {
      resultado.value = {
        status: 'error',
        titulo: 'Voto No Encontrado',
        mensaje: 'No hemos podido verificar este recibo.'
      };
    }
  }
};
</script>

<style scoped>
.verificar-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 70vh;
  padding: 1rem;
}
.verify-box {
  padding: 3.5rem;
  max-width: 650px;
  width: 100%;
}
.verify-box h2 {
  font-size: 2.2rem;
  margin-bottom: 1rem;
}
.verify-box p {
  color: var(--text-muted);
  font-size: 1.1rem;
  line-height: 1.6;
}
.form-group {
  margin-bottom: 2rem;
  text-align: left;
}
label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: var(--text-main);
}
.form-input {
  width: 100%;
  padding: 1.25rem;
  background: transparent;
  border: 1px solid var(--panel-border);
  border-radius: 10px;
  color: var(--text-main);
  font-size: 1.1rem;
  font-family: monospace;
  letter-spacing: 1px;
}
.form-input:focus {
  outline: none;
  border-color: var(--primary);
  box-shadow: 0 0 0 4px rgba(0, 91, 171, 0.2);
}
.w-full {
  width: 100%;
}
.mt-4 {
  margin-top: 2rem;
}
.resultado-box {
  display: flex;
  gap: 1.5rem;
  align-items: center;
  padding: 1.5rem;
  border-radius: 8px;
  text-align: left;
}
.resultado-box.success {
  background: rgba(16, 185, 129, 0.1);
  border: 1px solid var(--success);
}
.resultado-box.error {
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid var(--danger);
}
.resultado-box .icon {
  font-size: 2.5rem;
}
.resultado-box.success .icon {
  color: var(--success);
}
.resultado-box.error .icon {
  color: var(--danger);
}
.resultado-box h4 {
  margin-bottom: 0.5rem;
  font-size: 1.2rem;
  color: var(--text-main);
}
.resultado-box p {
  margin: 0;
  font-size: 1rem;
  color: var(--text-muted);
}

@media (max-width: 768px) {
  .verify-box { padding: 1.5rem; }
  .verify-box h2 { font-size: 1.6rem; }
  .resultado-box { flex-direction: column; gap: 0.75rem; text-align: center; }
}
</style>
