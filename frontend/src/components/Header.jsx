import React from 'react'
import SupportModal from './SupportModal'
import { Link, useLocation } from 'react-router-dom'
import ThemeToggle from './ThemeToggle'

const NAV_LINKS = [
  { to: '/', label: 'Anasayfa' },
  { to: '/egitim-kaynaklari', label: 'Ücretsiz Eğitimler' },
  { to: '/oneri-sikayet', label: 'Öneri / Şikayet' },
]

const Header = () => {
  const [showSupport, setShowSupport] = React.useState(false)
  const [mobileOpen, setMobileOpen] = React.useState(false)
  const location = useLocation()
  const navWrapRef = React.useRef(null)

  React.useEffect(() => {
    setMobileOpen(false)
  }, [location.pathname])

  React.useEffect(() => {
    if (!mobileOpen) return
    const handleOutside = (e) => {
      if (navWrapRef.current && !navWrapRef.current.contains(e.target)) {
        setMobileOpen(false)
      }
    }
    document.addEventListener('mousedown', handleOutside)
    document.addEventListener('touchstart', handleOutside, { passive: true })
    return () => {
      document.removeEventListener('mousedown', handleOutside)
      document.removeEventListener('touchstart', handleOutside)
    }
  }, [mobileOpen])

  return (
    <>
      <header className="main-header">
        <div className="container">
          <div
            className="d-flex justify-content-between align-items-center"
            style={{ position: 'relative' }}
            ref={navWrapRef}
          >
            {/* Logo */}
            <Link to="/" className="logo-link">
              <img
                src="/techeventradar_logo.webp"
                alt="TechEventRadar"
                className="header-logo"
                width="36"
                height="36"
              />
              <span className="logo-text gradient-text">TechEventRadar</span>
            </Link>

            {/* Desktop + mobile nav */}
            <nav className={`header-nav ${mobileOpen ? 'open' : ''}`} aria-label="Ana menü">
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
                <img src="/github-mark-white.webp" alt="GitHub" className="github-icon" />
                GitHub
              </a>
              <div className="nav-mobile-divider" />
              <div className="nav-mobile-row">
                <ThemeToggle />
                <button
                  onClick={() => setShowSupport(true)}
                  className="support-btn-link"
                >
                  <img src="/coffee.webp" className="bmc-icon" alt="" width="18" height="18" />
                  Destek Ol
                </button>
              </div>
            </nav>

            {/* Mobile hamburger */}
            <button
              className="nav-mobile-toggle"
              onClick={() => setMobileOpen(v => !v)}
              aria-label="Menüyü aç/kapat"
              aria-expanded={mobileOpen}
            >
              <span className={`hamburger-icon ${mobileOpen ? 'open' : ''}`}>
                <span />
                <span />
                <span />
              </span>
            </button>
          </div>
        </div>

        <SupportModal show={showSupport} handleClose={() => setShowSupport(false)} />
      </header>

      {/* Backdrop for mobile menu */}
      <div
        className={`nav-mobile-backdrop ${mobileOpen ? 'open' : ''}`}
        onClick={() => setMobileOpen(false)}
        aria-hidden="true"
      />
    </>
  )
}

export default Header
