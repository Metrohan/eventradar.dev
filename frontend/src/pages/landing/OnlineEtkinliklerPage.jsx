import React, { useEffect } from 'react'
import EventListing from '../../components/EventListing'
import { setPageSEO } from '../../utils/seo'

const OnlineEtkinliklerPage = () => {
  useEffect(() => {
    setPageSEO({
      title: 'Online Teknoloji Etkinlikleri | TechEventRadar',
      description: 'Evden katılabileceğin online hackathon, webinar ve bootcamp etkinliklerini tek listede keşfet.',
      path: '/online-etkinlikler',
    })
  }, [])

  return (
    <EventListing
      title="Online Etkinlikler"
      initialLocation="Online"
      intro={
        <div>
          <h1 style={{ fontSize: '1.75rem', fontWeight: 700, marginBottom: '0.5rem' }}>
            Online Katılabileceğin Teknoloji Etkinlikleri
          </h1>
          <p className="text-muted" style={{ maxWidth: '640px' }}>
            Şehir fark etmeksizin evden katılabileceğin güncel online etkinlikler.
          </p>
        </div>
      }
      emptyStateText="Şu anda açık bir online etkinlik bulunmuyor, filtreleri değiştirerek diğer etkinliklere göz atabilirsin."
    />
  )
}

export default OnlineEtkinliklerPage
