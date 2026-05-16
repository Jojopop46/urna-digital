import { onMounted, onUnmounted } from 'vue'

const FOCUSABLE =
  'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'

export function trapFocus(container: HTMLElement) {
  const focusable = Array.from(container.querySelectorAll<HTMLElement>(FOCUSABLE)).filter(
    (el) => !el.hasAttribute('disabled') && !el.getAttribute('aria-hidden')
  )
  const first = focusable[0]
  const last = focusable[focusable.length - 1]

  const handler = (e: KeyboardEvent) => {
    if (e.key !== 'Tab') return
    if (focusable.length === 0) {
      e.preventDefault()
      return
    }
    if (e.shiftKey) {
      if (document.activeElement === first) {
        e.preventDefault()
        last?.focus()
      }
    } else {
      if (document.activeElement === last) {
        e.preventDefault()
        first?.focus()
      }
    }
  }

  container.addEventListener('keydown', handler)
  first?.focus()

  return () => container.removeEventListener('keydown', handler)
}

export function useFocusTrap(containerRef: { value: HTMLElement | null }) {
  let cleanup: (() => void) | null = null

  onMounted(() => {
    if (containerRef.value) {
      cleanup = trapFocus(containerRef.value)
    }
  })

  onUnmounted(() => {
    cleanup?.()
  })
}
