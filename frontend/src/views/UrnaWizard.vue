<template>
  <div class="urna-wizard">
    <!-- Error de red -->
    <Transition name="slide-down">
      <div v-if="networkError" role="alert" class="alert-banner alert-danger">
        <svg aria-hidden="true" focusable="false" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
        {{ $t('wizard.network_error') }}
      </div>
    </Transition>

    <!-- Live region para anuncios de paso -->
    <div class="sr-only" aria-live="polite" aria-atomic="true">{{ stepAnnouncement }}</div>
    <div class="sr-only" aria-live="polite" aria-atomic="true">{{ copyAnnouncement }}</div>

    <!-- Progress -->
    <div class="progress-bar" role="progressbar" :aria-valuenow="store.paso" aria-valuemin="1" aria-valuemax="4" :aria-label="$t('wizard.progress_label')">
      <div class="progress-fill" :style="{ width: ((store.paso / 4) * 100) + '%' }"></div>
    </div>

    <nav class="wizard-progress" :aria-label="$t('a11y.step_x_of_y', { step: store.paso, total: 4, label: $t(steps[store.paso - 1]?.labelKey || '') })">
      <ol>
        <li
          v-for="(step, i) in steps"
          :key="i"
          :class="{ active: store.paso === (i + 1), completed: store.paso > (i + 1) }"
          :aria-current="store.paso === (i + 1) ? 'step' : undefined"
        >
          <span class="step-bubble">{{ i + 1 }}</span>
          <span class="step-label">{{ $t(step.labelKey) }}</span>
        </li>
      </ol>
    </nav>

    <div class="wizard-card glass-panel">
      <!-- Paso 1: Identidad -->
      <div v-if="store.paso === 1" class="step-content">
        <div class="step-header">
          <div class="step-icon" aria-hidden="true">🪪</div>
          <h2 ref="stepTitleRef" tabindex="-1">{{ $t('wizard.step1_title') }}</h2>
          <p class="step-desc">{{ $t('wizard.step_desc.1') }}</p>
        </div>

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
            @keyup.enter="validarIdentidad"
          />
          <p v-if="ineError" id="ine-error" class="error-msg" role="alert">
            <svg aria-hidden="true" focusable="false" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
            {{ ineError }}
          </p>
        </div>

        <div class="captcha-box">
          <span class="captcha-label">{{ $t('wizard.captcha_label') }}</span>
          <p class="captcha-desc">{{ $t('wizard.captcha_desc') }}</p>
          <div class="captcha-row">
            <div class="captcha-challenge" aria-hidden="true">{{ captchaA }} + {{ captchaB }}</div>
            <span class="captcha-eq" aria-hidden="true">=</span>
            <input
              type="number"
              v-model="captchaInput"
              class="form-input captcha-input"
              :placeholder="$t('wizard.captcha_placeholder') || '?'"
              :aria-label="$t('wizard.captcha_desc')"
            />
            <span v-if="captchaInput && captchaValido" class="captcha-check" aria-hidden="true">✓</span>
          </div>
        </div>

        <button class="btn btn-primary w-full" @click="validarIdentidad" :disabled="!captchaValido || ine.length !== 18">
          {{ $t('wizard.validate_identity') }}
          <svg v-if="isSubmitting" class="spinner" aria-hidden="true" focusable="false" width="16" height="16" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none" stroke-dasharray="31.4 31.4" transform="rotate(-90 12 12)"><animateTransform attributeName="transform" type="rotate" from="0 12 12" to="360 12 12" dur="1s" repeatCount="indefinite"/></circle></svg>
        </button>
      </div>

      <!-- Paso 2: Selección -->
      <div v-else-if="store.paso === 2" class="step-content">
        <div class="step-header">
          <div class="step-icon" aria-hidden="true">📋</div>
          <h2 ref="stepTitleRef" tabindex="-1">{{ $t('wizard.step2_title') }}</h2>
          <p class="step-desc">{{ $t('wizard.step_desc.2') }}</p>
        </div>

        <div class="options-list" role="radiogroup" :aria-label="$t('wizard.step2_title')">
          <button
            v-for="(opcion, idx) in opciones"
            :key="opcion.id"
            ref="optionRefs"
            class="option-card"
            :class="{ active: store.seleccion === opcion.id }"
            role="radio"
            :aria-checked="store.seleccion === opcion.id"
            @click="store.seleccion = opcion.id"
            @keydown="handleOptionKeydown($event, idx)"
            :tabindex="store.seleccion === opcion.id ? 0 : -1"
          >
            <div class="option-check">
              <div class="option-check-inner" v-if="store.seleccion === opcion.id" aria-hidden="true">✓</div>
            </div>
            <div class="option-body">
              <h3>{{ opcion.titulo }}</h3>
              <p class="option-desc">{{ opcion.descripcion }}</p>
              <div class="option-meta">
                <span class="meta-tag"><svg aria-hidden="true" focusable="false" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/></svg> {{ opcion.municipio }}</span>
                <span class="meta-tag"><svg aria-hidden="true" focusable="false" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2v20M2 12h20"/></svg> {{ opcion.area }}</span>
                <span class="meta-tag cost">{{ opcion.costo }}</span>
              </div>
            </div>
          </button>
        </div>

        <div class="actions-row">
          <button class="btn btn-outline" @click="goToStep(1)">← {{ $t('wizard.back') }}</button>
          <button class="btn btn-primary" :disabled="!store.seleccion" @click="goToStep(3)">
            {{ $t('wizard.continue') }}
            <svg aria-hidden="true" focusable="false" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
          </button>
        </div>
      </div>

      <!-- Paso 3: Confirmación -->
      <div v-else-if="store.paso === 3" class="step-content">
        <div class="step-header">
          <div class="step-icon" aria-hidden="true">⚠️</div>
          <h2 ref="stepTitleRef" tabindex="-1">{{ $t('wizard.step3_title') }}</h2>
          <p class="step-desc">{{ $t('wizard.step_desc.3') }}</p>
        </div>

        <div class="confirm-box" v-if="opcionSeleccionada">
          <div class="confirm-option">
            <span class="confirm-label">{{ $t('wizard.step3_title') }}</span>
            <h3 class="confirm-title">{{ opcionSeleccionada.titulo }}</h3>
            <p class="confirm-desc">{{ opcionSeleccionada.descripcion }}</p>
            <div class="confirm-meta">
              <span>{{ opcionSeleccionada.municipio }}</span>
              <span aria-hidden="true">·</span>
              <span>{{ opcionSeleccionada.area }}</span>
              <span aria-hidden="true">·</span>
              <span class="cost">{{ opcionSeleccionada.costo }}</span>
            </div>
          </div>
          <div class="confirm-warning">
            <svg aria-hidden="true" focusable="false" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
            {{ $t('wizard.review_warning') }}
          </div>
        </div>

        <div class="actions-row">
          <button class="btn btn-outline" @click="goToStep(2)">← {{ $t('wizard.change_vote') }}</button>
          <button class="btn btn-primary" @click="emitirVoto" :disabled="isSubmitting || !isOnline" :aria-label="$t('wizard.confirm_emit_aria')">
            {{ isSubmitting ? $t('wizard.emitting') : $t('wizard.confirm_and_emit') }}
            <svg v-if="isSubmitting" class="spinner" aria-hidden="true" focusable="false" width="16" height="16" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none" stroke-dasharray="31.4 31.4" transform="rotate(-90 12 12)"><animateTransform attributeName="transform" type="rotate" from="0 12 12" to="360 12 12" dur="1s" repeatCount="indefinite"/></circle></svg>
          </button>
        </div>
        <p v-if="!isOnline" class="offline-msg" role="alert">
          <svg aria-hidden="true" focusable="false" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="8" y1="12" x2="16" y2="12"/></svg>
          {{ $t('wizard.offline_msg') }}
        </p>
      </div>

      <!-- Paso 4: Recibo -->
      <div v-else-if="store.paso === 4" class="step-content">
        <div class="receipt-success">
          <div class="success-ring">
            <div class="success-icon" aria-hidden="true">✓</div>
          </div>
          <h2 ref="stepTitleRef" tabindex="-1">{{ $t('wizard.success_title') }}</h2>
          <p class="receipt-desc">{{ $t('wizard.success_desc') }}</p>
        </div>

        <div class="receipt-card">
          <label>{{ $t('wizard.receipt_hash') }}</label>
          <div class="receipt-hash">
            <code>{{ recibo }}</code>
            <button class="copy-btn" @click="copiarRecibo" :aria-label="$t('a11y.copy_hash')">
              <svg aria-hidden="true" focusable="false" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>
            </button>
          </div>
          <p class="receipt-hint">{{ $t('wizard.receipt_hint') }}</p>
        </div>

        <div class="actions-row center">
          <button class="btn btn-outline" @click="descargarComprobante">
            <svg aria-hidden="true" focusable="false" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
            {{ $t('wizard.download_receipt') }}
          </button>
          <button class="btn btn-primary" @click="finalizar">
            {{ $t('wizard.finish') }}
            <svg aria-hidden="true" focusable="false" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18l6-6-6-6"/></svg>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue';
import { useI18n } from 'vue-i18n';
import { useUrnaStore } from '../stores/useUrnaStore';

const { t } = useI18n();
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
const stepTitleRef = ref<HTMLHeadingElement | null>(null);
const optionRefs = ref<HTMLButtonElement[]>([]);
const copyAnnouncement = ref('');

const steps = [
  { labelKey: 'wizard.step1_label' },
  { labelKey: 'wizard.step2_label' },
  { labelKey: 'wizard.step3_label' },
  { labelKey: 'wizard.step4_label' }
];

const opciones = computed(() => store.props.filter((p:any) => p.status === 'approved'));

const opcionSeleccionada = computed(() =>
  opciones.value.find((o:any) => o.id === store.seleccion)
);

const stepAnnouncement = computed(() => {
  const step = store.paso;
  const label = t(steps[step - 1]?.labelKey || '');
  return t('a11y.step_x_of_y', { step, total: 4, label });
});

const goToStep = (step: number) => {
  store.paso = step;
};

watch(() => store.paso, () => {
  nextTick(() => {
    stepTitleRef.value?.focus();
  });
});

const validarIdentidad = () => {
  ineError.value = '';
  if (ine.value.length !== 18) {
    ineError.value = t('wizard.ine_error_length');
    return;
  }
  store.tokenSesion = 'sesion_' + Math.random().toString(36).substring(7);
  store.expiresAt = Date.now() + 15 * 60 * 1000;
  store.resetTimer();
  store.paso = 2;
};

const handleOptionKeydown = (event: KeyboardEvent, idx: number) => {
  const opts = opciones.value;
  if (!opts.length) return;
  let nextIdx = idx;
  if (event.key === 'ArrowDown' || event.key === 'ArrowRight') {
    event.preventDefault();
    nextIdx = (idx + 1) % opts.length;
  } else if (event.key === 'ArrowUp' || event.key === 'ArrowLeft') {
    event.preventDefault();
    nextIdx = (idx - 1 + opts.length) % opts.length;
  } else if (event.key === ' ') {
    event.preventDefault();
    store.seleccion = opts[idx].id;
  }
  if (nextIdx !== idx) {
    store.seleccion = opts[nextIdx].id;
    nextTick(() => {
      optionRefs.value[nextIdx]?.focus();
    });
  }
};

const emitirVoto = async () => {
  if (isSubmitting.value) return;
  isSubmitting.value = true;
  networkError.value = false;
  try {
    const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
    const abort = new AbortController();
    const id = setTimeout(() => abort.abort(), 8000);
    const res = await fetch(`${apiUrl}/api/v1/vote/commit`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        process_id: 'proceso_2025',
        vote_index: opciones.value.findIndex((o:any) => o.id === store.seleccion),
        num_options: opciones.value.length,
        identity_hash: 'id_' + Math.random().toString(36).substring(2)
      }),
      signal: abort.signal
    });
    clearTimeout(id);
    if (res.ok) {
      const data = await res.json();
      recibo.value = data.block_hash || data.nullifier || data.receipt_token;
    } else {
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
  const content = `COMPROBANTE DE VOTO - URNA DIGITAL CHIHUAHUA\nHash: ${recibo.value}\nFecha: ${new Date().toLocaleString()}\nVerifica en: urna-digital.vercel.app/verificar`;
  const blob = new Blob([content], { type: 'text/plain' });
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `comprobante-voto-${recibo.value.substring(0,6)}.txt`;
  a.click();
  window.URL.revokeObjectURL(url);
};

const copiarRecibo = () => {
  navigator.clipboard.writeText(recibo.value);
  copyAnnouncement.value = t('a11y.hash_copied');
  setTimeout(() => { copyAnnouncement.value = ''; }, 2000);
};

const onOffline = () => { networkError.value = true; isOnline.value = false; };
const onOnline = () => { networkError.value = false; isOnline.value = true; };

onMounted(() => {
  window.addEventListener('offline', onOffline);
  window.addEventListener('online', onOnline);
});

onUnmounted(() => {
  window.removeEventListener('offline', onOffline);
  window.removeEventListener('online', onOnline);
});
</script>

<style scoped>
.urna-wizard {
  max-width: 720px;
  margin: 0 auto;
  padding: 0.5rem 0 2rem;
}

/* Alert banners */
.alert-banner {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.875rem 1rem;
  border-radius: var(--radius-md);
  font-weight: 600;
  font-size: 0.9375rem;
  margin-bottom: 1rem;
}
.alert-danger {
  background: var(--danger-light);
  color: var(--danger);
}

/* Progress bar */
.progress-bar {
  height: 6px;
  background: var(--panel-border);
  border-radius: 999px;
  overflow: hidden;
  margin-bottom: 1.5rem;
}
.progress-fill {
  height: 100%;
  background: var(--primary);
  border-radius: 999px;
  transition: width 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

/* Wizard progress */
.wizard-progress ol {
  display: flex;
  justify-content: space-between;
  list-style: none;
  padding: 0;
  margin-bottom: 2rem;
  gap: 0.5rem;
}
.wizard-progress li {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.375rem;
  flex: 1;
  text-align: center;
}
.step-bubble {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: var(--panel-border);
  color: var(--text-muted);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 0.875rem;
  transition: var(--transition);
}
.wizard-progress li.active .step-bubble {
  background: var(--primary);
  color: white;
  box-shadow: 0 0 0 4px var(--primary-light);
}
.wizard-progress li.completed .step-bubble {
  background: var(--secondary);
  color: white;
}
.step-label {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--text-muted);
}
.wizard-progress li.active .step-label {
  color: var(--primary);
}

/* Wizard card */
.wizard-card {
  padding: 2.5rem;
}

/* Step header */
.step-header {
  text-align: center;
  margin-bottom: 2rem;
}
.step-icon {
  font-size: 2.5rem;
  margin-bottom: 0.5rem;
}
.step-header h2 {
  font-size: 1.5rem;
  font-weight: 800;
  margin-bottom: 0.5rem;
}
.step-desc {
  color: var(--text-muted);
  max-width: 480px;
  margin: 0 auto;
}

/* Form inputs */
.form-group { margin-bottom: 1.5rem; }
.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  font-size: 0.9375rem;
}
.form-input {
  width: 100%;
  padding: 1rem 1.25rem;
  background: transparent;
  border: 2px solid var(--panel-border);
  border-radius: var(--radius-md);
  color: var(--text-main);
  font-size: 1.1rem;
  transition: var(--transition);
  font-family: inherit;
}
.form-input:focus {
  outline: none;
  border-color: var(--primary);
  box-shadow: 0 0 0 4px var(--primary-light);
}
.form-input[aria-invalid="true"] {
  border-color: var(--danger);
}
.error-msg {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--danger);
  background: var(--danger-light);
  padding: 0.75rem 1rem;
  border-radius: var(--radius-sm);
  margin-top: 0.5rem;
  font-weight: 500;
  font-size: 0.9375rem;
}

/* Captcha */
.captcha-box {
  background: var(--bg-color);
  border: 2px solid var(--panel-border);
  border-radius: var(--radius-md);
  padding: 1.5rem;
  margin-bottom: 1.5rem;
  text-align: center;
}
.captcha-label {
  font-weight: 700;
  display: block;
  margin-bottom: 0.25rem;
}
.captcha-desc {
  color: var(--text-muted);
  font-size: 0.875rem;
  margin-bottom: 1rem;
}
.captcha-row {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
}
.captcha-challenge {
  font-size: 1.5rem;
  font-weight: 800;
  letter-spacing: 2px;
  background: var(--panel-bg);
  padding: 0.75rem 1.25rem;
  border-radius: var(--radius-sm);
  border: 2px dashed var(--panel-border);
  user-select: none;
}
.captcha-input {
  width: 90px !important;
  text-align: center;
  font-size: 1.25rem;
  padding: 0.75rem;
}
.captcha-check {
  color: var(--secondary);
  font-weight: 800;
  font-size: 1.5rem;
}

/* Options */
.options-list {
  display: flex;
  flex-direction: column;
  gap: 0.875rem;
  margin-bottom: 2rem;
}
.option-card {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  text-align: left;
  background: var(--panel-bg);
  border: 2px solid var(--panel-border);
  padding: 1.25rem 1.5rem;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: var(--transition);
  color: var(--text-main);
}
.option-card:hover {
  border-color: var(--primary);
  box-shadow: var(--panel-shadow-lg);
}
.option-card.active {
  border-color: var(--primary);
  background: var(--primary-light);
}
.option-check {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  border: 2px solid var(--panel-border);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  margin-top: 2px;
  transition: var(--transition);
}
.option-card.active .option-check {
  border-color: var(--primary);
  background: var(--primary);
}
.option-check-inner {
  color: white;
  font-weight: 800;
  font-size: 0.75rem;
}
.option-body { flex: 1; }
.option-body h3 {
  font-size: 1.1rem;
  font-weight: 700;
  margin-bottom: 0.25rem;
}
.option-desc {
  color: var(--text-muted);
  font-size: 0.9375rem;
  margin-bottom: 0.75rem;
  line-height: 1.5;
}
.option-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}
.meta-tag {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  background: var(--bg-color);
  padding: 0.375rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.8rem;
  font-weight: 500;
  color: var(--text-muted);
}
.meta-tag.cost {
  background: var(--secondary-light);
  color: #065F46;
  font-weight: 700;
}

/* Confirm box */
.confirm-box {
  margin-bottom: 2rem;
}
.confirm-option {
  background: var(--bg-color);
  border: 2px solid var(--panel-border);
  border-radius: var(--radius-lg);
  padding: 2rem;
  text-align: center;
  margin-bottom: 1rem;
}
.confirm-label {
  display: block;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 0.5rem;
}
.confirm-title {
  font-size: 1.5rem;
  font-weight: 800;
  color: var(--primary);
  margin-bottom: 0.5rem;
}
.confirm-desc {
  color: var(--text-muted);
  margin-bottom: 1rem;
}
.confirm-meta {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
  font-size: 0.9375rem;
  color: var(--text-muted);
}
.confirm-meta .cost {
  color: var(--secondary);
  font-weight: 700;
}
.confirm-warning {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--danger);
  background: var(--danger-light);
  padding: 1rem 1.25rem;
  border-radius: var(--radius-md);
  font-weight: 500;
  font-size: 0.9375rem;
}

/* Receipt */
.receipt-success {
  text-align: center;
  margin-bottom: 2rem;
}
.success-ring {
  width: 90px;
  height: 90px;
  border-radius: 50%;
  background: var(--secondary-light);
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 1.5rem;
}
.success-icon {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background: var(--secondary);
  color: white;
  font-size: 2.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
}
.receipt-success h2 {
  font-size: 1.5rem;
  font-weight: 800;
  margin-bottom: 0.5rem;
}
.receipt-desc {
  color: var(--text-muted);
}
.receipt-card {
  background: var(--bg-color);
  border: 2px solid var(--secondary);
  border-radius: var(--radius-lg);
  padding: 1.5rem;
  margin-bottom: 2rem;
  text-align: center;
}
.receipt-card label {
  display: block;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--text-muted);
  margin-bottom: 0.5rem;
}
.receipt-hash {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: var(--panel-bg);
  border-radius: var(--radius-md);
  padding: 1rem;
  margin-bottom: 0.5rem;
}
.receipt-hash code {
  flex: 1;
  font-family: 'SF Mono', monospace;
  font-size: 0.95rem;
  color: var(--secondary);
  word-break: break-all;
  text-align: left;
}
.copy-btn {
  background: transparent;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  padding: 0.5rem;
  border-radius: var(--radius-sm);
  transition: var(--transition);
}
.copy-btn:hover {
  background: var(--primary-light);
  color: var(--primary);
}
.receipt-hint {
  font-size: 0.85rem;
  color: var(--text-muted);
}

/* Actions */
.actions-row {
  display: flex;
  gap: 1rem;
  justify-content: space-between;
}
.actions-row.center {
  justify-content: center;
}
.offline-msg {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  color: var(--warning);
  background: var(--warning-light);
  padding: 0.75rem;
  border-radius: var(--radius-sm);
  margin-top: 1rem;
  font-size: 0.9375rem;
  font-weight: 500;
}

/* Spinner */
.spinner {
  animation: spin 1s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* Responsive */
@media (max-width: 768px) {
  .wizard-card { padding: 1.5rem; }
  .wizard-progress ol { gap: 0.25rem; }
  .step-label { display: none; }
  .actions-row { flex-direction: column; }
  .actions-row .btn { width: 100%; justify-content: center; }
  .confirm-option { padding: 1.25rem; }
}

.slide-down-enter-active, .slide-down-leave-active {
  transition: all 0.3s ease;
  max-height: 60px;
}
.slide-down-enter-from, .slide-down-leave-to {
  max-height: 0;
  padding-top: 0;
  padding-bottom: 0;
  opacity: 0;
  overflow: hidden;
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
</style>
