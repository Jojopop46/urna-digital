<template>
  <Teleport to="body">
    <div
      v-if="open"
      class="a11y-overlay"
      @click.self="close"
      role="dialog"
      aria-modal="true"
      aria-labelledby="a11y-title"
      ref="panelRef"
    >
      <div class="a11y-panel glass-panel">
        <div class="a11y-header">
          <h2 id="a11y-title">{{ $t('a11y_panel.title') }}</h2>
          <button
            class="a11y-close"
            @click="close"
            :aria-label="$t('a11y_panel.close')"
            ref="closeBtnRef"
          >
            <svg aria-hidden="true" focusable="false" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
          </button>
        </div>

        <div class="a11y-body">
          <!-- TTS Toggle -->
          <div class="a11y-row">
            <div class="a11y-info">
              <span class="a11y-label">{{ $t('a11y_panel.tts') }}</span>
              <span class="a11y-desc">{{ $t('a11y_panel.tts_desc') }}</span>
            </div>
            <button
              class="a11y-toggle"
              :class="{ active: ttsEnabled }"
              @click="toggleTTS"
              :aria-pressed="ttsEnabled"
            >
              <span class="a11y-toggle-knob"></span>
            </button>
          </div>

          <!-- TTS Rate -->
          <div class="a11y-row" v-if="ttsEnabled">
            <div class="a11y-info">
              <span class="a11y-label">{{ $t('a11y_panel.speed') }}</span>
              <span class="a11y-desc">{{ $t('a11y_panel.speed_desc') }}</span>
            </div>
            <input
              type="range"
              min="0.5"
              max="2"
              step="0.1"
              v-model.number="ttsRate"
              class="a11y-range"
              :aria-label="$t('a11y_panel.speed')"
              @change="onRateChange"
            />
          </div>

          <!-- TTS Pitch -->
          <div class="a11y-row" v-if="ttsEnabled">
            <div class="a11y-info">
              <span class="a11y-label">{{ $t('a11y_panel.pitch') }}</span>
              <span class="a11y-desc">{{ $t('a11y_panel.pitch_desc') }}</span>
            </div>
            <input
              type="range"
              min="0.5"
              max="2"
              step="0.1"
              v-model.number="ttsPitch"
              class="a11y-range"
              :aria-label="$t('a11y_panel.pitch')"
              @change="onPitchChange"
            />
          </div>

          <!-- Font size -->
          <div class="a11y-row">
            <div class="a11y-info">
              <span class="a11y-label">{{ $t('a11y_panel.font') }}</span>
              <span class="a11y-desc">{{ $t('a11y_panel.font_desc') }}</span>
            </div>
            <div class="a11y-seg">
              <button
                v-for="s in fontSizes"
                :key="s.value"
                class="a11y-seg-btn"
                :class="{ active: fontSize === s.value }"
                @click="setFontSize(s.value)"
                :aria-pressed="fontSize === s.value"
              >
                {{ s.label }}
              </button>
            </div>
          </div>

          <!-- High contrast -->
          <div class="a11y-row">
            <div class="a11y-info">
              <span class="a11y-label">{{ $t('a11y_panel.contrast') }}</span>
              <span class="a11y-desc">{{ $t('a11y_panel.contrast_desc') }}</span>
            </div>
            <button
              class="a11y-toggle"
              :class="{ active: highContrast }"
              @click="toggleContrast"
              :aria-pressed="highContrast"
            >
              <span class="a11y-toggle-knob"></span>
            </button>
          </div>

          <!-- Reduced motion -->
          <div class="a11y-row">
            <div class="a11y-info">
              <span class="a11y-label">{{ $t('a11y_panel.motion') }}</span>
              <span class="a11y-desc">{{ $t('a11y_panel.motion_desc') }}</span>
            </div>
            <button
              class="a11y-toggle"
              :class="{ active: reducedMotion }"
              @click="toggleMotion"
              :aria-pressed="reducedMotion"
            >
              <span class="a11y-toggle-knob"></span>
            </button>
          </div>

          <!-- Voice commands -->
          <div class="a11y-row" v-if="voiceSupported">
            <div class="a11y-info">
              <span class="a11y-label">{{ $t('a11y_panel.voice') }}</span>
              <span class="a11y-desc">{{ $t('a11y_panel.voice_desc') }}</span>
            </div>
            <button
              class="a11y-toggle"
              :class="{ active: voiceEnabled }"
              @click="toggleVoice"
              :aria-pressed="voiceEnabled"
            >
              <span class="a11y-toggle-knob"></span>
            </button>
          </div>

          <div class="a11y-help">
            <h3>{{ $t('a11y_panel.shortcuts_title') }}</h3>
            <ul>
              <li><kbd>Alt</kbd> + <kbd>A</kbd> — {{ $t('a11y_panel.shortcut_panel') }}</li>
              <li><kbd>Alt</kbd> + <kbd>V</kbd> — {{ $t('a11y_panel.shortcut_voice') }}</li>
              <li><kbd>Alt</kbd> + <kbd>S</kbd> — {{ $t('a11y_panel.shortcut_tts') }}</li>
              <li><kbd>Tab</kbd> — {{ $t('a11y_panel.shortcut_tab') }}</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick, onMounted, onUnmounted } from 'vue'
import { useTTS, getTTSConfig, setTTSConfig } from '../composables/useTTS'
import { useVoiceCommand, startListening } from '../composables/useVoiceCommand'
import { useKeyboardShortcuts } from '../composables/useKeyboardShortcuts'
import { trapFocus } from '../composables/useFocusTrap'
import { speak } from '../composables/useTTS'

const props = defineProps<{ modelValue: boolean }>()
const emit = defineEmits<{ (e: 'update:modelValue', v: boolean): void }>()

const open = computed({
  get: () => props.modelValue,
  set: (v: boolean) => emit('update:modelValue', v),
})

const { enabled: ttsEnabled, toggle: toggleTTS } = useTTS()
const { isSupported: voiceSupported } = useVoiceCommand()

const panelRef = ref<HTMLElement | null>(null)
const closeBtnRef = ref<HTMLButtonElement | null>(null)

const fontSizes = [
  { value: 'normal', label: 'A' },
  { value: 'large', label: 'A+' },
  { value: 'xlarge', label: 'A++' },
]

const fontSize = ref(localStorage.getItem('urna-font-size') || 'normal')
const highContrast = ref(localStorage.getItem('urna-high-contrast') === '1')
const reducedMotion = ref(localStorage.getItem('urna-reduced-motion') === '1')
const voiceEnabled = ref(localStorage.getItem('urna-voice-enabled') === '1')

const ttsRate = ref(getTTSConfig().rate)
const ttsPitch = ref(getTTSConfig().pitch)

function applyClasses() {
  const html = document.documentElement
  html.classList.remove('font-large', 'font-xlarge', 'high-contrast', 'reduced-motion')
  if (fontSize.value === 'large') html.classList.add('font-large')
  if (fontSize.value === 'xlarge') html.classList.add('font-xlarge')
  if (highContrast.value) html.classList.add('high-contrast')
  if (reducedMotion.value) html.classList.add('reduced-motion')
}

function setFontSize(size: string) {
  fontSize.value = size
  localStorage.setItem('urna-font-size', size)
  applyClasses()
  speak(`Tamaño de texto ${size === 'normal' ? 'normal' : size === 'large' ? 'grande' : 'muy grande'}`)
}

function toggleContrast() {
  highContrast.value = !highContrast.value
  localStorage.setItem('urna-high-contrast', highContrast.value ? '1' : '0')
  applyClasses()
  speak(highContrast.value ? 'Alto contraste activado' : 'Alto contraste desactivado')
}

function toggleMotion() {
  reducedMotion.value = !reducedMotion.value
  localStorage.setItem('urna-reduced-motion', reducedMotion.value ? '1' : '0')
  applyClasses()
  speak(reducedMotion.value ? 'Animaciones reducidas' : 'Animaciones normales')
}

function toggleVoice() {
  voiceEnabled.value = !voiceEnabled.value
  localStorage.setItem('urna-voice-enabled', voiceEnabled.value ? '1' : '0')
  speak(voiceEnabled.value ? 'Comandos de voz activados' : 'Comandos de voz desactivados')
}

function onRateChange() {
  setTTSConfig({ rate: ttsRate.value })
  speak(`Velocidad ${ttsRate.value}`)
}

function onPitchChange() {
  setTTSConfig({ pitch: ttsPitch.value })
  speak(`Tono ${ttsPitch.value}`)
}

function close() {
  open.value = false
}

let cleanupTrap: (() => void) | null = null

watch(open, (val) => {
  if (val) {
    nextTick(() => {
      if (panelRef.value) cleanupTrap = trapFocus(panelRef.value)
      closeBtnRef.value?.focus()
    })
  } else {
    cleanupTrap?.()
    cleanupTrap = null
  }
})

onMounted(() => {
  applyClasses()
})

onUnmounted(() => {
  cleanupTrap?.()
})

/* keyboard shortcuts */
useKeyboardShortcuts([
  { key: 'a', alt: true, handler: () => { open.value = !open.value } },
  { key: 'v', alt: true, handler: () => { if (voiceSupported.value) startListening() } },
  { key: 's', alt: true, handler: () => { toggleTTS() } },
])
</script>

<style scoped>
.a11y-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
}

.a11y-panel {
  width: 100%;
  max-width: 520px;
  max-height: 90vh;
  overflow-y: auto;
  border-radius: var(--radius-lg);
  padding: 1.5rem;
  animation: panelIn 0.2s ease;
}

@keyframes panelIn {
  from { opacity: 0; transform: translateY(12px) scale(0.98); }
  to   { opacity: 1; transform: translateY(0) scale(1); }
}

.a11y-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1.25rem;
}

.a11y-header h2 {
  font-size: 1.25rem;
  font-weight: 800;
}

.a11y-close {
  background: transparent;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  padding: 0.375rem;
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: var(--transition);
}

.a11y-close:hover {
  background: var(--danger-light);
  color: var(--danger);
}

.a11y-body {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.a11y-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  flex-wrap: wrap;
}

.a11y-info {
  display: flex;
  flex-direction: column;
  gap: 0.125rem;
  flex: 1;
}

.a11y-label {
  font-weight: 700;
  font-size: 0.9375rem;
}

.a11y-desc {
  font-size: 0.8125rem;
  color: var(--text-muted);
}

/* Toggle switch */
.a11y-toggle {
  width: 44px;
  height: 24px;
  border-radius: 999px;
  background: var(--panel-border);
  border: none;
  position: relative;
  cursor: pointer;
  padding: 0;
  transition: background 0.2s ease;
  flex-shrink: 0;
}

.a11y-toggle.active {
  background: var(--primary);
}

.a11y-toggle-knob {
  position: absolute;
  top: 2px;
  left: 2px;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: white;
  transition: transform 0.2s ease;
  box-shadow: 0 1px 3px rgba(0,0,0,0.2);
}

.a11y-toggle.active .a11y-toggle-knob {
  transform: translateX(20px);
}

/* Range */
.a11y-range {
  width: 120px;
  accent-color: var(--primary);
}

/* Segmented control */
.a11y-seg {
  display: inline-flex;
  border: 2px solid var(--panel-border);
  border-radius: var(--radius-md);
  overflow: hidden;
  flex-shrink: 0;
}

.a11y-seg-btn {
  background: transparent;
  border: none;
  padding: 0.375rem 0.75rem;
  font-weight: 700;
  cursor: pointer;
  color: var(--text-muted);
  transition: var(--transition);
}

.a11y-seg-btn.active {
  background: var(--primary);
  color: white;
}

.a11y-seg-btn:not(.active):hover {
  background: var(--primary-light);
  color: var(--primary);
}

/* Help section */
.a11y-help {
  margin-top: 0.5rem;
  padding-top: 1rem;
  border-top: 1px solid var(--panel-border);
}

.a11y-help h3 {
  font-size: 0.9375rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
}

.a11y-help ul {
  list-style: none;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
}

.a11y-help li {
  font-size: 0.875rem;
  color: var(--text-muted);
  display: flex;
  align-items: center;
  gap: 0.375rem;
}

.a11y-help kbd {
  background: var(--bg-color);
  border: 1px solid var(--panel-border);
  border-radius: var(--radius-sm);
  padding: 0.125rem 0.375rem;
  font-family: inherit;
  font-size: 0.8rem;
  font-weight: 600;
  box-shadow: 0 1px 0 var(--panel-border);
}

@media (max-width: 480px) {
  .a11y-panel { padding: 1rem; }
  .a11y-row { flex-direction: column; align-items: flex-start; gap: 0.5rem; }
  .a11y-range { width: 100%; }
}
</style>
