import React, { useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import EventListing from '../../components/EventListing'
import { setPageSEO, injectJsonLd } from '../../utils/seo'

const ONE_WEEK_MS = 7 * 24 * 60 * 60 * 1000

const isThisWeek = (event) => {
  if (!event.date) return false
  const eventDate = new Date(event.date)
  const now = new Date()
  return eventDate >= now && eventDate - now <= ONE_WEEK_MS
}

const BuHaftakiEtkinliklerPage = () => {
  const { t, i18n } = useTranslation()

  useEffect(() => {
    setPageSEO({
      title: 'Bu Hafta Başvurabileceğin Etkinlikler | TechEventRadar',
      tabTitle: `${t('landing.thisWeek.title')} | TechEventRadar`,
      description: 'Önümüzdeki 7 gün içinde gerçekleşecek hackathon, bootcamp ve webinar etkinliklerini tek listede keşfet.',
      path: '/bu-haftaki-etkinlikler',
    })
    return injectJsonLd('page-jsonld', {
      '@context': 'https://schema.org',
      '@type': 'CollectionPage',
      name: 'Bu Hafta Başvurabileceğin Etkinlikler | TechEventRadar',
      description: 'Önümüzdeki 7 gün içinde gerçekleşecek hackathon, bootcamp ve webinar etkinliklerini tek listede keşfet.',
      url: 'https://eventradar.dev/bu-haftaki-etkinlikler',
    })
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [i18n.language])

  return (
    <EventListing
      title={t('landing.thisWeek.title')}
      extraFilter={isThisWeek}
      intro={
        <div>
          <h1 style={{ fontSize: '1.75rem', fontWeight: 700, marginBottom: '0.5rem' }}>
            {t('landing.thisWeek.introHeading')}
          </h1>
          <p className="text-muted" style={{ maxWidth: '640px' }}>
            {t('landing.thisWeek.introText')}
          </p>
        </div>
      }
      emptyStateText={t('landing.thisWeek.emptyState')}
    />
  )
}

export default BuHaftakiEtkinliklerPage
