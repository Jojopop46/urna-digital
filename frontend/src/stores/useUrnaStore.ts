import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export interface Proposal {
  id: number
  titulo: string
  descripcion: string
  costo: string
  area: string
  municipio: string
  status: string
  votos?: number
}

export const useUrnaStore = defineStore('urna', () => {
  const paso = ref<number>(1)
  const seleccion = ref<number | null>(null)
  const tokenSesion = ref<string | null>(null)
  const expiresAt = ref<number | null>(null)
  const props = ref<Proposal[]>([])
  const dl = ref('')

  const sesionActiva = computed(() => tokenSesion.value !== null && Date.now() < (expiresAt.value ?? 0))

  function limpiarSesion() {
    paso.value = 1
    seleccion.value = null
    tokenSesion.value = null
    expiresAt.value = null
  }

  let timer: number | undefined
  function resetTimer() {
    if (typeof window === 'undefined') return
    clearTimeout(timer)
    if (tokenSesion.value) {
      timer = window.setTimeout(() => {
        limpiarSesion()
        window.location.href = '/'
      }, 300000)
    }
  }

  return { paso, seleccion, tokenSesion, expiresAt, sesionActiva, limpiarSesion, resetTimer, props, dl }
})
