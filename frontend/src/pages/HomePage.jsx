import React from 'react'
import { useQuery } from 'react-query'
import { useTranslation } from 'react-i18next'
import { publicAPI } from '../services/api'
import AnnouncementModal from '../components/AnnouncementModal'
import ChannelsBanner from '../components/ChannelsBanner'
import EventListing from '../components/EventListing'
import useSources from '../hooks/useSources'

const HomePage = () => {
  const { t } = useTranslation()
  const [searchTerm, setSearchTerm] = React.useState('')
  const { sources } = useSources()
  const isPrerenderPass = new URLSearchParams(window.location.search).get('__prerender') === '1'

  const { data: eventsData } = useQuery(
    'events',
    () => publicAPI.getEvents(true)
  )

  const { data: announcementData } = useQuery(
    'latest-announcement',
    () => publicAPI.getLatestAnnouncement(),
    { retry: false }
  )

  const totalCount = eventsData?.data?.total_count || 0
  const announcement = announcementData?.data

  return (
    <>
      {/* ── Hero ─────────────────────────────────────────── */}
      <section className="hero-section">
        <div className="hero-glow hero-glow--blue" />
        <div className="hero-glow hero-glow--purple" />
        <div className="hero-grid" />

        <div className="container">
          <div className="hero-content">
            <div className="hero-badge">
              <i className="fas fa-bolt"></i>
              {t('home.hero.badge')}
            </div>

            <h1 className="hero-title">
              {t('home.hero.titleLine1')}<br />
              <span className="gradient-text">{t('home.hero.titleLine2')}</span> {t('home.hero.titleSuffix')}
            </h1>

            <p className="hero-subtitle">
              {t('home.hero.subtitle')}
            </p>

            {/* Quick search */}
            <div className="hero-search">
              <i className="fas fa-search hero-search-icon"></i>
              <input
                type="text"
                className="hero-search-input"
                placeholder={t('home.hero.searchPlaceholder')}
                value={searchTerm}
                onChange={e => setSearchTerm(e.target.value)}
              />
            </div>

            {/* Stats */}
            <div className="hero-stats">
              <div className="hero-stat">
                <span className="hero-stat-number">{totalCount}+</span>
                <span className="hero-stat-label">{t('home.hero.statActive')}</span>
              </div>
              <div className="hero-stat-divider" />
              <div className="hero-stat">
                <span className="hero-stat-number">{sources.length}</span>
                <span className="hero-stat-label">{t('home.hero.statPlatforms')}</span>
              </div>
              <div className="hero-stat-divider" />
              <div className="hero-stat">
                <span className="hero-stat-number">{t('home.hero.statUpdateValue')}</span>
                <span className="hero-stat-label">{t('home.hero.statUpdateLabel')}</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ── Main content ─────────────────────────────────── */}
      <EventListing searchTerm={searchTerm} onSearchTermChange={setSearchTerm} />

      {/* ── Channel discovery ────────────────────────────── */}
      <ChannelsBanner />

      {/*
        AnnouncementModal reveals itself via a post-mount setTimeout, so its
        rendered output legitimately differs between "settled" (what the
        prerender snapshot captures) and "just mounted" (the client's first
        hydration render) — an unavoidable mismatch for any timer-driven UI
        under snapshot-based prerendering (see docs/adr/0006-prerender-poc.md).
        The prerender script navigates with ?__prerender=1; skipping the
        modal in that pass keeps the snapshot in the same state the client's
        first render starts from, so hydration has nothing to reconcile here
        and the timer-driven reveal happens the same way it always did.
      */}
      {announcement && !isPrerenderPass && <AnnouncementModal announcement={announcement} />}
    </>
  )
}

export default HomePage
