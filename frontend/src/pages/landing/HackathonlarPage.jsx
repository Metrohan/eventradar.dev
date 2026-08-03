import React, { useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import EventListing from '../../components/EventListing'
import { setPageSEO, injectJsonLd } from '../../utils/seo'

const HackathonlarPage = () => {
  const { t, i18n } = useTranslation()

  useEffect(() => {
    setPageSEO({
      title: 'Hackathon Etkinlikleri | TechEventRadar',
      tabTitle: `${t('landing.hackathonlar.title')} | TechEventRadar`,
      description: 'Türkiye\'deki güncel hackathon etkinliklerini tek listede keşfet. TechCareer, Kodluyoruz, Youthall ve daha fazla kaynaktan otomatik güncellenen hackathon takvimi.',
      path: '/hackathonlar',
    })
    return injectJsonLd('page-jsonld', {
      '@context': 'https://schema.org',
      '@type': 'CollectionPage',
      name: 'Hackathon Etkinlikleri | TechEventRadar',
      description: 'Türkiye\'deki güncel hackathon etkinliklerini tek listede keşfet.',
      url: 'https://eventradar.dev/hackathonlar',
    })
    // Re-run on language change so the tab title stays in sync — otherwise
    // it only ever reflects whatever language was active on first mount.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [i18n.language])

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
