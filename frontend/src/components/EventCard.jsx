import React from 'react'
import { Link } from 'react-router-dom'
import { format } from 'date-fns'
import { useTranslation } from 'react-i18next'
import TagBadge from './TagBadge'
import ShareButtons from './ShareButtons'
import { getSourceStyle } from '../utils/sourceColor'
import { useFavorites } from '../hooks/useBrowserPreferences'
import { useDateLocale } from '../hooks/useDateLocale'

const EventCard = ({ event }) => {
  const { t } = useTranslation()
  const dateLocale = useDateLocale()
  const { isFavorite, toggleFavorite } = useFavorites()
  const safeUrl = /^https?:\/\//i.test(event.url) ? event.url : '#'
  const canonicalUrl = `https://eventradar.dev/etkinlik/${event.id}`

  const formatDate = (dateString) => {
    if (!dateString) return t('eventCard.noDate')
    try {
      return format(new Date(dateString), 'dd MMM yyyy · HH:mm', { locale: dateLocale })
    } catch {
      return t('eventCard.noDate')
    }
  }

  const formatDeadline = (dateString) => {
    if (!dateString) return null
    try {
      const deadline = new Date(dateString)
      const daysLeft = Math.ceil((deadline - new Date()) / (1000 * 60 * 60 * 24))
      const formatted = format(deadline, 'dd MMM yyyy', { locale: dateLocale })
      if (daysLeft < 0) return null
      if (daysLeft === 0) return t('eventCard.deadlineToday')
      if (daysLeft <= 3) return t('eventCard.deadlineDaysLeft', { count: daysLeft })
      return t('eventCard.deadlinePrefix', { date: formatted })
    } catch {
      return null
    }
  }

  const sourceStyle = getSourceStyle(event.source)
  const isActive = event.is_active
  const deadlineText = formatDeadline(event.application_deadline)
  const deadlineSoon =
    event.application_deadline &&
    Math.ceil((new Date(event.application_deadline) - new Date()) / (1000 * 60 * 60 * 24)) <= 3

  return (
    <Link
      to={`/etkinlik/${event.id}`}
      style={{ textDecoration: 'none', color: 'inherit', display: 'block', height: '100%' }}
    >
    <div className="event-card h-100">
      {/* Image */}
      <div className="event-image-wrapper">
        <img
          src={event.thumbnail_url || event.image_url || '/placeholder-image-colored.webp'}
          alt={event.title}
          className="event-image"
          width="400"
          height="200"
          loading="lazy"
          onError={(e) => { e.target.src = '/placeholder-image-colored.webp' }}
        />
        <div className="event-image-overlay" />
        <span
          className="event-source-badge"
          style={{
            background: sourceStyle.bg,
            color: sourceStyle.color,
            border: `1px solid ${sourceStyle.border}`,
          }}
        >
          {event.source}
        </span>
        <div style={{ position: 'absolute', top: '8px', left: '8px' }}>
          <ShareButtons event={event} detailUrl={canonicalUrl} variant="icon" />
        </div>
        <button
          type="button"
          className={`favorite-button ${isFavorite(event.id) ? 'active' : ''}`}
          aria-label={isFavorite(event.id) ? t('eventCard.favoriteRemove') : t('eventCard.favoriteAdd')}
          title={isFavorite(event.id) ? t('eventCard.favoriteRemove') : t('eventCard.favoriteAdd')}
          onClick={e => {
            e.preventDefault()
            e.stopPropagation()
            toggleFavorite(event.id)
          }}
        >
          <i className={`${isFavorite(event.id) ? 'fas' : 'far'} fa-bookmark`} />
        </button>
        {event.tags && event.tags.length > 0 && (
          <div style={{ position: 'absolute', bottom: '8px', left: '8px', display: 'flex', gap: '4px', flexWrap: 'wrap' }}>
            {event.tags.slice(0, 2).map(name => (
              <TagBadge key={name} name={name} />
            ))}
            {event.tags.length > 2 && (
              <span style={{ fontSize: '0.65rem', color: 'var(--text-muted)', fontWeight: 700, alignSelf: 'center' }}>
                +{event.tags.length - 2}
              </span>
            )}
          </div>
        )}
      </div>

      {/* Content */}
      <div className="event-content">
        <h3 className="event-title">{event.title}</h3>

        {event.description && (
          <p className="event-description">
            {event.description.length > 120
              ? `${event.description.substring(0, 120)}…`
              : event.description}
          </p>
        )}

        <div className="event-meta">
          <div className="event-meta-item">
            <i className="fas fa-calendar-alt"></i>
            <span>{formatDate(event.date)}</span>
          </div>
          <div className="event-meta-item">
            <i className="fas fa-map-marker-alt"></i>
            <span>{event.location || t('eventCard.noLocation')}</span>
          </div>
          {deadlineText && (
            <div
              className="event-meta-item"
              style={deadlineSoon ? { color: '#EF4444', fontWeight: 600 } : undefined}
            >
              <i className="fas fa-hourglass-half"></i>
              <span>{deadlineText}</span>
            </div>
          )}
        </div>

        <div className="event-footer">
          <span className={`event-status ${isActive ? 'status-acik' : 'status-kapali'}`}>
            {isActive ? t('eventCard.statusOpen') : t('eventCard.statusClosed')}
          </span>
          <button
            type="button"
            className="btn-event"
            onClick={e => {
              e.preventDefault()
              e.stopPropagation()
              window.open(safeUrl, '_blank', 'noopener,noreferrer')
            }}
          >
            {t('eventCard.applyButton')}
            <i className="fas fa-arrow-right" style={{ fontSize: '0.7rem' }}></i>
          </button>
        </div>
      </div>
    </div>
    </Link>
  )
}

export default EventCard
