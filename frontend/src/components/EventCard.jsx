import React from 'react'
import { format } from 'date-fns'
import { tr } from 'date-fns/locale'

const EventCard = ({ event }) => {
  const formatDate = (dateString) => {
    if (!dateString) return 'Tarih belirtilmemiş'
    try {
      return format(new Date(dateString), 'dd MMMM yyyy, HH:mm', { locale: tr })
    } catch {
      return 'Geçersiz tarih'
    }
  }

  const getStatusInfo = (isActive) => {
    return {
      text: isActive ? 'Açık' : 'Kapalı',
      className: isActive ? 'status-acik' : 'status-kapali'
    }
  }

  const status = getStatusInfo(event.is_active)

  return (
    <div className="event-card">
      {/* Event image */}
      <div className="event-image-container">
        <img
          src={event.image_url || '/placeholder-image-colored.jpeg'}
          alt={event.title}
          className="event-image"
          onError={(e) => {
            e.target.src = '/placeholder-image-colored.jpeg'
          }}
        />
      </div>

      {/* Event content */}
      <div className="event-content">
        <h3 className="event-title">{event.title}</h3>
        
        {event.description && (
          <p className="event-description">
            {event.description.length > 150 
              ? `${event.description.substring(0, 150)}...` 
              : event.description
            }
          </p>
        )}

        {/* Event metadata */}
        <div className="event-meta">
          <div className="event-meta-item">
            <i className="fas fa-calendar-alt"></i>
            <span>{formatDate(event.date)}</span>
          </div>
          
          {event.location && (
            <div className="event-meta-item">
              <i className="fas fa-map-marker-alt"></i>
              <span>{event.location}</span>
            </div>
          )}
          
          <div className="event-meta-item">
            <i className="fas fa-tag"></i>
            <span>{event.source}</span>
          </div>
        </div>

        {/* Event status */}
        <div className="d-flex justify-content-between align-items-center mb-3">
          <span className={`event-status ${status.className}`}>
            {status.text}
          </span>
          
          <small className="text-muted">
            <i className="fas fa-clock me-1"></i>
            {formatDate(event.scraped_at)}
          </small>
        </div>

        {/* Action buttons */}
        <div className="d-flex gap-2">
          <a
            href={event.url}
            target="_blank"
            rel="noopener noreferrer"
            className="btn btn-primary btn-sm flex-fill"
          >
            <i className="fas fa-external-link-alt me-1"></i>
            Etkinlik Sayfası
          </a>
        </div>
      </div>
    </div>
  )
}

export default EventCard


