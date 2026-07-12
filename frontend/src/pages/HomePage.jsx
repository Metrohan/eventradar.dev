import React from 'react'
import { useQuery } from 'react-query'
import { publicAPI } from '../services/api'
import AnnouncementModal from '../components/AnnouncementModal'
import EventListing from '../components/EventListing'
import useSources from '../hooks/useSources'

const HomePage = () => {
  const [searchTerm, setSearchTerm] = React.useState('')
  const { sources } = useSources()

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
              Türkiye'nin Teknoloji Etkinlik Radarı
            </div>

            <h1 className="hero-title">
              Tüm Etkinlikleri<br />
              <span className="gradient-text">Tek Platformda</span> Keşfet
            </h1>

            <p className="hero-subtitle">
              Herkese açık farklı kaynaklarda yayımlanan hackathon, seminer ve atölye
              duyurularını tek yerde keşfet.
            </p>

            {/* Quick search */}
            <div className="hero-search">
              <i className="fas fa-search hero-search-icon"></i>
              <input
                type="text"
                className="hero-search-input"
                placeholder="Etkinlik, platform veya konu ara..."
                value={searchTerm}
                onChange={e => setSearchTerm(e.target.value)}
              />
            </div>

            {/* Stats */}
            <div className="hero-stats">
              <div className="hero-stat">
                <span className="hero-stat-number">{totalCount}+</span>
                <span className="hero-stat-label">Aktif Etkinlik</span>
              </div>
              <div className="hero-stat-divider" />
              <div className="hero-stat">
                <span className="hero-stat-number">{sources.length}</span>
                <span className="hero-stat-label">Platform</span>
              </div>
              <div className="hero-stat-divider" />
              <div className="hero-stat">
                <span className="hero-stat-number">Günlük</span>
                <span className="hero-stat-label">Güncelleme</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ── Main content ─────────────────────────────────── */}
      <EventListing searchTerm={searchTerm} onSearchTermChange={setSearchTerm} />

      {announcement && <AnnouncementModal announcement={announcement} />}
    </>
  )
}

export default HomePage
