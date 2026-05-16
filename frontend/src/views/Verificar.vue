<template>
  <div class="verificar-container">
    <div class="glass-panel verify-card">
      <div class="verify-header">
        <div class="verify-icon" aria-hidden="true">🔍</div>
        <h1>{{ $t('verify.title') }}</h1>
        <p>{{ $t('verify.subtitle') }}</p>
      </div>

      <div class="form-group">
        <label for="hash">{{ $t('verify.form.label') }}</label>
        <div class="input-wrap">
          <input
            id="hash"
            type="text"
            v-model="hashInput"
            :placeholder="$t('verify.form.placeholder')"
            class="form-input"
            @keyup.enter="verificar"
          />
          <button v-if="hashInput" class="clear-btn" @click="hashInput = ''" :aria-label="$t('a11y.clear') || 'Borrar'">✕</button>
        </div>
      </div>

      <button class="btn btn-primary w-full" @click="verificar" :disabled="!hashInput || loading">
        <svg v-if="loading" class="spinner" aria-hidden="true" focusable="false" width="16" height="16" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none" stroke-dasharray="31.4 31.4" transform="rotate(-90 12 12)"><animateTransform attributeName="transform" type="rotate" from="0 12 12" to="360 12 12" dur="1s" repeatCount="indefinite"/></circle></svg>
        <span v-else><span aria-hidden="true">🔎</span> {{ $t('verify.button') }}</span>
      </button>

      <div aria-live="polite" aria-atomic="true">
        <!-- Resultado éxito -->
        <div v-if="resultado?.status === 'success'" class="result-box result-success">
          <div class="result-icon" aria-hidden="true">✓</div>
          <div class="result-body">
            <h2>{{ resultado.titulo }}</h2>
            <p>{{ resultado.mensaje }}</p>
          </div>
        </div>

        <!-- Resultado error -->
        <div v-if="resultado?.status === 'error'" class="result-box result-error">
          <div class="result-icon" aria-hidden="true">✕</div>
          <div class="result-body">
            <h2>{{ resultado.titulo }}</h2>
            <p>{{ resultado.mensaje }}</p>
          </div>
        </div>
      </div>
    </div>

    <div class="glass-panel tips-card">
      <h3><span aria-hidden="true">💡</span> {{ $t('verify.tips.title') }}</h3>
      <ul>
        <li v-for="(item, i) in $tm('verify.tips.items')" :key="i">{{ item }}</li>
      </ul>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useI18n } from 'vue-i18n';
import { api } from '../services/api';

const { t } = useI18n();

const hashInput = ref('');
const loading = ref(false);
const resultado = ref<{status: 'success'|'error', titulo: string, mensaje: string} | null>(null);

const verificar = async () => {
  loading.value = true;
  resultado.value = null;

  try {
    const data = await api.get(`/transparencia/verificar/${hashInput.value}`);
    if (data.encontrado) {
      resultado.value = {
        status: 'success',
        titulo: t('verify.result.success.title'),
        mensaje: t('verify.result.success.desc', { block: data.block.index })
      };
    } else {
      resultado.value = {
        status: 'error',
        titulo: t('verify.result.error.title'),
        mensaje: t('verify.result.error.desc')
      };
    }
  } catch (e: any) {
    resultado.value = {
      status: 'error',
      titulo: t('verify.result.server_error.title'),
      mensaje: e.message || t('verify.result.server_error.desc')
    };
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.verificar-container {
  max-width: 600px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}
.verify-card {
  padding: 2.5rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}
.verify-header {
  text-align: center;
}
.verify-icon {
  font-size: 2.5rem;
  margin-bottom: 0.5rem;
}
.verify-header h1 {
  font-size: 1.5rem;
  font-weight: 800;
  margin-bottom: 0.5rem;
}
.verify-header p {
  color: var(--text-muted);
  font-size: 0.9375rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  font-size: 0.9375rem;
}
.input-wrap {
  position: relative;
}
.form-input {
  width: 100%;
  padding: 1rem 2.5rem 1rem 1.25rem;
  background: transparent;
  border: 2px solid var(--panel-border);
  border-radius: var(--radius-md);
  color: var(--text-main);
  font-size: 1rem;
  font-family: 'SF Mono', monospace;
  transition: var(--transition);
}
.form-input:focus {
  outline: none;
  border-color: var(--primary);
  box-shadow: 0 0 0 4px var(--primary-light);
}
.clear-btn {
  position: absolute;
  right: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  background: transparent;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  padding: 0.25rem;
  font-size: 0.875rem;
}

.result-box {
  display: flex;
  gap: 1rem;
  align-items: flex-start;
  padding: 1.25rem;
  border-radius: var(--radius-md);
  text-align: left;
  animation: slideUp 0.3s ease;
}
@keyframes slideUp {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
.result-success {
  background: var(--secondary-light);
  border: 1px solid var(--secondary);
}
.result-error {
  background: var(--danger-light);
  border: 1px solid var(--danger);
}
.result-icon {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  flex-shrink: 0;
}
.result-success .result-icon {
  background: var(--secondary);
  color: white;
}
.result-error .result-icon {
  background: var(--danger);
  color: white;
}
.result-body h2 {
  font-size: 1rem;
  font-weight: 700;
  margin-bottom: 0.25rem;
}
.result-body p {
  font-size: 0.9375rem;
  margin: 0;
  color: var(--text-muted);
}

.tips-card {
  padding: 1.5rem;
}
.tips-card h3 {
  font-size: 1rem;
  font-weight: 700;
  margin-bottom: 0.75rem;
}
.tips-card ul {
  padding-left: 1.25rem;
  color: var(--text-muted);
  font-size: 0.9375rem;
  line-height: 1.7;
}
.tips-card li { margin-bottom: 0.5rem; }

.spinner {
  animation: spin 1s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

@media (max-width: 768px) {
  .verify-card { padding: 1.5rem; }
}
</style>
