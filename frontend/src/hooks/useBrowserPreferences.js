import React from 'react'

const FAVORITES_KEY = 'eventradar:favorites'
// v2 resets preferences that were accidentally populated by preset SEO pages
// such as /online-etkinlikler.
const FILTERS_KEY = 'eventradar:filters:v2'
const FAVORITES_EVENT = 'eventradar:favorites-changed'

const readJSON = (key, fallback) => {
  try {
    return JSON.parse(localStorage.getItem(key)) ?? fallback
  } catch {
    return fallback
  }
}

const stringArray = value => Array.isArray(value) ? value.filter(item => typeof item === 'string') : []
let volatileFavorites = null
const readFavorites = () => volatileFavorites ?? stringArray(readJSON(FAVORITES_KEY, []))

export const readSavedFilters = () => {
  const value = readJSON(FILTERS_KEY, {})
  const filters = value && typeof value === 'object' && !Array.isArray(value) ? value : {}
  return {
    source: typeof filters.source === 'string' ? filters.source : '',
    location: typeof filters.location === 'string' ? filters.location : '',
    tags: stringArray(filters.tags),
    freeOnly: filters.freeOnly === true,
  }
}

export const saveFilters = filters => {
  try { localStorage.setItem(FILTERS_KEY, JSON.stringify(filters)) } catch { /* storage unavailable */ }
}

export const useFavorites = () => {
  const [favorites, setFavorites] = React.useState(readFavorites)

  React.useEffect(() => {
    const sync = event => {
      if (event.type === 'storage') {
        if (event.key !== null && event.key !== FAVORITES_KEY) return
        volatileFavorites = null
      }
      setFavorites(readFavorites())
    }
    window.addEventListener(FAVORITES_EVENT, sync)
    window.addEventListener('storage', sync)
    return () => {
      window.removeEventListener(FAVORITES_EVENT, sync)
      window.removeEventListener('storage', sync)
    }
  }, [])

  const toggleFavorite = React.useCallback(eventId => {
    const id = String(eventId)
    const current = readFavorites()
    const next = current.includes(id) ? current.filter(value => value !== id) : [...current, id]
    try {
      localStorage.setItem(FAVORITES_KEY, JSON.stringify(next))
      volatileFavorites = null
    } catch {
      // Keep all mounted favorite consumers in sync for this tab even if
      // persistence is denied or full. A reload cannot retain these changes.
      volatileFavorites = next
    }
    window.dispatchEvent(new Event(FAVORITES_EVENT))
  }, [])

  return {
    favorites,
    isFavorite: eventId => favorites.includes(String(eventId)),
    toggleFavorite,
  }
}
