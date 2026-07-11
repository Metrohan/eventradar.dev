import React, { useEffect } from 'react'
import EventListing from '../../components/EventListing'
import { setPageSEO } from '../../utils/seo'

const ONE_WEEK_MS = 7 * 24 * 60 * 60 * 1000

const isThisWeek = (event) => {
  if (!event.date) return false
  const eventDate = new Date(event.date)
  const now = new Date()
  return eventDate >= now && eventDate - now <= ONE_WEEK_MS
}

const BuHaftakiEtkinliklerPage = () => {
  useEffect(() => {
    setPageSEO({
      title: 'Bu Hafta Başvurabileceğin Etkinlikler | TechEventRadar',
      description: 'Önümüzdeki 7 gün içinde gerçekleşecek hackathon, bootcamp ve webinar etkinliklerini tek listede keşfet.',
      path: '/bu-haftaki-etkinlikler',
    })
  }, [])

  return (
    <EventListing
      title="Bu Haftaki Etkinlikler"
      extraFilter={isThisWeek}
      intro={
        <div>
          <h1 style={{ fontSize: '1.75rem', fontWeight: 700, marginBottom: '0.5rem' }}>
            Bu Hafta Gerçekleşecek Etkinlikler
          </h1>
          <p className="text-muted" style={{ maxWidth: '640px' }}>
            Önümüzdeki 7 gün içinde gerçekleşecek etkinlikleri kaçırma.
          </p>
        </div>
      }
      emptyStateText="Bu hafta içinde planlanmış bir etkinlik bulunmuyor, tüm etkinliklere göz atabilirsin."
    />
  )
}

export default BuHaftakiEtkinliklerPage
