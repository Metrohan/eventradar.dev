// Retain session behavior when browser privacy/quota policy denies persistence.
const volatile = new Map()

export const getStored = key => {
  if (volatile.has(key)) return volatile.get(key)
  try { return localStorage.getItem(key) } catch { return null }
}

export const setStored = (key, value) => {
  try {
    localStorage.setItem(key, value)
    volatile.delete(key)
  } catch { volatile.set(key, value) }
}

export const removeStored = key => {
  try {
    localStorage.removeItem(key)
    volatile.delete(key)
  } catch { volatile.set(key, null) }
}

window.addEventListener('storage', event => {
  if (event.key === null) volatile.clear()
  else volatile.delete(event.key)
})
