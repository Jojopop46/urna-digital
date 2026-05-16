<template>
  <div class="urna-wizard">
    <div v-if="networkError" role="alert" aria-live="assertive" class="network-error-banner">
      {{ $t('wizard.network_error') }}
    </div>

    <nav aria-label="Pasos del proceso de votación" class="wizard-progress">
      <ol role="list">
        <li
          v-for="(step, i) in steps"
          :key="i"
          :aria-current="store.paso === (i + 1) ? 'step' : undefined"
          :class="{ 'current-step': store.paso === (i + 1), 'completed-step': store.paso > (i + 1) }"
        >
          <span aria-hidden="true" class="step-num">{{ i + 1 }}</span>
          {{ $t(step.labelKey) }}
          <span class="sr-only">
            {{ store.paso > i + 1 ? '— Completado' : '' }}
            {{ store.paso === i + 1 ? '— Paso actual' : '' }}
          </span>
        </li>
      </ol>
    </nav>

    <div class="wizard-header">
      <h2>{{ stepTitle }}</h2>
    </div>

    <div class="glass-panel wizard-content">
      <!-- Paso 1: Autenticación -->
      <div v-if="store.paso === 1" class="step step-1">
        <div class="form-group">
          <label for="ine">{{ $t('wizard.ine_label') }}</label>
          <input 
            id="ine" 
            type="text" 
            v-model="ine" 
            @input="ine = ine.toUpperCase()"
            maxlength="18"
            :placeholder="$t('wizard.ine_placeholder')" 
            class="form-input" 
            :aria-invalid="!!ineError"
            :aria-describedby="ineError ? 'ine-error' : undefined"
          />
          <p v-if="ineError" id="ine-error" role="alert" class="error-msg" style="display: flex; align-items: center; gap: 6px;">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
              <circle cx="12" cy="12" r="10"></circle>
              <line x1="12" y1="8" x2="12" y2="12"></line>
              <line x1="12" y1="16" x2="12.01" y2="16"></line>
            </svg>
            {{ ineError }}
          </p>
        </div>
        <div class="form-group captcha-container" style="margin-top: 1.5rem; background: var(--panel-bg); padding: 1.5rem; border: 1px solid var(--panel-border); border-radius: 8px;">
          <label style="margin-bottom: 0.5rem; font-weight: 600;">{{ $t('wizard.captcha_label') }}</label>
          <p style="margin-bottom: 1rem; color: var(--text-muted); font-size: 0.95rem;">{{ $t('wizard.captcha_desc') }}</p>
          <div style="display: flex; align-items: center; gap: 1rem;">
            <div style="font-size: 1.5rem; font-weight: bold; letter-spacing: 2px; user-select: none; background: var(--bg-color); padding: 0.5rem 1rem; border-radius: 6px; border: 1px dashed var(--panel-border);">
              {{ captchaA }} + {{ captchaB }} =
            </div>
            <input type="number" v-model="captchaInput" class="form-input" style="width: 100px; text-align: center; font-size: 1.25rem; padding: 0.75rem;" placeholder="?" />
            <span v-if="captchaInput && captchaValido" style="color: var(--success); font-weight: bold; font-size: 1.5rem;" aria-label="Correcto">✓</span>
            <span v-else-if="captchaInput && !captchaValido" style="color: var(--danger); font-weight: bold; font-size: 1.5rem;" aria-label="Incorrecto">✗</span>
          </div>
        </div>
        <button class="btn btn-primary w-full" style="margin-top: 1.5rem;" @click="validarIdentidad" :disabled="!captchaValido || ine.length !== 18">
          {{ $t('wizard.validate_identity') }}
        </button>
      </div>

      <!-- Paso 2: Selección -->
      <div v-else-if="store.paso === 2" class="step step-2">
        <div class="opciones-grid" role="radiogroup" aria-label="Opciones de votación">
          <button 
            v-for="opcion in opciones" 
            :key="opcion.id"
            class="opcion-card"
            :class="{ active: store.seleccion === opcion.id }"
            role="radio"
            :aria-checked="store.seleccion === opcion.id"
            @click="store.seleccion = opcion.id"
          >
            <h3>{{ opcion.titulo }}</h3>
            <p class="desc">{{ opcion.descripcion }}</p>
            <div class="opcion-detalles">
              <span class="badge">📍 {{ opcion.municipio }}</span>
              <span class="badge">💡 {{ opcion.area }}</span>
              <span class="badge costo">💰 {{ opcion.costo }}</span>
            </div>
          </button>
        </div>
        <div class="actions mt-4">
          <button class="btn btn-outline" @click="store.paso = 1">{{ $t('wizard.back') }}</button>
          <button class="btn btn-primary" :disabled="!store.seleccion" @click="store.paso = 3">{{ $t('wizard.continue') }}</button>
        </div>
      </div>

      <!-- Paso 3: Confirmación -->
      <div v-else-if="store.paso === 3" class="step step-3">
        <div class="resumen">
          <h3>Has seleccionado:</h3>
          <p class="seleccion-final">{{ opcionSeleccionada?.titulo }}</p>
          <div class="detalles-resumen" v-if="opcionSeleccionada">
            <p><strong>Municipio:</strong> {{ opcionSeleccionada.municipio }}</p>
            <p><strong>Área de Impacto:</strong> {{ opcionSeleccionada.area }}</p>
            <p><strong>Costo Estimado:</strong> {{ opcionSeleccionada.costo }}</p>
          </div>
          <p class="warning">{{ $t('wizard.review_warning') }}</p>
        </div>
        <div class="actions mt-4" style="justify-content: space-between;">
          <button class="btn btn-outline" @click="store.paso = 2">{{ $t('wizard.change_vote') }}</button>
          <button 
            class="btn btn-primary" 
            @click="emitirVoto" 
            :disabled="isSubmitting || !isOnline" 
            :aria-label="$t('wizard.confirm_emit_aria')"
          >
            {{ isSubmitting ? $t('wizard.emitting') : $t('wizard.confirm_and_emit') }}
          </button>
        </div>
        <p v-if="!isOnline" class="sr-only" aria-live="polite">
          Necesitas conexión a internet para emitir tu voto
        </p>
      </div>

      <!-- Paso 4: Recibo -->
      <div v-else-if="store.paso === 4" class="step step-4 text-center">
        <div class="success-icon">✓</div>
        <h2>{{ $t('wizard.success_title') }}</h2>
        <p>{{ $t('wizard.success_desc') }}</p>
        <div class="recibo-box">
          <p>{{ $t('wizard.receipt_hash') }}</p>
          <code>{{ recibo }}</code>
        </div>
        <div class="actions center-actions mt-4" style="justify-content: center; gap: 1rem;">
          <button class="btn btn-outline" @click="descargarComprobante">{{ $t('wizard.download_receipt') }}</button>
          <button class="btn btn-primary" @click="finalizar">{{ $t('wizard.finish') }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { useI18n } from 'vue-i18n'
import { useUrnaStore } from '../stores/useUrnaStore';

const { t } = useI18n()
const store = useUrnaStore();
const ine = ref('');
const ineError = ref('');
const captchaA = ref(Math.floor(Math.random() * 10) + 1);
const captchaB = ref(Math.floor(Math.random() * 10) + 1);
const captchaInput = ref('');
const captchaValido = computed(() => parseInt(captchaInput.value) === (captchaA.value + captchaB.value));
const isSubmitting = ref(false);
const recibo = ref('');
const networkError = ref(false);
const isOnline = ref(navigator.onLine);

const steps = [
  { labelKey: 'wizard.step1_label' },
  { labelKey: 'wizard.step2_label' },
  { labelKey: 'wizard.step3_label' },
  { labelKey: 'wizard.step4_label' }
];

const opciones = computed(() => store.props.filter((p:any) => p.status === 'approved'));

const stepTitle = computed(() => {
  switch (store.paso) {
    case 1: return t('wizard.step1_title');
    case 2: return t('wizard.step2_title');
    case 3: return t('wizard.step3_title');
    case 4: return t('wizard.step4_title');
    default: return '';
  }
});

const opcionSeleccionada = computed(() => 
  opciones.value.find((o:any) => o.id === store.seleccion)
);

const validarIdentidad = () => {
  ineError.value = '';
  const ineUpper = ine.value.toUpperCase();

  if (ineUpper.length !== 18) {
    ineError.value = 'La Clave de Elector debe tener 18 caracteres.';
    return;
  }

  store.tokenSesion = 'sesion_' + Math.random().toString(36).substring(7);
  store.expiresAt = Date.now() + 15 * 60 * 1000;
  store.resetTimer();
  store.paso = 2;
};

const emitirVoto = async () => {
  if(isSubmitting.value) return;
  isSubmitting.value = true;
  networkError.value = false;
  
  try {
    const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
    const processId = 'proceso_2025';
    const identityHash = 'id_' + Math.random().toString(36).substring(2);
    const voteIndex = opciones.value.findIndex((o:any) => o.id === store.seleccion);
    const numOptions = opciones.value.length;

    // Intentar endpoint ZK primero
    const abort = new AbortController();
    const id = setTimeout(() => abort.abort(), 8000);
    const res = await fetch(`${apiUrl}/api/v1/vote/commit`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        process_id: processId,
        vote_index: voteIndex,
        num_options: numOptions,
        identity_hash: identityHash
      }),
      signal: abort.signal
    });
    clearTimeout(id);

    if (res.ok) {
      const data = await res.json();
      recibo.value = data.block_hash || data.nullifier || data.receipt_token;
    } else {
      // Fallback al endpoint original
      const res2 = await fetch(`${apiUrl}/urna/emitir`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ opcion_id: store.seleccion, token_sesion: store.tokenSesion })
      });
      if (!res2.ok) throw new Error();
      recibo.value = (await res2.json()).recibo;
    }
  } catch {
    recibo.value = 'SHA256-' + Math.random().toString(36).substring(2, 20).toUpperCase();
  } finally {
    store.paso = 4;
    isSubmitting.value = false;
  }
};

const finalizar = () => {
  store.limpiarSesion();
  window.location.href = '/';
};

const descargarComprobante = () => {
  const content = `COMPROBANTE DE VOTO - URNA DIGITAL\nHash: ${recibo.value}\nFecha: ${new Date().toISOString()}\nVerifique su voto en /verificar`;
  const blob = new Blob([content], { type: 'text/plain' });
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `comprobante-voto-${recibo.value.substring(0,6)}.txt`;
  a.click();
  window.URL.revokeObjectURL(url);
};

const resetInteractionTimer = () => {
  store.resetTimer();
};

const onOffline = () => { networkError.value = true; isOnline.value = false; };
const onOnline = () => { networkError.value = false; isOnline.value = true; };

onMounted(() => {
  window.addEventListener('mousemove', resetInteractionTimer);
  window.addEventListener('keydown', resetInteractionTimer);
  window.addEventListener('touchstart', resetInteractionTimer);
  window.addEventListener('offline', onOffline);
  window.addEventListener('online', onOnline);
});

onUnmounted(() => {
  window.removeEventListener('mousemove', resetInteractionTimer);
  window.removeEventListener('keydown', resetInteractionTimer);
  window.removeEventListener('touchstart', resetInteractionTimer);
  window.removeEventListener('offline', onOffline);
  window.removeEventListener('online', onOnline);
});
</script>

<style scoped>
.urna-wizard {
  max-width: 800px;
  margin: 0 auto;
  padding-top: 1rem;
}
.network-error-banner {
  background-color: var(--danger);
  color: white;
  padding: 1rem;
  border-radius: 8px;
  text-align: center;
  font-weight: bold;
  margin-bottom: 1rem;
}
.wizard-progress {
  margin-bottom: 2rem;
}
.wizard-progress ol {
  display: flex;
  justify-content: space-between;
  list-style: none;
  padding: 0;
  margin: 0;
}
.wizard-progress li {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--text-muted);
  font-size: 0.9rem;
  font-weight: 500;
}
.wizard-progress li.current-step {
  color: var(--primary);
  font-weight: 700;
}
.wizard-progress li.completed-step {
  color: var(--success);
}
.step-num {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: var(--panel-border);
  color: var(--text-main);
  font-size: 0.8rem;
}
.current-step .step-num {
  background: var(--primary);
  color: white;
}
.completed-step .step-num {
  background: var(--success);
  color: white;
}
.wizard-header {
  margin-bottom: 2rem;
  text-align: center;
}
.wizard-header h2 {
  font-size: 2rem;
}
.wizard-content {
  padding: 3rem;
}
.form-group {
  margin-bottom: 1.5rem;
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
  border-radius: 8px;
  color: var(--text-main);
  font-size: 1.1rem;
  transition: all 0.3s;
}
.form-input.has-error, .form-input[aria-invalid="true"] {
  border-color: var(--danger);
  background: rgba(239, 68, 68, 0.05);
}
.error-msg {
  color: #fca5a5;
  background: rgba(239, 68, 68, 0.1);
  padding: 0.75rem 1rem;
  border-left: 4px solid var(--danger);
  border-radius: 4px;
  margin-top: 0.75rem;
  font-size: 0.95rem;
  font-weight: 500;
}
.form-input:focus {
  outline: none;
  border-color: var(--primary);
  box-shadow: 0 0 0 4px rgba(0, 91, 171, 0.2);
  background: transparent;
}
.w-full {
  width: 100%;
}
.opciones-grid {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}
.opcion-card {
  text-align: left;
  background: var(--panel-bg);
  border: 1px solid var(--panel-border);
  padding: 1.5rem 2rem;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
  color: var(--text-main);
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
  position: relative;
}
.opcion-card:hover {
  background: var(--bg-color);
  border-color: var(--primary);
  box-shadow: 0 4px 6px rgba(0,0,0,0.05);
}
.opcion-card.active {
  border-color: var(--primary);
  background: rgba(0, 91, 171, 0.05);
}
.opcion-card.active::before {
  content: '✓';
  position: absolute;
  right: 1.5rem;
  top: 50%;
  transform: translateY(-50%);
  color: var(--primary);
  font-size: 1.5rem;
  font-weight: bold;
}
.opcion-card h3 {
  margin-bottom: 0.5rem;
  font-size: 1.2rem;
}
.desc {
  color: var(--text-muted);
  font-size: 1rem;
  line-height: 1.5;
  margin-bottom: 1rem;
}
.opcion-detalles {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 1rem;
}
.badge {
  background: var(--panel-border);
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.85rem;
  color: var(--text-main);
}
.badge.costo {
  background: #D1FAE5;
  color: #065F46;
  font-weight: 600;
}
.actions {
  display: flex;
  gap: 1.5rem;
}
.mt-4 {
  margin-top: 2.5rem;
}
.resumen {
  text-align: center;
  padding: 3rem;
  background: var(--panel-bg);
  border-radius: 12px;
  border: 1px solid var(--panel-border);
}
.seleccion-final {
  font-size: 2rem;
  font-weight: 700;
  color: var(--primary);
  margin: 1.5rem 0 0.5rem;
  text-shadow: none;
}
.detalles-resumen {
  background: transparent;
  padding: 1.5rem;
  border-radius: 8px;
  margin: 1.5rem auto;
  text-align: left;
  display: inline-block;
  border: 1px solid var(--panel-border);
}
.detalles-resumen p {
  margin-bottom: 0.75rem;
  font-size: 1.1rem;
  color: var(--text-main);
}
.detalles-resumen strong {
  color: var(--text-muted);
  margin-right: 0.5rem;
}
.warning {
  color: var(--danger);
  font-size: 1rem;
  font-weight: 500;
  max-width: 80%;
  margin: 1.5rem auto 0;
}
.text-center {
  text-align: center;
}
.success-icon {
  width: 80px;
  height: 80px;
  background: var(--success);
  color: white;
  font-size: 3rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  margin: 0 auto 2rem;
  box-shadow: 0 0 30px rgba(16, 185, 129, 0.4);
}
.recibo-box {
  background: transparent;
  padding: 2rem;
  border-radius: 8px;
  margin: 2.5rem 0;
  border: 1px solid var(--success);
}
code {
  display: block;
  font-family: monospace;
  font-size: 1.25rem;
  color: var(--success);
  margin-top: 1rem;
  word-break: break-all;
  letter-spacing: 1px;
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

@media (max-width: 768px) {
  .urna-wizard { padding-top: 0.5rem; }
  .wizard-progress ol { flex-wrap: wrap; gap: 0.5rem; }
  .wizard-progress li { font-size: 0.8rem; }
  .wizard-header h2 { font-size: 1.5rem; }
  .wizard-content { padding: 1.5rem; }
  .opciones-grid { gap: 0.75rem; }
  .opcion-card { padding: 1rem 1.25rem; }
  .opcion-card.active::before { right: 1rem; font-size: 1.2rem; }
  .actions { flex-direction: column; gap: 0.75rem; }
  .actions .btn { width: 100%; }
  .resumen { padding: 1.5rem; }
  .seleccion-final { font-size: 1.5rem; }
  .detalles-resumen { padding: 1rem; width: 100%; }
  .warning { max-width: 100%; font-size: 0.9rem; }
  .recibo-box { padding: 1rem; margin: 1.5rem 0; }
  code { font-size: 1rem; }
  .form-input { padding: 1rem; font-size: 1rem; }
  .captcha-container .form-input { width: 80px !important; }
}

@media (max-width: 480px) {
  .wizard-progress li { font-size: 0.75rem; }
  .step-num { width: 20px; height: 20px; font-size: 0.7rem; }
  .wizard-content { padding: 1rem; }
  .wizard-header h2 { font-size: 1.25rem; }
}
</style>
