import React from 'react'
import { useQuery } from 'react-query'
import { useTranslation } from 'react-i18next'
import { formatDistanceToNow } from 'date-fns'
import { publicAPI } from '../services/api'
import LoadingSpinner from '../components/LoadingSpinner'
import { useDateLocale } from '../hooks/useDateLocale'

const StatusPage = () => {
  const { t } = useTranslation()
  const dateLocale = useDateLocale()
  const { data, isLoading, error, dataUpdatedAt } = useQuery(
    'platform-status',
    () => publicAPI.getStatus(),
    { refetchInterval: 60_000 }
  )

  const status = data?.data

  return (
    <div className="container py-5">
      <div className="row justify-content-center">
        <div className="col-lg-8">

          <div className="d-flex align-items-center gap-3 mb-4">
            <h1 style={{ fontSize: '1.6rem', fontWeight: 700, color: 'var(--text-primary)', margin: 0 }}>
              {t('status.title')}
            </h1>
            {!isLoading && !error && (
              <span style={{
                background: 'rgba(34,197,94,0.15)',
                color: '#22c55e',
                border: '1px solid rgba(34,197,94,0.3)',
                borderRadius: '999px',
                padding: '2px 12px',
                fontSize: '0.8rem',
                fontWeight: 600,
              }}>
                {t('status.online')}
              </span>
            )}
          </div>

          {isLoading && <LoadingSpinner />}

          {error && (
            <div style={{
              padding: '1rem 1.25rem',
              background: 'rgba(239,68,68,0.1)',
              border: '1px solid rgba(239,68,68,0.3)',
              borderRadius: '10px',
              color: '#ef4444',
              fontSize: '0.9rem',
            }}>
              {t('status.loadError')}
            </div>
          )}

          {status && (
            <>
              {/* Özet kartlar */}
              <div className="row g-3 mb-4">
                <div className="col-6 col-md-4">
                  <StatCard label={t('status.activeEvents')} value={status.active_events} />
                </div>
                <div className="col-6 col-md-4">
                  <StatCard label={t('status.totalEvents')} value={status.total_events} />
                </div>
                <div className="col-6 col-md-4">
                  <StatCard label={t('status.sourceCount')} value={status.scrapers.length} />
                </div>
              </div>

              {/* Scraper tablosu */}
              <h2 style={{ fontSize: '1rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '0.75rem' }}>
                {t('status.dataSources')}
              </h2>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                {status.scrapers.map((s) => (
                  <ScraperRow key={s.source} scraper={s} t={t} dateLocale={dateLocale} />
                ))}
              </div>

              {dataUpdatedAt > 0 && (
                <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '1.5rem', textAlign: 'right' }}>
                  {t('status.lastUpdate')}{' '}
                  {formatDistanceToNow(new Date(dataUpdatedAt), { addSuffix: true, locale: dateLocale })}
                </p>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  )
}

const StatCard = ({ label, value }) => (
  <div style={{
    background: 'var(--bg-card)',
    border: '1px solid var(--border-color)',
    borderRadius: '10px',
    padding: '1rem',
    textAlign: 'center',
  }}>
    <div style={{ fontSize: '1.75rem', fontWeight: 700, color: 'var(--action-primary)' }}>{value}</div>
    <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '2px' }}>{label}</div>
  </div>
)

const ScraperRow = ({ scraper, t, dateLocale }) => {
  const ok = scraper.status === 'success'
  const lastRun = scraper.last_run
    ? formatDistanceToNow(new Date(scraper.last_run), { addSuffix: true, locale: dateLocale })
    : t('status.unknown')

  return (
    <div style={{
      background: 'var(--bg-card)',
      border: '1px solid var(--border-color)',
      borderRadius: '10px',
      padding: '0.875rem 1rem',
      display: 'flex',
      alignItems: 'center',
      gap: '0.75rem',
      flexWrap: 'wrap',
    }}>
      <span style={{
        width: '8px', height: '8px', borderRadius: '50%', flexShrink: 0,
        background: ok ? '#22c55e' : '#ef4444',
        boxShadow: ok ? '0 0 6px #22c55e88' : '0 0 6px #ef444488',
      }} />
      <span style={{ fontWeight: 600, color: 'var(--text-primary)', minWidth: '140px', fontSize: '0.9rem' }}>
        {scraper.source}
      </span>
      <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginRight: 'auto' }}>
        {lastRun}
      </span>
      <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
        {t('status.scraperStats', { newCount: scraper.new_events, foundCount: scraper.events_found })}
      </span>
      <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
        {scraper.duration_seconds}s
      </span>
      {scraper.error && (
        <div style={{
          width: '100%',
          marginTop: '0.25rem',
          fontSize: '0.75rem',
          color: '#ef4444',
          background: 'rgba(239,68,68,0.07)',
          padding: '0.375rem 0.625rem',
          borderRadius: '6px',
        }}>
          {scraper.error}
        </div>
      )}
    </div>
  )
}

export default StatusPage
