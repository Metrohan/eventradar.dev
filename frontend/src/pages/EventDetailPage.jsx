import React, { useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { useQuery } from 'react-query'
import { format } from 'date-fns'
import { tr } from 'date-fns/locale'
import { publicAPI } from '../services/api'
import LoadingSpinner from '../components/LoadingSpinner'
import ErrorMessage from '../components/ErrorMessage'
import TagBadge from '../components/TagBadge'
import ShareButtons from '../components/ShareButtons'

const DEFAULT_TITLE = 'TechEventRadar | Bootcamp, Hackathon & Kariyer Etkinlikleri'
const DEFAULT_DESC = 'Türkiye\'deki bootcamp, hackathon ve kariyer etkinliklerini tek yerden ücretsiz takip et. 8 kaynaktan günlük güncellenen etkinlik platformu.'

function setMeta(name, content, property = false) {
  const attr = property ? `[property="${name}"]` : `[name="${name}"]`
  let el = document.querySelector(`meta${attr}`)
  if (!el) {
    el = document.createElement('meta')
    el.setAttribute(property ? 'property' : 'name', name)
    document.head.appendChild(el)
  }
  el.setAttribute('content', content)
}

const EventDetailPage = () => {
  const { id } = useParams()

  const { data, isLoading, error } = useQuery(
    ['event', id],
    () => publicAPI.getEventById(id),
    { retry: 1 }
  )

  const event = data?.data

  useEffect(() => {
    if (!event) return

    const dateStr = event.date
      ? format(new Date(event.date), 'dd MMM yyyy', { locale: tr })
      : null
    const parts = [event.title]
    if (dateStr) parts.push(dateStr)
    if (event.location) parts.push(event.location)
    const description = parts.join(' — ') + '. Ücretsiz kariyer etkinliği.'

    const canonicalUrl = `https://eventradar.dev/etkinlik/${id}`
    const ogImage = (event.image_url && /^https?:\/\//i.test(event.image_url))
      ? event.image_url
      : 'https://eventradar.dev/banner.png'

    document.title = `${event.title} | TechEventRadar`
    setMeta('description', description)

    // Open Graph
    setMeta('og:title', `${event.title} | TechEventRadar`, true)
    setMeta('og:description', description, true)
    setMeta('og:image', ogImage, true)
    setMeta('og:url', canonicalUrl, true)
    setMeta('og:type', 'website', true)

    // Twitter Card
    setMeta('twitter:card', 'summary_large_image')
    setMeta('twitter:title', `${event.title} | TechEventRadar`)
    setMeta('twitter:description', description)
    setMeta('twitter:image', ogImage)

    // Canonical
    let canonical = document.querySelector('link[rel="canonical"]')
    if (!canonical) {
      canonical = document.createElement('link')
      canonical.setAttribute('rel', 'canonical')
      document.head.appendChild(canonical)
    }
    canonical.setAttribute('href', canonicalUrl)

    // JSON-LD Event schema
    const schema = {
      '@context': 'https://schema.org',
      '@type': 'Event',
      name: event.title,
      ...(event.date && { startDate: new Date(event.date).toISOString() }),
      ...(event.description && { description: event.description }),
      ...(event.image_url && { image: event.image_url }),
      url: `https://eventradar.dev/etkinlik/${id}`,
      isAccessibleForFree: true,
      eventStatus: 'https://schema.org/EventScheduled',
      ...(event.location && {
        location: { '@type': 'Place', name: event.location },
      }),
      organizer: { '@type': 'Organization', name: event.source },
    }
    document.getElementById('event-jsonld')?.remove()
    const script = document.createElement('script')
    script.id = 'event-jsonld'
    script.type = 'application/ld+json'
    script.text = JSON.stringify(schema)
      .replace(/</g, '\\u003c')
      .replace(/>/g, '\\u003e')
      .replace(/&/g, '\\u0026')
      .replace(/\u2028/g, '\\u2028')
      .replace(/\u2029/g, '\\u2029')
    document.head.appendChild(script)

    return () => {
      document.title = DEFAULT_TITLE
      setMeta('description', DEFAULT_DESC)
      setMeta('og:title', 'TechEventRadar', true)
      setMeta('og:description', DEFAULT_DESC, true)
      setMeta('og:image', 'https://eventradar.dev/banner.png', true)
      setMeta('og:url', 'https://eventradar.dev', true)
      setMeta('twitter:title', 'TechEventRadar')
      setMeta('twitter:description', DEFAULT_DESC)
      setMeta('twitter:image', 'https://eventradar.dev/banner.png')
      document.querySelector('link[rel="canonical"]')?.setAttribute('href', 'https://eventradar.dev')
      document.getElementById('event-jsonld')?.remove()
    }
  }, [event, id])

  if (isLoading) return <LoadingSpinner />
  if (error || !event) return <ErrorMessage message="Etkinlik bulunamadı veya yüklenirken hata oluştu." />

  const safeUrl = /^https?:\/\//i.test(event.url) ? event.url : '#'
  const safeImageUrl = event.image_url && /^https?:\/\//i.test(event.image_url) ? event.image_url : null

  const formatDate = (dateString) => {
    if (!dateString) return 'Tarih belirtilmemiş'
    try {
      return format(new Date(dateString), 'dd MMMM yyyy · HH:mm', { locale: tr })
    } catch {
      return 'Tarih belirtilmemiş'
    }
  }

  const formatDeadline = (dateString) => {
    if (!dateString) return null
    try {
      const deadline = new Date(dateString)
      const daysLeft = Math.ceil((deadline - new Date()) / (1000 * 60 * 60 * 24))
      const formatted = format(deadline, 'dd MMMM yyyy', { locale: tr })
      if (daysLeft < 0) return null
      if (daysLeft === 0) return 'Son başvuru: bugün'
      if (daysLeft <= 3) return `Son başvuruya ${daysLeft} gün kaldı (${formatted})`
      return `Son başvuru: ${formatted}`
    } catch {
      return null
    }
  }

  const deadlineText = formatDeadline(event.application_deadline)
  const canonicalUrl = `https://eventradar.dev/etkinlik/${id}`

  return (
    <div className="container py-5">
      <div className="row justify-content-center">
        <div className="col-lg-8">

          {/* Geri linki */}
          <Link
            to="/"
            className="d-inline-flex align-items-center gap-2 mb-4"
            style={{ color: 'var(--text-muted)', textDecoration: 'none', fontSize: '0.9rem' }}
          >
            <i className="fas fa-arrow-left" style={{ fontSize: '0.75rem' }}></i>
            Tüm Etkinlikler
          </Link>

          {/* Görsel */}
          {safeImageUrl && (
            <div className="mb-4" style={{ borderRadius: '12px', overflow: 'hidden', maxHeight: '320px' }}>
              <img
                src={safeImageUrl}
                alt={event.title}
                style={{ width: '100%', height: '320px', objectFit: 'cover' }}
                onError={(e) => { e.target.style.display = 'none' }}
              />
            </div>
          )}

          {/* Başlık */}
          <h1 style={{ fontSize: '1.75rem', fontWeight: 700, color: 'var(--text-primary)', lineHeight: 1.3, marginBottom: '1rem' }}>
            {event.title}
          </h1>

          {/* Meta bilgiler */}
          <div className="d-flex flex-wrap gap-3 mb-4" style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>
            <span>
              <i className="fas fa-calendar-alt me-2" style={{ color: 'var(--action-primary)' }}></i>
              {formatDate(event.date)}
            </span>
            <span>
              <i className="fas fa-map-marker-alt me-2" style={{ color: 'var(--action-primary)' }}></i>
              {event.location || 'Konum belirtilmemiş'}
            </span>
            <span>
              <i className="fas fa-globe me-2" style={{ color: 'var(--action-primary)' }}></i>
              {event.source}
            </span>
            {deadlineText && (
              <span style={{ color: '#EF4444', fontWeight: 600 }}>
                <i className="fas fa-hourglass-half me-2"></i>
                {deadlineText}
              </span>
            )}
          </div>

          {/* Etiketler */}
          {event.tags && event.tags.length > 0 && (
            <div className="d-flex flex-wrap gap-2 mb-4">
              {event.tags.map(name => (
                <TagBadge key={name} name={name} />
              ))}
            </div>
          )}

          {/* Açıklama */}
          {event.description && (
            <div
              className="mb-5"
              style={{
                color: 'var(--text-secondary)',
                lineHeight: 1.7,
                padding: '1.25rem',
                background: 'var(--bg-card)',
                borderRadius: '10px',
                border: '1px solid var(--border-color)',
              }}
            >
              <p style={{ margin: 0, whiteSpace: 'pre-line' }}>{event.description}</p>
            </div>
          )}

          {/* CTA butonu */}
          <a
            href={safeUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="btn-event"
            style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', padding: '0.75rem 1.5rem', fontSize: '1rem' }}
          >
            Etkinliğe Git
            <i className="fas fa-external-link-alt" style={{ fontSize: '0.8rem' }}></i>
          </a>

          <div className="mt-3">
            <ShareButtons event={event} detailUrl={canonicalUrl} variant="full" />
          </div>

        </div>
      </div>
    </div>
  )
}

export default EventDetailPage
