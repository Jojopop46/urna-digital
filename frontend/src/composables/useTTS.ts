import { ref, onMounted, onUnmounted } from 'vue'

const enabled = ref(false)
let focusHandler: ((e: FocusEvent) => void) | null = null
let clickHandler: ((e: MouseEvent) => void) | null = null
let listenersActive = false

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
    return (el.textContent?.trim() || el.getAttribute('title') || 'Botón')
  }
  if (el.tagName === 'A') {
    return (el.textContent?.trim() || el.getAttribute('title') || 'Enlace')
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
    if (text) speak(text)
  }

  clickHandler = (e: MouseEvent) => {
    if (!enabled.value) return
    const target = e.target as HTMLElement
    if (!target) return
    const text = getSpeakableText(target)
    if (text) speak(text)
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

export function speak(text: string) {
  if (!enabled.value || !text) return
  if (!window.speechSynthesis) return

  window.speechSynthesis.cancel()

  const utterance = new SpeechSynthesisUtterance(text)
  utterance.lang = document.documentElement.lang || 'es-MX'
  utterance.rate = 1.0
  utterance.pitch = 1.0

  const voices = window.speechSynthesis.getVoices()
  const esVoice = voices.find(v => v.lang.startsWith('es'))
  if (esVoice) utterance.voice = esVoice

  window.speechSynthesis.speak(utterance)
}

export function toggleTTS() {
  enabled.value = !enabled.value
  localStorage.setItem('urna-tts', enabled.value ? '1' : '0')
  if (!enabled.value) {
    window.speechSynthesis.cancel()
  } else {
    speak('Modo lector de pantalla activado')
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
}

export function useTTS() {
  onMounted(() => {
    initTTS()
  })
  onUnmounted(() => {
    // No destruimos aquí porque queremos que persista entre navegaciones
  })
  return { enabled, speak, toggle: toggleTTS }
}
