import React, { useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import EventListing from '../../components/EventListing'
import { setPageSEO } from '../../utils/seo'

const HackathonlarPage = () => {
  const { t } = useTranslation()

  useEffect(() => {
    setPageSEO({
      title: 'Hackathon Etkinlikleri | TechEventRadar',
      description: 'Türkiye\'deki güncel hackathon etkinliklerini tek listede keşfet. TechCareer, Kodluyoruz, Youthall ve daha fazla kaynaktan otomatik güncellenen hackathon takvimi.',
      path: '/hackathonlar',
    })
  }, [])

  return (
    <EventListing
      title={t('landing.hackathonlar.title')}
      initialTags={['hackathon']}
      intro={
        <div>
          <h1 style={{ fontSize: '1.75rem', fontWeight: 700, marginBottom: '0.5rem' }}>
            {t('landing.hackathonlar.introHeading')}
          </h1>
          <p className="text-muted" style={{ maxWidth: '640px' }}>
            {t('landing.hackathonlar.introText')}
          </p>
        </div>
      }
      emptyStateText={t('landing.hackathonlar.emptyState')}
    />
  )
}

export default HackathonlarPage
