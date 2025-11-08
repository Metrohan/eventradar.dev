import React from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'

const Header = () => {
  const { isAuthenticated, logout } = useAuth()

  return (
    <header className="main-header">
      <div className="container">
        <div className="d-flex justify-content-between align-items-center">
            {/* Left side - Logo and Support Button */}
            <div className="header-left-buttons d-flex align-items-center gap-3">
              <Link to="/" className="logo-link">
                <img 
                  src="/techeventradar_logo.png" 
                  alt="TechEventRadar Logo" 
                  className="header-logo"
                />
              </Link>
            <a 
              href="https://www.buymeacoffee.com/metehangnn" 
              target="_blank" 
              rel="noopener noreferrer"
              className="support-btn-link bmc-custom-button"
            >
              <img src="/coffee.svg" className="bmc-icon" alt="Coffee" />
              Destek Olmak İçin
            </a>
          </div>

          {/* Right buttons */}
          <div className="header-right-buttons">
            <Link to="/etkinlik-talep" className="button-link">
              Etkinlik Ekleme Talebi
            </Link>
            <Link to="/oneri-sikayet" className="button-link">
              Öneri/Şikayet
            </Link>
            <a 
              href="https://github.com/Metrohan/TechEventRadar" 
              target="_blank" 
              rel="noopener noreferrer" 
              className="button-link github-button"
            >
              <img src="/github-mark-white.png" alt="GitHub Logo" className="github-icon" />
              GitHub
            </a>
            {/* Admin login sadece direkt URL ile erişilebilir (/admin/login) */}
          </div>
        </div>
      </div>
    </header>
  )
}

export default Header



