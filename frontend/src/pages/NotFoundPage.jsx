import React from 'react'
import { Link } from 'react-router-dom'

const NotFoundPage = () => {
    return (
        <div className="error-page-container">
            <div className="error-page-content">
                <div className="error-icon-wrapper">
                    <div className="error-icon-bg">
                        <i className="fas fa-ghost error-icon-main"></i>
                    </div>
                    <div className="error-particles">
                        <span></span><span></span><span></span><span></span><span></span>
                    </div>
                </div>

                <h1 className="error-code">404</h1>
                <h2 className="error-title">Sayfa Bulunamadı</h2>
                <p className="error-description">
                    Aradığınız sayfa mevcut değil, taşınmış veya kaldırılmış olabilir.
                </p>

                <div className="error-actions">
                    <Link to="/" className="btn btn-primary btn-lg error-btn">
                        <i className="fas fa-home me-2"></i>
                        Ana Sayfaya Dön
                    </Link>
                    <button
                        onClick={() => window.history.back()}
                        className="btn btn-outline-secondary btn-lg error-btn"
                    >
                        <i className="fas fa-arrow-left me-2"></i>
                        Geri Git
                    </button>
                </div>

                <div className="error-suggestion">
                    <p className="text-muted">
                        <i className="fas fa-lightbulb me-2"></i>
                        URL adresini kontrol etmeyi deneyin veya ana sayfadan tekrar başlayın.
                    </p>
                </div>
            </div>
        </div>
    )
}

export default NotFoundPage
