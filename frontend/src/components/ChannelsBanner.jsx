import React from 'react'
import { useTranslation } from 'react-i18next'

const focusFooterEmail = (e) => {
  e.preventDefault()
  const form = document.getElementById('footer-subscribe')
  if (!form) return
  form.scrollIntoView({ behavior: 'smooth', block: 'center' })
  setTimeout(() => form.querySelector('input[type="email"]')?.focus(), 350)
}

const CHANNELS = (t) => [
  {
    icon: 'fas fa-envelope',
    color: 'var(--action-primary)',
    colorHex: '#38BDF8',
    label: t('channelsBanner.email.label'),
    desc: t('channelsBanner.email.desc'),
    action: t('channelsBanner.email.action'),
    href: '#footer-subscribe',
    external: false,
    onClick: focusFooterEmail,
  },
  {
    icon: 'fab fa-telegram',
    color: '#26A5E4',
    colorHex: '#26A5E4',
    label: t('channelsBanner.telegram.label'),
    desc: t('channelsBanner.telegram.desc'),
    action: t('channelsBanner.telegram.action'),
    href: 'https://t.me/eventradar_tr',
    external: true,
  },
  {
    icon: 'fas fa-rss',
    color: '#F26522',
    colorHex: '#F26522',
    label: t('channelsBanner.rss.label'),
    desc: t('channelsBanner.rss.desc'),
    action: t('channelsBanner.rss.action'),
    href: '/api/events/rss',
    external: true,
  },
]

const ChannelsBanner = () => {
  const { t } = useTranslation()

  return (
    <section style={{ padding: '1.5rem 0 2.5rem' }}>
      <div className="container">
        <p style={{
          fontWeight: 700,
          fontSize: '0.75rem',
          textTransform: 'uppercase',
          letterSpacing: '0.8px',
          color: 'var(--text-muted)',
          marginBottom: '0.75rem',
        }}>
          {t('channelsBanner.heading')}
        </p>
        <div className="row g-3">
          {CHANNELS(t).map((ch) => (
            <div key={ch.href} className="col-md-4">
              <ChannelCard {...ch} />
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}

const ChannelCard = ({ icon, color, colorHex, label, desc, action, href, external, onClick }) => {
  const [hovered, setHovered] = React.useState(false)

  return (
    <a
      href={href}
      target={external ? '_blank' : undefined}
      rel={external ? 'noopener noreferrer' : undefined}
      onClick={onClick}
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: '0.875rem',
        padding: '1rem 1.125rem',
        borderRadius: '12px',
        border: `1px solid ${hovered ? colorHex : 'var(--border-subtle)'}`,
        background: 'var(--bg-card)',
        textDecoration: 'none',
        transition: 'border-color 0.2s, box-shadow 0.2s',
        boxShadow: hovered ? `0 4px 16px ${colorHex}22` : 'none',
      }}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
    >
      <div style={{
        width: 40,
        height: 40,
        borderRadius: '10px',
        background: `${colorHex}18`,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        flexShrink: 0,
      }}>
        <i className={icon} style={{ fontSize: '1.1rem', color }} />
      </div>

      <div style={{ minWidth: 0, flex: 1 }}>
        <div style={{ fontWeight: 700, fontSize: '0.875rem', color: 'var(--text-primary)', marginBottom: '0.1rem' }}>
          {label}
        </div>
        <div style={{ fontSize: '0.775rem', color: 'var(--text-muted)', lineHeight: 1.4 }}>
          {desc}
        </div>
      </div>

      <span style={{
        fontSize: '0.75rem',
        fontWeight: 600,
        color,
        whiteSpace: 'nowrap',
        flexShrink: 0,
      }}>
        {action} <i className="fas fa-arrow-right" style={{ fontSize: '0.65rem' }} />
      </span>
    </a>
  )
}

export default ChannelsBanner
