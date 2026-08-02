import React, { useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import EventListing from '../../components/EventListing'
import { setPageSEO } from '../../utils/seo'

const BootcamplarPage = () => {
  const { t, i18n } = useTranslation()

  useEffect(() => {
    setPageSEO({
      title: 'Bootcamp Etkinlikleri | TechEventRadar',
      tabTitle: `${t('landing.bootcamplar.title')} | TechEventRadar`,
      description: 'Türkiye\'deki ücretsiz ve ücretli bootcamp programlarını tek listede keşfet. Yazılım, veri bilimi ve daha fazlası için güncel bootcamp takvimi.',
      path: '/bootcamplar',
    })
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [i18n.language])

  return (
    <EventListing
      title={t('landing.bootcamplar.title')}
      initialTags={['bootcamp']}
      intro={
        <div>
          <h1 style={{ fontSize: '1.75rem', fontWeight: 700, marginBottom: '0.5rem' }}>
            {t('landing.bootcamplar.introHeading')}
          </h1>
          <p className="text-muted" style={{ maxWidth: '640px' }}>
            {t('landing.bootcamplar.introText')}
          </p>
        </div>
      }
      emptyStateText={t('landing.bootcamplar.emptyState')}
    />
  )
}

export default BootcamplarPage
