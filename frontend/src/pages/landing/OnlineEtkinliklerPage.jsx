import React, { useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import EventListing from '../../components/EventListing'
import { setPageSEO, injectJsonLd } from '../../utils/seo'

const OnlineEtkinliklerPage = () => {
  const { t, i18n } = useTranslation()

  useEffect(() => {
    setPageSEO({
      title: 'Online Teknoloji Etkinlikleri | TechEventRadar',
      tabTitle: `${t('landing.online.title')} | TechEventRadar`,
      description: 'Evden katılabileceğin online hackathon, webinar ve bootcamp etkinliklerini tek listede keşfet.',
      path: '/online-etkinlikler',
    })
    return injectJsonLd('page-jsonld', {
      '@context': 'https://schema.org',
      '@type': 'CollectionPage',
      name: 'Online Teknoloji Etkinlikleri | TechEventRadar',
      description: 'Evden katılabileceğin online hackathon, webinar ve bootcamp etkinliklerini tek listede keşfet.',
      url: 'https://eventradar.dev/online-etkinlikler',
    })
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [i18n.language])

  return (
    <EventListing
      title={t('landing.online.title')}
      initialLocation="Online"
      intro={
        <div>
          <h1 style={{ fontSize: '1.75rem', fontWeight: 700, marginBottom: '0.5rem' }}>
            {t('landing.online.introHeading')}
          </h1>
          <p className="text-muted" style={{ maxWidth: '640px' }}>
            {t('landing.online.introText')}
          </p>
        </div>
      }
      emptyStateText={t('landing.online.emptyState')}
    />
  )
}

export default OnlineEtkinliklerPage
