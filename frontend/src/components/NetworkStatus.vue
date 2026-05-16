<template>
  <Transition name="slide-down">
    <div v-if="!isOnline" class="network-banner" role="alert" aria-live="assertive">
      <svg aria-hidden="true" focusable="false" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
      <span>{{ $t('wizard.offline_banner') }}</span>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'

const isOnline = ref(navigator.onLine)
const handleOnline = () => { isOnline.value = true }
const handleOffline = () => { isOnline.value = false }

onMounted(() => {
  window.addEventListener('online', handleOnline)
  window.addEventListener('offline', handleOffline)
})
onUnmounted(() => {
  window.removeEventListener('online', handleOnline)
  window.removeEventListener('offline', handleOffline)
})
</script>

<style scoped>
.network-banner {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  background: var(--warning-light);
  color: var(--warning);
  padding: 0.625rem 1rem;
  text-align: center;
  font-weight: 600;
  font-size: 0.875rem;
}
.slide-down-enter-active, .slide-down-leave-active {
  transition: all 0.3s ease;
  max-height: 50px;
}
.slide-down-enter-from, .slide-down-leave-to {
  max-height: 0;
  padding-top: 0;
  padding-bottom: 0;
  opacity: 0;
  overflow: hidden;
}
</style>
