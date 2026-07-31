import React, { useEffect } from 'react'
import { Link } from 'react-router-dom'
import { useQuery } from 'react-query'
import { publicAPI } from '../services/api'
import LoadingSpinner from '../components/LoadingSpinner'
import ErrorMessage from '../components/ErrorMessage'
import { TAG_STYLES } from '../components/TagBadge'
import { setPageSEO } from '../utils/seo'

const WEEKDAY_LABELS = ['Pzt', 'Sal', 'Çar', 'Per', 'Cum', 'Cmt', 'Paz']
const MONTH_LABELS = [
  'Ocak', 'Şubat', 'Mart', 'Nisan', 'Mayıs', 'Haziran',
  'Temmuz', 'Ağustos', 'Eylül', 'Ekim', 'Kasım', 'Aralık',
]

const dateKey = (d) => `${d.getFullYear()}-${d.getMonth()}-${d.getDate()}`

// Pazartesi başlangıçlı 6 haftalık grid (42 hücre) üretir; ay dışındaki
// günler de dolgu olarak gösterilir (boş hücre bırakmamak için).
const buildMonthGrid = (year, month) => {
  const firstOfMonth = new Date(year, month, 1)
  const startOffset = (firstOfMonth.getDay() + 6) % 7 // Pazartesi=0
  const gridStart = new Date(year, month, 1 - startOffset)

  return Array.from({ length: 42 }, (_, i) => {
    const d = new Date(gridStart)
    d.setDate(gridStart.getDate() + i)
    return d
  })
}

const CalendarPage = () => {
  const now = new Date()
  const [cursor, setCursor] = React.useState({ year: now.getFullYear(), month: now.getMonth() })

  useEffect(() => {
    setPageSEO({
      title: 'Etkinlik Takvimi | TechEventRadar',
      description: 'Türkiye\'deki teknoloji etkinliklerini aylık takvim görünümünde keşfet.',
      path: '/takvim',
    })
  }, [])

  const { data: eventsData, isLoading, error } = useQuery(
    'events',
    () => publicAPI.getEvents(true)
  )

  const eventsByDay = React.useMemo(() => {
    const allEvents = eventsData?.data?.events || []
    const map = new Map()
    for (const event of allEvents) {
      if (!event.date) continue
      const d = new Date(event.date)
      if (Number.isNaN(d.getTime())) continue
      const key = dateKey(d)
      if (!map.has(key)) map.set(key, [])
      map.get(key).push(event)
    }
    return map
  }, [eventsData])

  if (isLoading) return <LoadingSpinner />
  if (error) return <ErrorMessage message="Etkinlikler yüklenirken bir sorun oluştu." />

  const grid = buildMonthGrid(cursor.year, cursor.month)
  const today = new Date()

  const goToPrevMonth = () => {
    setCursor((c) => {
      const m = c.month - 1
      return m < 0 ? { year: c.year - 1, month: 11 } : { year: c.year, month: m }
    })
  }
  const goToNextMonth = () => {
    setCursor((c) => {
      const m = c.month + 1
      return m > 11 ? { year: c.year + 1, month: 0 } : { year: c.year, month: m }
    })
  }
  const goToToday = () => setCursor({ year: today.getFullYear(), month: today.getMonth() })

  return (
    <div className="container py-4">
      <div className="mb-4">
        <h1 style={{ fontSize: '1.75rem', fontWeight: 700, marginBottom: '0.5rem' }}>
          Etkinlik Takvimi
        </h1>
        <p className="text-muted" style={{ maxWidth: '640px' }}>
          Türkiye'deki teknoloji etkinliklerini aylık takvimde keşfet.
        </p>
      </div>

      <div className="d-flex align-items-center justify-content-between mb-3 flex-wrap gap-2">
        <div className="d-flex align-items-center gap-2">
          <button className="filter-toggle" onClick={goToPrevMonth} aria-label="Önceki ay">
            <i className="fas fa-chevron-left"></i>
          </button>
          <h2 style={{ fontSize: '1.15rem', fontWeight: 700, margin: 0, minWidth: '160px', textAlign: 'center' }}>
            {MONTH_LABELS[cursor.month]} {cursor.year}
          </h2>
          <button className="filter-toggle" onClick={goToNextMonth} aria-label="Sonraki ay">
            <i className="fas fa-chevron-right"></i>
          </button>
        </div>
        <button className="filter-toggle" onClick={goToToday}>
          Bugün
        </button>
      </div>

      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(7, 1fr)',
          gap: '1px',
          background: 'var(--border-subtle)',
          border: '1px solid var(--border-subtle)',
          borderRadius: '12px',
          overflow: 'hidden',
        }}
      >
        {WEEKDAY_LABELS.map((label) => (
          <div
            key={label}
            style={{
              background: 'var(--bg-card)',
              padding: '8px 6px',
              fontSize: '0.72rem',
              fontWeight: 700,
              color: 'var(--text-muted)',
              textAlign: 'center',
              letterSpacing: '0.05em',
            }}
          >
            {label}
          </div>
        ))}

        {grid.map((day) => {
          const inMonth = day.getMonth() === cursor.month
          const isToday = dateKey(day) === dateKey(today)
          const dayEvents = eventsByDay.get(dateKey(day)) || []

          return (
            <div
              key={day.toISOString()}
              style={{
                background: 'var(--bg-primary)',
                minHeight: '96px',
                padding: '6px',
                opacity: inMonth ? 1 : 0.35,
              }}
            >
              <div
                style={{
                  fontSize: '0.75rem',
                  fontWeight: isToday ? 800 : 600,
                  color: isToday ? 'var(--action-primary)' : 'var(--text-secondary)',
                  marginBottom: '4px',
                }}
              >
                {day.getDate()}
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '3px' }}>
                {dayEvents.slice(0, 3).map((event) => {
                  const tagKey = event.tags?.[0]
                  const tagStyle = TAG_STYLES[tagKey] || TAG_STYLES.diger
                  return (
                    <Link
                      key={event.id}
                      to={`/etkinlik/${event.id}`}
                      title={event.title}
                      style={{
                        display: 'block',
                        fontSize: '0.68rem',
                        fontWeight: 600,
                        padding: '2px 5px',
                        borderRadius: '5px',
                        background: tagStyle.bg,
                        color: tagStyle.color,
                        textDecoration: 'none',
                        overflow: 'hidden',
                        textOverflow: 'ellipsis',
                        whiteSpace: 'nowrap',
                      }}
                    >
                      {event.title}
                    </Link>
                  )
                })}
                {dayEvents.length > 3 && (
                  <span style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>
                    +{dayEvents.length - 3} daha
                  </span>
                )}
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

export default CalendarPage
