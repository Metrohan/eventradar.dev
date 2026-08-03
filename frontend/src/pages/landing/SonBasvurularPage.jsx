import React, { useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import EventListing from '../../components/EventListing'
import { setPageSEO, injectJsonLd } from '../../utils/seo'

const ONE_WEEK_MS = 7 * 24 * 60 * 60 * 1000

const deadlineSoon = (event) => {
  if (!event.application_deadline) return false
  const deadline = new Date(event.application_deadline)
  const now = new Date()
  return deadline >= now && deadline - now <= ONE_WEEK_MS
}

const SonBasvurularPage = () => {
  const { t, i18n } = useTranslation()

  useEffect(() => {
    setPageSEO({
      title: 'Son Başvuru Tarihi Yaklaşan Etkinlikler | TechEventRadar',
      tabTitle: `${t('landing.lastCall.title')} | TechEventRadar`,
      description: 'Başvuru son tarihi bu hafta dolacak hackathon, bootcamp ve webinar etkinliklerini kaçırma.',
      path: '/son-basvurular',
    })
    return injectJsonLd('page-jsonld', {
      '@context': 'https://schema.org',
      '@type': 'CollectionPage',
      name: 'Son Başvuru Tarihi Yaklaşan Etkinlikler | TechEventRadar',
      description: 'Başvuru son tarihi bu hafta dolacak hackathon, bootcamp ve webinar etkinliklerini kaçırma.',
      url: 'https://eventradar.dev/son-basvurular',
    })
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [i18n.language])

  return (
    <EventListing
      title={t('landing.lastCall.title')}
      extraFilter={deadlineSoon}
      intro={
        <div>
          <h1 style={{ fontSize: '1.75rem', fontWeight: 700, marginBottom: '0.5rem' }}>
            {t('landing.lastCall.introHeading')}
          </h1>
          <p className="text-muted" style={{ maxWidth: '640px' }}>
            {t('landing.lastCall.introText')}
          </p>
        </div>
      }
      emptyStateText={t('landing.lastCall.emptyState')}
    />
  )
}

export default SonBasvurularPage
