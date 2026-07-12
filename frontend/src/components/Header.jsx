import React from 'react'
import { Link, useLocation } from 'react-router-dom'

import SupportModal from './SupportModal'
import ThemeToggle from './ThemeToggle'

const DISCOVER_LINKS = [
  { to: '/', label: 'Tüm Etkinlikler', icon: 'fa-compass' },
  { to: '/takvim', label: 'Etkinlik Takvimi', icon: 'fa-calendar-days' },
  { to: '/hackathonlar', label: 'Hackathonlar', icon: 'fa-code' },
  { to: '/bootcamplar', label: 'Bootcamp’ler', icon: 'fa-laptop-code' },
  { to: '/online-etkinlikler', label: 'Online Etkinlikler', icon: 'fa-globe' },
  { to: '/bu-haftaki-etkinlikler', label: 'Bu Hafta', icon: 'fa-bolt' },
  { to: '/son-basvurular', label: 'Son Başvurular', icon: 'fa-hourglass-half' },
]

const CONTENT_LINKS = [
  { to: '/blog', label: 'Haftalık Rehber', icon: 'fa-newspaper' },
  { to: '/bootcamp-rehberi', label: 'Bootcamp Rehberi', icon: 'fa-book-open' },
  { to: '/egitim-kaynaklari', label: 'Ücretsiz Eğitimler', icon: 'fa-graduation-cap' },
]

const Header = () => {
  const [showSupport, setShowSupport] = React.useState(false)
  const [mobileOpen, setMobileOpen] = React.useState(false)
  const location = useLocation()

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
          <Link to="/" className="logo-link" aria-label="TechEventRadar anasayfa">
            <img src="/techeventradar_logo.png" alt="" className="header-logo" width="36" height="36" />
            <span className="logo-text gradient-text">TechEventRadar</span>
          </Link>

          <nav className={`header-nav ${mobileOpen ? 'open' : ''}`} aria-label="Ana menü">
            <NavMenu label="Keşfet" icon="fa-compass" links={DISCOVER_LINKS} isActive={isActive} />
            <NavMenu label="İçerikler" icon="fa-layer-group" links={CONTENT_LINKS} isActive={isActive} />
            <Link to="/status" className={`button-link ${isActive('/status') ? 'active' : ''}`}>Durum</Link>
            <Link to="/etkinlik-talep" className={`button-link ${isActive('/etkinlik-talep') ? 'active' : ''}`}>Etkinlik Ekle</Link>

            <div className="header-actions">
              <a href="https://github.com/Metrohan/eventradar.dev" target="_blank" rel="noopener noreferrer" className="header-icon-button" aria-label="GitHub deposu" title="GitHub">
                <i className="fab fa-github" />
              </a>
              <ThemeToggle />
              <button type="button" onClick={() => setShowSupport(true)} className="support-btn-link">
                <img src="/coffee.svg" className="bmc-icon" alt="" width="18" height="18" />
                <span>Destek Ol</span>
              </button>
            </div>
          </nav>

          <button className="nav-mobile-toggle" onClick={() => setMobileOpen(value => !value)} aria-expanded={mobileOpen} aria-label="Menüyü aç veya kapat">
            <i className={`fas fa-${mobileOpen ? 'times' : 'bars'}`} />
          </button>
        </div>
        <SupportModal show={showSupport} handleClose={() => setShowSupport(false)} />
      </header>
    </>
  )
}

const NavMenu = ({ label, icon, links, isActive }) => {
  const groupActive = links.some(link => isActive(link.to))
  return (
    <details className="nav-menu">
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
