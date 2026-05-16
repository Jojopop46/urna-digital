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
  const props = ref<Proposal[]>([
    { id: 1, titulo: 'Mejoramiento de alumbrado público en zonas rurales', descripcion: 'Instalación de luminarias LED solares en caminos rurales de difícil acceso para mejorar la seguridad nocturna y reducir accidentes.', costo: '$2,400,000 MXN', area: 'Infraestructura', municipio: 'Chihuahua', status: 'approved' },
    { id: 2, titulo: 'Centro de salud digital para comunidades indígenas', descripcion: 'Telemedicina y consulta médica remota en comunidades rarámuri y tepehuana con conectividad satelital y personal capacitado.', costo: '$1,800,000 MXN', area: 'Salud', municipio: 'Guachochi', status: 'approved' },
    { id: 3, titulo: 'Recolección de agua pluvial en escuelas primarias', descripcion: 'Sistemas de captación de agua de lluvia en 15 escuelas primarias rurales para garantizar abasto durante temporada de sequía.', costo: '$950,000 MXN', area: 'Educación', municipio: 'Cuauhtémoc', status: 'approved' },
  ])
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
