import React, { useEffect } from 'react'
import EventListing from '../../components/EventListing'
import { setPageSEO } from '../../utils/seo'

const ONE_WEEK_MS = 7 * 24 * 60 * 60 * 1000

const deadlineSoon = (event) => {
  if (!event.application_deadline) return false
  const deadline = new Date(event.application_deadline)
  const now = new Date()
  return deadline >= now && deadline - now <= ONE_WEEK_MS
}

const SonBasvurularPage = () => {
  useEffect(() => {
    setPageSEO({
      title: 'Son Başvuru Tarihi Yaklaşan Etkinlikler | TechEventRadar',
      description: 'Başvuru son tarihi bu hafta dolacak hackathon, bootcamp ve webinar etkinliklerini kaçırma.',
      path: '/son-basvurular',
    })
  }, [])

  return (
    <EventListing
      title="Son Başvurusu Yaklaşan Etkinlikler"
      extraFilter={deadlineSoon}
      intro={
        <div>
          <h1 style={{ fontSize: '1.75rem', fontWeight: 700, marginBottom: '0.5rem' }}>
            Son Başvurusu Yaklaşan Etkinlikler
          </h1>
          <p className="text-muted" style={{ maxWidth: '640px' }}>
            Başvuru son tarihi önümüzdeki 7 gün içinde dolacak etkinlikleri kaçırma.
          </p>
        </div>
      }
      emptyStateText="Son başvurusu bu hafta dolacak bir etkinlik bulunmuyor, tüm etkinliklere göz atabilirsin."
    />
  )
}

export default SonBasvurularPage
