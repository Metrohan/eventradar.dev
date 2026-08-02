import React, { Suspense, lazy } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { useTranslation } from 'react-i18next'

import ThemeToggle from './ThemeToggle'
import LanguageToggle from './LanguageToggle'

// Lazy: only needed once a user clicks "support", not for first paint —
// keeps its ~2KB out of the initial JS every visitor downloads (see
// docs/adr/0006-prerender-poc.md's bundle-analyzer step).
const SupportModal = lazy(() => import('./SupportModal'))

const Header = () => {
  const { t } = useTranslation()
  const [showSupport, setShowSupport] = React.useState(false)
  const [mobileOpen, setMobileOpen] = React.useState(false)
  const location = useLocation()

  const DISCOVER_LINKS = [
    { to: '/', label: t('nav.discoverLinks.all'), icon: 'fa-compass' },
    { to: '/takvim', label: t('nav.discoverLinks.calendar'), icon: 'fa-calendar-alt' },
    { to: '/hackathonlar', label: t('nav.discoverLinks.hackathons'), icon: 'fa-code' },
    { to: '/bootcamplar', label: t('nav.discoverLinks.bootcamps'), icon: 'fa-laptop-code' },
    { to: '/online-etkinlikler', label: t('nav.discoverLinks.online'), icon: 'fa-globe' },
    { to: '/bu-haftaki-etkinlikler', label: t('nav.discoverLinks.thisWeek'), icon: 'fa-bolt' },
    { to: '/son-basvurular', label: t('nav.discoverLinks.lastCall'), icon: 'fa-hourglass-half' },
  ]

  const CONTENT_LINKS = [
    { to: '/blog', label: t('nav.contentLinks.weeklyGuide'), icon: 'fa-newspaper' },
    { to: '/bootcamp-rehberi', label: t('nav.contentLinks.bootcampGuide'), icon: 'fa-book-open' },
    { to: '/egitim-kaynaklari', label: t('nav.contentLinks.freeTrainings'), icon: 'fa-graduation-cap' },
  ]

  React.useEffect(() => {
    setMobileOpen(false)
    document.querySelectorAll('.nav-menu[open]').forEach(menu => menu.removeAttribute('open'))
  }, [location.pathname])

  React.useEffect(() => {
    document.body.style.overflow = mobileOpen ? 'hidden' : ''
    return () => { document.body.style.overflow = '' }
  }, [mobileOpen])

  React.useEffect(() => {
    const closeMenus = event => {
      if (!event.target.closest('.nav-menu')) {
        document.querySelectorAll('.nav-menu[open]').forEach(menu => menu.removeAttribute('open'))
      }
    }
    document.addEventListener('click', closeMenus)
    return () => document.removeEventListener('click', closeMenus)
  }, [])

  const isActive = path => path === '/'
    ? location.pathname === '/'
    : location.pathname.startsWith(path)

  return (
    <>
      {mobileOpen && <div className="nav-overlay" onClick={() => setMobileOpen(false)} aria-hidden="true" />}
      <header className="main-header">
        <div className="container header-shell">
          <Link to="/" className="logo-link" aria-label={t('header.logoAlt')}>
            <img src="/techeventradar_logo.png" alt="" className="header-logo" width="69" height="36" />
            <span className="logo-text gradient-text">TechEventRadar</span>
          </Link>

          <nav className={`header-nav ${mobileOpen ? 'open' : ''}`} aria-label={t('nav.mainMenu')}>
            <NavMenu label={t('nav.discover')} icon="fa-compass" links={DISCOVER_LINKS} isActive={isActive} />
            <NavMenu label={t('nav.content')} icon="fa-layer-group" links={CONTENT_LINKS} isActive={isActive} />
            <Link to="/status" className={`button-link ${isActive('/status') ? 'active' : ''}`}>{t('nav.status')}</Link>
            <Link to="/etkinlik-talep" className={`button-link ${isActive('/etkinlik-talep') ? 'active' : ''}`}>{t('nav.addEvent')}</Link>

            <div className="header-actions">
              <a href="https://github.com/Metrohan/eventradar.dev" target="_blank" rel="noopener noreferrer" className="header-icon-button" aria-label={t('nav.github')} title="GitHub">
                <i className="fab fa-github" />
              </a>
              <LanguageToggle />
              <ThemeToggle />
              <button type="button" onClick={() => setShowSupport(true)} className="support-btn-link">
                <img src="/coffee.svg" className="bmc-icon" alt="" width="18" height="18" />
                <span>{t('header.supportButton')}</span>
              </button>
            </div>
          </nav>

          <button className="nav-mobile-toggle" onClick={() => setMobileOpen(value => !value)} aria-expanded={mobileOpen} aria-label={t('nav.menuToggle')}>
            <i className={`fas fa-${mobileOpen ? 'times' : 'bars'}`} />
          </button>
        </div>
        {showSupport && (
          <Suspense fallback={null}>
            <SupportModal show={showSupport} handleClose={() => setShowSupport(false)} />
          </Suspense>
        )}
      </header>
    </>
  )
}

const NavMenu = ({ label, icon, links, isActive }) => {
  const groupActive = links.some(link => isActive(link.to))

  // <details> elements don't close each other natively, so opening "İçerikler"
  // while "Keşfet" is still open leaves both panels absolutely positioned on
  // screen at once, overlapping. Close any other open nav menu on toggle.
  const handleToggle = e => {
    if (!e.target.open) return
    document.querySelectorAll('.nav-menu[open]').forEach(menu => {
      if (menu !== e.target) menu.removeAttribute('open')
    })
  }

  return (
    <details className="nav-menu" onToggle={handleToggle}>
      <summary className={`button-link nav-menu-trigger ${groupActive ? 'active' : ''}`}>
        <i className={`fas ${icon}`} />
        {label}
        <i className="fas fa-chevron-down nav-menu-chevron" />
      </summary>
      <div className="nav-menu-panel">
        {links.map(link => (
          <Link key={link.to} to={link.to} className={`nav-menu-item ${isActive(link.to) ? 'active' : ''}`}>
            <span className="nav-menu-icon"><i className={`fas ${link.icon}`} /></span>
            <span>{link.label}</span>
          </Link>
        ))}
      </div>
    </details>
  )
}

export default Header
