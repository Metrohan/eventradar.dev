import React from 'react'
import { useQuery } from 'react-query'
import { publicAPI } from '../services/api'
import EventCard from '../components/EventCard'
import AnnouncementModal from '../components/AnnouncementModal'
import LoadingSpinner from '../components/LoadingSpinner'
import ErrorMessage from '../components/ErrorMessage'

const HomePage = () => {
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

  if (eventsLoading) {
    return <LoadingSpinner />
  }

  if (eventsError) {
    return <ErrorMessage message="Etkinlikler yüklenirken bir sorun oluştu." />
  }

  const events = eventsData?.data?.events || []
  const totalCount = eventsData?.data?.total_count || 0
  const lastUpdated = eventsData?.data?.last_updated || "N/A"
  const announcement = announcementData?.data

  return (
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
            <div className="card border-0 shadow-sm">
              <div className="card-body text-center">
                <i className="fas fa-rocket fa-3x text-primary mb-3"></i>
                <h5 className="card-title">Etkinlik Ekleme Talebi</h5>
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

      {/* Events section (converted from Flask template events display) */}
      <div className="events-section">
        <h2 className="h3 mb-4">
          <i className="fas fa-list me-2"></i>
          Tüm Etkinlikler
        </h2>
        
        {events.length === 0 ? (
          <div className="text-center py-5">
            <i className="fas fa-calendar-times fa-4x text-muted mb-3"></i>
            <h4 className="text-muted">Henüz etkinlik bulunmuyor</h4>
            <p className="text-muted">Yakında yeni etkinlikler eklenecek!</p>
          </div>
        ) : (
          <div className="row">
            {events.map((event) => (
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
  )
}

export default HomePage


