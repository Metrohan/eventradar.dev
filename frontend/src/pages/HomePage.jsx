import React from 'react'

import { useQuery } from 'react-query'
import { publicAPI } from '../services/api'
import EventCard from '../components/EventCard'
import AnnouncementModal from '../components/AnnouncementModal'
import LoadingSpinner from '../components/LoadingSpinner'
import ErrorMessage from '../components/ErrorMessage'

const HomePage = () => {
  const [searchTerm, setSearchTerm] = React.useState('')
  const [selectedLocation, setSelectedLocation] = React.useState('')
  const [selectedSource, setSelectedSource] = React.useState('')
  const [showPastEvents, setShowPastEvents] = React.useState(false)

  // Fetch events (converted from Flask route /events)
  const {
    data: eventsData,
    isLoading: eventsLoading,
    error: eventsError
  } = useQuery('events', () => publicAPI.getEvents(true))

  // Fetch latest announcement (converted from Flask announcement logic)
  const {
    data: announcementData,
    isLoading: announcementLoading
  } = useQuery('latest-announcement', () => publicAPI.getLatestAnnouncement(), {
    retry: false, // Don't retry if no announcement exists
  })

  // Derive unique locations and sources for filters
  const filterOptions = React.useMemo(() => {
    if (!eventsData?.data?.events) return { locations: [], sources: [] }

    const events = eventsData.data.events
    const locations = [...new Set(events.map(e => e.location).filter(Boolean))].sort()
    const sources = [...new Set(events.map(e => e.source).filter(Boolean))].sort()

    return { locations, sources }
  }, [eventsData])

  if (eventsLoading) {
    return <LoadingSpinner />
  }

  if (eventsError) {
    return <ErrorMessage message="Etkinlikler yüklenirken bir sorun oluştu." />
  }

  const now = new Date();
  const allEvents = eventsData?.data?.events || []

  const filteredEvents = allEvents.filter(event => {
    // 1. Date Filter (Base filter)
    if (!showPastEvents && event.date) {
      if (new Date(event.date) < now) return false
    }

    // 2. Search Term Filter
    if (searchTerm) {
      const searchLower = searchTerm.toLowerCase()
      const titleMatch = event.title?.toLowerCase().includes(searchLower)
      const descMatch = event.description?.toLowerCase().includes(searchLower)
      if (!titleMatch && !descMatch) return false
    }

    // 3. Location Filter
    if (selectedLocation && event.location !== selectedLocation) {
      return false
    }

    // 4. Source Filter
    if (selectedSource && event.source !== selectedSource) {
      return false
    }

    return true
  }).sort((a, b) => {
    // Show upcoming events first if we are not showing past events primarily, 
    // or keep the scraped_at sort?
    // The original code used scraped_at. Let's stick to scraped_at for "Newest Added" feel,
    // OR maybe users want to see "Soonest" events?
    // Original: return new Date(b.scraped_at) - new Date(a.scraped_at);
    // Let's keep original sorting logic for consistency unless requested otherwise.
    return new Date(b.scraped_at) - new Date(a.scraped_at);
  });

  const totalCount = eventsData?.data?.total_count || 0
  const lastUpdated = eventsData?.data?.last_updated || "N/A"
  const announcement = announcementData?.data

  return (
    <>
      <div className="container py-4">
        {/* Header info section (converted from Flask template) */}
        <div className="header-info mb-4">
          <div className="row">
            <div className="col-md-8">
              <h1 className="display-4 fw-bold text-primary mb-3">
                TechEventRadar
              </h1>
              <p className="lead text-muted mb-4">
                En güncel teknoloji kariyer etkinliklerini keşfedin!
                Seminerler, hackathon'lar, atölyeler ve daha fazlası...
              </p>
              <div className="d-flex flex-wrap gap-3 mb-4">
                <div className="badge bg-primary fs-6 px-3 py-2">
                  <i className="fas fa-calendar-alt me-2"></i>
                  {totalCount} Aktif Etkinlik
                </div>
                <div className="badge bg-success fs-6 px-3 py-2">
                  <i className="fas fa-clock me-2"></i>
                  Son Güncelleme: {lastUpdated ? new Date(lastUpdated).toLocaleString('tr-TR') : 'N/A'}
                </div>
              </div>
            </div>
            <div className="col-md-4 text-end">
              <div className="card bg-card border-0 shadow-sm">
                <div className="card-body text-center">
                  <i className="fas fa-rocket fa-3x text-primary mb-3"></i>
                  <h5 className="card-title text-white">Etkinlik Ekleme Talebi</h5>
                  <p className="card-text text-muted">
                    Kaçırdığımız bir etkinlik mi var? Bize bildirin!
                  </p>
                  <a href="/etkinlik-talep" className="btn btn-primary">
                    Talep Gönder
                  </a>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Filters Section */}
        <div className="card bg-card border-0 shadow-sm mb-4">
          <div className="card-body">
            <div className="row g-3">
              <div className="col-md-4">
                <div className="input-group">
                  <span className="input-group-text input-group-text-dark border-end-0">
                    <i className="fas fa-search"></i>
                  </span>
                  <input
                    type="text"
                    className="form-control form-control-dark border-start-0 ps-0"
                    placeholder="Etkinlik ara..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                  />
                </div>
              </div>
              <div className="col-md-3">
                <select
                  className="form-select form-select-dark"
                  value={selectedLocation}
                  onChange={(e) => setSelectedLocation(e.target.value)}
                >
                  <option value="">Tüm Konumlar</option>
                  {filterOptions.locations.map(loc => (
                    <option key={loc} value={loc}>{loc}</option>
                  ))}
                </select>
              </div>
              <div className="col-md-3">
                <select
                  className="form-select form-select-dark"
                  value={selectedSource}
                  onChange={(e) => setSelectedSource(e.target.value)}
                >
                  <option value="">Tüm Kaynaklar</option>
                  {filterOptions.sources.map(src => (
                    <option key={src} value={src}>{src}</option>
                  ))}
                </select>
              </div>
              <div className="col-md-2 d-flex align-items-center">
                <div className="form-check form-switch">
                  <input
                    className="form-check-input"
                    type="checkbox"
                    id="showPastEvents"
                    checked={showPastEvents}
                    onChange={(e) => setShowPastEvents(e.target.checked)}
                  />
                  <label className="form-check-label" htmlFor="showPastEvents">
                    Geçmişleri Göster
                  </label>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Events section (converted from Flask template events display) */}
        <div className="events-section">
          <div className="d-flex justify-content-between align-items-center mb-4">
            <h2 className="h3 mb-0">
              <i className="fas fa-list me-2"></i>
              Etkinlikler
            </h2>
            <span className="text-muted">
              {filteredEvents.length} sonuç bulundu
            </span>
          </div>

          {filteredEvents.length === 0 ? (
            <div className="text-center py-5">
              <i className="fas fa-search fa-4x text-muted mb-3"></i>
              <h4 className="text-muted">Aradığınız kriterlere uygun etkinlik bulunamadı</h4>
              <button
                className="btn btn-outline-primary mt-3"
                onClick={() => {
                  setSearchTerm('')
                  setSelectedLocation('')
                  setSelectedSource('')
                  setShowPastEvents(false)
                }}
              >
                Filtreleri Temizle
              </button>
            </div>
          ) : (
            <div className="row">
              {filteredEvents.map((event) => (
                <div key={event.id} className="col-lg-6 col-xl-4 mb-4">
                  <EventCard event={event} />
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Announcement modal (converted from Flask template modal) */}
        {announcement && !announcementLoading && (
          <AnnouncementModal announcement={announcement} />
        )}
      </div>
    </>
  )
}

export default HomePage


