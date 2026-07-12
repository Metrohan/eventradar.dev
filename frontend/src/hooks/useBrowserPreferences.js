import React from 'react'

const FAVORITES_KEY = 'eventradar:favorites'
const FILTERS_KEY = 'eventradar:filters'
const FAVORITES_EVENT = 'eventradar:favorites-changed'

const readJSON = (key, fallback) => {
  try {
    return JSON.parse(localStorage.getItem(key)) ?? fallback
  } catch {
    return fallback
  }
}

export const readSavedFilters = () => readJSON(FILTERS_KEY, {})

export const saveFilters = filters => {
  try { localStorage.setItem(FILTERS_KEY, JSON.stringify(filters)) } catch { /* storage unavailable */ }
}

export const useFavorites = () => {
  const [favorites, setFavorites] = React.useState(() => readJSON(FAVORITES_KEY, []))

  React.useEffect(() => {
    const sync = () => setFavorites(readJSON(FAVORITES_KEY, []))
    window.addEventListener(FAVORITES_EVENT, sync)
    window.addEventListener('storage', sync)
    return () => {
      window.removeEventListener(FAVORITES_EVENT, sync)
      window.removeEventListener('storage', sync)
    }
  }, [])

  const toggleFavorite = React.useCallback(eventId => {
    const id = String(eventId)
    const current = readJSON(FAVORITES_KEY, [])
    const next = current.includes(id) ? current.filter(value => value !== id) : [...current, id]
    localStorage.setItem(FAVORITES_KEY, JSON.stringify(next))
    window.dispatchEvent(new Event(FAVORITES_EVENT))
  }, [])

  return {
    favorites,
    isFavorite: eventId => favorites.includes(String(eventId)),
    toggleFavorite,
  }
}
