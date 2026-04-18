import React from 'react'
import SupportModal from './SupportModal'
import { Link } from 'react-router-dom'
import ThemeToggle from './ThemeToggle'

const Header = () => {
  const [showSupport, setShowSupport] = React.useState(false)


  return (
    <header className="main-header">
      <div className="container">
        <div className="d-flex justify-content-between align-items-center">
          {/* Left side - Logo and Support Button */}
          <div className="header-left-buttons d-flex align-items-center gap-3">
            <Link to="/" className="logo-link">
              <img
                src="/techeventradar_logo.webp"
                alt="TechEventRadar Logo"
                className="header-logo"
                width="40"
                height="40"
              />
            </Link>
            <button
              onClick={() => setShowSupport(true)}
              className="support-btn-link bmc-custom-button border-0 cursor-pointer"
            >
              <img src="/coffee.webp" className="bmc-icon" alt="Coffee" width="24" height="24" />
              Destek Olmak İçin
            </button>
            <SupportModal show={showSupport} handleClose={() => setShowSupport(false)} />
          </div>

          {/* Right buttons */}
          <div className="header-right-buttons">
            <Link to="/" className="button-link">
              Anasayfa
            </Link>
            <Link to="/egitim-kaynaklari" className="button-link">
              Ücretsiz Eğitimler
            </Link>
            <Link to="/oneri-sikayet" className="button-link">
              Öneri/Şikayet
            </Link>
            <a
              href="https://github.com/Metrohan/eventradar.dev"
              target="_blank"
              rel="noopener noreferrer"
              className="button-link github-button"
            >
              <img src="/github-mark-white.webp" alt="GitHub Logo" className="github-icon" />
              GitHub
            </a>
            {/* Admin login sadece direkt URL ile erişilebilir (/admin/login) */}
            <ThemeToggle />
          </div>
        </div>
      </div>
    </header>
  )
}

export default Header



