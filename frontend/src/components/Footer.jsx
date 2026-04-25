import React from 'react'
import { Link } from 'react-router-dom'

const QUICK_LINKS = [
  { to: '/', label: 'Anasayfa' },
  { to: '/egitim-kaynaklari', label: 'Ücretsiz Eğitimler' },
  { to: '/oneri-sikayet', label: 'Öneri & Şikayet' },
  { to: '/etkinlik-talep', label: 'Etkinlik Ekle' },
]

const SOURCES = [
  'TechCareer.net', 'Kodluyoruz', 'Youthall',
  'Coderspace', 'Anbean', 'Akbank', 'Pupilica',
]

const Footer = () => (
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
            Türkiye'deki teknoloji etkinliklerini, hackathon'ları ve ücretsiz eğitimleri tek platformda takip edin.
          </p>
          <div style={{ display: 'flex', gap: '0.75rem' }}>
            <a
              href="https://github.com/Metrohan/eventradar.dev"
              target="_blank"
              rel="noopener noreferrer"
              aria-label="GitHub"
              style={socialLinkStyle}
            >
              <i className="fab fa-github"></i>
            </a>
            <a
              href="mailto:metehangnn@outlook.com"
              aria-label="E-posta"
              style={socialLinkStyle}
            >
              <i className="fas fa-envelope"></i>
            </a>
          </div>
        </div>

        {/* Quick links */}
        <div className="col-lg-2 col-md-3 col-6">
          <p style={sectionHeadStyle}>Sayfalar</p>
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
          <p style={sectionHeadStyle}>Kaynaklar</p>
          <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
            {SOURCES.map(src => (
              <li key={src} style={{ marginBottom: '0.5rem' }}>
                <span style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>{src}</span>
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
              flexDirection: 'column',
              alignItems: 'center',
              gap: '0.5rem',
              padding: '1.25rem 2rem',
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
            <i className="fab fa-github" style={{ fontSize: '1.75rem', color: 'var(--text-secondary)' }}></i>
            <span style={{ fontWeight: 700, color: 'var(--text-primary)', fontSize: '0.9rem' }}>Açık Kaynak</span>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>GitHub'da yıldız bırak ⭐</span>
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
          © {new Date().getFullYear()} TechEventRadar — Açık kaynak topluluk projesi
        </p>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.8rem', margin: 0 }}>
          Yazılımcılar için, yazılımcılar tarafından{' '}
          <i className="fas fa-heart" style={{ color: 'var(--danger)', margin: '0 2px' }}></i>
        </p>
      </div>
    </div>
  </footer>
)

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
