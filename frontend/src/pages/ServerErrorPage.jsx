import React from 'react'
import { Link, useLocation } from 'react-router-dom'

const ServerErrorPage = () => {
    const location = useLocation()
    const errorCode = location.state?.code || 500
    const errorMessage = location.state?.message || 'Sunucu tarafında beklenmeyen bir hata oluştu.'

    return (
        <div className="error-page-container">
            <div className="error-page-content">
                <div className="error-icon-wrapper">
                    <div className="error-icon-bg error-icon-bg--danger">
                        <i className="fas fa-server error-icon-main"></i>
                    </div>
                    <div className="error-pulse"></div>
                </div>

                <h1 className="error-code error-code--danger">{errorCode}</h1>
                <h2 className="error-title">Sunucu Hatası</h2>
                <p className="error-description">
                    {errorMessage}
                </p>

                <div className="error-actions">
                    <button
                        onClick={() => window.location.reload()}
                        className="btn btn-primary btn-lg error-btn"
                    >
                        <i className="fas fa-redo me-2"></i>
                        Sayfayı Yenile
                    </button>
                    <Link to="/" className="btn btn-outline-secondary btn-lg error-btn">
                        <i className="fas fa-home me-2"></i>
                        Ana Sayfaya Dön
                    </Link>
                </div>

                <div className="error-suggestion">
                    <p className="text-muted">
                        <i className="fas fa-info-circle me-2"></i>
                        Sorun devam ederse lütfen daha sonra tekrar deneyin.
                    </p>
                </div>
            </div>
        </div>
    )
}

export default ServerErrorPage
