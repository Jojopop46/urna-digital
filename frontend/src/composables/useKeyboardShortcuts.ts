import { onMounted, onUnmounted } from 'vue'

type ShortcutHandler = (e: KeyboardEvent) => void

const handlers: { key: string; ctrl?: boolean; alt?: boolean; shift?: boolean; handler: ShortcutHandler }[] = []

let globalListener: ((e: KeyboardEvent) => void) | null = null

function onKeydown(e: KeyboardEvent) {
  for (const h of handlers) {
    const keyMatch = e.key.toLowerCase() === h.key.toLowerCase()
    const ctrlMatch = !!h.ctrl === e.ctrlKey
    const altMatch = !!h.alt === e.altKey
    const shiftMatch = !!h.shift === e.shiftKey
    if (keyMatch && ctrlMatch && altMatch && shiftMatch) {
      e.preventDefault()
      h.handler(e)
      return
    }
  }
}

export function registerShortcut(
  key: string,
  opts: { ctrl?: boolean; alt?: boolean; shift?: boolean },
  handler: ShortcutHandler
) {
  handlers.push({ key, ...opts, handler })
  if (!globalListener) {
    globalListener = onKeydown
    document.addEventListener('keydown', globalListener)
  }
}

export function unregisterShortcut(key: string, opts?: { ctrl?: boolean; alt?: boolean; shift?: boolean }) {
  const idx = handlers.findIndex(
    (h) =>
      h.key.toLowerCase() === key.toLowerCase() &&
      !!h.ctrl === !!opts?.ctrl &&
      !!h.alt === !!opts?.alt &&
      !!h.shift === !!opts?.shift
  )
  if (idx >= 0) handlers.splice(idx, 1)
  if (handlers.length === 0 && globalListener) {
    document.removeEventListener('keydown', globalListener)
    globalListener = null
  }
}

export function useKeyboardShortcuts(
  shortcuts: { key: string; ctrl?: boolean; alt?: boolean; shift?: boolean; handler: ShortcutHandler }[]
) {
  onMounted(() => {
    for (const s of shortcuts) {
      registerShortcut(s.key, { ctrl: s.ctrl, alt: s.alt, shift: s.shift }, s.handler)
    }
  })
  onUnmounted(() => {
    for (const s of shortcuts) {
      unregisterShortcut(s.key, { ctrl: s.ctrl, alt: s.alt, shift: s.shift })
    }
  })
}
