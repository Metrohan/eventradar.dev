import React, { useEffect, useState } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'

const RedirectPage = () => {
    const navigate = useNavigate()
    const location = useLocation()
    const target = location.state?.target || '/'
    const message = location.state?.message || 'Yönlendiriliyorsunuz...'
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

                <h2 className="error-title">Yönlendirme</h2>
                <p className="error-description">
                    {message}
                </p>

                <div className="redirect-countdown">
                    <span className="countdown-number">{countdown}</span>
                    <span className="countdown-text">saniye içinde yönlendirileceksiniz</span>
                </div>

                <div className="error-actions">
                    <button
                        onClick={() => navigate(target, { replace: true })}
                        className="btn btn-primary btn-lg error-btn"
                    >
                        <i className="fas fa-forward me-2"></i>
                        Hemen Git
                    </button>
                </div>
            </div>
        </div>
    )
}

export default RedirectPage
