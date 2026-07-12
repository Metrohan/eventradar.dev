import React from 'react'
import SupportModal from './SupportModal'
import { Link, useLocation } from 'react-router-dom'
import ThemeToggle from './ThemeToggle'

const NAV_LINKS = [
  { to: '/', label: 'Anasayfa' },
  { to: '/takvim', label: 'Takvim' },
  { to: '/bootcamp-rehberi', label: 'Rehber' },
  { to: '/egitim-kaynaklari', label: 'Ücretsiz Eğitimler' },
  { to: '/oneri-sikayet', label: 'Öneri / Şikayet' },
  { to: '/status', label: 'Durum' },
]

const Header = () => {
  const [showSupport, setShowSupport] = React.useState(false)
  const [mobileOpen, setMobileOpen] = React.useState(false)
  const location = useLocation()

  React.useEffect(() => {
    setMobileOpen(false)
  }, [location.pathname])

  React.useEffect(() => {
    document.body.style.overflow = mobileOpen ? 'hidden' : ''
    return () => { document.body.style.overflow = '' }
  }, [mobileOpen])

  return (
    <>
      {mobileOpen && (
        <div
          className="nav-overlay"
          onClick={() => setMobileOpen(false)}
          aria-hidden="true"
        />
      )}
    <header className="main-header">
      <div className="container">
        <div className="d-flex justify-content-between align-items-center" style={{ position: 'relative' }}>

          {/* Logo */}
          <Link to="/" className="logo-link">
            <img
              src="/techeventradar_logo.png"
              alt="TechEventRadar"
              className="header-logo"
              width="36"
              height="36"
            />
            <span className="logo-text gradient-text">TechEventRadar</span>
          </Link>

          {/* Desktop nav */}
          <nav className={`header-nav ${mobileOpen ? 'open' : ''}`}>
            {NAV_LINKS.map(({ to, label }) => (
              <Link
                key={to}
                to={to}
                className="button-link"
                style={location.pathname === to ? {
                  color: 'var(--action-primary)',
                  background: 'rgba(56,189,248,0.08)',
                  borderColor: 'var(--border-subtle)',
                } : {}}
              >
                {label}
              </Link>
            ))}
	   <a
	  href="https://github.com/Metrohan/eventradar.dev"
  	  target="_blank"
	  rel="noopener noreferrer"
	  className="button-link github-button"
	>
	  <img src="/github-mark-white.png" alt="GitHub" className="github-icon" />
	  GitHub
	</a>
            <ThemeToggle />
            <button
              onClick={() => setShowSupport(true)}
              className="support-btn-link"
            >
              <img src="/coffee.svg" className="bmc-icon" alt="" width="18" height="18" />
              Destek Ol
            </button>
          </nav>

          {/* Mobile hamburger */}
          <button
            className="nav-mobile-toggle"
            onClick={() => setMobileOpen(v => !v)}
            aria-label="Menüyü aç/kapat"
          >
            <i className={`fas fa-${mobileOpen ? 'times' : 'bars'}`}></i>
          </button>
        </div>
      </div>

      <SupportModal show={showSupport} handleClose={() => setShowSupport(false)} />
    </header>
    </>
  )
}

export default Header
