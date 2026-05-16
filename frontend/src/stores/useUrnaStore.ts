import { defineStore } from 'pinia'
import { ref, computed, watch } from 'vue'

export const useUrnaStore = defineStore('urna', () => {
  const paso = ref<number>(1)
  const seleccion = ref<string | null>(null)
  const tokenSesion = ref<string | null>(null)
  const expiresAt = ref<number | null>(null)

  const defaultOptions = [{"id":"opt1","titulo":"Parque Lineal Norte","descripcion":"Construcción de parque de 5km","costo":"$15M","area":"Recreación","municipio":"Chihuahua","status":"approved"},{"id":"opt2","titulo":"Renovación Centro","descripcion":"Restauración de fachadas y peatonalización","costo":"$25.5M","area":"Cultura","municipio":"Hidalgo del Parral","status":"approved"},{"id":"opt3","titulo":"Escuelas Dignas","descripcion":"Mantenimiento a 50 escuelas","costo":"$10.2M","area":"Educación","municipio":"Ciudad Juárez","status":"approved"},{"id":"opt4","titulo":"Hospital Regional Sur","descripcion":"Equipamiento y ampliación","costo":"$40M","area":"Salud","municipio":"Delicias","status":"approved"},{"id":"opt5","titulo":"Digitalización Trámites","descripcion":"Plataforma estatal rápida","costo":"$5M","area":"Tecnología","municipio":"Estatal","status":"approved"}]
  let saved = JSON.parse(localStorage.getItem('props') || '[]');
  if(saved.length < 5) { saved = [...defaultOptions, ...saved.filter((x:any)=>!x.id.startsWith('opt'))]; localStorage.setItem('props', JSON.stringify(saved)); }
  const props = ref<any[]>(saved)
  const dl = ref(localStorage.getItem('dl') || '')

  watch(props, v => localStorage.setItem('props', JSON.stringify(v)), {deep:true})
  watch(dl, v => localStorage.setItem('dl', v))

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
    if (tokenSesion.value) timer = window.setTimeout(() => { limpiarSesion(); window.location.href='/' }, 300000)
  }

  return { paso, seleccion, tokenSesion, expiresAt, sesionActiva, limpiarSesion, resetTimer, props, dl }
})
