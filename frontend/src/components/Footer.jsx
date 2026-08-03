import React from 'react'
import { Link } from 'react-router-dom'
import toast from 'react-hot-toast'
import { useTranslation } from 'react-i18next'
import useSources from '../hooks/useSources'
import { publicAPI } from '../services/api'
import { getErrorMessage } from '../utils/errorMessage'
import PushNotificationToggle from './PushNotificationToggle'

const Footer = () => {
  const { t } = useTranslation()
  const { sources } = useSources()
  const [email, setEmail] = React.useState('')
  const [submitting, setSubmitting] = React.useState(false)

  const QUICK_LINKS = [
    { to: '/', label: t('footer.quickLinks.home') },
    { to: '/egitim-kaynaklari', label: t('footer.quickLinks.freeTrainings') },
    { to: '/oneri-sikayet', label: t('footer.quickLinks.feedback') },
    { to: '/etkinlik-talep', label: t('footer.quickLinks.addEvent') },
  ]

  const handleSubscribe = async (e) => {
    e.preventDefault()
    if (!email) return
    setSubmitting(true)
    try {
      const { data } = await publicAPI.subscribeEmail(email)
      toast.success(data.message || t('footer.subscribeSuccess'))
      setEmail('')
    } catch (err) {
      toast.error(getErrorMessage(err, t('footer.subscribeError')))
    } finally {
      setSubmitting(false)
    }
  }

  return (
  <footer style={{
    background: 'var(--bg-secondary, #0F172A)',
    borderTop: '1px solid var(--border-subtle)',
    padding: '3.5rem 0 1.5rem',
    marginTop: 'auto',
  }}>
    <div className="container">
      <div className="row gy-4 mb-4">

        {/* Brand */}
        <div className="col-lg-4 col-md-6">
          <Link to="/" style={{ textDecoration: 'none', display: 'inline-flex', alignItems: 'center', gap: '0.6rem', marginBottom: '1rem' }}>
            <span style={{ fontSize: '1.1rem', fontWeight: 800, letterSpacing: '-0.3px' }} className="gradient-text">
              TechEventRadar
            </span>
          </Link>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem', lineHeight: 1.7, maxWidth: 280, marginBottom: '1.25rem' }}>
            {t('footer.tagline')}
          </p>

          <form id="footer-subscribe" onSubmit={handleSubscribe} style={{ display: 'flex', gap: '0.5rem', maxWidth: 320, marginBottom: '1.25rem' }}>
            <input
              type="email"
              required
              placeholder={t('footer.emailPlaceholder')}
              value={email}
              onChange={e => setEmail(e.target.value)}
              style={{
                flex: 1,
                minWidth: 0,
                padding: '0.5rem 0.75rem',
                borderRadius: '8px',
                border: '1px solid var(--border-color)',
                background: 'var(--bg-card)',
                color: 'var(--text-primary)',
                fontSize: '0.85rem',
              }}
            />
            <button
              type="submit"
              disabled={submitting}
              style={{
                padding: '0.5rem 1rem',
                borderRadius: '8px',
                border: 'none',
                background: 'var(--action-primary)',
                color: '#0B1120',
                fontWeight: 700,
                fontSize: '0.85rem',
                whiteSpace: 'nowrap',
                cursor: submitting ? 'default' : 'pointer',
              }}
            >
              {submitting ? t('footer.subscribing') : t('footer.subscribeButton')}
            </button>
          </form>

          <PushNotificationToggle />

          <div style={{ display: 'flex', gap: '0.75rem' }}>
            <a
              href="https://github.com/Metrohan/eventradar.dev"
              target="_blank"
              rel="noopener noreferrer"
              aria-label={t('footer.githubAria')}
              style={socialLinkStyle}
            >
              <i className="fab fa-github"></i>
            </a>
            <a
              href="mailto:metehangnn@outlook.com"
              aria-label={t('footer.emailAria')}
              style={socialLinkStyle}
            >
              <i className="fas fa-envelope"></i>
            </a>
            <a
              href="https://t.me/eventradar_tr"
              target="_blank"
              rel="noopener noreferrer"
              aria-label={t('footer.telegramAria')}
              style={socialLinkStyle}
            >
              <i className="fab fa-telegram"></i>
            </a>
            <a
              href="/api/events/rss"
              target="_blank"
              rel="noopener noreferrer"
              aria-label={t('footer.rssAria')}
              style={socialLinkStyle}
            >
              <i className="fas fa-rss"></i>
            </a>
          </div>
        </div>

        {/* Quick links */}
        <div className="col-lg-2 col-md-3 col-6">
          <p style={sectionHeadStyle}>{t('footer.pagesHeading')}</p>
          <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
            {QUICK_LINKS.map(({ to, label }) => (
              <li key={to} style={{ marginBottom: '0.5rem' }}>
                <Link to={to} style={footerLinkStyle}>{label}</Link>
              </li>
            ))}
          </ul>
        </div>

        {/* Sources */}
        <div className="col-lg-2 col-md-3 col-6">
          <p style={sectionHeadStyle}>{t('footer.sourcesHeading')}</p>
          <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
            {sources.map(source => (
              <li key={source.key} style={{ marginBottom: '0.5rem' }}>
                <a href={source.website} target="_blank" rel="noopener noreferrer" style={footerLinkStyle}>
                  {source.name}
                </a>
              </li>
            ))}
          </ul>
        </div>

        {/* Open source badge */}
        <div className="col-lg-4 col-md-6 d-flex align-items-start justify-content-lg-end">
          <a
            href="https://github.com/Metrohan/eventradar.dev"
            target="_blank"
            rel="noopener noreferrer"
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '0.75rem',
              padding: '1rem 1.5rem',
              width: '100%',
              maxWidth: '280px',
              background: 'var(--bg-card)',
              border: '1px solid var(--border-subtle)',
              borderRadius: '16px',
              textDecoration: 'none',
              transition: 'all 0.25s ease',
            }}
            onMouseEnter={e => {
              e.currentTarget.style.borderColor = 'var(--action-primary)'
              e.currentTarget.style.boxShadow = '0 4px 20px rgba(56,189,248,0.12)'
            }}
            onMouseLeave={e => {
              e.currentTarget.style.borderColor = 'var(--border-subtle)'
              e.currentTarget.style.boxShadow = 'none'
            }}
          >
            <i className="fab fa-github" style={{ fontSize: '1.5rem', color: 'var(--text-secondary)' }}></i>
            <span>
              <span style={{ display: 'block', fontWeight: 700, color: 'var(--text-primary)', fontSize: '0.9rem' }}>{t('footer.openSourceHeading')}</span>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{t('footer.openSourceSubtitle')}</span>
            </span>
          </a>

        </div>
      </div>

      {/* Bottom bar */}
      <div style={{
        borderTop: '1px solid var(--border-color)',
        paddingTop: '1.5rem',
        display: 'flex',
        flexWrap: 'wrap',
        gap: '0.5rem',
        alignItems: 'center',
        justifyContent: 'space-between',
      }}>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.8rem', margin: 0 }}>
          {t('footer.copyright', { year: new Date().getFullYear() })}
        </p>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.8rem', margin: 0 }}>
          {t('footer.madeWith')}{' '}
          <i className="fas fa-heart" style={{ color: 'var(--danger)', margin: '0 2px' }}></i>
        </p>
      </div>
    </div>
  </footer>
  )
}

const sectionHeadStyle = {
  color: 'var(--text-primary)',
  fontWeight: 700,
  fontSize: '0.85rem',
  textTransform: 'uppercase',
  letterSpacing: '0.5px',
  marginBottom: '0.875rem',
}

const footerLinkStyle = {
  color: 'var(--text-secondary)',
  textDecoration: 'none',
  fontSize: '0.875rem',
  transition: 'color 0.2s ease',
}

const socialLinkStyle = {
  width: 36,
  height: 36,
  borderRadius: '8px',
  background: 'var(--bg-card)',
  border: '1px solid var(--border-color)',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  color: 'var(--text-secondary)',
  textDecoration: 'none',
  fontSize: '0.9rem',
  transition: 'all 0.2s ease',
}

export default Footer
