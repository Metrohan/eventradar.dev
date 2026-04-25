import React from 'react'
import { useQuery } from 'react-query'
import { publicAPI } from '../services/api'
import EventCard from '../components/EventCard'
import AnnouncementModal from '../components/AnnouncementModal'
import LoadingSpinner from '../components/LoadingSpinner'
import ErrorMessage from '../components/ErrorMessage'

const SOURCES = [
  'TechCareer.net', 'Kodluyoruz', 'Youthall',
  'Anbean', 'Coderspace', 'Akbank Gençlik Akademisi', 'Pupilica',
]

const HomePage = () => {
  const [searchTerm, setSearchTerm] = React.useState('')
  const [selectedSource, setSelectedSource] = React.useState('')
  const [selectedLocation, setSelectedLocation] = React.useState('')
  const [showPastEvents, setShowPastEvents] = React.useState(false)

  const { data: eventsData, isLoading, error } = useQuery(
    'events',
    () => publicAPI.getEvents(true)
  )

  const { data: announcementData } = useQuery(
    'latest-announcement',
    () => publicAPI.getLatestAnnouncement(),
    { retry: false }
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
  const totalCount = eventsData?.data?.total_count || 0

  const filteredEvents = allEvents.filter(event => {
    if (!showPastEvents && event.date && new Date(event.date) < now) return false
    if (searchTerm) {
      const s = searchTerm.toLowerCase()
      if (!event.title?.toLowerCase().includes(s) && !event.description?.toLowerCase().includes(s)) return false
    }
    if (selectedSource && event.source !== selectedSource) return false
    if (selectedLocation && event.location !== selectedLocation) return false
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
  }

  const hasFilters = searchTerm || selectedSource || selectedLocation || showPastEvents
  const announcement = announcementData?.data

  return (
    <>
      {/* ── Hero ─────────────────────────────────────────── */}
      <section className="hero-section">
        <div className="hero-glow hero-glow--blue" />
        <div className="hero-glow hero-glow--purple" />
        <div className="hero-grid" />

        <div className="container">
          <div className="hero-content">
            <div className="hero-badge">
              <i className="fas fa-bolt"></i>
              Türkiye'nin Teknoloji Etkinlik Radarı
            </div>

            <h1 className="hero-title">
              Tüm Etkinlikleri<br />
              <span className="gradient-text">Tek Platformda</span> Keşfet
            </h1>

            <p className="hero-subtitle">
              TechCareer, Kodluyoruz, Youthall ve daha fazla platformdan otomatik toplanan
              hackathon, seminer ve atölye etkinlikleri burada.
            </p>

            {/* Quick search */}
            <div className="hero-search">
              <i className="fas fa-search hero-search-icon"></i>
              <input
                type="text"
                className="hero-search-input"
                placeholder="Etkinlik, platform veya konu ara..."
                value={searchTerm}
                onChange={e => setSearchTerm(e.target.value)}
              />
            </div>

            {/* Stats */}
            <div className="hero-stats">
              <div className="hero-stat">
                <span className="hero-stat-number">{totalCount}+</span>
                <span className="hero-stat-label">Aktif Etkinlik</span>
              </div>
              <div className="hero-stat-divider" />
              <div className="hero-stat">
                <span className="hero-stat-number">{SOURCES.length}</span>
                <span className="hero-stat-label">Platform</span>
              </div>
              <div className="hero-stat-divider" />
              <div className="hero-stat">
                <span className="hero-stat-number">Günlük</span>
                <span className="hero-stat-label">Güncelleme</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ── Main content ─────────────────────────────────── */}
      <div className="container py-4">

        {/* Filters */}
        <div className="filters-section mb-4">
          <div className="filter-row">
            {/* Source filter */}
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

            {/* Location filter */}
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

            {/* Past events toggle */}
            <label className={`filter-toggle ${showPastEvents ? 'active' : ''}`}>
              <input
                type="checkbox"
                checked={showPastEvents}
                onChange={e => setShowPastEvents(e.target.checked)}
              />
              <i className="fas fa-history"></i>
              Geçmişleri Göster
            </label>

            {/* Clear */}
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
        </div>

        {/* Section header */}
        <div className="section-header">
          <div className="section-title">
            <span className="section-title-icon">
              <i className="fas fa-calendar-alt"></i>
            </span>
            Etkinlikler
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
            <p>Arama kriterlerinizi değiştirerek tekrar deneyin.</p>
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
          className="text-center mt-5 py-5"
          style={{
            background: 'var(--bg-card)',
            border: '1px solid var(--border-subtle)',
            borderRadius: '20px',
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
          <h5 style={{ fontWeight: 700, marginBottom: '0.5rem' }}>
            Bir etkinlik mi kaçırdık?
          </h5>
          <p className="text-muted" style={{ fontSize: '0.9rem', marginBottom: '1.25rem' }}>
            Eklenmesini istediğiniz bir etkinlik varsa bize bildirin.
          </p>
          <a href="/etkinlik-talep" className="btn-primary">
            Etkinlik Ekle
            <i className="fas fa-arrow-right" style={{ fontSize: '0.8rem' }}></i>
          </a>
        </div>
      </div>

      {announcement && <AnnouncementModal announcement={announcement} />}
    </>
  )
}

export default HomePage
