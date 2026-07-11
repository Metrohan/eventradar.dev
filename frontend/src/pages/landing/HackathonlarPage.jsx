import React, { useEffect } from 'react'
import EventListing from '../../components/EventListing'
import { setPageSEO } from '../../utils/seo'

const HackathonlarPage = () => {
  useEffect(() => {
    setPageSEO({
      title: 'Hackathon Etkinlikleri | TechEventRadar',
      description: 'Türkiye\'deki güncel hackathon etkinliklerini tek listede keşfet. TechCareer, Kodluyoruz, Youthall ve daha fazla kaynaktan otomatik güncellenen hackathon takvimi.',
      path: '/hackathonlar',
    })
  }, [])

  return (
    <EventListing
      title="Hackathon Etkinlikleri"
      initialTags={['hackathon']}
      intro={
        <div>
          <h1 style={{ fontSize: '1.75rem', fontWeight: 700, marginBottom: '0.5rem' }}>
            Türkiye'deki Hackathon Etkinlikleri
          </h1>
          <p className="text-muted" style={{ maxWidth: '640px' }}>
            Farklı platformlardan toplanan güncel hackathon'ları tek yerden takip et, başvuru
            son tarihini kaçırma.
          </p>
        </div>
      }
      emptyStateText="Şu anda açık bir hackathon bulunmuyor, filtreleri değiştirerek diğer etkinliklere göz atabilirsin."
    />
  )
}

export default HackathonlarPage
