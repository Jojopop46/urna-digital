import { ref, onMounted, onUnmounted } from 'vue'

/* ─── Estado ─── */
const enabled = ref(false)
const rate = ref(Number(localStorage.getItem('urna-tts-rate') || '1'))
const pitch = ref(Number(localStorage.getItem('urna-tts-pitch') || '1'))
const volume = ref(Number(localStorage.getItem('urna-tts-vol') || '1'))

let focusHandler: ((e: FocusEvent) => void) | null = null
let clickHandler: ((e: MouseEvent) => void) | null = null
let listenersActive = false

/* ─── Cola de anuncios ─── */
const queue: string[] = []
let isSpeaking = false

function processQueue() {
  if (!window.speechSynthesis || queue.length === 0) {
    isSpeaking = false
    return
  }
  isSpeaking = true
  const text = queue.shift()!
  const utterance = new SpeechSynthesisUtterance(text)
  utterance.lang = document.documentElement.lang || 'es-MX'
  utterance.rate = clamp(rate.value, 0.5, 2)
  utterance.pitch = clamp(pitch.value, 0.5, 2)
  utterance.volume = clamp(volume.value, 0, 1)

  const voices = window.speechSynthesis.getVoices()
  const esVoice =
    voices.find((v) => v.lang.startsWith('es-MX')) ||
    voices.find((v) => v.lang.startsWith('es')) ||
    voices.find((v) => v.lang.toLowerCase().includes('spanish')) ||
    null
  if (esVoice) utterance.voice = esVoice

  utterance.onend = () => processQueue()
  utterance.onerror = () => processQueue()
  window.speechSynthesis.speak(utterance)
}

function clamp(n: number, min: number, max: number) {
  return Math.max(min, Math.min(max, n))
}

export function enqueueSpeak(text: string) {
  if (!enabled.value || !text || !window.speechSynthesis) return
  queue.push(text)
  if (!isSpeaking) processQueue()
}

/* retro-compatibilidad */
export function speak(text: string) {
  enqueueSpeak(text)
}

/* ─── Extracción de texto ─── */
function getSpeakableText(el: HTMLElement): string {
  const ariaLabel = el.getAttribute('aria-label')
  if (ariaLabel) return ariaLabel

  const ariaLabelledBy = el.getAttribute('aria-labelledby')
  if (ariaLabelledBy) {
    const labelEl = document.getElementById(ariaLabelledBy)
    if (labelEl) return labelEl.textContent?.trim() || ''
  }

  const role = el.getAttribute('role')
  if (role === 'button' || el.tagName === 'BUTTON') {
    return el.textContent?.trim() || el.getAttribute('title') || 'Botón'
  }
  if (el.tagName === 'A') {
    return el.textContent?.trim() || el.getAttribute('title') || 'Enlace'
  }
  if (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA' || el.tagName === 'SELECT') {
    const label = document.querySelector(`label[for="${el.id}"]`)
    if (label) return label.textContent?.trim() || ''
    const ariaLabel2 = el.getAttribute('aria-label')
    if (ariaLabel2) return ariaLabel2
    const placeholder = (el as HTMLInputElement).placeholder
    if (placeholder) return placeholder
    return 'Campo de texto'
  }

  return el.textContent?.trim() || ''
}

function setupListeners() {
  if (listenersActive) return
  listenersActive = true

  focusHandler = (e: FocusEvent) => {
    if (!enabled.value) return
    const target = e.target as HTMLElement
    if (!target) return
    const text = getSpeakableText(target)
    if (text) enqueueSpeak(text)
  }

  clickHandler = (e: MouseEvent) => {
    if (!enabled.value) return
    const target = e.target as HTMLElement
    if (!target) return
    const text = getSpeakableText(target)
    if (text) enqueueSpeak(text)
  }

  document.addEventListener('focusin', focusHandler)
  document.addEventListener('click', clickHandler)
}

function removeListeners() {
  if (!listenersActive) return
  listenersActive = false
  if (focusHandler) document.removeEventListener('focusin', focusHandler)
  if (clickHandler) document.removeEventListener('click', clickHandler)
  focusHandler = null
  clickHandler = null
}

/* ─── API pública ─── */
export function toggleTTS() {
  enabled.value = !enabled.value
  localStorage.setItem('urna-tts', enabled.value ? '1' : '0')
  if (!enabled.value) {
    window.speechSynthesis?.cancel()
    queue.length = 0
    isSpeaking = false
  } else {
    enqueueSpeak('Modo lector de pantalla activado')
  }
}

export function initTTS() {
  if (localStorage.getItem('urna-tts') === '1') {
    enabled.value = true
  }
  setupListeners()
}

export function destroyTTS() {
  removeListeners()
  window.speechSynthesis?.cancel()
  queue.length = 0
}

export function setTTSConfig(opts: { rate?: number; pitch?: number; volume?: number }) {
  if (opts.rate !== undefined) {
    rate.value = clamp(opts.rate, 0.5, 2)
    localStorage.setItem('urna-tts-rate', String(rate.value))
  }
  if (opts.pitch !== undefined) {
    pitch.value = clamp(opts.pitch, 0.5, 2)
    localStorage.setItem('urna-tts-pitch', String(pitch.value))
  }
  if (opts.volume !== undefined) {
    volume.value = clamp(opts.volume, 0, 1)
    localStorage.setItem('urna-tts-vol', String(volume.value))
  }
}

export function getTTSConfig() {
  return { rate: rate.value, pitch: pitch.value, volume: volume.value }
}

export function useTTS() {
  onMounted(() => {
    initTTS()
  })
  onUnmounted(() => {
    // persistir entre navegaciones
  })
  return { enabled, rate, pitch, volume, speak: enqueueSpeak, toggle: toggleTTS, setConfig: setTTSConfig }
}
