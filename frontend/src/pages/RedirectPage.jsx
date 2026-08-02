import React, { useEffect, useState } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { useTranslation } from 'react-i18next'

const RedirectPage = () => {
    const { t } = useTranslation()
    const navigate = useNavigate()
    const location = useLocation()
    const target = location.state?.target || '/'
    const message = location.state?.message || t('redirectPage.defaultMessage')
    const [countdown, setCountdown] = useState(3)

    useEffect(() => {
        const timer = setInterval(() => {
            setCountdown(prev => {
                if (prev <= 1) {
                    clearInterval(timer)
                    navigate(target, { replace: true })
                    return 0
                }
                return prev - 1
            })
        }, 1000)

        return () => clearInterval(timer)
    }, [navigate, target])

    return (
        <div className="error-page-container">
            <div className="error-page-content">
                <div className="error-icon-wrapper">
                    <div className="error-icon-bg error-icon-bg--info">
                        <i className="fas fa-directions error-icon-main"></i>
                    </div>
                    <div className="redirect-spinner-ring"></div>
                </div>

                <h2 className="error-title">{t('redirectPage.title')}</h2>
                <p className="error-description">
                    {message}
                </p>

                <div className="redirect-countdown">
                    <span className="countdown-number">{countdown}</span>
                    <span className="countdown-text">{t('redirectPage.countdownText', { count: countdown })}</span>
                </div>

                <div className="error-actions">
                    <button
                        onClick={() => navigate(target, { replace: true })}
                        className="btn btn-primary btn-lg error-btn"
                    >
                        <i className="fas fa-forward me-2"></i>
                        {t('redirectPage.goNow')}
                    </button>
                </div>
            </div>
        </div>
    )
}

export default RedirectPage
