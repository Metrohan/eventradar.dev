import React from 'react'
import { useQuery } from 'react-query'
import { useSearchParams } from 'react-router-dom'
import { publicAPI } from '../services/api'
import EventCard from './EventCard'
import LoadingSpinner from './LoadingSpinner'
import ErrorMessage from './ErrorMessage'
import TagBadge, { TAG_STYLES } from './TagBadge'
import { readSavedFilters, saveFilters, useFavorites } from '../hooks/useBrowserPreferences'

/**
 * Etkinlik filtreleme + listeleme mantığı. HomePage ve kategori/zaman bazlı
 * SEO landing sayfaları (frontend/src/pages/landing/) bu bileşeni paylaşır;
 * her sayfa sadece hangi filtrenin önceden seçili geleceğini ve (varsa) ek bir
 * tarih bazlı süzgeci (extraFilter) belirler.
 */
const EventListing = ({
  title = 'Etkinlikler',
  intro = null,
  initialTags = [],
  initialLocation = '',
  extraFilter = null,
  emptyStateText = 'Arama kriterlerinizi değiştirerek tekrar deneyin.',
  searchTerm: controlledSearchTerm,
  onSearchTermChange,
}) => {
  const [searchParams, setSearchParams] = useSearchParams()
  const usesPresetFilters = initialTags.length > 0 || Boolean(initialLocation) || Boolean(extraFilter)
  const savedFilters = React.useMemo(
    () => usesPresetFilters ? {} : readSavedFilters(),
    [usesPresetFilters]
  )
  const { favorites } = useFavorites()

  const [internalSearchTerm, setInternalSearchTerm] = React.useState(() => searchParams.get('q') || '')
  const searchTerm = controlledSearchTerm !== undefined ? controlledSearchTerm : internalSearchTerm
  const setSearchTerm = onSearchTermChange || setInternalSearchTerm
  const [selectedSource, setSelectedSource] = React.useState(() => searchParams.get('source') || savedFilters.source || '')
  const [selectedLocation, setSelectedLocation] = React.useState(() => searchParams.get('location') || initialLocation || savedFilters.location || '')
  const [showPastEvents, setShowPastEvents] = React.useState(() => searchParams.get('past') === '1')
  const [selectedTags, setSelectedTags] = React.useState(() => {
    const fromUrl = searchParams.get('tags')
    return fromUrl ? fromUrl.split(',') : (initialTags.length ? initialTags : savedFilters.tags || [])
  })
  const [freeOnly, setFreeOnly] = React.useState(() => searchParams.has('free') ? searchParams.get('free') === '1' : Boolean(savedFilters.freeOnly))
  const [favoritesOnly, setFavoritesOnly] = React.useState(() => searchParams.get('favorites') === '1')
  const [dateFrom, setDateFrom] = React.useState(() => searchParams.get('from') || '')
  const [dateTo, setDateTo] = React.useState(() => searchParams.get('to') || '')

  // Filtreleri URL parametrelerine yansıtır, böylece filtrelenmiş görünüm
  // paylaşılabilir bir link olur (bkz. issue #25 kabul kriteri).
  React.useEffect(() => {
    const params = {}
    if (searchTerm) params.q = searchTerm
    if (selectedSource) params.source = selectedSource
    if (selectedLocation) params.location = selectedLocation
    if (showPastEvents) params.past = '1'
    if (selectedTags.length > 0) params.tags = selectedTags.join(',')
    if (freeOnly) params.free = '1'
    if (favoritesOnly) params.favorites = '1'
    if (dateFrom) params.from = dateFrom
    if (dateTo) params.to = dateTo
    setSearchParams(params, { replace: true })
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchTerm, selectedSource, selectedLocation, showPastEvents, selectedTags, freeOnly, favoritesOnly, dateFrom, dateTo])

  React.useEffect(() => {
    if (usesPresetFilters) return
    saveFilters({ source: selectedSource, location: selectedLocation, tags: selectedTags, freeOnly })
  }, [usesPresetFilters, selectedSource, selectedLocation, selectedTags, freeOnly])

  const { data: eventsData, isLoading, error } = useQuery(
    'events',
    () => publicAPI.getEvents(true)
  )

  const filterOptions = React.useMemo(() => {
    if (!eventsData?.data?.events) return { locations: [], sources: [] }
    const events = eventsData.data.events
    const locations = [...new Set(events.map(e => e.location).filter(Boolean))].sort()
    const sources = [...new Set(events.map(e => e.source).filter(Boolean))].sort()
    return { locations, sources }
  }, [eventsData])

  if (isLoading) return <LoadingSpinner />
  if (error) return <ErrorMessage message="Etkinlikler yüklenirken bir sorun oluştu." />

  const now = new Date()
  const allEvents = eventsData?.data?.events || []

  const filteredEvents = allEvents.filter(event => {
    if (!showPastEvents && event.date && new Date(event.date) < now) return false
    if (searchTerm) {
      const s = searchTerm.toLowerCase()
      if (!event.title?.toLowerCase().includes(s) && !event.description?.toLowerCase().includes(s)) return false
    }
    if (selectedSource && event.source !== selectedSource) return false
    if (selectedLocation && event.location !== selectedLocation) return false
    if (selectedTags.length > 0) {
      const eventTags = event.tags || []
      if (!selectedTags.some(t => eventTags.includes(t))) return false
    }
    if (freeOnly) {
      // Events have no structured price field; this is a best-effort keyword
      // match on title/description, not a reliable "is free" signal. Many
      // genuinely free events won't mention price at all and still won't match.
      const text = `${event.title || ''} ${event.description || ''}`.toLocaleLowerCase('tr-TR')
      const freeKeywords = ['ücretsiz', 'bedava', 'ücret yok', 'ücret alınmamaktadır', 'katılım ücretsiz']
      if (!freeKeywords.some(k => text.includes(k))) return false
    }
    if (favoritesOnly && !favorites.includes(String(event.id))) return false
    if (dateFrom) {
      if (!event.date || new Date(event.date) < new Date(dateFrom)) return false
    }
    if (dateTo) {
      // dateTo günün tamamını kapsasın diye gün sonuna kadar dahil ediyoruz
      const endOfDay = new Date(dateTo)
      endOfDay.setHours(23, 59, 59, 999)
      if (!event.date || new Date(event.date) > endOfDay) return false
    }
    if (extraFilter && !extraFilter(event)) return false
    return true
  }).sort((a, b) => {
    if (!a.date) return 1
    if (!b.date) return -1
    return new Date(a.date) - new Date(b.date)
  })

  const clearFilters = () => {
    setSearchTerm('')
    setSelectedSource('')
    setSelectedLocation('')
    setShowPastEvents(false)
    setSelectedTags([])
    setFreeOnly(false)
    setFavoritesOnly(false)
    setDateFrom('')
    setDateTo('')
  }

  const toggleTag = (name) => {
    setSelectedTags(prev =>
      prev.includes(name) ? prev.filter(t => t !== name) : [...prev, name]
    )
  }

  const hasFilters = searchTerm || selectedSource || selectedLocation || showPastEvents ||
    selectedTags.length > 0 || freeOnly || favoritesOnly || dateFrom || dateTo

  return (
    <div className="container py-4">
      {intro && <div className="mb-4">{intro}</div>}

      {/* Filters */}
      <div className="filters-section mb-4">
        <div className="filter-row">
          <div className="filter-select-wrap">
            <select
              className="filter-select"
              value={selectedSource}
              onChange={e => setSelectedSource(e.target.value)}
              aria-label="Platform seçin"
            >
              <option value="">Tüm Platformlar</option>
              {filterOptions.sources.map(src => (
                <option key={src} value={src}>{src}</option>
              ))}
            </select>
            <i className="fas fa-chevron-down filter-select-arrow"></i>
          </div>

          {filterOptions.locations.length > 0 && (
            <div className="filter-select-wrap">
              <select
                className="filter-select"
                value={selectedLocation}
                onChange={e => setSelectedLocation(e.target.value)}
                aria-label="Konum seçin"
              >
                <option value="">Tüm Konumlar</option>
                {filterOptions.locations.map(loc => (
                  <option key={loc} value={loc}>{loc}</option>
                ))}
              </select>
              <i className="fas fa-chevron-down filter-select-arrow"></i>
            </div>
          )}

          <label className={`filter-toggle ${showPastEvents ? 'active' : ''}`}>
            <input
              type="checkbox"
              checked={showPastEvents}
              onChange={e => setShowPastEvents(e.target.checked)}
            />
            <i className="fas fa-history"></i>
            Geçmişleri Göster
          </label>

          <label className={`filter-toggle ${freeOnly ? 'active' : ''}`}>
            <input
              type="checkbox"
              checked={freeOnly}
              onChange={e => setFreeOnly(e.target.checked)}
            />
            <i className="fas fa-tag"></i>
            Ücretsiz
          </label>

          <label className={`filter-toggle ${favoritesOnly ? 'active' : ''}`}>
            <input
              type="checkbox"
              checked={favoritesOnly}
              onChange={e => setFavoritesOnly(e.target.checked)}
            />
            <i className="fas fa-bookmark"></i>
            Favorilerim
          </label>
          <div className="filter-date-range">
            <input
              type="date"
              className="filter-select filter-date-input"
              value={dateFrom}
              onChange={e => setDateFrom(e.target.value)}
              aria-label="Başlangıç tarihi"
            />
            <span style={{ color: 'var(--text-muted)' }}>–</span>
            <input
              type="date"
              className="filter-select filter-date-input"
              value={dateTo}
              onChange={e => setDateTo(e.target.value)}
              aria-label="Bitiş tarihi"
            />
          </div>

          {hasFilters && (
            <button
              className="filter-toggle"
              onClick={clearFilters}
              style={{ marginLeft: 'auto', color: 'var(--danger)', borderColor: 'rgba(239,68,68,0.3)' }}
            >
              <i className="fas fa-times"></i>
              Temizle
            </button>
          )}
        </div>

        <div className="filter-row" style={{ marginTop: '10px', gap: '8px', flexWrap: 'wrap', alignItems: 'center' }}>
          <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)', fontWeight: 600, letterSpacing: '0.05em', flexShrink: 0 }}>
            KATEGORİ:
          </span>
          {Object.keys(TAG_STYLES).map(name => (
            <TagBadge
              key={name}
              name={name}
              selected={selectedTags.includes(name)}
              clickable
              onClick={() => toggleTag(name)}
            />
          ))}
        </div>
      </div>

      {/* Section header */}
      <div className="section-header">
        <div className="section-title">
          <span className="section-title-icon">
            <i className="fas fa-calendar-alt"></i>
          </span>
          {title}
        </div>
        <span className="results-count">
          {filteredEvents.length} sonuç
        </span>
      </div>

      {/* Events grid */}
      {filteredEvents.length === 0 ? (
        <div className="empty-state">
          <div className="empty-state-icon">
            <i className="fas fa-search"></i>
          </div>
          <h4>Etkinlik bulunamadı</h4>
          <p>{emptyStateText}</p>
          {hasFilters && (
            <button className="btn-outline-primary" onClick={clearFilters}>
              <i className="fas fa-times me-1"></i>
              Filtreleri Temizle
            </button>
          )}
        </div>
      ) : (
        <div className="row g-4">
          {filteredEvents.map(event => (
            <div key={event.id} className="col-lg-6 col-xl-4">
              <EventCard event={event} />
            </div>
          ))}
        </div>
      )}

      {/* Etkinlik ekleme CTA */}
      <div
        className="text-center cta-block"
        style={{
          background: 'var(--bg-card)',
          border: '1px solid var(--border-subtle)',
          borderRadius: '20px',
          marginTop: '3rem',
          padding: '3rem 2rem',
        }}
      >
        <div
          style={{
            width: 56, height: 56,
            borderRadius: '14px',
            background: 'rgba(56,189,248,0.1)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            margin: '0 auto 1rem',
            fontSize: '1.4rem',
            color: 'var(--action-primary)',
          }}
        >
          <i className="fas fa-plus"></i>
        </div>
        <h4 style={{ fontWeight: 700, marginBottom: '0.5rem' }}>
          Bir etkinlik mi kaçırdık?
        </h4>
        <p className="text-muted" style={{ fontSize: '0.9rem', marginBottom: '1.25rem' }}>
          Eklenmesini istediğiniz bir etkinlik varsa bize bildirin.
        </p>
        <a href="/etkinlik-talep" className="btn-primary">
          Etkinlik Ekle
          <i className="fas fa-arrow-right" style={{ fontSize: '0.8rem' }}></i>
        </a>
      </div>
    </div>
  )
}

export default EventListing
