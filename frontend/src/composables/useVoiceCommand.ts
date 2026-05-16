import { ref, onMounted, onUnmounted } from 'vue'

export type VoiceCommand =
  | { type: 'next' }
  | { type: 'back' }
  | { type: 'select'; index: number }
  | { type: 'confirm' }
  | { type: 'repeat' }
  | { type: 'cancel' }
  | { type: 'read_screen' }
  | { type: 'help' }
  | { type: 'focus_first' }
  | { type: 'stop' }
  | { type: 'unknown'; raw: string }

const SpeechRecognitionAPI =
  (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition

const isSupported = ref(!!SpeechRecognitionAPI)
const isListening = ref(false)
const lastCommand = ref<VoiceCommand | null>(null)
const transcript = ref('')
const error = ref<string | null>(null)

let recognition: any = null
let timeoutId: number | null = null

const NUMBER_WORDS: Record<string, number> = {
  uno: 0, dos: 1, tres: 2, cuatro: 3, cinco: 4,
  seis: 5, siete: 6, ocho: 7, nueve: 8, diez: 9,
  once: 10, doce: 11, trece: 12, catorce: 13, quince: 14,
  primera: 0, segunda: 1, tercera: 2, cuarta: 3, quinta: 4,
  sexta: 5, séptima: 6, octava: 7, novena: 8, décima: 9,
  'número uno': 0, 'número dos': 1, 'número tres': 2, 'número cuatro': 3, 'número cinco': 4,
  'número seis': 5, 'número siete': 6, 'número ocho': 7, 'número nueve': 8, 'número diez': 9,
  'opción uno': 0, 'opción dos': 1, 'opción tres': 2, 'opción cuatro': 3, 'opción cinco': 4,
  'opción seis': 5, 'opción siete': 6, 'opción ocho': 7, 'opción nueve': 8, 'opción diez': 9,
}

function parseCommand(text: string): VoiceCommand {
  const lower = text.toLowerCase().trim()

  if (/\b(siguiente|continuar|adelante|seguir|pasar|avanza|próximo|proximo)\b/.test(lower)) {
    return { type: 'next' }
  }
  if (/\b(atrás|regresar|volver|anterior|retroceder|vuelve|antes)\b/.test(lower)) {
    return { type: 'back' }
  }
  if (/\b(confirmar|votar|emitir|aceptar|sí|si|ok|acepto|enviar|guardar)\b/.test(lower)) {
    return { type: 'confirm' }
  }
  if (/\b(repetir|repite|escuchar de nuevo|instrucciones de nuevo|de nuevo|otra vez)\b/.test(lower)) {
    return { type: 'repeat' }
  }
  if (/\b(cancelar|salir|cerrar|abortar|detener|parar)\b/.test(lower)) {
    return { type: 'cancel' }
  }
  if (/\b(leer pantalla|leer todo|lee todo|describir|qué hay en pantalla|que hay)\b/.test(lower)) {
    return { type: 'read_screen' }
  }
  if (/\b(ayuda|comandos|qué puedo decir|que puedo decir|instrucciones)\b/.test(lower)) {
    return { type: 'help' }
  }
  if (/\b(primer campo|primer elemento|foco inicial|inicio|arriba del todo)\b/.test(lower)) {
    return { type: 'focus_first' }
  }
  if (/\b(silencio|callar|cállate|callate|quieto|stop|shut up)\b/.test(lower)) {
    return { type: 'stop' }
  }

  for (const [word, idx] of Object.entries(NUMBER_WORDS)) {
    if (
      lower.includes('seleccionar ' + word) ||
      lower.includes('opción ' + word) ||
      lower.includes('elegir ' + word) ||
      lower.includes('votar ' + word) ||
      lower.includes(word)
    ) {
      return { type: 'select', index: idx }
    }
  }

  return { type: 'unknown', raw: text }
}

function setupRecognition() {
  if (!SpeechRecognitionAPI) return

  recognition = new SpeechRecognitionAPI()
  recognition.lang = 'es-MX'
  recognition.continuous = false
  recognition.interimResults = false
  recognition.maxAlternatives = 1

  recognition.onstart = () => {
    isListening.value = true
    error.value = null
  }

  recognition.onend = () => {
    isListening.value = false
    if (timeoutId) {
      window.clearTimeout(timeoutId)
      timeoutId = null
    }
  }

  recognition.onresult = (event: any) => {
    const result = event.results[0][0].transcript
    transcript.value = result
    const cmd = parseCommand(result)
    lastCommand.value = cmd
  }

  recognition.onerror = (event: any) => {
    error.value = event.error
    isListening.value = false
  }
}

export function startListening() {
  if (!recognition) setupRecognition()
  if (!recognition) return
  try {
    recognition.start()
    timeoutId = window.setTimeout(() => {
      stopListening()
    }, 10000)
  } catch {
    // already started
  }
}

export function stopListening() {
  if (!recognition) return
  try {
    recognition.stop()
  } catch {
    // already stopped
  }
  if (timeoutId) {
    window.clearTimeout(timeoutId)
    timeoutId = null
  }
}

export function useVoiceCommand() {
  onMounted(() => {
    setupRecognition()
  })
  onUnmounted(() => {
    stopListening()
  })
  return { isSupported, isListening, lastCommand, transcript, error, startListening, stopListening }
}
