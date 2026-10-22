import { useEffect, useRef } from 'react'

// Open dialogs, topmost last: only the topmost one handles Escape/Tab.
const openDialogs = []

export const useDialogFocus = (open, onClose) => {
  const ref = useRef(null)
  const closeRef = useRef(onClose)
  closeRef.current = onClose

  useEffect(() => {
    if (!open || !ref.current) return undefined
    const dialog = ref.current
    const previous = document.activeElement
    openDialogs.push(dialog)
    const focusable = () => [...dialog.querySelectorAll(
      'button:not([disabled]), a[href], input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])'
    )].filter(element => element.getClientRects().length > 0)
    ;(focusable()[0] || dialog).focus()

    const handleKey = event => {
      if (openDialogs[openDialogs.length - 1] !== dialog) return
      if (event.key === 'Escape') {
        event.preventDefault()
        closeRef.current()
      } else if (event.key === 'Tab') {
        const elements = focusable()
        const first = elements[0] || dialog
        const last = elements[elements.length - 1] || dialog
        if (event.shiftKey && (document.activeElement === first || !dialog.contains(document.activeElement))) {
          event.preventDefault()
          last.focus()
        } else if (!event.shiftKey && (document.activeElement === last || !dialog.contains(document.activeElement))) {
          event.preventDefault()
          first.focus()
        }
      }
    }
    // Document-level so Escape/Tab still work if focus left the dialog (e.g. backdrop click).
    document.addEventListener('keydown', handleKey)
    return () => {
      document.removeEventListener('keydown', handleKey)
      const index = openDialogs.indexOf(dialog)
      const wasTop = index === openDialogs.length - 1
      if (index !== -1) openDialogs.splice(index, 1)
      // A dialog closed beneath another must not steal focus from the one on top.
      if (wasTop && previous?.isConnected) previous.focus()
    }
  }, [open])
  return ref
}
