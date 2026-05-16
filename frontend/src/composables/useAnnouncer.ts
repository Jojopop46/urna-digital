import { ref, onMounted, onUnmounted } from 'vue'

/**
 * Politely announces text to screen readers via an ARIA live region.
 * Creates a hidden live-region element if none exists.
 */
const announcerEl = ref<HTMLDivElement | null>(null)

function ensureAnnouncer() {
  if (announcerEl.value) return
  let el = document.getElementById('a11y-announcer') as HTMLDivElement | null
  if (!el) {
    el = document.createElement('div')
    el.id = 'a11y-announcer'
    el.setAttribute('aria-live', 'polite')
    el.setAttribute('aria-atomic', 'true')
    el.className = 'sr-only'
    document.body.appendChild(el)
  }
  announcerEl.value = el
}

export function announce(text: string, priority: 'polite' | 'assertive' = 'polite') {
  ensureAnnouncer()
  const el = announcerEl.value
  if (!el) return
  el.setAttribute('aria-live', priority)
  // small delay helps screen readers pick up the change
  requestAnimationFrame(() => {
    el.textContent = ''
    requestAnimationFrame(() => {
      el.textContent = text
    })
  })
}

export function assertiveAnnounce(text: string) {
  announce(text, 'assertive')
}

export function useAnnouncer() {
  onMounted(ensureAnnouncer)
  onUnmounted(() => {
    // leave element in DOM for cross-route announcements
  })
  return { announce, assertiveAnnounce }
}
