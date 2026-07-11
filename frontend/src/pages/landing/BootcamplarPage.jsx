import React, { useEffect } from 'react'
import EventListing from '../../components/EventListing'
import { setPageSEO } from '../../utils/seo'

const BootcamplarPage = () => {
  useEffect(() => {
    setPageSEO({
      title: 'Bootcamp Etkinlikleri | TechEventRadar',
      description: 'Türkiye\'deki ücretsiz ve ücretli bootcamp programlarını tek listede keşfet. Yazılım, veri bilimi ve daha fazlası için güncel bootcamp takvimi.',
      path: '/bootcamplar',
    })
  }, [])

  return (
    <EventListing
      title="Bootcamp Etkinlikleri"
      initialTags={['bootcamp']}
      intro={
        <div>
          <h1 style={{ fontSize: '1.75rem', fontWeight: 700, marginBottom: '0.5rem' }}>
            Türkiye'deki Bootcamp Programları
          </h1>
          <p className="text-muted" style={{ maxWidth: '640px' }}>
            Farklı platformlardan toplanan güncel bootcamp programlarını tek yerden takip et.
          </p>
        </div>
      }
      emptyStateText="Şu anda açık bir bootcamp bulunmuyor, filtreleri değiştirerek diğer etkinliklere göz atabilirsin."
    />
  )
}

export default BootcamplarPage
